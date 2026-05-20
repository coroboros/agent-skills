"""Tests for skills/code-ultrareview/scripts/aggregation.py and spec_claim.py.

Pins the three postmortem-driven contracts:
  - A2: sub-80 findings are SURFACED with the unverified prefix, not dropped.
  - A1: spec-claim trigger formats a high-confidence finding with the quote.
  - Always-on iteration: build verdict promotes / drops / leaves sub-80 findings.

Also covers dedup, ordering, severity-tier mapping, and the no-iteration
path when no sub-80 findings exist.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = REPO_ROOT / "skills" / "code-ultrareview" / "scripts"
AGGREGATION = SCRIPTS_DIR / "aggregation.py"
SPEC_CLAIM = SCRIPTS_DIR / "spec_claim.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


aggregation = _load("aggregation", AGGREGATION)
spec_claim = _load("spec_claim", SPEC_CLAIM)


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


# ---------------------------------------------------------------------------
# A2 — no silent drop
# ---------------------------------------------------------------------------


class TestA2NoSilentDrop(unittest.TestCase):
    def test_sub_80_finding_is_surfaced_not_dropped(self):
        findings = [_finding(confidence=70)]
        verified, unverified = aggregation.apply_a2(findings)
        self.assertEqual(verified, [])
        self.assertEqual(len(unverified), 1)

    def test_sub_80_finding_carries_unverified_prefix(self):
        findings = [_finding(confidence=70, finding="Off-by-one in loop bound")]
        _, unverified = aggregation.apply_a2(findings)
        self.assertTrue(
            unverified[0]["finding"].startswith(aggregation.UNVERIFIED_PREFIX)
        )

    def test_sub_80_finding_severity_downgraded_to_low(self):
        findings = [_finding(confidence=65, severity="High")]
        _, unverified = aggregation.apply_a2(findings)
        self.assertEqual(unverified[0]["severity"], "Low")

    def test_sub_80_finding_recommendation_explains_routing(self):
        findings = [_finding(confidence=55)]
        _, unverified = aggregation.apply_a2(findings)
        self.assertIn("Sub-80", unverified[0]["recommendation"])
        self.assertIn("55", unverified[0]["recommendation"])
        self.assertIn("-t deep", unverified[0]["recommendation"])

    def test_high_confidence_finding_unchanged_by_a2(self):
        original = _finding(confidence=95, severity="High",
                            finding="Resource leak", recommendation="Use with-statement")
        verified, unverified = aggregation.apply_a2([original])
        self.assertEqual(len(verified), 1)
        self.assertEqual(verified[0]["severity"], "High")
        self.assertEqual(verified[0]["finding"], "Resource leak")
        self.assertEqual(verified[0]["recommendation"], "Use with-statement")
        self.assertEqual(unverified, [])

    def test_zero_confidence_finding_is_dropped(self):
        findings = [_finding(confidence=0)]
        verified, unverified = aggregation.apply_a2(findings)
        self.assertEqual(verified, [])
        self.assertEqual(unverified, [])

    def test_boundary_at_80_routes_to_verified(self):
        findings = [_finding(confidence=80)]
        verified, unverified = aggregation.apply_a2(findings)
        self.assertEqual(len(verified), 1)
        self.assertEqual(unverified, [])

    def test_boundary_at_79_routes_to_unverified(self):
        findings = [_finding(confidence=79)]
        verified, unverified = aggregation.apply_a2(findings)
        self.assertEqual(verified, [])
        self.assertEqual(len(unverified), 1)


# ---------------------------------------------------------------------------
# A1 — spec-claim triggering
# ---------------------------------------------------------------------------


class TestA1SpecClaimTrigger(unittest.TestCase):
    def test_a1_finding_confidence_at_least_80(self):
        finding = spec_claim.trigger_a1_finding(
            spec_name="RFC 6874",
            spec_excerpt="ZoneID = 1*( unreserved / pct-encoded )",
            diff_excerpt="parseZoneId(s: string) { return s; }",
            location="src/uri/zone-id.ts:14",
        )
        self.assertGreaterEqual(finding["confidence"], 80)

    def test_a1_finding_quotes_governing_clause(self):
        finding = spec_claim.trigger_a1_finding(
            spec_name="RFC 6874",
            spec_excerpt="ZoneID = 1*( unreserved / pct-encoded )",
            diff_excerpt="…",
            location="src/uri/zone-id.ts:14",
        )
        self.assertIn("ZoneID", finding["recommendation"])
        self.assertIn("RFC 6874", finding["recommendation"])

    def test_a1_finding_lens_is_bugs_drift(self):
        finding = spec_claim.trigger_a1_finding(
            spec_name="WHATWG URL",
            spec_excerpt="A URL is parsed by …",
            diff_excerpt="…",
            location="src/url.ts:1",
        )
        self.assertEqual(finding["lens"], "bugs-drift")

    def test_a1_high_severity(self):
        finding = spec_claim.trigger_a1_finding(
            spec_name="RFC 7231",
            spec_excerpt="The Accept header field …",
            diff_excerpt="…",
            location="src/headers.ts:42",
        )
        self.assertEqual(finding["severity"], "High")

    def test_a1_requires_name_excerpt_location(self):
        with self.assertRaises(ValueError):
            spec_claim.trigger_a1_finding(
                spec_name="", spec_excerpt="x", diff_excerpt="", location="src:1"
            )

    def test_detect_specs_finds_rfc_and_whatwg(self):
        text = "We implement RFC 6874 and align with WHATWG URL."
        specs = spec_claim.detect_specs(text)
        self.assertIn("RFC 6874", specs)
        self.assertIn("WHATWG", specs)

    def test_detect_specs_empty_when_none_mentioned(self):
        self.assertEqual(spec_claim.detect_specs("nothing to see here"), [])

    def test_slugify_spec(self):
        self.assertEqual(spec_claim.slugify_spec("RFC 6874"), "rfc-6874")
        self.assertEqual(spec_claim.slugify_spec("WHATWG URL"), "whatwg-url")
        self.assertEqual(spec_claim.slugify_spec("ISO/IEC 7816"), "iso-iec-7816")

    def test_cache_path_format(self):
        p = spec_claim.cache_path("rfc-6874", "2026-05-20")
        self.assertTrue(p.name.endswith(".txt"))
        self.assertIn("rfc-6874", p.name)
        self.assertIn("2026-05-20", p.name)

    def test_unverified_a1_finding_surfaces_low_confidence(self):
        finding = spec_claim.trigger_unverified_a1_finding(
            spec_name="RFC 6874",
            location="src/uri.ts:14",
        )
        self.assertEqual(finding["confidence"], 50)
        self.assertIn("[unverified — needs network]", finding["finding"])


# ---------------------------------------------------------------------------
# Deep-tier iteration
# ---------------------------------------------------------------------------


class TestAlwaysIteration(unittest.TestCase):
    def test_deep_iteration_promotes_confidence_when_build_confirms(self):
        unverified = [_finding(confidence=70)]

        def builder(_):
            return "confirmed"

        promoted, remaining, dropped = aggregation.deep_iterate(unverified, builder)
        self.assertEqual(len(promoted), 1)
        self.assertEqual(remaining, [])
        self.assertEqual(dropped, [])
        self.assertGreaterEqual(promoted[0]["confidence"], 80)

    def test_deep_iteration_drops_when_build_disproves(self):
        unverified = [_finding(confidence=70)]

        def builder(_):
            return "disproved"

        promoted, remaining, dropped = aggregation.deep_iterate(unverified, builder)
        self.assertEqual(promoted, [])
        self.assertEqual(remaining, [])
        self.assertEqual(len(dropped), 1)

    def test_deep_iteration_keeps_inconclusive_in_remaining(self):
        unverified = [_finding(confidence=70)]

        def builder(_):
            return "inconclusive"

        promoted, remaining, dropped = aggregation.deep_iterate(unverified, builder)
        self.assertEqual(promoted, [])
        self.assertEqual(len(remaining), 1)
        self.assertEqual(dropped, [])

    def test_promoted_finding_strips_unverified_prefix(self):
        with_prefix = _finding(
            confidence=70,
            finding=f"{aggregation.UNVERIFIED_PREFIX} Off-by-one",
        )

        def builder(_):
            return "confirmed"

        promoted, _, _ = aggregation.deep_iterate([with_prefix], builder)
        self.assertFalse(promoted[0]["finding"].startswith(aggregation.UNVERIFIED_PREFIX))

    def test_promoted_finding_restores_original_severity(self):
        f = _finding(
            confidence=70, severity="Low",
            meta={"original_severity": "High"},
        )

        def builder(_):
            return "confirmed"

        promoted, _, _ = aggregation.deep_iterate([f], builder)
        self.assertEqual(promoted[0]["severity"], "High")

    def test_apply_a2_then_deep_iterate_restores_original_severity(self):
        # End-to-end regression: a High-severity sub-80 finding flows through
        # apply_a2 (which downgrades to Low) and then deep_iterate (which
        # promotes on confirm). The original High must survive.
        raw = _finding(confidence=70, severity="High", finding="Off-by-one in parser")
        _, unverified = aggregation.apply_a2([raw])
        self.assertEqual(unverified[0]["severity"], "Low")
        self.assertEqual(unverified[0]["meta"]["original_severity"], "High")

        def builder(_):
            return "confirmed"

        promoted, _, _ = aggregation.deep_iterate(unverified, builder)
        self.assertEqual(promoted[0]["severity"], "High")
        self.assertGreaterEqual(promoted[0]["confidence"], aggregation.CONFIDENCE_THRESHOLD)

    def test_iteration_cap_is_one_call_per_finding(self):
        unverified = [_finding(confidence=70), _finding(confidence=60, location="b:1")]
        calls = []

        def builder(f):
            calls.append(f["location"])
            return "inconclusive"

        aggregation.deep_iterate(unverified, builder)
        self.assertEqual(calls, ["src/a.ts:10", "b:1"])


# ---------------------------------------------------------------------------
# Dedup, ordering, severity-tier
# ---------------------------------------------------------------------------


class TestDedup(unittest.TestCase):
    def test_cross_lens_duplicate_collapses_keeping_higher_confidence(self):
        a = _finding(lens="rules", confidence=85, location="src/x.ts:5",
                     finding="Same problem here")
        b = _finding(lens="bugs-drift", confidence=70, location="src/x.ts:5",
                     finding="Same problem here")
        out = aggregation.dedupe([a, b])
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["lens"], "rules")
        self.assertEqual(out[0]["confidence"], 85)
        self.assertIn("bugs-drift", out[0]["meta"]["secondary_lens"])

    def test_distinct_findings_not_collapsed(self):
        a = _finding(location="src/x.ts:5", finding="Off by one")
        b = _finding(location="src/x.ts:8", finding="Off by one")
        out = aggregation.dedupe([a, b])
        self.assertEqual(len(out), 2)


class TestOrdering(unittest.TestCase):
    def test_severity_then_confidence_then_location(self):
        items = [
            _finding(severity="Low", confidence=80, location="z:1"),
            _finding(severity="High", confidence=85, location="b:1"),
            _finding(severity="High", confidence=95, location="a:1"),
            _finding(severity="Medium", confidence=80, location="c:1"),
        ]
        out = aggregation.order(items)
        self.assertEqual([f["location"] for f in out], ["a:1", "b:1", "c:1", "z:1"])


class TestSeverityTier(unittest.TestCase):
    def test_high_confidence_high_severity_is_important(self):
        f = aggregation.assign_anthropic_tier(_finding(severity="High", confidence=85))
        self.assertEqual(f["meta"]["anthropic_tier"], "Important")

    def test_high_confidence_low_severity_is_nit(self):
        f = aggregation.assign_anthropic_tier(_finding(severity="Low", confidence=85))
        self.assertEqual(f["meta"]["anthropic_tier"], "Nit")

    def test_pre_existing_flag_overrides_tier(self):
        f = aggregation.assign_anthropic_tier(
            _finding(severity="High", confidence=85, pre_existing=True)
        )
        self.assertEqual(f["meta"]["anthropic_tier"], "Pre-existing")


# ---------------------------------------------------------------------------
# End-to-end synthesizer
# ---------------------------------------------------------------------------


class TestAggregation(unittest.TestCase):
    def test_standard_tier_does_not_iterate(self):
        findings = [_finding(confidence=70)]
        calls = []

        def builder(_):
            calls.append(1)
            return "confirmed"

        out = aggregation.synthesize(findings, tier="standard", builder_fn=builder)
        self.assertEqual(out["verified"], [])
        self.assertEqual(len(out["unverified"]), 1)
        self.assertEqual(calls, [])

    def test_deep_tier_promotes_via_builder(self):
        findings = [_finding(confidence=70)]
        out = aggregation.synthesize(
            findings, tier="deep", builder_fn=lambda _: "confirmed"
        )
        self.assertEqual(len(out["verified"]), 1)
        self.assertEqual(out["unverified"], [])

    def test_synthesize_orders_verified_findings(self):
        findings = [
            _finding(severity="Low", confidence=90, location="z:1"),
            _finding(severity="High", confidence=90, location="a:1"),
        ]
        out = aggregation.synthesize(findings, tier="standard")
        self.assertEqual(out["verified"][0]["location"], "a:1")


if __name__ == "__main__":
    unittest.main()
