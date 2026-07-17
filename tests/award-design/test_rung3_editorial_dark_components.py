"""award-design completeness program — rung 3 (editorial-dark).

The seven interaction components built from the editorial-dark playbook's
`gaps`, pinned by filename ahead of the manifest merge. What the tests lock
is each build's LOAD-BEARING distinction: hover-preview-video surfaces
muted FOOTAGE in one cursor-lerped layer (the video sibling of
index-hover-preview) with the documented tap-to-play-inline-vs-navigate
touch answer and a never-plays reduce; the vertical reel wraps panel
positions modularly so the scroll has no start and no end, and reduce is a
full stand-aside onto the static stacked flow; drag-scrub maps pointer
delta to currentTime with the verified core only (inertia stays opt-in and
header-flagged unverified), suppresses the native drag ghost, declares the
axis-respecting touch-action, and ships the -g 12 baseline encoding recipe;
the cursor verb label hides the native cursor only via a JS-applied class
and gives coarse pointers a persistent hint chip, standing fully aside
under reduce; flicker-reveal randomizes every letter's opacity clock (never
a transform), preserves the accessible name, and never splits under reduce;
the stacked deck peels as a pure function of scroll over a NATIVE sticky
pin (no scroll hijack) with the sub-768 flat stack; and the continuous work
transition names the figure pair around a View Transition with the imposed
short ladder — reduce or no-VT means an instant cut, never a fade-to-ground."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
COMPONENTS = REPO_ROOT / "skills" / "award-design" / "assets" / "components"

# component file → the global its IIFE must export
RUNG3_GLOBALS = {
    "continuous-work-transition.js": "awardContinuousWorkTransition",
    "cursor-verb-label.js": "awardCursorVerbLabel",
    "drag-scrub-video.js": "awardDragScrubVideo",
    "flicker-reveal.js": "awardFlickerReveal",
    "fullscreen-vertical-reel.js": "awardFullscreenVerticalReel",
    "hover-preview-video.js": "awardHoverPreviewVideo",
    "stacked-card-scroll.js": "awardStackedCardScroll",
}


def _src(name):
    return (COMPONENTS / name).read_text(encoding="utf-8")


class TestRung3LibraryContract(unittest.TestCase):
    """The structural contract every library component keeps (the
    test_component_library floor, applied before the manifest merge)."""

    def test_files_exist(self):
        for name in RUNG3_GLOBALS:
            with self.subTest(file=name):
                self.assertTrue((COMPONENTS / name).is_file())

    def test_iife_and_global_export(self):
        for name, g in RUNG3_GLOBALS.items():
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("(function (global)", src)
                self.assertRegex(src, r"global\." + re.escape(g) + r"\s*=")

    def test_exposes_init_and_destroy(self):
        for name in RUNG3_GLOBALS:
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("function init", src)
                self.assertIn("destroy", src)

    def test_has_reduced_motion_path(self):
        for name in RUNG3_GLOBALS:
            with self.subTest(component=name):
                self.assertIn("prefers-reduced-motion", _src(name))

    def test_has_doc_comment_header(self):
        for name in RUNG3_GLOBALS:
            with self.subTest(component=name):
                self.assertTrue(_src(name).lstrip().startswith("/*"))

    def test_namespaced_stylesheet_injection(self):
        """One namespaced stylesheet per component (id='ad-<component>-css')."""
        for name in RUNG3_GLOBALS:
            src = _src(name)
            with self.subTest(component=name):
                self.assertRegex(src, r"CSS_ID = 'ad-[a-z-]+-css'")

    def test_no_bare_100vh(self):
        """svh/dvh only — a bare 100vh jumps under mobile chrome collapse."""
        for name in RUNG3_GLOBALS:
            src = _src(name)
            with self.subTest(component=name):
                self.assertNotRegex(src, r"100vh")


class TestHoverPreviewVideo(unittest.TestCase):
    """Bloom's index reveal: ONE cursor-lerped floating layer that PLAYS the
    work's muted footage, a marquee title gliding over it, the documented
    tap-to-play-inline-vs-navigate touch answer, and a reduce that keeps
    coverage but never plays a frame."""

    def setUp(self):
        self.src = _src("hover-preview-video.js")

    def test_rows_declare_footage_and_poster(self):
        for attr in ("data-ad-hpv-video", "data-ad-hpv-poster", "data-ad-hpv-label"):
            with self.subTest(attr=attr):
                self.assertIn(attr, self.src)

    def test_one_floating_layer_lerped_toward_the_pointer(self):
        self.assertIn("opts.lerp != null ? opts.lerp : 0.14", self.src)
        self.assertIn("cx += (tx - cx) * lerpK;", self.src)

    def test_footage_is_muted_looped_inline(self):
        self.assertIn("video.muted = true;", self.src)
        self.assertIn("video.loop = true;", self.src)
        self.assertIn("setAttribute('playsinline', '')", self.src)

    def test_leave_pauses_the_footage(self):
        self.assertIn("video.pause();", self.src)

    def test_marquee_glides_linear_and_wraps(self):
        """A continuous loop — linear stays legal; two copies wrap at -50%."""
        self.assertIn("@keyframes ad-hpv-glide{to{transform:translate3d(-50%,0,0);}}", self.src)
        self.assertIn("linear infinite", self.src)

    def test_touch_answer_is_tap_to_play_vs_navigate(self):
        """First tap on a resting row plays inline (preventDefault); a tap on
        a playing row falls through to the link."""
        self.assertIn("if (!v || !v.paused) return; // already playing → the tap navigates", self.src)
        self.assertIn("e.preventDefault();", self.src)
        self.assertIn("data-ad-hpv-touch", self.src)

    def test_reduce_never_plays_footage(self):
        """Coverage stays (the layer appears, snapped), playback never starts
        — on either pointer class."""
        self.assertIn("snap — no trailing under reduce", self.src)
        self.assertIn("if (!reduce()) {", self.src)
        self.assertIn("if (reduce()) return; // static poster, no playback — navigate", self.src)

    def test_layer_is_presentation_only(self):
        self.assertIn("float.setAttribute('aria-hidden', 'true');", self.src)
        self.assertIn("pointer-events:none", self.src)

    def test_inline_videos_preload_nothing(self):
        self.assertIn("v.preload = 'none';", self.src)

    def test_no_idle_raf(self):
        self.assertIn(
            "if (on || !settledNow) unit.raf = global.requestAnimationFrame(frame);", self.src
        )


class TestFullscreenVerticalReel(unittest.TestCase):
    """Bisous' home: infinite in BOTH directions via modular wrap, virtual
    offset eased each frame, drag release projected into the same ease, and
    a reduce/no-JS rest state that is a plain stacked page."""

    def setUp(self):
        self.src = _src("fullscreen-vertical-reel.js")

    def test_wrap_is_modular_no_start_no_end(self):
        self.assertIn("function wrap(v, total) { return ((v % total) + total) % total; }", self.src)
        self.assertIn("if (y > total - H) y -= total;", self.src)

    def test_offset_eases_toward_target(self):
        self.assertIn("current += (target - current) * easeK;", self.src)

    def test_offsets_recentered_never_unbounded(self):
        self.assertIn("re-center so offsets never grow unbounded", self.src)

    def test_release_velocity_projects_into_the_same_ease(self):
        """One physics: the throw extends the target; no second momentum loop."""
        self.assertIn("target += vel * flingMs; // the throw rides the same ease — no second physics", self.src)

    def test_rest_state_is_stacked_flow(self):
        self.assertIn("min-height:100svh", self.src)
        self.assertIn("if (reduce()) return { destroy: function () {} };", self.src)

    def test_live_mode_is_js_applied(self):
        """A dead script never strands a 100dvh overflow-hidden shell."""
        self.assertIn("ad-vreel--live", self.src)
        self.assertIn("height:100dvh;overflow:hidden", self.src)

    def test_keyboard_and_focus_reachability(self):
        self.assertIn("'ArrowDown'", self.src)
        self.assertIn("'PageUp'", self.src)
        self.assertIn("function onFocusIn(e)", self.src)
        self.assertIn("nearest wrapped congruent", self.src)

    def test_drag_click_discipline(self):
        """A traveled drag swallows its trailing click; a clean tap stays a tap."""
        self.assertIn("var DRAG_THRESHOLD = 6;", self.src)
        self.assertIn("function onClick(e)", self.src)

    def test_gated_off_screen_and_hidden_tab(self):
        self.assertIn("IntersectionObserver", self.src)
        self.assertIn("visibilitychange", self.src)

    def test_one_panel_cannot_loop(self):
        self.assertIn("if (panels.length < 2) return; // one panel cannot loop", self.src)


class TestDragScrubVideo(unittest.TestCase):
    """KAI's operable field: pointer/touch delta → currentTime, the verified
    core only — inertia opt-in and flagged unverified, drag ghost suppressed,
    touch-action respects the axis, seeks rAF-throttled with the blob
    self-heal, and a keyboard path that never drops a deliberate step."""

    def setUp(self):
        self.src = _src("drag-scrub-video.js")

    def test_whole_section_is_the_field(self):
        self.assertIn("'[data-ad-drag-scrub]'", self.src)
        self.assertIn("data-ad-drag-scrub-axis", self.src)

    def test_encoding_guidance_shipped(self):
        """H.264 baseline + -g 12 + the WebCodecs note — the cross-browser
        scrub recipe rides in the header."""
        self.assertIn("-profile:v baseline -g 12", self.src)
        self.assertIn("mediabunny", self.src)
        self.assertIn("noted, not built", self.src)

    def test_inertia_is_opt_in_and_unverified(self):
        self.assertIn("opt-in only — the winner documents currentTime = sec, no inertia", self.src)
        self.assertIn("opts.momentum != null &&", self.src)

    def test_no_native_drag_ghost(self):
        self.assertIn("function onDragStart(e) { e.preventDefault(); } // no native drag ghost", self.src)
        self.assertIn("-webkit-user-drag:none", self.src)

    def test_touch_action_respects_the_axis(self):
        """axis x keeps the page's vertical pan native; axis y the inverse."""
        self.assertIn("touch-action:pan-y pinch-zoom", self.src)
        self.assertIn('[data-ad-drag-scrub-axis="y"]{touch-action:pan-x pinch-zoom;}', self.src)

    def test_cross_axis_intent_abandons(self):
        self.assertIn("cross-axis intent → the page keeps its native pan, no scrub engages", self.src)

    def test_seek_discipline_is_scrub_films(self):
        self.assertIn("if (video.seeking) return;", self.src)
        self.assertIn("var minStep = Math.max(1 / 30, d / 600);", self.src)

    def test_blob_self_heal_for_rangeless_servers(self):
        self.assertIn("function ensureSeekable(video)", self.src)
        self.assertIn("in-memory blob", self.src)

    def test_keyboard_step_bypasses_the_drag_throttle(self):
        """Driven finding: a discrete arrow step written through apply() is
        swallowed by the mid-seek guard — the step writes currentTime past it."""
        self.assertIn("a deliberate step always lands", self.src)
        self.assertIn("mid-seek/min-step throttle", self.src)

    def test_reduce_holds_the_poster(self):
        self.assertIn("if (reduce()) return; // hold the poster; no seeking, no listeners", self.src)

    def test_never_autoplays(self):
        self.assertIn("video.pause();", self.src)


class TestCursorVerbLabel(unittest.TestCase):
    """The verb teacher: a field-scoped trailing label, native cursor hidden
    only by a JS-applied class, a persistent hint chip on coarse pointers,
    and a full stand-aside under reduce (the onboarding copy alone)."""

    def setUp(self):
        self.src = _src("cursor-verb-label.js")

    def test_fields_declare_their_verb(self):
        self.assertIn("data-ad-cursor-verb", self.src)

    def test_cursor_none_is_js_applied_only(self):
        """A dead script never strands a cursorless surface: cursor:none
        rides a class the JS toggles, never the bare field selector."""
        self.assertIn(".ad-cvl-hide,.ad-cvl-hide *{cursor:none!important;}", self.src)
        self.assertIn("classList.add('ad-cvl-hide')", self.src)
        self.assertNotIn("[data-ad-cursor-verb]{cursor:none", self.src)

    def test_label_is_presentation_only(self):
        self.assertIn("label.setAttribute('aria-hidden', 'true');", self.src)
        self.assertIn("pointer-events:none", self.src)

    def test_label_trails_with_lerp(self):
        self.assertIn("opts.lerp != null ? opts.lerp : 0.22", self.src)
        self.assertIn("cx += (tx - cx) * lerpK;", self.src)

    def test_coarse_gets_the_persistent_hint_chip(self):
        self.assertIn("ad-cvl__hint", self.src)
        self.assertIn("never a dead surface", self.src)

    def test_reduce_is_a_full_stand_aside(self):
        self.assertIn("// Reduced motion: static default cursor + the onboarding copy alone.", self.src)
        self.assertIn("if (reduce()) return { destroy: function () {} };", self.src)

    def test_singleton_like_the_pointer_chrome_class(self):
        self.assertIn("var current = null; // page-level singleton", self.src)

    def test_no_idle_raf(self):
        self.assertIn("if (on || !settled) raf = global.requestAnimationFrame(frame);", self.src)


class TestFlickerReveal(unittest.TestCase):
    """Bisous' text texture: every letter gets its own random opacity clock
    (opacity ONLY — no transform, no charset noise), the accessible name is
    preserved whole, hover replays dip-and-settle, reduce never splits."""

    def setUp(self):
        self.src = _src("flicker-reveal.js")

    def test_randomized_per_letter_clocks(self):
        self.assertIn("var dur = baseMs * (0.6 + Math.random() * 0.8);", self.src)
        self.assertIn("Math.random() * spread", self.src)

    def test_randomized_opacity_dips(self):
        self.assertIn("var hi = 0.55 + Math.random() * 0.45;", self.src)
        self.assertIn("var lo = 0.05 + Math.random() * 0.35;", self.src)

    def test_opacity_only_never_positional(self):
        """The distinction from char-assemble's positional stagger."""
        self.assertNotIn("translate", self.src)
        self.assertNotIn("rotate", self.src)

    def test_accessible_name_preserved(self):
        self.assertIn("aria-label", self.src)
        self.assertIn("reads it intact", self.src)

    def test_spaces_stay_real_text_nodes(self):
        self.assertIn("Real space text node BETWEEN the boxes", self.src)

    def test_js_applied_hidden_state(self):
        """No-JS/dead-script render stays visible."""
        self.assertIn("span.style.opacity = '0';", self.src)

    def test_hover_replay_is_marked_and_guarded(self):
        self.assertIn("data-ad-flicker-hover", self.src)
        self.assertIn("__adFlickBusyUntil", self.src)

    def test_entrance_plays_once_per_element(self):
        self.assertIn("data-ad-revealed", self.src)
        self.assertIn("io.unobserve(e.target);", self.src)

    def test_reduce_never_splits(self):
        self.assertIn("// Under reduce the text is never split — whole, visible, instant.", self.src)

    def test_destroy_restores_the_authored_markup(self):
        self.assertIn("el.innerHTML = el.__adFlickHTML;", self.src)


class TestStackedCardScroll(unittest.TestCase):
    """Bloom's deck: native sticky pin (never a scroll hijack), the peel a
    pure function of scroll position (reversible by construction), the
    sub-768 flat stack, and a reduce that never pins."""

    def setUp(self):
        self.src = _src("stacked-card-scroll.js")

    def test_pin_is_native_sticky(self):
        self.assertIn("position:sticky;top:0;min-height:100svh", self.src)

    def test_peel_reads_the_next_cards_rise(self):
        self.assertIn("var p = 1 - tops[i + 1] / Math.max(1, vh);", self.src)

    def test_compositor_only_transform_and_filter(self):
        self.assertIn("'scale(' + s.toFixed(4) + ')'", self.src)
        self.assertIn("'brightness(' + b.toFixed(3) + ')'", self.src)

    def test_reads_batched_before_writes(self):
        self.assertIn("batch the reads, then the writes", self.src)

    def test_live_mode_is_width_gated(self):
        """The documented mobile answer: a simple stack under 768px."""
        self.assertIn("var LIVE_MQ = '(min-width: 768px)';", self.src)

    def test_rest_state_is_the_flat_list(self):
        self.assertIn("ad-stack--live", self.src)
        self.assertIn("if (reduce()) return { destroy: function () {} };", self.src)

    def test_cards_clip_their_own_content(self):
        self.assertIn("[data-ad-stack-card]{position:relative;overflow:hidden;}", self.src)

    def test_gated_off_screen_and_hidden_tab(self):
        self.assertIn("IntersectionObserver", self.src)
        self.assertIn("visibilitychange", self.src)

    def test_leaving_live_clears_the_peel(self):
        self.assertIn("function clearPeel()", self.src)
        self.assertIn("if (!on) clearPeel();", self.src)


class TestContinuousWorkTransition(unittest.TestCase):
    """Bisous' seam: the figure pair morphs under a cross-dissolve with NO
    cover phase; the imposed ladder is short — reduce or no View Transitions
    means an instant cut, never a fade-to-ground, never a hand-rolled morph."""

    def setUp(self):
        self.src = _src("continuous-work-transition.js")

    def test_names_the_figure_pair_around_the_swap(self):
        self.assertIn("name(figure()); // the outgoing figure, before the browser snapshots", self.src)
        self.assertIn("name(figure()); // the incoming figure the swap produced", self.src)
        self.assertIn("viewTransitionName = NAME;", self.src)

    def test_the_imposed_instant_cut_ladder(self):
        self.assertIn("// The imposed ladder: reduce OR no View Transitions → instant cut.", self.src)
        self.assertIn(
            "if (reduce() || typeof document.startViewTransition !== 'function') {", self.src
        )

    def test_no_cover_phase_by_construction(self):
        """The root pair cross-dissolves on the same clock — no panel, no
        ground fill anywhere in the injected sheet."""
        self.assertIn("no cover phase", self.src)
        self.assertNotIn("--ad-ground", self.src)
        self.assertNotIn("background", self.src)

    def test_signature_tempo_tokens(self):
        self.assertIn("var DUR = 'var(--ad-cwt-dur,900ms)';", self.src)
        self.assertIn("--ad-ease-signature", self.src)

    def test_snapshots_fill_the_morphing_group(self):
        """object-fit:cover on old/new so mid-flight frames never letterbox."""
        self.assertIn("height:100%;width:100%;object-fit:cover;", self.src)

    def test_morphs_the_first_visible_figure(self):
        self.assertIn("if (r.width > 0 && r.height > 0) return els[i]; // the first visible one morphs", self.src)

    def test_imperative_go_with_inflight_guard(self):
        self.assertIn("if (state.playing) return state.playing;", self.src)
        self.assertIn("DEFAULT_TIMEOUT = 2000;", self.src)

    def test_a_skipped_transition_is_not_a_failure(self):
        self.assertIn(".catch(function () {}) // a skipped transition is not a swap failure", self.src)

    def test_names_cleared_after_finish_and_on_destroy(self):
        self.assertIn("function unname()", self.src)
        self.assertIn("skipTransition()", self.src)

    def test_singleton_handle(self):
        self.assertIn("if (instance) return instance.handle;", self.src)


if __name__ == "__main__":
    unittest.main()
