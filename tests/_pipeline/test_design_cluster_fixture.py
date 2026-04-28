"""Pipeline contract: award-design → design-system, FIXTURE-BASED.

A realistic DESIGN.md (Google standard — frontmatter tokens + 8 prose
sections in canonical order) must be parseable by the consumer's
expectations. This locks the schema contract end-to-end without
requiring the npx-backed audit.sh to run (that's covered by
tests/design-system/test_cli.py).

Pinning this in `_pipeline/` rather than per-skill catches drift on
EITHER side of the producer/consumer boundary in a single test.
"""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _contracts import CLUSTERS  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "skills" / "brand-voice" / "scripts"))
from utils import parse_yaml_minimal, split_frontmatter  # noqa: E402

FIXTURE = Path(__file__).parent / "fixtures" / "realistic_design.md"
DESIGN_CONTRACT = CLUSTERS["design"]


class TestFixtureExists(unittest.TestCase):
    def test_fixture_present(self):
        self.assertTrue(
            FIXTURE.is_file(),
            f"DESIGN.md fixture missing: {FIXTURE}",
        )

    def test_fixture_is_non_trivial(self):
        text = FIXTURE.read_text(encoding="utf-8")
        # A meaningful fixture has more than minimal scaffolding.
        self.assertGreater(
            len(text), 500,
            "fixture is too small to exercise the schema realistically",
        )


class TestFixtureFrontmatter(unittest.TestCase):
    """Producer's frontmatter must carry the token groups consumer expects."""

    def setUp(self):
        text = FIXTURE.read_text(encoding="utf-8")
        fm_text, _ = split_frontmatter(text)
        self.assertIsNotNone(fm_text, "fixture missing YAML frontmatter")
        self.fm = parse_yaml_minimal(fm_text)

    def test_each_token_group_present(self):
        for group in DESIGN_CONTRACT["design_md_token_groups"]:
            with self.subTest(group=group):
                self.assertIn(
                    group, self.fm,
                    f"frontmatter missing token group `{group}` "
                    f"(consumer audit will flag this as broken-ref)",
                )


class TestFixtureSectionsCanonicalOrder(unittest.TestCase):
    """Producer's prose body must contain the 8 canonical sections in order.
    Consumer expects this layout for diff/migrate/export to function."""

    def setUp(self):
        text = FIXTURE.read_text(encoding="utf-8")
        _, body = split_frontmatter(text)
        self.body = body
        self.canonical = list(DESIGN_CONTRACT["design_md_canonical_sections"])

    def test_each_section_is_h2(self):
        for section in self.canonical:
            with self.subTest(section=section):
                pattern = rf"^##\s+{re.escape(section)}\s*$"
                self.assertIsNotNone(
                    re.search(pattern, self.body, re.MULTILINE),
                    f"section '{section}' not present at H2 in fixture",
                )

    def test_sections_in_canonical_order(self):
        positions = []
        for section in self.canonical:
            m = re.search(rf"^##\s+{re.escape(section)}\s*$",
                          self.body, re.MULTILINE)
            self.assertIsNotNone(m, f"section missing: {section}")
            positions.append((m.start(), section))
        ordered = [s for _, s in sorted(positions)]
        self.assertEqual(
            ordered, self.canonical,
            f"sections out of canonical order: {ordered}",
        )

    def test_no_extra_h2_sections_beyond_canonical(self):
        """Stray H2 sections (e.g. legacy 'Tokens') would confuse the
        consumer's audit which expects exactly 8. Pin to the canonical set."""
        h2s = re.findall(r"^##\s+(.+?)\s*$", self.body, re.MULTILINE)
        unexpected = set(h2s) - set(self.canonical)
        self.assertEqual(
            unexpected, set(),
            f"fixture has H2 sections beyond the canonical 8: {sorted(unexpected)}",
        )


class TestSpecCommitsToCanonicalKeys(unittest.TestCase):
    """The cluster contract in `_contracts.py` declares the 8 canonical
    sections. If a producer evolves the format (e.g., adds a section),
    that change must propagate to the contract OR to the producer's
    SKILL.md, not silently drift in fixtures."""

    def test_contract_lists_eight_sections(self):
        sections = DESIGN_CONTRACT["design_md_canonical_sections"]
        self.assertEqual(
            len(sections), 8,
            f"design cluster contract should list exactly 8 sections, "
            f"got {len(sections)}: {sections}",
        )

    def test_contract_lists_token_groups(self):
        groups = DESIGN_CONTRACT["design_md_token_groups"]
        # The Google standard requires at least colors + typography + spacing.
        for required in ("colors", "typography", "spacing"):
            with self.subTest(group=required):
                self.assertIn(required, groups,
                              f"contract missing required token group: {required}")


# --- Adversarial fixtures ----------------------------------------------------
#
# A schema test that only validates the happy fixture proves the schema
# accepts good input — it does NOT prove the schema rejects bad input.
# These tests run the same structural checks against malformed fixtures
# and assert the checks correctly identify the problem. Together with the
# happy-path tests above, this gives the cluster a proper schema audit
# without requiring the consumer's npx-backed audit.sh to run.

FIXTURES_DIR = Path(__file__).parent / "fixtures"
MALFORMED_MISSING_TOKEN = FIXTURES_DIR / "malformed_missing_token.md"
MALFORMED_OUT_OF_ORDER = FIXTURES_DIR / "malformed_out_of_order.md"
MALFORMED_EXTRA_SECTION = FIXTURES_DIR / "malformed_extra_section.md"


def _frontmatter_and_body(path: Path):
    text = path.read_text(encoding="utf-8")
    fm_text, body = split_frontmatter(text)
    return parse_yaml_minimal(fm_text), body


class TestAdversarialMissingToken(unittest.TestCase):
    """Adversarial fixture: frontmatter omits the `spacing` token group.
    The schema check (`test_each_token_group_present` in the happy class)
    must FAIL on this input — verifying the check actually discriminates."""

    def test_fixture_present(self):
        self.assertTrue(MALFORMED_MISSING_TOKEN.is_file())

    def test_schema_check_detects_missing_token_group(self):
        fm, _ = _frontmatter_and_body(MALFORMED_MISSING_TOKEN)
        missing = [g for g in DESIGN_CONTRACT["design_md_token_groups"]
                   if g not in fm]
        self.assertIn(
            "spacing", missing,
            "fixture is supposed to omit `spacing` — adjust fixture or "
            "the contract's required token list",
        )
        # The schema rule says required groups (colors, typography, spacing)
        # MUST all be present. This fixture violates by missing one — the
        # check is therefore discriminating.
        self.assertGreater(
            len(missing), 0,
            "missing-token fixture didn't actually miss any tokens",
        )


class TestAdversarialOutOfOrder(unittest.TestCase):
    """Adversarial fixture: H2 sections present but in non-canonical order
    (Typography before Colors). The order check must catch this."""

    def test_fixture_present(self):
        self.assertTrue(MALFORMED_OUT_OF_ORDER.is_file())

    def test_order_check_detects_swap(self):
        _, body = _frontmatter_and_body(MALFORMED_OUT_OF_ORDER)
        canonical = list(DESIGN_CONTRACT["design_md_canonical_sections"])
        positions = []
        for section in canonical:
            m = re.search(rf"^##\s+{re.escape(section)}\s*$",
                          body, re.MULTILINE)
            if m:
                positions.append((m.start(), section))
        ordered = [s for _, s in sorted(positions)]
        # The swap (Typography before Colors) means `ordered` differs from
        # `canonical`. If the check is genuinely discriminating, this MUST
        # not equal the canonical list.
        self.assertNotEqual(
            ordered, canonical,
            "out-of-order fixture passes the order check — fixture or "
            "check is not actually discriminating",
        )


class TestAdversarialExtraSection(unittest.TestCase):
    """Adversarial fixture: all 8 canonical sections plus an extra `Tokens`
    H2. The 'no extra H2 sections' check must detect the stray heading."""

    def test_fixture_present(self):
        self.assertTrue(MALFORMED_EXTRA_SECTION.is_file())

    def test_extra_section_check_detects_stray_h2(self):
        _, body = _frontmatter_and_body(MALFORMED_EXTRA_SECTION)
        h2s = re.findall(r"^##\s+(.+?)\s*$", body, re.MULTILINE)
        canonical = set(DESIGN_CONTRACT["design_md_canonical_sections"])
        unexpected = set(h2s) - canonical
        self.assertEqual(
            unexpected, {"Tokens"},
            f"extra-section fixture should yield exactly {{Tokens}}, "
            f"got: {unexpected}",
        )


if __name__ == "__main__":
    unittest.main()
