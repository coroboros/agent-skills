"""Tests for audit_readme.py — slug, anchor resolution, structural HTML, bloat scan, CLI."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO_ROOT / "skills" / "write-clear-readme" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from audit_readme import audit, slugify, mask_code_only, mask_for_bloat  # noqa: E402

SCRIPT = SCRIPTS / "audit_readme.py"


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


class TestSlugify(unittest.TestCase):
    def test_simple_heading(self):
        self.assertEqual(slugify("Foo Bar"), "foo-bar")

    def test_inline_code_stripped(self):
        self.assertEqual(slugify("Use `pnpm`"), "use-pnpm")

    def test_bold_stripped(self):
        self.assertEqual(slugify("**Important** stuff"), "important-stuff")

    def test_special_chars_dropped(self):
        self.assertEqual(slugify("Foo (bar)!"), "foo-bar")

    def test_markdown_link_text_preserved(self):
        self.assertEqual(slugify("[doc](url) ref"), "doc-ref")


class TestAnchorResolution(unittest.TestCase):
    def test_resolved_anchor_no_error(self):
        text = "## Setup\n\nSee [setup](#setup) above.\n"
        report = audit(text)
        self.assertEqual(report["anchors"]["unresolved"], [])
        self.assertTrue(report["summary"]["rules"]["anchors"]["pass"])

    def test_unresolved_anchor_flagged(self):
        text = "## Setup\n\nSee [bad](#missing) above.\n"
        report = audit(text)
        self.assertEqual(len(report["anchors"]["unresolved"]), 1)
        self.assertEqual(report["anchors"]["unresolved"][0]["anchor"], "missing")
        self.assertFalse(report["summary"]["rules"]["anchors"]["pass"])

    def test_multiple_anchor_styles(self):
        text = (
            "# Top\n"
            "## Inline `code` Header\n"
            "## Bold **One**\n\n"
            "Links: [a](#top), [b](#inline-code-header), [c](#bold-one).\n"
        )
        report = audit(text)
        self.assertEqual(report["anchors"]["unresolved"], [])


class TestNestedDetailsDetection(unittest.TestCase):
    def test_nested_details_flagged(self):
        text = (
            "<details>\n<summary>Outer</summary>\n<br>\n"
            "<details>\n<summary>Inner</summary>\n<br>\n"
            "content\n</details>\n</details>\n"
        )
        report = audit(text)
        self.assertEqual(len(report["details"]["nested"]), 1)
        self.assertFalse(report["summary"]["rules"]["nested_details"]["pass"])

    def test_sibling_details_not_flagged(self):
        text = (
            "<details>\n<summary>One</summary>\n<br>\nA\n</details>\n\n"
            "<details>\n<summary>Two</summary>\n<br>\nB\n</details>\n"
        )
        report = audit(text)
        self.assertEqual(report["details"]["nested"], [])
        self.assertTrue(report["summary"]["rules"]["nested_details"]["pass"])


class TestSummaryBrCheck(unittest.TestCase):
    def test_br_within_window_passes(self):
        text = "<details>\n<summary>Title</summary>\n<br>\n\ncontent\n</details>\n"
        report = audit(text)
        self.assertEqual(report["details"]["summary_missing_br"], [])
        self.assertTrue(report["summary"]["rules"]["summary_br"]["pass"])

    def test_missing_br_flagged(self):
        text = (
            "<details>\n"
            "<summary>Title</summary>\n"
            "\n"
            "\n"
            "Long content goes here without any break tag.\n"
            "</details>\n"
        )
        report = audit(text)
        self.assertEqual(len(report["details"]["summary_missing_br"]), 1)
        self.assertFalse(report["summary"]["rules"]["summary_br"]["pass"])


class TestBloatPatterns(unittest.TestCase):
    def test_in_order_to_triggers(self):
        text = "We do this in order to ship faster.\n"
        report = audit(text)
        tokens = [hit["token"] for hit in report["bloat"]]
        self.assertIn("in order to", tokens)

    def test_leverage_triggers(self):
        text = "We leverage caching here.\n"
        report = audit(text)
        tokens = [hit["token"] for hit in report["bloat"]]
        self.assertIn("leverage", tokens)

    def test_powerful_and_robust_both_trigger(self):
        text = "A powerful, robust solution.\n"
        report = audit(text)
        tokens = [hit["token"] for hit in report["bloat"]]
        self.assertIn("powerful", tokens)
        self.assertIn("robust", tokens)

    def test_bloat_inside_code_fence_ignored(self):
        text = (
            "Clean prose here.\n\n"
            "```\n"
            "in order to leverage powerful robust seamlessly\n"
            "```\n"
        )
        report = audit(text)
        self.assertEqual(report["bloat"], [])
        self.assertTrue(report["summary"]["rules"]["bloat"]["pass"])


class TestCLI(unittest.TestCase):
    def test_missing_file_exit_2(self):
        result = _run("/path/that/does/not/exist.md")
        self.assertEqual(result.returncode, 2)

    def test_clean_readme_exit_0(self):
        text = "# Title\n\n## Setup\n\nSee [setup](#setup).\n"
        path = _write_temp(text)
        try:
            result = _run(path)
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertTrue(report["summary"]["ok"])
            self.assertIn("anchors", report)
            self.assertIn("details", report)
            self.assertIn("bloat", report)
            self.assertIn("summary", report)
        finally:
            path.unlink()

    def test_unresolved_anchor_exit_1(self):
        text = "# Title\n\nSee [bad](#nope).\n"
        path = _write_temp(text)
        try:
            result = _run(path)
            self.assertEqual(result.returncode, 1)
            report = json.loads(result.stdout)
            self.assertFalse(report["summary"]["ok"])
            self.assertGreaterEqual(len(report["anchors"]["unresolved"]), 1)
        finally:
            path.unlink()


if __name__ == "__main__":
    unittest.main()
