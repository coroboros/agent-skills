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
