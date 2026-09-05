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
        self.assertIn("do not claim completion", self.ref)
        self.assertIn("outside authorization", self.ref)
        self.assertIn("reversible implementation details", self.ref)

    def test_reference_cites_upstream_canonical(self):
        self.assertIn("requires no sibling skill or analyzer", self.ref)

    def test_upstream_canonical_actually_exists(self):
        """The cited upstream file exists in this repo."""
        self.assertTrue(
            UPSTREAM_REF.exists(),
            "Cited upstream taxonomy file must exist",
        )

    def test_reference_documents_detection_protocol(self):
        for source in ("committed", "staged", "unstaged", "untracked", "initial worktree status"):
            self.assertIn(source, self.ref)

    def test_reference_documents_inline_fallback(self):
        self.assertIn("02-plan.md", self.ref)
        self.assertIn("already satisfied before", self.ref)
        self.assertIn("do not cap", self.ref)

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
