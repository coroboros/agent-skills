"""award-design in-page detector — pure-core behavior via node.

The classifier boundaries ARE the product: the detector exists because a
:hover rule in the CSS was credited as alive while the page read dead. These
tests require() the asset in node and hold the color math, the transform
parsing, and every classifyDelta boundary to the floors — including the
fixture stylesheets' own literals, so the manual harness and the classifier
never drift apart."""

import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ASSET = REPO_ROOT / "skills" / "award-design" / "assets" / "detector.js"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "detector"


def _node(expr):
    """Evaluate one expression against the required asset; fail loud on stderr."""
    script = (
        f"const d = require({json.dumps(str(ASSET))});"
        f"console.log(JSON.stringify(({expr})));"
    )
    proc = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, timeout=30
    )
    if proc.returncode != 0:
        raise AssertionError(f"node -e failed:\n{proc.stderr}")
    return json.loads(proc.stdout.strip())


@unittest.skipUnless(shutil.which("node"), "node not on PATH")
class TestPureCore(unittest.TestCase):
    def test_module_exports(self):
        keys = _node("Object.keys(d)")
        for name in ("FLOORS", "RULES", "srgbToOklab", "relativeLuminance",
                     "contrastRatio", "parseTransform", "classifyDelta", "diffChannels"):
            self.assertIn(name, keys)

    def test_floors_values(self):
        self.assertEqual(
            {"scale": 1.04, "deltaL": 0.04, "translatePx": 2, "opacity": 0.1},
            _node("d.FLOORS"),
        )

    def test_srgb_to_oklab_known_values(self):
        self.assertAlmostEqual(_node("d.srgbToOklab(255,255,255).L"), 1.0, delta=0.01)
        self.assertAlmostEqual(_node("d.srgbToOklab(0,0,0).L"), 0.0, delta=0.01)
        # #808080 → OKLab L ≈ 0.5999 (published reference value).
        self.assertAlmostEqual(_node("d.srgbToOklab(128,128,128).L"), 0.5999, delta=0.01)

    def test_contrast_ratio(self):
        self.assertAlmostEqual(
            _node("d.contrastRatio([255,255,255],[0,0,0])"), 21.0, delta=0.05
        )
        self.assertAlmostEqual(
            _node("d.contrastRatio([128,128,128],[128,128,128])"), 1.0, delta=0.001
        )

    def test_parse_transform(self):
        scale = _node("d.parseTransform('matrix(1.05, 0, 0, 1.05, 0, 0)')")
        self.assertAlmostEqual(scale["scaleX"], 1.05, delta=0.001)
        self.assertAlmostEqual(scale["scaleY"], 1.05, delta=0.001)
        translate = _node("d.parseTransform('matrix(1, 0, 0, 1, 12, -8)')")
        self.assertEqual(translate["translateX"], 12)
        self.assertEqual(translate["translateY"], -8)


@unittest.skipUnless(shutil.which("node"), "node not on PATH")
class TestClassifyDeltaBoundaries(unittest.TestCase):
    """The floors are perceptibility thresholds — at the floor is felt, under
    it is homeopathic. A drift here re-opens the credited-as-alive failure."""

    def _classify(self, sample):
        return _node(f"d.classifyDelta({json.dumps(sample)})")

    def test_scale_boundary(self):
        base = {"hasStateRule": True, "hasAffordance": True}
        self.assertEqual("HOMEOPATHIC", self._classify({**base, "channels": {"scale": 1.039}}))
        self.assertEqual("OK", self._classify({**base, "channels": {"scale": 1.05}}))

    def test_delta_l_boundary(self):
        base = {"hasStateRule": True, "hasAffordance": True}
        self.assertEqual("HOMEOPATHIC", self._classify({**base, "channels": {"deltaL": 0.03}}))
        self.assertEqual("OK", self._classify({**base, "channels": {"deltaL": 0.06}}))

    def test_all_channels_under_floors(self):
        sample = {
            "hasStateRule": True, "hasAffordance": True,
            "channels": {"scale": 1.02, "deltaL": 0.02, "translatePx": 1, "opacity": 0.05},
        }
        self.assertEqual("HOMEOPATHIC", self._classify(sample))

    def test_zero_delta_affordance_routes_on_js(self):
        """No state rule and no delta: with JS on the page the element might be
        driven at tier 2 (UNMEASURED-JS); without JS nothing can drive it (DEAD)."""
        base = {"hasStateRule": False, "hasAffordance": True, "channels": {}}
        self.assertEqual("DEAD", self._classify({**base, "pageHasJs": False}))
        self.assertEqual("UNMEASURED-JS", self._classify({**base, "pageHasJs": True}))

    def test_non_interactive_skips(self):
        self.assertEqual(
            "SKIP",
            self._classify({"hasStateRule": False, "hasAffordance": False, "channels": {}}),
        )

    def test_unfloored_channel_is_perceptible(self):
        """Underline/outline/shadow changes have no floor — any change is OK."""
        sample = {"hasStateRule": True, "hasAffordance": True, "channels": {"discrete": 1}}
        self.assertEqual("OK", self._classify(sample))

    def test_diff_channels_feeds_classifier(self):
        expr = (
            "d.classifyDelta({hasStateRule: true, hasAffordance: true,"
            " channels: d.diffChannels("
            "{transform: 'none', color: 'rgb(47, 42, 38)', opacity: '1'},"
            "{transform: 'none', color: 'rgb(179, 71, 0)', opacity: '1'})})"
        )
        self.assertEqual("OK", _node(expr))


@unittest.skipUnless(shutil.which("node"), "node not on PATH")
class TestFixtureExpectations(unittest.TestCase):
    """The fixtures are the manual harness; their literals are also classifier
    expectations, so the pages and the floors cannot drift apart silently."""

    def test_dead_fixture_hover_is_homeopathic(self):
        css = (FIXTURES / "dead" / "styles.css").read_text(encoding="utf-8")
        match = re.search(r"a:hover\s*\{[^}]*scale\((1\.\d+)\)", css)
        self.assertIsNotNone(match, "dead fixture lost its scale-only hover")
        scale = float(match.group(1))
        sample = json.dumps(
            {"hasStateRule": True, "hasAffordance": True, "channels": {"scale": scale}}
        )
        self.assertEqual("HOMEOPATHIC", _node(f"d.classifyDelta({sample})"))

    def test_alive_fixture_lift_is_ok(self):
        css = (FIXTURES / "alive" / "styles.css").read_text(encoding="utf-8")
        match = re.search(r"a:hover\s*\{[^}]*translate:\s*0\s+-(\d+)px", css)
        self.assertIsNotNone(match, "alive fixture lost its hover lift")
        lift = int(match.group(1))
        sample = json.dumps(
            {"hasStateRule": True, "hasAffordance": True, "channels": {"translatePx": lift}}
        )
        self.assertEqual("OK", _node(f"d.classifyDelta({sample})"))

    def test_fixture_pages_exist(self):
        for name in ("dead", "alive"):
            with self.subTest(fixture=name):
                self.assertTrue((FIXTURES / name / "index.html").is_file())
                self.assertTrue((FIXTURES / name / "styles.css").is_file())
        self.assertTrue((FIXTURES / "README.md").is_file())


if __name__ == "__main__":
    unittest.main()
