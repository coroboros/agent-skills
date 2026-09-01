"""frontend-dev — the everyday-lane contract documented in SKILL.md must remain stable."""

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "skills" / "brand-voice" / "scripts"))

from utils import parse_yaml_minimal, split_frontmatter  # noqa: E402

SKILL_MD = REPO_ROOT / "skills" / "frontend-dev" / "SKILL.md"
AWARD_SKILL_MD = REPO_ROOT / "skills" / "award-design" / "SKILL.md"
DESIGN_SYSTEM_MD = REPO_ROOT / "skills" / "design-system" / "SKILL.md"
SCAFFOLD_MD = REPO_ROOT / "skills" / "scaffold" / "SKILL.md"
CHUNK_TEMPLATE_MD = REPO_ROOT / "skills" / "award-design" / "references" / "chunk-template.md"


def _frontmatter():
    text = SKILL_MD.read_text(encoding="utf-8")
    fm_text, _ = split_frontmatter(text)
    return parse_yaml_minimal(fm_text) if fm_text else {}


def _body():
    return SKILL_MD.read_text(encoding="utf-8")


def _section(heading):
    """Return the body of the `## <heading>` section (to the next `## ` or EOF)."""
    m = re.search(
        rf"(?m)^## {re.escape(heading)}.*?\n(.*?)(?=^## |\Z)",
        _body(),
        re.DOTALL,
    )
    return m.group(1) if m else None


class TestFrontmatterTier(unittest.TestCase):
    """frontend-dev ships portable: no compatibility string, no paths globs
    (paths would double-fire with design-system on the same UI files), no
    pinned model."""

    def test_no_compatibility_field(self):
        self.assertIsNone(_frontmatter().get("compatibility"))

    def test_no_paths_field(self):
        self.assertNotRegex(_body(), r"(?m)^paths:",
                            "paths: globs would double-fire with design-system")

    def test_model_unset_inherits_session(self):
        self.assertIsNone(_frontmatter().get("model"))


class TestBriefTiers(unittest.TestCase):
    """The brief tiers compose: a chunk ask decides the work, DESIGN.md
    decides the tokens, and the ritual fires only when neither exists.
    A DESIGN.md-first precedence would make the chunk tier unreachable
    (every ladder chunk lives in a project that already has a DESIGN.md)."""

    def _tiers(self):
        section = _section("The brief — three tiers")
        self.assertIsNotNone(section, "brief-tiers section missing")
        return section

    def test_tier_order(self):
        tiers = self._tiers()
        chunk = tiers.find("A ladder chunk")
        design = tiers.find("`DESIGN.md` at the project root")
        ritual = tiers.find("No chunk, no")
        self.assertTrue(0 <= chunk < design < ritual,
                        f"tiers out of order: {chunk}, {design}, {ritual}")

    def test_chunk_defers_to_award_design_when_installed(self):
        self.assertIn("hand the chunk to its chunk mode", self._tiers())

    def test_chunk_verify_runs_verbatim_with_declared_gaps(self):
        tiers = self._tiers()
        self.assertIn("run its Verify verbatim", tiers)
        self.assertIn("declared gap", tiers)

    def test_token_changes_route_to_design_system(self):
        self.assertIn("/design-system", self._tiers())


class TestCommitRitual(unittest.TestCase):
    """Five named lines, in order, committed to the response AND the first
    file's top comment — the anti-reflex mechanism the lane is built on."""

    RITUAL_LINES = ["SURFACE:", "WORLD:", "TYPE:", "COLOR:", "SIGNATURE:"]

    def _ritual(self):
        section = _section("The commit ritual — five lines before any code")
        self.assertIsNotNone(section, "commit-ritual section missing")
        return section

    def test_five_lines_in_order(self):
        ritual = self._ritual()
        positions = [ritual.find(line) for line in self.RITUAL_LINES]
        for line, pos in zip(self.RITUAL_LINES, positions):
            self.assertNotEqual(pos, -1, f"ritual line missing: {line}")
        self.assertEqual(positions, sorted(positions),
                         "ritual lines out of order")

    def test_lines_land_in_a_file_comment(self):
        self.assertIn("comment at the top of the first file", self._ritual())

    def test_first_instinct_named_and_rejected(self):
        self.assertIn("first instinct is already spent", self._ritual())

    def test_edit_inherits_neighboring_direction(self):
        self.assertIn("inherits the neighboring direction", self._ritual())


class TestSurfaceArchetypes(unittest.TestCase):
    """Seven surfaces decide composition; Monitor explicitly bans the hero."""

    SURFACES = ["Persuade", "Monitor", "Decide", "Create", "Browse", "Read", "Enter"]

    def _table(self):
        section = _section("Surface archetypes")
        self.assertIsNotNone(section, "surface-archetypes section missing")
        return section

    def test_all_seven_surfaces_present(self):
        table = self._table()
        for surface in self.SURFACES:
            with self.subTest(surface=surface):
                self.assertRegex(table, rf"(?m)^\| {surface} \|")

    def test_monitor_bans_hero(self):
        monitor_row = re.search(r"(?m)^\| Monitor \|.*$", self._table())
        self.assertIsNotNone(monitor_row)
        self.assertIn("no hero", monitor_row.group(0))


class TestFingerprintBan(unittest.TestCase):
    """The ten tells are the lane's match-and-refuse list — dropping one
    reopens the door to the reflex page."""

    TELLS = [
        "purple-to-blue gradient",
        "Inter, Roboto, Arial",
        "Three equal cards",
        "Eyebrow labels",
        "Center-stacked",
        "nested inside cards",
        "Glassmorphism",
        "Invented round stats",
        "Em-dash chains",
        "icon perched above",
    ]

    def test_ten_tells_pinned(self):
        section = _section("The fingerprint — match and refuse")
        self.assertIsNotNone(section, "fingerprint section missing")
        for tell in self.TELLS:
            with self.subTest(tell=tell):
                self.assertIn(tell, section)


class TestStatesAndShip(unittest.TestCase):
    """Five interactive states + three data states + the ship checklist."""

    def _section(self):
        section = _section("States and the ship checklist")
        self.assertIsNotNone(section, "states section missing")
        return section

    def test_interactive_and_data_states(self):
        section = self._section()
        for state in ["default", "hover", "focus-visible", "disabled",
                      "loading", "empty", "error"]:
            with self.subTest(state=state):
                self.assertIn(state, section)

    def test_ship_checklist_items(self):
        section = self._section()
        for item in ["verify widths", "favicon", "404", "alt text",
                     "skip link", "console errors", "signature moment"]:
            with self.subTest(item=item):
                self.assertIn(item, section)


class TestLandingConversion(unittest.TestCase):
    """The Persuade lane adds the three conversion lines and the
    objections/risk-reversal structure."""

    def _section(self):
        section = _section("Landing pages — the Persuade lane")
        self.assertIsNotNone(section, "landing section missing")
        return section

    def test_conversion_lines_in_order(self):
        section = self._section()
        positions = [section.find(line) for line in ("OFFER:", "AUDIENCE:", "ACTION:")]
        self.assertNotIn(-1, positions, "conversion line missing")
        self.assertEqual(positions, sorted(positions))

    def test_objections_and_risk_reversal(self):
        section = self._section()
        self.assertIn("objections", section.lower())
        self.assertIn("risk reversal", section.lower())


class TestRoutingOut(unittest.TestCase):
    def _routing(self):
        section = _section("Routing out")
        self.assertIsNotNone(section, "routing section missing")
        return section

    def test_ceiling_routes_to_award_design(self):
        routing = self._routing()
        self.assertIn("/award-design", routing)
        for word in ["award-winning", "premium", "signature"]:
            with self.subTest(word=word):
                self.assertIn(word, routing)

    def test_single_token_routes_to_design_system(self):
        routing = self._routing()
        self.assertIn("/design-system", routing)
        self.assertRegex(routing.lower(), r"single[- ]token")

    def test_empty_dir_routes_to_scaffold(self):
        self.assertIn("/scaffold", self._routing())

    def test_backend_passes_through(self):
        self.assertIn("backend", self._routing().lower())


class TestSiblingRouting(unittest.TestCase):
    """The lane split is bidirectional: award-design, design-system, and
    scaffold each point everyday work at /frontend-dev. A one-sided split
    regresses to the old orphaned lane."""

    def test_award_design_when_to_use_names_frontend_dev(self):
        text = AWARD_SKILL_MD.read_text(encoding="utf-8")
        m = re.search(r"(?m)^when_to_use:\s*(.+)$", text)
        self.assertIsNotNone(m)
        self.assertIn("/frontend-dev", m.group(1))

    def test_award_design_no_longer_claims_any_frontend(self):
        text = AWARD_SKILL_MD.read_text(encoding="utf-8")
        self.assertNotIn("any frontend design", text,
                         "award-design still claims the everyday lane")
        self.assertNotIn("make it look great", text)

    def test_award_design_routing_line(self):
        text = AWARD_SKILL_MD.read_text(encoding="utf-8")
        m = re.search(r"(?m)^## Routing.*?\n(.*?)(?=^## )", text, re.DOTALL)
        self.assertIsNotNone(m)
        self.assertIn("/frontend-dev", m.group(1))

    def test_design_system_step_aside_names_frontend_dev(self):
        self.assertIn("everyday UI work belongs to `/frontend-dev`",
                      DESIGN_SYSTEM_MD.read_text(encoding="utf-8"))

    def test_scaffold_handoff_names_frontend_dev(self):
        self.assertIn("`/frontend-dev` (everyday UI)",
                      SCAFFOLD_MD.read_text(encoding="utf-8"))


class TestVerifyFreshPixels(unittest.TestCase):
    def test_screenshot_widths(self):
        section = _section("Verify — fresh pixels")
        self.assertIsNotNone(section, "verify section missing")
        self.assertIn("375, 768, and 1440", section)


class TestChunkContractParity(unittest.TestCase):
    """Tier 1 quotes the chunk section names by value; the source of truth
    is award-design's chunk template. If a heading is renamed there,
    frontend-dev silently stops recognising chunks — this must fail first."""

    NAMES = ["Read first", "Implement", "Verify", "Out of scope", "Report"]

    def test_tier_quotes_the_template_headings(self):
        tier = _section("The brief — three tiers")
        self.assertIsNotNone(tier, "tiers section missing")
        self.assertIn(" / ".join(self.NAMES), tier)
        template = CHUNK_TEMPLATE_MD.read_text(encoding="utf-8")
        for name in self.NAMES:
            with self.subTest(name=name):
                self.assertIn(f"**{name}**", template)


if __name__ == "__main__":
    unittest.main()
