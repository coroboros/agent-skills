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


# Stable archetype identifiers (kebab-case file stems).
#
# IMPORTANT — cross-skill duplication: this list is mirrored in
# `skills/design-system/references/subcommand-init.md` (the kebab-case slug
# enumeration in the "On archetype flavors" section). When adding, removing,
# or renaming an archetype here, update that file in the same PR. The two
# skills form a contract — `award-design` produces a DESIGN.md, `design-system`
# governs it — and `init` needs to know which slugs are valid without loading
# the `award-design` selector table.
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

# Cross-cutting references that must exist for the protocol to function
CROSS_CUTTING = [
    "anti-patterns.md",
    "atmosphere-calibration.md",
    "audit-rubric.md",
    "award-imperatives.md",
    "brand-extraction.md",
    "design-md-anatomy.md",
    "exemplars.md",
    "external-truth.md",
    "foundations.md",
    "imagery.md",
    "inspiration.md",
    "optical-craft.md",
    "preflight.md",
    "premium-patterns.md",
    "production-hardening.md",
    "remixing.md",
    "retrofit.md",
    "ship-ready-floor.md",
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


class TestArchetypeTable(unittest.TestCase):
    """The archetype table in SKILL.md (Phase 0 — Read the room) must list all
    9 archetypes and reference each archetype's `references/<name>.md` file.
    This is the direction layer the Concept Spine draws its line from — a
    missing row silently strands a brief."""

    def _table_section(self):
        text = SKILL_MD.read_text(encoding="utf-8")
        m = re.search(r"^## Phase 0 — Read the room\b.*?\n(.*?)(?=^##\s)",
                      text, re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, "## Phase 0 — Read the room section missing")
        return m.group(1)

    def test_table_lists_every_archetype(self):
        text = SKILL_MD.read_text(encoding="utf-8")
        for archetype in ARCHETYPES:
            with self.subTest(archetype=archetype):
                # Each archetype's reference path appears in a table cell
                self.assertIn(f"references/{archetype}.md", text,
                              f"{archetype}: not referenced in SKILL.md")

    def test_table_row_count_matches(self):
        """Count rows in the archetype table — should be 9 (one per archetype)."""
        section = self._table_section()
        # Body rows: lines whose first cell is a bold archetype name, excluding
        # header and separator.
        rows = re.findall(r"^\|\s*\*\*[\w/ -]+\*\*\s*\|", section, re.MULTILINE)
        self.assertEqual(len(rows), 9, f"expected 9 archetype rows, found {len(rows)}")

    def test_brief_signal_routing_is_inline_prose(self):
        """Brief-signal → archetype routing is now inline prose under the table,
        not its own section. Every archetype must still be reachable by a brief
        signal — otherwise a vocabulary lookup routes nowhere."""
        section = self._table_section()
        m = re.search(r"Brief signal → first-pass archetype(.*?)(?=^##\s|\Z)",
                      section, re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, "inline brief-signal routing prose missing under the table")
        routing = m.group(1)
        for display in (
            "Corporate Luxury", "Minimalist", "Editorial", "Brutalist",
            "Bold/Maximal", "Immersive", "Experimental", "Bento", "Spatial Organic",
        ):
            with self.subTest(target=display):
                self.assertRegex(
                    routing, rf"→\s*{re.escape(display)}\b",
                    f"brief-signal routing must reach the {display} archetype",
                )


class TestAtmosphereCalibration(unittest.TestCase):
    """Atmosphere Calibration has two tables that drive design decisions:
    (1) the axis-range table (3 axes × 3 ranges) and (2) the default-scores table
    (9 archetypes × 3 axes). Both must stay aligned with the archetype list — drift
    here corrupts atmosphere calibration silently. Both tables live in
    references/atmosphere-calibration.md; SKILL.md carries only the pointer."""

    AXES = ["Density", "Variance", "Motion"]
    CALIBRATION_MD = REFS / "atmosphere-calibration.md"

    def _atmosphere_section(self):
        self.assertTrue(
            self.CALIBRATION_MD.is_file(),
            "references/atmosphere-calibration.md must exist after the refactor",
        )
        return self.CALIBRATION_MD.read_text(encoding="utf-8")

    def test_axis_table_lists_three_axes(self):
        """The axis-range table has one body row per axis (Density, Variance, Motion)."""
        section = self._atmosphere_section()
        for axis in self.AXES:
            with self.subTest(axis=axis):
                pattern = rf"\|\s*\*\*{axis}\*\*\s*\|"
                self.assertRegex(section, pattern, f"axis row for '{axis}' missing")

    def test_default_scores_row_per_archetype(self):
        """Each archetype must have a row in the default-scores table with three numeric scores."""
        section = self._atmosphere_section()
        # Map kebab → display name as it appears in the scores table (Title Case with separators)
        display_names = {
            "minimalist": "Minimalist",
            "brutalist": "Brutalist",
            "editorial": "Editorial",
            "bold-maximal": "Bold / Maximal",
            "immersive-cinematic": "Immersive / Cinematic",
            "experimental": "Experimental",
            "corporate-luxury": "Corporate Luxury",
            "bento-card": "Bento / Card",
            "spatial-organic": "Spatial Organic",
        }
        for archetype in ARCHETYPES:
            display = display_names[archetype]
            with self.subTest(archetype=archetype):
                # Match `| Display | <int> | <int> | <int> |` row
                pattern = rf"\|\s*{re.escape(display)}\s*\|\s*\d+\s*\|\s*\d+\s*\|\s*\d+\s*\|"
                self.assertRegex(section, pattern,
                                 f"default-scores row for '{display}' missing or malformed")

    def test_score_values_in_range(self):
        """Default scores are 1-10 per the axis-range table."""
        section = self._atmosphere_section()
        # Pick all rows that look like `| Name | N | N | N |` — three integer cells
        rows = re.findall(r"\|\s*[\w /]+?\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|", section)
        self.assertGreaterEqual(len(rows), 9, "expected at least 9 score rows")
        for row in rows:
            for score in row:
                value = int(score)
                self.assertGreaterEqual(value, 1, f"score {value} below 1")
                self.assertLessEqual(value, 10, f"score {value} above 10")


if __name__ == "__main__":
    unittest.main()
