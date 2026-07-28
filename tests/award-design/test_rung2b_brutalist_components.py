"""award-design completeness program — rung 2B (brutalist, second half).

The four interaction components and one section form built from the
brutalist playbook's `gaps`, plus the one authorized EDIT (smooth-scroll
anchor routing), pinned by filename ahead of the manifest merge. What the
tests lock is each build's LOAD-BEARING distinction: the idle carry couples
marquee speed AND skew to scroll velocity through the verified /-300 divisor
and eases back to zero at rest (never a fixed px/s unless asked), the clone
machine ships the Codrops-verified exit to the number (0.2s, scale 0.6,
back.in(1.7), stagger 0.4 random, 200-copy cap) and clips its own storm, the
terminal hero form is the corner-tag frame with structurally NO CTA slot and
its enhancer types over ONLY the char-diff span on a flat clock, the index
preview is ONE cursor-lerped floating layer with the documented centered-row
fallback under coarse pointers, the décor draw welds all three channels
(draw scrub:0, pluck scrub:8 bounce random, shear -300 powers) to scroll
POSITION so every pass re-fires, and the smooth-scroll rig now owns the two
travels builds kept re-inventing — anchors and wordmark-home ride
lenis.scrollTo and neither ever writes a #fragment into the URL."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
COMPONENTS = REPO_ROOT / "skills" / "award-design" / "assets" / "components"
FORMS = COMPONENTS / "forms"

# component file → the global its IIFE must export
RUNG2B_GLOBALS = {
    "continuous-idle-carry.js": "awardContinuousIdleCarry",
    "footer-clone-machine.js": "awardFooterCloneMachine",
    "index-hover-preview.js": "awardIndexHoverPreview",
    "scrubbed-decor-draw.js": "awardScrubbedDecorDraw",
}
HERO_CSS = FORMS / "identity-terminal-hero.css"
HERO_JS = FORMS / "identity-terminal-hero.js"
SMOOTH = COMPONENTS / "smooth-scroll.js"


def _src(name):
    return (COMPONENTS / name).read_text(encoding="utf-8")


class TestRung2bLibraryContract(unittest.TestCase):
    """The structural contract every library component keeps (the
    test_component_library floor, applied before the manifest merge)."""

    def test_files_exist(self):
        for name in RUNG2B_GLOBALS:
            with self.subTest(file=name):
                self.assertTrue((COMPONENTS / name).is_file())
        for path in (HERO_CSS, HERO_JS):
            with self.subTest(file=path.name):
                self.assertTrue(path.is_file())

    def test_iife_and_global_export(self):
        for name, g in RUNG2B_GLOBALS.items():
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("(function (global)", src)
                self.assertRegex(src, r"global\." + re.escape(g) + r"\s*=")

    def test_exposes_init_and_destroy(self):
        for name in RUNG2B_GLOBALS:
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("function init", src)
                self.assertIn("destroy", src)

    def test_has_reduced_motion_path(self):
        for name in RUNG2B_GLOBALS:
            with self.subTest(component=name):
                self.assertIn("prefers-reduced-motion", _src(name))

    def test_has_doc_comment_header(self):
        for name in RUNG2B_GLOBALS:
            with self.subTest(component=name):
                self.assertTrue(_src(name).lstrip().startswith("/*"))

    def test_namespaced_stylesheet_injection(self):
        """One namespaced stylesheet per component (id='ad-<component>-css')."""
        for name in RUNG2B_GLOBALS:
            src = _src(name)
            with self.subTest(component=name):
                self.assertRegex(src, r"CSS_ID = 'ad-[a-z-]+-css'")


class TestContinuousIdleCarry(unittest.TestCase):
    """The never-silent carry: velocity-coupled marquee (the Osmo variant),
    one cursor-lerped in-character idle with a touch bob, the restraint
    drift — one shared rAF, IO/visibility-gated, per-brief amplitude."""

    def setUp(self):
        self.src = _src("continuous-idle-carry.js")

    def test_three_channels_are_markup_opt_in(self):
        for attr in ("data-ad-carry-marquee", "data-ad-carry-idle", "data-ad-carry-drift"):
            with self.subTest(channel=attr):
                self.assertIn(attr, self.src)

    def test_skew_is_the_verified_osmo_divisor(self):
        """skew target = velocity / -300, clamped — the documented winner
        variant, never an invented curve."""
        self.assertIn("var SKEW_DIVISOR = -300;", self.src)
        self.assertIn("vel / SKEW_DIVISOR", self.src)

    def test_skew_and_speed_ease_back_at_rest(self):
        self.assertIn("// ease back to 0", self.src)
        self.assertIn("var multTarget = 1 + Math.min(Math.abs(vel) / 600, 3);", self.src)

    def test_constant_band_is_the_opt_in_fallback(self):
        """Velocity coupling is the default; ='constant' is the tamer
        fixed-px/s band, never the other way around."""
        self.assertIn("=== 'constant'", self.src)

    def test_marquee_wraps_modularly(self):
        self.assertIn("if (u.x <= -u.copyW) u.x += u.copyW;", self.src)

    def test_idle_is_cursor_lerped_with_touch_bob(self):
        """Fine pointers lean toward the cursor (the quickTo pattern);
        touch falls back to the time-driven bob — never a dead element."""
        self.assertIn("'(hover: hover) and (pointer: fine)'", self.src)
        self.assertIn("time-driven idle bob", self.src)

    def test_gated_off_screen_and_hidden_tab(self):
        self.assertIn("IntersectionObserver", self.src)
        self.assertIn("visibilitychange", self.src)

    def test_wcag_pause_hook(self):
        """An idle channel past five seconds carries the pause/stop path —
        the handle exposes it for the build's control."""
        self.assertIn("2.2.2", self.src)
        self.assertIn("pause: function ()", self.src)

    def test_reduce_is_a_no_op(self):
        self.assertIn(
            "if (reduce()) return { destroy: function () {}, "
            "pause: function () {}, resume: function () {} };",
            self.src,
        )

    def test_destroy_unwraps_the_marquee(self):
        self.assertIn("u.el.insertBefore(first.firstChild, u.track)", self.src)


class TestFooterCloneMachine(unittest.TestCase):
    """Eloy's deferred peak, Codrops-verified to the number: up to 200
    difference-blended clones on mousemove, the 0.2s back.in(1.7) staggered
    exit, fine-pointer only, the field clipping its own storm."""

    def setUp(self):
        self.src = _src("footer-clone-machine.js")

    def test_the_verified_numbers(self):
        self.assertIn("opts.max != null ? opts.max : 200", self.src)
        self.assertIn("opts.step != null ? opts.step : 200", self.src)
        self.assertIn("var EXIT_MS = 200;", self.src)
        self.assertIn("var EXIT_STAGGER_MS = 400;", self.src)

    def test_exit_ease_is_back_in(self):
        """back.in(1.7) — the overshoot pull-in, as cubic-bezier."""
        self.assertIn("cubic-bezier(0.36, 0, 0.66, -0.56)", self.src)
        self.assertIn("back.in(1.7)", self.src)
        self.assertIn("scale(0.6)", self.src)

    def test_stagger_is_random(self):
        self.assertIn("delay: Math.random() * EXIT_STAGGER_MS", self.src)

    def test_interference_is_difference_blend(self):
        self.assertIn("mix-blend-mode:difference", self.src)

    def test_field_clips_its_own_storm(self):
        """Clones never bleed across the section boundary (the clip-layers
        law) — the field owns position:relative + overflow:hidden."""
        self.assertIn(".ad-clonem{position:relative;overflow:hidden;}", self.src)

    def test_fine_pointer_only_touch_gets_the_static_cta(self):
        self.assertIn(
            "if (reduce() || !finePointer()) return { destroy: function () {} };", self.src
        )

    def test_clones_are_presentation_only(self):
        """aria-hidden, untabbable, ids stripped — the real CTA keeps the
        focus and the action."""
        self.assertIn("setAttribute('aria-hidden', 'true')", self.src)
        self.assertIn("setAttribute('tabindex', '-1')", self.src)
        self.assertIn("removeAttribute('id')", self.src)

    def test_spawn_is_distance_throttled(self):
        self.assertIn("dx * dx + dy * dy >= travel * travel", self.src)

    def test_exit_keyframes_keep_the_placement(self):
        """WAAPI transform would clobber the placement translate — the exit
        composes place + scale explicitly."""
        self.assertIn("place + ' scale(1)'", self.src)
        self.assertIn("place + ' scale(0.6)'", self.src)


class TestIdentityTerminalHeroForm(unittest.TestCase):
    """Eloy/Treize Grammes' studio-index hero under the section-form laws:
    the corner-tag terminal frame, one identity slab, and structurally NO
    CTA slot — the withheld CTA defers to the footer finale."""

    def setUp(self):
        self.css = HERO_CSS.read_text(encoding="utf-8")

    def test_root_selector_and_slots(self):
        self.assertIn('[data-ad-form="identity-terminal-hero"]', self.css)
        for slot in ("tag", "identity", "meta"):
            with self.subTest(slot=slot):
                self.assertIn(f'[data-slot="{slot}"]', self.css)

    def test_corner_variants(self):
        for corner in ("tl", "tr", "bl", "br"):
            with self.subTest(corner=corner):
                self.assertIn(f'[data-corner="{corner}"]', self.css)

    def test_no_cta_slot_by_construction(self):
        """The deferred-activation spine: the form defines no CTA slot at
        all, so a build cannot put one in the fold."""
        self.assertNotIn('data-slot="cta', self.css)
        self.assertIn("NO CTA slot", self.css)

    def test_viewport_unit_discipline(self):
        """svh only — a bare 100vh jumps under mobile chrome collapse."""
        self.assertIn("100svh", self.css)
        self.assertNotIn("100vh", self.css)

    def test_zero_motion(self):
        self.assertNotIn("@keyframes", self.css)
        self.assertNotRegex(self.css, r"\banimation\s*:")
        self.assertNotRegex(self.css, r"\btransition\s*:")

    def test_no_loose_component_selectors(self):
        self.assertNotIn(".ad-", self.css)

    def test_tags_preserve_spaces_for_the_diff(self):
        """The char-diff types over spaces — white-space:pre is the
        preserveSpaces analog, owned by the form."""
        self.assertIn("white-space: pre", self.css)

    def test_tokens_read_with_fallbacks(self):
        for token in ("--ad-space", "--ad-ink", "--ad-font-display", "--ad-font-mono"):
            with self.subTest(token=token):
                self.assertIn(token, self.css)

    def test_doc_comment_header(self):
        self.assertTrue(self.css.lstrip().startswith("/*"))

    def test_mobile_breakpoint(self):
        self.assertIn("@media (max-width: 768px)", self.css)


class TestIdentityTerminalHeroEnhancer(unittest.TestCase):
    """The char-DIFF tag swap (TextPlugin type:'diff', 0.3s, Codrops-
    verified): prefix and suffix never move, the middle is typed over on a
    flat clock; text-only mutation, no stylesheet, authored line restored."""

    def setUp(self):
        self.src = HERO_JS.read_text(encoding="utf-8")

    def test_global_export_and_contract(self):
        self.assertIn("(function (global)", self.src)
        self.assertRegex(self.src, r"global\.awardIdentityTerminalHero\s*=")
        self.assertIn("function init", self.src)
        self.assertIn("destroy", self.src)

    def test_diff_pins_prefix_and_suffix(self):
        """Common prefix/suffix stand still — that is what makes the swap
        read as a terminal correcting itself, not a re-type."""
        self.assertIn("while (p < maxP && from.charAt(p) === to.charAt(p)) p++;", self.src)
        self.assertIn("outgoing", self.src)
        self.assertIn("incoming", self.src)

    def test_the_winner_duration(self):
        self.assertIn("opts.swapMs != null ? opts.swapMs : 300", self.src)
        self.assertIn("0.3s", self.src)

    def test_flat_cadence_never_eased(self):
        self.assertIn("flat clock", self.src)
        self.assertNotIn("easeOutCubic", self.src)

    def test_reduce_is_a_no_op(self):
        self.assertIn("if (reduce()) return { destroy: function () {} };", self.src)

    def test_gated_off_screen_and_hidden_tab(self):
        self.assertIn("IntersectionObserver", self.src)
        self.assertIn("visibilitychange", self.src)

    def test_destroy_restores_the_authored_line(self):
        self.assertIn("t.el.textContent = t.authored;", self.src)

    def test_no_stylesheet_injection(self):
        """Layout must survive a dead script — the form CSS is linked."""
        self.assertNotIn("CSS_ID", self.src)


class TestIndexHoverPreview(unittest.TestCase):
    """The Awwwards index-module canon: one cursor-lerped floating preview
    that surfaces the WORK on row hover, with the documented coarse-pointer
    fallback — inline images revealed as rows center under scroll."""

    def setUp(self):
        self.src = _src("index-hover-preview.js")

    def test_rows_declare_their_artwork(self):
        self.assertIn("data-ad-preview-src", self.src)

    def test_one_floating_layer_lerped_toward_the_pointer(self):
        self.assertIn("opts.lerp != null ? opts.lerp : 0.14", self.src)
        self.assertIn("cx += (tx - cx) * lerpK;", self.src)

    def test_layer_is_presentation_only(self):
        self.assertIn("float.setAttribute('aria-hidden', 'true');", self.src)
        self.assertIn("pointer-events:none", self.src)

    def test_reduce_keeps_coverage_drops_amplitude(self):
        """The preview still appears and follows — it snaps instead of
        trailing; nothing scales or fades."""
        self.assertIn("snap — no trailing under reduce", self.src)
        self.assertIn("transition:none", self.src)

    def test_no_idle_raf(self):
        """The loop runs only while shown or still traveling."""
        self.assertIn(
            "if (on || !settledNow) unit.raf = global.requestAnimationFrame(frame);", self.src
        )

    def test_coarse_fallback_is_the_centered_reveal(self):
        """The documented mobile answer: the index flips vertical and each
        row's image reveals inside the viewport's middle band."""
        self.assertIn("'-40% 0px -40% 0px'", self.src)
        self.assertIn("is-centered", self.src)
        self.assertIn("ad-idxprev__inline", self.src)

    def test_fine_coarse_split_is_a_media_gate(self):
        self.assertIn("'(hover: hover) and (pointer: fine)'", self.src)
        self.assertIn("(hover: none), (pointer: coarse)", self.src)

    def test_inline_images_load_lazily(self):
        self.assertIn("im.loading = 'lazy';", self.src)

    def test_evidence_grade_disclosed(self):
        """Canon-documented, not single-winner-verified — the header must
        say so."""
        self.assertIn("canon-documented", self.src)


class TestScrubbedDecorDraw(unittest.TestCase):
    """The dead-middle fix: three channels welded to scroll POSITION (draw
    scrub:0, pluck scrub:8 bounce random, shear -300 powers) — pure
    functions of the bar, so every pass re-fires and reverses."""

    def setUp(self):
        self.src = _src("scrubbed-decor-draw.js")

    def test_three_channels_are_markup_opt_in(self):
        for attr in ("data-ad-decor-draw", "data-ad-decor-pluck", "data-ad-decor-shear"):
            with self.subTest(channel=attr):
                self.assertIn(attr, self.src)

    def test_the_verified_numbers(self):
        self.assertIn("var PLUCK_EACH = 0.1;", self.src)
        self.assertIn("var SHEAR_Y = -300;", self.src)
        self.assertIn("var SHEAR_SCRUB = 0.6;", self.src)
        self.assertIn("opts.scrub != null ? opts.scrub : 8", self.src)

    def test_shear_powers_cycle(self):
        """power3.in / power2.in / power1.in — GSAP powerN.in = p^(N+1)."""
        self.assertIn("var SHEAR_EXPS = [4, 3, 2];", self.src)

    def test_draw_is_a_dash_weld(self):
        self.assertIn("getTotalLength()", self.src)
        self.assertIn("strokeDasharray", self.src)
        self.assertIn("strokeDashoffset", self.src)

    def test_pluck_ease_is_bounce_in_out(self):
        self.assertIn("function bounceInOut(p)", self.src)
        self.assertIn("7.5625", self.src)

    def test_pluck_order_is_random_but_stable(self):
        self.assertIn("function shuffledOrder(n)", self.src)
        self.assertIn("from:'random'", self.src)

    def test_positional_not_fire_once(self):
        self.assertIn("pure function of scroll position", self.src)

    def test_reads_batched_before_writes(self):
        self.assertIn("batch the reads, then the writes", self.src)

    def test_gated_off_screen_and_hidden_tab(self):
        self.assertIn("IntersectionObserver", self.src)
        self.assertIn("visibilitychange", self.src)

    def test_reduce_is_a_no_op_on_an_authored_visible_layer(self):
        """No-JS and reduce show the finished state — the component only
        ever subtracts from a layer that is authored visible."""
        self.assertIn("if (reduce()) return { destroy: function () {} };", self.src)

    def test_destroy_restores_the_authored_layer(self):
        self.assertIn("p.style.strokeDasharray = '';", self.src)
        self.assertIn("p.style.strokeDashoffset = '';", self.src)


class TestSmoothScrollRouting(unittest.TestCase):
    """The authorized edit: in-page anchors and the wordmark-home travel
    ride the Lenis instance (MARE and AVALANCHE both re-invented this by
    hand), and neither ever writes a #fragment into the URL — the
    navigation-patterns wordmark rule."""

    def setUp(self):
        self.src = _src("smooth-scroll.js")

    def test_anchors_ride_the_instance(self):
        self.assertIn("lenis.scrollTo(target, { offset: anchorOffset });", self.src)

    def test_home_is_a_script_scroll_to_top(self):
        self.assertIn("lenis.scrollTo(0);", self.src)
        self.assertIn("'[data-ad-home]'", self.src)

    def test_never_writes_a_fragment(self):
        """No hash assignment, no pushState — preventDefault + scrollTo is
        the whole mechanism, so the URL stays clean."""
        self.assertNotIn("location.hash =", self.src)
        self.assertNotIn("pushState", self.src)
        self.assertIn("preventDefault", self.src)

    def test_at_top_same_page_reloads_natively(self):
        """The wordmark rule's third state: already at the top with a real
        same-page URL → the click falls through to the native reload."""
        self.assertIn("native reload (the wordmark rule)", self.src)

    def test_modified_and_off_page_clicks_stay_native(self):
        self.assertIn("if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;", self.src)
        self.assertIn("a.target || a.hasAttribute('download')", self.src)
        self.assertIn("a.pathname === global.location.pathname", self.src)

    def test_focus_follows_the_travel(self):
        """Sequential focus lands on the target the visitor was sent to —
        the platform only moves it on the native jump we prevented."""
        self.assertIn("target.focus({ preventScroll: true });", self.src)
        self.assertIn("setAttribute('tabindex', '-1')", self.src)

    def test_native_and_reduce_paths_bind_no_routing(self):
        """The pre-edit contract stands: no Lenis or reduced motion → the
        early null-instance return, so platform anchors stay untouched."""
        self.assertIn("return { destroy: function () {}, lenis: null };", self.src)

    def test_destroy_unbinds_the_listener(self):
        self.assertIn("listenRoot.removeEventListener('click', onClick);", self.src)


if __name__ == "__main__":
    unittest.main()
