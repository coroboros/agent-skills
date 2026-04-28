"""Performance budgets — protect hot-path scripts from silent regressions.

The budgets target frequently-invoked scripts on the critical path of
their respective workflows. A 10× regression on these would ship latency
to every user.

Budgets are deliberately generous to absorb CI variability on
`ubuntu-latest` (slower than dev hardware) — they catch real regressions,
not micro-optimisation drift. If a budget genuinely needs raising,
update the constant in this file and document why in the PR body.

We do NOT enforce a top-level suite-wall-clock budget here — that's
better left to CI's own job-timeout signal. Recursively running
`unittest discover` from inside a test introduces flaky timing without
adding meaningful protection beyond the per-script budgets below.
"""

import subprocess
import sys
import time
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS = REPO_ROOT / "skills"


# Per-script budgets (seconds). Calibrated for ubuntu-latest CI; local
# machines should run well under. Bump only with PR-body justification.
EXTRACT_RULES_BUDGET_SEC = 0.5
AUDIT_README_BUDGET_SEC = 0.5
VALIDATE_SPEC_BUDGET_SEC = 0.5
AUDIT_CLAUDE_MD_BUDGET_SEC = 0.5


class TestExtractRulesBudget(unittest.TestCase):
    """`brand-voice/scripts/extract_rules.py` is the hot path for the
    writing-v1 cluster: humanize-en invokes it on every -f voice doc to
    flatten the YAML and resolve any inheritance chain. A regression
    here lands latency in every humanize call across the brand."""

    def setUp(self):
        self.script = SKILLS / "brand-voice" / "scripts" / "extract_rules.py"
        # Use the chain-resolution fixture (child-founder extends parent-corp).
        # That's the realistic worst case — single-file fixtures would not
        # exercise the merge engine.
        self.fixture = (
            REPO_ROOT / "tests" / "brand-voice" / "fixtures" / "child-founder.md"
        )
        if not self.script.is_file():
            self.skipTest(f"extract_rules.py not present at {self.script}")
        if not self.fixture.is_file():
            self.skipTest(f"chain fixture not present at {self.fixture}")

    def test_chain_resolution_completes_under_budget(self):
        # Two runs — report the slower of the two so a one-off slow run
        # is not a free pass.
        timings = []
        for _ in range(2):
            t0 = time.perf_counter()
            r = subprocess.run(
                [sys.executable, str(self.script), str(self.fixture)],
                capture_output=True, text=True,
                timeout=10,
            )
            elapsed = time.perf_counter() - t0
            self.assertEqual(
                r.returncode, 0,
                f"extract_rules failed unexpectedly:\n{r.stderr}",
            )
            timings.append(elapsed)
        worst = max(timings)
        self.assertLess(
            worst, EXTRACT_RULES_BUDGET_SEC,
            f"extract_rules.py took {worst:.3f}s on the chain fixture "
            f"(budget {EXTRACT_RULES_BUDGET_SEC}s). Suspect a regression.",
        )


class TestValidateSpecBudget(unittest.TestCase):
    """`spec/scripts/validate_spec.py` runs on every spec.md before apex
    consumes it. The validator builds a workstream graph and runs
    cycle-detection — a quadratic regression here would surface as
    visible latency in the workflow cluster."""

    def setUp(self):
        self.script = SKILLS / "spec" / "scripts" / "validate_spec.py"
        if not self.script.is_file():
            self.skipTest(f"validate_spec.py not present at {self.script}")

    def _make_realistic_spec(self, td: Path) -> Path:
        """A 5-workstream linear-dependency spec — exercises split_blocks,
        validate_workstream, build_graph, find_cycle in a realistic shape."""
        spec = (
            "# Sample Spec\n\n"
            "## Summary\n\nBuild thing.\n\n"
            "## Workstreams\n\n"
        )
        for i in range(1, 6):
            dep = "—" if i == 1 else f"WS-{i-1}"
            spec += (
                f"### WS-{i}: Workstream {i}\n\n"
                f"| Priority | P{i % 2} |\n"
                f"| Complexity | M |\n"
                f"| Depends on | {dep} |\n\n"
                f"**Acceptance criteria:**\n\n"
                f"- [ ] Done\n\n"
            )
        path = td / "spec.md"
        path.write_text(spec, encoding="utf-8")
        return path

    def test_validate_spec_completes_under_budget(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            spec_path = self._make_realistic_spec(Path(td))
            timings = []
            for _ in range(2):
                t0 = time.perf_counter()
                r = subprocess.run(
                    [sys.executable, str(self.script), str(spec_path)],
                    capture_output=True, text=True,
                    timeout=10,
                )
                elapsed = time.perf_counter() - t0
                self.assertEqual(
                    r.returncode, 0,
                    f"validate_spec failed unexpectedly:\n{r.stderr}",
                )
                timings.append(elapsed)
            worst = max(timings)
            self.assertLess(
                worst, VALIDATE_SPEC_BUDGET_SEC,
                f"validate_spec.py took {worst:.3f}s on 5-WS fixture "
                f"(budget {VALIDATE_SPEC_BUDGET_SEC}s).",
            )


class TestAuditClaudeMdBudget(unittest.TestCase):
    """`claude-md/scripts/audit_claude_md.py` runs as the lint pass for
    CLAUDE.md files. A 500ms ceiling on a representative file catches
    a quadratic regression in the rule-walker."""

    def setUp(self):
        self.script = SKILLS / "claude-md" / "scripts" / "audit_claude_md.py"
        if not self.script.is_file():
            self.skipTest(f"audit_claude_md.py not present at {self.script}")

    def test_audit_claude_md_completes_under_budget(self):
        import tempfile
        # Use a synthetic CLAUDE.md with realistic content shape — short
        # enough to be valid input, long enough to exercise the scanner.
        sample = (
            "# Project\n\n"
            "## Stack\n\n"
            "- Runtime: Node.js\n"
            "- Language: TypeScript\n\n"
            "## Commands\n\n"
            "Run `pnpm test` to test.\n"
        ) * 5  # Repeat to get more content without bloat triggers.
        with tempfile.NamedTemporaryFile(
            "w", suffix=".md", delete=False, encoding="utf-8",
        ) as f:
            f.write(sample)
            path = Path(f.name)
        try:
            timings = []
            for _ in range(2):
                t0 = time.perf_counter()
                r = subprocess.run(
                    [sys.executable, str(self.script), str(path)],
                    capture_output=True, text=True,
                    timeout=10,
                )
                elapsed = time.perf_counter() - t0
                # exit 0 (clean) or 1 (findings) — both valid; we measure overhead.
                self.assertIn(
                    r.returncode, (0, 1),
                    f"audit_claude_md.py unexpected exit {r.returncode}:\n{r.stderr}",
                )
                timings.append(elapsed)
            worst = max(timings)
            self.assertLess(
                worst, AUDIT_CLAUDE_MD_BUDGET_SEC,
                f"audit_claude_md.py took {worst:.3f}s "
                f"(budget {AUDIT_CLAUDE_MD_BUDGET_SEC}s).",
            )
        finally:
            path.unlink(missing_ok=True)


class TestAuditReadmeBudget(unittest.TestCase):
    """`write-clear-readme/scripts/audit_readme.py` runs against every
    README touched by the audit/polish workflow. A 500ms ceiling on a
    realistic README protects the inner loop."""

    def setUp(self):
        self.script = SKILLS / "write-clear-readme" / "scripts" / "audit_readme.py"
        # Use the repo's own README as the realistic input — it exercises
        # anchor resolution, nested details detection, bloat scanning all
        # at once on real content.
        self.readme = REPO_ROOT / "README.md"
        if not self.script.is_file():
            self.skipTest(f"audit_readme.py not present at {self.script}")
        if not self.readme.is_file():
            self.skipTest(f"README.md not present at {self.readme}")

    def test_audit_readme_completes_under_budget(self):
        timings = []
        for _ in range(2):
            t0 = time.perf_counter()
            r = subprocess.run(
                [sys.executable, str(self.script), str(self.readme)],
                capture_output=True, text=True,
                timeout=10,
            )
            elapsed = time.perf_counter() - t0
            # The repo's own README may legitimately have audit findings —
            # exit 0 OR 1 is fine; we measure script overhead, not result.
            self.assertIn(
                r.returncode, (0, 1),
                f"audit_readme.py unexpected exit {r.returncode}:\n{r.stderr}",
            )
            timings.append(elapsed)
        worst = max(timings)
        self.assertLess(
            worst, AUDIT_README_BUDGET_SEC,
            f"audit_readme.py took {worst:.3f}s on the repo README "
            f"(budget {AUDIT_README_BUDGET_SEC}s). Suspect a regression.",
        )


if __name__ == "__main__":
    unittest.main()
