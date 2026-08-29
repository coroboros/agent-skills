"""award-design award-imperatives + comparative-review contract.

The 2025–2030 award reference is imposed as gates, not left to taste: the
transverse imperatives (signature interaction, a real nav pattern, smooth-scroll
narrative, clip-path reveals, micro-interactions, modern CSS, a measured perf
budget, AVIF/WebP, mobile reconsidered) and the calibration that makes an
otherwise-lenient adversarial review strict — the exemplar comparison as the
*primary* driver, the desire read raised from "screenshottable" to
"beats-the-SOTD", and the premise/restraint veto that attacks the concept's idea.

Each assertion would FAIL on the pre-upgrade skill, which had the adversarial
machinery but graded absolutely and left the recipe to judgment."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFS = SKILL_DIR / "references"


def _read(name):
    return (REFS / name).read_text(encoding="utf-8")


def _body():
    return SKILL_MD.read_text(encoding="utf-8")


def _path():
    m = re.search(r"^## The path\n(.*?)(?=^## )", _body(), re.DOTALL | re.MULTILINE)
    assert m is not None, "## The path section missing"
    return m.group(1)


def _gate(name):
    return (REFS / "gate" / name).read_text(encoding="utf-8").lower()


class TestAwardImperativesReference(unittest.TestCase):
    def setUp(self):
        self.imp = _read("award-imperatives.md")

    def test_file_exists(self):
        self.assertTrue((REFS / "award-imperatives.md").is_file(),
                        "references/award-imperatives.md missing")

    def test_the_8plus_vs_6to7_line(self):
        low = self.imp.lower()
        self.assertIn("signature", low)
        self.assertTrue("6–7" in self.imp or "6-7" in self.imp or "8+" in self.imp,
                        "must name the 8+ vs 6–7 line the reference exists to break")

    def test_transverse_gates_present(self):
        low = self.imp.lower()
        for gate in ["signature interaction", "navigation pattern", "clip-path",
                     "micro-interaction", "oklch", "mobile"]:
            with self.subTest(gate=gate):
                self.assertIn(gate, low, f"transverse imperative missing: {gate}")

    def test_no_nav_is_banned(self):
        self.assertIn("no nav", self.imp.lower(),
                      'a real nav pattern is mandatory — "no nav" must be named as banned')

    def test_measured_perf_budget_is_a_gate(self):
        low = self.imp.lower()
        for token in ["lcp", "cls", "inp", "avif"]:
            with self.subTest(token=token):
                self.assertIn(token, low, f"perf budget token missing: {token}")
        self.assertIn("measured", low,
                      "the perf budget is measured, never declared from memory")

    def test_comparative_bar_is_primary(self):
        low = self.imp.lower()
        self.assertIn("absolute judgment grades leniently", low,
                      "the reference must state why absolute judgment fails")
        self.assertTrue("beat" in low and ("site of the day" in low or "sotd" in low),
                        "the comparative bar is 'beats the current SOTD', not 'is it nice'")

    def test_restraint_veto_present(self):
        low = self.imp.lower()
        self.assertIn("restraint veto", low)
        self.assertIn("cleverness", low,
                      "the premise veto names art-directed cleverness as the failure")

    def test_per_archetype_expression_table(self):
        # every archetype's canonical winner appears in the per-archetype table
        for winner in ["Terminal Industries", "Eloy Benoffi", "Siena", "Ponpon",
                       "Lando Norris", "Bruno Simon", "Cartier", "Anime.js", "Igloo"]:
            with self.subTest(winner=winner):
                self.assertIn(winner, self.imp,
                              f"per-archetype expression missing winner: {winner}")


class TestRubricRecalibration(unittest.TestCase):
    def setUp(self):
        self.rubric = _read("audit-rubric.md")

    def test_desire_read_is_comparative_not_absolute(self):
        low = self.rubric.lower()
        self.assertIn("comparative", low,
                      "the desire read must be comparative, not absolute")
        self.assertTrue("apolog" in low or "proud" in low,
                        "the bar is 'proud/would you apologize', above 'screenshottable'")

    def test_absolute_judgment_leniency_is_named(self):
        self.assertIn("leniently", self.rubric.lower(),
                      "the rubric must explain that absolute judgment grades leniently")

    def test_premise_veto_present(self):
        low = self.rubric.lower()
        self.assertIn("premise veto", low)
        self.assertIn("attacks the idea", low,
                      "the premise veto attacks the idea, not the execution")

    def test_comparison_is_primary_not_a_footnote(self):
        self.assertIn("primary", self.rubric.lower(),
                      "the exemplar comparison must be the primary driver, not a closing footnote")

    def test_imperatives_check_wired(self):
        self.assertIn("award-imperatives.md", self.rubric,
                      "the rubric must route to the award-imperatives check")


class TestSkillWiring(unittest.TestCase):
    def test_build_step_commits_the_award_surfaces(self):
        """The imperatives bind through the roster: the ladder commits each
        award surface by name or declares it out, and award-imperatives.md is
        the catalog those names come from."""
        path = _path()
        self.assertIn("then the award surfaces — loader, nav, cursor, footer moment, "
                      "route transitions, sound — committed or declared out with a reason",
                      path)
        self.assertIn("committed or declared out with a reason", path,
                      "an unconsidered surface is a gap, never a style choice")
        for surface in ("loader", "nav", "cursor", "footer moment",
                        "route transitions", "sound"):
            with self.subTest(surface=surface):
                self.assertIn(surface, path, f"award surface missing: {surface}")
        self.assertIn("award surface roster", _read("award-imperatives.md").lower(),
                      "the roster catalog must survive in award-imperatives.md")

    def test_contract_commits_nav_and_signature(self):
        path = _path()
        self.assertIn("the award surfaces — loader, nav, cursor", path,
                      "the nav pattern must be an explicit award-surface commit")
        self.assertIn("**SIGNATURE** (verb · medium · trigger", path,
                      "the signature must be a contract block, named by verb and medium")

    def test_hero_gate_is_comparative(self):
        """The hero is the ladder's first visual chunk, judged comparatively
        before any section is built — a hero that loses re-enters by cause."""
        path = _path()
        self.assertIn("then the hero — 2–3 genuinely distinct directions through one "
                      "shared render frame", path,
                      "the ladder must gate the hero comparatively, before the sections")
        self.assertLess(path.find("the shell first"), path.find("then the hero"))
        self.assertLess(path.find("then the hero"), path.find("then the sections"))
        self.assertIn("a fresh-context judge (`references/gate/hero.md`) picking beside the archetype's live exemplar",
                      path, "the hero gate compares against the archetype's exemplar")
        self.assertIn("Only a hero that clears this earns the rest of the ladder",
                      _read("chunk-template.md"))

    def test_gates_carry_the_veto_and_the_comparative_read(self):
        self.assertIn("premise veto", _gate("concept.md"),
                      "R1 must run the premise/restraint veto")
        self.assertIn("comparative desire read", _gate("review.md"),
                      "the desire read that opens R2 must be comparative")


if __name__ == "__main__":
    unittest.main()
