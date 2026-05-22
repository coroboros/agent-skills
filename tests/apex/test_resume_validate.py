"""Tests for resume auto-validating state via validate_state.sh.

Step-00-init.md invokes validate_state.sh on every -r resume before state
restoration. SKILL.md Resume Workflow documents the auto-validate. The
script header documents the auto-invocation. Subprocess tests against the
valid-state and corrupt-state fixtures pin the exit-code contract.
"""

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "skills" / "apex" / "scripts" / "validate_state.sh"
STEP_00 = REPO_ROOT / "skills" / "apex" / "steps" / "step-00-init.md"
SKILL_MD = REPO_ROOT / "skills" / "apex" / "SKILL.md"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _project(root: Path) -> str:
    return re.sub(r"[^a-z0-9]+", "-", root.name.lower()).strip("-")


def _run(*args, cwd, home):
    env = os.environ.copy()
    env["GIT_CEILING_DIRECTORIES"] = str(cwd)
    env["HOME"] = str(home)
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=env,
        timeout=30,
    )


class TestResumeValidateDocs(unittest.TestCase):
    """Structural assertions on step-00, SKILL.md, validate_state.sh header."""

    def setUp(self):
        self.step_00 = STEP_00.read_text(encoding="utf-8")
        self.skill_md = SKILL_MD.read_text(encoding="utf-8")
        self.script = SCRIPT.read_text(encoding="utf-8")

    def test_step_00_resume_invokes_validate_state(self):
        """step-00-init.md resume branch invokes validate_state.sh."""
        # Slice the resume branch
        idx_resume = self.step_00.find("### 2. Check Resume Mode")
        idx_next = self.step_00.find("### 3. Run Optional Sub-Steps", idx_resume)
        resume_body = self.step_00[idx_resume:idx_next]
        self.assertIn(
            "validate_state.sh",
            resume_body,
            "Resume branch must invoke validate_state.sh",
        )
        self.assertIn(
            "Auto-validate",
            resume_body,
            "Resume branch must document the auto-validate step",
        )

    def test_step_00_halts_on_non_zero_exit(self):
        """Resume branch halts on non-zero exit from validate_state.sh."""
        idx_resume = self.step_00.find("### 2. Check Resume Mode")
        idx_next = self.step_00.find("### 3. Run Optional Sub-Steps", idx_resume)
        resume_body = self.step_00[idx_resume:idx_next]
        self.assertTrue(
            "Non-zero exit halts" in resume_body or "non-zero" in resume_body.lower(),
            "Resume branch must document the non-zero-exit halt behaviour",
        )

    def test_skill_md_resume_workflow_documents_auto_validate(self):
        """SKILL.md Resume Workflow describes the auto-validate behavior."""
        idx_resume = self.skill_md.find("## Resume Workflow")
        idx_next = self.skill_md.find("\n## ", idx_resume + 1)
        body = self.skill_md[idx_resume:idx_next]
        self.assertIn("auto-validate", body.lower())
        self.assertIn("validate_state.sh", body)

    def test_skill_md_no_longer_calls_validate_state_manual_only(self):
        """SKILL.md must NOT describe validate_state.sh as 'manual debugging utility' anywhere."""
        self.assertNotIn(
            "manual debugging utility",
            self.skill_md,
            "SKILL.md must drop the 'manual debugging utility' framing",
        )

    def test_script_header_documents_auto_invocation(self):
        """validate_state.sh header notes the auto-invocation contract."""
        header = self.script[:1000]  # first ~1KB
        self.assertIn(
            "Auto-invoked",
            header,
            "validate_state.sh header must document auto-invocation",
        )


class TestResumeValidateBehavior(unittest.TestCase):
    """Subprocess tests against fixture states."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._tmp_home = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name).resolve()
        self.home = Path(self._tmp_home.name).resolve()
        self.project = _project(self.root)

    def tearDown(self):
        self._tmp.cleanup()
        self._tmp_home.cleanup()

    def _materialize_fixture(self, fixture_name, task_id):
        """Copy fixture contents into the global apex task dir under temp HOME."""
        fixture_dir = FIXTURES / fixture_name
        task_dir = self.home / ".claude" / "output" / self.project / "apex" / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        for item in fixture_dir.iterdir():
            shutil.copy(item, task_dir / item.name)
        return task_dir

    def test_valid_state_fixture_passes(self):
        """Seeding the valid-state fixture and asking to enter step 4 returns exit 0."""
        self._materialize_fixture("valid-state", "01-test-valid")
        # The fixture marks 01-03 ✓ Complete and 04 ⏳ In Progress, with step
        # files 01-03 present. Validating entry into step 4 (prior steps 1-3
        # checked) must succeed.
        result = _run("01-test-valid", "4", cwd=self.root, home=self.home)
        self.assertEqual(result.returncode, 0, msg=f"stderr={result.stderr}")
        self.assertIn("RESULT: ok=true", result.stdout)

    def test_corrupt_state_fixture_fails_loud(self):
        """Seeding the corrupt-state fixture (00-context only, no step files)
        and asking to enter step 2 exits non-zero with diagnostic."""
        self._materialize_fixture("corrupt-state", "01-test-corrupt")
        result = _run("01-test-corrupt", "2", cwd=self.root, home=self.home)
        self.assertNotEqual(result.returncode, 0, msg="Corrupt state must fail")
        self.assertIn("error=", result.stderr)


if __name__ == "__main__":
    unittest.main()
