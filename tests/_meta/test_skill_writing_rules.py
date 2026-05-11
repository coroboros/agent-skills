"""Parity tests for the canonical writing-rules block embedded in prose-emitting skills.

The canonical block lives in `.claude/rules/skill-prose-rules.md` and is propagated
to each declared SKILL.md by `scripts/sync_writing_rules.py`. These tests enforce
byte-level parity, placement near the top, exclusion of non-prose skills, and
absence of personal/brand-voice path leaks.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import REPO_ROOT, SKILLS_DIR  # noqa: E402

CANONICAL_FILE = REPO_ROOT / ".claude" / "rules" / "skill-prose-rules.md"
SYNC_SCRIPT = REPO_ROOT / "scripts" / "sync_writing_rules.py"
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"

START_MARKER = "<!-- canonical:writing-rules:start -->"
END_MARKER = "<!-- canonical:writing-rules:end -->"

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


def _parse_canonical() -> tuple[str, list[str], list[str]]:
    """Return (canonical_block, declared_list, excluded_list) from the rule file."""
    text = CANONICAL_FILE.read_text(encoding="utf-8")
    s = text.find(START_MARKER)
    e = text.find(END_MARKER)
    if s == -1 or e == -1 or e <= s:
        raise AssertionError("canonical markers missing or malformed")
    block = text[s : e + len(END_MARKER)]

    def _list_under(header: str) -> list[str]:
        m = re.search(
            rf"^{re.escape(header)}\s*$(.*?)^## ",
            text,
            re.MULTILINE | re.DOTALL,
        )
        if not m:
            raise AssertionError(f"section {header!r} not found")
        out: list[str] = []
        for line in m.group(1).splitlines():
            bm = re.match(r"^- `?([a-z][a-z0-9-]*)`?", line.strip())
            if bm:
                out.append(bm.group(1))
        return out

    declared = _list_under("## Declared prose-emitting skills")
    excluded = _list_under("## Excluded skills (with reason)")
    return block, declared, excluded


def _extract_block(skill_md: Path) -> str | None:
    text = skill_md.read_text(encoding="utf-8")
    s = text.find(START_MARKER)
    e = text.find(END_MARKER)
    if s == -1 or e == -1 or e <= s:
        return None
    return text[s : e + len(END_MARKER)]


class TestCanonicalFile(unittest.TestCase):
    def test_canonical_rule_file_exists_and_parses(self):
        self.assertTrue(CANONICAL_FILE.is_file(), f"missing {CANONICAL_FILE}")
        block, declared, excluded = _parse_canonical()
        self.assertIn("## Important — Writing rules", block)
        self.assertGreaterEqual(len(declared), 1)
        self.assertGreaterEqual(len(excluded), 1)


class TestDeclaredSkillsCarryBlock(unittest.TestCase):
    def test_every_declared_skill_carries_canonical_block_verbatim(self):
        block, declared, _ = _parse_canonical()
        for name in declared:
            with self.subTest(skill=name):
                skill_md = SKILLS_DIR / name / "SKILL.md"
                self.assertTrue(skill_md.is_file(), f"missing {skill_md}")
                got = _extract_block(skill_md)
                self.assertIsNotNone(got, f"{name}: canonical markers absent")
                self.assertEqual(
                    got,
                    block,
                    f"{name}: canonical block drift — run scripts/sync_writing_rules.py",
                )

    def test_canonical_block_placed_near_top(self):
        """Auto-compaction protects the first 5000 tokens of each invoked skill.
        Placing the canonical block in the first 30 lines keeps it inside that window."""
        _, declared, _ = _parse_canonical()
        for name in declared:
            with self.subTest(skill=name):
                skill_md = SKILLS_DIR / name / "SKILL.md"
                lines = skill_md.read_text(encoding="utf-8").splitlines()
                for i, line in enumerate(lines, start=1):
                    if START_MARKER in line:
                        self.assertLessEqual(
                            i,
                            30,
                            f"{name}: canonical block starts at line {i} — must be ≤30",
                        )
                        break
                else:
                    self.fail(f"{name}: start marker not found")

    def test_canonical_block_appears_before_first_workflow_section(self):
        """The block sits between H1 and the first workflow/content `## ` section."""
        _, declared, _ = _parse_canonical()
        for name in declared:
            with self.subTest(skill=name):
                text = (SKILLS_DIR / name / "SKILL.md").read_text(encoding="utf-8")
                block_pos = text.find(START_MARKER)
                self.assertGreaterEqual(block_pos, 0, f"{name}: start marker missing")
                for header in WORKFLOW_HEADERS:
                    pos = text.find("\n" + header)
                    if pos != -1:
                        self.assertLess(
                            block_pos,
                            pos,
                            f"{name}: canonical block must precede {header!r}",
                        )

    def test_canonical_block_markers_unique_per_file(self):
        _, declared, _ = _parse_canonical()
        for name in declared:
            with self.subTest(skill=name):
                text = (SKILLS_DIR / name / "SKILL.md").read_text(encoding="utf-8")
                self.assertEqual(text.count(START_MARKER), 1, f"{name}: start marker not unique")
                self.assertEqual(text.count(END_MARKER), 1, f"{name}: end marker not unique")


class TestExcludedSkills(unittest.TestCase):
    def test_excluded_skills_have_no_canonical_block(self):
        _, _, excluded = _parse_canonical()
        for name in excluded:
            with self.subTest(skill=name):
                skill_md = SKILLS_DIR / name / "SKILL.md"
                self.assertTrue(skill_md.is_file(), f"missing {skill_md}")
                text = skill_md.read_text(encoding="utf-8")
                self.assertNotIn(START_MARKER, text, f"{name}: should not carry canonical block")
                self.assertNotIn(END_MARKER, text, f"{name}: should not carry canonical block")


class TestMarketplaceClassification(unittest.TestCase):
    def test_every_marketplace_skill_classified(self):
        """Every skill in marketplace.json is either declared or explicitly excluded."""
        _, declared, excluded = _parse_canonical()
        data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
        listed = {
            entry.removeprefix("./skills/")
            for plugin in data["plugins"]
            for entry in plugin.get("skills", [])
        }
        classified = set(declared) | set(excluded)
        unclassified = listed - classified
        self.assertFalse(
            unclassified,
            f"marketplace skills missing classification in skill-prose-rules.md: "
            f"{sorted(unclassified)}",
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

    def test_no_brand_voice_path_leak_in_canonical_block(self):
        block, _, _ = _parse_canonical()
        for pat in self.BANNED:
            self.assertNotIn(pat, block, f"canonical block leaks {pat!r}")

    def test_no_personal_paths_in_any_patched_skill(self):
        _, declared, _ = _parse_canonical()
        leak_patterns = ("/Users/", "/home/", "C:\\Users\\")
        for name in declared:
            with self.subTest(skill=name):
                block = _extract_block(SKILLS_DIR / name / "SKILL.md")
                if block is None:
                    self.fail(f"{name}: marker block missing")
                for pat in leak_patterns:
                    self.assertNotIn(pat, block, f"{name}: canonical block leaks {pat!r}")


class TestSyncIdempotent(unittest.TestCase):
    def test_sync_script_is_idempotent(self):
        """Running sync_writing_rules.py twice on a synced tree produces zero diff."""
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
        for line in second.stdout.splitlines():
            self.assertTrue(
                line.startswith("UNCHANGED "),
                f"second run not idempotent: {line!r}",
            )


if __name__ == "__main__":
    unittest.main()
