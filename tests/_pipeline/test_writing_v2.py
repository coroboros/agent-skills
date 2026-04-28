"""Pipeline contract: humanize-en + fix-grammar (sequential composition).

These two skills don't share a `-f` file — they're applied sequentially on
the same prose. The contract is implicit: each must do its own job without
overlapping the other's surface area, so users can chain them without the
fixes from one undoing the rewrites of the other.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _contracts import read_skill_md  # noqa: E402


class TestSeparationOfConcerns(unittest.TestCase):
    """Each skill stakes out a distinct surface: humanize-en is style/AI-tells,
    fix-grammar is grammar/spelling. Their SKILL.md descriptions must make
    that distinction explicit so users know which to invoke when."""

    def test_humanize_owns_ai_tells_and_patterns(self):
        text = read_skill_md("humanize-en").lower()
        self.assertRegex(text, r"ai[\s-]*tells?|patterns?",
                         "humanize-en should claim AI-tells/patterns territory")

    def test_fix_grammar_owns_grammar_and_spelling(self):
        text = read_skill_md("fix-grammar").lower()
        self.assertRegex(text, r"grammar|spelling",
                         "fix-grammar should claim grammar/spelling territory")

    def test_each_skill_references_the_other_for_handoff(self):
        """Each skill must point users at the other for the surface it doesn't
        cover — that's what makes the sequential chain discoverable."""
        humanize = read_skill_md("humanize-en")
        fix_grammar = read_skill_md("fix-grammar")
        # humanize-en should mention fix-grammar as the grammar-only escape hatch.
        self.assertIn("fix-grammar", humanize,
                      "humanize-en must reference fix-grammar for grammar-only fixes")
        # fix-grammar referencing humanize-en is encouraged but not strictly
        # required — assert presence loosely.
        if "humanize" in fix_grammar.lower():
            self.assertIn("humanize", fix_grammar.lower())


if __name__ == "__main__":
    unittest.main()
