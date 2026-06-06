"""award-design SKILL.md — 4-phase workflow, judging criteria, atmosphere
calibration ranges. The archetype tests pin the 9-archetype matrix; this
module pins the rest of the skill contract. Under code-first, the four phases
are the Instant build procedure (run when no DESIGN.md exists); the code-first
contract itself — mode detect, Persist, two-gate close — is pinned in
test_code_first.py."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_MD = REPO_ROOT / "skills" / "award-design" / "SKILL.md"


def _body():
    return SKILL_MD.read_text(encoding="utf-8")


WORKFLOW_PHASES = [
    "Discovery",
    "Decision",
    "Tokens",
    "Production",
]


class TestWorkflowPhases(unittest.TestCase):
    """The 4-phase workflow is the skill's procedure. Each phase is an H3
    heading inside `## Workflow`; reordering or dropping one changes the
    procedure. The old 10-step list was consolidated into these phases."""

    def test_workflow_section_exists(self):
        self.assertIn("## Workflow", _body())

    def test_each_phase_documented(self):
        body = _body()
        for i, phase in enumerate(WORKFLOW_PHASES, start=1):
            with self.subTest(phase=phase, index=i):
                # Phase pattern: `### Phase <n> — <Title>` at the start of a line.
                pattern = rf"^### Phase {i} — {re.escape(phase)}\b"
                self.assertIsNotNone(
                    re.search(pattern, body, re.MULTILINE),
                    f"workflow phase {i} ({phase}) missing or mis-numbered",
                )

    def test_workflow_has_four_phases(self):
        """Pin the phase count — adding a 5th must be intentional, not silent.
        Scope to the Workflow section only (stops at the next `## `)."""
        body = _body()
        m = re.search(
            r"## Workflow\s*\n(.*?)(?=^##\s)",
            body, re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(m, "Workflow region missing or has no terminating section")
        workflow_text = m.group(1)
        phase_headers = re.findall(r"^### Phase (\d+)", workflow_text, re.MULTILINE)
        self.assertEqual(
            len(phase_headers), 4,
            f"expected 4 workflow phases, found {len(phase_headers)}: {phase_headers}",
        )


class TestJudgingCriteria(unittest.TestCase):
    """The judging criteria section pins the Awwwards weighting (40/30/20/10)
    and score floors (6.5+ Honorable Mention, 7.5+ SOTD). These numbers are
    the contract — drift means the skill's recommendations stop matching
    the actual judging signal."""

    def test_judging_criteria_section_exists(self):
        self.assertIn("## Judging Criteria", _body())

    def test_weights_documented(self):
        body = _body()
        # The four weights must all be cited.
        for label, pct in [("Design", 40), ("Usability", 30), ("Creativity", 20), ("Content", 10)]:
            with self.subTest(label=label, pct=pct):
                # Format: `**Design 40%**` (with spaces) — match flexibly.
                pattern = rf"\*\*{label}\s*{pct}%\*\*"
                self.assertRegex(
                    body, pattern,
                    f"judging weight '{label} {pct}%' missing or mis-formatted",
                )

    def test_score_floors_documented(self):
        body = _body()
        # Honorable Mention floor = 6.5+, SOTD floor = 7.5+.
        self.assertIn("6.5+", body, "Honorable Mention floor (6.5+) not cited")
        self.assertIn("7.5", body, "SOTD floor (7.5+) not cited")


class TestAtmosphereAxisRanges(unittest.TestCase):
    """The Atmosphere Calibration axis-range table maps 1-10 scores to
    qualitative descriptors per axis (Density, Variance, Motion). The
    descriptors at the extremes anchor the calibration step — silently
    losing one means agents lose the rubric for ±2 adjustments."""

    AXIS_DESCRIPTORS = {
        "Density": ("Gallery airy", "Cockpit dense"),
        "Variance": ("Predictable", "Artsy chaotic"),
        "Motion": ("Static", "Cinematic"),
    }

    def test_each_axis_has_endpoint_descriptors(self):
        body = _body()
        for axis, (low, high) in self.AXIS_DESCRIPTORS.items():
            with self.subTest(axis=axis):
                self.assertIn(low, body, f"{axis} axis 1-3 descriptor missing: {low}")
                self.assertIn(high, body, f"{axis} axis 7-10 descriptor missing: {high}")


class TestRemixingFallback(unittest.TestCase):
    """The remix fallback documents the path when the brief refuses a single
    archetype. After the 4-phase consolidation, the fallback lives inline in
    Phase 2 as a 'Mid-project changes' paragraph rather than its own
    subsection — the routing-to-reference contract is what matters."""

    def test_remix_routes_to_reference(self):
        body = _body()
        # The remix path must route to references/remixing.md, not re-derive
        # the rules inline.
        self.assertIn(
            "references/remixing.md", body,
            "SKILL.md must route hybrid briefs to references/remixing.md",
        )


class TestProductionHardeningTrigger(unittest.TestCase):
    """Production hardening (now in Phase 4) is conditional — it triggers
    when implementation touches video, scroll-driven cinematic, or full-screen
    heroes on mobile. The trigger conditions must be documented so the phase
    doesn't get bypassed for genuinely-needed contexts."""

    def test_trigger_conditions_documented(self):
        body = _body()
        # Find Phase 4 region (Production) to scope assertions.
        m = re.search(
            r"^### Phase 4 — Production(.*?)(?=^### Phase|\Z|^##\s)",
            body, re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(m, "Phase 4 (Production) missing")
        section = m.group(1)
        # The three trigger surfaces must all be named.
        for trigger in ("video", "scroll", "hero"):
            with self.subTest(trigger=trigger):
                self.assertIn(
                    trigger, section.lower(),
                    f"Phase 4 must name trigger '{trigger}' to enable conditional skip",
                )


if __name__ == "__main__":
    unittest.main()
