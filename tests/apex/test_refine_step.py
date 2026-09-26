"""The step graph and rendered progress support Refine after Execute.

The step chain routes Execute through Refine, and the saved progress table
carries its row for resume selection.
"""

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
APEX = REPO_ROOT / "skills" / "apex"
STEPS = APEX / "steps"
SCRIPTS = APEX / "scripts"

BASH = shutil.which("bash") or "/bin/bash"


def _frontmatter_value(path: Path, key: str) -> str:
    block = path.read_text(encoding="utf-8").split("---", 2)[1]
    for line in block.splitlines():
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip()
    raise AssertionError(f"{key} missing from {path.name}")


def _project(root: Path) -> str:
    return re.sub(r"[^a-z0-9]+", "-", root.name.lower()).strip("-")


def _run(script: str, *args, cwd: Path, home: Path):
    env = os.environ.copy()
    env["HOME"] = str(home)
    env["GIT_CEILING_DIRECTORIES"] = str(cwd.parent)
    return subprocess.run(
        [BASH, str(SCRIPTS / script), *args],
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


class TestStepChain(unittest.TestCase):
    def test_next_step_chain_routes_through_refine(self):
        chain = []
        current = STEPS / "step-00-init.md"
        while True:
            chain.append(current.name)
            nxt = _frontmatter_value(current, "next_step")
            if nxt == "null":
                break
            current = APEX / nxt
            self.assertTrue(current.is_file(), f"next_step target missing: {nxt}")
            self.assertLess(len(chain), 10, "next_step chain loops")
        self.assertEqual(
            chain,
            [
                "step-00-init.md",
                "step-01-analyze.md",
                "step-02-plan.md",
                "step-03-execute.md",
                "step-03b-refine.md",
                "step-04-examine.md",
            ],
        )


class TestProgressRow(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name).resolve()
        self.proj = base / "proj"
        self.home = base / "home"
        self.proj.mkdir()
        self.home.mkdir()
        r = _run("setup-templates.sh", "add-auth", "Implement auth", cwd=self.proj, home=self.home)
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        match = re.search(r"TASK_ID=(\S+)", r.stdout)
        if match is None:
            self.fail(f"setup-templates.sh printed no TASK_ID: {r.stdout}")
        self.task_id = match.group(1)
        self.context = (
            self.home / ".agents" / "output" / _project(self.proj) / "apex" / self.task_id / "00-context.md"
        )

    def tearDown(self):
        self._tmp.cleanup()

    def _rows(self):
        return re.findall(r"^\| (\d{2}b?-[a-z]+) \| ([^|]+) \|", self.context.read_text(encoding="utf-8"), re.M)

    def test_updated_progress_validates_with_refine_as_first_pending_step(self):
        for num, name in (("01", "analyze"), ("02", "plan"), ("03", "execute")):
            r = _run("update-progress.sh", self.task_id, num, name, "complete", cwd=self.proj, home=self.home)
            self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)
        r = _run("update-progress.sh", self.task_id, "03b", "refine", "in_progress", cwd=self.proj, home=self.home)
        self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)

        pending = [name for name, status in self._rows() if "Complete" not in status]
        self.assertEqual(pending[0], "03b-refine")

        r = _run("validate_state.sh", self.task_id, "4", cwd=self.proj, home=self.home)
        self.assertEqual(r.returncode, 0, msg=r.stderr)


if __name__ == "__main__":
    unittest.main()
