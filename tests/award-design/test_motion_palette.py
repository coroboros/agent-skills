"""award-design — the motion palette, reversible-scroll default, navbar settle-fix,
signature-on-hero (axis 8), and immersive-CTA hardening.

The NOIRE re-test surfaced the next ceiling: the build shipped fire-once IO reveals
(a static second pass), a navbar that flashed back on every scroll-stop, a bespoke
signature buried below the fold, and an over-ornamented CTA. These lock the fixes:
  - a codified motion palette whose default is reversible native CSS scroll-driven,
  - the navbar show-gate distinguishes a scroll-stop from a scroll-up,
  - the signature must land on the make-or-break surface,
  - the immersive CTA drops the ornament and echoes the signature on hover.

Grounded in the MCLL technique (native `animation-timeline`, no animation library)."""

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
        self.assertIn("linear both", self.mp, "the reversible fill grammar")

    def test_default_model_is_reversible_not_fire_once(self):
        self.assertIn("reversible", self.mp)
        self.assertIn("fire-once", self.mp)
        self.assertTrue("re-arm" in self.mp, "the IO fallback re-arms, never plays once")

    def test_quantity_governed_by_restraint(self):
        # the model is imposed; the amount of motion is not "animate everything"
        self.assertIn("imposed", self.mp)
        self.assertIn("restraint", self.mp)

    def test_palette_indexes_the_known_mechanics(self):
        for token in ("scroll-aware navbar", "scroll-scrubbed media", "reversible scroll scrub"):
            with self.subTest(token=token):
                self.assertIn(token, self.mp)

    def test_invention_is_grounded_and_approved(self):
        self.assertIn("inventing a new mechanic", self.mp)
        self.assertTrue("grounded" in self.mp and "approved" in self.mp)


class TestReversibleDefaultWired(unittest.TestCase):
    def test_imperative_three_makes_reversible_the_default(self):
        imp = _read("award-imperatives.md")
        self.assertIn("reversible", imp)
        self.assertIn("motion-palette.md", imp)
        self.assertIn("fire-once", imp)

    def test_phase4_motion_is_scroll_linked(self):
        p4 = _phase(4).lower()
        self.assertIn("scroll-linked", p4)
        self.assertIn("motion-palette.md", p4)

    def test_skill_loads_the_palette(self):
        # loaded at Phase 3 (source) and Phase 4 (build)
        self.assertIn("motion-palette.md", _phase(3))
        self.assertIn("motion-palette.md", _phase(4))

    def test_anti_pattern_names_fire_once_reveal(self):
        ap = _read("anti-patterns.md")
        self.assertIn("fire-once scroll reveals", ap)

    def test_preflight_checks_reversible_replay(self):
        pf = _read("preflight.md")
        self.assertIn("reversible scroll motion", pf)


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
