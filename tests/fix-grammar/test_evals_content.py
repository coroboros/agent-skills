"""fix-grammar evals — pin the documented disciplines in the eval set.

The skill's contract (no rephrasing, no translation, no style edits,
preserve code blocks/frontmatter, parallelise multi-file) is encoded
in the SKILL.md `Rules` section. Each discipline must have a
corresponding eval case — otherwise the rule is a doc claim, not a
behavioural guarantee.
"""

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EVALS_PATH = REPO_ROOT / "skills" / "fix-grammar" / "evals" / "evals.json"


def _cases():
    return json.loads(EVALS_PATH.read_text(encoding="utf-8"))["evals"]


class TestDisciplineCoverage(unittest.TestCase):
    """Each documented discipline gets a case that exercises it. The mapping
    is keyword-based against `expected_output` — adjust the keywords if a
    case is renamed, but never drop a discipline silently."""

    DISCIPLINES = {
        # discipline_label: keywords any of which must appear in expected_output
        "typo-fixing": ("typo", "their", "wos", "fixed"),
        "code-block-preservation": ("code block", "fenced", "verbatim"),
        "frontmatter-preservation": ("frontmatter", "yaml"),
        "multilingual-content": ("french", "accent", "déployé", "multilingual"),
        "refuse-rephrasing": ("decline", "rephrase", "unchanged", "redirects"),
        "multi-file-parallelism": ("subagent", "parallel", "spawn"),
    }

    def test_each_discipline_has_a_case(self):
        cases = _cases()
        for discipline, keywords in self.DISCIPLINES.items():
            with self.subTest(discipline=discipline):
                hits = []
                for case in cases:
                    expected = case.get("expected_output", "").lower()
                    if any(kw.lower() in expected for kw in keywords):
                        hits.append(case.get("name") or case["id"])
                self.assertGreater(
                    len(hits), 0,
                    f"no eval case covers discipline '{discipline}'. "
                    f"Expected expected_output to mention one of: {keywords}",
                )


class TestNoStyleImprovements(unittest.TestCase):
    """The 'no style improvements' clause is the most likely to drift —
    a reviewer might tolerate a stylistic suggestion. Pin a case that
    explicitly verifies a grammatically-valid sentence is returned
    unchanged (no style cleanup, no flagging of redundant words)."""

    def test_at_least_one_no_style_case(self):
        cases = _cases()
        signals = ("returns sentence unchanged", "no spelling or grammar errors",
                   "redundant", "stylistic")
        hits = []
        for case in cases:
            expected = case.get("expected_output", "").lower()
            if any(s in expected for s in signals):
                hits.append(case.get("name") or case["id"])
        self.assertGreater(
            len(hits), 0,
            "no eval pins the 'no style improvements' clause. "
            "Add a case where the input is grammatically valid and the "
            "expected behaviour is to return it unchanged.",
        )


class TestRefuseTranslation(unittest.TestCase):
    """The 'no translation' rule is critical for multilingual repos —
    a French sentence with a typo must remain French. At least one case
    must explicitly verify this (multilingual content with non-English text)."""

    def test_at_least_one_multilingual_case(self):
        cases = _cases()
        # French content is the canonical test (matches the SKILL.md example).
        # Any non-ASCII-prose case satisfies the broader rule.
        hits = []
        for case in cases:
            prompt = case.get("prompt", "")
            # Heuristic: presence of accented chars or French articles
            if any(c in prompt for c in "éèàçùâêîôû") or " la " in prompt or " le " in prompt:
                hits.append(case.get("name") or case["id"])
        self.assertGreater(
            len(hits), 0,
            "no eval contains multilingual prose — the no-translation rule "
            "needs an explicit case (e.g. French with a missing accent).",
        )


if __name__ == "__main__":
    unittest.main()
