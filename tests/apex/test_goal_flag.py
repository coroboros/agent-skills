"""Tests for /goal integration via -g flag.

Verifies SKILL.md flag tables + argument-hint + Compatibility section,
step-00 parsing + headless auto-detection, step-04 /goal emission template.

Test approach. Apex is a prose-driven skill — no `apex.sh` / `apex.py`
entrypoint to subprocess-invoke. Per `.agents/rules/skill-authoring.md`
§ Testing, the convention for prompt-driven skills is structural tests
over runtime subprocess tests. The assertions below verify the documented
contracts (flag tables, parsing rules, headless detection logic, /goal
template shape). Runtime emission of the directive is exercised by
actual `/apex -g` invocations in user sessions, not by simulated
subprocess calls that wouldn't actually exercise apex.
"""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_MD = REPO_ROOT / "skills" / "apex" / "SKILL.md"
STEP_00 = REPO_ROOT / "skills" / "apex" / "steps" / "step-00-init.md"
STEP_04 = REPO_ROOT / "skills" / "apex" / "steps" / "step-04-examine.md"


class TestGoalFlag(unittest.TestCase):
    def setUp(self):
        self.skill_md = SKILL_MD.read_text(encoding="utf-8")
        self.step_00 = STEP_00.read_text(encoding="utf-8")
        self.step_04 = STEP_04.read_text(encoding="utf-8")

    def test_argument_hint_includes_g(self):
        """argument-hint includes [-g]."""
        for line in self.skill_md.splitlines():
            if line.startswith("argument-hint:"):
                self.assertIn("[-g]", line, "argument-hint must include [-g]")
                return
        self.fail("argument-hint line not found in SKILL.md")

    def test_enable_flag_table_has_g(self):
        """SKILL.md Enable flags table includes -g/--goal row."""
        self.assertRegex(
            self.skill_md,
            r"\|\s*`-g`\s*\|\s*`--goal`\s*\|",
            "SKILL.md Enable flags table must include -g/--goal row",
        )

    def test_disable_flag_table_has_G(self):
        """SKILL.md Disable flags table includes -G/--no-goal row."""
        self.assertRegex(
            self.skill_md,
            r"\|\s*`-G`\s*\|\s*`--no-goal`\s*\|",
            "SKILL.md Disable flags table must include -G/--no-goal row",
        )

    def test_state_variables_declare_goal_mode(self):
        """SKILL.md State Variables table includes {goal_mode}."""
        self.assertIn("{goal_mode}", self.skill_md)

    def test_compatibility_section_documents_version_floor(self):
        """SKILL.md ## Compatibility section mentions Claude Code v2.1.139."""
        self.assertIn("## Compatibility", self.skill_md)
        self.assertIn("v2.1.139", self.skill_md)

    def test_compatibility_documents_transcript_only_constraint(self):
        """Compatibility section warns about the transcript-only evaluator."""
        idx_compat = self.skill_md.find("## Compatibility")
        idx_next = self.skill_md.find("\n## ", idx_compat + 1)
        body = self.skill_md[idx_compat:idx_next].lower()
        self.assertIn("transcript", body, "Compatibility must mention the transcript-only evaluator")

    def test_step_00_parses_g_and_G(self):
        """step-00-init.md parses -g/-G and sets {goal_mode}."""
        self.assertIn("-g or --goal", self.step_00)
        self.assertIn("-G or --no-goal", self.step_00)
        self.assertIn("{goal_mode}", self.step_00)

    def test_step_00_has_headless_auto_detection(self):
        """step-00-init.md describes headless auto-detection logic."""
        self.assertIn("Headless auto-detection", self.step_00)
        self.assertIn("CLAUDE_NONINTERACTIVE", self.step_00)
        self.assertIn("TTY", self.step_00)
        self.assertIn("auto-on", self.step_00)
        self.assertIn("Do not probe the TTY", self.step_00,
                      "a tool shell is never a TTY — the probe must stay banned as a signal")
        self.assertNotIn("! [ -t 0 ]", self.step_00)

    def test_step_04_emits_goal_directive(self):
        """step-04-examine.md emits the /goal directive in a new § 0 sub-step."""
        self.assertIn("### 0. Emit /goal directive", self.step_04)
        self.assertIn("/goal All AC verified", self.step_04)
        self.assertNotIn("Stop after 15 turns", self.step_04)

    def test_goal_directive_requires_verbatim_commands(self):
        """The /goal template forces verbatim command output, not paraphrases."""
        idx_goal = self.step_04.find("### 0. Emit /goal directive")
        idx_next = self.step_04.find("### 1.", idx_goal)
        body = self.step_04[idx_goal:idx_next]
        self.assertIn("actual command output", body.lower())

    def test_goal_directive_handles_empty_ac(self):
        """Empty AC fall back to a documented placeholder."""
        self.assertIn(
            "task trivially completes when checks pass",
            self.step_04,
            "Empty-AC fallback must be documented in step-04",
        )

    def test_init_summary_includes_goal_mode(self):
        """step-00 references {goal_mode} both in parsing and in the init summary."""
        count = self.step_00.count("{goal_mode}")
        self.assertGreaterEqual(
            count,
            2,
            "{goal_mode} must appear in parsing AND the summary table (>= 2 occurrences)",
        )


if __name__ == "__main__":
    unittest.main()
