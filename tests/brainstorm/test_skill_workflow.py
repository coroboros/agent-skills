"""brainstorm SKILL.md — workflow phases, parameters table, rules section.
The template tests cover the brief.md output shape; this module pins the
SKILL.md contract that drives the prompt itself."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_MD = REPO_ROOT / "skills" / "brainstorm" / "SKILL.md"


def _body():
    return SKILL_MD.read_text(encoding="utf-8")


# Canonical workflow phases (H3 headings inside `## Workflow`)
EXPECTED_PHASES = [
    "Phase 1 — Frame the problem",
    "Phase 2 — Research",
    "Phase 3 — Challenge",
    "Phase 4 — Synthesize",
    "Phase 5 — Discuss",
]


class TestWorkflowPhases(unittest.TestCase):
    """The 5-phase workflow is the skill's spine. Reordering or dropping a
    phase silently changes the brainstorm flow — the brief might ship without
    a Challenge pass, or skip the Discuss step that ends the cycle."""

    def test_workflow_section_exists(self):
        self.assertIn("## Workflow", _body())

    def test_each_phase_present(self):
        body = _body()
        for phase in EXPECTED_PHASES:
            with self.subTest(phase=phase):
                # Phases live at H3 — `### Phase N — Title`.
                # The H3 heading is followed by optional parenthetical context
                # (e.g. "Phase 2 — Research (parallel subagents)") — match
                # the prefix only.
                self.assertIsNotNone(
                    re.search(rf"^###\s+{re.escape(phase)}", body, re.MULTILINE),
                    f"missing phase: ### {phase}",
                )

    def test_phases_in_canonical_order(self):
        body = _body()
        positions = []
        for phase in EXPECTED_PHASES:
            m = re.search(rf"^###\s+{re.escape(phase)}", body, re.MULTILINE)
            self.assertIsNotNone(m, f"phase missing: {phase}")
            positions.append((m.start(), phase))
        ordered = [p for _, p in sorted(positions)]
        self.assertEqual(
            ordered, EXPECTED_PHASES,
            f"phases out of order: {ordered}",
        )


class TestParametersTable(unittest.TestCase):
    """The Parameters section pins the `-s`/`-S` flag contract — the
    repo-wide convention. Drift here breaks the producer contract for
    `/spec -f brainstorm.md`."""

    def test_parameters_section_exists(self):
        self.assertIn("## Parameters", _body())

    def test_save_flag_documented(self):
        body = _body()
        # `-s` saves to the canonical .claude/output path.
        self.assertRegex(
            body,
            r"\|\s*`-s`\s*\|.*?\.claude/output/brainstorm",
            "Parameters table must document `-s` saving to .claude/output/brainstorm/",
        )

    def test_uppercase_S_documented(self):
        body = _body()
        # `-S` disables save (override of ambient save).
        self.assertRegex(
            body,
            r"\|\s*`-S`\s*\|.*?(no-save|disable|override)",
            "Parameters table must document `-S` as the no-save override",
        )

    def test_lowercase_uppercase_convention_explained(self):
        body = _body()
        # The repo-wide convention "lowercase enables, uppercase disables"
        # must be cited in the section so users understand the symmetry.
        self.assertRegex(
            body, r"[lL]owercase.*?[eE]nable.*?[uU]ppercase.*?[dD]isable",
            "Parameters section must explain the lowercase/uppercase convention",
        )


class TestRulesSection(unittest.TestCase):
    """The Rules section is the contract for what brainstorm WILL NOT do
    (no implementation, ask before assumptions, end with discussion). Each
    rule is a guardrail — silently dropping one degrades the skill."""

    REQUIRED_RULES = [
        ("Never implement", ("Never implement", "no code", "no implementation")),
        ("Ask before assuming", ("Ask before assuming", "ask focused questions",
                                "before researching")),
        ("End with discussion", ("End with discussion", "wait for user direction",
                                 "Present findings")),
    ]

    def test_rules_section_exists(self):
        self.assertIn("## Rules", _body())

    def test_each_rule_present(self):
        # Restrict the search to the Rules section so a stray `Never implement`
        # mention elsewhere doesn't satisfy the assertion.
        body = _body()
        m = re.search(r"## Rules\s*\n(.*?)(?=^##\s|\Z)", body, re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, "## Rules section missing")
        section = m.group(1)
        for label, keywords in self.REQUIRED_RULES:
            with self.subTest(rule=label):
                hit = any(kw in section for kw in keywords)
                self.assertTrue(
                    hit,
                    f"Rules section missing rule '{label}' "
                    f"(expected one of {keywords})",
                )


class TestModelOpus(unittest.TestCase):
    """brainstorm uses opus per skill design — strategic reasoning needs
    the strongest model. Pin the choice."""

    def test_model_is_opus(self):
        import sys
        sys.path.insert(0, str(REPO_ROOT / "skills" / "brand-voice" / "scripts"))
        from utils import parse_yaml_minimal, split_frontmatter  # noqa: E402
        fm_text, _ = split_frontmatter(_body())
        fm = parse_yaml_minimal(fm_text) if fm_text else {}
        self.assertEqual(fm.get("model"), "opus")


class TestBridgeSection(unittest.TestCase):
    """The 'Bridge to next steps' section commits brainstorm to specific
    hand-off paths (`/spec` for multi-workstream, `/apex` for focused
    implementation). Drift in the documented `-f` syntax silently breaks
    the producer→consumer chain — `/spec -f` and `/apex -f` MUST receive
    a path matching the saved brainstorm output."""

    def test_bridge_section_exists(self):
        self.assertIn("## Bridge to next steps", _body())

    def test_bridge_to_spec_documented(self):
        body = _body()
        # Multi-workstream path → `/spec -s -f <brainstorm-output>`.
        # Pin both the verb (-s -f) and the canonical output path so a
        # change to either side surfaces here.
        self.assertIn("/spec -s -f", body,
                      "bridge to /spec must use canonical -s -f flag combo")
        self.assertRegex(
            body,
            r"/spec -s -f \.claude/output/brainstorm/.+?brainstorm\.md",
            "bridge to /spec must point at the canonical brainstorm output path",
        )

    def test_bridge_to_apex_documented(self):
        body = _body()
        # Focused-work path → `/apex -f <brainstorm-output>`.
        self.assertIn("/apex -f", body,
                      "bridge to /apex must use the -f flag")
        self.assertRegex(
            body,
            r"/apex -f \.claude/output/brainstorm/.+?brainstorm\.md",
            "bridge to /apex must point at the canonical brainstorm output path",
        )

    def test_bridge_documents_strategic_skip(self):
        """Not every brainstorm leads to code — the section must explicitly
        cover the 'pure strategic, no bridge' path so users don't think a
        bridge is mandatory."""
        body = _body()
        m = re.search(
            r"## Bridge to next steps\s*\n(.*?)(?=^## |\Z)",
            body, re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(m, "Bridge section missing")
        section = m.group(1).lower()
        # The pure-strategic path must say something equivalent to
        # "no bridge needed" / "simply conclude" — pin loosely.
        self.assertRegex(
            section, r"no bridging|no bridge|conclude|purely strategic",
            "Bridge section must document the no-bridge path for strategic-only work",
        )


if __name__ == "__main__":
    unittest.main()
