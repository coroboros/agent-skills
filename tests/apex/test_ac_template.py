"""Tests for the AC discipline upgrade in step-01 analyze.

Verifies step-01-analyze.md adopted the Given/When/Then AC template, the
`## Not Included (negative scope)` section, and the `### 0a. Spec AC closure`
rule that accepts spec AC verbatim when `-f` points to a spec.

Test approach. Apex is a prose-driven skill — no `apex.sh` / `apex.py`
entrypoint to subprocess-invoke. Per `.claude/rules/skill-authoring.md`
§ Testing, the convention for prompt-driven skills is structural tests
over runtime subprocess tests. The assertions below verify that the
SKILL.md / step files / templates document the contracts. Runtime
emission of the documented behavior is exercised by the universal
`tests/_meta/` suite (frontmatter, references, parity) plus actual
`/apex` invocations in user sessions.
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
STEP_01 = REPO_ROOT / "skills" / "apex" / "steps" / "step-01-analyze.md"
TEMPLATE_01 = REPO_ROOT / "skills" / "apex" / "templates" / "01-analyze.md"
SKILL_MD = REPO_ROOT / "skills" / "apex" / "SKILL.md"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


class TestACTemplate(unittest.TestCase):
    def setUp(self):
        self.step_01 = STEP_01.read_text(encoding="utf-8")
        self.template_01 = TEMPLATE_01.read_text(encoding="utf-8")
        self.skill_md = SKILL_MD.read_text(encoding="utf-8")

    def test_step_01_has_given_when_then(self):
        """step-01-analyze.md AC template uses Given/When/Then form."""
        pattern = re.compile(
            r"Given\s+<[^>]+>,\s+when\s+<[^>]+>,\s+then\s+<[^>]+>",
            re.IGNORECASE,
        )
        self.assertTrue(
            pattern.search(self.step_01),
            "step-01-analyze.md AC template must use Given/When/Then form",
        )

    def test_step_01_has_negative_scope_section(self):
        """step-01-analyze.md AC template includes the Not Included header."""
        self.assertIn(
            "## Not Included (negative scope)",
            self.step_01,
            "step-01-analyze.md must declare the Not Included section",
        )

    def test_step_01_documents_spec_closure_rule(self):
        """`### 0a. Spec AC closure` must appear and reference the H1 +
        Workstreams heuristic plus the spec-AC-accepted log line."""
        self.assertIn(
            "### 0a. Spec AC closure",
            self.step_01,
            "Spec AC closure subsection must be present",
        )
        self.assertIn(
            "# Spec:",
            self.step_01,
            "Spec detection heuristic (H1 `# Spec:`) must be documented",
        )
        self.assertIn(
            "## Workstreams",
            self.step_01,
            "Spec detection heuristic (subheader `## Workstreams`) must be documented",
        )
        self.assertIn(
            "Spec AC accepted verbatim",
            self.step_01,
            "Log line for spec-closure activation must be documented",
        )

    def test_step_01_drops_legacy_template(self):
        """Bare `[ ] AC1: [specific measurable outcome]` template must NOT survive."""
        self.assertNotIn(
            "[ ] AC1: [specific measurable outcome]",
            self.step_01,
            "Legacy bare-AC template must be replaced by G/W/T form",
        )

    def test_template_01_carries_new_sections(self):
        """templates/01-analyze.md mirrors the new AC + Not Included structure."""
        self.assertIn(
            "## Inferred Acceptance Criteria",
            self.template_01,
        )
        self.assertIn(
            "## Not Included (negative scope)",
            self.template_01,
        )

    def test_skill_md_declares_negative_acceptance_state_var(self):
        """SKILL.md State Variables table includes {negative_acceptance}."""
        self.assertIn(
            "{negative_acceptance}",
            self.skill_md,
            "SKILL.md must declare {negative_acceptance} state variable",
        )

    def test_spec_fixture_matches_spec_heuristic(self):
        """spec-input.md fixture matches the spec-closure heuristic."""
        spec = (FIXTURES / "spec-input.md").read_text(encoding="utf-8")
        self.assertTrue(
            spec.lstrip().startswith("# Spec:"),
            "spec-input.md must start with `# Spec:` (H1 heuristic)",
        )
        self.assertIn(
            "## Workstreams",
            spec,
            "spec-input.md must contain `## Workstreams` subheader",
        )

    def test_decision_fixture_does_not_match_spec_heuristic(self):
        """forge-decision-input.md (a pure-strategy forge artifact) must NOT match
        the spec heuristic — H1 is `# Decision:` and there is no `## Workstreams`."""
        decision = (FIXTURES / "forge-decision-input.md").read_text(encoding="utf-8")
        self.assertTrue(
            decision.lstrip().startswith("# Decision:"),
            "forge-decision-input.md must start with `# Decision:`",
        )
        self.assertNotIn(
            "## Workstreams",
            decision,
            "forge-decision-input.md must not contain `## Workstreams` (would trigger spec-closure)",
        )

    def test_malformed_spec_does_not_match_spec_heuristic(self):
        """A file with `# Spec:` H1 but no `## Workstreams` subheader is NOT a
        valid spec for closure. The heuristic is AND-gated — both must be
        present. Exercises the negative case for the AND-gate that the
        forge-decision-input.md fixture (decision-only forge artifact, different
        H1) does not cover."""
        malformed = (FIXTURES / "malformed-spec.md").read_text(encoding="utf-8")
        self.assertTrue(
            malformed.lstrip().startswith("# Spec:"),
            "malformed-spec.md must start with `# Spec:` (H1 half of the gate)",
        )
        self.assertNotIn(
            "## Workstreams",
            malformed,
            "malformed-spec.md must lack `## Workstreams` to exercise the negative case",
        )


if __name__ == "__main__":
    unittest.main()
