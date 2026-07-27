"""award-design — the PIG IRON round-4 UAT hardening: subject temperature, the ambient
channel, the travelling thread, the world's own colour code, and diegetic legibility.

The PIG IRON build scored ~8 on craft and 6.5 with the user: every element responded on
touch yet the page sat still between inputs ("not enough micro-animations"), the LOAD
echoes were entrance-only episodes ("a stronger through-line"), calibrated plates —
colour-coded in the real sport — shipped ink-black ("more joy and colour"), and the bar
drawing had one sleeve, unreadable as a barbell at a glance. These lock the laws."""

import re
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


def _phase(n):
    body = SKILL_MD.read_text(encoding="utf-8")
    m = re.search(rf"^## Phase {n} — .*?\n(.*?)(?=^## )", body, re.DOTALL | re.MULTILINE)
    assert m is not None, f"## Phase {n} section missing"
    return m.group(1).lower()


class TestSubjectTemperature(unittest.TestCase):
    def test_atmosphere_floors_the_dials(self):
        at = _read("atmosphere-calibration.md")
        self.assertIn("the subject's lived temperature floors the dials", at)
        self.assertIn("never the world's pulse", at)
        self.assertIn("a brochure *about* the thing", at)

    def test_phase0_reads_the_temperature(self):
        p0 = _phase(0)
        self.assertIn("the subject's lived temperature", p0)
        self.assertIn("floors motion above the archetype's resting default", p0)


class TestAmbientChannel(unittest.TestCase):
    def test_interaction_signatures_third_channel(self):
        ix = _read("interaction-signatures.md")
        self.assertIn("the page breathes at rest", ix)
        self.assertIn("reads embalmed between interactions", ix)

    def test_phase4_commits_the_idle_channel(self):
        p4 = _phase(4)
        self.assertIn("one ambient idle channel", p4)

    def test_review_density_read_carries_the_channel(self):
        s = _skill()
        self.assertIn("the density/aliveness read", s)
        self.assertIn("live channels", s)


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
