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
        [sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True,
        timeout=30,
    )


class TestParsePaths(unittest.TestCase):
    def test_yaml_indicators_require_quoted_strings(self):
        for glob in ("**/*.ts", "!vendor/**", "[ab]/*.ts", "&anchor", "true", "123", "0x10", ".nan", "2026-09-06"):
            for frontmatter in (f"paths:\n  - {glob}", f"paths: [{glob}]"):
                with self.subTest(frontmatter=frontmatter), self.assertRaises(ValueError):
                    parse_paths(frontmatter)
        for glob in ("**/*.ts", "!vendor/**", "[ab]/*.ts", "src/{a,b}.ts"):
            self.assertEqual(parse_paths(f'paths:\n  - "{glob}"'), (True, [glob]))
            self.assertEqual(parse_paths(f'paths: ["{glob}"]'), (True, [glob]))

    def test_invalid_quoted_and_flow_scalars_are_rejected(self):
        for raw in ('paths: [src/{a,b}.ts]', 'paths: ["a" "b"]',
                    "paths:\n - 'unclosed", 'paths: [a,,b]'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                parse_paths(raw)

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

    def test_quoted_brace_glob_keeps_comma(self):
        self.assertEqual(parse_paths('paths: ["src/**/*.{ts,tsx}", \'test/**/*.py\']'),
                         (True, ["src/**/*.{ts,tsx}", "test/**/*.py"]))

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

    def test_block_list_requires_consistent_space_indentation(self):
        for first, second in (("  ", "    "), ("    ", "  "), ("\t", "\t")):
            with self.subTest(first=first, second=second), self.assertRaises(ValueError):
                parse_paths(f'paths:\n{first}- "src/**"\n{second}- "lib/**"')
        for indent in ("", "  ", "    "):
            with self.subTest(indent=indent):
                self.assertEqual(
                    parse_paths(f'paths:\n{indent}- "src/**"\n  # a comment\n{indent}- "lib/**"'),
                    (True, ["src/**", "lib/**"]),
                )

    def test_malformed_list_tail_does_not_disappear(self):
        for tail in ('  - ', '    trailing text', '  nested: value'):
            with self.subTest(tail=tail), self.assertRaises(ValueError):
                parse_paths('paths:\n  - "src/**"\n' + tail)

    def test_empty_list(self):
        declared, items = parse_paths("paths: []\n")
        self.assertTrue(declared)
        self.assertEqual(items, [])


class TestCLI(unittest.TestCase):
    def test_mixed_paths_indentation_exits_one(self):
        path = _write_temp('---\npaths:\n  - "src/**"\n    - "lib/**"\n---\n# Rule\n')
        try:
            result = _run(path)
            self.assertEqual(result.returncode, 1)
            report = json.loads(result.stdout)
            self.assertFalse(report["summary"]["ok"])
            self.assertTrue(any("indentation" in error for error in report["errors"]))
        finally:
            path.unlink()

    def test_unquoted_alias_glob_exits_one_with_quoting_guidance(self):
        path = _write_temp('---\npaths:\n  - **/*.ts\n---\n# Rule\n')
        try:
            result = _run(path)
            self.assertEqual(result.returncode, 1)
            data = json.loads(result.stdout)
            self.assertFalse(data["summary"]["ok"])
            self.assertTrue(any("quote paths item" in error for error in data["errors"]))
        finally:
            path.unlink()

    def test_unclosed_frontmatter_rejected(self):
        path = _write_temp('---\npaths: ["src/**/*.ts"]\n# rule\n')
        try:
            r = _run(path)
            self.assertEqual(r.returncode, 1)
            self.assertIn("closing", r.stdout)
        finally:
            path.unlink()

    def test_malformed_inline_quote_rejected(self):
        path = _write_temp('---\npaths: ["src/**/*.ts]\n---\n')
        try:
            r = _run(path)
            self.assertEqual(r.returncode, 1)
            self.assertFalse(json.loads(r.stdout)["summary"]["ok"])
        finally:
            path.unlink()

    def test_no_args_exits_2(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, timeout=30)
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
    """Every rule file in the repo (.agents/rules/ canonical + .claude/rules/
    behavior adapters) should validate cleanly. This catches rule-file
    regressions across the project root."""

    def test_repo_rules_validate(self):
        rule_dirs = [REPO_ROOT / ".agents" / "rules", REPO_ROOT / ".claude" / "rules"]
        rules = [r for d in rule_dirs if d.is_dir() for r in sorted(d.glob("*.md"))]
        if not rules:
            self.skipTest("no rule directories at repo root")
        for rule in rules:
            with self.subTest(rule=rule.name):
                r = _run(rule)
                self.assertEqual(r.returncode, 0,
                                 f"{rule.name} failed: {r.stdout}")


if __name__ == "__main__":
    unittest.main()
