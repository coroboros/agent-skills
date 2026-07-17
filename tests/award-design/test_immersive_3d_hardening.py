"""award-design — the immersive/3D signature hardening (the seven axes).

The NOIRE test exposed the weakest path: the WebGL delegation guaranteed a scene,
not a good one. A primitive amber flacon shipped as "noire", the drag fired the
browser's native drag-ghost, the hit-area was on the title, the CTA was a
saturated slab. These lock the fixes:
  1 fidelity governs the medium (real media can beat a primitive 3D),
  2 a 3D material/lighting fidelity floor,
  3 an interactive input-correctness floor,
  4 "sourced" is not "used well",
  5 R2 judges the signature's execution as a real user,
  6 the signature serves the identity, never bends it,
  7 a register-appropriate CTA (no saturated slab on a refined page).

Each assertion would FAIL before this hardening."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFS = SKILL_DIR / "references"


def _read(rel):
    return (REFS / rel).read_text(encoding="utf-8")


def _body():
    return SKILL_MD.read_text(encoding="utf-8")


def _phase(n):
    m = re.search(rf"^## Phase {n} — .*?\n(.*?)(?=^## )", _body(), re.DOTALL | re.MULTILINE)
    assert m is not None, f"## Phase {n} section missing"
    return m.group(1)


def _review_mode():
    m = re.search(r"^## Review mode.*?(?=^## )", _body(), re.DOTALL | re.MULTILINE)
    assert m is not None, "Review mode section missing"
    return m.group(0)


class TestAxis1FidelityRouting(unittest.TestCase):
    def test_signature_invention_routes_by_fidelity(self):
        sig = _read("signature-invention.md").lower()
        self.assertIn("fidelity governs the medium", sig)
        self.assertIn("scroll-scrubbed real video", sig)
        self.assertIn("silhouette test", sig, "the imagery silhouette test is wired onto 3D")

    def test_immersive_ref_routes_by_fidelity(self):
        imm = _read("immersive-cinematic.md").lower()
        self.assertIn("fidelity governs the medium", imm)
        self.assertIn("scrubbed real", imm)

    def test_phase3_commits_the_medium_by_fidelity(self):
        p3 = _phase(3).lower()
        self.assertIn("chosen for fidelity", p3)
        self.assertIn("scroll-scrubbed real video", p3)


class TestAxis2FidelityFloor(unittest.TestCase):
    def setUp(self):
        self.web3d = _read("ingredients/web3d-for-sites.md")
        self.low = self.web3d.lower()

    def test_material_and_lighting_floor(self):
        self.assertIn("fidelity floor", self.low)
        self.assertIn("meshphysicalmaterial", self.low)
        self.assertTrue("hdri" in self.low or "<environment>" in self.low,
                        "the render is lit by an HDRI environment, not flat point lights")

    def test_no_primitive_hero_object(self):
        self.assertIn("no primitive geometry as the hero object", self.low)
        self.assertIn("silhouette test", self.low)

    def test_preflight_gates_used_well(self):
        pf = _read("preflight.md").lower()
        self.assertTrue("physical material" in pf and "hdri" in pf,
                        "preflight §7 must gate the WebGL scene's material + HDRI fidelity")

    def test_two_tier_streaming_hold_gate(self):
        self.assertIn("two-tier texture streaming", self.low)
        for token in ("hold-gate", "inittexture", "requestidlecallback",
                      "min(progress", "loadingmanager"):
            with self.subTest(token=token):
                self.assertIn(token, self.low)
        self.assertIn("the scroll waits for fidelity", self.low)

    def test_streaming_verify_probes_the_compositor(self):
        self.assertIn("preservedrawingbuffer", self.low)
        self.assertIn("compositor", self.low)


class TestSequenceFidelityFloor(unittest.TestCase):
    """CALDERA postmortem: 62 frames baked from 4 stills at 1280x720, cover-drawn on
    2880x1800 device px. Corpus-measured floor (r4 medium-floor verdict): winners ship
    distinct real frames at >= device pixels on the signature surface; the one 2x
    upscale ever measured scored 7.3, the SOTD floor; synthetic in-betweens from
    stills have zero precedent."""

    def test_imagery_carries_the_floor(self):
        img = _read("imagery.md")
        self.assertIn("## Native resolution or nothing", img)
        self.assertIn("delivered pixels ≥ device pixels", img)
        self.assertIn("zero winner precedent", img)
        self.assertIn("animate the full-resolution still live", img)
        self.assertIn("Treatment never buys back resolution", img)

    def test_preflight_asset_fidelity_box(self):
        pf = _read("preflight.md")
        self.assertIn("**Asset fidelity — measured, one row per signature asset**", pf)
        self.assertIn("rendered device px at the worst moment", pf)

    def test_phase1_wires_floor_and_source_clause(self):
        p1 = _phase(1)
        self.assertIn("sequence-fidelity floor", p1)
        self.assertIn("constrains SOURCES, never the engine", p1)

    def test_immersive_playbook_carries_the_floor(self):
        import json
        pb = SKILL_DIR / "assets" / "components" / "playbooks" / "immersive.json"
        d = json.loads(pb.read_text(encoding="utf-8"))
        self.assertGreaterEqual(d["revision"], 3)
        hero = d["spectacle_model"]["hero"]
        self.assertIn("sequence-fidelity floor", hero)
        self.assertIn("ZERO winner precedent", hero)


class TestAxis3InputCorrectness(unittest.TestCase):
    def setUp(self):
        self.web3d = _read("ingredients/web3d-for-sites.md").lower()

    def test_input_floor_section(self):
        self.assertIn("input-correctness floor", self.web3d)
        for token in ('draggable="false"', "user-select: none", "touch-action: none"):
            with self.subTest(token=token):
                self.assertIn(token, self.web3d)

    def test_native_drag_ghost_named(self):
        self.assertTrue("native ghost" in self.web3d or "native drag" in self.web3d,
                        "the native drag-ghost bug must be named")

    def test_hit_area_and_affordance(self):
        self.assertIn("hit-area is the object", self.web3d)
        self.assertIn("grab-hand", self.web3d, "the native grab-hand cursor is called out")

    def test_anti_patterns_carry_the_tells(self):
        ap = _read("anti-patterns.md").lower()
        self.assertIn("draggable poster", ap)
        self.assertIn("native drag-ghost", ap)
        self.assertTrue("grab-hand cursor" in ap or "cursor: grab" in ap)

    def test_preflight_drives_a_real_drag(self):
        pf = _read("preflight.md").lower()
        self.assertIn("interactive signature driven as a real user", pf)
        self.assertIn("real mouse drag", pf)

    def test_phase4_loop_drives_a_real_drag(self):
        self.assertIn("real mouse drag", _phase(4).lower())


class TestAxis4SourcedNotUsedWell(unittest.TestCase):
    def test_web3d_names_the_gap(self):
        w = _read("ingredients/web3d-for-sites.md").lower()
        self.assertTrue("using the medium well" in w or "used the medium well" in w
                        or "using it well" in w or "low-effort" in w)

    def test_phase3_says_sourcing_is_not_using_well(self):
        self.assertIn("not using it well", _phase(3).lower())


class TestAxis5ExecutionReview(unittest.TestCase):
    def test_r2_drives_signature_as_real_user(self):
        r = _review_mode().lower()
        self.assertIn("drive the signature as a real user", r)
        self.assertIn("reads cheap", r)

    def test_imperative_one_execution_fidelity(self):
        imp = _read("award-imperatives.md").lower()
        self.assertIn("execution fidelity", imp)


class TestAxis6SignatureServesIdentity(unittest.TestCase):
    def test_signature_invention_identity_gate(self):
        sig = _read("signature-invention.md").lower()
        self.assertIn("serves the identity, never the reverse", sig)
        self.assertIn("non-negotiable attribute", sig)

    def test_r2_checks_the_identity(self):
        self.assertIn("non-negotiable attribute", _review_mode().lower())

    def test_imperative_one_identity(self):
        self.assertIn("serves the identity", _read("award-imperatives.md").lower())


class TestAxis7RegisterCTA(unittest.TestCase):
    def test_premium_patterns_register_fill(self):
        pp = _read("premium-patterns.md").lower()
        self.assertIn("register-appropriate fill", pp)
        self.assertIn("saturated", pp)

    def test_anti_pattern_saturated_slab(self):
        ap = _read("anti-patterns.md").lower()
        self.assertIn("saturated color-block cta", ap)


if __name__ == "__main__":
    unittest.main()
