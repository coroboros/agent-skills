"""Structural tests for `skills/code-ultrareview/templates/code-ultrareview.md`.

Pins the section order, the canonical emoji prefix on every `##` heading, the
`---` separator above every `##` section, the four mandatory severity
sub-sections inside `## 🔎 Findings` (### 🔴 High / ### 🟠 Medium /
### 🟢 Low / ### ⚠️ Unverified — each rendered even when count is 0), the
header tokens (Scope + Estimated wall-clock), the dual severity scheme columns
in the verified tables, and the six sub-graphs in the Coherence-graph status
table. The template is the wire format the synthesizer fills in — any drift
here propagates to every report consumer.
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


# All canonical top-level `##` sections in canonical order, including their
# mandatory emoji prefix. Drift in this tuple fails both the presence and
# ordering tests below; mirror updates to
# `tests/_pipeline/_contracts.py::CLUSTERS["review"]["report_required_sections"]`
# (which intentionally omits `--apply-safe summary` — it's opt-in).
CANONICAL_SECTIONS = (
    "📋 Lens summary",
    "🔎 Findings",
    "🧭 Deferred to sibling skills",
    "✅ What looks good",
    "🕸️ Coherence-graph status",
    "📐 Derivation coverage",
    "⚖️ Verdict",
    "🛠️ Action plan",
    "🪛 --apply-safe summary",
)

# Four mandatory sub-sections inside `## 🔎 Findings`, in render order. Mirror
# `_contracts.py::CLUSTERS["review"]["report_findings_subsections"]`.
FINDINGS_SUBSECTIONS = (
    "🔴 High",
    "🟠 Medium",
    "🟢 Low",
    "⚠️ Unverified",
)


class TestSectionPresence(unittest.TestCase):
    def test_all_canonical_sections_present(self):
        text = _read()
        for section in CANONICAL_SECTIONS:
            self.assertIn(
                f"## {section}", text, f"section `## {section}` missing"
            )

    def test_required_sections_match_pipeline_contract(self):
        text = _read()
        for section in REVIEW["report_required_sections"]:
            self.assertIn(f"## {section}", text)

    def test_no_plain_section_headings_without_emoji(self):
        """A plain `## Findings` or `## Verdict` etc. means the emoji prefix
        dropped off the heading — the regression this PR fixes. Catch it at
        the template level."""
        text = _read()
        plain_headings = (
            "## Lens summary",
            "## Findings",
            "## Deferred to sibling skills",
            "## What looks good",
            "## Coherence-graph status",
            "## Derivation coverage",
            "## Verdict",
            "## Action plan",
            "## --apply-safe summary",
        )
        for heading in plain_headings:
            # Use a regex anchored to a line so a plain `## Findings` line
            # would match, but `## 🔎 Findings` would not.
            pattern = re.compile(rf"^{re.escape(heading)}\s*$", re.MULTILINE)
            self.assertIsNone(
                pattern.search(text),
                f"plain heading `{heading}` is present — must carry its emoji prefix",
            )


class TestSectionOrder(unittest.TestCase):
    def test_canonical_section_order(self):
        text = _read()
        order = [t for t, _ in _section_positions(text)]
        positions = [order.index(s) for s in CANONICAL_SECTIONS]
        self.assertEqual(
            positions, sorted(positions),
            f"sections out of canonical order: {order}",
        )


class TestSectionSeparators(unittest.TestCase):
    """Every `##` section is preceded by a `---` horizontal-rule separator —
    the immediately-preceding non-blank line is `---`. The HR is the visual
    cue for scanning between sections."""

    def test_every_section_preceded_by_hr(self):
        text = _read()
        lines = text.splitlines()
        violations: list[str] = []
        for idx, line in enumerate(lines):
            if not line.startswith("## "):
                continue
            # Walk backwards to find the previous non-blank line.
            prev = idx - 1
            while prev >= 0 and lines[prev].strip() == "":
                prev -= 1
            if prev < 0 or lines[prev].strip() != "---":
                violations.append(
                    f"line {idx + 1} (`{line}`) — previous non-blank line is "
                    f"{lines[prev] if prev >= 0 else '(start of file)'!r}, "
                    "not `---`"
                )
        self.assertEqual(
            violations, [],
            "Sections missing `---` separator above:\n  " + "\n  ".join(violations),
        )


class TestHeaderTokens(unittest.TestCase):
    def test_scope_in_header(self):
        text = _read()
        self.assertIn("**Scope:**", text)

    def test_estimated_wall_clock_in_header(self):
        text = _read()
        self.assertIn("Estimated wall-clock:", text)

    def test_rules_baseline_in_header(self):
        text = _read()
        self.assertIn("Rules baseline:", text)

    def test_no_legacy_tier_header_field(self):
        # The old `**Tier:**` field is gone — only the Anthropic-severity
        # `| Tier |` column inside the per-severity findings tables remains.
        text = _read()
        self.assertNotIn("**Tier:**", text)
        self.assertNotIn("Tier rationale:", text)
        self.assertNotIn("Token estimate:", text)


class TestFindingsSubSections(unittest.TestCase):
    """The Findings section uses four per-severity sub-sections (one per
    severity tier plus Unverified), each emoji-prefixed. The regression that
    motivated this layout: the emoji prefix dropped off when the model
    improvised a per-severity split from the previous single-table layout."""

    def test_findings_uses_per_severity_subsections(self):
        text = _read()
        for sub in FINDINGS_SUBSECTIONS:
            self.assertIn(
                f"### {sub}", text,
                f"sub-section `### {sub}` missing from Findings",
            )

    def test_findings_subsections_appear_in_canonical_order(self):
        text = _read()
        offsets = [text.index(f"### {sub}") for sub in FINDINGS_SUBSECTIONS]
        self.assertEqual(
            offsets, sorted(offsets),
            f"Findings sub-sections out of order: {FINDINGS_SUBSECTIONS}",
        )

    def test_findings_subsections_match_pipeline_contract(self):
        text = _read()
        for sub in REVIEW["report_findings_subsections"]:
            self.assertIn(f"### {sub}", text)

    def test_findings_subsections_contained_within_findings_section(self):
        """The four sub-sections must sit INSIDE `## 🔎 Findings`, not under
        `## 🛠️ Action plan` or any other `##`. Closes the implicit-assumption
        gap where `assertIn(f"### {sub}", text)` would pass even if a
        sub-section slipped to a wrong parent section."""
        text = _read()
        # Find the `## 🔎 Findings` HEADING (line start), not any inline
        # backtick mention inside a blockquote.
        heading_match = re.search(r"^## 🔎 Findings\s*$", text, re.MULTILINE)
        if heading_match is None:
            self.fail("`## 🔎 Findings` heading not found in template")
        findings_idx = heading_match.start()
        # Block runs from heading to the next `## ` heading.
        rest = text[findings_idx:]
        next_h2 = re.search(r"^## ", rest[1:], re.MULTILINE)
        findings_block = rest if next_h2 is None else rest[:next_h2.start() + 1]
        for sub in FINDINGS_SUBSECTIONS:
            self.assertIn(
                f"### {sub}", findings_block,
                f"sub-section `### {sub}` not inside `## 🔎 Findings` block",
            )

    def test_findings_zero_count_renders_none_body(self):
        """SKILL.md and the template prose mandate `_None._` as the zero-count
        body for each sub-section. The realistic fixture has `### 🟢 Low (0
        findings)` followed by `_None._` — pin this so a future template edit
        that silently drops the `_None._` body fails the suite."""
        fixture = (REPO_ROOT / "tests" / "_pipeline" / "fixtures"
                   / "realistic_code_ultrareview.md")
        fixture_text = fixture.read_text(encoding="utf-8")
        # The fixture has at least one zero-count sub-section followed by
        # `_None._`. Locate the `(0 findings)` marker and assert `_None._`
        # appears in the block before the next heading.
        match = re.search(
            r"### .+? \(0 findings?\)\s*\n+(.+?)(\n### |\n## )",
            fixture_text, re.DOTALL,
        )
        if match is None:
            self.fail(
                "fixture has no zero-count sub-section to exercise the contract"
            )
        body = match.group(1).strip()
        self.assertIn(
            "_None._", body,
            f"zero-count sub-section body is `{body!r}`, expected `_None._`",
        )

    def test_legacy_verified_unverified_headings_removed(self):
        """Pre-fix layout used `### Verified` and `### Unverified` as the only
        two sub-sections. The new layout splits Verified by severity and uses
        `### ⚠️ Unverified` (with emoji prefix). Either legacy heading
        reappearing means a regression."""
        text = _read()
        for legacy in ("### Verified\n", "### Unverified\n"):
            self.assertNotIn(
                legacy, text,
                f"legacy sub-section heading `{legacy.strip()}` reintroduced",
            )
        # Always-Ultra refactor leftovers from the previous layout.
        self.assertNotIn("recommend Deep pass", text)
        self.assertNotIn("-t deep", text)

    def test_severity_subsections_carry_tier_column(self):
        """High / Medium / Low tables list the Anthropic tier (Important /
        Nit / Pre-existing) so the dual scheme stays visible. The Severity
        column is gone (severity lives in the sub-section heading)."""
        text = _read()
        # Heading must be followed by a row table with `| Tier |`.
        for sub in ("🔴 High", "🟠 Medium", "🟢 Low"):
            sub_offset = text.index(f"### {sub}")
            # Block runs to the next `###` or `##`.
            rest = text[sub_offset:]
            next_heading = re.search(r"\n(##|###) ", rest[1:])
            block = rest if next_heading is None else rest[:next_heading.start() + 1]
            self.assertIn("| Tier |", block, f"`### {sub}` missing Tier column")

    def test_unverified_subsection_omits_tier_column(self):
        """Unverified findings are A2-routed (severity downgraded to Low,
        confidence < 80) — Anthropic tier is null by mapping, so the column
        is dropped from the Unverified table."""
        text = _read()
        sub_offset = text.index("### ⚠️ Unverified")
        rest = text[sub_offset:]
        next_heading = re.search(r"\n(##|###) ", rest[1:])
        block = rest if next_heading is None else rest[:next_heading.start() + 1]
        self.assertNotIn("| Tier |", block)


class TestCoherenceGraphStatus(unittest.TestCase):
    def test_lists_all_six_sub_graphs(self):
        text = _read()
        status_idx = text.index("## 🕸️ Coherence-graph status")
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
        section_idx = text.index("## 🪛 --apply-safe summary")
        rest = text[section_idx:]
        # apply-safe summary is the final ## section
        next_section_match = re.search(r"\n## ", rest[1:])
        block = rest if next_section_match is None else rest[:next_section_match.start() + 1]
        for writer in ("version_sync", "description_sync", "failing_test_writer"):
            self.assertIn(writer, block, f"writer {writer!r} missing")


class TestSeveritySchemeInTemplate(unittest.TestCase):
    def test_tier_column_uses_anthropic_terms(self):
        text = _read()
        # Example rows in the per-severity tables demonstrate the Anthropic tier.
        for term in ("Important",):
            self.assertIn(term, text)


if __name__ == "__main__":
    unittest.main()
