"""award-design — the mid-page aliveness round (HALDANE UAT: "superbe hero, les
images s'ouvrent superbement, mais le milieu est mort"). Nine Opus researchers
mined the tier's top scorers per archetype (Lusion 8.25 and Lando 8.18 are the
measured ceiling — the >=8.5 tier barely exists), nine refuters re-opened every
claim (one fabricated view-timeline system struck, Gabriel's "no Lenis" reversed
by a bundle the researcher never opened, Siena's award month corrected). These
lock: the Mid-page life palette rows, the dead-middle law (channels stack through
the middle, never run sequentially), the hover-on-text evidence catalog, the
per-archetype smooth-scroll ruling, and the score-reality calibration."""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
REFS = SKILL_DIR / "references"

ARCHETYPES = ("minimalist", "brutalist", "editorial", "bold-maximal",
              "immersive-cinematic", "experimental", "corporate-luxury",
              "bento-card", "spatial-organic")


def _read(rel):
    return (REFS / rel).read_text(encoding="utf-8").lower()


class TestMidPageLifeRows(unittest.TestCase):
    def test_every_palette_carries_the_row(self):
        for a in ARCHETYPES:
            body = _read(f"{a}.md")
            with self.subTest(archetype=a):
                # tier 2 loads by heading, so the row is a `##` section of its own
                self.assertIn("## mid-page life", body)
                # the section precedes the pinned Scroll texture section
                self.assertLess(body.index("## mid-page life"),
                                body.index("## scroll texture"))


class TestDeadMiddleLaw(unittest.TestCase):
    def test_layered_never_sequential(self):
        ix = _read("interaction-signatures.md")
        self.assertIn(
            "**the middle is layered, never sequential — the dead-middle law.**",
            ix)
        self.assertIn("the channels run together from hero to footer", ix)


class TestHoverOnText(unittest.TestCase):
    def test_catalog_section(self):
        te = _read("text-effects.md")
        self.assertIn("## hover on text — what the tier ships", te)

    def test_misfire_guard(self):
        te = _read("text-effects.md")
        self.assertIn("never reflows the line", te)


class TestSmoothScrollRuling(unittest.TestCase):
    def test_imperative_carries_the_per_archetype_ruling(self):
        ai = _read("award-imperatives.md")
        self.assertIn("from the bento canon", ai)
        self.assertIn("in-engine** on experimental", ai)

    def test_foundations_universal_claim_corrected(self):
        f = _read("foundations.md")
        self.assertIn("never universal", f)

    def test_bento_palette_says_native(self):
        self.assertIn("native scroll is the canon", _read("bento-card.md"))


class TestScoreRealityCalibration(unittest.TestCase):
    def test_skill_names_the_measured_ceiling(self):
        s = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("routine sotd lands 7.2–7.9", s)
        self.assertIn("never an imagined 9", s)


if __name__ == "__main__":
    unittest.main()
