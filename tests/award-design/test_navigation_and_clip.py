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


class TestNavComponentImplementsTheAccumulator(unittest.TestCase):
    """The library component must implement the machine navigation-patterns.md
    prescribes. MARE and CALDERA both shipped nav flicker from the same root: the
    component tested the raw per-frame delta while the reference prescribed
    accumulators — a reference/component contradiction no test drove. Harness
    evidence (2026-07-17): raw delta = 19 hide/show flips under ±3px jitter;
    accumulator = 0 flips, 1 transition per genuine intent."""

    def setUp(self):
        comp = SKILL_DIR / "assets" / "components" / "show-on-scroll-up-nav.js"
        self.src = comp.read_text(encoding="utf-8")

    def test_direction_from_accumulators_never_raw_delta(self):
        self.assertIn("downAcc", self.src)
        self.assertIn("upAcc", self.src)
        self.assertNotIn("y > lastY", self.src,
                         "raw-delta direction test — the flicker root MARE and CALDERA shipped")

    def test_direction_change_resets_the_opposite_accumulator(self):
        self.assertRegex(self.src, r"upAcc\s*=\s*0;\s*downAcc\s*\+=")
        self.assertRegex(self.src, r"downAcc\s*=\s*0;\s*upAcc\s*-?=")

    def test_dy_zero_holds_state(self):
        self.assertIn("dy == 0", self.src)
        self.assertIn("hold", self.src.lower())

    def test_tolerances_exposed_as_css_custom_properties(self):
        for prop in ("--ad-nav-top-guard", "--ad-nav-hide-tol", "--ad-nav-show-tol"):
            with self.subTest(prop=prop):
                self.assertIn(prop, self.src)


class TestNavOverHeroEncoding(unittest.TestCase):
    """ARDEN shipped an opaque bone bar over the hero photo — decapitation from
    pixel 0 — while passing every gate, because the transparent-over-hero rule
    lived only in prose. This locks the gate that now consumes it: a detector
    rule, a §8 box, an imposed verdict, and the covering ids the pick-path names."""

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
        self.assertIn("fatal six", self.detector_md)
        self.assertIn("NAV-HERO-OPAQUE", self.detector_md)

    def test_preflight_has_nav_over_hero_box(self):
        self.assertIn("Nav over the hero", self.pf,
                      "preflight §8 must carry the nav-over-hero box")
        self.assertIn("sentinel", self.pf.lower())

    def test_imposed_verdict_row_present(self):
        self.assertIn("Nav paints no opaque band over a media hero", self.body,
                      "the imposed-verdicts register must carry the nav-over-hero row")

    def test_pickpath_names_covering_ids(self):
        # the nav commit must name the covering component per pattern
        self.assertIn("nav-hero-surface", self.body)
        self.assertIn("show-on-scroll-up-nav", self.body)


class TestNavHeroSurfaceComponent(unittest.TestCase):
    """The persistent-bar surface axis had no covering id — the winner norm
    (a quiet persistent bar over the hero) could not be composed, so a build
    fell back to a hand-authored opaque bar. nav-hero-surface fills it: surface
    only, hero-bottom sentinel, no visibility hiding."""

    def setUp(self):
        self.comp = SKILL_DIR / "assets" / "components" / "nav-hero-surface.js"
        self.src = self.comp.read_text(encoding="utf-8")

    def test_file_exists_and_in_manifest(self):
        import json
        self.assertTrue(self.comp.is_file())
        manifest = json.loads((SKILL_DIR / "assets" / "components" / "manifest.json").read_text(encoding="utf-8"))
        ids = {c["id"] for c in manifest["components"]}
        self.assertIn("nav-hero-surface", ids)

    def test_grounds_on_hero_sentinel_not_scrolly(self):
        self.assertIn("IntersectionObserver", self.src)
        self.assertIn("sentinel", self.src.lower())
        self.assertIn("is-grounded", self.src)

    def test_no_hero_forces_solid(self):
        # navigation-patterns.md: a page with no hero forces the solid state
        self.assertRegex(self.src, r"setGrounded\(true\)")

    def test_surface_axis_only_never_hides(self):
        # this component owns surface, not visibility — no is-hidden axis here
        self.assertNotIn("is-hidden", self.src,
                         "nav-hero-surface is the surface axis only; hiding belongs to show-on-scroll-up-nav")

    def test_reduced_motion_path(self):
        self.assertIn("prefers-reduced-motion", self.src)


class TestShowNavGainsSentinel(unittest.TestCase):
    """The surface axis grounded at a fixed 64px scrollY — grounding the bar while
    it still floated over a full-viewport hero. navigation-patterns.md prescribes a
    hero-bottom sentinel; the component now implements it (fallback to threshold on
    a hero-less page)."""

    def setUp(self):
        comp = SKILL_DIR / "assets" / "components" / "show-on-scroll-up-nav.js"
        self.src = comp.read_text(encoding="utf-8")

    def test_surface_axis_uses_sentinel_observer(self):
        self.assertIn("IntersectionObserver", self.src)
        self.assertIn("sentinel", self.src.lower())

    def test_threshold_is_fallback_only(self):
        # is-scrolled is threshold-driven only when no sentinel observer runs
        self.assertRegex(self.src, r"if \(!surfaceObserver\) nav\.classList\.toggle\('is-scrolled'")

    def test_accumulator_visibility_axis_intact(self):
        # the sentinel upgrade must not touch the flicker-proof visibility machine
        self.assertIn("downAcc", self.src)
        self.assertIn("upAcc", self.src)
        self.assertIn("dy == 0", self.src)


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
