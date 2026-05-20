"""Smoke test for `scripts/remote_stub.py` — the `--remote` flag's MVP redirect.

The stub must exit cleanly (so an orchestrator can chain it with `&&`)
and point the user at the phase-2 plan inline.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
STUB = REPO_ROOT / "skills" / "code-ultrareview" / "scripts" / "remote_stub.py"


class TestRemoteStub(unittest.TestCase):
    def test_exits_zero_with_documented_message(self):
        result = subprocess.run(
            [sys.executable, str(STUB)],
            capture_output=True,
            text=True,
            timeout=5,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("phase-2", result.stdout)
        self.assertIn("In-session Ultra", result.stdout)
        self.assertIn("remote-escalation-design.md", result.stdout)


if __name__ == "__main__":
    unittest.main()
