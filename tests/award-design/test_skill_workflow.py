"""award-design SKILL.md — 10-step workflow, judging criteria, atmosphere
calibration ranges. The archetype tests pin the 9-archetype matrix; this
module pins the rest of the skill contract."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_MD = REPO_ROOT / "skills" / "award-design" / "SKILL.md"


def _body():
    return SKILL_MD.read_text(encoding="utf-8")


WORKFLOW_STEPS = [
    "Understand the brief",
    "Recommend an archetype",
    "Read archetype reference",
    "Calibrate atmosphere",
    "Load foundations",
    "Produce DESIGN.md",
    "Design with intent",
    "Production hardening",
    "Validate",
    "Visual review",
]


class TestWorkflowSteps(unittest.TestCase):
    """The 10-step workflow is the skill's procedure. Each step is numbered
    and documented; reordering or dropping a step changes the procedure.
    Step 10 is optional ('*(optional)*'); the rest are required."""

    def test_workflow_section_exists(self):
        self.assertIn("## Workflow", _body())

    def test_each_step_documented(self):
        body = _body()
        for i, step in enumerate(WORKFLOW_STEPS, start=1):
            with self.subTest(step=step, index=i):
                # Step pattern: `<n>. **<Title>**` at the start of a line.
                # Use re.MULTILINE explicitly — assertRegex applies re.search
                # without MULTILINE, so `^` would only match start-of-string.
                pattern = rf"^{i}\.\s+\*\*{re.escape(step)}\*\*"
                self.assertIsNotNone(
                    re.search(pattern, body, re.MULTILINE),
                    f"workflow step {i} ({step}) missing or mis-numbered",
                )

    def test_step_count_is_ten(self):
        """Pin the step count — adding step 11 must be intentional, not silent.
        Scope strictly to the top-level workflow numbered list (stops at the
        first `### ` subsection like 'Changing archetype mid-project'),
        otherwise nested numbered lists in subsections inflate the count."""
        body = _body()
        # Top-level workflow region: from `## Workflow` up to the first `### ` or `## ` after it.
        m = re.search(
            r"## Workflow\s*\n(.*?)(?=^###?\s)",
            body, re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(m, "Workflow region missing or has no terminating subsection")
        workflow_text = m.group(1)
        # Only count `N. **Title**` entries (with bold) — bare numbered list items
        # in nested prose use `N. plain text` and would not match.
        workflow_steps = re.findall(
            r"^(\d+)\.\s+\*\*[^*]+\*\*", workflow_text, re.MULTILINE,
        )
        self.assertEqual(
            len(workflow_steps), 10,
            f"expected 10 workflow steps, found {len(workflow_steps)}: {workflow_steps}",
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
    """The 'Combining archetypes (remix)' subsection documents the fallback
    when the brief refuses a single archetype. Without it, the workflow
    has no path for a hybrid brief — the user gets stuck."""

    def test_remix_section_exists(self):
        self.assertIn("Combining archetypes", _body())

    def test_remix_routes_to_reference(self):
        body = _body()
        # The remix path must route to references/remixing.md, not re-derive
        # the rules inline.
        self.assertIn(
            "references/remixing.md", body,
            "remix subsection must route to references/remixing.md",
        )


class TestProductionHardeningTrigger(unittest.TestCase):
    """The Production hardening step (8) is conditional — it triggers when
    implementation touches video, scroll-driven cinematic, or full-screen
    heroes on mobile. The trigger conditions must be documented so the
    step doesn't get bypassed for genuinely-needed contexts."""

    def test_trigger_conditions_documented(self):
        body = _body()
        # Find the step 8 region to scope assertions.
        m = re.search(
            r"^8\.\s+\*\*Production hardening\*\*(.*?)(?=^\d+\.\s+\*\*|\Z)",
            body, re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(m, "step 8 (Production hardening) missing")
        section = m.group(1)
        # The three trigger surfaces must all be named.
        for trigger in ("video", "scroll", "hero"):
            with self.subTest(trigger=trigger):
                self.assertIn(
                    trigger, section.lower(),
                    f"step 8 must name trigger '{trigger}' to enable conditional skip",
                )


if __name__ == "__main__":
    unittest.main()
