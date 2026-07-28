"""award-design pre-flight scanner — the deterministic half of the Phase 5 gate.

The scanner exists so the countable anti-slop tells are machine-checked instead
of self-attested. These tests pin four contracts: a dirty build trips every
wired rule, a clean build exits 0 with zero findings, a zero-file scan exits 2
instead of printing a perfect summary, and every `(scanner: RULE-ID)` tag in
the preflight.md checklist names a rule the script actually ships (a tag
naming a dead rule lies about its mechanical help)."""

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
    """--archetype is the override path; it must actually suppress, and be
    visible in the suppression notes so the verdict can cite it."""

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


class TestCopyLangRule(unittest.TestCase):
    """COPY-LANG is the mechanical half of the §6 language box: copy ships in
    English unless the brief's exact ask names another language (the HALDANE
    validation shipped French sentences inside English copy — conversation
    bleed). Density-gated per file (≥4 distinct + ≥6 total non-English function
    words in visible text) so a register device ("Maison Lumière"), a
    "Des Moines", or an AUX label never fires — false-negative bias, the box
    holds the judgment."""

    @staticmethod
    def _scan_html(body):
        import tempfile
        html = ('<!doctype html><html><body><main><h1>Page</h1>'
                f'{body}<p>' + " ".join(f"w{i}" for i in range(40)) + '</p>'
                '</main></body></html>')
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "index.html").write_text(html, encoding="utf-8")
            findings, _ = scan.scan_paths([tmp])
        return findings

    def test_french_sentences_fire_as_fail(self):
        findings = self._scan_html(
            "<p>Nous concevons des maisons avec vous — cette lumière est "
            "votre héritage, chez nous les gestes sont déjà très anciens.</p>")
        hits = [f for f in findings if f.rule_id == "COPY-LANG"]
        self.assertTrue(hits, "French body copy must trip COPY-LANG")
        self.assertEqual(hits[0].severity, scan.FAIL)
        self.assertIn("French", hits[0].description)
        self.assertIn("function words", hits[0].excerpt)

    def test_register_devices_and_addresses_stay_silent(self):
        findings = self._scan_html(
            "<p>The Maison Lumière atelier keeps a Des Moines archive and a "
            "pied-à-terre at 13 Rue de la Paix. Maison Lumière endures.</p>")
        self.assertNotIn("COPY-LANG", _rule_ids(findings))

    def test_script_tokens_never_count_as_copy(self):
        findings = self._scan_html(
            "<script>const les = 1, des = 2, avec = 3, vous = 4, nous = 5, "
            "cette = 6, sont = 7;</script>")
        self.assertNotIn("COPY-LANG", _rule_ids(findings))

    def test_non_english_months_fire_without_function_words(self):
        """The HALDANE defect verbatim: French months beside English row
        states, zero function words — the month channel must still catch it."""
        findings = self._scan_html(
            "<li><span>Janvier</span><span>delivered</span></li>"
            "<li><span>Février</span><span>delivered</span></li>"
            "<li><span>Décembre</span><span>spoken for</span></li>")
        hits = [f for f in findings if f.rule_id == "COPY-LANG"]
        self.assertTrue(hits, "non-English month rows must trip COPY-LANG")
        self.assertIn("month names", hits[0].description)
        self.assertIn("janvier", hits[0].excerpt)

    def test_single_foreign_month_stays_silent(self):
        findings = self._scan_html(
            "<p>The Août capsule collection arrives this autumn.</p>")
        self.assertNotIn("COPY-LANG", _rule_ids(findings))


class TestCopyEcho(unittest.TestCase):
    """The ARDEN copy defect: "THE 2026 SEASON" above "Book your season." — a
    cross-block word echo META-LABEL/EYEBROW-DENSITY (pattern/count) cannot see.
    Class-agnostic markup parse, since the skill's own output is vanilla CSS."""

    def _scan_html(self, body):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "page.html"
            f.write_text(f"<!doctype html><html><body>{body}</body></html>", encoding="utf-8")
            findings, _ = scan.scan_paths([str(f)])
        return findings

    def _echoes(self, body):
        return [f for f in self._scan_html(body) if f.rule_id == "COPY-ECHO"]

    def test_arden_kicker_heading_echo_fires(self):
        hits = self._echoes('<span class="k">THE 2026 SEASON</span><h2>Book your season.</h2>')
        self.assertEqual(1, len(hits))
        self.assertIn("season", hits[0].excerpt)

    def test_severity_is_review(self):
        hits = self._echoes('<p class="k">The night vigil</p><h2>A vigil at dusk</h2>')
        self.assertTrue(hits)
        self.assertEqual("REVIEW", hits[0].severity)

    def test_no_shared_word_is_silent(self):
        self.assertEqual([], self._echoes('<span class="k">SELECTED WORK</span><h2>Studio index</h2>'))

    def test_long_preceding_paragraph_is_not_a_kicker(self):
        # a real sentence before a heading is not a kicker — length + punctuation gate
        body = ('<p>This is a full standfirst sentence about the season ahead and it runs long.</p>'
                '<h2>The season opens</h2>')
        self.assertEqual([], self._echoes(body))

    def test_nested_styled_word_stays_part_of_the_heading(self):
        # a styled span inside the heading must not split "season" out of it
        hits = self._echoes('<span class="k">2026 SEASON</span><h2>Book your <em>season</em> now</h2>')
        self.assertEqual(1, len(hits))

    def test_preflight_box_carries_both_pairs_and_exemption(self):
        pf = PREFLIGHT_MD.read_text(encoding="utf-8")
        self.assertIn("kicker+heading", pf)
        self.assertIn("heading+first-line", pf)
        self.assertIn("brand proper nouns exempt", pf)


class TestEyebrowDensityMarkupForms(unittest.TestCase):
    """EYEBROW-DENSITY must count vanilla-CSS eyebrows — `<p class="kicker">` /
    `data-slot="kicker"`, uppercase from plain CSS — not only Tailwind
    `tracking-` utilities. Keying off `tracking-` alone counts zero on every
    vanilla-CSS build, which let a mono-caps kicker stamped over every section
    ship unflagged (the regression the owner flagged on Aubry)."""

    def _rule_ids(self, body):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "page.html"
            f.write_text(f"<!doctype html><html><body>{body}</body></html>", encoding="utf-8")
            findings, _ = scan.scan_paths([str(f)])
        return {fd.rule_id for fd in findings}

    @staticmethod
    def _sections(kicker, n_sections, n_kickers):
        parts = []
        for i in range(n_sections):
            head = kicker if i < n_kickers else ""
            parts.append(f"<section>{head}<h2>Heading {i}</h2><p>Body copy for section {i}.</p></section>")
        return "".join(parts)

    def test_vanilla_css_class_kicker_over_every_section_fires(self):
        body = self._sections('<p class="kicker">The going train</p>', 4, 4)
        self.assertIn("EYEBROW-DENSITY", self._rule_ids(body))

    def test_data_slot_kicker_signature_counts(self):
        body = self._sections('<p data-slot="kicker">The jewels</p>', 4, 4)
        self.assertIn("EYEBROW-DENSITY", self._rule_ids(body))

    def test_rationed_kickers_stay_silent(self):
        # one informative kicker across four sections is within ceil(4/3)=2
        body = self._sections('<p class="kicker">Specification</p>', 4, 1)
        self.assertNotIn("EYEBROW-DENSITY", self._rule_ids(body))

    def test_tailwind_signature_still_counts(self):
        body = self._sections('<span class="uppercase tracking-[0.2em]">Selected work</span>', 4, 4)
        self.assertIn("EYEBROW-DENSITY", self._rule_ids(body))


class TestOpticalCraftFamily(unittest.TestCase):
    """The OPTICAL-* family reads the craft pass back off the stylesheet. Two
    fixtures carry the same page: `optical-dirty` skipped the pass, and
    `optical-clean` made every one of the five decisions. Both are real built
    pages, because the family's precondition is exactly that — a stylesheet
    with no document (or a document with no stylesheet) has no craft pass to
    have skipped, and flagging one would be the scanner guessing.

    Every finding is REVIEW: whether a shared tracking value or an unstyled
    selection is deliberate is the reviewer's call, and a proxy never FAILs
    on a guess."""

    @classmethod
    def setUpClass(cls):
        cls.dirty, _ = scan.scan_paths([str(FIXTURES / "tooling" / "optical-dirty")])
        cls.dirty_ids = _rule_ids(cls.dirty)

    def test_every_optical_rule_fires_on_the_skipped_pass(self):
        for rule_id in sorted(scan.OPTICAL_RULE_IDS):
            with self.subTest(rule=rule_id):
                self.assertIn(rule_id, self.dirty_ids)

    def test_review_only_never_fail(self):
        optical = [f for f in self.dirty if f.rule_id in scan.OPTICAL_RULE_IDS]
        self.assertTrue(all(f.severity == scan.REVIEW for f in optical))

    def test_clean_fixture_is_silent(self):
        findings, _ = scan.scan_paths([str(FIXTURES / "tooling" / "optical-clean")])
        self.assertEqual([], [(f.rule_id, f.excerpt) for f in findings])

    def test_tracking_finding_cites_the_value_and_the_sizes(self):
        hit = [f for f in self.dirty if f.rule_id == "OPTICAL-TRACKING"][0]
        self.assertIn("-0.02em", hit.excerpt, "the shared value must be named")
        self.assertIn("3 display sizes", hit.excerpt)

    def test_tracking_ignores_body_sizes(self):
        """optical-craft's curve says body tracks at 0 — a shared value below
        the heading band is correct, not a skipped pass."""
        css = "\n".join(f".t{i} {{ font-size: {12 + i}px; letter-spacing: 0; }}" for i in range(5))
        self.assertNotIn("OPTICAL-TRACKING", self._ids(css))

    def test_tracking_silent_once_the_curve_moves(self):
        css = ("h1 { font-size: 4rem; letter-spacing: -0.04em; }"
               "h2 { font-size: 2.5rem; letter-spacing: -0.02em; }"
               "h3 { font-size: 32px; letter-spacing: -0.01em; }")
        self.assertNotIn("OPTICAL-TRACKING", self._ids(css))

    def test_shadow_needs_a_hued_ground(self):
        """A pure-black shadow on a genuinely neutral ground is not a
        temperature mismatch — the rule is about light having a colour."""
        neutral = (":root { --surface: #f4f4f4; }"
                   ".card { box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2); }")
        hued = (":root { --surface: oklch(96% 0.03 82); }"
                ".card { box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2); }")
        self.assertNotIn("OPTICAL-SHADOW", self._ids(neutral))
        self.assertIn("OPTICAL-SHADOW", self._ids(hued))

    def test_tabular_needs_a_stat_surface_not_a_stray_numeral(self):
        """A percentage inside a sentence is prose; a named stat slot is a
        column that has to line up."""
        prose = "<p>Ledgerline reads it back at 47.2% less cost.</p>"
        stats = '<dl><dd class="stat">1284</dd></dl>'
        self.assertNotIn("OPTICAL-TABULAR", self._ids("body { color: #222; }", prose))
        self.assertIn("OPTICAL-TABULAR", self._ids("body { color: #222; }", stats))

    def test_astro_style_blocks_count_as_stylesheets(self):
        """Astro is the skill's own default for four archetypes and routinely
        ships every rule in a component <style> block with no .css file — a
        family blind to that is blind on the stack the skill recommends."""
        import tempfile
        words = " ".join(f"w{i}" for i in range(40))
        astro = ("---\nconst x = 1;\n---\n"
                 f"<main><h1>Kiln</h1><p>{words}</p></main>\n"
                 "<style>body { color: #222; }</style>\n")
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "index.astro").write_text(astro, encoding="utf-8")
            findings, _ = scan.scan_paths([tmp])
        self.assertIn("OPTICAL-SELECTION", _rule_ids(findings))

    def test_a_readme_beside_a_stylesheet_is_not_a_page(self):
        """Markdown is in TEXT_EXTS for the copy rules, but a README next to a
        stylesheet is a repo, not a built page — judging its craft would be the
        scanner inventing a surface."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "README.md").write_text(
                "Docs " + " ".join(f"w{i}" for i in range(40)), encoding="utf-8")
            (Path(tmp) / "site.css").write_text("body { color: #222; }", encoding="utf-8")
            findings, _ = scan.scan_paths([tmp])
        self.assertFalse(scan.OPTICAL_RULE_IDS & _rule_ids(findings))

    def test_family_is_silent_without_a_built_page(self):
        """A stylesheet alone, or markup alone, is a fragment — the family
        must not judge a craft pass that has no page to have happened on."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "site.css").write_text("body { color: #222; }", encoding="utf-8")
            findings, _ = scan.scan_paths([tmp])
        self.assertFalse(scan.OPTICAL_RULE_IDS & _rule_ids(findings))

    def test_family_is_registered_for_the_checklist_lockstep(self):
        self.assertLessEqual(scan.OPTICAL_RULE_IDS, scan.known_rule_ids())

    @staticmethod
    def _ids(css, body=None):
        import tempfile
        body = body or "<h1>Heading</h1>"
        page = ("<!doctype html><html><body><main>" + body
                + "<p>" + " ".join(f"w{i}" for i in range(40)) + "</p></main></body></html>")
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "site.css").write_text(css, encoding="utf-8")
            (Path(tmp) / "index.html").write_text(page, encoding="utf-8")
            findings, _ = scan.scan_paths([tmp])
        return _rule_ids(findings)


class TestStackFactsStale(unittest.TestCase):
    """The skill auditing its own dated facts. Scoped to the CLI report rather
    than scan_paths: the freshness of stack-facts.md is not a property of the
    build being scanned, so a clean build never starts reporting a maintenance
    notice it cannot act on."""

    ROW = "| Three.js current release | r185 | checked: {date} | fetch | releases |\n"

    def _findings(self, dates, today):
        import tempfile
        from datetime import date
        text = "".join(self.ROW.format(date=d) for d in dates)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stack-facts.md"
            path.write_text(text, encoding="utf-8")
            return scan.stack_facts_findings(path, date(*today))

    def test_fresh_rows_are_silent(self):
        self.assertEqual([], self._findings(["2026-07", "2026-05"], (2026, 7, 28)))

    def test_a_row_past_the_window_fires_once(self):
        findings = self._findings(["2026-07", "2025-01", "2024-06"], (2026, 7, 28))
        self.assertEqual(1, len(findings), "one notice, however many rows went stale")
        self.assertEqual("STACK-FACTS-STALE", findings[0].rule_id)
        self.assertEqual(scan.REVIEW, findings[0].severity)

    def test_the_notice_cites_the_count_and_the_oldest_row(self):
        finding = self._findings(["2025-01", "2024-06"], (2026, 7, 28))[0]
        self.assertIn("2 stale row(s)", finding.excerpt)
        self.assertIn("2024-06-01", finding.excerpt, "the oldest check date is the one cited")

    def test_the_boundary_is_the_window_not_a_guess(self):
        from datetime import date, timedelta
        today = date(2026, 7, 28)
        edge = today - timedelta(days=scan.STACK_FACTS_MAX_AGE_DAYS)
        past = today - timedelta(days=scan.STACK_FACTS_MAX_AGE_DAYS + 1)
        self.assertEqual([], self._findings([edge.isoformat()], (2026, 7, 28)))
        self.assertEqual(1, len(self._findings([past.isoformat()], (2026, 7, 28))))

    def test_absent_file_is_silent(self):
        """An installed skill may ship without the reference tree — silence,
        never a guessed staleness."""
        self.assertEqual([], scan.stack_facts_findings(Path("/nonexistent/stack-facts.md")))

    def test_the_shipped_file_parses(self):
        """The real reference must be readable by the rule — a table the parser
        cannot see would make the notice permanently, silently unreachable."""
        shipped = SKILL_DIR / "references" / "stack-facts.md"
        dated = scan.STACK_FACTS_CHECKED_RE.findall(shipped.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(dated), 50, "every stack-facts row carries a checked date")

    def test_rule_is_registered(self):
        self.assertIn(scan.STACK_FACTS_RULE_ID, scan.known_rule_ids())


class TestScannerChecklistLockstep(unittest.TestCase):
    """Every `(scanner: RULE-ID)` tag in preflight.md names a real rule — a tag
    naming a dead rule lies about its mechanical help. The reverse does not
    hold: pure defect rules fire without a checklist box, so not every rule
    needs a tag."""

    @classmethod
    def setUpClass(cls):
        cls.preflight = PREFLIGHT_MD.read_text(encoding="utf-8")
        cls.md_ids = set()
        # A tag may carry trailing prose ("EMDASH — suppressed for …"); only
        # the leading comma-separated rule IDs are the citation.
        for tag in re.findall(r"\(scanner:\s*([A-Z][A-Z0-9-]*(?:,\s*[A-Z][A-Z0-9-]*)*)",
                              cls.preflight):
            cls.md_ids.update(part.strip() for part in tag.split(","))
        cls.script_ids = scan.known_rule_ids()

    def test_every_checklist_tag_names_a_real_rule(self):
        self.assertTrue(self.md_ids, "preflight.md carries no scanner tags — extraction broke")
        for rule_id in sorted(self.md_ids):
            with self.subTest(rule=rule_id):
                self.assertIn(rule_id, self.script_ids,
                              f"preflight.md cites unknown scanner rule: {rule_id}")


if __name__ == "__main__":
    unittest.main()
