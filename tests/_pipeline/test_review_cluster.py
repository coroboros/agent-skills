"""Pipeline contract: code-ultrareview → apex (report-only producer).

code-ultrareview saves a report under .claude/output/code-ultrareview/{slug}/; /apex
consumes it via -f as generic foundational context (no apex change needed).
/oneshot is intentionally excluded — it has no -f flag and takes a
description, not a file. A realistic report fixture must satisfy the schema;
a malformed one must fail it — pinning the producer↔consumer contract so
drift on either side breaks this test in the same PR.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _contracts import CLUSTERS, read_skill_md  # noqa: E402

REVIEW = CLUSTERS["review"]
FIX = Path(__file__).parent / "fixtures"


def _missing_sections(text: str, required) -> list:
    return [s for s in required if f"## {s}" not in text]


def _argument_hint(skill_md: str) -> str:
    fm = skill_md.split("---", 2)[1]
    for line in fm.splitlines():
        if line.startswith("argument-hint:"):
            return line
    return ""


class TestProducerConsumerPaths(unittest.TestCase):
    """The producer commits to its output path in its own SKILL.md; the
    consumer documents generic -f consumption; the excluded skill must not
    expose an -f file flag."""

    def test_code_ultrareview_documents_its_output_path(self):
        md = read_skill_md(REVIEW["producer"])
        self.assertIn(".claude/output/{project}/code-ultrareview/", md)
        self.assertIn("code-ultrareview-{slug}.md", md)

    def test_apex_consumes_any_file_via_from(self):
        md = read_skill_md(REVIEW["consumer"])
        # apex's -f takes "any file as foundational input" — generic
        # consumption, so no apex change is needed to read a review report.
        self.assertIn("any file as foundational input", md)

    def test_oneshot_excluded_no_from_flag(self):
        hint = _argument_hint(read_skill_md("oneshot"))
        self.assertTrue(hint, "oneshot argument-hint missing")
        # oneshot takes a description/issue, never a -f file path.
        self.assertNotIn("-f", hint)


class TestReportSchema(unittest.TestCase):
    """A realistic report conforms to the pinned schema; a malformed one
    fails it loudly."""

    def test_realistic_fixture_conforms(self):
        text = (FIX / "realistic_code_ultrareview.md").read_text(encoding="utf-8")
        self.assertEqual(
            _missing_sections(text, REVIEW["report_required_sections"]), []
        )
        for token in ("Base:", "Target:", "Rule:"):
            self.assertIn(token, text)
        self.assertTrue(
            any(k in text for k in REVIEW["report_lens_keys"]),
            "no canonical lens key in realistic fixture",
        )
        self.assertTrue(
            any(s in text for s in REVIEW["report_severities"]),
            "no severity in realistic fixture",
        )
        for target in REVIEW["deferral_targets"][:2]:
            self.assertIn(target, text)

    def test_malformed_fixture_fails(self):
        text = (FIX / "malformed_code_ultrareview.md").read_text(encoding="utf-8")
        self.assertNotEqual(
            _missing_sections(text, REVIEW["report_required_sections"]), []
        )

    def test_coherence_graph_status_in_required_sections(self):
        self.assertIn("Coherence-graph status", REVIEW["report_required_sections"])

    def test_realistic_fixture_carries_tier_header(self):
        text = (FIX / "realistic_code_ultrareview.md").read_text(encoding="utf-8")
        # Tier + Tier rationale must always appear in the header.
        self.assertIn("Tier:", text)
        self.assertIn("Tier rationale:", text)

    def test_realistic_fixture_lists_all_six_sub_graphs(self):
        text = (FIX / "realistic_code_ultrareview.md").read_text(encoding="utf-8")
        for sub_graph in REVIEW["coherence_sub_graphs"]:
            self.assertIn(sub_graph, text, f"sub-graph {sub_graph!r} missing")


class TestSeverityScheme(unittest.TestCase):
    """Dual severity scheme — High/Medium/Low retained for compatibility,
    Important/Nit/Pre-existing added per Anthropic Managed Code Review."""

    def test_dual_scheme_present(self):
        for sev in ("High", "Medium", "Low"):
            self.assertIn(sev, REVIEW["report_severities"])
        for tier in ("Important", "Nit", "Pre-existing"):
            self.assertIn(tier, REVIEW["report_severities"])

    def test_realistic_fixture_uses_anthropic_tier(self):
        text = (FIX / "realistic_code_ultrareview.md").read_text(encoding="utf-8")
        self.assertIn("Important", text)


class TestProducerOutputTemplate(unittest.TestCase):
    """The producer_output template must render to a valid path-shaped
    string when formatted with {project}/{slug}."""

    def test_template_formats_cleanly(self):
        path = REVIEW["producer_output"].format(project="agent-skills", slug="audit")
        self.assertTrue(path.endswith("code-ultrareview-audit.md"))
        self.assertIn("/code-ultrareview/", path)


class TestConfidenceThresholdSemantics(unittest.TestCase):
    """confidence_threshold is the routing boundary, NOT a silent drop —
    sub-80 findings surface in the Unverified sub-section per A2."""

    def test_threshold_is_80(self):
        self.assertEqual(REVIEW["confidence_threshold"], 80)

    def test_realistic_fixture_documents_unverified_subsection(self):
        text = (FIX / "realistic_code_ultrareview.md").read_text(encoding="utf-8")
        self.assertIn("Unverified", text)
        self.assertIn("unverified — recommend Deep pass", text)


if __name__ == "__main__":
    unittest.main()
