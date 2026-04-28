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

    def test_sections_at_h2_level(self):
        """All required sections must be at level 2 (`##`). The brainstorm output
        generator may rely on level depth — bumping a section to ### or # would
        break section parsing without breaking presence checks."""
        import re
        text = TEMPLATE.read_text(encoding="utf-8")
        for section in REQUIRED_SECTIONS:
            with self.subTest(section=section):
                # Strict: line starts with exactly '## ' followed by section
                pattern = rf"^##\s+{re.escape(section)}"
                self.assertTrue(re.search(pattern, text, re.MULTILINE),
                                f"{section}: not at H2 level")

    def test_sections_in_canonical_order(self):
        """Section order is part of the template contract — output downstream may
        rely on Summary appearing first, Next steps last. A reordered template
        breaks consumer expectations silently."""
        import re
        text = TEMPLATE.read_text(encoding="utf-8")
        positions = []
        for section in REQUIRED_SECTIONS:
            m = re.search(rf"^##\s+{re.escape(section)}", text, re.MULTILINE)
            self.assertIsNotNone(m, f"{section}: not found")
            positions.append((m.start(), section))
        sorted_by_pos = [s for _, s in sorted(positions)]
        self.assertEqual(sorted_by_pos, REQUIRED_SECTIONS,
                         f"sections out of order: {sorted_by_pos}")


class TestTemplatePlaceholders(unittest.TestCase):
    """The brainstorm prompt fills placeholders like {topic} and {YYYY-MM-DD}.
    Drift in placeholder syntax breaks the substitution silently — the rendered
    brief would carry the literal placeholder text into the output."""

    def test_topic_placeholder_present(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        # Title must include a `{topic}` placeholder for the brainstorm prompt to fill.
        self.assertIn("{topic}", text,
                      "template missing {topic} placeholder in title")

    def test_date_placeholder_present(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        # Date placeholder uses a `{YYYY-MM-DD}` pattern documented in the prompt.
        self.assertIn("{YYYY-MM-DD}", text,
                      "template missing {YYYY-MM-DD} date placeholder")

    def test_placeholders_only_in_documented_locations(self):
        """A placeholder leaking outside the title/date area would leak into
        the rendered brief. Pin the count of `{` characters in the template
        — drift here surfaces unintended substitution slots."""
        text = TEMPLATE.read_text(encoding="utf-8")
        # The template uses `{topic}`, `{YYYY-MM-DD}`, and `[bracket prose hints]`
        # only. Curly braces should appear ≤4 times (open + close × 2).
        curly_count = text.count("{")
        self.assertLessEqual(curly_count, 4,
                             f"unexpected placeholder count ({curly_count}) — "
                             "audit for stray substitution slots")


if __name__ == "__main__":
    unittest.main()
