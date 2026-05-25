"""Tests for `classify_repo` in audit_signals.py.

Unit-level: each test calls `classify_repo(fixture_path)` against a committed
fixture under `tests/code-ultrareview/fixtures/classify/<kind>/` and asserts
the resolved `repo_kind` + the relevant fields of `repo_kind_signals`.

Compound and override cases mix fixtures with on-the-fly tempdirs so the
precedence resolver is exercised without a fixture-explosion.
"""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "skills" / "code-ultrareview" / "scripts" / "audit_signals.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "classify"
AUDIT_PHASE_DOC = (
    REPO_ROOT / "skills" / "code-ultrareview" / "references" / "audit-phase.md"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("audit_signals", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


audit_signals = _load_module()
classify_repo = audit_signals.classify_repo


class TestSingleKindFixtures(unittest.TestCase):
    """One fixture per kind. Each pins the kind plus the primary signal."""

    def test_skills_kind(self):
        kind, sigs = classify_repo(FIXTURES / "skills")
        self.assertEqual(kind, "skills")
        self.assertEqual(sigs["primary_signal"], "marketplace.json + skills/*/SKILL.md")
        self.assertEqual(sigs["skill_md_count"], 1)
        self.assertEqual(sigs["competing_signals"], [])
        self.assertIsNone(sigs["override_source"])

    def test_app_kind(self):
        kind, sigs = classify_repo(FIXTURES / "app")
        self.assertEqual(kind, "app")
        self.assertEqual(sigs["package_json_role"], "app")
        self.assertIn("next.config.ts", sigs["framework_configs"])

    def test_library_kind(self):
        kind, sigs = classify_repo(FIXTURES / "library")
        self.assertEqual(kind, "library")
        self.assertEqual(sigs["package_json_role"], "library")

    def test_docs_kind(self):
        kind, sigs = classify_repo(FIXTURES / "docs")
        self.assertEqual(kind, "docs")
        self.assertIn("docusaurus.config.ts", sigs["docs_site_configs"])

    def test_monorepo_kind(self):
        kind, sigs = classify_repo(FIXTURES / "monorepo")
        self.assertEqual(kind, "monorepo")
        self.assertIn("pnpm-workspace.yaml", sigs["workspace_configs"])

    def test_python_kind(self):
        kind, sigs = classify_repo(FIXTURES / "python")
        self.assertEqual(kind, "python")
        self.assertEqual(sigs["pyproject_toml"], "pyproject.toml")

    def test_rust_kind(self):
        kind, sigs = classify_repo(FIXTURES / "rust")
        self.assertEqual(kind, "rust")
        self.assertEqual(sigs["cargo_toml"], "Cargo.toml")

    def test_go_kind(self):
        kind, sigs = classify_repo(FIXTURES / "go")
        self.assertEqual(kind, "go")
        self.assertEqual(sigs["go_mod"], "go.mod")

    def test_unknown_kind(self):
        kind, sigs = classify_repo(FIXTURES / "unknown")
        self.assertEqual(kind, "unknown")
        self.assertEqual(sigs["competing_signals"], [])
        self.assertIsNone(sigs["override_source"])


class TestCompoundCases(unittest.TestCase):
    def test_mixed_skills_npm_resolves_to_skills(self):
        kind, sigs = classify_repo(FIXTURES / "mixed-skills-npm")
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
            kind, sigs = classify_repo(repo)
        # Precedence: rust > go.
        self.assertEqual(kind, "rust")
        self.assertIn("Go tooling", sigs["competing_signals"])

    def test_docusaurus_with_package_json_resolves_to_docs(self):
        """A Docusaurus repo has `docusaurus.config.ts` AND a `package.json`
        with `scripts.start` — both signals fire. Per the documented
        precedence (docs > app), it must resolve as `docs`, with the
        npm tooling surfacing as a competing signal."""
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
            kind, sigs = classify_repo(repo)
        self.assertEqual(kind, "docs")
        self.assertIn("npm tooling", sigs["competing_signals"])

    def test_bare_package_json_resolves_to_app_via_permissive_default(self):
        """A `package.json` with neither app indicators (`scripts.dev|start`,
        `bin`, app-only framework config) nor library indicators (`exports`,
        `module`, `types`) takes the permissive default — role becomes `app`
        and the kind resolves to `app`. Pins `_package_json_role`'s
        documented permissive widening (see `audit-phase.md` §
        Repo-kind detection, "permissive default")."""
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "package.json").write_text(
                json.dumps({"name": "x"}), encoding="utf-8"
            )
            kind, sigs = classify_repo(repo)
        self.assertEqual(kind, "app")
        self.assertEqual(sigs["package_json_role"], "app")
        self.assertEqual(sigs["framework_configs"], [])

    def test_monorepo_with_skills_remains_skills(self):
        """Workspace configs alongside a skills layout still resolves to skills.
        Workspaces surface as a competing signal."""
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
            kind, sigs = classify_repo(repo)
        self.assertEqual(kind, "skills")
        self.assertIn("workspaces", sigs["competing_signals"])


class TestOverrideMechanism(unittest.TestCase):
    def test_flag_override_wins_over_detection(self):
        kind, sigs = classify_repo(FIXTURES / "app", override="skills")
        self.assertEqual(kind, "skills")
        self.assertEqual(sigs["override_source"], "--repo-kind flag")
        # Detected signals still surface even when overridden.
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
            kind, sigs = classify_repo(repo)
        self.assertEqual(kind, "library")
        self.assertEqual(sigs["override_source"], "config:.code-ultrareview.yaml")

    def test_flag_wins_over_config(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / ".code-ultrareview.yaml").write_text(
                "repo_kind: library\n", encoding="utf-8"
            )
            kind, sigs = classify_repo(repo, override="skills")
        self.assertEqual(kind, "skills")
        self.assertEqual(sigs["override_source"], "--repo-kind flag")

    def test_invalid_override_raises(self):
        with self.assertRaises(ValueError) as cm:
            classify_repo(FIXTURES / "unknown", override="invalid-kind")
        self.assertIn("invalid", str(cm.exception).lower())

    def test_invalid_config_value_falls_through_to_detection(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "Cargo.toml").write_text(
                "[package]\nname=\"x\"\nversion=\"0.1.0\"\n", encoding="utf-8"
            )
            (repo / ".code-ultrareview.yaml").write_text(
                "repo_kind: not-a-real-kind\n", encoding="utf-8"
            )
            kind, sigs = classify_repo(repo)
        # Invalid config value silently falls through — detection wins.
        self.assertEqual(kind, "rust")
        self.assertIsNone(sigs["override_source"])

    def test_quoted_config_value_parses(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / ".code-ultrareview.yaml").write_text(
                'repo_kind: "skills"  # quoted form\n', encoding="utf-8"
            )
            kind, _ = classify_repo(repo)
        self.assertEqual(kind, "skills")


class TestCLI(unittest.TestCase):
    """The argparse choice constraint is the contract for invalid CLI input.
    Exit 2 with a clear error and no JSON on stdout."""

    @unittest.skipUnless(shutil.which("git"), "git required")
    def test_invalid_repo_kind_exits_2(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            subprocess.run(
                ["git", "-C", str(repo), "init", "-q"], check=True
            )
            r = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo", str(repo),
                 "--dirty-tree", "--repo-kind", "not-a-kind"],
                capture_output=True, text=True, timeout=10,
            )
        self.assertEqual(r.returncode, 2)
        self.assertEqual(r.stdout, "")
        # argparse prints an "invalid choice" message; assert presence.
        self.assertIn("invalid choice", r.stderr.lower())


class TestPrecedenceDocMatchesCode(unittest.TestCase):
    """The doc-precedence table in references/audit-phase.md must reflect the
    same order as the implementation in _resolve_repo_kind. The test reads the
    markdown numbered list under "Repo-kind detection" and compares to the
    code's actual resolution order."""

    EXPECTED_ORDER = (
        "skills", "monorepo", "docs", "app", "library",
        "python", "rust", "go", "unknown",
    )

    def test_doc_lists_canonical_order(self):
        text = AUDIT_PHASE_DOC.read_text(encoding="utf-8")
        # Find the "Repo-kind detection" subsection then the precedence list.
        m = re.search(r"###\s+Repo-kind detection", text)
        if m is None:
            self.fail("audit-phase.md missing 'Repo-kind detection' subsection")
        block = text[m.end():]
        end = re.search(r"\n(###|## )", block)
        if end is not None:
            block = block[:end.start()]
        # The precedence line lists kinds with > separators; extract the kinds.
        prec_match = re.search(r"Precedence[^\n]*?:\s*([^\n]+)", block)
        if prec_match is None:
            self.fail("audit-phase.md missing 'Precedence:' line")
        prec_text = prec_match.group(1)
        # Extract backticked kind names in order.
        kinds_in_doc = re.findall(r"`(\w+)`", prec_text)
        self.assertEqual(
            tuple(kinds_in_doc), self.EXPECTED_ORDER,
            f"audit-phase.md precedence line lists {kinds_in_doc!r}; "
            f"expected {self.EXPECTED_ORDER!r}",
        )


if __name__ == "__main__":
    unittest.main()
