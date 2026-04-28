"""Tests for prescan.py — pattern matching, masking, and scan integration.

Each of the 8 patterns gets positive (must trigger) and negative (must not trigger)
cases. Masking ensures code/URLs/frontmatter are never flagged. The scan() integration
verifies end-to-end behavior on multi-pattern documents.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO_ROOT / "skills" / "humanize-en" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from prescan import PATTERNS, mask_protected_regions, scan  # noqa: E402

SCRIPT = SCRIPTS / "prescan.py"


def _hits_for_pattern(text, pattern_id):
    return [h for h in scan(text) if h["pattern"] == pattern_id]


class TestSignificanceInflation(unittest.TestCase):
    """Pattern 1 — pivotal moment, testament to, evolving landscape, today's world, etc."""

    def test_triggers_pivotal_moment(self):
        self.assertGreater(len(_hits_for_pattern("This is a pivotal moment for AI.", 1)), 0)

    def test_triggers_testament_to(self):
        self.assertGreater(len(_hits_for_pattern("Their work is a testament to discipline.", 1)), 0)

    def test_triggers_game_changing(self):
        self.assertGreater(len(_hits_for_pattern("A game-changing release.", 1)), 0)

    def test_does_not_trigger_pivotal_alone(self):
        """`pivotal` outside the `pivotal moment/role` collocation belongs to pattern 7
        (ai-vocabulary), not pattern 1. We assert BOTH directions so this test
        cannot quietly lie if pattern 1 regex breaks (the filter would mask the
        regression). Pattern 7 must still trigger on bare `pivotal`."""
        text = "That decision was pivotal."
        self.assertEqual(_hits_for_pattern(text, 1), [])
        self.assertGreater(len(_hits_for_pattern(text, 7)), 0,
                           "pattern 7 should trigger on bare 'pivotal'")


class TestPromotional(unittest.TestCase):
    """Pattern 4 — nestled, breathtaking, vibrant, etc."""

    def test_triggers_nestled(self):
        self.assertGreater(len(_hits_for_pattern("Nestled in the mountains.", 4)), 0)

    def test_triggers_breathtaking(self):
        self.assertGreater(len(_hits_for_pattern("Breathtaking views await.", 4)), 0)

    def test_does_not_trigger_random_word(self):
        self.assertEqual(_hits_for_pattern("The view was nice.", 4), [])


class TestAIVocabulary(unittest.TestCase):
    """Pattern 7 — delve, tapestry, crucial, underscore, moreover, indeed, etc."""

    def test_triggers_delve(self):
        self.assertGreater(len(_hits_for_pattern("Let us delve into the data.", 7)), 0)

    def test_triggers_moreover(self):
        self.assertGreater(len(_hits_for_pattern("Moreover, the trend continues.", 7)), 0)

    def test_triggers_underscore_inflected(self):
        for verb in ("underscores", "underscored", "underscoring"):
            with self.subTest(verb=verb):
                self.assertGreater(
                    len(_hits_for_pattern(f"This {verb} the point.", 7)), 0
                )

    def test_navigate_complexity_collocation(self):
        self.assertGreater(
            len(_hits_for_pattern("They navigate the complexities of regulation.", 7)), 0
        )


class TestCopulaAvoidance(unittest.TestCase):
    """Pattern 8 — serves as, stands as, boasts, features a/an/the."""

    def test_triggers_serves_as(self):
        self.assertGreater(len(_hits_for_pattern("It serves as a reminder.", 8)), 0)

    def test_triggers_features_a(self):
        self.assertGreater(len(_hits_for_pattern("The car features a new engine.", 8)), 0)

    def test_does_not_trigger_features_plural(self):
        """`features` followed by a non-article noun should not trigger."""
        self.assertEqual(_hits_for_pattern("Notable features include speed.", 8), [])


class TestNegativeParallelism(unittest.TestCase):
    """Pattern 9 — `it's not just X, it's Y` and `not only X but also Y`."""

    def test_triggers_its_not_just(self):
        self.assertGreater(
            len(_hits_for_pattern("It's not just fast, it's instant.", 9)), 0
        )

    def test_triggers_not_only_but_also(self):
        self.assertGreater(
            len(_hits_for_pattern("Not only is it fast but also reliable.", 9)), 0
        )


class TestFiller(unittest.TestCase):
    """Pattern 23 — in order to, it is important to note, please note, etc."""

    def test_triggers_in_order_to(self):
        self.assertGreater(len(_hits_for_pattern("Click here in order to proceed.", 23)), 0)

    def test_triggers_it_is_important_to_note(self):
        self.assertGreater(
            len(_hits_for_pattern("It is important to note that this is true.", 23)), 0
        )

    def test_does_not_trigger_to_alone(self):
        self.assertEqual(_hits_for_pattern("Press to continue.", 23), [])


class TestSignposting(unittest.TestCase):
    """Pattern 28 — let's dive in, without further ado, in conclusion, etc."""

    def test_triggers_lets_dive_in(self):
        self.assertGreater(len(_hits_for_pattern("Let's dive into the topic.", 28)), 0)

    def test_triggers_in_conclusion(self):
        self.assertGreater(len(_hits_for_pattern("In conclusion, the data shows...", 28)), 0)


class TestEmDashDensity(unittest.TestCase):
    """Pattern 14 — flag lines with ≥3 em-dashes (cheap proxy for density)."""

    def test_triggers_three_em_dashes(self):
        line = "We saw — felt — and recorded — the change."
        self.assertGreater(len(_hits_for_pattern(line, 14)), 0)

    def test_does_not_trigger_two_em_dashes(self):
        self.assertEqual(
            _hits_for_pattern("Some text — with one — pause.", 14), []
        )

    def test_does_not_trigger_hyphens(self):
        """ASCII hyphen is not U+2014 — must not trip the density check."""
        line = "We saw - felt - and recorded - the change."
        self.assertEqual(_hits_for_pattern(line, 14), [])


class TestMasking(unittest.TestCase):
    """Protected regions (code, URLs, frontmatter) must be masked before scan."""

    def test_fenced_code_block_masked(self):
        text = "Outside.\n```\npivotal moment in code\n```\nAlso outside."
        hits = _hits_for_pattern(text, 1)
        # No hit because the only candidate phrase is in a code block
        self.assertEqual(hits, [])

    def test_inline_backticks_masked(self):
        text = "Use `pivotal moment` syntax to reference."
        self.assertEqual(_hits_for_pattern(text, 1), [])

    def test_yaml_frontmatter_masked(self):
        text = "---\nname: pivotal moment example\n---\nProse here."
        self.assertEqual(_hits_for_pattern(text, 1), [])

    def test_url_masked(self):
        text = "See https://example.com/pivotal-moment-guide for context."
        self.assertEqual(_hits_for_pattern(text, 1), [])

    def test_markdown_link_target_masked(self):
        text = "Visit [the guide](https://example.com/delve-into) for help."
        # 'delve' inside the URL must be masked
        self.assertEqual(_hits_for_pattern(text, 7), [])

    def test_line_numbers_preserved_through_masking(self):
        """Mask must replace with spaces (not delete) so subsequent line numbers stay correct."""
        text = "line one\n```\ncode line\n```\npivotal moment\n"
        hits = _hits_for_pattern(text, 1)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["line"], 5)


class TestScanShape(unittest.TestCase):
    """scan() output schema invariants."""

    def test_each_hit_has_required_keys(self):
        hits = scan("This is pivotal moment text.\nMoreover, more text.")
        self.assertGreater(len(hits), 0)
        for h in hits:
            for key in ("pattern", "label", "line", "snippet"):
                self.assertIn(key, h)

    def test_hits_carry_pattern_id_and_label(self):
        hits = scan("Moreover, this is fine.")
        match = [h for h in hits if h["pattern"] == 7]
        self.assertGreater(len(match), 0)
        self.assertEqual(match[0]["label"], "ai-vocabulary")


class TestCLI(unittest.TestCase):
    """Run prescan.py as a subprocess for end-to-end behavior."""

    def _run(self, *args, stdin=None):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            input=stdin,
            capture_output=True,
            text=True,
        )

    def test_no_args_exits_1(self):
        r = self._run()
        self.assertEqual(r.returncode, 1)
        self.assertIn("usage", r.stderr)

    def test_missing_file_exits_1(self):
        r = self._run("/tmp/_does_not_exist_humanize.md")
        self.assertEqual(r.returncode, 1)
        self.assertIn("not found", r.stderr)

    def test_stdin_works(self):
        r = self._run("-", stdin="Moreover, the test passes.")
        self.assertEqual(r.returncode, 0)
        data = json.loads(r.stdout)
        self.assertGreater(len(data), 0)

    def test_clean_text_returns_empty_array(self):
        r = self._run("-", stdin="The cat sat on the mat. The dog ran fast.\n")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), [])


class TestPatternsRegistry(unittest.TestCase):
    """The PATTERNS list must remain a stable registry — every entry has the
    correct shape and unique IDs. Catches accidental duplication or shape drift."""

    def test_pattern_count(self):
        # 7 regex patterns + em-dash density = 8 covered, but PATTERNS only holds 7
        # since em-dash uses a separate counter.
        self.assertEqual(len(PATTERNS), 7)

    def test_unique_pattern_ids(self):
        ids = [p[0] for p in PATTERNS]
        self.assertEqual(len(ids), len(set(ids)), "duplicate pattern IDs in registry")

    def test_each_entry_is_3tuple(self):
        for entry in PATTERNS:
            self.assertEqual(len(entry), 3)
            self.assertIsInstance(entry[0], int)
            self.assertIsInstance(entry[1], str)
            # Third is a compiled regex — has .search method
            self.assertTrue(hasattr(entry[2], "search"))


if __name__ == "__main__":
    unittest.main()
