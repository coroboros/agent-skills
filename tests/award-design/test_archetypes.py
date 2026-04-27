"""award-design has 9 archetypes — each must have its own reference file
plus the supporting cross-cutting refs. Catches drift when an archetype is
added to the SKILL.md selector without a matching reference file."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
REFS = SKILL_DIR / "references"
SKILL_MD = SKILL_DIR / "SKILL.md"


# Stable archetype identifiers (kebab-case file stems)
ARCHETYPES = [
    "minimalist",
    "brutalist",
    "editorial",
    "bold-maximal",
    "immersive-cinematic",
    "experimental",
    "corporate-luxury",
    "bento-card",
    "spatial-organic",
]

# Cross-cutting references that must exist for the workflow to function
CROSS_CUTTING = [
    "anti-patterns.md",
    "audit-rubric.md",
    "brand-extraction.md",
    "exemplars.md",
    "foundations.md",
    "production-hardening.md",
    "remixing.md",
]


class TestArchetypeReferences(unittest.TestCase):
    def test_each_archetype_has_reference_file(self):
        for archetype in ARCHETYPES:
            with self.subTest(archetype=archetype):
                self.assertTrue((REFS / f"{archetype}.md").is_file(),
                                f"references/{archetype}.md missing")

    def test_no_orphan_archetype_files(self):
        """Every .md in references/ that isn't cross-cutting should be a known archetype."""
        known = set(ARCHETYPES) | {p.replace(".md", "") for p in CROSS_CUTTING}
        for ref in REFS.glob("*.md"):
            with self.subTest(ref=ref.name):
                stem = ref.stem
                self.assertIn(stem, known,
                              f"orphan reference file: references/{ref.name}")


class TestCrossCuttingReferences(unittest.TestCase):
    def test_each_cross_cutting_ref_exists(self):
        for ref in CROSS_CUTTING:
            with self.subTest(ref=ref):
                self.assertTrue((REFS / ref).is_file(),
                                f"references/{ref} missing")


class TestArchetypeSelectorTable(unittest.TestCase):
    """The 'Archetype Selector' table in SKILL.md must list all 9 archetypes
    and reference each archetype's `references/<name>.md` file."""

    def test_table_lists_every_archetype(self):
        text = SKILL_MD.read_text(encoding="utf-8")
        for archetype in ARCHETYPES:
            with self.subTest(archetype=archetype):
                # Each archetype's reference path appears in a table cell
                self.assertIn(f"references/{archetype}.md", text,
                              f"{archetype}: not referenced in SKILL.md")

    def test_table_row_count_matches(self):
        """Count rows in the Archetype Selector table — should be 9 (one per archetype)."""
        text = SKILL_MD.read_text(encoding="utf-8")
        m = re.search(r"## Archetype Selector\s*\n(.*?)(?=^##|\Z)",
                      text, re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, "Archetype Selector section missing")
        section = m.group(1)
        # Body rows: lines starting with `|` and ending with `|`, excluding header and separator
        rows = re.findall(r"^\|\s*\*\*[\w/ -]+\*\*\s*\|", section, re.MULTILINE)
        self.assertEqual(len(rows), 9, f"expected 9 archetype rows, found {len(rows)}")


if __name__ == "__main__":
    unittest.main()
