"""oneshot — circuit-breaker contract documented in SKILL.md must remain stable."""

import re
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
    The 'Complexity check (circuit breaker)' section must exist AND mention both
    escalation targets within its scope — not just somewhere in the file. Catches
    a real regression where the section gets refactored away while leaving stale
    `/apex` mentions elsewhere (e.g., in workflow narrative)."""

    def _circuit_breaker_section(self):
        """Return the body of the 'Complexity check' / 'circuit breaker' section."""
        body = _body()
        # Match `### N. Complexity check (circuit breaker)` through next `### ` or `## `
        m = re.search(
            r"^###\s+[\w.]+\s+Complexity check.*?circuit breaker.*?\n(.*?)(?=^###?\s|\Z)",
            body,
            re.DOTALL | re.MULTILINE | re.IGNORECASE,
        )
        return m.group(1) if m else None

    def test_circuit_breaker_section_exists(self):
        section = self._circuit_breaker_section()
        self.assertIsNotNone(section,
                             "missing '### N. Complexity check (circuit breaker)' section")

    def test_section_names_apex_as_escalation(self):
        """`/apex` must be cited inside the circuit-breaker section, not just anywhere."""
        section = self._circuit_breaker_section()
        self.assertIsNotNone(section, "circuit-breaker section missing")
        self.assertIn("/apex", section,
                      "/apex not mentioned within the circuit-breaker section")

    def test_section_names_spec_as_escalation(self):
        section = self._circuit_breaker_section()
        self.assertIsNotNone(section, "circuit-breaker section missing")
        self.assertIn("/spec", section,
                      "/spec not mentioned within the circuit-breaker section")

    def test_section_describes_signals(self):
        """The circuit-breaker section must describe what trips it — at least one
        of: 'files', 'domains', 'cross-cutting', 'unfamiliar', or a numeric threshold."""
        section = self._circuit_breaker_section()
        self.assertIsNotNone(section, "circuit-breaker section missing")
        signals = ["files", "domains", "cross-cutting", "unfamiliar", "complex"]
        section_lower = section.lower()
        hits = [s for s in signals if s in section_lower]
        self.assertGreater(len(hits), 0,
                           f"circuit-breaker section names none of: {signals}")


if __name__ == "__main__":
    unittest.main()
