"""award-design in-page detector — asset contract.

The detector ships as a browser-injected file, so its safety properties are
textual: no module syntax on the evaluate_script path, a parseable RULES
registry, FLOORS as the one literal both the JS and detector.md mirror, and
the catches-never-clears doctrine present where the model will read it. These
tests also pin detector.md to the registry — a rule the reference never names
is a rule the audit never runs."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
ASSET = SKILL_DIR / "assets" / "detector.js"
DETECTOR_MD = SKILL_DIR / "references" / "detector.md"

FLOORS_LITERAL = "const FLOORS = { scale: 1.04, deltaL: 0.04, translatePx: 2, opacity: 0.1 };"
FOOTER = "Catches, never clears — composition, desire, fidelity, copy, pacing, seams stay judgment."

RULE_RE = re.compile(r"\{\s*id:\s*'([^']+)',\s*severity:\s*'([^']+)',\s*box:\s*'([^']+)'\s*\}")
UPPER_KEBAB = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*$")
BOX_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MODULE_SYNTAX = re.compile(r"^(?:import\s|export\s|require\(|(?:const|let|var)\s.*=\s*require\()")

# The spec-named rules; the registry may grow, never shrink below these.
REQUIRED_IDS = {
    "FONT-RESOLVE", "SUBSTRATE-DEAD", "DEAD", "HOMEOPATHIC", "UNMEASURED-JS",
    "CONTRAST", "UNCOMPUTABLE-BG", "NAV-BORDER", "TOKEN-CONFORM", "H1-LINES",
    "IDLE-CHANNEL", "IMG-BROKEN", "H-OVERFLOW", "TAP-TARGET",
}


def _rules(source):
    return RULE_RE.findall(source)


class TestDetectorAsset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert ASSET.is_file(), f"missing detector asset: {ASSET}"
        cls.source = ASSET.read_text(encoding="utf-8")

    def test_size_under_64kb(self):
        self.assertLess(ASSET.stat().st_size, 64 * 1024)

    def test_no_top_level_module_syntax(self):
        """evaluate_script runs the file as a classic script — any top-level
        import/export/require breaks the browser injection path."""
        offenders = [
            f"{i}: {line.rstrip()}"
            for i, line in enumerate(self.source.splitlines(), 1)
            if MODULE_SYNTAX.match(line)
        ]
        self.assertEqual([], offenders)

    def test_rules_registry_shape(self):
        rules = _rules(self.source)
        self.assertTrue(rules, "RULES registry not parseable from the asset")
        for rule_id, severity, box in rules:
            with self.subTest(rule=rule_id):
                self.assertRegex(rule_id, UPPER_KEBAB)
                self.assertIn(severity, {"FAIL", "REVIEW"})
                self.assertRegex(box, BOX_SLUG)

    def test_spec_rules_present(self):
        ids = {rule_id for rule_id, _, _ in _rules(self.source)}
        self.assertLessEqual(REQUIRED_IDS, ids, f"missing rules: {REQUIRED_IDS - ids}")

    def test_floors_literal_exact(self):
        """FLOORS is the single source of truth — the literal must not drift."""
        self.assertIn(FLOORS_LITERAL, self.source)

    def test_footer_doctrine_present(self):
        self.assertIn(FOOTER, self.source)


class TestDetectorReference(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert DETECTOR_MD.is_file(), f"missing reference: {DETECTOR_MD}"
        cls.md = DETECTOR_MD.read_text(encoding="utf-8")
        cls.rule_ids = {rule_id for rule_id, _, _ in _rules(ASSET.read_text(encoding="utf-8"))}

    def test_names_every_rule(self):
        """A rule detector.md never names is a finding the model cannot route."""
        for rule_id in sorted(self.rule_ids):
            with self.subTest(rule=rule_id):
                self.assertIn(rule_id, self.md)

    def test_states_the_floors(self):
        for value in ("1.04", "0.04", "2px", "0.1"):
            with self.subTest(floor=value):
                self.assertIn(value, self.md)

    def test_injection_recipe_present(self):
        self.assertIn("awardDetector.run", self.md)

    def test_doctrine_present(self):
        self.assertIn("catches, it never clears", self.md)


if __name__ == "__main__":
    unittest.main()
