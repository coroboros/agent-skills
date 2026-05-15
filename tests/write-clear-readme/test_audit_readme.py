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


class TestExpandPrefix(unittest.TestCase):
    def test_expand_prefix_flagged(self):
        text = "<details>\n<summary>Expand — files installed</summary>\n<br>\nA\n</details>\n"
        report = audit(text)
        self.assertEqual(len(report["summary_quality"]["expand_prefix"]), 1)
        self.assertFalse(report["summary"]["rules"]["expand_prefix"]["pass"])

    def test_expand_prefix_inside_em_flagged(self):
        text = "<details>\n<summary><em>Expand — files installed</em></summary>\n<br>\nA\n</details>\n"
        report = audit(text)
        self.assertEqual(len(report["summary_quality"]["expand_prefix"]), 1)

    def test_expand_prefix_with_en_dash_flagged(self):
        text = "<details>\n<summary>Expand – foo</summary>\n<br>\nA\n</details>\n"
        report = audit(text)
        self.assertEqual(len(report["summary_quality"]["expand_prefix"]), 1)

    def test_expand_prefix_with_hyphen_flagged(self):
        text = "<details>\n<summary>Expand - foo</summary>\n<br>\nA\n</details>\n"
        report = audit(text)
        self.assertEqual(len(report["summary_quality"]["expand_prefix"]), 1)

    def test_clean_summary_passes(self):
        text = "<details>\n<summary><em>Files installed</em></summary>\n<br>\nA\n</details>\n"
        report = audit(text)
        self.assertEqual(report["summary_quality"]["expand_prefix"], [])
        self.assertTrue(report["summary"]["rules"]["expand_prefix"]["pass"])

    def test_expand_word_alone_not_flagged(self):
        # "Expand the buffer" is not the disclosure-prefix pattern.
        text = "<details>\n<summary>Expand the buffer here</summary>\n<br>\nA\n</details>\n"
        report = audit(text)
        self.assertEqual(report["summary_quality"]["expand_prefix"], [])

    def test_expand_prefix_inside_code_fence_ignored(self):
        text = (
            "```markdown\n"
            "<details>\n<summary>Expand — example</summary>\n</details>\n"
            "```\n"
        )
        report = audit(text)
        self.assertEqual(report["summary_quality"]["expand_prefix"], [])


class TestStaleCounts(unittest.TestCase):
    def test_stale_count_with_symlinks_flagged(self):
        text = "Installs 25 symlinks under `~/.claude/`.\n"
        report = audit(text)
        self.assertEqual(len(report["summary_quality"]["stale_counts"]), 1)
        self.assertFalse(report["summary"]["rules"]["stale_counts"]["pass"])

    def test_stale_count_with_skills_flagged(self):
        text = "The repo ships 10 skills today.\n"
        report = audit(text)
        self.assertEqual(len(report["summary_quality"]["stale_counts"]), 1)

    def test_stale_count_in_summary_flagged(self):
        text = (
            "<details>\n<summary>14 declared tasks</summary>\n<br>\nA\n</details>\n"
        )
        report = audit(text)
        self.assertEqual(len(report["summary_quality"]["stale_counts"]), 1)

    def test_version_number_not_flagged(self):
        text = "Requires Python 3.7+. Version 1.20.0 is the latest.\n"
        report = audit(text)
        self.assertEqual(report["summary_quality"]["stale_counts"], [])

    def test_unrelated_count_not_flagged(self):
        # "5 minutes", "3 stars" — not maintainable-content nouns.
        text = "Install takes 5 minutes. Project has 3 stars.\n"
        report = audit(text)
        self.assertEqual(report["summary_quality"]["stale_counts"], [])

    def test_count_with_adjectives_flagged(self):
        # The postmortem's real-world form — adjectives between number and noun.
        text = "Manages 14 declared periodic tasks across the install.\n"
        report = audit(text)
        self.assertEqual(len(report["summary_quality"]["stale_counts"]), 1)

    def test_up_to_limit_not_flagged(self):
        # API limits — stable, not stale.
        text = "Batches up to 100 tasks per call.\n"
        report = audit(text)
        self.assertEqual(report["summary_quality"]["stale_counts"], [])

    def test_threshold_with_gt_not_flagged(self):
        # `>5 commands` is a threshold, not a count of internal content.
        text = "If >5 commands run, escalate to /apex.\n"
        report = audit(text)
        self.assertEqual(report["summary_quality"]["stale_counts"], [])

    def test_max_prefix_not_flagged(self):
        text = "Max 3 hooks may register simultaneously.\n"
        report = audit(text)
        self.assertEqual(report["summary_quality"]["stale_counts"], [])

    def test_range_not_flagged(self):
        # `2–3 tasks` is a range; the second digit is not a stale count.
        text = "Finds 2–3 key tasks worth shipping this week.\n"
        report = audit(text)
        self.assertEqual(report["summary_quality"]["stale_counts"], [])

    def test_generic_noun_files_not_flagged(self):
        # `files`, `rows`, `columns`, `fields` are intentionally outside the
        # noun list — too generic to be reliable stale signals.
        text = "Touches 5 files and 100 rows in one go.\n"
        report = audit(text)
        self.assertEqual(report["summary_quality"]["stale_counts"], [])

    def test_stale_count_inside_code_fence_ignored(self):
        text = (
            "```\n"
            "Output: 25 symlinks installed, 14 tasks queued.\n"
            "```\n"
        )
        report = audit(text)
        self.assertEqual(report["summary_quality"]["stale_counts"], [])


class TestRedundantHeading(unittest.TestCase):
    def test_redundant_h3_above_details_flagged(self):
        text = (
            "### Files installed\n\n"
            "<details>\n<summary><em>Files installed</em></summary>\n<br>\n"
            "A\n</details>\n"
        )
        report = audit(text)
        self.assertEqual(len(report["summary_quality"]["redundant_heading"]), 1)
        self.assertFalse(report["summary"]["rules"]["redundant_heading"]["pass"])

    def test_redundant_h2_above_details_flagged(self):
        text = (
            "## Configuration\n\n"
            "<details>\n<summary>Configuration</summary>\n<br>\nA\n</details>\n"
        )
        report = audit(text)
        self.assertEqual(len(report["summary_quality"]["redundant_heading"]), 1)

    def test_different_label_not_flagged(self):
        text = (
            "### Setup\n\n"
            "<details>\n<summary><em>Install steps</em></summary>\n<br>\nA\n</details>\n"
        )
        report = audit(text)
        self.assertEqual(report["summary_quality"]["redundant_heading"], [])

    def test_far_apart_not_flagged(self):
        text = (
            "### Setup\n\n"
            + "Some content paragraph.\n\n" * 4
            + "<details>\n<summary>Setup</summary>\n<br>\nA\n</details>\n"
        )
        report = audit(text)
        self.assertEqual(report["summary_quality"]["redundant_heading"], [])

    def test_redundant_inside_code_fence_ignored(self):
        text = (
            "```markdown\n"
            "### Files\n\n"
            "<details>\n<summary>Files</summary>\n</details>\n"
            "```\n"
        )
        report = audit(text)
        self.assertEqual(report["summary_quality"]["redundant_heading"], [])

    def test_clean_pattern_a_passes(self):
        # Pattern A done right: h2 visible, no h3, summary carries the label.
        text = (
            "## Configuration\n\n"
            "Short intro paragraph.\n\n"
            "<details>\n<summary><em>Token scopes</em></summary>\n<br>\nA\n</details>\n\n"
            "<details>\n<summary><em>Environment variables</em></summary>\n<br>\nB\n</details>\n"
        )
        report = audit(text)
        self.assertEqual(report["summary_quality"]["redundant_heading"], [])


class TestVisualRhythm(unittest.TestCase):
    def _long(self, body):
        # Pad to over the 200-line threshold so the soft flag can activate.
        return body + ("\n" * 250)

    def test_long_doc_no_callouts_no_images_flat(self):
        text = self._long("# Title\n\n## Section\n\nContent paragraph.\n")
        report = audit(text)
        self.assertEqual(report["visual_rhythm"]["callouts"], 0)
        self.assertEqual(report["visual_rhythm"]["images"], 0)
        self.assertTrue(report["visual_rhythm"]["flat_flag"])

    def test_long_doc_with_callout_not_flat(self):
        text = self._long(
            "# Title\n\n## Section\n\n> [!NOTE]\n> Useful aside.\n\nMore content.\n"
        )
        report = audit(text)
        self.assertEqual(report["visual_rhythm"]["callouts"], 1)
        self.assertFalse(report["visual_rhythm"]["flat_flag"])

    def test_long_doc_with_md_image_not_flat(self):
        text = self._long("# Title\n\n![logo](assets/logo.png)\n\n## Section\n\nContent.\n")
        report = audit(text)
        self.assertGreaterEqual(report["visual_rhythm"]["images"], 1)
        self.assertFalse(report["visual_rhythm"]["flat_flag"])

    def test_long_doc_with_html_img_not_flat(self):
        text = self._long('# Title\n\n<img src="x.png" alt="x"/>\n\n## Section\n\nContent.\n')
        report = audit(text)
        self.assertGreaterEqual(report["visual_rhythm"]["images"], 1)
        self.assertFalse(report["visual_rhythm"]["flat_flag"])

    def test_short_doc_no_flat_flag(self):
        # Below the threshold — flat_flag stays false regardless.
        text = "# Title\n\n## Section\n\nContent.\n"
        report = audit(text)
        self.assertFalse(report["visual_rhythm"]["flat_flag"])

    def test_callout_count_multiple(self):
        text = (
            "# Title\n\n"
            "> [!NOTE]\n> One.\n\n"
            "> [!TIP]\n> Two.\n\n"
            "> [!WARNING]\n> Three.\n"
        )
        report = audit(text)
        self.assertEqual(report["visual_rhythm"]["callouts"], 3)

    def test_visual_rhythm_is_soft_not_counted_in_findings(self):
        # A long flat doc with no other issues should still exit 0 (ok=true).
        text = self._long("# Title\n\n## Section\n\nClean content.\n")
        report = audit(text)
        self.assertTrue(report["visual_rhythm"]["flat_flag"])
        self.assertTrue(report["summary"]["ok"])


if __name__ == "__main__":
    unittest.main()
