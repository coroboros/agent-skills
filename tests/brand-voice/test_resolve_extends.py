"""Tests for chain resolution: cycles, depth, identity, paths."""

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "skills" / "brand-voice" / "scripts"))
from utils import (  # noqa: E402
    ExtendsError,
    MAX_EXTENDS_DEPTH,
    canonical_file_id,
    resolve_extends_chain,
)

FIXTURES = Path(__file__).parent / "fixtures"


class TestChainResolution(unittest.TestCase):
    def test_single_node_no_extends(self):
        chain = resolve_extends_chain(FIXTURES / "parent-corp.md")
        self.assertEqual(len(chain), 1)
        path, data = chain[0]
        self.assertEqual(path.name, "parent-corp.md")
        self.assertEqual(data.get("voice", {}).get("name"), "ParentCorp")

    def test_two_node_chain(self):
        chain = resolve_extends_chain(FIXTURES / "child-pure-inherit.md")
        self.assertEqual(len(chain), 2)
        # Root-first: parent first, then child
        self.assertEqual(chain[0][0].name, "parent-corp.md")
        self.assertEqual(chain[1][0].name, "child-pure-inherit.md")

    def test_cycle_two_node(self):
        with self.assertRaises(ExtendsError) as ctx:
            resolve_extends_chain(FIXTURES / "cycle-a.md")
        self.assertEqual(ctx.exception.code, "extends-cycle")

    def test_cycle_self(self):
        with self.assertRaises(ExtendsError) as ctx:
            resolve_extends_chain(FIXTURES / "cycle-self.md")
        self.assertEqual(ctx.exception.code, "extends-cycle")

    def test_depth_exceeded(self):
        with self.assertRaises(ExtendsError) as ctx:
            resolve_extends_chain(FIXTURES / "depth-1.md")
        self.assertEqual(ctx.exception.code, "extends-depth-exceeded")

    def test_depth_at_limit_succeeds(self):
        # depth-2.md → depth-3 → depth-4 → depth-5 → depth-6 → depth-7 = 5 hops, depth=5 (at limit)
        chain = resolve_extends_chain(FIXTURES / "depth-2.md")
        self.assertEqual(len(chain), 6)
        self.assertEqual(chain[0][0].name, "depth-7.md")
        self.assertEqual(chain[-1][0].name, "depth-2.md")

    def test_missing_parent(self):
        with self.assertRaises(ExtendsError) as ctx:
            resolve_extends_chain(FIXTURES / "missing-parent.md")
        self.assertEqual(ctx.exception.code, "extends-parent-not-found")

    def test_invalid_parent_yaml(self):
        # invalid-parent.md → _invalid-parent-target.md (which has missing required fields
        # but parses OK as YAML; resolve_extends_chain only checks parseability, not lint)
        chain = resolve_extends_chain(FIXTURES / "invalid-parent.md")
        self.assertEqual(len(chain), 2)
        # Parent's voice.name is BrokenParent
        self.assertEqual(chain[0][1].get("voice", {}).get("name"), "BrokenParent")


class TestCanonicalFileId(unittest.TestCase):
    def test_same_path_same_id(self):
        p = FIXTURES / "parent-corp.md"
        self.assertEqual(canonical_file_id(p), canonical_file_id(p))

    def test_different_paths_different_ids(self):
        p1 = FIXTURES / "parent-corp.md"
        p2 = FIXTURES / "child-founder.md"
        self.assertNotEqual(canonical_file_id(p1), canonical_file_id(p2))

    def test_case_insensitive_filesystem_same_id(self):
        """On case-insensitive filesystems (default macOS), `./x.md` and `./X.md`
        resolve to different path strings but the same inode. canonical_file_id
        must produce equal IDs."""
        if os.name == "nt":
            self.skipTest("Windows uses path-based fallback")
        p_orig = FIXTURES / "parent-corp.md"
        # On macOS APFS-default, the upper-case form references the same file.
        p_upper = FIXTURES / "PARENT-CORP.md"
        try:
            p_upper_stat = p_upper.stat()
        except (FileNotFoundError, OSError):
            self.skipTest("filesystem is case-sensitive; skip")
        if not p_upper_stat:
            self.skipTest("filesystem is case-sensitive; skip")
        self.assertEqual(canonical_file_id(p_orig), canonical_file_id(p_upper))


class TestRelativePathResolution(unittest.TestCase):
    def test_relative_resolves_against_child_dir(self):
        """`voice.extends: "./parent-corp.md"` must resolve from the child file's
        directory, not the current working directory."""
        # Run with a different CWD to ensure resolution is relative to the child file.
        original_cwd = os.getcwd()
        try:
            os.chdir(tempfile.gettempdir())
            chain = resolve_extends_chain(FIXTURES / "child-founder.md")
            self.assertEqual(len(chain), 2)
            self.assertEqual(chain[0][0].name, "parent-corp.md")
        finally:
            os.chdir(original_cwd)

    def test_absolute_path_works(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            parent = td / "parent.md"
            parent.write_text(
                "---\nvoice:\n  name: \"AbsParent\"\n  last_updated: \"2026-04-27\"\nforbidden_lexicon: []\n"
                "rewrite_rules:\n  - reject: \"a\"\n    accept: \"b\"\n    rule_id: r\n"
                "sentence_norms:\n  word_count_min: 8\n  word_count_max: 22\n  sentence_max_hard: 30\n"
                "---\n# Brand Voice — AbsParent\n## 1. Core voice attributes\nStub.\n"
                "## 2. Rewrite rules — do/don't\nStub.\n## 3. Forbidden lexicon and patterns\nStub.\n"
                "## 4. Sentence-level norms\nStub.\n",
                encoding="utf-8",
            )
            child = td / "child.md"
            child.write_text(
                f"---\nvoice:\n  name: \"AbsChild\"\n  extends: \"{parent.resolve()}\"\n  last_updated: \"2026-04-27\"\n"
                "forbidden_lexicon: []\n"
                "rewrite_rules:\n  - reject: \"a\"\n    accept: \"b\"\n    rule_id: r2\n"
                "sentence_norms:\n  word_count_min: 8\n  word_count_max: 22\n  sentence_max_hard: 30\n"
                "---\n# Brand Voice — AbsChild\n## 1. Core voice attributes\nStub.\n"
                "## 2. Rewrite rules — do/don't\nStub.\n## 3. Forbidden lexicon and patterns\nStub.\n"
                "## 4. Sentence-level norms\nStub.\n",
                encoding="utf-8",
            )
            chain = resolve_extends_chain(child)
            self.assertEqual(len(chain), 2)


if __name__ == "__main__":
    unittest.main()
