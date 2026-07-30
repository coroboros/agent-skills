"""award-design render floor — asset contract and pure-core behavior.

The floor ships as a browser-injected payload, so half its safety properties are
textual: no module syntax on the evaluate_script path, a parseable RULES
registry, one global, and a runtime contract it cannot break (never own a
browser, never resize a viewport, never reach the network). The other half is
arithmetic — a text collision, a clipped glyph, a collapsed box and a CTA under
the fold are all rect comparisons, and every boundary here traces to a P0
measured on a failed reference build, where the builder's own verdict said READY
and an independent assessor said LOSES on the finish.

Severity is the Law-1 boundary and is pinned rule by rule: what can FAIL names
an objectively broken thing; a deferred CTA and a captured console throw are
REVIEW, because taste and runtime noise are not defects.
"""

import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ASSET = REPO_ROOT / "skills" / "award-design" / "assets" / "render-floor.js"

RULE_RE = re.compile(r"\{\s*id:\s*'([^']+)',\s*severity:\s*'([^']+)',\s*box:\s*'([^']+)'\s*\}")
UPPER_KEBAB = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*$")
BOX_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MODULE_SYNTAX = re.compile(r"^(?:import\s|export\s|require\(|(?:const|let|var)\s.*=\s*require\()")
BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.S)
LINE_COMMENT = re.compile(r"^\s*//.*$", re.M)

# Severity per rule is the contract, not a detail: a REVIEW promoted to FAIL
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

TOL_LITERAL = ("const TOL = { overlapPx: 2, overlapRatio: 0.15, overlapAbsW: 24, overlapAbsH: 8, "
               "clipPx: 2, zeroBoxPx: 0.5, foldPx: 1 };")
GATES_LITERAL = "const GATES = { mobileMaxW: 500, desktopMinW: 1024, minHiddenLinks: 2 };"
SWEEP_LITERAL = "const SWEEP = [375, 768, 1024, 1440, 1920];"
FINDING_SHAPE = "return { rule, severity: spec.severity, box: spec.box, selector, measurement, note };"
FOOTER = "Mechanical floor — every finding carries the boxes that prove it. A clean sweep says the type is not broken; it says nothing about the design."

# The harness rung injects, resizes and re-invokes; a payload that opened or
# sized a browser, or fetched anything, would break the one-session economics
# the whole verification stack is built on.
FORBIDDEN_RUNTIME = [
    "window.open", "resizeTo(", "resizeBy(", "puppeteer", "playwright",
    "XMLHttpRequest", "navigator.sendBeacon", "new Worker(",
]


def _rules(source):
    return RULE_RE.findall(source)


def _code(source):
    """Source with comments removed — prose may discuss severities; code may not."""
    return LINE_COMMENT.sub("", BLOCK_COMMENT.sub("", source))


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


class TestRenderFloorAsset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert ASSET.is_file(), f"missing render-floor asset: {ASSET}"
        cls.source = ASSET.read_text(encoding="utf-8")

    def test_size_under_64kb(self):
        self.assertLess(ASSET.stat().st_size, 64 * 1024)

    def test_no_top_level_module_syntax(self):
        """evaluate_script runs the file as a classic script — any top-level
        import/export/require breaks the browser injection path."""
        offenders = [
            f"{i}: {line.rstrip()}"
            for i, line in enumerate(self.source.splitlines(), 1)
            if MODULE_SYNTAX.match(line)
        ]
        self.assertEqual([], offenders)

    def test_rules_registry_shape(self):
        rules = _rules(self.source)
        self.assertTrue(rules, "RULES registry not parseable from the asset")
        for rule_id, severity, box in rules:
            with self.subTest(rule=rule_id):
                self.assertRegex(rule_id, UPPER_KEBAB)
                self.assertIn(severity, {"FAIL", "REVIEW"})
                self.assertRegex(box, BOX_SLUG)

    def test_every_spec_rule_present_at_its_severity(self):
        severities = {rule_id: sev for rule_id, sev, _ in _rules(self.source)}
        for rule_id, expected in EXPECTED_SEVERITY.items():
            with self.subTest(rule=rule_id):
                self.assertEqual(expected, severities.get(rule_id))

    def test_no_rule_outside_the_spec(self):
        """The floor is mechanical: a rule nobody specified is a rule nobody
        can dismiss with a measurement."""
        ids = {rule_id for rule_id, _, _ in _rules(self.source)}
        self.assertEqual(set(EXPECTED_SEVERITY), ids)

    def test_tolerance_and_gate_literals_exact(self):
        """TOL, GATES and SWEEP are the single source of truth for the sweep;
        a silent drift here moves a FAIL boundary nobody reviewed."""
        for literal in (TOL_LITERAL, GATES_LITERAL, SWEEP_LITERAL):
            with self.subTest(literal=literal.split("=")[0].strip()):
                self.assertIn(literal, self.source)

    def test_finding_shape_matches_the_spec(self):
        """rule / severity / selector / measurement / note — a finding without
        its measurement is a guess, and the doctrine dismisses findings only
        against measurements."""
        self.assertIn(FINDING_SHAPE, self.source)

    def test_footer_doctrine_present(self):
        self.assertIn(FOOTER, self.source)

    def test_single_global(self):
        """One window property — counted anywhere in the file, in either syntax.
        A line-anchored dot-form scan misses both `window['__x'] = …` and the
        mid-expression `const g = window.__x = window.__x || {}` that a state bag
        is naturally written as."""
        code = _code(self.source)
        dotted = set(re.findall(r"window\.(\w+)\s*=(?!=)", code))
        self.assertEqual({"awardRenderFloor"}, dotted)
        self.assertEqual([], re.findall(r"window\[[^\]]+\]\s*=(?!=)", code))
        # assigns ONTO the existing object: re-injecting across the width sweep
        # must not drop the armed listeners' buffer
        self.assertIn("Object.assign(window.awardRenderFloor || {}, api, { arm, run })", self.source)

    def test_never_owns_or_resizes_a_browser(self):
        code = _code(self.source)
        offenders = [token for token in FORBIDDEN_RUNTIME if token in code]
        self.assertEqual([], offenders, f"payload reaches outside its contract: {offenders}")

    def test_transitions_die_during_measurement_and_are_restored(self):
        """A rect read mid-transition is a different page every call. The kill
        must also be undone — the payload runs inside a session the judges reuse."""
        self.assertIn("transition: none !important", self.source)
        self.assertIn("kill.restore()", self.source)
        self.assertIn("} finally {", self.source)

    def test_arm_installs_both_error_channels_once(self):
        """A second arm() across the width sweep would double-count every throw."""
        self.assertIn("addEventListener('error'", self.source)
        self.assertIn("addEventListener('unhandledrejection'", self.source)
        self.assertIn("if (s.armed) return", self.source)

    def test_clipped_measures_the_glyph_box_not_the_border_box(self):
        """The canonical cut is a nowrap heading inside a narrower
        overflow:hidden parent: the element's RECT is in bounds and its TYPE is
        not. Measuring the border box misses it entirely, so the ancestor arm
        must run on range client rects."""
        self.assertIn("range.selectNodeContents(el)", self.source)
        self.assertIn("range.getClientRects()", self.source)
        self.assertIn("const ink = textInkRect(el) || rect;", self.source)
        self.assertIn("rectEscape(ink, clip.rect", self.source)

    def test_track_exemption_needs_a_live_scroll_offset(self):
        """overflow:hidden IS a scroll container, so scrollWidth > clientWidth is
        true exactly when the box is cutting content. Using the scroll EXTENT as
        a track exemption suppressed every ordinary clipped card; only a live
        offset proves something drives the box as a track."""
        self.assertIn("scrolledX: Math.abs(node.scrollLeft || 0) > 1", self.source)
        self.assertIn("scrolledY: Math.abs(node.scrollTop || 0) > 1", self.source)
        self.assertNotIn("node.scrollWidth > node.clientWidth", self.source)
        self.assertNotIn("node.scrollHeight > node.clientHeight", self.source)

    def test_only_fixed_subtrees_are_excluded_from_geometry(self):
        """A sticky box at rest is in normal flow. Folding it in with fixed would
        exempt a whole scroll-pinned chapter from the collision pass and hand any
        CTA inside one a free pass on the fold rule."""
        self.assertIn("getComputedStyle(node).position === 'fixed'", self.source)
        self.assertNotIn("p === 'fixed' || p === 'sticky'", self.source)
        # and what was excluded is reported, never silently dropped
        self.assertIn("fixedExcluded", self.source)

    def test_both_scan_caps_are_reported_against_what_they_truncate(self):
        """Comparing survivors to the pre-filter cap reports a truncated sweep as
        a complete one."""
        self.assertIn("out.scanCapped = all.length > MAX_SCAN;", self.source)
        self.assertIn("out.textCapped = out.length >= MAX_TEXT;", self.source)

    def test_default_cta_selector_present(self):
        self.assertIn('a[class*="cta" i], a[class*="btn" i], button[class*="primary" i], [data-cta]',
                      self.source)


class TestRenderFloorHeader(unittest.TestCase):
    """The header is the routing layer: the harness reads it to learn the sweep,
    and the model reads it to learn what a finding means and what it cannot see."""

    @classmethod
    def setUpClass(cls):
        cls.header = BLOCK_COMMENT.search(ASSET.read_text(encoding="utf-8")).group(0)

    def test_names_every_rule(self):
        for rule_id in sorted(EXPECTED_SEVERITY):
            with self.subTest(rule=rule_id):
                self.assertIn(rule_id, self.header)

    def test_states_the_sweep_protocol(self):
        for token in ("arm()", "run()", "375", "768", "1024", "1440", "1920"):
            with self.subTest(token=token):
                self.assertIn(token, self.header)

    def test_states_the_honest_limits(self):
        """Canvas text is pixels and declared truncation is a choice — an
        undocumented blind spot is the one a reviewer trusts by accident."""
        for token in ("canvas", "ellipsis", "getBBox()"):
            with self.subTest(token=token):
                self.assertIn(token, self.header)


@unittest.skipUnless(shutil.which("node"), "node not on PATH")
class TestRenderFloorConstants(unittest.TestCase):
    def test_module_exports(self):
        keys = _node("Object.keys(rf)")
        for name in ("RULES", "TOL", "GATES", "SWEEP", "classifyRectPair", "classifyClip",
                     "rectEscape", "classifyZeroBox", "classifyFold", "classifyMobileNav"):
            self.assertIn(name, keys)

    def test_tolerances(self):
        self.assertEqual(
            {"overlapPx": 2, "overlapRatio": 0.15, "overlapAbsW": 24, "overlapAbsH": 8,
             "clipPx": 2, "zeroBoxPx": 0.5, "foldPx": 1},
            _node("rf.TOL"),
        )

    def test_gates(self):
        self.assertEqual({"mobileMaxW": 500, "desktopMinW": 1024, "minHiddenLinks": 2}, _node("rf.GATES"))

    def test_sweep_widths(self):
        self.assertEqual([375, 768, 1024, 1440, 1920], _node("rf.SWEEP"))


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

    def test_the_dom_answer_comes_from_the_caller_not_a_second_hidden_rule(self):
        """The sweep must route its DOM check through the classifier, or the
        exemption exists in two places and only one of them is tested."""
        source = ASSET.read_text(encoding="utf-8")
        self.assertIn("const related = a.el.contains(b.el) || b.el.contains(a.el);", source)
        self.assertIn("classifyRectPair(a.rect, b.rect, null, related)", source)

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
        """Counting VISIBLE links would clear the shipped defect outright: the
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
