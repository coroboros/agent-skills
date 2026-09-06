"""award-design — the PIG IRON round-4 UAT hardening: subject temperature, the ambient
channel, the travelling thread, the world's own colour code, and diegetic legibility.

The PIG IRON build scored ~8 on craft and 6.5 with the user: every element responded on
touch yet the page sat still between inputs ("not enough micro-animations"), the LOAD
echoes were entrance-only episodes ("a stronger through-line"), calibrated plates —
colour-coded in the real sport — shipped ink-black ("more joy and colour"), and the bar
drawing had one sleeve, unreadable as a barbell at a glance. These lock the laws."""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFS = SKILL_DIR / "references"


def _read(rel):
    return (REFS / rel).read_text(encoding="utf-8").lower()


def _skill():
    return SKILL_MD.read_text(encoding="utf-8").lower()


def _gate(rel):
    return (REFS / "gate" / rel).read_text(encoding="utf-8").lower()


class TestSubjectTemperature(unittest.TestCase):
    def test_atmosphere_floors_the_dials(self):
        at = _read("atmosphere-calibration.md")
        self.assertIn("the subject's lived temperature floors the dials", at)
        self.assertIn("never the world's pulse", at)
        self.assertIn("a brochure *about* the thing", at)

    def test_the_dials_reference_carries_the_floor(self):
        """Step 0 reads the dials through atmosphere-calibration.md, which is
        where the temperature floor outranks the archetype's resting default."""
        self.assertIn("references/atmosphere-calibration.md", _skill())
        at = _read("atmosphere-calibration.md")
        self.assertIn("the subject's lived temperature floors the dials", at)
        self.assertIn("the floor outranks the archetype's resting default", at)


class TestAmbientChannel(unittest.TestCase):
    def test_interaction_signatures_third_channel(self):
        ix = _read("interaction-signatures.md")
        self.assertIn("ambient life follows the archetype", ix)
        self.assertIn("minimalist may declare ambient absence", ix)

    def test_density_read_commits_the_idle_channel(self):
        self.assertIn("a reading register may be static", _gate("review.md"))
        self.assertIn("a declared live scene must sustain its medium", _gate("review.md"))

    def test_review_density_read_carries_the_channel(self):
        r = _gate("review.md")
        self.assertIn("the density read follows", r)
        self.assertIn("judge missing declared choreography", r)


class TestTravellingThread(unittest.TestCase):
    def test_interaction_signatures_travel_clause(self):
        ix = _read("interaction-signatures.md")
        self.assertIn("at least one signature element *travels* that distance", ix)
        self.assertIn("entrance-only echoes are episodes, not a thread", ix)

    def test_carry_mechanics_named(self):
        ix = _read("interaction-signatures.md")
        self.assertIn("persists, accumulates, or progresses section by section", ix)


class TestWorldsOwnColour(unittest.TestCase):
    def test_anti_pattern_muted_world(self):
        ap = _read("anti-patterns.md")
        self.assertIn("the muted world", ap)
        self.assertIn("canonical colour system", ap)
        self.assertIn("gaiety is not a register violation", ap)


class TestDiegeticLegibility(unittest.TestCase):
    def test_anti_pattern_whole_anatomy(self):
        ap = _read("anti-patterns.md")
        self.assertIn("drawn whole with its real anatomy", ap)
        self.assertIn("a sleeve at *both* ends", ap)


if __name__ == "__main__":
    unittest.main()
