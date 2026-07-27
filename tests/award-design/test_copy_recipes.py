"""award-design — the copy-ingredients layer: winner copy decomposed into committable
structure (copy-recipes.md), the category-headline test at review, and the §6 copy floor.

The transverse dossier read 22 winners live and extracted the headline shapes, CTA
families, specificity anchors, and voice mechanics they share. These lock the encoded
layer: the three governing laws verbatim, the contracted section headings, the rubric's
category-headline test, the three §6 boxes, the CLICHE-COPY tag on the clichés box —
and the scanner sync: every BANNED_EXEMPLARS string traces to a quote in
copy-recipes.md, so no scanner constant orphans."""

import importlib.util
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
REFS = SKILL_DIR / "references"
RECIPES = REFS / "copy-recipes.md"

_spec = importlib.util.spec_from_file_location(
    "preflight_scan", SKILL_DIR / "scripts" / "preflight_scan.py")
assert _spec is not None and _spec.loader is not None
scan = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(scan)


def _read(rel):
    return (REFS / rel).read_text(encoding="utf-8").lower()


FORMULA_LAW = ("A voice formula is structural, never lexical — its slots are filled "
               "only from the build's world-lexicon; a formula filled with category "
               "words is a template.")
CALIBRATION_LAW = ("Quoted to calibrate, never to ship — imitate the specificity "
                   "(the named place, the count, the refusal), never the wording.")
LANGUAGE_LAW = ("Copy ships in English unless the brief's exact ask names another "
                "language — one language, chosen once, page-wide; the brief's own "
                "language is never the ask.")

HEADINGS = (
    "# Copy Recipes",
    "## Headline structures by section job",
    "## CTA labels",
    "## The specificity floor",
    "## Voice mechanics and refusals",
    "## Microcopy",
    "## Anti-signals",
)


class TestCopyRecipesStructure(unittest.TestCase):
    def test_contracted_headings_present(self):
        raw = RECIPES.read_text(encoding="utf-8")
        for heading in HEADINGS:
            with self.subTest(heading=heading):
                self.assertRegex(raw, rf"(?m)^{re.escape(heading)}$")

    def test_both_laws_verbatim_in_intro(self):
        raw = RECIPES.read_text(encoding="utf-8")
        self.assertIn(FORMULA_LAW, raw)
        self.assertIn(CALIBRATION_LAW, raw)

    def test_specificity_floor_states_the_countable_rule(self):
        cr = _read("copy-recipes.md")
        self.assertIn("every headline and subhead carries ≥1 concrete from the "
                      "build's world", cr)
        self.assertIn("category-words-only fails", cr)


class TestCategoryHeadlineTest(unittest.TestCase):
    def test_rubric_reads_hero_beside_winner_strings(self):
        ar = _read("audit-rubric.md")
        self.assertIn("the category-headline test", ar)
        self.assertIn("read beside the archetype's quoted winner strings", ar)
        self.assertIn("`copy-recipes.md`", ar)

    def test_category_headline_is_off_track_not_a_gap(self):
        ar = _read("audit-rubric.md")
        self.assertIn("would sit unchanged on a rival's site", ar)
        self.assertIn("category headline", ar)
        self.assertIn("regenerate at the concept, never filed as a gap", ar)


class TestPreflightCopyFloor(unittest.TestCase):
    def test_specificity_floor_box(self):
        pf = _read("preflight.md")
        self.assertIn("**specificity floor** — every headline and subhead carries "
                      "≥1 concrete from the build's world", pf)

    def test_no_exemplar_reuse_box(self):
        pf = _read("preflight.md")
        self.assertIn("no quoted catalog string ships verbatim", pf)
        self.assertIn("`(scanner: quoted-exemplar)`", pf)

    def test_cliche_box_carries_scanner_tag(self):
        pf = _read("preflight.md")
        self.assertIn("no ai copy clichés (elevate, seamless, unleash, "
                      "next-gen, delve) `(scanner: cliche-copy)`", pf)


class TestLanguageLaw(unittest.TestCase):
    """The HALDANE validation shipped French sentences inside English copy —
    conversation bleed: the model wrote in its working language, not the
    deliverable's. The law: English unless the brief's exact ask names another
    language; one language, page-wide; register devices only."""

    def test_law_verbatim_in_intro(self):
        raw = RECIPES.read_text(encoding="utf-8")
        self.assertIn(LANGUAGE_LAW, raw)

    def test_voice_mechanics_carry_the_bullet(self):
        cr = _read("copy-recipes.md")
        self.assertIn("**language.** english by default", cr)
        self.assertIn("never an inheritance", cr)
        self.assertIn("conversation bleed", cr)
        self.assertIn("`(scanner: copy-lang)`", cr)

    def test_preflight_box(self):
        pf = _read("preflight.md")
        self.assertIn("one copy language, english unless the brief asks — and then total", pf)
        self.assertIn("`(scanner: copy-lang)`", pf)


class TestExemplarSync(unittest.TestCase):
    """BANNED_EXEMPLARS bans only what copy-recipes.md quotes — a banned string
    with no quote behind it is an orphaned constant, and a quote pool below 12
    is too thin to police exemplar reuse."""

    def test_every_banned_exemplar_is_quoted_in_the_recipes(self):
        raw = RECIPES.read_text(encoding="utf-8")
        for exemplar in scan.BANNED_EXEMPLARS:
            with self.subTest(exemplar=exemplar):
                self.assertIn(exemplar, raw,
                              f"BANNED_EXEMPLARS entry not quoted in copy-recipes.md: {exemplar}")

    def test_exemplar_pool_size(self):
        self.assertGreaterEqual(len(scan.BANNED_EXEMPLARS), 12)
        self.assertLessEqual(len(scan.BANNED_EXEMPLARS), 20)


if __name__ == "__main__":
    unittest.main()
