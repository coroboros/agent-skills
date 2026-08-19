"""Tests for skills/code-ultrareview/scripts/scope.py.

Covers repo-kind classification (reusing the committed fixtures under
`fixtures/classify/`), cross-agent instruction-chain ordering, Coherence-axis
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
    subprocess.run(["git", "-C", str(repo), "config", "core.hooksPath", os.devnull], check=True)


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


class TestScopeFailures(unittest.TestCase):
    def test_clean_dirty_tree_exits_2_without_scope(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            _init_repo(repo)
            (repo / "README.md").write_text("# Clean\n", encoding="utf-8")
            _commit(repo)
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo", str(repo), "--dirty-tree"],
                capture_output=True,
                text=True,
                timeout=10,
            )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("review scope is empty", result.stderr)

    def test_failed_git_diff_raises_instead_of_returning_empty_scope(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            _init_repo(repo)
            (repo / "README.md").write_text("# Initial\n", encoding="utf-8")
            _commit(repo)
            with self.assertRaisesRegex(RuntimeError, "git diff --numstat failed"):
                scope.diff_files(repo, "missing-ref", "HEAD")


# ---------------------------------------------------------------------------
# Cross-agent instruction chain ordering
# ---------------------------------------------------------------------------


class TestInstructionChain(unittest.TestCase):
    """The baseline follows effective entrypoints from broad to specific."""

    def setUp(self):
        # Hide global agent rules during these tests so the chain
        # only reflects the temp repo's content.
        self._old_home = os.environ.get("HOME")
        self._old_codex_home = os.environ.get("CODEX_HOME")
        self._tmp_home = tempfile.mkdtemp(prefix="scope-test-home-")
        os.environ["HOME"] = self._tmp_home
        os.environ["CODEX_HOME"] = str(Path(self._tmp_home) / ".codex")

    def tearDown(self):
        if self._old_home is not None:
            os.environ["HOME"] = self._old_home
        else:
            os.environ.pop("HOME", None)
        if self._old_codex_home is not None:
            os.environ["CODEX_HOME"] = self._old_codex_home
        else:
            os.environ.pop("CODEX_HOME", None)
        import shutil
        shutil.rmtree(self._tmp_home, ignore_errors=True)

    def test_agents_override_replaces_agents_at_the_same_level(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "AGENTS.md").write_text("# shared\n", encoding="utf-8")
            (repo / "AGENTS.override.md").write_text("# override\n", encoding="utf-8")
            (repo / "CLAUDE.md").write_text("# root\n", encoding="utf-8")
            chain = scope.instruction_chain(repo, [])
            self.assertEqual(
                chain,
                ["AGENTS.override.md", "CLAUDE.md"],
            )

    def test_empty_agents_override_falls_back_to_agents(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "AGENTS.md").write_text("# shared\n", encoding="utf-8")
            (repo / "AGENTS.override.md").write_text("\n", encoding="utf-8")
            self.assertEqual(scope.instruction_chain(repo, []), ["AGENTS.md"])

    def test_shared_and_claude_rules_are_recursive(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "AGENTS.md").write_text(
                "Read `.agents/rules/` before reviewing.\n", encoding="utf-8",
            )
            shared = repo / ".agents" / "rules"
            shared.mkdir(parents=True)
            (shared / "behavior.md").write_text("# behavior\n", encoding="utf-8")
            claude = repo / ".claude" / "rules" / "frontend"
            claude.mkdir(parents=True)
            (claude / "behave.md").write_text("# behave\n", encoding="utf-8")
            (claude / "writing.md").write_text("# writing\n", encoding="utf-8")
            chain = scope.instruction_chain(repo, [])
            self.assertEqual(chain, [
                "AGENTS.md",
                ".agents/rules/behavior.md",
                ".claude/rules/frontend/behave.md",
                ".claude/rules/frontend/writing.md",
            ])

    def test_unreferenced_shared_rules_are_not_loaded(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "AGENTS.md").write_text("# project\n", encoding="utf-8")
            rules = repo / ".agents" / "rules"
            rules.mkdir(parents=True)
            (rules / "behavior.md").write_text("# behavior\n", encoding="utf-8")

            self.assertEqual(scope.instruction_chain(repo, []), ["AGENTS.md"])

    def test_only_explicitly_referenced_shared_rule_is_loaded(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "AGENTS.md").write_text(
                "Read `.agents/rules/a.md` before reviewing.\n",
                encoding="utf-8",
            )
            rules = repo / ".agents" / "rules"
            rules.mkdir(parents=True)
            (rules / "a.md").write_text("# a\n", encoding="utf-8")
            (rules / "b.md").write_text("# b\n", encoding="utf-8")

            self.assertEqual(scope.instruction_chain(repo, []), [
                "AGENTS.md",
                ".agents/rules/a.md",
            ])

    def test_explicit_dot_slash_shared_rule_is_loaded(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "AGENTS.md").write_text(
                "Read `./.agents/rules/a.md` before reviewing.\n",
                encoding="utf-8",
            )
            rules = repo / ".agents" / "rules"
            rules.mkdir(parents=True)
            (rules / "a.md").write_text("# a\n", encoding="utf-8")

            self.assertEqual(scope.instruction_chain(repo, []), [
                "AGENTS.md",
                ".agents/rules/a.md",
            ])

    def test_claude_alternate_and_local_entrypoints_are_included(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / ".claude").mkdir()
            (repo / ".claude" / "CLAUDE.md").write_text(
                "# project\n", encoding="utf-8",
            )
            (repo / "CLAUDE.local.md").write_text(
                "# local\n", encoding="utf-8",
            )
            self.assertEqual(scope.instruction_chain(repo, []), [
                ".claude/CLAUDE.md",
                "CLAUDE.local.md",
            ])

    def test_user_instructions_precede_project_instructions(self):
        home = Path(self._tmp_home)
        (home / ".agents").mkdir(parents=True)
        (home / ".agents" / "AGENTS.md").write_text(
            "# global shared\n", encoding="utf-8",
        )
        (home / ".claude").mkdir(parents=True)
        (home / ".claude" / "CLAUDE.md").write_text(
            "# global claude\n", encoding="utf-8",
        )
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "AGENTS.md").write_text("# project\n", encoding="utf-8")
            chain = scope.instruction_chain(repo, [])
        self.assertEqual(Path(chain[0]).name, "AGENTS.md")
        self.assertIn("/.agents/AGENTS.md", chain[0])
        self.assertIn("/.claude/CLAUDE.md", chain[1])
        self.assertEqual(chain[2], "AGENTS.md")

    def test_empty_codex_home_uses_the_default_location(self):
        home = Path(self._tmp_home)
        codex_home = home / ".codex"
        codex_home.mkdir(parents=True)
        (codex_home / "AGENTS.md").write_text(
            "# global codex\n", encoding="utf-8",
        )
        os.environ["CODEX_HOME"] = ""
        with tempfile.TemporaryDirectory() as td:
            chain = scope.instruction_chain(Path(td), [])
        self.assertEqual(chain, [str((codex_home / "AGENTS.md").resolve())])

    def test_duplicate_override_does_not_activate_same_level_fallback(self):
        home = Path(self._tmp_home)
        agents_home = home / ".agents"
        codex_home = home / ".codex"
        agents_home.mkdir(parents=True)
        codex_home.mkdir(parents=True)
        shared_override = agents_home / "AGENTS.override.md"
        shared_override.write_text("# shared override\n", encoding="utf-8")
        (codex_home / "AGENTS.override.md").symlink_to(shared_override)
        (codex_home / "AGENTS.md").write_text(
            "# shadowed fallback\n", encoding="utf-8",
        )

        with tempfile.TemporaryDirectory() as td:
            chain = scope.instruction_chain(Path(td), [])

        self.assertEqual(chain, [str(shared_override.resolve())])

    def test_nested_entrypoints_only_follow_changed_directories(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "AGENTS.md").write_text("# shared\n", encoding="utf-8")
            (repo / "CLAUDE.md").write_text("# root\n", encoding="utf-8")
            sub = repo / "skills" / "foo"
            sub.mkdir(parents=True)
            (sub / "AGENTS.md").write_text("# nested shared\n", encoding="utf-8")
            (sub / "CLAUDE.md").write_text("# nested\n", encoding="utf-8")
            (sub / "SKILL.md").write_text("---\nname: foo\n---\n", encoding="utf-8")
            chain = scope.instruction_chain(repo, ["skills/foo/SKILL.md"])
            self.assertIn("AGENTS.md", chain)
            self.assertIn("skills/foo/AGENTS.md", chain)
            self.assertIn("CLAUDE.md", chain)
            self.assertIn("skills/foo/CLAUDE.md", chain)
            self.assertLess(chain.index("AGENTS.md"), chain.index("skills/foo/AGENTS.md"))
            self.assertLess(chain.index("CLAUDE.md"), chain.index("skills/foo/CLAUDE.md"))

    def test_nested_not_included_when_dir_unchanged(self):
        # If the nested entrypoint's directory has no touched files, it must NOT
        # appear in the chain — only changed-dir lineage counts.
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "skills" / "foo").mkdir(parents=True)
            (repo / "skills" / "foo" / "AGENTS.md").write_text("# nested\n", encoding="utf-8")
            (repo / "skills" / "foo" / "CLAUDE.md").write_text("# nested\n", encoding="utf-8")
            # Touch a file in a different subtree.
            (repo / "src").mkdir()
            (repo / "src" / "a.py").write_text("pass\n", encoding="utf-8")
            chain = scope.instruction_chain(repo, ["src/a.py"])
            self.assertNotIn("skills/foo/AGENTS.md", chain)
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
# Target-side changed line ranges
# ---------------------------------------------------------------------------


class TestChangedLineRanges(unittest.TestCase):
    def test_dirty_tree_tracks_modified_hunks_and_full_untracked_files(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            _init_repo(repo)
            tracked = repo / "src" / "app.py"
            tracked.parent.mkdir()
            tracked.write_text(
                "one\ntwo\nthree\nfour\nfive\nsix\n",
                encoding="utf-8",
            )
            _commit(repo)
            tracked.write_text(
                "one\nTWO\nthree\nfour\nFIVE\nsix\n",
                encoding="utf-8",
            )
            untracked = repo / "src" / "new.py"
            untracked.write_text("alpha\nbeta\n", encoding="utf-8")

            ranges = scope.changed_line_ranges(
                repo,
                "HEAD",
                "HEAD",
                ["src/app.py", "src/new.py"],
                dirty_tree=True,
            )

        self.assertEqual(ranges["src/app.py"], [[2, 2], [5, 5]])
        self.assertEqual(ranges["src/new.py"], [[1, 2]])

    def test_deletion_only_hunk_has_no_target_lines(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            _init_repo(repo)
            tracked = repo / "app.py"
            tracked.write_text("one\ntwo\nthree\n", encoding="utf-8")
            _commit(repo)
            tracked.write_text("one\nthree\n", encoding="utf-8")

            ranges = scope.changed_line_ranges(
                repo,
                "HEAD",
                "HEAD",
                ["app.py"],
                dirty_tree=True,
            )

        self.assertEqual(ranges["app.py"], [])


# ---------------------------------------------------------------------------
# End-to-end scope assembly (dirty-tree path — bypasses resolve_base.sh)
# ---------------------------------------------------------------------------


class TestBuildScopeDirtyTree(unittest.TestCase):
    """scope.json carries both instruction-chain keys during migration.

    It also carries repo_kind, activates_coherence,
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
            (repo / "AGENTS.md").write_text("# shared\n", encoding="utf-8")
            (repo / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
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
            self.assertEqual(
                payload["changed_line_ranges"][".claude-plugin/marketplace.json"],
                [[1, 1]],
            )
            self.assertIn("AGENTS.md", payload["instruction_chain"])
            self.assertIn("CLAUDE.md", payload["instruction_chain"])
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
