"""Structural tests for `skills/code-ultrareview/templates/code-ultrareview.md`.

Pins the section order, the canonical emoji prefix on every `##` heading, the
`---` separator above every `##` section, the four mandatory severity
sub-sections inside `## 🔎 Findings` (### 🔴 High / ### 🟠 Medium /
### 🟢 Low / ### ⚠️ Unverified — each rendered even when count is 0), the
header tokens (Base + Target + Rule + Repo + Coherence axis), and the
`🛡️ What I did NOT check` deferral block. The template is the wire format the
synthesizer documents — drift here propagates to every report consumer.
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
# `tests/_pipeline/_contracts.py::CLUSTERS["review"]["report_required_sections"]`.
# `📐 Derivation coverage` and `🪛 --apply-safe summary` are opt-in (rendered
# only under their respective flags) — present in the TEMPLATE for reference
# but not enforced in the contract.
CANONICAL_SECTIONS = (
    "📋 Axis summary",
    "🔎 Findings",
    "✅ What looks good",
    "⚖️ Verdict",
    "🧰 Tools skipped",
    "🛡️ What I did NOT check",
    "📐 Derivation coverage",
    "🪛 --apply-safe summary",
)

# Four mandatory sub-sections inside `## 🔎 Findings`, in render order.
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
        dropped off the heading — the regression this contract pins. Catch
        it at the template level."""
        text = _read()
        plain_headings = (
            "## Axis summary",
            "## Findings",
            "## What looks good",
            "## Verdict",
            "## Tools skipped",
            "## What I did NOT check",
            "## Derivation coverage",
            "## --apply-safe summary",
        )
        for heading in plain_headings:
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
    def test_base_target_rule_in_header(self):
        text = _read()
        self.assertIn("**Base:**", text)
        self.assertIn("**Target:**", text)
        self.assertIn("**Rule:**", text)

    def test_repo_in_header(self):
        text = _read()
        self.assertIn("**Repo:**", text)

    def test_languages_in_header(self):
        text = _read()
        self.assertIn("**Languages:**", text)

    def test_rules_baseline_in_header(self):
        text = _read()
        self.assertIn("**Rules baseline:**", text)

    def test_coherence_axis_state_in_header(self):
        """Header surfaces whether the conditional Coherence axis ran."""
        text = _read()
        self.assertIn("**Coherence axis:**", text)

    def test_findings_counts_in_header(self):
        """Severity counters live in the header so a reader sees the
        verdict-relevant numbers at a glance."""
        text = _read()
        self.assertIn("**Findings:**", text)
        self.assertIn("🔴", text)
        self.assertIn("🟠", text)
        self.assertIn("🟢", text)

    def test_no_legacy_tier_header_fields(self):
        # The old `**Tier:**` / `Tier rationale:` / `Token estimate:` fields
        # are gone — they belonged to the always-Ultra refactor and the prior
        # 7-lens layout.
        text = _read()
        self.assertNotIn("**Tier:**", text)
        self.assertNotIn("Tier rationale:", text)
        self.assertNotIn("Token estimate:", text)


class TestFindingsSubSections(unittest.TestCase):
    """The Findings section uses four per-severity sub-sections (one per
    severity tier plus Unverified), each emoji-prefixed."""

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
        `## ⚖️ Verdict` or any other `##`."""
        text = _read()
        heading_match = re.search(r"^## 🔎 Findings\s*$", text, re.MULTILINE)
        if heading_match is None:
            self.fail("`## 🔎 Findings` heading not found in template")
        findings_idx = heading_match.start()
        rest = text[findings_idx:]
        next_h2 = re.search(r"^## ", rest[1:], re.MULTILINE)
        findings_block = rest if next_h2 is None else rest[:next_h2.start() + 1]
        for sub in FINDINGS_SUBSECTIONS:
            self.assertIn(
                f"### {sub}", findings_block,
                f"sub-section `### {sub}` not inside `## 🔎 Findings` block",
            )

    def test_severity_subsections_carry_tier_column(self):
        """High / Medium / Low tables list the Anthropic tier (Important /
        Nit / Pre-existing). The Severity column lives in the sub-section
        heading instead of a redundant cell."""
        text = _read()
        for sub in ("🔴 High", "🟠 Medium", "🟢 Low"):
            sub_offset = text.index(f"### {sub}")
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


class TestAxisSummary(unittest.TestCase):
    """`📋 Axis summary` lists every canonical axis."""

    def test_axis_summary_contains_all_canonical_axes(self):
        text = _read()
        sub_offset = text.index("## 📋 Axis summary")
        rest = text[sub_offset:]
        next_heading = re.search(r"\n## ", rest[1:])
        block = rest if next_heading is None else rest[:next_heading.start() + 1]
        for axis in REVIEW["report_axis_keys"]:
            self.assertIn(
                axis, block,
                f"axis `{axis}` missing from `## 📋 Axis summary` table",
            )


class TestDidNotCheckSection(unittest.TestCase):
    """`🛡️ What I did NOT check` is the mandatory closing safety contract."""

    def test_did_not_check_section_present(self):
        text = _read()
        self.assertIn("## 🛡️ What I did NOT check", text)

    def test_did_not_check_lists_security_runtime_perf_flake(self):
        text = _read()
        sub_offset = text.index("## 🛡️ What I did NOT check")
        rest = text[sub_offset:]
        next_heading = re.search(r"\n## ", rest[1:])
        block = rest if next_heading is None else rest[:next_heading.start() + 1]
        # Security pointer must point at /security-review.
        self.assertIn("/security-review", block)
        # Runtime performance + flaky test detection both surface as their
        # own bullets — explicit user-facing calibration of coverage.
        self.assertIn("Runtime performance", block)
        self.assertIn("Flaky test detection", block)


class TestToolsSkippedSection(unittest.TestCase):
    """`🧰 Tools skipped` always renders, even when no tools were skipped
    (body: `_None — every detected tool ran._`). Documenting the table
    shape with a tool example keeps the wire format stable."""

    def test_tools_skipped_section_present(self):
        text = _read()
        self.assertIn("## 🧰 Tools skipped", text)


class TestApplySafeSummary(unittest.TestCase):
    def test_apply_safe_summary_documents_three_writers(self):
        text = _read()
        sub_offset = text.index("## 🪛 --apply-safe summary")
        rest = text[sub_offset:]
        next_heading = re.search(r"\n## ", rest[1:])
        block = rest if next_heading is None else rest[:next_heading.start() + 1]
        for writer in ("version_sync", "description_sync", "failing_test_writer"):
            self.assertIn(writer, block)


class TestTerminalEchoRuleMirroredInThreePlaces(unittest.TestCase):
    """The terminal-echo rule states the full canonical report prints to the
    chat-terminal on every invocation, and that `-s` is purely additive
    (writes to disk, never gates the terminal output). The rule must be
    present in three places — SKILL.md `Final report layout`, SKILL.md
    `Rules`, and the template's `Section discipline` blockquote — so a
    model reading any of them encounters the contract."""

    SENTINEL_PHRASES = (
        "byte-for-byte identical",
        "chat-terminal",
    )
    SKILL_MD = REPO_ROOT / "skills" / "code-ultrareview" / "SKILL.md"

    def _section_block(self, text: str, heading: str) -> str:
        """Extract the block from `## <heading>` up to (but excluding) the
        next `## ` heading."""
        idx = text.index(heading)
        rest = text[idx:]
        next_h2 = re.search(r"\n## ", rest[1:])
        return rest if next_h2 is None else rest[:next_h2.start() + 1]

    def test_rule_in_skill_md_final_report_layout(self):
        text = self.SKILL_MD.read_text(encoding="utf-8")
        block = self._section_block(text, "## Final report layout")
        for phrase in self.SENTINEL_PHRASES:
            self.assertIn(
                phrase, block,
                f"`## Final report layout` missing terminal-echo phrase {phrase!r}",
            )

    def test_rule_in_skill_md_rules(self):
        text = self.SKILL_MD.read_text(encoding="utf-8")
        block = self._section_block(text, "## Rules")
        self.assertRegex(
            block,
            r"(?i)full report in chat every time",
            "`## Rules` missing terminal-echo mandate",
        )

    def test_rule_in_template_section_discipline(self):
        text = _read()
        for phrase in self.SENTINEL_PHRASES:
            self.assertIn(
                phrase, text,
                f"template missing terminal-echo phrase {phrase!r} in "
                "Section discipline blockquote",
            )


if __name__ == "__main__":
    unittest.main()
