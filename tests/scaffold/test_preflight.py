"""Tests for skills/scaffold/scripts/preflight.sh.

Strategy: build a per-test fake-bin directory containing stub `node`/`pnpm`
scripts, prepend it to PATH, and run preflight.sh against a temp target dir.
That gives full deterministic control over the version reported and over
presence/absence of each binary.
"""

import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO_ROOT / "skills" / "scaffold" / "scripts"
PREFLIGHT = SCRIPTS / "preflight.sh"


def _make_stub(bin_dir: Path, name: str, body: str) -> None:
    p = bin_dir / name
    p.write_text(body)
    p.chmod(p.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def _run(target_dir: Path, fake_bin: Path | None = None):
    env = os.environ.copy()
    # Keep only system essentials; prepend fake_bin so the stubs win.
    base_path = "/usr/bin:/bin:/usr/sbin:/sbin"
    env["PATH"] = f"{fake_bin}:{base_path}" if fake_bin else base_path
    return subprocess.run(
        ["bash", str(PREFLIGHT), str(target_dir)],
        capture_output=True,
        text=True,
        env=env,
    )


class TestPreflightEnvironment(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.fake_bin = self.tmp / "bin"
        self.fake_bin.mkdir()
        self.target = self.tmp / "project"
        self.target.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def test_node_too_old_flagged(self):
        _make_stub(self.fake_bin, "node", '#!/bin/sh\necho v18.20.0\n')
        _make_stub(self.fake_bin, "pnpm", '#!/bin/sh\necho 9.0.0\n')
        r = _run(self.target, fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 1)
        self.assertIn("RESULT: node=too-old", r.stdout)
        self.assertIn("required=22", r.stdout)
        self.assertIn("RESULT: ok=false", r.stdout)

    def test_node_22_passes(self):
        _make_stub(self.fake_bin, "node", '#!/bin/sh\necho v22.11.0\n')
        _make_stub(self.fake_bin, "pnpm", '#!/bin/sh\necho 9.0.0\n')
        r = _run(self.target, fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 0)
        self.assertIn("RESULT: node=yes version=22.11.0", r.stdout)
        self.assertIn("RESULT: pnpm=yes", r.stdout)
        self.assertIn("RESULT: ok=true", r.stdout)

    def test_pnpm_missing_flagged(self):
        # node present, pnpm absent → exit 1, ok=false, RESULT: pnpm=no.
        _make_stub(self.fake_bin, "node", '#!/bin/sh\necho v22.0.0\n')
        r = _run(self.target, fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 1)
        self.assertIn("RESULT: pnpm=no", r.stdout)
        self.assertIn("RESULT: ok=false", r.stdout)

    def test_node_missing_flagged(self):
        _make_stub(self.fake_bin, "pnpm", '#!/bin/sh\necho 9.0.0\n')
        r = _run(self.target, fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 1)
        self.assertIn("RESULT: node=no", r.stdout)
        self.assertIn("RESULT: ok=false", r.stdout)


class TestPreflightTargetDirState(unittest.TestCase):
    """Target dir state is informational (does not flip ok=*) but must report."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.fake_bin = self.tmp / "bin"
        self.fake_bin.mkdir()
        # Always stub a passing env so we isolate target-state behaviour.
        _make_stub(self.fake_bin, "node", '#!/bin/sh\necho v22.11.0\n')
        _make_stub(self.fake_bin, "pnpm", '#!/bin/sh\necho 9.0.0\n')

    def tearDown(self):
        self._tmp.cleanup()

    def test_target_missing_reported(self):
        missing = self.tmp / "does-not-exist"
        r = _run(missing, fake_bin=self.fake_bin)
        self.assertIn("RESULT: target=missing", r.stdout)
        # Target state is informational — env still OK so exit=0.
        self.assertEqual(r.returncode, 0)

    def test_target_clean_reported(self):
        clean = self.tmp / "clean"
        clean.mkdir()
        r = _run(clean, fake_bin=self.fake_bin)
        self.assertIn("RESULT: target=clean", r.stdout)
        self.assertIn("files=0", r.stdout)
        self.assertEqual(r.returncode, 0)

    def test_target_occupied_via_package_json(self):
        occupied = self.tmp / "occupied"
        occupied.mkdir()
        (occupied / "package.json").write_text("{}")
        r = _run(occupied, fake_bin=self.fake_bin)
        self.assertIn("RESULT: target=occupied", r.stdout)
        self.assertEqual(r.returncode, 0)

    def test_target_occupied_via_next_config(self):
        occupied = self.tmp / "next-occupied"
        occupied.mkdir()
        (occupied / "next.config.ts").write_text("export default {};")
        r = _run(occupied, fake_bin=self.fake_bin)
        self.assertIn("RESULT: target=occupied", r.stdout)


if __name__ == "__main__":
    unittest.main()
