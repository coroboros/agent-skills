"""award-design v2 round 2 — section forms + the composition floors.

Forms are the layout-ownership answer to the round-2 defect classes (crowded
data-strips, sprawling meta-lines): a form's CSS owns placement, the builder
fills contracted slots. These tests lock the drift surface: manifest ↔ forms/
sync, every contracted slot styled by its stylesheet, the no-JS floor (a form
that hides a slot at rest blacks out content when the script dies), the
layering law on any form enhancer, and the Phase 4/preflight/audit wiring that
makes the floors and the placement pass binding rather than decorative."""

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
COMPONENTS = SKILL_DIR / "assets" / "components"
FORMS = COMPONENTS / "forms"
MANIFEST = COMPONENTS / "manifest.json"


def _forms():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))["forms"]


class TestFormsManifestSync(unittest.TestCase):
    def test_manifest_and_directory_agree(self):
        on_disk = {p.name for p in FORMS.glob("*.css")}
        in_manifest = {f["css"].split("/")[-1] for f in _forms()}
        self.assertEqual(on_disk, in_manifest)

    def test_every_form_has_required_fields(self):
        for f in _forms():
            for field in ("id", "css", "winner", "archetypes", "tokens",
                          "slots", "variants", "pairs", "whenToUse"):
                with self.subTest(form=f.get("id"), field=field):
                    self.assertIn(field, f)

    def test_every_form_has_a_required_slot(self):
        for f in _forms():
            with self.subTest(form=f["id"]):
                self.assertTrue(any(s["required"] for s in f["slots"]))


class TestFormStylesheets(unittest.TestCase):
    def test_every_contracted_slot_is_styled(self):
        """A slot the manifest promises but the CSS never places is a contract
        the builder cannot rely on."""
        for f in _forms():
            css = (COMPONENTS / f["css"]).read_text(encoding="utf-8")
            for slot in f["slots"]:
                with self.subTest(form=f["id"], slot=slot["name"]):
                    self.assertIn(f'[data-slot="{slot["name"]}"]', css)

    def test_declared_tokens_are_read(self):
        for f in _forms():
            css = (COMPONENTS / f["css"]).read_text(encoding="utf-8")
            for token in f["tokens"]:
                with self.subTest(form=f["id"], token=token):
                    self.assertIn(token, css)

    def test_form_root_selector_present(self):
        for f in _forms():
            css = (COMPONENTS / f["css"]).read_text(encoding="utf-8")
            with self.subTest(form=f["id"]):
                self.assertIn(f'[data-ad-form="{f["id"]}"]', css)

    def test_no_js_floor_no_hidden_slots(self):
        """Forms are plain linked stylesheets precisely so a dead script keeps
        the layout — a form that hides content at rest reintroduces the
        blackout the packaging was chosen to prevent."""
        for f in _forms():
            css = (COMPONENTS / f["css"]).read_text(encoding="utf-8")
            with self.subTest(form=f["id"]):
                self.assertNotRegex(css, r"display:\s*none")
                self.assertNotRegex(css, r"visibility:\s*hidden")
                self.assertNotRegex(css, r"opacity:\s*0(?![.\d])")

    def test_forms_ship_zero_motion(self):
        """Character comes from paired interaction components; a form that
        animates has crossed the layering law."""
        for f in _forms():
            css = (COMPONENTS / f["css"]).read_text(encoding="utf-8")
            with self.subTest(form=f["id"]):
                self.assertNotIn("@keyframes", css)
                self.assertNotRegex(css, r"\banimation\s*:")

    def test_doc_comment_header(self):
        for f in _forms():
            css = (COMPONENTS / f["css"]).read_text(encoding="utf-8")
            with self.subTest(form=f["id"]):
                self.assertTrue(css.lstrip().startswith("/*"))


class TestLayeringLaw(unittest.TestCase):
    def test_form_enhancers_never_restructure_slot_dom(self):
        """A form's JS may toggle classes on the slot element itself; inner-DOM
        surgery is the exclusive right of interaction components. No enhancers
        exist yet — the test binds the contract for the first one that does."""
        for js in FORMS.glob("*.js"):
            src = js.read_text(encoding="utf-8")
            with self.subTest(file=js.name):
                self.assertNotRegex(src, r"\binnerHTML\s*=")
                self.assertNotRegex(src, r"\binsertAdjacentHTML\b")


RECIPES = COMPONENTS / "recipes.json"
KNOWN_ARCHETYPES = {"editorial-dark", "minimalist", "corporate-luxury", "immersive",
                    "bento", "brutalist", "spatial-organic", "bold-maximal", "experimental"}


class TestRecipes(unittest.TestCase):
    """Recipes are the layer between the palette and a deterministic page —
    a winner's ordered section chain the model picks and fills. Lock the data's
    integrity: the pairs vocabulary must reference real components, and a recipe
    with two climaxes (or a fabricated archetype) is corrupted composition data."""

    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(RECIPES.read_text(encoding="utf-8"))
        cls.recipes = cls.data["recipes"]
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.component_ids = {c["id"] for c in manifest["components"]}

    def test_ids_unique(self):
        ids = [r["id"] for r in self.recipes]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_archetype_has_recipes(self):
        covered = {r["archetype"] for r in self.recipes}
        self.assertEqual(covered, KNOWN_ARCHETYPES)

    def test_recipe_shape(self):
        for r in self.recipes:
            with self.subTest(recipe=r["id"]):
                for field in ("archetype", "winner", "macrostructure", "sections",
                              "footer", "loader", "paceNotes", "whenToUse"):
                    self.assertIn(field, r)
                self.assertGreaterEqual(len(r["sections"]), 2)

    def test_at_most_one_climax(self):
        for r in self.recipes:
            with self.subTest(recipe=r["id"]):
                self.assertLessEqual(
                    sum(1 for s in r["sections"] if s.get("climax")), 1)

    def test_sections_carry_intensity(self):
        for r in self.recipes:
            for s in r["sections"]:
                with self.subTest(recipe=r["id"], role=s["role"]):
                    self.assertIn("intensity", s)
                    self.assertTrue(1 <= s["intensity"] <= 10)

    def test_pairs_reference_real_components(self):
        for r in self.recipes:
            for s in r["sections"]:
                for slot, val in s.get("pairs", {}).items():
                    vals = val if isinstance(val, list) else [val]
                    for v in vals:
                        with self.subTest(recipe=r["id"], slot=slot, component=v):
                            self.assertIn(v, self.component_ids)

    def test_skill_wires_recipes(self):
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("assets/components/recipes.json", skill)
        self.assertIn("Pick the recipe, then diverge inside it", skill)
        self.assertIn("never re-sequences a winner's ordering to taste", skill)


class TestCompositionFloorsWiring(unittest.TestCase):
    """The floors are inert unless the phases carry them — pin the phrases."""

    def setUp(self):
        self.skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.preflight = (SKILL_DIR / "references" / "preflight.md").read_text(encoding="utf-8")
        self.rubric = (SKILL_DIR / "references" / "audit-rubric.md").read_text(encoding="utf-8")

    def test_phase4_forms_grammar(self):
        self.assertIn("Section layout composes the same way", self.skill)
        self.assertIn("an undeclared freeform section is drift", self.skill)

    def test_phase4_coverage_floor(self):
        self.assertIn("The coverage floor binds here, not at review", self.skill)

    def test_phase4_text_effect_and_spectacle(self):
        self.assertIn("≥1 named text effect", self.skill)
        self.assertIn("exactly one spectacle moment", self.skill)
        self.assertIn("never a restraint choice", self.skill)

    def test_phase4_non_contradiction(self):
        self.assertIn("Restraint and the floors never trade", self.skill)

    def test_preflight_countable_boxes(self):
        for name in ("**Text-effect commit**", "**Spectacle commit**",
                     "**Media-response coverage**", "**Form-slot integrity**"):
            with self.subTest(box=name):
                self.assertIn(name, self.preflight)

    def test_preflight_placement_pass_box(self):
        self.assertIn("**Placement pass — one placement row per standard capture**", self.preflight)
        self.assertIn("placement rows <n>/<captures>", self.preflight)

    def test_rubric_placement_pass(self):
        self.assertIn("**The placement pass — composition is judged in stills, beside the exemplar.**", self.rubric)
        for defect in ("**crowding**", "**baseline misalignment**", "**stretched meta-line**",
                       "**orphan label**", "**text-over-image contrast**", "**dead-zone / sprawl**"):
            with self.subTest(defect=defect):
                self.assertIn(defect, self.rubric)
        self.assertIn("regenerates its own placement ledger", self.rubric)
        self.assertIn("the verdict is comparative or it is nothing", self.rubric)


if __name__ == "__main__":
    unittest.main()
