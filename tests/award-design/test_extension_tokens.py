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

sys.path.insert(0, str(REPO_ROOT / "tests" / "_pipeline"))
from _contracts import CLUSTERS  # noqa: E402

DESIGN = CLUSTERS["design"]


def _body():
    return SKILL_MD.read_text(encoding="utf-8")


class TestStep6References(unittest.TestCase):
    """Step 6 (Produce DESIGN.md) is where the agent decides what goes in
    the file. The extension contract must be explicit there — leaving it to
    inference reproduces the field-tested failure mode."""

    def setUp(self):
        body = _body()
        m = re.search(
            r"^6\.\s+\*\*Produce DESIGN\.md\*\*(.*?)(?=^\d+\.\s+\*\*|\Z)",
            body, re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(m, "step 6 (Produce DESIGN.md) missing or mis-numbered")
        self.step_6 = m.group(1)

    def test_step_6_lists_canonical_5_namespaces(self):
        for namespace in DESIGN["design_md_token_groups"]:
            with self.subTest(namespace=namespace):
                self.assertIn(
                    namespace, self.step_6,
                    f"step 6 must name canonical namespace `{namespace}`",
                )

    def test_step_6_lists_extension_namespaces(self):
        """Without extension names in step 6, agents invent (or omit) them."""
        for namespace in DESIGN["design_md_extension_namespaces"]:
            with self.subTest(namespace=namespace):
                self.assertIn(
                    namespace, self.step_6,
                    f"step 6 must name extension namespace `{namespace}`",
                )

    def test_step_6_states_components_canonical_only_rule(self):
        """Components binding to extension namespaces was the field-tested lint
        failure mode. Step 6 must explicitly forbid it."""
        text = self.step_6.lower()
        # Either phrasing: "8 canonical" / "canonical property tokens" /
        # "8 property tokens" — pin the rule's existence with a flexible match.
        self.assertRegex(
            text,
            r"(8|eight)\s+canonical|canonical\s+property\s+tokens|8\s+property\s+tokens",
            "step 6 must state the components-bind-only-to-8-canonical-property-tokens rule",
        )

    def test_step_6_cross_references_extended_tokens_md(self):
        self.assertIn(
            "extended-tokens.md", self.step_6,
            "step 6 must cross-reference the shared extended-tokens.md convention",
        )

    def test_step_6_documents_audit_extensions_step(self):
        """The bidirectional drift check is required after the canonical audit."""
        self.assertIn("audit-extensions", self.step_6)


class TestProseSectionMapping(unittest.TestCase):
    """The DESIGN.md anatomy section must map every award-grade narrative
    concept to one of the eight canonical Google sections — the user's
    explicit requirement that nothing vital is dropped."""

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

    def test_anatomy_section_exists(self):
        self.assertIn("DESIGN.md anatomy", _body())

    def test_anatomy_lists_all_narrative_concepts(self):
        body = _body()
        for narrative in self.REQUIRED_NARRATIVES:
            with self.subTest(narrative=narrative):
                self.assertIn(
                    narrative, body,
                    f"prose-section mapping must host narrative concept: {narrative}",
                )

    def test_anatomy_lists_all_eight_canonical_sections(self):
        """Every canonical Google section must appear at least once in the
        anatomy mapping — otherwise the agent can't tell where to put content."""
        body = _body()
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
