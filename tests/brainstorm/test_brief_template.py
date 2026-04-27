"""brainstorm produces a brief.md following references/brief-template.md.
The template's section structure must remain stable — drift breaks the brief shape."""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATE = REPO_ROOT / "skills" / "brainstorm" / "references" / "brief-template.md"


REQUIRED_SECTIONS = [
    "Summary",
    "Problem analysis",
    "Research findings",
    "Recommendation",
    "Alternatives considered",
    "Risks",
    "Open questions",
    "Next steps",
]


class TestBriefTemplate(unittest.TestCase):
    def test_template_exists(self):
        self.assertTrue(TEMPLATE.is_file(), "brief-template.md missing")

    def test_template_non_empty(self):
        self.assertGreater(len(TEMPLATE.read_text(encoding="utf-8")), 0)

    def test_required_sections_present(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        for section in REQUIRED_SECTIONS:
            with self.subTest(section=section):
                # Match `## Section` or `### Section` flexibly
                self.assertRegex(text, rf"##+\s+{section}",
                                 f"brief-template missing section: {section}")


if __name__ == "__main__":
    unittest.main()
