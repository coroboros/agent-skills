"""oneshot evals — every documented complexity-trigger and discipline
must map to a case. The skill's circuit breaker is what protects users
from a multi-hour wrong turn; if the evals don't pin its trigger
conditions, the breaker can drift silently."""

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EVALS_PATH = REPO_ROOT / "skills" / "oneshot" / "evals" / "evals.json"


def _cases():
    return json.loads(EVALS_PATH.read_text(encoding="utf-8"))["evals"]


class TestCircuitBreakerScenarios(unittest.TestCase):
    """The four documented circuit-breaker triggers (>5 files, >2 systems,
    cross-cutting, unclear requirements) must each have at least one
    case OR the trigger set is doc-only."""

    SCENARIOS = {
        "multi-file": ("5 files", ">5 files", "multi-file", "files across", "8 files"),
        "multi-system": (">2 distinct systems", "2 distinct systems", "auth + billing",
                         "api, the web app, and the mobile"),
        "cross-cutting": ("cross-cutting", "database migration", "migration + multi-component"),
    }

    def test_each_trigger_has_a_case(self):
        cases = _cases()
        for trigger, keywords in self.SCENARIOS.items():
            with self.subTest(trigger=trigger):
                hits = []
                for case in cases:
                    blob = (case.get("prompt", "") + " " + case.get("expected_output", "")).lower()
                    if any(kw.lower() in blob for kw in keywords):
                        hits.append(case.get("name") or case["id"])
                self.assertGreater(
                    len(hits), 0,
                    f"no eval covers circuit-breaker trigger '{trigger}'. "
                    f"Expected prompt or expected_output to mention one of: {keywords}",
                )


class TestEscalationRecommendation(unittest.TestCase):
    """When the breaker fires, the skill must recommend `/apex` or `/spec`.
    At least one case must verify the escalation recommendation."""

    def test_escalation_target_named(self):
        cases = _cases()
        hits = []
        for case in cases:
            expected = case.get("expected_output", "")
            if "/apex" in expected or "/spec" in expected:
                hits.append(case.get("name") or case["id"])
        self.assertGreater(
            len(hits), 0,
            "no eval verifies the escalation recommendation. "
            "Expected at least one case where expected_output names /apex or /spec.",
        )


class TestStaysInScopeDiscipline(unittest.TestCase):
    """oneshot's 'one task only — no tangential improvements' rule is the
    skill's identity. At least one case must pin a no-side-quest scenario:
    a trivial edit where the expected behaviour is to NOT refactor, NOT
    add comments, NOT improve unrelated code."""

    def test_at_least_one_stays_in_scope_case(self):
        cases = _cases()
        signals = ("does not refactor", "no tangential", "exactly one file",
                   "stays in scope", "no comments")
        hits = []
        for case in cases:
            expected = case.get("expected_output", "").lower()
            if any(s in expected for s in signals):
                hits.append(case.get("name") or case["id"])
        self.assertGreater(
            len(hits), 0,
            "no eval pins the 'stays in scope / one task only' discipline. "
            "Add a trivial-edit case where the expected behaviour explicitly "
            "rules out refactoring or tangential improvements.",
        )


class TestStuckAfterTwoAttemptsDiscipline(unittest.TestCase):
    """The 'stuck after 2 attempts → stop and report' rule prevents runaway
    thrash. At least one case must verify the 2-attempt cap."""

    def test_at_least_one_thrash_cap_case(self):
        cases = _cases()
        signals = ("2 attempts", "two attempts", "stops", "thrash", "blocker")
        hits = []
        for case in cases:
            expected = case.get("expected_output", "").lower()
            if any(s in expected for s in signals):
                hits.append(case.get("name") or case["id"])
        self.assertGreater(
            len(hits), 0,
            "no eval pins the 'stuck after 2 attempts → stop' rule. "
            "Add a case where after 2 failed attempts the skill reports and stops.",
        )


class TestGitHubIssueResolution(unittest.TestCase):
    """The Resolve phase accepts `#N`, `owner/repo#N`, or a GitHub URL and
    fetches via `gh issue view`. At least one case must verify this
    resolution path — without it, the documented input format is fiction."""

    def test_at_least_one_github_issue_case(self):
        cases = _cases()
        hits = []
        for case in cases:
            blob = case.get("prompt", "") + " " + case.get("expected_output", "")
            if "gh issue view" in blob or "#42" in blob or "github.com" in blob.lower():
                hits.append(case.get("name") or case["id"])
        self.assertGreater(
            len(hits), 0,
            "no eval verifies the GitHub issue resolution path "
            "(`#N` or `gh issue view ...`).",
        )


if __name__ == "__main__":
    unittest.main()
