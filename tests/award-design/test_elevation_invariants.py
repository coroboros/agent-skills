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
    """The harvest added falsifiable named traps the catalog lacked, and the
    protocol rebuild moved the countable table to its single home — the Phase 5
    gate (preflight.md §4). Each check keeps a brief-tied override (or a
    declared archetype scope) so it raises the floor without manufacturing a
    new monoculture; anti-patterns.md keeps the rationale and a pointer."""

    def setUp(self):
        self.anti = _read(REFS / "anti-patterns.md")
        self.preflight = _read(REFS / "preflight.md")

    def _countable_table(self):
        m = re.search(r"## 4\. Countable boxes(.*?)(?=^## )", self.preflight,
                      re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, "preflight.md §4 Countable boxes missing")
        return m.group(1)

    def test_anti_patterns_points_to_the_moved_table(self):
        m = re.search(r"## Countable checks(.*?)(?=^## )", self.anti,
                      re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, "anti-patterns.md Countable checks pointer missing")
        self.assertIn("preflight.md", m.group(1),
                      "the catalog must route to preflight.md — one home, no drift")

    def test_harvested_countable_checks_present(self):
        table = self._countable_table()
        for check in ("Hero-stack cap", "CTA-intent consistency", "Zigzag cap",
                      "Marquee cap", "Layout-family variety"):
            with self.subTest(check=check):
                self.assertIn(f"**{check}**", table,
                              f"countable check missing: {check}")

    def test_checks_declare_scope(self):
        """Every countable check declares Global vs archetype-conditional —
        the scope column is the override mechanism for the gate."""
        for check in ("Hero-stack cap", "CTA-intent consistency", "Zigzag cap",
                      "Marquee cap", "Layout-family variety", "Em-dash density"):
            row = next((ln for ln in self.preflight.splitlines()
                        if f"**{check}**" in ln), "")
            with self.subTest(check=check):
                self.assertTrue(row, f"row missing for {check}")
                self.assertTrue(
                    "Global" in row or "Archetype-conditional" in row,
                    f"{check} must declare a scope",
                )

    def test_layout_family_exempts_single_fold(self):
        """Layout-family variety must not fire on single-fold portfolios / docs —
        that exemption is what keeps it from smothering minimal builds."""
        row = next((ln for ln in self.preflight.splitlines()
                    if "Layout-family variety" in ln), "")
        self.assertIn("single-fold", row.lower(),
                      "layout-family check must exempt single-fold portfolios / docs")

    def test_countable_only_checks_carry_inline_override(self):
        """The global-scope caps with no archetype exception must still offer a
        brief-tied path (an 'Override:' clause or an explicit 'is fine' allowance)
        so no ban is a dead end."""
        for check in ("Hero-stack cap", "CTA-intent consistency", "Zigzag cap"):
            row = next((ln for ln in self.preflight.splitlines()
                        if f"**{check}**" in ln), "")
            with self.subTest(check=check):
                self.assertTrue(
                    "Override" in row or "is fine" in row,
                    f"{check} must carry an override / allowance clause",
                )

    def test_imported_production_checks_present(self):
        """The taste-skill/hallmark import round added rules the catalog lacked;
        each must land as a countable box so the gate can count it."""
        table = self._countable_table()
        for check in ("Hero top padding", "Nav discipline", "CTA wrap",
                      "Quote length", "Middle-dot rationing", "Split-header",
                      "Long-list component", "Italic descenders"):
            with self.subTest(check=check):
                self.assertIn(f"**{check}**", table,
                              f"imported countable check missing: {check}")

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
    carries the protocol; two axiomatic rejections wire it into the anti-slop
    catalog the review mode runs; the build loads the protocol and imposes a real
    visual ambiently. The protocol reaches for generated / seeded /
    honest-placeholder assets — never stock."""

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

    def test_skill_md_wires_imagery_into_the_protocol(self):
        """The protocol front-loads assets: Phase 3 loads the imagery protocol
        and secures assets before the build; the pre-flight gate carries the
        hero-real-visual box so a placeholder hero cannot ship."""
        m = re.search(r"^## Phase 3 — .*?\n(.*?)(?=^## )", self.skill,
                      re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, "## Phase 3 section missing")
        phase3 = m.group(1)
        self.assertIn("references/imagery.md", phase3,
                      "Phase 3 must load the imagery acquisition protocol")
        self.assertIn("asset list", phase3.lower(),
                      "Phase 3's artifact must include the asset list")
        preflight = _read(REFS / "preflight.md")
        self.assertIn("Hero carries a real visual", preflight,
                      "the pre-flight gate must carry the hero-real-visual box")


class TestShipReadyFloor(unittest.TestCase):
    """The tiered ship-ready floor (impose / offer / template) consolidates the
    scattered UX-Quality + Accessibility rules into a named floor the build's
    Ship-ready block cites, keeps production weight opt-in so it never smothers a
    small build, and stays below the signature moment in prominence."""

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

    def _phase(self, n):
        m = re.search(rf"^## Phase {n} — .*?\n(.*?)(?=^## )", self.skill,
                      re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m, f"## Phase {n} section missing")
        return m.group(1)

    def test_impose_tier_auto_authored_in_build(self):
        """The protocol splits the floor: Impose is auto-authored while building
        (Phase 4)."""
        phase4 = self._phase(4)
        self.assertIn("ship-ready-floor.md", phase4,
                      "Phase 4 must cite the ship-ready floor's Impose tier")
        self.assertIn("auto-authored as you build", phase4.lower(),
                      "the Impose tier must be auto-authored during the build")
        self.assertIn("8-state contract", phase4,
                      "the 8-state interactive contract rides the Impose tier")

    def test_offer_tier_is_per_brief_never_auto_built(self):
        """…and Offer is surfaced per brief at ship time (Phase 6)."""
        phase6 = self._phase(6).lower()
        self.assertIn("offer production plumbing", phase6,
                      "the Offer tier must be surfaced as production plumbing")
        self.assertIn("never auto-built", phase6,
                      "the Offer tier must never be auto-built")
        self.assertIn("single-fold build needs none", phase6,
                      "the Offer tier must exempt a single-fold build")

    def test_signature_moment_outranks_floor_in_prominence(self):
        sig = self.skill.lower().find("signature moment")
        floor_ref = self.skill.find("ship-ready-floor.md")
        self.assertNotEqual(sig, -1, "signature moment must appear in SKILL.md")
        self.assertNotEqual(floor_ref, -1, "ship-ready-floor must be referenced in SKILL.md")
        self.assertLess(sig, floor_ref,
                        "the signature moment must precede (outrank) the ship-ready floor")


class TestMotionVocabulary(unittest.TestCase):
    """The harvest consolidated the missing scroll skeletons and the signature
    easing lexicon into foundations.md Animation Toolkit, plus a GSAP
    reduced-motion gate, and added a brief signal → dial inference table to
    atmosphere-calibration.md. Posture stays CSS-native-first with no mandated
    runtime dependency or npx author-time step."""

    def setUp(self):
        self.foundations = _read(REFS / "foundations.md")
        self.calibration = _read(REFS / "atmosphere-calibration.md")

    def test_sticky_stack_skeleton_present(self):
        self.assertIn("Sticky-stack", self.foundations, "sticky-stack skeleton missing")
        # pinSpacing:false is the defining detail — and is new to this file.
        self.assertIn("pinSpacing: false", self.foundations,
                      "sticky-stack must set pinSpacing: false")

    def test_horizontal_pan_skeleton_present(self):
        self.assertIn("Horizontal-pan", self.foundations, "horizontal-pan skeleton missing")
        self.assertRegex(self.foundations, r"ease:\s*'none'",
                         "horizontal-pan must use ease: 'none' (1:1 with scroll)")

    def test_signature_easing_lexicon_present(self):
        for ease in ("back.out(1.7)", "elastic.out(1, 0.3)", "CustomEase"):
            with self.subTest(ease=ease):
                self.assertIn(ease, self.foundations, f"easing lexicon missing: {ease}")
        # CSS linear() physics-easing strings (distinct from linear-gradient).
        self.assertIn("--ease-spring:", self.foundations,
                      "CSS linear() physics-easing strings must be present")

    def test_gsap_reduced_motion_gate_present(self):
        self.assertIn("gsap.matchMedia()", self.foundations,
                      "GSAP reduced-motion gate (matchMedia) must be present")
        self.assertIn("prefers-reduced-motion: reduce", self.foundations)

    def test_no_npx_author_time_dependency(self):
        self.assertNotIn("npx ", self.foundations,
                         "motion vocabulary must not introduce an npx author-time step")

    def test_signal_to_dial_inference_table(self):
        self.assertIn("Signal → dial inference", self.calibration,
                      "atmosphere-calibration.md must carry the signal → dial inference table")
        cal = self.calibration.lower()
        self.assertIn("dashboard-like", cal, "inference table must map a representative signal")
        # Contradictions surface, never average — the behavior rule the table must honor.
        self.assertIn("never average", cal,
                      "conflicting signals must surface as a contradiction, not be averaged")


class TestArchetypeGateCompliance(unittest.TestCase):
    """An archetype file that prescribes a value the skill's own gate FAILs is
    a self-contradiction — a build following it can never ship. Pure #FFFFFF
    prescriptions and un-alpha'd bg-white samples were the field-found class;
    this pins the whole class shut."""

    ARCHETYPE_FILES = [
        "minimalist.md", "brutalist.md", "editorial.md", "bold-maximal.md",
        "immersive-cinematic.md", "experimental.md", "corporate-luxury.md",
        "bento-card.md", "spatial-organic.md", "premium-patterns.md",
    ]

    def test_no_pure_white_prescriptions(self):
        for name in self.ARCHETYPE_FILES:
            body = _read(REFS / name)
            with self.subTest(file=name):
                self.assertNotIn("#FFFFFF", body,
                                 f"{name} prescribes pure #FFFFFF — axiom 3 fails it")
                self.assertIsNone(
                    re.search(r"\bbg-white\b(?!/)", body),
                    f"{name} ships an un-alpha'd bg-white sample — the scanner fails it")

    def test_no_pure_black_prescriptions(self):
        for name in self.ARCHETYPE_FILES:
            body = _read(REFS / name)
            with self.subTest(file=name):
                self.assertIsNone(
                    re.search(r"`#000000`|`#000`(?!/)", body),
                    f"{name} prescribes pure #000 — axiom 3 fails it")


class TestOpticalCraft(unittest.TestCase):
    """references/optical-craft.md is the last-10% layer — type optics, spatial
    optics, interaction personality, and the quiet layer. Model defaults are
    geometrically correct and optically wrong; losing a section here reopens
    the exact ceiling the file exists to break."""

    def setUp(self):
        self.craft = _read(REFS / "optical-craft.md")

    def test_four_sections_present(self):
        for section in ("## Type optics", "## Spatial optics",
                        "## Interaction personality", "## The quiet layer"):
            with self.subTest(section=section):
                self.assertIn(section, self.craft)

    def test_tracking_is_a_curve_with_values(self):
        self.assertIn("Tracking is a curve, not a value", self.craft)
        self.assertIn("-0.03em", self.craft, "display tracking values must be concrete")
        self.assertIn("+0.05em", self.craft, "uppercase tracking values must be concrete")

    def test_text_wrap_polish_present(self):
        self.assertIn("text-wrap: balance", self.craft)
        self.assertIn("text-wrap: pretty", self.craft)
        self.assertIn("tabular-nums", self.craft)

    def test_interaction_personality_covers_all_nine_archetypes(self):
        m = re.search(r"## Interaction personality(.*?)(?=^## )", self.craft,
                      re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m)
        table = m.group(1)
        for archetype in ("Minimalist", "Brutalist", "Editorial", "Bold / Maximal",
                          "Immersive / Cinematic", "Experimental", "Corporate Luxury",
                          "Bento / Card", "Spatial Organic"):
            with self.subTest(archetype=archetype):
                self.assertIn(f"| {archetype} |", table,
                              f"personality row missing for {archetype}")

    def test_quiet_layer_demands_two(self):
        self.assertIn("pick ≥2", self.craft)
        for detail in ("::selection", "favicon", "<title>"):
            with self.subTest(detail=detail):
                self.assertIn(detail, self.craft)


class TestInspirationSet(unittest.TestCase):
    """references/inspiration.md curates cross-archetype galleries and the motion
    canon as URLs (never a vendored corpus), and frames component kits as
    scaffold-only. anti-patterns.md carries the component-kit-sameness tell with
    a restyle override that routes to it — the inspiration set's reachable path
    after the lean rebuild dropped the SKILL.md body pointer."""

    def setUp(self):
        self.insp = _read(REFS / "inspiration.md")
        self.anti = _read(REFS / "anti-patterns.md")

    def test_galleries_and_motion_canon_present(self):
        for src in ("Awwwards", "Godly", "SiteInspire", "Codrops"):
            with self.subTest(src=src):
                self.assertIn(src, self.insp, f"gallery missing: {src}")
        for lib in ("GSAP", "Lenis", "Motion"):
            with self.subTest(lib=lib):
                self.assertIn(lib, self.insp, f"motion-canon entry missing: {lib}")

    def test_component_kits_marked_scaffold_only(self):
        for kit in ("Aceternity", "Magic UI"):
            with self.subTest(kit=kit):
                self.assertIn(kit, self.insp, f"component kit missing: {kit}")
        self.assertIn("scaffold", self.insp.lower(),
                      "component kits must be framed as scaffold-only")
        self.assertIn("restyle", self.insp.lower(),
                      "the override must be to restyle past kit defaults")

    def test_no_vendored_corpus_only_urls(self):
        # No snapshotted corpus: a code fence would signal vendored source.
        self.assertNotIn("```", self.insp,
                         "inspiration.md must cite URLs, not vendor code / corpus")

    def test_component_kit_sameness_tell_with_override(self):
        line = next((ln for ln in self.anti.splitlines()
                     if "component-kit sameness" in ln.lower()
                     or "component-kit-sameness" in ln.lower()), "")
        self.assertTrue(line, "component-kit-sameness tell missing from anti-patterns.md")
        self.assertIn("Override", line, "the component-kit-sameness tell must carry an override")

    def test_inspiration_reachable_from_kit_override(self):
        """The lean rebuild dropped the SKILL.md body pointer; the inspiration set
        must stay reachable from the component-kit-sameness override, or its
        curation orphans."""
        line = next((ln for ln in self.anti.splitlines()
                     if "component-kit sameness" in ln.lower()
                     or "component-kit-sameness" in ln.lower()), "")
        self.assertIn("inspiration.md", line,
                      "the component-kit override must route to inspiration.md so the set stays reachable")


if __name__ == "__main__":
    unittest.main()
