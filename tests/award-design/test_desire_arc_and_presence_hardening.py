"""award-design — the round-6 UAT hardening: the desire arc, the promise hero, the
inhabited world, the world's gestures, the spectacle floor, and content generosity.

PIG IRON v2 held every craft gate and the user held it at 6.5: "nothing spectacular,
a bit empty, no one to identify with, the sport's own movements never played — why?
for whom? who is there? why would I go? — and that binds absolutely every landing."
Beside the category's own SOTDs (Capitolium's "Qui se Ressemble, Rassemble", Radian's
"A new era of enduro starts here", Balmoral's runners mid-stride) the gap was content:
the skill forced the form and never the persuasion. These lock the desire layer."""

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


class TestDesireArc(unittest.TestCase):
    def test_phase1_forces_the_five_answers(self):
        p1 = _phase(1)
        self.assertIn("**desire arc**", p1)
        self.assertIn("why this exists (the belief), for whom, who is there", p1)
        self.assertIn("this binds every landing, whatever the archetype", p1)

    def test_phase1_artifact_carries_the_arc(self):
        p1 = _phase(1)
        self.assertIn("desire arc (the five answers)", p1)

    def test_anti_pattern_entry(self):
        ap = _read("anti-patterns.md")
        self.assertIn("a landing that describes and never asks you in", ap)
        self.assertIn("description informs; desire moves", ap)

    def test_preflight_copy_box(self):
        pf = _read("preflight.md")
        self.assertIn("the page answers the desire arc", pf)


class TestPromiseHero(unittest.TestCase):
    def test_phase1_promise_over_description(self):
        p1 = _phase(1)
        self.assertIn("the hero leads with the promise", p1)

    def test_anti_pattern_brochure_hero(self):
        ap = _read("anti-patterns.md")
        self.assertIn("the brochure hero", ap)
        self.assertIn("the promise says where it takes you", ap)


class TestInhabitedWorld(unittest.TestCase):
    def test_anti_pattern_entry(self):
        ap = _read("anti-patterns.md")
        self.assertIn("the uninhabited world", ap)
        self.assertIn("human, animal, machine, vegetal, or the moving element itself", ap)
        self.assertIn("a quiet reading register may earn stillness — declared, never defaulted", ap)

    def test_preflight_assets_box(self):
        pf = _read("preflight.md")
        self.assertIn("the world is inhabited", pf)
        self.assertIn("wind through dust", pf)


class TestWorldsGestures(unittest.TestCase):
    def test_spine_plays_the_gestures(self):
        p1 = _phase(1)
        self.assertIn("the world's own gestures supply structure and motion", p1)

    def test_anti_pattern_entry(self):
        ap = _read("anti-patterns.md")
        self.assertIn("the world's gestures left unplayed", ap)
        self.assertIn("play the gestures, not only the objects", ap)


class TestSpectacleFloor(unittest.TestCase):
    def test_phase1_signature_floor(self):
        p1 = _phase(1)
        self.assertIn("the spectacle floor", p1)
        self.assertIn("passage a judge would replay", p1)

    def test_anti_pattern_entry(self):
        ap = _read("anti-patterns.md")
        self.assertIn("tasteful competence with no spectacle", ap)

    def test_preflight_desire_read_extended(self):
        pf = _read("preflight.md")
        self.assertIn("clean everywhere, spectacular nowhere is the structural 6.5", pf)


class TestGenerosityAndCategoryBar(unittest.TestCase):
    def test_phase4_generous_page(self):
        p4 = _phase(4)
        self.assertIn("an award landing is generous", p4)

    def test_anti_pattern_thin_landing(self):
        ap = _read("anti-patterns.md")
        self.assertIn("the thin landing", ap)
        self.assertIn("thin reads empty, not minimal", ap)

    def test_review_compares_against_the_subject_category(self):
        body = _skill()
        self.assertIn("the subject category's current best", body)
        self.assertIn("judged beside the sport sotds, not only the archetype's canon", body)


if __name__ == "__main__":
    unittest.main()
