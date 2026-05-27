"""End-to-end tests for the PR-body internal-label scanner.

The script reads `{"title": ..., "body": ...}` JSON from stdin and exits
1 on a hit, 2 on JSON error. Driven via subprocess to pin the contract.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

_SCRIPT = (
    Path(__file__).resolve().parent / "scripts" / "scan_pr_for_internal_label.py"
)


def _run(payload: dict) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(_SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )


class TestScanPrForInternalLabel(unittest.TestCase):
    def test_clean_pr_exits_zero(self):
        result = _run(
            {"title": "feat(skills): add a thing", "body": "Does the thing."}
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_ws_label_in_title_exits_one(self):
        result = _run(
            {
                "title": "feat(code-ultrareview): WS-6 opt-in flag orchestration",
                "body": "",
            }
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("PR title", result.stderr)
        self.assertIn("WS-6", result.stderr)

    def test_leaky_phrase_in_body_exits_one(self):
        body = (
            "Line one is fine.\n"
            "Line two mentions the rebuild here.\n"
            "Line three is fine."
        )
        result = _run({"title": "clean title", "body": body})
        self.assertEqual(result.returncode, 1)
        self.assertIn("PR body:line 2", result.stderr)
        self.assertIn("the rebuild", result.stderr)

    def test_opt_out_marker_passes(self):
        body = (
            "the rebuild reference here <!-- noqa: internal-label -->\n"
            "clean line"
        )
        result = _run({"title": "clean", "body": body})
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_null_body_handled(self):
        # `gh pr view --json body` emits `"body": null` when the PR body is empty.
        result = _run({"title": "clean", "body": None})
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_missing_keys_handled(self):
        result = _run({})
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_invalid_json_exits_two(self):
        result = subprocess.run(
            [sys.executable, str(_SCRIPT)],
            input="not json{",
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid JSON", result.stderr)


if __name__ == "__main__":
    unittest.main()
