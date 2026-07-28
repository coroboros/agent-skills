"""award-design universe-mandatory contract — now carried by protocol phases.

The universe remains MANDATORY: no frontend ships without a committed one.
The rebuilt skill carries its enforcement in phases — Phase 0 reads the room
(design read, archetype, declared dials), Phase 1 conceives the universe
(spine, two-altitude anti-default, rotation, signature, R1 refutation),
Phase 2 writes it as a DESIGN.md, Phase 4 commits a binding design_plan before
any markup and carries the WebGL one-subagent delegation. Review mode stays
the always-on refuter. These tests pin those contracts at their current homes;
each would FAIL on a SKILL.md with no universe forcing at all."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_MD = REPO_ROOT / "skills" / "award-design" / "SKILL.md"
FOUNDATIONS_MD = REPO_ROOT / "skills" / "award-design" / "references" / "foundations.md"
PREFLIGHT_MD = REPO_ROOT / "skills" / "award-design" / "references" / "preflight.md"


def _body():
    return SKILL_MD.read_text(encoding="utf-8")


def _foundations():
    return FOUNDATIONS_MD.read_text(encoding="utf-8")


def _phase(n):
    m = re.search(rf"^## Phase {n} — .*?\n(.*?)(?=^## )", _body(), re.DOTALL | re.MULTILINE)
    assert m is not None, f"## Phase {n} section missing"
    return m.group(1)


class TestUniverseIsMandatory(unittest.TestCase):
    """No frontend ships without a committed universe — the build is gated on
    it (Phases 1–2), never an opt-in."""

    def test_no_ship_without_committed_universe(self):
        self.assertIn("No frontend ships without a committed universe", _phase(1),
                      "the universe must stay a hard precondition of any build")

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
    """Phase 1 forces the moves that push a model past its lazy defaults:
    a concept spine, the two-altitude anti-default, an out-loud rotation, a
    signature moment, and the regenerate-on-thin R1 gate."""

    def setUp(self):
        self.phase1 = _phase(1)

    def test_design_read_declared_at_phase_0(self):
        phase0 = _phase(0)
        self.assertIn("Design read", phase0)
        self.assertIn("Reading this as:", phase0,
                      "Phase 0 must force the committed one-line design read")

    def test_concept_spine_forced(self):
        self.assertIn("Concept spine", self.phase1)
        self.assertIn("ONE world", self.phase1,
                      "the spine commits to one world, not a literal restatement")

    def test_anti_default_at_two_altitudes(self):
        """One rejection produces the second-most-obvious default; the
        two-altitude cut (reject the lazy default AND the told-to-avoid-it
        reach) is what lands on a genuinely non-obvious direction."""
        phase1 = self.phase1
        self.assertIn("Anti-default at two altitudes", phase1)
        self.assertRegex(phase1.lower(), r"reject.*reject that too|reject it; then name",
                         "both altitudes must be named and rejected")
        self.assertIn("survives both cuts", phase1,
                      "what survives both cuts is the committed direction")

    def test_rotation_is_stated_and_ledgered(self):
        phase1 = self.phase1
        self.assertIn("Rotation", phase1)
        self.assertIn("stamp", phase1,
                      "rotation must read the previous build's stylesheet stamp")
        self.assertRegex(phase1.lower(), r"palette family, type pairing, hero layout",
                         "rotation must name its rotated axes")
        self.assertIn("≥2 named axes", phase1,
                      "every build must rotate at least two named axes")
        self.assertIn("old→new stated", phase1)

    def test_signature_moment_forced(self):
        self.assertIn("Signature moment", self.phase1)
        self.assertIn("sit unchanged on a rival's site", self.phase1,
                      "the signature keeps its falsifiable bespoke test")

    def test_thin_universe_regenerated_and_veto_wired(self):
        phase1 = self.phase1
        self.assertIn("is regenerated", phase1,
                      "a thin / literal / safe spine must be regenerated")
        self.assertIn("concept quality caps the build", phase1,
                      "concept quality must cap the build — polish cannot rescue it")

    def test_r1_refutes_before_any_file(self):
        self.assertIn("before any file is written", self.phase1,
                      "R1 must refute the universe before any file exists")


class TestDesignMdAuthoredAndAdapted(unittest.TestCase):
    """Phase 2 writes the DESIGN.md (Google format) when none exists, adopts
    an existing one as the ultimate reference, alerts when it is thin, and
    hands governance to /design-system after the build."""

    def setUp(self):
        self.phase2 = _phase(2)

    def test_authors_design_md_when_none_exists(self):
        phase2 = self.phase2
        self.assertRegex(phase2, r"Author the complete DESIGN\.md")
        self.assertIn("Google format", phase2)
        self.assertIn("all eight sections", phase2)

    def test_adapts_to_existing_design_md(self):
        phase2 = self.phase2
        self.assertIn("Existing DESIGN.md", phase2)
        self.assertRegex(phase2.lower(), r"adopt it|build consistent")

    def test_alerts_when_existing_design_md_is_thin(self):
        self.assertIn("alert when thin", self.phase2)
        self.assertIn("never silently re-author", self.phase2.lower())

    def test_design_system_governs_after_the_build(self):
        phase2 = self.phase2
        self.assertIn("After the build", phase2)
        self.assertIn("/design-system", phase2)
        self.assertIn("governs", phase2.lower())

    def test_design_md_is_the_constant_reference(self):
        phase2 = self.phase2.lower()
        self.assertIn("re-read it each phase", phase2)
        self.assertIn("every subagent", phase2)


class TestDesignPlanCommit(unittest.TestCase):
    """Phase 4 commits a binding design_plan before any markup — explicit
    per-element commitments, paced like a score, mobile as its own
    performance — then builds section by section under a browser loop."""

    def setUp(self):
        self.phase4 = _phase(4)

    def test_design_plan_is_binding_and_pre_markup(self):
        phase4 = self.phase4
        self.assertIn("design_plan", phase4)
        self.assertIn("before any markup", phase4.lower())
        self.assertIn("binding, amendable in writing", phase4,
                      "amendments happen in writing, never by silent drift")

    def test_commits_explicit_per_element_selections(self):
        phase4 = self.phase4
        self.assertIn("Commit a design_plan", phase4)
        for element in ("hero architecture", "navigation pattern", "type stack",
                        "color roles", "motion register", "signature"):
            with self.subTest(element=element):
                self.assertIn(element, phase4.lower())

    def test_sections_carry_funnel_jobs(self):
        self.assertIn("attention → understanding → proof → close", self.phase4,
                      "every section commits its funnel job in the design_plan")

    def test_claimed_equals_shown(self):
        phase4 = self.phase4
        self.assertIn("Claimed = shown", phase4)
        self.assertIn("Every universe claim is in the code", phase4)

    def test_per_section_browser_gate(self):
        phase4 = self.phase4
        self.assertIn("Per-section browser loop", phase4)
        self.assertIn("375px", phase4)
        self.assertIn("1440px", phase4)
        self.assertIn("console clean", phase4.lower())
        self.assertIn("Resolve the browser rung", phase4)
        self.assertIn("references/external-truth.md", phase4,
                      "the browser ladder lives in external-truth.md")

    def test_conformance_loop_is_the_gate(self):
        """The gate is a loop, not a single look: screenshot → hunt drift →
        fix → re-render, exit only when both widths pass in the same iteration,
        capped with declared residue."""
        phase4 = self.phase4
        self.assertIn("until both widths pass in the same iteration", phase4)
        self.assertIn("cap 5", phase4)
        self.assertIn("file what still stands", phase4,
                      "residue past the cap is filed, never silently accepted")

    def test_font_resolution_proof(self):
        """A display font silently falling back to a system font is invisible
        in the code and destroys the whole design — the loop hunts the
        committed face, and pre-flight verifies the computed value."""
        self.assertIn("the committed display face renders", self.phase4)
        preflight = PREFLIGHT_MD.read_text(encoding="utf-8")
        self.assertIn("resolves to the committed face", preflight)
        self.assertIn("(detector: FONT-RESOLVE)", preflight)

    def test_pacing_map_committed(self):
        """Models compose section by section — locally fine, globally flat.
        The design_plan must pace the page like a score: at most one climax,
        at least one rest, never a flat curve."""
        phase4 = self.phase4
        self.assertIn("Pace like a score", phase4)
        self.assertIn("At most one climax", phase4)
        self.assertIn("at least one rest", phase4)
        self.assertIn("flat curve", phase4.lower())

    def test_mobile_intent_committed(self):
        phase4 = self.phase4
        self.assertIn("Mobile is a different performance of the same universe", phase4)
        self.assertIn("below 768px beyond stacking", phase4)

    def test_phase_4_loads_optical_craft(self):
        self.assertIn("references/optical-craft.md", self.phase4,
                      "Phase 4 must load the optical-craft reference before the first component")

    def test_rotation_stamp_written(self):
        self.assertIn("/* award-design ·", self.phase4,
                      "Phase 4 must stamp the stylesheet for the rotation ledger")


class TestReviewMode(unittest.TestCase):
    """Review mode stays the always-on refuter — standalone via
    `award-design review <url|path>` and as R1/R2 inside every build, judging
    pixels before machine output."""

    def _review(self):
        m = re.search(r"^## Review mode\b(.*?)(?=^##\s)", _body(), re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, "## Review mode section missing")
        return m.group(1)

    def test_review_invoked_by_subcommand(self):
        self.assertIn("award-design review <url|path>", self._review())

    def test_review_refutes_never_confirms(self):
        review = self._review().lower()
        self.assertRegex(review, r"\*\*refute\*\*, not confirm|refute by default")
        self.assertIn("never a silent pass", review)

    def test_review_runs_inside_every_build(self):
        self.assertIn("R1/R2 inside every build", self._review())

    def test_review_judges_pixels_before_scanner(self):
        review = self._review().lower()
        self.assertIn("judge from pixels", review)
        self.assertIn("run the scanner second", review,
                      "the anti-anchoring order must hold in standalone review too")

    def test_review_runs_against_rubric_and_exemplars(self):
        review = self._review()
        for ref in ("references/audit-rubric.md", "references/exemplars.md"):
            with self.subTest(ref=ref):
                self.assertIn(ref, review)


class TestWebGLDelegation(unittest.TestCase):
    """The single delegation carve-out lives in Phase 4: one subagent for a
    self-contained WebGL/3D scene, briefed with the DESIGN.md verbatim and the
    ingredients cheat, integrated by the skill itself — never a co-written
    file."""

    def setUp(self):
        m = re.search(r"\*\*WebGL/3D delegation\.\*\*(.*?)(?=\n- \*\*|\n\n|\n##)",
                      _body(), re.DOTALL)
        self.assertIsNotNone(m, "WebGL/3D delegation clause missing")
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
        self.assertIn("DESIGN.md quoted verbatim", carve,
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
