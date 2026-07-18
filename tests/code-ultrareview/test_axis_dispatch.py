"""Tests for skills/code-ultrareview/scripts/axis_dispatch.py.

Covers the deterministic Phase 3 orchestrator contracts: axis selection
(8 always + Coherence conditional), tool-finding filtering by axis,
per-axis prompt construction (verbatim references), bundle preparation,
and the parallel concurrency cap.

Behavioral evaluation of axis subagent output (severity, confidence,
"single-use factory abstraction" wording) lives in `evals/evals.json`,
not in this unit-test file — that work is non-deterministic LLM output.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
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


# ---------------------------------------------------------------------------
# Axis selection
# ---------------------------------------------------------------------------


class TestDecideAxes(unittest.TestCase):

    def test_always_returns_eight_canonical_axes(self):
        axes = axis_dispatch.decide_axes({"activates_coherence": False})
        self.assertEqual(len(axes), 8)
        self.assertEqual(
            tuple(axes),
            (
                "correctness", "simplification", "tests", "documentation",
                "style", "intent", "design-api", "performance",
            ),
        )

    def test_returns_nine_with_coherence_active(self):
        axes = axis_dispatch.decide_axes({"activates_coherence": True})
        self.assertEqual(len(axes), 9)
        self.assertEqual(axes[-1], "coherence")

    def test_coherence_never_launched_without_metadata_diff(self):
        # Spec AC: Coherence axis is NEVER launched if no metadata files in diff.
        axes = axis_dispatch.decide_axes({})
        self.assertNotIn("coherence", axes)
        axes = axis_dispatch.decide_axes({"activates_coherence": False})
        self.assertNotIn("coherence", axes)

    def test_returns_fresh_list_not_tuple(self):
        # Callers may want to mutate the list.
        axes = axis_dispatch.decide_axes({})
        axes.append("test-mutation")  # must not raise
        self.assertIn("test-mutation", axes)

    def test_explicit_subset_is_honored(self):
        axes = axis_dispatch.decide_axes(
            {"activates_coherence": False}, ["correctness", "tests"]
        )
        self.assertEqual(axes, ["correctness", "tests"])

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


class TestParallelCap(unittest.TestCase):

    def test_axis_count_within_cap(self):
        # 8 + Coherence = 9, within 10 cap.
        self.assertLessEqual(
            len(axis_dispatch.CANONICAL_AXES)
            + len(axis_dispatch.CONDITIONAL_AXES),
            axis_dispatch.MAX_PARALLEL_AXES,
        )


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


class TestFilterFindings(unittest.TestCase):

    def test_correctness_has_no_deterministic_tool_findings(self):
        out = axis_dispatch.filter_findings_by_axis(
            SAMPLE_FINDINGS, "correctness"
        )
        self.assertEqual(out, [])

    def test_simplification_returns_only_simplification(self):
        # Spec AC: Correctness subagent does NOT see Simplification axis tool findings.
        out = axis_dispatch.filter_findings_by_axis(
            SAMPLE_FINDINGS, "simplification"
        )
        tools = {f["source_tool"] for f in out}
        self.assertEqual(tools, {"knip", "dupl"})
        self.assertEqual(len(out), 2)

    def test_axes_with_no_tool_input_return_empty(self):
        # These axes have no deterministic findings in the battery fixture.
        for axis in ("correctness", "tests", "style", "intent", "coherence"):
            out = axis_dispatch.filter_findings_by_axis(SAMPLE_FINDINGS, axis)
            self.assertEqual(out, [], f"axis {axis} should have no findings")

    def test_no_axis_leak_across_filters(self):
        # Every finding routes to exactly one axis — sum of per-axis counts
        # equals total finding count.
        total = 0
        for axis in axis_dispatch.CANONICAL_AXES + axis_dispatch.CONDITIONAL_AXES:
            total += len(axis_dispatch.filter_findings_by_axis(
                SAMPLE_FINDINGS, axis
            ))
        self.assertEqual(total, len(SAMPLE_FINDINGS))

    def test_findings_without_axis_field_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown or missing axis"):
            axis_dispatch.filter_findings_by_axis(
                [{"file": "a.py", "message": "no axis"}], "correctness"
            )

    def test_unknown_axis_and_non_deterministic_confidence_are_rejected(self):
        invalid = dict(SAMPLE_FINDINGS[0], axis="security")
        with self.assertRaisesRegex(ValueError, "unknown or missing axis"):
            axis_dispatch.filter_findings_by_axis([invalid], "correctness")
        invalid = dict(SAMPLE_FINDINGS[0], confidence=99)
        with self.assertRaisesRegex(ValueError, "confidence 100"):
            axis_dispatch.filter_findings_by_axis([invalid], "simplification")

    def test_incomplete_canonical_finding_is_rejected(self):
        invalid = dict(SAMPLE_FINDINGS[0])
        invalid.pop("severity")
        with self.assertRaisesRegex(ValueError, "invalid severity"):
            axis_dispatch.filter_findings_by_axis([invalid], "simplification")
        invalid = dict(SAMPLE_FINDINGS[0], line_end=0)
        with self.assertRaisesRegex(ValueError, "invalid line range"):
            axis_dispatch.filter_findings_by_axis([invalid], "simplification")

    def test_unknown_source_tool_and_wrong_tool_axis_are_rejected(self):
        unknown = dict(SAMPLE_FINDINGS[0], source_tool="invented-analyzer")
        with self.assertRaisesRegex(ValueError, "unknown source_tool"):
            axis_dispatch.filter_findings_by_axis([unknown], "simplification")
        misrouted = dict(SAMPLE_FINDINGS[0], axis="documentation")
        with self.assertRaisesRegex(ValueError, "expected 'simplification'"):
            axis_dispatch.filter_findings_by_axis([misrouted], "documentation")

    def test_mutation_sources_route_only_to_tests(self):
        for source_tool in ("stryker", "mutmut", "pitest"):
            with self.subTest(source_tool=source_tool):
                finding = {
                    "axis": "tests",
                    "location": "src/example.py:1",
                    "severity": "Medium",
                    "source_tool": source_tool,
                    "finding": "mutation survived",
                    "recommendation": "add a covering assertion",
                    "confidence": 100,
                }
                self.assertEqual(
                    axis_dispatch.filter_findings_by_axis([finding], "tests"),
                    [finding],
                )

    def test_mutation_finding_rejects_battery_schema(self):
        with self.assertRaisesRegex(ValueError, "invalid location"):
            axis_dispatch._validate_tool_finding(
                {
                    "axis": "tests",
                    "file": "src/example.py",
                    "line_start": 1,
                    "line_end": 1,
                    "severity": "Medium",
                    "source_tool": "mutmut",
                    "message": "mutation survived",
                    "confidence": 100,
                }
            )


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------


class TestBuildPrompt(unittest.TestCase):
    """Spec AC: Each subagent prompt cites references/anthropic-verbatim.md
    HIGH SIGNAL criteria AND false-positive list."""

    def setUp(self):
        self.input_path = Path("/tmp/axis-input-test/correctness.json")

    def test_prompt_cites_anthropic_verbatim_rubric(self):
        prompt = axis_dispatch.build_axis_prompt(
            axis="correctness", findings_count=3,
            skill_dir=SKILL_DIR, input_path=self.input_path,
        )
        self.assertIn("references/anthropic-verbatim.md", prompt)
        self.assertIn("0-100 confidence rubric", prompt)
        self.assertIn("VERBATIM", prompt)

    def test_prompt_cites_false_positive_taxonomy(self):
        prompt = axis_dispatch.build_axis_prompt(
            axis="simplification", findings_count=0,
            skill_dir=SKILL_DIR, input_path=self.input_path,
        )
        self.assertIn("false positives", prompt)
        self.assertIn("documented taxonomy", prompt)

    def test_prompt_cites_agent_assumption_rule(self):
        # Verbatim agent-assumption rule: do not check build signal.
        prompt = axis_dispatch.build_axis_prompt(
            axis="correctness", findings_count=0,
            skill_dir=SKILL_DIR, input_path=self.input_path,
        )
        self.assertIn("build signal", prompt)
        self.assertIn("CI does that", prompt)

    def test_prompt_instructs_coverage_not_filtering(self):
        # Two-stage harness: finders maximize coverage, validators filter.
        # Without this, current models self-filter at the finding stage and recall drops.
        prompt = axis_dispatch.build_axis_prompt(
            axis="correctness", findings_count=0,
            skill_dir=SKILL_DIR, input_path=self.input_path,
        )
        self.assertIn("Coverage, not filtering", prompt)
        self.assertIn("coverage, not ranking", prompt)
        self.assertIn("Phase 4 validators", prompt)

    def test_prompt_cites_axis_brief(self):
        prompt = axis_dispatch.build_axis_prompt(
            axis="tests", findings_count=0,
            skill_dir=SKILL_DIR, input_path=self.input_path,
        )
        self.assertIn("references/axes/tests.md", prompt)

    def test_prompt_includes_input_path(self):
        prompt = axis_dispatch.build_axis_prompt(
            axis="design-api", findings_count=5,
            skill_dir=SKILL_DIR, input_path=self.input_path,
        )
        self.assertIn(str(self.input_path), prompt)

    def test_prompt_includes_findings_count(self):
        prompt = axis_dispatch.build_axis_prompt(
            axis="correctness", findings_count=7,
            skill_dir=SKILL_DIR, input_path=self.input_path,
        )
        self.assertIn("Tool findings (pre-filtered to your axis, confidence 100): 7", prompt)

    def test_prompt_forbids_write_edit(self):
        prompt = axis_dispatch.build_axis_prompt(
            axis="style", findings_count=0,
            skill_dir=SKILL_DIR, input_path=self.input_path,
        )
        self.assertIn("Do NOT use `Write`, `Edit`", prompt)

    def test_unknown_axis_raises(self):
        with self.assertRaises(ValueError):
            axis_dispatch.build_axis_prompt(
                axis="bogus-axis", findings_count=0,
                skill_dir=SKILL_DIR, input_path=self.input_path,
            )


# ---------------------------------------------------------------------------
# Bundle preparation
# ---------------------------------------------------------------------------


class TestPrepareAxisBundle(unittest.TestCase):

    def test_writes_input_and_prompt_files(self):
        with tempfile.TemporaryDirectory() as td:
            output_dir = Path(td)
            scope = {"repo_kind": "app", "activates_coherence": False}
            result = axis_dispatch.prepare_axis_bundle(
                axis="correctness", scope=scope,
                all_findings=SAMPLE_FINDINGS, diff_text="diff --git",
                output_dir=output_dir, skill_dir=SKILL_DIR,
            )

            self.assertEqual(result["axis"], "correctness")
            self.assertEqual(result["findings_count"], 0)
            self.assertTrue(Path(result["input_path"]).is_file())
            self.assertTrue(Path(result["prompt_path"]).is_file())

            bundle = json.loads(
                Path(result["input_path"]).read_text(encoding="utf-8")
            )
            self.assertEqual(bundle["axis"], "correctness")
            self.assertEqual(bundle["scope"], scope)
            self.assertEqual(bundle["findings"], [])
            self.assertEqual(bundle["diff_text"], "diff --git")
            self.assertTrue(bundle["brief_path"].endswith(
                "references/axes/correctness.md"
            ))
            self.assertTrue(bundle["anthropic_verbatim_path"].endswith(
                "references/anthropic-verbatim.md"
            ))

    def test_bundle_for_empty_axis_still_valid(self):
        # An axis with zero tool findings still produces a bundle —
        # subagent runs LLM judgment on the diff alone.
        with tempfile.TemporaryDirectory() as td:
            result = axis_dispatch.prepare_axis_bundle(
                axis="style", scope={"activates_coherence": False},
                all_findings=SAMPLE_FINDINGS, diff_text="",
                output_dir=Path(td), skill_dir=SKILL_DIR,
            )
            self.assertEqual(result["findings_count"], 0)
            bundle = json.loads(
                Path(result["input_path"]).read_text(encoding="utf-8")
            )
            self.assertEqual(bundle["findings"], [])


class TestPrepareAll(unittest.TestCase):

    def test_prepare_emits_eight_bundles_when_coherence_inactive(self):
        with tempfile.TemporaryDirectory() as td:
            result = axis_dispatch.prepare(
                scope={"activates_coherence": False},
                all_findings=SAMPLE_FINDINGS, diff_text="",
                output_dir=Path(td), skill_dir=SKILL_DIR,
            )
            self.assertEqual(len(result["axes"]), 8)
            self.assertEqual(len(result["bundles"]), 8)
            self.assertFalse(result["coherence_active"])
            self.assertNotIn("coherence", result["bundles"])

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
            corr_bundle = json.loads(
                Path(result["bundles"]["correctness"]["input_path"])
                .read_text(encoding="utf-8")
            )
            # Correctness has no deterministic analyzer in this battery.
            corr_tools = {f["source_tool"] for f in corr_bundle["findings"]}
            self.assertEqual(corr_tools, set())
            self.assertNotIn("knip", corr_tools)
            self.assertNotIn("dupl", corr_tools)
            # Semgrep's bundled rules route only to Performance.
            perf_bundle = json.loads(
                Path(result["bundles"]["performance"]["input_path"])
                .read_text(encoding="utf-8")
            )
            self.assertEqual(
                {f["source_tool"] for f in perf_bundle["findings"]},
                {"semgrep"},
            )

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
# Cross-checks against synthesis_core
# ---------------------------------------------------------------------------


class TestAxisKeyParity(unittest.TestCase):
    """The canonical axis tuple in axis_dispatch.py must mirror the one in
    synthesis_core.py — a divergence breaks Phase 5 dedup."""

    def test_canonical_axes_match_synthesis_core(self):
        synth_spec = importlib.util.spec_from_file_location(
            "synthesis_core",
            REPO_ROOT / "skills" / "code-ultrareview" / "scripts"
            / "synthesis_core.py",
        )
        assert synth_spec is not None and synth_spec.loader is not None
        synth = importlib.util.module_from_spec(synth_spec)
        synth_spec.loader.exec_module(synth)
        self.assertEqual(
            axis_dispatch.CANONICAL_AXES,
            synth.CANONICAL_AXES,
        )
        self.assertEqual(
            axis_dispatch.CONDITIONAL_AXES,
            synth.CONDITIONAL_AXES,
        )


# ---------------------------------------------------------------------------
# CLI smoke test
# ---------------------------------------------------------------------------


class TestCliPrepare(unittest.TestCase):
    def test_prepare_rejects_mistyped_coverage_without_traceback(self):
        import subprocess

        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            scope_path = tdir / "scope.json"
            findings_path = tdir / "tool-findings.jsonl"
            diff_path = tdir / "diff.patch"
            scope_path.write_text(
                json.dumps({
                    "repo_kind": "app",
                    "languages": ["typescript"],
                    "tool_coverage": "complete",
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

        self.assertEqual(result.returncode, 4)
        self.assertIn("tool_coverage must be an object", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_prepare_rejects_non_object_mutation_manifest_without_traceback(self):
        import subprocess

        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            scope_path = tdir / "scope.json"
            findings_path = tdir / "tool-findings.jsonl"
            diff_path = tdir / "diff.patch"
            scope_path.write_text(
                json.dumps({
                    "repo_kind": "app",
                    "languages": ["typescript"],
                    "tools_skipped": [],
                    "tools_missing": [],
                    "tool_coverage": {"complete": True},
                    "mutation_coverage": "complete",
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

        self.assertEqual(result.returncode, 4)
        self.assertIn("mutation_coverage must be an object", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    """End-to-end: prepare command writes bundles for the 8 canonical axes
    when invoked from the shell."""

    def test_cli_prepare_writes_bundles(self):
        import subprocess

        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            scope_path = tdir / "scope.json"
            findings_path = tdir / "tool-findings.jsonl"
            diff_path = tdir / "diff.patch"
            output_dir = tdir / "run"

            scope_path.write_text(json.dumps({
                "repo_kind": "app",
                "languages": ["typescript"],
                "claude_md_chain": [],
                "activates_coherence": False,
                "files": ["src/x.ts"],
                "tools_skipped": [],
                "tools_missing": [],
                "tool_coverage": {"complete": True},
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
                self.assertTrue(Path(bundle["input_path"]).is_file())
                self.assertTrue(Path(bundle["prompt_path"]).is_file())

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
                            "repo_kind": "app",
                            "languages": ["typescript"],
                            "claude_md_chain": [],
                            "activates_coherence": coherence,
                            "files": ["src/x.ts"],
                            "tools_skipped": [],
                            "tools_missing": [],
                            "tool_coverage": {"complete": True},
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
                    "repo_kind": "app",
                    "languages": ["markdown"],
                    "activates_coherence": False,
                    "tools_skipped": [],
                    "tools_missing": [],
                    "tool_coverage": {"complete": True},
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
            self.assertIn("required tool findings file is missing", result.stderr)
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
                    "repo_kind": "app",
                    "languages": ["java"],
                    "activates_coherence": False,
                    "tools_skipped": [],
                    "tools_missing": [],
                    "tool_coverage": {"complete": True},
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
                    "repo_kind": "app",
                    "languages": ["typescript"],
                    "activates_coherence": False,
                    "tools_skipped": [],
                    "tools_missing": [],
                    "tool_coverage": {"complete": True},
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
            self.assertIn("digest mismatch", blocked.stderr)
            self.assertFalse((tdir / "blocked").exists())

    def test_prepare_rejects_invalid_tool_finding_without_writing_bundles(self):
        import subprocess

        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            scope_path = tdir / "scope.json"
            findings_path = tdir / "tool-findings.jsonl"
            diff_path = tdir / "diff.patch"
            scope_path.write_text(
                json.dumps({
                    "repo_kind": "app",
                    "languages": ["typescript"],
                    "activates_coherence": False,
                    "tools_skipped": [],
                    "tools_missing": [],
                    "tool_coverage": {"complete": True},
                }),
                encoding="utf-8",
            )
            findings_path.write_text(
                json.dumps({
                    "axis": "security",
                    "source_tool": "fake",
                    "message": "must not be dropped",
                    "confidence": 100,
                }) + "\n",
                encoding="utf-8",
            )
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
            self.assertIn("unknown or missing axis", result.stderr)
            self.assertFalse((tdir / "run").exists())


class TestCliIngest(unittest.TestCase):
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
