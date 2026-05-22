"""Tests for the deliverable-hygiene enforcement in apex step-03 + step-04.

apex implements specs whose workstreams are labeled WS-N; without a guard it
carries those labels (and other internal scaffolding) into the code, comments,
and commits it produces. step-03 states the rule, step-04 gates on it before
completion. These tests pin both so the enforcement can't silently regress.
"""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
APEX_STEPS = REPO_ROOT / "skills" / "apex" / "steps"
STEP_03 = APEX_STEPS / "step-03-execute.md"
STEP_04 = APEX_STEPS / "step-04-examine.md"


class TestStep03StatesTheRule(unittest.TestCase):
    def setUp(self):
        self.text = STEP_03.read_text(encoding="utf-8")

    def test_has_deliverable_hygiene_section(self):
        self.assertIn("## Deliverable hygiene", self.text)

    def test_covers_label_translation(self):
        # The canonical leak: carrying a spec's task labels into deliverables.
        self.assertIn("Translate internal labels", self.text)

    def test_covers_machinery_references(self):
        for token in ("plan", "spec", "postmortem"):
            self.assertIn(token, self.text)

    def test_covers_useless_comments(self):
        self.assertIn("Comment the why", self.text)


class TestStep04GatesOnIt(unittest.TestCase):
    def setUp(self):
        self.text = STEP_04.read_text(encoding="utf-8")

    def test_self_audit_has_deliverable_hygiene_block(self):
        self.assertIn("Deliverable Hygiene", self.text)

    def test_gate_names_the_label_leak(self):
        idx = self.text.index("Deliverable Hygiene")
        block = self.text[idx:idx + 600]
        self.assertIn("WS-N", block)


if __name__ == "__main__":
    unittest.main()
