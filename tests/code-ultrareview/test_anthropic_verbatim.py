"""Tests for references/anthropic-verbatim.md byte-for-byte parity with the
Anthropic `code-review` plugin source file.

The verbatim blocks must match the upstream source character-for-character so
that Phase 4 Haiku validators apply the same rubric as Anthropic's own
plugin. If the upstream source drifts, these tests fail and the verbatim
doc must be re-synced (and the `Last verified` date bumped).

The upstream source lives outside this repo at
    ~/Desktop/Dev/coroboros/sources/claude-plugins-official/plugins/code-review/commands/code-review.md
Tests skip gracefully when the source file is not present (CI / fresh
clones without the sibling sources tree).
"""

from __future__ import annotations

import os
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
VERBATIM_DOC = (
    REPO_ROOT / "skills" / "code-ultrareview" / "references" / "anthropic-verbatim.md"
)


def _source_path() -> Path | None:
    """Locate the upstream source file. Walk up from REPO_ROOT looking for
    a sibling `sources/claude-plugins-official/...` directory, then fall
    back to `~/Desktop/Dev/coroboros/...`."""
    candidates = [
        REPO_ROOT.parent / "sources" / "claude-plugins-official" / "plugins"
            / "code-review" / "commands" / "code-review.md",
        Path(os.path.expanduser("~/Desktop/Dev/coroboros/sources/claude-plugins-official/plugins/code-review/commands/code-review.md")),
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None


# Canonical blocks — both the upstream source AND our verbatim doc must
# contain these substrings. If either drifts, the test fails.

RUBRIC_BLOCK = """\
   a. 0: Not confident at all. This is a false positive that doesn't stand up to light scrutiny, or is a pre-existing issue.
   b. 25: Somewhat confident. This might be a real issue, but may also be a false positive. The agent wasn't able to verify that it's a real issue. If the issue is stylistic, it is one that was not explicitly called out in the relevant CLAUDE.md.
   c. 50: Moderately confident. The agent was able to verify this is a real issue, but it might be a nitpick or not happen very often in practice. Relative to the rest of the PR, it's not very important.
   d. 75: Highly confident. The agent double checked the issue, and verified that it is very likely it is a real issue that will be hit in practice. The existing approach in the PR is insufficient. The issue is very important and will directly impact the code's functionality, or it is an issue that is directly mentioned in the relevant CLAUDE.md.
   e. 100: Absolutely certain. The agent double checked the issue, and confirmed that it is definitely a real issue, that will happen frequently in practice. The evidence directly confirms this."""

# Note: "compily" is an upstream typo preserved deliberately — byte-for-byte parity.
HIGH_SIGNAL_BLOCK = """\
   a. Agent #1: Audit the changes to make sure they compily with the CLAUDE.md. Note that CLAUDE.md is guidance for Claude as it writes code, so not all instructions will be applicable during code review.
   b. Agent #2: Read the file changes in the pull request, then do a shallow scan for obvious bugs. Avoid reading extra context beyond the changes, focusing just on the changes themselves. Focus on large bugs, and avoid small issues and nitpicks. Ignore likely false positives.
   c. Agent #3: Read the git blame and history of the code modified, to identify any bugs in light of that historical context
   d. Agent #4: Read previous pull requests that touched these files, and check for any comments on those pull requests that may also apply to the current pull request.
   e. Agent #5: Read code comments in the modified files, and make sure the changes in the pull request comply with any guidance in the comments."""

FALSE_POSITIVES_BLOCK = """\
- Pre-existing issues
- Something that looks like a bug but is not actually a bug
- Pedantic nitpicks that a senior engineer wouldn't call out
- Issues that a linter, typechecker, or compiler would catch (eg. missing or incorrect imports, type errors, broken tests, formatting issues, pedantic style issues like newlines). No need to run these build steps yourself -- it is safe to assume that they will be run separately as part of CI.
- General code quality issues (eg. lack of test coverage, general security issues, poor documentation), unless explicitly required in CLAUDE.md
- Issues that are called out in CLAUDE.md, but explicitly silenced in the code (eg. due to a lint ignore comment)
- Changes in functionality that are likely intentional or are directly related to the broader change
- Real issues, but on lines that the user did not modify in their pull request"""

AGENT_ASSUMPTION_BLOCK = (
    "Do not check build signal or attempt to build or typecheck the app. "
    "These will run separately, and are not relevant to your code review."
)


class TestVerbatimDocContainsAllBlocks(unittest.TestCase):
    """Our verbatim doc must contain each canonical block. Run unconditionally —
    no skip — because this is a contract on our own file."""

    @classmethod
    def setUpClass(cls):
        cls.text = VERBATIM_DOC.read_text(encoding="utf-8")

    def test_doc_exists(self):
        self.assertTrue(VERBATIM_DOC.is_file(),
                        "references/anthropic-verbatim.md missing")

    def test_doc_contains_rubric(self):
        self.assertIn(RUBRIC_BLOCK, self.text,
                      "0-100 rubric block missing or modified in verbatim doc")

    def test_doc_contains_high_signal_criteria(self):
        self.assertIn(HIGH_SIGNAL_BLOCK, self.text,
                      "HIGH SIGNAL criteria block missing or modified")

    def test_doc_contains_false_positives(self):
        self.assertIn(FALSE_POSITIVES_BLOCK, self.text,
                      "false-positive taxonomy block missing or modified")

    def test_doc_contains_agent_assumption_rule(self):
        self.assertIn(AGENT_ASSUMPTION_BLOCK, self.text,
                      "agent assumption rule missing or modified")

    def test_doc_preserves_compily_typo(self):
        """Upstream has 'compily' (typo). Our copy must preserve it verbatim.
        Pinning this explicitly so a 'cleanup' PR cannot silently fix it."""
        self.assertIn("compily", self.text,
                      "Upstream 'compily' typo must be preserved verbatim")


class TestUpstreamSourceParity(unittest.TestCase):
    """The same canonical blocks must appear in the upstream source. Skip
    gracefully when the upstream tree is not available (CI / fresh clones)."""

    @classmethod
    def setUpClass(cls):
        cls.source_path = _source_path()
        if cls.source_path is None:
            return
        cls.source_text = cls.source_path.read_text(encoding="utf-8")

    def setUp(self):
        if self.source_path is None:
            self.skipTest("claude-plugins-official sources tree not present")

    def test_source_contains_rubric(self):
        self.assertIn(RUBRIC_BLOCK, self.source_text,
                      "0-100 rubric drifted upstream — re-sync verbatim doc")

    def test_source_contains_high_signal_criteria(self):
        self.assertIn(HIGH_SIGNAL_BLOCK, self.source_text,
                      "HIGH SIGNAL criteria drifted upstream — re-sync verbatim doc")

    def test_source_contains_false_positives(self):
        self.assertIn(FALSE_POSITIVES_BLOCK, self.source_text,
                      "false-positive taxonomy drifted upstream — re-sync verbatim doc")

    def test_source_contains_agent_assumption_rule(self):
        self.assertIn(AGENT_ASSUMPTION_BLOCK, self.source_text,
                      "agent assumption rule drifted upstream — re-sync verbatim doc")


class TestVerbatimDocStructure(unittest.TestCase):
    """Each block carries a `### Source` line + a `Last verified:` date."""

    @classmethod
    def setUpClass(cls):
        cls.text = VERBATIM_DOC.read_text(encoding="utf-8")

    def test_has_four_source_attributions(self):
        # One per block: rubric, HIGH SIGNAL, false-positive, agent-assumption.
        count = self.text.count("### Source")
        self.assertGreaterEqual(count, 4,
                                f"expected ≥4 '### Source' attributions, got {count}")

    def test_has_last_verified_dates(self):
        # Every Source attribution must carry a date.
        count = self.text.count("Last verified:")
        self.assertGreaterEqual(count, 4,
                                f"expected ≥4 'Last verified:' lines, got {count}")

    def test_cites_upstream_path(self):
        self.assertIn(
            "sources/claude-plugins-official/plugins/code-review/commands/code-review.md",
            self.text,
        )


if __name__ == "__main__":
    unittest.main()
