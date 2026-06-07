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


class TestImageryProtocol(unittest.TestCase):
    """Imagery is the largest single missing imposition. references/imagery.md
    carries the protocol; two axiomatic rejections wire it into the HARD gate;
    SKILL.md loads it during the build and names it at the gate. The protocol
    reaches for generated / seeded / honest-placeholder assets — never stock."""

    def setUp(self):
        self.imagery = _read(REFS / "imagery.md")
        self.anti = _read(REFS / "anti-patterns.md")
        self.skill = _read(SKILL_MD)

    def test_imagery_reference_covers_protocol(self):
        for marker in ("Zero images is a bug", "No fake-div screenshots",
                       "Real brand logos", "Acquisition priority order"):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.imagery, f"imagery.md missing section: {marker}")

    def test_acquisition_order_is_generate_seed_placeholder(self):
        order = self.imagery.lower()
        gen = order.find("generate it")
        seed = order.find("seed a real source")
        placeholder = order.find("labeled placeholder + tell the user")
        self.assertTrue(
            0 <= gen < seed < placeholder,
            "acquisition order must be generate → seed → labeled placeholder",
        )

    def test_real_logo_sources_and_variants(self):
        self.assertIn("Simple Icons", self.imagery, "logo protocol must name Simple Icons")
        self.assertIn("devicon", self.imagery, "logo protocol must name devicon")
        self.assertIn("light and dark variants", self.imagery.lower(),
                      "logos must ship light + dark variants")

    def test_protocol_never_forces_stock(self):
        self.assertIn("stock photography is not on this list", self.imagery.lower(),
                      "the imagery protocol must explicitly exclude stock photography")

    def test_two_imagery_axioms_route_to_protocol(self):
        m = re.search(r"## Axiomatic rejections(.*?)(?=^## )", self.anti,
                      re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, "Axiomatic rejections section missing")
        axioms = m.group(1)
        self.assertRegex(axioms, r"13\.\s+\*\*Never ship a hero with no real visual",
                         "axiom 13 (hero needs a real visual) missing")
        self.assertRegex(axioms, r"14\.\s+\*\*Never hand-roll fake product screenshots",
                         "axiom 14 (no fake-div screenshots) missing")
        self.assertGreaterEqual(axioms.count("imagery.md"), 2,
                                "both imagery axioms must cite the protocol file")

    def test_hero_visual_axiom_has_typographic_override(self):
        line = next((ln for ln in self.anti.splitlines()
                     if "Never ship a hero with no real visual" in ln), "")
        self.assertTrue(line, "hero-visual axiom missing")
        self.assertIn("typographic", line.lower(),
                      "hero-visual axiom must carry the deliberate-typographic-hero override")

    def test_skill_md_wires_imagery_into_gate(self):
        self.assertIn("references/imagery.md", self.skill,
                      "SKILL.md must reference references/imagery.md")
        m = re.search(r"\*\*HARD gate.*?(?=\*\*SOFT gate)", self.skill, re.DOTALL)
        self.assertIsNotNone(m, "HARD gate block missing from Phase 4")
        self.assertIn("Imagery floor", m.group(0),
                      "the HARD gate must name the imagery floor")


class TestShipReadyFloor(unittest.TestCase):
    """The tiered ship-ready floor (impose / offer / template) consolidates the
    scattered UX-Quality + Accessibility rules into a named floor the gate cites,
    keeps production weight opt-in so it never smothers a small build, and stays
    below the signature moment in prominence."""

    def setUp(self):
        self.floor = _read(REFS / "ship-ready-floor.md")
        self.skill = _read(SKILL_MD)

    def _tier(self, name):
        m = re.search(rf"## {name}(.*?)(?=^## )", self.floor, re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, f"ship-ready-floor.md missing tier: {name}")
        return m.group(1).lower()

    def test_three_tiers_named(self):
        for tier in ("## Impose", "## Offer", "## Template"):
            with self.subTest(tier=tier):
                self.assertIn(tier, self.floor, f"ship-ready-floor.md missing tier: {tier}")

    def test_impose_tier_is_cheap_floor(self):
        impose = self._tier("Impose")
        for item in ("interactive cycles", "focus-visible", "skip-link",
                     "reduced-motion", "theme-color"):
            with self.subTest(item=item):
                self.assertIn(item, impose, f"impose tier must include: {item}")

    def test_offer_tier_is_opt_in_production_weight(self):
        offer = self._tier("Offer")
        for item in ("force-static", "blur", "manifest", "sitemap"):
            with self.subTest(item=item):
                self.assertIn(item, offer, f"offer tier must include: {item}")
        self.assertIn("single-fold", offer,
                      "offer tier must exempt single-fold builds from force-static")

    def test_jsonld_is_template_not_autogenerated(self):
        tmpl = self._tier("Template")
        self.assertIn("json-ld", tmpl, "template tier must carry JSON-LD")
        self.assertIn("never auto-generated", tmpl,
                      "JSON-LD must be a template, never auto-generated with placeholder data")

    def test_floor_wired_into_hard_gate(self):
        m = re.search(r"\*\*HARD gate.*?(?=\*\*SOFT gate)", self.skill, re.DOTALL)
        self.assertIsNotNone(m, "HARD gate block missing")
        self.assertIn("ship-ready-floor.md", m.group(0),
                      "HARD gate must cite the ship-ready floor impose tier")

    def test_offer_tier_surfaced_as_optin_question(self):
        m = re.search(r"^### Phase 4 — Production(.*?)(?=^### Phase|\Z|^##\s)",
                      self.skill, re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, "Phase 4 missing")
        p4 = m.group(1)
        self.assertIn("ship-ready-floor.md", p4,
                      "Phase 4 must reference the ship-ready floor")
        self.assertTrue("opt-in" in p4.lower() and "never auto-build" in p4.lower(),
                        "Phase 4 must surface the production tier as opt-in, never auto-built")

    def test_signature_moment_outranks_floor_in_prominence(self):
        sig = self.skill.lower().find("signature moment")
        floor_ref = self.skill.find("ship-ready-floor.md")
        self.assertNotEqual(sig, -1, "signature moment must appear in SKILL.md")
        self.assertNotEqual(floor_ref, -1, "ship-ready-floor must be referenced in SKILL.md")
        self.assertLess(sig, floor_ref,
                        "the signature moment must precede (outrank) the ship-ready floor")


if __name__ == "__main__":
    unittest.main()
