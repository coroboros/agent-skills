"""Tests for validate_rule_file.py — frontmatter, paths list parsing, glob syntax."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO_ROOT / "skills" / "claude-md" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_rule_file import parse_paths  # noqa: E402

SCRIPT = SCRIPTS / "validate_rule_file.py"


def _write_temp(text):
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8")
    f.write(text)
    f.close()
    return Path(f.name)


def _run(path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True
    )


class TestParsePaths(unittest.TestCase):
    def test_no_paths_key(self):
        declared, items = parse_paths("name: example\n")
        self.assertFalse(declared)
        self.assertEqual(items, [])

    def test_inline_list_quoted(self):
        declared, items = parse_paths('paths: ["src/**/*.ts", "test/**/*.ts"]\n')
        self.assertTrue(declared)
        self.assertEqual(items, ["src/**/*.ts", "test/**/*.ts"])

    def test_inline_list_unquoted(self):
        declared, items = parse_paths("paths: [src/**/*.ts, test/**/*.ts]\n")
        self.assertTrue(declared)
        self.assertEqual(items, ["src/**/*.ts", "test/**/*.ts"])

    def test_block_list(self):
        fm = "paths:\n  - 'src/**/*.ts'\n  - test/**/*.ts\n"
        declared, items = parse_paths(fm)
        self.assertTrue(declared)
        self.assertEqual(items, ["src/**/*.ts", "test/**/*.ts"])

    def test_block_list_terminates_at_next_key(self):
        fm = "paths:\n  - src/**/*.ts\nname: x\n"
        declared, items = parse_paths(fm)
        self.assertTrue(declared)
        self.assertEqual(items, ["src/**/*.ts"])

    def test_empty_list(self):
        declared, items = parse_paths("paths: []\n")
        self.assertTrue(declared)
        self.assertEqual(items, [])


class TestCLI(unittest.TestCase):
    def test_no_args_exits_2(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertIn("usage", r.stderr)

    def test_missing_file_exits_2(self):
        r = _run("/tmp/_does_not_exist_rule.md")
        self.assertEqual(r.returncode, 2)

    def test_no_frontmatter_passes(self):
        path = _write_temp("# Just markdown\n\nNo frontmatter is fine.\n")
        try:
            r = _run(path)
            self.assertEqual(r.returncode, 0)
            data = json.loads(r.stdout)
            self.assertFalse(data["has_frontmatter"])
        finally:
            path.unlink()

    def test_valid_frontmatter_with_paths_passes(self):
        path = _write_temp('---\npaths:\n  - "src/**/*.ts"\n---\n\n# Rule\n')
        try:
            r = _run(path)
            self.assertEqual(r.returncode, 0)
            data = json.loads(r.stdout)
            self.assertTrue(data["has_frontmatter"])
            self.assertTrue(data["has_paths"])
            self.assertEqual(data["paths"], ["src/**/*.ts"])
        finally:
            path.unlink()

    def test_empty_frontmatter_block_flagged(self):
        path = _write_temp("---\n   \n---\n\nBody\n")
        try:
            r = _run(path)
            self.assertEqual(r.returncode, 1)
            data = json.loads(r.stdout)
            self.assertGreater(len(data["errors"]), 0)
        finally:
            path.unlink()

    def test_paths_declared_no_items_flagged(self):
        path = _write_temp("---\npaths:\n---\n\nBody\n")
        try:
            r = _run(path)
            self.assertEqual(r.returncode, 1)
            data = json.loads(r.stdout)
            self.assertTrue(any("no list items" in e for e in data["errors"]))
        finally:
            path.unlink()

    def test_invalid_glob_chars_flagged(self):
        path = _write_temp('---\npaths:\n  - "src/$@%/foo"\n---\n\nBody\n')
        try:
            r = _run(path)
            self.assertEqual(r.returncode, 1)
            data = json.loads(r.stdout)
            self.assertTrue(any("unexpected characters" in e for e in data["errors"]))
        finally:
            path.unlink()


class TestExistingRulesAreValid(unittest.TestCase):
    """Every .claude/rules/*.md in the repo should validate cleanly. This catches
    rule-file regressions across the project root."""

    def test_repo_rules_validate(self):
        rules_dir = REPO_ROOT / ".claude" / "rules"
        if not rules_dir.is_dir():
            self.skipTest("no .claude/rules/ at repo root")
        for rule in rules_dir.glob("*.md"):
            with self.subTest(rule=rule.name):
                r = _run(rule)
                self.assertEqual(r.returncode, 0,
                                 f"{rule.name} failed: {r.stdout}")


if __name__ == "__main__":
    unittest.main()
