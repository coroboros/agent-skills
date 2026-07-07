"""award-design — the BOREALIS-test hardening: real brand mark, graded image seams,
adversarial copy pass, responsive signature text, and a real overlay close control.

The BOREALIS build shipped a decorative green dot as its logo, a hard-cut hero seam
that "faded too brutally" into the next section, registration-meta copy (READING 01),
a hero reading overlay that broke responsively, and a mobile overlay menu with no
clearly-visible close. These lock the fixes."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFS = SKILL_DIR / "references"


def _read(rel):
    return (REFS / rel).read_text(encoding="utf-8").lower()


def _phase(n):
    body = SKILL_MD.read_text(encoding="utf-8")
    m = re.search(rf"^## Phase {n} — .*?\n(.*?)(?=^## )", body, re.DOTALL | re.MULTILINE)
    assert m is not None, f"## Phase {n} section missing"
    return m.group(1).lower()


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
        self.assertIn("brand mark + favicon real", pf)


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

    def test_phase4_loop_gates_graded_seam(self):
        p4 = _phase(4)
        self.assertIn("graded, never a hard cut", p4)


class TestAdversarialCopyPass(unittest.TestCase):
    def test_preflight_has_adversarial_copy_pass(self):
        pf = _read("preflight.md")
        self.assertIn("adversarial copy pass", pf)
        self.assertIn("what does this add here", pf)

    def test_registration_meta_has_teeth(self):
        pf = _read("preflight.md")
        # numbered diegetic labels + atmospheric stat strips called out by example
        self.assertIn("reading 01", pf)
        self.assertTrue("stat strip" in pf or "set-dressing" in pf)


class TestResponsiveSignatureText(unittest.TestCase):
    def test_preflight_gates_signature_text_responsive(self):
        pf = _read("preflight.md")
        self.assertIn("signature text driven responsive", pf)

    def test_phase4_loop_drives_signature_text_at_every_width(self):
        p4 = _phase(4)
        self.assertIn("signature's own text overlay", p4)


class TestOverlayClose(unittest.TestCase):
    def test_navigation_forces_labeled_close(self):
        nav = _read("navigation-patterns.md")
        self.assertIn("unmistakable, labeled close control", nav)
        self.assertIn("close menu", nav)
        self.assertIn("focus returns to the trigger", nav)

    def test_preflight_gates_overlay_close(self):
        pf = _read("preflight.md")
        self.assertIn("overlay menu close", pf)


if __name__ == "__main__":
    unittest.main()
