"""Tests that --legacy output is byte-identical to v1 (pre-extends) output.

The v1 reference is checked out from git into a temp dir before each test so
the comparison is exact and stable across edits.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
LIVE_SCRIPTS = REPO_ROOT / "skills" / "brand-voice" / "scripts"
FIXTURES = Path(__file__).parent / "fixtures"


_V1_REF = "1.6.0"  # the pre-inheritance baseline (last release before extends:)


def _git_show(path):
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), "show", f"{_V1_REF}:{path}"],
        capture_output=True, text=True, check=False,
        timeout=30,
    ).stdout


class TestByteIdentity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp(prefix="brand-voice-v1-")
        cls.tmp = Path(cls.tmpdir)

        # Write v1 extract_rules.py + utils.py from the pre-inheritance ref (main)
        old_extract = _git_show("skills/brand-voice/scripts/extract_rules.py")
        old_utils = _git_show("skills/brand-voice/scripts/utils.py")
        if not old_extract or not old_utils:
            raise unittest.SkipTest(f"v1 scripts not present at {_V1_REF}")
        (cls.tmp / "extract_rules.py").write_text(old_extract, encoding="utf-8")
        (cls.tmp / "utils.py").write_text(old_utils, encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def _run_v1(self, fixture):
        return subprocess.run(
            [sys.executable, str(self.tmp / "extract_rules.py"), str(fixture)],
            capture_output=True, text=True,
            timeout=30,
        )

    def _run_legacy(self, fixture):
        return subprocess.run(
            [sys.executable, str(LIVE_SCRIPTS / "extract_rules.py"), "--legacy", str(fixture)],
            capture_output=True, text=True,
            timeout=30,
        )

    def test_parent_corp_byte_identical(self):
        v1 = self._run_v1(FIXTURES / "parent-corp.md")
        legacy = self._run_legacy(FIXTURES / "parent-corp.md")
        self.assertEqual(v1.returncode, 0, f"v1 failed: {v1.stderr}")
        self.assertEqual(legacy.returncode, 0, f"legacy failed: {legacy.stderr}")
        self.assertEqual(v1.stdout, legacy.stdout)

    def test_external_brand_voice_byte_identical(self):
        """Use BRAND_VOICE_TEST_FILE when set, else the optional workspace voice."""
        explicit_voice = os.environ.get("BRAND_VOICE_TEST_FILE")
        workspace_voice = (Path(explicit_voice).expanduser() if explicit_voice
                           else REPO_ROOT.parent / "BRAND-VOICE.md")
        if explicit_voice:
            self.assertTrue(workspace_voice.is_file(),
                            "BRAND_VOICE_TEST_FILE must point to an existing file")
        if not workspace_voice.is_file():
            self.skipTest("external fixture is not configured or available")
        # External fixtures may be private; failure logs must not echo their data.
        try:
            v1 = self._run_v1(workspace_voice)
            legacy = self._run_legacy(workspace_voice)
        except (OSError, subprocess.TimeoutExpired):
            raise self.failureException("external fixture extraction could not finish") from None
        self.assertEqual(v1.returncode, 0, "v1 extraction failed for external fixture")
        self.assertEqual(legacy.returncode, 0, "legacy extraction failed for external fixture")
        self.assertTrue(v1.stdout == legacy.stdout,
                        "external fixture extraction results differ")


if __name__ == "__main__":
    unittest.main()
