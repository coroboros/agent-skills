"""Tests for skills/apex/scripts/update-progress.sh.

Strategy: build a fresh tempdir with a synthetic 00-context.md containing a
Progress table, run the script with cwd=tempdir (so `git rev-parse
--show-toplevel` falls back to `pwd` outside any repo), and inspect the
resulting file.
"""

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "skills" / "apex" / "scripts" / "update-progress.sh"

BASH = shutil.which("bash") or "/bin/bash"


CONTEXT_TEMPLATE = """\
# Task Context

## Progress

| step | status | timestamp |
|------|--------|-----------|
| 01-analyze | ⏳ Pending | n/a |
| 02-implement | ⏳ Pending | n/a |
"""


def _run(*args, cwd):
    env = os.environ.copy()
    # Prevent `git rev-parse --show-toplevel` from walking above the tempdir
    # and discovering an unrelated repo on the host. The script's `|| pwd`
    # fallback then deterministically yields cwd as PROJECT_ROOT.
    env["GIT_CEILING_DIRECTORIES"] = str(Path(cwd).parent)
    return subprocess.run(
        [BASH, str(SCRIPT), *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )


def _seed(workdir: Path, task_id: str = "01-add-auth",
          body: str = CONTEXT_TEMPLATE) -> Path:
    ctx_dir = workdir / ".claude" / "output" / "apex" / task_id
    ctx_dir.mkdir(parents=True)
    ctx_file = ctx_dir / "00-context.md"
    ctx_file.write_text(body, encoding="utf-8")
    return ctx_file


class TestArgValidation(unittest.TestCase):
    def test_no_args_exits_1(self):
        with tempfile.TemporaryDirectory() as t:
            r = _run(cwd=t)
        self.assertEqual(r.returncode, 1)
        self.assertIn("Usage:", r.stdout + r.stderr)

    def test_partial_args_exits_1(self):
        with tempfile.TemporaryDirectory() as t:
            r = _run("01-add-auth", "01", "analyze", cwd=t)
        self.assertEqual(r.returncode, 1)

    def test_invalid_status_exits_1(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            _seed(tmp)
            r = _run("01-add-auth", "01", "analyze", "started", cwd=t)
        self.assertEqual(r.returncode, 1)
        self.assertIn("Invalid status", r.stdout + r.stderr)


class TestMissingContext(unittest.TestCase):
    def test_missing_context_file_exits_1(self):
        with tempfile.TemporaryDirectory() as t:
            r = _run("01-add-auth", "01", "analyze", "complete", cwd=t)
        self.assertEqual(r.returncode, 1)
        self.assertIn("Context file not found", r.stdout + r.stderr)


class TestRowMutation(unittest.TestCase):
    """Happy-path: matched row is replaced with the new status + timestamp."""

    ISO8601_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

    def test_in_progress_marks_step(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            ctx = _seed(tmp)
            r = _run("01-add-auth", "01", "analyze", "in_progress", cwd=t)
            self.assertEqual(r.returncode, 0,
                             f"stderr={r.stderr}\nstdout={r.stdout}")
            updated = ctx.read_text(encoding="utf-8")

        rows = [ln for ln in updated.splitlines() if ln.startswith("| 01-analyze ")]
        self.assertEqual(len(rows), 1, f"expected one matching row, got {rows}")
        self.assertIn("⏳ In Progress", rows[0])
        cols = [c.strip() for c in rows[0].strip("|").split("|")]
        self.assertTrue(self.ISO8601_UTC.match(cols[2]),
                        f"timestamp not ISO 8601 UTC: {cols[2]}")

    def test_complete_marks_step(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            ctx = _seed(tmp)
            r = _run("01-add-auth", "01", "analyze", "complete", cwd=t)
            self.assertEqual(r.returncode, 0)
            updated = ctx.read_text(encoding="utf-8")
        self.assertIn("✓ Complete", updated)
        # The other row is left untouched.
        self.assertIn("| 02-implement | ⏳ Pending |", updated)

    def test_idempotent_re_run(self):
        """Running twice with the same args yields one row for the step;
        the second run replaces the row with a fresh timestamp, no duplication."""
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            ctx = _seed(tmp)
            r1 = _run("01-add-auth", "01", "analyze", "complete", cwd=t)
            self.assertEqual(r1.returncode, 0)
            r2 = _run("01-add-auth", "01", "analyze", "complete", cwd=t)
            self.assertEqual(r2.returncode, 0)
            updated = ctx.read_text(encoding="utf-8")
        rows = [ln for ln in updated.splitlines() if ln.startswith("| 01-analyze ")]
        self.assertEqual(len(rows), 1, "step row duplicated on re-run")


class TestUnknownStep(unittest.TestCase):
    """Unknown step: the awk END block warns to stderr; the script still
    exits 0 because awk completes normally and `mv` succeeds."""

    def test_unknown_step_warns_and_leaves_file_intact(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            ctx = _seed(tmp)
            original = ctx.read_text(encoding="utf-8")
            r = _run("01-add-auth", "99", "ghost-step", "complete", cwd=t)
            updated = ctx.read_text(encoding="utf-8")
        self.assertEqual(r.returncode, 0,
                         f"unknown step should still exit 0; got {r.returncode}")
        self.assertIn("Warning: Step not found", r.stderr)
        # File content is preserved because no row matched the awk replacement.
        self.assertEqual(updated, original)


if __name__ == "__main__":
    unittest.main()
