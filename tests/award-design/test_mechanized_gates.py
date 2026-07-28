"""award-design — the enforceability survivors. The rebuild retired the
self-attested machinery (pre-emit critique, conformance ledger, capability
lines, axiomatic-box suppressions) and kept the gates a lazy run cannot narrate
around: the status ceiling on browserless runs, probe-before-declaring-a-gap,
the detector beside the scanner with fix-only FAILs, reviewer isolation,
the predictability probe, the desire read as driven evidence, and perf-number
provenance."""

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


def _gate(rel):
    return (REFS / "gate" / rel).read_text(encoding="utf-8").lower()


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
        c = _gate("concept.md")
        self.assertIn("degraded: same-context", c)
        self.assertIn("a probe that vanishes without one is a skipped gate", c,
                      "a review that emits no written verdict clears nothing")

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


class TestReviewerIsolation(unittest.TestCase):
    def test_isolation_invariant(self):
        """One driven audit replaced the A/B assessor pair, so isolation is
        carried by the reviewer's own discipline: fresh context, read-only, its
        own browser session, and the render inventoried before any report or
        contract is read. Driven evidence still outranks declared."""
        r = _gate("review.md")
        self.assertIn("fresh-context subagent, read-only", r)
        self.assertIn("parallel reviewers never share a browser session", r)
        self.assertIn("before reading the direction contract", r)
        self.assertIn("spec fiction", r,
                      "a declared beat that does not render is a finding, whatever the code claims")

    def test_rubric_supersedes_ordering(self):
        self.assertIn("isolation supersedes ordering", _read("audit-rubric.md"))


class TestPredictabilityProbe(unittest.TestCase):
    def test_r1_opens_with_the_probe(self):
        c = _gate("concept.md")
        self.assertIn("predictability probe", c)
        self.assertIn("means it is still a default", c)

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
        self.review = (REFS / "gate" / "review.md").read_text(encoding="utf-8")
        self.pf = (SKILL_DIR / "references" / "preflight.md").read_text(encoding="utf-8")

    def test_desire_read_is_driven_evidence(self):
        low = self.review.lower()
        self.assertIn("a loses read is driven evidence", low)
        self.assertIn("it outranks every clean mechanical report", low)
        self.assertIn("never softened", low)

    def test_first_line_fixed_format(self):
        # the format token is case-sensitive
        self.assertIn('DESIRE-READ: BEATS|LOSES <exemplar>', self.review)
        low = self.review.lower()
        self.assertIn("first emitted line", low)
        self.assertIn("travels into the ship report", low)

    def test_skip_vs_gap_doctrine(self):
        # a false tick and a lazily declared gap are the same fail
        self.assertIn("Falsely ticking a browser box is worse than declaring the gap",
                      self.pf)
        self.assertIn("declaring a gap the harness could have closed is the same fail",
                      self.pf)


class TestProvenance(unittest.TestCase):
    def test_truth_source_freshness_token(self):
        self.assertIn("freshness token", _read("preflight.md"))

    def test_perf_numbers_carry_provenance(self):
        pf = _read("preflight.md")
        self.assertIn("an asserted number is a fail", pf)
        self.assertIn("provenance", pf)


if __name__ == "__main__":
    unittest.main()
