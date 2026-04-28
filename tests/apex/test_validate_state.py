"""Tests for skills/apex/scripts/validate_state.sh.

The script resolves the project root via `git rev-parse --show-toplevel`
with a `pwd` fallback; tests run with `cwd=` set to a temp dir outside any
git repo so the fallback is exercised deterministically.
"""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "skills" / "apex" / "scripts" / "validate_state.sh"


def _run(*args, cwd):
    """Run validate_state.sh from `cwd` with `GIT_CEILING_DIRECTORIES` set
    so git never walks above the temp dir."""
    env = os.environ.copy()
    env["GIT_CEILING_DIRECTORIES"] = str(cwd)
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=env,
        timeout=30,
    )


def _seed_task(root: Path, task_id: str, *, with_context=True, step_files=None, progress_rows=None):
    """Materialize a fake apex task tree under `root/.claude/output/apex/<task_id>/`."""
    task_dir = root / ".claude" / "output" / "apex" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    if with_context:
        body = "# Context\n\n## Progress\n\n| Step | Status | Updated |\n|------|--------|---------|\n"
        for row in progress_rows or []:
            body += f"| {row} |\n"
        (task_dir / "00-context.md").write_text(body, encoding="utf-8")
    for fname in step_files or []:
        (task_dir / fname).write_text(f"# {fname}\n", encoding="utf-8")
    return task_dir


class TestValidateState(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        # `.resolve()` follows /var → /private/var on macOS so paths in stdout
        # (which the script emits via `pwd`-style resolution) match.
        self.root = Path(self._tmp.name).resolve()

    def tearDown(self):
        self._tmp.cleanup()

    def test_invalid_step_num_rejected(self):
        """step_num must be 1-4; anything else exits 1 with stderr error."""
        result = _run("01-foo", "9", cwd=self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("step_num must be 1-4", result.stderr)

    def test_missing_task_folder_exits_1(self):
        """No task dir under .claude/output/apex/ → exit 1, task-missing."""
        result = _run("01-nonexistent", "2", cwd=self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("error=task-missing", result.stderr)

    def test_missing_context_file_exits_1(self):
        """Task dir present but no 00-context.md → exit 1, context-missing."""
        _seed_task(self.root, "01-foo", with_context=False)
        result = _run("01-foo", "2", cwd=self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("error=context-missing", result.stderr)

    def test_missing_prior_step_file_exits_2(self):
        """Asking for step 2 without 01-*.md present → exit 2, step-file-missing."""
        _seed_task(self.root, "01-foo")
        result = _run("01-foo", "2", cwd=self.root)
        self.assertEqual(result.returncode, 2)
        self.assertIn("error=step-file-missing", result.stderr)
        self.assertIn("step=01", result.stderr)

    def test_prior_step_not_marked_complete_exits_3(self):
        """01-analyze.md exists but progress row is not '✓ Complete' → exit 3."""
        _seed_task(
            self.root,
            "01-foo",
            step_files=["01-analyze.md"],
            progress_rows=["01-analyze | ⏳ In Progress | 2026-01-01T00:00:00Z"],
        )
        result = _run("01-foo", "2", cwd=self.root)
        self.assertEqual(result.returncode, 3)
        self.assertIn("error=step-incomplete", result.stderr)
        self.assertIn("name=analyze", result.stderr)

    def test_full_chain_complete_exits_0(self):
        """All prior steps present and marked ✓ Complete → exit 0, RESULT: ok=true."""
        _seed_task(
            self.root,
            "01-foo",
            step_files=["01-analyze.md", "02-plan.md"],
            progress_rows=[
                "01-analyze | ✓ Complete | 2026-01-01T00:00:00Z",
                "02-plan | ✓ Complete | 2026-01-01T00:00:00Z",
            ],
        )
        result = _run("01-foo", "3", cwd=self.root)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("RESULT: ok=true", result.stdout)
        self.assertIn("step=3", result.stdout)

    def test_step_one_skips_prior_check(self):
        """Step 1 has no prior steps to verify. Empty range under macOS BSD-seq
        used to count down (`seq 1 0` → '1\n0'), making validation try non-existent
        prior steps. The C-style for-loop fix makes this a clean no-op."""
        _seed_task(self.root, "01-foo")
        result = _run("01-foo", "1", cwd=self.root)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("RESULT: ok=true", result.stdout)
        self.assertIn("step=1", result.stdout)


if __name__ == "__main__":
    unittest.main()
