"""Structural test: every lens brief carries a `## Repo-kind branches` section.

Four lenses (`bugs-drift`, `docs-version`, `tests-blindspots`,
`coherence-graph`) have real branch tables; three (`rules`, `derivation`,
`prose-hygiene`) carry an explicit `No branches — <reason>` one-liner. Both
shapes count as "present"; the test enforces presence, uniqueness, and the
canonical kind value space.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REFERENCES_DIR = REPO_ROOT / "skills" / "code-ultrareview" / "references"

LENS_FILES = (
    "lens-rules.md",
    "lens-bugs-drift.md",
    "lens-docs-version.md",
    "lens-tests-blindspots.md",
    "lens-coherence-graph.md",
    "lens-derivation.md",
    "lens-prose-hygiene.md",
)

# Lenses that have real per-kind branching content (table or per-sub-graph
# table). The other three carry a "No branches — <reason>" one-liner.
LENSES_WITH_REAL_BRANCHES = (
    "lens-bugs-drift.md",
    "lens-docs-version.md",
    "lens-tests-blindspots.md",
    "lens-coherence-graph.md",
)

VALID_KINDS = (
    "skills", "app", "library", "docs", "monorepo",
    "python", "rust", "go", "unknown",
)


def _read(lens_file: str) -> str:
    return (REFERENCES_DIR / lens_file).read_text(encoding="utf-8")


def _section_block(text: str, heading: str) -> str:
    """Return the body of `## <heading>` up to the next `##` heading."""
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.MULTILINE)
    if m is None:
        return ""
    start = m.end()
    nxt = re.search(r"^##\s+", text[start:], re.MULTILINE)
    if nxt is None:
        return text[start:]
    return text[start:start + nxt.start()]


class TestSectionPresence(unittest.TestCase):
    def test_every_lens_has_repo_kind_section(self):
        for lens in LENS_FILES:
            text = _read(lens)
            self.assertIn(
                "## Repo-kind branches", text,
                f"{lens} missing `## Repo-kind branches` section",
            )

    def test_section_appears_exactly_once(self):
        for lens in LENS_FILES:
            text = _read(lens)
            count = text.count("## Repo-kind branches")
            self.assertEqual(
                count, 1,
                f"{lens} has `## Repo-kind branches` {count}× — expected exactly 1",
            )

    def test_section_body_is_non_empty(self):
        for lens in LENS_FILES:
            text = _read(lens)
            body = _section_block(text, "Repo-kind branches").strip()
            self.assertNotEqual(
                body, "",
                f"{lens} has an empty `## Repo-kind branches` section",
            )


class TestRealBranches(unittest.TestCase):
    """Lenses that should carry per-kind tables — verify all nine kinds
    appear in the section so no kind is silently missing."""

    def test_real_branch_tables_mention_every_kind(self):
        for lens in LENSES_WITH_REAL_BRANCHES:
            text = _read(lens)
            body = _section_block(text, "Repo-kind branches")
            for kind in VALID_KINDS:
                self.assertIn(
                    f"`{kind}`", body,
                    f"{lens} repo-kind section missing kind `{kind}`",
                )


class TestKindValueSpace(unittest.TestCase):
    """No lens may reference a kind name outside the canonical nine inside
    its `## Repo-kind branches` section."""

    KIND_NAME_RE = re.compile(r"`([a-z][a-z0-9-]*)`")
    # Tokens that are backticked in branch tables but aren't kind names —
    # filenames, config keys, glob shapes, code paths.
    NON_KIND_BACKTICKS = re.compile(
        r"^(skills|app|library|docs|monorepo|python|rust|go|unknown)$"
    )

    def test_no_invented_kind_names_in_sections(self):
        for lens in LENS_FILES:
            text = _read(lens)
            body = _section_block(text, "Repo-kind branches")
            # Heuristic: a backticked single-word lowercase token in the
            # "leftmost column" of a markdown row (between `|` and `|`) is
            # a kind candidate. Filter to those rows for the assertion.
            for line in body.splitlines():
                cells = [c.strip() for c in line.split("|") if c.strip()]
                if not cells:
                    continue
                # First cell of a table row is the kind. Skip header rows
                # (`---`) and non-row lines.
                first = cells[0]
                if first.startswith("---") or first in ("`repo_kind`",):
                    continue
                # A pure backticked single kind name like `skills` only.
                m = re.fullmatch(r"`([a-z][a-z0-9-]*)`", first)
                if m is None:
                    continue
                token = m.group(1)
                # Only flag if it looks like a kind candidate (single word,
                # lowercase). Filename-ish tokens like "audit-phase" pass
                # the regex but won't appear in leftmost column of a
                # repo-kind row in any well-formed lens brief.
                self.assertIn(
                    token, VALID_KINDS,
                    f"{lens} repo-kind row uses invented kind `{token}`",
                )


if __name__ == "__main__":
    unittest.main()
