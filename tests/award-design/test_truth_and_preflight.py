"""award-design external-truth + preflight contracts — the two files the
protocol rebuild added as gates.

external-truth.md keeps heavy layers (GSAP, Three/R3F, Lenis, View Transitions,
Web Audio, modern CSS) off training memory via a three-rung resolution ladder;
preflight.md is the single ship gate Phase 5 runs box by box. These tests pin
the ladder order, the verified install commands, the stale-signature
tripwires, and the gate's section spine + verdict block."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REFS = REPO_ROOT / "skills" / "award-design" / "references"


def _read(name):
    return (REFS / name).read_text(encoding="utf-8")


class TestExternalTruthLadder(unittest.TestCase):
    """The ladder is walked in order and never stalls the build — reordering
    or softening a rung reopens the write-from-memory hole."""

    def setUp(self):
        self.truth = _read("external-truth.md")

    def test_three_rungs_in_order(self):
        rungs = ["**Installed skill.**", "**Offer the install.**", "**Fetch current docs.**"]
        positions = [self.truth.find(r) for r in rungs]
        self.assertTrue(all(p != -1 for p in positions),
                        "all three ladder rungs must be present")
        self.assertEqual(positions, sorted(positions), "ladder rungs out of order")

    def test_offer_is_once_and_never_stalls(self):
        self.assertIn("once", self.truth)
        self.assertIn("Never stall the build", self.truth)

    def test_docs_rung_requires_citation(self):
        self.assertIn("Cite what was actually read", self.truth,
                      "the docs rung must require citing what was read")

    def test_undeclared_source_fails_preflight(self):
        self.assertIn("pre-flight fails any heavy layer without a declared source",
                      self.truth)

    def test_ingredients_are_floor_not_substitute(self):
        self.assertIn("never replace current docs for API signatures", self.truth,
                      "bundled cheats must not substitute for current docs")


class TestCapabilityMap(unittest.TestCase):
    """Capability rows carry verified install commands and official docs —
    an invented command here breaks the user-facing offer."""

    def setUp(self):
        self.truth = _read("external-truth.md")

    def test_gsap_row_carries_verified_install(self):
        self.assertIn("npx skills add https://github.com/greensock/gsap-skills",
                      self.truth)

    def test_modern_web_guidance_row_with_skill_less_fallback(self):
        self.assertIn("npx skills add https://github.com/GoogleChrome/modern-web-guidance",
                      self.truth)
        self.assertIn("npx -y modern-web-guidance@latest search", self.truth,
                      "the docs fallback must work without the skill installed")

    def test_gate_is_proportional_to_usage(self):
        self.assertIn("static minimalist page loads none of this", self.truth,
                      "the gate must scale to what the build actually uses")

    def test_stale_signature_tripwires_present(self):
        for tripwire in ("motion/react", "@tailwindcss/postcss",
                         "gsap.registerPlugin(ScrollTrigger)"):
            with self.subTest(tripwire=tripwire):
                self.assertIn(tripwire, self.truth,
                              f"stale-signature tripwire missing: {tripwire}")

    def test_browser_verification_is_a_gated_capability(self):
        """Rendering proof resolves like a heavy layer: MCP → dev-browser →
        webwright → install offer; only a declined offer degrades."""
        self.assertIn("## Browser verification", self.truth)
        self.assertIn("npm install -g dev-browser && dev-browser install", self.truth)
        for candidate in ("Chrome DevTools MCP", "dev-browser", "webwright"):
            with self.subTest(candidate=candidate):
                self.assertIn(candidate, self.truth)
        self.assertIn("*declined* offer", self.truth,
                      "only a declined install offer may degrade the gate")


class TestPreflightGateStructure(unittest.TestCase):
    """The gate's spine: scan first, then axiomatic boxes, locks, countables,
    craft floor, copy audit, truth & assets, browser proof, verdict."""

    SECTIONS = [
        "## 1. Mechanical scan",
        "## 2. Axiomatic boxes",
        "## 3. Consistency locks",
        "## 4. Countable boxes",
        "## 5. Craft floor",
        "## 6. Copy audit",
        "## 7. Truth & assets",
        "## 8. Browser proof",
        "## Verdict block",
    ]

    def setUp(self):
        self.preflight = _read("preflight.md")

    def test_sections_present_and_ordered(self):
        positions = [self.preflight.find(s) for s in self.SECTIONS]
        for section, pos in zip(self.SECTIONS, positions):
            with self.subTest(section=section):
                self.assertNotEqual(pos, -1, f"preflight section missing: {section}")
        self.assertEqual(positions, sorted(positions),
                         "preflight sections out of the contracted order")

    def test_binary_no_compression_framing(self):
        head = self.preflight[:800]
        self.assertIn("every box ticks or the build is not done", head)
        self.assertIn("No sampling, no compression", head)

    def test_fourteen_axiomatic_boxes(self):
        m = re.search(r"## 2\. Axiomatic boxes(.*?)(?=^## )", self.preflight,
                      re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m)
        boxes = re.findall(r"^- \[ \]", m.group(1), re.MULTILINE)
        self.assertEqual(len(boxes), 14,
                         "the axiomatic boxes must mirror the catalog's 14 rejections")

    def test_five_consistency_locks(self):
        m = re.search(r"## 3\. Consistency locks(.*?)(?=^## )", self.preflight,
                      re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m)
        for lock in ("Theme lock", "Accent lock", "Shape lock",
                     "Emphasis lock", "Register lock"):
            with self.subTest(lock=lock):
                self.assertIn(f"**{lock}**", m.group(1), f"missing lock: {lock}")

    def test_browser_proof_names_the_three_widths(self):
        self.assertIn("375px, 768px, 1440px", self.preflight,
                      "browser proof must pin the three verification widths")

    def test_font_resolution_box_in_browser_proof(self):
        self.assertIn("resolves to the committed face", self.preflight,
                      "browser proof must carry the computed-font-resolution box")

    def test_conformance_loop_box_in_browser_proof(self):
        self.assertIn("conformance loop exited clean", self.preflight.lower())
        self.assertIn("5-loop cap", self.preflight)

    def test_mcp_measurements_are_mandatory_when_connected(self):
        """'Where the tooling offers' was a latitude hole — a connected MCP
        makes the trace mandatory; a miss is a finding, not a gap."""
        self.assertIn("performance trace is mandatory", self.preflight)
        self.assertIn("a miss is a finding, not a gap", self.preflight)

    def test_pacing_and_quiet_layer_boxes(self):
        for box in ("**Pacing curve**", "**Quiet layer**"):
            with self.subTest(box=box):
                self.assertIn(box, self.preflight, f"countable box missing: {box}")
        self.assertIn("optical-craft.md", self.preflight,
                      "the quiet-layer box must route to the optical-craft menu")

    def test_verdict_block_fields(self):
        m = re.search(r"## Verdict block(.*)\Z", self.preflight, re.DOTALL)
        self.assertIsNotNone(m)
        verdict = m.group(1)
        for field in ("**Scanner:**", "**Detector:**", "**Open with:**", "**Boxes:**",
                      "**Counts:**", "**Ledger:**", "**Justified overrides:**",
                      "**Suppressions:**", "**Tooling gaps:**", "**Status:**"):
            with self.subTest(field=field):
                self.assertIn(field, verdict, f"verdict block missing field: {field}")
        # Three-status model from the enforceability audit: browserless runs cap
        # below READY instead of converting every driven gate into a free pass.
        self.assertIn("READY | READY-UNVERIFIED", verdict)
        self.assertIn("NOT DONE", verdict)

    def test_no_js_floor_gated(self):
        """A module build opened over file:// runs zero JS — a base-CSS-hidden
        page ships a blackout. The floor box and the JS-disabled loop render
        exist so the artifact the user opens is the artifact that was verified."""
        self.assertIn("**No-JS floor**", self.preflight)
        self.assertIn("static fallback", self.preflight)

    def test_rotation_stamp_box_matches_phase_4_format(self):
        self.assertIn("/* award-design ·", self.preflight,
                      "the stamp box must carry the Phase 4 stamp format")


if __name__ == "__main__":
    unittest.main()
