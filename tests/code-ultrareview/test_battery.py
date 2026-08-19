"""Behavioral tests for the Code Ultrareview analyzer battery."""

from __future__ import annotations

import json
import os
import shlex
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT_DIR = REPO_ROOT / "skills" / "code-ultrareview" / "scripts"
BATTERY = SCRIPT_DIR / "run_battery.sh"
PREFLIGHT = SCRIPT_DIR / "preflight_tools.sh"
SCOPE = SCRIPT_DIR / "scope.py"
AXES = SCRIPT_DIR / "axis_dispatch.py"
SYNTHESIZE = SCRIPT_DIR / "synthesize.py"

ALL_TOOLS = (
    "knip", "jscpd", "markdownlint-cli2", "api-extractor", "lizard",
    "vulture", "semgrep", "vale", "oasdiff", "atlas", "deadcode",
    "gocyclo", "dupl", "cargo-machete",
)


def _shim(directory: Path, name: str, body: str = "exit 0") -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(f"#!/bin/bash\n{body}\n", encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return path


def _python_shim(directory: Path) -> None:
    _shim(
        directory,
        "python3",
        f'exec {shlex.quote(sys.executable)} "$@"',
    )


def _jscpd_empty(directory: Path, returncode: int = 0) -> None:
    _shim(
        directory,
        "jscpd",
        'while [[ $# -gt 0 ]]; do\n'
        '  if [[ "$1" == "--output" ]]; then\n'
        '    mkdir -p "$2"\n'
        '    printf \'{"duplicates":[]}\\n\' > "$2/jscpd-report.json"\n'
        f'    exit {returncode}\n'
        '  fi\n'
        '  shift\n'
        'done\nexit 2',
    )


def _touch(repo: Path, relative: str, body: str = "") -> None:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _write_scope(
    repo: Path,
    files: list[str],
    languages: list[str],
    *,
    create_files: bool = True,
    **overrides,
) -> Path:
    if create_files:
        for relative in files:
            if not (repo / relative).exists():
                _touch(repo, relative)
    payload = {
        "base": "HEAD",
        "target": "HEAD",
        "rule": "test",
        "repo_kind": "app",
        "languages": languages,
        "instruction_chain": [],
        "files_touched": len(files),
        "files_touched_list": files,
        "activates_coherence": False,
        "tools_skipped": [],
        "tools_missing": [],
    }
    payload.update(overrides)
    path = repo / "scope.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _env(bin_dir: Optional[Path] = None, **extra: str) -> dict[str, str]:
    path = "/usr/bin:/bin"
    if bin_dir is not None:
        _python_shim(bin_dir)
        path = f"{bin_dir}:{path}"
    return {**os.environ, "PATH": path, **extra}


def _run_battery(
    repo: Path,
    scope: Path,
    *,
    bin_dir: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    axes: Optional[str] = None,
    dry_run: bool = False,
    env: Optional[dict[str, str]] = None,
    timeout: int = 20,
) -> subprocess.CompletedProcess:
    args = [
        "bash", str(BATTERY), "--scope", str(scope), "--output-dir",
        str(output_dir or repo / "out"), "--repo", str(repo),
    ]
    if axes:
        args.extend(["--axes", axes])
    if dry_run:
        args.append("--dry-run")
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
        env=env or _env(bin_dir),
    )


def _plan(
    repo: Path,
    scope: Path,
    bin_dir: Optional[Path] = None,
    axes: Optional[str] = None,
) -> tuple[subprocess.CompletedProcess, dict]:
    result = _run_battery(
        repo, scope, bin_dir=bin_dir, axes=axes, dry_run=True
    )
    payload = json.loads(result.stdout) if result.stdout.strip() else {}
    return result, payload


def _names(plan: dict, key: str) -> set[str]:
    return {entry["tool"] for entry in plan.get(key, [])}


def _shims(directory: Path, names=ALL_TOOLS) -> None:
    for name in names:
        _shim(directory, name)


def _findings_exit_without_finding_case(repo: Path, tool: str) -> tuple[Path, Path, str]:
    bin_dir = repo / "bin"
    cases = {
        "knip": (["src/app.js"], ["javascript"], "simplification",
                 "printf '%s\\n' '{\"issues\":[]}'\nexit 1", ("jscpd", "lizard")),
        "jscpd": (["src/app.py"], ["python"], "simplification", "", ("lizard", "vulture")),
        "markdownlint-cli2": (["README.md"], ["markdown"], "documentation",
                              "printf '%s\\n' 'markdownlint-cli2 v0.23.2 "
                              "(markdownlint v0.41.1)'\nexit 1", ()),
        "api-extractor": (["src/index.ts"], ["typescript"], "design-api",
                          "printf '%s\\n' 'API Extractor completed "
                          "successfully'\nexit 1", ()),
        "vulture": (["src/app.py"], ["python"], "simplification", "exit 3", ("jscpd", "lizard")),
        "semgrep": (["src/app.py"], ["python"], "performance",
                    "printf '%s\\n' '{\"results\":[],\"errors\":[]}'\nexit 1", ()),
        "vale": (["README.md"], ["markdown"], "documentation",
                 "printf '%s\\n' '{}'\nexit 1", ("markdownlint-cli2",)),
        "oasdiff": (["spec/openapi.yaml"], ["yaml"], "design-api",
                    "printf '%s\\n' '[]'\nexit 1", ()),
        "atlas": (["migrations/001.sql"], ["sql"], "design-api", "", ()),
        "gocyclo": (["main.go"], ["go"], "simplification", "exit 1",
                    ("jscpd", "lizard", "deadcode", "dupl")),
        "cargo-machete": (["src/lib.rs"], ["rust"], "simplification",
                          "printf '%s\\n' 'cargo-machete did not find any "
                          "unused dependencies'\nexit 1", ("jscpd", "lizard")),
    }
    files, languages, axes, body, companions = cases[tool]
    if tool == "api-extractor":
        _touch(repo, "api-extractor.json", "{}\n")
    elif tool == "vale":
        _touch(repo, ".vale.ini", "StylesPath = styles\n")
    if tool == "oasdiff":
        _touch(repo, "spec/openapi.yaml", "openapi: 3.1.0\n")
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "add", "spec/openapi.yaml"], check=True)
        subprocess.run(
            ["git", "-C", str(repo), "-c", "user.name=Test",
                "-c", "user.email=test@example.com", "-c",
                "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
                "commit", "-qm", "base"], check=True,
        )
        _touch(repo, "spec/openapi.yaml", "openapi: 3.1.0\ninfo: {}\n")
    elif tool == "atlas":
        _touch(repo, "atlas.hcl")
        report = json.dumps({"Steps": [{"Name": "Migration Integrity Check",
                                        "Error": "checksum mismatch"}],
                             "Files": [{"Name": "atlas.sum",
                                        "Error": "checksum mismatch"}]})
        body = f"printf '%s\\n' {shlex.quote(report)}\nexit 1"
    scope = _write_scope(repo, files, languages, create_files=tool != "oasdiff")
    for companion in companions:
        _jscpd_empty(bin_dir) if companion == "jscpd" else _shim(bin_dir, companion)
    if tool == "jscpd":
        _jscpd_empty(bin_dir, returncode=1)
    else:
        _shim(bin_dir, tool, body)
    return scope, bin_dir, axes


class TestInputAndDispatch(unittest.TestCase):
    def test_invalid_scope_fails_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope = repo / "scope.json"
            scope.write_text("{broken\n", encoding="utf-8")
            result = _run_battery(repo, scope)
        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid Code Ultrareview scope", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_scope_count_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope = _write_scope(repo, ["README.md"], ["markdown"])
            payload = json.loads(scope.read_text(encoding="utf-8"))
            payload["files_touched"] = 2
            scope.write_text(json.dumps(payload), encoding="utf-8")
            result = _run_battery(repo, scope)
        self.assertEqual(result.returncode, 2)
        self.assertIn("does not match files_touched_list", result.stderr)

    def test_invalid_package_manifest_removes_stale_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _touch(repo, "src/app.ts", "export const value = 1;\n")
            _touch(repo, "package.json", "{broken\n")
            scope = _write_scope(
                repo,
                ["src/app.ts", "package.json"],
                ["typescript"],
                tool_coverage={"complete": True},
                coverage_complete=True,
            )
            output = repo / "out"
            output.mkdir()
            stale = output / "tool-findings.jsonl"
            stale.write_text('{"message":"stale"}\n', encoding="utf-8")
            result = _run_battery(repo, scope, output_dir=output)
            state = json.loads(scope.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 2)
        self.assertFalse(stale.exists())
        self.assertFalse(state["tool_coverage"]["complete"])
        self.assertFalse(state["coverage_complete"])

    def test_dry_run_preserves_previous_completed_battery(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope = _write_scope(
                repo, ["README.md"], ["markdown"],
                tool_coverage={"complete": True}, coverage_complete=True,
            )
            output = repo / "out"
            output.mkdir()
            previous = output / "tool-findings.jsonl"
            previous.write_text('{"message":"previous"}\n', encoding="utf-8")
            bin_dir = repo / "bin"
            _shim(bin_dir, "markdownlint-cli2")
            result = _run_battery(
                repo, scope, bin_dir=bin_dir, output_dir=output,
                axes="documentation", dry_run=True,
            )
            state = json.loads(scope.read_text(encoding="utf-8"))
            previous_text = previous.read_text(encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(state["tool_coverage"]["complete"])
        self.assertTrue(state["coverage_complete"])
        self.assertEqual(previous_text, '{"message":"previous"}\n')

    def test_language_matrix_and_triggers(self):
        cases = (
            (
                ["src/app.ts", "README.md"],
                ["typescript"],
                {"knip", "jscpd", "markdownlint-cli2", "lizard", "semgrep"},
                set(),
            ),
            (
                ["src/app.py"],
                ["python"],
                {"jscpd", "lizard", "vulture", "semgrep"},
                {"knip"},
            ),
            (
                ["main.go", "migrations/001.sql"],
                ["go"],
                {"jscpd", "lizard", "semgrep", "deadcode", "gocyclo", "dupl"},
                {"vulture", "cargo-machete"},
            ),
            (
                ["src/lib.rs"],
                ["rust"],
                {"jscpd", "lizard", "semgrep", "cargo-machete"},
                {"knip", "deadcode"},
            ),
        )
        for files, languages, expected, absent in cases:
            with self.subTest(languages=languages), tempfile.TemporaryDirectory() as tmp:
                repo = Path(tmp)
                scope = _write_scope(repo, files, languages)
                bin_dir = repo / "bin"
                _shims(bin_dir)
                result, plan = _plan(repo, scope, bin_dir)
                wanted = _names(plan, "available") | _names(plan, "missing")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(expected <= wanted)
                self.assertTrue(absent.isdisjoint(wanted))

    def test_configured_tools_require_a_relevant_changed_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _touch(repo, "api-extractor.json", "{}\n")
            _touch(repo, ".vale.ini", "StylesPath = styles\n")
            scope = _write_scope(repo, ["README.md"], ["markdown"])
            bin_dir = repo / "bin"
            _shims(bin_dir)
            result, plan = _plan(repo, scope, bin_dir)
            wanted = _names(plan, "available") | _names(plan, "missing")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("api-extractor", wanted)
        self.assertIn("vale", wanted)

    def test_npx_and_uvx_do_not_resolve_analyzers(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope = _write_scope(
                repo, ["src/app.ts", "src/app.py"], ["typescript", "python"]
            )
            bin_dir = repo / "bin"
            _shim(bin_dir, "npx")
            _shim(bin_dir, "uvx")
            result, plan = _plan(repo, scope, bin_dir)
        self.assertEqual(result.returncode, 3)
        self.assertIn("knip", _names(plan, "missing"))
        self.assertIn("vulture", _names(plan, "missing"))
        self.assertEqual(_names(plan, "available"), set())


class TestPreflightAndResolution(unittest.TestCase):
    def test_missing_analyzer_blocks_without_executing_install_guidance(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope = _write_scope(repo, ["spec/openapi.yaml"], ["yaml"])
            marker = repo / "brew-ran"
            bin_dir = repo / "bin"
            _shim(bin_dir, "brew", f"touch {shlex.quote(str(marker))}")
            result = _run_battery(repo, scope, bin_dir=bin_dir)
            state = json.loads(scope.read_text(encoding="utf-8"))
            plan = json.loads((repo / "out" / "tool-preflight.json").read_text())
        self.assertEqual(result.returncode, 3)
        self.assertFalse(marker.exists())
        self.assertEqual(_names(plan, "missing"), {"oasdiff"})
        self.assertEqual({entry["tool"] for entry in state["tools_missing"]}, {"oasdiff"})
        self.assertFalse(state["tool_coverage"]["complete"])

    def test_preflight_command_reports_the_same_missing_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope = _write_scope(repo, ["src/app.py"], ["python"])
            bin_dir = repo / "bin"
            env = _env(bin_dir)
            dry, plan = _plan(repo, scope, bin_dir)
            result = subprocess.run(
                ["bash", str(PREFLIGHT), "--scope", str(scope), "--repo", str(repo)],
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )
        self.assertEqual(dry.returncode, 3)
        self.assertEqual(result.returncode, 3)
        for tool in _names(plan, "missing"):
            self.assertIn(tool, result.stdout)
        self.assertIn("BLOCKED:", result.stdout)

    def test_declared_npm_analyzer_executes_without_installing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _touch(repo, "README.md", "# Title\n")
            _touch(
                repo,
                "package.json",
                json.dumps({"devDependencies": {"markdownlint-cli2": "1.0.0"}}),
            )
            _touch(repo, "package-lock.json", "{}\n")
            binary = repo / "node_modules" / ".bin" / "markdownlint-cli2"
            analyzer_log = repo / "analyzer.log"
            _shim(
                binary.parent,
                binary.name,
                f'printf "%s\\n" "$*" >> {shlex.quote(str(analyzer_log))}',
            )
            manager_log = repo / "npm.log"
            bin_dir = repo / "bin"
            _shim(
                bin_dir,
                "npm",
                f'printf "%s\\n" "$*" >> {shlex.quote(str(manager_log))}\nexit 1',
            )
            scope = _write_scope(repo, ["README.md"], ["markdown"])
            result = _run_battery(
                repo, scope, bin_dir=bin_dir, axes="documentation"
            )
            state = json.loads(scope.read_text(encoding="utf-8"))
            invocation = analyzer_log.read_text(encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--config", invocation)
        self.assertFalse(manager_log.exists())
        self.assertEqual(state["tool_coverage"]["executed"], ["markdownlint-cli2"])
        self.assertTrue(state["tool_coverage"]["complete"])

    def test_markdown_only_repo_gets_path_install_guidance(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope = _write_scope(repo, ["README.md"], ["markdown"])
            result, plan = _plan(repo, scope, repo / "bin", axes="documentation")
        self.assertEqual(result.returncode, 3)
        self.assertEqual(_names(plan, "missing"), {"markdownlint-cli2"})
        self.assertIn("on PATH", plan["missing"][0]["install"])
        self.assertNotIn("npm install", plan["missing"][0]["install"])

    def test_preflight_available_set_equals_executed_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope = _write_scope(repo, ["README.md"], ["markdown"])
            bin_dir = repo / "bin"
            _shim(bin_dir, "markdownlint-cli2")
            dry, plan = _plan(repo, scope, bin_dir, axes="documentation")
            result = _run_battery(
                repo, scope, bin_dir=bin_dir, axes="documentation"
            )
            state = json.loads(scope.read_text(encoding="utf-8"))
        self.assertEqual(dry.returncode, 0, dry.stderr)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            _names(plan, "available"), set(state["tool_coverage"]["executed"])
        )
        self.assertEqual(
            set(state["tool_coverage"]["applicable"]),
            set(state["tool_coverage"]["executed"]),
        )

    def test_preflight_recomputes_js_scope_for_each_analyzer(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _touch(repo, "packages/app/src/app.ts", "export const value = 1;\n")
            _touch(repo, "packages/docs/README.md", "# Docs\n")
            _touch(
                repo,
                "packages/app/package.json",
                json.dumps({"devDependencies": {"knip": "1.0.0"}}),
            )
            _touch(
                repo,
                "packages/docs/package.json",
                json.dumps({"devDependencies": {"markdownlint-cli2": "1.0.0"}}),
            )
            _shim(repo / "packages/app/node_modules/.bin", "knip")
            _shim(
                repo / "packages/docs/node_modules/.bin", "markdownlint-cli2"
            )
            bin_dir = repo / "bin"
            _shim(bin_dir, "jscpd")
            _shim(bin_dir, "lizard")
            scope = _write_scope(
                repo,
                ["packages/app/src/app.ts", "packages/docs/README.md"],
                ["typescript"],
            )
            result, plan = _plan(
                repo, scope, bin_dir, axes="simplification,documentation"
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            _names(plan, "available"),
            {"knip", "jscpd", "markdownlint-cli2", "lizard"},
        )
        self.assertEqual(_names(plan, "missing"), set())


class TestAnalyzerExecution(unittest.TestCase):
    def test_findings_exit_requires_at_least_one_parsed_finding(self):
        for tool in (
            "knip", "jscpd", "markdownlint-cli2", "api-extractor",
            "vulture", "semgrep", "vale", "oasdiff", "atlas", "gocyclo",
            "cargo-machete",
        ):
            with self.subTest(tool=tool), tempfile.TemporaryDirectory() as tmp:
                repo = Path(tmp)
                scope, bin_dir, axes = _findings_exit_without_finding_case(repo, tool)
                result = _run_battery(repo, scope, bin_dir=bin_dir, axes=axes)
                state = json.loads(scope.read_text(encoding="utf-8"))
                self.assertEqual(result.returncode, 4, result.stderr)
                if tool == "atlas":
                    self.assertIn("checksum mismatch", result.stderr)
                else:
                    self.assertIn("parsed report contains no findings", result.stderr)
                self.assertFalse(state["tool_coverage"]["complete"])

    def test_markdownlint_real_text_shape_is_ingested_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope = _write_scope(repo, ["README.md"], ["markdown"])
            bin_dir = repo / "bin"
            _shim(
                bin_dir,
                "markdownlint-cli2",
                "echo 'markdownlint-cli2 v0.23.2 (markdownlint v0.41.1)'\n"
                "echo 'README.md:1 error MD022/blanks-around-headings "
                "Headings should be surrounded by blank lines' >&2\nexit 1",
            )
            result = _run_battery(
                repo, scope, bin_dir=bin_dir, axes="documentation"
            )
            finding = json.loads((repo / "out/tool-findings.jsonl").read_text())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(finding["source_tool"], "markdownlint-cli2")
        self.assertEqual(finding["file"], "README.md")

    def test_atlas_diagnostic_findings_exit_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _touch(repo, "atlas.hcl")
            scope = _write_scope(repo, ["migrations/001.sql"], ["sql"])
            report = json.dumps({"Files": [{
                "Name": "migrations/001.sql", "Reports": [{"Diagnostics": [{
                    "Pos": 1, "Text": "Adding NOT NULL column without default",
                    "Code": "MF101"}]}]}]})
            _shim(repo / "bin", "atlas", f"printf '%s\\n' {shlex.quote(report)}\nexit 1")
            result = _run_battery(repo, scope, bin_dir=repo / "bin", axes="design-api")
            finding = json.loads((repo / "out/tool-findings.jsonl").read_text())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(finding["source_tool"], "atlas")

    def test_markdownlint_semantic_failure_preserves_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope = _write_scope(repo, ["README.md"], ["markdown"])
            _shim(
                repo / "bin", "markdownlint-cli2",
                "printf '%s' 'unexpected markdownlint output'\n"
                "printf '%s' 'config diagnostic' >&2",
            )
            result = _run_battery(
                repo, scope, bin_dir=repo / "bin", axes="documentation"
            )
            state = json.loads(scope.read_text(encoding="utf-8"))
            raw = repo / "out/raw"
            self.assertEqual([(raw / name).read_text() for name in
                              ("markdownlint-cli2.txt", "markdownlint-cli2.stderr")],
                             ["unexpected markdownlint output", "config diagnostic"])
        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertFalse(state["tool_coverage"]["complete"])

    def test_markdownlint_runs_once_with_the_base_config_and_repo_relative_paths(self):
        # markdownlint-cli2 layers .markdownlint-cli2.* / .markdownlint.* found in
        # the repository tree on top of --config, so nested project configs keep
        # precedence without a second invocation (verified against 0.23.2).
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _touch(repo, "packages/docs/.markdownlint.jsonc", '{"MD041": false}\n')
            files = ["README.md", "packages/docs/guide.md"]
            scope = _write_scope(repo, files, ["markdown"])
            bin_dir = repo / "bin"
            log = repo / "invocations.log"
            _shim(bin_dir, "markdownlint-cli2",
                  f'{{ printf "cwd=%s\\n" "$PWD"; printf "arg=%s\\n" "$@"; printf "end\\n"; }} >> {shlex.quote(str(log))}\nexit 0')
            result = _run_battery(repo, scope, bin_dir=bin_dir, axes="documentation")
            invocations = [block for block in log.read_text().split("end\n") if block]
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(invocations), 1, invocations)
        base_config = (BATTERY.parent / "../references/markdownlint-base.markdownlint-cli2.jsonc")
        self.assertIn(f"cwd={repo.resolve()}", invocations[0])
        self.assertIn(f"arg=--config\narg={base_config}", invocations[0])
        for relative in files:
            self.assertIn(f"arg={relative}\n", invocations[0])

    def test_non_js_repo_gets_path_guidance_for_every_js_analyzer(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope = _write_scope(repo, ["src/main.rs", "README.md"], ["rust", "markdown"])
            result, plan = _plan(repo, scope, repo / "bin")
        self.assertEqual(result.returncode, 3)
        self.assertTrue({"jscpd", "markdownlint-cli2"} <= _names(plan, "missing"))
        for entry in plan["missing"]:
            if entry["tool"] in {"jscpd", "markdownlint-cli2"}:
                self.assertIn("on PATH", entry["install"])
                self.assertNotIn("npm install", entry["install"])

    def test_markdownlint_crash_blocks_and_invalidates_previous_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope = _write_scope(repo, ["README.md"], ["markdown"])
            output = repo / "out"
            bin_dir = repo / "bin"
            analyzer = _shim(
                bin_dir,
                "markdownlint-cli2",
                'printf "%s:1 MD013 line too long\\n" "$PWD/README.md"\nexit 1',
            )
            passed = _run_battery(
                repo, scope, bin_dir=bin_dir, output_dir=output,
                axes="documentation",
            )
            self.assertEqual(passed.returncode, 0, passed.stderr)
            final = output / "tool-findings.jsonl"
            self.assertTrue(final.is_file())

            analyzer.write_text(
                "#!/bin/bash\nprintf '%s' 'partial analyzer output'\n"
                "printf '%s' 'Cannot find module markdownlint' >&2\nexit 2\n",
                encoding="utf-8",
            )
            analyzer.chmod(analyzer.stat().st_mode | stat.S_IEXEC)
            failed = _run_battery(
                repo, scope, bin_dir=bin_dir, output_dir=output,
                axes="documentation",
            )
            state = json.loads(scope.read_text(encoding="utf-8"))
            raw = output / "raw"
            self.assertEqual([(raw / name).read_text() for name in
                              ("markdownlint-cli2.txt", "markdownlint-cli2.stderr")],
                             ["partial analyzer output", "Cannot find module markdownlint"])
            self.assertFalse(final.exists())
        self.assertEqual(failed.returncode, 4)
        self.assertIn("failed with exit code 2", failed.stderr)
        self.assertFalse(state["tool_coverage"]["complete"])
        self.assertFalse(state["coverage_complete"])

    def test_go_analyzers_use_supported_offline_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope = _write_scope(repo, ["main.go"], ["go"])
            trace = repo / "trace.log"
            bin_dir = repo / "bin"
            _jscpd_empty(bin_dir)
            _shim(bin_dir, "lizard")
            for tool, rc in (("deadcode", 0), ("gocyclo", 0)):
                _shim(
                    bin_dir,
                    tool,
                    f'printf "{tool}|%s|%s|%s|%s\\n" "$GOFLAGS" "$GOPROXY" '
                    f'"$GOTOOLCHAIN" "$*" >> {shlex.quote(str(trace))}\nexit {rc}',
                )
            _shim(
                bin_dir,
                "dupl",
                f'printf "dupl|%s|%s|%s|%s\\n" "$GOFLAGS" "$GOPROXY" '
                f'"$GOTOOLCHAIN" "$*" >> {shlex.quote(str(trace))}\n'
                "printf '\\nFound total 0 clone groups.\\n'",
            )
            result = _run_battery(
                repo,
                scope,
                bin_dir=bin_dir,
                axes="simplification",
            )
            state = json.loads(scope.read_text(encoding="utf-8"))
            lines = trace.read_text(encoding="utf-8").splitlines()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            set(state["tool_coverage"]["executed"]),
            {"jscpd", "lizard", "deadcode", "gocyclo", "dupl"},
        )
        self.assertIn("deadcode|-mod=readonly|off|local|./...", lines)
        self.assertIn("gocyclo|-mod=readonly|off|local|-over 10 .", lines)
        self.assertIn("dupl|-mod=readonly|off|local|-t 50 .", lines)

    def test_semgrep_runs_offline_against_changed_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope = _write_scope(repo, ["src/app.py"], ["python"])
            trace = repo / "semgrep.log"
            bin_dir = repo / "bin"
            _shim(
                bin_dir,
                "semgrep",
                f'printf "%s|%s\\n" "$SEMGREP_LOG_FILE" "$*" > '
                f'{shlex.quote(str(trace))}\nprintf \'{{"results":[],"errors":[]}}\\n\'',
            )
            result = _run_battery(
                repo, scope, bin_dir=bin_dir, axes="performance"
            )
            line = trace.read_text(encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(str(repo / "out" / "raw" / "semgrep.log"), line)
        self.assertIn("--metrics=off", line)
        self.assertIn("--disable-version-check", line)
        self.assertIn("--no-rewrite-rule-ids", line)
        self.assertIn("./src/app.py", line)
        self.assertNotIn("--config=auto", line)

    def test_semgrep_report_errors_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope = _write_scope(repo, ["src/app.py"], ["python"])
            bin_dir = repo / "bin"
            _shim(
                bin_dir,
                "semgrep",
                "printf '{\"results\":[],\"errors\":[{\"message\":\"parse failed\"}]}\\n'",
            )
            result = _run_battery(
                repo, scope, bin_dir=bin_dir, axes="performance"
            )
        self.assertEqual(result.returncode, 4)
        self.assertIn("Semgrep reported analyzer errors", result.stderr)

    def test_semgrep_warning_does_not_block_complete_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope = _write_scope(repo, ["src/app.py"], ["python"])
            bin_dir = repo / "bin"
            _shim(
                bin_dir,
                "semgrep",
                "printf '{\"results\":[],\"errors\":[{\"level\":\"warn\","
                "\"message\":\"partial parse\"}]}\\n'",
            )
            result = _run_battery(
                repo, scope, bin_dir=bin_dir, axes="performance"
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("non-blocking analyzer warning", result.stderr)

    def test_cargo_machete_real_unused_dependency_shape_is_ingested(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope = _write_scope(repo, ["src/lib.rs", "Cargo.toml"], ["rust"])
            bin_dir = repo / "bin"
            _jscpd_empty(bin_dir)
            _shim(bin_dir, "lizard")
            _shim(
                bin_dir,
                "cargo-machete",
                "printf 'cargo-machete found the following unused dependencies "
                "in this directory:\\nrustfix -- ./Cargo.toml:\\n\\tserde\\n\\n"
                "If you believe cargo-machete detected this incorrectly.\\n'\nexit 1",
            )
            result = _run_battery(
                repo, scope, bin_dir=bin_dir, axes="simplification"
            )
            findings = [json.loads(line) for line in
                        (repo / "out/tool-findings.jsonl").read_text().splitlines()]
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(any(item["source_tool"] == "cargo-machete" for item in findings))

    def test_final_findings_publish_failure_keeps_coverage_incomplete(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope = _write_scope(repo, ["src/app.py"], ["python"])
            bin_dir = repo / "bin"
            _shim(
                bin_dir,
                "semgrep",
                "printf '{\"results\":[],\"errors\":[]}\\n'",
            )
            _shim(
                bin_dir,
                "mv",
                'last=""\nfor arg in "$@"; do last="$arg"; done\n'
                'case "$last" in *tool-findings.jsonl) exit 1;; esac\n'
                'exec /bin/mv "$@"',
            )
            result = _run_battery(
                repo, scope, bin_dir=bin_dir, axes="performance"
            )
            state = json.loads(scope.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 4)
        self.assertIn("could not be published atomically", result.stderr)
        self.assertFalse((repo / "out" / "tool-findings.jsonl").exists())
        self.assertFalse(state["tool_coverage"]["complete"])


class TestPhaseChain(unittest.TestCase):
    def test_scope_battery_axes_and_synthesis_complete_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            _touch(repo, "README.md", "# Initial\n")
            subprocess.run(["git", "-C", str(repo), "add", "README.md"], check=True)
            subprocess.run(
                [
                    "git", "-C", str(repo), "-c", "user.name=Test",
                    "-c", "user.email=test@example.com",
                    "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
                    "commit", "-qm", "initial",
                ],
                check=True,
            )
            _touch(repo, "README.md", "# Changed\n")
            scope_path = repo / "scope.json"
            scoped = subprocess.run(
                [sys.executable, str(SCOPE), "--dirty-tree", "--repo", str(repo)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(scoped.returncode, 0, scoped.stderr)
            scope_path.write_text(scoped.stdout, encoding="utf-8")

            bin_dir = repo / "bin"
            _shim(bin_dir, "markdownlint-cli2")
            output = repo / "run"
            battery = _run_battery(
                repo, scope_path, bin_dir=bin_dir, output_dir=output,
                axes="documentation",
            )
            self.assertEqual(battery.returncode, 0, battery.stderr)

            diff_path = output / "diff.patch"
            diff = subprocess.run(
                ["git", "-C", str(repo), "diff", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
            diff_path.write_text(diff.stdout, encoding="utf-8")
            prepared = subprocess.run(
                [
                    sys.executable, str(AXES), "prepare", "--scope", str(scope_path),
                    "--findings", str(output / "tool-findings.jsonl"), "--diff",
                    str(diff_path), "--output-dir", str(output), "--axes", "documentation",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            run_id = json.loads(prepared.stdout)["run_id"]
            results = output / "axis-results"
            results.mkdir()
            (results / "documentation.jsonl").write_text(
                json.dumps({
                    "run_id": run_id,
                    "axis": "documentation",
                    "no_findings": True,
                }) + "\n",
                encoding="utf-8",
            )
            axis_findings = output / "axis-findings.jsonl"
            ingested = subprocess.run(
                [
                    sys.executable, str(AXES), "ingest", "--scope", str(scope_path),
                    "--results-dir", str(results), "--output", str(axis_findings),
                    "--axes", "documentation",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(ingested.returncode, 0, ingested.stderr)
            synthesized = subprocess.run(
                [
                    sys.executable, str(SYNTHESIZE), "--scope", str(scope_path),
                    "--findings", str(axis_findings), "--tool-findings",
                    str(output / "tool-findings.jsonl"), "--output-dir",
                    str(output / "report"),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(synthesized.returncode, 0, synthesized.stderr)
        self.assertIn("**Scoped findings only**", synthesized.stdout)


if __name__ == "__main__":
    unittest.main()
