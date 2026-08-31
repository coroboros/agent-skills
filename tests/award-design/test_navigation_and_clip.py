"""award-design — the three surgical hardenings from the Maison Aurèle test run.

The gated protocol and most award imperatives already existed; these lock the
gaps that run surfaced as real shipped defects:
  1. the canonical scroll-aware nav *implementation* behind imperative #2 (the
     rule existed; the proven pattern — two axes, hero sentinel, SSR paint,
     freeze-on-focus, reduced-motion-flips — did not),
  2. overflow-clip discipline for animated fills / full-bleed layers (a CTA fill
     spilled its pill; a negative-inset hero layer bled into the next section),
  3. verify-loop granularity — hover→leave, section seams, and a
     modern-CSS-degraded render (a scroll-scrim hit opacity:.82 unguarded).

Each assertion would fail on the skill before this hardening."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFS = SKILL_DIR / "references"


def _read(name):
    return (REFS / name).read_text(encoding="utf-8")


def _body():
    return SKILL_MD.read_text(encoding="utf-8")


def _verify():
    m = re.search(r"^## Verify, then ship\n(.*?)(?=^## )", _body(), re.DOTALL | re.MULTILINE)
    assert m is not None, "## Verify, then ship section missing"
    return m.group(1)


class TestNavigationPatternsReference(unittest.TestCase):
    def setUp(self):
        self.nav = _read("navigation-patterns.md")
        self.low = self.nav.lower()

    def test_file_exists(self):
        self.assertTrue((REFS / "navigation-patterns.md").is_file(),
                        "references/navigation-patterns.md missing")

    def test_imperative_points_here(self):
        imp = _read("award-imperatives.md")
        self.assertIn("navigation-patterns.md", imp,
                      "award-imperatives.md #2 must point to the canonical implementation")

    def test_two_decoupled_axes(self):
        # visibility (headroom) and surface (hero crossing) as independent machines
        self.assertTrue("visibility" in self.low and "surface" in self.low,
                        "the pattern is two axes: visibility (headroom) + surface (hero crossing)")
        self.assertIn("state machine", self.low)

    def test_hero_sentinel_not_scrolly_math(self):
        self.assertIn("sentinel", self.low,
                      "surface crossing uses a hero-bottom sentinel, not a scrollY threshold")

    def test_the_four_competent_version_misses(self):
        # SSR-correct first paint, freeze-on-focus (WCAG 2.4.11),
        # reduced-motion flips instantly, JS-writes-state / CSS-owns-motion
        self.assertTrue("ssr" in self.low or "first paint" in self.low or "first-paint" in self.low,
                        "SSR/first-paint must already be the correct surface (no flash)")
        self.assertIn("2.4.11", self.nav,
                      "freeze-revealed on focus must cite WCAG 2.4.11")
        self.assertIn("prefers-reduced-motion", self.nav,
                      "reduced motion flips state instantly, does not disable the behavior")
        self.assertTrue("translateY(-100%)".lower() in self.low,
                        "hidden = translateY(-100%), transform/paint only (zero CLS)")

    def test_thresholds_and_coalescing(self):
        self.assertTrue("top_guard" in self.low and "hide_tol" in self.low,
                        "the headroom machine names its TOP_GUARD / HIDE_TOL thresholds")
        self.assertIn("requestanimationframe", self.low,
                      "reads are rAF-coalesced, not throttled")


class TestNavOverHeroEncoding(unittest.TestCase):
    """ARDEN shipped an opaque bone bar over the hero photo — decapitation from
    pixel 0 — while passing every gate, because the transparent-over-hero rule
    lived only in prose. This locks the gate that now consumes it: a detector
    rule, a §8 box, and the SKILL.md hard constraint."""

    def setUp(self):
        self.detector_md = _read("detector.md")
        self.pf = _read("preflight.md")
        self.body = _body()

    def test_detector_names_both_nav_hero_rules(self):
        for rule in ("NAV-HERO-OPAQUE", "NAV-HERO-SURFACE"):
            with self.subTest(rule=rule):
                self.assertIn(rule, self.detector_md,
                              "detector.md must name the nav-over-hero rule or the audit cannot route it")

    def test_detector_fatal_set_includes_the_decapitation(self):
        self.assertIn("fatal nine", self.detector_md)
        self.assertIn("NAV-HERO-OPAQUE", self.detector_md)

    def test_preflight_has_nav_over_hero_box(self):
        self.assertIn("Nav over the hero", self.pf,
                      "preflight §8 must carry the nav-over-hero box")
        self.assertIn("sentinel", self.pf.lower())

    def test_hard_constraint_names_the_band(self):
        self.assertIn("paints an opaque unblurred band over a media hero", self.body,
                      "the hard-constraints list must carry the nav-over-hero refusal")
        self.assertIn("(detector: NAV-HERO-OPAQUE)", self.body)


class TestOverflowClipDiscipline(unittest.TestCase):
    def test_anti_pattern_tell_present(self):
        ap = _read("anti-patterns.md").lower()
        self.assertIn("spill", ap, "the unclipped-fill tell must name the spill failure")
        self.assertTrue("overflow: hidden" in ap or "clip-path" in ap,
                        "the fix is overflow:hidden / clip-path on the shaped ancestor")
        self.assertIn("scalex", ap,
                      "prefer translateX/clip-path over scaleX on rounded shapes (border-radius distortion)")

    def test_preflight_craft_box(self):
        pf = _read("preflight.md").lower()
        self.assertIn("clips to its container's shape", pf,
                      "preflight §5 must carry the fill/overlay clip craft-floor box")


class TestVerifyGranularity(unittest.TestCase):
    def setUp(self):
        self.pf = _read("preflight.md")
        self.pf_low = self.pf.lower()
        self.verify = _verify()

    def test_preflight_hover_leave_box(self):
        self.assertIn("hover→leave", self.pf,
                      "preflight §8 must drive hover→leave (the retract-frame spill)")

    def test_preflight_section_seam_box(self):
        self.assertIn("section seams", self.pf_low,
                      "preflight §8 must capture section seams, not only centers")

    def test_preflight_degraded_render_box(self):
        self.assertTrue("modern-css-degraded" in self.pf_low or "degraded render" in self.pf_low,
                        "preflight §8 must check a modern-CSS/@supports-degraded render")
        self.assertIn("animation-timeline", self.pf,
                      "the degraded check names the scroll-timeline @supports guard")

    def test_render_floor_sweep_runs_per_chunk(self):
        """The render-floor sweep is per chunk: the payload sweeps
        each chunk as it lands, and the driven hover→leave / seam /
        degraded-render boxes above are what it feeds. A loop deferred to the
        review chunk is the mobile collapse nobody re-drove."""
        self.assertIn("after each chunk, inject `assets/render-floor.js` and sweep "
                      "375/768/1024/1440/1920 on the pages the chunk touches",
                      self.verify)


if __name__ == "__main__":
    unittest.main()
