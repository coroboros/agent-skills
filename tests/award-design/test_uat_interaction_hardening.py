"""award-design — the UAT hardening from the PICA literary-journal build.

The user rated a build the review scored ~7.9 at SOTD 2-3: gorgeous type-led hero,
dead body. The failures the reviewers (self + fresh refuter) kept missing:

- the interaction substrate is built HOMEOPATHIC (a ~3% figure scale, no wordmark/accent
  response) or absent, and no single signature carries through the whole scroll — the
  page dies after the hero, again;
- the review reads `:hover` rules in the CSS instead of driving the interaction and
  judging whether it is perceptible — the root of the score inflation;
- ornamental section kickers ("THE CURRENT NUMBER", "SUBSCRIBE") stamped on every h2;
- brand-story copy orphaned in the footer instead of presenting the subject in the body;
- nav stays transparent under the pointer; the figure zoom escapes its frame;
- the scroll text effect is a single-channel fade, not the two-channel accent-settle
  (Terminal Industries) recipe.

This locks all of it into the gate + the palette.
"""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REFS = REPO_ROOT / "skills" / "award-design" / "references"


def _read(rel):
    return (REFS / rel).read_text(encoding="utf-8").lower()


class TestPerceptibleSubstrate(unittest.TestCase):
    def test_low_amplitude_not_imperceptible(self):
        isig = _read("interaction-signatures.md")
        self.assertIn("low amplitude is not imperceptible", isig)

    def test_figure_hover_perceptible(self):
        isig = _read("interaction-signatures.md")
        self.assertIn("perceptible contained zoom", isig)
        self.assertIn("escape its frame", isig)

    def test_minimalist_perceptible_not_invisible(self):
        isig = _read("interaction-signatures.md")
        self.assertIn("quiet is the tempo, not the invisibility", isig)

    def test_substrate_measured_and_routed_to_r2(self):
        # the perceptibility floor is the detector's job now; the gate routes
        # its homeopathic findings to R2 instead of carrying its own box
        self.assertIn("perceptibility floors", _read("detector.md"))
        self.assertIn("homeopathic responses", _read("preflight.md"))


class TestCarriedSignature(unittest.TestCase):
    def test_signature_must_carry(self):
        isig = _read("interaction-signatures.md")
        self.assertIn("the signature must carry, not merely recur", isig)

    def test_rubric_one_signature_carries(self):
        ar = _read("audit-rubric.md")
        self.assertIn("**carry:** one signature behaviour recurs and builds "
                      "through the *whole* scroll", ar)


class TestReviewJudgedDriven(unittest.TestCase):
    def test_interaction_judged_driven_not_read(self):
        ar = _read("audit-rubric.md")
        self.assertIn("the interaction layer is judged driven, not read", ar)


class TestWordmark(unittest.TestCase):
    def test_wordmark_secondary_cut(self):
        isig = _read("interaction-signatures.md")
        self.assertIn("beside the nav wordmark: cut", isig)


class TestNavSurfaceOnHover(unittest.TestCase):
    def test_nav_bg_on_hover_default(self):
        nav = _read("navigation-patterns.md")
        self.assertIn("surface on hover — legibility-on-demand", nav)
        self.assertIn("takes its solid surface the instant the pointer enters", nav)


class TestTextEffectRecipe(unittest.TestCase):
    def test_craft_lever_two_channels(self):
        te = _read("text-effects.md")
        self.assertIn("the craft lever — two channels, staggered", te)
        self.assertIn("two channels moving together", te)

    def test_sustained_is_sticky_scrub(self):
        te = _read("text-effects.md")
        self.assertIn("scrubbed over a sticky pin", te)


class TestKickerAndFooter(unittest.TestCase):
    def test_default_no_kicker(self):
        self.assertIn("the default is no kicker", _read("anti-patterns.md"))
        self.assertIn("**eyebrows** — default none", _read("preflight.md"))
        self.assertIn("default is no kicker — the section title stands alone", _read("editorial.md"))

    def test_footer_no_story_copy(self):
        self.assertIn("story copy orphaned in the footer", _read("anti-patterns.md"))
        self.assertIn("footer carries no presentation copy", _read("page-anatomy.md"))


if __name__ == "__main__":
    unittest.main()
