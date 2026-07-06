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

Each assertion would FAIL on the skill before this hardening."""

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


def _phase(n):
    m = re.search(rf"^## Phase {n} — .*?\n(.*?)(?=^## )", _body(), re.DOTALL | re.MULTILINE)
    assert m is not None, f"## Phase {n} section missing"
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
        self.assertIn("fill / overlay clip", pf,
                      "preflight §5 must carry a fill/overlay clip craft-floor box")


class TestVerifyGranularity(unittest.TestCase):
    def setUp(self):
        self.pf = _read("preflight.md")
        self.pf_low = self.pf.lower()
        self.p4 = _phase(4).lower()

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

    def test_phase4_loop_mirrors_the_checks(self):
        self.assertIn("hover→leave", self.p4,
                      "the Phase 4 conformance loop must drive hover→leave")
        self.assertTrue("seam" in self.p4,
                        "the Phase 4 loop must capture the section seam")
        self.assertTrue("@supports" in _phase(4) or "modern-css-degraded" in self.p4,
                        "the Phase 4 loop must run the modern-CSS-degraded render")


if __name__ == "__main__":
    unittest.main()
