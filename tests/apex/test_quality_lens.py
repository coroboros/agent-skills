"""Tests for the quality lens and the gates that consume it.

Ambient quality rules do not change behavior; apex binds them to checkpoints
that must produce evidence. These tests pin that binding: every consuming
step routes to the lens, the lens protects what must never be simplified
away, a budget overrun reaches the derivation lens, the kill council never
proposes additions, and every reviewer degrades to a disclosed self-check.
"""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
APEX = REPO_ROOT / "skills" / "apex"
LENS = APEX / "references" / "quality-lens.md"


def _read(rel: str) -> str:
    return (APEX / rel).read_text(encoding="utf-8")


def _section(text: str, start: str, end: str) -> str:
    i = text.index(start)
    j = text.index(end, i + len(start))
    return text[i:j]


class TestLensIsBound(unittest.TestCase):
    def test_consuming_steps_route_to_the_lens(self):
        for rel in (
            "SKILL.md",
            "steps/step-02-plan.md",
            "steps/step-03-execute.md",
            "steps/step-03b-refine.md",
            "steps/step-04-examine.md",
        ):
            with self.subTest(file=rel):
                self.assertIn("references/quality-lens.md", _read(rel))

    def test_lens_protects_what_must_survive_simplification(self):
        lens = LENS.read_text(encoding="utf-8")
        protected = _section(lens, "## Never simplified away", "## Readability guards")
        for item in ("trust boundaries", "data loss", "Security controls", "Tests"):
            with self.subTest(item=item):
                self.assertIn(item, protected)

    def test_lens_rules_name_violations(self):
        lens = LENS.read_text(encoding="utf-8")
        for heading in ("## Build ladder", "## One owner (DRY)", "## Minimum structure (KISS, YAGNI)", "## Comments"):
            with self.subTest(section=heading):
                self.assertIn("Violation", _section(lens, heading, "\n## "))


class TestBudgetReachesDerivationLens(unittest.TestCase):
    def test_unrecorded_budget_overrun_is_scope_add(self):
        row = next(
            line for line in _read("references/derivation-lens.md").splitlines()
            if line.startswith("| `SCOPE-ADD`")
        )
        self.assertIn("Design budget", row)

    def test_plan_template_carries_a_numeric_budget(self):
        self.assertIn("### Design budget", _read("steps/step-02-plan.md"))


class TestKillCouncil(unittest.TestCase):
    def setUp(self):
        self.council = _section(_read("steps/step-02-plan.md"), "### 4c. Kill council", "### 5.")

    def test_council_is_fresh_and_never_proposes_additions(self):
        self.assertIn("fresh-context", self.council)
        self.assertIn("Never propose features, checks or abstractions", self.council)
        self.assertIn("GAP", self.council)

    def test_outcome_kills_stay_user_owned_under_auto(self):
        self.assertIn("User-owned", self.council)
        self.assertIn("{auto_mode}", self.council)
        self.assertIn("accepted criteria and negative scope stay fixed", self.council)
        self.assertIn("documented constraint", self.council)

    def test_minimal_plans_skip_with_a_record(self):
        self.assertIn("Council: skipped — minimal plan", self.council)

    def test_council_asks_no_questions(self):
        self.assertNotIn("questions:\n  - header:", self.council)


class TestExamineGates(unittest.TestCase):
    def setUp(self):
        self.text = _read("steps/step-04-examine.md")

    def test_skeptic_reports_defects_only(self):
        self.assertIn("**Defects only.**", self.text)

    def test_security_check_uses_exactly_one_backend(self):
        security = _section(self.text, "**3.5 Security check", "### 4.")
        self.assertIn("exactly one backend", security)
        self.assertIn("outside economy mode", security)
        # /security-review diffs the branch against origin's default branch, so
        # uncommitted task work falls back to the lens's security floor.
        self.assertIn("git rev-parse --verify origin/HEAD", security)
        self.assertIn("every task change is committed", security)
        self.assertIn("Security floor", security)

    def test_quality_evidence_replaces_self_assessment(self):
        evidence = _section(self.text, "**Quality Evidence**", "**Deliverable Hygiene**")
        for artifact in ("Budget:", "Refine:", "Comments:", "Skills:"):
            with self.subTest(artifact=artifact):
                self.assertIn(artifact, evidence)


class TestEconomyFallbacks(unittest.TestCase):
    def test_council_and_refine_degrade_to_disclosed_self_checks(self):
        economy = _read("steps/step-00b-economy.md")
        self.assertIn("kill council", economy)
        self.assertIn("### Step 03b: Refine (Economy)", economy)
        self.assertIn("shared-context", economy)


if __name__ == "__main__":
    unittest.main()
