"""Closure pass — the orchestrator-scope orders that ended the completeness
program: the two compositions the rulings ordered (cinematic-pavilion,
playable-verb), now carried in the two archetypes' tier-2 Anatomy."""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class TestClosureCompositions(unittest.TestCase):
    """The two compositions ordered by the rung-6B pavilion note and the rung-9B
    playable-verb ruling. They lived in `recipes.json` as recipe rows; the
    two-tier restructure merged them into the two archetypes' tier-2 Anatomy,
    which is what the design_plan commit loads."""

    CLOSURE_ARCHETYPES = {"experimental": "playable-verb", "corporate-luxury": "cinematic-pavilion"}

    @classmethod
    def setUpClass(cls):
        cls.refs = REPO_ROOT / "skills" / "award-design" / "references"

    def _anatomy(self, archetype):
        body = (self.refs / f"{archetype}.md").read_text(encoding="utf-8")
        return body[body.index("**Anatomy**"):body.index("**Hero architectures**")]

    def test_the_playable_verb_climax_composes_the_ruled_pieces(self):
        anatomy = self._anatomy("experimental")
        for piece in ("raycast hover and tap state", "DOM-to-3D input bridge", "press-and-hold reveal",
                      "idle attract auto-demo", "positional audio bed", "in-scene ambient life"):
            with self.subTest(mechanic=piece):
                self.assertIn(piece, anatomy)

    def test_the_pavilion_procession_composes_the_ruled_pieces(self):
        anatomy = self._anatomy("corporate-luxury")
        for piece in ("rooms procession", "continuous score", "pinned media step-through"):
            with self.subTest(mechanic=piece):
                self.assertIn(piece, anatomy)

    def test_scene_grammar_stated(self):
        """A WebGL composition with no scene is an unbuildable order — both
        compositions route the scene to the delegated build; no reference-scene
        set exists to reach for."""
        for archetype in self.CLOSURE_ARCHETYPES:
            with self.subTest(archetype=archetype):
                anatomy = self._anatomy(archetype)
                self.assertIn("author the scene through the delegated WebGL build "
                              "(`ingredients/web3d-for-sites.md` §The delegation contract)", anatomy)
                self.assertNotIn("covering reference scene", anatomy)


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
