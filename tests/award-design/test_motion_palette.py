"""award-design — the motion palette (content/decoration split), navbar settle-fix,
signature-on-hero (axis 8), and immersive-CTA hardening.

The NOIRE re-test surfaced the next ceiling: a navbar that flashed back on every
scroll-stop, a bespoke signature buried below the fold, and an over-ornamented CTA;
and adversarial deep-research corrected the motion default. These lock the fixes:
  - a codified motion palette split by what moves — content reveals fire once and
    persist (NN/g), decorative/scrubbed motion is reversible native CSS scroll-driven,
  - the navbar show-gate distinguishes a scroll-stop from a scroll-up,
  - the signature must land on the make-or-break surface,
  - the immersive CTA drops the ornament and echoes the signature on hover.

Grounded in NN/g's scroll-fading study and a shipped premium build's native
`animation-timeline` technique (no animation library)."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFS = SKILL_DIR / "references"


def _read(rel):
    return (REFS / rel).read_text(encoding="utf-8").lower()


def _body():
    return SKILL_MD.read_text(encoding="utf-8")


def _phase(n):
    m = re.search(rf"^## Phase {n} — .*?\n(.*?)(?=^## )", _body(), re.DOTALL | re.MULTILINE)
    assert m is not None, f"## Phase {n} section missing"
    return m.group(1)


def _review_mode():
    m = re.search(r"^## Review mode.*?(?=^## )", _body(), re.DOTALL | re.MULTILINE)
    assert m is not None, "Review mode section missing"
    return m.group(0)


class TestMotionPaletteFile(unittest.TestCase):
    def setUp(self):
        self.path = REFS / "motion-palette.md"
        self.assertTrue(self.path.is_file(), "references/motion-palette.md must exist")
        self.mp = self.path.read_text(encoding="utf-8").lower()

    def test_centerpiece_is_native_scroll_driven(self):
        self.assertIn("animation-timeline: view()", self.mp)
        self.assertTrue("scroll(root block)" in self.mp or "scroll()" in self.mp)
        self.assertIn("linear both", self.mp, "the scrubbed fill grammar")

    def test_model_splits_content_and_decoration(self):
        # corrected model: content = fire-once + persist, decoration = reversible
        self.assertIn("split by what moves", self.mp)
        self.assertIn("fire-once", self.mp)
        self.assertIn("persist", self.mp)
        self.assertIn("reversible", self.mp)
        self.assertIn("re-hide", self.mp, "re-hiding content on scroll-up is the tell")

    def test_grounded_in_nng_and_cover_phase_rule(self):
        self.assertTrue("nielsen norman" in self.mp or "nn/g" in self.mp)
        self.assertIn("cover", self.mp)  # the cover-phase range rule for the editorial exception
        self.assertIn("declared", self.mp)  # reversible content reveal is opt-in, not default

    def test_browser_reality_progressive_enhancement(self):
        self.assertIn("not baseline", self.mp)
        self.assertIn("@supports", self.mp)
        self.assertIn("animation-trigger", self.mp)  # emerging primitive, flagged not-yet-shippable

    def test_quantity_governed_by_restraint(self):
        self.assertIn("imposed", self.mp)
        self.assertIn("restraint", self.mp)

    def test_palette_table_tiers_the_mechanics(self):
        for token in ("winner", "shipped", "technique"):
            with self.subTest(token=token):
                self.assertIn(token, self.mp)
        for mech in ("pinned scroll-scrubbed video", "webgl 3d scene", "view-transition morph"):
            with self.subTest(mech=mech):
                self.assertIn(mech, self.mp)

    def test_story_leads_over_technique(self):
        # the evidence tier measures proven-ness, never permission to win — story decides
        self.assertIn("story leads", self.mp)
        self.assertIn("terminal industries", self.mp)
        self.assertIn("not whether the build wins", self.mp)

    def test_signature_medium_is_archetype_dependent(self):
        self.assertIn("medium is archetype-dependent", self.mp)
        self.assertIn("site of the year", self.mp)  # Lando SOTY heads the WebGL winner roster

    def test_invention_is_grounded_and_approved(self):
        self.assertIn("inventing a new mechanic", self.mp)
        self.assertTrue("grounded" in self.mp and "approved" in self.mp)


class TestModelSplitWired(unittest.TestCase):
    def test_imperative_three_splits_the_model(self):
        imp = _read("award-imperatives.md")
        self.assertIn("motion-palette.md", imp)
        self.assertIn("fire once and persist", imp)
        self.assertTrue("nn/g" in imp or "usability failure" in imp)
        self.assertIn("reversible", imp)

    def test_phase4_motion_splits(self):
        p4 = _phase(4).lower()
        self.assertIn("motion-palette.md", p4)
        self.assertIn("fire once and persist", p4)
        self.assertIn("reversible", p4)

    def test_skill_loads_the_palette(self):
        # loaded at Phase 4, where the palette binds (the Phase 3 copy was dead weight)
        self.assertIn("motion-palette.md", _phase(4))

    def test_anti_pattern_names_rehide_on_scroll_up(self):
        ap = _read("anti-patterns.md")
        self.assertIn("re-hide on scroll-up", ap)
        self.assertIn("fire once and persist", ap)

    def test_preflight_checks_the_split(self):
        pf = _read("preflight.md")
        self.assertIn("content persists", pf)


class TestNavbarSettleFix(unittest.TestCase):
    def setUp(self):
        self.nav = _read("navigation-patterns.md")

    def test_show_tolerance_exists(self):
        self.assertIn("show_tol", self.nav)

    def test_scroll_stop_is_not_scroll_up(self):
        self.assertIn("a scroll-stop is not a scroll-up", self.nav)
        self.assertIn("five things a competent version misses", self.nav)

    def test_dy_zero_holds_state(self):
        self.assertTrue("dy == 0" in self.nav or "dy === 0" in self.nav)
        self.assertIn("hold", self.nav)

    def test_preflight_gates_no_flash_on_stop(self):
        pf = _read("preflight.md")
        self.assertIn("nav holds on scroll-stop", pf)

    def test_imperative_two_names_the_stop_vs_up_gate(self):
        imp = _read("award-imperatives.md")
        self.assertTrue("scroll-*stop*" in imp or "scroll-stop" in imp
                        or "flashes back at rest" in imp or "never flashes back" in imp)


class TestAxis8SignatureOnMakeOrBreakSurface(unittest.TestCase):
    def test_signature_invention_places_it_on_the_hero(self):
        sig = _read("signature-invention.md")
        self.assertIn("make-or-break surface", sig)
        self.assertIn("below the fold", sig)

    def test_skill_phase1_and_r1_bind_placement(self):
        self.assertIn("make-or-break surface", _phase(1))
        r1 = _review_mode().lower()
        self.assertIn("make-or-break surface", r1)
        self.assertIn("placement", r1)

    def test_imperative_one_binds_placement(self):
        imp = _read("award-imperatives.md")
        self.assertIn("make-or-break surface", imp)
        self.assertTrue("below the fold" in imp or "section four" in imp)


class TestImmersiveCTA(unittest.TestCase):
    def test_premium_patterns_drops_the_ornament(self):
        pp = _read("premium-patterns.md")
        self.assertIn("drops the ornament", pp)
        self.assertIn("echoes the page's signature", pp)

    def test_anti_pattern_names_over_ornamented_cta(self):
        ap = _read("anti-patterns.md")
        self.assertIn("over-ornamented cta", ap)


if __name__ == "__main__":
    unittest.main()
