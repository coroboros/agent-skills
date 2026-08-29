"""award-design — the moving-window flicker law (HALDANE UAT). A pointer-tracked
loupe shipped `clip-path: circle(at var())` + `transform-origin: var()` chased per
pointermove over a 2.1x-scaled raster with no layer promotion: the compositor
presented last-good raster under fresh geometry — bright content popping stale
positions on the user's screen recording — and the copy-block clamp teleported its
target, making the lerp lunge. The adversarial pass confirmed the paint-lag
diagnosis, scoped the law to per-frame-TRACKED windows over transformed content
(fire-once reveals and 1:1 comparison wipes correctly use animated clip), corrected
the overstated "clip-path is off-main-thread" line, and picked the performance
trace over screenshots as the only driven form that can prove no-pop."""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REFS = REPO_ROOT / "skills" / "award-design" / "references"


def _read(rel):
    return (REFS / rel).read_text(encoding="utf-8").lower()


class TestMovingWindowLaw(unittest.TestCase):
    def test_the_law(self):
        mp = _read("motion-palette.md")
        self.assertIn("## moving windows — compositor-clean tracking", mp)
        self.assertIn("the clip is static", mp)
        self.assertIn("continuous eased trajectory", mp)
        self.assertIn("smooth input, popping output", mp)

    def test_scope_exempts_fire_once(self):
        mp = _read("motion-palette.md")
        self.assertIn("per-frame-tracked windows over transformed content only", mp)
        self.assertIn("never translate-rig those", mp)

    def test_off_main_thread_claim_corrected(self):
        mp = _read("motion-palette.md")
        self.assertIn(
            "only when the clip's parameters are not tracked per input frame", mp)

    def test_fixed_background_corollary(self):
        self.assertIn("never `background-attachment: fixed`",
                      _read("motion-palette.md"))


class TestDrivenTraceBox(unittest.TestCase):
    # the dedicated preflight box died in the floor rewrite; the driven-trace
    # law survives in the motion-palette canon
    def test_compositor_clean_trace_law(self):
        mp = _read("motion-palette.md")
        self.assertIn("verified compositor-clean at verify with a performance trace", mp)
        self.assertIn("zero per-frame paint/raster", mp)

    def test_screenshots_cannot_prove_no_pop(self):
        self.assertIn(
            "screenshots cannot prove the absence of a pop",
            _read("motion-palette.md"))


if __name__ == "__main__":
    unittest.main()
