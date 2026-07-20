"""Tests for skills/code-ultrareview/scripts/run_battery.sh.

Cover per-language dispatch, trigger-based dispatch (api-extractor, oasdiff,
atlas, vale), atomic failure for missing tools, the no-auto-install contract,
and README ↔ dispatch parity (no drift between the script's
BATTERY_TABLE and the README's tool table).

Tests use a controlled PATH via tmpdir shims rather than the host's installed
tools, so the suite is hermetic across contributor machines.
"""

from __future__ import annotations

import json
import os
import re
import stat
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "skills" / "code-ultrareview" / "scripts" / "run_battery.sh"
PREFLIGHT = REPO_ROOT / "skills" / "code-ultrareview" / "scripts" / "preflight_tools.sh"
INSTALL_GUIDANCE = (
    REPO_ROOT / "skills" / "code-ultrareview" / "scripts" / "install-guidance.sh"
)
README = REPO_ROOT / "README.md"

# All tools known to the dispatch matrix. Mirrors BATTERY_TABLE in the script.
ALL_TOOLS = [
    "knip", "jscpd", "markdownlint-cli2", "api-extractor",
    "lizard", "vulture", "semgrep", "vale",
    "oasdiff", "atlas", "deadcode", "gocyclo", "dupl", "cargo-machete",
]


def _make_shim(bin_dir: Path, name: str, body: str = "exit 0") -> Path:
    """Write an executable bash shim at <bin_dir>/<name>."""
    bin_dir.mkdir(parents=True, exist_ok=True)
    p = bin_dir / name
    p.write_text(f"#!/usr/bin/env bash\n{body}\n", encoding="utf-8")
    p.chmod(p.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return p


def _write_scope(path: Path, **overrides) -> None:
    """Write a minimal scope.json. Pass any field as kwarg to override."""
    defaults = {
        "base": "main",
        "target": "HEAD",
        "rule": "test",
        "dirty_tree": False,
        "repo_kind": "app",
        "repo_kind_signals": {},
        "languages": [],
        "instruction_chain": [],
        "loc_changed": 0,
        "files_touched": 0,
        "files_touched_list": [],
        "activates_coherence": False,
        "tools_skipped": [],
    }
    defaults.update(overrides)
    path.write_text(json.dumps(defaults, indent=2), encoding="utf-8")
    for relative in defaults["files_touched_list"]:
        touched = path.parent / relative
        if not touched.exists():
            touched.parent.mkdir(parents=True, exist_ok=True)
            touched.write_text(
                "{}\n" if relative == "package.json" else "",
                encoding="utf-8",
            )


def _run_dry(scope: Path, repo: Path, bin_dir: Path | None = None) -> dict:
    """Run the script in --dry-run mode under the given controlled PATH.

    The shim bin dir is appended to a minimal base PATH so basic shell
    commands (cd, mktemp, etc.) still resolve.
    """
    base_path = "/usr/bin:/bin:/usr/local/bin"
    env = os.environ.copy()
    if bin_dir is not None:
        env["PATH"] = f"{bin_dir}:{base_path}"
    else:
        env["PATH"] = base_path
    with tempfile.TemporaryDirectory() as td:
        out_dir = Path(td) / "out"
        r = subprocess.run(
            ["bash", str(SCRIPT),
             "--scope", str(scope),
             "--output-dir", str(out_dir),
             "--repo", str(repo),
             "--dry-run"],
            capture_output=True, text=True, env=env, check=False,
        )
    if r.returncode not in (0, 3):
        raise AssertionError(f"run_battery --dry-run failed ({r.returncode})\n"
                             f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}")
    return json.loads(r.stdout)


def _dispatched_tools(plan: dict) -> set[str]:
    return {e["tool"] for e in plan.get("available", [])}


def _skipped_tools(plan: dict) -> set[str]:
    return {e["tool"] for e in plan.get("missing", [])}


def _wanted_tools(plan: dict) -> set[str]:
    """Union — both dispatched (available) and skipped (missing) were wanted."""
    return _dispatched_tools(plan) | _skipped_tools(plan)


# ---------------------------------------------------------------------------
# Input integrity.
# ---------------------------------------------------------------------------


class TestInputIntegrity(unittest.TestCase):
    def _run(self, repo: Path, scope: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                "bash",
                str(SCRIPT),
                "--scope",
                str(scope),
                "--output-dir",
                str(repo / "out"),
                "--repo",
                str(repo),
                "--dry-run",
            ],
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "PATH": "/usr/bin:/bin:/usr/local/bin"},
        )

    def test_malformed_scope_fails_without_traceback_and_prints_rerun(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            scope = repo / "scope.json"
            scope.write_text("{broken\n", encoding="utf-8")

            result = self._run(repo, scope)

        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid Code Ultrareview scope", result.stderr)
        self.assertIn("rerun scope.py", result.stderr)
        self.assertIn("ERROR: rerun:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_mistyped_scope_manifest_fails_before_dispatch(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            scope = repo / "scope.json"
            _write_scope(scope, tool_coverage="complete")

            result = self._run(repo, scope)

        self.assertEqual(result.returncode, 2)
        self.assertIn("tool_coverage must be an object", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_invalid_changed_line_ranges_fail_before_dispatch(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            scope = repo / "scope.json"
            _write_scope(
                scope,
                languages=["python"],
                files_touched_list=["src/app.py"],
                changed_line_ranges={"src/app.py": [[0, 4]]},
            )

            result = self._run(repo, scope)

        self.assertEqual(result.returncode, 2)
        self.assertIn("positive [start, end] pairs", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_invalid_jscpd_thresholds_fail_before_dispatch(self):
        for variable in ("JSCPD_MIN_LINES", "JSCPD_MIN_TOKENS"):
            with self.subTest(variable=variable), tempfile.TemporaryDirectory() as td:
                repo = Path(td)
                scope = repo / "scope.json"
                _write_scope(scope)
                result = subprocess.run(
                    [
                        "bash",
                        str(SCRIPT),
                        "--scope",
                        str(scope),
                        "--output-dir",
                        str(repo / "out"),
                        "--repo",
                        str(repo),
                        "--dry-run",
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                    env={
                        **os.environ,
                        "PATH": "/usr/bin:/bin:/usr/local/bin",
                        variable: "0",
                    },
                )

            self.assertEqual(result.returncode, 2)
            self.assertIn(f"{variable} must be a positive integer", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_invalid_package_json_never_falls_back_to_global_analyzers(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            scope = repo / "scope.json"
            _write_scope(
                scope,
                languages=["typescript"],
                files_touched_list=["src/foo.ts"],
            )
            (repo / "package.json").write_text("{broken\n", encoding="utf-8")
            bin_dir = repo / "bin"
            _make_shim(bin_dir, "knip")

            result = subprocess.run(
                [
                    "bash",
                    str(SCRIPT),
                    "--scope",
                    str(scope),
                    "--output-dir",
                    str(repo / "out"),
                    "--repo",
                    str(repo),
                    "--dry-run",
                ],
                capture_output=True,
                text=True,
                check=False,
                env={
                    **os.environ,
                    "PATH": f"{bin_dir}:/usr/bin:/bin:/usr/local/bin",
                },
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid project manifest", result.stderr)
        self.assertIn("repair package.json", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


# ---------------------------------------------------------------------------
# Dispatch — per language / repo kind.
# ---------------------------------------------------------------------------


class TestDispatchPerLanguage(unittest.TestCase):
    """AC: Per-language dispatch reads scope.json[languages] and routes the
    expected tool subset."""

    def test_typescript_repo_dispatches_js_tools(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            scope = tdp / "scope.json"
            _write_scope(scope, repo_kind="app", languages=["typescript"],
                         files_touched_list=["src/foo.ts", "README.md"])
            bin_dir = tdp / "bin"
            for tool in ALL_TOOLS:
                _make_shim(bin_dir, tool)
            plan = _run_dry(scope, tdp, bin_dir)
            wanted = _wanted_tools(plan)
            self.assertIn("knip", wanted)
            self.assertIn("jscpd", wanted)
            self.assertIn("markdownlint-cli2", wanted)  # README.md in diff
            self.assertNotIn("vulture", wanted)
            self.assertNotIn("cargo-machete", wanted)
            self.assertNotIn("deadcode", wanted)

    def test_python_repo_dispatches_python_tools(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            scope = tdp / "scope.json"
            _write_scope(scope, repo_kind="python", languages=["python"],
                         files_touched_list=["src/foo.py"])
            bin_dir = tdp / "bin"
            for tool in ALL_TOOLS:
                _make_shim(bin_dir, tool)
            plan = _run_dry(scope, tdp, bin_dir)
            wanted = _wanted_tools(plan)
            self.assertIn("lizard", wanted)
            self.assertIn("vulture", wanted)
            self.assertIn("semgrep", wanted)
            self.assertIn("jscpd", wanted)  # cross-language
            self.assertNotIn("knip", wanted)  # no JS/TS in scope
            self.assertNotIn("deadcode", wanted)

    def test_go_repo_dispatches_go_tools(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            scope = tdp / "scope.json"
            _write_scope(scope, repo_kind="go", languages=["go"],
                         files_touched_list=["main.go"])
            bin_dir = tdp / "bin"
            for tool in ALL_TOOLS:
                _make_shim(bin_dir, tool)
            plan = _run_dry(scope, tdp, bin_dir)
            wanted = _wanted_tools(plan)
            self.assertIn("deadcode", wanted)
            self.assertIn("gocyclo", wanted)
            self.assertIn("dupl", wanted)
            self.assertIn("jscpd", wanted)
            self.assertIn("lizard", wanted)
            self.assertNotIn("vulture", wanted)

    def test_rust_repo_dispatches_rust_tools(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            scope = tdp / "scope.json"
            _write_scope(scope, repo_kind="rust", languages=["rust"],
                         files_touched_list=["src/lib.rs"])
            bin_dir = tdp / "bin"
            for tool in ALL_TOOLS:
                _make_shim(bin_dir, tool)
            plan = _run_dry(scope, tdp, bin_dir)
            wanted = _wanted_tools(plan)
            self.assertIn("cargo-machete", wanted)
            self.assertIn("lizard", wanted)
            self.assertIn("jscpd", wanted)
            self.assertNotIn("knip", wanted)


class TestDispatchPerTrigger(unittest.TestCase):
    """AC: Trigger-based dispatch for api-extractor (api-extractor.json present),
    oasdiff (OpenAPI in diff), atlas (migrations/ in diff), vale (.vale.ini)."""

    def _shim_all(self, bin_dir: Path) -> None:
        for tool in ALL_TOOLS:
            _make_shim(bin_dir, tool)

    def test_api_extractor_only_when_config_present(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            scope = tdp / "scope.json"
            _write_scope(scope, languages=["typescript"],
                         files_touched_list=["package.json", "src/foo.ts"])
            bin_dir = tdp / "bin"
            self._shim_all(bin_dir)
            plan = _run_dry(scope, tdp, bin_dir)
            self.assertNotIn("api-extractor", _wanted_tools(plan))
            (tdp / "api-extractor.json").write_text("{}")
            plan2 = _run_dry(scope, tdp, bin_dir)
            self.assertIn("api-extractor", _wanted_tools(plan2))

    def test_oasdiff_triggers_on_openapi_in_diff(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            scope = tdp / "scope.json"
            _write_scope(scope, languages=["typescript"],
                         files_touched_list=["spec/openapi.yaml"])
            bin_dir = tdp / "bin"
            self._shim_all(bin_dir)
            plan = _run_dry(scope, tdp, bin_dir)
            self.assertIn("oasdiff", _wanted_tools(plan))

    def test_atlas_triggers_on_migrations_in_diff(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            scope = tdp / "scope.json"
            _write_scope(scope, languages=["go"],
                         files_touched_list=["migrations/001.sql"])
            (tdp / "atlas.hcl").write_text("env \"local\" {}\n")
            bin_dir = tdp / "bin"
            self._shim_all(bin_dir)
            plan = _run_dry(scope, tdp, bin_dir)
            self.assertIn("atlas", _wanted_tools(plan))

    def test_vale_only_when_vale_ini_present(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            scope = tdp / "scope.json"
            _write_scope(scope, languages=["typescript"],
                         files_touched_list=["docs/guide.md"])
            bin_dir = tdp / "bin"
            self._shim_all(bin_dir)
            plan = _run_dry(scope, tdp, bin_dir)
            self.assertNotIn("vale", _wanted_tools(plan))
            (tdp / ".vale.ini").write_text("StylesPath = styles\n")
            plan2 = _run_dry(scope, tdp, bin_dir)
            self.assertIn("vale", _wanted_tools(plan2))

    def test_deleted_markdown_is_not_dispatched_to_markdownlint(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            scope = tdp / "scope.json"
            _write_scope(
                scope,
                languages=[],
                files_touched_list=["docs/deleted.md"],
            )
            (tdp / "docs" / "deleted.md").unlink()
            bin_dir = tdp / "bin"
            _make_shim(bin_dir, "markdownlint-cli2")
            plan = _run_dry(scope, tdp, bin_dir)
        self.assertNotIn("markdownlint-cli2", _wanted_tools(plan))


# ---------------------------------------------------------------------------
# Tool resolution — project binaries first, then PATH; resolvers are ignored.
# ---------------------------------------------------------------------------


class TestToolResolution(unittest.TestCase):
    """The battery never downloads a missing tool during a review."""

    def test_npx_only_does_not_dispatch_js_tools(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            scope = tdp / "scope.json"
            _write_scope(scope, repo_kind="app", languages=["typescript"],
                         files_touched_list=["src/foo.ts", "README.md"])
            bin_dir = tdp / "bin"
            _make_shim(bin_dir, "npx")
            plan = _run_dry(scope, tdp, bin_dir)
            skipped = _skipped_tools(plan)
            for tool in ("knip", "jscpd", "markdownlint-cli2"):
                self.assertIn(tool, skipped)

    def test_uvx_only_does_not_dispatch_python_tools(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            scope = tdp / "scope.json"
            _write_scope(scope, repo_kind="python", languages=["python"],
                         files_touched_list=["src/foo.py"])
            bin_dir = tdp / "bin"
            _make_shim(bin_dir, "uvx")
            plan = _run_dry(scope, tdp, bin_dir)
            skipped = _skipped_tools(plan)
            for tool in ("lizard", "vulture", "semgrep"):
                self.assertIn(tool, skipped)

    def test_project_binary_precedes_path(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            scope = tdp / "scope.json"
            _write_scope(scope, repo_kind="app", languages=["typescript"],
                         files_touched_list=["src/foo.ts"])
            _make_shim(tdp / "node_modules" / ".bin", "knip")
            (tdp / "package.json").write_text(
                '{"devDependencies":{"knip":"1.0.0"}}\n', encoding="utf-8"
            )
            path_bin = tdp / "path-bin"
            _make_shim(path_bin, "knip")
            plan = _run_dry(scope, tdp, path_bin)
            dispatched = {e["tool"]: e["wrapper"] for e in plan["available"]}
            self.assertEqual(dispatched.get("knip"), "project")

    def test_declared_missing_project_binary_never_falls_back_to_path(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            scope = repo / "scope.json"
            _write_scope(
                scope,
                languages=["markdown"],
                files_touched_list=["README.md"],
            )
            (repo / "package.json").write_text(
                '{"devDependencies":{"markdownlint-cli2":"0.18.1"}}\n',
                encoding="utf-8",
            )
            bin_dir = repo / "bin"
            _make_shim(bin_dir, "markdownlint-cli2")

            plan = _run_dry(scope, repo, bin_dir)

        self.assertIn("markdownlint-cli2", _skipped_tools(plan))
        self.assertNotIn("markdownlint-cli2", _dispatched_tools(plan))

    def test_declared_yarn_pnp_binary_dispatches_without_node_modules(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            scope = tdp / "scope.json"
            _write_scope(
                scope,
                repo_kind="app",
                languages=["typescript"],
                files_touched_list=["src/foo.ts"],
            )
            (tdp / "package.json").write_text(
                '{"packageManager":"yarn@4.9.2",'
                '"devDependencies":{"knip":"5.61.2"}}\n',
                encoding="utf-8",
            )
            (tdp / "yarn.lock").write_text("", encoding="utf-8")
            bin_dir = tdp / "bin"
            _make_shim(
                bin_dir,
                "yarn",
                '[[ "${COREPACK_ENABLE_NETWORK-}" == "0" ]] || exit 66\n'
                '[[ "${COREPACK_DEFAULT_TO_LATEST-}" == "0" ]] || exit 67\n'
                'if [[ "$3" == "bin" && "$4" == "knip" ]]; then\n'
                '  printf "/virtual/.yarn/knip\\n"\n'
                "  exit 0\n"
                "fi\n"
                "exit 64",
            )

            plan = _run_dry(scope, tdp, bin_dir)

            dispatched = {e["tool"]: e["wrapper"] for e in plan["available"]}
            self.assertEqual(dispatched.get("knip"), "yarn-pnp")

    def test_yarn_pnp_binary_executes_through_yarn_run(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            scope = tdp / "scope.json"
            _write_scope(
                scope,
                repo_kind="app",
                languages=["typescript"],
                files_touched_list=["src/foo.ts"],
            )
            (tdp / "package.json").write_text(
                '{"packageManager":"yarn@4.9.2",'
                '"devDependencies":{"knip":"5.61.2","jscpd":"4.0.8"}}\n',
                encoding="utf-8",
            )
            (tdp / "yarn.lock").write_text("", encoding="utf-8")
            bin_dir = tdp / "bin"
            marker = tdp / "yarn-runs.log"
            _make_shim(
                bin_dir,
                "yarn",
                '[[ "${COREPACK_ENABLE_NETWORK-}" == "0" ]] || exit 66\n'
                '[[ "${COREPACK_DEFAULT_TO_LATEST-}" == "0" ]] || exit 67\n'
                'if [[ "$3" == "bin" ]]; then\n'
                '  case "$4" in knip|jscpd) exit 0 ;; esac\n'
                "  exit 1\n"
                "fi\n"
                'if [[ "$3" != "run" || "$4" != "-B" ]]; then exit 64; fi\n'
                f'printf "%s\\n" "$5" >> "{marker}"\n'
                'if [[ "$5" == "knip" ]]; then printf "[]\\n"; exit 0; fi\n'
                'if [[ "$5" == "jscpd" ]]; then\n'
                "  shift 5\n"
                "  out=\n"
                "  while [[ $# -gt 0 ]]; do\n"
                '    if [[ "$1" == "--output" ]]; then out="$2"; break; fi\n'
                "    shift\n"
                "  done\n"
                '  mkdir -p "$out"\n'
                '  printf "{\\\"duplicates\\\":[]}\\n" > "$out/jscpd-report.json"\n'
                "  exit 0\n"
                "fi\n"
                "exit 65",
            )
            _make_shim(
                bin_dir,
                "lizard",
                'printf "NLOC,CCN,token,PARAM,length,location\\n'
                '1,1,1,0,1,foo@1-1@src/foo.ts\\n"',
            )
            out_dir = tdp / "out"
            env = os.environ.copy()
            env["PATH"] = f"{bin_dir}:/usr/bin:/bin:/usr/local/bin"

            result = subprocess.run(
                [
                    "bash",
                    str(SCRIPT),
                    "--scope",
                    str(scope),
                    "--output-dir",
                    str(out_dir),
                    "--repo",
                    str(tdp),
                    "--axes",
                    "simplification",
                ],
                capture_output=True,
                text=True,
                env=env,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(marker.read_text(encoding="utf-8").splitlines(), ["knip", "jscpd"])
            plan = json.loads((out_dir / "tool-preflight.json").read_text())
            wrappers = {entry["tool"]: entry["wrapper"] for entry in plan["available"]}
            self.assertEqual(
                wrappers,
                {"knip": "yarn-pnp", "jscpd": "yarn-pnp", "lizard": "path"},
            )

    def test_undeclared_project_binary_does_not_shadow_path(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            scope = tdp / "scope.json"
            _write_scope(scope, repo_kind="app", languages=["typescript"],
                         files_touched_list=["src/foo.ts"])
            _make_shim(tdp / "node_modules" / ".bin", "knip")
            path_bin = tdp / "path-bin"
            _make_shim(path_bin, "knip")

            plan = _run_dry(scope, tdp, path_bin)

            dispatched = {e["tool"]: e["wrapper"] for e in plan["available"]}
            self.assertEqual(dispatched.get("knip"), "path")

    def test_path_binary_dispatches(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            scope = tdp / "scope.json"
            _write_scope(scope, repo_kind="python", languages=["python"],
                         files_touched_list=["src/foo.py"])
            bin_dir = tdp / "bin"
            _make_shim(bin_dir, "vulture")
            plan = _run_dry(scope, tdp, bin_dir)
            dispatched = {e["tool"]: e["wrapper"] for e in plan["available"]}
            self.assertEqual(dispatched.get("vulture"), "path")

    def test_source_has_no_runtime_package_resolver(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertNotRegex(text, r"\bnpx\b")
        self.assertNotRegex(text, r"\buvx\b")

    def test_project_binary_resolution_is_limited_to_javascript_tools(self):
        text = SCRIPT.read_text(encoding="utf-8")
        resolver = text.split("resolve_tool() {", 1)[1].split("\n}", 1)[0]
        for tool in ("knip", "jscpd", "markdownlint-cli2", "api-extractor"):
            self.assertIn(tool, resolver)
        for tool in ("lizard", "vulture", "semgrep"):
            self.assertNotIn(tool, resolver)


# ---------------------------------------------------------------------------
# Atomic preflight — no native tool, no wrapper means no review.
# ---------------------------------------------------------------------------


class TestAtomicPreflight(unittest.TestCase):
    """Missing applicable analyzers block before any analyzer executes."""

    def test_missing_oasdiff_blocks_with_exact_remediation(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            scope = tdp / "scope.json"
            _write_scope(scope, languages=["typescript"],
                         files_touched_list=["openapi.yaml"])
            out_dir = tdp / "out"
            # Minimal PATH — no oasdiff anywhere.
            env = os.environ.copy()
            env["PATH"] = "/usr/bin:/bin"
            r = subprocess.run(
                ["bash", str(SCRIPT),
                 "--scope", str(scope),
                 "--output-dir", str(out_dir),
                 "--repo", str(tdp)],
                capture_output=True, text=True, env=env, check=False,
            )
            self.assertEqual(r.returncode, 3, msg=r.stderr)
            self.assertIn("required analyzer 'oasdiff' is missing", r.stderr)
            self.assertIn("go install github.com/oasdiff/oasdiff@latest", r.stderr)
            self.assertIn("then rerun Code Ultrareview", r.stderr)
            plan = json.loads((out_dir / "tool-preflight.json").read_text())
            self.assertFalse(plan["complete"])
            self.assertIn("oasdiff", {e["tool"] for e in plan["missing"]})
            self.assertFalse((out_dir / "tool-findings.jsonl").exists())

    def test_pnpm_workspace_guidance_targets_the_workspace_root(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "package.json").write_text(
                '{"packageManager":"pnpm@10.0.0"}\n', encoding="utf-8"
            )
            (repo / "pnpm-workspace.yaml").write_text(
                "packages:\n  - packages/*\n", encoding="utf-8"
            )
            scope = repo / "scope.json"
            _write_scope(
                scope,
                languages=["javascript"],
                files_touched_list=["src/index.js"],
            )
            result = subprocess.run(
                [
                    "bash", str(SCRIPT),
                    "--scope", str(scope),
                    "--output-dir", str(repo / "out"),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                env={**os.environ, "PATH": "/usr/bin:/bin"},
                check=False,
            )

            self.assertEqual(result.returncode, 3, result.stderr)
            plan = json.loads((repo / "out" / "tool-preflight.json").read_text())
            installs = {entry["tool"]: entry["install"] for entry in plan["missing"]}
            self.assertEqual(installs["knip"], "pnpm add -Dw knip")

    def test_battery_blocks_when_all_native_tools_missing(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            scope = tdp / "scope.json"
            _write_scope(scope, languages=["go"],
                         files_touched_list=["main.go", "migrations/001.sql"])
            (tdp / "atlas.hcl").write_text("env \"local\" {}\n")
            out_dir = tdp / "out"
            env = os.environ.copy()
            env["PATH"] = "/usr/bin:/bin"
            r = subprocess.run(
                ["bash", str(SCRIPT),
                 "--scope", str(scope),
                 "--output-dir", str(out_dir),
                 "--repo", str(tdp)],
                capture_output=True, text=True, env=env, check=False,
            )
            self.assertEqual(r.returncode, 3, "missing analyzers must block")
            payload = json.loads((out_dir / "tool-preflight.json").read_text())
            names = {e["tool"] for e in payload["missing"]}
            for tool in ("deadcode", "gocyclo", "dupl", "atlas"):
                self.assertIn(tool, names)

    def test_no_available_analyzer_runs_when_another_is_missing(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            scope = tdp / "scope.json"
            _write_scope(scope, languages=["python"], files_touched_list=["src/foo.py"])
            marker = tdp / "lizard-ran"
            bin_dir = tdp / "bin"
            _make_shim(bin_dir, "lizard", f"touch {marker!s}; exit 0")
            env = os.environ.copy()
            env["PATH"] = f"{bin_dir}:/usr/bin:/bin"
            result = subprocess.run(
                ["bash", str(SCRIPT), "--scope", str(scope),
                 "--output-dir", str(tdp / "out"), "--repo", str(tdp)],
                capture_output=True, text=True, env=env, check=False,
            )
            self.assertEqual(result.returncode, 3)
            self.assertFalse(marker.exists(), "preflight must be atomic")

    def test_tool_findings_jsonl_always_emitted(self):
        """Even when no tool runs, the JSONL exists (empty)."""
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            scope = tdp / "scope.json"
            _write_scope(scope, languages=[], files_touched_list=[])
            out_dir = tdp / "out"
            env = os.environ.copy()
            env["PATH"] = "/usr/bin:/bin"
            r = subprocess.run(
                ["bash", str(SCRIPT),
                 "--scope", str(scope),
                 "--output-dir", str(out_dir),
                 "--repo", str(tdp)],
                capture_output=True, text=True, env=env, check=False,
            )
            self.assertEqual(r.returncode, 0)
            self.assertTrue((out_dir / "tool-findings.jsonl").is_file())

    def test_scope_json_records_missing_tools_without_claiming_skips(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            scope = tdp / "scope.json"
            _write_scope(scope, languages=["typescript"],
                         files_touched_list=["openapi.yaml", "main.go"])
            out_dir = tdp / "out"
            env = os.environ.copy()
            env["PATH"] = "/usr/bin:/bin"
            r = subprocess.run(
                ["bash", str(SCRIPT),
                 "--scope", str(scope),
                 "--output-dir", str(out_dir),
                 "--repo", str(tdp)],
                capture_output=True, text=True, env=env, check=False,
            )
            self.assertEqual(r.returncode, 3, msg=r.stderr)
            mutated = json.loads(scope.read_text())
            missing_names = {e["tool"] for e in mutated["tools_missing"]}
            self.assertIn("oasdiff", missing_names)
            self.assertEqual(mutated["tools_skipped"], [])
            # Other scope.json fields preserved untouched.
            self.assertEqual(mutated["languages"], ["typescript"])
            self.assertIn("openapi.yaml", mutated["files_touched_list"])


class TestAnalyzerExecution(unittest.TestCase):
    def _init_git(self, repo: Path) -> None:
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"], cwd=repo, check=True
        )
        subprocess.run(
            ["git", "config", "commit.gpgsign", "false"], cwd=repo, check=True
        )
        subprocess.run(
            ["git", "config", "core.hooksPath", "/dev/null"], cwd=repo, check=True
        )

    def _commit(self, repo: Path, message: str) -> str:
        subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", message], cwd=repo, check=True)
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def test_knip_6_wrapped_report_is_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            scope = repo / "scope.json"
            _write_scope(
                scope,
                languages=["typescript"],
                files_touched_list=["package.json"],
            )
            (repo / "package.json").write_text("{}\n", encoding="utf-8")
            out_dir = repo / "out"
            bin_dir = repo / "bin"
            _make_shim(bin_dir, "knip", "printf '{\"issues\":[]}\\n'")

            result = subprocess.run(
                [
                    "bash", str(SCRIPT),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                    "--axes", "simplification",
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=15,
                env={
                    **os.environ,
                    "PATH": f"{bin_dir}:/usr/bin:/bin:/usr/local/bin",
                },
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                (out_dir / "tool-findings.jsonl").read_text(encoding="utf-8"),
                "",
            )
            coverage = json.loads(scope.read_text(encoding="utf-8"))["tool_coverage"]
            self.assertEqual(coverage["executed"], ["knip"])

    def test_semgrep_report_errors_block_with_repair_and_rerun_guidance(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            scope = repo / "scope.json"
            _write_scope(
                scope,
                languages=["python"],
                files_touched_list=["app.py"],
            )
            (repo / "app.py").write_text("print('ok')\n", encoding="utf-8")
            out_dir = repo / "out"
            bin_dir = repo / "bin"
            _make_shim(
                bin_dir,
                "semgrep",
                "printf '%s\\n' '{\"results\":[],\"errors\":[{\"type\":\"Rule parse error\"}]}'",
            )

            result = subprocess.run(
                [
                    "bash",
                    str(SCRIPT),
                    "--scope",
                    str(scope),
                    "--output-dir",
                    str(out_dir),
                    "--repo",
                    str(repo),
                    "--axes",
                    "performance",
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=15,
                env={
                    **os.environ,
                    "PATH": f"{bin_dir}:/usr/bin:/bin:/usr/local/bin",
                },
            )

            self.assertEqual(result.returncode, 4, result.stderr)
            self.assertIn("Semgrep reported analyzer errors", result.stderr)
            self.assertIn(str(out_dir / "raw" / "semgrep.json"), result.stderr)
            self.assertIn(str(out_dir / "raw" / "semgrep.stderr"), result.stderr)
            self.assertIn("pipx install semgrep", result.stderr)
            self.assertIn("then rerun Code Ultrareview", result.stderr)
            coverage = json.loads(scope.read_text())["tool_coverage"]
            self.assertFalse(coverage["complete"])
            self.assertEqual(coverage["applicable"], ["semgrep"])
            self.assertEqual(coverage["executed"], [])
            self.assertFalse((out_dir / "tool-findings.jsonl").exists())

    def test_semgrep_invalid_report_surfaces_stderr_and_exact_verification(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            scope = repo / "scope.json"
            _write_scope(
                scope,
                languages=["python"],
                files_touched_list=["app.py"],
            )
            (repo / "app.py").write_text("print('ok')\n", encoding="utf-8")
            out_dir = repo / "out"
            bin_dir = repo / "bin"
            _make_shim(
                bin_dir,
                "semgrep",
                "printf 'permission denied\\n' >&2\nexit 1",
            )

            result = subprocess.run(
                [
                    "bash",
                    str(SCRIPT),
                    "--scope",
                    str(scope),
                    "--output-dir",
                    str(out_dir),
                    "--repo",
                    str(repo),
                    "--axes",
                    "performance",
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=15,
                env={
                    **os.environ,
                    "PATH": f"{bin_dir}:/usr/bin:/bin:/usr/local/bin",
                },
            )

        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertIn("did not produce its documented JSON schema", result.stderr)
        self.assertIn(str(out_dir / "raw" / "semgrep.stderr"), result.stderr)
        self.assertIn("ERROR: verify:", result.stderr)
        self.assertIn("semgrep --version", result.stderr)
        self.assertIn("pipx install semgrep", result.stderr)
        self.assertIn("inspect the report and stderr", result.stderr)

    def test_jscpd_v5_receives_changed_file_tree_with_relative_paths(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            scope = repo / "scope.json"
            _write_scope(
                scope,
                languages=["python"],
                files_touched_list=["src/a.py", "src/b.py", "src/deleted.py"],
            )
            (repo / "src" / "a.py").write_text("value = 1\n", encoding="utf-8")
            (repo / "src" / "b.py").write_text("value = 1\n", encoding="utf-8")
            (repo / "src" / "deleted.py").unlink()
            out_dir = repo / "out"
            bin_dir = repo / "bin"
            _make_shim(
                bin_dir,
                "jscpd",
                'out=""\n'
                'target=""\n'
                'while [[ $# -gt 0 ]]; do\n'
                '  case "$1" in\n'
                '    --output) out="$2"; shift 2 ;;\n'
                '    --min-lines) [[ "$2" == "15" ]] || exit 9; shift 2 ;;\n'
                '    --min-tokens) [[ "$2" == "100" ]] || exit 9; shift 2 ;;\n'
                '    --reporters) shift 2 ;;\n'
                '    --silent) shift ;;\n'
                '    *) target="$1"; shift ;;\n'
                '  esac\n'
                'done\n'
                '[[ -d "$target" ]] || exit 9\n'
                '[[ -f "$target/src/a.py" ]] || exit 9\n'
                '[[ -f "$target/src/b.py" ]] || exit 9\n'
                '[[ ! -e "$target/src/deleted.py" ]] || exit 9\n'
                'mkdir -p "$out"\n'
                "printf '%s\\n' "
                "'{\"duplicates\":[{\"firstFile\":{\"name\":\"src/a.py\",\"start\":1,\"end\":2},"
                "\"secondFile\":{\"name\":\"src/b.py\",\"start\":1,\"end\":2},"
                "\"lines\":2,\"tokens\":12}]}' > \"$out/jscpd-report.json\"",
            )
            _make_shim(
                bin_dir,
                "lizard",
                'printf "NLOC,CCN,token,PARAM,length,location\\n"',
            )
            _make_shim(bin_dir, "vulture")

            result = subprocess.run(
                [
                    "bash",
                    str(SCRIPT),
                    "--scope",
                    str(scope),
                    "--output-dir",
                    str(out_dir),
                    "--repo",
                    str(repo),
                    "--axes",
                    "simplification",
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=15,
                env={
                    **os.environ,
                    "PATH": f"{bin_dir}:/usr/bin:/bin:/usr/local/bin",
                },
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            findings = [
                json.loads(line)
                for line in (out_dir / "tool-findings.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
                if line.strip()
            ]
            self.assertEqual([finding["file"] for finding in findings], ["src/a.py"])
            self.assertEqual(list((out_dir / "raw").glob("jscpd-input.*")), [])
            self.assertEqual(list((out_dir / "raw").glob("jscpd-report.*")), [])

    def test_malformed_markdownlint_output_reports_evidence_and_remediation(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            scope = repo / "scope.json"
            _write_scope(
                scope,
                languages=["markdown"],
                files_touched_list=["README.md"],
            )
            (repo / "README.md").write_text("# Test\n", encoding="utf-8")
            out_dir = repo / "out"
            bin_dir = repo / "bin"
            _make_shim(
                bin_dir,
                "markdownlint-cli2",
                "printf '%s\\n' 'unrecognized analyzer output'",
            )

            result = subprocess.run(
                [
                    "bash", str(SCRIPT),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                    "--axes", "documentation",
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=15,
                env={
                    **os.environ,
                    "PATH": f"{bin_dir}:/usr/bin:/bin:/usr/local/bin",
                },
            )

            self.assertEqual(result.returncode, 4, result.stderr)
            self.assertIn(
                "markdownlint-cli2 produced non-empty output", result.stderr
            )
            self.assertIn("documented text or JSON schema", result.stderr)
            self.assertIn(
                str(out_dir / "raw" / "markdownlint-cli2.txt"),
                result.stderr,
            )
            self.assertIn(
                str(out_dir / "raw" / "markdownlint-cli2.stderr"),
                result.stderr,
            )
            self.assertIn(
                "npm install --save-dev markdownlint-cli2", result.stderr
            )
            self.assertIn("repair only the analyzer reports listed above", result.stderr)
            self.assertIn("ERROR: rerun: bash", result.stderr)
            self.assertFalse((out_dir / "tool-findings.jsonl").exists())

    def test_markdownlint_uses_bundled_base_config_without_resolving_packages(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            scope = repo / "scope.json"
            _write_scope(
                scope,
                languages=["markdown"],
                files_touched_list=["README.md"],
            )
            (repo / "README.md").write_text("# Test\n", encoding="utf-8")
            out_dir = repo / "out"
            bin_dir = repo / "bin"
            marker = repo / "markdownlint-args.txt"
            _make_shim(
                bin_dir,
                "markdownlint-cli2",
                f"printf '%s\\n' \"$@\" > {marker!s}",
            )

            result = subprocess.run(
                [
                    "bash",
                    str(SCRIPT),
                    "--scope",
                    str(scope),
                    "--output-dir",
                    str(out_dir),
                    "--repo",
                    str(repo),
                    "--axes",
                    "documentation",
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=15,
                env={
                    **os.environ,
                    "PATH": f"{bin_dir}:/usr/bin:/bin:/usr/local/bin",
                },
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            args = marker.read_text(encoding="utf-8").splitlines()
            self.assertIn("--config", args)
            config = Path(args[args.index("--config") + 1])
            self.assertEqual(
                config.name,
                "markdownlint-base.markdownlint-cli2.jsonc",
            )
            base_rules = json.loads(config.read_text(encoding="utf-8"))["config"]
            self.assertEqual(base_rules["MD013"], False)
            self.assertEqual(base_rules["MD060"], {"style": "compact"})
            self.assertFalse({"npx", "pnpm", "npm", "yarn", "bunx"} & set(args))

    def test_ingest_failure_names_only_the_invalid_analyzer(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            scope = repo / "scope.json"
            _write_scope(
                scope,
                languages=["markdown"],
                files_touched_list=["README.md"],
            )
            (repo / "README.md").write_text("# Test\n", encoding="utf-8")
            (repo / ".vale.ini").write_text("StylesPath = styles\n", encoding="utf-8")
            out_dir = repo / "out"
            bin_dir = repo / "bin"
            _make_shim(
                bin_dir,
                "markdownlint-cli2",
                "printf '%s\\n' 'unrecognized analyzer output'",
            )
            _make_shim(bin_dir, "vale", "printf '{}\\n'")

            result = subprocess.run(
                [
                    "bash",
                    str(SCRIPT),
                    "--scope",
                    str(scope),
                    "--output-dir",
                    str(out_dir),
                    "--repo",
                    str(repo),
                    "--axes",
                    "documentation",
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=15,
                env={
                    **os.environ,
                    "PATH": f"{bin_dir}:/usr/bin:/bin:/usr/local/bin",
                },
            )

        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertIn("markdownlint-cli2 produced non-empty output", result.stderr)
        self.assertIn(str(out_dir / "raw" / "markdownlint-cli2.txt"), result.stderr)
        self.assertNotIn(str(out_dir / "raw" / "vale.json"), result.stderr)
        self.assertIn("npm install --save-dev markdownlint-cli2", result.stderr)
        self.assertNotIn("errata-ai/vale", result.stderr)

    def test_findings_exit_without_report_blocks_markdownlint(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            scope = repo / "scope.json"
            _write_scope(
                scope,
                languages=["markdown"],
                files_touched_list=["README.md"],
            )
            out_dir = repo / "out"
            bin_dir = repo / "bin"
            _make_shim(bin_dir, "markdownlint-cli2", "exit 1")

            result = subprocess.run(
                [
                    "bash", str(SCRIPT),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                    "--axes", "documentation",
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=15,
                env={
                    **os.environ,
                    "PATH": f"{bin_dir}:/usr/bin:/bin:/usr/local/bin",
                },
            )

        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertIn("findings code but produced no parseable report", result.stderr)
        self.assertIn("npm install --save-dev markdownlint-cli2", result.stderr)

    def test_findings_exit_without_report_blocks_text_analyzers(self):
        cases = (
            ("python", "src/app.py", "vulture", 3),
            ("rust", "src/lib.rs", "cargo-machete", 1),
        )
        for language, changed_file, failing_tool, exit_code in cases:
            with self.subTest(tool=failing_tool), tempfile.TemporaryDirectory() as td:
                repo = Path(td)
                scope = repo / "scope.json"
                _write_scope(
                    scope,
                    languages=[language],
                    files_touched_list=[changed_file],
                )
                out_dir = repo / "out"
                bin_dir = repo / "bin"
                _make_shim(
                    bin_dir,
                    "jscpd",
                    'out=""\n'
                    'while [[ $# -gt 0 ]]; do\n'
                    '  if [[ "$1" == "--output" ]]; then out="$2"; break; fi\n'
                    '  shift\n'
                    'done\n'
                    'mkdir -p "$out"\n'
                    'printf \'{"duplicates":[]}\\n\' > "$out/jscpd-report.json"',
                )
                _make_shim(
                    bin_dir,
                    "lizard",
                    'printf "NLOC,CCN,token,PARAM,length,location\\n"',
                )
                _make_shim(bin_dir, failing_tool, f"exit {exit_code}")

                result = subprocess.run(
                    [
                        "bash", str(SCRIPT),
                        "--scope", str(scope),
                        "--output-dir", str(out_dir),
                        "--repo", str(repo),
                        "--axes", "simplification",
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=15,
                    env={
                        **os.environ,
                        "PATH": f"{bin_dir}:/usr/bin:/bin:/usr/local/bin",
                    },
                )

            self.assertEqual(result.returncode, 4, result.stderr)
            self.assertIn(
                f"{failing_tool} exited with its findings code but produced no parseable report",
                result.stderr,
            )

    def test_failed_rerun_invalidates_stale_coverage_and_findings(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            scope = repo / "scope.json"
            _write_scope(
                scope,
                languages=["markdown"],
                files_touched_list=["README.md"],
                tool_coverage={
                    "complete": True,
                    "selected_axes": ["documentation"],
                    "applicable": ["markdownlint-cli2"],
                    "executed": ["markdownlint-cli2"],
                },
                coverage_complete=True,
            )
            (repo / "README.md").write_text("# Test\n", encoding="utf-8")
            out_dir = repo / "out"
            out_dir.mkdir()
            stale_finding = {
                "axis": "documentation",
                "confidence": 100,
                "file": "README.md",
                "line_end": 1,
                "line_start": 1,
                "message": "stale finding",
                "severity": "P1",
                "source_tool": "markdownlint-cli2",
            }
            (out_dir / "tool-findings.jsonl").write_text(
                json.dumps(stale_finding) + "\n",
                encoding="utf-8",
            )
            bin_dir = repo / "bin"
            _make_shim(
                bin_dir,
                "markdownlint-cli2",
                "printf '%s\\n' 'unrecognized analyzer output'",
            )

            result = subprocess.run(
                [
                    "bash", str(SCRIPT),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                    "--axes", "documentation",
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=15,
                env={
                    **os.environ,
                    "PATH": f"{bin_dir}:/usr/bin:/bin:/usr/local/bin",
                },
            )

            self.assertEqual(result.returncode, 4, result.stderr)
            mutated = json.loads(scope.read_text(encoding="utf-8"))
            self.assertFalse(mutated["tool_coverage"]["complete"])
            self.assertFalse(mutated["coverage_complete"])
            self.assertEqual(mutated["tool_coverage"]["executed"], [])
            self.assertFalse((out_dir / "tool-findings.jsonl").exists())
            self.assertFalse(
                (out_dir / ".tool-findings.pending.jsonl").exists()
            )

    def test_oasdiff_uses_scope_base_for_every_changed_spec(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            self._init_git(repo)
            specs = ["api/openapi.yaml", "api/admin-openapi.yaml"]
            for index, relative in enumerate(specs, start=1):
                path = repo / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"base-{index}\n", encoding="utf-8")
            base = self._commit(repo, "base")
            for index, relative in enumerate(specs, start=1):
                (repo / relative).write_text(f"head-{index}\n", encoding="utf-8")
            self._commit(repo, "intermediate")
            for index, relative in enumerate(specs, start=1):
                (repo / relative).write_text(f"worktree-{index}\n", encoding="utf-8")

            scope = repo / "scope.json"
            _write_scope(
                scope,
                base=base,
                languages=[],
                files_touched_list=specs,
            )
            out_dir = repo / "out"
            bin_dir = repo / "bin"
            log = repo / "oasdiff.log"
            _make_shim(
                bin_dir,
                "oasdiff",
                "previous=$4\n"
                "current=$5\n"
                "printf '%s|%s\\n' \"$(cat \"$previous\")\" \"$current\" >> \"$OASDIFF_LOG\"\n"
                "printf '[]\\n'",
            )
            result = subprocess.run(
                [
                    "bash", str(SCRIPT),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=15,
                env={
                    **os.environ,
                    "PATH": f"{bin_dir}:/usr/bin:/bin:/usr/local/bin",
                    "OASDIFF_LOG": str(log),
                },
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            lines = log.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 2)
            self.assertTrue(any(line.startswith("base-1|") for line in lines))
            self.assertTrue(any(line.startswith("base-2|") for line in lines))
            self.assertFalse(any("head-" in line for line in lines))
            for relative in specs:
                self.assertTrue(any(line.endswith(relative) for line in lines))

    def test_battery_timeout_terminates_analyzer_children(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            self._init_git(repo)
            spec = repo / "openapi.yaml"
            spec.write_text("base\n", encoding="utf-8")
            base = self._commit(repo, "base")
            spec.write_text("changed\n", encoding="utf-8")
            scope = repo / "scope.json"
            _write_scope(
                scope,
                base=base,
                languages=[],
                files_touched_list=["openapi.yaml"],
            )
            out_dir = repo / "out"
            bin_dir = repo / "bin"
            sentinel = repo / "child-completed"
            child = repo / "child.py"
            child.write_text(
                "import pathlib, time\n"
                "time.sleep(1.5)\n"
                f"pathlib.Path({str(sentinel)!r}).write_text('alive')\n",
                encoding="utf-8",
            )
            _make_shim(
                bin_dir,
                "oasdiff",
                f'python3 "{child}" &\n'
                "sleep 10",
            )

            result = subprocess.run(
                [
                    "bash", str(SCRIPT),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                    "--timeout", "1",
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
                env={
                    **os.environ,
                    "PATH": f"{bin_dir}:/usr/bin:/bin:/usr/local/bin",
                },
            )

            self.assertEqual(result.returncode, 4, result.stderr)
            self.assertIn("oasdiff timed out after 1s", result.stderr)
            time.sleep(2)
            self.assertFalse(sentinel.exists(), "battery timeout left a child running")


# ---------------------------------------------------------------------------
# No-auto-install — script never invokes brew/pip/npm/cargo/go install.
# ---------------------------------------------------------------------------


class TestNoAutoInstall(unittest.TestCase):
    """AC: The battery NEVER runs brew install, cargo install, go install,
    pip install, npm install -g."""

    FORBIDDEN = ("brew install", "npm install -g", "npm i -g",
                 "cargo install", "go install", "pip install", "pipx install")

    def _strip_table(self, text: str) -> str:
        """Remove the BATTERY_TABLE block (it documents install commands as
        strings — those are not invocations)."""
        return re.sub(
            r'BATTERY_TABLE=\(.+?\n\)',
            'BATTERY_TABLE=()',
            text,
            count=1,
            flags=re.DOTALL,
        )

    def test_script_source_has_no_install_invocations(self):
        text = SCRIPT.read_text(encoding="utf-8")
        stripped = self._strip_table(text)
        for line_no, raw_line in enumerate(stripped.splitlines(), start=1):
            line = raw_line.split("#", 1)[0]
            for pattern in self.FORBIDDEN:
                self.assertNotIn(
                    pattern, line,
                    f"{SCRIPT.name}:{line_no} invokes a forbidden install "
                    f"pattern {pattern!r}: {raw_line!r}",
                )

    def test_apt_guidance_names_maven_package_without_sudo(self):
        with tempfile.TemporaryDirectory() as td:
            bin_dir = Path(td) / "bin"
            _make_shim(bin_dir, "apt-get")
            result = subprocess.run(
                [
                    "bash",
                    "-c",
                    'source "$1"; tool_install_command . mvn',
                    "test",
                    str(INSTALL_GUIDANCE),
                ],
                capture_output=True,
                text=True,
                check=False,
                env={
                    **os.environ,
                    "PATH": f"{bin_dir}:/usr/bin:/bin",
                },
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Debian package maven", result.stdout)
        self.assertIn("https://maven.apache.org/install.html", result.stdout)
        self.assertNotIn("sudo", result.stdout)


# ---------------------------------------------------------------------------
# README parity — BATTERY_TABLE tools all listed in the README's tool table.
# ---------------------------------------------------------------------------


def _parse_battery_table() -> list[tuple[str, str, str]]:
    """Read BATTERY_TABLE from run_battery.sh — returns [(tool, install, axis_hint), ...]."""
    text = SCRIPT.read_text(encoding="utf-8")
    m = re.search(r"BATTERY_TABLE=\(\s*\n(.+?)\n\)", text, re.DOTALL)
    assert m, "BATTERY_TABLE not found in run_battery.sh"
    out: list[tuple[str, str, str]] = []
    for raw in m.group(1).splitlines():
        line = raw.strip()
        if not line.startswith('"') or not line.endswith('"'):
            continue
        parts = line.strip('"').split("|")
        if len(parts) == 3:
            out.append((parts[0], parts[1], parts[2]))
    return out


class TestReadmeParity(unittest.TestCase):
    """AC: README's tool table matches dispatch matrix in run_battery.sh."""

    def setUp(self):
        self.table = _parse_battery_table()
        self.text = README.read_text(encoding="utf-8")

    def test_battery_table_completeness(self):
        names = [t for t, _, _ in self.table]
        # All 14 tools present, no duplicates.
        self.assertEqual(len(names), 14)
        self.assertEqual(len(set(names)), 14)

    def test_every_tool_appears_in_readme(self):
        for tool, _, _ in self.table:
            with self.subTest(tool=tool):
                # Tool name appears at least once in README (in a code span or table cell).
                self.assertIn(tool, self.text, f"{tool} missing from root README.md")


# ---------------------------------------------------------------------------
# Preflight — wraps dry-run, renders human-readable.
# ---------------------------------------------------------------------------


class TestPreflight(unittest.TestCase):
    def test_preflight_blocks_and_prints_exact_install_commands(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            scope = tdp / "scope.json"
            _write_scope(scope, languages=["python"],
                         files_touched_list=["src/foo.py"])
            bin_dir = tdp / "bin"
            bin_dir.mkdir()
            env = os.environ.copy()
            env["PATH"] = f"{bin_dir}:/usr/bin:/bin"
            r = subprocess.run(
                ["bash", str(PREFLIGHT),
                 "--scope", str(scope),
                 "--repo", str(tdp)],
                capture_output=True, text=True, env=env, check=False,
            )
            self.assertEqual(r.returncode, 3, msg=r.stderr)
            self.assertIn("Repo kind:", r.stdout)
            self.assertIn("Available", r.stdout)
            self.assertIn("Missing", r.stdout)
            self.assertIn("pipx install vulture", r.stdout)
            self.assertIn("BLOCKED:", r.stdout)


# ---------------------------------------------------------------------------
# WS-2 regression — default-run safety (no `--config=auto`, diff-scoped tools)
# ---------------------------------------------------------------------------


class TestDefaultRunSafety(unittest.TestCase):
    """Pins WS-2 contracts at the dispatch-script source level.

    Parses `run_battery.sh` directly rather than running it — keeps the
    test offline and fast, and asserts the bug signature (the literal
    `--config=auto` string or a bare `"$REPO"` target) is absent from the
    function body for the relevant tool.
    """

    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text(encoding="utf-8")

    def _function_body(self, name: str) -> str:
        """Return the bash function body for `name()`."""
        marker = f"\n{name}() {{"
        start = self.source.find(marker)
        self.assertNotEqual(start, -1, f"function `{name}` not found in run_battery.sh")
        # Naive matching brace — bash functions in this file don't nest braces
        # at the top level, so a single closing brace on its own line ends it.
        end = self.source.find("\n}\n", start)
        self.assertNotEqual(end, -1, f"close brace for `{name}` not found")
        return self.source[start:end + 3]

    def test_semgrep_does_not_call_config_auto(self):
        """`run_semgrep` no longer invokes `--config=auto` — the implicit
        registry network call is removed for the public-skill posture.

        Allow the literal `--config=auto` token in comments (documenting
        why it was removed); block it from any code line.
        """
        body = self._function_body("run_semgrep")
        for lineno, line in enumerate(body.splitlines(), 1):
            # Strip the bash comment portion (everything after #).
            code = line.split("#", 1)[0]
            self.assertNotIn(
                "--config=auto", code,
                f"--config=auto in code (not comment) at line {lineno}: {line}",
            )

    def test_semgrep_disables_runtime_network_features(self):
        """Bundled-rule scans do not phone home or wait on version checks."""
        body = self._function_body("run_semgrep")
        self.assertIn("--metrics=off", body)
        self.assertIn("--disable-version-check", body)

    def test_semgrep_preserves_bundled_rule_ids(self):
        """Local config paths must not leak into the reported rule IDs."""
        body = self._function_body("run_semgrep")
        self.assertIn("--no-rewrite-rule-ids", body)

    def test_jscpd_target_is_changed_files_not_whole_repo(self):
        """`run_jscpd` passes a `code_files` array, not `"$REPO"`."""
        body = self._function_body("run_jscpd")
        # The fixed dispatch passes `"${code_files[@]}"`; the old shape
        # passed `"$REPO"` as the bare target.
        self.assertIn('"${code_files[@]}"', body)
        # No bare-`"$REPO"` invocation of jscpd remains.
        self.assertNotRegex(body, r'jscpd[^|]+"\$REPO"')

    def test_vale_target_is_changed_files_not_whole_repo(self):
        """`run_vale` passes a `prose_files` array, not `"$REPO"`."""
        body = self._function_body("run_vale")
        self.assertIn('"${prose_files[@]}"', body)
        self.assertNotRegex(body, r'vale[^|]+"\$REPO"')

    def test_semgrep_target_is_changed_files_not_whole_repo(self):
        """`run_semgrep` passes a `code_files` array, not `"$REPO"`."""
        body = self._function_body("run_semgrep")
        self.assertIn('"${code_files[@]}"', body)
        self.assertNotRegex(body, r'semgrep[^|]+"\$REPO"')

    def test_changed_paths_cannot_be_parsed_as_analyzer_options(self):
        """Changed-file analyzers receive explicit repository-relative paths."""
        for function_name, array_name in (
            ("run_jscpd", "code_files"),
            ("run_markdownlint", "md_files"),
            ("run_semgrep", "code_files"),
            ("run_vale", "prose_files"),
        ):
            body = self._function_body(function_name)
            self.assertIn(
                f'{array_name}+=("./$f")',
                body,
                f"{function_name} does not protect leading-hyphen paths",
            )


if __name__ == "__main__":
    unittest.main()
