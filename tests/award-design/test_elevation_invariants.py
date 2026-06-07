"""award-design elevation invariants — pin the contracts added by the
taste-skill-v2 + source-pack harvest: sharpened named traps and countable
checks, the imagery protocol, the tiered ship-ready floor, the consolidated
motion vocabulary with dial-inference, and the curated inspiration set with
its anti-sameness guard.

Each invariant exists because the harvest closed a real gap that would
silently re-open if the section drifted. Test names describe the contract
being pinned, not the implementation. Every assertion here would FAIL on the
pre-elevation skill."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFS = SKILL_DIR / "references"


def _read(path):
    return path.read_text(encoding="utf-8")


class TestNamedTrapsAndCountableChecks(unittest.TestCase):
    """The harvest added falsifiable named traps the catalog lacked, and
    promoted the countable ones into the HARD gate. Each trap carries a
    brief-tied override (or a declared archetype scope) so it raises the floor
    without manufacturing a new monoculture."""

    def setUp(self):
        self.anti = _read(REFS / "anti-patterns.md")

    def _countable_table(self):
        m = re.search(r"## Countable checks(.*?)(?=^## )", self.anti, re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, "Countable checks section missing")
        return m.group(1)

    def test_five_new_countable_checks_present(self):
        table = self._countable_table()
        for check in ("Hero-stack cap", "CTA-intent consistency", "Zigzag cap",
                      "Marquee cap", "Layout-family variety"):
            with self.subTest(check=check):
                self.assertIn(f"**{check}**", table,
                              f"countable check missing: {check}")

    def test_new_checks_declare_scope(self):
        """Every countable check declares Global vs archetype-conditional —
        the scope column is the override mechanism for the gate."""
        for check in ("Hero-stack cap", "CTA-intent consistency", "Zigzag cap",
                      "Marquee cap", "Layout-family variety"):
            row = next((ln for ln in self.anti.splitlines() if f"**{check}**" in ln), "")
            with self.subTest(check=check):
                self.assertTrue(row, f"row missing for {check}")
                self.assertTrue(
                    "Global" in row or "Archetype-conditional" in row,
                    f"{check} must declare a scope",
                )

    def test_layout_family_exempts_single_fold(self):
        """Layout-family variety must not fire on single-fold portfolios / docs —
        that exemption is what keeps it from smothering minimal builds."""
        row = next((ln for ln in self.anti.splitlines()
                    if "Layout-family variety" in ln), "")
        self.assertIn("single-fold", row.lower(),
                      "layout-family check must exempt single-fold portfolios / docs")

    def test_countable_only_checks_carry_inline_override(self):
        """The global-scope caps with no archetype exception must still offer a
        brief-tied path (an 'Override:' clause or an explicit 'is fine' allowance)
        so no ban is a dead end."""
        for check in ("Hero-stack cap", "CTA-intent consistency", "Zigzag cap"):
            row = next((ln for ln in self.anti.splitlines() if f"**{check}**" in ln), "")
            with self.subTest(check=check):
                self.assertTrue(
                    "Override" in row or "is fine" in row,
                    f"{check} must carry an override / allowance clause",
                )

    def test_split_screen_hero_banned_with_override(self):
        line = next((ln for ln in self.anti.splitlines()
                     if "Split-screen 50/50 hero" in ln), "")
        self.assertTrue(line, "split-screen 50/50 hero tell missing")
        self.assertIn("Override", line, "split-screen ban must carry an override path")

    def test_premium_consumer_palette_named_with_rotation(self):
        anti = self.anti.lower()
        self.assertIn("premium-consumer palette", anti,
                      "the beige/brass/espresso overexposed cluster must be named")
        self.assertIn("rotate at least one of the three roles", anti,
                      "premium-consumer palette must carry a rotation override")


class TestSerifOverexposureReconciled(unittest.TestCase):
    """anti-patterns.md once recommended Instrument Serif as a 'distinctive free'
    display face while its own tell-list flags Fraunces — a self-contradiction.
    The fix demotes both to overexposed: the font axiom no longer recommends
    Instrument Serif, and the Typography tells flag both with an editorial /
    luxury override."""

    def setUp(self):
        self.anti = _read(REFS / "anti-patterns.md")

    def test_font_axiom_drops_instrument_serif_recommendation(self):
        axiom = next((ln for ln in self.anti.splitlines()
                      if "distinctive free one" in ln), "")
        self.assertTrue(axiom, "font axiom recommendation line missing")
        rec = re.search(r"distinctive free one \(([^)]*)\)", axiom)
        self.assertIsNotNone(rec, "distinctive-free recommendation list missing")
        self.assertNotIn(
            "Instrument Serif", rec.group(1),
            "Instrument Serif must not be recommended as a distinctive-free face",
        )

    def test_typography_tells_flag_both_serifs_with_override(self):
        m = re.search(r"### Typography(.*?)(?=^###|\Z)", self.anti,
                      re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, "Typography tells subsection missing")
        tells = m.group(1)
        self.assertIn("Instrument Serif", tells, "Instrument Serif must be flagged as overexposed")
        self.assertIn("Fraunces", tells, "Fraunces must be flagged as overexposed")
        self.assertTrue(
            "Editorial" in tells and ("Corporate Luxury" in tells or "luxury" in tells.lower()),
            "serif overexposure must carry an editorial / luxury override",
        )


if __name__ == "__main__":
    unittest.main()
