"""ultrapex — the judgment-first contract documented in SKILL.md must remain stable."""

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "skills" / "brand-voice" / "scripts"))

from utils import parse_yaml_minimal, split_frontmatter  # noqa: E402

SKILL_MD = REPO_ROOT / "skills" / "ultrapex" / "SKILL.md"


def _frontmatter():
    text = SKILL_MD.read_text(encoding="utf-8")
    fm_text, _ = split_frontmatter(text)
    return parse_yaml_minimal(fm_text) if fm_text else {}


def _body():
    return SKILL_MD.read_text(encoding="utf-8")


class TestUltrapexFrontmatter(unittest.TestCase):
    def test_model_unset_inherits_session(self):
        """model stays unset — ultrapex exists precisely so frontier sessions run at full capability."""
        self.assertIsNone(_frontmatter().get("model"))

    def test_effort_unset(self):
        """effort stays unset — the session owns the dial; a pin over-deliberates on frontier models."""
        self.assertIsNone(_frontmatter().get("effort"))

    def test_coupled_compatibility_tier(self):
        """ultrapex dispatches subagents — it belongs to the harness-coupled tier.
        The exact string is pinned repo-wide by tests/_meta/test_skill_frontmatter.py."""
        self.assertIsNotNone(_frontmatter().get("compatibility"))

    def test_routes_to_apex_below_class(self):
        """when_to_use must keep the /apex routing — apex is the workhorse below Fable-class."""
        self.assertIn("/apex", _frontmatter().get("when_to_use", ""))


class TestUltrapexContract(unittest.TestCase):
    def test_model_scope_section_present(self):
        """The Model scope section is the self-scoping mechanism."""
        body = _body()
        self.assertTrue(re.search(r"^## Model scope\s*$", body, re.MULTILINE))
        self.assertIn("use `/apex`", body.split("## Model scope")[1].split("##")[0])

    def test_adversarial_verification_is_explicit(self):
        """The explicit word is load-bearing: the contract itself names adversarial
        verification and refuters — not just the injected canonical block."""
        contract = _body().split("## The contract")[1].split("## Shape")[0]
        self.assertIn("Verify adversarially", contract)
        self.assertIn("refute", contract)

    def test_subagent_degradation_clause(self):
        self.assertIn("No subagents in your harness", _body())

    def test_output_path_convention(self):
        """Single-file producer per repo conventions."""
        self.assertIn("~/.claude/output/{project}/ultrapex/ultrapex-{slug}.md", _body())

    def test_no_raw_skill_dir_env(self):
        """ultrapex ships no scripts; nothing should reference the env var at all."""
        self.assertNotIn("CLAUDE_SKILL_DIR", _body())

    def test_size_budget(self):
        self.assertLess(len(_body().splitlines()), 500, "Agent Skills spec size guidance")


if __name__ == "__main__":
    unittest.main()
