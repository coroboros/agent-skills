"""Execute published recipes under explicit DOM/library stubs; no GPU/browser claim."""

import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NODE = shutil.which("node")
HARNESS = Path(__file__).parent / "fixtures/animation-lifecycles.cjs"


@unittest.skipUnless(NODE, "Node.js is required to execute the published JavaScript examples")
class TestAnimationLifecycles(unittest.TestCase):
    def check_recipe(self, case):
        result = subprocess.run(
            [NODE, str(HARNESS), case, str(ROOT / "skills/award-design/references")],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_io_reveals_fail_visible_and_preserve_already_visible_content(self):
        self.check_recipe("reveal")

    def test_splittext_respects_preference_and_restores_markup(self):
        self.check_recipe("split")

    def test_three_poster_readiness_failure_visibility_and_cleanup(self):
        self.check_recipe("three")

    def test_fiber_activity_ands_viewport_visibility_and_motion(self):
        self.check_recipe("fiber")

    def test_cinematic_scroll_requires_input_and_remains_interruptible(self):
        self.check_recipe("cinematic")
