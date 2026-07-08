"""award-design — the modern-web baseline: the CSS/HTML/JS best practices award
winners ship and AI-generated code skips (OKLCH, rem + fluid clamp, CSS custom
properties, factorization, modern primitives, semantic HTML, GPU motion).

Framed as best practices to ADOPT (distinct from the tells to BAN in anti-patterns),
grounded in the reference article + an adversarial Baseline-status research pass, with
an anti-invention law: adoption tier follows CURRENT Baseline status, verified via
find-docs, never assumed from memory. Also locks the Core-Web-Vitals correction: the
skill's LCP<1.5s budget is an award stretch, not Google's 'good' floor (2.5s)."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFS = SKILL_DIR / "references"


def _read(rel):
    return (REFS / rel).read_text(encoding="utf-8").lower()


def _phase(n):
    body = SKILL_MD.read_text(encoding="utf-8")
    m = re.search(rf"^## Phase {n} — .*?\n(.*?)(?=^## )", body, re.DOTALL | re.MULTILINE)
    assert m is not None, f"## Phase {n} section missing"
    return m.group(1).lower()


class TestFileAndFraming(unittest.TestCase):
    def test_file_exists(self):
        self.assertTrue((REFS / "modern-web-baseline.md").is_file())

    def test_adopt_not_ban_framing(self):
        mb = _read("modern-web-baseline.md")
        self.assertIn("best practices to adopt", mb)
        self.assertIn("tells to ban", mb)

    def test_code_review_distinguishes_adopt_from_ban(self):
        cr = _read("code-review.md")
        self.assertIn("modern-web-baseline.md", cr)
        self.assertIn("best practices to adopt", cr)


class TestBaselineLaw(unittest.TestCase):
    def test_adopt_vs_guard_law(self):
        mb = _read("modern-web-baseline.md")
        self.assertIn("follow current baseline, never memory", mb)
        self.assertIn("adopt unguarded", mb)
        self.assertIn("progressive enhancement", mb)

    def test_anti_invention_verify_first(self):
        mb = _read("modern-web-baseline.md")
        self.assertIn("never assume from training memory", mb)

    def test_baseline_table_present(self):
        mb = _read("modern-web-baseline.md")
        self.assertIn("container queries", mb)
        self.assertIn("not baseline", mb)


class TestAdoptedPractices(unittest.TestCase):
    def test_factorization(self):
        mb = _read("modern-web-baseline.md")
        self.assertIn("define once, reference", mb)

    def test_units_rem_and_wcag_px(self):
        mb = _read("modern-web-baseline.md")
        self.assertIn("css-px minimum interactive target", mb)

    def test_colour_oklch(self):
        mb = _read("modern-web-baseline.md")
        self.assertIn("author colour in", mb)

    def test_semantic_a11y(self):
        mb = _read("modern-web-baseline.md")
        self.assertIn("first rule of aria", mb)


class TestCoreWebVitalsCorrection(unittest.TestCase):
    def test_budget_is_a_stretch_not_googles_floor(self):
        mb = _read("modern-web-baseline.md")
        self.assertIn("tighter than google's official", mb)
        self.assertIn("google's baseline", mb)


class TestSkillPointers(unittest.TestCase):
    def test_points_to_precious_skills(self):
        mb = _read("modern-web-baseline.md")
        for skill in ("vercel-react-best-practices", "vercel-composition-patterns",
                      "web-perf", "a11y-debugging"):
            self.assertIn(skill, mb, skill)

    def test_ai_code_gap_named(self):
        mb = _read("modern-web-baseline.md")
        self.assertIn("ai-code gap", mb)


class TestWiredIntoProtocol(unittest.TestCase):
    def test_phase4_loads_baseline(self):
        self.assertIn("references/modern-web-baseline.md", _phase(4))

    def test_preflight_code_craft_points_to_baseline(self):
        self.assertIn("modern-web-baseline.md", _read("preflight.md"))


if __name__ == "__main__":
    unittest.main()
