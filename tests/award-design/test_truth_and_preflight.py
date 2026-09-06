"""award-design external-truth + preflight contracts — the two files the
protocol rebuild added as gates.

external-truth.md keeps heavy layers (GSAP, Three/R3F, Lenis, View Transitions,
Web Audio, modern CSS) off training memory via a three-rung resolution ladder;
preflight.md is the mechanical floor a chunk's Verify ticks box by box. These tests pin
the ladder order, the verified install commands, the stale-signature
tripwires, and the floor's section spine + verdict block."""

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
        rungs = ["**Available capability and installed skill.**", "**Fetch current docs.**", "**Missing prerequisite.**"]
        positions = [self.truth.find(r) for r in rungs]
        self.assertTrue(all(p != -1 for p in positions),
                        "all three ladder rungs must be present")
        self.assertEqual(positions, sorted(positions), "ladder rungs out of order")

    def test_offer_is_once_and_never_stalls(self):
        self.assertIn("Continue unaffected work", self.truth)
        self.assertIn("silence cannot", self.truth)

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

    def test_modern_web_docs_fallback_does_not_resolve_a_package(self):
        self.assertIn("npx skills add https://github.com/GoogleChrome/modern-web-guidance",
                      self.truth)
        self.assertIn("Current MDN and official browser-platform documentation", self.truth)
        self.assertNotIn("npx -y modern-web-guidance@latest", self.truth)

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
        self.assertIn("Harness-native browser", self.truth)
        for candidate in ("Chrome DevTools MCP", "dev-browser", "webwright"):
            with self.subTest(candidate=candidate):
                self.assertIn(candidate, self.truth)
        self.assertIn("missing rendered proof or required measurements limits the verdict", self.truth)
        self.assertIn("one available browser tool does not prove all of them", self.truth)


class TestPreflightGateStructure(unittest.TestCase):
    """The floor's spine: scan first, then tells, locks, countables,
    craft floor, copy floor, assets, driven browser checks, verdict."""

    SECTIONS = [
        "## 1. Mechanical scan",
        "## 2. Tells",
        "## 3. Consistency locks",
        "## 4. Countable",
        "## 5. Craft floor",
        "## 6. Copy floor",
        "## 7. Assets",
        "## 8. Driven in the browser",
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

    def test_binary_no_taste_framing(self):
        head = self.preflight[:800]
        self.assertIn("countable or binary — no taste lives in this file", head)
        self.assertIn("Every box ticks or the build is not done", head)

    def test_tells_section_boxes(self):
        m = re.search(r"## 2\. Tells(.*?)(?=^## )", self.preflight,
                      re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m)
        boxes = re.findall(r"^- \[ \]", m.group(1), re.MULTILINE)
        self.assertGreaterEqual(len(boxes), 12,
                                "the tells section must keep its catalog breadth")

    def test_five_consistency_locks(self):
        m = re.search(r"## 3\. Consistency locks(.*?)(?=^## )", self.preflight,
                      re.DOTALL | re.MULTILINE)
        self.assertIsNotNone(m)
        for lock in ("Theme lock", "Accent lock", "Shape lock",
                     "Emphasis lock", "Register lock"):
            with self.subTest(lock=lock):
                self.assertIn(f"**{lock}**", m.group(1), f"missing lock: {lock}")

    def test_browser_proof_names_the_sweep_widths(self):
        self.assertIn("375px, 768px, 1024px, 1440px, 1920px", self.preflight,
                      "browser proof must pin the payload's verification widths")

    def test_font_resolution_box_in_browser_proof(self):
        self.assertIn("resolves to the committed face", self.preflight,
                      "browser proof must carry the computed-font-resolution box")

    def test_render_floor_sweep_runs_per_chunk(self):
        # the render-floor sweep runs per chunk as it lands, not once at the review
        skill = (REFS.parent / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("after each chunk, inject `assets/render-floor.js`", skill)
        self.assertIn("render-floor.js` through the browser rung (`references/external-truth.md`), sweep 375/768/1024/1440/1920", _read("chunk-template.md"),
                      "every chunk's Verify block carries the sweep")

    def test_measurements_are_mandatory_when_connected(self):
        """'Where the tooling offers' was a latitude hole — a connected harness
        cannot declare a gap it could have closed, and asserted numbers never
        count as measurements."""
        self.assertIn("an asserted number is a fail", self.preflight)
        self.assertIn("declaring a gap the harness could have closed is the same fail",
                      self.preflight)

    def test_verdict_block_fields(self):
        m = re.search(r"## Verdict block(.*)\Z", self.preflight, re.DOTALL)
        self.assertIsNotNone(m)
        verdict = m.group(1)
        for field in ("**Scanner:**", "**Detector:**", "**Open with:**", "**Boxes:**",
                      "**Perf:**", "**Justified overrides:**",
                      "**Tooling gaps:**", "**Status:**"):
            with self.subTest(field=field):
                self.assertIn(field, verdict, f"verdict block missing field: {field}")
        # Three-status model from the enforceability audit: browserless runs cap
        # below READY instead of converting every driven gate into a free pass.
        self.assertIn("READY | REVIEWED-SAME-CONTEXT | NOT DONE", verdict)
        self.assertIn("NOT DONE", verdict)

    def test_no_js_floor_gated(self):
        """A module build opened over file:// runs zero JS — a base-CSS-hidden
        page ships a blackout. The floor box and the JS-disabled loop render
        exist so the artifact the user opens is the artifact that was verified."""
        self.assertIn("**No-JS floor**", self.preflight)
        self.assertIn("static fallback", self.preflight)


if __name__ == "__main__":
    unittest.main()
