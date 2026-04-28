"""Pipeline contract: award-design → design-system.

award-design produces DESIGN.md (Google's open standard — YAML frontmatter
with design tokens + 8 ordered prose sections). design-system governs that
file via audit/diff/export/spec/migrate/init subcommands. Schema drift
between producer and consumer is the failure mode this cluster prevents.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _contracts import read_skill_md  # noqa: E402


class TestProducerCommitsToGoogleStandard(unittest.TestCase):
    def test_award_design_references_google_standard(self):
        text = read_skill_md("award-design")
        self.assertIn("DESIGN.md", text)
        # Producer must explicitly reference the Google standard so changes
        # cannot drift to a custom format silently.
        self.assertRegex(text.lower(), r"google.*design\.md|google design")

    def test_award_design_lists_eight_canonical_sections(self):
        """The 8 prose sections in the Google standard (Overview, Colors,
        Typography, Layout, Elevation & Depth, Shapes, Components, Do's and
        Don'ts) must be enumerated so the consumer's audit has a fixed target."""
        text = read_skill_md("award-design")
        for section in (
            "Overview",
            "Colors",
            "Typography",
            "Layout",
            "Components",
        ):
            with self.subTest(section=section):
                self.assertIn(section, text,
                              f"Google-standard section not documented: {section}")


class TestConsumerHandoff(unittest.TestCase):
    def test_design_system_documents_award_design_handoff(self):
        text = read_skill_md("design-system")
        self.assertIn("DESIGN.md", text)
        # design-system must document delegation to award-design when no
        # DESIGN.md exists — pins the empty-state handoff.
        self.assertIn("award-design", text)


class TestPathsAutoActivation(unittest.TestCase):
    """design-system's SKILL.md `paths:` must include DESIGN.md so editing
    that file auto-triggers the skill (the auto-activation contract)."""

    def test_design_system_paths_includes_design_md(self):
        text = read_skill_md("design-system")
        # The frontmatter `paths:` block lists DESIGN.md as an auto-trigger.
        self.assertIn("DESIGN.md", text)
        # Also expect the `paths:` key in YAML frontmatter.
        self.assertIn("paths:", text)


if __name__ == "__main__":
    unittest.main()
