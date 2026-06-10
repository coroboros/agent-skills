"""Tests for the derivation lens in step-04 eXamine.

Verifies the reference file taxonomy + severity rules + detection protocol,
step-04's invocation sub-step ordering, removal of the legacy AC checklist,
and the template-level placeholder.

Test approach. Apex is a prose-driven skill — no `apex.sh` / `apex.py`
entrypoint to subprocess-invoke. Per `.agents/rules/skill-authoring.md`
§ Testing, the convention for prompt-driven skills is structural tests
over runtime subprocess tests. The assertions below verify that the
reference file declares the taxonomy and the detection protocol, and
that step-04 places the lens sub-step before typecheck. Runtime
invocation of the lens (orchestrator detection, inline fallback) is
exercised by actual `/apex` invocations and by the code-ultrareview
skill's own subprocess tests over its Python orchestrator.
"""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REF = REPO_ROOT / "skills" / "apex" / "references" / "derivation-lens.md"
STEP_04 = REPO_ROOT / "skills" / "apex" / "steps" / "step-04-examine.md"
TEMPLATE_04 = REPO_ROOT / "skills" / "apex" / "templates" / "04-examine.md"
UPSTREAM_REF = REPO_ROOT / "skills" / "code-ultrareview" / "references" / "axes" / "intent.md"


class TestDerivationLensReference(unittest.TestCase):
    def setUp(self):
        self.ref = REF.read_text(encoding="utf-8")
        self.step_04 = STEP_04.read_text(encoding="utf-8")
        self.template_04 = TEMPLATE_04.read_text(encoding="utf-8")

    def test_reference_file_exists(self):
        self.assertTrue(REF.exists(), f"{REF} missing")

    def test_reference_declares_all_four_classifications(self):
        for cls in ("GAP", "SCOPE-ADD", "DECISION-OVERRIDE", "CONSISTENT"):
            self.assertIn(cls, self.ref, f"Reference must declare {cls}")

    def test_reference_severity_rules_documented(self):
        """GAP blocks, SCOPE-ADD advisory, DECISION-OVERRIDE surfaces."""
        self.assertIn("Block completion", self.ref, "GAP-block rule must be documented")
        self.assertTrue(
            "Advisory" in self.ref or "advisory" in self.ref,
            "SCOPE-ADD advisory rule must be documented",
        )
        self.assertIn(
            "Surface for user judgment",
            self.ref,
            "DECISION-OVERRIDE surface rule must be documented",
        )

    def test_reference_cites_upstream_canonical(self):
        """Reference cites code-ultrareview's Intent axis brief as canonical taxonomy."""
        self.assertIn(
            "code-ultrareview/references/axes/intent.md",
            self.ref,
            "Reference must cite the upstream canonical taxonomy",
        )

    def test_upstream_canonical_actually_exists(self):
        """The cited upstream file exists in this repo."""
        self.assertTrue(
            UPSTREAM_REF.exists(),
            "Cited upstream taxonomy file must exist",
        )

    def test_reference_documents_detection_protocol(self):
        """Detection protocol mentions the code-ultrareview orchestrator path."""
        self.assertIn(
            "code-ultrareview/scripts/derivation/run.py",
            self.ref,
            "Detection protocol must reference the Python orchestrator path",
        )

    def test_reference_documents_inline_fallback(self):
        """Inline fallback protocol is documented for when the orchestrator is absent."""
        self.assertIn("Inline protocol", self.ref)
        self.assertIn("02-plan.md", self.ref, "Inline protocol must reference the plan file")
        self.assertIn("git diff", self.ref, "Inline protocol must reference git diff")

    def test_step_04_invokes_derivation_lens_before_typecheck(self):
        """step-04 § 3.0 Derivation lens appears BEFORE § 3.1 Typecheck."""
        idx_lens = self.step_04.find("3.0 Derivation lens")
        idx_typecheck = self.step_04.find("3.1 Typecheck")
        self.assertGreater(idx_lens, 0, "Derivation lens sub-step missing from step-04")
        self.assertGreater(idx_typecheck, idx_lens, "Derivation lens must precede typecheck")

    def test_step_04_documents_gap_blocking(self):
        """Step-04 documents that GAP findings block completion."""
        # Slice the new 3.0 sub-step from step-04
        idx_lens = self.step_04.find("3.0 Derivation lens")
        idx_typecheck = self.step_04.find("3.1 Typecheck", idx_lens)
        body = self.step_04[idx_lens:idx_typecheck]
        self.assertIn("GAP", body, "GAP classification must appear in the lens sub-step")
        self.assertTrue(
            "blocks" in body.lower() or "block" in body.lower(),
            "GAP-block behaviour must be documented in step-04",
        )

    def test_step_04_drops_legacy_ac_checkbox_template(self):
        """Legacy `[✓] AC1: Verified by [how]` template must NOT survive."""
        self.assertNotIn(
            "[✓] AC1: Verified by [how]",
            self.step_04,
            "Legacy AC verification checkbox must be removed from step-04",
        )

    def test_step_04_drops_legacy_ac_subsection_in_self_audit(self):
        """The `**Acceptance Criteria:**` sub-section of Self-Audit must NOT survive."""
        self.assertNotIn(
            "**Acceptance Criteria:**\n- [ ] Each AC demonstrably met",
            self.step_04,
            "Legacy AC self-audit checklist must be removed; lens supersets it",
        )

    def test_template_carries_derivation_lens_section(self):
        """templates/04-examine.md carries the derivation-lens placeholder."""
        self.assertIn(
            "## Derivation Lens",
            self.template_04,
        )


if __name__ == "__main__":
    unittest.main()
