"""award-design — the per-archetype effect palettes and the composition grammar.

Every archetype reference gained an evidence-based Effect palette — recipes per element
class read from the line's actual awarded sites — and the protocol forces composition
from it: the design_plan commits one named recipe per element class, distinct across
classes, bound by one declared grammar (easing family + accent role + metaphor). Locks
the research round that answered the recurring cross-build defect: one pale fill-sweep
recycled on every control of every build."""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFS = SKILL_DIR / "references"

ARCHETYPES = [
    "minimalist",
    "brutalist",
    "editorial",
    "bold-maximal",
    "immersive-cinematic",
    "experimental",
    "corporate-luxury",
    "bento-card",
    "spatial-organic",
]


def _read(rel):
    return (REFS / rel).read_text(encoding="utf-8").lower()


def _skill():
    return SKILL_MD.read_text(encoding="utf-8")


class TestEffectPalettesExist(unittest.TestCase):
    def test_every_archetype_carries_an_effect_palette(self):
        for a in ARCHETYPES:
            body = _read(f"{a}.md")
            self.assertIn(
                "## effect palette — what this line's winners ship", body, f"{a}.md"
            )

    def test_every_palette_states_its_grammar(self):
        for a in ARCHETYPES:
            body = _read(f"{a}.md")
            self.assertIn("**the grammar**", body, f"{a}.md")

    def test_every_palette_lists_anti_signals(self):
        for a in ARCHETYPES:
            body = _read(f"{a}.md")
            self.assertIn("anti-signals", body, f"{a}.md")


class TestCompositionForcing(unittest.TestCase):
    def test_ingredient_set_draws_from_the_palette(self):
        ix = _read("interaction-signatures.md")
        self.assertIn("drawn first from the chosen archetype's *effect palette*", ix)
        self.assertIn("four rules hold it together", ix)

    def test_grammar_law_present(self):
        ix = _read("interaction-signatures.md")
        self.assertIn("the grammar is what makes the variety cohere", ix)
        self.assertIn("it is the absence of a grammar", ix)

    def test_design_plan_picks_one_recipe_per_class(self):
        ix = _read("interaction-signatures.md")
        self.assertIn("the design_plan picks one per class and names the grammar", ix)
        self.assertIn("is a default in costume", ix,
                      "one trick stamped on every class must stay named as the fail")

    def test_tier_two_palette_and_recipe_load_at_the_design_plan_commit(self):
        """The palette binds because the design_plan commit loads the archetype's
        tier-2 file by heading — an unloaded palette composes nothing."""
        self.assertIn(
            "tier-2 `references/<name>.md` — by heading via its Contents index | step 9, committing the section list",
            _skill(), "the load map must price the tier-2 load at the section-list commit")
        for a in ARCHETYPES:
            with self.subTest(archetype=a):
                tier2 = _read(f"{a}.md")
                self.assertIn("## effect palette", tier2)
                self.assertIn("## page recipe", tier2)


if __name__ == "__main__":
    unittest.main()
