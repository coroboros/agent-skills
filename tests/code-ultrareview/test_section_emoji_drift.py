"""Regression guard for plain `##` and `###` section references in the
skill's prose.

The template, SKILL.md, references, and evals are the source-of-truth docs a
lens subagent reads at dispatch and the eval evaluator scores against. A
plain-heading reference (`` `## Findings` ``, `### Verified`, …) in any of
these makes the subagent copy the wrong spelling and the visual-scheme bug
recurs. The template-level test in `test_report_template.py` catches drift
in the template itself; this one catches drift everywhere else.

The sweep is byte-literal: the substring `## Findings` does not appear in
the canonical `## 🔎 Findings` (the emoji + space sit between `##` and
`Findings`), so a literal match is the right detector. Backtick-quoted
references like `` `## Findings` `` are flagged too — that was the exact
drift the first /skill-creator pass surfaced.
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

# Canonical `##` base-names (without the leading emoji). A reference to
# `## <base-name>` is a regression because the canonical form is
# `## <emoji> <base-name>`. Mirror the 8-axis section list pinned in
# `tests/_pipeline/_contracts.py::CLUSTERS["review"]["report_required_sections"]`
# plus the two opt-in sections (`Derivation coverage`, `--apply-safe summary`).
CANONICAL_H2_BASE_NAMES = (
    "Axis summary",
    "Findings",
    "What looks good",
    "Verdict",
    "Tools skipped",
    "What I did NOT check",
    "Derivation coverage",
    "--apply-safe summary",
)

# Legacy `###` sub-section headings that the pre-fix layout used. Any
# resurfacing of these is a regression — the canonical forms are
# `### 🔴 High`, `### 🟠 Medium`, `### 🟢 Low`, `### ⚠️ Unverified`.
LEGACY_H3_HEADINGS = (
    "### Verified",
    "### Unverified",
    "### High",
    "### Medium",
    "### Low",
)

# Files swept for drift. The template is excluded — it is covered by
# `test_report_template.py` and contains the canonical emoji forms by
# definition.
SWEPT_FILES: tuple[Path, ...] = (
    SKILL_DIR / "SKILL.md",
    *(SKILL_DIR / "references").glob("*.md"),
    SKILL_DIR / "evals" / "evals.json",
)


def _line_no(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


class TestNoPlainH2Headings(unittest.TestCase):
    """Plain `## <base-name>` references — at line start, in inline backticks,
    or anywhere else — recreate the bug. Each must carry its emoji prefix."""

    def test_no_plain_h2_in_swept_files(self):
        violations: list[str] = []
        for path in SWEPT_FILES:
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            for base in CANONICAL_H2_BASE_NAMES:
                pattern = re.compile(rf"## {re.escape(base)}\b")
                for match in pattern.finditer(text):
                    rel = path.relative_to(REPO_ROOT)
                    violations.append(
                        f"{rel}:{_line_no(text, match.start())} — plain "
                        f"`## {base}` reference; must carry its canonical "
                        "emoji prefix"
                    )
        self.assertEqual(
            violations, [],
            "Plain `## <name>` references found — every reference to a "
            "canonical section must carry its emoji prefix:\n  "
            + "\n  ".join(violations),
        )


class TestNoLegacyH3Headings(unittest.TestCase):
    """The legacy `### Verified` / `### Unverified` / `### High` / etc.
    sub-section headings were replaced by emoji-prefixed forms. Any
    resurfacing is a regression.

    The pattern matches the heading form (line start) followed by end of line
    or a `(N findings)`-shaped count suffix — `### Unverified follow-up` (a
    distinct sub-block inside the Action plan section) does NOT match."""

    def test_no_legacy_h3_in_swept_files(self):
        violations: list[str] = []
        for path in SWEPT_FILES:
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            for legacy in LEGACY_H3_HEADINGS:
                pattern = re.compile(
                    rf"^{re.escape(legacy)}(\s*\(\d+ findings?\))?\s*$",
                    re.MULTILINE,
                )
                for match in pattern.finditer(text):
                    rel = path.relative_to(REPO_ROOT)
                    violations.append(
                        f"{rel}:{_line_no(text, match.start())} — legacy "
                        f"heading `{legacy}`; canonical form carries an "
                        "emoji prefix"
                    )
        self.assertEqual(
            violations, [],
            "Legacy `### <name>` headings found — replace with the canonical "
            "emoji-prefixed form:\n  " + "\n  ".join(violations),
        )


class TestDetectorCatchesBacktickedDrift(unittest.TestCase):
    """Self-test: prove the detector actually catches the backticked drift
    pattern the first /skill-creator pass flagged (`` `## Verdict` `` inside
    prose). A regex bug that lets backtick context slip past would mean the
    detector lies about coverage."""

    def test_backticked_plain_reference_is_detected(self):
        sample = "see the `## Verdict` section for the algorithm"
        pattern = re.compile(rf"## {re.escape('Verdict')}\b")
        self.assertIsNotNone(pattern.search(sample))

    def test_emoji_prefixed_reference_is_not_detected(self):
        sample = "see the `## ⚖️ Verdict` section for the algorithm"
        pattern = re.compile(rf"## {re.escape('Verdict')}\b")
        self.assertIsNone(pattern.search(sample))


class TestEvalsAndContractsAgreeOnSections(unittest.TestCase):
    """The canonical base-names listed above must match
    `_contracts.py::report_required_sections` (after stripping the emoji
    prefix). Drift between the two lists is the same bug at a higher level."""

    def test_canonical_base_names_match_contract(self):
        contract_sections = CLUSTERS["review"]["report_required_sections"]
        stripped = [
            re.sub(r"^[^\sA-Za-z]+\s+", "", entry).strip()
            for entry in contract_sections
        ]
        for base in stripped:
            self.assertIn(base, CANONICAL_H2_BASE_NAMES)


class TestEvalsJsonIsValid(unittest.TestCase):
    """JSON validity guard — the `replace_all` Edit on evals.json must keep
    the document parseable."""

    def test_evals_parses(self):
        with (SKILL_DIR / "evals" / "evals.json").open(encoding="utf-8") as f:
            payload = json.load(f)
        self.assertIn("evals", payload)
        self.assertTrue(payload["evals"], "evals list is empty")


class TestTerminalEchoRuleMirroredInThreePlaces(unittest.TestCase):
    """The terminal-echo rule states the full canonical report prints to the
    chat-terminal on every invocation, and that `-s` is purely additive (writes
    to disk, never gates the terminal output). The rule must be present in
    three places — SKILL.md `Final report layout`, SKILL.md `Rules`, and the
    template's `Section discipline` blockquote — so a model reading any of
    them encounters the contract. A future edit that removes the rule from
    one of the three breaks this test."""

    SENTINEL_PHRASES = (
        "byte-for-byte identical",
        "chat-terminal",
    )

    def _section_block(self, text: str, heading: str) -> str:
        """Extract the block from `## <heading>` up to (but excluding) the
        next `## ` heading."""
        idx = text.index(heading)
        rest = text[idx:]
        next_h2 = re.search(r"\n## ", rest[1:])
        return rest if next_h2 is None else rest[:next_h2.start() + 1]

    def test_rule_in_skill_md_final_report_layout(self):
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        block = self._section_block(text, "## Final report layout")
        for phrase in self.SENTINEL_PHRASES:
            self.assertIn(
                phrase, block,
                f"`## Final report layout` missing terminal-echo phrase {phrase!r}",
            )

    def test_rule_in_skill_md_rules(self):
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        block = self._section_block(text, "## Rules")
        # `## Rules` block carries the additive contract — `-s` does not gate
        # the chat-terminal output.
        self.assertRegex(
            block,
            r"(?i)full report in chat every time",
            "`## Rules` missing terminal-echo mandate",
        )

    def test_rule_in_template_section_discipline(self):
        text = (SKILL_DIR / "templates" / "code-ultrareview.md").read_text(
            encoding="utf-8"
        )
        # The `Section discipline` blockquote is the only blockquote near the
        # top of the template. Pin both sentinel phrases — they must appear
        # together inside it.
        for phrase in self.SENTINEL_PHRASES:
            self.assertIn(
                phrase, text,
                f"template missing terminal-echo phrase {phrase!r} in "
                "Section discipline blockquote",
            )


if __name__ == "__main__":
    unittest.main()
