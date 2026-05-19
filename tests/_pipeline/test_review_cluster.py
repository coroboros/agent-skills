"""Pipeline contract: code-review → apex (report-only producer).

code-review saves a report under .claude/output/code-review/{slug}/; /apex
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

    def test_code_review_documents_its_output_path(self):
        md = read_skill_md(REVIEW["producer"])
        self.assertIn(".claude/output/{project}/code-review/", md)
        self.assertIn("code-review-{slug}.md", md)

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
        text = (FIX / "realistic_code_review.md").read_text(encoding="utf-8")
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
        text = (FIX / "malformed_code_review.md").read_text(encoding="utf-8")
        self.assertNotEqual(
            _missing_sections(text, REVIEW["report_required_sections"]), []
        )


if __name__ == "__main__":
    unittest.main()
