"""Render-floor collision, clipping, and responsive navigation boundaries."""

import json
import shutil
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ASSET = REPO_ROOT / "skills" / "award-design" / "assets" / "render-floor.js"

# Severity per rule is the contract: a REVIEW promoted to FAIL
# turns a legal archetype choice into a blocker, and a FAIL demoted to REVIEW
# lets broken type ship.
EXPECTED_SEVERITY = {
    "TEXT-OVERLAP": "FAIL",
    "TEXT-CLIPPED": "FAIL",
    "ZERO-BOX-CONTENT": "FAIL",
    "CTA-FOLD": "REVIEW",
    "MOBILE-NAV-MISSING": "FAIL",
    "H-OVERFLOW": "FAIL",
    "CONSOLE-ERROR": "REVIEW",
}

def _node(expr):
    """Evaluate one expression against the required asset; fail loud on stderr."""
    script = (
        f"const rf = require({json.dumps(str(ASSET))});"
        f"console.log(JSON.stringify(({expr})));"
    )
    proc = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=30)
    if proc.returncode != 0:
        raise AssertionError(f"node -e failed:\n{proc.stderr}")
    return json.loads(proc.stdout.strip())


@unittest.skipUnless(shutil.which("node"), "node not on PATH")
class TestFindingSeverity(unittest.TestCase):
    def test_defects_fail_while_cta_placement_and_console_noise_require_review(self):
        rules = _node("rf.RULES")
        severities = {rule["id"]: rule["severity"] for rule in rules}
        self.assertEqual(len(severities), len(rules), "rule IDs must be unique")
        for rule_id, expected in EXPECTED_SEVERITY.items():
            with self.subTest(rule=rule_id):
                self.assertEqual(expected, severities.get(rule_id))


@unittest.skipUnless(shutil.which("node"), "node not on PATH")
class TestTextCollisionGeometry(unittest.TestCase):
    """TEXT-OVERLAP's boundary. The shipped defect was a citation printing on
    top of its own label; the shape to spare is a caption nested inside a panel,
    which every layout produces on purpose."""

    def _pair(self, a, b, dom_related=False):
        return _node(
            f"rf.classifyRectPair({json.dumps(a)}, {json.dumps(b)}, null, {json.dumps(dom_related)})")

    def test_text_printing_over_text_is_an_overlap(self):
        label = {"left": 0, "top": 0, "right": 200, "bottom": 24}
        citation = {"left": 60, "top": 4, "right": 260, "bottom": 28}
        self.assertEqual("OVERLAP", self._pair(label, citation)["verdict"])

    def test_a_span_inside_its_own_paragraph_is_exempt(self):
        """The one legitimate shared box: an element nested inside the element it
        overlaps. Layout produces this on every page that has an inline span."""
        paragraph = {"left": 0, "top": 0, "right": 400, "bottom": 200}
        span = {"left": 20, "top": 20, "right": 200, "bottom": 60}
        self.assertEqual("NESTED", self._pair(paragraph, span, dom_related=True)["verdict"])

    def test_a_citation_inside_an_unrelated_label_box_is_a_collision(self):
        """The regression this rule was narrowed for. Geometry alone used to
        excuse it, and it is the shape the shipped defect took: the citation sat
        wholly inside the label column's box, which is text on text at 100% of
        the smaller box — the most total form of the defect, not an exemption."""
        label_column = {"left": 0, "top": 0, "right": 400, "bottom": 60}
        citation = {"left": 100, "top": 20, "right": 220, "bottom": 40}
        result = self._pair(label_column, citation, dom_related=False)
        self.assertEqual("OVERLAP", result["verdict"])
        self.assertEqual(1, result["ratio"])

    def test_subpixel_touch_is_clear(self):
        a = {"left": 0, "top": 0, "right": 100, "bottom": 20}
        b = {"left": 99, "top": 0, "right": 200, "bottom": 20}
        self.assertEqual("CLEAR", self._pair(a, b)["verdict"])

    def test_corner_nick_under_both_floors_is_a_graze(self):
        """A few px of corner bleed between two large blocks is layout rounding,
        not text on text — it must not spend a FAIL."""
        a = {"left": 0, "top": 0, "right": 300, "bottom": 100}
        b = {"left": 295, "top": 95, "right": 600, "bottom": 200}
        self.assertEqual("GRAZE", self._pair(a, b)["verdict"])

    def test_a_ruined_line_across_two_large_blocks_is_not_excused_by_ratio(self):
        """The absolute floor exists because the ratio alone buys big blocks
        immunity: 700x30px of collision is a destroyed line of type, and against
        two 800x400 blocks that is a ratio of 0.075 — under the relative floor."""
        a = {"left": 0, "top": 0, "right": 800, "bottom": 400}
        b = {"left": 100, "top": 370, "right": 800, "bottom": 770}
        result = self._pair(a, b)
        self.assertEqual("OVERLAP", result["verdict"])
        self.assertLess(result["ratio"], 0.15)

    def test_overlap_reports_the_numbers_that_prove_it(self):
        result = self._pair({"left": 0, "top": 0, "right": 100, "bottom": 40},
                            {"left": 50, "top": 10, "right": 150, "bottom": 50})
        self.assertEqual(50, result["overlapW"])
        self.assertEqual(30, result["overlapH"])
        self.assertAlmostEqual(0.375, result["ratio"], delta=1e-9)


@unittest.skipUnless(shutil.which("node"), "node not on PATH")
class TestClipGeometry(unittest.TestCase):
    """TEXT-CLIPPED's two axes: a box cutting its own text, and a box cut by an
    ancestor. "ΓRANSIENT" and the diagram's lost trailing " m" are both here."""

    def _clip(self, sample):
        return _node(f"rf.classifyClip({json.dumps(sample)})")

    def test_hidden_overflow_cutting_its_own_text_is_clipped(self):
        result = self._clip({"scrollW": 240, "clientW": 180, "scrollH": 20, "clientH": 20,
                             "overflowX": "hidden", "overflowY": "hidden"})
        self.assertEqual("CLIPPED", result["verdict"])
        self.assertEqual("x", result["axis"])
        self.assertEqual(60, result["hiddenX"])

    def test_declared_truncation_is_not_a_defect(self):
        """An ellipsis cuts glyphs on purpose and says so; a hard cut does not."""
        self.assertEqual("DECLARED", self._clip({
            "scrollW": 240, "clientW": 180, "overflowX": "hidden", "overflowY": "hidden",
            "declaredTruncation": True})["verdict"])

    def test_visible_overflow_is_not_a_cut(self):
        self.assertEqual("OK", self._clip({
            "scrollW": 240, "clientW": 180, "overflowX": "visible", "overflowY": "visible"})["verdict"])

    def test_leading_edge_escape_names_its_side(self):
        # the hero strip at 375: the first glyph of every label falls off the left
        rect = {"left": -12, "top": 0, "right": 180, "bottom": 20}
        clip = {"left": 0, "top": 0, "right": 200, "bottom": 20}
        escape = _node(f"rf.rectEscape({json.dumps(rect)}, {json.dumps(clip)})")
        self.assertTrue(escape["clipped"])
        self.assertEqual("left", escape["side"])
        self.assertEqual(12, escape["max"])

    def test_escape_inside_tolerance_is_not_a_finding(self):
        rect = {"left": -1, "top": 0, "right": 199, "bottom": 20}
        clip = {"left": 0, "top": 0, "right": 200, "bottom": 20}
        self.assertFalse(_node(f"rf.rectEscape({json.dumps(rect)}, {json.dumps(clip)})")["clipped"])

    def test_a_track_exemption_applies_per_side_not_per_box(self):
        """A live scroll offset on one axis excuses that axis only. Exempting the
        whole clip box would lose an unreachable cut on the other axis whenever
        the deepest escape happened to be the excused one."""
        rect = {"left": 0, "top": -40, "right": 100, "bottom": 220}
        clip = {"left": 0, "top": 0, "right": 100, "bottom": 200}
        both = _node(f"rf.rectEscape({json.dumps(rect)}, {json.dumps(clip)}, 2, ['top','bottom'])")
        self.assertFalse(both["clipped"])
        other_axis = _node(f"rf.rectEscape({json.dumps(rect)}, {json.dumps(clip)}, 2, ['left','right'])")
        self.assertTrue(other_axis["clipped"])
        self.assertEqual("top", other_axis["side"])


@unittest.skipUnless(shutil.which("node"), "node not on PATH")
class TestZeroBoxAndFoldAndNav(unittest.TestCase):
    def _zero(self, sample):
        return _node(f"rf.classifyZeroBox({json.dumps(sample)})")

    def test_collapsed_dt_is_the_shipped_defect(self):
        # the measured shape: w:0 h:120, text still in the DOM
        self.assertEqual("COLLAPSED", self._zero({"width": 0, "height": 120}))

    def test_screen_reader_only_box_is_not_a_defect(self):
        self.assertEqual("SR-ONLY", self._zero(
            {"width": 0, "height": 0, "clipped": True, "positioned": True}))

    def test_laid_out_box_is_fine(self):
        self.assertEqual("OK", self._zero({"width": 240, "height": 20}))

    def _fold(self, sample):
        return _node(f"rf.classifyFold({json.dumps(sample)})")

    def test_fold_rule_is_desktop_only(self):
        self.assertEqual("SKIP", self._fold({"viewportW": 768, "candidates": 3, "inFold": 0}))

    def test_cta_below_the_fold_is_flagged(self):
        # the measured defect: primary CTA at y=963 under a 900px fold
        self.assertEqual("BELOW", self._fold({"viewportW": 1440, "candidates": 2, "inFold": 0}))

    def test_one_cta_in_the_fold_clears_the_page(self):
        self.assertEqual("OK", self._fold({"viewportW": 1440, "candidates": 3, "inFold": 1}))

    def test_no_cta_candidate_reports_none(self):
        self.assertEqual("NONE", self._fold({"viewportW": 1440, "candidates": 0, "inFold": 0}))

    def _nav(self, sample):
        return _node(f"rf.classifyMobileNav({json.dumps(sample)})")

    def test_hidden_links_with_no_toggle_is_the_unreachable_page(self):
        # .nav__links{display:none} with no drawer — four sections unreachable
        self.assertEqual("MISSING", self._nav({"viewportW": 375, "hiddenNavLinks": 4, "hasToggle": False}))

    def test_a_toggle_is_navigation(self):
        self.assertEqual("TOGGLE", self._nav({"viewportW": 375, "hiddenNavLinks": 4, "hasToggle": True}))

    def test_a_logo_and_a_cta_do_not_cover_a_hidden_menu(self):
        """Counting visible links would clear the shipped defect outright: the
        header still renders a logo anchor and a CTA anchor while the real menu
        is display:none. The proof is the hidden links, not the visible ones."""
        self.assertEqual("MISSING", self._nav(
            {"viewportW": 375, "visibleNavLinks": 2, "hiddenNavLinks": 4, "hasToggle": False}))

    def test_a_header_with_nothing_hidden_is_not_a_defect(self):
        """The mirror of the above: a legitimate one-link header must not FAIL
        just for being short."""
        self.assertEqual("OK", self._nav(
            {"viewportW": 375, "visibleNavLinks": 1, "hiddenNavLinks": 0, "hasToggle": False}))

    def test_rule_is_phone_width_only(self):
        self.assertEqual("SKIP", self._nav({"viewportW": 768, "hiddenNavLinks": 4, "hasToggle": False}))


if __name__ == "__main__":
    unittest.main()
