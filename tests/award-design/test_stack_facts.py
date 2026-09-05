"""stack-facts.md — the dated single source for every stack claim.

The file exists because the same fact was stated twice and drifted: scroll-driven
support read ~85% in motion-palette.md and ~82% in text-effects.md, and neither
matched the live figure. So these tests pin the *properties that make the file
a single source* — every row dated, every fetch-class layer covered, the ladder
stated, and no other reference restating a number this file owns.

They never assert freshness. `checked: 2026-07` going stale is a real event the
scanner reports (STACK-FACTS-STALE, a REVIEW notice) and a maintainer resolves
with a lookup; a test that failed on the calendar would only teach the next
maintainer to bump the date without doing the lookup, which is the one failure
mode worse than a stale row.
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REFS = REPO_ROOT / "skills" / "award-design" / "references"
STACK_FACTS = REFS / "stack-facts.md"

ROW_RE = re.compile(r"^\|(?!\s*(?:-{2,}|Fact\b))(.+)\|\s*$", re.MULTILINE)
CHECKED_RE = re.compile(r"checked:\s*(\d{4})-(\d{2})(?:-(\d{2}))?")


def _body():
    return STACK_FACTS.read_text(encoding="utf-8")


def _rows():
    """(fact, value, checked, verdict, source) for every data row."""
    out = []
    for match in ROW_RE.finditer(_body()):
        cells = [cell.strip() for cell in match.group(1).split("|")]
        if len(cells) == 5:
            out.append(tuple(cells))
    return out


class TestEveryRowIsDated(unittest.TestCase):
    """A row without a date is a claim without provenance — indistinguishable
    from the memory-quoted numbers the file replaces."""

    @classmethod
    def setUpClass(cls):
        cls.rows = _rows()

    def test_the_table_parses(self):
        self.assertGreaterEqual(len(self.rows), 50,
                                "stack-facts.md should carry the full fact surface (~60 rows)")

    def test_every_row_carries_a_parseable_checked_date(self):
        for fact, _, checked, _, _ in self.rows:
            with self.subTest(fact=fact[:60]):
                match = CHECKED_RE.search(checked)
                self.assertIsNotNone(match, f"row has no parseable checked date: {checked!r}")
                year, month = int(match.group(1)), int(match.group(2))
                self.assertGreaterEqual(year, 2020)
                self.assertTrue(1 <= month <= 12, f"month out of range in {checked!r}")

    def test_every_row_carries_a_verdict_and_a_source(self):
        for fact, _, _, verdict, source in self.rows:
            with self.subTest(fact=fact[:60]):
                self.assertIn(verdict, ("fetch", "trust"),
                              f"verdict must be fetch or trust, got {verdict!r}")
                self.assertTrue(source, "every row names where the value came from")

    def test_no_row_has_an_empty_value(self):
        for fact, value, _, _, _ in self.rows:
            with self.subTest(fact=fact[:60]):
                self.assertTrue(value.strip(), "a row with no value is a row that lies by omission")


class TestTheLadderIsNarrow(unittest.TestCase):
    """fetch-class is the expensive class — every fetch row costs a lookup on
    every refresh. The blueprint's ruling: Three.js, SplitText, and support
    figures are fetch; the rest is trust. A file where everything is fetch has
    no ladder, just a warning."""

    @classmethod
    def setUpClass(cls):
        cls.rows = _rows()
        cls.body = _body()

    def test_the_ladder_rule_is_stated(self):
        self.assertIn("fetch", self.body)
        self.assertIn("trust", self.body)
        self.assertRegex(self.body, r"(?i)fetch-class is narrow")

    def test_three_js_rows_are_fetch_class(self):
        three = [row for row in self.rows if "three.js" in row[0].lower()
                 or "webgpu" in row[0].lower()]
        self.assertTrue(three, "stack-facts.md must carry the Three.js / WebGPU rows")
        for row in three:
            with self.subTest(fact=row[0]):
                self.assertEqual(row[3], "fetch", "the fastest-churning layer is fetch-class")

    def test_splittext_rows_are_fetch_class(self):
        split = [row for row in self.rows if "splittext" in row[0].lower()]
        self.assertTrue(split, "stack-facts.md must carry the SplitText rows")
        for row in split:
            with self.subTest(fact=row[0]):
                self.assertEqual(row[3], "fetch")

    def test_baseline_tier_rows_are_fetch_class(self):
        """A Baseline tier is bolded in the value column — matched on that, so
        a prose row merely containing the word (the stretch-vs-official
        warning) or an unrelated percentage (AVIF's size saving) is not
        mistaken for a status row."""
        tiers = [row for row in self.rows
                 if re.search(r"\*\*(?:Widely|Newly|Limited|Experimental)", row[1])]
        self.assertGreaterEqual(len(tiers), 10, "the Baseline ladder must be covered")
        for row in tiers:
            with self.subTest(fact=row[0][:60]):
                self.assertEqual(row[3], "fetch", "a Baseline tier is only true on its check date")

    def test_support_figure_rows_are_fetch_class(self):
        support = [row for row in self.rows if "support" in row[0].lower()]
        self.assertTrue(support, "the global-support figure must be a row of its own")
        for row in support:
            with self.subTest(fact=row[0][:60]):
                self.assertEqual(row[3], "fetch", "a support figure is only true on its check date")

    def test_stable_shapes_stay_trust_class(self):
        trust = [row for row in self.rows if row[3] == "trust"]
        self.assertGreaterEqual(len(trust), 15,
                                "a file where everything is fetch-class has no ladder")


class TestTheFactSurfaceIsCovered(unittest.TestCase):
    """Every layer a reference is allowed to cite has a row here — otherwise
    that reference has no choice but to quote memory."""

    LAYERS = ("GSAP", "SplitText", "Lenis", "Three.js", "animation-timeline",
              "View Transitions", "content-visibility", "Relative colour",
              "Container queries", "Core Web Vitals", "TanStack Start")

    def test_each_named_layer_has_a_row(self):
        body = _body()
        for layer in self.LAYERS:
            with self.subTest(layer=layer):
                self.assertIn(layer, body, f"stack-facts.md must own the {layer} fact")

    def test_the_conflicting_support_figures_are_resolved(self):
        """motion-palette.md said ~85%, text-effects.md said ~82%, and the live
        figure was neither. One number lives here now; the other two are gone."""
        body = _body()
        self.assertIn("83.66%", body, "the verified figure must be the one stated")
        for dead in ("~85% support", "~82% global"):
            with self.subTest(dead=dead):
                self.assertNotIn(dead, body)

    def test_the_stale_webgpu_floor_is_corrected(self):
        """foundations.md carried `Three.js r171+` for the WebGPU path; the real
        entry point and async init landed in r167."""
        rows = [row for row in _rows() if "minimum revision" in row[0].lower()]
        self.assertTrue(rows, "the WebGPU minimum-revision row must exist")
        self.assertIn("r167", rows[0][1])

    def test_the_deprecated_lenis_package_is_named(self):
        self.assertIn("@studio-freight/lenis", _body(),
                      "the stale package name must be named as stale, not silently dropped")


class TestNoOtherReferenceRestatesAFact(unittest.TestCase):
    """The point of a single source is that nothing else states the number.
    These are the exact drifts that motivated the file."""

    @classmethod
    def setUpClass(cls):
        # Keyed by path relative to references/, never by basename: the archetype
        # tier-1 files share names with the top-level references, so a name-keyed
        # map silently drops one of each pair — and it drops exactly the files
        # most likely to restate a Three.js revision.
        cls.others = {str(path.relative_to(REFS)): path.read_text(encoding="utf-8")
                      for path in REFS.rglob("*.md") if path.name != "stack-facts.md"}

    def test_scroll_driven_support_percentages_live_only_here(self):
        for name, body in self.others.items():
            with self.subTest(reference=name):
                self.assertIsNone(
                    re.search(r"~\s*8[0-9]%\s*(?:global|support)", body),
                    f"{name} restates a scroll-driven support figure — point it at stack-facts.md")

    def test_the_webgpu_revision_claim_lives_only_here(self):
        """Scoped to the whole reference tree, not to the files the split
        happened to edit — a check that only looks where the author worked
        confirms the edit instead of testing the invariant."""
        for name, body in self.others.items():
            with self.subTest(reference=name):
                self.assertIsNone(re.search(r"\br1\d{2}\+", body),
                                  f"{name} states a Three.js revision — that fact is stack-facts.md's")

    def test_the_technique_references_point_here(self):
        for name in ("foundations.md", "motion-palette.md", "text-effects.md", "skeletons.md"):
            with self.subTest(reference=name):
                self.assertIn("stack-facts.md", self.others[name],
                              f"{name} must route its stack claims to the single source")


if __name__ == "__main__":
    unittest.main()
