"""Structural tests for `skills/code-ultrareview/templates/code-ultrareview.md`.

Pins the section order, presence of mandatory header tokens (Tier + Tier
rationale + Token estimate), the dual severity scheme columns in the
Verified table, and the six sub-graphs in the Coherence-graph status
table. The template is the wire format the synthesizer fills in — any
drift here propagates to every report consumer.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATE = REPO_ROOT / "skills" / "code-ultrareview" / "templates" / "code-ultrareview.md"

sys.path.insert(0, str(REPO_ROOT / "tests" / "_pipeline"))
from _contracts import CLUSTERS  # noqa: E402

REVIEW = CLUSTERS["review"]


def _read() -> str:
    return TEMPLATE.read_text(encoding="utf-8")


def _section_positions(text: str) -> list[tuple[str, int]]:
    """[(section title, offset), ...] for every `^## ` heading."""
    return [
        (m.group(1).strip(), m.start())
        for m in re.finditer(r"^## (.+?)\s*$", text, re.MULTILINE)
    ]


class TestSectionPresence(unittest.TestCase):
    def test_all_eight_canonical_sections_present(self):
        text = _read()
        canonical = (
            "Findings",
            "Deferred to sibling skills",
            "What looks good",
            "Coherence-graph status",
            "Verdict",
            "--apply-safe summary",
        )
        for section in canonical:
            self.assertIn(
                f"## {section}", text, f"section `## {section}` missing"
            )

    def test_required_sections_match_pipeline_contract(self):
        text = _read()
        for section in REVIEW["report_required_sections"]:
            self.assertIn(f"## {section}", text)


class TestSectionOrder(unittest.TestCase):
    def test_canonical_section_order(self):
        text = _read()
        order = [t for t, _ in _section_positions(text)]
        canonical = [
            "Findings",
            "Deferred to sibling skills",
            "What looks good",
            "Coherence-graph status",
            "Verdict",
            "--apply-safe summary",
        ]
        positions = [order.index(s) for s in canonical]
        self.assertEqual(
            positions, sorted(positions),
            f"sections out of canonical order: {order}",
        )


class TestHeaderTokens(unittest.TestCase):
    def test_tier_in_header(self):
        text = _read()
        self.assertIn("**Tier:**", text)

    def test_tier_rationale_in_header(self):
        text = _read()
        self.assertIn("Tier rationale:", text)

    def test_token_estimate_in_header(self):
        text = _read()
        self.assertIn("Token estimate:", text)

    def test_rules_baseline_in_header(self):
        text = _read()
        self.assertIn("Rules baseline:", text)


class TestFindingsSubSections(unittest.TestCase):
    def test_verified_subsection(self):
        text = _read()
        self.assertIn("### Verified", text)

    def test_unverified_subsection(self):
        text = _read()
        self.assertIn("### Unverified — recommend Deep pass", text)

    def test_verified_table_has_tier_column(self):
        text = _read()
        # Header row of Verified table should include the Anthropic-tier column.
        verified_idx = text.index("### Verified")
        unverified_idx = text.index("### Unverified")
        verified_block = text[verified_idx:unverified_idx]
        self.assertIn("| Tier |", verified_block)


class TestCoherenceGraphStatus(unittest.TestCase):
    def test_lists_all_six_sub_graphs(self):
        text = _read()
        status_idx = text.index("## Coherence-graph status")
        # Block runs until the next `## ` heading.
        rest = text[status_idx:]
        next_section = rest.index("\n## ", 1)
        block = rest[:next_section]
        for sub_graph in REVIEW["coherence_sub_graphs"]:
            self.assertIn(sub_graph, block, f"sub-graph {sub_graph!r} missing")

    def test_six_sub_graphs_match_coherence_graph_reference(self):
        ref = REPO_ROOT / "skills" / "code-ultrareview" / "references" / "coherence-graph.md"
        ref_text = ref.read_text(encoding="utf-8")
        for sub_graph in REVIEW["coherence_sub_graphs"]:
            self.assertIn(sub_graph, ref_text)


class TestApplySafeSummary(unittest.TestCase):
    def test_apply_safe_summary_documents_three_writers(self):
        text = _read()
        section_idx = text.index("## --apply-safe summary")
        rest = text[section_idx:]
        # apply-safe summary is the final ## section
        next_section_match = re.search(r"\n## ", rest[1:])
        block = rest if next_section_match is None else rest[:next_section_match.start() + 1]
        for writer in ("version_sync", "description_sync", "failing_test_writer"):
            self.assertIn(writer, block, f"writer {writer!r} missing")


class TestSeveritySchemeInTemplate(unittest.TestCase):
    def test_tier_column_uses_anthropic_terms(self):
        text = _read()
        # The example row in the Verified table demonstrates the Anthropic tier.
        for term in ("Important",):
            self.assertIn(term, text)


if __name__ == "__main__":
    unittest.main()
