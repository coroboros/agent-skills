"""Tests for voice_lint.py error codes, validation order, and source discriminator."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from voice_lint import lint  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"


def _read(path):
    return Path(path).read_text(encoding="utf-8")


def _codes(items):
    return [item["code"] for item in items]


class TestParentCorpGreen(unittest.TestCase):
    def test_parent_corp_lints_green(self):
        result = lint(_read(FIXTURES / "parent-corp.md"), str(FIXTURES / "parent-corp.md"))
        # Should be GREEN or YELLOW (no errors). Possibly YELLOW for outdated/age warnings.
        self.assertNotEqual(result["verdict"], "RED")
        self.assertEqual(result["errors"], [])


class TestInheritanceErrors(unittest.TestCase):
    def test_replace_without_extends(self):
        path = FIXTURES / "replace-without-extends.md"
        result = lint(_read(path), str(path))
        self.assertEqual(result["verdict"], "RED")
        self.assertIn("replace-without-extends", _codes(result["errors"]))

    def test_replace_and_cousin_mutex(self):
        path = FIXTURES / "replace-and-cousin.md"
        result = lint(_read(path), str(path))
        self.assertEqual(result["verdict"], "RED")
        self.assertIn("replace-conflict-with-extending", _codes(result["errors"]))

    def test_unsupported_replace_field(self):
        path = FIXTURES / "unsupported-replace.md"
        result = lint(_read(path), str(path))
        self.assertEqual(result["verdict"], "RED")
        self.assertIn("replace-on-unsupported-field", _codes(result["errors"]))

    def test_core_attribute_missing_id_under_extends_is_red(self):
        path = FIXTURES / "core-attr-missing-id.md"
        result = lint(_read(path), str(path))
        self.assertEqual(result["verdict"], "RED")
        self.assertIn("core-attribute-missing-id", _codes(result["errors"]))

    def test_core_attribute_missing_id_without_extends_is_also_red(self):
        """attribute_id is REQUIRED on every core_attributes entry, regardless of
        whether voice.extends is set. No soft-migration warning — the schema is
        strict because the merge key needs a stable identifier."""
        import tempfile
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False)
        tmp.write(
            "---\n"
            "voice:\n  name: \"NoExtends\"\n  last_updated: \"2026-04-27\"\n"
            "core_attributes:\n  - name: \"Foo\"\n    failure_mode: \"bar\"\n"
            "forbidden_lexicon: [\"x\"]\n"
            "rewrite_rules:\n  - reject: \"a\"\n    accept: \"b\"\n    rule_id: r\n"
            "sentence_norms:\n  word_count_min: 8\n  word_count_max: 22\n  sentence_max_hard: 30\n"
            "---\n# Brand Voice — NoExtends\n## 1. Core voice attributes\nStub stub stub stub stub stub stub stub stub stub.\n"
            "## 2. Rewrite rules — do/don't\nStub stub stub stub stub stub stub stub stub stub.\n"
            "## 3. Forbidden lexicon and patterns\nStub stub stub stub stub stub stub stub stub stub.\n"
            "## 4. Sentence-level norms\nStub stub stub stub stub stub stub stub stub stub.\n"
        )
        tmp.close()
        try:
            result = lint(_read(tmp.name), tmp.name)
            self.assertEqual(result["verdict"], "RED")
            self.assertIn("core-attribute-missing-id", _codes(result["errors"]))
        finally:
            Path(tmp.name).unlink()


class TestChainErrors(unittest.TestCase):
    def test_cycle_detected(self):
        path = FIXTURES / "cycle-a.md"
        result = lint(_read(path), str(path))
        self.assertEqual(result["verdict"], "RED")
        self.assertIn("extends-cycle", _codes(result["errors"]))

    def test_cycle_self_detected(self):
        path = FIXTURES / "cycle-self.md"
        result = lint(_read(path), str(path))
        self.assertEqual(result["verdict"], "RED")
        self.assertIn("extends-cycle", _codes(result["errors"]))

    def test_depth_exceeded(self):
        path = FIXTURES / "depth-1.md"
        result = lint(_read(path), str(path))
        self.assertEqual(result["verdict"], "RED")
        self.assertIn("extends-depth-exceeded", _codes(result["errors"]))

    def test_missing_parent(self):
        path = FIXTURES / "missing-parent.md"
        result = lint(_read(path), str(path))
        self.assertEqual(result["verdict"], "RED")
        self.assertIn("extends-parent-not-found", _codes(result["errors"]))

    def test_invalid_parent_aggregated(self):
        path = FIXTURES / "invalid-parent.md"
        result = lint(_read(path), str(path))
        self.assertEqual(result["verdict"], "RED")
        codes = _codes(result["errors"])
        self.assertIn("extends-parent-invalid", codes)
        # The wrapping error carries the actual parent_errors as a nested array
        wrapping = next(e for e in result["errors"] if e["code"] == "extends-parent-invalid")
        self.assertIn("parent_errors", wrapping)
        self.assertGreater(len(wrapping["parent_errors"]), 0)


class TestChainSuccess(unittest.TestCase):
    def test_child_pure_inherit_chain_resolves(self):
        path = FIXTURES / "child-pure-inherit.md"
        result = lint(_read(path), str(path))
        # Child has empty forbidden_lexicon (warning), parent is fine — should be YELLOW or GREEN
        self.assertNotEqual(result["verdict"], "RED")
        self.assertIn("chain", result)
        # Chain has 2 entries: parent, child
        self.assertEqual(len(result["chain"]), 2)
        self.assertIn("merged_stats", result)
        self.assertGreater(result["merged_stats"]["forbidden_lexicon_count"], 0)

    def test_silent_override_warns(self):
        path = FIXTURES / "child-override-rule-silent.md"
        result = lint(_read(path), str(path))
        # Should be YELLOW (no errors, has rewrite-rule-overridden-by-child warning)
        self.assertNotEqual(result["verdict"], "RED")
        self.assertIn("rewrite-rule-overridden-by-child", _codes(result["warnings"]))

    def test_explicit_override_silenced(self):
        path = FIXTURES / "child-override-rule.md"
        result = lint(_read(path), str(path))
        self.assertNotEqual(result["verdict"], "RED")
        self.assertNotIn("rewrite-rule-overridden-by-child", _codes(result["warnings"]))

    def test_canonical_field_plus_remove_is_valid(self):
        """child-founder.md declares both `forbidden_lexicon` (additive) and
        `forbidden_lexicon_remove` (selective subtraction). This combination
        is intentionally valid — the common case where a child adds a few
        entries and removes a couple of inherited ones."""
        path = FIXTURES / "child-founder.md"
        result = lint(_read(path), str(path))
        self.assertNotEqual(result["verdict"], "RED")
        self.assertNotIn("replace-conflict-with-extending", _codes(result["errors"]))


class TestSourceDiscriminator(unittest.TestCase):
    def test_child_errors_tagged_child(self):
        path = FIXTURES / "replace-without-extends.md"
        result = lint(_read(path), str(path))
        # The replace-without-extends error originates in the child file
        e = next(x for x in result["errors"] if x["code"] == "replace-without-extends")
        self.assertEqual(e.get("source"), "child")

    def test_parent_errors_carry_source_path(self):
        path = FIXTURES / "invalid-parent.md"
        result = lint(_read(path), str(path))
        e = next(x for x in result["errors"] if x["code"] == "extends-parent-invalid")
        self.assertTrue(e.get("source", "").startswith("parent:"))
        self.assertTrue(e.get("source_path", "").endswith("_invalid-parent-target.md"))


if __name__ == "__main__":
    unittest.main()
