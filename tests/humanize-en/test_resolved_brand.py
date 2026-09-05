"""Exercise the resolver-to-consumer contract without importing sibling modules."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
EXTRACT = ROOT / "skills/brand-voice/scripts/extract_rules.py"
SCRIPTS = ROOT / "skills/humanize-en/scripts"
FIXTURES = ROOT / "tests/brand-voice/fixtures"


class TestResolvedBrand(unittest.TestCase):
    def run_cli(self, script, *args):
        return subprocess.run([sys.executable, str(script), *map(str, args)],
                              capture_output=True, text=True)

    def scan_resolved(self, fixture, prose):
        extraction = self.run_cli(EXTRACT, "--resolved-json", FIXTURES / fixture)
        self.assertEqual(extraction.returncode, 0, extraction.stderr)
        rules = json.loads(extraction.stdout)
        self.assertNotIn("extends", rules["voice"])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            voice = root / "rules.json"
            voice.write_text(extraction.stdout)
            draft = root / "draft.md"
            draft.write_text(prose)
            scan = self.run_cli(SCRIPTS / "prescan.py", "--rules-json", voice, draft)
            validation = self.run_cli(SCRIPTS / "validate.py", "--rules-json", voice, draft)
            self.assertEqual(scan.returncode, 0, scan.stderr)
            self.assertEqual(validation.returncode, 0, validation.stderr)
            hits = json.loads(scan.stdout)
            self.assertEqual(hits, json.loads(validation.stdout)["residuals"])
        return rules, [h for h in hits if h.get("source") == "brand"]

    def test_parent_rules_reach_both_consumers(self):
        _, hits = self.scan_resolved("child-pure-inherit.md", "The synergies last.")
        self.assertTrue(any(h["rule_id"] == "forbidden_lexicon:synergies" for h in hits))

    def test_remove_and_replace_reach_both_consumers(self):
        rules, hits = self.scan_resolved("child-founder.md", "I am passionate about synergies.")
        self.assertEqual(rules["pronouns"]["forbid"], [])
        self.assertNotIn("passionate", rules["forbidden_lexicon"])
        self.assertEqual([h["rule_id"] for h in hits], ["forbidden_lexicon:synergies"])

    def test_rule_override_keeps_one_effective_rule(self):
        rules, hits = self.scan_resolved("child-override-rule.md", "It might be worth considering...")
        effective = [r for r in rules["rewrite_rules"] if r["rule_id"] == "no-hedging-imperative"]
        self.assertEqual(len(effective), 1)
        self.assertEqual(effective[0]["accept"], "Just do X.")
        self.assertEqual(len([h for h in hits if h["rule_id"] == "rewrite_rule:no-hedging-imperative"]), 1)

    def test_bad_chain_never_emits_resolved_success(self):
        for fixture in ["cycle-a.md", "missing-parent.md"]:
            with self.subTest(fixture=fixture):
                result = self.run_cli(EXTRACT, "--resolved-json", FIXTURES / fixture)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertIn("extends", result.stderr)

    def test_standalone_raw_inheritance_fails_with_rerun_guidance(self):
        with tempfile.TemporaryDirectory() as directory:
            draft = Path(directory) / "draft.md"
            draft.write_text("The synergies last.")
            for script in ["prescan.py", "validate.py"]:
                result = self.run_cli(SCRIPTS / script, "--brand", FIXTURES / "child-pure-inherit.md", draft)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertIn("--rules-json", result.stderr)
                self.assertIn("npx skills add", result.stderr)

    def test_invalid_explicit_rules_never_clean(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft = root / "draft.md"
            draft.write_text("The file exists.")
            rules = root / "rules.json"
            for value in ["[]", "broken", '{"voice":{"extends":"parent.md"}}']:
                rules.write_text(value)
                for script in ["prescan.py", "validate.py"]:
                    result = self.run_cli(SCRIPTS / script, "--rules-json", rules, draft)
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertEqual(result.stdout, "")

    def test_falsy_inheritance_directives_never_clean(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft = root / "draft.md"
            draft.write_text("The file exists.")
            rules = root / "rules.json"
            brand = root / "brand.md"
            for value in (None, False, 0, []):
                rules.write_text(json.dumps({"voice": {"extends": value}}))
                brand.write_text(f"---\nvoice:\n  extends: {json.dumps(value)}\n---\n")
                for script in ("prescan.py", "validate.py"):
                    for flag, source in (("--brand", brand), ("--rules-json", rules)):
                        with self.subTest(value=value, script=script, flag=flag):
                            result = self.run_cli(SCRIPTS / script, flag, source, draft)
                            self.assertNotEqual(result.returncode, 0, result.stdout)
                            self.assertEqual(result.stdout, "")
                            self.assertIn("unresolved voice.extends", result.stderr)


if __name__ == "__main__":
    unittest.main()
