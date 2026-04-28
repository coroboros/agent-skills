"""Tests for audit_claude_md.py — bloat patterns, import resolution, masking."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO_ROOT / "skills" / "claude-md" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from audit_claude_md import (  # noqa: E402
    BLOAT_CATEGORIES,
    check_imports,
    mask_protected,
    scan_bloat,
)

SCRIPT = SCRIPTS / "audit_claude_md.py"


def _run(path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True
    )


class TestBloatCategories(unittest.TestCase):
    def test_categories_present(self):
        for cat in (
            "linter-enforced",
            "marketing-or-vision",
            "obvious-info",
            "verbose-explanation",
            "redundant-spec",
            "generic-best-practices",
        ):
            self.assertIn(cat, BLOAT_CATEGORIES, f"{cat} category missing")

    def test_every_category_has_patterns(self):
        """Catches a subtle regression where a category key exists but the pattern
        list is empty — the bloat scan would silently skip the category. Without
        this assertion, deletion of patterns goes undetected."""
        for cat, patterns in BLOAT_CATEGORIES.items():
            with self.subTest(category=cat):
                self.assertGreater(len(patterns), 0,
                                   f"{cat}: pattern list is empty — scan would skip silently")
                for pattern in patterns:
                    self.assertIsInstance(pattern, str)
                    self.assertGreater(len(pattern), 0)

    def test_linter_enforced_triggers_eslint(self):
        hits = scan_bloat(["Use eslint and prettier"])
        cats = [h["category"] for h in hits]
        self.assertIn("linter-enforced", cats)

    def test_marketing_triggers_we_believe(self):
        hits = scan_bloat(["We believe in clean code."])
        cats = [h["category"] for h in hits]
        self.assertIn("marketing-or-vision", cats)

    def test_verbose_triggers_in_order_to(self):
        hits = scan_bloat(["Run this in order to deploy."])
        cats = [h["category"] for h in hits]
        self.assertIn("verbose-explanation", cats)

    def test_generic_triggers_solid(self):
        hits = scan_bloat(["Apply the SOLID principles."])
        cats = [h["category"] for h in hits]
        self.assertIn("generic-best-practices", cats)

    def test_obvious_triggers_node_modules(self):
        hits = scan_bloat(["node_modules/ contains dependencies"])
        cats = [h["category"] for h in hits]
        self.assertIn("obvious-info", cats)


class TestMasking(unittest.TestCase):
    def test_fenced_code_masked(self):
        text = "Real text.\n```\nin order to test\n```\nMore real text.\n"
        masked = mask_protected(text)
        # The phrase 'in order to' inside fence is masked, so no bloat hit on those lines.
        hits = scan_bloat(masked.splitlines())
        # Hits on 'in order to' should not appear (the phrase is in fenced code)
        in_order = [h for h in hits if "in order to" in h["match"].lower()]
        self.assertEqual(in_order, [])

    def test_inline_backticks_masked(self):
        text = "Use `in order to` syntax."
        masked = mask_protected(text)
        hits = scan_bloat(masked.splitlines())
        self.assertEqual(hits, [])

    def test_html_comment_masked(self):
        text = "<!-- in order to skip -->"
        masked = mask_protected(text)
        hits = scan_bloat(masked.splitlines())
        self.assertEqual(hits, [])

    def test_line_count_preserved(self):
        text = "line1\n```\nline2\nline3\n```\nline5\n"
        masked = mask_protected(text)
        # Both raw and masked should split into the same number of lines
        self.assertEqual(len(text.splitlines()), len(masked.splitlines()))


class TestImportResolution(unittest.TestCase):
    def test_resolves_existing_relative(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            (td / "rule.md").write_text("rule content", encoding="utf-8")
            text = "See @rule.md for details."
            broken = check_imports(text, td)
            self.assertEqual(broken, [])

    def test_flags_missing_relative(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            text = "See @missing.md for details."
            broken = check_imports(text, td)
            self.assertEqual(len(broken), 1)
            self.assertEqual(broken[0]["path"], "missing.md")

    def test_line_number_reported(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            text = "line 1\nline 2\n@missing.md\nline 4\n"
            broken = check_imports(text, td)
            self.assertEqual(broken[0]["line"], 3)


class TestCLI(unittest.TestCase):
    def setUp(self):
        self._tempdirs = []

    def tearDown(self):
        # Explicit shutil.rmtree with ignore_errors=False so any cleanup failure
        # surfaces as a test error. The previous `finally: pass` masked leaks.
        for td in self._tempdirs:
            shutil.rmtree(td, ignore_errors=False)

    def _write_temp(self, text, name="CLAUDE.md"):
        td = tempfile.mkdtemp(prefix="audit-test-")
        self._tempdirs.append(td)
        path = Path(td) / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_no_args_exits_2(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)

    def test_missing_file_exits_2(self):
        r = _run("/tmp/_does_not_exist_audit.md")
        self.assertEqual(r.returncode, 2)

    def test_clean_short_file_exits_0(self):
        path = self._write_temp("# Project\n\n- Run `pnpm test` to test.\n")
        r = _run(path)
        self.assertEqual(r.returncode, 0, f"output: {r.stdout}")
        data = json.loads(r.stdout)
        self.assertTrue(data["summary"]["ok"])

    def test_bloated_file_exits_1(self):
        path = self._write_temp(
            "# Project\n\n"
            "We believe in clean code.\n"
            "Apply SOLID principles.\n"
            "Use eslint everywhere.\n"
        )
        r = _run(path)
        self.assertEqual(r.returncode, 1)
        data = json.loads(r.stdout)
        self.assertGreater(data["summary"]["findings"], 0)

    def test_over_target_lines_flagged(self):
        body = "# Project\n\n" + "\n".join(f"- line {i}" for i in range(1, 250)) + "\n"
        path = self._write_temp(body)
        r = _run(path)
        data = json.loads(r.stdout)
        self.assertTrue(data["over_target"])
        self.assertGreater(data["lines"], 200)


if __name__ == "__main__":
    unittest.main()
