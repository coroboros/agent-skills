"""award-design universe-mandatory contract — the inversion of code-first.

The rebuild reversed the old "code-first, no upfront DESIGN.md required, inline
token block, offer Persist" posture. The universe is now MANDATORY: no frontend
ships without a committed universe; the skill writes a DESIGN.md when none
exists, adapts to (and alerts on a thin) existing one, and /design-system
governs the file after. The build first emits a binding `design_plan` with
per-element commitments and a proof line each — before any JSX — and every
universe claim must be shown in the code, not just promised. A standalone
`review` mode audits any site refute-by-default.

Each assertion would FAIL on the pre-rebuild SKILL.md (which declared the
DESIGN.md optional, gated nothing on a committed universe, and crystallized the
file only on an opt-in Persist) — that is what makes them verify the inversion
rather than merely describe it."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_MD = REPO_ROOT / "skills" / "award-design" / "SKILL.md"


def _body():
    return SKILL_MD.read_text(encoding="utf-8")


def _universe_section():
    """The `## The universe is mandatory` block — the heart of the inversion."""
    m = re.search(
        r"^## The universe is mandatory\b(.*?)(?=^##\s)",
        _body(), re.DOTALL | re.MULTILINE,
    )
    assert m is not None, "## The universe is mandatory section missing"
    return m.group(1)


def _build_section():
    """The `## Build the frontend yourself, under the forcing` block."""
    m = re.search(
        r"^## Build the frontend yourself, under the forcing\b(.*?)(?=^##\s)",
        _body(), re.DOTALL | re.MULTILINE,
    )
    assert m is not None, "## Build the frontend yourself section missing"
    return m.group(1)


class TestUniverseIsMandatory(unittest.TestCase):
    """No frontend ships without a committed universe — the exact opposite of
    the old code-first default. The build is gated on it, not on an opt-in."""

    def test_section_exists(self):
        self.assertIn("## The universe is mandatory", _body())

    def test_no_ship_without_committed_universe(self):
        section = _universe_section().lower()
        self.assertIn("no frontend ships without a committed universe", section,
                      "the universe must be declared a hard precondition of any build")

    def test_design_md_is_not_optional(self):
        """The old 'no DESIGN.md required before pixels' posture must be gone."""
        body = _body().lower()
        for stale in (
            "no design.md required",
            "no design.md is required",
            "no design file is authored before pixels",
            "no design file before pixels",
        ):
            with self.subTest(phrase=stale):
                self.assertNotIn(stale, body,
                                 f"the optional-DESIGN.md posture must not survive: {stale!r}")

    def test_no_inline_token_block_default(self):
        """The build no longer commits an inline YAML token block in place of a
        DESIGN.md — it authors the file."""
        body = _body().lower()
        self.assertNotIn("inline token block", body,
                         "the inline-token-block-instead-of-DESIGN.md posture must be gone")

    def test_no_opt_in_persist_path(self):
        """The DESIGN.md is authored up front now, not crystallized on a later
        opt-in. No `## Persist` section, no 'opt-in Persist' wording."""
        body = _body()
        self.assertNotRegex(body, r"(?m)^## Persist\b",
                            "the opt-in Persist section must not survive the rebuild")
        self.assertNotIn("Persist path", body,
                         "the opt-in Persist path must be gone — the universe is authored up front")


class TestForcedConcepting(unittest.TestCase):
    """Conceiving the universe forces four moves before any code: a Design Read,
    a Concept Spine, anti-default-with-teeth, and a signature moment. Each is the
    discipline that pushes Opus past its lazy defaults; dropping one re-opens a
    generic-build escape hatch. The skill must refuse a thin universe."""

    def setUp(self):
        self.section = _universe_section()

    def test_design_read_forced(self):
        self.assertIn("Design Read", self.section,
                      "concepting must force a committed Design Read line")

    def test_concept_spine_forced(self):
        self.assertIn("Concept Spine", self.section,
                      "concepting must force a named Concept Spine")
        self.assertIn("ONE world", self.section,
                      "the Concept Spine must commit to one world, not a literal restatement")

    def test_anti_default_with_teeth(self):
        section = self.section
        self.assertIn("Anti-default with teeth", section,
                      "concepting must force anti-default-with-teeth")
        # The teeth: name-then-reject the lazy default, rotate across builds,
        # and invent a fresh mechanic — not a generic 'be original'.
        self.assertRegex(section.lower(), r"reject|lazy default",
                         "anti-default must name and reject the brief's lazy default")
        self.assertIn("Rotate", section,
                      "anti-default must rotate off the last build's palette / type / hero")

    def test_signature_moment_forced(self):
        section = self.section
        self.assertIn("Signature moment", section,
                      "concepting must force a signature moment")
        # The falsifiable test for a real signature.
        self.assertIn("removing every effect", section.lower(),
                      "the signature must carry its falsifiable removing-every-effect test")

    def test_thin_universe_is_refused(self):
        section = self.section.lower()
        self.assertIn("refuse", section,
                      "a thin / literal / safe universe must be refused and regenerated")


class TestDesignMdAuthoredAndAdapted(unittest.TestCase):
    """The skill writes a DESIGN.md (Google format) when none exists, adapts to
    an existing one as the ultimate reference, and alerts when that file is thin
    — never silently re-authoring. /design-system governs the file after."""

    def setUp(self):
        self.section = _universe_section()

    def test_authors_design_md_when_none_exists(self):
        section = self.section
        self.assertIn("DESIGN.md", section, "the universe must be written as a DESIGN.md")
        self.assertRegex(
            section, r"Author a complete DESIGN\.md|write it as a DESIGN\.md",
            "the skill must author a complete DESIGN.md when none exists",
        )
        self.assertIn("Google format", section,
                      "the authored DESIGN.md must be the Google format")

    def test_adapts_to_existing_design_md(self):
        section = self.section
        self.assertIn("Existing DESIGN.md", section,
                      "the skill must branch on an existing DESIGN.md")
        self.assertRegex(
            section.lower(), r"adopt it|build consistent",
            "an existing DESIGN.md must be adopted as the reference, not ignored",
        )

    def test_alerts_when_existing_design_md_is_thin(self):
        section = self.section
        self.assertIn("Alert", section,
                      "the skill must alert when an existing DESIGN.md is thin/incomplete")
        self.assertIn("never silently re-author", section.lower(),
                      "a thin DESIGN.md must trigger an alert, never a silent re-author")

    def test_design_system_governs_after_the_build(self):
        section = self.section.lower()
        self.assertIn("after the build", section,
                      "governance must hand off after the build")
        self.assertIn("/design-system", self.section,
                      "/design-system must govern the DESIGN.md after the build")
        self.assertIn("design-system governs", section,
                      "the author-vs-govern split must be stated explicitly")

    def test_design_md_is_the_constant_reference(self):
        """The DESIGN.md is re-read every pass and handed to every subagent —
        the reference contract, not a write-once artifact."""
        section = self.section.lower()
        self.assertIn("re-read it every pass", section,
                      "the DESIGN.md must be re-read every pass")
        self.assertIn("every subagent", section,
                      "the DESIGN.md must be passed to every subagent")


class TestCommitAndProve(unittest.TestCase):
    """Before any JSX the build emits a binding `design_plan`: explicit
    per-element commitments, each load-bearing one paired with a proof line.
    This is the gate that converts the universe into code commitments; without
    it the build drifts to a default mid-stream."""

    def setUp(self):
        self.build = _build_section()
        m = re.search(
            r"### Commit-and-prove(.*?)(?=^###\s|\Z)",
            self.build, re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(m, "### Commit-and-prove subsection missing")
        self.commit = m.group(1)

    def test_design_plan_is_binding_and_pre_jsx(self):
        self.assertIn("design_plan", self.commit,
                      "the build must output a binding design_plan")
        self.assertIn("before any jsx", self.build.lower(),
                      "the design_plan must precede any JSX")
        self.assertRegex(
            self.commit.lower(), r"follow it exactly|drifting to a default.*forbidden",
            "the design_plan must be binding — drifting to a default is forbidden",
        )

    def test_commits_explicit_per_element_selections(self):
        commit = self.commit
        self.assertRegex(commit, r"\*\*Commit\*\*",
                         "commit-and-prove must carry an explicit Commit clause")
        # The per-element commitments must enumerate the load-bearing surfaces.
        for element in ("hero", "type", "color", "motion", "signature"):
            with self.subTest(element=element):
                self.assertIn(element, commit.lower(),
                              f"the design_plan must commit the {element} selection")

    def test_each_commitment_carries_a_proof(self):
        commit = self.commit
        self.assertRegex(commit, r"\*\*Prove\*\*",
                         "commit-and-prove must carry an explicit Prove clause")
        # Proofs are concrete guarantees, not restatements.
        self.assertIn("clamp()", commit,
                      "the H1 proof must name the clamp()/max-w that guarantees ≤2 lines")
        self.assertRegex(commit.lower(), r"≤2 lines|≤ 2 lines|2 lines",
                         "the H1 proof must guarantee the headline lands in ≤2 lines")

    def test_claimed_equals_shown(self):
        """Every universe claim must be present in the code, not just promised —
        the rule that makes the design_plan binding rather than aspirational."""
        build = self.build
        self.assertIn("Claimed = shown", build,
                      "the build must enforce claimed = shown")
        self.assertIn("not just promised", build.lower(),
                      "claimed = shown must require the claim be in the code, not just promised")


class TestReviewMode(unittest.TestCase):
    """A standalone review mode audits any site refute-by-default — invoked via
    `award-design review <url|path>`, run on yourself before ship, and never a
    silent pass. This replaces nothing in the old code-first contract; it is a
    new always-on critic the tests must pin."""

    def _review(self):
        m = re.search(
            r"^## Review mode\b(.*?)(?=^##\s)",
            _body(), re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(m, "## Review mode section missing")
        return m.group(1)

    def test_review_section_exists(self):
        self.assertIn("## Review mode", _body())

    def test_review_invoked_by_subcommand(self):
        review = self._review()
        self.assertIn("award-design review <url|path>", review,
                      "review mode must document the `award-design review <url|path>` invocation")

    def test_review_is_refute_by_default(self):
        review = self._review().lower()
        self.assertIn("refute by default", review,
                      "review mode must refute by default, not confirm")
        self.assertIn("never a silent pass", review,
                      "review mode must never silently pass")

    def test_review_runs_against_rubric_and_anti_slop(self):
        review = self._review()
        self.assertIn("references/audit-rubric.md", review,
                      "review must audit against the awwwards rubric reference")
        self.assertIn("references/anti-patterns.md", review,
                      "review must audit against the anti-slop catalog")

    def test_review_runs_on_self_before_ship(self):
        review = self._review().lower()
        self.assertRegex(
            review, r"on yourself before ship|before ship",
            "review must be run on the build itself before ship",
        )


class TestWebGLOneSubagentCarveOut(unittest.TestCase):
    """The single delegation carve-out: an Immersive/Experimental WebGL/R3F
    signature with a clean component boundary delegates ONE subagent to author
    that module — never for other archetypes, never a shared file, never more
    than one parallel writer. The build is otherwise authored by the skill
    itself (no handoff)."""

    def setUp(self):
        m = re.search(
            r"### WebGL / 3D — the one delegation(.*?)(?=^###\s|^##\s)",
            _body(), re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(m, "### WebGL / 3D — the one delegation subsection missing")
        self.carve = m.group(1)

    def test_single_subagent_only(self):
        carve = self.carve
        self.assertIn("ONE subagent", carve,
                      "the carve-out must delegate exactly one subagent")
        self.assertIn("never more than one parallel writer", carve.lower(),
                      "the carve-out must forbid more than one parallel writer")

    def test_scoped_to_immersive_experimental_only(self):
        carve = self.carve
        self.assertTrue(
            "Immersive" in carve and "Experimental" in carve,
            "the carve-out must scope to Immersive / Experimental signatures",
        )
        self.assertIn("Never for the other archetypes", carve,
                      "the carve-out must exclude the other archetypes")

    def test_clean_boundary_and_self_integration(self):
        carve = self.carve.lower()
        self.assertRegex(carve, r"clean component boundary|props in, canvas out",
                         "the carve-out requires a clean component boundary")
        self.assertIn("integrate the returned module yourself", carve,
                      "the skill must integrate the returned module itself")

    def test_no_shared_file_co_authoring(self):
        self.assertIn("never co-write a shared file", self.carve.lower(),
                      "the carve-out must forbid co-writing a shared file")


class TestStackMapping(unittest.TestCase):
    """The stack is keyed to the archetype, not locked to one framework: Astro
    for content archetypes, TanStack Start for motion/3D archetypes, with a
    locked universal craft layer and host kept orthogonal. Drift here means the
    skill recommends the wrong runtime for the chosen archetype."""

    def _stack(self):
        m = re.search(r"^## Stack\b.*?\n(.*?)(?=^##\s)", _body(), re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, "## Stack section missing")
        return m.group(1)

    def test_locked_universal_craft(self):
        stack = self._stack()
        for craft in ("GSAP", "Lenis", "View Transitions", "variable fonts", "OKLCH"):
            with self.subTest(craft=craft):
                self.assertIn(craft, stack, f"locked universal craft must include {craft}")
        self.assertRegex(stack.lower(), r"css scroll-driven",
                         "locked craft must include CSS scroll-driven animations")

    def test_astro_for_content_archetypes(self):
        stack = self._stack()
        m = next((ln for ln in stack.splitlines() if "Astro" in ln), "")
        self.assertTrue(m, "stack must map Astro to its archetypes")
        for archetype in ("Minimalist", "Editorial", "Corporate-Luxury", "Bento"):
            with self.subTest(archetype=archetype):
                self.assertIn(archetype, m,
                              f"Astro must be keyed to the {archetype} content archetype")

    def test_tanstack_for_motion_3d_archetypes(self):
        stack = self._stack()
        m = next((ln for ln in stack.splitlines() if "TanStack Start" in ln), "")
        self.assertTrue(m, "stack must map TanStack Start to its archetypes")
        for archetype in ("Immersive", "Experimental", "Bold", "Spatial-Organic"):
            with self.subTest(archetype=archetype):
                self.assertIn(archetype, m,
                              f"TanStack Start must be keyed to the {archetype} archetype")

    def test_motion_framer_and_r3f_on_tanstack_path_only(self):
        stack = self._stack()
        self.assertRegex(
            stack, r"(Motion/Framer \+ R3F|Motion \(Framer\).*R3F).*TanStack path only",
            "Motion/Framer + R3F must be scoped to the TanStack path only",
        )

    def test_existing_stack_wins_no_migration(self):
        stack = self._stack()
        self.assertIn("Existing project's stack wins", stack,
                      "an existing project's stack must win — adapt, not migrate")
        self.assertRegex(stack.lower(), r"adapt, don't migrate|adapt, never migrate",
                         "the rule must be adapt-not-migrate")

    def test_host_is_orthogonal(self):
        stack = self._stack().lower()
        self.assertIn("host orthogonal", stack,
                      "host must be declared orthogonal (Nitro presets, /scaffold optional)")
        self.assertIn("never assumed", stack,
                      "the /scaffold deploy preset must never be assumed")


if __name__ == "__main__":
    unittest.main()
