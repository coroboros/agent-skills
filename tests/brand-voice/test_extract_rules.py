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
