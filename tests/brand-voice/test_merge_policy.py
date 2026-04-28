"""Tests for per-field merge policy."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "skills" / "brand-voice" / "scripts"))
from utils import merge_voice_dicts  # noqa: E402


class TestListUnionDedup(unittest.TestCase):
    def test_forbidden_lexicon_union(self):
        parent = {"forbidden_lexicon": ["a", "b"]}
        child = {"forbidden_lexicon": ["c"]}
        merged = merge_voice_dicts(parent, child)
        self.assertEqual(merged["forbidden_lexicon"], ["a", "b", "c"])

    def test_forbidden_lexicon_dedup_preserves_order(self):
        parent = {"forbidden_lexicon": ["a", "b"]}
        child = {"forbidden_lexicon": ["b", "c"]}
        merged = merge_voice_dicts(parent, child)
        self.assertEqual(merged["forbidden_lexicon"], ["a", "b", "c"])

    def test_required_lexicon_union(self):
        parent = {"required_lexicon": ["x"]}
        child = {"required_lexicon": ["y"]}
        merged = merge_voice_dicts(parent, child)
        self.assertEqual(merged["required_lexicon"], ["x", "y"])

    def test_forbidden_patterns_union(self):
        parent = {"forbidden_patterns": ["rule_of_three"]}
        child = {"forbidden_patterns": ["emoji"]}
        merged = merge_voice_dicts(parent, child)
        self.assertEqual(merged["forbidden_patterns"], ["rule_of_three", "emoji"])

    def test_empty_lists_omitted(self):
        merged = merge_voice_dicts({"forbidden_lexicon": []}, {"forbidden_lexicon": []})
        self.assertNotIn("forbidden_lexicon", merged)


class TestKeyedListMerge(unittest.TestCase):
    def test_rewrite_rules_merge_by_rule_id(self):
        parent = {"rewrite_rules": [
            {"rule_id": "a", "reject": "old-a", "accept": "ok"},
            {"rule_id": "b", "reject": "old-b", "accept": "ok"},
        ]}
        child = {"rewrite_rules": [
            {"rule_id": "a", "reject": "new-a", "accept": "ok"},  # overrides
            {"rule_id": "c", "reject": "new-c", "accept": "ok"},  # added
        ]}
        merged = merge_voice_dicts(parent, child)
        rules = merged["rewrite_rules"]
        self.assertEqual(len(rules), 3)
        ids = [r["rule_id"] for r in rules]
        self.assertEqual(ids, ["a", "b", "c"])
        self.assertEqual(rules[0]["reject"], "new-a")  # child wins

    def test_core_attributes_merge_by_attribute_id(self):
        parent = {"core_attributes": [
            {"attribute_id": "auth", "name": "Authoritative", "failure_mode": "soft"},
            {"attribute_id": "tech", "name": "Technical", "failure_mode": "fluffy"},
        ]}
        child = {"core_attributes": [
            {"attribute_id": "auth", "name": "Authoritative", "failure_mode": "softer"},
            {"attribute_id": "warm", "name": "Warm", "failure_mode": "cold"},
        ]}
        merged = merge_voice_dicts(parent, child)
        ids = [a["attribute_id"] for a in merged["core_attributes"]]
        self.assertEqual(ids, ["auth", "tech", "warm"])
        self.assertEqual(merged["core_attributes"][0]["failure_mode"], "softer")

    def test_core_attributes_fallback_normalized_name(self):
        """When attribute_id is absent, merge falls back to normalized name."""
        parent = {"core_attributes": [
            {"name": "Authoritative", "failure_mode": "soft"},
        ]}
        child = {"core_attributes": [
            {"name": "  authoritative  ", "failure_mode": "softer"},
        ]}
        merged = merge_voice_dicts(parent, child)
        self.assertEqual(len(merged["core_attributes"]), 1)
        self.assertEqual(merged["core_attributes"][0]["failure_mode"], "softer")


class TestObjectMerge(unittest.TestCase):
    def test_sentence_norms_shallow_merge(self):
        parent = {"sentence_norms": {"word_count_min": 8, "word_count_max": 18, "contractions": "allow"}}
        child = {"sentence_norms": {"word_count_max": 22}}
        merged = merge_voice_dicts(parent, child)
        self.assertEqual(merged["sentence_norms"]["word_count_min"], 8)
        self.assertEqual(merged["sentence_norms"]["word_count_max"], 22)
        self.assertEqual(merged["sentence_norms"]["contractions"], "allow")

    def test_contexts_deep_merge_by_name(self):
        parent = {"contexts": {
            "rfc": {"density": "max", "numbered_sections": True},
            "readme": {"tagline_first": True},
        }}
        child = {"contexts": {
            "rfc": {"density": "high"},  # overrides density, keeps numbered_sections
            "blog": {"open_with_anecdote": True},  # new context
        }}
        merged = merge_voice_dicts(parent, child)
        self.assertEqual(merged["contexts"]["rfc"]["density"], "high")
        self.assertTrue(merged["contexts"]["rfc"]["numbered_sections"])
        self.assertTrue(merged["contexts"]["readme"]["tagline_first"])
        self.assertTrue(merged["contexts"]["blog"]["open_with_anecdote"])

    def test_pronouns_shallow_merge(self):
        parent = {"pronouns": {"default": "third-person", "forbid": ["first-person singular"]}}
        child = {"pronouns": {"default": "first-person singular"}}
        merged = merge_voice_dicts(parent, child)
        self.assertEqual(merged["pronouns"]["default"], "first-person singular")
        # Child didn't declare forbid → parent's preserved
        self.assertEqual(merged["pronouns"]["forbid"], ["first-person singular"])

    def test_pronouns_forbid_replaced_when_child_declares(self):
        """pronouns.forbid is the one place a child's list REPLACES parent's,
        because personas legitimately invert parent rules."""
        parent = {"pronouns": {"default": "third-person", "forbid": ["first-person singular"]}}
        child = {"pronouns": {"forbid": ["second-person 'you'"]}}
        merged = merge_voice_dicts(parent, child)
        # Child's forbid REPLACES parent's
        self.assertEqual(merged["pronouns"]["forbid"], ["second-person 'you'"])
        # Parent's default preserved
        self.assertEqual(merged["pronouns"]["default"], "third-person")


class TestVoiceMetadataMerge(unittest.TestCase):
    def test_voice_name_child_wins(self):
        parent = {"voice": {"name": "Parent"}}
        child = {"voice": {"name": "Child"}}
        merged = merge_voice_dicts(parent, child)
        self.assertEqual(merged["voice"]["name"], "Child")

    def test_voice_extends_not_inherited_downstream(self):
        """voice.extends is per-file metadata; never propagated through merge."""
        parent = {"voice": {"name": "Parent", "extends": "./grandparent.md"}}
        child = {"voice": {"name": "Child"}}
        merged = merge_voice_dicts(parent, child)
        self.assertNotIn("extends", merged["voice"])

    def test_voice_source_urls_child_wins(self):
        parent = {"voice": {"source_urls": ["a", "b"]}}
        child = {"voice": {"source_urls": ["c"]}}
        merged = merge_voice_dicts(parent, child)
        self.assertEqual(merged["voice"]["source_urls"], ["c"])


class TestEdgeCases(unittest.TestCase):
    def test_empty_parent(self):
        merged = merge_voice_dicts(None, {"forbidden_lexicon": ["a"]})
        self.assertEqual(merged["forbidden_lexicon"], ["a"])

    def test_empty_child(self):
        merged = merge_voice_dicts({"forbidden_lexicon": ["a"]}, None)
        self.assertEqual(merged["forbidden_lexicon"], ["a"])

    def test_both_empty(self):
        merged = merge_voice_dicts(None, None)
        self.assertEqual(merged, {})

    def test_replace_keys_carried_forward(self):
        """merge_voice_dicts carries _replace/_remove keys from child unchanged
        for downstream apply_*_overrides to consume."""
        merged = merge_voice_dicts(
            {"forbidden_lexicon": ["a"]},
            {"forbidden_lexicon_replace": ["x"]},
        )
        self.assertIn("forbidden_lexicon_replace", merged)
        self.assertEqual(merged["forbidden_lexicon_replace"], ["x"])

    def test_unknown_top_level_keys_passed_through(self):
        merged = merge_voice_dicts(
            {"forbidden_lexicon": ["a"], "experimental_flag": True},
            {"forbidden_lexicon": ["b"]},
        )
        self.assertEqual(merged.get("experimental_flag"), True)


if __name__ == "__main__":
    unittest.main()
