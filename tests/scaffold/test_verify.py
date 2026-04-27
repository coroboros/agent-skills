"""Tests for skills/scaffold/scripts/verify_scaffold.sh.

Strategy: stub `pnpm` with a fake-bin script that branches on its first
argument (`biome` vs `typecheck`) and uses env vars to control exit codes
and output payloads. That gives full determinism over both code paths
plus the diagnostics-truncation behaviour.
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
VERIFY = SCRIPTS / "verify_scaffold.sh"

BASH = shutil.which("bash") or "/bin/bash"


def _make_pnpm_stub(bin_dir: Path) -> None:
    """Stub pnpm: behaviour driven by FAKE_BIOME_EXIT, FAKE_TYPECHECK_EXIT,
    FAKE_BIOME_LINES, FAKE_TYPECHECK_LINES env vars.
    """
    stub = bin_dir / "pnpm"
    stub.write_text(
        '#!/bin/sh\n'
        'case "$1" in\n'
        '  biome)\n'
        '    n="${FAKE_BIOME_LINES:-0}"\n'
        '    i=0\n'
        '    while [ "$i" -lt "$n" ]; do\n'
        '      echo "biome diag line $i"\n'
        '      i=$((i+1))\n'
        '    done\n'
        '    exit "${FAKE_BIOME_EXIT:-0}"\n'
        '    ;;\n'
        '  typecheck)\n'
        '    n="${FAKE_TYPECHECK_LINES:-0}"\n'
        '    i=0\n'
        '    while [ "$i" -lt "$n" ]; do\n'
        '      echo "ts diag line $i"\n'
        '      i=$((i+1))\n'
        '    done\n'
        '    exit "${FAKE_TYPECHECK_EXIT:-0}"\n'
        '    ;;\n'
        '  *) exit 0 ;;\n'
        'esac\n'
    )
    stub.chmod(stub.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def _run(target_dir, fake_bin: Path | None = None, extra_env: dict | None = None):
    env = os.environ.copy()
    base_path = "/usr/bin:/bin:/usr/sbin:/sbin"
    env["PATH"] = f"{fake_bin}:{base_path}" if fake_bin else base_path
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [BASH, str(VERIFY), str(target_dir)],
        capture_output=True,
        text=True,
        env=env,
    )


class TestPreconditions(unittest.TestCase):
    def test_missing_target_dir_flagged(self):
        with tempfile.TemporaryDirectory() as t:
            ghost = Path(t) / "does-not-exist"
            r = _run(ghost)
        self.assertEqual(r.returncode, 1)
        self.assertIn("project_dir does not exist", r.stderr)

    def test_target_without_package_json_flagged(self):
        with tempfile.TemporaryDirectory() as t:
            empty = Path(t) / "proj"
            empty.mkdir()
            r = _run(empty)
        self.assertEqual(r.returncode, 1)
        self.assertIn("no package.json", r.stderr)


class TestBiomeAndTypecheckCapture(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.target = self.tmp / "proj"
        self.target.mkdir()
        (self.target / "package.json").write_text('{"name": "demo"}')
        self.fake_bin = self.tmp / "bin"
        self.fake_bin.mkdir()
        _make_pnpm_stub(self.fake_bin)

    def tearDown(self):
        self._tmp.cleanup()

    def test_both_pass(self):
        r = _run(self.target, fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 0)
        self.assertIn("RESULT: biome=pass", r.stdout)
        self.assertIn("RESULT: typecheck=pass", r.stdout)
        self.assertIn("RESULT: ok=true", r.stdout)

    def test_biome_failure_recorded(self):
        """biome fails → both RESULT lines emitted, typecheck still runs,
        verdict reaches ok=false, script exits 1."""
        r = _run(self.target, fake_bin=self.fake_bin, extra_env={"FAKE_BIOME_EXIT": "1"})
        self.assertEqual(r.returncode, 1)
        self.assertIn("RESULT: biome=fail", r.stdout)
        self.assertIn("RESULT: typecheck=", r.stdout)  # typecheck branch still runs
        self.assertIn("RESULT: ok=false", r.stdout)

    def test_typecheck_failure_recorded(self):
        """typecheck fails (biome ok) → verdict reaches ok=false, exits 1."""
        r = _run(self.target, fake_bin=self.fake_bin, extra_env={"FAKE_TYPECHECK_EXIT": "2"})
        self.assertEqual(r.returncode, 1)
        self.assertIn("RESULT: biome=pass", r.stdout)
        self.assertIn("RESULT: typecheck=fail", r.stdout)
        self.assertIn("RESULT: ok=false", r.stdout)


class TestDiagnosticsTruncation(unittest.TestCase):
    """On failure, the script tails diagnostics to stderr capped at 60 lines."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.target = self.tmp / "proj"
        self.target.mkdir()
        (self.target / "package.json").write_text('{"name": "demo"}')
        self.fake_bin = self.tmp / "bin"
        self.fake_bin.mkdir()
        _make_pnpm_stub(self.fake_bin)

    def tearDown(self):
        self._tmp.cleanup()

    def test_typecheck_diagnostics_capped_at_60_lines(self):
        # Generate 200 diag lines from the failing typecheck — only 60 should
        # appear in stderr between the diagnostics markers. The pipeline-induced
        # early exit doesn't matter here: `head -60` runs before the script
        # short-circuits, so the truncated payload is fully written.
        r = _run(
            self.target,
            fake_bin=self.fake_bin,
            extra_env={"FAKE_TYPECHECK_EXIT": "1", "FAKE_TYPECHECK_LINES": "200"},
        )
        self.assertNotEqual(r.returncode, 0)
        marker_open = "--- typecheck diagnostics (first 60 lines) ---"
        # The closing marker sits after the pipe in the script — depending on
        # `pipefail` propagation it may not be emitted. Assert the cap directly.
        self.assertIn(marker_open, r.stderr)
        diag_lines = [ln for ln in r.stderr.splitlines() if ln.startswith("ts diag line")]
        self.assertEqual(len(diag_lines), 60, msg=f"got {len(diag_lines)} lines")
        # Confirms `head -60` cut at exactly 60 (lines 0..59).
        self.assertIn("ts diag line 0", r.stderr)
        self.assertIn("ts diag line 59", r.stderr)
        self.assertNotIn("ts diag line 60", r.stderr)


if __name__ == "__main__":
    unittest.main()
