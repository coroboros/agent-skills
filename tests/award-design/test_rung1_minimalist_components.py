"""award-design completeness program — rung 1 (minimalist) library components.

The five interaction components and one section form built from the
minimalist playbook's `gaps` (winner-cited build orders) are pinned here by
filename, not through manifest.json — the orchestrator merges the manifest
side file after the build, and these contracts must hold either way. What the
tests lock is each component's LOAD-BEARING distinction: the inverse-scale
figure is positional (re-fires, never a fire-once latch), the route carrier
prefers native View Transitions, the type intro is the stylistic Gabriel
sequence (not the honest load-gated roll), the cursor is monochrome by law
(no accent read), the recolor carry is a GLOBAL page-progress driver with a
legible dim floor, and the name-card form ships zero decoration and zero
motion."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
COMPONENTS = REPO_ROOT / "skills" / "award-design" / "assets" / "components"
FORMS = COMPONENTS / "forms"

# component file → the global its IIFE must export
RUNG1_GLOBALS = {
    "scrubbed-inverse-scale-figure.js": "awardInverseScaleFigure",
    "route-view-transition-carrier.js": "awardRouteCarrier",
    "type-forward-intro-loader.js": "awardTypeIntroLoader",
    "minimal-cursor-signature.js": "awardMinimalCursor",
    "full-page-scrub-recolor-carry.js": "awardPageRecolor",
}
NAME_CARD = FORMS / "name-card.css"


def _src(name):
    return (COMPONENTS / name).read_text(encoding="utf-8")


class TestRung1LibraryContract(unittest.TestCase):
    """The structural contract every library component keeps (the
    test_component_library floor, applied before the manifest merge)."""

    def test_files_exist(self):
        for name in RUNG1_GLOBALS:
            with self.subTest(file=name):
                self.assertTrue((COMPONENTS / name).is_file())
        self.assertTrue(NAME_CARD.is_file())

    def test_iife_and_global_export(self):
        for name, g in RUNG1_GLOBALS.items():
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("(function (global)", src)
                self.assertRegex(src, r"global\." + re.escape(g) + r"\s*=")

    def test_exposes_init_and_destroy(self):
        for name in RUNG1_GLOBALS:
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("function init", src)
                self.assertIn("destroy", src)

    def test_has_reduced_motion_path(self):
        for name in RUNG1_GLOBALS:
            with self.subTest(component=name):
                self.assertIn("prefers-reduced-motion", _src(name))

    def test_has_doc_comment_header(self):
        for name in RUNG1_GLOBALS:
            with self.subTest(component=name):
                self.assertTrue(_src(name).lstrip().startswith("/*"))

    def test_namespaced_stylesheet_injection(self):
        """One namespaced stylesheet per component (id='ad-<component>-css')."""
        for name in RUNG1_GLOBALS:
            src = _src(name)
            with self.subTest(component=name):
                self.assertRegex(src, r"CSS_ID = 'ad-[a-z-]+-css'")


class TestInverseScaleFigure(unittest.TestCase):
    """The continuation carry: clip opens WHILE the media scales inversely,
    welded to scroll position — never a fire-once entrance."""

    def setUp(self):
        self.src = _src("scrubbed-inverse-scale-figure.js")

    def test_clip_and_inverse_scale(self):
        self.assertIn("inset(", self.src)
        self.assertIn("scale(", self.src)
        # inverse: the closed state carries the EXTRA scale, open settles to 1
        self.assertIn("(1 - q)", self.src)

    def test_positional_never_latched(self):
        """clip-reveal latches with data-ad-revealed + unobserve-on-play; the
        carry must re-fire every pass — no latch, a live positional driver."""
        self.assertNotIn("data-ad-revealed", self.src)
        self.assertNotIn("unobserve", self.src)
        self.assertIn("getBoundingClientRect", self.src)
        self.assertIn("requestAnimationFrame", self.src)

    def test_clip_rides_an_inner_box_not_the_observed_wrapper(self):
        """A clip-path on the IntersectionObserver target zeroes its
        intersection rect (the clip-reveal lesson)."""
        self.assertIn("ad-invfig__box", self.src)
        self.assertIn("IntersectionObserver", self.src)

    def test_amplitude_documented_as_illustrative(self):
        """The Codrops source verifies the mechanic, not the numbers — the
        header must not present 0.2 as winner-verified."""
        self.assertIn("illustrative", self.src)
        self.assertIn("--ad-inverse-amp", self.src)


class TestRouteCarrier(unittest.TestCase):
    """The cross-navigation momentum carrier: native View Transitions first,
    WAAPI crossfade fallback, imperative go(fn) around the swap."""

    def setUp(self):
        self.src = _src("route-view-transition-carrier.js")

    def test_native_view_transitions_path(self):
        self.assertIn("startViewTransition", self.src)
        self.assertIn("::view-transition-old(root)", self.src)

    def test_waapi_crossfade_fallback(self):
        self.assertIn(".animate(", self.src)
        self.assertIn("opacity", self.src)

    def test_stefan_register_defaults(self):
        """Stefan's Codrops-verified crossfade — .5s easeQuadInOut — is the
        token default."""
        self.assertIn("--ad-route-dur", self.src)
        self.assertIn("500", self.src)
        self.assertIn("cubic-bezier(.45,0,.55,1)", self.src)

    def test_hung_swap_never_strands_the_view(self):
        self.assertIn("timeout", self.src)
        self.assertIn("DEFAULT_TIMEOUT", self.src)


class TestTypeIntroLoader(unittest.TestCase):
    """Gabriel's stylistic sequence: linear 1→100 (2.8s), slow-in fade, then
    the scramble-decode handoff — decoupled from real asset load by design."""

    def setUp(self):
        self.src = _src("type-forward-intro-loader.js")

    def test_gabriel_numbers(self):
        self.assertIn("2800", self.src)                      # the 2.8s count
        self.assertIn("[1200, 1500, 400, 200, 1000, 600, 600]", self.src)
        self.assertIn("1 + p * 99", self.src)                # values 1..100

    def test_fade_rides_the_reveal_token(self):
        self.assertIn("--ad-dur-reveal", self.src)

    def test_gated_splash_law(self):
        """Authored `hidden`, un-hidden by JS — no-JS never blocks the page."""
        self.assertIn("removeAttribute('hidden')", self.src)
        self.assertIn("aria-busy", self.src)

    def test_skip_paths_fire_ondone(self):
        """reduced-motion and sessionOnce skip the roll but never the handoff
        callback — the first beat must not depend on the roll having played."""
        self.assertIn("sessionStorage", self.src)
        self.assertIn("if (onDone) onDone();", self.src)

    def test_decode_pins_accessible_name(self):
        self.assertIn("aria-label", self.src)


class TestMinimalCursor(unittest.TestCase):
    """The quiet cursor slot: monochrome by law, fine-pointer only, never a
    gate on content or a11y."""

    def setUp(self):
        self.src = _src("minimal-cursor-signature.js")

    def test_monochrome_law(self):
        """No color spectacle — the component reads --ad-ink and NEVER the
        accent; an accent read here would break the archetype."""
        self.assertIn("--ad-ink", self.src)
        self.assertNotIn("--ad-accent", self.src)

    def test_fine_pointer_gate_and_dormant_touch(self):
        self.assertIn("(pointer: fine)", self.src)

    def test_never_gates_content(self):
        self.assertIn("pointer-events:none", self.src)
        self.assertIn("aria-hidden", self.src)

    def test_both_modes(self):
        self.assertIn("'trail'", self.src)
        self.assertIn("'dot'", self.src)

    def test_native_cursor_kept_in_trail_mode(self):
        """cursor:none rides a class applied in dot mode only — the trail is
        décor behind the native cursor."""
        self.assertIn("cursor:none", self.src)
        self.assertIn("mode === 'dot'", self.src)


class TestPageRecolorCarry(unittest.TestCase):
    """The substrate carry: one GLOBAL page-progress driver over a
    document-ordered per-char sequence, reversible, legible at the floor."""

    def setUp(self):
        self.src = _src("full-page-scrub-recolor-carry.js")

    def test_global_page_progress_driver(self):
        """The distinction from text-emphasis-fill: scrollY over the whole
        document, not the block's own viewport traversal."""
        self.assertIn("scrollY", self.src)
        self.assertIn("scrollHeight", self.src)

    def test_per_char_granularity(self):
        self.assertIn("ad-recolor__c", self.src)
        self.assertIn("charAt", self.src)

    def test_legible_dim_floor(self):
        self.assertIn("0.45", self.src)
        self.assertIn("--ad-recolor-floor", self.src)

    def test_reversible_never_latched(self):
        self.assertNotIn("unobserve", self.src)
        # delta writes walk both directions
        self.assertIn("Math.min(lit, next)", self.src)

    def test_no_js_render_is_bright(self):
        """The dim state exists only under the JS-set armed attribute."""
        self.assertIn("data-ad-recolor-armed", self.src)


class TestNameCardForm(unittest.TestCase):
    """The gallery-stack opening slot — a layout-only form under the
    section-form laws (zero decoration, zero motion, no hidden slots)."""

    def setUp(self):
        self.css = NAME_CARD.read_text(encoding="utf-8")

    def test_root_selector_and_slots(self):
        self.assertIn('[data-ad-form="name-card"]', self.css)
        for slot in ("h1", "role", "meta", "cue"):
            with self.subTest(slot=slot):
                self.assertIn(f'[data-slot="{slot}"]', self.css)

    def test_zero_motion(self):
        self.assertNotIn("@keyframes", self.css)
        self.assertNotRegex(self.css, r"\banimation\s*:")
        self.assertNotRegex(self.css, r"\btransition\s*:")

    def test_no_hidden_slots(self):
        self.assertNotRegex(self.css, r"visibility:\s*hidden")
        self.assertNotRegex(self.css, r"opacity:\s*0(?![.\d])")
        self.assertNotRegex(self.css, r"display:\s*none")

    def test_tokens_read_with_fallbacks(self):
        for token in ("--ad-space", "--ad-measure", "--ad-ink",
                      "--ad-font-display", "--ad-font-mono"):
            with self.subTest(token=token):
                self.assertIn(token, self.css)

    def test_doc_comment_header(self):
        self.assertTrue(self.css.lstrip().startswith("/*"))

    def test_mobile_breakpoint(self):
        self.assertIn("@media (max-width: 768px)", self.css)


if __name__ == "__main__":
    unittest.main()
