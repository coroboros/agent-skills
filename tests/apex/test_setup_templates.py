"""Tests for skills/apex/scripts/setup-templates.sh.

Strategy: run the script with cwd=<project> and an isolated HOME, then verify
the global `$HOME/.agents/output/<project>/apex/<NN-feature>/` structure was
created with all 5 step templates rendered (variable substitution applied).
`<project>` = kebab-cased basename of the project root (git toplevel, else
pwd). Output is global per .agents/rules/repo-conventions.md § Output paths —
the tests also assert it never lands inside the project tree (de-pollution).
"""

import os
import re
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


def _project(root: Path) -> str:
    """Python mirror of the scripts' bash kebab:
    basename | tr lower | tr -cs a-z0-9 - | strip leading/trailing -."""
    return re.sub(r"[^a-z0-9]+", "-", root.name.lower()).strip("-")


def _run(*args, cwd, home):
    env = os.environ.copy()
    env["HOME"] = str(home)  # isolate global output dir from the dev's real ~
    return subprocess.run(
        [BASH, str(SCRIPT), *args],
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


class TestArgValidation(unittest.TestCase):
    def test_no_args_exits_1(self):
        with tempfile.TemporaryDirectory() as t:
            r = _run(cwd=t, home=t)
        self.assertEqual(r.returncode, 1)
        self.assertIn("FEATURE_NAME is required", r.stdout + r.stderr)

    def test_missing_task_description_exits_1(self):
        with tempfile.TemporaryDirectory() as t:
            r = _run("add-auth", cwd=t, home=t)
        self.assertEqual(r.returncode, 1)
        self.assertIn("TASK_DESCRIPTION is required", r.stdout + r.stderr)


class TestFreshRun(unittest.TestCase):
    def test_creates_full_template_set(self):
        with tempfile.TemporaryDirectory() as t:
            proj = Path(t) / "proj"
            home = Path(t) / "home"
            proj.mkdir()
            home.mkdir()
            r = _run("add-auth", "Implement JWT-based auth", cwd=proj, home=home)
            self.assertEqual(r.returncode, 0,
                             f"stderr={r.stderr}\nstdout={r.stdout}")

            apex = home / ".agents" / "output" / _project(proj) / "apex"
            self.assertTrue(apex.is_dir(),
                            f"expected global apex dir at {apex}")
            # De-pollution: nothing written inside the project tree.
            self.assertFalse((proj / ".agents").exists(),
                             "output must NOT be created inside the project")

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
            self.assertIn(f"OUTPUT_DIR={task}", r.stdout)


class TestProjectRootAnchor(unittest.TestCase):
    """`{project}` derives from `git rev-parse --show-toplevel`, falling back
    to pwd outside a git repo — identical to resume_lookup.sh /
    update-progress.sh / validate_state.sh. Output is global under $HOME,
    keyed by that project name, never inside the project tree.
    """

    def test_subdir_of_git_repo_anchors_to_toplevel(self):
        with tempfile.TemporaryDirectory() as t:
            proj = Path(t).resolve() / "proj"
            home = Path(t).resolve() / "home"
            proj.mkdir()
            home.mkdir()
            subprocess.run(["git", "init", "--quiet", str(proj)], check=True)
            nested = proj / "packages" / "app"
            nested.mkdir(parents=True)
            r = _run("nested-task", "Run from a subdirectory",
                     cwd=nested, home=home)
            self.assertEqual(r.returncode, 0,
                             f"stderr={r.stderr}\nstdout={r.stdout}")

            apex = home / ".agents" / "output" / _project(proj) / "apex"
            self.assertTrue(apex.is_dir(),
                            "output keyed by git-toplevel basename, global")
            self.assertFalse((proj / ".agents").exists(),
                             "output must NOT be created in the repo")
            self.assertFalse((nested / ".agents").exists(),
                             "output must NOT be created at the nested cwd")
            task = next(apex.iterdir())
            self.assertIn(f"OUTPUT_DIR={task}", r.stdout)

    def test_non_git_dir_falls_back_to_pwd(self):
        with tempfile.TemporaryDirectory() as t:
            proj = Path(t).resolve() / "proj"
            home = Path(t).resolve() / "home"
            proj.mkdir()
            home.mkdir()
            r = _run("plain-task", "No git here", cwd=proj, home=home)
            self.assertEqual(r.returncode, 0,
                             f"stderr={r.stderr}\nstdout={r.stdout}")
            apex = home / ".agents" / "output" / _project(proj) / "apex"
            self.assertTrue(apex.is_dir())
            self.assertFalse((proj / ".agents").exists())


class TestMetacharSafety(unittest.TestCase):
    """awk -v with index/substr substitution renders TASK_DESCRIPTION
    literally — no regex interpretation of sed s/// metachars (|, &, \\, /, $).
    Pins the W011 hardening: shell metachars in user input cannot escape into
    the template machinery."""

    NASTY = "pipe|amp&backslash\\slash/dollar$quote\"apos'brace{close}"

    def test_metachars_render_literally_in_context(self):
        with tempfile.TemporaryDirectory() as t:
            proj = Path(t) / "proj"
            home = Path(t) / "home"
            proj.mkdir()
            home.mkdir()
            r = _run("metachar-test", self.NASTY, cwd=proj, home=home)
            self.assertEqual(r.returncode, 0,
                             f"stderr={r.stderr}\nstdout={r.stdout}")

            apex = home / ".agents" / "output" / _project(proj) / "apex"
            task = next(apex.iterdir())
            ctx = (task / "00-context.md").read_text(encoding="utf-8")
            self.assertIn(self.NASTY, ctx,
                          f"TASK_DESCRIPTION metachars not preserved literally; "
                          f"context excerpt:\n{ctx[:600]}")

    def test_sed_delimiter_pipe_does_not_break_substitution(self):
        """A bare `|` in TASK_DESCRIPTION would have crashed the old sed
        s|...|...| chain — must now render as a plain pipe character."""
        with tempfile.TemporaryDirectory() as t:
            proj = Path(t) / "proj"
            home = Path(t) / "home"
            proj.mkdir()
            home.mkdir()
            r = _run("pipe-test", "a|b|c", cwd=proj, home=home)
            self.assertEqual(r.returncode, 0,
                             f"stderr={r.stderr}\nstdout={r.stdout}")
            apex = home / ".agents" / "output" / _project(proj) / "apex"
            task = next(apex.iterdir())
            ctx = (task / "00-context.md").read_text(encoding="utf-8")
            self.assertIn("a|b|c", ctx)


class TestAutoIncrement(unittest.TestCase):
    def test_second_run_increments_task_number(self):
        with tempfile.TemporaryDirectory() as t:
            proj = Path(t) / "proj"
            home = Path(t) / "home"
            proj.mkdir()
            home.mkdir()
            r1 = _run("first-feature", "First task", cwd=proj, home=home)
            self.assertEqual(r1.returncode, 0)
            r2 = _run("second-feature", "Second task", cwd=proj, home=home)
            self.assertEqual(r2.returncode, 0)

            apex = home / ".agents" / "output" / _project(proj) / "apex"
            tasks = sorted(p.name for p in apex.iterdir())
            self.assertEqual(len(tasks), 2)
            self.assertEqual(tasks[0], "01-first-feature")
            self.assertEqual(tasks[1], "02-second-feature")

    def test_high_existing_number_continues(self):
        """Existing 09-foo → next is 10-bar."""
        with tempfile.TemporaryDirectory() as t:
            proj = Path(t) / "proj"
            home = Path(t) / "home"
            proj.mkdir()
            (home / ".agents" / "output" / _project(proj) / "apex" / "09-existing").mkdir(parents=True)
            r = _run("new-task", "Description", cwd=proj, home=home)
            self.assertEqual(r.returncode, 0,
                             f"stderr={r.stderr}\nstdout={r.stdout}")
            apex = home / ".agents" / "output" / _project(proj) / "apex"
            new = [p.name for p in apex.iterdir() if "new-task" in p.name]
            self.assertEqual(new, ["10-new-task"])

    def test_octal_safe_eight_increments_to_nine(self):
        """Pin the `10#$HIGHEST` base-10 cast: 08 + 1 = 9, not bash-octal error."""
        with tempfile.TemporaryDirectory() as t:
            proj = Path(t) / "proj"
            home = Path(t) / "home"
            proj.mkdir()
            (home / ".agents" / "output" / _project(proj) / "apex" / "08-prior").mkdir(parents=True)
            r = _run("octal-edge", "case", cwd=proj, home=home)
            self.assertEqual(r.returncode, 0,
                             f"stderr={r.stderr}\nstdout={r.stdout}")
            apex = home / ".agents" / "output" / _project(proj) / "apex"
            new = [p.name for p in apex.iterdir() if "octal-edge" in p.name]
            self.assertEqual(new, ["09-octal-edge"])


class TestContextTemplateSeed(unittest.TestCase):
    """00-init must seed complete: the table exists only once init wrote it, and a
    Pending row makes every resume resolve step_num 0, which validate_state rejects."""

    def test_template_seeds_00_init_complete(self):
        template = (REPO_ROOT / "skills" / "apex" / "templates" / "00-context.md").read_text(encoding="utf-8")
        self.assertIn("| 00-init | ✓ Complete |", template)
        self.assertNotIn("| 00-init | ⏸ Pending |", template)


if __name__ == "__main__":
    unittest.main()
