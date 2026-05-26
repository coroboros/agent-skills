"""Tests for skills/code-ultrareview/scripts/run_validators.py.

Covers the deterministic Phase 4 orchestrator contracts: sub-80 filter
(tool findings never validated), batching cap (≤10 parallel),
CLAUDE.md snippet lookup with deepest-match precedence, validator
prompt construction (verbatim anthropic rubric, CLAUDE.md re-check,
agent-assumption rule), per-finding bundle preparation, validator
stdout parsing, and the A2-preserving ingest contract (promote ≥80 /
demote <80 / no silent drop).

Behavioral evaluation of validator scoring lives in `evals/evals.json`,
not in this unit-test file — that work is non-deterministic LLM output.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "skills" / "code-ultrareview" / "scripts" / "run_validators.py"
SYNTH = REPO_ROOT / "skills" / "code-ultrareview" / "scripts" / "synthesis_core.py"
SKILL_DIR = REPO_ROOT / "skills" / "code-ultrareview"


def _load_module():
    spec = importlib.util.spec_from_file_location("run_validators", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_synth():
    spec = importlib.util.spec_from_file_location("synthesis_core", SYNTH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


run_validators = _load_module()
synthesis_core = _load_synth()


# ---------------------------------------------------------------------------
# Sample sub-80 finding — shape mirrors Phase 3 output AFTER apply_a2 has
# downgraded to Low + added [unverified] prefix + preserved original_severity.
# ---------------------------------------------------------------------------


def make_unverified_finding(
    *,
    confidence: int = 70,
    location: str = "src/auth.ts:42",
    axis: str = "correctness",
    rule: str | None = None,
    finding_text: str | None = None,
    original_severity: str = "Medium",
) -> dict:
    """Build a sub-80 finding in the post-A2 shape Phase 4 receives."""
    base_text = finding_text or "Off-by-one in user lookup"
    return {
        "axis": axis,
        "severity": "Low",
        "location": location,
        "finding": f"{synthesis_core.UNVERIFIED_PREFIX} {base_text}",
        "recommendation": (
            f"Sub-{synthesis_core.CONFIDENCE_THRESHOLD} confidence "
            f"({confidence}) — verify locally before action. "
            "Replace `< len` with `<= len - 1`."
        ),
        "confidence": confidence,
        "rule": rule,
        "meta": {
            "original_severity": original_severity,
            "marker": "🟢",
        },
    }


# ---------------------------------------------------------------------------
# Threshold SSOT — run_validators must defer to synthesis_core
# ---------------------------------------------------------------------------


class TestThresholdSsot(unittest.TestCase):
    """A divergence between run_validators.CONFIDENCE_THRESHOLD and
    synthesis_core.CONFIDENCE_THRESHOLD breaks the A2 contract — one
    side promotes, the other still says sub-80."""

    def test_threshold_matches_synthesis_core(self):
        self.assertEqual(
            run_validators.CONFIDENCE_THRESHOLD,
            synthesis_core.CONFIDENCE_THRESHOLD,
        )

    def test_promotion_cap_matches_synthesis_core(self):
        self.assertEqual(
            run_validators.PROMOTION_CAP,
            synthesis_core.PROMOTION_CAP,
        )

    def test_unverified_prefix_matches_synthesis_core(self):
        self.assertEqual(
            run_validators.UNVERIFIED_PREFIX,
            synthesis_core.UNVERIFIED_PREFIX,
        )


# ---------------------------------------------------------------------------
# filter_sub_threshold — confidence-100 tool findings never validated
# ---------------------------------------------------------------------------


class TestFilterSubThreshold(unittest.TestCase):

    def test_confidence_100_excluded(self):
        """Spec AC: Validators NEVER run on confidence-100 tool findings."""
        out = run_validators.filter_sub_threshold([
            {"confidence": 100, "source_tool": "semgrep"},
            {"confidence": 100, "source_tool": "knip"},
        ])
        self.assertEqual(out, [])

    def test_confidence_0_excluded(self):
        """Confidence 0 is the false-positive sentinel from the rubric — A2
        already drops these; validators never see them either."""
        out = run_validators.filter_sub_threshold([{"confidence": 0}])
        self.assertEqual(out, [])

    def test_confidence_at_threshold_excluded(self):
        """80 is already verified; no validator pass needed."""
        out = run_validators.filter_sub_threshold([{"confidence": 80}])
        self.assertEqual(out, [])

    def test_confidence_above_threshold_excluded(self):
        out = run_validators.filter_sub_threshold([
            {"confidence": 85},
            {"confidence": 95},
        ])
        self.assertEqual(out, [])

    def test_sub_80_above_zero_included(self):
        findings = [
            {"confidence": 1},
            {"confidence": 50},
            {"confidence": 75},
            {"confidence": 79},
        ]
        out = run_validators.filter_sub_threshold(findings)
        self.assertEqual(len(out), 4)

    def test_mixed_set_keeps_only_sub_threshold_above_zero(self):
        findings = [
            {"confidence": 100, "id": "tool"},
            {"confidence": 0, "id": "drop"},
            {"confidence": 50, "id": "keep"},
            {"confidence": 80, "id": "verified"},
            {"confidence": 75, "id": "keep2"},
        ]
        out = run_validators.filter_sub_threshold(findings)
        ids = {f["id"] for f in out}
        self.assertEqual(ids, {"keep", "keep2"})


# ---------------------------------------------------------------------------
# batch — never exceed 10 parallel validators
# ---------------------------------------------------------------------------


class TestBatch(unittest.TestCase):

    def test_25_findings_to_three_batches_10_10_5(self):
        """Spec AC verbatim: 25 still-sub-80 findings → 3 batches
        (10 + 10 + 5), never 25 simultaneously."""
        batches = run_validators.batch(list(range(25)))
        self.assertEqual(len(batches), 3)
        self.assertEqual([len(b) for b in batches], [10, 10, 5])

    def test_under_cap_single_batch(self):
        batches = run_validators.batch(list(range(7)))
        self.assertEqual(len(batches), 1)
        self.assertEqual(len(batches[0]), 7)

    def test_exactly_at_cap_single_batch(self):
        batches = run_validators.batch(list(range(10)))
        self.assertEqual(len(batches), 1)
        self.assertEqual(len(batches[0]), 10)

    def test_empty_list_zero_batches(self):
        batches = run_validators.batch([])
        self.assertEqual(batches, [])

    def test_invalid_size_raises(self):
        with self.assertRaises(ValueError):
            run_validators.batch([1, 2, 3], size=0)
        with self.assertRaises(ValueError):
            run_validators.batch([1, 2, 3], size=-1)

    def test_batches_cover_all_items_in_order(self):
        items = list(range(23))
        batches = run_validators.batch(items)
        rebuilt: list[int] = []
        for b in batches:
            rebuilt.extend(b)
        self.assertEqual(rebuilt, items)


# ---------------------------------------------------------------------------
# find_claude_md_snippet — deepest-match precedence
# ---------------------------------------------------------------------------


class TestFindClaudeMdSnippet(unittest.TestCase):

    def test_returns_none_when_chain_empty(self):
        with tempfile.TemporaryDirectory() as td:
            path, snippet = run_validators.find_claude_md_snippet(
                "production grade or nothing", [], Path(td),
            )
            self.assertIsNone(path)
            self.assertIsNone(snippet)

    def test_returns_none_when_rule_text_empty(self):
        with tempfile.TemporaryDirectory() as td:
            path, snippet = run_validators.find_claude_md_snippet(
                "", ["CLAUDE.md"], Path(td),
            )
            self.assertIsNone(path)
            self.assertIsNone(snippet)

    def test_deepest_match_wins(self):
        """Chain ordered root-to-deepest; nested overrides surface correctly."""
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            root = repo / "CLAUDE.md"
            nested = repo / "src" / "CLAUDE.md"
            nested.parent.mkdir(parents=True)
            root.write_text(
                "## Behavior\n\nProduction grade or nothing.\n",
                encoding="utf-8",
            )
            nested.write_text(
                "## Local override\n\nProduction grade or nothing. Stricter here.\n",
                encoding="utf-8",
            )
            path, snippet = run_validators.find_claude_md_snippet(
                "production grade or nothing",
                ["CLAUDE.md", "src/CLAUDE.md"],
                repo,
            )
            self.assertEqual(path, "src/CLAUDE.md")
            self.assertIn("Stricter here", snippet)

    def test_returns_none_when_rule_absent_from_all(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "CLAUDE.md").write_text(
                "## Behavior\n\nReadable code.\n", encoding="utf-8",
            )
            path, snippet = run_validators.find_claude_md_snippet(
                "an entirely different rule that does not exist anywhere",
                ["CLAUDE.md"], repo,
            )
            self.assertIsNone(path)
            self.assertIsNone(snippet)

    def test_case_insensitive_match(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "CLAUDE.md").write_text(
                "## Behavior\n\nNEVER COMMIT SECRETS to git.\n",
                encoding="utf-8",
            )
            path, _ = run_validators.find_claude_md_snippet(
                "never commit secrets", ["CLAUDE.md"], repo,
            )
            self.assertEqual(path, "CLAUDE.md")

    def test_absolute_path_in_chain_resolved_directly(self):
        with tempfile.TemporaryDirectory() as td:
            external = Path(td) / "global-rules.md"
            external.write_text(
                "Single source of truth for every value.\n", encoding="utf-8",
            )
            path, snippet = run_validators.find_claude_md_snippet(
                "single source of truth",
                [str(external)],
                Path(td) / "unrelated-repo",
            )
            self.assertEqual(path, str(external))
            self.assertIn("Single source of truth", snippet)


# ---------------------------------------------------------------------------
# extract_diff_context
# ---------------------------------------------------------------------------


class TestExtractDiffContext(unittest.TestCase):

    def test_returns_empty_for_empty_diff(self):
        self.assertEqual(
            run_validators.extract_diff_context("", "src/x.ts:1"), "",
        )

    def test_anchors_on_filename(self):
        diff = "\n".join([
            "diff --git a/unrelated.ts b/unrelated.ts",
            "@@ -1 +1 @@",
            "-old",
            "+new",
        ] + ["padding"] * 50 + [
            "diff --git a/target.ts b/target.ts",
            "@@ -10 +10 @@",
            "-bad",
            "+good",
        ])
        ctx = run_validators.extract_diff_context(diff, "target.ts:10")
        self.assertIn("target.ts", ctx)

    def test_falls_back_to_head_when_filename_missing(self):
        diff = "line1\nline2\nline3\n"
        ctx = run_validators.extract_diff_context(diff, "missing.ts:1")
        self.assertIn("line1", ctx)


# ---------------------------------------------------------------------------
# build_validator_prompt — cites the contract sources verbatim
# ---------------------------------------------------------------------------


class TestBuildValidatorPrompt(unittest.TestCase):
    """Spec AC: validator prompt cites the verbatim anthropic rubric + the
    CLAUDE.md re-check requirement + the agent-assumption rule."""

    def _build(self, **overrides):
        finding = overrides.pop("finding", make_unverified_finding())
        return run_validators.build_validator_prompt(
            finding=finding,
            diff_context=overrides.get("diff_context", "@@ -1 +1 @@\n+bad\n"),
            claude_md_snippet=overrides.get(
                "claude_md_snippet", "Single source of truth."
            ),
            claude_md_path=overrides.get("claude_md_path", "CLAUDE.md"),
            anthropic_verbatim_path=overrides.get(
                "anthropic_verbatim_path",
                str(SKILL_DIR / "references" / "anthropic-verbatim.md"),
            ),
        )

    def test_cites_anthropic_verbatim_rubric(self):
        prompt = self._build()
        self.assertIn("references/anthropic-verbatim.md", prompt)
        self.assertIn("0-100 confidence rubric", prompt)
        self.assertIn("VERBATIM", prompt)

    def test_cites_false_positive_taxonomy(self):
        prompt = self._build()
        self.assertIn("false positives", prompt)
        self.assertIn("documented taxonomy", prompt)

    def test_cites_claude_md_re_check_requirement(self):
        """Spec AC: validator confirms the rule exists in claude_md_chain
        AND either promotes or demotes with 'CLAUDE.md rule not found at <path>'."""
        prompt = self._build()
        self.assertIn("CLAUDE.md", prompt)
        self.assertIn("CLAUDE.md rule not found at", prompt)

    def test_cites_agent_assumption_rule(self):
        prompt = self._build()
        self.assertIn("build signal", prompt)
        self.assertIn("CI does that", prompt)

    def test_emits_finding_json(self):
        prompt = self._build(
            finding=make_unverified_finding(location="src/foo.py:10"),
        )
        self.assertIn("src/foo.py:10", prompt)

    def test_output_schema_present(self):
        prompt = self._build()
        self.assertIn("score:", prompt)
        self.assertIn("reason:", prompt)

    def test_missing_claude_md_renders_placeholder(self):
        prompt = self._build(claude_md_snippet=None, claude_md_path=None)
        self.assertIn("not found in claude_md_chain", prompt)
        self.assertIn("(none)", prompt)

    def test_forbids_write_edit_bash(self):
        prompt = self._build()
        self.assertIn("Do NOT use `Write`", prompt)

    def test_uses_read_only(self):
        prompt = self._build()
        self.assertIn("`Read`", prompt)


# ---------------------------------------------------------------------------
# prepare_validator_bundle — disk artefacts the orchestrator reads
# ---------------------------------------------------------------------------


class TestPrepareValidatorBundle(unittest.TestCase):

    def test_writes_input_and_prompt_files(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "CLAUDE.md").write_text(
                "Production grade or nothing.\n", encoding="utf-8",
            )
            output_dir = repo / "run"
            scope = {
                "claude_md_chain": ["CLAUDE.md"],
                "repo_kind": "app",
            }
            finding = make_unverified_finding(
                rule="production grade or nothing",
            )
            result = run_validators.prepare_validator_bundle(
                index=0, finding=finding, scope=scope,
                diff_text="@@ -1 +1 @@\n+bad\n",
                output_dir=output_dir, skill_dir=SKILL_DIR, repo_dir=repo,
            )
            self.assertEqual(result["index"], 0)
            self.assertTrue(Path(result["input_path"]).is_file())
            self.assertTrue(Path(result["prompt_path"]).is_file())

            bundle = json.loads(
                Path(result["input_path"]).read_text(encoding="utf-8")
            )
            self.assertEqual(bundle["index"], 0)
            self.assertEqual(bundle["finding"]["location"], "src/auth.ts:42")
            self.assertEqual(bundle["claude_md_path"], "CLAUDE.md")
            self.assertIn("Production grade", bundle["claude_md_snippet"])
            self.assertTrue(bundle["anthropic_verbatim_path"].endswith(
                "references/anthropic-verbatim.md"
            ))

    def test_bundle_with_no_matching_claude_rule(self):
        with tempfile.TemporaryDirectory() as td:
            output_dir = Path(td) / "run"
            finding = make_unverified_finding(rule="rule that does not exist")
            result = run_validators.prepare_validator_bundle(
                index=3, finding=finding,
                scope={"claude_md_chain": []},
                diff_text="", output_dir=output_dir,
                skill_dir=SKILL_DIR, repo_dir=Path(td),
            )
            bundle = json.loads(
                Path(result["input_path"]).read_text(encoding="utf-8")
            )
            self.assertIsNone(bundle["claude_md_path"])
            self.assertIsNone(bundle["claude_md_snippet"])
            prompt = Path(result["prompt_path"]).read_text(encoding="utf-8")
            self.assertIn("not found in claude_md_chain", prompt)

    def test_zero_padded_filenames(self):
        with tempfile.TemporaryDirectory() as td:
            output_dir = Path(td) / "run"
            result = run_validators.prepare_validator_bundle(
                index=7, finding=make_unverified_finding(),
                scope={"claude_md_chain": []},
                diff_text="", output_dir=output_dir,
                skill_dir=SKILL_DIR, repo_dir=Path(td),
            )
            self.assertTrue(result["input_path"].endswith("0007.json"))
            self.assertTrue(result["prompt_path"].endswith("0007.txt"))


# ---------------------------------------------------------------------------
# prepare — full pipeline; filtering + bundling + batching
# ---------------------------------------------------------------------------


class TestPrepare(unittest.TestCase):

    def test_filter_applied_before_bundling(self):
        with tempfile.TemporaryDirectory() as td:
            output_dir = Path(td) / "run"
            findings = [
                {"confidence": 100, "source_tool": "semgrep", "axis": "correctness"},
                make_unverified_finding(confidence=70),
                {"confidence": 0, "axis": "intent"},
                make_unverified_finding(confidence=55, location="src/b.ts:5"),
                {"confidence": 90, "axis": "tests"},
            ]
            result = run_validators.prepare(
                findings=findings,
                scope={"claude_md_chain": []},
                diff_text="", output_dir=output_dir,
                skill_dir=SKILL_DIR, repo_dir=Path(td),
            )
            # Only the two sub-80 + above-zero findings made it through.
            self.assertEqual(result["count"], 2)
            self.assertEqual(len(result["bundles"]), 2)

    def test_25_findings_three_batches(self):
        with tempfile.TemporaryDirectory() as td:
            output_dir = Path(td) / "run"
            findings = [
                make_unverified_finding(
                    confidence=50 + i % 25, location=f"src/x.ts:{i}",
                )
                for i in range(25)
            ]
            result = run_validators.prepare(
                findings=findings,
                scope={"claude_md_chain": []},
                diff_text="", output_dir=output_dir,
                skill_dir=SKILL_DIR, repo_dir=Path(td),
            )
            self.assertEqual(result["count"], 25)
            self.assertEqual(len(result["batches"]), 3)
            self.assertEqual(
                [len(b) for b in result["batches"]], [10, 10, 5],
            )

    def test_tool_findings_never_bundled(self):
        """Spec AC verified end-to-end: confidence-100 tool findings never
        get a validator-input bundle."""
        with tempfile.TemporaryDirectory() as td:
            output_dir = Path(td) / "run"
            tool_finding = {
                "confidence": 100, "source_tool": "semgrep",
                "axis": "performance", "location": "src/q.py:22",
                "severity": "High", "finding": "N+1",
                "recommendation": "use joinedload",
            }
            findings = [tool_finding, make_unverified_finding(confidence=60)]
            result = run_validators.prepare(
                findings=findings,
                scope={"claude_md_chain": []},
                diff_text="", output_dir=output_dir,
                skill_dir=SKILL_DIR, repo_dir=Path(td),
            )
            self.assertEqual(result["count"], 1)
            # The single bundle's finding must be the sub-80 one, not the tool.
            bundle_path = Path(result["bundles"][0]["input_path"])
            bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
            self.assertEqual(bundle["finding"]["location"], "src/auth.ts:42")
            self.assertNotEqual(bundle["finding"].get("source_tool"), "semgrep")


# ---------------------------------------------------------------------------
# parse_validator_output
# ---------------------------------------------------------------------------


class TestParseValidatorOutput(unittest.TestCase):

    def test_canonical_two_line_output(self):
        score, reason = run_validators.parse_validator_output(
            "score: 90\nreason: Confirmed via CLAUDE.md citation"
        )
        self.assertEqual(score, 90)
        self.assertEqual(reason, "Confirmed via CLAUDE.md citation")

    def test_tolerates_surrounding_chatter(self):
        score, reason = run_validators.parse_validator_output(
            "Looking at the finding…\n\nscore: 45\nreason: rule not found\n"
        )
        self.assertEqual(score, 45)
        self.assertEqual(reason, "rule not found")

    def test_empty_stdout_raises(self):
        with self.assertRaises(ValueError):
            run_validators.parse_validator_output("")

    def test_missing_score_raises(self):
        with self.assertRaises(ValueError):
            run_validators.parse_validator_output("reason: standalone\n")

    def test_missing_reason_raises(self):
        with self.assertRaises(ValueError):
            run_validators.parse_validator_output("score: 80\n")

    def test_score_out_of_range_raises(self):
        with self.assertRaises(ValueError):
            run_validators.parse_validator_output(
                "score: 101\nreason: too high"
            )


# ---------------------------------------------------------------------------
# ingest — A2 promote/demote semantics
# ---------------------------------------------------------------------------


class TestIngestPromote(unittest.TestCase):
    """Spec AC: a finding promoted by the validator from confidence 70 →
    90 appears in the main report (not Unverified) with the
    `validator_score: 90` field."""

    def test_score_at_threshold_promotes(self):
        findings = [make_unverified_finding(confidence=70)]
        results = [{"index": 0, "score": 80, "reason": "rule confirmed"}]
        out = run_validators.ingest(results, findings)
        self.assertEqual(len(out), 1)
        f = out[0]
        self.assertEqual(f["confidence"], 80)
        self.assertEqual(f["validator_score"], 80)
        self.assertEqual(f["meta"]["validator_outcome"], "promoted")

    def test_promote_70_to_90_records_validator_score(self):
        findings = [make_unverified_finding(confidence=70)]
        results = [{"index": 0, "score": 90, "reason": "real bug confirmed"}]
        out = run_validators.ingest(results, findings)
        f = out[0]
        self.assertEqual(f["validator_score"], 90)
        self.assertEqual(f["confidence"], 90)

    def test_promote_restores_original_severity(self):
        findings = [
            make_unverified_finding(confidence=60, original_severity="High"),
        ]
        results = [{"index": 0, "score": 85, "reason": "confirmed"}]
        out = run_validators.ingest(results, findings)
        self.assertEqual(out[0]["severity"], "High")
        self.assertEqual(out[0]["meta"]["marker"], "🔴")

    def test_promote_strips_unverified_prefix(self):
        findings = [make_unverified_finding(confidence=70)]
        results = [{"index": 0, "score": 85, "reason": "confirmed"}]
        out = run_validators.ingest(results, findings)
        self.assertFalse(
            out[0]["finding"].startswith(synthesis_core.UNVERIFIED_PREFIX),
            f"finding still has unverified prefix: {out[0]['finding']}",
        )

    def test_promote_caps_at_promotion_cap(self):
        findings = [make_unverified_finding(confidence=70)]
        # Validators may not exceed PROMOTION_CAP — keeps a ceiling
        # parallel to build-verification's promotion bonus path.
        results = [{"index": 0, "score": 100, "reason": "absolutely certain"}]
        out = run_validators.ingest(results, findings)
        self.assertLessEqual(
            out[0]["confidence"], synthesis_core.PROMOTION_CAP,
        )
        self.assertEqual(
            out[0]["validator_score"], 100,
            "validator_score records the raw validator output, not the capped value",
        )


class TestIngestDemote(unittest.TestCase):
    """Spec AC: a finding demoted by the validator (stays <80) appears in
    `### ⚠️ Unverified` with the validator's reason text."""

    def test_score_below_threshold_demotes(self):
        findings = [make_unverified_finding(confidence=60)]
        results = [{"index": 0, "score": 40, "reason": "looks like nitpick"}]
        out = run_validators.ingest(results, findings)
        f = out[0]
        self.assertEqual(f["confidence"], 40)
        self.assertEqual(f["validator_score"], 40)
        self.assertEqual(f["meta"]["validator_outcome"], "demoted")
        self.assertEqual(f["meta"]["validator_reason"], "looks like nitpick")

    def test_demote_keeps_severity_low_for_unverified(self):
        findings = [
            make_unverified_finding(confidence=60, original_severity="High"),
        ]
        results = [{"index": 0, "score": 50, "reason": "too speculative"}]
        out = run_validators.ingest(results, findings)
        # Sub-80 stays at Low — A2 routing keeps the marker calm so the
        # report's `### ⚠️ Unverified` section reads as advisory.
        self.assertEqual(out[0]["severity"], "Low")

    def test_demote_records_reason_text(self):
        findings = [make_unverified_finding(confidence=55)]
        reason = "Linter would catch this — false positive per Anthropic taxonomy"
        results = [{"index": 0, "score": 25, "reason": reason}]
        out = run_validators.ingest(results, findings)
        self.assertEqual(out[0]["meta"]["validator_reason"], reason)


class TestIngestClaudeMdNotFound(unittest.TestCase):
    """Spec AC: when the cited CLAUDE.md rule does not exist in
    claude_md_chain, demote with 'CLAUDE.md rule not found at <path>'."""

    def test_demote_with_claude_md_rule_not_found_reason(self):
        findings = [
            make_unverified_finding(
                confidence=70, rule="single source of truth",
            ),
        ]
        reason = "CLAUDE.md rule not found at .claude/rules/behave.md"
        results = [{"index": 0, "score": 30, "reason": reason}]
        out = run_validators.ingest(results, findings)
        self.assertEqual(out[0]["meta"]["validator_reason"], reason)
        self.assertEqual(out[0]["meta"]["validator_outcome"], "demoted")


class TestIngestA2NoDrop(unittest.TestCase):
    """Spec AC: A2 contract — no sub-80 finding silently dropped. Every
    one is either promoted, demoted with reason, or stays in Unverified."""

    def test_input_length_equals_output_length(self):
        findings = [
            make_unverified_finding(confidence=60, location=f"src/x.ts:{i}")
            for i in range(5)
        ]
        results = [
            {"index": 0, "score": 90, "reason": "ok"},
            {"index": 1, "score": 40, "reason": "no"},
            {"index": 2, "score": 85, "reason": "ok"},
            {"index": 3, "score": 30, "reason": "no"},
            {"index": 4, "score": 70, "reason": "still unsure"},
        ]
        out = run_validators.ingest(results, findings)
        self.assertEqual(len(out), len(findings))

    def test_missing_validator_result_surfaces_finding_with_reason(self):
        """No result for a finding → kept as unverified, never dropped."""
        findings = [
            make_unverified_finding(confidence=60, location="src/a.ts:1"),
            make_unverified_finding(confidence=55, location="src/b.ts:2"),
        ]
        # Validator only produced output for index 0.
        results = [{"index": 0, "score": 85, "reason": "ok"}]
        out = run_validators.ingest(results, findings)
        self.assertEqual(len(out), 2)
        self.assertEqual(out[1]["meta"]["validator_outcome"], "demoted")
        self.assertIn(
            "no output",
            out[1]["meta"]["validator_reason"].lower(),
        )

    def test_promoted_and_demoted_findings_partition_the_input(self):
        findings = [
            make_unverified_finding(confidence=60, location=f"src/x.ts:{i}")
            for i in range(3)
        ]
        results = [
            {"index": 0, "score": 90, "reason": "promote"},
            {"index": 1, "score": 30, "reason": "demote"},
            {"index": 2, "score": 80, "reason": "promote at threshold"},
        ]
        out = run_validators.ingest(results, findings)
        outcomes = [f["meta"]["validator_outcome"] for f in out]
        self.assertEqual(outcomes, ["promoted", "demoted", "promoted"])


# ---------------------------------------------------------------------------
# CLI smoke tests — end-to-end via subprocess
# ---------------------------------------------------------------------------


class TestCliPrepare(unittest.TestCase):

    def test_cli_prepare_writes_bundles(self):
        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            scope_path = tdir / "scope.json"
            findings_path = tdir / "axis-findings.jsonl"
            diff_path = tdir / "diff.patch"
            output_dir = tdir / "run"

            scope_path.write_text(json.dumps({
                "claude_md_chain": [],
                "repo_kind": "app",
            }), encoding="utf-8")
            sub_findings = [
                make_unverified_finding(confidence=60, location="src/a.ts:1"),
                make_unverified_finding(confidence=70, location="src/b.ts:2"),
            ]
            findings_path.write_text(
                "\n".join(json.dumps(f) for f in sub_findings) + "\n",
                encoding="utf-8",
            )
            diff_path.write_text("diff --git", encoding="utf-8")

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
            self.assertEqual(payload["count"], 2)
            self.assertEqual(len(payload["bundles"]), 2)
            for info in payload["bundles"].values():
                self.assertTrue(Path(info["input_path"]).is_file())
                self.assertTrue(Path(info["prompt_path"]).is_file())


class TestCliIngest(unittest.TestCase):

    def test_cli_ingest_writes_validated_jsonl(self):
        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            findings_path = tdir / "axis-findings.jsonl"
            results_path = tdir / "validator-results.jsonl"
            output_path = tdir / "validated-findings.jsonl"

            findings = [
                make_unverified_finding(confidence=60, location="src/a.ts:1"),
                make_unverified_finding(confidence=70, location="src/b.ts:2"),
            ]
            findings_path.write_text(
                "\n".join(json.dumps(f) for f in findings) + "\n",
                encoding="utf-8",
            )
            results_path.write_text(
                "\n".join(json.dumps(r) for r in [
                    {"index": 0, "score": 90, "reason": "promote"},
                    {"index": 1, "score": 40, "reason": "demote"},
                ]) + "\n",
                encoding="utf-8",
            )

            proc = subprocess.run(
                [
                    "python3", str(SCRIPT), "ingest",
                    "--findings", str(findings_path),
                    "--results", str(results_path),
                    "--output", str(output_path),
                ],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stderr)
            self.assertTrue(output_path.is_file())
            lines = output_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 2)
            parsed = [json.loads(line) for line in lines]
            outcomes = [p["meta"]["validator_outcome"] for p in parsed]
            self.assertEqual(outcomes, ["promoted", "demoted"])


if __name__ == "__main__":
    unittest.main()
