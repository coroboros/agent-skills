"""award-design completeness program — rung 2A (brutalist, first half).

The four interaction components and two section forms built from the
brutalist playbook's `gaps` and the recipes' MISSING refs are pinned here by
filename, not through manifest.json — the orchestrator merges the manifest
side file after the build, and these contracts must hold either way. What the
tests lock is each component's LOAD-BEARING distinction: the chat-cloud
loader types its beats at a flat cadence (the ease:none tell — a typing
curve breaks character), the stepped counter RATCHETS in discrete jumps and
never rolls (the steps(n) tell vs counter-loader's smooth easeOutCubic), the
navbar loader is single-source (the nav element IS the bar, authored visible
so no-JS keeps its nav), the CRT figure is a WebGL dissolve with the spec's
invert fallback and a video floor, the FAQ form rides native details (zero
script needed to disclose) with a motion-free stylesheet, and the lineup
grid locks the 3/4 card frame even under a paired component's clip wrapper."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
COMPONENTS = REPO_ROOT / "skills" / "award-design" / "assets" / "components"
FORMS = COMPONENTS / "forms"

# component file → the global its IIFE must export
RUNG2A_GLOBALS = {
    "chat-cloud-loader.js": "awardChatCloudLoader",
    "stepped-counter-loader.js": "awardSteppedCounterLoader",
    "loader-into-navbar.js": "awardLoaderIntoNavbar",
    "crt-dissolve-figure.js": "awardCrtDissolve",
}
FAQ_CSS = FORMS / "faq-accordion.css"
FAQ_JS = FORMS / "faq-accordion.js"
LINEUP_CSS = FORMS / "lineup-grid.css"


def _src(name):
    return (COMPONENTS / name).read_text(encoding="utf-8")


class TestRung2aLibraryContract(unittest.TestCase):
    """The structural contract every library component keeps (the
    test_component_library floor, applied before the manifest merge)."""

    def test_files_exist(self):
        for name in RUNG2A_GLOBALS:
            with self.subTest(file=name):
                self.assertTrue((COMPONENTS / name).is_file())
        for path in (FAQ_CSS, FAQ_JS, LINEUP_CSS):
            with self.subTest(file=path.name):
                self.assertTrue(path.is_file())

    def test_iife_and_global_export(self):
        for name, g in RUNG2A_GLOBALS.items():
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("(function (global)", src)
                self.assertRegex(src, r"global\." + re.escape(g) + r"\s*=")

    def test_exposes_init_and_destroy(self):
        for name in RUNG2A_GLOBALS:
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("function init", src)
                self.assertIn("destroy", src)

    def test_has_reduced_motion_path(self):
        for name in RUNG2A_GLOBALS:
            with self.subTest(component=name):
                self.assertIn("prefers-reduced-motion", _src(name))

    def test_has_doc_comment_header(self):
        for name in RUNG2A_GLOBALS:
            with self.subTest(component=name):
                self.assertTrue(_src(name).lstrip().startswith("/*"))

    def test_namespaced_stylesheet_injection(self):
        """One namespaced stylesheet per component (id='ad-<component>-css')."""
        for name in RUNG2A_GLOBALS:
            src = _src(name)
            with self.subTest(component=name):
                self.assertRegex(src, r"CSS_ID = 'ad-[a-z-]+-css'")


class TestChatCloudLoader(unittest.TestCase):
    """FlowFest's in-character typed loader: flat-cadence beats, a linear
    stepped count, the 0.3s fade, then the nav drop + card stagger handoff."""

    def setUp(self):
        self.src = _src("chat-cloud-loader.js")

    def test_default_beats_are_the_flowfest_lines(self):
        for beat in ("'...'", "'Hi Friends!'", "'We are back...'"):
            with self.subTest(beat=beat):
                self.assertIn(beat, self.src)
        self.assertIn("heroLine", self.src)

    def test_flat_cadence_never_eased(self):
        """The winner types via TextPlugin all ease:none — chars land on a
        flat clock, no easing function ever shapes the typing."""
        self.assertIn("Math.floor((t - acc) / charMs)", self.src)
        self.assertNotIn("easeOutCubic", self.src)

    def test_exit_fade_is_the_300ms_autoalpha(self):
        self.assertIn("FADE_MS = 300", self.src)

    def test_handoff_nav_drop_and_stagger(self):
        """The winner's beat: nav yPercent −102→0, welcome cards stagger."""
        self.assertIn("translateY(-102%)", self.src)
        self.assertIn("delay: i * 80", self.src)

    def test_gated_splash_law(self):
        """Authored `hidden`, un-hidden by JS — no-JS never blocks the page."""
        self.assertIn("removeAttribute('hidden')", self.src)
        self.assertIn("aria-busy", self.src)

    def test_honest_gate_on_real_load(self):
        self.assertIn("addEventListener('load'", self.src)

    def test_skip_paths_fire_ondone(self):
        self.assertIn("sessionStorage", self.src)
        self.assertIn("if (onDone) onDone();", self.src)

    def test_params_documented_as_illustrative(self):
        """FlowFest's beat params live in unread Slater JS — the header must
        not present them as winner-verified numbers."""
        self.assertIn("illustrative", self.src)


class TestSteppedCounterLoader(unittest.TestCase):
    """The brutalist ratchet: discrete steps(14) jumps (never a smooth roll),
    the clip-path inset wipe, and the optional Flip hand-off."""

    def setUp(self):
        self.src = _src("stepped-counter-loader.js")

    def test_steps_default_fourteen(self):
        self.assertIn("opts.steps != null ? opts.steps : 14", self.src)

    def test_ratchet_is_discrete_never_rolled(self):
        """floor(p * steps) on a flat clock — the jump IS the tell; the
        smooth easeOutCubic roll belongs to counter-loader, not here."""
        self.assertIn("Math.floor(p * steps)", self.src)
        self.assertIn("step === lastStep", self.src)
        self.assertNotIn("easeOutCubic", self.src)

    def test_three_second_beat(self):
        self.assertIn("3000", self.src)

    def test_exit_is_a_clip_path_inset_wipe(self):
        self.assertIn("inset(0 0 0 0)", self.src)
        self.assertIn("inset(0 0 100% 0)", self.src)

    def test_flip_handoff_first_last_invert_play(self):
        """The studio-reel hand-off: the plate FLIPs to the showreel's rect."""
        self.assertIn("flipTo", self.src)
        self.assertIn("getBoundingClientRect", self.src)
        self.assertIn("transformOrigin = 'top left'", self.src)

    def test_gated_splash_and_skip_paths(self):
        self.assertIn("removeAttribute('hidden')", self.src)
        self.assertIn("if (onDone) onDone();", self.src)

    def test_award_status_disclosed(self):
        """Joffrey Spitzer is technique-sourced — the header must say so."""
        self.assertIn("award-unverified", self.src)


class TestLoaderIntoNavbar(unittest.TestCase):
    """Eloy's progress-becomes-UI: one element plays bar and navbar; the nav
    is authored visible so no-JS keeps a nav."""

    def setUp(self):
        self.src = _src("loader-into-navbar.js")

    def test_single_source_bar_is_the_nav(self):
        """The nav rides up to its bottom sliver — bar and navbar are ONE
        element, never a discarded overlay."""
        self.assertIn("data-ad-navload-armed", self.src)
        self.assertIn("translateY(calc(-100% + var(--ad-navload-bar", self.src)

    def test_nav_authored_visible_not_hidden(self):
        """A nav must survive no-JS: the armed state exists only under the
        JS-set attribute — the component never un-hides a `hidden` nav."""
        self.assertNotIn("removeAttribute('hidden')", self.src)

    def test_fill_is_accent_and_transform_only(self):
        self.assertIn("ad-navload__fill", self.src)
        self.assertIn("--ad-accent", self.src)
        self.assertIn("scaleX(", self.src)

    def test_honest_fill_holds_for_real_load(self):
        """Eases toward 90% over the floor, holds until window load."""
        self.assertIn("0.9", self.src)
        self.assertIn("addEventListener('load'", self.src)

    def test_skip_paths_fire_ondone(self):
        self.assertIn("sessionStorage", self.src)
        self.assertIn("if (onDone) onDone();", self.src)

    def test_becomes_navbar_is_flagged_single_source(self):
        self.assertIn("single-source", self.src)


class TestCrtDissolveFigure(unittest.TestCase):
    """Naked City's shader dissolve-to-video: R/G/B split tinted toward the
    accent, a buffered video floor, the spec's invert fallback."""

    def setUp(self):
        self.src = _src("crt-dissolve-figure.js")

    def test_webgl_channel_split_scaled_by_progress(self):
        self.assertIn("u_progress", self.src)
        self.assertIn("off=.035*p", self.src)

    def test_channels_tint_toward_the_accent(self):
        self.assertIn("u_accent", self.src)
        self.assertIn("--ad-accent", self.src)

    def test_video_floor_plays_on_complete_pauses_at_rest(self):
        """The video autoplays only AFTER the transition completes, and the
        reverse pass pauses it — the floor never runs under the still."""
        self.assertIn("if (unit.p >= 1) playFloor()", self.src)
        self.assertIn("if (unit.p <= 0) unit.video.pause()", self.src)

    def test_fallback_is_the_spec_invert_flash(self):
        """No WebGL → filter:invert(100%) kept ≤0.2s, then the video."""
        self.assertIn("ad-crt--fallback", self.src)
        self.assertIn("invert(100%)", self.src)
        self.assertIn("160ms", self.src)

    def test_raf_only_while_the_dissolve_travels(self):
        """No idle loop: the frame re-arms only while q < 1."""
        self.assertIn("if (q < 1) { unit.raf = global.requestAnimationFrame(frame); return; }", self.src)

    def test_reduced_motion_is_a_no_op(self):
        """The still IS the finished state; nothing autoplays under reduce."""
        self.assertIn("if (reduce()) return { destroy: function () {} };", self.src)

    def test_canvas_hygiene(self):
        self.assertIn("aria-hidden", self.src)
        self.assertIn("pointer-events:none", self.src)
        self.assertIn("Math.min(2, global.devicePixelRatio", self.src)
        self.assertIn("WEBGL_lose_context", self.src)

    def test_touch_gets_the_tap_toggle(self):
        self.assertIn("(hover: none)", self.src)

    def test_shader_documented_as_illustrative(self):
        """The winner's uniforms are WebGL-internal — the header must not
        present these numbers as winner-verified."""
        self.assertIn("illustrative", self.src)


class TestFaqAccordionForm(unittest.TestCase):
    """FlowFest's designed rest — native details/summary disclosure under
    the section-form laws (zero decoration, zero motion in the stylesheet)."""

    def setUp(self):
        self.css = FAQ_CSS.read_text(encoding="utf-8")

    def test_root_selector_and_item_slot(self):
        self.assertIn('[data-ad-form="faq-accordion"]', self.css)
        self.assertIn('[data-slot="item"]', self.css)

    def test_rides_native_details_summary(self):
        """Open/close must work with ZERO script — the no-JS render is
        fully operable and rows answer :active on touch by construction."""
        self.assertIn("details", self.css)
        self.assertIn("summary", self.css)

    def test_zero_motion(self):
        self.assertNotIn("@keyframes", self.css)
        self.assertNotRegex(self.css, r"\banimation\s*:")
        self.assertNotRegex(self.css, r"\btransition\s*:")

    def test_marker_is_a_state_swap(self):
        """+/− is disclosure affordance swapped by [open] — never a spin."""
        self.assertIn('content: "+"', self.css)
        self.assertIn('content: "\\2212"', self.css)

    def test_answer_capped_at_the_measure(self):
        self.assertIn("--ad-measure", self.css)

    def test_tokens_read_with_fallbacks(self):
        for token in ("--ad-space", "--ad-ink", "--ad-font-display", "--ad-font-mono"):
            with self.subTest(token=token):
                self.assertIn(token, self.css)

    def test_doc_comment_header(self):
        self.assertTrue(self.css.lstrip().startswith("/*"))

    def test_mobile_breakpoint(self):
        self.assertIn("@media (max-width: 768px)", self.css)


class TestFaqAccordionEnhancer(unittest.TestCase):
    """The optional enhancer: eases the disclosure, stands aside under
    reduce, injects no stylesheet (the form's CSS is linked, not injected)."""

    def setUp(self):
        self.src = FAQ_JS.read_text(encoding="utf-8")

    def test_global_export_and_contract(self):
        self.assertIn("(function (global)", self.src)
        self.assertRegex(self.src, r"global\.awardFaqAccordion\s*=")
        self.assertIn("function init", self.src)
        self.assertIn("destroy", self.src)

    def test_native_path_under_reduce_or_no_waapi(self):
        """No preventDefault when standing aside — native instant disclosure
        is the whole behavior."""
        self.assertIn("if (!answer || !answer.animate || reduce()) return;", self.src)

    def test_padding_rides_the_keyframes(self):
        """border-box floors height at the padding — height alone would stop
        short and snap the close tail (driven-caught defect)."""
        self.assertIn("paddingBottom", self.src)

    def test_close_finishes_before_open_drops(self):
        self.assertIn("closing.onfinish", self.src)
        self.assertIn("item.open = false;", self.src)

    def test_no_stylesheet_injection(self):
        """Layout must survive a dead script — the form CSS is linked."""
        self.assertNotIn("CSS_ID", self.src)


class TestLineupGridForm(unittest.TestCase):
    """FlowFest's proof peak — the index+card hybrid: a headliner card tier
    over divided bill rows, layout-only, 3/4 frames that survive a paired
    component's clip wrapper."""

    def setUp(self):
        self.css = LINEUP_CSS.read_text(encoding="utf-8")

    def test_root_selector_and_slots(self):
        self.assertIn('[data-ad-form="lineup-grid"]', self.css)
        for slot in ("h2", "cards", "rows"):
            with self.subTest(slot=slot):
                self.assertIn(f'[data-slot="{slot}"]', self.css)

    def test_card_and_row_parts(self):
        for part in ("data-card-media", "data-card-name", "data-card-meta",
                     "data-row-name", "data-row-meta"):
            with self.subTest(part=part):
                self.assertIn(f"[{part}]", self.css)

    def test_cards_lock_to_the_frame(self):
        self.assertIn("aspect-ratio: 3 / 4", self.css)
        self.assertIn("overflow: hidden", self.css)

    def test_frame_fill_survives_a_paired_wrapper(self):
        """figure-hover interposes its own clip box inside the media figure;
        the form guarantees the fill generically — without naming any
        component's internal class (driven-caught defect)."""
        self.assertIn(":not(figcaption)", self.css)
        self.assertNotIn(".ad-", self.css)

    def test_zero_motion(self):
        self.assertNotIn("@keyframes", self.css)
        self.assertNotRegex(self.css, r"\banimation\s*:")
        self.assertNotRegex(self.css, r"\btransition\s*:")

    def test_variants(self):
        self.assertIn('[data-cards="2"]', self.css)
        self.assertIn('[data-cards="4"]', self.css)
        self.assertIn('[data-density="airy"]', self.css)
        self.assertIn('[data-density="dense"]', self.css)

    def test_tokens_read_with_fallbacks(self):
        for token in ("--ad-space", "--ad-ink", "--ad-font-display", "--ad-font-mono"):
            with self.subTest(token=token):
                self.assertIn(token, self.css)

    def test_doc_comment_header(self):
        self.assertTrue(self.css.lstrip().startswith("/*"))

    def test_mobile_breakpoint(self):
        self.assertIn("@media (max-width: 768px)", self.css)


if __name__ == "__main__":
    unittest.main()
