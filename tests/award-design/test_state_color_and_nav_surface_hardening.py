"""award-design — the KINDRED round-3 UAT hardening: state-colour commitment and the
nav-bar surface.

The KINDRED build swept its button fill in --blush (a 74%-lightness wash) while every
link answered in the committed --blush-ink accent, and hardcoded an off-token literal
as the hover text colour; its nav took a derived grey (--ground-2) plus a border-bottom
hairline on hover, over a white page that called for white. These lock the user-imposed
defaults: control state colours are full-strength committed tokens, hover treatments are
distinct per element class, and the nav's solid surface is the page ground or dominant
primary with no border-bottom in any state."""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REFS = REPO_ROOT / "skills" / "award-design" / "references"


def _read(rel):
    return (REFS / rel).read_text(encoding="utf-8").lower()


class TestStateColorCommitment(unittest.TestCase):
    def test_interaction_signatures_rule_exists(self):
        ix = _read("interaction-signatures.md")
        self.assertIn("state colours are committed tokens at full strength", ix)
        self.assertIn("not its paler sibling", ix)
        self.assertIn("the pale hover nobody chose", ix)

    def test_off_token_state_literal_is_drift(self):
        ix = _read("interaction-signatures.md")
        self.assertIn("appears in no token sheet is token drift", ix)

    def test_anti_pattern_entry(self):
        ap = _read("anti-patterns.md")
        self.assertIn("the pale hover nobody chose", ap)
        self.assertIn("never its faded sibling", ap)

    def test_preflight_code_craft_box(self):
        pf = _read("preflight.md")
        self.assertIn("state-colour commitment", pf)
        self.assertIn("never a paler wash", pf)


class TestHoverVarietyAcrossClasses(unittest.TestCase):
    def test_one_vocabulary_distinct_across_classes(self):
        ix = _read("interaction-signatures.md")
        self.assertIn("within a class; distinct across classes", ix)
        self.assertIn("never all answer with one recycled move", ix)


class TestNavSurfaceAndHairline(unittest.TestCase):
    def test_surface_is_ground_or_dominant_primary(self):
        nav = _read("navigation-patterns.md")
        self.assertIn("the page ground (or the dominant primary)", nav)
        self.assertIn("a grey nobody chose", nav)

    def test_bar_never_takes_a_border_bottom(self):
        nav = _read("navigation-patterns.md")
        self.assertIn("the bar hangs no hairline", nav)
        self.assertIn("never takes a `border-bottom`", nav)
        self.assertIn("at rest, on scroll, or on hover", nav)

    def test_hover_surface_snippet_obeys_the_rule(self):
        nav = _read("navigation-patterns.md")
        self.assertIn("never a derived neutral", nav)

    def test_anti_pattern_entry(self):
        ap = _read("anti-patterns.md")
        self.assertIn("`border-bottom` hung under the nav bar", ap)
        self.assertIn("one that appears on hover reads as a glitch", ap)

    def test_preflight_box_covers_nav(self):
        pf = _read("preflight.md")
        self.assertIn("zero `border-bottom` in any state", pf)
        self.assertIn("the page ground or the dominant primary", pf)


if __name__ == "__main__":
    unittest.main()
