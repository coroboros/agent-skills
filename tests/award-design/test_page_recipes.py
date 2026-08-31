"""award-design — the winners' page recipes: the generative layer the 6.5 ceiling
was missing. Effect palettes covered element-class interactions; builds still
improvised what winners design deliberately — page shape, hero architecture,
loader handoff, footer moment, copy voice, spectacle. Twelve researchers read the
winner corpus live, twelve fresh-context refuters re-opened every load-bearing
claim (one fabricated quote cut, one skill-encoded belief refuted), and the
surviving recipes landed as a Page recipe section per archetype plus the
cross-archetype page-anatomy catalog whose shape slugs are the committable
macrostructure vocabulary (design_plan + contract)."""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REFS = REPO_ROOT / "skills" / "award-design" / "references"

ARCHETYPES = ("minimalist", "brutalist", "editorial", "bold-maximal",
              "immersive-cinematic", "experimental", "corporate-luxury",
              "bento-card", "spatial-organic")

RECIPE_HEADING = "## page recipe — how this line's winners build the page"
RECIPE_ROWS = ("**anatomy**", "**hero architectures**", "**footer**",
               "**arrival**", "**copy voice**", "**imagery art direction**",
               # the spectacle menu became its own `##` section so tier 2 can load
               # it by heading; the slice below still pins it after the page recipe
               "## spectacle menu", "**anti-signals**")
CALIBRATE_LAW = ("quoted to calibrate, never to ship — imitate the specificity "
                 "(the named place, the count, the refusal), never the wording.")

CATALOG_SLUGS = ("argument-scroll", "maison-scroll", "specimen-tour",
                 "capability-grid", "standfirst-stack", "studio-reel",
                 "gallery-stack", "studio-index", "type-index", "gated-reel",
                 "portrait-procession", "chapter-world", "engine-world")


def _read(rel):
    return (REFS / rel).read_text(encoding="utf-8").lower()


class TestPageRecipeSections(unittest.TestCase):
    def test_every_archetype_carries_the_section(self):
        for a in ARCHETYPES:
            with self.subTest(archetype=a):
                self.assertIn(RECIPE_HEADING, _read(f"{a}.md"))

    def test_every_section_carries_the_rows(self):
        for a in ARCHETYPES:
            body = _read(f"{a}.md")
            recipe = body[body.index(RECIPE_HEADING):]
            for row in RECIPE_ROWS:
                with self.subTest(archetype=a, row=row):
                    self.assertIn(row, recipe)
            self.assertIn("corpus —", recipe)

    def test_copy_voice_opens_with_the_calibrate_law(self):
        for a in ARCHETYPES:
            with self.subTest(archetype=a):
                self.assertIn(CALIBRATE_LAW, _read(f"{a}.md"))

    def test_anatomy_shapes_carry_a_catalog_slug(self):
        # The contract and the design_plan commit macrostructure by catalog name;
        # a local shape name with no slug is uncommittable vocabulary.
        for a in ARCHETYPES:
            body = _read(f"{a}.md")
            recipe = body[body.index(RECIPE_HEADING):]
            anatomy = recipe.split("**hero architectures**")[0]
            hits = [s for s in CATALOG_SLUGS if f"`{s}`" in anatomy]
            with self.subTest(archetype=a):
                self.assertTrue(
                    hits, f"{a} anatomy row names no page-anatomy catalog slug")


class TestPageAnatomyCatalog(unittest.TestCase):
    def test_catalog_sections(self):
        pa = _read("page-anatomy.md")
        for heading in ("## macrostructures — the page shapes winners ship",
                        "## the funnel — section jobs and pacing",
                        "## footers — the last designed moment"):
            with self.subTest(heading=heading):
                self.assertIn(heading, pa)

    def test_every_slug_defined_in_the_catalog(self):
        pa = _read("page-anatomy.md")
        for slug in CATALOG_SLUGS:
            with self.subTest(slug=slug):
                self.assertIn(f"`{slug}`", pa)

    def test_template_footer_anti_signal(self):
        self.assertIn("link-columns-only", _read("page-anatomy.md"))


class TestNewAntiPatternEntries(unittest.TestCase):
    def test_arrival_and_route_and_footer_and_headline_tells(self):
        ap = _read("anti-patterns.md")
        for tell in ("**the unconsidered arrival**", "**the hard route cut**",
                     "**the template footer**", "**the category headline**"):
            with self.subTest(tell=tell):
                self.assertIn(tell, ap)


class TestImageryBrief(unittest.TestCase):
    def test_art_direction_brief_rule(self):
        im = _read("imagery.md")
        self.assertIn("## the art-direction brief", im)
        self.assertIn("the brief comes first; the filter is the fallback", im)


if __name__ == "__main__":
    unittest.main()
