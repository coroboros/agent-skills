"""award-design SKILL.md — extension-token contract.

Pins the Option C′ resolution of the synergy with /design-system: the produced
DESIGN.md uses the canonical 5 namespaces validated by the Google CLI plus
top-level extension namespaces (motion, shadows, aspectRatios, heights,
containers, breakpoints, zIndex, borderWidths, opacity, scrollTriggers) that
are preserved-but-unvalidated per the Google spec. Components bind ONLY to
the 8 canonical property tokens — that is the empirical lint-failure mode
this contract prevents.
"""

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_MD = REPO_ROOT / "skills" / "award-design" / "SKILL.md"
ANATOMY_MD = REPO_ROOT / "skills" / "award-design" / "references" / "design-md-anatomy.md"

sys.path.insert(0, str(REPO_ROOT / "tests" / "_pipeline"))
from _contracts import CLUSTERS  # noqa: E402

DESIGN = CLUSTERS["design"]


def _body():
    return SKILL_MD.read_text(encoding="utf-8")


def _anatomy():
    return ANATOMY_MD.read_text(encoding="utf-8")


class TestTokensPhaseReferences(unittest.TestCase):
    """Phase 3 (Tokens) is where the agent commits the inline token block (and,
    on Persist, the DESIGN.md). The extension contract must be explicit there —
    leaving it to inference reproduces the field-tested failure mode."""

    def setUp(self):
        body = _body()
        m = re.search(
            r"^### Phase 3 — Tokens(.*?)(?=^### Phase|\Z|^##\s)",
            body, re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(m, "Phase 3 (Tokens) missing or mis-numbered")
        self.phase_3 = m.group(1)

    def test_phase_3_lists_canonical_5_namespaces(self):
        for namespace in DESIGN["design_md_token_groups"]:
            with self.subTest(namespace=namespace):
                self.assertIn(
                    namespace, self.phase_3,
                    f"Phase 3 must name canonical namespace `{namespace}`",
                )

    def test_phase_3_lists_extension_namespaces(self):
        """Without extension names in Phase 3, agents invent (or omit) them."""
        for namespace in DESIGN["design_md_extension_namespaces"]:
            with self.subTest(namespace=namespace):
                self.assertIn(
                    namespace, self.phase_3,
                    f"Phase 3 must name extension namespace `{namespace}`",
                )

    def test_phase_3_states_components_canonical_only_rule(self):
        """Components binding to extension namespaces was the field-tested lint
        failure mode. Phase 3 must explicitly forbid it."""
        text = self.phase_3.lower()
        self.assertRegex(
            text,
            r"(8|eight)\s+canonical|canonical\s+property\s+tokens|8\s+property\s+tokens",
            "Phase 3 must state the components-bind-only-to-8-canonical-property-tokens rule",
        )

    def test_phase_3_cross_references_extended_tokens_md(self):
        self.assertIn(
            "extended-tokens.md", self.phase_3,
            "Phase 3 must cross-reference the shared extended-tokens.md convention",
        )

    def test_phase_3_documents_audit_extensions_step(self):
        """The bidirectional drift check is required after the canonical audit."""
        self.assertIn("audit-extensions", self.phase_3)


class TestProseSectionMapping(unittest.TestCase):
    """The DESIGN.md anatomy reference must map every award-grade narrative
    concept to one of the eight canonical Google sections — the user's
    explicit requirement that nothing vital is dropped. (Was checked against
    SKILL.md pre-refactor; content now lives in references/design-md-anatomy.md.)"""

    REQUIRED_NARRATIVES = (
        "Atmosphere",
        "Archetype",
        "Signature moment",
        "Photography direction",
        "Copy register",
        "Scroll choreography",
        "Micro-interactions",
        "Motion philosophy",
    )

    def test_anatomy_reference_file_exists(self):
        self.assertTrue(
            ANATOMY_MD.is_file(),
            "references/design-md-anatomy.md must exist after the refactor",
        )

    def test_skill_md_points_at_anatomy_reference(self):
        self.assertIn(
            "design-md-anatomy.md", _body(),
            "SKILL.md must cross-reference references/design-md-anatomy.md",
        )

    def test_anatomy_lists_all_narrative_concepts(self):
        body = _anatomy()
        for narrative in self.REQUIRED_NARRATIVES:
            with self.subTest(narrative=narrative):
                self.assertIn(
                    narrative, body,
                    f"prose-section mapping must host narrative concept: {narrative}",
                )

    def test_anatomy_lists_all_eight_canonical_sections(self):
        """Every canonical Google section must appear at least once in the
        anatomy mapping — otherwise the agent can't tell where to put content."""
        body = _anatomy()
        for section in DESIGN["design_md_canonical_sections"]:
            with self.subTest(section=section):
                self.assertIn(
                    section, body,
                    f"anatomy mapping must reference canonical section: {section}",
                )


class TestExtensionTokenInvariants(unittest.TestCase):
    """Top-level invariants the SKILL.md must carry, regardless of section."""

    def test_skill_references_extended_tokens_md(self):
        """Cross-skill reference — verifies the convention is hooked up to
        the shared spec doc, not re-derived inline."""
        self.assertIn("extended-tokens.md", _body())

    def test_skill_references_audit_extensions(self):
        """The validation subcommand must be named so the agent knows to run it."""
        self.assertIn("audit-extensions", _body())


if __name__ == "__main__":
    unittest.main()
