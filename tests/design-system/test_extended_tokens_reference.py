"""Pins the structure of extended-tokens.md and the SKILL.md / spec edits
that hook it into the design-system surface. This is documentation-as-contract:
the audit-extensions script and the cross-skill convention both depend on
the file's content matching the names the script encodes.
"""

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "design-system"
EXTENDED_TOKENS_MD = SKILL_DIR / "references" / "extended-tokens.md"
SKILL_MD = SKILL_DIR / "SKILL.md"
SPEC_MD = SKILL_DIR / "references" / "design-md-spec.md"
EXAMPLE_CLAUDE = SKILL_DIR / "references" / "example-claude.md"
SUBCOMMAND_AUDIT_EXT = SKILL_DIR / "references" / "subcommand-audit-extensions.md"
CLI_REFERENCE = SKILL_DIR / "references" / "cli-reference.md"
SUBCOMMAND_EXPORT = SKILL_DIR / "references" / "subcommand-export.md"

sys.path.insert(0, str(REPO_ROOT / "tests" / "_pipeline"))
from _contracts import CLUSTERS  # noqa: E402

DESIGN = CLUSTERS["design"]


class TestExtendedTokensReferenceExists(unittest.TestCase):
    def test_file_present(self):
        self.assertTrue(
            EXTENDED_TOKENS_MD.is_file(),
            "skills/design-system/references/extended-tokens.md must exist",
        )


class TestExtendedTokensContent(unittest.TestCase):
    def setUp(self):
        self.text = EXTENDED_TOKENS_MD.read_text(encoding="utf-8")

    def test_lists_all_curated_namespaces(self):
        for namespace in DESIGN["design_md_extension_namespaces"]:
            with self.subTest(namespace=namespace):
                self.assertIn(
                    namespace, self.text,
                    f"extended-tokens.md must document namespace `{namespace}`",
                )

    def test_lists_all_8_canonical_property_tokens(self):
        """Components-rule reminder — the closed set must be enumerated."""
        for token in DESIGN["design_md_canonical_property_tokens"]:
            with self.subTest(token=token):
                self.assertIn(
                    token, self.text,
                    f"extended-tokens.md must name canonical property token `{token}`",
                )

    def test_documents_components_anti_pattern(self):
        """The empirical field-tested failure mode (components.modal.shadow:
        "{shadows.lifted}") must be called out as the anti-pattern."""
        self.assertIn("modal.shadow", self.text)

    def test_provides_css_mirror_table(self):
        """The 1:1 namespace → CSS prefix mapping is the contract the
        audit-extensions script encodes — drift breaks the script."""
        for prefix in (
            "--shadow-",
            "--aspect-",
            "--height-",
            "--container-",
            "--breakpoint-",
            "--z-",
            "--border-",
            "--opacity-",
            "--scroll-",
        ):
            with self.subTest(prefix=prefix):
                self.assertIn(
                    prefix, self.text,
                    f"extended-tokens.md mapping table must list CSS prefix `{prefix}`",
                )
        # Motion has two prefixes (durations + easings) handled specially
        self.assertIn("--duration-", self.text)
        self.assertIn("--ease-", self.text)

    def test_references_google_spec_extension_section(self):
        """Authority cite — extensions are spec-blessed, not a fork."""
        self.assertIn("design-md-spec.md", self.text)


class TestSkillMdRulesBullet(unittest.TestCase):
    """The Rules section must carry the extended-tokens bullet — that's how
    auto-activated UI edits learn the convention without having to read the
    full reference."""

    def setUp(self):
        self.text = SKILL_MD.read_text(encoding="utf-8")

    def test_rules_section_documents_extended_tokens(self):
        # The Rules bullet must name the extension namespaces and the rule.
        self.assertIn("Extended tokens", self.text)
        self.assertIn("MUST NOT bind to extension namespaces", self.text)

    def test_subcommand_routing_includes_audit_extensions(self):
        """The subcommand routing table must register audit-extensions."""
        self.assertIn("audit-extensions", self.text)
        self.assertIn("subcommand-audit-extensions.md", self.text)

    def test_argument_hint_includes_audit_extensions(self):
        m = re.search(r'argument-hint:\s*"([^"]+)"', self.text)
        self.assertIsNotNone(m, "argument-hint missing from frontmatter")
        self.assertIn(
            "audit-extensions", m.group(1),
            "audit-extensions must be discoverable via argument-hint",
        )


class TestSpecMdExtendingRules(unittest.TestCase):
    """The Google-spec snapshot's 'Rules when extending' must carry the
    components-canonical-only bullet so spec readers see the field-tested rule."""

    def setUp(self):
        self.text = SPEC_MD.read_text(encoding="utf-8")

    def test_components_canonical_rule_documented(self):
        # The bullet must name the closed set rule explicitly.
        self.assertRegex(
            self.text,
            r"closed set of 8 component property tokens|MUST stay within the closed set",
            "design-md-spec.md must carry the components-canonical-only rule",
        )

    def test_cross_references_extended_tokens_md(self):
        self.assertIn("extended-tokens.md", self.text)


class TestSubcommandAuditExtensionsReference(unittest.TestCase):
    def test_reference_file_exists(self):
        self.assertTrue(
            SUBCOMMAND_AUDIT_EXT.is_file(),
            "skills/design-system/references/subcommand-audit-extensions.md must exist",
        )

    def test_reference_documents_three_drift_rules(self):
        text = SUBCOMMAND_AUDIT_EXT.read_text(encoding="utf-8")
        for rule in (
            "extension-missing-css",
            "extension-orphan-css",
            "extension-broken-ref",
        ):
            with self.subTest(rule=rule):
                self.assertIn(
                    rule, text,
                    f"audit-extensions reference must document drift rule `{rule}`",
                )


class TestCliReferenceProjectSideRules(unittest.TestCase):
    """cli-reference.md must distinguish Google CLI rules from
    project-side audit-extensions rules — same severity vocabulary, different
    source."""

    def setUp(self):
        self.text = CLI_REFERENCE.read_text(encoding="utf-8")

    def test_project_side_rules_table_present(self):
        self.assertIn("audit-extensions", self.text)
        for rule in (
            "extension-missing-css",
            "extension-orphan-css",
            "extension-broken-ref",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, self.text)


class TestSubcommandExportExtensions(unittest.TestCase):
    def test_export_documents_extended_tokens_section(self):
        text = SUBCOMMAND_EXPORT.read_text(encoding="utf-8")
        self.assertIn("Extended-token export", text)
        self.assertIn("audit-extensions", text)


class TestExampleClaudeShowcasesExtensions(unittest.TestCase):
    """example-claude.md is the Editorial archetype's worked example — the
    pedagogical artifact agents read when in doubt. It must demonstrate at
    least one extension namespace so the convention is concrete, not theoretical."""

    def setUp(self):
        self.text = EXAMPLE_CLAUDE.read_text(encoding="utf-8")

    def test_yaml_includes_at_least_one_extension(self):
        # Pick `motion:` as a top-level YAML key.
        self.assertRegex(
            self.text,
            r"(?m)^motion:\s*$",
            "example-claude.md must include at least one extension namespace (motion)",
        )

    def test_dos_donts_warns_against_component_binding(self):
        """The Don't-bind-extensions-to-components rule must appear in the
        Editorial example's Do's and Don'ts so the lesson is reinforced."""
        self.assertIn("extended-tokens.md", self.text)


if __name__ == "__main__":
    unittest.main()
