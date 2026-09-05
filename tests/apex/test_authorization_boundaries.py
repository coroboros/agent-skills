"""Authorization survives workflow entry; the latest explicit checkpoint wins."""

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2] / "skills" / "apex"


class TestAuthorizationBoundaries(unittest.TestCase):
    def test_initialization_preserves_conversation(self):
        text = (ROOT / "steps" / "step-00-init.md").read_text()
        self.assertNotIn("no previous context exists", text)
        self.assertIn("earlier conversation, authorization, corrections", text)

    def test_plan_checkpoint_honors_approval_and_latest_pause(self):
        text = (ROOT / "steps" / "step-02-plan.md").read_text()
        self.assertIn("already approved this plan", text)
        self.assertIn("latest user instruction requests a checkpoint", text)

    def test_evals_cover_both_authorization_directions(self):
        cases = json.loads((ROOT / "evals" / "evals.json").read_text())["evals"]
        self.assertEqual({case["name"] for case in cases}, {
            "inherit-approved-plan", "latest-explicit-checkpoint-wins",
            "dirty-worktree-criterion-closure",
        })
