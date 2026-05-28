"""Parity tests for the canonical blocks embedded in prose-emitting and label-hygiene skills.

Two canonical rules share this suite — `writing-rules` (style) and `label-hygiene`
(internal-label vocabulary leakage). Each lives in its own `.claude/rules/skill-*.md`
file with its own marker pair and declared-skill list, and propagates via
`scripts/sync_writing_rules.py`. These tests enforce byte-level parity, placement
near the top, exclusion of non-declared skills, and absence of personal/brand-voice
path leaks — once per rule.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import REPO_ROOT, SKILLS_DIR  # noqa: E402

SYNC_SCRIPT = REPO_ROOT / "scripts" / "sync_writing_rules.py"
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"


class Rule(NamedTuple):
    id: str
    canonical_file: Path
    start_marker: str
    end_marker: str
    declared_header: str
    excluded_header: str
    expected_h2_in_block: str


CANONICAL_RULES: tuple[Rule, ...] = (
    Rule(
        id="writing-rules",
        canonical_file=REPO_ROOT / ".claude" / "rules" / "skill-prose-rules.md",
        start_marker="<!-- canonical:writing-rules:start -->",
        end_marker="<!-- canonical:writing-rules:end -->",
        declared_header="## Declared prose-emitting skills",
        excluded_header="## Excluded skills (with reason)",
        expected_h2_in_block="## Important — Writing rules",
    ),
    Rule(
        id="label-hygiene",
        canonical_file=REPO_ROOT / ".claude" / "rules" / "skill-label-hygiene-rules.md",
        start_marker="<!-- canonical:label-hygiene:start -->",
        end_marker="<!-- canonical:label-hygiene:end -->",
        declared_header="## Declared label-hygiene skills",
        excluded_header="## Excluded skills (with reason)",
        expected_h2_in_block="## Critical — Label hygiene",
    ),
)

PLACEMENT_LINE_CAP = 50

WORKFLOW_HEADERS = (
    "## Workflow",
    "## Objective",
    "## Quick Start",
    "## Process",
    "## Subcommands",
    "## Subcommand routing",
    "## Parameters",
    "## Core Principle",
    "## Capture Intent",
    "## Context",
    "## Universal rules",
    "## Two patterns",
    "## API",
)


def _parse_canonical(rule: Rule) -> tuple[str, list[str], list[str]]:
    """Return (canonical_block, declared_list, excluded_list) for one rule."""
    text = rule.canonical_file.read_text(encoding="utf-8")
    s = text.find(rule.start_marker)
    e = text.find(rule.end_marker)
    if s == -1 or e == -1 or e <= s:
        raise AssertionError(
            f"{rule.id}: canonical markers missing or malformed in {rule.canonical_file}"
        )
    block = text[s : e + len(rule.end_marker)]

    def _list_under(header: str) -> list[str]:
        m = re.search(
            rf"^{re.escape(header)}\s*$(.*?)^## ",
            text,
            re.MULTILINE | re.DOTALL,
        )
        if not m:
            raise AssertionError(f"{rule.id}: section {header!r} not found")
        out: list[str] = []
        for line in m.group(1).splitlines():
            bm = re.match(r"^- `?([a-z][a-z0-9-]*)`?", line.strip())
            if bm:
                out.append(bm.group(1))
        return out

    declared = _list_under(rule.declared_header)
    excluded = _list_under(rule.excluded_header)
    return block, declared, excluded


def _extract_block(skill_md: Path, start_marker: str, end_marker: str) -> str | None:
    text = skill_md.read_text(encoding="utf-8")
    s = text.find(start_marker)
    e = text.find(end_marker)
    if s == -1 or e == -1 or e <= s:
        return None
    return text[s : e + len(end_marker)]


class TestCanonicalFiles(unittest.TestCase):
    def test_each_canonical_rule_file_exists_and_parses(self):
        for rule in CANONICAL_RULES:
            with self.subTest(rule=rule.id):
                self.assertTrue(
                    rule.canonical_file.is_file(), f"missing {rule.canonical_file}"
                )
                block, declared, excluded = _parse_canonical(rule)
                self.assertIn(rule.expected_h2_in_block, block)
                self.assertGreaterEqual(len(declared), 1)
                self.assertGreaterEqual(len(excluded), 1)


class TestDeclaredSkillsCarryBlock(unittest.TestCase):
    def test_every_declared_skill_carries_canonical_block_verbatim(self):
        for rule in CANONICAL_RULES:
            block, declared, _ = _parse_canonical(rule)
            for name in declared:
                with self.subTest(rule=rule.id, skill=name):
                    skill_md = SKILLS_DIR / name / "SKILL.md"
                    self.assertTrue(skill_md.is_file(), f"missing {skill_md}")
                    got = _extract_block(skill_md, rule.start_marker, rule.end_marker)
                    self.assertIsNotNone(
                        got, f"{name} ({rule.id}): canonical markers absent"
                    )
                    self.assertEqual(
                        got,
                        block,
                        f"{name} ({rule.id}): canonical block drift — "
                        f"run scripts/sync_writing_rules.py",
                    )

    def test_canonical_block_placed_near_top(self):
        """Auto-compaction protects the first 5000 tokens of each invoked skill.
        Placing each canonical block within the first 50 lines keeps it inside that
        window. The cap accommodates two stacked canonical blocks (writing-rules +
        label-hygiene) which together span ~30-35 lines after H1."""
        for rule in CANONICAL_RULES:
            _, declared, _ = _parse_canonical(rule)
            for name in declared:
                with self.subTest(rule=rule.id, skill=name):
                    skill_md = SKILLS_DIR / name / "SKILL.md"
                    lines = skill_md.read_text(encoding="utf-8").splitlines()
                    for i, line in enumerate(lines, start=1):
                        if rule.start_marker in line:
                            self.assertLessEqual(
                                i,
                                PLACEMENT_LINE_CAP,
                                f"{name} ({rule.id}): canonical block starts at "
                                f"line {i} — must be ≤{PLACEMENT_LINE_CAP}",
                            )
                            break
                    else:
                        self.fail(f"{name} ({rule.id}): start marker not found")

    def test_canonical_block_appears_before_first_workflow_section(self):
        """The block sits between H1 and the first non-canonical `## ` section.

        With multiple canonical blocks present, the first `## ` after one
        block's end marker may be a sibling canonical block's header. The
        regex skips any prefix used by a canonical block (built from
        CANONICAL_RULES.expected_h2_in_block) so the search walks past
        sibling blocks and finds the first workflow section.
        """
        canonical_prefixes = {
            rule.expected_h2_in_block.split(" — ", 1)[0].removeprefix("## ").strip()
            for rule in CANONICAL_RULES
        }
        skip_pattern = "|".join(re.escape(p) for p in sorted(canonical_prefixes))
        first_workflow_re = re.compile(rf"^## (?!(?:{skip_pattern}))", re.MULTILINE)

        for rule in CANONICAL_RULES:
            _, declared, _ = _parse_canonical(rule)
            for name in declared:
                with self.subTest(rule=rule.id, skill=name):
                    text = (SKILLS_DIR / name / "SKILL.md").read_text(encoding="utf-8")
                    block_pos = text.find(rule.start_marker)
                    self.assertGreaterEqual(
                        block_pos, 0, f"{name} ({rule.id}): start marker missing"
                    )
                    end_pos = text.find(rule.end_marker)
                    self.assertGreater(
                        end_pos,
                        block_pos,
                        f"{name} ({rule.id}): end marker missing or before start",
                    )
                    tail = text[end_pos + len(rule.end_marker) :]
                    m = first_workflow_re.search(tail)
                    self.assertIsNotNone(
                        m,
                        f"{name} ({rule.id}): no non-canonical `## ` section "
                        f"follows the canonical block",
                    )
                    for header in WORKFLOW_HEADERS:
                        pos = text.find("\n" + header)
                        if pos != -1:
                            self.assertLess(
                                block_pos,
                                pos,
                                f"{name} ({rule.id}): canonical block must "
                                f"precede {header!r}",
                            )

    def test_canonical_block_markers_unique_per_file(self):
        for rule in CANONICAL_RULES:
            _, declared, _ = _parse_canonical(rule)
            for name in declared:
                with self.subTest(rule=rule.id, skill=name):
                    text = (SKILLS_DIR / name / "SKILL.md").read_text(encoding="utf-8")
                    self.assertEqual(
                        text.count(rule.start_marker),
                        1,
                        f"{name} ({rule.id}): start marker not unique",
                    )
                    self.assertEqual(
                        text.count(rule.end_marker),
                        1,
                        f"{name} ({rule.id}): end marker not unique",
                    )


class TestExcludedSkills(unittest.TestCase):
    def test_excluded_skills_have_no_canonical_block(self):
        for rule in CANONICAL_RULES:
            _, _, excluded = _parse_canonical(rule)
            for name in excluded:
                with self.subTest(rule=rule.id, skill=name):
                    skill_md = SKILLS_DIR / name / "SKILL.md"
                    self.assertTrue(skill_md.is_file(), f"missing {skill_md}")
                    text = skill_md.read_text(encoding="utf-8")
                    self.assertNotIn(
                        rule.start_marker,
                        text,
                        f"{name} ({rule.id}): should not carry canonical block",
                    )
                    self.assertNotIn(
                        rule.end_marker,
                        text,
                        f"{name} ({rule.id}): should not carry canonical block",
                    )


class TestMarketplaceClassification(unittest.TestCase):
    def test_every_marketplace_skill_classified_per_rule(self):
        """Every skill in marketplace.json is classified by each canonical rule
        — declared XOR excluded."""
        data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
        listed = {
            entry.removeprefix("./skills/")
            for plugin in data["plugins"]
            for entry in plugin.get("skills", [])
        }
        for rule in CANONICAL_RULES:
            with self.subTest(rule=rule.id):
                _, declared, excluded = _parse_canonical(rule)
                classified = set(declared) | set(excluded)
                unclassified = listed - classified
                self.assertFalse(
                    unclassified,
                    f"{rule.id}: marketplace skills missing classification "
                    f"in {rule.canonical_file.name}: {sorted(unclassified)}",
                )


class TestPrivacy(unittest.TestCase):
    BANNED = (
        "BRAND-VOICE",
        "/.claude/brand-voices",
        "/Users/",
        "/home/",
        "C:\\Users\\",
        "$HOME/.claude",
    )
    PERSONAL_PATH_PATTERNS = ("/Users/", "/home/", "C:\\Users\\")

    def test_no_brand_voice_path_leak_in_canonical_block(self):
        for rule in CANONICAL_RULES:
            with self.subTest(rule=rule.id):
                block, _, _ = _parse_canonical(rule)
                for pat in self.BANNED:
                    self.assertNotIn(
                        pat, block, f"{rule.id}: canonical block leaks {pat!r}"
                    )

    def test_no_personal_paths_in_any_patched_skill(self):
        for rule in CANONICAL_RULES:
            _, declared, _ = _parse_canonical(rule)
            for name in declared:
                with self.subTest(rule=rule.id, skill=name):
                    block = _extract_block(
                        SKILLS_DIR / name / "SKILL.md",
                        rule.start_marker,
                        rule.end_marker,
                    )
                    if block is None:
                        self.fail(f"{name} ({rule.id}): marker block missing")
                    for pat in self.PERSONAL_PATH_PATTERNS:
                        self.assertNotIn(
                            pat,
                            block,
                            f"{name} ({rule.id}): canonical block leaks {pat!r}",
                        )


class TestSyncIdempotent(unittest.TestCase):
    def test_sync_script_is_idempotent_across_both_rules(self):
        """Running sync_writing_rules.py twice on a synced tree produces zero diff.
        Both rule families appear in the second run's UNCHANGED stream."""
        self.assertTrue(SYNC_SCRIPT.is_file(), f"missing {SYNC_SCRIPT}")
        first = subprocess.run(
            [sys.executable, str(SYNC_SCRIPT)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(first.returncode, 0, f"first run failed: {first.stderr}")
        second = subprocess.run(
            [sys.executable, str(SYNC_SCRIPT)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(second.returncode, 0, f"second run failed: {second.stderr}")
        rule_ids_seen: set[str] = set()
        for line in second.stdout.splitlines():
            self.assertTrue(
                line.startswith("UNCHANGED "),
                f"second run not idempotent: {line!r}",
            )
            for rule in CANONICAL_RULES:
                if f"({rule.id})" in line:
                    rule_ids_seen.add(rule.id)
        for rule in CANONICAL_RULES:
            self.assertIn(
                rule.id,
                rule_ids_seen,
                f"second run output missing entries for rule {rule.id!r}",
            )


if __name__ == "__main__":
    unittest.main()
