"""Tests for the WS-5 action-plan computation in aggregation.py."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = REPO_ROOT / "skills" / "code-ultrareview" / "scripts"
AGGREGATION = SCRIPTS_DIR / "aggregation.py"
DETECT_SKILLS = SCRIPTS_DIR / "detect_skills.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


aggregation = _load("aggregation", AGGREGATION)
detect_skills = _load("detect_skills", DETECT_SKILLS)


def _verified(lens: str, severity: str, location: str, finding: str = "Some issue") -> dict:
    f = {
        "lens": lens,
        "severity": severity,
        "location": location,
        "finding": finding,
        "recommendation": "Fix it",
        "confidence": 90,
    }
    return aggregation._attach_marker(f)


def _unverified(lens: str, location: str, finding: str = "Maybe issue") -> dict:
    # Mimic A2 output: severity=Low, marker=🟢, [unverified] prefix.
    f = {
        "lens": lens,
        "severity": "Low",
        "location": location,
        "finding": f"[unverified] {finding}",
        "recommendation": "Sub-80 confidence — verify locally.",
        "confidence": 65,
        "meta": {"original_severity": "High"},
    }
    return aggregation._attach_marker(f)


ALL_SKILLS = {
    "apex": Path("/x/apex/SKILL.md"),
    "oneshot": Path("/x/oneshot/SKILL.md"),
    "humanize-en": Path("/x/humanize-en/SKILL.md"),
    "fix-grammar": Path("/x/fix-grammar/SKILL.md"),
}


class TestActionPlanZeroFindings(unittest.TestCase):
    def test_zero_findings_flag(self):
        plan = aggregation.compute_action_plan(
            [], [], ALL_SKILLS, detect_skills.route_cluster
        )
        self.assertTrue(plan["zero_findings"])
        self.assertEqual(plan["clusters"], [])
        self.assertIsNone(plan["unverified_block"])


class TestActionPlanClusters(unittest.TestCase):
    def test_only_red_findings(self):
        verified = [_verified("bugs-drift", "High", "src/a.ts:1")]
        plan = aggregation.compute_action_plan(
            verified, [], ALL_SKILLS, detect_skills.route_cluster
        )
        self.assertEqual(len(plan["clusters"]), 1)
        self.assertEqual(plan["clusters"][0]["severity"], "🔴")

    def test_only_orange_findings(self):
        verified = [_verified("docs-version", "Medium", "README.md:5")]
        plan = aggregation.compute_action_plan(
            verified, [], ALL_SKILLS, detect_skills.route_cluster
        )
        self.assertEqual(len(plan["clusters"]), 1)
        self.assertEqual(plan["clusters"][0]["severity"], "🟠")

    def test_only_green_collapses_into_single_cluster(self):
        verified = [
            _verified("rules", "Low", "a:1"),
            _verified("bugs-drift", "Low", "b:2"),
            _verified("docs-version", "Low", "c:3"),
        ]
        plan = aggregation.compute_action_plan(
            verified, [], ALL_SKILLS, detect_skills.route_cluster
        )
        green = [c for c in plan["clusters"] if c["severity"] == "🟢"]
        self.assertEqual(len(green), 1)
        self.assertEqual(green[0]["count"], 3)

    def test_severity_ordering(self):
        verified = [
            _verified("rules", "Low", "a:1"),
            _verified("docs-version", "Medium", "b:2"),
            _verified("bugs-drift", "High", "c:3"),
        ]
        plan = aggregation.compute_action_plan(
            verified, [], ALL_SKILLS, detect_skills.route_cluster
        )
        markers = [c["severity"] for c in plan["clusters"]]
        red_idx = markers.index("🔴")
        orange_idx = markers.index("🟠")
        green_idx = markers.index("🟢")
        self.assertLess(red_idx, orange_idx)
        self.assertLess(orange_idx, green_idx)


class TestActionPlanCoverage(unittest.TestCase):
    def test_every_finding_appears_in_some_prompt(self):
        verified = [
            _verified("rules", "High", "a:1", "Critical rule issue"),
            _verified("bugs-drift", "Medium", "b:2", "Drift detected"),
            _verified("docs-version", "Low", "c:3", "Tiny doc nit"),
        ]
        plan = aggregation.compute_action_plan(
            verified, [], ALL_SKILLS, detect_skills.route_cluster
        )
        all_text = " ".join(c["prompt_text"] for c in plan["clusters"])
        self.assertIn("a:1", all_text)
        self.assertIn("b:2", all_text)
        self.assertIn("c:3", all_text)


class TestActionPlanRouting(unittest.TestCase):
    def test_docs_version_orange_routes_through_humanize_en(self):
        verified = [_verified("docs-version", "Medium", "README.md:5")]
        plan = aggregation.compute_action_plan(
            verified, [], ALL_SKILLS, detect_skills.route_cluster
        )
        self.assertEqual(plan["clusters"][0]["command"], "/humanize-en")
        self.assertFalse(plan["clusters"][0]["fallback_used"])

    def test_docs_version_orange_falls_back_when_humanize_missing(self):
        installed = {"apex": Path("/x")}
        verified = [_verified("docs-version", "Medium", "README.md:5")]
        plan = aggregation.compute_action_plan(
            verified, [], installed, detect_skills.route_cluster
        )
        self.assertEqual(plan["clusters"][0]["command"], "/apex")
        self.assertTrue(plan["clusters"][0]["fallback_used"])

    def test_bugs_drift_red_routes_to_apex(self):
        verified = [_verified("bugs-drift", "High", "src/a.ts:1")]
        plan = aggregation.compute_action_plan(
            verified, [], ALL_SKILLS, detect_skills.route_cluster
        )
        self.assertEqual(plan["clusters"][0]["command"], "/apex")


class TestActionPlanUnverified(unittest.TestCase):
    def test_unverified_block_populated_when_unverified_present(self):
        unverified = [_unverified("bugs-drift", "src/a.ts:1")]
        plan = aggregation.compute_action_plan(
            [], unverified, ALL_SKILLS, detect_skills.route_cluster
        )
        self.assertIsNotNone(plan["unverified_block"])
        self.assertEqual(plan["unverified_block"]["count"], 1)

    def test_unverified_block_prompt_starts_with_apex(self):
        unverified = [_unverified("bugs-drift", "src/a.ts:1")]
        plan = aggregation.compute_action_plan(
            [], unverified, ALL_SKILLS, detect_skills.route_cluster
        )
        prompt = plan["unverified_block"]["prompt_text"]
        self.assertTrue(prompt.startswith("/apex"))

    def test_unverified_block_has_no_fix_sketch_arrow(self):
        # Verified clusters include "→ <fix sketch>"; unverified does not.
        unverified = [_unverified("bugs-drift", "src/a.ts:1")]
        plan = aggregation.compute_action_plan(
            [], unverified, ALL_SKILLS, detect_skills.route_cluster
        )
        prompt = plan["unverified_block"]["prompt_text"]
        self.assertNotIn("→", prompt)

    def test_unverified_block_absent_when_no_unverified(self):
        verified = [_verified("rules", "High", "a:1")]
        plan = aggregation.compute_action_plan(
            verified, [], ALL_SKILLS, detect_skills.route_cluster
        )
        self.assertIsNone(plan["unverified_block"])


class TestActionPlanPromptFormat(unittest.TestCase):
    def test_prompt_starts_with_slash_command(self):
        verified = [_verified("bugs-drift", "High", "src/a.ts:1")]
        plan = aggregation.compute_action_plan(
            verified, [], ALL_SKILLS, detect_skills.route_cluster
        )
        for cluster in plan["clusters"]:
            self.assertTrue(
                cluster["prompt_text"].startswith("/"),
                f"Prompt should start with /command: {cluster['prompt_text'][:60]!r}",
            )

    def test_prompt_includes_lens_name(self):
        verified = [_verified("bugs-drift", "High", "src/a.ts:1")]
        plan = aggregation.compute_action_plan(
            verified, [], ALL_SKILLS, detect_skills.route_cluster
        )
        self.assertIn("bugs-drift", plan["clusters"][0]["prompt_text"])

    def test_prompt_includes_location(self):
        verified = [_verified("bugs-drift", "High", "src/a.ts:42")]
        plan = aggregation.compute_action_plan(
            verified, [], ALL_SKILLS, detect_skills.route_cluster
        )
        self.assertIn("src/a.ts:42", plan["clusters"][0]["prompt_text"])

    def test_green_prompt_uses_polish_verb(self):
        verified = [_verified("rules", "Low", "a:1")]
        plan = aggregation.compute_action_plan(
            verified, [], ALL_SKILLS, detect_skills.route_cluster
        )
        green = next(c for c in plan["clusters"] if c["severity"] == "🟢")
        self.assertIn("polish", green["prompt_text"])


class TestActionPlanInSynthesize(unittest.TestCase):
    def test_synthesize_returns_action_plan_key(self):
        out = aggregation.synthesize(
            [],
            installed_skills=ALL_SKILLS,
            route_fn=detect_skills.route_cluster,
        )
        self.assertIn("action_plan", out)
        self.assertIn("clusters", out["action_plan"])
        self.assertIn("unverified_block", out["action_plan"])
        self.assertIn("zero_findings", out["action_plan"])


if __name__ == "__main__":
    unittest.main()
