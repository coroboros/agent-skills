"""Tests for the plan-step guardrails — Challenge mini-phase + Surgical-scope check.

The Challenge mini-phase is an inline artifact write at step-02 § 4a (no
user gate). The surgical-scope check at § 4b is advisory and never blocks.
"""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
STEP_02 = REPO_ROOT / "skills" / "apex" / "steps" / "step-02-plan.md"
TEMPLATE_02 = REPO_ROOT / "skills" / "apex" / "templates" / "02-plan.md"


class TestChallengePhase(unittest.TestCase):
    def setUp(self):
        self.step_02 = STEP_02.read_text(encoding="utf-8")
        self.template_02 = TEMPLATE_02.read_text(encoding="utf-8")

    def test_step_02_has_challenge_subsection(self):
        """step-02-plan.md contains the Challenge mini-phase subsection."""
        self.assertIn(
            "### 4a. Challenge the plan",
            self.step_02,
            "Challenge mini-phase subsection must appear in step-02-plan.md",
        )

    def test_step_02_has_surgical_scope_check(self):
        """step-02-plan.md contains the surgical-scope check subsection."""
        self.assertIn(
            "### 4b. Surgical-scope check",
            self.step_02,
            "Surgical-scope check subsection must appear in step-02-plan.md",
        )

    def test_challenge_documents_premortem_and_alternative(self):
        """Challenge subsection documents both a premortem and an alternative."""
        challenge_start = self.step_02.find("### 4a. Challenge the plan")
        challenge_end = self.step_02.find("### 4b.", challenge_start)
        self.assertGreater(challenge_start, 0, "Challenge anchor missing")
        self.assertGreater(challenge_end, challenge_start, "Challenge body not bounded")
        body = self.step_02[challenge_start:challenge_end]
        self.assertIn("Premortem", body, "Premortem bullet must be documented")
        self.assertIn("Alternative", body, "Alternative bullet must be documented")

    def test_challenge_heading_disavows_user_gate(self):
        """Challenge subsection heading itself encodes the rule —
        '(inline, no user gate)'. That phrase IS the contract."""
        self.assertIn(
            "### 4a. Challenge the plan (inline, no user gate)",
            self.step_02,
            "Challenge heading must include '(inline, no user gate)'",
        )

    def test_challenge_does_not_invoke_ask_user_question_yaml(self):
        """Challenge subsection must NOT carry the apex AskUserQuestion
        invocation pattern (a YAML `questions:` block). Mention of the literal
        word in prose disavowing it is fine; an actual YAML invocation is not."""
        challenge_start = self.step_02.find("### 4a. Challenge the plan")
        challenge_end = self.step_02.find("### 4b.", challenge_start)
        body = self.step_02[challenge_start:challenge_end]
        # The apex skill pattern for an AskUserQuestion call is:
        #   ```yaml
        #   questions:
        #     - header: "..."
        # Detect by the structural YAML key + indented `- header:` anchor.
        self.assertNotIn(
            "questions:\n  - header:",
            body,
            "Challenge subsection must NOT carry a YAML AskUserQuestion invocation",
        )

    def test_surgical_scope_thresholds_documented(self):
        """Surgical-scope check documents all three thresholds."""
        scope_start = self.step_02.find("### 4b. Surgical-scope check")
        scope_end = self.step_02.find("### 5.", scope_start)
        body = self.step_02[scope_start:scope_end]
        self.assertIn("> 5", body, "Files threshold (>5) must be documented")
        self.assertIn("> 2", body, "Systems threshold (>2) must be documented")
        self.assertIn("Cross-cutting", body, "Cross-cutting concerns must be documented")

    def test_surgical_scope_is_advisory_not_blocking(self):
        """Surgical-scope check explicitly states it is advisory and never blocks."""
        scope_start = self.step_02.find("### 4b. Surgical-scope check")
        scope_end = self.step_02.find("### 5.", scope_start)
        body = self.step_02[scope_start:scope_end].lower()
        self.assertIn("advisory", body, "Surgical-scope check must be documented as advisory")
        self.assertTrue(
            "never blocks" in body or "advisory only" in body,
            "Surgical-scope check must state it never blocks",
        )

    def test_template_carries_placeholders(self):
        """templates/02-plan.md carries placeholders for both new sections."""
        self.assertIn("## Challenge the plan", self.template_02)
        self.assertIn("## Surgical-scope check", self.template_02)


if __name__ == "__main__":
    unittest.main()
