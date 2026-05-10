"""Tests for extract_rules.py CLI flags and integration with extends."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"
SCRIPT = Path(__file__).parent.parent.parent / "skills" / "brand-voice" / "scripts" / "extract_rules.py"


def _run(*args):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result


class TestFullDefault(unittest.TestCase):
    def test_full_emits_core_attributes(self):
        r = _run(str(FIXTURES / "parent-corp.md"))
        self.assertEqual(r.returncode, 0)
        self.assertIn("core_attributes:", r.stdout)
        self.assertIn("[precise]", r.stdout)

    def test_full_emits_source_urls(self):
        r = _run(str(FIXTURES / "parent-corp.md"))
        self.assertIn("source_urls:", r.stdout)
        self.assertIn("https://example.com", r.stdout)

    def test_full_emits_contexts(self):
        r = _run(str(FIXTURES / "parent-corp.md"))
        self.assertIn("contexts:", r.stdout)
        self.assertIn("rfc:", r.stdout)


class TestLegacy(unittest.TestCase):
    def test_legacy_skips_core_attributes(self):
        r = _run("--legacy", str(FIXTURES / "parent-corp.md"))
        self.assertEqual(r.returncode, 0)
        self.assertNotIn("core_attributes:", r.stdout)
        self.assertNotIn("source_urls:", r.stdout)
        self.assertNotIn("contexts:", r.stdout)

    def test_legacy_full_mutually_exclusive(self):
        r = _run("--legacy", "--full", str(FIXTURES / "parent-corp.md"))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("mutually exclusive", r.stderr)


class TestResolveExtends(unittest.TestCase):
    def test_default_resolves_chain(self):
        r = _run(str(FIXTURES / "child-founder.md"))
        self.assertEqual(r.returncode, 0)
        # Founder voice: should see merged forbidden_lexicon (parent's + child's, minus removed)
        self.assertIn("game-changing", r.stdout)
        self.assertIn("synergies", r.stdout)
        self.assertIn("thought leader", r.stdout)
        # 'passionate' was removed via _remove
        self.assertNotIn("passionate", r.stdout)

    def test_no_resolve_extends(self):
        r = _run("--no-resolve-extends", str(FIXTURES / "child-founder.md"))
        self.assertEqual(r.returncode, 0)
        # Without resolution: child-only forbidden_lexicon = ["thought leader"]
        self.assertIn("thought leader", r.stdout)
        self.assertNotIn("game-changing", r.stdout)


class TestExplain(unittest.TestCase):
    def test_explain_annotates_provenance(self):
        r = _run("--explain", str(FIXTURES / "child-founder.md"))
        self.assertEqual(r.returncode, 0)
        # Each forbidden entry should have '# from <relpath>' annotation
        self.assertIn("# from parent-corp.md", r.stdout)
        self.assertIn("# from child-founder.md", r.stdout)

    def test_explain_json_emits_structured(self):
        r = _run("--explain-json", str(FIXTURES / "child-founder.md"))
        self.assertEqual(r.returncode, 0)
        data = json.loads(r.stdout)
        self.assertIn("chain", data)
        self.assertIn("merged", data)
        # Each forbidden entry has a source field
        for entry in data["merged"]["forbidden_lexicon"]:
            self.assertIn("source", entry)
            self.assertIn("value", entry)


class TestLexicalExceptions(unittest.TestCase):
    """--full emits lexical_exceptions block when present."""

    def test_full_emits_lexical_exceptions(self):
        r = _run(str(FIXTURES / "parent-with-lexical-exceptions.md"))
        self.assertEqual(r.returncode, 0)
        self.assertIn("lexical_exceptions:", r.stdout)
        self.assertIn("BPM", r.stdout)
        self.assertIn("MIDI", r.stdout)
        self.assertIn("in-your-face", r.stdout)

    def test_legacy_skips_lexical_exceptions(self):
        r = _run("--legacy", str(FIXTURES / "parent-with-lexical-exceptions.md"))
        self.assertEqual(r.returncode, 0)
        self.assertNotIn("lexical_exceptions:", r.stdout)

    def test_inheritance_unions_lists(self):
        r = _run(str(FIXTURES / "child-extends-lexical-exceptions.md"))
        self.assertEqual(r.returncode, 0)
        # Parent's BPM/MIDI + child's DAW
        self.assertIn("BPM", r.stdout)
        self.assertIn("MIDI", r.stdout)
        self.assertIn("DAW", r.stdout)
        # Parent's in-your-face + child's do-it-yourself
        self.assertIn("in-your-face", r.stdout)
        self.assertIn("do-it-yourself", r.stdout)

    def test_replace_drops_parent_lists(self):
        r = _run(str(FIXTURES / "child-replaces-lexical-exceptions.md"))
        self.assertEqual(r.returncode, 0)
        self.assertIn("API", r.stdout)
        # BPM/MIDI/in-your-face from parent must be gone after _replace
        self.assertNotIn("BPM", r.stdout)
        self.assertNotIn("MIDI", r.stdout)
        self.assertNotIn("in-your-face", r.stdout)

    def test_full_omits_section_when_inner_lists_empty(self):
        """A YAML with `lexical_exceptions: {acronyms: [], compound_idioms: []}`
        must NOT emit a blank `lexical_exceptions:` section in --full output —
        empty fields are omitted to keep the LLM prompt lean. Pinned because
        the conditional at extract_rules.py:249 is easy to invert by accident."""
        import tempfile
        body = (
            "---\n"
            "voice:\n  name: \"EmptyLex\"\n"
            "forbidden_lexicon:\n  - \"foo\"\n"
            "rewrite_rules:\n  - reject: \"a\"\n    accept: \"b\"\n    rule_id: r\n"
            "sentence_norms:\n  word_count_min: 8\n  word_count_max: 18\n  sentence_max_hard: 25\n"
            "lexical_exceptions:\n  acronyms: []\n  compound_idioms: []\n"
            "---\n# Brand Voice — EmptyLex\n## 1. Core voice attributes\nstub stub stub stub stub stub stub stub.\n"
            "## 2. Rewrite rules — do/don't\nstub stub stub stub stub stub stub stub.\n"
            "## 3. Forbidden lexicon and patterns\nstub stub stub stub stub stub stub stub.\n"
            "## 4. Sentence-level norms\nstub stub stub stub stub stub stub stub.\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(body)
            path = f.name
        try:
            r = _run(path)
            self.assertEqual(r.returncode, 0)
            self.assertNotIn("lexical_exceptions:", r.stdout,
                             "empty inner lists must omit the whole section")
        finally:
            Path(path).unlink()


class TestUtf8Bom(unittest.TestCase):
    """Editors that save BRAND-VOICE.md with a UTF-8 BOM (U+FEFF prefix) must
    not silently break frontmatter detection. Without BOM stripping, the
    leading `\\ufeff---` would not match `---` and split_frontmatter would
    return (None, text) — extract_rules would then exit 1 with `no YAML
    frontmatter` despite the file being well-formed."""

    def test_extract_rules_handles_bom_prefixed_voice_doc(self):
        import tempfile
        bom = "﻿"
        body = (
            "---\n"
            "voice:\n  name: \"BomTest\"\n"
            "forbidden_lexicon:\n  - \"foo\"\n"
            "rewrite_rules:\n  - reject: \"a\"\n    accept: \"b\"\n    rule_id: r\n"
            "sentence_norms:\n  word_count_min: 8\n  word_count_max: 18\n  sentence_max_hard: 25\n"
            "---\n# Brand Voice — BomTest\n## 1. Core voice attributes\nstub stub stub stub stub stub stub stub.\n"
            "## 2. Rewrite rules — do/don't\nstub stub stub stub stub stub stub stub.\n"
            "## 3. Forbidden lexicon and patterns\nstub stub stub stub stub stub stub stub.\n"
            "## 4. Sentence-level norms\nstub stub stub stub stub stub stub stub.\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md",
                                          delete=False, encoding="utf-8") as f:
            f.write(bom + body)
            path = f.name
        try:
            r = _run(path)
            self.assertEqual(r.returncode, 0,
                             f"BOM-prefixed file must parse, got stderr: {r.stderr}")
            self.assertIn("voice: BomTest", r.stdout,
                          "BOM-prefixed YAML must still resolve voice.name")
        finally:
            Path(path).unlink()


class TestExitCodes(unittest.TestCase):
    def test_missing_file(self):
        r = _run(str(FIXTURES / "_does_not_exist.md"))
        self.assertEqual(r.returncode, 1)
        # The failure message must surface the original path so callers can
        # diagnose typos or wrong working directory without re-running.
        self.assertIn("_does_not_exist.md", r.stderr)

    def test_cycle_returns_error(self):
        r = _run(str(FIXTURES / "cycle-a.md"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("extends-cycle", r.stderr)

    def test_depth_exceeded(self):
        r = _run(str(FIXTURES / "depth-1.md"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("extends-depth-exceeded", r.stderr)


if __name__ == "__main__":
    unittest.main()
