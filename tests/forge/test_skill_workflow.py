"""forge SKILL.md — workflow phases, parameters table, rules section, bridge.
The template test covers the artifact output shape; this module pins the
SKILL.md contract that drives the prompt itself."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_MD = REPO_ROOT / "skills" / "forge" / "SKILL.md"


def _body():
    return SKILL_MD.read_text(encoding="utf-8")


# Canonical workflow phases (H3 headings inside `## Workflow — four phases`)
EXPECTED_PHASES = [
    "Phase 1 — Hunt",
    "Phase 2 — Judge",
    "Phase 3 — Decide",
    "Phase 4 — Forge",
]


class TestWorkflowPhases(unittest.TestCase):
    """The 4-phase workflow is the skill's spine. Hunt (research) → Judge
    (diverge + stress-test) → Decide (the discriminator) → Forge (emit one
    artifact). Reordering or dropping a phase silently changes the flow —
    the plan might ship without the Decide pass that resolves the open forks."""

    def test_workflow_section_exists(self):
        self.assertIn("## Workflow", _body())

    def test_each_phase_present(self):
        body = _body()
        for phase in EXPECTED_PHASES:
            with self.subTest(phase=phase):
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


class TestDecidePhaseDiscriminator(unittest.TestCase):
    """The Decide phase is forge's reason to exist — it resolves engineering
    judgment calls and escalates only the few user-owned forks. The decide-
    vs-escalate distinction MUST be explicit, or forge degrades into a skill
    that surfaces a wall of open questions instead of a plan."""

    def test_decide_phase_documents_decide_and_escalate(self):
        body = _body()
        m = re.search(
            r"### Phase 3 — Decide\s*\n(.*?)(?=^### |\Z)",
            body, re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(m, "Phase 3 — Decide section missing")
        section = m.group(1)
        self.assertRegex(section, r"[Dd]ecide", "Decide phase must instruct deciding")
        self.assertRegex(section, r"[Ee]scalate", "Decide phase must define escalation")


class TestParametersTable(unittest.TestCase):
    """The Parameters section pins the flag contract — `-s` saves to the forge
    output path that `/apex -f` consumes. Drift here breaks the producer
    contract for the forge → apex chain."""

    def test_parameters_section_exists(self):
        self.assertIn("## Parameters", _body())

    def test_save_flag_documented(self):
        body = _body()
        # `-s` saves to ~/.claude/output/{project}/forge/forge-{slug}.md.
        self.assertRegex(
            body,
            r"`-s`.*?~/\.claude/output/\{project\}/forge/forge-",
            "Parameters table must document `-s` → ~/.claude/output/{project}/forge/forge-{slug}.md",
        )

    def test_uppercase_S_documented(self):
        body = _body()
        self.assertRegex(
            body,
            r"`-S`.*?(no-save|disable|override)",
            "Parameters table must document `-S` as the no-save override",
        )

    def test_lowercase_uppercase_convention_explained(self):
        body = _body()
        self.assertRegex(
            body, r"[lL]owercase.*?[eE]nable.*?[uU]ppercase.*?[dD]isable",
            "Parameters section must explain the lowercase/uppercase convention",
        )


class TestRulesSection(unittest.TestCase):
    """The Rules section is forge's contract: never implement, decide-don't-
    defer, validate before finalizing. Each is a guardrail — dropping one
    degrades the skill (e.g. losing 'never implement' lets forge write code)."""

    REQUIRED_RULES = [
        ("Never implement", ("Never implement", "not code changes", "no code")),
        ("Decide vs escalate", ("Decide, don't defer", "Escalate only", "escalate")),
        ("Validate before finalizing", ("Validate before finalizing", "validate_spec")),
    ]

    def test_rules_section_exists(self):
        self.assertIn("## Rules", _body())

    def test_each_rule_present(self):
        body = _body()
        m = re.search(r"## Rules\s*\n(.*?)(?=^##\s|\Z)", body, re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, "## Rules section missing")
        section = m.group(1)
        for label, keywords in self.REQUIRED_RULES:
            with self.subTest(rule=label):
                hit = any(kw in section for kw in keywords)
                self.assertTrue(
                    hit,
                    f"Rules section missing rule '{label}' (expected one of {keywords})",
                )


class TestModelOpus(unittest.TestCase):
    """forge uses opus per skill design — strategic reasoning and decomposition
    need the strongest model. Pin the choice."""

    def test_model_is_opus(self):
        import sys
        sys.path.insert(0, str(REPO_ROOT / "skills" / "brand-voice" / "scripts"))
        from utils import parse_yaml_minimal, split_frontmatter  # noqa: E402
        fm_text, _ = split_frontmatter(_body())
        fm = parse_yaml_minimal(fm_text) if fm_text else {}
        self.assertEqual(fm.get("model"), "opus")


class TestBridge(unittest.TestCase):
    """Phase 4 commits forge to the `/apex -f` hand-off, inlining the artifact's
    explicit path `~/.claude/output/{project}/forge/forge-{slug}.md` (no
    reconstruction) per repo-conventions.md § Pipeline chaining. The pure-
    strategy path must explicitly conclude without a bridge so users don't
    think one is mandatory."""

    def test_bridge_to_apex_documented(self):
        body = _body()
        self.assertIn("/apex -f", body, "forge must bridge to /apex via -f")
        self.assertRegex(
            body,
            r"/apex -f ~/\.claude/output/\{project\}/forge/forge-\{slug\}\.md",
            "bridge to /apex must inline the explicit forge artifact path",
        )

    def test_documents_canonical_filename(self):
        # forge commits to the {skill}-{slug}.md filename convention.
        self.assertIn("forge-{slug}.md", _body())

    def test_pure_strategy_no_bridge_path(self):
        body = _body().lower()
        self.assertRegex(
            body, r"no bridge|conclude the discussion|pure-strategy",
            "SKILL.md must document the no-bridge path for pure-strategy outcomes",
        )


if __name__ == "__main__":
    unittest.main()
