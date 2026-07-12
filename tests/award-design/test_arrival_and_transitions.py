"""award-design — the arrival layer: preloaders, page transitions, and the physics
of authored motion.

Two adversarially refuted dossiers (a 30-winner preloader corpus, a 15-winner route
corpus) settled the arrival record: loaders are archetype-conditional and live or die
on the handoff into the hero; every verified route transition is JS-orchestrated
(zero winners ship native View Transitions as the signature); and one site speaks one
arrival language — the transition family rhymes with the loader family. A product-film
analysis adds the physics of any authored beat: slow-fast-boom-stop time allocation,
the easing map, the pre-beat hold, and the three-channel focus switch. These pin the
two ingredient files and the motion-palette section that encode it."""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REFS = REPO_ROOT / "skills" / "award-design" / "references"


def _read(rel):
    return (REFS / rel).read_text(encoding="utf-8").lower()


class TestPreloadersIngredient(unittest.TestCase):
    def setUp(self):
        self.path = REFS / "ingredients" / "preloaders.md"
        self.assertTrue(self.path.is_file(), "references/ingredients/preloaders.md must exist")
        self.body = self.path.read_text(encoding="utf-8").lower()

    def test_headings(self):
        for heading in (
            "## loader families — beat tables",
            "## the handoff patterns",
            "## the lcp interaction",
            "## archetype-fit map",
            "## anti-signals",
        ):
            with self.subTest(heading=heading):
                self.assertIn(heading, self.body)

    def test_handoff_is_the_craft_lever(self):
        self.assertIn("the craft lever", self.body)
        self.assertIn("a loader with no handoff choreography is the disqualifier", self.body)

    def test_anti_signal_lines(self):
        self.assertIn("spinner", self.body)
        self.assertIn("blocking splash with no handoff", self.body)
        self.assertIn(">3s ceremony", self.body)
        self.assertIn("decorative counter over a static hero", self.body)

    def test_repeat_visit_and_reduced_motion_are_named_gaps(self):
        # both absent from every winner read — adopted as build decisions, never winner-cited
        self.assertIn("sessionstorage", self.body)
        self.assertIn("prefers-reduced-motion", self.body)
        self.assertIn("record gap", self.body)

    def test_lcp_honesty(self):
        self.assertIn("fixed-duration theater", self.body)
        self.assertIn("pre-composed", self.body)
        # the ≤2.8s ceiling was asserted in the record, never frame-timed
        self.assertIn("≤2.8s", self.body)
        self.assertIn("heuristic", self.body)

    def test_truekind_correction_survives(self):
        # the refutation's one hard correction: Truekind is a loader-shipping winner,
        # not a light-editorial "none" example
        self.assertIn("it ships a progress-tracked full-screen white preloader", self.body)


class TestPageTransitionsIngredient(unittest.TestCase):
    def setUp(self):
        self.path = REFS / "ingredients" / "page-transitions.md"
        self.assertTrue(self.path.is_file(), "references/ingredients/page-transitions.md must exist")
        self.body = self.path.read_text(encoding="utf-8").lower()

    def test_headings(self):
        for heading in (
            "## transition forms — beat tables",
            "## tech paths — what each costs",
            "## the loader-coherence rule",
            "## mpa / spa notes",
            "## archetype-fit map",
            "## anti-signals",
        ):
            with self.subTest(heading=heading):
                self.assertIn(heading, self.body)

    def test_loader_coherence_rule_sentence(self):
        self.assertIn("one arrival language per site", self.body)
        self.assertIn("the route transition rhymes with the loader family", self.body)

    def test_view_transitions_baseline_as_verified(self):
        self.assertIn("zero of 15 winners", self.body)
        self.assertIn("baseline newly available", self.body)  # same-document, 2025-10
        self.assertIn("not baseline", self.body)              # cross-document, no Firefox
        self.assertIn("progressive-enhancement floor", self.body)

    def test_tech_path_costs(self):
        self.assertIn("taxi.js", self.body)
        self.assertIn("barba", self.body)
        self.assertIn("scrollrestoration", self.body)
        self.assertIn('"manual"', self.body)

    def test_anti_signal_lines(self):
        self.assertIn("a hard cut on a site that choreographs everything else", self.body)
        self.assertIn("broken scroll restoration", self.body)
        self.assertIn("focus trapped behind the cover", self.body)
        self.assertIn("does not rhyme with the loader", self.body)


class TestArrivalCoherenceWiring(unittest.TestCase):
    def test_siblings_cross_reference_each_other(self):
        pre = _read("ingredients/preloaders.md")
        pt = _read("ingredients/page-transitions.md")
        self.assertIn("page-transitions.md", pre)
        self.assertIn("preloaders.md", pt)
        # the rule lives on both sides of the seam
        self.assertIn("one arrival language per site", pre)


class TestPhysicsOfMotion(unittest.TestCase):
    def setUp(self):
        self.mp = _read("motion-palette.md")

    def test_section_exists_and_is_tagged(self):
        self.assertIn("## physics of motion", self.mp)
        self.assertIn("(technique — product-film analysis)", self.mp)

    def test_slow_fast_boom_stop(self):
        self.assertIn("slow-fast-boom-stop", self.mp)
        self.assertIn("even pacing is a tech demo; rhythm is narrative", self.mp)
        self.assertIn("never a fade-out", self.mp)

    def test_easing_scenario_map(self):
        self.assertIn("cubic-bezier(0.16, 1, 0.3, 1)", self.mp)    # expo-out, reveal default
        self.assertIn("cubic-bezier(0.34, 1.56, 0.64, 1)", self.mp)  # overshoot, toggles/arrivals
        self.assertIn("spring", self.mp)                            # physical settles

    def test_pre_beat_hold(self):
        self.assertIn("300–500ms", self.mp)
        self.assertIn("reaction time", self.mp)

    def test_focus_switch_takes_three_channels(self):
        self.assertIn("never opacity alone", self.mp)
        for channel in ("brightness", "saturation", "blur"):
            with self.subTest(channel=channel):
                self.assertIn(channel, self.mp)


if __name__ == "__main__":
    unittest.main()
