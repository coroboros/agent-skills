"""award-design — the enforceability round: the 5-lens adversarial audit's adopted
closings. The panel's convergent P0: a lazy run could declare the browser and the
subagents absent, narrate the conformance loop, and ship a 5/10 as READY — every
load-bearing gate was self-attested prose. These lock the closings: capability
probes with verbatim evidence, a status ceiling on browserless runs, the per-section
conformance ledger, the detector beside the scanner (fix-only FAILs, binding
UNMEASURED accounting), the ranked pre-emit critique, isolated dual assessors, the
predictability probe, the live-winner comparative read, and the gate-over-palette
precedence rule."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
REFS = SKILL_DIR / "references"


def _read(rel):
    return (REFS / rel).read_text(encoding="utf-8").lower()


def _skill():
    return (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").lower()


class TestStatusCeiling(unittest.TestCase):
    def test_three_status_model(self):
        pf = _read("preflight.md")
        self.assertIn("ready-unverified", pf)
        self.assertIn("caps at **not done — unverified render**", pf)

    def test_tooling_gaps_carry_the_probe(self):
        self.assertIn("verbatim failed probe", _read("preflight.md"))

    def test_blocking_is_defined(self):
        pf = _read("preflight.md")
        self.assertIn("blocking is defined, not felt", pf)
        self.assertIn("fatal-class fail", pf)

    def test_override_pressure_routes_to_r2(self):
        pf = _read("preflight.md")
        self.assertIn("any override on an axiomatic box", pf)
        self.assertIn("**suppressions:**", pf)


class TestCapabilityProbes(unittest.TestCase):
    def test_review_capability_line(self):
        s = _skill()
        self.assertIn("subagents: present | absent (checked:", s)
        self.assertIn(
            "a claimed absence on a harness whose subagent tool answers the check "
            "is a skipped gate", s)

    def test_degraded_label_travels(self):
        s = _skill()
        self.assertIn("travels verbatim into the final ship report", s)
        self.assertIn("a refutation with no anchor is theater", s)


class TestConformanceLedger(unittest.TestCase):
    def test_ledger_replaces_narration(self):
        s = _skill()
        self.assertIn("ledger row", s)
        self.assertIn("never a narration", s)

    def test_uniform_first_try_is_an_anomaly(self):
        self.assertIn("uniform-verdict anomaly", _skill())
        self.assertIn("**ledger:**", _read("preflight.md"))


class TestDetectorWiring(unittest.TestCase):
    def test_detector_beside_the_scanner(self):
        pf = _read("preflight.md")
        self.assertIn("the detector catches, it never clears", pf)
        self.assertIn("unmeasured: n → driven: m", pf)
        self.assertIn("detector fails are fix-only", pf)

    def test_skill_invokes_detector_at_phase_5(self):
        self.assertIn("assets/detector.js", _skill())

    def test_every_preflight_tag_has_a_detector_rule(self):
        pf_raw = (REFS / "preflight.md").read_text(encoding="utf-8")
        tags = set(re.findall(r"\(detector: ([A-Z0-9-]+)\)", pf_raw))
        self.assertTrue(tags, "preflight must tag detector-backed boxes")
        js = (SKILL_DIR / "assets" / "detector.js").read_text(encoding="utf-8")
        ids = set(re.findall(r"id:\s*['\"]([A-Z0-9-]+)['\"]", js))
        missing = tags - ids
        self.assertFalse(
            missing, f"preflight tags with no detector rule: {sorted(missing)}")


class TestPreEmitCritique(unittest.TestCase):
    def test_section_zero_axes(self):
        pf = _read("preflight.md")
        self.assertIn("## 0. pre-emit critique", pf)
        for axis in ("world", "hierarchy", "craft", "specificity",
                     "restraint", "aliveness"):
            with self.subTest(axis=axis):
                self.assertIn(f"**{axis}**", pf)

    def test_ranking_not_threshold(self):
        # A threshold teaches the passing constant (score everything 4); a
        # ranking cannot be scored around — there is always a lowest.
        self.assertIn(
            "the lowest axis always takes one named, targeted revision",
            _read("preflight.md"))
        s = _skill()
        self.assertIn(
            "there is always a lowest, so the gate cannot be scored around", s)
        self.assertIn("· critique: w4 h3 c4 s4 r5 a3", s)


class TestDualAssessors(unittest.TestCase):
    def test_isolation_invariant(self):
        s = _skill()
        self.assertIn("both assessors are subagents by definition", s)
        self.assertIn(
            "never sees scanner output, detector output, or the preflight verdict", s)

    def test_rubric_supersedes_ordering(self):
        self.assertIn("isolation supersedes ordering", _read("audit-rubric.md"))


class TestPredictabilityProbe(unittest.TestCase):
    def test_r1_opens_with_the_probe(self):
        s = _skill()
        self.assertIn("predictability probe", s)
        self.assertIn(
            "a matched prediction means the direction is still a default", s)

    def test_probe_void_in_degraded_run(self):
        ar = _read("audit-rubric.md")
        self.assertIn("the predictability probe (r1)", ar)
        self.assertIn("void in a degraded same-context run", ar)


class TestPrecedence(unittest.TestCase):
    def test_gate_over_palette(self):
        s = _skill()
        self.assertIn("a phase 5 gate wins over an archetype palette row", s)
        self.assertIn("never a licence", s)


class TestComparativeReadIsLive(unittest.TestCase):
    def test_pull_up_means_live_url(self):
        ar = _read("audit-rubric.md")
        self.assertIn(
            "the winner's live url opened and screenshotted beside the build", ar)
        self.assertIn("comparison from description", ar)


class TestDesireReadTravels(unittest.TestCase):
    """ARDEN's review wrote "dishwater" mid-pass, then softened it into a clean
    conclusion at synthesis — the desire verdict, filed as "declared" evidence,
    lost to green mechanics. The read is now driven evidence, emitted first in a
    fixed format, verbatim-travel protected like READY-UNVERIFIED."""

    def setUp(self):
        self.skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.pf = (SKILL_DIR / "references" / "preflight.md").read_text(encoding="utf-8")

    def test_desire_read_is_driven_evidence(self):
        low = self.skill.lower()
        self.assertIn("comparative desire read run on the rendered pixels beside the live exemplar is driven evidence",
                      low)
        self.assertIn("never outranked by clean mechanical reports", low)

    def test_first_emitted_line_fixed_format(self):
        # the format token is case-sensitive
        self.assertIn('DESIRE-READ: BEATS|LOSES <exemplar>', self.skill)
        self.assertIn("first emitted line is the read", self.skill.lower())
        self.assertIn("travels verbatim", self.skill.lower())

    def test_verdict_block_carries_the_field(self):
        self.assertIn("**Desire read:**", self.pf)
        self.assertIn("DESIRE-READ:", self.pf)

    def test_skip_vs_gap_doctrine(self):
        low = self.skill.lower()
        # with a rung present, comparison-from-description is the same fail as a false tick
        self.assertIn("legal only with no browser rung", low)
        self.assertIn("the same fail as falsely ticking a box", low)


class TestRotationQuotesTheStamp(unittest.TestCase):
    def test_quoted_stamp_or_failed_lookup(self):
        s = _skill()
        self.assertIn("quotes the stamp line it found, verbatim", s)
        self.assertIn("nav:<pattern>", s)


class TestProvenance(unittest.TestCase):
    def test_truth_source_freshness_token(self):
        self.assertIn("freshness token", _read("preflight.md"))

    def test_perf_numbers_carry_provenance(self):
        self.assertIn(
            "a number with no provenance is an asserted number",
            _read("preflight.md"))


if __name__ == "__main__":
    unittest.main()
