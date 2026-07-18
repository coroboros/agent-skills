"""Closure pass — the orchestrator-scope orders that ended the completeness
program: the visibilitychange defect fix across all three audio carriers, and
the two composition recipes the rulings ordered (cinematic-pavilion,
playable-verb). Every referenced id must resolve to a shipped library piece —
the closed-world law applied to the recipe layer itself."""

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
COMPONENTS = REPO_ROOT / "skills" / "award-design" / "assets" / "components"

AUDIO_CARRIERS = ("sound-channel.js", "scored-scene-procession.js", "spatial-audio-world.js")
CLOSURE_RECIPES = ("cinematic-pavilion-cartier", "playable-verb-bruno")


class TestAudioCarriersPauseHidden(unittest.TestCase):
    """The rung-9B residual: the pause-on-visibilitychange clause existed only
    in spatial-audio-world. All three carriers now suspend on a hidden tab and
    resume only a still-ON channel."""

    def test_every_carrier_handles_visibilitychange(self):
        for name in AUDIO_CARRIERS:
            src = (COMPONENTS / name).read_text(encoding="utf-8")
            with self.subTest(carrier=name):
                self.assertIn("visibilitychange", src)
                self.assertIn("document.hidden", src)
                self.assertIn("suspend()", src)

    def test_resume_is_gated_on_the_on_state(self):
        for name in ("sound-channel.js", "scored-scene-procession.js"):
            src = (COMPONENTS / name).read_text(encoding="utf-8")
            with self.subTest(carrier=name):
                self.assertRegex(src, r"else if \((?:audio\.)?on && (?:audio\.)?ctx\.state === 'suspended'\)")

    def test_listeners_are_removed_on_destroy(self):
        for name in ("sound-channel.js", "scored-scene-procession.js"):
            src = (COMPONENTS / name).read_text(encoding="utf-8")
            with self.subTest(carrier=name):
                self.assertIn("removeEventListener('visibilitychange', onVis)", src)


class TestClosureRecipes(unittest.TestCase):
    """The two composition recipes ordered by the rung-6B pavilion note and
    the rung-9B playable-verb ruling."""

    @classmethod
    def setUpClass(cls):
        raw = json.loads((COMPONENTS / "recipes.json").read_text(encoding="utf-8"))
        cls.recipes = {r["id"]: r for r in (raw if isinstance(raw, list) else raw["recipes"])}
        manifest = json.loads((COMPONENTS / "manifest.json").read_text(encoding="utf-8"))
        cls.known = ({c["id"] for c in manifest["components"]}
                     | {f["id"] for f in manifest["forms"]})

    def test_both_recipes_exist(self):
        for rid in CLOSURE_RECIPES:
            with self.subTest(recipe=rid):
                self.assertIn(rid, self.recipes)

    def test_every_pair_value_is_a_shipped_library_id(self):
        for rid in CLOSURE_RECIPES:
            for section in self.recipes[rid]["sections"]:
                for slot, comp in section["pairs"].items():
                    with self.subTest(recipe=rid, slot=slot, component=comp):
                        self.assertIn(comp, self.known)

    def test_the_climax_composes_the_ruled_pieces(self):
        playable = self.recipes["playable-verb-bruno"]
        climax = next(s for s in playable["sections"] if s.get("climax"))
        for piece in ("raycast-object-state", "in-3d-dom-input-bridge", "press-hold-reveal"):
            self.assertIn(piece, climax["pairs"].values())

    def test_closed_world_clause_stated(self):
        for rid in CLOSURE_RECIPES:
            with self.subTest(recipe=rid):
                self.assertIn("closed-world", self.recipes[rid]["paceNotes"])


if __name__ == "__main__":
    unittest.main()
