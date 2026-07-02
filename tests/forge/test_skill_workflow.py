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
        # `-s` saves to ~/.agents/output/{project}/forge/forge-{slug}.md.
        self.assertRegex(
            body,
            r"`-s`.*?~/\.agents/output/\{project\}/forge/forge-",
            "Parameters table must document `-s` → ~/.agents/output/{project}/forge/forge-{slug}.md",
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
    """The Rules section is forge's contract: never implement, three-tier
    Decide (Decide / Surface / Escalate), audit + validate before finalizing.
    Each is a guardrail — dropping one degrades the skill (e.g. losing 'never
    implement' lets forge write code; losing 'Surface' drops the load-bearing
    fork the user came to think about)."""

    REQUIRED_RULES = [
        ("Never implement", ("Never implement", "not code changes", "no code")),
        ("Three tiers in Decide", ("Three tiers in Decide", "Surface", "surface")),
        ("Audit and validate", ("Audit and validate", "pre-save audit", "validate_spec")),
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


class TestModelInherit(unittest.TestCase):
    """model stays unset — a pin would downgrade stronger sessions; forge
    inherits the session model."""

    def test_model_unset_inherits_session(self):
        import sys
        sys.path.insert(0, str(REPO_ROOT / "skills" / "brand-voice" / "scripts"))
        from utils import parse_yaml_minimal, split_frontmatter  # noqa: E402
        fm_text, _ = split_frontmatter(_body())
        fm = parse_yaml_minimal(fm_text) if fm_text else {}
        self.assertIsNone(fm.get("model"),
                          "model must stay unset — skills inherit the session model")


class TestBridge(unittest.TestCase):
    """Phase 4 commits forge to the `/apex -f` hand-off for the Spec shape,
    inlining the artifact's explicit path `~/.agents/output/{project}/forge/
    forge-{slug}.md` (no reconstruction) per repo-conventions.md § Pipeline
    chaining. The Decision shape (default) explicitly has no apex bridge —
    it asks the decompose question and waits, so users don't think a bridge
    is mandatory before the decompose."""

    def test_bridge_to_apex_documented(self):
        body = _body()
        self.assertIn("/apex -f", body, "forge must bridge to /apex via -f")
        self.assertRegex(
            body,
            r"/apex -f ~/\.agents/output/\{project\}/forge/forge-\{slug\}\.md",
            "bridge to /apex must inline the explicit forge artifact path",
        )

    def test_documents_canonical_filename(self):
        # forge commits to the {skill}-{slug}.md filename convention.
        self.assertIn("forge-{slug}.md", _body())

    def test_decision_shape_has_no_apex_bridge(self):
        """Routing flipped: Decision is the default. SKILL.md must document
        that the Decision shape skips the apex bridge and waits for the
        decompose answer — the restored brainstorm Discuss posture."""
        body = _body().lower()
        # "no apex bridge" is the canonical phrase used in Present-and-route;
        # accept the equivalent "no bridge" wording too in case it gets
        # tightened to the shorter form later.
        self.assertRegex(
            body, r"no apex bridge|no bridge",
            "Decision shape must document the no-apex-bridge default path",
        )
        self.assertRegex(
            body, r"decompose.*workstreams?|workstreams?.*decompose",
            "Decision shape must document the decompose question",
        )


class TestDecisionDefaultRouting(unittest.TestCase):
    """Decision-default routing is the new posture (commit 889cb3f). Spec
    shape promotion fires only on enumerated conditions: auto_mode,
    issues_mode, prior-Spec from_file, build verb in idea, decomposition
    signal in idea, or Decision-IS-build-plan. Drift in this list silently
    re-introduces the overcommitment bias the rebuild exists to fix."""

    PHASE_4_PATTERN = re.compile(
        r"### Phase 4 — Forge\s*\n(.*?)(?=^### |\Z)",
        re.DOTALL | re.MULTILINE,
    )

    def _phase_4(self):
        m = self.PHASE_4_PATTERN.search(_body())
        self.assertIsNotNone(m, "Phase 4 — Forge section missing")
        assert m is not None
        return m.group(1)

    def test_decision_is_default(self):
        section = self._phase_4()
        self.assertRegex(
            section, r"[Dd]efault\s*=\s*`?#\s*Decision",
            "Phase 4 must state Decision is the default shape",
        )

    def test_promotion_conditions_complete(self):
        """The promotion list must include all 6 conditions — anything
        missing here silently downgrades a user request (e.g. -i on an
        exploratory idea emits a Decision and skips issue creation)."""
        section = self._phase_4()
        required_signals = [
            "auto_mode",          # commit-and-emit opt-in
            "issues_mode",        # -i forces workstreams
            "from_file",          # iteration on prior Spec preserves shape
            "build",              # build verb (build/add/implement/...)
            "decompose",          # explicit decomposition signal
        ]
        for signal in required_signals:
            with self.subTest(signal=signal):
                self.assertIn(
                    signal, section,
                    f"Phase 4 promotion conditions missing '{signal}' — "
                    "see SKILL.md routing list",
                )

    def test_decompose_question_pause(self):
        """When Decision is emitted, SKILL.md must say to ask the decompose
        question and WAIT — the discuss-then-build seam."""
        section = self._phase_4()
        self.assertRegex(
            section.lower(),
            r"(ask.+decompose|decompose.+workstreams?).+(wait|pause)",
            "Decision shape must pause for the user's decompose answer",
        )


class TestThreeTierDecide(unittest.TestCase):
    """Phase 3 runs three tiers: decide reversible/conventional, surface
    load-bearing forks, escalate user-owned. The Surface tier is the new
    one (commit 14019d9) — auto-deciding a load-bearing call is the
    overengineering tell the rebuild fixes."""

    def _phase_3(self):
        m = re.search(
            r"### Phase 3 — Decide\s*\n(.*?)(?=^### |\Z)",
            _body(), re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(m, "Phase 3 — Decide section missing")
        assert m is not None
        return m.group(1)

    def test_three_tiers_named(self):
        section = self._phase_3()
        # All three tier verbs must appear as bolded/header anchors.
        for tier in ("Decide", "Surface", "Escalate"):
            with self.subTest(tier=tier):
                self.assertRegex(
                    section, rf"\*\*{tier}\*\*",
                    f"Phase 3 missing **{tier}** tier anchor",
                )

    def test_surface_tier_explains_visibility(self):
        """Surface tier's whole point is that the load-bearing call is the
        thinking the user asked for, named visibly rather than buried in
        the Assumption ledger. The 'pick + runner-up + flip' triad is the
        canonical surfacing format."""
        section = self._phase_3()
        self.assertRegex(
            section.lower(),
            r"runner-up.+flip|flip.+runner-up",
            "Surface tier must require runner-up + what-would-flip-it",
        )


class TestAdversarialPanel(unittest.TestCase):
    """Judge runs an adversarial panel (3-5 lensed critics in parallel)
    then a bounded convergence round after Stress-test. Each critic gets a
    clean context (leader + runner-up + premortem only) — the same
    conversation cannot reliably argue against the plan it just shipped.
    Pattern from Anthropic's adversarial-review, fanned out per lens and
    converged on the survivors (bounded to <=2 rounds)."""

    ADVERSARIAL_HEADER = r"\*\*Adversarial panel \+ convergence\.?\*\*"

    def _judge_section(self):
        m = re.search(
            r"### Phase 2 — Judge\s*\n(.*?)(?=^### |\Z)",
            _body(), re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(m, "Phase 2 — Judge section missing")
        assert m is not None
        return m.group(1)

    def test_adversarial_step_in_phase_2(self):
        section = self._judge_section()
        self.assertRegex(
            section, self.ADVERSARIAL_HEADER,
            "Phase 2 must include the **Adversarial panel + convergence** step",
        )
        self.assertRegex(
            section.lower(), r"general-purpose.+clean context",
            "Panel must spawn general-purpose critics with a clean context",
        )

    def test_panel_fans_out_multiple_lensed_critics(self):
        """Round 1 launches 3-5 critics, one per lens, in one parallel
        message — the depth upgrade over the prior single one-shot critic."""
        section = self._judge_section().lower()
        self.assertIn("3-5", section,
                      "Phase 2 must launch a 3-5 critic panel (Round 1)")
        self.assertIn("lens", section,
                      "Panel critics must each carry a distinct lens")
        self.assertIn("parallel", section,
                      "Panel critics launch in one parallel message")

    def test_convergence_round_bounded(self):
        """Round 2 converges on surviving findings, bounded to <=2 rounds —
        forge emits a bounded plan, not an unbounded refute loop."""
        section = self._judge_section().lower()
        self.assertIn("convergence", section,
                      "Phase 2 must run a convergence round on survivors")
        self.assertRegex(
            section, r"2 rounds|two rounds",
            "Convergence must be bounded to <=2 rounds",
        )

    def test_adversarial_default_on_with_economy_skip(self):
        """ON by default; skipped under economy_mode. The economy flag
        is the user's opt-out for token/latency reasons."""
        section = self._judge_section()
        self.assertIn("ON by default", section,
                      "Adversarial step must declare 'ON by default'")
        self.assertIn("economy_mode", section,
                      "Adversarial step must document the economy_mode skip")


class TestResearchFloor(unittest.TestCase):
    """Always-deep: forge is invoked deliberately, never for trivial work,
    so there is no zero-agent path. Every run launches >=1 Explore + >=1
    general-purpose; economy_mode is the only escape hatch. Drift back to a
    skip-gate re-introduces the skim the deepening fixes."""

    def _subagent_section(self):
        m = re.search(
            r"## Subagent strategy\s*\n(.*?)(?=^## |\Z)",
            _body(), re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(m, "## Subagent strategy section missing")
        assert m is not None
        return m.group(1)

    def test_floor_documented(self):
        section = self._subagent_section().lower()
        self.assertIn("floor", section,
                      "Subagent strategy must state the research floor")
        self.assertIn("1 explore", section,
                      "Floor must require >=1 Explore agent")
        self.assertIn("1 general-purpose", section,
                      "Floor must require >=1 general-purpose agent")

    def test_no_zero_agent_skip_row(self):
        section = self._subagent_section()
        self.assertNotIn("Answer already clear", section,
                         "The zero-agent skip row must be removed")
        self.assertNotRegex(
            section, r"\|\s*0\s*\|",
            "No row may set the agent count to 0 — there is no skip path",
        )

    def test_economy_is_the_only_escape(self):
        section = self._subagent_section()
        self.assertIn("economy_mode", section,
                      "economy_mode must be named as the floor's escape hatch")

    def test_rules_section_pins_floor(self):
        m = re.search(r"## Rules\s*\n(.*?)(?=^##\s|\Z)", _body(),
                      re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, "## Rules section missing")
        assert m is not None
        rules = m.group(1).lower()
        self.assertIn("never skim hunt", rules,
                      "Rules must pin the never-skim-Hunt research floor")


class TestPreSaveAuditAndRevisionPause(unittest.TestCase):
    """Pre-save audit walks references/spec-craft.md § Pre-save audit
    before save (commit a5d0116); the schema validator runs after. The
    revision pause asks 'want to revise anything?' after Save + Validate
    when the shape is Spec and auto_mode is false — restores the soft-
    quality gate the validator alone does not catch."""

    # Trailing period sits inside the bold markers in the canonical body.
    AUDIT_HEADER = r"\*\*Pre-save audit\.?\*\*"
    PAUSE_HEADER = r"\*\*Revision pause\.?\*\*"

    def test_pre_save_audit_step_present(self):
        body = _body()
        self.assertRegex(
            body, self.AUDIT_HEADER,
            "Phase 4 must include the **Pre-save audit** step",
        )
        self.assertIn(
            "Pre-save audit", body,
            "Audit must reference the spec-craft.md § Pre-save audit section",
        )

    def test_revision_pause_step_present(self):
        body = _body()
        self.assertRegex(
            body, self.PAUSE_HEADER,
            "Phase 4 must include the **Revision pause** step",
        )

    def test_revision_pause_only_when_not_auto(self):
        """The pause is for non-auto mode; auto_mode skips it (user opted
        into commit-and-emit). Drift here re-introduces friction under -a."""
        body = _body()
        m = re.search(
            self.PAUSE_HEADER + r".*?(?=\*\*[A-Z]|\Z)",
            body, re.DOTALL,
        )
        self.assertIsNotNone(m, "Revision pause section missing")
        assert m is not None
        text = m.group(0).lower()
        self.assertRegex(
            text, r"auto_mode.+false|not.+auto_mode",
            "Revision pause must gate on auto_mode = false",
        )


class TestNewReferencesRouted(unittest.TestCase):
    """The rebuild added four references — research-discipline (Hunt),
    clarify-playbook (Hunt), subagent-prompts (Hunt + Judge), and
    adversarial-panel (Judge). SKILL.md must route to each on demand.
    Drift here turns load-bearing depth into orphan files."""

    REFERENCES = [
        "research-discipline.md",
        "clarify-playbook.md",
        "subagent-prompts.md",
        "adversarial-panel.md",
    ]

    def test_each_new_reference_routed(self):
        body = _body()
        for ref in self.REFERENCES:
            with self.subTest(reference=ref):
                self.assertIn(
                    f"references/{ref}", body,
                    f"SKILL.md must route to references/{ref} on demand",
                )

    def test_each_new_reference_file_exists(self):
        ref_dir = REPO_ROOT / "skills" / "forge" / "references"
        for ref in self.REFERENCES:
            with self.subTest(reference=ref):
                self.assertTrue(
                    (ref_dir / ref).is_file(),
                    f"references/{ref} missing on disk",
                )


class TestPromotionImpliesSave(unittest.TestCase):
    """An unsaved Spec promotion used to hit the mandatory validate gate with no
    file on disk and emit an apex bridge to a missing path."""

    def test_promotion_implies_save(self):
        body = _body()
        self.assertIn("**Promotion implies `-s`.**", body)
        self.assertIn("Explicit `-S` wins", body)


if __name__ == "__main__":
    unittest.main()
