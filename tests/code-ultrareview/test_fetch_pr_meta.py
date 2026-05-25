"""Tests for scripts/fetch_pr_meta.sh — graceful degradation contract."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "skills" / "code-ultrareview" / "scripts" / "fetch_pr_meta.sh"


class TestNoGh(unittest.TestCase):
    """When `gh` is not on PATH, the script must emit pr_found=false and exit 0."""

    def test_no_gh_on_path(self):
        # A minimal PATH that intentionally excludes anywhere gh might live.
        # Use absolute /bin/bash so the subprocess can still find bash itself.
        with tempfile.TemporaryDirectory() as tmpdir:
            env = {**os.environ, "PATH": tmpdir, "HOME": tmpdir}
            result = subprocess.run(
                ["/bin/bash", str(SCRIPT)],
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("RESULT: pr_found=false", result.stdout)
        self.assertIn("RESULT: hint=gh CLI not on PATH", result.stdout)


@unittest.skipUnless(shutil.which("gh"), "gh CLI not installed; skipping live path")
class TestGhPresentNotAuthOrNoPR(unittest.TestCase):
    """When `gh` is present but auth or PR resolution fails, still exit 0."""

    def test_outside_a_repo_yields_pr_found_false(self):
        # Run from a tmpdir that is not a git repo; whatever the user's gh
        # auth state, the script must report pr_found=false and exit 0.
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                ["bash", str(SCRIPT)],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("RESULT: pr_found=false", result.stdout)


class TestScriptShape(unittest.TestCase):
    def test_script_is_executable(self):
        self.assertTrue(os.access(SCRIPT, os.X_OK), "script must be chmod +x")


if __name__ == "__main__":
    unittest.main()
