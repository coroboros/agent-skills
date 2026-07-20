"""Structural tests for the per-axis briefs at references/axes/*.md.

Pins the contract every brief must satisfy so axis_dispatch.py can rely
on a uniform shape. Subagent BEHAVIOR (does Simplification flag a
single-use factory at confidence ≥75? does Performance skip on docs
repos?) lives in evals/evals.json — non-deterministic LLM output, not
unit-test territory.

Per-axis tests in this file pin the deterministic surface only:
- Every brief exists.
- Every brief carries the canonical headings the dispatcher templates against.
- Every brief references anthropic-verbatim.md.
- Per-axis specifics: Simplification cites code-simplifier; Performance lists
  the bundled rules; Style describes the instruction chain; Coherence lists
  its six sub-graphs; tool-fed axes name their tool inputs.
"""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
AXES_DIR = (
    REPO_ROOT / "skills" / "code-ultrareview" / "references" / "axes"
)
CANONICAL_AXES = (
    "correctness", "simplification", "tests", "documentation",
    "style", "intent", "design-api", "performance",
)
CONDITIONAL_AXES = ("coherence",)
ALL_AXES = CANONICAL_AXES + CONDITIONAL_AXES


def _brief(axis: str) -> str:
    path = AXES_DIR / f"{axis}.md"
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# File presence
# ---------------------------------------------------------------------------


class TestBriefsExist(unittest.TestCase):

    def test_every_axis_has_a_brief(self):
        for axis in ALL_AXES:
            path = AXES_DIR / f"{axis}.md"
            self.assertTrue(
                path.is_file(),
                f"missing brief: {path}",
            )


# ---------------------------------------------------------------------------
# Uniform structure
# ---------------------------------------------------------------------------


class TestBriefStructure(unittest.TestCase):

    REQUIRED_HEADINGS = (
        "## In scope",        # Coherence uses "## Activation" + sub-graph headings
        "## Out of scope",
        "## Tool inputs",
        "## Severity calibration",
        "## Subagent inputs",
    )

    def test_canonical_axes_carry_required_headings(self):
        # Coherence has a different shape (sub-graphs); test the 8 canonical
        # axes only here. Coherence gets its own structural test below.
        for axis in CANONICAL_AXES:
            body = _brief(axis)
            for heading in self.REQUIRED_HEADINGS:
                self.assertIn(
                    heading, body,
                    f"axis {axis} missing heading '{heading}'",
                )

    def test_every_brief_starts_with_h1_axis_title(self):
        for axis in ALL_AXES:
            body = _brief(axis)
            first_line = body.splitlines()[0]
            self.assertTrue(
                first_line.startswith(f"# Axis: "),
                f"axis {axis} brief does not start with '# Axis:': {first_line!r}",
            )
            self.assertIn(f"`{axis}`", first_line)

    def test_every_brief_lists_subagent_inputs(self):
        # Every brief must spell out what the orchestrator hands the subagent.
        for axis in ALL_AXES:
            body = _brief(axis)
            self.assertIn(
                "scope.json", body,
                f"axis {axis} brief missing scope.json reference",
            )
            self.assertIn(
                "tool-findings.jsonl", body,
                f"axis {axis} brief missing tool-findings.jsonl reference",
            )
            self.assertIn(
                "diff", body.lower(),
                f"axis {axis} brief missing diff reference",
            )


# ---------------------------------------------------------------------------
# Anthropic-verbatim reference
# ---------------------------------------------------------------------------


class TestAnthropicVerbatimReferenced(unittest.TestCase):
    """Every brief must point the subagent at the verbatim rubric +
    false-positive list (the anthropic-verbatim.md source)."""

    def test_every_brief_references_anthropic_verbatim(self):
        for axis in ALL_AXES:
            body = _brief(axis)
            self.assertIn(
                "anthropic-verbatim.md", body,
                f"axis {axis} brief does not reference anthropic-verbatim.md",
            )


# ---------------------------------------------------------------------------
# Per-axis content checks (deterministic — keyword-based)
# ---------------------------------------------------------------------------


class TestCorrectnessBrief(unittest.TestCase):

    def test_has_no_deterministic_tool_input(self):
        body = _brief("correctness").lower()
        self.assertIn("no deterministic tool findings route to correctness", body)
        self.assertIn("every accepted semgrep finding routes to the performance axis", body)

    def test_excludes_typechecker_caught_issues(self):
        body = _brief("correctness")
        self.assertIn("typechecker", body.lower())


class TestSimplificationBrief(unittest.TestCase):

    def test_cites_code_simplifier_plugin(self):
        body = _brief("simplification")
        self.assertIn("code-simplifier", body)

    def test_lists_dead_code_tools(self):
        body = _brief("simplification")
        for tool in ("knip", "vulture", "cargo-machete", "deadcode"):
            self.assertIn(
                tool, body,
                f"simplification brief missing tool {tool}",
            )

    def test_caps_severity_at_medium(self):
        body = _brief("simplification")
        self.assertIn("🔴 High — never", body)


class TestTestsBrief(unittest.TestCase):

    def test_calls_out_skip_xit_xdescribe(self):
        body = _brief("tests")
        for token in (".skip", "xit"):
            self.assertIn(token, body)

    def test_explicit_non_goal_flake_detection(self):
        body = _brief("tests")
        self.assertIn("flake", body.lower())


class TestDocumentationBrief(unittest.TestCase):

    def test_install_context_paths_are_cross_agent(self):
        body = _brief("documentation")
        self.assertIn("~/.agents/skills/<other>/", body)
        self.assertIn("~/.claude/skills/<other>/", body)

    def test_lists_ai_vocabulary_terms(self):
        body = _brief("documentation")
        for term in ("delve", "tapestry", "underscore"):
            self.assertIn(term, body)

    def test_em_dash_density_rule(self):
        body = _brief("documentation")
        self.assertIn("em-dash", body.lower())
        self.assertIn("100 words", body)


class TestStyleBrief(unittest.TestCase):

    def test_describes_cross_agent_instruction_chain(self):
        body = _brief("style")
        self.assertIn("AGENTS.md", body)
        self.assertIn("CLAUDE.md", body)
        self.assertIn("instruction_chain", body)
        self.assertIn("AGENTS.override.md", body)

    def test_graceful_degradation_when_no_baseline(self):
        body = _brief("style")
        self.assertIn("Style axis still runs", body)
        self.assertIn("repeated neighboring repository evidence", body)
        self.assertIn("never marked skipped", body)


class TestIntentBrief(unittest.TestCase):

    def test_reconcile_taxonomy_listed(self):
        body = _brief("intent")
        for tag in ("GAP", "SCOPE-ADD", "DECISION-OVERRIDE", "CONSISTENT"):
            self.assertIn(tag, body)

    def test_lockfile_drift_called_out(self):
        body = _brief("intent")
        self.assertIn("lockfile", body.lower())


class TestDesignApiBrief(unittest.TestCase):

    def test_lists_api_extractor_oasdiff_atlas(self):
        body = _brief("design-api")
        for tool in ("api-extractor", "oasdiff", "atlas"):
            self.assertIn(
                tool, body,
                f"design-api brief missing tool {tool}",
            )


class TestPerformanceBrief(unittest.TestCase):

    def test_lists_bundled_perf_rules(self):
        body = _brief("performance")
        for rule in (
            "n-plus-one-sqlalchemy.yml",
            "n-plus-one-sequelize.yml",
            "sync-io-async-py.yml",
        ):
            self.assertIn(
                rule, body,
                f"performance brief missing perf-rule {rule}",
            )

    def test_explicit_non_goal_benchmarks(self):
        body = _brief("performance")
        self.assertIn("benchmarks", body.lower())
        self.assertIn("flamegraph", body.lower())

    def test_code_bearing_skills_are_not_skipped(self):
        body = _brief("performance")
        self.assertIn("Review executable scripts", body)
        self.assertIn('"no_findings":true', body)
        self.assertNotIn("Skipped — skills repo", body)

    def test_semgrep_rules_require_prefix_and_axis_metadata(self):
        body = _brief("performance")
        self.assertIn("starts with `code-ultrareview-` AND", body)


class TestCoherenceBrief(unittest.TestCase):

    def test_lists_six_sub_graphs(self):
        body = _brief("coherence")
        for sub in (
            "description", "version", "capability",
            "cross-reference", "example", "spec-conformance",
        ):
            self.assertIn(
                sub, body,
                f"coherence brief missing sub-graph {sub}",
            )

    def test_activation_triggers_listed(self):
        body = _brief("coherence")
        for trigger in (
            "package.json", "marketplace.json", "SKILL.md",
            "README.md", "tsconfig.json", "pyproject.toml",
            "Cargo.toml", "go.mod",
        ):
            self.assertIn(
                trigger, body,
                f"coherence brief missing trigger {trigger}",
            )


# ---------------------------------------------------------------------------
# Repo-kind branches required on every axis (per axes-overview convention)
# ---------------------------------------------------------------------------


class TestRepoKindBranches(unittest.TestCase):

    def test_every_axis_documents_repo_kind_branches(self):
        # The 8 canonical axes each declare per-repo-kind behavior; Style
        # explicitly opts out ("No branches"). Coherence has per-sub-graph
        # branches. Accept either explicit "## Repo-kind branches" or
        # "No branches" with the rationale.
        for axis in ALL_AXES:
            body = _brief(axis)
            self.assertTrue(
                ("## Repo-kind branches" in body)
                or ("No branches" in body),
                f"axis {axis} brief missing repo-kind branches section",
            )


if __name__ == "__main__":
    unittest.main()
