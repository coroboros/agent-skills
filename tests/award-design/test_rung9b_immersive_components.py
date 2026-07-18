"""award-design completeness program — rung 9B (immersive cluster, second half,
the FINAL builder wave).

Four orders, one build. ambient-audio-score closed as an ALIAS onto the three
merged audio carriers — every winner the gap cites is already a carrier's cited
winner (Cartier's Mooders score is scored-scene-procession's primary citation;
Messenger and Bruno Simon are spatial-audio-world's; the scene-agnostic bed
register is sound-channel's contract clause for clause), and the one-carrier-
per-page partition written into spatial-audio-world's header assigns the seam.
playable-verb-scene closed as a COMPOSITION ruling — the gap's own text says
'worth a RECIPE slot... inherently hand-built, not a drop-in': the verb loop is
raycast-object-state + in-3d-dom-input-bridge + press-hold-reveal, taught by
idle-attract-auto-demo, routed to a recipes-authoring order (the rung-6
cinematic-pavilion-recipe precedent). in-scene-ambient-life was BUILT: the
engine-agnostic clock+gates+kinematics scheduler (populations are DATA fed to a
library init — the hand rAF loop a builder would otherwise write is
CW-RAF-LOOP), three deterministic modes (path/wander/drift, one per cited
register), no THREE across the boundary, no paint, no audio. Drive record:
alive at rest with zero input (0.7s: traffic +47.3px along the road path,
flutter +9.4/+22.1 curl, wind -23.1 drift), parked by IO off-screen (ticking
false, byte-identical frozen state over 700ms) and resumed continuing, ?rm a
composed non-zero t=0 still that never ticks (t=0, byte-identical over 800ms).

celestial-dive-skin-surface (the authorized EDIT) landed the boundary verdict's
three formalization orders (§3) on the WORKBENCH copy of the scene — the scene
lives outside this repo (award-workbench/reference-scenes/celestial-dive/), so
these tests reach it as a sibling checkout and SKIP loudly when absent (CI):
(i) unique SKIN markers around the parameter block, (ii) asset URLs lifted to
skin consts with zero URL literals below the closing marker (the BEFORE drive
proved the body-hardcoded './assets/moon/…' paths were a live defect — textures
FAILED in the harvested folder), (iii) scene-generic createDiveScene export
with createMoonScene kept as the backwards-compatible alias. Driven after the
edit: boot on the generic export with textures ready, the scrub through orbit
z=4.756 → crater z=1.268/fov 54 → glide → return z=14.958, and the pointer
channel answering markerScreen → hitTest → 'tranquillitatis' with seaProgress
0.22 = contactProgress."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
COMPONENTS = REPO_ROOT / "skills" / "award-design" / "assets" / "components"

# The one rung-9B build — file → exported global.
LIFE_FILE = "in-scene-ambient-life.js"
LIFE_GLOBAL = "awardInSceneAmbientLife"

# The authorized-edit target lives in the sibling workbench checkout, not in
# this repo — skip (never fail) when the checkout is absent.
DIVE_SCENE = (
    REPO_ROOT.parent
    / "award-workbench"
    / "reference-scenes"
    / "celestial-dive"
    / "celestial-dive-scene.js"
)

SKIN_OPEN = "// SKIN >>>"
SKIN_CLOSE = "// <<< SKIN"


def _life():
    return (COMPONENTS / LIFE_FILE).read_text(encoding="utf-8")


class TestRung9bLibraryContract(unittest.TestCase):
    """The structural floor every library component keeps (the
    test_component_library contract, applied before the manifest merge)."""

    def test_file_exists(self):
        self.assertTrue((COMPONENTS / LIFE_FILE).is_file())

    def test_iife_and_global_export(self):
        src = _life()
        self.assertIn("(function (global)", src)
        self.assertRegex(src, r"global\." + re.escape(LIFE_GLOBAL) + r"\s*=")

    def test_exposes_init_and_destroy(self):
        src = _life()
        self.assertIn("function init", src)
        self.assertIn("destroy", src)

    def test_has_reduced_motion_contract(self):
        self.assertIn("reduced-motion", _life())

    def test_has_doc_comment_header(self):
        self.assertTrue(_life().lstrip().startswith("/*"))

    def test_no_bare_100vh(self):
        self.assertNotRegex(_life(), r"100vh")


class TestInSceneAmbientLife(unittest.TestCase):
    """The between-input life scheduler: engine-agnostic, deterministic,
    gated — the scene paints, the library clocks."""

    def setUp(self):
        self.src = _life()

    def test_winner_evidence_in_header(self):
        for token in ("ERA", "Jordan Breton", "Messenger"):
            self.assertIn(token, self.src)

    def test_alias_rulings_in_header(self):
        """DISTINCT from the DOM idle channel and the live-peer channel — and
        the no-synthetic-peers law is restated, not inherited silently."""
        for token in ("ambient-idle", "living-presence-layer", "never faked"):
            self.assertIn(token, self.src)

    def test_closed_world_grounds_in_header(self):
        """Why this is library machinery at all: the hand loop is
        CW-RAF-LOOP; populations-as-DATA are legal composition."""
        self.assertIn("CW-RAF-LOOP", self.src)

    def test_no_engine_import_crosses_the_boundary(self):
        """The raycast-object-state seam: the scene owns rendering — the
        component never imports or touches an engine (statements, not the
        header prose that states this very law)."""
        self.assertNotRegex(self.src, re.compile(r"^\s*import\b", re.M))
        self.assertNotIn("require(", self.src)
        self.assertNotIn("new THREE.", self.src)
        self.assertNotIn("WebGLRenderer", self.src)

    def test_paints_nothing(self):
        """The nav-context-ink no-paint precedent: no stylesheet, no canvas,
        no style writes — the engine owns every pixel."""
        self.assertNotIn("createElement", self.src)
        self.assertNotRegex(self.src, r"\.style\b")

    def test_carries_no_audio(self):
        """The one-audio-carrier-per-page law stays untouched."""
        self.assertNotIn("AudioContext", self.src)

    def test_deterministic_no_math_random(self):
        """Seeded fract-sine hash only — the same populations compose the
        same world every load (the assembly-loader precedent)."""
        self.assertNotRegex(self.src, r"Math\.random\s*\(")
        self.assertIn("43758.5453", self.src)

    def test_three_modes_one_per_cited_register(self):
        for mode in ("'path'", "'wander'", "'drift'"):
            self.assertIn(mode, self.src)

    def test_path_mode_is_arc_length_parameterized(self):
        """ERA's cars ride at constant world speed — cumulative segment
        lengths, not per-segment time."""
        self.assertIn("buildPath", self.src)
        self.assertIn("samplePath", self.src)

    def test_gates_io_and_visibility(self):
        """The loop runs only on-screen and tab-visible — drive-verified
        parked off-screen with a byte-identical frozen state."""
        self.assertIn("IntersectionObserver", self.src)
        self.assertIn("visibilitychange", self.src)
        self.assertIn("cancelAnimationFrame", self.src)

    def test_reduce_is_a_composed_still(self):
        """Under reduce the loop NEVER starts — one t=0 pose, applied once
        (drive-verified: ticking=false, t=0, samples posed non-zero)."""
        self.assertIn("pose(inst, 0)", self.src)
        self.assertIn("prefers-reduced-motion", self.src)

    def test_getstate_is_the_drive_readout(self):
        """The 'is the world actually alive at rest' readout: ticking + the
        live agent-0 sample per population."""
        self.assertIn("getState", self.src)
        self.assertIn("ticking", self.src)
        self.assertIn("sample", self.src)

    def test_apply_is_required_per_population(self):
        """A population without an engine painter is dropped, never
        half-scheduled."""
        self.assertIn("typeof o.apply !== 'function'", self.src)


@unittest.skipUnless(
    DIVE_SCENE.is_file(),
    "award-workbench sibling checkout not present — the celestial-dive "
    "skin-surface contract is only checkable next to the workbench",
)
class TestCelestialDiveSkinSurface(unittest.TestCase):
    """The boundary verdict's three formalization orders (§3), made
    machine-decidable: unique markers, a URL-free machine body, and the
    generic export with its legacy alias."""

    @classmethod
    def setUpClass(cls):
        cls.src = DIVE_SCENE.read_text(encoding="utf-8")

    def test_skin_markers_present_and_unique(self):
        """Exactly one opener and one closer — the hash gate strips the block
        by grepping the literals, so prose must never repeat them."""
        self.assertEqual(self.src.count(SKIN_OPEN), 1)
        self.assertEqual(self.src.count(SKIN_CLOSE), 1)
        self.assertLess(self.src.index(SKIN_OPEN), self.src.index(SKIN_CLOSE))

    def test_no_asset_url_below_the_skin_block(self):
        """Verdict §3.2: re-pointing textures never touches the machine —
        zero image/asset literals after the closing marker."""
        body = self.src.split(SKIN_CLOSE, 1)[1]
        self.assertNotRegex(body, r"assets/")
        self.assertNotRegex(body, r"\.(jpe?g|png|webp|ktx2|glb)\b")

    def test_asset_urls_live_in_the_skin_block(self):
        skin = self.src.split(SKIN_OPEN, 1)[1].split(SKIN_CLOSE, 1)[0]
        for const in ("ASSET_COLOR_2K", "ASSET_COLOR_4K", "ASSET_COLOR_8K",
                      "ASSET_DISP_2K", "ASSET_DISP_4K"):
            self.assertIn(const, skin)

    def test_generic_export_with_legacy_alias(self):
        """Verdict §3.3: scene-generic naming, celestial identity in the
        skin — and the old name keeps working."""
        self.assertIn("export function createDiveScene", self.src)
        self.assertIn("export const createMoonScene = createDiveScene", self.src)

    def test_moon_identifier_maria_is_gone(self):
        """The verdict's named residual: MARIA renamed to the generic
        FEATURES (its keys stay — they are the marker-id API surface)."""
        self.assertNotIn("MARIA", self.src)
        self.assertIn("const FEATURES", self.src)

    def test_api_surface_preserved(self):
        """The formalization never touches the contract the campaign's
        builds drive against."""
        for member in ("setProgress", "setPointer", "hitTest", "paintMarker",
                       "markerScreen", "seaProgress", "ready", "start",
                       "resize", "dispose"):
            self.assertIn(member, self.src)

    def test_skin_block_carries_the_parameter_surface(self):
        """Tokens, triggers, feature slots and the motion curves all sit
        inside the markers — the re-skin surface is one contiguous block."""
        skin = self.src.split(SKIN_OPEN, 1)[1].split(SKIN_CLOSE, 1)[0]
        for const in ("const TOKENS", "const TRIGGER", "const FEATURES",
                      "const EASE_SIGNATURE", "const EASE_GLIDE"):
            self.assertIn(const, skin)


if __name__ == "__main__":
    unittest.main()
