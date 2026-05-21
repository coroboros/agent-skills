"""Tests for the WS-1 severity-marker pipeline in aggregation.py.

Covers `_attach_marker`, marker propagation through `apply_a2`,
`iterate_unverified`, and `synthesize`, plus `compute_severity_counts`.
"""

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
    return base


def _stub_route(lens, marker, _installed_skills):
    return {
        "command": "/apex",
        "skill": "apex",
        "lens": lens,
        "marker": marker,
        "fallback_used": False,
    }


class TestMarkerMapping(unittest.TestCase):
    def test_high_severity_maps_to_red(self):
        f = aggregation._attach_marker(_finding(severity="High"))
        self.assertEqual(f["meta"]["marker"], "🔴")

    def test_medium_severity_maps_to_orange(self):
        f = aggregation._attach_marker(_finding(severity="Medium"))
        self.assertEqual(f["meta"]["marker"], "🟠")

    def test_low_severity_maps_to_green(self):
        f = aggregation._attach_marker(_finding(severity="Low"))
        self.assertEqual(f["meta"]["marker"], "🟢")

    def test_unknown_severity_falls_back_to_green(self):
        f = aggregation._attach_marker(_finding(severity="Catastrophic"))
        self.assertEqual(f["meta"]["marker"], "🟢")

    def test_attach_marker_is_idempotent(self):
        once = aggregation._attach_marker(_finding(severity="High"))
        twice = aggregation._attach_marker(once)
        self.assertEqual(once["meta"]["marker"], twice["meta"]["marker"])
        self.assertEqual(once["severity"], twice["severity"])


class TestMarkerPropagation(unittest.TestCase):
    def test_apply_a2_attaches_marker_to_verified(self):
        verified, _ = aggregation.apply_a2([_finding(severity="High", confidence=90)])
        self.assertEqual(verified[0]["meta"]["marker"], "🔴")

    def test_apply_a2_attaches_marker_to_unverified_as_green(self):
        # Sub-80 severity is downgraded to Low; marker reflects post-downgrade.
        _, unverified = aggregation.apply_a2(
            [_finding(severity="High", confidence=65)]
        )
        self.assertEqual(unverified[0]["meta"]["marker"], "🟢")

    def test_iteration_restores_marker_on_promotion(self):
        # A2-downgraded finding promoted → marker should track restored severity.
        _, unverified = aggregation.apply_a2(
            [_finding(severity="High", confidence=60)]
        )
        promoted, _, _ = aggregation.iterate_unverified(
            unverified, lambda _: "confirmed"
        )
        self.assertEqual(promoted[0]["severity"], "High")
        self.assertEqual(promoted[0]["meta"]["marker"], "🔴")


class TestSeverityCounts(unittest.TestCase):
    def test_severity_counts_keys_are_three_markers(self):
        counts = aggregation.compute_severity_counts([])
        self.assertEqual(set(counts.keys()), {"🔴", "🟠", "🟢"})

    def test_severity_counts_zero_findings_returns_zeros(self):
        counts = aggregation.compute_severity_counts([])
        self.assertEqual(counts, {"🔴": 0, "🟠": 0, "🟢": 0})

    def test_severity_counts_counts_each_marker(self):
        verified = [
            aggregation._attach_marker(_finding(severity="High")),
            aggregation._attach_marker(_finding(severity="High")),
            aggregation._attach_marker(_finding(severity="Medium")),
            aggregation._attach_marker(_finding(severity="Low")),
            aggregation._attach_marker(_finding(severity="Low")),
            aggregation._attach_marker(_finding(severity="Low")),
        ]
        counts = aggregation.compute_severity_counts(verified)
        self.assertEqual(counts, {"🔴": 2, "🟠": 1, "🟢": 3})

    def test_severity_counts_ignores_findings_without_marker(self):
        # A finding that never went through _attach_marker has no meta.marker.
        verified = [_finding(severity="High")]
        counts = aggregation.compute_severity_counts(verified)
        self.assertEqual(counts, {"🔴": 0, "🟠": 0, "🟢": 0})


class TestSynthesizeMarkers(unittest.TestCase):
    def _synth(self, findings, builder_fn=None):
        return aggregation.synthesize(
            findings,
            builder_fn=builder_fn,
            installed_skills={"apex": Path("/fake/apex/SKILL.md")},
            route_fn=_stub_route,
        )

    def test_every_verified_finding_has_marker(self):
        out = self._synth([
            _finding(severity="High", confidence=90, location="a:1"),
            _finding(severity="Medium", confidence=85, location="b:2"),
            _finding(severity="Low", confidence=85, location="c:3"),
        ])
        for f in out["verified"]:
            self.assertIn("marker", f.get("meta", {}))

    def test_every_unverified_finding_has_marker(self):
        out = self._synth([
            _finding(severity="High", confidence=60, location="a:1"),
            _finding(severity="Medium", confidence=50, location="b:2"),
        ])
        for f in out["unverified"]:
            self.assertIn("marker", f.get("meta", {}))

    def test_unverified_marker_is_always_green(self):
        # A2 downgrades to Low → marker 🟢.
        out = self._synth([
            _finding(severity="High", confidence=60, location="a:1"),
            _finding(severity="Medium", confidence=50, location="b:2"),
        ])
        for f in out["unverified"]:
            self.assertEqual(f["meta"]["marker"], "🟢")

    def test_severity_counts_in_synthesize_output(self):
        out = self._synth([
            _finding(severity="High", confidence=85, location="a:1"),
            _finding(severity="Medium", confidence=85, location="b:2"),
        ])
        self.assertIn("severity_counts", out)
        self.assertEqual(out["severity_counts"]["🔴"], 1)
        self.assertEqual(out["severity_counts"]["🟠"], 1)

    def test_severity_counts_excludes_unverified(self):
        # Verified=1 High, Unverified=1 sub-80.
        out = self._synth([
            _finding(severity="High", confidence=85, location="a:1"),
            _finding(severity="High", confidence=60, location="b:2"),
        ])
        self.assertEqual(out["severity_counts"]["🔴"], 1)
        # Unverified does not contribute to severity_counts.
        self.assertEqual(out["severity_counts"]["🟢"], 0)


if __name__ == "__main__":
    unittest.main()
