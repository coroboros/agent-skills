"""award-design extension-token contract.

Pins the resolution of the synergy with /design-system: the produced DESIGN.md
uses the canonical 5 namespaces validated by the Google CLI plus top-level
extension namespaces (motion, shadows, aspectRatios, heights, containers,
breakpoints, zIndex, borderWidths, opacity, scrollTriggers) that are
preserved-but-unvalidated per the Google spec. Components bind ONLY to the 8
canonical property tokens — that is the empirical lint-failure mode this
contract prevents.

The rebuild moved this contract OUT of the SKILL.md body (which no longer
carries a Phase 3 / Tokens section) into the reference files — the lean body is
intentional. design-md-anatomy.md is the token-namespace authority;
foundations.md carries the same boundary at its Tokenization boundary. The
tests follow the content to those references; they do not re-bloat the body."""

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_MD = REPO_ROOT / "skills" / "award-design" / "SKILL.md"
ANATOMY_MD = REPO_ROOT / "skills" / "award-design" / "references" / "design-md-anatomy.md"
FOUNDATIONS_MD = REPO_ROOT / "skills" / "award-design" / "references" / "foundations.md"

sys.path.insert(0, str(REPO_ROOT / "tests" / "_pipeline"))
from _contracts import CLUSTERS  # noqa: E402

DESIGN = CLUSTERS["design"]


def _body():
    return SKILL_MD.read_text(encoding="utf-8")


def _anatomy():
    return ANATOMY_MD.read_text(encoding="utf-8")


def _foundations():
    return FOUNDATIONS_MD.read_text(encoding="utf-8")


class TestAnatomyTokenContract(unittest.TestCase):
    """design-md-anatomy.md is the token-namespace authority the SKILL.md body
    points at. The full extension contract must be explicit there — leaving it
    to inference reproduces the field-tested lint failure."""

    def test_lists_canonical_5_namespaces(self):
        anatomy = _anatomy()
        for namespace in DESIGN["design_md_token_groups"]:
            with self.subTest(namespace=namespace):
                self.assertIn(
                    namespace, anatomy,
                    f"anatomy must name canonical namespace `{namespace}`",
                )

    def test_lists_extension_namespaces(self):
        """Without extension names enumerated, agents invent (or omit) them."""
        anatomy = _anatomy()
        for namespace in DESIGN["design_md_extension_namespaces"]:
            with self.subTest(namespace=namespace):
                self.assertIn(
                    namespace, anatomy,
                    f"anatomy must name extension namespace `{namespace}`",
                )

    def test_lists_all_eight_canonical_property_tokens(self):
        """The closed property-token set — anything outside it is rejected."""
        anatomy = _anatomy()
        for token in DESIGN["design_md_canonical_property_tokens"]:
            with self.subTest(token=token):
                self.assertIn(
                    token, anatomy,
                    f"anatomy must name canonical property token `{token}`",
                )

    def test_states_components_canonical_only_rule(self):
        """Components binding to extension namespaces was the field-tested lint
        failure mode. The anatomy must explicitly forbid it."""
        anatomy = _anatomy().lower()
        self.assertRegex(
            anatomy,
            r"(8|eight)\s+canonical\s+property\s+tokens",
            "anatomy must state the components-bind-only-to-8-canonical-property-tokens rule",
        )
        self.assertRegex(
            anatomy,
            r"never as `?components:?`?\s*keys|referenced from prose only",
            "anatomy must forbid binding extension tokens as component keys",
        )

    def test_cross_references_extended_tokens_md(self):
        self.assertIn(
            "extended-tokens.md", _anatomy(),
            "anatomy must cross-reference the shared extended-tokens.md convention",
        )

    def test_documents_audit_extensions_step(self):
        """The bidirectional drift check is the validator the agent must know to run."""
        self.assertIn("audit-extensions", _anatomy())


class TestFoundationsTokenizationBoundary(unittest.TestCase):
    """foundations.md restates the same tokenization boundary at its
    Tokenization boundary section — the canon the build draws on ambiently. The
    two references must agree on the closed property-token set and the validator,
    so a build reading either lands on the same contract."""

    def _boundary(self):
        m = re.search(
            r"^## Tokenization boundary\s*\n(.*?)(?=^##\s)",
            _foundations(), re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(m, "foundations.md missing ## Tokenization boundary section")
        return m.group(1)

    def test_boundary_names_canonical_5_and_property_tokens(self):
        boundary = self._boundary()
        for namespace in DESIGN["design_md_token_groups"]:
            with self.subTest(namespace=namespace):
                self.assertIn(namespace, boundary,
                              f"tokenization boundary must name canonical namespace `{namespace}`")
        for token in DESIGN["design_md_canonical_property_tokens"]:
            with self.subTest(token=token):
                self.assertIn(token, boundary,
                              f"tokenization boundary must name property token `{token}`")

    def test_boundary_routes_to_extended_tokens_and_validator(self):
        boundary = self._boundary()
        self.assertIn("extended-tokens.md", boundary,
                      "tokenization boundary must route to extended-tokens.md")
        self.assertIn("audit-extensions", boundary,
                      "tokenization boundary must name the audit-extensions validator")


class TestProseSectionMapping(unittest.TestCase):
    """The DESIGN.md anatomy reference must map every award-grade narrative
    concept to one of the eight canonical Google sections — the requirement that
    nothing vital is dropped. SKILL.md points at this reference; the mapping
    lives there."""

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
        self.assertTrue(ANATOMY_MD.is_file(), "references/design-md-anatomy.md must exist")

    def test_skill_md_points_at_anatomy_reference(self):
        self.assertIn(
            "design-md-anatomy.md", _body(),
            "SKILL.md must cross-reference references/design-md-anatomy.md",
        )

    def test_anatomy_lists_all_narrative_concepts(self):
        anatomy = _anatomy()
        for narrative in self.REQUIRED_NARRATIVES:
            with self.subTest(narrative=narrative):
                self.assertIn(
                    narrative, anatomy,
                    f"prose-section mapping must host narrative concept: {narrative}",
                )

    def test_anatomy_specifies_the_signature_beat_table(self):
        """Motion is designed like an animator designs it — as beats, before
        code. The anatomy must carry the beat-table format the DESIGN.md's
        signature choreography is written in."""
        anatomy = _anatomy()
        self.assertIn("Signature beat table", anatomy)
        for column in ("Beat", "Trigger", "Element", "Transform", "Duration / ease"):
            with self.subTest(column=column):
                self.assertIn(column, anatomy,
                              f"beat table must carry the {column} column")

    def test_anatomy_lists_all_eight_canonical_sections(self):
        """Every canonical Google section must appear at least once in the
        anatomy mapping — otherwise the agent can't tell where to put content."""
        anatomy = _anatomy()
        for section in DESIGN["design_md_canonical_sections"]:
            with self.subTest(section=section):
                self.assertIn(
                    section, anatomy,
                    f"anatomy mapping must reference canonical section: {section}",
                )


class TestSkillBodyStaysLean(unittest.TestCase):
    """The rebuild deliberately kept the extension-token mechanics OUT of the
    SKILL.md body. The body routes to the references; it does not re-derive the
    contract. These assertions guard against re-bloating the body to satisfy a
    test — the body keeps only the pointer."""

    def test_body_routes_to_extended_tokens(self):
        """The body names the token-namespace requirement as a route, not an
        inline contract — the anatomy reference holds the actual detail."""
        self.assertIn("token namespaces", _body(),
                      "SKILL.md must name the token-namespace requirement as a route")

    def test_body_points_at_token_authority(self):
        self.assertIn("design-md-anatomy.md", _body(),
                      "SKILL.md must point at the token-namespace authority reference")

    def test_body_does_not_reintroduce_phase_3_tokens(self):
        """No `### Phase 3 — Tokens` heading may return — the contract lives in
        references now, and the body carries no phased workflow."""
        self.assertNotRegex(
            _body(), r"(?m)^###\s+Phase\s+3\s+—\s+Tokens",
            "the Phase 3 — Tokens section must not return to the SKILL.md body",
        )

    def test_body_does_not_inline_the_property_token_list(self):
        """The full 8-property-token enumeration belongs in the references; a
        body that re-lists all eight is re-bloating it. Guard against that by
        asserting the closed set is NOT enumerated in the body."""
        body = _body()
        inlined = sum(1 for t in DESIGN["design_md_canonical_property_tokens"] if t in body)
        self.assertLess(
            inlined, len(DESIGN["design_md_canonical_property_tokens"]),
            "SKILL.md must not re-list the full closed property-token set — "
            "that contract lives in the references",
        )


if __name__ == "__main__":
    unittest.main()
