"""Closure pass — the orchestrator-scope orders that ended the completeness
program: the visibilitychange defect fix across all three audio carriers, and
the two compositions the rulings ordered (cinematic-pavilion, playable-verb),
now carried in the two archetypes' tier-2 Anatomy. Every referenced id must
resolve to a shipped library piece — the closed-world law applied to the
composition layer itself."""

import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
COMPONENTS = REPO_ROOT / "skills" / "award-design" / "assets" / "components"

AUDIO_CARRIERS = ("sound-channel.js", "scored-scene-procession.js", "spatial-audio-world.js")
CATALOG_SLUGS = ("argument-scroll", "maison-scroll", "specimen-tour", "capability-grid",
                 "standfirst-stack", "studio-reel", "gallery-stack", "studio-index",
                 "type-index", "gated-reel", "portrait-procession", "chapter-world",
                 "engine-world", "scene-scroll", "rooms-procession")


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


class TestClosureCompositions(unittest.TestCase):
    """The two compositions ordered by the rung-6B pavilion note and the rung-9B
    playable-verb ruling. They lived in `recipes.json` as recipe rows; the
    two-tier restructure merged them into the two archetypes' tier-2 Anatomy,
    which is what the design_plan commit loads. The closed-world law follows
    them: every id the prose names still has to be a shipped library piece."""

    CLOSURE_ARCHETYPES = {"experimental": "playable-verb", "corporate-luxury": "cinematic-pavilion"}

    @classmethod
    def setUpClass(cls):
        manifest = json.loads((COMPONENTS / "manifest.json").read_text(encoding="utf-8"))
        cls.known = ({c["id"] for c in manifest["components"]}
                     | {f["id"] for f in manifest["forms"]})
        cls.refs = REPO_ROOT / "skills" / "award-design" / "references"

    def _anatomy(self, archetype):
        body = (self.refs / f"{archetype}.md").read_text(encoding="utf-8")
        return body[body.index("**Anatomy**"):body.index("**Hero architectures**")]

    def test_the_playable_verb_climax_composes_the_ruled_pieces(self):
        anatomy = self._anatomy("experimental")
        for piece in ("raycast-object-state", "in-3d-dom-input-bridge", "press-hold-reveal",
                      "idle-attract-auto-demo", "spatial-audio-world", "in-scene-ambient-life"):
            with self.subTest(component=piece):
                self.assertIn(f"`{piece}`", anatomy)

    def test_the_pavilion_procession_composes_the_ruled_pieces(self):
        anatomy = self._anatomy("corporate-luxury")
        for piece in ("rooms-procession", "scored-scene-procession", "pinned-media-stepthrough"):
            with self.subTest(component=piece):
                self.assertIn(f"`{piece}`", anatomy)

    def test_every_named_id_is_a_shipped_library_piece(self):
        for archetype in self.CLOSURE_ARCHETYPES:
            anatomy = self._anatomy(archetype)
            for cid in re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`", anatomy):
                if cid in self.known or "-" not in cid:
                    continue
                with self.subTest(archetype=archetype, token=cid):
                    # macrostructure slugs are catalog vocabulary, not library ids
                    self.assertIn(cid, CATALOG_SLUGS,
                                  f"{cid} is neither a shipped library id nor a catalog slug")

    def test_scene_grammar_stated(self):
        """A WebGL composition with no covering scene is an unbuildable order —
        both compositions state where the scene comes from."""
        for archetype in self.CLOSURE_ARCHETYPES:
            with self.subTest(archetype=archetype):
                anatomy = self._anatomy(archetype)
                self.assertIn("author the scene at library quality", anatomy)


class TestWordmarkEnrollmentRule(unittest.TestCase):
    """The live wordmark-floor verdict retracted the universal hover floor
    (0/6 winners build a bespoke wordmark hover): the letter is enrollment in
    the site's uniform link grammar, never a bespoke response."""

    def test_preflight_carries_the_enrollment_letter(self):
        preflight = (REPO_ROOT / "skills" / "award-design" / "references"
                     / "preflight.md").read_text(encoding="utf-8")
        self.assertIn("The wordmark follows the enrollment rule", preflight)
        self.assertNotIn("The wordmark and the accent word are not exempt", preflight)


if __name__ == "__main__":
    unittest.main()
