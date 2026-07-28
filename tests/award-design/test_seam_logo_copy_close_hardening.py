"""award-design — the BOREALIS-test hardening: real brand mark, graded image seams,
the copy re-read pass, and a real overlay close control.

The BOREALIS build shipped a decorative green dot as its logo, a hard-cut hero seam
that "faded too brutally" into the next section, registration-meta copy (READING 01),
a hero reading overlay that broke responsively, and a mobile overlay menu with no
clearly-visible close. These lock the fixes that survived the floor rewrite."""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
REFS = SKILL_DIR / "references"


def _read(rel):
    return (REFS / rel).read_text(encoding="utf-8").lower()


class TestRealBrandMark(unittest.TestCase):
    def test_anti_pattern_bans_decorative_dot_logo(self):
        ap = _read("anti-patterns.md")
        self.assertIn("decorative dot, tick, or status glyph", ap)
        self.assertIn("mark drives the favicon", ap)

    def test_imagery_forces_verified_mark_and_shared_favicon(self):
        im = _read("imagery.md")
        self.assertIn("verified rendered in the browser", im)
        self.assertIn("colored dot / status-tick", im)
        self.assertIn("mark drives the favicon", im)

    def test_optical_craft_favicon_is_the_real_mark(self):
        oc = _read("optical-craft.md")
        self.assertIn("the favicon is the real brand mark", oc)

    def test_preflight_gates_mark_and_favicon(self):
        pf = _read("preflight.md")
        self.assertIn("the same mark drives the favicon, both verified rendered", pf)


class TestGradedSeams(unittest.TestCase):
    def test_imagery_seams_grade_never_cut(self):
        im = _read("imagery.md")
        self.assertIn("seams grade, never cut", im)
        self.assertIn("graded transition", im)
        self.assertIn("hard horizontal cut", im)
        self.assertIn("mask-image", im)

    def test_preflight_seam_box_gates_graded(self):
        pf = _read("preflight.md")
        self.assertIn("grades into its neighbour", pf)


class TestAdversarialCopyPass(unittest.TestCase):
    def test_preflight_rereads_every_string(self):
        pf = _read("preflight.md")
        self.assertIn("re-read every visible string", pf)
        self.assertIn("no self-narration", pf)

    def test_registration_meta_has_teeth(self):
        pf = _read("preflight.md")
        # numbered diegetic labels (READING 01) are now the scanner's META-LABEL class
        self.assertIn("zero `section 01` / index meta-labels", pf)
        self.assertIn("`(scanner: meta-label)`", pf)


class TestOverlayClose(unittest.TestCase):
    # superseded by the round-5 UAT: the close is findable because it is icon-only AND
    # sits at the trigger's exact point — the invariant (an unmissable exit, aria-named,
    # focus returned) survives in the new form
    def test_navigation_forces_in_place_iconic_close(self):
        nav = _read("navigation-patterns.md")
        self.assertIn("the toggle is icon-only", nav)
        self.assertIn("close menu", nav)
        self.assertIn("focus returns to the trigger", nav)

    def test_preflight_gates_overlay_toggle(self):
        pf = _read("preflight.md")
        self.assertIn("icon-only toggle", pf)
        self.assertIn("`esc` closes, focus returns", pf)


if __name__ == "__main__":
    unittest.main()
