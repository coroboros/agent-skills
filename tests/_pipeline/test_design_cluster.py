"""Pipeline contract: award-design → design-system.

award-design produces DESIGN.md (Google's open standard — YAML frontmatter
with design tokens + 8 ordered prose sections). design-system governs that
file via audit/diff/export/spec/migrate/init/audit-extensions subcommands.
Schema drift between producer and consumer is the failure mode this cluster
prevents.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _contracts import CLUSTERS, SKILLS_DIR, read_skill_md  # noqa: E402

DESIGN = CLUSTERS["design"]

# award-design's DESIGN.md contract spans the lean SKILL.md plus its format
# references — the rebuild moved the token / section / namespace detail out of
# the forcing body into design-md-anatomy.md and foundations.md. Read the
# producer's full contract surface so producer↔consumer drift still breaks here.
AWARD_REFS = ("design-md-anatomy.md", "foundations.md")


def _award_design_contract_text() -> str:
    text = read_skill_md("award-design")
    refs_dir = SKILLS_DIR / "award-design" / "references"
    for ref in AWARD_REFS:
        text += "\n" + (refs_dir / ref).read_text(encoding="utf-8")
    return text


class TestProducerCommitsToGoogleStandard(unittest.TestCase):
    def test_award_design_references_google_standard(self):
        text = read_skill_md("award-design")
        self.assertIn("DESIGN.md", text)
        # Producer must explicitly reference the Google standard so changes
        # cannot drift to a custom format silently.
        self.assertRegex(text.lower(), r"google.*design\.md|google design")

    def test_award_design_lists_eight_canonical_sections(self):
        """The 8 prose sections in the Google standard (Overview, Colors,
        Typography, Layout, Elevation & Depth, Shapes, Components, Do's and
        Don'ts) must be enumerated so the consumer's audit has a fixed target."""
        text = _award_design_contract_text()
        for section in (
            "Overview",
            "Colors",
            "Typography",
            "Layout",
            "Components",
        ):
            with self.subTest(section=section):
                self.assertIn(section, text,
                              f"Google-standard section not documented: {section}")


class TestConsumerHandoff(unittest.TestCase):
    def test_design_system_documents_award_design_handoff(self):
        text = read_skill_md("design-system")
        self.assertIn("DESIGN.md", text)
        # design-system must document delegation to award-design when no
        # DESIGN.md exists — pins the empty-state handoff.
        self.assertIn("award-design", text)


class TestPortableActivation(unittest.TestCase):
    """design-system's portable description must make UI and DESIGN.md
    triggering discoverable without a harness-specific frontmatter key."""

    def test_design_system_description_covers_ui_and_design_md(self):
        text = read_skill_md("design-system")
        frontmatter = text.split("---", 2)[1]
        self.assertIn("description:", frontmatter)
        self.assertIn("DESIGN.md", frontmatter)
        self.assertIn("UI", frontmatter)
        self.assertNotIn("paths:", frontmatter)


class TestExtensionContract(unittest.TestCase):
    """Both skills must agree on the extension-tokens convention. Producer
    documents which extensions go in the YAML; consumer governs them via
    audit-extensions. The two SKILL.md files must converge on the same
    namespace list, the same components-canonical-only rule, and a shared
    cross-reference to the spec doc."""

    def test_both_skills_name_each_extension_namespace(self):
        producer = _award_design_contract_text()
        consumer = read_skill_md("design-system")
        for namespace in DESIGN["design_md_extension_namespaces"]:
            with self.subTest(namespace=namespace):
                self.assertIn(
                    namespace, producer,
                    f"award-design must name extension namespace `{namespace}`",
                )
                self.assertIn(
                    namespace, consumer,
                    f"design-system must name extension namespace `{namespace}`",
                )

    def test_both_skills_cross_reference_extended_tokens_md(self):
        # award-design's reference lives in its format refs (design-md-anatomy.md /
        # foundations.md), design-system's in its SKILL.md — check each where it lives.
        self.assertIn(
            "extended-tokens.md", _award_design_contract_text(),
            "award-design must cross-reference extended-tokens.md",
        )
        self.assertIn(
            "extended-tokens.md", read_skill_md("design-system"),
            "design-system must cross-reference extended-tokens.md",
        )

    def test_both_skills_register_audit_extensions(self):
        self.assertIn(
            "audit-extensions", _award_design_contract_text(),
            "award-design must register the audit-extensions subcommand",
        )
        self.assertIn(
            "audit-extensions", read_skill_md("design-system"),
            "design-system must register the audit-extensions subcommand",
        )

    def test_components_canonical_property_tokens_documented(self):
        """The closed set of 8 component property tokens must appear in
        award-design (so the agent producing DESIGN.md respects it). The
        list is the failure-mode contract."""
        producer = _award_design_contract_text()
        for token in DESIGN["design_md_canonical_property_tokens"]:
            with self.subTest(token=token):
                self.assertIn(
                    token, producer,
                    f"award-design must name canonical property token `{token}`",
                )


if __name__ == "__main__":
    unittest.main()
