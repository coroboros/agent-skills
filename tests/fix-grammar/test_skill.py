"""fix-grammar is a pure-prompt skill — frontmatter contract guards regression."""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "skills" / "brand-voice" / "scripts"))

from utils import parse_yaml_minimal, split_frontmatter  # noqa: E402

SKILL_MD = REPO_ROOT / "skills" / "fix-grammar" / "SKILL.md"


def _frontmatter():
    text = SKILL_MD.read_text(encoding="utf-8")
    fm_text, _ = split_frontmatter(text)
    return parse_yaml_minimal(fm_text) if fm_text else {}


class TestFixGrammarFrontmatter(unittest.TestCase):
    def test_argument_hint_present(self):
        fm = _frontmatter()
        hint = fm.get("argument-hint", "")
        self.assertIn("file-path", hint.lower(),
                      "argument-hint should mention file-path")

    def test_allowed_tools_includes_read_and_edit(self):
        """fix-grammar edits files in place — must declare Read and Edit access."""
        fm = _frontmatter()
        tools = fm.get("allowed-tools", "") or ""
        self.assertIn("Read", tools)
        self.assertIn("Edit", tools)

    def test_model_haiku(self):
        """fix-grammar uses haiku per repo convention for deterministic flows."""
        fm = _frontmatter()
        self.assertEqual(fm.get("model"), "haiku")


class TestFixGrammarBody(unittest.TestCase):
    """The body sections — Rules, Workflow, Output — encode the skill's
    behavior. Missing or mis-shaped sections silently degrade the result."""

    def _body(self):
        return SKILL_MD.read_text(encoding="utf-8")

    def test_rules_section_lists_constraints(self):
        body = self._body()
        self.assertIn("## Rules", body)
        # The critical do-not constraints must be enumerated. Tolerate
        # markdown emphasis (`**Do not** rephrase`) by matching loosely.
        body_lower = body.lower()
        self.assertIn("rephrase", body_lower,
                      "Rules must forbid rephrasing")
        self.assertIn("translate", body_lower,
                      "Rules must forbid translation")
        # Code blocks and frontmatter must be preserved.
        self.assertIn("code blocks", body_lower)
        self.assertIn("frontmatter", body_lower)

    def test_workflow_documents_single_and_multi_file(self):
        body = self._body()
        self.assertIn("## Workflow", body)
        self.assertIn("Single file", body)
        self.assertIn("Multiple files", body)
        # Multi-file is parallelised via subagents — the parallelism call-out
        # is part of the contract and not optional.
        self.assertRegex(body.lower(), r"parallel|subagent")

    def test_output_format_documented(self):
        body = self._body()
        self.assertIn("## Output", body)
        # Output format pins the per-file line shape.
        self.assertIn("corrections", body)


if __name__ == "__main__":
    unittest.main()
