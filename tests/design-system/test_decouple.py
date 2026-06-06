"""design-system decouple contract.

Pins the half of the reorder that lives in design-system: it governs an
existing DESIGN.md but steps aside when none exists — it never blocks an edit
for lack of a file and never authors a design from scratch. These assertions
would FAIL on the pre-refactor SKILL.md, which delegated to /award-design or
forced `init` whenever a DESIGN.md was absent."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_MD = REPO_ROOT / "skills" / "design-system" / "SKILL.md"


def _body():
    return SKILL_MD.read_text(encoding="utf-8")


def _frontmatter():
    return _body().split("---", 2)[1]


def _routing_table():
    """The subcommand routing region — from its heading to the next H2."""
    m = re.search(r"## Subcommand routing(.*?)(?=^##\s)", _body(), re.DOTALL | re.MULTILINE)
    assert m, "Subcommand routing section missing"
    return m.group(1)


class TestStepAside(unittest.TestCase):
    """No DESIGN.md → design-system gets out of the way."""

    def test_step_aside_documented(self):
        self.assertRegex(
            _body(), r"[Ss]teps? aside",
            "SKILL.md must document the step-aside behaviour when no DESIGN.md exists",
        )

    def test_no_file_does_not_block_edit(self):
        body = _body().lower()
        self.assertTrue(
            "no block on the edit" in body
            or "never blocks an edit" in body
            or "does not block" in body
            or "no enforcement, no block" in body,
            "no-DESIGN.md path must not block the edit",
        )

    def test_auto_activation_is_conditional_on_file(self):
        self.assertRegex(
            _body().lower(),
            r"a `design.md` is present|when a `design.md` is present|design\.md is present",
            "auto-activation must enforce only when a DESIGN.md is present",
        )


class TestOwnershipRule(unittest.TestCase):
    """design-system governs; award-design creates. One owner for file
    creation, stated in both the description and the body."""

    def test_never_authors_from_scratch(self):
        body = _body().lower()
        self.assertTrue(
            "never authors a design from scratch" in body
            or "does not author a design file from scratch" in body
            or "never forces or authors one" in body,
            "ownership rule: design-system must never author a design file from scratch",
        )

    def test_points_at_award_design_for_creation(self):
        self.assertIn(
            "award-design", _body(),
            "design-system must point at /award-design for DESIGN.md creation",
        )

    def test_description_carries_step_aside_or_ownership(self):
        desc = re.search(r"^description:\s*(.*)$", _frontmatter(), re.MULTILINE)
        assert desc is not None, "description frontmatter missing"
        text = desc.group(1).lower()
        self.assertTrue(
            "steps aside" in text or "never forces or authors" in text,
            "description must surface the step-aside / ownership rule for triggering",
        )


class TestNoExtractSubcommand(unittest.TestCase):
    """Guard against an `extract` (code→DESIGN.md) verb. It never shipped — `migrate`
    already covers extraction and crystallization is award-design's — so this is a
    forward guard against a future addition, not a removal check."""

    def test_extract_not_in_routing_table(self):
        self.assertNotRegex(
            _routing_table(), r"\bextract\b",
            "no `extract` verb may be registered in the subcommand routing table",
        )

    def test_extract_not_invoked_anywhere(self):
        self.assertNotIn(
            "/design-system extract", _body(),
            "no `extract` subcommand may be referenced",
        )

    def test_subcommand_count_pinned_at_seven(self):
        """The description pins seven subcommands — an eighth (e.g. extract) breaks this guard."""
        self.assertIn(
            "seven CLI-backed subcommands", _frontmatter(),
            "the description must pin the subcommand count at seven",
        )


if __name__ == "__main__":
    unittest.main()
