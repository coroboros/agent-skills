"""award-design's direction-first contract — the ladder and its chunks.

A run ends with DESIGN.md and a design_plan whose `LADDER:` lists build chunks,
each a self-contained prompt from `references/chunk-template.md`; the build is
the chunks, one per executor run, and the review chunk ends it. This module
pins the template's shape, the ladder's order, the step that names them, the
finish that builds nothing, the chunk run's routing surface, and the absence
of the retired component library."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFS = SKILL_DIR / "references"
TEMPLATE = REFS / "chunk-template.md"
TESTS_DIR = Path(__file__).resolve().parent

CHUNK_BLOCKS = ["**Read first**", "**Implement**", "**Verify**", "**Out of scope**", "**Report**"]
LADDER_ORDER = ["1. **shell**", "2. **hero**", "3. **sections**", "4. **award surfaces**",
                "5. **pages**", "6. **review**"]
# Library residue: a path, a token prefix, a form attribute, the manifest, the
# tier-2 index heading. Each literal is split so this file clears the grep it enforces.
LIBRARY_RESIDUE = ["assets/" "components", "--ad" "-", "data-ad" "-", "manifest" ".json",
                   "Component " "index"]
# Every id the library's manifest declared at the deletion commit. Bare here, so the
# backtick scan below never matches this file; a backticked id in prose points at a
# module that no longer exists.
RETIRED_IDS = tuple("""
    about-overlay-footer accent-link ambient-idle ambient-orb-field bare-cue border-glow-bloom
    brand-object-assembly-loader branded-preloader card-list chapter-cover chapter-select
    char-assemble chat-cloud-loader clip-reveal close-panel conic-border-shine
    contextual-cursor-label continuous-idle-carry continuous-work-transition corner-counter-boot
    counter-loader counter-odometer crt-dissolve-figure cursor-proximity-typefield
    cursor-spawn-trail cursor-verb-label curtain-transition custom-contextual-cursor
    diegetic-nav divided-capability-strip dolly-zoom drag-scrub-video editorial-split
    faq-accordion feature-card-grid figure-hover fill-invert-cta flicker-reveal
    flip-handoff-loader focus-defocus footer-clone-machine full-bleed-figure
    full-page-scrub-recolor-carry fullscreen-vertical-reel gated-splash glass-card glitch-type
    grain-grade hard-press-button hero-masthead horizontal-scroll-chain hover-preview-video
    identity-terminal-hero idle-attract-auto-demo image-curtain in-3d-dom-input-bridge
    in-engine-hero in-engine-hud-fold in-engine-intro in-scene-ambient-life index-hover-preview
    index-list index-reel-header index-row-hover infinite-scroll-loop journey-touch-momentum
    kinetic-reveal kinetic-splittext-maximal line-draw-cta lineup-grid liquid-glass-refraction
    live-demo-tile living-presence-layer loader-into-navbar logo-wall magnetic-cursor
    marquee-hero masked-label-swap minimal-cursor-signature morph-tile-grid name-card
    narrative-scene-one-loader nav-context-ink nav-hero-surface organic-section-edge
    oversized-wordmark page-transition-choreography perpetual-tile-machines physics-tumble-field
    pinned-demo-panels pinned-filmstrip pinned-media-stepthrough place-tour pointer-parallax
    pointer-scene-reveal press-hold-reveal procession-wayfinding raycast-object-state
    rooms-procession route-transition-overlay route-view-transition-carrier
    scored-scene-procession scramble-decode scroll-camera-dive scroll-speed-oscillator
    scroll-velocity-scene-distortion scrub-film scrub-parallax-bed scrubbed-decor-draw
    scrubbed-inverse-scale-figure sdf-scramble-substrate section-accent-rotation
    section-scale-momentum semantic-accent shader-surface show-on-scroll-up-nav smooth-scroll
    sound-channel spatial-audio-world specimen-grid split-rollover spotlight-expand-tile
    stacked-card-scroll stat-band stepped-counter-loader svg-path-fill-loader swipe-snap-gallery
    telemetry-readout text-emphasis-fill tilt-parity-figure type-as-image
    type-forward-intro-loader type-index-grid type-tester valediction-footer
    velocity-flowmap-hover vf-scroll-morph world-boot
""".split())


def _body():
    return SKILL_MD.read_text(encoding="utf-8")


def _section(name):
    m = re.search(rf"^## {re.escape(name)}\b(.*?)(?=^##\s)", _body(), re.DOTALL | re.MULTILINE)
    assert m is not None, f"## {name} section missing"
    return m.group(1)


def _step(n):
    """One numbered step of the path — each is a single line."""
    m = re.search(rf"(?m)^{n}\. \*\*.*$", _body())
    assert m is not None, f"path step {n} missing"
    return m.group(0)


def _load_map():
    m = re.search(r"^## The load map — .*?\n(.*?)(?=^## )", _body(), re.DOTALL | re.MULTILINE)
    assert m is not None, "## The load map section missing"
    return m.group(1)


def _frontmatter(key):
    m = re.search(rf"(?m)^{key}:\s*(.+)$", _body())
    assert m is not None, f"{key} frontmatter field missing"
    return m.group(1)


class TestChunkTemplate(unittest.TestCase):
    """The template is the executor's whole brief: five blocks in a fixed
    order, and a ladder order the director fills top to bottom."""

    def setUp(self):
        self.assertTrue(TEMPLATE.is_file(), "references/chunk-template.md missing")
        self.template = TEMPLATE.read_text(encoding="utf-8")

    def test_five_blocks_in_order(self):
        positions = [self.template.find(block) for block in CHUNK_BLOCKS]
        for block, pos in zip(CHUNK_BLOCKS, positions):
            with self.subTest(block=block):
                self.assertNotEqual(pos, -1, f"chunk block missing: {block}")
        self.assertEqual(positions, sorted(positions), "chunk blocks out of the contracted order")

    def test_six_step_ladder_order(self):
        positions = [self.template.find(step) for step in LADDER_ORDER]
        for step, pos in zip(LADDER_ORDER, positions):
            with self.subTest(step=step):
                self.assertNotEqual(pos, -1, f"ladder step missing: {step}")
        self.assertEqual(positions, sorted(positions), "ladder steps out of the contracted order")


class TestLadderInThePath(unittest.TestCase):
    """Step 8 writes the ladder from the template; step 9 ends the run with
    nothing built — the chunks build, one per executor run."""

    def test_step_eight_names_the_template_and_the_ladder(self):
        step = _step(8)
        self.assertIn("**The ladder.**", step)
        self.assertIn("`LADDER:`", step)
        self.assertIn("references/chunk-template.md", step)
        self.assertIn("`references/chunk-template.md`", _load_map(),
                      "the template load is priced like every other reference")

    def test_step_nine_builds_nothing(self):
        step = _step(9)
        self.assertIn("**Finish.**", step)
        self.assertIn("builds nothing", step)
        self.assertIn("one per executor run", step)


class TestChunkRunSurface(unittest.TestCase):
    """A chunk reaches the skill by id or by paste; Routing and the
    argument hint both carry it."""

    def test_routing_carries_the_chunk_run(self):
        routing = _section("Routing")
        self.assertIn("award-design chunk <id>", routing)
        self.assertIn("**chunk run**", routing)

    def test_argument_hint_carries_the_chunk_form(self):
        self.assertIn("[chunk <id>]", _frontmatter("argument-hint"))


class TestLibraryRetired(unittest.TestCase):
    """The component library is gone: no directory, and no line in the skill
    or its tests still points at it."""

    def test_no_components_directory(self):
        self.assertFalse((SKILL_DIR / "assets" / "components").exists())

    def test_no_residue_in_skill_or_tests(self):
        residue = [pattern.encode() for pattern in LIBRARY_RESIDUE]
        for root in (SKILL_DIR, TESTS_DIR):
            for path in root.rglob("*"):
                if not path.is_file() or "__pycache__" in path.parts:
                    continue
                content = path.read_bytes()
                rel = str(path.relative_to(REPO_ROOT))
                for pattern in residue:
                    with self.subTest(file=rel, pattern=pattern.decode()):
                        self.assertNotIn(pattern, content)

    def test_no_backticked_retired_id(self):
        """Prose names the mechanic; a backticked id claims a module to fetch."""
        for root, glob in ((SKILL_DIR, "*.md"), (TESTS_DIR, "*.py")):
            for path in root.rglob(glob):
                if "__pycache__" in path.parts:
                    continue
                content = path.read_text(encoding="utf-8")
                hits = [stem for stem in RETIRED_IDS if f"`{stem}`" in content]
                with self.subTest(file=str(path.relative_to(REPO_ROOT))):
                    self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
