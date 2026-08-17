"""design-system decouple contract.

Pins the half of the reorder that lives in design-system: it governs an
existing DESIGN.md but steps aside when none exists — it never blocks an edit
for lack of a file and never authors a design from scratch. These assertions
would FAIL on the pre-refactor SKILL.md, which delegated to /award-design or
forced `init` whenever a DESIGN.md was absent."""

import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_MD = REPO_ROOT / "skills" / "design-system" / "SKILL.md"
AUDIT_REFERENCE = (
    REPO_ROOT / "skills" / "design-system" / "references" / "subcommand-audit.md"
)
MIGRATE_REFERENCE = (
    REPO_ROOT / "skills" / "design-system" / "references" / "subcommand-migrate.md"
)
INIT_REFERENCE = (
    REPO_ROOT / "skills" / "design-system" / "references" / "subcommand-init.md"
)
EVALS = REPO_ROOT / "skills" / "design-system" / "evals" / "evals.json"
README = REPO_ROOT / "README.md"


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
            "seven subcommands, four backed by the canonical CLI", _frontmatter(),
            "the description must pin the subcommand count at seven",
        )


class TestCrossAgentRuntimeContracts(unittest.TestCase):
    def test_shared_brand_guidance_uses_cross_agent_instructions(self):
        text = _body()
        self.assertIn("applicable project instructions", text)
        self.assertIn("AGENTS.md", text)
        self.assertIn("CLAUDE.md", text)

    def test_strict_mode_probes_shared_agents_install(self):
        text = AUDIT_REFERENCE.read_text(encoding="utf-8")
        self.assertIn(
            "~/.agents/skills/award-design/references/anti-patterns.md", text
        )

    def test_strict_mode_stops_when_either_catalog_is_absent(self):
        text = AUDIT_REFERENCE.read_text(encoding="utf-8")
        self.assertIn("Resolve `anti-patterns.md` and `exemplars.md` independently", text)
        self.assertIn("If either catalog is absent", text)
        self.assertIn("requires the complete `/award-design` catalogs", text)
        self.assertIn(
            "npx skills add coroboros/agent-skills --skill award-design", text
        )
        self.assertIn("Stop the strict audit when either catalog is missing", text)
        self.assertIn("Never emit a partial strict result", text)
        self.assertIn("drop `--strict`", text)

    def test_strict_mode_contract_matches_readme_and_eval(self):
        readme = README.read_text(encoding="utf-8")
        self.assertIn("if either is absent, stop with the install command", readme)
        self.assertIn("instruct the user to drop `--strict`", readme)

        evals = json.loads(EVALS.read_text(encoding="utf-8"))["evals"]
        strict_eval = next(case for case in evals if case["id"] == 7)
        self.assertIn("award-design is not installed", strict_eval["prompt"])
        self.assertIn("npx skills add coroboros/agent-skills --skill award-design", strict_eval["expected_output"])
        self.assertIn("drop `--strict`", strict_eval["expected_output"])
        self.assertIn("does not emit a degraded strict result", strict_eval["expected_output"])

        partial_eval = next(case for case in evals if case["id"] == 8)
        self.assertIn("only anti-patterns.md is present", partial_eval["prompt"])
        self.assertIn("exemplars.md", partial_eval["expected_output"])
        self.assertIn("no partial strict result", partial_eval["expected_output"])

    def test_migration_preflights_before_any_write(self):
        text = MIGRATE_REFERENCE.read_text(encoding="utf-8")
        preflight = text.index("Preflight the canonical CLI before any write")
        candidate = text.index("Write a candidate temp file")
        commit = text.index("Commit atomically")
        self.assertLess(preflight, candidate)
        self.assertLess(candidate, commit)
        self.assertIn("leaves the source and final output untouched", text)

    def test_init_preflights_and_audits_before_atomic_commit(self):
        text = INIT_REFERENCE.read_text(encoding="utf-8")
        preflight = text.index("Preflight the canonical CLI before any write")
        candidate = text.index("Write a candidate temp file")
        audit = text.index("Run audit on the candidate")
        commit = text.index("Commit atomically")
        self.assertLess(preflight, candidate)
        self.assertLess(candidate, audit)
        self.assertLess(audit, commit)
        self.assertIn("leaves the final path untouched", text)


if __name__ == "__main__":
    unittest.main()
