"""Tests for skills/forge/scripts/setup-labels.sh.

The script delegates to `gh label create` for each of 8 labels (P0/P1/P2,
size:S/M/L/XL, forge). Tests use a stub `gh` on PATH to capture invocations
and force exit codes — the real `gh` binary is never exercised.
"""

import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "skills" / "forge" / "scripts" / "setup-labels.sh"

BASH = shutil.which("bash") or "/bin/bash"


def _make_stub_gh(bin_dir: Path, behavior: str = "ok") -> None:
    body = (
        '#!/usr/bin/env bash\n'
        'echo "$@" >> "$STUB_LOG"\n'
        + ('exit 0\n' if behavior == "ok" else 'exit 4\n')
    )
    p = bin_dir / "gh"
    p.write_text(body)
    p.chmod(p.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def _run_with_stub(behavior: str = "ok"):
    with tempfile.TemporaryDirectory() as t:
        bin_dir = Path(t) / "bin"
        bin_dir.mkdir()
        _make_stub_gh(bin_dir, behavior)
        log_path = Path(t) / "calls.log"
        env = os.environ.copy()
        # Stub MUST come first on PATH so it shadows any real gh installed
        # globally on the developer's machine.
        env["PATH"] = f"{bin_dir}{os.pathsep}/usr/bin:/bin"
        env["STUB_LOG"] = str(log_path)
        r = subprocess.run(
            [BASH, str(SCRIPT)],
            capture_output=True, text=True, env=env,
            timeout=30,
        )
        log = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    return r, log


class TestStubSuccess(unittest.TestCase):
    """All `gh label create` calls succeed → exit 0."""

    def test_creates_complete_label_set_with_force(self):
        r, log = _run_with_stub("ok")
        self.assertEqual(r.returncode, 0,
                         f"stderr={r.stderr}\nstdout={r.stdout}")
        invocations = [l for l in log.splitlines() if l.startswith("label create")]
        self.assertEqual(len(invocations), 8,
                         f"expected 8 label invocations, got {len(invocations)}: {invocations}")
        for line in invocations:
            self.assertIn("--force", line.split(), f"missing --force: {line}")
        self.assertEqual({line.split()[2] for line in invocations}, {
            "P0", "P1", "P2",
            "size:S", "size:M", "size:L", "size:XL",
            "forge",
        })


class TestStubFailure(unittest.TestCase):
    """First `gh label create` failing aborts the script under set -e."""

    def test_propagates_non_zero_exit(self):
        r, log = _run_with_stub("fail")
        self.assertEqual(r.returncode, 4)
        self.assertEqual(len(log.splitlines()), 1, "label creation must stop at the first failure")


if __name__ == "__main__":
    unittest.main()
