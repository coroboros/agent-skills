"""award-design universe-mandatory contract — now carried by protocol phases.

The universe remains MANDATORY: no frontend ships without a committed one.
The protocol rebuild moved its enforcement into phases — Phase 0 reads the
room (Design Read, archetype, declared dials), Phase 1 conceives the universe
(spine, two-altitude anti-default, rotation, signature, R1 refutation),
Phase 2 writes it as a DESIGN.md, Phase 4 commits-and-proves before any markup
and carries the WebGL one-subagent carve-out. Review mode stays the always-on
refuter. These tests pin those contracts at their new homes; each would FAIL
on the pre-protocol SKILL.md (different sections) AND on the pre-rebuild one
(no universe forcing at all)."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_MD = REPO_ROOT / "skills" / "award-design" / "SKILL.md"
FOUNDATIONS_MD = REPO_ROOT / "skills" / "award-design" / "references" / "foundations.md"


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
    a Concept Spine, the two-altitude anti-default, an out-loud rotation, a
    signature moment, and a regenerate-on-thin self-check capped by the
    concept veto."""

    def setUp(self):
        self.phase1 = _phase(1)

    def test_design_read_declared_at_phase_0(self):
        phase0 = _phase(0)
        self.assertIn("Design Read", phase0)
        self.assertIn("Reading this as:", phase0,
                      "Phase 0 must force the committed one-line Design Read")

    def test_concept_spine_forced(self):
        self.assertIn("Concept Spine", self.phase1)
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
        self.assertIn("never the first option", phase1)

    def test_rotation_is_stated_and_ledgered(self):
        phase1 = self.phase1
        self.assertIn("Rotation", phase1)
        self.assertIn("stamp", phase1,
                      "rotation must read the previous build's stylesheet stamp")
        self.assertRegex(phase1.lower(), r"palette family, type pairing, hero layout",
                         "rotation must name the three rotated axes")
        self.assertIn("≥1 mechanic", phase1,
                      "every build must invent at least one fresh mechanic")

    def test_signature_moment_forced(self):
        self.assertIn("Signature moment", self.phase1)
        self.assertIn("removing every effect", self.phase1.lower(),
                      "the signature keeps its falsifiable removing-every-effect test")

    def test_thin_universe_regenerated_and_veto_wired(self):
        phase1 = self.phase1
        self.assertIn("regenerated before proceeding", phase1,
                      "a thin / literal / safe spine must be regenerated")
        self.assertIn("concept veto", phase1.lower(),
                      "concept quality must cap the build via the rubric's veto")

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
        self.assertIn("eight prose sections", phase2)

    def test_adapts_to_existing_design_md(self):
        phase2 = self.phase2
        self.assertIn("Existing DESIGN.md", phase2)
        self.assertRegex(phase2.lower(), r"adopt it|build consistent")

    def test_alerts_when_existing_design_md_is_thin(self):
        self.assertIn("Alert", self.phase2)
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


class TestCommitAndProve(unittest.TestCase):
    """Phase 4 emits a binding design_plan before any markup: explicit
    per-element commitments, each load-bearing one paired with a proof line."""

    def setUp(self):
        self.phase4 = _phase(4)

    def test_design_plan_is_binding_and_pre_markup(self):
        phase4 = self.phase4
        self.assertIn("design_plan", phase4)
        self.assertIn("before any markup", phase4.lower())
        self.assertRegex(phase4.lower(),
                         r"follow it exactly|drifting to a default.*forbidden")

    def test_commits_explicit_per_element_selections(self):
        phase4 = self.phase4
        self.assertRegex(phase4, r"\*\*Commit\*\*")
        for element in ("hero", "type", "color", "motion", "signature"):
            with self.subTest(element=element):
                self.assertIn(element, phase4.lower())

    def test_each_commitment_carries_a_proof(self):
        phase4 = self.phase4
        self.assertRegex(phase4, r"\*\*Prove\*\*")
        self.assertIn("clamp()", phase4)
        self.assertRegex(phase4.lower(), r"≤2 lines|≤ 2 lines|2 lines")

    def test_claimed_equals_shown(self):
        phase4 = self.phase4
        self.assertIn("Claimed = shown", phase4)
        self.assertIn("not just promised", phase4.lower())

    def test_per_section_browser_gate(self):
        phase4 = self.phase4
        self.assertRegex(phase4, r"375px and 1440px",
                         "the per-section browser gate must name its widths")
        self.assertIn("console clean", phase4.lower())
        self.assertIn("before starting the next section", phase4.lower())

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
        self.assertIn("pixels are the evidence", review)
        self.assertRegex(review, r"judgment first.*mechanical results second",
                         "the anti-anchoring order must hold in standalone review too")

    def test_review_runs_against_rubric_catalog_and_gate(self):
        review = self._review()
        for ref in ("references/audit-rubric.md", "references/anti-patterns.md",
                    "references/preflight.md"):
            with self.subTest(ref=ref):
                self.assertIn(ref, review)


class TestWebGLOneSubagentCarveOut(unittest.TestCase):
    """The single delegation carve-out lives in Phase 4: one subagent for a
    self-contained Immersive/Experimental WebGL/R3F scene, integrated by the
    skill itself — never for other archetypes, never a shared file."""

    def setUp(self):
        m = re.search(r"\*\*WebGL / 3D — the one delegation\.\*\*(.*?)(?=\n- \*\*|\n\n\*\*|\n##)",
                      _body(), re.DOTALL)
        self.assertIsNotNone(m, "WebGL / 3D — the one delegation clause missing")
        self.carve = m.group(1)

    def test_single_subagent_only(self):
        self.assertIn("ONE subagent", self.carve)
        self.assertIn("never more than one parallel writer", self.carve.lower())

    def test_scoped_to_immersive_experimental_only(self):
        self.assertTrue("Immersive" in self.carve and "Experimental" in self.carve)
        self.assertIn("never for other archetypes", self.carve.lower())

    def test_clean_boundary_and_self_integration(self):
        carve = self.carve.lower()
        self.assertIn("props in, canvas out", carve)
        self.assertIn("integrate the returned module yourself", carve)

    def test_no_shared_file_co_authoring(self):
        self.assertIn("never co-write a shared file", self.carve.lower())

    def test_briefed_with_design_md_and_truth_source(self):
        carve = self.carve
        self.assertIn("DESIGN.md", carve, "the subagent's brief is the DESIGN.md")
        self.assertIn("Phase 3", carve,
                      "the subagent must ride the truth source resolved at Phase 3")


class TestStackMapping(unittest.TestCase):
    """The stack is keyed to the archetype in Phase 4 (terse) with the detail
    in foundations.md — Astro for content archetypes, TanStack Start for
    motion/3D, locked universal craft, existing stack wins."""

    def _stack_detail(self):
        m = re.search(r"^## Stack\b.*?\n(.*?)(?=^##\s)", _foundations(), re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, "foundations.md ## Stack section missing")
        return m.group(1)

    def test_phase_4_keys_stack_and_routes(self):
        phase4 = _phase(4)
        self.assertIn("Astro", phase4)
        self.assertIn("TanStack Start", phase4)
        self.assertIn("foundations.md", phase4)
        self.assertIn("existing project's stack always wins", phase4.lower())

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
