"""award-design pre-flight scanner — the deterministic half of the Phase 5 gate.

The scanner exists so the countable anti-slop tells are machine-checked instead
of self-attested. These tests pin four contracts: a dirty build trips every
wired rule, a clean build exits 0 with zero findings, a zero-file scan exits 2
instead of printing a perfect summary, and the rule IDs stay in lockstep
between the script and the preflight.md checklist (drift there orphans either
the box or the rule)."""

import contextlib
import importlib.util
import io
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
SCRIPT = SKILL_DIR / "scripts" / "preflight_scan.py"
PREFLIGHT_MD = SKILL_DIR / "references" / "preflight.md"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "preflight"

_spec = importlib.util.spec_from_file_location("preflight_scan", SCRIPT)
assert _spec is not None and _spec.loader is not None
scan = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(scan)


def _run_main(argv):
    """main() prints its report; swallow it so the suite output stays clean."""
    with contextlib.redirect_stdout(io.StringIO()):
        return scan.main(argv)

# Rules emitted outside the LINE_RULES loop (project-level + density-gated).
PROJECT_RULES = scan.PROJECT_RULE_IDS


def _rule_ids(findings):
    return {f.rule_id for f in findings}


class TestDirtyFixtureTripsEveryRule(unittest.TestCase):
    """The dirty fixture embeds one instance of every wired tell. A rule that
    stops firing here has silently died — the fixture is the regression net."""

    @classmethod
    def setUpClass(cls):
        cls.findings, cls.suppressed = scan.scan_paths([str(FIXTURES / "dirty")])
        cls.ids = _rule_ids(cls.findings)

    def test_every_line_rule_fires(self):
        for rule in scan.LINE_RULES:
            rule_id = rule[0]
            with self.subTest(rule=rule_id):
                self.assertIn(rule_id, self.ids, f"rule {rule_id} did not fire on the dirty fixture")

    def test_every_project_rule_fires(self):
        for rule_id in PROJECT_RULES:
            with self.subTest(rule=rule_id):
                self.assertIn(rule_id, self.ids, f"project rule {rule_id} did not fire")

    def test_fail_findings_present_and_exit_code_1(self):
        self.assertTrue(any(f.severity == scan.FAIL for f in self.findings))
        self.assertEqual(_run_main([str(FIXTURES / "dirty")]), 1)

    def test_findings_carry_file_line_locations(self):
        located = [f for f in self.findings if ":" in f.location and f.location != "project"]
        self.assertTrue(located, "line findings must carry file:line locations")
        for finding in located[:5]:
            self.assertRegex(finding.location, r".+:\d+$")


class TestCleanFixturePasses(unittest.TestCase):
    """The clean fixture is a small but honest page (main landmark, one h1,
    alt text, focus-visible, reduced-motion guard, off-black/off-white). Any
    finding here is a false positive worth fixing in the rule, not the page."""

    def test_zero_findings_and_exit_code_0(self):
        findings, _ = scan.scan_paths([str(FIXTURES / "clean")])
        self.assertEqual([], [(f.rule_id, f.location, f.excerpt) for f in findings])
        self.assertEqual(_run_main([str(FIXTURES / "clean")]), 0)


class TestSuppressions(unittest.TestCase):
    """--archetype and --allow are the override paths; both must actually
    suppress, and both must be visible in the suppression notes so the verdict
    can cite them."""

    def test_editorial_archetype_suppresses_emdash_only(self):
        findings, notes = scan.scan_paths([str(FIXTURES / "dirty")], archetype="editorial")
        self.assertNotIn("EMDASH", _rule_ids(findings))
        self.assertIn("AI-PURPLE", _rule_ids(findings), "other rules must keep firing")
        self.assertTrue(any("EMDASH" in note for note in notes))

    def test_corporate_luxury_suppresses_emdash(self):
        findings, _ = scan.scan_paths([str(FIXTURES / "dirty")], archetype="corporate-luxury")
        self.assertNotIn("EMDASH", _rule_ids(findings))

    def test_brutalist_suppresses_meta_label_only(self):
        """ASCII process flags are declared Brutalist grammar — META-LABEL is
        suppressed there, but the palette and structure rules keep firing."""
        findings, notes = scan.scan_paths([str(FIXTURES / "dirty")], archetype="brutalist")
        ids = _rule_ids(findings)
        self.assertNotIn("META-LABEL", ids)
        self.assertIn("EMDASH", ids, "brutalist does not suppress EMDASH")
        self.assertIn("AI-PURPLE", ids)
        self.assertTrue(any("META-LABEL" in note for note in notes))

    def test_pure_bw_ignores_alpha_variants(self):
        """`bg-white/5` is a translucent glass layer, not a pure surface —
        the PURE-BW tailwind pattern must skip alpha-suffixed utilities."""
        import tempfile
        html = ('<!doctype html><html><body><main><h1>Glass</h1>'
                '<div class="bg-white/5 border-white/10">panel</div>'
                '<p>' + " ".join(f"w{i}" for i in range(40)) + '</p>'
                '</main></body></html>')
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "index.html").write_text(html, encoding="utf-8")
            findings, _ = scan.scan_paths([tmp])
        self.assertNotIn("PURE-BW", _rule_ids(findings))

    def test_allow_suppresses_named_rule(self):
        findings, notes = scan.scan_paths([str(FIXTURES / "dirty")], allow=["IMG-ALT"])
        self.assertNotIn("IMG-ALT", _rule_ids(findings))
        self.assertTrue(any("IMG-ALT" in note for note in notes))

    def test_outline_none_downgrades_when_focus_visible_exists(self):
        """OUTLINE-NONE is a fail only when the project ships no :focus-visible
        replacement — the clean fixture proves the guard, the dirty one the fail."""
        findings, _ = scan.scan_paths([str(FIXTURES / "dirty")])
        outline = [f for f in findings if f.rule_id == "OUTLINE-NONE"]
        self.assertTrue(outline and all(f.severity == scan.FAIL for f in outline),
                        "dirty fixture has no :focus-visible — OUTLINE-NONE must be FAIL")


class TestEmdashDensitySemantics(unittest.TestCase):
    """EMDASH is a density rule (> ~1 per 100 visible words, min 3 dashes) —
    a page with one or two legitimate dashes must never fail, matching the
    preflight box it feeds."""

    def test_sparse_dashes_below_threshold_do_not_fire(self):
        import tempfile
        body = " ".join(f"word{i}" for i in range(400))
        html = (f"<!doctype html><html><body><main><h1>Ledger — proven</h1>"
                f"<p>{body}</p><p>2019–2024</p></main></body></html>")
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "index.html"
            page.write_text(html, encoding="utf-8")
            findings, _ = scan.scan_paths([tmp])
        self.assertNotIn("EMDASH", _rule_ids(findings),
                         "2 dashes in 400+ words is below the density threshold")

    def test_dense_dashes_fire_with_counts_in_description(self):
        findings, _ = scan.scan_paths([str(FIXTURES / "dirty")])
        emdash = [f for f in findings if f.rule_id == "EMDASH"]
        self.assertTrue(emdash, "dirty fixture is dash-dense — EMDASH must fire")
        self.assertRegex(emdash[0].description, r"\d+ per \d+ visible words",
                         "the finding must cite the computed density")


class TestDesignMdExcluded(unittest.TestCase):
    """DESIGN.md is the spec, not the build — its Don'ts quote banned phrases
    as prohibitions and would never scan clean. The scanner must skip it."""

    def test_design_md_tells_do_not_scan(self):
        import tempfile
        design = ("# DESIGN\n\n## Do's and Don'ts\n\n"
                  "- Never use SECTION 01 meta-labels or 'Scroll to explore' cues.\n"
                  "- Never use h-screen; lorem ipsum never ships; no John Doe.\n")
        page = ('<!doctype html><html><body><main><h1>Real page</h1>'
                '<p>' + " ".join(f"w{i}" for i in range(40)) + '</p>'
                '</main></body></html>')
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "DESIGN.md").write_text(design, encoding="utf-8")
            (Path(tmp) / "index.html").write_text(page, encoding="utf-8")
            findings, _ = scan.scan_paths([tmp])
        self.assertEqual([], [(f.rule_id, f.location) for f in findings],
                         "DESIGN.md prohibition prose must not produce findings")


class TestSpaShellStructuralSkip(unittest.TestCase):
    """H1-COUNT / MAIN-LANDMARK skip near-empty documents — an SPA shell
    (<body><div id=\"root\">) renders its landmarks from JS and must not fail."""

    def test_spa_shell_is_skipped(self):
        import tempfile
        html = ('<!doctype html><html><head><title>App</title></head>'
                '<body><div id="root"></div><script src="/main.js"></script>'
                '</body></html>')
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "index.html"
            page.write_text(html, encoding="utf-8")
            findings, _ = scan.scan_paths([tmp])
        ids = _rule_ids(findings)
        self.assertNotIn("H1-COUNT", ids)
        self.assertNotIn("MAIN-LANDMARK", ids)


class TestZeroFileScan(unittest.TestCase):
    """A scan of a wrong or empty path used to print a perfect summary and
    exit 0 — a typo'd build directory read as a clean build. The inventory
    line and exit code 2 close that hole."""

    def test_empty_dir_exits_2_and_reports_zero_files(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = scan.main([tmp])
        self.assertEqual(code, 2)
        self.assertIn("0 files scanned (0 text / 0 code)", out.getvalue())

    def test_file_count_line_in_normal_output(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            scan.main([str(FIXTURES / "clean")])
        self.assertIn("2 files scanned (1 text / 1 code)", out.getvalue())


class TestStampRule(unittest.TestCase):
    """STAMP is the mechanical half of the §7 rotation-stamp box: a scanned
    stylesheet set where no first line opens with `/* award-design ·` gets one
    project-level REVIEW finding; a stamped set stays silent, and a build with
    no stylesheet at all is out of the rule's reach."""

    def test_missing_stamp_fires_once_as_review(self):
        findings, _ = scan.scan_paths([str(FIXTURES / "dirty")])
        stamp = [f for f in findings if f.rule_id == "STAMP"]
        self.assertEqual(len(stamp), 1, "STAMP emits exactly one project finding")
        self.assertEqual(stamp[0].severity, scan.REVIEW)
        self.assertEqual(stamp[0].location, "project")
        self.assertIn("missing rotation stamp", stamp[0].description)

    def test_stamped_stylesheet_is_silent(self):
        findings, _ = scan.scan_paths([str(FIXTURES / "clean")])
        self.assertNotIn("STAMP", _rule_ids(findings))

    def test_zero_css_files_skip_the_rule(self):
        import tempfile
        html = ('<!doctype html><html><body><main><h1>Page</h1>'
                '<p>' + " ".join(f"w{i}" for i in range(40)) + '</p>'
                '</main></body></html>')
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "index.html").write_text(html, encoding="utf-8")
            findings, _ = scan.scan_paths([tmp])
        self.assertNotIn("STAMP", _rule_ids(findings))


class TestExtendedRuleForms(unittest.TestCase):
    """Audit-driven regex extensions: PURE-BW beyond hex, META-LABEL beyond
    all-caps. The silent cases are the contract — translucent forms, hyphenated
    tokens, and lowercase running prose must never match (false-negative bias)."""

    @staticmethod
    def _pattern(rule_id):
        return next(rule[3] for rule in scan.LINE_RULES if rule[0] == rule_id)

    def test_pure_bw_extended_forms_match(self):
        pattern = self._pattern("PURE-BW")
        for line in ("color: white;",
                     "border-top: 1px solid black",
                     "background-color: rgb(255, 255, 255);",
                     "background: rgb(0,0,0)",
                     "fill: oklch(1 0 0)",
                     "stroke: oklch(0 0 0)"):
            with self.subTest(line=line):
                self.assertTrue(pattern.search(line), f"extended form escaped: {line}")

    def test_pure_bw_ambiguous_forms_stay_silent(self):
        pattern = self._pattern("PURE-BW")
        for line in ("white-space: nowrap;",
                     "color: whitesmoke;",
                     "border: 1px solid var(--white-soft);",
                     "background: rgb(0 0 0 / 0.4);",
                     "color: oklch(0.98 0 0);"):
            with self.subTest(line=line):
                self.assertFalse(pattern.search(line), f"false positive: {line}")

    def test_meta_label_title_case_caught_lowercase_prose_silent(self):
        pattern = self._pattern("META-LABEL")
        self.assertTrue(pattern.search("Section 01"))
        self.assertTrue(pattern.search("Step 2"))
        self.assertFalse(pattern.search("see section 01 for details"),
                         "lowercase running prose is not a meta-label")

    def test_deadlink_matches_bare_hash_only(self):
        pattern = self._pattern("DEADLINK")
        self.assertTrue(pattern.search('<a href="#">Learn more</a>'))
        self.assertTrue(pattern.search("<a href='#'>Learn more</a>"))
        self.assertFalse(pattern.search('<a href="#work">Work</a>'),
                         "in-page anchors are real targets")


class TestScannerChecklistLockstep(unittest.TestCase):
    """Every `(scanner: RULE-ID)` tag in preflight.md names a real rule, and
    every rule the script ships is reachable from the checklist. One-sided
    drift means a box lies about its mechanical help, or a rule runs with no
    box to feed."""

    @classmethod
    def setUpClass(cls):
        cls.preflight = PREFLIGHT_MD.read_text(encoding="utf-8")
        cls.md_ids = set()
        for tag in re.findall(r"\(scanner:\s*([A-Z0-9-,\s]+)\)", cls.preflight):
            cls.md_ids.update(part.strip() for part in tag.split(","))
        cls.script_ids = scan.known_rule_ids()

    def test_every_checklist_tag_names_a_real_rule(self):
        for rule_id in sorted(self.md_ids):
            with self.subTest(rule=rule_id):
                self.assertIn(rule_id, self.script_ids,
                              f"preflight.md cites unknown scanner rule: {rule_id}")

    def test_every_script_rule_is_reachable_from_the_checklist(self):
        for rule_id in sorted(self.script_ids):
            with self.subTest(rule=rule_id):
                self.assertIn(rule_id, self.md_ids,
                              f"scanner rule {rule_id} has no `(scanner: …)` tag in preflight.md")


if __name__ == "__main__":
    unittest.main()
