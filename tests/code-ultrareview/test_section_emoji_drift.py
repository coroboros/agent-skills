"""Regression guard for plain `##` section references in the skill's prose.

The template, SKILL.md, references, and evals are the source-of-truth docs a
lens subagent reads at dispatch and the eval evaluator scores against. When
any one carries a plain-heading reference (e.g., `## Findings` instead of
`## 🔎 Findings`), a subagent will copy the spelling it sees in those files
and the user-reported bug recurs — the template-level test catches drift in
`templates/code-ultrareview.md`, this one catches drift everywhere else.

Pinned to the same canonical list as
`tests/_pipeline/_contracts.py::CLUSTERS["review"]["report_required_sections"]`
plus `## 🪛 --apply-safe summary` (opt-in in the contract, but its section
name follows the same convention).
"""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "code-ultrareview"

sys.path.insert(0, str(REPO_ROOT / "tests" / "_pipeline"))
from _contracts import CLUSTERS  # noqa: E402

# Canonical section base-names (without the leading emoji). A reference to
# `## <base-name>` without the matching emoji prefix is a regression.
CANONICAL_BASE_NAMES = (
    "Lens summary",
    "Findings",
    "Deferred to sibling skills",
    "What looks good",
    "Coherence-graph status",
    "Derivation coverage",
    "Verdict",
    "Action plan",
    "--apply-safe summary",
)

# Files swept for plain-heading references.
SWEPT_FILES: tuple[Path, ...] = (
    SKILL_DIR / "SKILL.md",
    *(SKILL_DIR / "references").glob("*.md"),
    SKILL_DIR / "evals" / "evals.json",
)


def _plain_heading_pattern(base_name: str) -> re.Pattern[str]:
    """Match `## <base-name>` not preceded by an emoji prefix on the same
    heading. Anchored to the literal text — checks both standalone `##` lines
    and inline backtick references like `` `## Verdict` ``."""
    escaped = re.escape(base_name)
    # Look for `## <name>` where the char before `##` is NOT an emoji-bearing
    # heading. We forbid the plain form anywhere the literal `## <name>` text
    # appears (line start or backtick context).
    return re.compile(rf"(?<!\S)## {escaped}\b")


class TestNoPlainSectionHeadings(unittest.TestCase):
    def test_no_plain_headings_in_swept_files(self):
        violations: list[str] = []
        for path in SWEPT_FILES:
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            for base in CANONICAL_BASE_NAMES:
                pattern = _plain_heading_pattern(base)
                for match in pattern.finditer(text):
                    # Compute line number.
                    line_no = text.count("\n", 0, match.start()) + 1
                    rel = path.relative_to(REPO_ROOT)
                    violations.append(
                        f"{rel}:{line_no} — plain `## {base}` reference; "
                        f"must carry its canonical emoji prefix"
                    )
        self.assertEqual(
            violations, [],
            "Plain section-name references found — every reference to a "
            "canonical section must carry its emoji prefix:\n  "
            + "\n  ".join(violations),
        )


class TestEvalsAndContractsAgreeOnSections(unittest.TestCase):
    """The canonical base-names listed above must match
    `_contracts.py::report_required_sections` (after stripping the emoji
    prefix) — drift between these two lists is the same bug at a higher
    level."""

    def test_canonical_base_names_match_contract(self):
        contract_sections = CLUSTERS["review"]["report_required_sections"]
        # Strip leading emoji + space from each contract entry; expect the
        # remainder to be in CANONICAL_BASE_NAMES (which adds the opt-in
        # --apply-safe summary on top).
        stripped = [
            re.sub(r"^[^\sA-Za-z]+\s+", "", entry).strip()
            for entry in contract_sections
        ]
        for base in stripped:
            self.assertIn(base, CANONICAL_BASE_NAMES)


class TestEvalsJsonIsValid(unittest.TestCase):
    """Sanity check the evals.json edits didn't break JSON parsing."""

    def test_evals_parses(self):
        with (SKILL_DIR / "evals" / "evals.json").open(encoding="utf-8") as f:
            payload = json.load(f)
        self.assertIn("evals", payload)
        self.assertTrue(payload["evals"], "evals list is empty")


if __name__ == "__main__":
    unittest.main()
