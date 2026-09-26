"""Pixel-metric color, raster, and scroll-corrected motion calculations."""

import json
import shutil
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ASSET = REPO_ROOT / "skills" / "award-design" / "assets" / "pixel-metrics.js"

def _node(expr):
    """Evaluate one expression against the required asset; fail loud on stderr."""
    script = (
        f"const pm = require({json.dumps(str(ASSET))});"
        f"console.log(JSON.stringify(({expr})));"
    )
    proc = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=30)
    if proc.returncode != 0:
        raise AssertionError(f"node -e failed:\n{proc.stderr}")
    return json.loads(proc.stdout.strip())


@unittest.skipUnless(shutil.which("node"), "node not on PATH")
class TestColorCore(unittest.TestCase):
    """Accent matching and ground commitment both turn on OKLab distance, so the
    conversion and the parser are load-bearing: a colour the parser drops is an
    accent occurrence the evidence never counts."""

    def test_srgb_to_oklab_known_values(self):
        self.assertAlmostEqual(_node("pm.srgbToOklab(255,255,255).L"), 1.0, delta=0.01)
        self.assertAlmostEqual(_node("pm.srgbToOklab(0,0,0).L"), 0.0, delta=0.01)
        self.assertAlmostEqual(_node("pm.srgbToOklab(128,128,128).L"), 0.5999, delta=0.01)

    def test_parses_the_families_chrome_serializes(self):
        self.assertAlmostEqual(_node("pm.parseColor('rgba(10, 20, 30, 0.5)').alpha"), 0.5, delta=1e-9)
        self.assertAlmostEqual(_node("pm.parseColor('oklch(0.7 0.15 30)').lab.L"), 0.7, delta=1e-9)
        self.assertAlmostEqual(_node("pm.parseColor('#b3470080').alpha"), 128 / 255, delta=0.01)
        self.assertEqual(0, _node("pm.parseColor('transparent').alpha"))

    def test_unparsable_color_is_null_not_a_guess(self):
        self.assertIsNone(_node("pm.parseColor('var(--accent)')"))
        self.assertIsNone(_node("pm.parseColor('currentcolor')"))

    def test_a_repaint_of_the_same_token_stays_inside_the_accent_tolerance(self):
        """Rounding between an authored token and its computed serialization must
        not split one accent into two."""
        expr = "pm.oklabDistance(pm.srgbToOklab(179,71,0), pm.srgbToOklab(180,72,1))"
        self.assertLess(_node(expr), _node("pm.ACCENT.oklabTol"))

    def test_two_different_hues_are_outside_it(self):
        expr = "pm.oklabDistance(pm.srgbToOklab(179,71,0), pm.srgbToOklab(0,90,200))"
        self.assertGreater(_node(expr), _node("pm.ACCENT.oklabTol"))

    def test_grey_has_no_chroma(self):
        self.assertLess(_node("pm.chroma(pm.srgbToOklab(128,128,128))"), 0.01)
        self.assertGreater(_node("pm.chroma(pm.srgbToOklab(179,71,0))"), 0.05)

    def test_one_ground_authored_two_ways_merges_into_one_share(self):
        """Chrome serializes an oklch()-authored ground as oklch(...) and a
        hex-authored one as rgb(...). Keyed on the string alone, a token system
        that mixes both splits its ground in two and halves the headline share
        the judge reads — the number that separates 84.7% from 26.7%."""
        expr = (
            "pm.mergeByColor(["
            "{color:'rgb(20, 22, 26)', lab: pm.srgbToOklab(20,22,26), area: 6000, elements: 3},"
            "{color:'oklch(0.21 0.01 265)', lab: pm.srgbToOklab(21,23,27), area: 4000, elements: 2},"
            "{color:'rgb(179, 71, 0)', lab: pm.srgbToOklab(179,71,0), area: 500, elements: 4}"
            "])"
        )
        merged = _node(expr)
        self.assertEqual(2, len(merged))
        self.assertEqual(10000, merged[0]["area"])
        self.assertEqual(5, merged[0]["elements"])
        self.assertEqual(["oklch(0.21 0.01 265)"], merged[0]["aliases"])

    def test_merge_keeps_genuinely_different_grounds_apart(self):
        expr = (
            "pm.mergeByColor(["
            "{color:'rgb(20, 22, 26)', lab: pm.srgbToOklab(20,22,26), area: 6000, elements: 1},"
            "{color:'rgb(240, 238, 232)', lab: pm.srgbToOklab(240,238,232), area: 5000, elements: 1}"
            "])"
        )
        self.assertEqual(2, len(_node(expr)))


@unittest.skipUnless(shutil.which("node"), "node not on PATH")
class TestRaster(unittest.TestCase):
    """quadrantEmptiness and inkProfile are two readings of one occupancy grid —
    the empty-cell count and the flat-metronome profile both come from here."""

    BOX = {"left": 0, "top": 0, "w": 100, "h": 100}

    def _cells(self, rects, cols=10, rows=10):
        return _node(f"Array.from(pm.rasterize({json.dumps(rects)}, {json.dumps(self.BOX)}, {cols}, {rows}))")

    def _coverage(self, rects, r0, r1, c0, c1):
        expr = (f"pm.blockCoverage(pm.rasterize({json.dumps(rects)}, {json.dumps(self.BOX)}, 10, 10),"
                f" 10, {r0}, {r1}, {c0}, {c1})")
        return _node(expr)

    def test_empty_page_covers_nothing(self):
        self.assertEqual(0, sum(self._cells([])))

    def test_quadrant_block_reads_its_own_corner(self):
        top_left = [{"left": 0, "top": 0, "width": 50, "height": 50}]
        self.assertEqual(1.0, self._coverage(top_left, 0, 5, 0, 5))
        self.assertEqual(0.0, self._coverage(top_left, 5, 10, 5, 10))

    def test_rects_outside_the_document_box_are_clipped_not_wrapped(self):
        """A negative-offset decoration must not paint ink into the first band."""
        self.assertEqual(0, sum(self._cells([{"left": -500, "top": -500, "width": 100, "height": 100}])))

    def test_a_hairline_fills_the_cell_it_crosses(self):
        """Occupancy, not painted alpha — the honest limit stated in the header."""
        self.assertEqual(1.0, self._coverage([{"left": 0, "top": 0, "width": 1, "height": 100}], 0, 10, 0, 1))

    def test_distribution_orders_the_band_profile(self):
        dist = _node("pm.distribution([0.151, 0.082, 0.11, 0.09, 0.13])")
        self.assertAlmostEqual(0.082, dist["min"], delta=1e-9)
        self.assertAlmostEqual(0.151, dist["max"], delta=1e-9)
        self.assertAlmostEqual(0.11, dist["median"], delta=1e-9)

    def test_distribution_of_nothing_is_null_not_zero(self):
        self.assertIsNone(_node("pm.distribution([])"))


@unittest.skipUnless(shutil.which("node"), "node not on PATH")
class TestMotionProxy(unittest.TestCase):
    """The scroll correction is the whole instrument: without it every element
    on the page "moves" the moment the page scrolls, and the metric says nothing."""

    REST = {"x": 0, "y": 400, "w": 200, "h": 100, "transform": "none", "opacity": "1"}

    def _delta(self, after, shift):
        return _node(f"pm.delta({json.dumps(self.REST)}, {json.dumps(after)}, {shift})")

    def test_a_static_element_under_a_scroll_step_has_not_moved(self):
        after = dict(self.REST, y=100)
        self.assertFalse(self._delta(after, 300)["moved"])

    def test_an_element_moving_against_the_page_is_caught(self):
        # parallax: the page moved 300px, this moved 260
        after = dict(self.REST, y=140)
        result = self._delta(after, 300)
        self.assertTrue(result["moved"])
        self.assertEqual(40, result["dy"])

    def test_an_opacity_shift_at_rest_counts(self):
        self.assertTrue(self._delta(dict(self.REST, opacity="0.4"), 0)["moved"])

    def test_a_transform_change_counts_even_when_the_rect_holds(self):
        """A rotation leaves the bounding box where it was; the matrix does not."""
        after = dict(self.REST, transform="matrix(0.99, 0.14, -0.14, 0.99, 0, 0)")
        self.assertTrue(self._delta(after, 0)["moved"])

    def test_subpixel_jitter_is_not_motion(self):
        self.assertFalse(self._delta(dict(self.REST, y=400.2), 0)["moved"])


if __name__ == "__main__":
    unittest.main()
