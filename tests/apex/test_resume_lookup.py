"""Tests for skills/apex/scripts/resume_lookup.sh.

Same project-root resolution as validate_state.sh: `git rev-parse` then `pwd`.
Tests run with `cwd=` a temp project dir and `GIT_CEILING_DIRECTORIES` capping
the git walk so the fallback is deterministic. Output is global —
`$HOME/.claude/output/apex/<project>/` — so HOME is isolated to a temp dir and
`<project>` = kebab-cased basename of the project root.
"""

import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "skills" / "apex" / "scripts" / "resume_lookup.sh"


def _project(root: Path) -> str:
    """Python mirror of the script's bash kebab."""
    return re.sub(r"[^a-z0-9]+", "-", root.name.lower()).strip("-")


def _run(*args, cwd, home):
    env = os.environ.copy()
    env["GIT_CEILING_DIRECTORIES"] = str(cwd)
    env["HOME"] = str(home)  # isolate global output dir from the dev's real ~
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=env,
        timeout=30,
    )


class TestResumeLookup(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._tmp_home = tempfile.TemporaryDirectory()
        # `.resolve()` follows /var → /private/var on macOS so paths emitted by
        # the script (which resolves cwd via `pwd`) match what we assert against.
        self.root = Path(self._tmp.name).resolve()
        self.home = Path(self._tmp_home.name).resolve()
        self.project = _project(self.root)

    def tearDown(self):
        self._tmp.cleanup()
        self._tmp_home.cleanup()

    def _seed_tasks(self, *task_ids):
        base = self.home / ".claude" / "output" / self.project / "apex"
        base.mkdir(parents=True, exist_ok=True)
        for tid in task_ids:
            (base / tid).mkdir(exist_ok=True)
        return base

    def test_missing_argument_is_usage_error(self):
        """No partial → bash `${1:?...}` triggers a non-zero exit and usage hint."""
        env = os.environ.copy()
        env["GIT_CEILING_DIRECTORIES"] = str(self.root)
        env["HOME"] = str(self.home)
        result = subprocess.run(
            ["bash", str(SCRIPT)],
            capture_output=True,
            text=True,
            cwd=str(self.root),
            env=env,
            timeout=30,
        )
        self.assertEqual(result.returncode, 1, msg=result.stderr)
        self.assertIn("usage", result.stderr.lower())

    def test_missing_apex_dir_exits_2(self):
        """No global apex dir for this project → exit 2, apex-dir-missing."""
        result = _run("01", cwd=self.root, home=self.home)
        self.assertEqual(result.returncode, 2)
        self.assertIn("error=apex-dir-missing", result.stderr)

    def test_no_match_exits_2(self):
        """Apex dir exists but nothing matches the partial → exit 2, no-match."""
        self._seed_tasks("01-auth", "02-payments")
        result = _run("99", cwd=self.root, home=self.home)
        self.assertEqual(result.returncode, 2)
        self.assertIn("error=no-match", result.stderr)
        self.assertIn("partial=99", result.stderr)

    def test_exact_prefix_match_returns_path(self):
        """Single prefix match → exit 0, absolute path on stdout, RESULT line."""
        base = self._seed_tasks("01-auth-middleware", "02-payments")
        result = _run("01", cwd=self.root, home=self.home)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        expected = str(base / "01-auth-middleware")
        self.assertIn(expected, result.stdout)
        self.assertIn("RESULT: ok=true", result.stdout)
        self.assertIn(f"path={expected}", result.stdout)

    def test_substring_match_when_no_prefix_match(self):
        """Partial matches mid-name only → falls back to substring match."""
        base = self._seed_tasks("01-auth-middleware", "02-payments")
        result = _run("middleware", cwd=self.root, home=self.home)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn(str(base / "01-auth-middleware"), result.stdout)

    def test_prefix_match_preferred_over_substring(self):
        """When both prefix and substring matches exist, prefix wins.

        Seeded layout: `01-auth` (prefix match for "01") and `99-foo-01-bar`
        (substring match). Lookup of "01" must resolve to `01-auth` only,
        not flag ambiguity.
        """
        base = self._seed_tasks("01-auth", "99-foo-01-bar")
        result = _run("01", cwd=self.root, home=self.home)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn(str(base / "01-auth"), result.stdout)
        self.assertNotIn("99-foo-01-bar", result.stdout)

    def test_ambiguous_prefix_exits_1_with_candidates(self):
        """Two prefix matches → exit 1, error=ambiguous, candidates listed on stderr."""
        self._seed_tasks("01-auth", "01-billing", "02-payments")
        result = _run("01", cwd=self.root, home=self.home)
        self.assertEqual(result.returncode, 1)
        self.assertIn("error=ambiguous", result.stderr)
        self.assertIn("count=2", result.stderr)
        self.assertIn("01-auth", result.stderr)
        self.assertIn("01-billing", result.stderr)


if __name__ == "__main__":
    unittest.main()
