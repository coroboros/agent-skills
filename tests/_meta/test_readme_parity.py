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

if __name__ == "__main__":
    unittest.main()
