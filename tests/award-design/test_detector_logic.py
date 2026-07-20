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
                     "contrastRatio", "parseTransform", "classifyDelta", "diffChannels",
                     "classifyContact", "classifyNavHero", "peakChannels"):
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
class TestPeakHold(unittest.TestCase):
    """A press transient peaks then settles; a post-settle read measures zero.
    The peak fold keeps the crest of every channel across sampled frames — the
    140ms spring that shipped unmeasured is caught at its crest."""

    def test_fold_keeps_the_crest_of_a_settling_transient(self):
        # per-frame diffs against rest for a press spring: rise, crest, settle
        frames = [
            {"scale": 1.0, "translatePx": 0, "deltaL": 0, "opacity": 0, "discrete": 0},
            {"scale": 1.055, "translatePx": 0, "deltaL": 0, "opacity": 0.3, "discrete": 0},
            {"scale": 1.02, "translatePx": 3, "deltaL": 0.05, "opacity": 0.1, "discrete": 0},
            {"scale": 1.0, "translatePx": 0, "deltaL": 0, "opacity": 0, "discrete": 0},
        ]
        expr = f"{json.dumps(frames)}.reduce((acc, f) => d.peakChannels(acc, f), null)"
        peak = _node(expr)
        self.assertAlmostEqual(1.055, peak["scale"], delta=1e-9)
        self.assertEqual(3, peak["translatePx"])
        self.assertAlmostEqual(0.05, peak["deltaL"], delta=1e-9)
        self.assertAlmostEqual(0.3, peak["opacity"], delta=1e-9)

    def test_discrete_maxes_across_frames(self):
        """Every frame diffs against the same rest, so a persistent structural
        change is one delta — summing would count it once per frame."""
        frame = {"scale": 1.0, "translatePx": 0, "deltaL": 0, "opacity": 0, "discrete": 1}
        expr = f"{json.dumps([frame] * 3)}.reduce((acc, f) => d.peakChannels(acc, f), null)"
        self.assertEqual(1, _node(expr)["discrete"])


@unittest.skipUnless(shutil.which("node"), "node not on PATH")
class TestClassifyContact(unittest.TestCase):
    """The paper-cutout boundary: a struck object whose only above-floor
    response is a whole-element scale/opacity is the squash; any secondary or
    any structural channel above a floor is a local response and stays
    judgment."""

    def _classify(self, object_ch, secondaries):
        return _node(f"d.classifyContact({json.dumps(object_ch)}, {json.dumps(secondaries)})")

    def test_uniform_scale_only_is_the_squash(self):
        # the shipped failure: scale(1.055, 0.968) on the whole element
        self.assertEqual("GLOBAL-SQUASH", self._classify({"scale": 1.055}, []))

    def test_opacity_only_is_the_squash(self):
        self.assertEqual("GLOBAL-SQUASH", self._classify({"opacity": 0.2}, [{}]))

    def test_secondary_above_floor_is_local(self):
        self.assertEqual("LOCAL", self._classify({"scale": 1.055}, [{"translatePx": 4}]))

    def test_structural_channel_on_object_is_local(self):
        # a clip-path/shadow/pseudo change is deformation, not the rigid squash
        self.assertEqual("LOCAL", self._classify({"scale": 1.055, "discrete": 1}, []))

    def test_under_floor_response_is_none(self):
        self.assertEqual(
            "NONE", self._classify({"scale": 1.02, "opacity": 0.05}, [{"translatePx": 1}]))


@unittest.skipUnless(shutil.which("node"), "node not on PATH")
class TestClassifyNavHero(unittest.TestCase):
    """The decapitation boundary: at rest, a top bar over hero media. Transparent
    or a to-transparent scrim is the winner norm; an opaque unblurred band off the
    page ground is the FAIL that shipped over ARDEN's photo; frost-with-blur,
    translucent, or an opaque same-ground bar (Cyd's always-solid cream) is judged
    in §8. FAIL fires only on proof — a resolvable solid colour off the ground."""

    def _classify(self, sample):
        return _node(f"d.classifyNavHero({json.dumps(sample)})")

    def test_opaque_off_ground_over_media_is_fail(self):
        # the ARDEN bone strip: opaque, no blur, surface far off the page ground
        self.assertEqual("FAIL", self._classify(
            {"hasMediaUnder": True, "isScrim": False, "alpha": 1,
             "hasBackdropFilter": False, "groundDeltaL": 0.2}))

    def test_transparent_over_hero_is_exempt(self):
        # show-on-scroll-up-nav at rest — the winner norm
        self.assertEqual("EXEMPT", self._classify(
            {"hasMediaUnder": True, "alpha": 0, "hasBackdropFilter": False, "groundDeltaL": 0}))

    def test_gradient_scrim_is_exempt(self):
        self.assertEqual("EXEMPT", self._classify(
            {"hasMediaUnder": True, "isScrim": True, "alpha": 0.6, "groundDeltaL": 0.3}))

    def test_no_media_under_bar_is_exempt(self):
        # text-only hero, or "a page with no hero forces the solid state"
        self.assertEqual("EXEMPT", self._classify(
            {"hasMediaUnder": False, "alpha": 1, "hasBackdropFilter": False, "groundDeltaL": 0.3}))

    def test_frost_with_blur_is_review(self):
        # Terminal's glass pill — winner-normal, judged not failed
        self.assertEqual("REVIEW", self._classify(
            {"hasMediaUnder": True, "alpha": 0.8, "hasBackdropFilter": True, "groundDeltaL": 0.2}))

    def test_opaque_same_ground_is_review(self):
        # Cyd's always-solid cream bar — winner-cited, judged against the canon
        self.assertEqual("REVIEW", self._classify(
            {"hasMediaUnder": True, "alpha": 1, "hasBackdropFilter": False, "groundDeltaL": 0.02}))

    def test_translucent_unblurred_is_review(self):
        self.assertEqual("REVIEW", self._classify(
            {"hasMediaUnder": True, "alpha": 0.5, "hasBackdropFilter": False, "groundDeltaL": 0.2}))


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
