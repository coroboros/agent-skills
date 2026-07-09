"""award-design — the editorial / copy hardening from the bell-foundry test build.

The build honored the mechanical craft (OKLCH, rem, tonal arc, real Web Audio) but
failed on COPY: self-narrating colophon ("a feature on… set in Bodoni Moda"), stacked
label layers (eyebrow + folio + pyrometer + title all naming one section), a count
costume ("first/second/third casting"), and over-written reading blocks. Both the
self-review and a fresh refuter under-weighted it. This locks:

- a copy law (anti-patterns + preflight §6): no self-narration / process credits, no
  stacked label layers, no over-writing;
- copy weighted inside the desire read (audit-rubric) so craft cannot buy back bad copy;
- editorial type-as-image (editorial.md): Bodoni-at-default is the "obvious answer",
  the fix is opsz instancing / SVG masthead / type-as-composition;
- the hide-reveal reframed (interaction-signatures): cut is the default, the reveal is
  rare / subtle / justified and not itself a marker of award quality;
- the two mobile gates (preflight §5/§8/§9 + code-review): tap-target measured at each
  breakpoint (label-hidden shrink), and an absolutely-positioned hero affordance that
  overlaps the H1.
"""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFS = SKILL_DIR / "references"


def _read(rel):
    return (REFS / rel).read_text(encoding="utf-8").lower()


class TestCopyLaw(unittest.TestCase):
    def test_anti_patterns_self_narration(self):
        ap = _read("anti-patterns.md")
        self.assertIn("copy that narrates the artifact or credits its own making", ap)
        # both tells named: describing the piece + crediting the tools/fonts
        self.assertIn("set in bodoni moda", ap)

    def test_anti_patterns_stacked_labels(self):
        ap = _read("anti-patterns.md")
        self.assertIn("stacked label layers that restate each other", ap)
        # the count-costume folio is named as set-dressing
        self.assertIn("first / second / third casting", ap)

    def test_anti_patterns_over_written(self):
        ap = _read("anti-patterns.md")
        self.assertIn("over-written reading copy", ap)

    def test_preflight_copy_boxes(self):
        pf = _read("preflight.md")
        self.assertIn("no self-narration / no process credits", pf)
        self.assertIn("label-layer collapse", pf)
        self.assertIn("copy volume — composed, not poured", pf)


class TestCopyWeightedInDesireRead(unittest.TestCase):
    def test_audit_rubric_copy_in_desire_read(self):
        ar = _read("audit-rubric.md")
        self.assertIn("copy is inside the desire read", ar)
        # craft cannot buy back bad copy
        self.assertIn("craft does not buy back bad copy", ar)


class TestEditorialTypeAsImage(unittest.TestCase):
    def test_type_as_image_over_font_pick(self):
        ed = _read("editorial.md")
        self.assertIn("treating the display type as an image", ed)

    def test_overexposed_didone_default_flagged(self):
        ed = _read("editorial.md")
        self.assertIn("bodoni moda, editorial new, playfair", ed)

    def test_opsz_and_svg_masthead_levers(self):
        ed = _read("editorial.md")
        self.assertIn("optical-size (`opsz`) custom instancing", ed)
        self.assertIn("draw the one masthead word as svg outlines", ed)

    def test_editorial_copy_discipline_section(self):
        ed = _read("editorial.md")
        self.assertIn("copy is composed, not poured", ed)
        self.assertIn("the site never narrates or credits itself", ed)


class TestHideRevealReframed(unittest.TestCase):
    def test_cut_is_the_default(self):
        isig = _read("interaction-signatures.md")
        self.assertIn("its default exit is to cut it", isig)
        self.assertIn("(default)", isig)

    def test_not_an_award_marker(self):
        isig = _read("interaction-signatures.md")
        self.assertIn("not itself a marker of award quality", isig)


class TestMobileGates(unittest.TestCase):
    def test_tap_target_measured_at_breakpoint(self):
        cr = _read("code-review.md")
        self.assertIn("tap targets are measured at each breakpoint", cr)
        pf = _read("preflight.md")
        self.assertIn("shrunk under 24×24", pf)
        self.assertIn("tap targets measured at each breakpoint", pf)

    def test_hero_affordance_overlaps_h1(self):
        pf = _read("preflight.md")
        self.assertIn("no absolute affordance over the h1", pf)

    def test_design_css_token_drift(self):
        cr = _read("code-review.md")
        self.assertIn("drifts from its design.md declaration", cr)
        pf = _read("preflight.md")
        self.assertIn("drifting from its design.md declaration", pf)


if __name__ == "__main__":
    unittest.main()
