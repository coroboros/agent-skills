"""Tests for scripts/fetch_commits.sh — base resolution + NUL-delimited records."""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "skills" / "code-ultrareview" / "scripts" / "fetch_commits.sh"


def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        env={
            **os.environ,
            # Fixture repositories must not inherit signing or global hooks.
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull,
            # Deterministic identity for fixture commits — these are throwaway.
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.invalid",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.invalid",
        },
    )


def _seed_repo(repo: Path) -> str:
    """Create a tmp git repo with one base commit on main + three on a branch."""
    _git(["init", "-q", "-b", "main"], repo)
    (repo / "README.md").write_text("# base\n", encoding="utf-8")
    _git(["add", "README.md"], repo)
    _git(["commit", "-q", "-m", "chore: base"], repo)
    _git(["checkout", "-q", "-b", "feat/test"], repo)

    (repo / "a.md").write_text("a\n", encoding="utf-8")
    _git(["add", "a.md"], repo)
    _git(["commit", "-q", "-m", "feat: add a"], repo)

    (repo / "b.md").write_text("b\n", encoding="utf-8")
    _git(["add", "b.md"], repo)
    _git(["commit", "-q", "-m", "fix: add b\n\nWith body\nand newline"], repo)

    (repo / "c.md").write_text("c\n", encoding="utf-8")
    _git(["add", "c.md"], repo)
    _git(["commit", "-q", "-m", "docs: add c"], repo)

    return "main"


class TestFetchCommits(unittest.TestCase):
    def test_emits_records_for_branch_ahead_of_main(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            base = _seed_repo(repo)
            result = subprocess.run(
                ["bash", str(SCRIPT), "-b", base],
                cwd=repo,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        # Header line carries the commit count.
        self.assertIn("commit_count=3", result.stdout)
        # Three `---\n` record separators in the body.
        records = [r for r in result.stdout.split("---\n") if "\x00" in r]
        self.assertEqual(len(records), 3)

    def test_body_with_newlines_preserved(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            base = _seed_repo(repo)
            result = subprocess.run(
                ["bash", str(SCRIPT), "-b", base],
                cwd=repo,
                capture_output=True,
                text=True,
                check=False,
            )
        # The "fix: add b" commit body has a newline; check the body survives.
        self.assertIn("With body\nand newline", result.stdout)

    def test_zero_commits_when_branch_equals_base(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            _seed_repo(repo)
            # Switch back to base, no commits ahead.
            _git(["checkout", "-q", "main"], repo)
            result = subprocess.run(
                ["bash", str(SCRIPT), "-b", "main"],
                cwd=repo,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("commit_count=0", result.stdout)


class TestScriptShape(unittest.TestCase):
    def test_script_is_executable(self):
        self.assertTrue(os.access(SCRIPT, os.X_OK), "script must be chmod +x")


if __name__ == "__main__":
    unittest.main()
