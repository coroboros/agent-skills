"""award-design — the round-5 UAT hardening: the in-place icon-only nav toggle, the
keyboard-only custom focus ring, and the special-state native-cursor ban.

The user's UAT across builds: hamburger shipping with a visible "MENU" word (then a
cross with "CLOSE"), the close appearing far from the point the hamburger was clicked,
native focus outlines flashing on mouse click, unstyled input focus, and native
zoom/wait/blocked cursors. These lock the imposed defaults: icon-only toggle morphing
in place under the pointer, focus styling on `:focus-visible` only (inputs in the
committed accent), and the whole special-state cursor family designed, never native."""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REFS = REPO_ROOT / "skills" / "award-design" / "references"


def _read(rel):
    return (REFS / rel).read_text(encoding="utf-8").lower()


class TestInPlaceIconOnlyToggle(unittest.TestCase):
    def test_navigation_law(self):
        nav = _read("navigation-patterns.md")
        self.assertIn("the toggle is icon-only", nav)
        self.assertIn("the close lands under the pointer that opened it", nav)
        self.assertIn("same button, morphed or swapped in place", nav)
        self.assertIn("the second click must land on the cross", nav)

    def test_anti_pattern_entry(self):
        ap = _read("anti-patterns.md")
        self.assertIn('"menu" or "close" text beside the nav toggle icon', ap)
        self.assertIn("teleporting-close", ap)

    def test_preflight_box(self):
        pf = _read("preflight.md")
        self.assertIn("icon-only hamburger", pf)
        self.assertIn("the exact point of the hamburger", pf)


class TestKeyboardOnlyCustomFocus(unittest.TestCase):
    def test_preflight_focus_box(self):
        pf = _read("preflight.md")
        self.assertIn("a mouse click or tap never shows an outline", pf)
        self.assertIn("designed focus state in the committed accent", pf)

    def test_anti_pattern_entry(self):
        ap = _read("anti-patterns.md")
        self.assertIn("the native focus ring left on mouse click", ap)

    def test_code_review_lint(self):
        cr = _read("code-review.md")
        self.assertIn("no `:focus` outline that fires on mouse click", cr)


class TestWordmarkHomeBehavior(unittest.TestCase):
    def test_navigation_law(self):
        nav = _read("navigation-patterns.md")
        self.assertIn("the wordmark is the home affordance", nav)
        self.assertIn("never an `href=\"#top\"` anchor", nav)
        self.assertIn("already at the top of the homepage → reload the page", nav)

    def test_anti_pattern_entry(self):
        ap = _read("anti-patterns.md")
        self.assertIn("the unfinished-anchor tell", ap)

    def test_preflight_box(self):
        pf = _read("preflight.md")
        self.assertIn("wordmark home behavior", pf)
        self.assertIn("no `#fragment` appearing in the url", pf)


class TestSpecialCursorFamilyBan(unittest.TestCase):
    def test_code_review_covers_the_family(self):
        cr = _read("code-review.md")
        self.assertIn("the ban covers the whole special-state family", cr)
        self.assertIn("`zoom-in`/`zoom-out`", cr)

    def test_anti_pattern_entry(self):
        ap = _read("anti-patterns.md")
        self.assertIn("any special-state native cursor as an affordance", ap)
        self.assertIn("system `default`/`pointer`/`text` stay legitimate", ap)

    def test_preflight_lint_box(self):
        pf = _read("preflight.md")
        self.assertIn("any special-state native cursor", pf)


if __name__ == "__main__":
    unittest.main()
