"""WS-6 — opt-in flag contracts for code-ultrareview.

Pins the acceptance criteria from the forge spec:

- Without `--verify-build`, build verification NEVER runs.
- Without `--mutation-test`, mutation testing NEVER runs.
- Without `--reconcile`, Intent axis runs in standard mode (no GAP/SCOPE-ADD).
- Without `--apply-safe`, NO files are modified.
- `--verify-build --mutation-test` → build verification in Phase 3.5,
  mutation in Phase 2 extension.
- `--apply-safe` → diff preview + per-file y/N confirmation before any write.

Each script's entry point is exercised via subprocess (CLI contract) AND
as an importable module where applicable (unit contract). External tools
(stryker, mutmut, pitest, the repo's own test command) are mocked via
fixtures or environment switches so this test passes on any contributor's
machine.

Cross-references:
    `test_ultra_execution.py` — pins build_detect + apply_safe writer
        contracts. This file pins the orchestration above those.
    `test_derivation_graph.py` — pins derivation's deterministic structure.
        This file pins the `--reconcile` flag toggle.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import stat
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_SCRIPTS = REPO_ROOT / "skills" / "code-ultrareview" / "scripts"
RUN_BUILD_VERIFY = SKILL_SCRIPTS / "run_build_verify.py"
RUN_MUTATION = SKILL_SCRIPTS / "run_mutation.sh"

if str(SKILL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SKILL_SCRIPTS))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Import the module so we can call `.run()` directly for fast unit tests.
run_build_verify = _load("run_build_verify", RUN_BUILD_VERIFY)
synthesis_core = _load("synthesis_core", SKILL_SCRIPTS / "synthesis_core.py")
build_detect = _load("build_detect", SKILL_SCRIPTS / "build_detect.py")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _write_scope(repo: Path, *, languages: list[str], files: list[str]) -> Path:
    """Write a minimal `scope.json` for the script under test."""
    scope = {
        "repo_kind": "app",
        "languages": languages,
        "files_touched_list": files,
        "activates_coherence": False,
        "instruction_chain": [],
        "tools_skipped": [],
    }
    scope_path = repo / "scope.json"
    scope_path.write_text(json.dumps(scope, indent=2), encoding="utf-8")
    for relative in files:
        touched = repo / relative
        if not touched.exists():
            touched.parent.mkdir(parents=True, exist_ok=True)
            touched.write_text(
                "{}\n" if touched.name == "package.json" else "",
                encoding="utf-8",
            )
    return scope_path


def _write_executable(path: Path, body: str = "exit 0") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"#!/usr/bin/env bash\n{body}\n", encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return path


def _configure_mutmut(repo: Path) -> None:
    (repo / "setup.cfg").write_text(
        '[mutmut]\nsource_paths = .\n', encoding="utf-8"
    )


def _write_findings(path: Path, findings: list[dict]) -> Path:
    """Write a JSONL findings file."""
    with path.open("w", encoding="utf-8") as fh:
        for finding in findings:
            fh.write(json.dumps(finding) + "\n")
    return path


# ---------------------------------------------------------------------------
# `--verify-build` — Phase 3.5 orchestration
# ---------------------------------------------------------------------------


class TestVerifyBuildOff(unittest.TestCase):
    """The orchestrator omits this script unless `--verify-build` is set.

    Once invoked, a missing Phase 4 findings artifact is a runtime coverage
    failure, not a no-op or a command-line syntax error.
    """

    def test_missing_findings_file_is_an_input_error(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(repo, languages=["python"], files=[])
            out = repo / "out.jsonl"
            r = subprocess.run(
                [
                    sys.executable, str(RUN_BUILD_VERIFY),
                    "--scope", str(scope),
                    "--findings", str(repo / "does-not-exist.jsonl"),
                    "--output", str(out),
                    "--repo", str(repo),
                ],
                capture_output=True, text=True, timeout=10,
            )
            self.assertEqual(r.returncode, 4)
            self.assertIn("findings JSONL not found", r.stderr)
            self.assertIn("Rerun the axis and validator phases", r.stderr)
            self.assertFalse(out.exists())


class TestVerifyBuildGate(unittest.TestCase):
    """A generic build result gates the review but never proves a finding."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _findings(self) -> list[dict]:
        return [
            {
                "axis": "correctness",
                "severity": "High",
                "location": "src/app.py:42",
                "finding": "Off-by-one bound",
                "recommendation": "Use < n, not <= n",
                "confidence": 65,
            },
            {
                "axis": "tests",
                "severity": "Medium",
                "location": "tests/test_app.py:10",
                "finding": "Weak assertion",
                "recommendation": "Assert on value, not truthiness",
                "confidence": 70,
            },
            {
                "axis": "style",
                "severity": "Low",
                "location": "src/app.py:1",
                "finding": "Inconsistent quoting",
                "recommendation": "Pick single or double quotes consistently",
                "confidence": 60,
            },
            {
                "axis": "performance",
                "severity": "Medium",
                "location": "src/app.py:55",
                "finding": "N+1 query",
                "recommendation": "Use eager load",
                "confidence": 50,  # +30 = 80 → just at threshold, still promotes
            },
        ]

    def test_failing_build_blocks_without_promoting_findings(self):
        verified_input = self._findings()
        out, meta = run_build_verify.run(
            self.repo, verified_input, "echo fail && exit 1",
            tool="pytest", tool_available=True, timeout=10,
        )
        self.assertEqual(out, verified_input)
        self.assertEqual(meta["build_status"], "failed")
        self.assertFalse(meta["complete"])
        self.assertEqual(meta["promoted_count"], 0)

    def test_passing_build_completes_without_promoting_findings(self):
        verified_input = self._findings()
        out, meta = run_build_verify.run(
            self.repo, verified_input, "true",
            tool="pytest", tool_available=True, timeout=10,
        )
        for f in out:
            self.assertEqual(
                f["confidence"],
                next(g["confidence"] for g in verified_input if g["axis"] == f["axis"]),
            )
        self.assertEqual(meta["build_status"], "passed")
        self.assertTrue(meta["complete"])
        self.assertEqual(meta["promoted_count"], 0)

    def test_build_timeout_terminates_child_processes(self):
        sentinel = self.repo / "child-completed"
        child = self.repo / "child.py"
        parent = self.repo / "parent.py"
        child.write_text(
            "import pathlib, time\n"
            "time.sleep(1.5)\n"
            f"pathlib.Path({str(sentinel)!r}).write_text('alive')\n",
            encoding="utf-8",
        )
        parent.write_text(
            "import subprocess, sys, time\n"
            f"subprocess.Popen([sys.executable, {str(child)!r}])\n"
            "time.sleep(10)\n",
            encoding="utf-8",
        )

        result = run_build_verify._run_build(
            self.repo,
            f'"{sys.executable}" "{parent}"',
            "unittest",
            timeout=1,
        )

        self.assertEqual(result["build_status"], "timeout")
        time.sleep(2)
        self.assertFalse(sentinel.exists(), "build timeout left a child running")

    def test_build_gate_disables_corepack_network_resolution(self):
        result = run_build_verify._run_build(
            self.repo,
            'test "$COREPACK_ENABLE_NETWORK" = 0 && '
            'test "$COREPACK_DEFAULT_TO_LATEST" = 0',
            "yarn",
            timeout=10,
        )

        self.assertEqual(result["build_status"], "passed")

    def test_tool_unavailable_is_incomplete_with_remediation(self):
        verified_input = self._findings()
        out, meta = run_build_verify.run(
            self.repo, verified_input, "pytest -x",
            tool="pytest", tool_available=False, timeout=10,
        )
        self.assertEqual(out, verified_input)  # untouched
        self.assertEqual(meta["build_status"], "missing-runner")
        self.assertFalse(meta["complete"])
        self.assertEqual(meta["promoted_count"], 0)
        self.assertIn("command -v pytest", meta["remediation"])

    def test_pytest_remediation_uses_declared_dev_requirements(self):
        (self.repo / "requirements-dev.txt").write_text(
            "pytest==8.4.1\n",
            encoding="utf-8",
        )
        remediation = run_build_verify._missing_runner_remediation(
            self.repo,
            "pytest",
        )
        self.assertIn(
            "`python3 -m pip install -r requirements-dev.txt`",
            remediation,
        )
        self.assertIn("exact command printed below", remediation)

    def test_pinned_pnpm_remediation_preserves_declared_version(self):
        (self.repo / "package.json").write_text(
            json.dumps({"packageManager": "pnpm@10.15.0"}),
            encoding="utf-8",
        )
        remediation = run_build_verify._missing_runner_remediation(
            self.repo,
            "pnpm",
        )
        self.assertIn(
            "`corepack install --global pnpm@10.15.0 && corepack enable pnpm`",
            remediation,
        )
        self.assertIn("command -v pnpm", remediation)

    def test_apt_remediation_names_packages_without_delegating_sudo(self):
        def available(command: str) -> str | None:
            return "/usr/bin/apt-get" if command == "apt-get" else None

        with mock.patch.object(run_build_verify.shutil, "which", side_effect=available):
            remediation = run_build_verify._missing_runner_remediation(
                self.repo,
                "go",
            )

        self.assertIn("Debian package(s) `golang-go`", remediation)
        self.assertIn("https://go.dev/doc/install", remediation)
        self.assertNotIn("sudo", remediation)

    def test_zero_test_report_blocks_the_gate(self):
        verified_input = self._findings()
        out, meta = run_build_verify.run(
            self.repo,
            verified_input,
            "printf 'Ran 0 tests\\n' >&2",
            tool="unittest",
            tool_available=True,
            timeout=10,
        )
        self.assertEqual(out, verified_input)
        self.assertEqual(meta["build_status"], "no-tests-collected")
        self.assertFalse(meta["complete"])
        self.assertEqual(meta["promoted_count"], 0)

    def test_pytest_zero_test_report_blocks_the_gate(self):
        verified_input = self._findings()
        out, meta = run_build_verify.run(
            self.repo,
            verified_input,
            "printf 'collected 0 items\\n\\nno tests ran in 0.01s\\n'",
            tool="pytest",
            tool_available=True,
            timeout=10,
        )
        self.assertEqual(out, verified_input)
        self.assertEqual(meta["build_status"], "no-tests-collected")
        self.assertFalse(meta["complete"])
        self.assertEqual(meta["promoted_count"], 0)

    def test_no_tool_detected_is_incomplete_with_remediation(self):
        verified_input = self._findings()
        out, meta = run_build_verify.run(
            self.repo, verified_input, None,
            tool=None, tool_available=False, timeout=10,
        )
        self.assertEqual(out, verified_input)
        self.assertEqual(meta["build_status"], "missing-test-command")
        self.assertFalse(meta["complete"])
        self.assertIn("Add a canonical test entry", meta["remediation"])
        self.assertIn("`pytest`", meta["remediation"])
        self.assertIn("`unittest`", meta["remediation"])

    def test_requested_gate_runs_even_when_all_findings_are_verified(self):
        """Finding confidence never disables an explicitly requested gate."""
        already_verified = [
            {
                "axis": "correctness",
                "severity": "High",
                "location": "src/app.py:42",
                "finding": "Real bug",
                "recommendation": "Fix it",
                "confidence": 90,  # already ≥80
            },
        ]
        out, meta = run_build_verify.run(
            self.repo, already_verified, "exit 1",
            tool="pytest", tool_available=True, timeout=10,
        )
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["confidence"], 90)  # unchanged
        self.assertEqual(meta["build_status"], "failed")
        self.assertFalse(meta["complete"])


class TestVerifyBuildCli(unittest.TestCase):
    """End-to-end CLI invocation — exercises argparse + sidecar layout."""

    def test_missing_test_command_blocks_with_remediation(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(repo, languages=[], files=[])
            findings_path = _write_findings(repo / "findings.jsonl", [
                {
                    "axis": "correctness", "severity": "High",
                    "location": "x:1", "finding": "f",
                    "recommendation": "r", "confidence": 70,
                },
            ])
            out = repo / "out.jsonl"
            r = subprocess.run(
                [
                    sys.executable, str(RUN_BUILD_VERIFY),
                    "--scope", str(scope),
                    "--findings", str(findings_path),
                    "--output", str(out),
                    "--repo", str(repo),
                ],
                capture_output=True, text=True, timeout=15,
            )
            self.assertEqual(r.returncode, 3, r.stderr)
            self.assertTrue(out.exists())
            lines = [l for l in out.read_text(encoding="utf-8").splitlines() if l.strip()]
            self.assertEqual(len(lines), 1)
            parsed = json.loads(lines[0])
            self.assertEqual(parsed["confidence"], 70)  # unchanged — no build tool
            sidecar = json.loads(
                (out.with_suffix(out.suffix + ".meta.json")).read_text(encoding="utf-8")
            )
            self.assertEqual(sidecar["build_status"], "missing-test-command")
            self.assertIn("Add a canonical test entry", r.stderr)
            self.assertIn("`pytest`", r.stderr)
            self.assertIn("`unittest`", r.stderr)
            self.assertIn("ERROR: rerun:", r.stderr)
            self.assertIn(str(RUN_BUILD_VERIFY.resolve()), r.stderr)
            scope_data = json.loads(scope.read_text(encoding="utf-8"))
            self.assertFalse(scope_data["build_coverage"]["complete"])

    def test_exit_2_on_missing_scope(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            r = subprocess.run(
                [
                    sys.executable, str(RUN_BUILD_VERIFY),
                    "--scope", str(repo / "missing.json"),
                    "--findings", str(repo / "f.jsonl"),
                    "--output", str(repo / "o.jsonl"),
                    "--repo", str(repo),
                ],
                capture_output=True, text=True, timeout=5,
            )
        self.assertEqual(r.returncode, 2)
        self.assertIn("scope.json not found", r.stderr)

    def test_invalid_package_json_blocks_with_exact_remediation(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "package.json").write_text("{broken\n", encoding="utf-8")
            scope = _write_scope(repo, languages=["typescript"], files=["app.ts"])
            findings_path = _write_findings(repo / "findings.jsonl", [])
            output = repo / "out.jsonl"

            result = subprocess.run(
                [
                    sys.executable,
                    str(RUN_BUILD_VERIFY),
                    "--scope",
                    str(scope),
                    "--findings",
                    str(findings_path),
                    "--output",
                    str(output),
                    "--repo",
                    str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )

            scope_data = json.loads(scope.read_text(encoding="utf-8"))

        self.assertEqual(result.returncode, 4)
        self.assertIn("project manifest is invalid", result.stderr)
        self.assertIn("Repair package.json so it is valid JSON", result.stderr)
        self.assertIn("ERROR: rerun:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(
            scope_data["build_coverage"]["build_status"],
            "invalid-manifest",
        )

    def test_invalid_rerun_input_invalidates_stale_build_state_and_output(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(repo, languages=["python"], files=["app.py"])
            scope_data = json.loads(scope.read_text(encoding="utf-8"))
            scope_data.update({
                "tool_coverage": {"complete": True},
                "axis_coverage": {"complete": True},
                "validator_coverage": {"complete": True},
                "build_coverage": {
                    "complete": True,
                    "applicable": True,
                    "build_status": "passed",
                },
                "coverage_complete": True,
            })
            scope.write_text(json.dumps(scope_data), encoding="utf-8")
            out = repo / "build-findings.jsonl"
            out.write_text("stale\n", encoding="utf-8")
            out.with_suffix(out.suffix + ".meta.json").write_text(
                '{"complete": true}\n',
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable, str(RUN_BUILD_VERIFY),
                    "--scope", str(scope),
                    "--findings", str(repo / "missing-findings.jsonl"),
                    "--output", str(out),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            self.assertEqual(result.returncode, 4, result.stderr)
            self.assertIn("Rerun the axis and validator phases", result.stderr)
            self.assertIn("ERROR: rerun:", result.stderr)
            mutated = json.loads(scope.read_text(encoding="utf-8"))
            self.assertFalse(mutated["build_coverage"]["complete"])
            self.assertEqual(
                mutated["build_coverage"]["build_status"],
                "invalid-input",
            )
            self.assertFalse(mutated["coverage_complete"])
            self.assertFalse(out.exists())
            self.assertFalse(out.with_suffix(out.suffix + ".meta.json").exists())

    def test_detected_unittest_suite_with_zero_collected_tests_blocks(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "test_empty.py").write_text(
                "import unittest\n# def test_placeholder(): pass\n",
                encoding="utf-8",
            )
            scope = _write_scope(repo, languages=["python"], files=["test_empty.py"])
            findings_path = _write_findings(repo / "findings.jsonl", [])
            out = repo / "out.jsonl"
            result = subprocess.run(
                [
                    sys.executable,
                    str(RUN_BUILD_VERIFY),
                    "--scope",
                    str(scope),
                    "--findings",
                    str(findings_path),
                    "--output",
                    str(out),
                    "--repo",
                    str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertEqual(result.returncode, 4, result.stderr)
            self.assertIn("no-tests-collected", result.stderr)
            self.assertIn("Add at least one collectable test", result.stderr)
            self.assertIn("python3 -m unittest discover", result.stderr)
            self.assertIn("ERROR: rerun:", result.stderr)

    def test_detected_failing_suite_prints_direct_fix_and_exact_rerun(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "test_failure.py").write_text(
                "import unittest\n"
                "class Failure(unittest.TestCase):\n"
                "    def test_failure(self):\n"
                "        self.fail('expected failure')\n",
                encoding="utf-8",
            )
            scope = _write_scope(repo, languages=["python"], files=["test_failure.py"])
            findings_path = _write_findings(repo / "findings.jsonl", [])
            out = repo / "out.jsonl"
            result = subprocess.run(
                [
                    sys.executable,
                    str(RUN_BUILD_VERIFY),
                    "--scope",
                    str(scope),
                    "--findings",
                    str(findings_path),
                    "--output",
                    str(out),
                    "--repo",
                    str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertEqual(result.returncode, 4, result.stderr)
            self.assertIn("build verification failed: failed", result.stderr)
            self.assertIn("Run `python3 -m unittest discover` directly", result.stderr)
            self.assertIn("ERROR: rerun:", result.stderr)
            self.assertIn(str(scope), result.stderr)


# ---------------------------------------------------------------------------
# `--mutation-test` — Phase 2 extension
# ---------------------------------------------------------------------------


class TestMutationDryRun(unittest.TestCase):
    """Toggle + atomic-preflight contracts for `scripts/run_mutation.sh`."""

    def _run(self, repo: Path, *, env: dict | None = None,
             languages: list[str] | None = None,
             files: list[str] | None = None) -> subprocess.CompletedProcess:
        scope = _write_scope(
            repo,
            languages=languages or [],
            files=files or [],
        )
        out_dir = repo / "out"
        out_dir.mkdir()
        merged_env = {**os.environ, **(env or {})}
        return subprocess.run(
            [
                "bash", str(RUN_MUTATION),
                "--scope", str(scope),
                "--output-dir", str(out_dir),
                "--repo", str(repo),
            ],
            capture_output=True, text=True, timeout=15, env=merged_env,
        )

    def test_dry_run_exits_clean_with_empty_findings(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            _configure_mutmut(repo)
            bin_dir = repo / "bin"
            _write_executable(bin_dir / "mutmut")
            r = self._run(
                repo, env={
                    "MUTATION_DRY_RUN": "1",
                    "PATH": f"{bin_dir}:/usr/bin:/bin",
                },
                languages=["python"], files=["x.py"],
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            # The exit-zero path must produce an empty findings file
            # (truncated at start) — downstream JSONL readers stay happy.
            out_file = Path(t) / "out" / "mutation-findings.jsonl"
            self.assertTrue(out_file.exists())
            self.assertEqual(out_file.read_text(encoding="utf-8"), "")
            self.assertIn("MUTATION_DRY_RUN=1", r.stderr)
            coverage = json.loads((repo / "scope.json").read_text())["mutation_coverage"]
            self.assertFalse(coverage["complete"])
            self.assertEqual(coverage["status"], "dry-run")

    def test_malformed_scope_blocks_with_exact_recovery(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = repo / "scope.json"
            scope.write_text("{broken\n", encoding="utf-8")
            out_dir = repo / "out"
            out_dir.mkdir()

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("invalid Code Ultrareview scope", result.stderr)
        self.assertIn("rerun scope.py", result.stderr)
        self.assertIn("ERROR: rerun:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_malformed_package_manifest_blocks_before_mutation_output(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(repo, languages=["javascript"], files=["x.js"])
            (repo / "package.json").write_text("{broken\n", encoding="utf-8")
            out_dir = repo / "out"
            out_dir.mkdir()

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("invalid project manifest", result.stderr)
            self.assertIn("repair package.json", result.stderr)
            self.assertIn("ERROR: rerun:", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertFalse((out_dir / "mutation-findings.jsonl").exists())

    def test_malformed_package_manifest_invalidates_stale_mutation_success(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(repo, languages=["javascript"], files=["x.js"])
            scope_data = json.loads(scope.read_text(encoding="utf-8"))
            scope_data["mutation_coverage"] = {
                "requested": True,
                "complete": True,
                "applicable": True,
                "status": "complete",
            }
            scope_data["coverage_complete"] = True
            scope.write_text(
                json.dumps(scope_data, indent=2) + "\n", encoding="utf-8"
            )
            (repo / "package.json").write_text("{broken\n", encoding="utf-8")
            out_dir = repo / "out"
            out_dir.mkdir()
            stale = out_dir / "mutation-findings.jsonl"
            stale.write_text('{"finding":"stale"}\n', encoding="utf-8")

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            mutated = json.loads(scope.read_text(encoding="utf-8"))
            stale_exists = stale.exists()

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertFalse(mutated["mutation_coverage"]["complete"])
        self.assertEqual(mutated["mutation_coverage"]["status"], "preflight")
        self.assertFalse(mutated["coverage_complete"])
        self.assertFalse(stale_exists)

    def test_malformed_python_mutation_manifest_blocks_as_invalid_input(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(repo, languages=["python"], files=["x.py"])
            (repo / "pyproject.toml").write_text(
                "[tool.mutmut\nsource_paths = [\"src\"]\n",
                encoding="utf-8",
            )
            out_dir = repo / "out"
            out_dir.mkdir()
            bin_dir = repo / "bin"
            _write_executable(
                bin_dir / "python3", f'exec "{sys.executable}" "$@"'
            )

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin"},
            )

            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("pyproject.toml is not valid TOML", result.stderr)
            self.assertIn("standard-library tomllib", result.stderr)
            self.assertIn("ERROR: rerun:", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_python_mutation_pyproject_without_tomllib_blocks_explicitly(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(repo, languages=["python"], files=["x.py"])
            (repo / "pyproject.toml").write_text(
                '[tool.mutmut]\nsource_paths = ["src"]\n', encoding="utf-8"
            )
            out_dir = repo / "out"
            out_dir.mkdir()
            bin_dir = repo / "bin"
            _write_executable(
                bin_dir / "python3", f'exec "{sys.executable}" "$@"'
            )
            hook_dir = repo / "python-hook"
            hook_dir.mkdir()
            (hook_dir / "sitecustomize.py").write_text(
                "import builtins\n"
                "original_import = builtins.__import__\n"
                "def guarded_import(name, *args, **kwargs):\n"
                "    if name == 'tomllib':\n"
                "        raise ModuleNotFoundError(name)\n"
                "    return original_import(name, *args, **kwargs)\n"
                "builtins.__import__ = guarded_import\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=10,
                env={
                    **os.environ,
                    "PATH": f"{bin_dir}:/usr/bin:/bin",
                    "PYTHONPATH": str(hook_dir),
                },
            )

            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("Python 3.11+ is required", result.stderr)
            self.assertIn("standard-library tomllib", result.stderr)
            self.assertIn("ERROR: rerun:", result.stderr)
            self.assertFalse((out_dir / "mutation-findings.jsonl").exists())

    def test_malformed_pom_blocks_as_invalid_input(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(repo, languages=["java"], files=["X.java"])
            (repo / "pom.xml").write_text("<project>", encoding="utf-8")
            out_dir = repo / "out"
            out_dir.mkdir()

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("pom.xml is not valid XML", result.stderr)
            self.assertIn("ET.parse", result.stderr)
            self.assertIn("ERROR: rerun:", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_no_languages_is_not_applicable(self):
        """Empty scope has complete, explicitly not-applicable coverage."""
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            r = self._run(repo, languages=[], files=[])
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("not applicable", r.stderr)
            coverage = json.loads((repo / "scope.json").read_text())["mutation_coverage"]
            self.assertTrue(coverage["complete"])
            self.assertFalse(coverage["applicable"])
            self.assertEqual(coverage["status"], "not-applicable")

    def test_mutation_publish_failure_keeps_coverage_incomplete(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(repo, languages=[], files=[])
            out_dir = repo / "out"
            out_dir.mkdir()
            bin_dir = repo / "bin"
            _write_executable(
                bin_dir / "mv",
                'target="${!#}"\n'
                '[[ "$target" == */mutation-findings.jsonl ]] && exit 73\n'
                'exec /bin/mv "$@"',
            )

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin"},
            )

            coverage = json.loads(scope.read_text(encoding="utf-8"))["mutation_coverage"]
            self.assertEqual(result.returncode, 4, result.stderr)
            self.assertIn("could not be published atomically", result.stderr)
            self.assertIn("same-directory rename", result.stderr)
            self.assertIn("ERROR: rerun:", result.stderr)
            self.assertFalse(coverage["complete"])
            self.assertEqual(coverage["status"], "failed")
            self.assertFalse((out_dir / "mutation-findings.jsonl").exists())
            self.assertFalse((out_dir / ".mutation-findings.pending.jsonl").exists())

    def test_mutation_coverage_persist_failure_discards_findings(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(repo, languages=[], files=[])
            out_dir = repo / "out"
            out_dir.mkdir()
            bin_dir = repo / "bin"
            _write_executable(
                bin_dir / "mv",
                f'/bin/mv "$@" || exit $?\nchmod 0555 {str(repo)!r}',
            )

            try:
                result = subprocess.run(
                    [
                        "bash", str(RUN_MUTATION),
                        "--scope", str(scope),
                        "--output-dir", str(out_dir),
                        "--repo", str(repo),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin"},
                )
            finally:
                repo.chmod(0o755)

            coverage = json.loads(scope.read_text(encoding="utf-8"))["mutation_coverage"]
            self.assertEqual(result.returncode, 4, result.stderr)
            self.assertIn("coverage state could not be persisted", result.stderr)
            self.assertIn("atomic replacement", result.stderr)
            self.assertFalse(coverage["complete"])
            self.assertFalse((out_dir / "mutation-findings.jsonl").exists())

    def test_initial_coverage_publish_failure_invalidates_stale_outputs(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(repo, languages=[], files=[])
            out_dir = repo / "out"
            raw_dir = out_dir / "raw"
            raw_dir.mkdir(parents=True)
            stale_paths = (
                out_dir / "mutation-findings.jsonl",
                out_dir / "mutation-preflight.json",
                raw_dir / "mutation-preflight.stdout",
                raw_dir / "mutation-preflight.stderr",
            )
            for stale in stale_paths:
                stale.write_text("stale\n", encoding="utf-8")
            hook_dir = repo / "python-hook"
            hook_dir.mkdir()
            (hook_dir / "sitecustomize.py").write_text(
                "import os\n"
                "_real_replace = os.replace\n"
                "def guarded_replace(source, destination):\n"
                "    if str(destination).endswith('scope.json'):\n"
                "        raise OSError('simulated coverage publication failure')\n"
                "    return _real_replace(source, destination)\n"
                "os.replace = guarded_replace\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, "PYTHONPATH": str(hook_dir)},
            )

            self.assertEqual(result.returncode, 4, result.stderr)
            self.assertIn("could not initialize mutation coverage", result.stderr)
            self.assertIn("atomic replacement", result.stderr)
            self.assertIn("ERROR: rerun:", result.stderr)
            for stale in stale_paths:
                self.assertFalse(stale.exists(), stale)
            self.assertEqual(list(repo.glob(".scope.json.*.tmp")), [])

    def test_preflight_publish_failure_invalidates_stale_outputs(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            _configure_mutmut(repo)
            scope = _write_scope(repo, languages=["python"], files=["x.py"])
            out_dir = repo / "out"
            raw_dir = out_dir / "raw"
            raw_dir.mkdir(parents=True)
            (out_dir / "mutation-preflight.json").write_text(
                '{"status":"stale"}\n', encoding="utf-8"
            )
            (raw_dir / "mutation-preflight.stdout").write_text(
                "stale\n", encoding="utf-8"
            )
            bin_dir = repo / "bin"
            _write_executable(bin_dir / "mutmut")
            hook_dir = repo / "python-hook"
            hook_dir.mkdir()
            (hook_dir / "sitecustomize.py").write_text(
                "import os\n"
                "_real_replace = os.replace\n"
                "def guarded_replace(source, destination):\n"
                "    if str(destination).endswith('mutation-preflight.json'):\n"
                "        raise OSError('simulated preflight publication failure')\n"
                "    return _real_replace(source, destination)\n"
                "os.replace = guarded_replace\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=15,
                env={
                    **os.environ,
                    "MUTATION_DRY_RUN": "1",
                    "PATH": f"{bin_dir}:{os.environ['PATH']}",
                    "PYTHONPATH": str(hook_dir),
                },
            )
            coverage = json.loads(scope.read_text(encoding="utf-8"))[
                "mutation_coverage"
            ]

            self.assertEqual(result.returncode, 4, result.stderr)
            self.assertIn("could not be published atomically", result.stderr)
            self.assertIn("same-directory atomic replacement", result.stderr)
            self.assertIn("ERROR: rerun:", result.stderr)
            self.assertEqual(coverage["status"], "failed")
            self.assertFalse(coverage["complete"])
            self.assertFalse((out_dir / "mutation-preflight.json").exists())
            self.assertFalse((raw_dir / "mutation-preflight.stdout").exists())
            self.assertEqual(
                list(out_dir.glob(".mutation-preflight.json.*.tmp")), []
            )
            self.assertEqual(
                list(raw_dir.glob(".mutation-preflight.stdout.*")), []
            )

    def test_python_without_mutmut_blocks_with_install_command(self):
        """When mutmut is absent from PATH, mutation coverage cannot start."""
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            _configure_mutmut(repo)
            scope = _write_scope(repo, languages=["python"], files=["x.py"])
            out_dir = repo / "out"; out_dir.mkdir()
            # Reset PATH inside the script so mutmut is guaranteed absent.
            r = subprocess.run(
                [
                    "bash", "-c",
                    f'export PATH=/usr/bin:/bin && bash {RUN_MUTATION} '
                    f'--scope {scope} --output-dir {out_dir} --repo {repo}',
                ],
                capture_output=True, text=True, timeout=10,
            )
            self.assertEqual(r.returncode, 3, r.stderr)
            self.assertIn("mutation prerequisite 'mutmut' is missing", r.stderr)
            self.assertIn("pipx install mutmut", r.stderr)

    def test_mutation_source_has_no_runtime_package_resolver(self):
        text = RUN_MUTATION.read_text(encoding="utf-8")
        self.assertNotRegex(text, r"\bnpx\b")
        self.assertNotRegex(text, r"\buvx\b")

    def test_yarn_pnp_preflight_disables_corepack_network_resolution(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "package.json").write_text(
                json.dumps({
                    "packageManager": "yarn@4.9.2",
                    "devDependencies": {"@stryker-mutator/core": "9.2.0"},
                }),
                encoding="utf-8",
            )
            (repo / "yarn.lock").write_text("", encoding="utf-8")
            (repo / "stryker.config.json").write_text("{}\n", encoding="utf-8")
            bin_dir = repo / "bin"
            _write_executable(
                bin_dir / "yarn",
                '[[ "${COREPACK_ENABLE_NETWORK-}" == "0" ]] || exit 66\n'
                '[[ "${COREPACK_DEFAULT_TO_LATEST-}" == "0" ]] || exit 67\n'
                '[[ "${YARN_ENABLE_NETWORK-}" == "0" ]] || exit 68\n'
                '[[ "$3" == "bin" && "$4" == "stryker" ]] || exit 69',
            )

            result = self._run(
                repo,
                env={
                    "MUTATION_DRY_RUN": "1",
                    "PATH": f"{bin_dir}:/usr/bin:/bin",
                },
                languages=["javascript"],
                files=["src/app.js"],
            )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_yarn_pnp_config_guidance_is_offline_and_cwd_explicit(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "package.json").write_text(
                json.dumps({
                    "packageManager": "yarn@4.9.2",
                    "devDependencies": {"@stryker-mutator/core": "9.2.0"},
                }),
                encoding="utf-8",
            )
            (repo / "yarn.lock").write_text("", encoding="utf-8")
            bin_dir = repo / "bin"
            _write_executable(
                bin_dir / "yarn",
                '[[ "${COREPACK_ENABLE_NETWORK-}" == "0" ]] || exit 66\n'
                '[[ "${COREPACK_DEFAULT_TO_LATEST-}" == "0" ]] || exit 67\n'
                '[[ "${YARN_ENABLE_NETWORK-}" == "0" ]] || exit 68\n'
                '[[ "$3" == "bin" && "$4" == "stryker" ]] || exit 69',
            )

            result = self._run(
                repo,
                env={"PATH": f"{bin_dir}:/usr/bin:/bin"},
                languages=["javascript"],
                files=["src/app.js"],
            )

        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertIn("no stryker.config.* file", result.stderr)
        self.assertIn("COREPACK_ENABLE_NETWORK=0", result.stderr)
        self.assertIn("COREPACK_DEFAULT_TO_LATEST=0", result.stderr)
        self.assertIn("YARN_ENABLE_NETWORK=0", result.stderr)
        self.assertIn(f"yarn --cwd {repo.resolve()} run -B stryker init", result.stderr)

    def test_nested_yarn_pnp_config_guidance_targets_declaring_workspace(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            package_dir = repo / "packages" / "app"
            package_dir.mkdir(parents=True)
            (repo / "package.json").write_text(
                json.dumps({
                    "packageManager": "yarn@4.9.2",
                    "workspaces": ["packages/*"],
                }),
                encoding="utf-8",
            )
            (repo / "yarn.lock").write_text("", encoding="utf-8")
            (package_dir / "package.json").write_text(
                json.dumps({
                    "devDependencies": {"@stryker-mutator/core": "9.2.0"},
                }),
                encoding="utf-8",
            )
            bin_dir = repo / "bin"
            _write_executable(
                bin_dir / "yarn",
                '[[ "${COREPACK_ENABLE_NETWORK-}" == "0" ]] || exit 66\n'
                '[[ "${COREPACK_DEFAULT_TO_LATEST-}" == "0" ]] || exit 67\n'
                '[[ "${YARN_ENABLE_NETWORK-}" == "0" ]] || exit 68\n'
                '[[ "$3" == "bin" && "$4" == "stryker" ]] || exit 69',
            )

            result = self._run(
                repo,
                env={"PATH": f"{bin_dir}:/usr/bin:/bin"},
                languages=["javascript"],
                files=["packages/app/src/app.js"],
            )

        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertIn("no stryker.config.* file", result.stderr)
        self.assertIn(
            f"yarn --cwd {package_dir.resolve()} run -B stryker init",
            result.stderr,
        )
        self.assertNotIn(
            f"yarn --cwd {repo.resolve()} run -B stryker init",
            result.stderr,
        )

    def test_yarn_pnp_without_lockfile_requires_reviewed_lock_restore(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "package.json").write_text(
                json.dumps({
                    "packageManager": "yarn@4.9.2",
                    "devDependencies": {"@stryker-mutator/core": "9.2.0"},
                }),
                encoding="utf-8",
            )
            (repo / "stryker.config.json").write_text("{}\n", encoding="utf-8")
            bin_dir = repo / "bin"
            _write_executable(bin_dir / "yarn", "exit 1")

            result = self._run(
                repo,
                env={
                    "MUTATION_DRY_RUN": "1",
                    "PATH": f"{bin_dir}:/usr/bin:/bin",
                },
                languages=["javascript"],
                files=["src/app.js"],
            )

        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertIn(f"Restore {repo.resolve()}/yarn.lock", result.stderr)
        self.assertIn("create and review it deliberately", result.stderr)
        self.assertIn(
            f"yarn --cwd {repo.resolve()} install --immutable",
            result.stderr,
        )
        self.assertNotIn("yarn add", result.stderr)

    def test_workspace_stryker_uses_hoisted_binary_and_normalizes_report_path(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            package_dir = repo / "packages" / "app"
            (repo / "package.json").write_text(
                json.dumps({"workspaces": ["packages/*"]}), encoding="utf-8"
            )
            (repo / "package-lock.json").write_text("{}\n", encoding="utf-8")
            package_dir.mkdir(parents=True)
            (package_dir / "package.json").write_text(
                json.dumps({
                    "devDependencies": {"@stryker-mutator/core": "9.2.0"},
                }),
                encoding="utf-8",
            )
            (package_dir / "stryker.config.json").write_text(
                "{}\n", encoding="utf-8"
            )
            report = json.dumps({
                "files": {
                    "src/app.js": {
                        "mutants": [{
                            "status": "Survived",
                            "mutatorName": "BooleanLiteral",
                            "description": "flip boolean",
                            "location": {"start": {"line": 7, "column": 2}},
                        }],
                    },
                },
            })
            _write_executable(
                repo / "node_modules" / ".bin" / "stryker",
                "mkdir -p reports/mutation\n"
                f"printf '%s\\n' '{report}' > reports/mutation/mutation.json",
            )
            scope = _write_scope(
                repo,
                languages=["javascript"],
                files=["packages/app/src/app.js"],
            )
            out_dir = repo / "out"
            out_dir.mkdir()

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )
            findings = [
                json.loads(line)
                for line in (out_dir / "mutation-findings.jsonl").read_text(
                    encoding="utf-8"
                ).splitlines()
            ]

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["location"], "packages/app/src/app.js:7:2")

    def test_multiple_workspace_stryker_declarations_block_atomically(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "package.json").write_text(
                json.dumps({"workspaces": ["packages/*"]}), encoding="utf-8"
            )
            for name in ("a", "b"):
                package_dir = repo / "packages" / name
                package_dir.mkdir(parents=True)
                (package_dir / "package.json").write_text(
                    json.dumps({
                        "devDependencies": {"@stryker-mutator/core": "9.2.0"},
                    }),
                    encoding="utf-8",
                )
                (package_dir / "stryker.config.json").write_text(
                    "{}\n", encoding="utf-8"
                )

            result = self._run(
                repo,
                env={"MUTATION_DRY_RUN": "1"},
                languages=["javascript"],
                files=["packages/a/src/a.js", "packages/b/src/b.js"],
            )
            final_exists = (repo / "out" / "mutation-findings.jsonl").exists()

        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertIn("multiple Stryker declarations", result.stderr)
        self.assertIn(
            "npm install --save-dev @stryker-mutator/core", result.stderr
        )
        self.assertIn("packages/a", result.stderr)
        self.assertIn("packages/b", result.stderr)
        self.assertFalse(final_exists)

    def test_partial_workspace_stryker_declaration_reports_exact_root_repair(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "package.json").write_text(
                json.dumps({"workspaces": ["packages/*"]}), encoding="utf-8"
            )
            declared = repo / "packages" / "a"
            declared.mkdir(parents=True)
            (declared / "package.json").write_text(
                json.dumps({
                    "devDependencies": {"@stryker-mutator/core": "9.2.0"},
                }),
                encoding="utf-8",
            )
            uncovered = repo / "packages" / "b"
            uncovered.mkdir(parents=True)
            (uncovered / "package.json").write_text(
                json.dumps({"name": "b"}), encoding="utf-8"
            )

            result = self._run(
                repo,
                env={"MUTATION_DRY_RUN": "1"},
                languages=["javascript"],
                files=["packages/a/src/a.js", "packages/b/src/b.js"],
            )
            final_exists = (repo / "out" / "mutation-findings.jsonl").exists()

        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertIn(
            "only partially covered by Stryker declaration", result.stderr
        )
        self.assertIn(str(declared.resolve()), result.stderr)
        self.assertIn("packages/b/src/b.js", result.stderr)
        self.assertIn(
            f"from {repo.resolve()} run: "
            "npm install --save-dev @stryker-mutator/core",
            result.stderr,
        )
        self.assertFalse(final_exists)

    def test_nested_stryker_runtime_failure_prints_exact_restore_and_rerun(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            package_dir = repo / "packages" / "app"
            (repo / "package.json").write_text(
                json.dumps({"workspaces": ["packages/*"]}), encoding="utf-8"
            )
            (repo / "package-lock.json").write_text("{}\n", encoding="utf-8")
            package_dir.mkdir(parents=True)
            (package_dir / "package.json").write_text(
                json.dumps({
                    "devDependencies": {"@stryker-mutator/core": "9.2.0"},
                }),
                encoding="utf-8",
            )
            (package_dir / "stryker.config.json").write_text(
                "{}\n", encoding="utf-8"
            )
            _write_executable(repo / "node_modules" / ".bin" / "stryker", "exit 7")

            result = self._run(
                repo,
                languages=["javascript"],
                files=["packages/app/src/app.js"],
            )
            final_exists = (repo / "out" / "mutation-findings.jsonl").exists()

        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertIn("Stryker failed with exit code 7", result.stderr)
        self.assertIn(
            f"repair/install: npm --prefix {repo.resolve()} ci", result.stderr
        )
        self.assertIn("ERROR: rerun: bash", result.stderr)
        self.assertFalse(final_exists)

    def test_declared_stryker_never_falls_back_to_global_binary(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "package.json").write_text(
                json.dumps({
                    "packageManager": "npm@11.4.2",
                    "devDependencies": {"@stryker-mutator/core": "9.2.0"},
                }),
                encoding="utf-8",
            )
            (repo / "package-lock.json").write_text("{}\n", encoding="utf-8")
            (repo / "stryker.config.json").write_text("{}\n", encoding="utf-8")
            bin_dir = repo / "bin"
            _write_executable(bin_dir / "stryker")

            result = self._run(
                repo,
                env={
                    "MUTATION_DRY_RUN": "1",
                    "PATH": f"{bin_dir}:/usr/bin:/bin",
                },
                languages=["javascript"],
                files=["src/app.js"],
            )

        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertIn("declared Stryker binary is unavailable", result.stderr)
        self.assertIn(f"npm --prefix {repo.resolve()} ci", result.stderr)
        self.assertNotIn("--save-dev @stryker-mutator/core", result.stderr)

    def test_invalid_stryker_schema_blocks_atomically(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(repo, languages=["javascript"], files=["x.js"])
            (repo / "package.json").write_text(
                json.dumps({
                    "devDependencies": {"@stryker-mutator/core": "1.0.0"},
                }),
                encoding="utf-8",
            )
            (repo / "stryker.config.json").write_text("{}\n", encoding="utf-8")
            _write_executable(
                repo / "node_modules" / ".bin" / "stryker",
                "mkdir -p reports/mutation\n"
                "printf '%s\\n' '{}' > reports/mutation/mutation.json",
            )
            out_dir = repo / "out"
            out_dir.mkdir()

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )
        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertIn("non-empty files object is required", result.stderr)
        self.assertFalse((out_dir / "mutation-findings.jsonl").exists())

    def test_stryker_no_coverage_is_a_finding(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(repo, languages=["javascript"], files=["x.js"])
            (repo / "package.json").write_text(
                json.dumps({
                    "devDependencies": {"@stryker-mutator/core": "1.0.0"},
                }),
                encoding="utf-8",
            )
            (repo / "stryker.config.json").write_text("{}\n", encoding="utf-8")
            report = json.dumps({
                "files": {
                    "x.js": {
                        "mutants": [{
                            "status": "NoCoverage",
                            "mutatorName": "BooleanLiteral",
                            "description": "flip boolean",
                            "location": {"start": {"line": 1, "column": 0}},
                        }],
                    },
                },
            })
            _write_executable(
                repo / "node_modules" / ".bin" / "stryker",
                "mkdir -p reports/mutation\n"
                f"printf '%s\\n' '{report}' > reports/mutation/mutation.json",
            )
            out_dir = repo / "out"
            out_dir.mkdir()

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )
            findings_text = (out_dir / "mutation-findings.jsonl").read_text(
                encoding="utf-8"
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        finding = json.loads(findings_text)
        self.assertIn("Uncovered mutant", finding["finding"])

    def test_stryker_incomplete_statuses_block_atomically(self):
        for status in ("Ignored", "Pending"):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as t:
                repo = Path(t)
                scope = _write_scope(
                    repo,
                    languages=["javascript"],
                    files=["x.js"],
                )
                (repo / "package.json").write_text(
                    json.dumps({
                        "devDependencies": {"@stryker-mutator/core": "1.0.0"},
                    }),
                    encoding="utf-8",
                )
                (repo / "stryker.config.json").write_text(
                    "{}\n", encoding="utf-8"
                )
                report = json.dumps({
                    "files": {
                        "x.js": {
                            "mutants": [{"status": status}],
                        },
                    },
                })
                _write_executable(
                    repo / "node_modules" / ".bin" / "stryker",
                    "mkdir -p reports/mutation\n"
                    f"printf '%s\\n' '{report}' > reports/mutation/mutation.json",
                )
                out_dir = repo / "out"
                out_dir.mkdir()

                result = subprocess.run(
                    [
                        "bash", str(RUN_MUTATION),
                        "--scope", str(scope),
                        "--output-dir", str(out_dir),
                        "--repo", str(repo),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )

                self.assertEqual(result.returncode, 4, result.stderr)
                self.assertIn("incomplete Stryker results", result.stderr)
                self.assertIn(status, result.stderr)
                self.assertFalse(
                    (out_dir / "mutation-findings.jsonl").exists()
                )

    def test_mutmut_empty_results_block_as_zero_evaluation(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(repo, languages=["python"], files=["x.py"])
            _configure_mutmut(repo)
            bin_dir = repo / "bin"
            _write_executable(
                bin_dir / "mutmut",
                'case "${1:-}" in run|results) exit 0 ;; *) exit 2 ;; esac',
            )
            out_dir = repo / "out"
            out_dir.mkdir()

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=15,
                env={**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"},
            )
        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertIn("no mutants were evaluated", result.stderr)
        self.assertIn("mutmut results --all", result.stderr)
        self.assertFalse((out_dir / "mutation-findings.jsonl").exists())

    def test_mutmut_all_killed_changed_file_results_are_complete(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(repo, languages=["python"], files=["x.py"])
            _configure_mutmut(repo)
            bin_dir = repo / "bin"
            _write_executable(
                bin_dir / "mutmut",
                'if [[ "${1:-}" == "run" ]]; then exit 0; fi\n'
                'if [[ "${1:-}" == "results" && "${2:-}" == "--all" ]]; then\n'
                '  echo "x.x__mutmut_1: killed"; exit 0\n'
                'fi\n'
                'if [[ "${1:-}" == "show" ]]; then\n'
                "  printf '%s\\n' '--- a/x.py' '+++ b/x.py' '@@ -1 +1 @@' '-old' '+new'\n"
                '  exit 0\n'
                'fi\n'
                "exit 2",
            )
            out_dir = repo / "out"
            out_dir.mkdir()

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=15,
                env={**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"},
            )
            findings_text = (out_dir / "mutation-findings.jsonl").read_text(
                encoding="utf-8"
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(findings_text, "")

    def test_mutmut_caught_by_type_check_is_terminal_and_diff_scoped(self):
        for mapped_file, expected_rc in (("x.py", 0), ("y.py", 4)):
            with self.subTest(mapped_file=mapped_file), tempfile.TemporaryDirectory() as t:
                repo = Path(t)
                scope = _write_scope(repo, languages=["python"], files=["x.py"])
                _configure_mutmut(repo)
                bin_dir = repo / "bin"
                _write_executable(
                    bin_dir / "mutmut",
                    'if [[ "${1:-}" == "run" ]]; then exit 0; fi\n'
                    'if [[ "${1:-}" == "results" && "${2:-}" == "--all" ]]; then\n'
                    '  echo "x.x__mutmut_1: caught by type check"; exit 0\n'
                    'fi\n'
                    'if [[ "${1:-}" == "show" ]]; then\n'
                    f"  printf '%s\\n' '--- a/{mapped_file}' '+++ b/{mapped_file}' '@@ -1 +1 @@' '-old' '+new'\n"
                    '  exit 0\n'
                    'fi\n'
                    "exit 2",
                )
                out_dir = repo / "out"
                out_dir.mkdir()

                result = subprocess.run(
                    [
                        "bash", str(RUN_MUTATION),
                        "--scope", str(scope),
                        "--output-dir", str(out_dir),
                        "--repo", str(repo),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    env={**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"},
                )

                self.assertEqual(result.returncode, expected_rc, result.stderr)
                if expected_rc == 0:
                    self.assertEqual(
                        (out_dir / "mutation-findings.jsonl").read_text(
                            encoding="utf-8"
                        ),
                        "",
                    )
                else:
                    self.assertIn(
                        "no changed-file mutants were evaluated", result.stderr
                    )
                    self.assertFalse(
                        (out_dir / "mutation-findings.jsonl").exists()
                    )

    def test_mutmut_all_killed_outside_diff_blocks_completion(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(repo, languages=["python"], files=["x.py"])
            _configure_mutmut(repo)
            bin_dir = repo / "bin"
            _write_executable(
                bin_dir / "mutmut",
                'if [[ "${1:-}" == "run" ]]; then exit 0; fi\n'
                'if [[ "${1:-}" == "results" && "${2:-}" == "--all" ]]; then\n'
                '  echo "y.y__mutmut_1: killed"; exit 0\n'
                'fi\n'
                'if [[ "${1:-}" == "show" ]]; then\n'
                "  printf '%s\\n' '--- a/y.py' '+++ b/y.py' '@@ -1 +1 @@' '-old' '+new'\n"
                '  exit 0\n'
                'fi\n'
                "exit 2",
            )
            out_dir = repo / "out"
            out_dir.mkdir()

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=15,
                env={**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"},
            )
            coverage = json.loads(scope.read_text(encoding="utf-8"))[
                "mutation_coverage"
            ]
            findings_exists = (out_dir / "mutation-findings.jsonl").exists()

        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertIn("no changed-file mutants were evaluated", result.stderr)
        self.assertEqual(coverage["status"], "failed")
        self.assertFalse(coverage["complete"])
        self.assertFalse(findings_exists)

    def test_mutmut_malformed_results_block(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(repo, languages=["python"], files=["x.py"])
            _configure_mutmut(repo)
            bin_dir = repo / "bin"
            _write_executable(
                bin_dir / "mutmut",
                'if [[ "${1:-}" == "run" ]]; then exit 0; fi\n'
                'if [[ "${1:-}" == "results" ]]; then echo malformed; exit 0; fi\n'
                "exit 2",
            )
            out_dir = repo / "out"
            out_dir.mkdir()

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=15,
                env={**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"},
            )

        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertIn("invalid mutmut results line", result.stderr)

    def test_mutmut_skipped_result_blocks_atomically(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(repo, languages=["python"], files=["x.py"])
            _configure_mutmut(repo)
            bin_dir = repo / "bin"
            _write_executable(
                bin_dir / "mutmut",
                'if [[ "${1:-}" == "run" ]]; then exit 0; fi\n'
                'if [[ "${1:-}" == "results" ]]; then\n'
                '  echo "x.x__mutmut_1: skipped"; exit 0\n'
                'fi\n'
                "exit 2",
            )
            out_dir = repo / "out"
            out_dir.mkdir()

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=15,
                env={**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"},
            )

        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertIn("incomplete mutmut results", result.stderr)
        self.assertIn("skipped", result.stderr)
        self.assertFalse((out_dir / "mutation-findings.jsonl").exists())

    def test_mutmut_no_tests_is_a_finding(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(repo, languages=["python"], files=["x.py"])
            _configure_mutmut(repo)
            bin_dir = repo / "bin"
            _write_executable(
                bin_dir / "mutmut",
                'if [[ "${1:-}" == "run" ]]; then exit 0; fi\n'
                'if [[ "${1:-}" == "results" ]]; then\n'
                '  echo "x.x__mutmut_1: no tests"; exit 0\n'
                'fi\n'
                'if [[ "${1:-}" == "show" ]]; then\n'
                "  printf '%s\\n' '--- a/x.py' '+++ b/x.py' '@@ -1 +1 @@' '-old' '+new'\n"
                '  exit 0\n'
                'fi\n'
                "exit 2",
            )
            out_dir = repo / "out"
            out_dir.mkdir()

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=15,
                env={**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"},
            )
            findings_text = (out_dir / "mutation-findings.jsonl").read_text(
                encoding="utf-8"
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        finding = json.loads(findings_text)
        self.assertIn("Uncovered mutmut mutant", finding["finding"])

    def test_mutation_timeout_is_portable(self):
        mutation_text = RUN_MUTATION.read_text(encoding="utf-8")
        timeout_text = (SKILL_SCRIPTS / "process_timeout.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("run_with_timeout", mutation_text)
        self.assertIn("subprocess.Popen", timeout_text)
        self.assertIn("start_new_session=True", timeout_text)
        self.assertIn("os.killpg", timeout_text)
        self.assertNotRegex(mutation_text, r'(^|\s)timeout "\$TIMEOUT"')

    def test_mutation_timeout_interrupts_slow_project_tool(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(repo, languages=["javascript"], files=["x.js"])
            out_dir = repo / "out"
            out_dir.mkdir()
            (repo / "package.json").write_text(
                json.dumps({
                    "devDependencies": {"@stryker-mutator/core": "1.0.0"},
                }),
                encoding="utf-8",
            )
            (repo / "stryker.config.json").write_text("{}\n", encoding="utf-8")
            tool = repo / "node_modules" / ".bin" / "stryker"
            tool.parent.mkdir(parents=True)
            sentinel = repo / "child-completed"
            child = repo / "child.py"
            child.write_text(
                "import pathlib, time\n"
                "time.sleep(1.5)\n"
                f"pathlib.Path({str(sentinel)!r}).write_text('alive')\n",
                encoding="utf-8",
            )
            tool.write_text(
                "#!/usr/bin/env python3\n"
                "import subprocess, sys, time\n"
                f"subprocess.Popen([sys.executable, {str(child)!r}])\n"
                "time.sleep(10)\n",
                encoding="utf-8",
            )
            tool.chmod(0o755)

            r = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                    "--timeout", "1",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            self.assertEqual(r.returncode, 4, r.stderr)
            self.assertIn("timed out after 1s", r.stderr)
            time.sleep(2)
            self.assertFalse(sentinel.exists(), "timeout left a child process running")

    def test_mutmut_results_timeout_terminates_child_processes(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(repo, languages=["python"], files=["x.py"])
            _configure_mutmut(repo)
            out_dir = repo / "out"
            out_dir.mkdir()
            sentinel = repo / "results-child-completed"
            child = repo / "child.py"
            child.write_text(
                "import pathlib, time\n"
                "time.sleep(1.5)\n"
                f"pathlib.Path({str(sentinel)!r}).write_text('alive')\n",
                encoding="utf-8",
            )
            bin_dir = repo / "bin"
            mutmut = bin_dir / "mutmut"
            mutmut.parent.mkdir()
            mutmut.write_text(
                "#!/usr/bin/env python3\n"
                "import subprocess, sys, time\n"
                "if len(sys.argv) > 1 and sys.argv[1] == 'run':\n"
                "    raise SystemExit(0)\n"
                "if len(sys.argv) > 1 and sys.argv[1] == 'results':\n"
                f"    subprocess.Popen([sys.executable, {str(child)!r}])\n"
                "    time.sleep(10)\n"
                "raise SystemExit(2)\n",
                encoding="utf-8",
            )
            mutmut.chmod(0o755)

            r = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                    "--timeout", "1",
                ],
                capture_output=True,
                text=True,
                timeout=5,
                env={**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"},
            )

            self.assertEqual(r.returncode, 4, r.stderr)
            self.assertIn("mutmut results timed out after 1s", r.stderr)
            time.sleep(2)
            self.assertFalse(
                sentinel.exists(), "mutmut results timeout left a child running"
            )

    def test_pitest_nonzero_exit_blocks_even_with_fresh_report(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(
                repo, languages=["java"], files=["src/main/java/App.java"]
            )
            (repo / "pom.xml").write_text(
                "<project><build><plugins><plugin>"
                "<groupId>org.pitest</groupId>"
                "<artifactId>pitest-maven</artifactId>"
                "</plugin></plugins></build></project>\n",
                encoding="utf-8",
            )
            out_dir = repo / "out"
            out_dir.mkdir()
            bin_dir = repo / "bin"
            _write_executable(
                bin_dir / "mvn",
                "mkdir -p target/pit-reports/run\n"
                "printf '%s\\n' '<mutations />' > target/pit-reports/run/mutations.xml\n"
                "exit 1",
            )

            r = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                    "--timeout", "5",
                ],
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"},
            )

            self.assertEqual(r.returncode, 4, r.stderr)
            self.assertIn("Pitest failed with exit code 1", r.stderr)
            self.assertFalse((out_dir / "mutation-findings.jsonl").exists())
            coverage = json.loads(scope.read_text())["mutation_coverage"]
            self.assertFalse(coverage["complete"])
            self.assertEqual(coverage["status"], "failed")

    def test_later_language_failure_discards_earlier_findings_atomically(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(
                repo,
                languages=["javascript", "python"],
                files=["x.js", "x.py"],
            )
            (repo / "package.json").write_text(
                json.dumps({
                    "devDependencies": {"@stryker-mutator/core": "1.0.0"},
                }),
                encoding="utf-8",
            )
            (repo / "stryker.config.json").write_text("{}\n", encoding="utf-8")
            stryker_report = json.dumps({
                "files": {
                    "x.js": {
                        "mutants": [{
                            "status": "Survived",
                            "mutatorName": "BooleanLiteral",
                            "description": "flip boolean",
                            "location": {"start": {"line": 1, "column": 0}},
                        }],
                    },
                },
            })
            _write_executable(
                repo / "node_modules" / ".bin" / "stryker",
                "mkdir -p reports/mutation\n"
                f"printf '%s\\n' '{stryker_report}' > reports/mutation/mutation.json",
            )
            _configure_mutmut(repo)
            bin_dir = repo / "bin"
            _write_executable(
                bin_dir / "mutmut",
                'if [[ "${1:-}" == "run" ]]; then exit 0; fi\n'
                'if [[ "${1:-}" == "results" ]]; then exit 2; fi\n'
                "exit 2",
            )
            out_dir = repo / "out"
            out_dir.mkdir()

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=15,
                env={**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"},
            )

            self.assertEqual(result.returncode, 4, result.stderr)
            self.assertIn("mutmut results failed", result.stderr)
            self.assertFalse((out_dir / "mutation-findings.jsonl").exists())
            self.assertFalse((out_dir / ".mutation-findings.pending.jsonl").exists())
            coverage = json.loads(scope.read_text())["mutation_coverage"]
            self.assertFalse(coverage["complete"])
            self.assertEqual(coverage["status"], "failed")

    def test_invalid_pitest_schema_blocks_atomically(self):
        reports = (
            ("<report />", "root element must be mutations"),
            ("<mutations />", "no mutations were evaluated"),
            (
                '<mutations><mutation status="KILLED">'
                "<sourceFile>Other.java</sourceFile>"
                "<mutatedClass>com.example.Other</mutatedClass>"
                "<lineNumber>1</lineNumber>"
                "</mutation></mutations>",
                "no changed-file mutations were evaluated",
            ),
        )
        for report, expected in reports:
            with self.subTest(report=report), tempfile.TemporaryDirectory() as t:
                repo = Path(t)
                scope = _write_scope(
                    repo,
                    languages=["java"],
                    files=["src/main/java/App.java"],
                )
                (repo / "pom.xml").write_text(
                    "<project><build><plugins><plugin>"
                    "<groupId>org.pitest</groupId>"
                    "<artifactId>pitest-maven</artifactId>"
                    "</plugin></plugins></build></project>\n",
                    encoding="utf-8",
                )
                out_dir = repo / "out"
                out_dir.mkdir()
                bin_dir = repo / "bin"
                _write_executable(
                    bin_dir / "mvn",
                    "mkdir -p target/pit-reports/run\n"
                    f"printf '%s\\n' '{report}' > target/pit-reports/run/mutations.xml",
                )

                result = subprocess.run(
                    [
                        "bash", str(RUN_MUTATION),
                        "--scope", str(scope),
                        "--output-dir", str(out_dir),
                        "--repo", str(repo),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    env={**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"},
                )
            self.assertEqual(result.returncode, 4, result.stderr)
            self.assertIn(expected, result.stderr)
            self.assertFalse((out_dir / "mutation-findings.jsonl").exists())

    def test_pitest_all_killed_changed_file_is_complete(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            changed = "src/main/java/com/example/App.java"
            scope = _write_scope(repo, languages=["java"], files=[changed])
            (repo / "pom.xml").write_text(
                "<project><build><plugins><plugin>"
                "<groupId>org.pitest</groupId>"
                "<artifactId>pitest-maven</artifactId>"
                "</plugin></plugins></build></project>\n",
                encoding="utf-8",
            )
            report = (
                '<mutations><mutation status="KILLED">'
                "<sourceFile>App.java</sourceFile>"
                "<mutatedClass>com.example.App</mutatedClass>"
                "<lineNumber>11</lineNumber>"
                "</mutation></mutations>"
            )
            out_dir = repo / "out"
            out_dir.mkdir()
            bin_dir = repo / "bin"
            _write_executable(
                bin_dir / "mvn",
                "mkdir -p target/pit-reports/run\n"
                f"printf '%s\\n' '{report}' > target/pit-reports/run/mutations.xml",
            )

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"},
            )
            findings_text = (out_dir / "mutation-findings.jsonl").read_text(
                encoding="utf-8"
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(findings_text, "")

    def test_pitest_unknown_changed_file_status_blocks_atomically(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            changed = "src/main/java/com/example/App.java"
            scope = _write_scope(repo, languages=["java"], files=[changed])
            (repo / "pom.xml").write_text(
                "<project><build><plugins><plugin>"
                "<groupId>org.pitest</groupId>"
                "<artifactId>pitest-maven</artifactId>"
                "</plugin></plugins></build></project>\n",
                encoding="utf-8",
            )
            report = (
                '<mutations><mutation status="QUEUED">'
                "<sourceFile>App.java</sourceFile>"
                "<mutatedClass>com.example.App</mutatedClass>"
                "<lineNumber>11</lineNumber>"
                "</mutation></mutations>"
            )
            out_dir = repo / "out"
            out_dir.mkdir()
            bin_dir = repo / "bin"
            _write_executable(
                bin_dir / "mvn",
                "mkdir -p target/pit-reports/run\n"
                f"printf '%s\\n' '{report}' > target/pit-reports/run/mutations.xml",
            )

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"},
            )

        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertIn("unsupported changed-file status 'QUEUED'", result.stderr)
        self.assertFalse((out_dir / "mutation-findings.jsonl").exists())

    def test_pitest_no_coverage_is_a_finding(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            changed = "src/main/java/com/example/App.java"
            scope = _write_scope(repo, languages=["java"], files=[changed])
            (repo / "pom.xml").write_text(
                "<project><build><plugins><plugin>"
                "<groupId>org.pitest</groupId>"
                "<artifactId>pitest-maven</artifactId>"
                "</plugin></plugins></build></project>\n",
                encoding="utf-8",
            )
            report = (
                '<mutations><mutation status="NO_COVERAGE">'
                "<sourceFile>App.java</sourceFile>"
                "<mutatedClass>com.example.App</mutatedClass>"
                "<lineNumber>11</lineNumber>"
                "<description>removed call</description>"
                "</mutation></mutations>"
            )
            out_dir = repo / "out"
            out_dir.mkdir()
            bin_dir = repo / "bin"
            args_log = repo / "maven-args.log"
            _write_executable(
                bin_dir / "mvn",
                f'printf "%s\\n" "$*" > "{args_log}"\n'
                "mkdir -p target/pit-reports/run\n"
                f"printf '%s\\n' '{report}' > target/pit-reports/run/mutations.xml",
            )

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"},
            )
            findings_text = (out_dir / "mutation-findings.jsonl").read_text(
                encoding="utf-8"
            )
            args_text = args_log.read_text(encoding="utf-8").strip()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(args_text, "--offline -q -B pitest:mutationCoverage")
        finding = json.loads(findings_text)
        self.assertIn("Uncovered Pitest mutant", finding["finding"])

    def test_pitest_survivor_maps_by_package_path(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            changed = "module-a/src/main/java/com/example/App.java"
            scope = _write_scope(repo, languages=["java"], files=[changed])
            (repo / "pom.xml").write_text(
                "<project><build><plugins><plugin>"
                "<groupId>org.pitest</groupId>"
                "<artifactId>pitest-maven</artifactId>"
                "</plugin></plugins></build></project>\n",
                encoding="utf-8",
            )
            out_dir = repo / "out"
            out_dir.mkdir()
            bin_dir = repo / "bin"
            report = (
                '<mutations><mutation status="SURVIVED">'
                "<sourceFile>App.java</sourceFile>"
                "<mutatedClass>com.example.App</mutatedClass>"
                "<lineNumber>17</lineNumber>"
                "<description>changed conditional boundary</description>"
                "</mutation></mutations>"
            )
            _write_executable(
                bin_dir / "mvn",
                "mkdir -p target/pit-reports/run\n"
                f"printf '%s\\n' '{report}' > target/pit-reports/run/mutations.xml",
            )

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"},
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            findings = [
                json.loads(line)
                for line in (out_dir / "mutation-findings.jsonl").read_text().splitlines()
            ]
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0]["location"], f"{changed}:17")

    def test_pitest_ambiguous_multimodule_source_blocks_atomically(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            changed = [
                "module-a/src/main/java/com/example/App.java",
                "module-b/src/main/java/com/example/App.java",
            ]
            scope = _write_scope(repo, languages=["java"], files=changed)
            (repo / "pom.xml").write_text(
                "<project><build><plugins><plugin>"
                "<groupId>org.pitest</groupId>"
                "<artifactId>pitest-maven</artifactId>"
                "</plugin></plugins></build></project>\n",
                encoding="utf-8",
            )
            out_dir = repo / "out"
            out_dir.mkdir()
            bin_dir = repo / "bin"
            report = (
                '<mutations><mutation status="SURVIVED">'
                "<sourceFile>App.java</sourceFile>"
                "<mutatedClass>com.example.App</mutatedClass>"
                "<lineNumber>17</lineNumber>"
                "<description>changed conditional boundary</description>"
                "</mutation></mutations>"
            )
            _write_executable(
                bin_dir / "mvn",
                "mkdir -p target/pit-reports/run\n"
                f"printf '%s\\n' '{report}' > target/pit-reports/run/mutations.xml",
            )

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"},
            )

            self.assertEqual(result.returncode, 4, result.stderr)
            self.assertIn("ambiguous Pitest source mapping", result.stderr)
            self.assertIn("maps each package/source pair", result.stderr)
            self.assertIn("run one module at a time", result.stderr)
            self.assertIn("--offline -q -B pitest:mutationCoverage", result.stderr)
            self.assertIn("ERROR: rerun: bash", result.stderr)
            self.assertFalse((out_dir / "mutation-findings.jsonl").exists())

    def test_maven_wrapper_does_not_bypass_offline_runner_preflight(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "pom.xml").write_text(
                "<project><build><plugins><plugin>"
                "<groupId>org.pitest</groupId>"
                "<artifactId>pitest-maven</artifactId>"
                "</plugin></plugins></build></project>\n",
                encoding="utf-8",
            )
            _write_executable(repo / "mvnw")

            result = self._run(
                repo,
                env={"MUTATION_DRY_RUN": "1", "PATH": "/usr/bin:/bin"},
                languages=["java"],
                files=["src/main/java/App.java"],
            )

        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertIn("mutation prerequisite 'mvn' is missing", result.stderr)
        self.assertIn("Install Maven", result.stderr)

    def test_mutation_rejects_invalid_timeout(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(repo, languages=["javascript"], files=["x.js"])
            out_dir = repo / "out"

            r = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                    "--timeout", "never",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            self.assertEqual(r.returncode, 2)
            self.assertIn("timeout must be a positive integer", r.stderr)

    def test_javascript_without_config_blocks(self):
        """An undeclared Stryker dependency blocks before config validation."""
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "package.json").write_text(
                json.dumps({"name": "no-stryker", "devDependencies": {}}),
                encoding="utf-8",
            )
            r = self._run(repo, languages=["javascript"], files=["x.js"])
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("mutation prerequisite 'stryker' is missing", r.stderr)
        self.assertIn("npm install --save-dev @stryker-mutator/core", r.stderr)
        self.assertNotIn("node_modules/.bin/stryker init", r.stderr)

    def test_jvm_without_supported_build_manifest_blocks(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            r = self._run(repo, languages=["java"], files=["X.java"])
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("mutation prerequisite 'pitest-build' is missing", r.stderr)
        self.assertIn("project's existing build system", r.stderr)

    def test_gradle_remediation_never_suggests_maven(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "build.gradle.kts").write_text(
                "plugins { java }\n", encoding="utf-8"
            )
            _write_executable(repo / "gradlew")
            r = self._run(
                repo,
                env={"PATH": "/usr/bin:/bin"},
                languages=["java"],
                files=["src/App.java"],
            )
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("mutation prerequisite 'pitest-gradle' is missing", r.stderr)
        self.assertIn("mutation prerequisite 'gradle' is missing", r.stderr)
        self.assertIn("info.solidsoft.pitest", r.stderr)
        self.assertIn("Install Gradle", r.stderr)
        self.assertNotIn("Maven", r.stderr)
        self.assertNotIn("pom.xml", r.stderr)

    def test_gradle_wrapper_does_not_bypass_offline_runner_preflight(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "build.gradle.kts").write_text(
                'plugins { id("info.solidsoft.pitest") version "1.19.0-rc.3" }\n',
                encoding="utf-8",
            )
            _write_executable(repo / "gradlew")

            result = self._run(
                repo,
                env={"MUTATION_DRY_RUN": "1", "PATH": "/usr/bin:/bin"},
                languages=["java"],
                files=["src/main/java/App.java"],
            )

        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertIn("mutation prerequisite 'gradle' is missing", result.stderr)

    def test_gradle_pitest_runs_with_offline_path_runner(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            changed = "src/main/java/App.java"
            scope = _write_scope(repo, languages=["java"], files=[changed])
            (repo / "build.gradle.kts").write_text(
                'plugins { id("info.solidsoft.pitest") version "1.19.0-rc.3" }\n',
                encoding="utf-8",
            )
            report = (
                '<mutations><mutation status="SURVIVED">'
                "<sourceFile>App.java</sourceFile>"
                "<mutatedClass>App</mutatedClass>"
                "<lineNumber>3</lineNumber>"
                "<description>changed return value</description>"
                "</mutation></mutations>"
            )
            out_dir = repo / "out"
            out_dir.mkdir()
            bin_dir = repo / "bin"
            args_log = repo / "gradle-args.log"
            _write_executable(
                bin_dir / "gradle",
                f'printf "%s\\n" "$*" > "{args_log}"\n'
                "mkdir -p build/reports/pitest\n"
                f"printf '%s\\n' '{report}' > build/reports/pitest/mutations.xml",
            )

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin"},
            )
            args_text = args_log.read_text(encoding="utf-8").strip()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(args_text, "--offline --no-daemon pitest")

    def test_gradle_report_mapping_failure_reuses_offline_path_runner(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            changed = [
                "module-a/src/main/java/com/example/App.java",
                "module-b/src/main/java/com/example/App.java",
            ]
            scope = _write_scope(repo, languages=["java"], files=changed)
            (repo / "build.gradle.kts").write_text(
                'plugins { id("info.solidsoft.pitest") version "1.19.0-rc.3" }\n',
                encoding="utf-8",
            )
            report = (
                '<mutations><mutation status="SURVIVED">'
                "<sourceFile>App.java</sourceFile>"
                "<mutatedClass>com.example.App</mutatedClass>"
                "<lineNumber>3</lineNumber>"
                "<description>changed return value</description>"
                "</mutation></mutations>"
            )
            out_dir = repo / "out"
            out_dir.mkdir()
            bin_dir = repo / "bin"
            _write_executable(
                bin_dir / "gradle",
                "mkdir -p build/reports/pitest\n"
                f"printf '%s\\n' '{report}' > build/reports/pitest/mutations.xml",
            )

            result = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin"},
            )

        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertIn("ambiguous Pitest source mapping", result.stderr)
        self.assertIn("--offline --no-daemon pitest", result.stderr)
        self.assertNotIn("gradlew", result.stderr)

    def test_exit_2_on_missing_scope_arg(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            r = subprocess.run(
                ["bash", str(RUN_MUTATION), "--output-dir", str(repo / "out")],
                capture_output=True, text=True, timeout=5,
            )
        self.assertEqual(r.returncode, 2)


# ---------------------------------------------------------------------------
# `--reconcile` — Intent axis derivation sub-mode toggle
# ---------------------------------------------------------------------------


class TestReconcileToggle(unittest.TestCase):
    """Pin that derivation/run.py is the entry point and that its output
    schema carries the UNCLASSIFIED placeholders the Intent axis classifies.

    Detailed extraction / freshness / ignore tests live in
    `test_derivation_graph.py` — this file pins the flag-toggle contract.
    """

    def test_run_py_emits_unclassified_placeholders(self):
        run_py = SKILL_SCRIPTS / "derivation" / "run.py"
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            spec = repo / "spec.md"
            spec.write_text(
                "# Spec\n\n## Acceptance criteria\n\n- [ ] Item one is asserted\n",
                encoding="utf-8",
            )
            scope = _write_scope(repo, languages=[], files=[])
            output = repo / "reconcile.json"
            r = subprocess.run(
                [
                    sys.executable, str(run_py),
                    "--repo", str(repo),
                    "--scope", str(scope),
                    "--output", str(output),
                    "--reconcile", str(spec),
                ],
                capture_output=True, text=True, timeout=10,
                env={**os.environ, "DERIVATION_SKIP_GH": "1"},
            )
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        self.assertEqual(out["lens"], "derivation")
        self.assertEqual(len(out["findings"]), 1)
        self.assertEqual(out["findings"][0]["classification"], "UNCLASSIFIED")
        # Recommendation must direct the LLM toward the 4 final tags.
        rec = out["findings"][0]["recommendation"]
        self.assertIn("GAP", rec)
        self.assertIn("SCOPE-ADD", rec)
        self.assertIn("DECISION-OVERRIDE", rec)
        self.assertIn("CONSISTENT", rec)

    def test_empty_auto_blocks_instead_of_reducing_intent_coverage(self):
        run_py = SKILL_SCRIPTS / "derivation" / "run.py"
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(repo, languages=[], files=[])
            output = repo / "reconcile.json"
            r = subprocess.run(
                [
                    sys.executable, str(run_py),
                    "--repo", str(repo),
                    "--scope", str(scope),
                    "--output", str(output),
                    "--reconcile", "@auto",
                ],
                capture_output=True, text=True, timeout=10,
                env={**os.environ, "DERIVATION_SKIP_GH": "1"},
            )
            self.assertEqual(r.returncode, 3, r.stderr)
            self.assertIn("@auto found no planning artifact", r.stderr)
            self.assertIn("then rerun Code Ultrareview", r.stderr)
            coverage = json.loads(scope.read_text())["reconcile_coverage"]
            self.assertFalse(coverage["complete"])
            self.assertEqual(coverage["status"], "blocked")


# ---------------------------------------------------------------------------
# `--apply-safe` — confirmation-gated writers
# ---------------------------------------------------------------------------


class TestApplySafeOff(unittest.TestCase):
    """Toggle: without `--apply-safe`, no writer is invoked → no file
    modification. The orchestrator-level guarantee — pinned here at the
    module-import level: the writers are dormant code.

    The actual confirmation-gate contract is pinned in
    `test_ultra_execution.py::TestApplySafeConfirm` (mock input n/y/yes).
    """

    def test_writers_are_dormant_imports(self):
        """Importing apply_safe must NOT modify anything on disk."""
        # The package import itself runs no I/O — pinned by importing it
        # and asserting no exception.
        from apply_safe import version_sync, description_sync, failing_test_writer  # noqa: F401
        # All three modules expose a clear write-trigger entry point —
        # `sync()` / `write()` — so the orchestrator must call into them
        # explicitly. There's no module-level side effect.
        self.assertTrue(callable(version_sync.sync))
        self.assertTrue(callable(description_sync.sync))
        self.assertTrue(callable(failing_test_writer.write))

    def test_no_write_without_confirmation(self):
        """The `confirm_write` helper is the single gate. Decline → no write."""
        from apply_safe._common import confirm_write
        with tempfile.TemporaryDirectory() as t:
            target = Path(t) / "f.txt"
            target.write_text("original\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()), \
                    mock.patch("builtins.input", return_value="n"):
                approved = confirm_write(target, "diff text", yes=False)
            # confirm_write doesn't write itself — it just gates the writer.
            self.assertEqual(target.read_text(encoding="utf-8"), "original\n")
            self.assertFalse(approved)


# ---------------------------------------------------------------------------
# Composition — `--verify-build --mutation-test` runs both
# ---------------------------------------------------------------------------


class TestCompositionVerifyAndMutation(unittest.TestCase):
    """AC: `--verify-build --mutation-test` → build verification runs
    Phase 3.5 AND mutation runs Phase 2 extension. The two scripts must
    not interfere when invoked back-to-back."""

    def test_both_scripts_emit_independent_output(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            scope = _write_scope(repo, languages=["python"], files=["x.py"])
            _configure_mutmut(repo)
            (repo / "test_gate.py").write_text(
                "import unittest\n\n"
                "class TestGate(unittest.TestCase):\n"
                "    def test_passes(self):\n"
                "        self.assertTrue(True)\n",
                encoding="utf-8",
            )
            bin_dir = repo / "bin"
            _write_executable(bin_dir / "mutmut")
            findings_path = _write_findings(repo / "axis.jsonl", [
                {
                    "axis": "correctness", "severity": "High",
                    "location": "x.py:1", "finding": "bug",
                    "recommendation": "fix", "confidence": 70,
                },
            ])
            verify_out = repo / "build-verified.jsonl"
            mutation_out_dir = repo / "mut"
            mutation_out_dir.mkdir()

            # 1. Build verification — the canonical Python test gate passes.
            r1 = subprocess.run(
                [
                    sys.executable, str(RUN_BUILD_VERIFY),
                    "--scope", str(scope),
                    "--findings", str(findings_path),
                    "--output", str(verify_out),
                    "--repo", str(repo),
                ],
                capture_output=True, text=True, timeout=15,
            )
            # 2. Mutation — dry-run hook → exit clean, empty findings.
            r2 = subprocess.run(
                [
                    "bash", str(RUN_MUTATION),
                    "--scope", str(scope),
                    "--output-dir", str(mutation_out_dir),
                    "--repo", str(repo),
                ],
                capture_output=True, text=True, timeout=15,
                env={
                    **os.environ,
                    "MUTATION_DRY_RUN": "1",
                    "PATH": f"{bin_dir}:/usr/bin:/bin",
                },
            )

            self.assertEqual(r1.returncode, 0, r1.stderr)
            self.assertEqual(r2.returncode, 0, r2.stderr)
            # A passing generic test gate never changes finding confidence.
            verify_lines = [l for l in verify_out.read_text(encoding="utf-8").splitlines() if l.strip()]
            self.assertEqual(len(verify_lines), 1)
            self.assertEqual(json.loads(verify_lines[0])["confidence"], 70)
            # Mutation findings empty under dry-run.
            mutation_findings = mutation_out_dir / "mutation-findings.jsonl"
            self.assertTrue(mutation_findings.exists())
            self.assertEqual(mutation_findings.read_text(encoding="utf-8"), "")


# ---------------------------------------------------------------------------
# Validator promotion constants remain centralized in synthesis_core.
# ---------------------------------------------------------------------------


class TestPhaseConstants(unittest.TestCase):
    """The promotion contract (+30, cap 95, floor at threshold 80) lives in
    one place — `synthesis_core.py`. Pin those values so a silent change
    fails this test."""

    def test_threshold_is_80(self):
        self.assertEqual(synthesis_core.CONFIDENCE_THRESHOLD, 80)

    def test_promotion_bonus_is_30(self):
        self.assertEqual(synthesis_core.PROMOTION_BONUS, 30)

    def test_promotion_cap_is_95(self):
        self.assertEqual(synthesis_core.PROMOTION_CAP, 95)

# ---------------------------------------------------------------------------
# Build verification never changes finding confidence.
# ---------------------------------------------------------------------------


class TestBuildVerifyPreservesConfidence(unittest.TestCase):
    def test_failed_gate_preserves_zero_and_sub80_findings(self):
        conf_zero = {
            "axis": "correctness",
            "severity": "Medium",
            "location": "src/a.ts:10",
            "finding": "Flagged FP",
            "recommendation": "—",
            "confidence": 0,
        }
        conf_sub80 = {
            "axis": "correctness",
            "severity": "Medium",
            "location": "src/b.ts:5",
            "finding": "Real sub-80",
            "recommendation": "—",
            "confidence": 60,
        }

        # Bypass the real subprocess with a deterministic failing gate.
        with mock.patch.object(run_build_verify, "_run_build",
                               return_value={
                                   "build_status": "failed",
                                   "exit_code": 1,
                                   "stdout_tail": "",
                                   "stderr_tail": "failure",
                               }):
            out, meta = run_build_verify.run(
                repo=Path("."),
                findings=[conf_zero, conf_sub80],
                test_command="true",
                tool="python3",
                tool_available=True,
                timeout=5,
            )

        # The conf-0 finding survives in the output with its original
        # confidence — never promoted.
        survivors_by_loc = {f["location"]: f for f in out}
        self.assertIn("src/a.ts:10", survivors_by_loc)
        self.assertEqual(survivors_by_loc["src/a.ts:10"]["confidence"], 0)
        self.assertIn("src/b.ts:5", survivors_by_loc)
        self.assertEqual(survivors_by_loc["src/b.ts:5"]["confidence"], 60)
        self.assertEqual(meta["promoted_count"], 0)
        self.assertFalse(meta["complete"])


if __name__ == "__main__":
    unittest.main()
