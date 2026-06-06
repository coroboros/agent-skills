"""award-design code-first contract.

These assertions encode the reorder away from DESIGN.md-first: the skill builds
a site without requiring a token file, adapts to one when present, and
crystallizes one only on opt-in. Each test here would FAIL on the pre-refactor
SKILL.md (which authored a full DESIGN.md in Phase 3 and gated the build on two
mandatory validation stops) — that is what makes them verify the change rather
than merely describe it."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_MD = REPO_ROOT / "skills" / "award-design" / "SKILL.md"
ANTI_PATTERNS = REPO_ROOT / "skills" / "award-design" / "references" / "anti-patterns.md"
AUDIT_RUBRIC = REPO_ROOT / "skills" / "award-design" / "references" / "audit-rubric.md"


def _body():
    return SKILL_MD.read_text(encoding="utf-8")


def _phase_4():
    m = re.search(
        r"^### Phase 4 — Production(.*?)(?=^### Phase|\Z|^##\s)",
        _body(), re.DOTALL | re.MULTILINE,
    )
    assert m, "Phase 4 (Production) missing"
    return m.group(1)


class TestModeDetect(unittest.TestCase):
    """The skill branches on whether a DESIGN.md exists — the entry point of
    the code-first design. The old skill had no such branch."""

    def test_mode_detect_block_present(self):
        self.assertRegex(
            _body(), r"[Mm]ode detect",
            "Workflow must open with a mode-detect step",
        )

    def test_names_adapt_and_instant_modes(self):
        body = _body()
        for mode in ("Adapt", "Instant"):
            with self.subTest(mode=mode):
                self.assertIn(mode, body, f"mode-detect must name the {mode} mode")

    def test_instant_is_the_default(self):
        self.assertRegex(
            _body(), r"Instant\b.*\(default\)|\(default\).*Instant",
            "Instant must be marked the default (no-DESIGN.md) path",
        )


class TestNoMandatoryDesignFile(unittest.TestCase):
    """Code-first: pixels do not wait on a DESIGN.md, and the two old mandatory
    'ask the user to validate before proceeding' stops are gone."""

    def test_design_md_declared_optional(self):
        body = _body().lower()
        self.assertTrue(
            "no design file is authored before pixels" in body
            or "no design.md required" in body
            or "no design.md is required" in body,
            "Workflow must state a DESIGN.md is not required before building",
        )

    def test_old_mandatory_validation_gate_removed(self):
        """The pre-refactor blocking gate phrasing must not survive."""
        self.assertNotIn(
            "Ask the user to validate before proceeding", _body(),
            "the mandatory pre-build validation stop must be removed",
        )

    def test_confirm_is_optional(self):
        self.assertRegex(
            _body(), r"[Oo]ne optional confirm|optional .*confirm|never blocks the build",
            "the single archetype confirm must be optional and non-blocking",
        )


class TestPersistPath(unittest.TestCase):
    """The full DESIGN.md is an opt-in artifact authored AFTER the build."""

    def test_persist_section_exists(self):
        self.assertIn(
            "## Persist", _body(),
            "a Persist section must document opt-in DESIGN.md crystallization",
        )

    def test_persist_is_opt_in_after_build(self):
        m = re.search(r"^## Persist(.*?)(?=^##\s)", _body(), re.DOTALL | re.MULTILINE)
        assert m is not None, "Persist section missing or unterminated"
        section = m.group(1).lower()
        self.assertIn("opt-in", section, "Persist must be opt-in")
        self.assertTrue(
            "after the build" in section or "after the site ships" in section,
            "Persist must run after the build, not before",
        )

    def test_award_design_owns_crystallization(self):
        self.assertRegex(
            _body().lower(),
            r"award-design owns this crystallization|owns (the )?crystalliz",
            "ownership rule: award-design crystallizes the DESIGN.md",
        )


class TestTwoGateClose(unittest.TestCase):
    """Phase 4 closes on two gates — a HARD gate that can fail and a SOFT
    advisory rubric — replacing any single self-scored pass."""

    def test_hard_and_soft_gates_named(self):
        section = _phase_4()
        self.assertRegex(section, r"HARD gate", "Phase 4 must define a HARD gate")
        self.assertRegex(section, r"SOFT gate", "Phase 4 must define a SOFT (advisory) gate")

    def test_audit_is_conditional_on_file_presence(self):
        """The design-system audit only runs when a DESIGN.md exists — a no-file
        build must remain scorable without it."""
        section = _phase_4().lower()
        self.assertIn(
            "only when a design.md exists", section,
            "the HARD gate must skip the design-system audit when no DESIGN.md exists",
        )

    def test_soft_gate_is_advisory_not_a_pass(self):
        section = _phase_4().lower()
        self.assertTrue(
            "advisory" in section and "never present a self-graded number as a pass" in section,
            "the SOFT rubric must be advisory, never a self-graded pass",
        )


class TestCountableChecks(unittest.TestCase):
    """anti-patterns.md carries the deterministic, archetype-scoped checks that
    make the HARD gate able to fail on a no-DESIGN.md build."""

    def _anti(self):
        return ANTI_PATTERNS.read_text(encoding="utf-8")

    def test_countable_checks_section_exists(self):
        self.assertIn("## Countable checks", self._anti(), "countable-checks section missing")

    def test_eyebrow_count_rule_present(self):
        self.assertIn(
            "ceil(sectionCount / 3)", self._anti(),
            "eyebrow-density countable check missing",
        )

    def test_em_dash_check_is_archetype_gated(self):
        anti = self._anti()
        self.assertIn("Em-dash density", anti, "em-dash countable check missing")
        # The check must declare a scope and suppress for the two editorial archetypes.
        self.assertRegex(
            anti, r"suppressed for `editorial` and `corporate-luxury`",
            "em-dash check must be archetype-conditional, not a global ban",
        )

    def test_scope_is_declared(self):
        """Every countable check declares global vs archetype-conditional."""
        anti = self._anti()
        self.assertIn("Global", anti)
        self.assertIn("Archetype-conditional", anti)


class TestRubricDecoupledFromDesignMd(unittest.TestCase):
    """The rubric's top anchors no longer require a DESIGN.md — token trace is a
    bonus, so a no-file build can reach the top of the scale."""

    def _rubric(self):
        return AUDIT_RUBRIC.read_text(encoding="utf-8")

    def test_rubric_framed_as_soft_advisory_gate(self):
        self.assertRegex(
            self._rubric(), r"SOFT \(advisory\) gate",
            "audit-rubric.md must declare itself the SOFT advisory gate",
        )

    def test_token_trace_is_a_bonus_not_a_prerequisite(self):
        rubric = self._rubric().lower()
        self.assertIn(
            "token trace is a bonus, not a prerequisite", rubric,
            "value-consistency rule must make token trace a bonus, not a requirement",
        )

    def test_no_file_build_can_reach_top_anchor(self):
        """At least one top anchor explicitly states a no-file build reaches 10."""
        self.assertRegex(
            self._rubric().lower(),
            r"no-file build reaches 10|reaches 10 on .*alone",
            "a top anchor must state a no-DESIGN.md build can score 10",
        )


if __name__ == "__main__":
    unittest.main()
