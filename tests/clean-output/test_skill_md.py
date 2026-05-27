"""SKILL.md doc-level invariants for clean-output.

The skill's `-l` / `-d` resolution rule lives only in `SKILL.md` natural
language — `list_artifacts.py` enumerates and `delete_artifact.py` deletes,
but neither sees the slash-skill flags. Pin the doc so the contract cannot
drift silently.
"""

from __future__ import annotations

import unittest
from pathlib import Path

_SKILL_MD = (
    Path(__file__).resolve().parents[2] / "skills" / "clean-output" / "SKILL.md"
)


class TestCleanOutputSkillMd(unittest.TestCase):
    def setUp(self) -> None:
        self.text = _SKILL_MD.read_text(encoding="utf-8")

    def test_l_d_conflict_resolution_documented(self) -> None:
        """SKILL.md must name the `-l` / `-d` conflict and state `-l` wins.

        The slash-skill workflow chooses the resolution; no script enforces
        it, so the only check is structural on the doc.
        """
        self.assertIn(
            "`-l` and `-d` conflict",
            self.text,
            "Rules section must name the conflict explicitly",
        )
        self.assertIn(
            "`-l` always wins",
            self.text,
            "Resolution must spell out that `-l` wins (read-only fail-safe)",
        )
        self.assertIn(
            "Surface a one-line warning",
            self.text,
            "Workflow must surface a warning before falling back to listing mode",
        )

    def test_l_d_resolution_pinned_to_this_test(self) -> None:
        """The Rules entry must back-reference this test so a doc revert
        without a test update fails loud.
        """
        self.assertIn(
            "tests/clean-output/test_skill_md.py",
            self.text,
            "Rules entry must reference this test by path",
        )

    def test_ask_user_question_cap_resolution_documented(self) -> None:
        """SKILL.md must spell out the >4-candidate paging strategy for
        step 6's multi-select. The harness caps `AskUserQuestion` at 4
        options; a candidate list of 5+ files would silently break the
        call without an explicit paging rule.
        """
        self.assertIn(
            "4-option cap",
            self.text,
            "Rules must name the AskUserQuestion 4-option cap",
        )
        self.assertIn(
            "page",
            self.text,
            "Resolution must spell out paging 4-at-a-time",
        )
        self.assertIn(
            "accumulating selections",
            self.text,
            "Paging must accumulate selections across pages before deletion",
        )


if __name__ == "__main__":
    unittest.main()
