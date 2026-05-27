"""Tests for skills/code-ultrareview/scripts/scope.py.

Covers repo-kind classification (reusing the committed fixtures under
`fixtures/classify/`), CLAUDE.md hierarchy ordering, Coherence-axis
activation triggers, and languages detection. Diff resolution is covered
end-to-end via temp-repo init.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "skills" / "code-ultrareview" / "scripts" / "scope.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "classify"


def _load_module():
    spec = importlib.util.spec_from_file_location("scope", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


scope = _load_module()


def _init_repo(repo: Path) -> None:
    """Minimal git init — no commits, no upstream."""
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "commit.gpgsign", "false"], check=True)


def _commit(repo: Path, msg: str = "init") -> None:
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", msg], check=True)


# ---------------------------------------------------------------------------
# Repo-kind classification (reuses classify_repo against committed fixtures)
# ---------------------------------------------------------------------------


class TestRepoKindClassification(unittest.TestCase):
    """Carried from test_classify_repo.py — same fixtures, new module."""

    def test_skills_kind(self):
        kind, sigs = scope.classify_repo(FIXTURES / "skills")
        self.assertEqual(kind, "skills")
        self.assertEqual(sigs["primary_signal"], "marketplace.json + skills/*/SKILL.md")
        self.assertGreaterEqual(sigs["skill_md_count"], 1)
        self.assertIsNone(sigs["override_source"])

    def test_app_kind(self):
        kind, sigs = scope.classify_repo(FIXTURES / "app")
        self.assertEqual(kind, "app")
        self.assertEqual(sigs["package_json_role"], "app")

    def test_library_kind(self):
        kind, sigs = scope.classify_repo(FIXTURES / "library")
        self.assertEqual(kind, "library")
        self.assertEqual(sigs["package_json_role"], "library")

    def test_docs_kind(self):
        kind, _ = scope.classify_repo(FIXTURES / "docs")
        self.assertEqual(kind, "docs")

    def test_monorepo_kind(self):
        kind, _ = scope.classify_repo(FIXTURES / "monorepo")
        self.assertEqual(kind, "monorepo")

    def test_python_kind(self):
        kind, sigs = scope.classify_repo(FIXTURES / "python")
        self.assertEqual(kind, "python")
        self.assertEqual(sigs["pyproject_toml"], "pyproject.toml")

    def test_rust_kind(self):
        kind, _ = scope.classify_repo(FIXTURES / "rust")
        self.assertEqual(kind, "rust")

    def test_go_kind(self):
        kind, _ = scope.classify_repo(FIXTURES / "go")
        self.assertEqual(kind, "go")

    def test_unknown_kind(self):
        kind, _ = scope.classify_repo(FIXTURES / "unknown")
        self.assertEqual(kind, "unknown")

    def test_override_wins_over_detection(self):
        kind, sigs = scope.classify_repo(FIXTURES / "app", override="docs")
        self.assertEqual(kind, "docs")
        self.assertEqual(sigs["override_source"], "--repo-kind flag")

    def test_invalid_override_raises(self):
        with self.assertRaises(ValueError):
            scope.classify_repo(FIXTURES / "app", override="not-a-kind")


class TestRepoKindCompoundCases(unittest.TestCase):
    """Compound + edge cases beyond the single-kind fixtures."""

    def test_mixed_skills_npm_resolves_to_skills(self):
        kind, sigs = scope.classify_repo(FIXTURES / "mixed-skills-npm")
        self.assertEqual(kind, "skills")
        self.assertIn("npm tooling", sigs["competing_signals"])

    def test_dual_language_resolves_via_precedence(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "Cargo.toml").write_text(
                "[package]\nname=\"x\"\nversion=\"0.1.0\"\n", encoding="utf-8"
            )
            (repo / "go.mod").write_text(
                "module example.com/x\ngo 1.21\n", encoding="utf-8"
            )
            kind, sigs = scope.classify_repo(repo)
        self.assertEqual(kind, "rust")
        self.assertIn("Go tooling", sigs["competing_signals"])

    def test_docusaurus_with_package_json_resolves_to_docs(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "docusaurus.config.ts").write_text(
                "export default { title: \"x\" };\n", encoding="utf-8"
            )
            (repo / "package.json").write_text(
                json.dumps({
                    "name": "x",
                    "scripts": {"start": "docusaurus start",
                                "build": "docusaurus build"},
                }),
                encoding="utf-8",
            )
            kind, sigs = scope.classify_repo(repo)
        self.assertEqual(kind, "docs")
        self.assertIn("npm tooling", sigs["competing_signals"])

    def test_bare_package_json_resolves_to_app_via_permissive_default(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "package.json").write_text(
                json.dumps({"name": "x"}), encoding="utf-8"
            )
            kind, sigs = scope.classify_repo(repo)
        self.assertEqual(kind, "app")
        self.assertEqual(sigs["package_json_role"], "app")
        self.assertEqual(sigs["framework_configs"], [])

    def test_monorepo_with_skills_remains_skills(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / ".claude-plugin").mkdir()
            (repo / ".claude-plugin" / "marketplace.json").write_text(
                json.dumps({"name": "x"}), encoding="utf-8"
            )
            (repo / "skills" / "foo").mkdir(parents=True)
            (repo / "skills" / "foo" / "SKILL.md").write_text(
                "---\nname: foo\ndescription: x\n---\n", encoding="utf-8"
            )
            (repo / "pnpm-workspace.yaml").write_text("packages:\n  - x\n", encoding="utf-8")
            kind, sigs = scope.classify_repo(repo)
        self.assertEqual(kind, "skills")
        self.assertIn("workspaces", sigs["competing_signals"])


class TestRepoKindOverrideMechanism(unittest.TestCase):
    """Override precedence — flag > config > detection."""

    def test_flag_override_surfaces_detected_signals(self):
        kind, sigs = scope.classify_repo(FIXTURES / "app", override="skills")
        self.assertEqual(kind, "skills")
        self.assertEqual(sigs["override_source"], "--repo-kind flag")
        self.assertEqual(sigs["package_json_role"], "app")

    def test_config_override_wins_over_detection(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "package.json").write_text(
                json.dumps({"name": "x", "scripts": {"dev": "x"}}), encoding="utf-8"
            )
            (repo / ".code-ultrareview.yaml").write_text(
                "repo_kind: library\n", encoding="utf-8"
            )
            kind, sigs = scope.classify_repo(repo)
        self.assertEqual(kind, "library")
        self.assertEqual(sigs["override_source"], "config:.code-ultrareview.yaml")

    def test_flag_wins_over_config(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / ".code-ultrareview.yaml").write_text(
                "repo_kind: library\n", encoding="utf-8"
            )
            kind, sigs = scope.classify_repo(repo, override="skills")
        self.assertEqual(kind, "skills")
        self.assertEqual(sigs["override_source"], "--repo-kind flag")

    def test_invalid_config_value_falls_through_to_detection(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "Cargo.toml").write_text(
                "[package]\nname=\"x\"\nversion=\"0.1.0\"\n", encoding="utf-8"
            )
            (repo / ".code-ultrareview.yaml").write_text(
                "repo_kind: not-a-real-kind\n", encoding="utf-8"
            )
            kind, sigs = scope.classify_repo(repo)
        self.assertEqual(kind, "rust")
        self.assertIsNone(sigs["override_source"])

    def test_quoted_config_value_parses(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / ".code-ultrareview.yaml").write_text(
                'repo_kind: "skills"  # quoted form\n', encoding="utf-8"
            )
            kind, _ = scope.classify_repo(repo)
        self.assertEqual(kind, "skills")


class TestRepoKindCLI(unittest.TestCase):
    """`--repo-kind` argparse choice constraint — exit 2 on invalid input."""

    @unittest.skipUnless(shutil.which("git"), "git required")
    def test_invalid_repo_kind_exits_2(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
            r = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo", str(repo),
                 "--dirty-tree", "--repo-kind", "not-a-kind"],
                capture_output=True, text=True, timeout=10,
            )
        self.assertEqual(r.returncode, 2)
        self.assertEqual(r.stdout, "")
        self.assertIn("invalid choice", r.stderr.lower())


# ---------------------------------------------------------------------------
# CLAUDE.md chain ordering
# ---------------------------------------------------------------------------


class TestClaudeMdChain(unittest.TestCase):
    """Spec AC: root + .claude/rules/ files appear in claude_md_chain ordered
    root-to-deepest."""

    def setUp(self):
        # Hide the global ~/.claude/rules during these tests so the chain
        # only reflects the temp repo's content.
        self._old_home = os.environ.get("HOME")
        self._tmp_home = tempfile.mkdtemp(prefix="scope-test-home-")
        os.environ["HOME"] = self._tmp_home

    def tearDown(self):
        if self._old_home is not None:
            os.environ["HOME"] = self._old_home
        else:
            os.environ.pop("HOME", None)
        import shutil
        shutil.rmtree(self._tmp_home, ignore_errors=True)

    def test_root_claude_md_first(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "CLAUDE.md").write_text("# root\n", encoding="utf-8")
            chain = scope.claude_md_chain(repo, [])
            self.assertEqual(chain[0], "CLAUDE.md")

    def test_root_plus_claude_rules_ordering(self):
        # Spec AC: root CLAUDE.md + .claude/rules/<name>.md → both present,
        # root first, rules after, sorted alphabetically by filename.
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "CLAUDE.md").write_text("# root\n", encoding="utf-8")
            rules = repo / ".claude" / "rules"
            rules.mkdir(parents=True)
            (rules / "behave.md").write_text("# behave\n", encoding="utf-8")
            (rules / "writing.md").write_text("# writing\n", encoding="utf-8")
            chain = scope.claude_md_chain(repo, [])
            self.assertEqual(chain, [
                "CLAUDE.md",
                ".claude/rules/behave.md",
                ".claude/rules/writing.md",
            ])

    def test_nested_claude_md_in_changed_dir(self):
        # Nested CLAUDE.md in a directory containing a touched file appears
        # AFTER root CLAUDE.md and BEFORE project rules.
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "CLAUDE.md").write_text("# root\n", encoding="utf-8")
            sub = repo / "skills" / "foo"
            sub.mkdir(parents=True)
            (sub / "CLAUDE.md").write_text("# nested\n", encoding="utf-8")
            (sub / "SKILL.md").write_text("---\nname: foo\n---\n", encoding="utf-8")
            chain = scope.claude_md_chain(repo, ["skills/foo/SKILL.md"])
            self.assertIn("CLAUDE.md", chain)
            self.assertIn("skills/foo/CLAUDE.md", chain)
            # Root before nested.
            self.assertLess(chain.index("CLAUDE.md"), chain.index("skills/foo/CLAUDE.md"))

    def test_nested_not_included_when_dir_unchanged(self):
        # If the nested CLAUDE.md's directory has no touched files, it must NOT
        # appear in the chain — only changed-dir lineage counts.
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "CLAUDE.md").write_text("# root\n", encoding="utf-8")
            (repo / "skills" / "foo").mkdir(parents=True)
            (repo / "skills" / "foo" / "CLAUDE.md").write_text("# nested\n", encoding="utf-8")
            # Touch a file in a different subtree.
            (repo / "src").mkdir()
            (repo / "src" / "a.py").write_text("pass\n", encoding="utf-8")
            chain = scope.claude_md_chain(repo, ["src/a.py"])
            self.assertNotIn("skills/foo/CLAUDE.md", chain)


# ---------------------------------------------------------------------------
# Coherence activation
# ---------------------------------------------------------------------------


class TestActivatesCoherence(unittest.TestCase):
    """Spec AC: any of marketplace.json | package.json | SKILL.md | root README.md
    | tsconfig.json | pyproject.toml | Cargo.toml | go.mod in diff → True."""

    def test_marketplace_json_triggers(self):
        self.assertTrue(scope.activates_coherence([".claude-plugin/marketplace.json"]))
        self.assertTrue(scope.activates_coherence(["marketplace.json"]))

    def test_package_json_triggers(self):
        self.assertTrue(scope.activates_coherence(["package.json"]))
        # Also at any depth (workspace package.json).
        self.assertTrue(scope.activates_coherence(["packages/foo/package.json"]))

    def test_skill_md_anywhere_triggers(self):
        self.assertTrue(scope.activates_coherence(["skills/foo/SKILL.md"]))
        self.assertTrue(scope.activates_coherence(["SKILL.md"]))

    def test_root_readme_triggers(self):
        self.assertTrue(scope.activates_coherence(["README.md"]))

    def test_nested_readme_does_not_trigger(self):
        # Root-only — every subfolder README would over-trigger.
        self.assertFalse(scope.activates_coherence(["skills/foo/README.md"]))

    def test_tsconfig_pyproject_cargo_gomod_trigger(self):
        self.assertTrue(scope.activates_coherence(["tsconfig.json"]))
        self.assertTrue(scope.activates_coherence(["pyproject.toml"]))
        self.assertTrue(scope.activates_coherence(["Cargo.toml"]))
        self.assertTrue(scope.activates_coherence(["go.mod"]))

    def test_no_trigger_for_unrelated_files(self):
        self.assertFalse(scope.activates_coherence(["src/foo.py", "docs/bar.md"]))

    def test_empty_files_list_does_not_trigger(self):
        self.assertFalse(scope.activates_coherence([]))


# ---------------------------------------------------------------------------
# Languages detection
# ---------------------------------------------------------------------------


class TestDetectLanguages(unittest.TestCase):

    def test_python_files_detect_python(self):
        self.assertEqual(scope.detect_languages(["src/a.py"]), ["python"])

    def test_mixed_files_sorted_dedup(self):
        langs = scope.detect_languages(["a.py", "b.ts", "c.go", "d.py"])
        # Sorted alphabetically, no duplicates.
        self.assertEqual(langs, ["go", "python", "typescript"])

    def test_unknown_extension_silently_dropped(self):
        # .xyz is not a known language — should not raise, just omit.
        self.assertEqual(scope.detect_languages(["weird.xyz"]), [])

    def test_markdown_counts(self):
        self.assertIn("markdown", scope.detect_languages(["doc.md"]))


# ---------------------------------------------------------------------------
# End-to-end scope assembly (dirty-tree path — bypasses resolve_base.sh)
# ---------------------------------------------------------------------------


class TestBuildScopeDirtyTree(unittest.TestCase):
    """Spec AC: scope.json carries repo_kind, claude_md_chain, activates_coherence,
    files_touched_list, tools_skipped (empty)."""

    def setUp(self):
        self._old_home = os.environ.get("HOME")
        self._tmp_home = tempfile.mkdtemp(prefix="scope-buildtest-home-")
        os.environ["HOME"] = self._tmp_home

    def tearDown(self):
        if self._old_home is not None:
            os.environ["HOME"] = self._old_home
        else:
            os.environ.pop("HOME", None)
        import shutil
        shutil.rmtree(self._tmp_home, ignore_errors=True)

    def test_dirty_tree_skills_repo_with_marketplace_change(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            _init_repo(repo)
            (repo / ".claude-plugin").mkdir()
            (repo / ".claude-plugin" / "marketplace.json").write_text("{}", encoding="utf-8")
            (repo / "skills" / "foo").mkdir(parents=True)
            (repo / "skills" / "foo" / "SKILL.md").write_text(
                "---\nname: foo\ndescription: x\n---\n", encoding="utf-8",
            )
            (repo / "CLAUDE.md").write_text("# root\n", encoding="utf-8")
            _commit(repo)
            # Touch marketplace.json so it appears in the dirty tree.
            (repo / ".claude-plugin" / "marketplace.json").write_text(
                '{"changed": true}', encoding="utf-8",
            )

            payload = scope.build_scope(repo, dirty_tree=True)

            self.assertEqual(payload["repo_kind"], "skills")
            self.assertTrue(payload["activates_coherence"],
                            "marketplace.json change must trigger coherence")
            self.assertIn(".claude-plugin/marketplace.json", payload["files_touched_list"])
            self.assertIn("CLAUDE.md", payload["claude_md_chain"])
            self.assertEqual(payload["tools_skipped"], [])
            self.assertEqual(payload["rule"], "dirty-tree")

    def test_no_coherence_on_unrelated_change(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            _init_repo(repo)
            (repo / "src").mkdir()
            (repo / "src" / "a.py").write_text("pass\n", encoding="utf-8")
            _commit(repo)
            (repo / "src" / "a.py").write_text("pass  # changed\n", encoding="utf-8")
            payload = scope.build_scope(repo, dirty_tree=True)
            self.assertFalse(payload["activates_coherence"])


if __name__ == "__main__":
    unittest.main()
