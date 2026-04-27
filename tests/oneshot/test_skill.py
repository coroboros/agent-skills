"""oneshot — circuit-breaker contract documented in SKILL.md must remain stable."""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "skills" / "brand-voice" / "scripts"))

from utils import parse_yaml_minimal, split_frontmatter  # noqa: E402

SKILL_MD = REPO_ROOT / "skills" / "oneshot" / "SKILL.md"


def _frontmatter():
    text = SKILL_MD.read_text(encoding="utf-8")
    fm_text, _ = split_frontmatter(text)
    return parse_yaml_minimal(fm_text) if fm_text else {}


def _body():
    return SKILL_MD.read_text(encoding="utf-8")


class TestOneshotFrontmatter(unittest.TestCase):
    def test_model_sonnet(self):
        """oneshot is sonnet-tier — bounded reasoning for fast turnarounds."""
        fm = _frontmatter()
        self.assertEqual(fm.get("model"), "sonnet")

    def test_argument_hint_format(self):
        fm = _frontmatter()
        hint = fm.get("argument-hint", "")
        self.assertGreater(len(hint), 0)
        self.assertTrue(hint.startswith('"<') or hint.startswith("<"),
                        "argument-hint should start with a placeholder")


class TestCircuitBreakerDocumented(unittest.TestCase):
    """oneshot escalates to /apex or /spec when complexity signals trip.
    The doc must mention these escalation paths so users know the contract."""

    def test_mentions_apex_escalation(self):
        body = _body()
        self.assertIn("/apex", body, "missing /apex escalation reference")

    def test_mentions_spec_escalation(self):
        body = _body()
        self.assertIn("/spec", body, "missing /spec escalation reference")

    def test_mentions_complexity_signals(self):
        """The skill describes when to escalate. Look for terms like 'complexity',
        'circuit breaker', or 'too complex' in the body — at least one must appear."""
        body = _body().lower()
        signals = ["complexity", "circuit breaker", "too complex", "more complex"]
        self.assertTrue(any(s in body for s in signals),
                        "no complexity/escalation language found in SKILL.md")


if __name__ == "__main__":
    unittest.main()
