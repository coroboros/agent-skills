"""award-design — the enforceability survivors. The rebuild retired the
self-attested machinery (pre-emit critique, conformance ledger, capability
lines, axiomatic-box suppressions) and kept the gates a lazy run cannot narrate
around: the status ceiling on browserless runs, probe-before-declaring-a-gap,
the detector beside the scanner with fix-only FAILs, isolated dual assessors,
the predictability probe, the desire read as driven evidence, the rotation
stamp, and perf-number provenance."""

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
        self.assertIn("any unticked box or any fail without a written justification", pf)

    def test_overrides_written_and_brief_tied(self):
        pf = _read("preflight.md")
        self.assertIn("**justified overrides:**", pf)
        self.assertIn("an unstated override is a fail", pf)


class TestCapabilityProbes(unittest.TestCase):
    def test_degraded_review_is_labeled(self):
        s = _skill()
        self.assertIn("degraded: same-context", s)
        self.assertIn('a bare "re-read, looks fine" clears nothing', s)

    def test_probe_before_declaring_gap(self):
        pf = _read("preflight.md")
        self.assertIn("toolsearch for the browser mcp is the mandatory first probe", pf)
        self.assertIn("declaring a gap the harness could have closed is the same fail", pf)


class TestDetectorWiring(unittest.TestCase):
    def test_detector_beside_the_scanner(self):
        pf = _read("preflight.md")
        self.assertIn("the detector runs beside the scanner", pf)
        self.assertIn("detector fails are fix-only", pf)
        self.assertIn("no prose override clears one", pf)

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


class TestDualAssessors(unittest.TestCase):
    def test_isolation_invariant(self):
        s = _skill()
        self.assertIn("two isolated assessors", s)
        self.assertIn("never sees the reports", s)
        self.assertIn("never sees the pixels", s)
        self.assertIn("driven > computed > declared", s)

    def test_rubric_supersedes_ordering(self):
        self.assertIn("isolation supersedes ordering", _read("audit-rubric.md"))


class TestPredictabilityProbe(unittest.TestCase):
    def test_r1_opens_with_the_probe(self):
        s = _skill()
        self.assertIn("predictability probe", s)
        self.assertIn("a match means the direction is still a default", s)

    def test_probe_void_in_degraded_run(self):
        ar = _read("audit-rubric.md")
        self.assertIn("the predictability probe (r1)", ar)
        self.assertIn("void in a degraded same-context run", ar)


class TestComparativeReadIsLive(unittest.TestCase):
    def test_pull_up_means_live_url(self):
        ar = _read("audit-rubric.md")
        self.assertIn(
            "the winner's live url opened and screenshotted beside the build", ar)
        self.assertIn("comparison from description", ar)


class TestDesireReadTravels(unittest.TestCase):
    """ARDEN's review wrote "dishwater" mid-pass, then softened it into a clean
    conclusion at synthesis — the desire verdict lost to green mechanics. The
    read is driven evidence, emitted first in a fixed format, and travels
    verbatim into the ship report."""

    def setUp(self):
        self.skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.pf = (SKILL_DIR / "references" / "preflight.md").read_text(encoding="utf-8")

    def test_desire_read_is_driven_evidence(self):
        low = self.skill.lower()
        self.assertIn("the desire read is driven evidence", low)
        self.assertIn("outranks clean mechanical reports", low)
        self.assertIn("never softened", low)

    def test_first_line_fixed_format(self):
        # the format token is case-sensitive
        self.assertIn('DESIRE-READ: BEATS|LOSES <exemplar>', self.skill)
        low = self.skill.lower()
        self.assertIn("the review's first line", low)
        self.assertIn("travels verbatim", low)

    def test_skip_vs_gap_doctrine(self):
        # a false tick and a lazily declared gap are the same fail
        self.assertIn("Falsely ticking a browser box is worse than declaring the gap",
                      self.pf)
        self.assertIn("declaring a gap the harness could have closed is the same fail",
                      self.pf)


class TestRotationStamp(unittest.TestCase):
    def test_stamp_written_and_read(self):
        s = _skill()
        self.assertIn("nav:<pattern>", s)
        self.assertIn("read the previous build's stamp", s)
        self.assertIn("the rotation ledger the next build reads", s)


class TestProvenance(unittest.TestCase):
    def test_truth_source_freshness_token(self):
        self.assertIn("freshness token", _read("preflight.md"))

    def test_perf_numbers_carry_provenance(self):
        pf = _read("preflight.md")
        self.assertIn("an asserted number is a fail", pf)
        self.assertIn("provenance", pf)


if __name__ == "__main__":
    unittest.main()
