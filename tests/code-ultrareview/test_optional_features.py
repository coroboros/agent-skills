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
import sys
import tempfile
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
        "claude_md_chain": [],
        "tools_skipped": [],
    }
    scope_path = repo / "scope.json"
    scope_path.write_text(json.dumps(scope, indent=2), encoding="utf-8")
    return scope_path


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
    """Toggle: without `--verify-build`, `run_build_verify.py` is never invoked.

    Trivially the case at the orchestrator level — this test pins the
    *script-level* property that an empty / missing findings file is
    still a clean no-op, so a buggy orchestrator that calls the script
    with empty input never raises.
    """

    def test_missing_findings_file_is_clean_skip(self):
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
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(out.exists())
            self.assertEqual(out.read_text(encoding="utf-8").strip(), "")
            sidecar = out.with_suffix(out.suffix + ".meta.json")
            self.assertTrue(sidecar.exists())
            meta = json.loads(sidecar.read_text(encoding="utf-8"))
            self.assertEqual(meta["build_status"], "skipped")
            self.assertEqual(meta["promoted_count"], 0)


class TestVerifyBuildPromotion(unittest.TestCase):
    """Pin the +30 / cap-95 / floor-80 promotion contract end-to-end."""

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

    def test_failing_build_promotes_bug_axes_only(self):
        verified_input = self._findings()
        out, meta = run_build_verify.run(
            self.repo, verified_input, "echo fail && exit 1",
            tool_available=True, timeout=10,
        )
        by_axis = {f["axis"]: f for f in out}
        # Correctness 65 → 95 (capped at 95 since 65+30 = 95).
        self.assertEqual(by_axis["correctness"]["confidence"], 95)
        # Tests 70 → 95 (capped at 95 since 70+30 = 100 → cap).
        self.assertEqual(by_axis["tests"]["confidence"], 95)
        # Performance 50 → 80 (50+30 = 80, exactly at floor).
        self.assertEqual(by_axis["performance"]["confidence"], 80)
        # Style axis is unaffected by build verification.
        self.assertEqual(by_axis["style"]["confidence"], 60)
        self.assertEqual(meta["build_failed"], True)
        self.assertEqual(meta["promoted_count"], 3)

    def test_passing_build_promotes_nothing(self):
        verified_input = self._findings()
        out, meta = run_build_verify.run(
            self.repo, verified_input, "true",
            tool_available=True, timeout=10,
        )
        for f in out:
            self.assertEqual(
                f["confidence"],
                next(g["confidence"] for g in verified_input if g["axis"] == f["axis"]),
            )
        self.assertEqual(meta["build_failed"], False)
        self.assertEqual(meta["promoted_count"], 0)

    def test_tool_unavailable_passes_findings_through(self):
        verified_input = self._findings()
        out, meta = run_build_verify.run(
            self.repo, verified_input, "pytest -x",
            tool_available=False, timeout=10,
        )
        self.assertEqual(out, verified_input)  # untouched
        self.assertEqual(meta["build_status"], "skipped")
        self.assertEqual(meta["promoted_count"], 0)
        self.assertIn("PATH", meta["reason"])

    def test_no_tool_detected_passes_findings_through(self):
        verified_input = self._findings()
        out, meta = run_build_verify.run(
            self.repo, verified_input, None,
            tool_available=False, timeout=10,
        )
        self.assertEqual(out, verified_input)
        self.assertEqual(meta["build_status"], "skipped")
        self.assertIn("no build tool detected", meta["reason"])

    def test_only_sub80_findings_are_eligible(self):
        """Findings already at ≥80 must not be touched even on a failing build."""
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
            tool_available=True, timeout=10,
        )
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["confidence"], 90)  # unchanged
        # No sub-80 to verify → skipped path.
        self.assertEqual(meta["build_status"], "skipped")

    def test_verdict_fn_axis_filter(self):
        """The verdict function only promotes bug-class axes."""
        fn = run_build_verify.make_verdict_fn(build_failed=True)
        for axis in run_build_verify.BUILD_RELEVANT_AXES:
            self.assertEqual(fn({"axis": axis}), "confirmed")
        for axis in ("style", "documentation", "intent", "simplification", "coherence"):
            self.assertEqual(fn({"axis": axis}), "inconclusive")

    def test_verdict_fn_passing_build(self):
        fn = run_build_verify.make_verdict_fn(build_failed=False)
        # Every axis is inconclusive on a passing build.
        for axis in ("correctness", "tests", "design-api", "performance", "style"):
            self.assertEqual(fn({"axis": axis}), "inconclusive")


class TestVerifyBuildCli(unittest.TestCase):
    """End-to-end CLI invocation — exercises argparse + sidecar layout."""

    def test_passes_findings_through_when_no_tool(self):
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
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(out.exists())
            lines = [l for l in out.read_text(encoding="utf-8").splitlines() if l.strip()]
            self.assertEqual(len(lines), 1)
            parsed = json.loads(lines[0])
            self.assertEqual(parsed["confidence"], 70)  # unchanged — no build tool
            sidecar = json.loads(
                (out.with_suffix(out.suffix + ".meta.json")).read_text(encoding="utf-8")
            )
            self.assertEqual(sidecar["build_status"], "skipped")

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


# ---------------------------------------------------------------------------
# `--mutation-test` — Phase 2 extension
# ---------------------------------------------------------------------------


class TestMutationDryRun(unittest.TestCase):
    """Toggle + graceful-skip pinning for `scripts/run_mutation.sh`."""

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
            r = self._run(
                repo, env={"MUTATION_DRY_RUN": "1"},
                languages=["python"], files=["x.py"],
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            # The exit-zero path must produce an empty findings file
            # (truncated at start) — downstream JSONL readers stay happy.
            out_file = Path(t) / "out" / "mutation-findings.jsonl"
            self.assertTrue(out_file.exists())
            self.assertEqual(out_file.read_text(encoding="utf-8"), "")
            self.assertIn("MUTATION_DRY_RUN=1", r.stderr)

    def test_no_languages_skips_without_failure(self):
        """Empty scope → no dispatch, exit 0, WARN on stderr."""
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            r = self._run(repo, languages=[], files=[])
        self.assertEqual(r.returncode, 0, r.stderr)
        # No JS/TS, no Python, no JVM → final fallback WARN should fire.
        self.assertIn("no JS/TS, Python, or JVM languages detected", r.stderr)

    def test_python_without_mutmut_skips(self):
        """When mutmut is absent from PATH, the Python branch skips."""
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
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
            self.assertEqual(r.returncode, 0, r.stderr)
            # /usr/bin + /bin typically ship no mutmut.
            self.assertIn("mutmut", r.stderr)

    def test_mutation_source_has_no_runtime_package_resolver(self):
        text = RUN_MUTATION.read_text(encoding="utf-8")
        self.assertNotRegex(text, r"\bnpx\b")
        self.assertNotRegex(text, r"\buvx\b")

    def test_mutation_timeout_is_portable(self):
        text = RUN_MUTATION.read_text(encoding="utf-8")
        self.assertIn("run_with_timeout", text)
        self.assertIn("subprocess.run", text)
        self.assertNotRegex(text, r'(^|\s)timeout "\$TIMEOUT"')

    def test_javascript_without_config_skips(self):
        """JS/TS dispatch requires a stryker config or @stryker-mutator/core in package.json."""
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "package.json").write_text(
                json.dumps({"name": "no-stryker", "devDependencies": {}}),
                encoding="utf-8",
            )
            r = self._run(repo, languages=["javascript"], files=["x.js"])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("stryker:", r.stderr)
        self.assertIn("no stryker config", r.stderr)

    def test_jvm_without_pom_skips(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            r = self._run(repo, languages=["java"], files=["X.java"])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("pitest:", r.stderr)
        self.assertIn("no pom.xml", r.stderr)

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
            r = subprocess.run(
                [
                    sys.executable, str(run_py),
                    "--repo", str(repo),
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

    def test_empty_auto_resolves_to_empty_findings(self):
        """`@auto` in a repo with no planning artifacts → empty findings."""
        run_py = SKILL_SCRIPTS / "derivation" / "run.py"
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            r = subprocess.run(
                [
                    sys.executable, str(run_py),
                    "--repo", str(repo), "--reconcile", "@auto",
                ],
                capture_output=True, text=True, timeout=10,
                env={**os.environ, "DERIVATION_SKIP_GH": "1"},
            )
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        self.assertEqual(out["findings"], [])


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

            # 1. Build verification — no build tool detected → pass-through.
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
                env={**os.environ, "MUTATION_DRY_RUN": "1"},
            )

            self.assertEqual(r1.returncode, 0, r1.stderr)
            self.assertEqual(r2.returncode, 0, r2.stderr)
            # Build verification preserved the input.
            verify_lines = [l for l in verify_out.read_text(encoding="utf-8").splitlines() if l.strip()]
            self.assertEqual(len(verify_lines), 1)
            self.assertEqual(json.loads(verify_lines[0])["confidence"], 70)
            # Mutation findings empty under dry-run.
            mutation_findings = mutation_out_dir / "mutation-findings.jsonl"
            self.assertTrue(mutation_findings.exists())
            self.assertEqual(mutation_findings.read_text(encoding="utf-8"), "")


# ---------------------------------------------------------------------------
# Acceptance criteria — keep CONFIDENCE_THRESHOLD / PROMOTION_BONUS visible
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

    def test_build_relevant_axes_match_spec(self):
        """Spec WS-6: build verification promotes bug-class axes only."""
        self.assertEqual(
            run_build_verify.BUILD_RELEVANT_AXES,
            frozenset({"correctness", "tests", "design-api", "performance"}),
        )


# ---------------------------------------------------------------------------
# Build-verify sub-80 filter — confidence-0 stays excluded
# ---------------------------------------------------------------------------


class TestBuildVerifyExcludesConfZero(unittest.TestCase):
    """`apply_a2` drops confidence-0 findings as flagged false positives.
    `run_build_verification` must NOT re-promote a conf-0 finding above
    threshold even when the build fails — confidence-0 has carried explicit
    intent to drop from the rubric.
    """

    def test_conf_zero_finding_is_not_iterated(self):
        # A failing build that, if conf-0 leaked into the sub-80 list, would
        # promote it to threshold via `make_verdict_fn(build_failed=True)`.
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

        # Bypass the real subprocess — return a non-zero exit (failing build).
        with mock.patch.object(run_build_verify, "_run_build",
                               return_value=(1, "ran")):
            out, meta = run_build_verify.run(
                repo=Path("."),
                findings=[conf_zero, conf_sub80],
                test_command="true",
                tool_available=True,
                timeout=5,
            )

        # The conf-0 finding survives in the output with its original
        # confidence — never promoted.
        survivors_by_loc = {f["location"]: f for f in out}
        self.assertIn("src/a.ts:10", survivors_by_loc)
        self.assertEqual(survivors_by_loc["src/a.ts:10"]["confidence"], 0)
        # The genuine sub-80 correctness finding WAS promoted to ≥ threshold
        # (correctness ∈ BUILD_RELEVANT_AXES, build failed → "confirmed").
        self.assertIn("src/b.ts:5", survivors_by_loc)
        self.assertGreaterEqual(
            survivors_by_loc["src/b.ts:5"]["confidence"],
            synthesis_core.CONFIDENCE_THRESHOLD,
        )
        # Meta reports a single promotion (only the genuine sub-80).
        self.assertEqual(meta["promoted_count"], 1)


if __name__ == "__main__":
    unittest.main()
