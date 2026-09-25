"""Tests for the Refine sub-step between Execute and eXamine.

Refine only earns its place if no path skips it: the step chain must route
Execute through it, the saved progress table must carry its row so a resume
interrupted mid-refine lands back on it, and the step must protect every
accepted behavior so it cannot trade correctness for line count.
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
REFINE = STEPS / "step-03b-refine.md"

BASH = shutil.which("bash") or "/bin/bash"


def _frontmatter_value(path: Path, key: str) -> str:
    text = path.read_text(encoding="utf-8")
    block = text.split("---", 2)[1]
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

    def test_skill_md_step_table_lists_refine(self):
        skill = (APEX / "SKILL.md").read_text(encoding="utf-8")
        self.assertRegex(skill, r"\|\s*03b\s*\|\s*`steps/step-03b-refine\.md`")


class TestProgressRow(unittest.TestCase):
    """The saved progress table drives resume; the refine row must exist,
    sit between Execute and eXamine, and be writable by update-progress.sh."""

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

    def test_refine_row_sits_between_execute_and_examine(self):
        names = [name for name, _ in self._rows()]
        self.assertEqual(names.index("03b-refine"), names.index("03-execute") + 1)
        self.assertEqual(names.index("04-examine"), names.index("03b-refine") + 1)

    def test_resume_after_execute_lands_on_refine(self):
        for num, name in (("01", "analyze"), ("02", "plan"), ("03", "execute")):
            r = _run("update-progress.sh", self.task_id, num, name, "complete", cwd=self.proj, home=self.home)
            self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)
        r = _run("update-progress.sh", self.task_id, "03b", "refine", "in_progress", cwd=self.proj, home=self.home)
        self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)

        pending = [name for name, status in self._rows() if "Complete" not in status]
        self.assertEqual(pending[0], "03b-refine")

        # Step-00 validates entry with step 4 (prior steps 01-03 complete).
        r = _run("validate_state.sh", self.task_id, "4", cwd=self.proj, home=self.home)
        self.assertEqual(r.returncode, 0, msg=r.stderr)

    def test_each_step_hands_off_to_the_next_row(self):
        handoffs = {
            "step-03-execute.md": '"03b" "refine" "in_progress"',
            "step-03b-refine.md": '"04" "examine" "in_progress"',
        }
        for filename, handoff in handoffs.items():
            with self.subTest(step=filename):
                self.assertIn(handoff, (STEPS / filename).read_text(encoding="utf-8"))

    def test_step_00_resume_routes_refine_row(self):
        step_00 = (STEPS / "step-00-init.md").read_text(encoding="utf-8")
        self.assertIn("`03b-refine`", step_00)
        self.assertIn("Load the step file of the first non-✓ row (`steps/step-03b-refine.md`", step_00)

    def test_legacy_table_without_refine_row_still_hands_off(self):
        """Tasks saved before Refine existed have no 03b row; update-progress.sh
        rejects it, so step-03 must hand off to 04 directly for those tables."""
        text = self.context.read_text(encoding="utf-8").replace("| 03b-refine | ⏸ Pending | |\n", "")
        self.context.write_text(text, encoding="utf-8")
        r = _run("update-progress.sh", self.task_id, "03b", "refine", "in_progress", cwd=self.proj, home=self.home)
        self.assertNotEqual(r.returncode, 0)
        step_03 = (STEPS / "step-03-execute.md").read_text(encoding="utf-8")
        self.assertIn('without a `03b-refine` row (saved before Refine existed) marks `"04" "examine" "in_progress"` instead', step_03)
        r = _run("update-progress.sh", self.task_id, "04", "examine", "in_progress", cwd=self.proj, home=self.home)
        self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)


class TestRefineContract(unittest.TestCase):
    def setUp(self):
        self.text = REFINE.read_text(encoding="utf-8")

    def test_only_accepted_behavior_is_protected(self):
        # Refine may shrink what the task itself introduced, never accepted
        # behavior or pre-existing public signatures.
        self.assertIn("keep every accepted behavior, the public signatures that existed before the task", self.text)
        self.assertIn("Signatures, options, files and tests the task itself introduced may shrink", self.text)
        self.assertIn("would change an accepted behavior or pre-existing code to Examine", self.text)

    def test_user_checkpoint_follows_refine(self):
        step_03 = (STEPS / "step-03-execute.md").read_text(encoding="utf-8")
        self.assertIn("checkpoint the user requested before validation happens after Refine", step_03)

    def test_skip_still_closes_the_progress_row(self):
        self.assertIn("then run § 7 so the progress row still closes", self.text)

    def test_guards_protect_what_must_never_be_simplified(self):
        self.assertIn("Never simplified away", self.text)
        self.assertIn("Readability guard", self.text)

    def test_failed_recheck_reverts_instead_of_fixing_forward(self):
        self.assertIn("reverts the finding that caused it", self.text)

    def test_reviewer_is_fresh_with_disclosed_fallback(self):
        self.assertIn("fresh-context reviewer", self.text)
        self.assertIn("shared-context", self.text)

    def test_records_net_delta(self):
        self.assertIn("Net: −N lines", self.text)

    def test_asks_no_questions(self):
        self.assertNotIn("questions:\n  - header:", self.text)


if __name__ == "__main__":
    unittest.main()
