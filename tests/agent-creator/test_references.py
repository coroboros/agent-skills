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


if __name__ == "__main__":
    unittest.main()
