"""Tests for skills/apex/scripts/setup-templates.sh.

Strategy: run the script with cwd=tempdir so PROJECT_ROOT (pwd) is the
tempdir, then verify the .claude/output/apex/<NN-feature>/ structure was
created with all 5 step templates rendered (variable substitution applied).
"""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "skills" / "apex" / "scripts" / "setup-templates.sh"

BASH = shutil.which("bash") or "/bin/bash"

EXPECTED_FILES = (
    "00-context.md",
    "01-analyze.md",
    "02-plan.md",
    "03-execute.md",
    "04-examine.md",
)


def _run(*args, cwd):
    return subprocess.run(
        [BASH, str(SCRIPT), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=30,
    )


class TestArgValidation(unittest.TestCase):
    def test_no_args_exits_1(self):
        with tempfile.TemporaryDirectory() as t:
            r = _run(cwd=t)
        self.assertEqual(r.returncode, 1)
        self.assertIn("FEATURE_NAME is required", r.stdout + r.stderr)

    def test_missing_task_description_exits_1(self):
        with tempfile.TemporaryDirectory() as t:
            r = _run("add-auth", cwd=t)
        self.assertEqual(r.returncode, 1)
        self.assertIn("TASK_DESCRIPTION is required", r.stdout + r.stderr)


class TestFreshRun(unittest.TestCase):
    def test_creates_full_template_set(self):
        with tempfile.TemporaryDirectory() as t:
            r = _run("add-auth", "Implement JWT-based auth", cwd=t)
            self.assertEqual(r.returncode, 0,
                             f"stderr={r.stderr}\nstdout={r.stdout}")
            tmp = Path(t)
            apex = tmp / ".claude" / "output" / "apex"
            self.assertTrue(apex.is_dir())

            tasks = list(apex.iterdir())
            self.assertEqual(len(tasks), 1)
            task = tasks[0]
            self.assertRegex(task.name, r"^\d{2}-add-auth$")

            for fn in EXPECTED_FILES:
                f = task / fn
                self.assertTrue(f.is_file(), f"missing rendered file: {fn}")
                content = f.read_text(encoding="utf-8")
                # Template tokens must be substituted, not left raw.
                self.assertNotIn("{{task_id}}", content)
                self.assertNotIn("{{task_description}}", content)
                self.assertNotIn("{{timestamp}}", content)

            # Stdout reports TASK_ID + OUTPUT_DIR for caller capture.
            self.assertIn(f"TASK_ID={task.name}", r.stdout)
            self.assertIn("OUTPUT_DIR=", r.stdout)


class TestAutoIncrement(unittest.TestCase):
    def test_second_run_increments_task_number(self):
        with tempfile.TemporaryDirectory() as t:
            r1 = _run("first-feature", "First task", cwd=t)
            self.assertEqual(r1.returncode, 0)
            r2 = _run("second-feature", "Second task", cwd=t)
            self.assertEqual(r2.returncode, 0)

            apex = Path(t) / ".claude" / "output" / "apex"
            tasks = sorted(p.name for p in apex.iterdir())
            self.assertEqual(len(tasks), 2)
            self.assertEqual(tasks[0], "01-first-feature")
            self.assertEqual(tasks[1], "02-second-feature")

    def test_high_existing_number_continues(self):
        """Existing 09-foo → next is 10-bar."""
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            (tmp / ".claude" / "output" / "apex" / "09-existing").mkdir(parents=True)
            r = _run("new-task", "Description", cwd=t)
            self.assertEqual(r.returncode, 0,
                             f"stderr={r.stderr}\nstdout={r.stdout}")
            apex = tmp / ".claude" / "output" / "apex"
            new = [p.name for p in apex.iterdir() if "new-task" in p.name]
            self.assertEqual(new, ["10-new-task"])

    def test_octal_safe_eight_increments_to_nine(self):
        """Pin the `10#$HIGHEST` base-10 cast: 08 + 1 = 9, not bash-octal error."""
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            (tmp / ".claude" / "output" / "apex" / "08-prior").mkdir(parents=True)
            r = _run("octal-edge", "case", cwd=t)
            self.assertEqual(r.returncode, 0,
                             f"stderr={r.stderr}\nstdout={r.stdout}")
            apex = tmp / ".claude" / "output" / "apex"
            new = [p.name for p in apex.iterdir() if "octal-edge" in p.name]
            self.assertEqual(new, ["09-octal-edge"])


if __name__ == "__main__":
    unittest.main()
