"""agent-creator SKILL.md body — section ordering, table integrity, embedded
example validity. Catches regressions where sections get reordered, the
configuration table loses a frontmatter field, or the embedded subagent
example drifts away from the spec it teaches."""

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "skills" / "brand-voice" / "scripts"))

from utils import parse_yaml_minimal, split_frontmatter  # noqa: E402

SKILL_MD = REPO_ROOT / "skills" / "agent-creator" / "SKILL.md"


def _body():
    return SKILL_MD.read_text(encoding="utf-8")


CANONICAL_SECTIONS = [
    "## Quick Start",
    "## Scope and Priority",
    "## Configuration",
    "## Execution Model",
    "## System Prompt Guidelines",
    "## Background Execution",
    "## Management",
    "## Reference",
    "## Success Criteria",
    "## See also",
]


class TestSectionOrder(unittest.TestCase):
    """The canonical section order encodes the reading flow — Quick Start
    before deep configuration, Reference after concept teaching. Reordering
    silently degrades onboarding."""

    def test_each_section_present(self):
        body = _body()
        for section in CANONICAL_SECTIONS:
            with self.subTest(section=section):
                self.assertIn(section, body, f"missing section: {section}")

    def test_sections_in_canonical_order(self):
        body = _body()
        positions = []
        for section in CANONICAL_SECTIONS:
            idx = body.find(section)
            self.assertNotEqual(idx, -1, f"section missing: {section}")
            positions.append((idx, section))
        actual = [s for _, s in sorted(positions)]
        self.assertEqual(
            actual, CANONICAL_SECTIONS,
            f"sections out of order:\n  expected: {CANONICAL_SECTIONS}\n  got: {actual}",
        )


class TestConfigurationTable(unittest.TestCase):
    """The Configuration section ships a Markdown table of frontmatter
    fields. The fields are the public contract — silently dropping one
    (e.g., `permissionMode`) leaves users without guidance."""

    REQUIRED_FIELDS = [
        "name", "description", "tools", "disallowedTools", "model",
        "permissionMode", "maxTurns", "skills", "mcpServers", "hooks",
        "memory", "background", "effort", "isolation", "color", "initialPrompt",
    ]

    def test_each_field_documented(self):
        body = _body()
        # Look only inside the Configuration section to avoid matching
        # mentions in other sections.
        m = re.search(
            r"## Configuration\b(.*?)(?=^## |\Z)",
            body, re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(m, "## Configuration section missing")
        section = m.group(1)
        for field in self.REQUIRED_FIELDS:
            with self.subTest(field=field):
                self.assertIn(
                    f"`{field}`", section,
                    f"frontmatter field `{field}` not documented in Configuration table",
                )


class TestNoXmlInBody(unittest.TestCase):
    """Per agentskills-spec, frontmatter must not contain XML angle brackets.
    By extension, the SKILL.md body in this repo uses plain Markdown — no
    `<objective>`, `<workflow>`, `<rules>` containers. (HTML inside fenced
    code blocks is fine — that's user content, not skill structure.)"""

    SUSPECT_TAGS = (
        "<objective>", "<workflow>", "<rules>", "<context>", "<task>",
        "<instructions>", "<output>", "<role>",
    )

    def test_body_has_no_xml_structure_tags(self):
        body = _body()
        # Strip fenced code blocks before searching — those may legitimately
        # contain XML examples (e.g. showing how an agent prompt could use tags).
        without_fences = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
        for tag in self.SUSPECT_TAGS:
            with self.subTest(tag=tag):
                self.assertNotIn(
                    tag, without_fences.lower(),
                    f"SKILL.md body uses XML structure tag {tag} — use Markdown instead",
                )


class TestEmbeddedExampleIsValid(unittest.TestCase):
    """The Quick Start section embeds an example subagent (`code-reviewer`)
    inside a fenced ```markdown block. That example IS the teaching artifact
    — if its frontmatter is malformed, every reader who copies it gets a
    broken subagent. Pin its shape."""

    def _extract_first_markdown_example(self):
        body = _body()
        # Find the first ```markdown ... ``` fenced block.
        m = re.search(r"```markdown\n(.*?)```", body, re.DOTALL)
        if not m:
            return None
        return m.group(1)

    def test_example_present(self):
        self.assertIsNotNone(
            self._extract_first_markdown_example(),
            "no ```markdown example block found",
        )

    def test_example_has_valid_frontmatter(self):
        example = self._extract_first_markdown_example()
        self.assertIsNotNone(example, "no example to validate")
        fm_text, body = split_frontmatter(example)
        self.assertIsNotNone(fm_text, "example has no YAML frontmatter")
        fm = parse_yaml_minimal(fm_text)
        # name is required and must be kebab-case (lowercase + hyphens).
        self.assertIn("name", fm)
        self.assertRegex(
            fm["name"], r"^[a-z][a-z0-9-]*$",
            f"example name '{fm['name']}' is not kebab-case",
        )
        # description is required and substantive (not a stub).
        self.assertIn("description", fm)
        self.assertGreater(
            len(fm["description"]), 30,
            "example description too short to be useful as a template",
        )

    def test_example_body_not_empty(self):
        """A frontmatter-only example would teach the reader to ship a
        no-op agent. The body must include an instruction beyond a heading."""
        example = self._extract_first_markdown_example()
        self.assertIsNotNone(example, "no example to validate")
        _, body = split_frontmatter(example)
        # At minimum a sentence (>50 chars) of system-prompt guidance.
        body_stripped = body.strip()
        self.assertGreater(
            len(body_stripped), 50,
            "example body is empty or too short — no system prompt to copy",
        )


class TestToolRestrictionPatterns(unittest.TestCase):
    """The Configuration section calls out four explicit tool-restriction
    patterns (allowlist, denylist, agent-restriction, both). The patterns
    are how readers learn least-privilege — drop one and the lesson degrades."""

    REQUIRED_PATTERNS = [
        ("read-only", "tools: Read"),
        ("denylist", "disallowedTools: Write"),
        ("both-rule", "disallowedTools` applied first"),
    ]

    def test_each_restriction_pattern_present(self):
        body = _body()
        for label, needle in self.REQUIRED_PATTERNS:
            with self.subTest(pattern=label):
                self.assertIn(
                    needle, body,
                    f"tool-restriction pattern '{label}' missing — needle: {needle!r}",
                )


if __name__ == "__main__":
    unittest.main()
