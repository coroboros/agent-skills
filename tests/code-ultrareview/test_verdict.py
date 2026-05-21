"""Tests for the WS-4 verdict computation in aggregation.py."""

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


def _verified_finding(lens: str, severity: str, tier: str) -> dict:
    f = {
        "lens": lens,
        "severity": severity,
        "location": f"src/{lens}.ts:10",
        "finding": f"{severity} finding in {lens}",
        "recommendation": "Fix",
        "confidence": 90,
    }
    f = aggregation._attach_marker(f)
    f["meta"]["anthropic_tier"] = tier
    return f


def _stub_route(lens, marker, _installed):
    return {
        "command": "/apex",
        "skill": "apex",
        "lens": lens,
        "marker": marker,
        "fallback_used": False,
    }


class TestVerdictLabels(unittest.TestCase):
    def test_clean_findings_is_ship(self):
        verdict = aggregation.compute_verdict([])
        self.assertEqual(verdict["label"], "Ship")
        self.assertEqual(verdict["rationale"], "Six lenses ran clean. Ship.")

    def test_only_nits_is_ship(self):
        verified = [_verified_finding("rules", "Low", "Nit")]
        verdict = aggregation.compute_verdict(verified)
        self.assertEqual(verdict["label"], "Ship")
        self.assertIn("Only Nits", verdict["rationale"])

    def test_orange_important_is_fix_then_ship(self):
        verified = [_verified_finding("docs-version", "Medium", "Important")]
        verdict = aggregation.compute_verdict(verified)
        self.assertEqual(verdict["label"], "Fix-then-ship")
        self.assertIn("🟠 Important", verdict["rationale"])

    def test_red_important_is_needs_work(self):
        verified = [_verified_finding("bugs-drift", "High", "Important")]
        verdict = aggregation.compute_verdict(verified)
        self.assertEqual(verdict["label"], "Needs work")
        self.assertIn("🔴 Important", verdict["rationale"])

    def test_red_wins_when_red_and_orange_present(self):
        verified = [
            _verified_finding("bugs-drift", "High", "Important"),
            _verified_finding("docs-version", "Medium", "Important"),
        ]
        verdict = aggregation.compute_verdict(verified)
        self.assertEqual(verdict["label"], "Needs work")


class TestVerdictRationale(unittest.TestCase):
    def test_rationale_cites_lens_for_needs_work(self):
        verified = [_verified_finding("bugs-drift", "High", "Important")]
        verdict = aggregation.compute_verdict(verified)
        self.assertIn("bugs-drift", verdict["rationale"])

    def test_rationale_counts_findings(self):
        verified = [
            _verified_finding("bugs-drift", "High", "Important"),
            _verified_finding("bugs-drift", "High", "Important"),
        ]
        verdict = aggregation.compute_verdict(verified)
        self.assertIn("2", verdict["rationale"])

    def test_drivers_list_lenses_for_needs_work(self):
        verified = [
            _verified_finding("bugs-drift", "High", "Important"),
            _verified_finding("rules", "High", "Important"),
        ]
        verdict = aggregation.compute_verdict(verified)
        drivers_joined = " ".join(verdict["drivers"])
        self.assertIn("bugs-drift", drivers_joined)
        self.assertIn("rules", drivers_joined)

    def test_drivers_empty_for_ship(self):
        verdict = aggregation.compute_verdict([])
        self.assertEqual(verdict["drivers"], [])


class TestVerdictExclusions(unittest.TestCase):
    def test_unverified_excluded_from_verdict(self):
        # compute_verdict only sees verified set — unverified findings are
        # not passed in. This test pins the synthesize-level behavior.
        out = aggregation.synthesize(
            [
                {
                    "lens": "bugs-drift",
                    "severity": "High",
                    "location": "src/a.ts:1",
                    "finding": "Sub-80 red",
                    "recommendation": "Maybe",
                    "confidence": 65,  # routed to unverified
                },
            ],
            installed_skills={"apex": Path("/x")},
            route_fn=_stub_route,
        )
        self.assertEqual(out["verdict"]["label"], "Ship")

    def test_low_with_high_original_severity_doesnt_flip_verdict(self):
        # A2-downgraded finding has marker 🟢 and severity Low; tier None.
        # Even if original_severity was "High", verdict treats it as a nit.
        f = {
            "lens": "bugs-drift",
            "severity": "Low",
            "location": "src/a.ts:1",
            "finding": "Was high, downgraded",
            "recommendation": "Fix",
            "confidence": 50,
            "meta": {"original_severity": "High", "marker": "🟢"},
        }
        verdict = aggregation.compute_verdict([f])
        self.assertEqual(verdict["label"], "Ship")

    def test_pre_existing_tier_doesnt_count_as_important(self):
        # Pre-existing findings have tier "Pre-existing", not "Important".
        f = _verified_finding("bugs-drift", "High", "Pre-existing")
        verdict = aggregation.compute_verdict([f])
        self.assertEqual(verdict["label"], "Ship")


class TestVerdictInSynthesize(unittest.TestCase):
    def test_synthesize_returns_verdict_key(self):
        out = aggregation.synthesize(
            [],
            installed_skills={"apex": Path("/x")},
            route_fn=_stub_route,
        )
        self.assertIn("verdict", out)
        self.assertIn("label", out["verdict"])
        self.assertIn("rationale", out["verdict"])
        self.assertIn("drivers", out["verdict"])


if __name__ == "__main__":
    unittest.main()
