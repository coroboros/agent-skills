"""forge emits one artifact following templates/forge-artifact.md.
The template's section structure must remain stable — drift breaks the artifact
shape that `/apex -f` consumes (the `# Spec:` + `## Workstreams` closure shape)."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATE = REPO_ROOT / "skills" / "forge" / "templates" / "forge-artifact.md"


# H2 sections in canonical order. Decision + Assumption ledger + Research
# findings lead (the brief-derived header, research made visible); the spec
# body (Overview…Execution order) follows, with Kill criteria after Risks.
REQUIRED_SECTIONS = [
    "Decision",
    "Assumption ledger",
    "Research findings",
    "Overview",
    "Goals",
    "Non-goals",
    "Background",
    "Workstreams",
    "Dependencies",
    "Risks",
    "Kill criteria",
    "Open questions",
    "Parking lot",
    "Execution order",
]


class TestArtifactTemplate(unittest.TestCase):
    def test_template_exists(self):
        self.assertTrue(TEMPLATE.is_file(), "forge-artifact.md missing")

    def test_template_non_empty(self):
        self.assertGreater(len(TEMPLATE.read_text(encoding="utf-8")), 0)

    def test_required_sections_present(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        for section in REQUIRED_SECTIONS:
            with self.subTest(section=section):
                self.assertRegex(text, rf"##+\s+{re.escape(section)}",
                                 f"forge-artifact missing section: {section}")

    def test_sections_at_h2_level(self):
        """Every required section sits at level 2 (`##`). Bumping one to ### or #
        would break section parsing and the apex spec-closure heuristic that keys
        on `## Workstreams`."""
        text = TEMPLATE.read_text(encoding="utf-8")
        for section in REQUIRED_SECTIONS:
            with self.subTest(section=section):
                pattern = rf"^##\s+{re.escape(section)}"
                self.assertTrue(re.search(pattern, text, re.MULTILINE),
                                f"{section}: not at H2 level")

    def test_sections_in_canonical_order(self):
        """Section order is part of the contract — Decision leads (the chosen
        approach), Execution order trails. A reordered template breaks the
        decision-first read and downstream consumer expectations."""
        text = TEMPLATE.read_text(encoding="utf-8")
        positions = []
        for section in REQUIRED_SECTIONS:
            m = re.search(rf"^##\s+{re.escape(section)}", text, re.MULTILINE)
            self.assertIsNotNone(m, f"{section}: not found")
            positions.append((m.start(), section))
        sorted_by_pos = [s for _, s in sorted(positions)]
        self.assertEqual(sorted_by_pos, REQUIRED_SECTIONS,
                         f"sections out of order: {sorted_by_pos}")

    def test_default_h1_is_decision_spec_documented(self):
        """Routing flipped: Decision is the default H1; Spec is the promotion.
        The template H1 must start `# Decision:` so the default emission is
        terminal (no workstreams, present-and-pause). The Spec variant must
        be documented inline so the promotion path keeps the apex § 0a
        closure (`# Spec:` + `## Workstreams`)."""
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertTrue(
            text.lstrip().startswith("# Decision:"),
            "forge-artifact template H1 must default to `# Decision:` per routing rule",
        )
        self.assertIn(
            "# Spec:", text,
            "template must document the promoted `# Spec:` variant for apex closure",
        )


class TestTemplatePlaceholders(unittest.TestCase):
    """Phase 4 fills `{title}` and `{YYYY-MM-DD}`. Drift in placeholder syntax
    breaks substitution silently — the rendered artifact carries literal
    placeholder text into the output."""

    def test_title_placeholder_present(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("{title}", text,
                      "template missing {title} placeholder in title")

    def test_date_placeholder_present(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("{YYYY-MM-DD}", text,
                      "template missing {YYYY-MM-DD} date placeholder")


if __name__ == "__main__":
    unittest.main()
