"""award-design universe-mandatory contract — now carried by the nine-step path.

The universe remains MANDATORY: no frontend ships without a committed one.
The core carries its enforcement across the path — step 0 reads the room
(mode, archetype, declared dials), steps 1–4 force the spine list, the roll and
the anti-attractor cut, step 5 commits the six-block contract, step 6 refutes it
in a fresh context before any build file exists, step 7 writes it as a DESIGN.md.
The gate files carry the review that never confirms, and the WebGL/3D delegation
rides the cheat its subagent is briefed with. These tests pin those contracts at
their current homes; each would FAIL on a SKILL.md with no universe forcing at
all."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFS = SKILL_DIR / "references"
FOUNDATIONS_MD = REFS / "foundations.md"
PREFLIGHT_MD = REFS / "preflight.md"


def _body():
    return SKILL_MD.read_text(encoding="utf-8")


def _foundations():
    return FOUNDATIONS_MD.read_text(encoding="utf-8")


def _ref(rel):
    return (REFS / rel).read_text(encoding="utf-8")


def _section(name):
    m = re.search(rf"^## {re.escape(name)}\b(.*?)(?=^##\s)", _body(),
                  re.DOTALL | re.MULTILINE)
    assert m is not None, f"## {name} section missing"
    return m.group(1)


def _path():
    return _section("The path")


def _step(n):
    """One numbered step of the path — each is a single line."""
    m = re.search(rf"(?m)^{n}\. \*\*.*$", _body())
    assert m is not None, f"path step {n} missing"
    return m.group(0)


class TestUniverseIsMandatory(unittest.TestCase):
    """No frontend ships without a committed universe — the build is gated on
    the six-block contract and its fresh-context refutation, never an opt-in."""

    def test_no_ship_without_committed_universe(self):
        path = _path()
        self.assertIn("**The contract.** Six blocks", path,
                      "the universe is a committed contract, not an intention")
        self.assertIn('Close with **FINISH:** "this build ends with the review, '
                      'the verdict, and DESIGN.md."', path,
                      "the contract states its own terminus")

    def test_design_md_is_not_optional(self):
        body = _body().lower()
        for stale in ("no design.md required", "no design.md is required",
                      "no design file is authored before pixels"):
            with self.subTest(phrase=stale):
                self.assertNotIn(stale, body)

    def test_no_inline_token_block_or_persist_path(self):
        body = _body()
        self.assertNotIn("inline token block", body.lower())
        self.assertNotRegex(body, r"(?m)^## Persist\b")


class TestForcedConcepting(unittest.TestCase):
    """The path forces the moves that push a model past its lazy defaults: the
    room read out loud, a written spine list, the roll's assignment, the
    two-altitude anti-attractor cut, a declared signature, and the
    regenerate-on-OFF-TRACK R1 gate."""

    def test_the_room_is_read_out_loud(self):
        step0 = _step(0)
        self.assertIn("Mode (build · redesign-preserve · redesign-overhaul", step0)
        self.assertIn("archetype from the signal map below, validated against "
                      "the brand's personality", step0)
        self.assertIn("dials (Density / Variance / Motion", step0)

    def test_concept_spine_forced(self):
        self.assertIn("Write 5–7 candidate spines into it under `SPINES:`",
                      _step(1))
        self.assertIn("the world, and the replayable moment it promises", _step(1),
                      "a spine commits to one world, not a literal restatement")
        self.assertIn("The assigned spine is the commitment", _step(2))

    def test_anti_default_at_two_altitudes(self):
        """One rejection produces the second-most-obvious default; the
        two-altitude cut (reject the reflex AND the told-to-avoid-it reach) is
        what lands on a genuinely non-obvious direction."""
        step4 = _step(4)
        self.assertIn("**Anti-attractor.**", step4)
        self.assertIn("reject them by name", step4)
        self.assertIn("name what a model avoiding those reaches next, and reject that too",
                      step4, "both altitudes must be named and rejected")

    def test_variance_is_forced_by_the_roll(self):
        """Convergence build after build is the documented failure of
        model-driven design; the roll is the mechanism that prevents it, and
        taste is never grounds for a re-roll."""
        step2 = _step(2)
        self.assertIn("python3 scripts/direction_roll.py", step2)
        self.assertIn("a model's own ranking converges on the same direction every run",
                      step2)
        self.assertIn("Taste is never grounds for a re-roll", step2)

    def test_signature_moment_forced(self):
        self.assertIn("**SIGNATURE** (verb · medium · trigger · replay behavior", _step(5))
        self.assertIn("sit unchanged on a rival's site", _ref("gate/concept.md"),
                      "the signature keeps its falsifiable bespoke test at R1")

    def test_thin_universe_regenerated_and_veto_wired(self):
        self.assertIn("OFF-TRACK regenerates the named target; polish is never the remedy",
                      _step(6), "a thin / literal / safe concept is regenerated")
        self.assertIn("a concept-stage failure with the same weight as a thin spine",
                      _ref("signature-invention.md"),
                      "concept quality caps the build — polish cannot rescue it")

    def test_r1_refutes_before_any_file(self):
        self.assertIn("before any build file exists", _step(6),
                      "R1 must refute the universe before any build file exists")


class TestDesignMdAuthoredAndAdapted(unittest.TestCase):
    """The path writes the DESIGN.md when none exists, Routing adopts an
    existing one as the universe, alerts when it is thin, and hands governance
    to /design-system after the build."""

    def test_authors_design_md_when_none_exists(self):
        self.assertIn("Author the full DESIGN.md (`references/design-md-anatomy.md`)", _step(7))
        self.assertIn("signature choreography as a beat table", _step(7))
        self.assertIn("eight ordered prose sections", _ref("design-md-anatomy.md"))

    def test_adapts_to_existing_design_md(self):
        self.assertIn("A bounded change inside a healthy DESIGN.md adopts the universe",
                      _section("Routing"))

    def test_alerts_when_existing_design_md_is_thin(self):
        self.assertIn("alert when thin, never silently regenerate", _section("Routing"))

    def test_design_system_governs_after_the_build(self):
        self.assertIn("/design-system", _section("Routing"))
        self.assertIn("`/design-system` governs it after", _ref("design-md-anatomy.md"))

    def test_design_md_is_the_constant_reference(self):
        self.assertIn("the constant reference for every build pass and every subagent",
                      _ref("design-md-anatomy.md"))


class TestDesignPlanCommit(unittest.TestCase):
    """The design_plan carries the spines, the seed and the six-block contract
    before any build file exists — paced like a score, verified per chapter, and
    amendable only in writing."""

    def test_design_plan_is_binding_and_pre_markup(self):
        path = _path()
        self.assertIn("design_plan", path)
        self.assertIn("before any build file exists", path)
        self.assertIn("copied verbatim into the first build file's opening comment", path,
                      "the contract travels with the artifact, never as a side note")

    def test_the_contract_commits_the_universe_block_by_block(self):
        step5 = _step(5)
        for block in ("**THESIS**", "**OWN-WORLD**", "**STORY**", "**FIRST-VIEWPORT**",
                      "**FORM+SEED**", "**SIGNATURE**"):
            with self.subTest(block=block):
                self.assertIn(block, step5, f"contract block missing: {block}")
        self.assertIn("palette and component language, recognizable with all content removed",
                      step5)
        self.assertIn("A block that reads like a mood is not decided yet", step5)

    def test_sections_carry_funnel_jobs(self):
        anatomy = _ref("page-anatomy.md")
        self.assertIn("Every section commits its funnel job before it is built", anatomy)
        self.assertIn("attention → understanding → proof → close", anatomy)
        self.assertIn("a flat curve is a template however good each section looks alone",
                      anatomy, "the diagnostic is what makes the commitment enforceable")

    def test_claimed_equals_shown(self):
        path = _path()
        self.assertIn("Claimed = shown", path)
        self.assertIn("cut only by a written amendment, never in cleanup", path)

    def test_per_chapter_browser_gate(self):
        self.assertIn("After each chapter, inject `assets/render-floor.js`", _path())
        verify = _section("Verify, then ship")
        self.assertIn("sweep 375/768/1024/1440/1920", verify)
        self.assertIn("one browser session per run", verify)

    def test_conformance_loop_is_bounded(self):
        """The gate is a loop, not a single look — and a bounded one: one fix
        batch, one recheck, and the second verdict ends work whatever it says."""
        review = _ref("gate/review.md")
        self.assertIn("Fixes apply in ONE batch", review)
        self.assertIn("the second verdict ends work whatever it says", review)
        self.assertIn("A finding is dismissed only with a measurement", review,
                      "residue is measured out, never glanced away")

    def test_font_resolution_proof(self):
        """A display font silently falling back to a system font is invisible
        in the code and destroys the whole design — the face is a hard
        constraint, and pre-flight verifies the computed value."""
        self.assertIn("Inter/Roboto/Arial/system on the display face", _body())
        preflight = PREFLIGHT_MD.read_text(encoding="utf-8")
        self.assertIn("resolves to the committed face", preflight)
        self.assertIn("(detector: FONT-RESOLVE)", preflight)

    def test_pacing_map_committed(self):
        """Models compose section by section — locally fine, globally flat.
        The build paces the page like a score: one climax, at least one rest."""
        path = _path()
        self.assertIn("Pace like a score", path)
        self.assertIn("with one climax", path)
        self.assertIn("at least one rest", path)

    def test_mobile_intent_committed(self):
        imp = _ref("award-imperatives.md")
        self.assertIn("Mobile reconsidered, not responsive-bolted-on", imp)
        self.assertIn("a re-thought performance of the same idea", imp)

    def test_build_loads_optical_craft(self):
        self.assertIn("Apply `references/optical-craft.md` while building", _path(),
                      "optical craft is installed during the build, never detected after")


class TestReviewGate(unittest.TestCase):
    """The review stays the always-on refuter — standalone via
    `award-design review <url|path>` and as R1/R2 inside every build, judging
    the render in its own words before any machine output."""

    def test_review_invoked_by_subcommand(self):
        self.assertIn("`award-design review <url|path>` → run `references/gate/review.md` "
                      "standalone on the target", _section("Routing"))

    def test_review_refutes_never_confirms(self):
        self.assertIn("The reviewer refutes; it never confirms", _ref("gate/concept.md"))
        review = _ref("gate/review.md")
        self.assertIn("No praise, no summary prose", review,
                      "R2 emits ranked findings, never a silent pass")
        self.assertIn("the builder never writes READY", review,
                      "the reviewer's return is the only thing that can clear the build")

    def test_review_runs_inside_every_build(self):
        self.assertIn("references/gate/concept.md", _path(), "R1 runs inside every build")
        self.assertIn("references/gate/review.md", _section("Verify, then ship"),
                      "R2 runs inside every build")

    def test_review_judges_pixels_before_scanner(self):
        review = _ref("gate/review.md")
        self.assertIn("after the mechanical layers are clean", review,
                      "a judge run over a broken page returns unusable signal")
        self.assertIn("describes the rendered page in its own words", review,
                      "the anti-anchoring order holds in standalone review too")

    def test_review_runs_against_the_exemplar(self):
        self.assertIn("references/exemplars.md", _ref("gate/concept.md"))
        self.assertIn("the live exemplar (tier-1 names it)", _ref("gate/review.md"))


class TestWebGLDelegation(unittest.TestCase):
    """The single delegation carve-out lives with the cheat its subagent rides:
    one subagent for a self-contained WebGL/3D scene, briefed with the DESIGN.md
    verbatim and the ingredients cheat, integrated by the skill itself — never a
    co-written file."""

    def setUp(self):
        m = re.search(r"^## The delegation contract\n(.*?)(?=^## )",
                      _ref("ingredients/web3d-for-sites.md"), re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, "## The delegation contract section missing")
        self.carve = m.group(1)

    def test_single_subagent_only(self):
        self.assertIn("ONE subagent", self.carve)

    def test_scene_is_self_contained(self):
        self.assertIn("self-contained scene", self.carve.lower())

    def test_fidelity_and_input_floors(self):
        carve = self.carve.lower()
        self.assertIn("fidelity floor", carve)
        self.assertIn("no primitive geometry as the hero object", carve)
        self.assertIn("drag-ghost", carve,
                      "the input-correctness floor must name the drag-ghost defect")

    def test_self_integration(self):
        self.assertIn("integrate the returned module yourself", self.carve.lower())

    def test_no_shared_file_co_authoring(self):
        self.assertIn("never co-write a file", self.carve.lower())

    def test_briefed_with_design_md_and_ingredients(self):
        carve = self.carve
        self.assertIn("`DESIGN.md` quoted verbatim", carve,
                      "the subagent's brief is the DESIGN.md, verbatim")
        self.assertIn("references/ingredients/", carve,
                      "the subagent must ride the matching ingredients cheat")


class TestStackMapping(unittest.TestCase):
    """The stack detail lives in foundations.md — Astro for content
    archetypes, TanStack Start for motion/3D, locked universal craft, existing
    stack wins — and the SKILL.md routes to its Stack map at bootstrap."""

    def _stack_detail(self):
        m = re.search(r"^## Stack\b.*?\n(.*?)(?=^##\s)", _foundations(), re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, "foundations.md ## Stack section missing")
        return m.group(1)

    def test_routing_points_at_stack_map(self):
        body = _body()
        self.assertIn("`references/foundations.md` §Stack", body,
                      "bootstrap must route through the foundations Stack section")
        self.assertIn("prescribes its own stack wins", body,
                      "a brief that prescribes its own stack overrides the routing")

    def test_locked_universal_craft(self):
        stack = self._stack_detail()
        for craft in ("GSAP", "Lenis", "View Transitions", "variable fonts", "OKLCH"):
            with self.subTest(craft=craft):
                self.assertIn(craft, stack)
        self.assertRegex(stack.lower(), r"css scroll-driven")

    def test_astro_for_content_archetypes(self):
        line = next((ln for ln in self._stack_detail().splitlines() if "Astro" in ln), "")
        self.assertTrue(line, "stack must map Astro to its archetypes")
        for archetype in ("Minimalist", "Editorial", "Corporate-Luxury", "Bento"):
            with self.subTest(archetype=archetype):
                self.assertIn(archetype, line)

    def test_tanstack_for_motion_3d_archetypes(self):
        line = next((ln for ln in self._stack_detail().splitlines()
                     if "TanStack Start" in ln), "")
        self.assertTrue(line, "stack must map TanStack Start to its archetypes")
        for archetype in ("Immersive", "Experimental", "Bold", "Spatial-Organic"):
            with self.subTest(archetype=archetype):
                self.assertIn(archetype, line)

    def test_motion_framer_and_r3f_on_tanstack_path_only(self):
        self.assertRegex(
            self._stack_detail(),
            r"(Motion/Framer \+ R3F|Motion \(Framer\).*R3F).*TanStack path only")

    def test_existing_stack_wins_no_migration(self):
        stack = self._stack_detail()
        self.assertIn("Existing project's stack wins", stack)
        self.assertRegex(stack.lower(), r"adapt, don't migrate|adapt, never migrate")

    def test_host_is_orthogonal(self):
        stack = self._stack_detail().lower()
        self.assertIn("host orthogonal", stack)
        self.assertIn("never assumed", stack)


if __name__ == "__main__":
    unittest.main()
