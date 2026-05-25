"""Tests for the lens-summary computation in aggregation.py."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = REPO_ROOT / "skills" / "code-ultrareview" / "scripts"
AGGREGATION = SCRIPTS_DIR / "aggregation.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


aggregation = _load("aggregation", AGGREGATION)


def _finding(**overrides) -> dict:
    base = {
        "lens": "bugs-drift",
        "severity": "Medium",
        "location": "src/a.ts:10",
        "finding": "Potential null deref",
        "recommendation": "Add a guard",
        "confidence": 85,
    }
    base.update(overrides)
    f = dict(base)
    return aggregation._attach_marker(f)


class TestLensSummaryShape(unittest.TestCase):
    def test_returns_seven_rows(self):
        summary = aggregation.compute_lens_summary(
            [], [], aggregation.ALWAYS_ON_LENSES
        )
        self.assertEqual(len(summary), 7)

    def test_canonical_lens_order(self):
        summary = aggregation.compute_lens_summary(
            [], [], aggregation.ALWAYS_ON_LENSES
        )
        names = [row["lens"] for row in summary]
        self.assertEqual(tuple(names), aggregation.CANONICAL_LENSES)

    def test_each_row_has_required_keys(self):
        summary = aggregation.compute_lens_summary(
            [], [], aggregation.ALWAYS_ON_LENSES
        )
        for row in summary:
            self.assertEqual(
                set(row.keys()),
                {"lens", "status", "verified_count", "unverified_count", "top_finding"},
            )


class TestLensSummaryStatus(unittest.TestCase):
    def test_clean_lens_is_green(self):
        summary = aggregation.compute_lens_summary(
            [], [], aggregation.ALWAYS_ON_LENSES
        )
        for row in summary:
            if row["status"] != "skipped":
                self.assertEqual(row["status"], "🟢")

    def test_high_finding_in_lens_yields_red(self):
        verified = [_finding(lens="bugs-drift", severity="High")]
        summary = aggregation.compute_lens_summary(
            verified, [], aggregation.ALWAYS_ON_LENSES
        )
        bugs = next(row for row in summary if row["lens"] == "bugs-drift")
        self.assertEqual(bugs["status"], "🔴")

    def test_medium_only_yields_orange(self):
        verified = [_finding(lens="docs-version", severity="Medium")]
        summary = aggregation.compute_lens_summary(
            verified, [], aggregation.ALWAYS_ON_LENSES
        )
        docs = next(row for row in summary if row["lens"] == "docs-version")
        self.assertEqual(docs["status"], "🟠")

    def test_low_only_yields_green(self):
        verified = [_finding(lens="tests-blindspots", severity="Low")]
        summary = aggregation.compute_lens_summary(
            verified, [], aggregation.ALWAYS_ON_LENSES
        )
        tests = next(row for row in summary if row["lens"] == "tests-blindspots")
        self.assertEqual(tests["status"], "🟢")

    def test_red_wins_over_orange_and_green(self):
        verified = [
            _finding(lens="rules", severity="High"),
            _finding(lens="rules", severity="Medium"),
            _finding(lens="rules", severity="Low"),
        ]
        summary = aggregation.compute_lens_summary(
            verified, [], aggregation.ALWAYS_ON_LENSES
        )
        rules = next(row for row in summary if row["lens"] == "rules")
        self.assertEqual(rules["status"], "🔴")


class TestLensSummarySkipped(unittest.TestCase):
    def test_derivation_skipped_when_not_in_ran_lenses(self):
        summary = aggregation.compute_lens_summary(
            [], [], aggregation.ALWAYS_ON_LENSES
        )
        derivation = next(row for row in summary if row["lens"] == "derivation")
        self.assertEqual(derivation["status"], "skipped")

    def test_derivation_runs_when_in_ran_lenses(self):
        summary = aggregation.compute_lens_summary(
            [], [], list(aggregation.ALWAYS_ON_LENSES) + ["derivation"]
        )
        derivation = next(row for row in summary if row["lens"] == "derivation")
        self.assertEqual(derivation["status"], "🟢")

    def test_skipped_lens_has_zero_counts(self):
        summary = aggregation.compute_lens_summary(
            [], [], aggregation.ALWAYS_ON_LENSES
        )
        derivation = next(row for row in summary if row["lens"] == "derivation")
        self.assertEqual(derivation["verified_count"], 0)
        self.assertEqual(derivation["unverified_count"], 0)
        self.assertIsNone(derivation["top_finding"])


class TestLensSummaryCounts(unittest.TestCase):
    def test_verified_count_matches(self):
        verified = [
            _finding(lens="rules", severity="High", location="a:1"),
            _finding(lens="rules", severity="Medium", location="b:2"),
            _finding(lens="bugs-drift", severity="Low", location="c:3"),
        ]
        summary = aggregation.compute_lens_summary(
            verified, [], aggregation.ALWAYS_ON_LENSES
        )
        rules = next(row for row in summary if row["lens"] == "rules")
        bugs = next(row for row in summary if row["lens"] == "bugs-drift")
        self.assertEqual(rules["verified_count"], 2)
        self.assertEqual(bugs["verified_count"], 1)

    def test_unverified_count_matches(self):
        unverified = [
            _finding(lens="rules", severity="Low", location="a:1"),
            _finding(lens="rules", severity="Low", location="b:2"),
        ]
        summary = aggregation.compute_lens_summary(
            [], unverified, aggregation.ALWAYS_ON_LENSES
        )
        rules = next(row for row in summary if row["lens"] == "rules")
        self.assertEqual(rules["unverified_count"], 2)


class TestLensSummaryTopFinding(unittest.TestCase):
    def test_top_finding_text_present_when_findings_exist(self):
        verified = [
            _finding(lens="rules", severity="High", finding="Critical issue")
        ]
        summary = aggregation.compute_lens_summary(
            verified, [], aggregation.ALWAYS_ON_LENSES
        )
        rules = next(row for row in summary if row["lens"] == "rules")
        self.assertEqual(rules["top_finding"], "Critical issue")

    def test_top_finding_truncated_above_80_chars(self):
        long_text = "x" * 200
        verified = [_finding(lens="rules", finding=long_text)]
        summary = aggregation.compute_lens_summary(
            verified, [], aggregation.ALWAYS_ON_LENSES
        )
        rules = next(row for row in summary if row["lens"] == "rules")
        self.assertLessEqual(len(rules["top_finding"]), 80)
        self.assertTrue(rules["top_finding"].endswith("…"))

    def test_top_finding_picks_highest_severity(self):
        verified = [
            _finding(lens="rules", severity="Low", finding="low one", location="a:1"),
            _finding(lens="rules", severity="High", finding="high one", location="b:2"),
            _finding(lens="rules", severity="Medium", finding="medium one", location="c:3"),
        ]
        summary = aggregation.compute_lens_summary(
            verified, [], aggregation.ALWAYS_ON_LENSES
        )
        rules = next(row for row in summary if row["lens"] == "rules")
        self.assertEqual(rules["top_finding"], "high one")


if __name__ == "__main__":
    unittest.main()
