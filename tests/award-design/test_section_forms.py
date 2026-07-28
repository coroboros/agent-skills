"""award-design v2 round 2 — section forms + the composition floors.

Forms are the layout-ownership answer to the round-2 defect classes (crowded
data-strips, sprawling meta-lines): a form's CSS owns placement, the builder
fills contracted slots. These tests lock the drift surface: manifest ↔ forms/
sync, every contracted slot styled by its stylesheet, the no-JS floor (a form
that hides a slot at rest blacks out content when the script dies), the
layering law on any form enhancer, and the Phase 4/preflight/audit wiring that
keeps the surviving composition laws binding rather than decorative."""

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



ARCHETYPES = ("minimalist", "brutalist", "editorial", "bold-maximal",
              "immersive-cinematic", "experimental", "corporate-luxury",
              "bento-card", "spatial-organic")
REFS = SKILL_DIR / "references"


def _tier_two(archetype):
    return (REFS / f"{archetype}.md").read_text(encoding="utf-8")


class TestArchetypeCompositionCapital(unittest.TestCase):
    """The composition layer the JSON playbooks and recipes.json used to carry.
    The two-tier restructure merged it into each archetype's tier-2 reference —
    the section chain, the per-element states, the spectacle beats and the
    variation clause now live where the design_plan commit already loads them,
    by heading. These assertions follow the capital, not the file it used to
    sit in: the checks that only proved a JSON file parsed went with it."""

    def test_spectacle_model_is_diffable(self):
        """The build's spectacle conformance table diffs its shipped beats against
        the model. That diff target must exist and be non-empty for every archetype:
        a hero beat and the continuation beats. A model with no beats to quote is
        the gate ARDEN escaped — a hover shipped as the page climax with nothing to
        check it against."""
        for archetype in ARCHETYPES:
            with self.subTest(archetype=archetype):
                body = _tier_two(archetype)
                menu = body[body.index("## Spectacle menu"):]
                self.assertIn("**The hero beat.**", menu)
                self.assertIn("**The continuation beats**", menu)
                self.assertIn("**The peak law**", menu)
                self.assertTrue(
                    any(v in menu for v in ("SUPPORTED", "REFINED", "REFUTED")),
                    "the peak law carries the one-climax verdict it was adjudicated to")

    def test_section_chain_and_element_states_are_present(self):
        """section_playbook + element_states: the per-role form/pair/intensity
        chain and the tap/focus/dormancy answers per element class. A hover-only
        state table reads dead under `hover: none`."""
        for archetype in ARCHETYPES:
            with self.subTest(archetype=archetype):
                body = _tier_two(archetype)
                self.assertIn("**Section chain**", body)
                self.assertIn("**Element states — tap, focus, dormancy.**", body)
                self.assertIn("**Mobile / touch**", body)

    def test_variation_axes_present(self):
        """CALDERA postmortem: two same-archetype builds shipped isomorphic
        skeletons. R-sameness corpus (21 artifacts, 5 serial studios): the
        skeleton is one legal costume; the device kit + content archetype +
        close rotate — an archetype without the variation clause reads as THE
        skeleton and reproduces the monoculture."""
        for archetype in ARCHETYPES:
            with self.subTest(archetype=archetype):
                body = _tier_two(archetype)
                self.assertIn("**Variation**", body)
                self.assertIn("one legal costume", body)
                self.assertIn("never reused across builds", body)
                self.assertIn("zero winner precedent", body)

    def test_reading_kit_is_a_device_not_dna(self):
        """ARDEN monoculture: the reading kit shipped identical across five
        different-brand builds because every variation clause listed "interaction
        vocabulary" as persisting DNA. The reword scopes it — the motion register
        persists, the named kit is a device that rotates."""
        for archetype in ARCHETYPES:
            with self.subTest(archetype=archetype):
                body = _tier_two(archetype)
                self.assertNotIn("motion register + interaction vocabulary", body,
                                 "the DNA clause must not list the named kit as persisting")
                self.assertIn("device, rotated per build", body)

    def test_minimalist_structural_variety(self):
        """One rigid shape meant the same page every build. Minimalist carries
        three macrostructures, and gallery-stack no longer contradicts its own
        evidence (the 'imageless withholding hero' framing was refuted)."""
        body = _tier_two("minimalist")
        anatomy = body[body.index("**Anatomy**"):body.index("**Hero architectures**")]
        for slug in ("`argument-scroll`", "`gallery-stack`", "`scene-scroll`"):
            with self.subTest(macrostructure=slug):
                self.assertIn(slug, anatomy)
        self.assertNotIn("text-only name card", body)
        self.assertIn("MAIN GALLERY", body)

    def test_minimalist_reaches_the_ambitious_medium(self):
        """Terminal (our minimalist exemplar) ships a canvas frame-sequence + a
        Three.js showreel (Pacome); the skill had locked the rendered medium out of
        minimalist, so builds stayed sparse. The exemplar-proven pieces stay
        minimalist-reachable, and the scene macrostructure carries a medium climax."""
        arche = {c["id"]: set(c["archetypes"])
                 for c in json.loads(MANIFEST.read_text(encoding="utf-8"))["components"]}
        for cid in ("scrub-film", "shader-surface", "scramble-decode", "flicker-reveal"):
            with self.subTest(component=cid):
                self.assertIn("minimalist", arche[cid],
                              f"{cid} must be reachable in minimalist (exemplar-proven)")
        body = _tier_two("minimalist")
        scene = body[body.index("`scene-scroll`"):]
        self.assertIn("`scrub-film`", scene[:800],
                      "the scene hero's medium is the canvas frame-sequence (Terminal's mechanic)")
        self.assertIn("climax", scene[:800])

    def test_corpus_entries_carry_awards(self):
        """The Effect palette corpus is the evidence line every claim below it
        cites. A corpus row with no award is an unsourced opinion."""
        for archetype in ARCHETYPES:
            with self.subTest(archetype=archetype):
                body = _tier_two(archetype)
                corpus = body[body.index("Corpus —"):]
                corpus = corpus[:corpus.index("\n\n")]
                self.assertTrue(
                    any(badge in corpus
                        for badge in ("Awwwards", "SOTD", "SOTM", "SOTY", "CSSDA", "FWA",
                                      "Honorable Mention", "Codrops")),
                    "the corpus line must name the award or case study each entry rests on")


class TestArchetypeWiring(unittest.TestCase):
    """The phrases that keep the composition layer binding rather than decorative."""

    def test_skill_carries_the_mobile_commit(self):
        """The R-D research's load-bearing finding: winners let pointer classes
        go dormant on touch, and the tap answer on press-class elements is the
        floor — a hover-only substrate reads dead under hover:none."""
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("go dormant on touch", skill)
        self.assertIn("answer the tap on `:active`", skill)
        preflight = (SKILL_DIR / "references" / "preflight.md").read_text(encoding="utf-8")
        self.assertIn("pointer-only classes rest dormant (that is the winner answer, not a gap)",
                      preflight)



class TestCompositionFloorsWiring(unittest.TestCase):
    """The floors are inert unless the phases carry them — pin the phrases."""

    def setUp(self):
        self.skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.preflight = (SKILL_DIR / "references" / "preflight.md").read_text(encoding="utf-8")
        self.rubric = (SKILL_DIR / "references" / "audit-rubric.md").read_text(encoding="utf-8")

    def test_phase4_pace_like_a_score(self):
        # the surviving spectacle law: the climax cap plus the trigger law —
        # ARDEN's hover-as-climax stays impossible without the conformance table
        self.assertIn("At most one climax", self.skill)
        self.assertIn("never pointer-gated", self.skill)
        self.assertIn("at least one rest", self.skill)
        self.assertIn("a flat curve is a template", self.skill)

    def test_density_aliveness_bar(self):
        """Cennini cleared every floor and shipped "empty and dead" because no gate
        measured richness. The floor is not the ceiling; the exemplar is the bar,
        and a sparse/static build fails the density/aliveness read comparatively."""
        self.assertIn("empty and dead", self.skill)
        self.assertIn("Aim at the exemplar's ceiling, never at the floor the checks define",
                      self.skill)
        self.assertIn("does this carry as many live channels", self.skill)
        self.assertIn("necessary, never sufficient", self.preflight)
        self.assertIn("does the build carry as many live channels", self.rubric)

    def test_felt_text_effect_law(self):
        """Cennini shipped "zero text effect" because a static colour accent
        cleared the old gate. The commit box died with the floor rewrite; the
        law survives in the text-effects canon and Phase 4's motion rules."""
        self.assertIn("Text is a motion surface too", self.skill)
        te = (SKILL_DIR / "references" / "text-effects.md").read_text(encoding="utf-8")
        self.assertIn("DISPLAY entrance still carries a felt reveal", te)
        self.assertIn("the Cennini failure", te)

    def test_motion_continuity_law(self):
        """The R4 motion-continuity law survives compressed: never silent after
        the hero — live channels run page-deep and the footer closes live."""
        self.assertIn("their footers close on the live signature", self.skill)
        self.assertIn("winners close on a live footer, never a static contact block", self.skill)
        self.assertIn("never one hero moment then a dead page", self.skill)

    def test_phase4_non_contradiction(self):
        self.assertIn("Sparse-and-static is not restraint", self.skill)
        self.assertIn("restraint lowers amplitude, never coverage", self.skill)

    def test_preflight_countable_boxes(self):
        for name in ("**Eyebrows**", "**Legibility floor**", "**Layout variety**",
                     "**Zigzag**", "**Grid fill**", "**Hero stack**",
                     "**CTA wrap**", "**Italic descenders**"):
            with self.subTest(box=name):
                self.assertIn(name, self.preflight)

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
    defaults ('I know a better way'). The imposed-verdicts table died with the
    library-quality; these pin its load-bearing rows where they live on as law."""

    @classmethod
    def setUpClass(cls):
        cls.skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.preflight = (SKILL_DIR / "references" / "preflight.md").read_text(encoding="utf-8")
        cls.interactions = (SKILL_DIR / "references" / "interaction-signatures.md").read_text(encoding="utf-8")
        cls.navpat = (SKILL_DIR / "references" / "navigation-patterns.md").read_text(encoding="utf-8")

    def test_hard_constraints_override_protocol(self):
        self.assertIn("each match-and-refuse", self.skill)
        self.assertIn("The only override is an explicit client clause quoted in the DESIGN.md",
                      self.skill)

    def test_surviving_verdict_laws(self):
        self.assertIn("registers never mix on a page", self.skill)
        self.assertIn("Mixed motion registers on one page", self.skill)
        self.assertIn("A nav that flickers under scroll jitter", self.skill)
        self.assertIn("zero hide/show flips", self.preflight)
        self.assertIn("the absence of a grammar", self.interactions)

    def test_story_native_law_in_phase1(self):
        self.assertIn("its rituals become the chapters and the effect vocabulary", self.skill)
        self.assertIn("only forced variance prevents it", self.skill)

    def test_motion_register_amendment(self):
        # R-imposed live measurement: a SOTD winner runs 9 timing tokens across
        # 4 curve families, all one register — the cap moved from family to register.
        self.assertIn("one motion register page-wide", self.preflight)
        self.assertIn("What no winner does is cross registers", self.interactions)
        self.assertIn("all decelerating-mechanical", self.interactions)

    def test_nav_winner_norm(self):
        self.assertIn("**The winner norm is not hiding at all.**", self.navpat)
        self.assertIn("zero visible hide/show flips under scroll jitter", self.navpat)

    def test_loophole_closures(self):
        """Red-team round (2026-07-17): the closures that survived the rewrite —
        the Siena route on an immersive brief, provenance on asset numbers, the
        fixed probe order, and the instrumented flip count."""
        # #1 — a stills procession never satisfies the immersive hero-medium bar.
        self.assertIn("zero winner precedent on an immersive brief", self.skill)
        # #3 — asset numbers carry provenance; the builder cannot narrow the class.
        self.assertIn("(full-bleed, scrubbed, zoomed) holds ≥ device pixels", self.preflight)
        self.assertIn("an asserted number is a fail", self.preflight)
        # #4 — probe order is fixed; a chosen-to-fail probe is the escape, not a gap.
        self.assertIn("ToolSearch for the browser MCP is the mandatory first probe", self.preflight)
        # #6 — the instrumented count is the pass, the mechanism is the implementation.
        self.assertIn("the sampled flip count pasted", self.preflight)


if __name__ == "__main__":
    unittest.main()
