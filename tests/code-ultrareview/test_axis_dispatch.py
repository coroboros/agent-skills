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
    {"axis": "correctness", "file": "a.py", "line_start": 1,
     "severity": "High", "source_tool": "semgrep",
     "message": "null-deref", "confidence": 100},
    {"axis": "simplification", "file": "b.ts", "line_start": 5,
     "severity": "Low", "source_tool": "knip",
     "message": "unused export", "confidence": 100},
    {"axis": "simplification", "file": "c.go", "line_start": 10,
     "severity": "Medium", "source_tool": "dupl",
     "message": "duplicated block", "confidence": 100},
    {"axis": "documentation", "file": "README.md", "line_start": 3,
     "severity": "Low", "source_tool": "markdownlint-cli2",
     "message": "MD012: multiple blanks", "confidence": 100},
    {"axis": "design-api", "file": "openapi.yaml", "line_start": 12,
     "severity": "High", "source_tool": "oasdiff",
     "message": "DELETE /users — breaking", "confidence": 100},
    {"axis": "performance", "file": "queries.py", "line_start": 22,
     "severity": "High", "source_tool": "semgrep",
     "message": "code-ultrareview-n-plus-one-sqlalchemy", "confidence": 100},
]


class TestFilterFindings(unittest.TestCase):

    def test_correctness_only_returns_correctness(self):
        out = axis_dispatch.filter_findings_by_axis(
            SAMPLE_FINDINGS, "correctness"
        )
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["source_tool"], "semgrep")
        self.assertEqual(out[0]["message"], "null-deref")

    def test_simplification_returns_only_simplification(self):
        # Spec AC: Correctness subagent does NOT see Simplification axis tool findings.
        out = axis_dispatch.filter_findings_by_axis(
            SAMPLE_FINDINGS, "simplification"
        )
        tools = {f["source_tool"] for f in out}
        self.assertEqual(tools, {"knip", "dupl"})
        self.assertEqual(len(out), 2)

    def test_axes_with_no_tool_input_return_empty(self):
        # tests, style, intent, coherence — pure LLM judgment axes.
        for axis in ("tests", "style", "intent", "coherence"):
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

    def test_findings_without_axis_field_silently_skipped(self):
        out = axis_dispatch.filter_findings_by_axis(
            [{"file": "a.py", "message": "no axis"}], "correctness"
        )
        self.assertEqual(out, [])


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
            self.assertEqual(result["findings_count"], 1)
            self.assertTrue(Path(result["input_path"]).is_file())
            self.assertTrue(Path(result["prompt_path"]).is_file())

            bundle = json.loads(
                Path(result["input_path"]).read_text(encoding="utf-8")
            )
            self.assertEqual(bundle["axis"], "correctness")
            self.assertEqual(bundle["scope"], scope)
            self.assertEqual(len(bundle["findings"]), 1)
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
            simp_bundle = json.loads(
                Path(result["bundles"]["simplification"]["input_path"])
                .read_text(encoding="utf-8")
            )
            corr_bundle = json.loads(
                Path(result["bundles"]["correctness"]["input_path"])
                .read_text(encoding="utf-8")
            )
            # Correctness must not see simplification tool findings.
            corr_tools = {f["source_tool"] for f in corr_bundle["findings"]}
            self.assertEqual(corr_tools, {"semgrep"})
            self.assertNotIn("knip", corr_tools)
            self.assertNotIn("dupl", corr_tools)
            # Simplification must not see correctness findings.
            simp_messages = {f["message"] for f in simp_bundle["findings"]}
            self.assertNotIn("null-deref", simp_messages)


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


if __name__ == "__main__":
    unittest.main()
