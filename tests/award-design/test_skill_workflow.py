"""award-design SKILL.md top-level structure — the ambient-forcing contract.

The rebuild dropped the 4-phase Discovery/Decision/Tokens/Production workflow:
the skill is now "ambient forcing, not a checklist" (art-director, not
project-manager). This module pins the new section spine, the judging-criteria
numbers, and the remix routing. The universe-mandatory / commit-and-prove /
review-mode contracts are pinned in test_universe_mandatory.py; the moved-out
token + atmosphere contracts in test_extension_tokens.py and test_archetypes.py.

Each assertion here would FAIL on the pre-rebuild SKILL.md, which carried
`## Workflow` with four `### Phase N — Title` headings and no ambient-forcing
framing."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_MD = REPO_ROOT / "skills" / "award-design" / "SKILL.md"


def _body():
    return SKILL_MD.read_text(encoding="utf-8")


# The rebuilt skill's top-level spine — H2 sections, in document order. The
# rebuild replaced the phased workflow with these; reordering or dropping one
# changes the art-director framing the skill is built on.
EXPECTED_SECTIONS = [
    "## Ambient forcing, not a checklist",
    "## Scope",
    "## The universe is mandatory",
    "## Build the frontend yourself, under the forcing",
    "## Review mode",
    "## Stack",
]


class TestAmbientForcingStructure(unittest.TestCase):
    """The rebuilt skill is ambient forcing, not a phased checklist. The new
    H2 spine must be present and ordered; the phased-workflow vocabulary must
    be gone — its survival would mean the rebuild only half-landed."""

    def test_each_section_present(self):
        body = _body()
        for header in EXPECTED_SECTIONS:
            with self.subTest(section=header):
                self.assertIn(header, body, f"top-level section missing: {header}")

    def test_sections_in_document_order(self):
        body = _body()
        positions = [body.find(h) for h in EXPECTED_SECTIONS]
        self.assertTrue(all(p != -1 for p in positions), "a spine section is missing")
        self.assertEqual(
            positions, sorted(positions),
            "top-level sections are out of the contracted order",
        )

    def test_art_director_framing_present(self):
        """The framing line is the load-bearing reframe: the rules are ambient
        air the build breathes, not phases to clear. Losing it returns the skill
        to a checklist posture."""
        body = _body().lower()
        self.assertIn("art-director, not a project-manager", body,
                      "the art-director (not project-manager) framing must be stated")
        self.assertIn("not phases to clear", body,
                      "the rules must be framed as ambient forcing, not phases to clear")

    def test_no_phased_workflow_survives(self):
        """The 4-phase workflow is gone. Neither a `## Workflow` section nor any
        `### Phase N — Title` heading may remain."""
        body = _body()
        self.assertNotRegex(
            body, r"(?m)^## Workflow\b",
            "the `## Workflow` section must not survive the rebuild",
        )
        self.assertNotRegex(
            body, r"(?m)^### Phase \d+ —",
            "no `### Phase N — Title` heading may survive the rebuild",
        )

    def test_old_phase_titles_gone(self):
        """The four phase titles, as phase headings, must not return."""
        body = _body()
        for phase in ("Discovery", "Decision", "Tokens", "Production"):
            with self.subTest(phase=phase):
                self.assertNotRegex(
                    body, rf"(?m)^###.*\b{phase}\b",
                    f"phase heading '{phase}' must not survive as an H3",
                )


class TestScopeBoundary(unittest.TestCase):
    """Scope is the discipline that keeps the skill from sprawling: it takes the
    lead on frontend, routes single-token tweaks to /design-system, and never
    touches backend. All three must be stated or the auto-trigger over-reaches."""

    def _scope(self):
        body = _body()
        m = re.search(r"^## Scope\b.*?\n(.*?)(?=^##\s)", body, re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, "## Scope section missing")
        return m.group(1)

    def test_takes_the_lead_on_frontend(self):
        scope = self._scope().lower()
        self.assertIn("take the lead", scope,
                      "Scope must state the skill takes the lead on frontend")

    def test_single_token_routes_to_design_system(self):
        scope = self._scope()
        self.assertIn("/design-system", scope,
                      "Scope must route single-token changes to /design-system")
        self.assertRegex(
            scope.lower(), r"single[- ]token",
            "Scope must name the single-token-change route-out explicitly",
        )

    def test_never_touches_backend(self):
        scope = self._scope().lower()
        self.assertIn("never", scope)
        self.assertIn("backend", scope)
        self.assertIn("frontend only", scope,
                      "Scope must declare the skill frontend-only")

    def test_empty_dir_routes_to_scaffold(self):
        self.assertIn("/scaffold", self._scope(),
                      "Scope must route an empty directory to /scaffold first")


class TestAutoTriggerInWhenToUse(unittest.TestCase):
    """The auto-trigger-from-line-1 contract lives in the `when_to_use`
    frontmatter (the trigger surface), not the body. It must declare the
    take-the-lead posture and the same scope route-outs."""

    def _when_to_use(self):
        # `when_to_use:` is a single logical line in the YAML frontmatter.
        m = re.search(r"(?m)^when_to_use:\s*(.+)$", _body())
        self.assertIsNotNone(m, "when_to_use frontmatter field missing")
        return m.group(1)

    def test_auto_triggers_from_line_one(self):
        wtu = self._when_to_use().lower()
        self.assertIn("auto-trigger", wtu,
                      "when_to_use must declare the skill auto-triggers")
        self.assertIn("take the lead", wtu,
                      "when_to_use must state the take-the-lead-from-line-1 posture")

    def test_routes_single_token_and_ignores_backend(self):
        wtu = self._when_to_use().lower()
        self.assertIn("/design-system", wtu,
                      "when_to_use must route single-token changes to /design-system")
        self.assertIn("backend", wtu,
                      "when_to_use must state it ignores backend work")

    def test_review_subcommand_advertised(self):
        wtu = self._when_to_use()
        self.assertIn("award-design review", wtu,
                      "when_to_use must advertise the `award-design review <url|path>` mode")


class TestJudgingCriteria(unittest.TestCase):
    """The judging-criteria section pins the Awwwards weighting (40/30/20/10)
    and the score floors (6.5+ Honorable Mention, 7.5+ SOTD). These numbers are
    the contract — drift means the skill's recommendations stop matching the
    actual judging signal."""

    def test_judging_criteria_section_exists(self):
        self.assertIn("## Judging criteria", _body())

    def test_weights_documented(self):
        body = _body()
        for label, pct in [("Design", 40), ("Usability", 30),
                            ("Creativity", 20), ("Content", 10)]:
            with self.subTest(label=label, pct=pct):
                # Format: `Design 40%` — match the label adjacent to its weight.
                self.assertRegex(
                    body, rf"{label}\s*{pct}%",
                    f"judging weight '{label} {pct}%' missing or mis-formatted",
                )

    def test_score_floors_documented(self):
        body = _body()
        self.assertIn("6.5+", body, "Honorable Mention floor (6.5+) not cited")
        self.assertIn("7.5", body, "SOTD floor (7.5+) not cited")


class TestAtmosphereCalibrationRouting(unittest.TestCase):
    """The 1-10 atmosphere axes (Density / Variance / Motion) moved into
    references/atmosphere-calibration.md; SKILL.md carries only the pointer.
    The body must route there rather than re-deriving the ranges inline —
    the lean body is intentional."""

    def test_skill_routes_to_calibration_reference(self):
        self.assertIn("references/atmosphere-calibration.md", _body(),
                      "SKILL.md must route atmosphere calibration to its reference file")

    def test_three_axes_named_at_the_pointer(self):
        """The pointer names the axes so the reader knows what calibration
        covers — Density / Variance / Motion."""
        body = _body()
        m = re.search(r"atmosphere.{0,60}references/atmosphere-calibration\.md",
                      body, re.IGNORECASE | re.DOTALL)
        self.assertIsNotNone(m, "atmosphere-calibration pointer prose missing")
        self.assertRegex(
            m.group(0), r"Density.*Variance.*Motion",
            "the calibration pointer must name the Density / Variance / Motion axes",
        )


class TestRemixingFallback(unittest.TestCase):
    """The remix fallback documents the path when the brief refuses a single
    archetype. It routes to references/remixing.md rather than re-deriving the
    mix rules inline — the routing-to-reference contract is what matters."""

    def test_remix_routes_to_reference(self):
        self.assertIn("references/remixing.md", _body(),
                      "SKILL.md must route hybrid briefs to references/remixing.md")


if __name__ == "__main__":
    unittest.main()
