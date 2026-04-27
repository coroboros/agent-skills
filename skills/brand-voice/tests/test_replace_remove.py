"""Tests for `_replace` and `_remove` semantics."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from utils import (  # noqa: E402
    apply_remove_overrides,
    apply_replace_overrides,
    merge_voice_dicts,
    resolve_and_merge,
)

FIXTURES = Path(__file__).parent / "fixtures"


class TestReplaceOverrides(unittest.TestCase):
    def test_replace_replaces_canonical(self):
        merged = {
            "forbidden_lexicon": ["a", "b"],
            "forbidden_lexicon_replace": ["x"],
        }
        out = apply_replace_overrides(merged)
        self.assertEqual(out["forbidden_lexicon"], ["x"])
        self.assertNotIn("forbidden_lexicon_replace", out)

    def test_replace_pronouns_full_block(self):
        merged = {
            "pronouns": {"default": "third-person", "forbid": ["first-person singular"]},
            "pronouns_replace": {"default": "first-person singular", "forbid": []},
        }
        out = apply_replace_overrides(merged)
        self.assertEqual(out["pronouns"]["default"], "first-person singular")
        self.assertEqual(out["pronouns"]["forbid"], [])
        self.assertNotIn("pronouns_replace", out)

    def test_replace_unsupported_field_left_alone(self):
        """`voice.name_replace` is not whitelisted; apply_replace_overrides
        leaves it alone (the linter flags it)."""
        merged = {
            "voice": {"name": "Parent"},
            "voice_replace": {"name": "Child"},
        }
        out = apply_replace_overrides(merged)
        # voice_replace is NOT in REPLACE_ALLOWED_FIELDS — left unchanged
        self.assertIn("voice_replace", out)
        self.assertEqual(out["voice"]["name"], "Parent")


class TestRemoveOverrides(unittest.TestCase):
    def test_remove_subtracts_strings(self):
        merged = {
            "forbidden_lexicon": ["a", "b", "c"],
            "forbidden_lexicon_remove": ["b"],
        }
        out = apply_remove_overrides(merged)
        self.assertEqual(out["forbidden_lexicon"], ["a", "c"])
        self.assertNotIn("forbidden_lexicon_remove", out)

    def test_remove_rewrite_rules_by_id(self):
        merged = {
            "rewrite_rules": [
                {"rule_id": "a", "reject": "x", "accept": "y"},
                {"rule_id": "b", "reject": "x", "accept": "y"},
                {"rule_id": "c", "reject": "x", "accept": "y"},
            ],
            "rewrite_rules_remove": ["b"],
        }
        out = apply_remove_overrides(merged)
        ids = [r["rule_id"] for r in out["rewrite_rules"]]
        self.assertEqual(ids, ["a", "c"])

    def test_remove_core_attributes_by_id(self):
        merged = {
            "core_attributes": [
                {"attribute_id": "auth", "name": "Authoritative"},
                {"attribute_id": "tech", "name": "Technical"},
            ],
            "core_attributes_remove": ["auth"],
        }
        out = apply_remove_overrides(merged)
        ids = [a["attribute_id"] for a in out["core_attributes"]]
        self.assertEqual(ids, ["tech"])

    def test_remove_unsupported_field_left_alone(self):
        merged = {
            "voice": {"name": "x"},
            "voice_remove": ["whatever"],
        }
        out = apply_remove_overrides(merged)
        self.assertIn("voice_remove", out)


class TestEndToEndOverrides(unittest.TestCase):
    def test_child_remove_lexicon_subtracts_parent_entries(self):
        chain, merged = resolve_and_merge(FIXTURES / "child-remove-lexicon.md")
        # Parent had: ["game-changing", "passionate", "synergies"]
        # Child removes: ["passionate", "synergies"]
        # Result: ["game-changing"]
        self.assertEqual(merged["forbidden_lexicon"], ["game-changing"])

    def test_child_replace_pronouns_drops_parents_block(self):
        chain, merged = resolve_and_merge(FIXTURES / "child-replace-pronouns.md")
        # Parent had: {default: third-person, forbid: [first-person singular]}
        # Child replaced with: {default: first-person plural, forbid: [second-person 'you' as command]}
        self.assertEqual(merged["pronouns"]["default"], "first-person plural")
        self.assertEqual(merged["pronouns"]["forbid"], ["second-person 'you' as command"])

    def test_child_founder_full_inheritance(self):
        chain, merged = resolve_and_merge(FIXTURES / "child-founder.md")
        # forbidden_lexicon: parent had [game-changing, passionate, synergies]
        # child added [thought leader] and removed [passionate]
        self.assertIn("game-changing", merged["forbidden_lexicon"])
        self.assertIn("synergies", merged["forbidden_lexicon"])
        self.assertIn("thought leader", merged["forbidden_lexicon"])
        self.assertNotIn("passionate", merged["forbidden_lexicon"])
        # pronouns_replace flipped to first-person
        self.assertEqual(merged["pronouns"]["default"], "first-person singular")
        # rewrite_rules: parent's 2 + child's 1 = 3
        ids = [r["rule_id"] for r in merged["rewrite_rules"]]
        self.assertIn("no-hedging-imperative", ids)
        self.assertIn("specific-over-abstract-speed", ids)
        self.assertIn("founder-no-third-person-self", ids)
        # core_attributes: parent's 2 (precise, technical) + child's 1 (warm)
        attr_ids = [a["attribute_id"] for a in merged["core_attributes"]]
        self.assertEqual(attr_ids, ["precise", "technical", "warm"])
        # contexts: parent's rfc + readme + child's blog = 3
        self.assertIn("rfc", merged["contexts"])
        self.assertIn("readme", merged["contexts"])
        self.assertIn("blog", merged["contexts"])

    def test_child_pure_inherit_minimal_overrides(self):
        chain, merged = resolve_and_merge(FIXTURES / "child-pure-inherit.md")
        # forbidden_lexicon: child empty → parent's 3
        self.assertEqual(set(merged["forbidden_lexicon"]),
                         {"game-changing", "passionate", "synergies"})
        # rewrite_rules: parent's 2 + child's 1 stub = 3
        self.assertEqual(len(merged["rewrite_rules"]), 3)
        # core_attributes: parent's 2 + child's 1 = 3
        self.assertEqual(len(merged["core_attributes"]), 3)


if __name__ == "__main__":
    unittest.main()
