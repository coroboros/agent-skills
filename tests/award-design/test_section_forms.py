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
        # The read surface is the form's declared files: motion tokens may live
        # in the optional js enhancer (faq-accordion), never unread.
        for f in _forms():
            surface = (COMPONENTS / f["css"]).read_text(encoding="utf-8")
            if f.get("js"):
                surface += (COMPONENTS / f["js"]).read_text(encoding="utf-8")
            for token in f["tokens"]:
                with self.subTest(form=f["id"], token=token):
                    self.assertIn(token, surface)

    def test_form_root_selector_present(self):
        for f in _forms():
            css = (COMPONENTS / f["css"]).read_text(encoding="utf-8")
            with self.subTest(form=f["id"]):
                self.assertIn(f'[data-ad-form="{f["id"]}"]', css)

    def test_no_js_floor_no_hidden_slots(self):
        """Forms are plain linked stylesheets precisely so a dead script keeps
        the layout — a SLOT hidden at rest reintroduces the blackout the
        packaging was chosen to prevent. Sub-parts (a [data-row-thumb] excluded
        by a variant, an index number dropped on mobile) may legitimately hide;
        the slot element itself never does."""
        import re
        for f in _forms():
            css = (COMPONENTS / f["css"]).read_text(encoding="utf-8")
            with self.subTest(form=f["id"]):
                self.assertNotRegex(css, r"visibility:\s*hidden")
                self.assertNotRegex(css, r"opacity:\s*0(?![.\d])")
                for m in re.finditer(r"([^{}]+)\{[^{}]*display:\s*none", css):
                    # the final compound of the selector must not be the slot
                    # itself — a pseudo-element on a slot (::-webkit-scrollbar)
                    # hides chrome, not content
                    last = m.group(1).strip().split(",")[-1].split()[-1]
                    if "::" in last:
                        continue
                    self.assertNotIn("data-slot=", last,
                                     f"{f['id']}: a slot element is hidden: {m.group(1).strip()[:80]}")

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

    def test_footer_is_structured_and_resolves(self):
        """Freeform footers weren't drift — they were forced: the named costumes
        had no files. Every footer is now a structured object under closed-world:
        a real form file, a manifest component, an in-world sign-off, or a declared
        MISSING costume (the BLOCKED-row grammar). Zero free-text footers remain."""
        form_files = {p.name for p in (COMPONENTS / "forms").glob("*.css")}
        for r in self.recipes:
            f = r["footer"]
            with self.subTest(recipe=r["id"]):
                self.assertIsInstance(f, dict, "footer must be a structured object, not free text")
                self.assertIn("note", f)
                if "form" in f:
                    form_id = f["form"]
                    if form_id.startswith("MISSING:"):
                        self.assertRegex(form_id, r"^MISSING:[A-Za-z].*-footer$",
                                         "a MISSING footer names its build order")
                    else:
                        self.assertIn(f"{form_id}.css", form_files,
                                      f"footer form {form_id} has no file")
                elif "component" in f:
                    self.assertIn(f["component"], self.component_ids,
                                  f"footer component {f['component']} is not in the manifest")
                else:
                    self.assertTrue(f.get("inWorld") is True,
                                    "a footer with no form/component must be an in-world sign-off")

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

    def test_skill_carries_the_mobile_commit(self):
        """The R-D research's load-bearing finding: winners let pointer classes
        go DORMANT on touch, and the tap-flash on press-class elements is the
        floor — a hover-only substrate reads dead under hover:none."""
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("The mobile commit", skill)
        self.assertIn("go DORMANT", skill)
        self.assertIn("answer the TAP", skill)
        self.assertIn("an honest dormant state is a winner answer", skill)
        preflight = (SKILL_DIR / "references" / "preflight.md").read_text(encoding="utf-8")
        self.assertIn("the press-class elements answer the TAP", preflight)


PLAYBOOKS = COMPONENTS / "playbooks"


class TestPlaybooks(unittest.TestCase):
    """Playbooks are the decision layer above recipes — each archetype's
    winner-derived algorithm from the R4 adversarial research (researcher →
    refuter → reviser). Lock the data: full archetype coverage, the
    refuter-survived revision stamp, an executable ordered tree, awarded
    corpus entries, and buildable gap orders."""

    @classmethod
    def setUpClass(cls):
        cls.books = {p.stem: json.loads(p.read_text(encoding="utf-8"))
                     for p in PLAYBOOKS.glob("*.json")}

    def test_every_archetype_has_a_playbook(self):
        self.assertEqual(set(self.books), KNOWN_ARCHETYPES)

    def test_playbook_shape(self):
        for name, b in self.books.items():
            with self.subTest(playbook=name):
                for field in ("archetype", "revision", "corpus", "story",
                              "spectacle_model", "algorithm", "section_playbook",
                              "element_states", "mobile_answer", "gaps", "unverified"):
                    self.assertIn(field, b)
                self.assertEqual(b["archetype"], name)

    def test_adversarially_revised(self):
        """Revision 2 is the refuter-survived state — a revision-1 playbook is
        unrefuted research and never ships in the skill."""
        for name, b in self.books.items():
            with self.subTest(playbook=name):
                self.assertGreaterEqual(b["revision"], 2)

    def test_algorithm_is_an_ordered_executable_tree(self):
        for name, b in self.books.items():
            with self.subTest(playbook=name):
                steps = b["algorithm"]
                self.assertGreaterEqual(len(steps), 6)
                self.assertEqual([s["step"] for s in steps],
                                 list(range(1, len(steps) + 1)))
                for s in steps:
                    self.assertTrue(s["decide"] and s["rule"])

    def test_corpus_entries_carry_awards(self):
        for name, b in self.books.items():
            with self.subTest(playbook=name):
                self.assertGreaterEqual(len(b["corpus"]), 4)
            for c in b["corpus"]:
                with self.subTest(playbook=name, site=c.get("site")):
                    self.assertTrue(c["site"] and c["award"])

    def test_spectacle_verdict_recorded(self):
        for name, b in self.books.items():
            with self.subTest(playbook=name):
                self.assertIn(b["spectacle_model"]["one_climax_verdict"],
                              {"SUPPORTED", "REFINED", "REFUTED"})

    def test_spectacle_model_is_diffable(self):
        """The build's spectacle conformance table diffs its shipped beats against
        the model. That diff target must exist and be non-empty for every playbook:
        a hero beat and at least one continuation beat. A model with no beats to
        quote is the gate ARDEN escaped — a hover shipped as the page climax with
        nothing to check it against."""
        for name, b in self.books.items():
            with self.subTest(playbook=name):
                sm = b["spectacle_model"]
                self.assertTrue(sm.get("hero"), "spectacle_model.hero is the hero beat to diff against")
                self.assertIsInstance(sm.get("continuation"), list)
                self.assertGreaterEqual(len(sm["continuation"]), 1,
                                        "continuation carries the beats the build maps its sections onto")

    def test_gaps_are_buildable_orders(self):
        for name, b in self.books.items():
            for g in b["gaps"]:
                with self.subTest(playbook=name, gap=g.get("component")):
                    self.assertTrue(g["component"] and g["mechanic"])
                    self.assertIn("priority", g)

    def test_skill_wires_playbooks(self):
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("assets/components/playbooks/<archetype>.json", skill)

    def test_variation_axes_present(self):
        """CALDERA postmortem: two same-archetype builds shipped isomorphic
        skeletons. R-sameness corpus (21 artifacts, 5 serial studios): the
        skeleton is one legal costume; the device kit + content archetype +
        close rotate — a playbook without the variation clause reads as THE
        skeleton and reproduces the monoculture."""
        for name, b in self.books.items():
            with self.subTest(playbook=name):
                self.assertGreaterEqual(b["revision"], 3)
                v = b.get("variation", "")
                self.assertIn("one legal costume", v)
                self.assertIn("never reused across builds", v)
                self.assertIn("zero winner precedent", v)

    def test_reading_kit_is_a_device_not_dna(self):
        """ARDEN monoculture: the reading kit shipped identical across five
        different-brand builds because every playbook's variation field listed
        "interaction vocabulary" as persisting DNA. The reword scopes it — the
        motion register persists, the named kit is a device that rotates."""
        for name, b in self.books.items():
            with self.subTest(playbook=name):
                v = b.get("variation", "")
                self.assertNotIn("motion register + interaction vocabulary", v,
                                 "the DNA clause must not list the named kit as persisting")
                self.assertIn("device, rotated per build", v)


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
        # the R4 sauce verdict: "exactly one" was refuted (3/6 verified winners
        # run zero peak) — the surviving invariant is the cap plus placement
        self.assertIn("at most one climax", self.skill)
        self.assertIn("never a restraint choice", self.skill)
        self.assertIn("declared archetype-canon citation", self.skill)
        # the MERIDIAN v2 lesson: the cap holds peaks, never vocabulary,
        # and a committed beat is never silently cut in cleanup
        self.assertIn("A committed beat survives to ship", self.skill)

    def test_reading_kit_rotation_axis(self):
        """The monoculture had no named rotation axis. The reading kit joins the
        rotate list, the stamp carries a text: field, and slot_roles is the pick."""
        self.assertIn("· text:<h1-entrance>/<prose-substrate>", self.skill,
                      "the stamp must carry the reading-kit field")
        self.assertIn("the reading kit", self.skill)
        self.assertIn("slot_roles", self.skill)
        ap = (SKILL_DIR / "references" / "anti-patterns.md").read_text(encoding="utf-8")
        self.assertIn("or reading kit", ap)

    def test_spectacle_conformance_gate(self):
        """ARDEN shipped a hover as the page climax and passed: the Spectacle-commit
        box checked the build against its own plan, never against the model. The
        conformance table + trigger law close it."""
        self.assertIn("spectacle conformance table", self.skill)
        self.assertIn("diffs against the playbook's `spectacle_model`", self.skill)
        # the trigger law — a pointer-gated peak is not a climax
        self.assertIn("a pointer-gated peak never fills the climax row", self.skill)
        # preflight consumes it, and the verdict Counts the trigger
        self.assertIn("Conformance:", self.preflight)
        self.assertIn("never a pointer-gated peak", self.preflight)
        self.assertIn("climax trigger <scroll|load|zero-by-canon>", self.preflight)
        self.assertIn("The desktop pointer layer is committed explicitly", self.skill)
        self.assertIn("Optional kicker/eyebrow slots default ABSENT", self.skill)

    def test_phase4_motion_continuity(self):
        """The R4 motion-continuity law: never silent after the hero — the
        signature vocabulary recurs in every section, the footer closes live,
        and reduced-motion is a legitimate static state judged on composition.
        MARE's UAT sharpened it: a live canvas over dead DOM is the same
        failure in costume."""
        self.assertIn("no section goes fully static in the default render, footer included", self.skill)
        self.assertIn("footer closes on the live signature", self.skill)
        self.assertIn("static-frame integrity", self.skill)
        self.assertIn("never discharges the floor alone", self.skill)
        self.assertIn("FELT mid-scroll", self.skill)

    def test_phase4_effect_cohesion(self):
        """MARE's UAT + the effect-grammar adversarial verdict: no numeric
        family cap is evidenced (winners run 2-5, mode 4) — the cap is on
        LINEAGES, exactly one; the primary verb is one full-strength treatment
        repeated verbatim, and the product-UI default hovers are banned as the
        primary."""
        self.assertIn("PICKED from the library's winner-verified palette", self.skill)
        self.assertIn("The cap is on lineages, never on families", self.skill)
        self.assertIn("repeated verbatim on every primary instance", self.skill)
        self.assertIn("legal only on a ghost/tertiary", self.skill)

    def test_phase4_non_contradiction(self):
        self.assertIn("Restraint and the floors never trade", self.skill)

    def test_preflight_countable_boxes(self):
        for name in ("**Text-effect commit**", "**Spectacle commit**",
                     "**Media-response coverage**", "**Form-slot integrity**",
                     "**Motion continuity**", "**Static-frame integrity**",
                     "**Legibility floor**", "**Nav under momentum**",
                     "**Primary-verb consistency**", "**Class-role uniformity**"):
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

    def test_rubric_asset_fidelity_audit(self):
        self.assertIn("**The asset-fidelity audit — measured from files, before any composition verdict.**",
                      self.rubric)
        self.assertIn("source px → shipped px → rendered device px at the asset's worst moment", self.rubric)
        self.assertIn("no capture can clear this row", self.rubric)
        self.assertIn("it never spends fidelity", self.rubric)


class TestImposedVerdicts(unittest.TestCase):
    """CALDERA postmortem: the builder treated corpus verdicts as improvable
    defaults ('I know a better way'). The imposed register converts them to
    non-negotiable rows, each gate-carried, with one narrow written override."""

    @classmethod
    def setUpClass(cls):
        cls.skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.preflight = (SKILL_DIR / "references" / "preflight.md").read_text(encoding="utf-8")
        cls.interactions = (SKILL_DIR / "references" / "interaction-signatures.md").read_text(encoding="utf-8")
        cls.navpat = (SKILL_DIR / "references" / "navigation-patterns.md").read_text(encoding="utf-8")

    def test_register_exists_with_override_protocol(self):
        self.assertIn("### The imposed verdicts — never negotiated", self.skill)
        self.assertIn('OVERRIDE: <verdict> — "<the clause>"', self.skill)
        self.assertIn("No override exists for nav flicker or sub-CSS assets", self.skill)

    def test_verdict_rows_present(self):
        for token in ("dense and moving",
                      "zero hide/show flips under scroll jitter",
                      "sources, never the engine",
                      "One library treatment per role, page-wide",
                      "One motion register page-wide",
                      "Structure is story-native"):
            with self.subTest(verdict=token):
                self.assertIn(token, self.skill)

    def test_story_native_law_in_phase1(self):
        self.assertIn("**Structure is story-native.**", self.skill)
        self.assertIn("story reason", self.skill)
        self.assertIn("never reused across builds — the clearest law in the data", self.skill)

    def test_motion_register_amendment(self):
        # R-imposed live measurement: a SOTD winner runs 9 timing tokens across
        # 4 curve families, all one register — the cap moved from family to register.
        self.assertIn("motion register + accent role", self.preflight)
        self.assertIn("What no winner does is cross registers", self.interactions)
        self.assertIn("all decelerating-mechanical", self.skill)

    def test_nav_winner_norm(self):
        self.assertIn("**The winner norm is not hiding at all.**", self.navpat)
        self.assertIn("zero visible hide/show flips under scroll jitter", self.navpat)

    def test_loophole_closures(self):
        """Red-team round (2026-07-17): a lazy builder defeats prose gates through
        self-defined predicates, self-graded evidence, and escape hatches. Pin the
        closures for the four BREAKS-class findings."""
        # #1/#2 — the Siena route never satisfies the immersive hero; re-scope
        # needs evidence + the user.
        self.assertIn("never the immersive hero-medium verdict", self.skill)
        self.assertIn("the re-scope is not the builder's call", self.skill)
        # #3 — asset numbers carry provenance; the builder cannot narrow the class.
        self.assertIn("a dimension with no provenance is an asserted number", self.preflight)
        self.assertIn("**Signature asset = every full-bleed surface and every scrubbed/zoomed surface**",
                      self.preflight)
        # #5 — the OVERRIDE form is re-adjudicated, not self-satisfied.
        self.assertIn("Every OVERRIDE line is a standing refutation target", self.skill)
        # #4 — probe order is fixed; a chosen-to-fail probe is the escape, not a gap.
        self.assertIn("ToolSearch for the browser MCP is the mandatory first probe", self.preflight)
        # #6 — the instrumented count is the pass, the mechanism is the implementation.
        self.assertIn("the recorded zero-flip count is the pass", self.preflight)


if __name__ == "__main__":
    unittest.main()
