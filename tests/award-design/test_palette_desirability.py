"""award-design — palette desirability, the lived A/B gate.

ARDEN's bone + pure-red cleared every color gate — the AI-slop hue bans, the OKLCH
lint, the role-clarity rubric — and shipped clinical: a mortuary palette whose accent
underlines scanned as broken links. Role-coherence is not desirability, and nothing
measured the latter. These lock the gate that now does: a lived A/B in the DESIGN.md
Colors section, refuted at R1, scored comparatively in the rubric, with the clinical
cluster named as an observed-cluster to rotate away from."""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
REFS = SKILL_DIR / "references"


def _read(name):
    return (REFS / name).read_text(encoding="utf-8")


class TestDesignMdCarriesTheLivedAB(unittest.TestCase):
    def setUp(self):
        self.md = _read("design-md-anatomy.md")

    def test_palette_ab_section_present(self):
        self.assertIn("Palette desirability", self.md)
        self.assertIn("lived A/B", self.md)

    def test_judged_at_page_proportions_not_swatches(self):
        low = self.md.lower()
        self.assertIn("page proportions", low)
        self.assertIn("beside the archetype exemplar", low)
        # equal-size swatches hide the failure — the rule must say so
        self.assertIn("swatches at equal size", low)

    def test_clinical_verdict_fails_r1(self):
        self.assertIn("clinical fails R1", self.md)

    def test_quotes_the_lived_temperature(self):
        # the read cites atmosphere-calibration's temperature floor
        self.assertIn("atmosphere-calibration.md", self.md)


class TestR1RefutesThePalette(unittest.TestCase):
    def test_r1_gate_refutes_palette_ab(self):
        gate = (REFS / "gate" / "concept.md").read_text(encoding="utf-8")
        self.assertIn("**Palette lived A/B.**", gate)
        self.assertIn("role-coherence is not desirability", gate)


class TestRubricScoresDesirability(unittest.TestCase):
    def setUp(self):
        self.rubric = _read("audit-rubric.md")

    def test_color_section_names_desirability(self):
        self.assertIn("desirability, judged beside the exemplar", self.rubric)

    def test_clinical_caps_at_five(self):
        # a role-coherent but clinical palette cannot pass 5
        self.assertIn("role-coherence cannot lift it past here", self.rubric)

    def test_ten_requires_alive_beside_exemplar(self):
        self.assertIn("the palette reads alive", self.rubric)


class TestClinicalClusterNamed(unittest.TestCase):
    def setUp(self):
        self.ap = _read("anti-patterns.md")

    def test_clinical_minimal_cluster(self):
        self.assertIn("clinical minimal", self.ap)

    def test_accent_underline_broken_link_tell(self):
        low = self.ap.lower()
        self.assertIn("accent underlines scan as broken", low)

    def test_is_a_desirability_cluster_not_a_blocklist(self):
        self.assertIn("lived-desirability", self.ap)
        # judged beside the exemplar, not by hex
        self.assertIn("judge the composed system beside the exemplar", self.ap)


if __name__ == "__main__":
    unittest.main()
