"""Tests for skills/code-ultrareview/scripts/synthesis_core.py.

Pins the A2 no-silent-drop contract, build-verification iteration,
verdict algorithm, severity-tier classification, and canonical ordering.
Findings carry the `axis` field — the module is axis-aware.

Pinned contracts:
  - A2: sub-80 findings surface with the unverified prefix, severity
    downgraded to Low, recommendation prepended with rationale.
  - Iteration: confirmed → promotes; disproved → drops; inconclusive → keeps.
  - Verdict: 🔴 Important → Needs work; 🟠 Important → Fix-then-ship; else Ship.
  - Axis priority + canonical-axis order: stable constants for inter-axis
    precedence in Phase 5 synthesis (`scripts/synthesize.py`).
"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = (
    REPO_ROOT / "skills" / "code-ultrareview" / "scripts" / "synthesis_core.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("synthesis_core", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sc = _load()


def _finding(**overrides) -> dict:
    base = {
        "axis": "correctness",
        "severity": "Medium",
        "location": "src/a.ts:10",
        "finding": "Potential null deref",
        "recommendation": "Add a guard",
        "confidence": 85,
    }
    base.update(overrides)
    return base


def _verified(axis: str, severity: str, tier: str) -> dict:
    f = {
        "axis": axis,
        "severity": severity,
        "location": f"src/{axis}.ts:10",
        "finding": f"{severity} finding in {axis}",
        "recommendation": "Fix",
        "confidence": 90,
    }
    f = sc._attach_marker(f)
    f["meta"]["anthropic_tier"] = tier
    return f


# ---------------------------------------------------------------------------
# A2 — no silent drop
# ---------------------------------------------------------------------------


class TestA2NoSilentDrop(unittest.TestCase):
    def test_sub_80_surfaced_not_dropped(self):
        verified, unverified = sc.apply_a2([_finding(confidence=70)])
        self.assertEqual(verified, [])
        self.assertEqual(len(unverified), 1)

    def test_sub_80_carries_unverified_prefix(self):
        _, unverified = sc.apply_a2([_finding(confidence=70, finding="Off-by-one")])
        self.assertTrue(unverified[0]["finding"].startswith(sc.UNVERIFIED_PREFIX))

    def test_sub_80_severity_downgraded_to_low(self):
        _, unverified = sc.apply_a2([_finding(confidence=65, severity="High")])
        self.assertEqual(unverified[0]["severity"], "Low")
        self.assertEqual(unverified[0]["meta"]["original_severity"], "High")

    def test_sub_80_rationale_prepended(self):
        _, unverified = sc.apply_a2([_finding(confidence=55)])
        rec = unverified[0]["recommendation"]
        self.assertIn("Sub-80", rec)
        self.assertIn("55", rec)
        self.assertIn("verify locally", rec)

    def test_high_confidence_unchanged(self):
        original = _finding(confidence=95, severity="High",
                            finding="Resource leak", recommendation="Use with")
        verified, unverified = sc.apply_a2([original])
        self.assertEqual(len(verified), 1)
        self.assertEqual(verified[0]["severity"], "High")
        self.assertEqual(verified[0]["finding"], "Resource leak")
        self.assertEqual(unverified, [])

    def test_zero_confidence_dropped(self):
        verified, unverified = sc.apply_a2([_finding(confidence=0)])
        self.assertEqual(verified, [])
        self.assertEqual(unverified, [])

    def test_boundary_at_80_verified(self):
        verified, unverified = sc.apply_a2([_finding(confidence=80)])
        self.assertEqual(len(verified), 1)
        self.assertEqual(unverified, [])

    def test_boundary_at_79_unverified(self):
        verified, unverified = sc.apply_a2([_finding(confidence=79)])
        self.assertEqual(verified, [])
        self.assertEqual(len(unverified), 1)

    def test_marker_attached_to_verified(self):
        verified, _ = sc.apply_a2([_finding(confidence=90, severity="High")])
        self.assertEqual(verified[0]["meta"]["marker"], "🔴")


# ---------------------------------------------------------------------------
# Build verification iteration
# ---------------------------------------------------------------------------


class TestIteration(unittest.TestCase):
    def test_confirmed_promotes_to_threshold_or_above(self):
        promoted, remaining, dropped = sc.iterate_unverified(
            [_finding(confidence=70)], lambda _: "confirmed",
        )
        self.assertEqual(len(promoted), 1)
        self.assertEqual(remaining, [])
        self.assertEqual(dropped, [])
        self.assertGreaterEqual(promoted[0]["confidence"], sc.CONFIDENCE_THRESHOLD)

    def test_disproved_drops(self):
        promoted, remaining, dropped = sc.iterate_unverified(
            [_finding(confidence=70)], lambda _: "disproved",
        )
        self.assertEqual(promoted, [])
        self.assertEqual(remaining, [])
        self.assertEqual(len(dropped), 1)

    def test_inconclusive_keeps_in_remaining(self):
        promoted, remaining, dropped = sc.iterate_unverified(
            [_finding(confidence=70)], lambda _: "inconclusive",
        )
        self.assertEqual(promoted, [])
        self.assertEqual(len(remaining), 1)
        self.assertEqual(dropped, [])

    def test_promotion_strips_unverified_prefix(self):
        f = _finding(confidence=70, finding=f"{sc.UNVERIFIED_PREFIX} Off-by-one")
        promoted, _, _ = sc.iterate_unverified([f], lambda _: "confirmed")
        self.assertFalse(promoted[0]["finding"].startswith(sc.UNVERIFIED_PREFIX))

    def test_promotion_restores_original_severity(self):
        f = _finding(confidence=70, severity="Low",
                     meta={"original_severity": "High"})
        promoted, _, _ = sc.iterate_unverified([f], lambda _: "confirmed")
        self.assertEqual(promoted[0]["severity"], "High")

    def test_a2_then_iterate_restores_high(self):
        raw = _finding(confidence=70, severity="High", finding="Off-by-one")
        _, unverified = sc.apply_a2([raw])
        self.assertEqual(unverified[0]["severity"], "Low")
        self.assertEqual(unverified[0]["meta"]["original_severity"], "High")
        promoted, _, _ = sc.iterate_unverified(unverified, lambda _: "confirmed")
        self.assertEqual(promoted[0]["severity"], "High")
        self.assertGreaterEqual(promoted[0]["confidence"], sc.CONFIDENCE_THRESHOLD)

    def test_iteration_one_call_per_finding(self):
        calls: list[str] = []
        sc.iterate_unverified(
            [_finding(confidence=70), _finding(confidence=60, location="b:1")],
            lambda f: calls.append(f["location"]) or "inconclusive",
        )
        self.assertEqual(calls, ["src/a.ts:10", "b:1"])

    def test_promotion_caps_at_promotion_cap(self):
        # 70 + 30 = 100 → capped at PROMOTION_CAP (95).
        _, unverified = sc.apply_a2([_finding(confidence=70, severity="High")])
        promoted, _, _ = sc.iterate_unverified(unverified, lambda _: "confirmed")
        self.assertEqual(promoted[0]["confidence"], sc.PROMOTION_CAP)

    def test_promotion_floor_at_confidence_threshold(self):
        # 10 + 30 = 40 → floor lifts to CONFIDENCE_THRESHOLD (80).
        _, unverified = sc.apply_a2([_finding(confidence=10, severity="High")])
        promoted, _, _ = sc.iterate_unverified(unverified, lambda _: "confirmed")
        self.assertEqual(promoted[0]["confidence"], sc.CONFIDENCE_THRESHOLD)


# ---------------------------------------------------------------------------
# Anthropic tier classification
# ---------------------------------------------------------------------------


class TestTier(unittest.TestCase):
    def test_high_confidence_high_severity_is_important(self):
        f = sc.assign_anthropic_tier(_finding(severity="High", confidence=85))
        self.assertEqual(f["meta"]["anthropic_tier"], "Important")

    def test_high_confidence_low_severity_is_nit(self):
        f = sc.assign_anthropic_tier(_finding(severity="Low", confidence=85))
        self.assertEqual(f["meta"]["anthropic_tier"], "Nit")

    def test_pre_existing_overrides_tier(self):
        f = sc.assign_anthropic_tier(
            _finding(severity="High", confidence=85, pre_existing=True)
        )
        self.assertEqual(f["meta"]["anthropic_tier"], "Pre-existing")


# ---------------------------------------------------------------------------
# Ordering
# ---------------------------------------------------------------------------


class TestOrdering(unittest.TestCase):
    def test_severity_then_confidence_then_location(self):
        items = [
            _finding(severity="Low", confidence=80, location="z:1"),
            _finding(severity="High", confidence=85, location="b:1"),
            _finding(severity="High", confidence=95, location="a:1"),
            _finding(severity="Medium", confidence=80, location="c:1"),
        ]
        out = sc.order(items)
        self.assertEqual([f["location"] for f in out], ["a:1", "b:1", "c:1", "z:1"])


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------


class TestVerdict(unittest.TestCase):
    def test_no_findings_is_ship(self):
        verdict = sc.compute_verdict([])
        self.assertEqual(verdict["label"], "Ship")
        self.assertIn("Eight axes", verdict["rationale"])

    def test_only_nits_is_ship(self):
        verdict = sc.compute_verdict([_verified("correctness", "Low", "Nit")])
        self.assertEqual(verdict["label"], "Ship")
        self.assertIn("Only Nits", verdict["rationale"])

    def test_orange_important_is_fix_then_ship(self):
        verdict = sc.compute_verdict([_verified("documentation", "Medium", "Important")])
        self.assertEqual(verdict["label"], "Fix-then-ship")
        self.assertIn("🟠 Important", verdict["rationale"])

    def test_red_important_is_needs_work(self):
        verdict = sc.compute_verdict([_verified("correctness", "High", "Important")])
        self.assertEqual(verdict["label"], "Needs work")
        self.assertIn("🔴 Important", verdict["rationale"])

    def test_red_wins_when_red_and_orange_present(self):
        verdict = sc.compute_verdict([
            _verified("correctness", "High", "Important"),
            _verified("documentation", "Medium", "Important"),
        ])
        self.assertEqual(verdict["label"], "Needs work")

    def test_rationale_cites_axis_for_needs_work(self):
        verdict = sc.compute_verdict([_verified("correctness", "High", "Important")])
        self.assertIn("correctness", verdict["rationale"])

    def test_rationale_counts_findings(self):
        verdict = sc.compute_verdict([
            _verified("correctness", "High", "Important"),
            _verified("correctness", "High", "Important"),
        ])
        self.assertIn("2", verdict["rationale"])

    def test_drivers_empty_for_ship(self):
        self.assertEqual(sc.compute_verdict([]).get("drivers"), [])

    def test_pre_existing_tier_doesnt_count_as_important(self):
        f = _verified("correctness", "High", "Pre-existing")
        verdict = sc.compute_verdict([f])
        self.assertEqual(verdict["label"], "Ship")


# ---------------------------------------------------------------------------
# Severity counts
# ---------------------------------------------------------------------------


class TestSeverityCounts(unittest.TestCase):
    def test_counts_by_marker(self):
        verified = [
            _verified("correctness", "High", "Important"),
            _verified("documentation", "Medium", "Important"),
            _verified("style", "Low", "Nit"),
            _verified("style", "Low", "Nit"),
        ]
        counts = sc.compute_severity_counts(verified)
        self.assertEqual(counts["🔴"], 1)
        self.assertEqual(counts["🟠"], 1)
        self.assertEqual(counts["🟢"], 2)

    def test_counts_zero_when_empty(self):
        counts = sc.compute_severity_counts([])
        self.assertEqual(counts["🔴"], 0)
        self.assertEqual(counts["🟠"], 0)
        self.assertEqual(counts["🟢"], 0)


# ---------------------------------------------------------------------------
# Axis taxonomy constants
# ---------------------------------------------------------------------------


class TestAxisTaxonomy(unittest.TestCase):
    def test_canonical_axes_count(self):
        self.assertEqual(len(sc.CANONICAL_AXES), 8)

    def test_canonical_axes_kebab_lowercase(self):
        for axis in sc.CANONICAL_AXES:
            self.assertRegex(axis, r"^[a-z]+(-[a-z]+)*$",
                             f"axis {axis!r} not kebab-lowercase")

    def test_axis_priority_includes_all_canonical(self):
        for axis in sc.CANONICAL_AXES:
            self.assertIn(axis, sc.AXIS_PRIORITY,
                          f"axis {axis!r} missing from AXIS_PRIORITY")

    def test_axis_priority_includes_coherence(self):
        self.assertIn("coherence", sc.AXIS_PRIORITY)

    def test_axis_priority_correctness_first(self):
        # Correctness must dominate inter-axis precedence — a real bug
        # beats every other concern at the same line.
        self.assertEqual(sc.AXIS_PRIORITY[0], "correctness")

    def test_axis_priority_coherence_last(self):
        self.assertEqual(sc.AXIS_PRIORITY[-1], "coherence")

    def test_conditional_axes(self):
        self.assertEqual(sc.CONDITIONAL_AXES, ("coherence",))


if __name__ == "__main__":
    unittest.main()
