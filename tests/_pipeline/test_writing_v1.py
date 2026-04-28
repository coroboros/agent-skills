"""Pipeline contract: brand-voice → humanize-en.

humanize-en's SKILL.md documents that `-f <voice-doc>` triggers an invocation
of `extract_rules.py` (from brand-voice) to flatten YAML, resolve any
voice.extends chain, and emit merged rules. This test runs extract_rules on
a real fixture (child-founder extends parent-corp) and asserts the merged
output flows through correctly — pins the cross-skill interface.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _contracts import CLUSTERS  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EXTRACT_RULES = REPO_ROOT / "skills" / "brand-voice" / "scripts" / "extract_rules.py"
BRAND_VOICE_FIXTURES = REPO_ROOT / "tests" / "brand-voice" / "fixtures"
HUMANIZE_SKILL = REPO_ROOT / "skills" / "humanize-en" / "SKILL.md"


WV1 = CLUSTERS["writing-v1"]


class TestExtractRulesFlowsToHumanize(unittest.TestCase):
    """The merged forbidden_lexicon and rewrite_rules from extract_rules.py
    must contain the data humanize-en's prompt expects to read."""

    def test_chain_resolution_emits_merged_lexicon(self):
        r = subprocess.run(
            [sys.executable, str(EXTRACT_RULES),
             str(BRAND_VOICE_FIXTURES / "child-founder.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(r.returncode, 0,
                         f"extract_rules failed:\n{r.stderr}")
        # Parent's forbidden_lexicon: game-changing, passionate, synergies.
        # Child adds: thought leader. Child removes: passionate.
        self.assertIn("game-changing", r.stdout)
        self.assertIn("synergies", r.stdout)
        self.assertIn("thought leader", r.stdout)
        # `passionate` must be removed from the merged output.
        self.assertNotIn("passionate", r.stdout)

    def test_explain_json_shape_humanize_can_consume(self):
        """humanize-en may consume --explain-json — verify the keys it depends
        on (chain + merged with provenance) are present and stable."""
        r = subprocess.run(
            [sys.executable, str(EXTRACT_RULES), "--explain-json",
             str(BRAND_VOICE_FIXTURES / "child-founder.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(r.returncode, 0)
        data = json.loads(r.stdout)
        self.assertIn("chain", data)
        self.assertIn("merged", data)
        # Each forbidden entry carries source provenance — humanize-en uses
        # this to attribute rules in its report.
        self.assertIn("forbidden_lexicon", data["merged"])
        for entry in data["merged"]["forbidden_lexicon"]:
            self.assertIn("source", entry)
            self.assertIn("value", entry)


class TestHumanizeDocumentsExtractRulesPath(unittest.TestCase):
    """humanize-en's SKILL.md must document the extract_rules.py resolution
    chain plus a graceful fallback when brand-voice is not installed."""

    def test_skill_references_extract_rules_script(self):
        text = HUMANIZE_SKILL.read_text(encoding="utf-8")
        self.assertIn(WV1["consumer_reader_script"], text)
        # Sibling install path is the first fallback the skill walks.
        self.assertIn("brand-voice/scripts/extract_rules.py", text)

    def test_skill_documents_fallback_for_missing_brand_voice(self):
        text = HUMANIZE_SKILL.read_text(encoding="utf-8").lower()
        # Fallback path: read voice doc directly via Read, parse YAML inline.
        self.assertIn("fallback", text)


if __name__ == "__main__":
    unittest.main()
