"""award-design — the award surface roster: the seven surfaces winners design
that competent builds leave unconsidered (loader, nav, cursor, hero architecture,
footer moment, route transitions, sound). The empirical 6.5 ceiling includes
surfaces the model never decided on — an arrival with no loader decision, a
template footer, a hard route cut. The roster catalog lives in
award-imperatives.md; Phase 4 commits each surface from it or declares it out
with a reason — an unconsidered surface is a gap, never a style choice."""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
REFS = SKILL_DIR / "references"

SURFACES = ("loader / intro", "navigation", "cursor", "hero architecture",
            "footer moment", "route transitions", "sound")


def _read(rel):
    return (REFS / rel).read_text(encoding="utf-8").lower()


def _skill():
    return (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").lower()


class TestRosterCatalog(unittest.TestCase):
    def test_roster_section_and_surfaces(self):
        ai = _read("award-imperatives.md")
        self.assertIn("## the award surface roster", ai)
        for surface in SURFACES:
            with self.subTest(surface=surface):
                self.assertIn(f"**{surface}**", ai)

    def test_commit_by_name_or_declared_out(self):
        ai = _read("award-imperatives.md")
        self.assertIn("by catalog name", ai)
        self.assertIn("brief- or archetype-canon-tied reason", ai)
        self.assertIn("an unconsidered surface", ai)

    def test_roster_routes_loading(self):
        ai = _read("award-imperatives.md")
        self.assertIn("the roster routes loading", ai)
        self.assertIn("load its catalog then, not before", ai)

    def test_quiet_constraints_outrank(self):
        self.assertIn("quiet-constraints briefs (phase 0) outrank the roster",
                      _read("award-imperatives.md"))


class TestPhase4Commit(unittest.TestCase):
    def test_commit_sentence(self):
        s = _skill()
        self.assertIn("**the award surfaces**", s)
        self.assertIn("declared out with a reason", s)
        self.assertIn("an unconsidered surface is a gap", s)

    def test_footer_closes_live(self):
        self.assertIn("winners close on a live footer", _skill())

    def test_page_catalogs_load_at_phase_4(self):
        s = _skill()
        self.assertIn("references/page-anatomy.md", s)
        self.assertIn("references/copy-recipes.md", s)


if __name__ == "__main__":
    unittest.main()
