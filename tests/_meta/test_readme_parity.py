"""README parity: every skill has a row in the skills table AND a per-skill section."""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import REPO_ROOT, get_skill_dirs  # noqa: E402

README = REPO_ROOT / "README.md"


def _readme_text():
    return README.read_text(encoding="utf-8")


class TestReadmeStructure(unittest.TestCase):
    def test_readme_exists(self):
        self.assertTrue(README.is_file())

    def test_has_skills_section(self):
        self.assertTrue(re.search(r"^## Skills\b", _readme_text(), re.MULTILINE),
                        "README missing '## Skills' section")

    def test_has_install_section(self):
        self.assertTrue(re.search(r"^## Install\b", _readme_text(), re.MULTILINE))


class TestSkillsTableRows(unittest.TestCase):
    """Every skill should have a row in the skills table.
    A row is identified by `[skill-name](#skill-name)` link in pipe-table syntax."""

    def test_every_skill_has_table_row(self):
        text = _readme_text()
        for skill in get_skill_dirs():
            with self.subTest(skill=skill.name):
                # Row format: `| ... | [skill-name](#skill-name) | ... |`
                pattern = rf"\|\s*\[{re.escape(skill.name)}\]\(#{re.escape(skill.name)}\)\s*\|"
                self.assertRegex(text, pattern,
                                 f"{skill.name}: no table row found")


class TestPerSkillSections(unittest.TestCase):
    """Every skill should have its own subsection heading.
    The pattern is `#### skill-name` (under `### <Plugin> Skills`)."""

    def test_every_skill_has_section_heading(self):
        text = _readme_text()
        for skill in get_skill_dirs():
            with self.subTest(skill=skill.name):
                pattern = rf"^####\s+{re.escape(skill.name)}\s*$"
                self.assertTrue(re.search(pattern, text, re.MULTILINE),
                                f"{skill.name}: no '#### {skill.name}' heading")

    def test_anchor_link_resolves(self):
        """Each table-row link `(#skill-name)` should point at an actual heading
        whose GitHub-flavored slug is `skill-name`. Since our headings are exactly
        the skill name, slug == name; we just verify the heading exists (covered
        above), and additionally that the link is well-formed."""
        text = _readme_text()
        for skill in get_skill_dirs():
            with self.subTest(skill=skill.name):
                # Link target appears in the table row
                self.assertIn(f"](#{skill.name})", text,
                              f"{skill.name}: anchor link missing in table")


class TestPluginSectionPresence(unittest.TestCase):
    """Each plugin in marketplace.json maps to a `### <Title> Skills` block."""

    def test_each_plugin_has_section(self):
        import json
        data = json.loads((REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        text = _readme_text()
        for plugin in data["plugins"]:
            # Plugin name "workflow-skills" → "### Workflow Skills"
            title = plugin["name"].replace("-", " ").title()
            with self.subTest(plugin=plugin["name"]):
                pattern = rf"^###\s+{re.escape(title)}\s*$"
                self.assertTrue(re.search(pattern, text, re.MULTILINE),
                                f"plugin {plugin['name']}: missing '### {title}' heading")


if __name__ == "__main__":
    unittest.main()
