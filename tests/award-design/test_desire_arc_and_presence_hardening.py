"""award-design — the round-6 UAT hardening: the desire arc, the promise hero, the
inhabited world, the world's gestures, the spectacle floor, and content generosity.

PIG IRON v2 held every craft gate and the user held it at 6.5: "nothing spectacular,
a bit empty, no one to identify with, the sport's own movements never played — why?
for whom? who is there? why would I go? — and that binds absolutely every landing."
Beside the category's own SOTDs (Capitolium's "Qui se Ressemble, Rassemble", Radian's
"A new era of enduro starts here", Balmoral's runners mid-stride) the gap was content:
the skill forced the form and never the persuasion. These lock the desire layer."""

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


class TestDesireArc(unittest.TestCase):
    def test_copy_recipes_force_the_five_answers(self):
        cr = _read("copy-recipes.md")
        self.assertIn("why this exists, for whom, who is already there", cr)
        self.assertIn("why come now", cr)

    def test_the_contract_carries_the_arc(self):
        """The arc has to land in a committed block rather than a mood; the
        direction contract's STORY block is where it binds."""
        self.assertIn("**story** (the desire arc's five content answers", _skill())
        self.assertIn("the direction contract's story block", _read("copy-recipes.md"))

    def test_anti_pattern_entry(self):
        ap = _read("anti-patterns.md")
        self.assertIn("a landing that describes and never asks you in", ap)
        self.assertIn("description informs; desire moves", ap)


class TestPromiseHero(unittest.TestCase):
    def test_copy_recipes_promise_over_description(self):
        self.assertIn("the hero leads with the promise", _read("copy-recipes.md"))

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


class TestWorldsGestures(unittest.TestCase):
    def test_spine_plays_the_gestures(self):
        si = _read("signature-invention.md")
        self.assertIn("the world's gestures supply structure and motion", si)
        self.assertIn("its rituals become the chapters", si)

    def test_anti_pattern_entry(self):
        ap = _read("anti-patterns.md")
        self.assertIn("the world's gestures left unplayed", ap)
        self.assertIn("play the gestures, not only the objects", ap)


class TestSpectacleFloor(unittest.TestCase):
    def test_signature_floor(self):
        si = _read("signature-invention.md")
        self.assertIn("passage a judge would replay", si)
        self.assertIn("a quiet second-read detail", si)

    def test_anti_pattern_entry(self):
        ap = _read("anti-patterns.md")
        self.assertIn("tasteful competence with no spectacle", ap)

    def test_structural_ceiling_in_the_catalog(self):
        ap = _read("anti-patterns.md")
        self.assertIn("spectacular nowhere is the structural 6.5", ap)


class TestGenerosityAndCategoryBar(unittest.TestCase):
    def test_generous_page(self):
        self.assertIn("award landings are generous", _read("anti-patterns.md"))

    def test_anti_pattern_thin_landing(self):
        ap = _read("anti-patterns.md")
        self.assertIn("the thin landing", ap)
        self.assertIn("thin reads empty, not minimal", ap)

    def test_review_compares_against_the_subject_category(self):
        self.assertIn("the category's recent award winners", _gate("review.md"))


if __name__ == "__main__":
    unittest.main()
