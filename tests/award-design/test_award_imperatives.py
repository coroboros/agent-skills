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


def _phase(n):
    m = re.search(rf"^## Phase {n} — .*?\n(.*?)(?=^## )", _body(), re.DOTALL | re.MULTILINE)
    assert m is not None, f"## Phase {n} section missing"
    return m.group(1)


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
        for winner in ["Terminal Industries", "FlowFest", "Siena", "Ponpon",
                       "Lando Norris", "Bruno Simon", "Cartier", "Anime.js"]:
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
    def test_phase_4_loads_imperatives(self):
        self.assertIn("award-imperatives.md", _phase(4),
                      "Phase 4 must reference award-imperatives.md")

    def test_phase4_commits_nav_and_signature(self):
        p4 = _phase(4).lower()
        self.assertIn("navigation pattern", p4,
                      "the nav pattern must be an explicit design_plan commit")
        self.assertIn("the signature (verb, medium, trigger)", p4,
                      "the signature must be an explicit commit, named by verb and medium")

    def test_phase4_hero_micro_loop(self):
        p4 = _phase(4)
        self.assertIn("Hero first", p4,
                      "Phase 4 must gate the hero first, comparatively, before the rest")
        low = p4.lower()
        self.assertTrue("panel" in low and "canonical winner" in low,
                        "the hero gate compares against the archetype's canonical winner")

    def test_review_mode_premise_veto_and_panel(self):
        body = _body()
        m = re.search(r"^## Review mode.*?(?=^## )", body, re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, "Review mode section missing")
        review = m.group(0).lower()
        self.assertIn("restraint veto", review,
                      "R1 must run the premise/restraint veto")
        self.assertIn("multi-lens panel", review,
                      "Review mode must offer the multi-lens adversarial panel")
        self.assertIn("comparative desire read", review,
                      "the desire read in Review mode must be comparative")


if __name__ == "__main__":
    unittest.main()
