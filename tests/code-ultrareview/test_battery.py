"""Tests for skills/code-ultrareview/scripts/run_battery.sh.

Covers per-language dispatch matrix, trigger-based dispatch (api-extractor,
oasdiff, atlas, vale), graceful skip for missing tools, the no-auto-install
contract, and README ↔ dispatch parity (no drift between the script's
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
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "skills" / "code-ultrareview" / "scripts" / "run_battery.sh"
PREFLIGHT = REPO_ROOT / "skills" / "code-ultrareview" / "scripts" / "preflight_tools.sh"
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
        "claude_md_chain": [],
        "loc_changed": 0,
        "files_touched": 0,
        "files_touched_list": [],
        "activates_coherence": False,
        "tools_skipped": [],
    }
    defaults.update(overrides)
    path.write_text(json.dumps(defaults, indent=2), encoding="utf-8")


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
    if r.returncode != 0:
        raise AssertionError(f"run_battery --dry-run failed ({r.returncode})\n"
                             f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}")
    return json.loads(r.stdout)


def _dispatched_tools(plan: dict) -> set[str]:
    return {e["tool"] for e in plan.get("dispatched", [])}


def _skipped_tools(plan: dict) -> set[str]:
    return {e["tool"] for e in plan.get("skipped", [])}


def _wanted_tools(plan: dict) -> set[str]:
    """Union — both dispatched (available) and skipped (missing) were wanted."""
    return _dispatched_tools(plan) | _skipped_tools(plan)


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
            _make_shim(bin_dir, "npx")
            _make_shim(bin_dir, "uvx")
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
            _make_shim(bin_dir, "npx")
            _make_shim(bin_dir, "uvx")
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
            _make_shim(bin_dir, "npx")
            _make_shim(bin_dir, "uvx")
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
            _make_shim(bin_dir, "npx")
            _make_shim(bin_dir, "uvx")
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
        _make_shim(bin_dir, "npx")
        _make_shim(bin_dir, "uvx")

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
            path_bin = tdp / "path-bin"
            _make_shim(path_bin, "knip")
            plan = _run_dry(scope, tdp, path_bin)
            dispatched = {e["tool"]: e["wrapper"] for e in plan["dispatched"]}
            self.assertEqual(dispatched.get("knip"), "project")

    def test_path_binary_dispatches(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            scope = tdp / "scope.json"
            _write_scope(scope, repo_kind="python", languages=["python"],
                         files_touched_list=["src/foo.py"])
            bin_dir = tdp / "bin"
            _make_shim(bin_dir, "vulture")
            plan = _run_dry(scope, tdp, bin_dir)
            dispatched = {e["tool"]: e["wrapper"] for e in plan["dispatched"]}
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
# Graceful skip — no native tool, no wrapper → WARN + tools-skipped.json.
# ---------------------------------------------------------------------------


class TestGracefulSkip(unittest.TestCase):
    """AC: OpenAPI repo without oasdiff installed →
    `WARN: oasdiff skipped — not found — install: brew install oasdiff` on stderr,
    scope.json["tools_skipped"] contains oasdiff, skill continues without error.
    """

    def test_missing_oasdiff_emits_warn_and_logs_skip(self):
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
            self.assertEqual(r.returncode, 0, msg=r.stderr)
            self.assertIn("WARN: oasdiff skipped — not found", r.stderr)
            self.assertIn("brew install oasdiff", r.stderr)
            skipped_path = out_dir / "tools-skipped.json"
            self.assertTrue(skipped_path.is_file())
            payload = json.loads(skipped_path.read_text())
            skipped_names = {e["tool"] for e in payload["skipped"]}
            self.assertIn("oasdiff", skipped_names)

    def test_battery_continues_when_all_native_tools_missing(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            scope = tdp / "scope.json"
            _write_scope(scope, languages=["go"],
                         files_touched_list=["main.go", "migrations/001.sql"])
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
            self.assertEqual(r.returncode, 0, "battery must continue on missing tools")
            payload = json.loads((out_dir / "tools-skipped.json").read_text())
            # deadcode, gocyclo, dupl, atlas — all path-only and missing.
            names = {e["tool"] for e in payload["skipped"]}
            for tool in ("deadcode", "gocyclo", "dupl", "atlas"):
                self.assertIn(tool, names)

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

    def test_scope_json_tools_skipped_mutated_in_place(self):
        """SKILL.md says skipped tools land in scope.json[tools_skipped]. The
        battery writes both <output>/tools-skipped.json AND mutates scope.json
        so downstream phases can read either file."""
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
            self.assertEqual(r.returncode, 0, msg=r.stderr)
            mutated = json.loads(scope.read_text())
            skipped_names = {e["tool"] for e in mutated["tools_skipped"]}
            self.assertIn("oasdiff", skipped_names)
            # Shape parity with tools-skipped.json.
            payload = json.loads((out_dir / "tools-skipped.json").read_text())
            file_names = {e["tool"] for e in payload["skipped"]}
            self.assertEqual(skipped_names, file_names)
            # Other scope.json fields preserved untouched.
            self.assertEqual(mutated["languages"], ["typescript"])
            self.assertIn("openapi.yaml", mutated["files_touched_list"])


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
    def test_preflight_prints_dispatched_and_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            scope = tdp / "scope.json"
            _write_scope(scope, languages=["python"],
                         files_touched_list=["src/foo.py"])
            bin_dir = tdp / "bin"
            _make_shim(bin_dir, "uvx")
            env = os.environ.copy()
            env["PATH"] = f"{bin_dir}:/usr/bin:/bin"
            r = subprocess.run(
                ["bash", str(PREFLIGHT),
                 "--scope", str(scope),
                 "--repo", str(tdp)],
                capture_output=True, text=True, env=env, check=False,
            )
            self.assertEqual(r.returncode, 0, msg=r.stderr)
            self.assertIn("Repo kind:", r.stdout)
            self.assertIn("Dispatched", r.stdout)
            self.assertIn("Skipped", r.stdout)
            self.assertIn("Informational only", r.stdout)


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


if __name__ == "__main__":
    unittest.main()
