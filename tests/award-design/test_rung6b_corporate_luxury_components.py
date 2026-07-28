"""award-design completeness program — rung 6B (corporate-luxury, second half).

Six builds: four shipped as components (scrub-parallax-bed,
route-transition-overlay, press-hold-reveal, scored-scene-procession), one
as a loader component (svg-path-fill-loader — the MISSING loader of
engine-world-depoluxe) and one as a SECTION FORM (place-tour — the MISSING
proof form of argument-scroll-sondaven). MISSING refs resolved: place-tour
and svg-path-fill-loader. Alias rulings on evidence, written into each
header: route-transition-overlay is DISTINCT from curtain-transition (wipe
tool — no interception, no fetch, no history), route-view-transition-carrier
(SPA crossfade around a builder-supplied fn) and page-transition-choreography
(bold-maximal spectacle blend) — only this one keeps a real href alive
(intercept → cover → fetch + swap + pushState → held re-entry → uncover,
popstate both directions); scored-scene-procession is a COMPANION of
rooms-procession, never a rebuild (the rig owns the scroll math; this
conductor requires it and adds the dispose/load lifecycle + the
position-keyed score behind a gesture-unlocked toggle), and DISTINCT from
sound-channel (scene-agnostic ambient — one audio carrier per page, ever);
press-hold-reveal completes the charge arc contextual-cursor-label left to
the object, on the SHARED data-ad-gesture markup (one clock) with the same
700ms band and 3x retract; scrub-parallax-bed is scroll-driven always-on
(pointer-parallax is pointer-driven fine-only dormant-on-touch). What the
tests lock is each build's LOAD-BEARING driven distinction: the bed's
layers are a pure function of scroll (driven: identical transforms at the
same y down and back up, film ranged + 0.25s-lagged); the overlay swaps
under FULL cover and its transitionend filter ignores the ::after hairline
(driven: the unfiltered listener resolved the exit early and stranded the
panel in is-exit); the charge tracks the declared hold (driven:
0.276/0.56/0.846 at 200/400/600ms of 700, retract 0.421 → 0 in ~180ms,
first-class under touch emulation); the conductor's live window moved
1100→1110→0111→0011 and the stems mixed [1,0,0,0] → [0,.38,.62,0] with the
walk, the graph absent until the trusted toggle click; the loader's mark IS
the gauge (driven: valuenow 22→82→100 with the clip falling in lockstep,
then dissolve, unwrap, unlock, onDone at 2893ms)."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
COMPONENTS = REPO_ROOT / "skills" / "award-design" / "assets" / "components"
FORMS = COMPONENTS / "forms"

# interaction/loader component file → the global its IIFE must export
RUNG6B_GLOBALS = {
    "scrub-parallax-bed.js": "awardScrubParallaxBed",
    "route-transition-overlay.js": "awardRouteTransitionOverlay",
    "press-hold-reveal.js": "awardPressHoldReveal",
    "scored-scene-procession.js": "awardScoredSceneProcession",
    "svg-path-fill-loader.js": "awardSvgPathFillLoader",
}

# form id → (css, enhancer js, enhancer global)
RUNG6B_FORMS = {
    "place-tour": ("place-tour.css", "place-tour.js", "awardPlaceTour"),
}


def _src(name):
    return (COMPONENTS / name).read_text(encoding="utf-8")


def _form(name):
    return (FORMS / name).read_text(encoding="utf-8")


class TestRung6bLibraryContract(unittest.TestCase):
    """The structural contract every library component keeps (the
    test_component_library floor, applied before the manifest merge)."""

    def test_files_exist(self):
        for name in RUNG6B_GLOBALS:
            with self.subTest(file=name):
                self.assertTrue((COMPONENTS / name).is_file())
        for form_id, (css, js, _g) in RUNG6B_FORMS.items():
            with self.subTest(form=form_id):
                self.assertTrue((FORMS / css).is_file())
                self.assertTrue((FORMS / js).is_file())

    def test_iife_and_global_export(self):
        everything = dict(RUNG6B_GLOBALS)
        for _id, (_css, js, g) in RUNG6B_FORMS.items():
            everything["forms/" + js] = g
        for name, g in everything.items():
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("(function (global)", src)
                self.assertRegex(src, r"global\." + re.escape(g) + r"\s*=")

    def test_exposes_init_and_destroy(self):
        files = list(RUNG6B_GLOBALS) + ["forms/" + js for _c, js, _g in RUNG6B_FORMS.values()]
        for name in files:
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("function init", src)
                self.assertIn("destroy", src)

    def test_has_reduced_motion_path(self):
        files = list(RUNG6B_GLOBALS) + ["forms/" + js for _c, js, _g in RUNG6B_FORMS.values()]
        for name in files:
            with self.subTest(component=name):
                self.assertIn("prefers-reduced-motion", _src(name))

    def test_has_doc_comment_header(self):
        files = (list(RUNG6B_GLOBALS)
                 + ["forms/" + js for _c, js, _g in RUNG6B_FORMS.values()]
                 + ["forms/" + css for css, _j, _g in RUNG6B_FORMS.values()])
        for name in files:
            with self.subTest(file=name):
                self.assertTrue(_src(name).lstrip().startswith("/*"))

    def test_namespaced_stylesheet_injection(self):
        """One namespaced stylesheet per interaction component. The form
        enhancer injects nothing — its states live in the linked form CSS."""
        for name in RUNG6B_GLOBALS:
            with self.subTest(component=name):
                self.assertRegex(_src(name), r"CSS_ID = 'ad-[a-z-]+-css'")
        for _id, (_css, js, _g) in RUNG6B_FORMS.items():
            self.assertNotIn("createElement('style')", _src("forms/" + js))

    def test_no_bare_100vh(self):
        """svh/lvh/dvh only — a bare 100vh jumps under mobile chrome
        collapse."""
        files = (list(RUNG6B_GLOBALS)
                 + ["forms/" + js for _c, js, _g in RUNG6B_FORMS.values()]
                 + ["forms/" + css for css, _j, _g in RUNG6B_FORMS.values()])
        for name in files:
            with self.subTest(file=name):
                self.assertNotRegex(_src(name), r"100vh")


class TestRung6bFormDiscipline(unittest.TestCase):
    """The section-form floors (the test_section_forms contract, applied to
    place-tour before the manifest merge)."""

    def setUp(self):
        self.css = _form("place-tour.css")
        self.js = _form("place-tour.js")

    def test_form_root_selector_present(self):
        self.assertIn('[data-ad-form="place-tour"]', self.css)

    def test_form_ships_zero_motion(self):
        self.assertNotIn("@keyframes", self.css)
        self.assertNotRegex(self.css, r"\banimation\s*:")
        self.assertNotRegex(self.css, r"\btransition\s*:")

    def test_no_js_floor_no_hidden_slots(self):
        """A dead script leaves the full itinerary legible — nothing hides
        at rest, ever (place-tour has no live-swap state at all)."""
        self.assertNotRegex(self.css, r"opacity:\s*0(?![.\d])")
        self.assertNotIn("visibility: hidden", self.css)
        self.assertNotIn("display: none", self.css)

    def test_enhancer_publishes_attributes_only(self):
        """No markup strings, nothing mounted, no inner-DOM surgery — the
        publish is data attributes on the form root and the station."""
        self.assertNotRegex(self.js, r"\binnerHTML\s*=")
        self.assertNotRegex(self.js, r"\binsertAdjacentHTML\b")
        self.assertNotRegex(self.js, r"\bappendChild\b")
        self.assertNotIn("createElement", self.js)
        self.assertIn("data-ad-place-station", self.js)
        self.assertIn("data-ad-place-active", self.js)

    def test_form_styles_attributes_never_role_classes(self):
        """class-role uniformity rule: form state rides data attributes — a
        .ad-*/.is-* selector in a form stylesheet is class-role drift."""
        self.assertNotRegex(self.css, r"\.ad-")
        self.assertNotRegex(self.css, r"\.is-")

    def test_resolves_the_recipes_missing_ref(self):
        self.assertIn("MISSING:place-tour", self.css)
        self.assertIn("argument-scroll-sondaven", self.css)

    def test_the_alias_ruling_rides_in_the_header(self):
        """DISTINCT from the held-object stepthrough and the single split
        band — the walk owns a plate PER station."""
        self.assertIn("pinned-media-stepthrough", self.css)
        self.assertIn("editorial-split", self.css)
        self.assertIn("DISTINCT", self.css)

    def test_walk_time_counter_is_tabular(self):
        """The playbook's copy law: tabular numerals for counts."""
        self.assertIn("font-variant-numeric: tabular-nums", self.css)

    def test_publish_is_zero_flip_and_reversible(self):
        """Attributes write only on change; the walk is a pure function of
        scroll (driven: 0→1→2 down, 2→1→0 back up)."""
        self.assertIn("if (nearest !== u.active) {", self.js)
        self.assertIn("Math.abs(u.centers[i] - vc)", self.js)

    def test_reduce_is_the_static_itinerary(self):
        self.assertIn("if (reduce()) return { destroy: function () {} };", self.js)


class TestScrubParallaxBed(unittest.TestCase):
    """Son Daven's continuation bed: scroll-welded differential layers +
    the lagged film channel — always-on, reversible, works on touch."""

    def setUp(self):
        self.src = _src("scrub-parallax-bed.js")

    def test_the_alias_ruling_rides_in_the_header(self):
        self.assertIn("Ruled DISTINCT", self.src)
        self.assertIn("pointer-parallax", self.src)
        self.assertIn("scrubbed-decor-draw", self.src)
        self.assertIn("dolly-zoom", self.src)

    def test_layers_are_a_pure_function_of_scroll(self):
        """ease:none — the raw weld (driven: identical transforms at the
        same scroll position walking down AND back up)."""
        self.assertIn("return clamp01((sy + vh - u.top) / (vh + u.height));", self.src)
        self.assertIn("ease:none", self.src)

    def test_layer_writes_are_transform_only_and_differential(self):
        self.assertIn(
            "'translate3d(0,' + (-offset * L.depth * u.amp).toFixed(2) + 'px,0)'", self.src)

    def test_film_chases_through_the_quarter_second_catchup(self):
        """The scrub:.25 register (driven: film t trailing the layer weld,
        7.34s at the same y both directions)."""
        self.assertIn("var FILM_TAU = 0.25;", self.src)
        self.assertIn("1 - Math.exp(-dt / FILM_TAU)", self.src)

    def test_seeks_are_throttled_to_the_frame(self):
        self.assertIn("var FRAME = 1 / 30;", self.src)
        self.assertIn("if (!u.seeking && Math.abs(u.film.currentTime - t) > FRAME)", self.src)

    def test_rangeless_serving_self_heals_to_blob(self):
        """The scrub-film law (driven: on the Range-capable lab server the
        source stayed 'ranged' and seekable — the heal never fired)."""
        self.assertIn("film.seekable.length", self.src)
        self.assertIn("URL.createObjectURL", self.src)

    def test_offscreen_and_hidden_tabs_park_the_bed(self):
        self.assertIn("IntersectionObserver", self.src)
        self.assertIn("visibilitychange", self.src)

    def test_promotion_rides_a_js_applied_class(self):
        """No-JS pays nothing — will-change binds only under .ad-spb-live."""
        self.assertIn(".ad-spb-live [data-depth]{will-change:transform;}", self.src)
        self.assertIn("el.classList.add('ad-spb-live');", self.src)

    def test_reduce_is_the_authored_rest(self):
        """Driven under ?rm: four transforms 'none', film held at poster,
        no live class."""
        self.assertIn("if (reduce()) return { destroy: function () {} };", self.src)


class TestRouteTransitionOverlay(unittest.TestCase):
    """The multi-page continuity pipeline: intercept → cover → fetch + swap
    + pushState → held re-entry → uncover; popstate both directions."""

    def setUp(self):
        self.src = _src("route-transition-overlay.js")

    def test_the_alias_ruling_rides_in_the_header(self):
        """DISTINCT from all three shipped transition tools, by mechanism —
        none of them keeps a real href alive."""
        self.assertIn("Ruled DISTINCT", self.src)
        self.assertIn("curtain-transition", self.src)
        self.assertIn("route-view-transition-carrier", self.src)
        self.assertIn("page-transition-choreography", self.src)

    def test_intercepts_only_plain_same_origin_left_clicks(self):
        self.assertIn("e.metaKey || e.ctrlKey || e.shiftKey || e.altKey", self.src)
        self.assertIn("if (url.origin !== global.location.origin) return;", self.src)
        self.assertIn("a.hasAttribute('download')", self.src)

    def test_swap_happens_under_full_cover(self):
        """Fetch + DOMParser + adoptNode into the standing container; the
        title travels (driven: path and title flipped while ty=0)."""
        self.assertIn("new DOMParser().parseFromString(html, 'text/html')", self.src)
        self.assertIn("document.adoptNode(n)", self.src)
        self.assertIn("document.title = doc.title || document.title;", self.src)

    def test_history_is_honest_both_directions(self):
        """pushState on navigate, popstate riding the same beat (driven:
        history.back() played cover → swap → re-entry → uncover)."""
        self.assertIn("history.pushState({ adRto: true }, '', url);", self.src)
        self.assertIn("global.addEventListener('popstate', onPop);", self.src)

    def test_transitionend_filter_is_the_driven_fix(self):
        """The ::after hairline's transitions bubble from the panel and
        resolved the exit a beat early — the unfiltered listener stranded
        the panel in is-exit (driven, then re-driven clean)."""
        self.assertIn("e.propertyName !== 'transform'", self.src)
        self.assertIn("e.pseudoElement", self.src)

    def test_reentry_beat_is_held_and_capped(self):
        """onEnter may return a promise; the cover holds for it, capped so
        a slow re-init never strands the visitor."""
        self.assertIn("Promise.race([", self.src)
        self.assertIn("setTimeout(res, reentryCap)", self.src)

    def test_focus_lands_and_the_tabindex_survives_until_blur(self):
        """Driven finding: removing tabindex synchronously dropped the
        focus we just placed."""
        self.assertIn("mine.addEventListener('blur', function onBlur() {", self.src)
        self.assertIn("mine.focus({ preventScroll: true });", self.src)

    def test_any_failure_falls_through_to_the_browser(self):
        self.assertIn("global.location.href = url;", self.src)

    def test_reduce_is_instant_swap_plus_short_crossfade(self):
        """The gap's own degrade order (driven under ?rm: no panel ever
        existed, path and title flipped, thread still re-rooted)."""
        self.assertIn("mine.animate([{ opacity: 0.35 }, { opacity: 1 }]", self.src)

    def test_one_navigation_owner_per_page(self):
        self.assertIn("var current = null; // one navigation owner per page, ever", self.src)


class TestPressHoldReveal(unittest.TestCase):
    """LV's hold-to-charge gesture — the object half of the charge arc,
    welded to the cursor by the shared markup contract."""

    def setUp(self):
        self.src = _src("press-hold-reveal.js")

    def test_the_weld_is_the_shared_markup_contract(self):
        """One attribute times the cursor's dial AND the object's charge —
        never two clocks; the same LV band and retract grammar."""
        self.assertIn("'[data-ad-gesture=\"HOLD\"]'", self.src)
        self.assertIn("data-ad-gesture-hold", self.src)
        self.assertIn("the same default as contextual-cursor-label", self.src)
        self.assertIn("var HOLD_DEFAULT = 700;", self.src)
        self.assertIn("var RETRACT_RATE = 3;", self.src)

    def test_the_alias_ruling_rides_in_the_header(self):
        self.assertIn("Ruled DISTINCT", self.src)
        self.assertIn("hard-press-button", self.src)
        self.assertIn("drives no reveal", self.src)

    def test_charge_publishes_the_three_surfaces(self):
        """--ad-phr-charge + data-ad-charging + data-ad-revealed (driven:
        0.276/0.56/0.846 at 200/400/600ms of a 700ms hold, locked at 1)."""
        self.assertIn("host.style.setProperty('--ad-phr-charge', u.charge.toFixed(3));", self.src)
        self.assertIn("host.setAttribute('data-ad-charging', '');", self.src)
        self.assertIn("host.setAttribute('data-ad-revealed', '');", self.src)

    def test_completion_locks_and_announces(self):
        self.assertIn("if (u.charge >= 1) { reveal(host); return; } // complete — locked", self.src)
        self.assertIn("host.setAttribute('aria-expanded', 'true');", self.src)

    def test_early_release_retracts_at_the_cursor_rate(self):
        """Driven: 0.421 at release → 0.137 at +60ms → 0 at +180ms, the
        charging attribute cleared, never revealed."""
        self.assertIn("u.charge = Math.max(0, u.charge - dt * RETRACT_RATE / u.holdMs);", self.src)

    def test_cancel_on_leave_is_the_gaps_contract(self):
        self.assertIn("host.addEventListener('pointercancel', u.onUp);", self.src)
        self.assertIn("host.addEventListener('pointerleave', u.onLeave);", self.src)

    def test_touch_is_first_class_never_dormant(self):
        """Driven under touch emulation: charge 0.495 mid-hold, complete at
        1 — plus the long-press guards."""
        self.assertIn("touch-action:manipulation", self.src)
        self.assertIn("u.onMenu", self.src)
        self.assertIn("user-select:none", self.src)

    def test_keyboard_is_a_single_activate(self):
        """The gap's sanctioned equivalent — no timing barrier."""
        self.assertIn("if (e.key !== 'Enter' && e.key !== ' ') return;", self.src)
        self.assertIn("single activate", self.src)

    def test_reduce_reveals_instantly_and_gates_the_settle(self):
        """Driven under ?rm: press = instant reveal; parse-verified: the
        settle transition lives ONLY inside the no-preference block."""
        self.assertIn("if (reduce()) { reveal(host); return; }", self.src)
        self.assertIn("'@media (prefers-reduced-motion: no-preference){'", self.src)

    def test_destroy_never_slams_the_trunk(self):
        self.assertIn("a revealed trunk never slams shut", self.src)


class TestScoredSceneProcession(unittest.TestCase):
    """The pavilion conductor: dispose/load lifecycle + the position-keyed
    score, welded onto the rooms-procession rig."""

    def setUp(self):
        self.src = _src("scored-scene-procession.js")

    def test_companion_of_the_rig_never_a_rebuild(self):
        """Requires awardRoomsProcession, constructs it, passes the
        builder's callbacks through — no scroll math re-derived here."""
        self.assertIn("var rigLib = global.awardRoomsProcession;", self.src)
        self.assertIn("rooms-procession is required", self.src)
        self.assertIn("if (opts.onRoom) opts.onRoom(index, prev);", self.src)
        # no code-level scroll math — the rig owns it (the header MAY name
        # scrollY in prose; the code never reads it)
        self.assertNotIn("pageYOffset", self.src)
        self.assertNotIn("getBoundingClientRect", self.src)
        self.assertNotRegex(self.src, r"\baddEventListener\('scroll'")

    def test_the_alias_ruling_rides_in_the_header(self):
        self.assertIn("Ruled DISTINCT", self.src)
        self.assertIn("sound-channel", self.src)
        self.assertIn("One audio carrier per page, ever", self.src)

    def test_lifecycle_window_is_the_dispose_load_policy(self):
        """Driven: window 1100→1110→0111→0011 across a 4-room walk, loads
        and disposes firing once per crossing, reversing on the way up."""
        self.assertIn("var MARGIN_DEFAULT = 1;", self.src)
        self.assertIn("var want = Math.abs(i - active) <= margin;", self.src)
        self.assertIn("roomEls[i].setAttribute('data-ad-ssp-load', '');", self.src)
        self.assertIn("if (opts.onSceneDispose) opts.onSceneDispose(i, roomEls[i]);", self.src)

    def test_stems_are_keyed_to_walk_proximity(self):
        """Crossing a boundary IS the crossfade (driven: [1,0,0,0] in room
        0 → [0,.38,.62,0] mid-crossing)."""
        self.assertIn("var g = clamp01(1 - Math.abs(pos - i));", self.src)
        self.assertIn("mixStems(index + t, false);", self.src)

    def test_the_unlock_law_is_absolute(self):
        """The AudioContext is created ONLY inside the toggle's gesture
        (driven: the gain graph was absent until the trusted click)."""
        self.assertIn("audio.ctx = new AC(); // inside the gesture — the unlock law", self.src)
        self.assertIn("toggle.setAttribute('aria-pressed', 'false');", self.src)

    def test_toggle_names_its_action(self):
        self.assertIn("'Play the score'", self.src)
        self.assertIn("'Mute the score'", self.src)

    def test_ramps_are_zipper_safe_and_snap_under_reduce(self):
        self.assertIn("var RAMP = 0.08;", self.src)
        self.assertIn("if (snap || reduce()) p.setValueAtTime(g, t);", self.src)

    def test_a_lost_stem_thins_the_mix_never_breaks_the_walk(self):
        self.assertIn("a lost stem thins the mix, never breaks the walk", self.src)

    def test_destroy_closes_the_graph_and_the_rig(self):
        self.assertIn("rig.destroy();", self.src)
        self.assertIn("audio.ctx.close()", self.src)


class TestSvgPathFillLoader(unittest.TestCase):
    """Depo Luxe's entrance: the mark fills with honest progress, then the
    scene dissolves — no hard cut, the mark IS the gauge."""

    def setUp(self):
        self.src = _src("svg-path-fill-loader.js")

    def test_resolves_the_recipes_missing_ref(self):
        self.assertIn("MISSING:svg-path-fill-loader", self.src)
        self.assertIn("engine-world-depoluxe", self.src)

    def test_the_alias_ruling_rides_in_the_header(self):
        self.assertIn("Ruled DISTINCT", self.src)
        self.assertIn("branded-preloader", self.src)
        self.assertIn("flip-handoff-loader", self.src)
        self.assertIn("counter-loader", self.src)
        self.assertIn("type-forward-intro-loader", self.src)

    def test_the_mark_is_the_gauge(self):
        """A ghost+fill clone pair; the fill's clip-path falls with
        progress (driven: valuenow 22→82 with clip 78%→17.8% in lockstep)."""
        self.assertIn("clip-path:inset(100% 0 0 0)", self.src)
        self.assertIn(
            "fillLayer.style.clipPath = 'inset(' + ((1 - v) * 100).toFixed(2) + '% 0 0 0)';",
            self.src)
        self.assertIn("svg.cloneNode(true)", self.src)
        self.assertIn("the author's mark is never mutated", self.src)

    def test_fill_stays_honest(self):
        """Ease to 90, hold for the real window load, settle (the library's
        loader law; driven: settle at 100 only past minDuration + load)."""
        self.assertIn("var target = easeOutCubic(p) * 0.9;", self.src)
        self.assertIn("if (p >= 1 && loaded) target = 1;", self.src)

    def test_dissolve_has_a_held_beat_and_no_hard_cut(self):
        """Full mark held one base duration, then opacity-only dissolve
        over the painted hero (driven: 3 samples at 100, then 6 'leaving')."""
        self.assertIn("scene.classList.add('is-leaving');", self.src)
        self.assertIn("no hard cut", self.src)

    def test_progressbar_announced(self):
        self.assertIn("mark.setAttribute('role', 'progressbar');", self.src)
        self.assertIn("aria-valuenow", self.src)
        self.assertIn("scene.setAttribute('aria-busy', 'true');", self.src)

    def test_scene_authored_hidden_and_restored(self):
        """No-JS never gets covered; the teardown returns the authored svg
        and the hidden state (driven: hidden-restored, mark unwrapped,
        scroll unlocked)."""
        self.assertIn("scene.removeAttribute('hidden');", self.src)
        self.assertIn("scene.setAttribute('hidden', '');", self.src)
        self.assertIn("document.body.style.overflow = prevOverflow;", self.src)

    def test_skip_paths_still_fire_ondone(self):
        """Reduce or a seen session: the scene never shows, onDone fires
        (driven under ?rm with a sentinel wrapper: 'fired')."""
        self.assertIn("reduce() || (opts.sessionOnce && seen())", self.src)


if __name__ == "__main__":
    unittest.main()
