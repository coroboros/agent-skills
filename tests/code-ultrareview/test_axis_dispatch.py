"""Tests for skills/code-ultrareview/scripts/axis_dispatch.py.

Covers the deterministic Phase 3 orchestrator contracts: axis selection
(8 always + Coherence conditional), tool-finding filtering by axis,
bundle preparation, stale-run rejection, and complete result collection.

Behavioral evaluation of axis subagent output (severity, confidence,
"single-use factory abstraction" wording) lives in `evals/evals.json`,
not in this unit-test file — that work is non-deterministic LLM output.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "skills" / "code-ultrareview" / "scripts" / "axis_dispatch.py"
SKILL_DIR = REPO_ROOT / "skills" / "code-ultrareview"


def _load_module():
    spec = importlib.util.spec_from_file_location("axis_dispatch", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


axis_dispatch = _load_module()


def _scope_fields(path: str = "src/x.ts") -> dict:
    return {"files_touched": 1, "files_touched_list": [path]}


def _tool_coverage(path: Path, body: str = "") -> dict:
    data = body.encode("utf-8")
    return {
        "complete": True,
        "output": str(path.resolve()),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "finding_count": sum(1 for line in body.splitlines() if line.strip()),
    }


def _run_prepare(scope: dict) -> subprocess.CompletedProcess:
    with tempfile.TemporaryDirectory() as td:
        workdir = Path(td)
        scope_path = workdir / "scope.json"
        findings_path = workdir / "tool-findings.jsonl"
        diff_path = workdir / "diff.patch"
        payload = {**_scope_fields(), **scope}
        if isinstance(payload.get("tool_coverage"), dict) and payload["tool_coverage"].get("complete") is True:
            payload["tool_coverage"] = _tool_coverage(findings_path)
        scope_path.write_text(json.dumps(payload), encoding="utf-8")
        findings_path.write_text("", encoding="utf-8")
        diff_path.write_text("diff --git a/x.ts b/x.ts", encoding="utf-8")
        return subprocess.run(
            [
                "python3",
                str(SCRIPT),
                "prepare",
                "--scope",
                str(scope_path),
                "--findings",
                str(findings_path),
                "--diff",
                str(diff_path),
                "--output-dir",
                str(workdir / "run"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )


# ---------------------------------------------------------------------------
# Axis selection
# ---------------------------------------------------------------------------


class TestDecideAxes(unittest.TestCase):

    def test_inactive_coherence_subset_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Coherence is inactive"):
            axis_dispatch.decide_axes(
                {"activates_coherence": False}, ["coherence"]
            )

    def test_parse_axes_rejects_duplicates_and_unknown_values(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            axis_dispatch.parse_axes("tests,tests")
        with self.assertRaisesRegex(ValueError, "Unknown axis"):
            axis_dispatch.parse_axes("correctness,security")


# ---------------------------------------------------------------------------
# Tool-finding filtering
# ---------------------------------------------------------------------------


SAMPLE_FINDINGS = [
    {"axis": "simplification", "file": "b.ts", "line_start": 5, "line_end": 5,
     "severity": "Low", "source_tool": "knip",
     "message": "unused export", "confidence": 100},
    {"axis": "simplification", "file": "c.go", "line_start": 10, "line_end": 10,
     "severity": "Medium", "source_tool": "dupl",
     "message": "duplicated block", "confidence": 100},
    {"axis": "documentation", "file": "README.md", "line_start": 3, "line_end": 3,
     "severity": "Low", "source_tool": "markdownlint-cli2",
     "message": "MD012: multiple blanks", "confidence": 100},
    {"axis": "design-api", "file": "openapi.yaml", "line_start": 12, "line_end": 12,
     "severity": "High", "source_tool": "oasdiff",
     "message": "DELETE /users — breaking", "confidence": 100},
    {"axis": "performance", "file": "queries.py", "line_start": 22, "line_end": 22,
     "severity": "High", "source_tool": "semgrep",
     "message": "code-ultrareview-n-plus-one-sqlalchemy", "confidence": 100},
]


# ---------------------------------------------------------------------------
# Bundle preparation
# ---------------------------------------------------------------------------


class TestPrepareAll(unittest.TestCase):

    def test_prepare_emits_nine_bundles_when_coherence_active(self):
        with tempfile.TemporaryDirectory() as td:
            result = axis_dispatch.prepare(
                scope={"activates_coherence": True},
                all_findings=SAMPLE_FINDINGS, diff_text="",
                output_dir=Path(td), skill_dir=SKILL_DIR,
            )
            self.assertEqual(len(result["axes"]), 9)
            self.assertEqual(len(result["bundles"]), 9)
            self.assertTrue(result["coherence_active"])
            self.assertIn("coherence", result["bundles"])

    def test_prepare_filtering_isolates_findings_per_axis(self):
        # Spec AC: tool findings pre-filtered per axis BEFORE subagent dispatch.
        with tempfile.TemporaryDirectory() as td:
            result = axis_dispatch.prepare(
                scope={"activates_coherence": False},
                all_findings=SAMPLE_FINDINGS, diff_text="",
                output_dir=Path(td), skill_dir=SKILL_DIR,
            )
            expected = {
                "correctness": [], "simplification": ["knip", "dupl"],
                "tests": [], "documentation": ["markdownlint-cli2"],
                "style": [], "intent": [], "design-api": ["oasdiff"],
                "performance": ["semgrep"],
            }
            self.assertEqual(set(result["bundles"]), set(expected))
            for axis, tools in expected.items():
                with self.subTest(axis=axis):
                    bundle = json.loads(Path(result["bundles"][axis]["input_path"]).read_text())
                    self.assertEqual([f["source_tool"] for f in bundle["findings"]], tools)

    def test_prepare_emits_only_selected_axis_bundles(self):
        with tempfile.TemporaryDirectory() as td:
            result = axis_dispatch.prepare(
                scope={"activates_coherence": False},
                all_findings=SAMPLE_FINDINGS,
                diff_text="",
                output_dir=Path(td),
                skill_dir=SKILL_DIR,
                selected_axes=["correctness", "tests"],
            )
        self.assertEqual(result["axes"], ["correctness", "tests"])
        self.assertEqual(set(result["bundles"]), {"correctness", "tests"})


class TestAxisResultIngest(unittest.TestCase):
    def test_ingest_axes_must_match_prepared_dispatch(self):
        scope = {
            "activates_coherence": False,
            "axis_coverage": {
                "requested": ["correctness", "tests"],
                "completed": [],
            },
        }
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(
                ValueError, "do not match the axes prepared for dispatch"
            ):
                axis_dispatch.ingest_axis_results(
                    scope, Path(td), ["correctness"]
                )

    def test_requires_one_valid_result_per_axis(self):
        scope = {"activates_coherence": False}
        with tempfile.TemporaryDirectory() as td:
            result_dir = Path(td)
            (result_dir / "correctness.jsonl").write_text(
                json.dumps({"axis": "correctness", "no_findings": True}) + "\n",
                encoding="utf-8",
            )
            (result_dir / "tests.jsonl").write_text(
                json.dumps({
                    "axis": "tests",
                    "severity": "Medium",
                    "location": "tests/a.test.ts:4",
                    "finding": "Assertion misses the failure path",
                    "recommendation": "Add a rejection assertion",
                    "confidence": 88,
                }) + "\n",
                encoding="utf-8",
            )
            findings, coverage = axis_dispatch.ingest_axis_results(
                scope, result_dir, ["correctness", "tests"]
            )
        self.assertEqual(len(findings), 1)
        self.assertTrue(coverage["complete"])
        self.assertFalse(coverage["full"])

    def test_confidence_zero_is_a_valid_axis_result(self):
        scope = {"activates_coherence": False}
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "correctness.jsonl").write_text(
                json.dumps({
                    "axis": "correctness",
                    "severity": "Low",
                    "location": "src/a.py:1",
                    "finding": "Uncertain edge case",
                    "recommendation": "Validate the input contract",
                    "confidence": 0,
                }) + "\n",
                encoding="utf-8",
            )
            findings, coverage = axis_dispatch.ingest_axis_results(
                scope, Path(td), ["correctness"]
            )
        self.assertEqual(findings[0]["confidence"], 0)
        self.assertTrue(coverage["complete"])

    def test_missing_empty_and_malformed_results_block(self):
        scope = {"activates_coherence": False}
        for body, expected in (("", "empty"), ("{bad\n", "malformed")):
            with self.subTest(body=body), tempfile.TemporaryDirectory() as td:
                path = Path(td) / "correctness.jsonl"
                path.write_text(body, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, expected):
                    axis_dispatch.ingest_axis_results(
                        scope, Path(td), ["correctness"]
                    )

    def test_no_findings_marker_cannot_hide_real_findings(self):
        scope = {"activates_coherence": False}
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "correctness.jsonl"
            path.write_text(
                json.dumps({"axis": "correctness", "no_findings": True}) + "\n"
                + json.dumps({
                    "axis": "correctness",
                    "severity": "Low",
                    "location": "a.py:1",
                    "finding": "Issue",
                    "recommendation": "Fix it",
                    "confidence": 90,
                }) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "cannot be mixed"):
                axis_dispatch.ingest_axis_results(
                    scope, Path(td), ["correctness"]
                )


# ---------------------------------------------------------------------------
# CLI smoke test
# ---------------------------------------------------------------------------


class TestCliPrepare(unittest.TestCase):
    def test_prepare_rejects_mistyped_coverage_without_traceback(self):
        result = _run_prepare({
            "repo_kind": "app",
            "languages": ["typescript"],
            "tool_coverage": "complete",
        })

        self.assertEqual(result.returncode, 4)
        self.assertIn("tool_coverage must be an object", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_prepare_accepts_not_applicable_skips_and_blocks_the_rest(self):
        """`tools_skipped` blocks unless every entry is marked not applicable."""
        base = {
            "repo_kind": "app",
            "languages": ["javascript"],
            "tools_missing": [],
            "tool_coverage": {"complete": True},
        }
        accepted = _run_prepare({**base, "tools_skipped": [
            {"tool": "knip", "applicable": False,
             "reason": "no package.json covers the changed JS/TS files"},
        ]})
        blocked = _run_prepare({**base, "tools_skipped": [
            {"tool": "knip", "reason": "operator skipped"},
        ]})
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        self.assertEqual(blocked.returncode, 4)
        self.assertIn("missing or skipped", blocked.stderr)

    def test_prepare_rejects_non_object_mutation_manifest_without_traceback(self):
        result = _run_prepare({
            "repo_kind": "app",
            "languages": ["typescript"],
            "tools_skipped": [],
            "tools_missing": [],
            "tool_coverage": {"complete": True},
            "mutation_coverage": "complete",
        })

        self.assertEqual(result.returncode, 4)
        self.assertIn("mutation_coverage must be an object", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    """End-to-end: prepare command writes bundles for the 8 canonical axes
    when invoked from the shell."""

    def test_cli_prepare_writes_bundles(self):
        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            scope_path = tdir / "scope.json"
            findings_path = tdir / "tool-findings.jsonl"
            diff_path = tdir / "diff.patch"
            output_dir = tdir / "run"

            scope_path.write_text(json.dumps({
                **_scope_fields(),
                "repo_kind": "app",
                "languages": ["typescript"],
                "instruction_chain": [],
                "activates_coherence": False,
                "files": ["src/x.ts"],
                "tools_skipped": [],
                "tools_missing": [],
                "tool_coverage": _tool_coverage(
                    findings_path,
                    "\n".join(json.dumps(f) for f in SAMPLE_FINDINGS) + "\n",
                ),
            }), encoding="utf-8")
            findings_path.write_text(
                "\n".join(json.dumps(f) for f in SAMPLE_FINDINGS) + "\n",
                encoding="utf-8",
            )
            diff_path.write_text("diff --git a/x b/x", encoding="utf-8")

            proc = subprocess.run(
                [
                    "python3", str(SCRIPT), "prepare",
                    "--scope", str(scope_path),
                    "--findings", str(findings_path),
                    "--diff", str(diff_path),
                    "--output-dir", str(output_dir),
                ],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(len(payload["axes"]), 8)
            self.assertFalse(payload["coherence_active"])
            for axis in axis_dispatch.CANONICAL_AXES:
                bundle = payload["bundles"][axis]
                inputs = json.loads(Path(bundle["input_path"]).read_text())
                prompt = Path(bundle["prompt_path"]).read_text()
                self.assertEqual(inputs["axis"], axis)
                self.assertEqual(inputs["diff_text"], "diff --git a/x b/x")
                self.assertIn(bundle["input_path"], prompt)
                for key in ("brief_path", "anthropic_verbatim_path"):
                    self.assertTrue(Path(inputs[key]).is_file())
                    self.assertIn(inputs[key], prompt)

    def test_explicit_complete_axis_lists_remain_scoped(self):
        import subprocess

        cases = (
            (False, list(axis_dispatch.CANONICAL_AXES)),
            (False, list(reversed(axis_dispatch.CANONICAL_AXES))),
            (
                True,
                list(axis_dispatch.CANONICAL_AXES)
                + list(axis_dispatch.CONDITIONAL_AXES),
            ),
        )
        for coherence, axes in cases:
            with self.subTest(coherence=coherence, axes=axes):
                with tempfile.TemporaryDirectory() as td:
                    tdir = Path(td)
                    scope_path = tdir / "scope.json"
                    findings_path = tdir / "tool-findings.jsonl"
                    diff_path = tdir / "diff.patch"
                    scope_path.write_text(
                        json.dumps({
                            **_scope_fields(),
                            "repo_kind": "app",
                            "languages": ["typescript"],
                            "instruction_chain": [],
                            "activates_coherence": coherence,
                            "files": ["src/x.ts"],
                            "tools_skipped": [],
                            "tools_missing": [],
                            "tool_coverage": _tool_coverage(findings_path),
                        }),
                        encoding="utf-8",
                    )
                    findings_path.write_text("", encoding="utf-8")
                    diff_path.write_text("diff --git a/x b/x", encoding="utf-8")
                    result = subprocess.run(
                        [
                            "python3",
                            str(SCRIPT),
                            "prepare",
                            "--scope",
                            str(scope_path),
                            "--findings",
                            str(findings_path),
                            "--diff",
                            str(diff_path),
                            "--output-dir",
                            str(tdir / "run"),
                            "--axes",
                            ",".join(axes),
                        ],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    coverage = json.loads(
                        scope_path.read_text(encoding="utf-8")
                    )["axis_coverage"]
                    self.assertTrue(coverage["explicit_scope"])
                    self.assertFalse(coverage["full"])

    def test_prepare_rejects_missing_findings_after_failed_battery(self):
        import subprocess

        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            scope_path = tdir / "scope.json"
            diff_path = tdir / "diff.patch"
            scope_path.write_text(
                json.dumps({
                    **_scope_fields("README.md"),
                    "repo_kind": "app",
                    "languages": ["markdown"],
                    "activates_coherence": False,
                    "tools_skipped": [],
                    "tools_missing": [],
                    "tool_coverage": _tool_coverage(
                        tdir / "missing-tool-findings.jsonl"
                    ),
                }),
                encoding="utf-8",
            )
            diff_path.write_text("diff --git a/README.md b/README.md", encoding="utf-8")
            result = subprocess.run(
                [
                    "python3", str(SCRIPT), "prepare",
                    "--scope", str(scope_path),
                    "--findings", str(tdir / "missing-tool-findings.jsonl"),
                    "--diff", str(diff_path),
                    "--output-dir", str(tdir / "run"),
                ],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 4)
            self.assertIn("required run artifact is missing", result.stderr)
            self.assertFalse((tdir / "run").exists())

    def test_prepare_rejects_incomplete_tool_coverage(self):
        import subprocess

        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            scope_path = tdir / "scope.json"
            findings_path = tdir / "tool-findings.jsonl"
            diff_path = tdir / "diff.patch"
            scope_path.write_text(
                json.dumps({
                    **_scope_fields("README.md"),
                    "repo_kind": "app",
                    "languages": ["markdown"],
                    "activates_coherence": False,
                    "tools_skipped": [],
                    "tools_missing": [{"tool": "markdownlint-cli2"}],
                    "tool_coverage": {"complete": False},
                }),
                encoding="utf-8",
            )
            findings_path.write_text("", encoding="utf-8")
            diff_path.write_text("diff --git a/README.md b/README.md", encoding="utf-8")
            result = subprocess.run(
                [
                    "python3", str(SCRIPT), "prepare",
                    "--scope", str(scope_path),
                    "--findings", str(findings_path),
                    "--diff", str(diff_path),
                    "--output-dir", str(tdir / "run"),
                ],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 4)
            self.assertIn("deterministic analyzer coverage is incomplete", result.stderr)
            self.assertFalse((tdir / "run").exists())

    def test_prepare_rejects_incomplete_requested_mutation_coverage(self):
        import subprocess

        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            scope_path = tdir / "scope.json"
            findings_path = tdir / "tool-findings.jsonl"
            diff_path = tdir / "diff.patch"
            scope_path.write_text(
                json.dumps({
                    **_scope_fields("App.java"),
                    "repo_kind": "app",
                    "languages": ["java"],
                    "activates_coherence": False,
                    "tools_skipped": [],
                    "tools_missing": [],
                    "tool_coverage": _tool_coverage(findings_path),
                    "mutation_coverage": {
                        "requested": True,
                        "complete": False,
                        "applicable": True,
                        "status": "failed",
                    },
                }),
                encoding="utf-8",
            )
            findings_path.write_text("", encoding="utf-8")
            diff_path.write_text("diff --git a/App.java b/App.java", encoding="utf-8")
            result = subprocess.run(
                [
                    "python3", str(SCRIPT), "prepare",
                    "--scope", str(scope_path),
                    "--findings", str(findings_path),
                    "--diff", str(diff_path),
                    "--output-dir", str(tdir / "run"),
                ],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 4)
            self.assertIn("requested mutation coverage is incomplete", result.stderr)
            self.assertFalse((tdir / "run").exists())

    def test_prepare_verifies_reconcile_result_and_scopes_it_to_intent(self):
        import subprocess

        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            reconcile_path = tdir / "reconcile.json"
            reconcile_payload = {
                "lens": "derivation",
                "artifacts": [{"path": "plan.md", "claim_count": 1}],
                "findings": [{
                    "classification": "UNCLASSIFIED",
                    "finding": "The cache remains bounded",
                }],
            }
            reconcile_bytes = (
                json.dumps(reconcile_payload, indent=2) + "\n"
            ).encode("utf-8")
            reconcile_path.write_bytes(reconcile_bytes)
            scope_path = tdir / "scope.json"
            findings_path = tdir / "tool-findings.jsonl"
            diff_path = tdir / "diff.patch"
            scope_path.write_text(
                json.dumps({
                    **_scope_fields(),
                    "repo_kind": "app",
                    "languages": ["typescript"],
                    "activates_coherence": False,
                    "tools_skipped": [],
                    "tools_missing": [],
                    "tool_coverage": _tool_coverage(findings_path),
                    "reconcile_coverage": {
                        "requested": True,
                        "complete": True,
                        "status": "complete",
                        "output": str(reconcile_path),
                        "sha256": hashlib.sha256(reconcile_bytes).hexdigest(),
                        "finding_count": 1,
                    },
                }),
                encoding="utf-8",
            )
            findings_path.write_text("", encoding="utf-8")
            diff_path.write_text("diff --git a/x.ts b/x.ts", encoding="utf-8")

            result = subprocess.run(
                [
                    "python3", str(SCRIPT), "prepare",
                    "--scope", str(scope_path),
                    "--findings", str(findings_path),
                    "--diff", str(diff_path),
                    "--output-dir", str(tdir / "run"),
                ],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            intent = json.loads(
                (tdir / "run" / "axis-input" / "intent.json").read_text()
            )
            correctness = json.loads(
                (tdir / "run" / "axis-input" / "correctness.json").read_text()
            )
            self.assertEqual(intent["reconcile"], reconcile_payload)
            self.assertNotIn("reconcile", correctness)

            reconcile_path.write_text("{}\n", encoding="utf-8")
            blocked = subprocess.run(
                [
                    "python3", str(SCRIPT), "prepare",
                    "--scope", str(scope_path),
                    "--findings", str(findings_path),
                    "--diff", str(diff_path),
                    "--output-dir", str(tdir / "blocked"),
                ],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(blocked.returncode, 4)
            self.assertIn("reconcile result changed after prepare", blocked.stderr)
            self.assertFalse((tdir / "blocked").exists())

    def test_prepare_rejects_tampered_tool_findings_without_writing_bundles(self):
        import subprocess

        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            scope_path = tdir / "scope.json"
            findings_path = tdir / "tool-findings.jsonl"
            diff_path = tdir / "diff.patch"
            tampered_finding = json.dumps({
                "axis": "security",
                "source_tool": "fake",
                "message": "must not be dropped",
                "confidence": 100,
            }) + "\n"
            scope_path.write_text(
                json.dumps({
                    **_scope_fields(),
                    "repo_kind": "app",
                    "languages": ["typescript"],
                    "activates_coherence": False,
                    "tools_skipped": [],
                    "tools_missing": [],
                    "tool_coverage": _tool_coverage(findings_path),
                }),
                encoding="utf-8",
            )
            findings_path.write_text(tampered_finding, encoding="utf-8")
            diff_path.write_text("diff --git a/x.ts b/x.ts", encoding="utf-8")
            result = subprocess.run(
                [
                    "python3", str(SCRIPT), "prepare",
                    "--scope", str(scope_path),
                    "--findings", str(findings_path),
                    "--diff", str(diff_path),
                    "--output-dir", str(tdir / "run"),
                ],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 4)
            self.assertIn("tool findings changed after prepare", result.stderr)
            self.assertFalse((tdir / "run").exists())


class TestCliIngest(unittest.TestCase):
    def test_omitted_tool_observation_still_requires_validation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            scope_path = root / "scope.json"
            findings_path = root / "tool-findings.jsonl"
            diff_path = root / "diff.patch"
            observation = {
                "axis": "correctness", "severity": "High",
                "location": "src/x.ts:1", "finding": "Potential defect",
                "recommendation": "Verify the caller contract",
                "confidence": 0, "source_tool": "semgrep",
            }
            raw = json.dumps(observation) + "\n"
            findings_path.write_text(raw, encoding="utf-8")
            diff_path.write_text("diff --git a/x b/x", encoding="utf-8")
            scope_path.write_text(json.dumps({
                **_scope_fields(), "repo_kind": "app",
                "languages": ["typescript"], "activates_coherence": False,
                "instruction_chain": [], "tools_skipped": [], "tools_missing": [],
                "tool_coverage": _tool_coverage(findings_path, raw),
            }), encoding="utf-8")
            prepare = subprocess.run([
                sys.executable, str(SCRIPT), "prepare", "--scope", str(scope_path),
                "--findings", str(findings_path), "--diff", str(diff_path),
                "--output-dir", str(root / "run"), "--axes", "correctness",
            ], capture_output=True, text=True)
            self.assertEqual(prepare.returncode, 0, prepare.stderr)
            scope = json.loads(scope_path.read_text(encoding="utf-8"))
            results = root / "results"
            results.mkdir()
            (results / "correctness.jsonl").write_text(json.dumps({
                "run_id": scope["axis_coverage"]["run_id"],
                "axis": "correctness", "no_findings": True,
            }) + "\n", encoding="utf-8")
            output = root / "axis-findings.jsonl"
            ingest = subprocess.run([
                sys.executable, str(SCRIPT), "ingest", "--scope", str(scope_path),
                "--results-dir", str(results), "--output", str(output),
                "--axes", "correctness",
            ], capture_output=True, text=True)
            self.assertEqual(ingest.returncode, 0, ingest.stderr)
            self.assertEqual([json.loads(line) for line in output.read_text().splitlines()], [observation])
            scope = json.loads(scope_path.read_text(encoding="utf-8"))
            self.assertEqual(scope["validator_coverage"]["expected"], 1)
            self.assertFalse(scope["validator_coverage"]["complete"])

    def test_failed_rerun_invalidates_stale_axis_state_and_output(self):
        import subprocess

        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            scope_path = tdir / "scope.json"
            results_dir = tdir / "results"
            results_dir.mkdir()
            output_path = tdir / "axis-findings.jsonl"
            scope_path.write_text(
                json.dumps({
                    **_scope_fields(),
                    "repo_kind": "app",
                    "languages": ["typescript"],
                    "activates_coherence": False,
                    "tool_coverage": {"complete": True},
                    "axis_coverage": {
                        "complete": True,
                        "full": False,
                        "explicit_scope": True,
                        "requested": ["correctness"],
                        "completed": ["correctness"],
                    },
                    "validator_coverage": {
                        "complete": True,
                        "expected": 0,
                        "completed": 0,
                    },
                    "coverage_complete": True,
                }),
                encoding="utf-8",
            )
            output_path.write_text(
                json.dumps({
                    "axis": "correctness",
                    "severity": "High",
                    "location": "src/stale.ts:1",
                    "finding": "stale finding",
                    "recommendation": "stale recommendation",
                    "confidence": 90,
                }) + "\n",
                encoding="utf-8",
            )
            (results_dir / "correctness.jsonl").write_text(
                "{malformed\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "python3", str(SCRIPT), "ingest",
                    "--scope", str(scope_path),
                    "--results-dir", str(results_dir),
                    "--output", str(output_path),
                    "--axes", "correctness",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 4, result.stderr)
            scope = json.loads(scope_path.read_text(encoding="utf-8"))
            self.assertFalse(scope["axis_coverage"]["complete"])
            self.assertEqual(scope["axis_coverage"]["completed"], [])
            self.assertFalse(scope["validator_coverage"]["complete"])
            self.assertFalse(scope["coverage_complete"])
            self.assertFalse(output_path.exists())


if __name__ == "__main__":
    unittest.main()
