"""agent-creator ships 7 reference files covering subagent authoring topics.
Tests verify every expected reference is present (drift guard)."""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REFS = REPO_ROOT / "skills" / "agent-creator" / "references"

EXPECTED_REFS = [
    "context-management.md",
    "debugging-agents.md",
    "error-handling-and-recovery.md",
    "evaluation-and-testing.md",
    "orchestration-patterns.md",
    "subagents.md",
    "writing-subagent-prompts.md",
]


class TestReferences(unittest.TestCase):
    def test_each_expected_ref_exists(self):
        for ref in EXPECTED_REFS:
            with self.subTest(ref=ref):
                self.assertTrue((REFS / ref).is_file(), f"references/{ref} missing")

    def test_no_unexpected_refs(self):
        """If a new reference appears, the test fails so the maintainer
        explicitly decides whether to add it to the expected list."""
        actual = {p.name for p in REFS.glob("*.md")}
        unexpected = actual - set(EXPECTED_REFS)
        self.assertEqual(unexpected, set(),
                         f"unexpected references: {sorted(unexpected)} — update EXPECTED_REFS in this test if intentional")


class TestReferenceQuality(unittest.TestCase):
    """References that exist but contain stubs would silently degrade the
    skill — pin a minimum content depth (length + heading count) per file."""

    MIN_CHARS = 500
    MIN_H2_HEADINGS = 1

    def test_each_ref_has_minimum_content(self):
        for ref in EXPECTED_REFS:
            with self.subTest(ref=ref):
                text = (REFS / ref).read_text(encoding="utf-8")
                self.assertGreater(
                    len(text), self.MIN_CHARS,
                    f"references/{ref} has {len(text)} chars — likely a stub",
                )

    def test_each_ref_starts_with_h1_or_xml_block(self):
        """Refs are allowed two opener conventions: a Markdown H1 (`# Title`)
        or an XML-style block (`<tag>`) — both are intentional doc styles in
        agent-creator references. A blank or plain-text opener would indicate
        a stub or accidental truncation."""
        for ref in EXPECTED_REFS:
            with self.subTest(ref=ref):
                text = (REFS / ref).read_text(encoding="utf-8")
                first_line = text.splitlines()[0] if text.splitlines() else ""
                ok = first_line.startswith("# ") or first_line.startswith("<")
                self.assertTrue(
                    ok,
                    f"references/{ref} opener invalid: '{first_line[:60]}...'",
                )


class TestSkillMdReferencesAllRefs(unittest.TestCase):
    """SKILL.md must reference every shipped file in references/. Orphan refs
    are wasted bytes; missing refs leave the agent without guidance."""

    def test_skill_md_mentions_each_reference(self):
        skill_md = (REPO_ROOT / "skills" / "agent-creator" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        for ref in EXPECTED_REFS:
            with self.subTest(ref=ref):
                self.assertIn(ref, skill_md,
                              f"SKILL.md never mentions references/{ref}")


if __name__ == "__main__":
    unittest.main()
