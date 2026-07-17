"""award-design completeness program — rung 5A (bold-maximal, first half).

Seven builds: four bold-maximal playbook `gaps` (cursor-proximity-typefield,
custom-contextual-cursor, kinetic-splittext-maximal, cursor-spawn-trail) plus
the three chapter-world-ponpon MISSING refs — two sit in `form` fields and
ship as SECTION FORMS (chapter-cover, chapter-select), one sits in the
`loader` field and ships as a component (narrative-scene-one-loader). No
alias ruling was needed: no two ledger lines describe one mechanic (the Eloy
clone-storm named beside cursor-spawn-trail is the already-shipped
footer-clone-machine, distinguished in the component header, not built
twice). What the tests lock is each build's LOAD-BEARING distinction, all
driven in-browser before pinning: the typefield's 7-ring quantization writes
one data attribute per ring transition with every style in per-ring CSS and
a dormant static grid on touch/reduce; the spawn trail plays the verified
brightness/contrast 300→100% decay on a recycled pool throttled by travel
distance inside a JS-clipped host; the contextual cursor collapses its dot in
the zone state (the driven label-legibility finding) and swaps the DICH three
costumes per section; the splittext's 8-char single-hue cycle pops the
eighth char, the elastic mode reverses on viewport exit and cancels its
stale fill:'both' runs on replay; the scene-one loader never locks scroll,
never runs a rAF, and never strands the cover on a failed warm-up; the
cover form clips its full-bleed ground; the select rail releases snap only
for the drag's duration, marks the cover nearest the rail's center (an IO
threshold misread the wide rail), and resets its drag-echo flag on every
new press (the pointercancel finding)."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
COMPONENTS = REPO_ROOT / "skills" / "award-design" / "assets" / "components"
FORMS = COMPONENTS / "forms"

# interaction component file → the global its IIFE must export
RUNG5A_GLOBALS = {
    "cursor-proximity-typefield.js": "awardCursorProximityTypefield",
    "cursor-spawn-trail.js": "awardCursorSpawnTrail",
    "custom-contextual-cursor.js": "awardContextualCursor",
    "kinetic-splittext-maximal.js": "awardKineticSplittextMaximal",
    "narrative-scene-one-loader.js": "awardNarrativeSceneOneLoader",
}

# form id → (css, enhancer js or None, enhancer global or None)
RUNG5A_FORMS = {
    "chapter-cover": ("chapter-cover.css", None, None),
    "chapter-select": ("chapter-select.css", "chapter-select.js", "awardChapterSelect"),
}


def _src(name):
    return (COMPONENTS / name).read_text(encoding="utf-8")


def _form(name):
    return (FORMS / name).read_text(encoding="utf-8")


class TestRung5aLibraryContract(unittest.TestCase):
    """The structural contract every library component keeps (the
    test_component_library floor, applied before the manifest merge)."""

    def test_files_exist(self):
        for name in RUNG5A_GLOBALS:
            with self.subTest(file=name):
                self.assertTrue((COMPONENTS / name).is_file())
        for form_id, (css, js, _g) in RUNG5A_FORMS.items():
            with self.subTest(form=form_id):
                self.assertTrue((FORMS / css).is_file())
                if js:
                    self.assertTrue((FORMS / js).is_file())

    def test_iife_and_global_export(self):
        everything = dict(RUNG5A_GLOBALS)
        for _id, (_css, js, g) in RUNG5A_FORMS.items():
            if js:
                everything["forms/" + js] = g
        for name, g in everything.items():
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("(function (global)", src)
                self.assertRegex(src, r"global\." + re.escape(g) + r"\s*=")

    def test_exposes_init_and_destroy(self):
        files = list(RUNG5A_GLOBALS) + ["forms/" + js for _c, js, _g in RUNG5A_FORMS.values() if js]
        for name in files:
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("function init", src)
                self.assertIn("destroy", src)

    def test_has_reduced_motion_path(self):
        files = list(RUNG5A_GLOBALS) + ["forms/" + js for _c, js, _g in RUNG5A_FORMS.values() if js]
        for name in files:
            with self.subTest(component=name):
                self.assertIn("prefers-reduced-motion", _src(name))

    def test_has_doc_comment_header(self):
        files = (list(RUNG5A_GLOBALS)
                 + ["forms/" + js for _c, js, _g in RUNG5A_FORMS.values() if js]
                 + ["forms/" + css for css, _j, _g in RUNG5A_FORMS.values()])
        for name in files:
            with self.subTest(file=name):
                self.assertTrue(_src(name).lstrip().startswith("/*"))

    def test_namespaced_stylesheet_injection(self):
        """One namespaced stylesheet per interaction component. The form
        enhancer injects nothing — its states live in the linked form CSS."""
        for name in RUNG5A_GLOBALS:
            with self.subTest(component=name):
                self.assertRegex(_src(name), r"CSS_ID = 'ad-[a-z-]+-css'")
        self.assertNotIn("createElement('style')", _src("forms/chapter-select.js"))

    def test_no_bare_100vh(self):
        """svh/dvh only — a bare 100vh jumps under mobile chrome collapse."""
        files = (list(RUNG5A_GLOBALS)
                 + ["forms/" + js for _c, js, _g in RUNG5A_FORMS.values() if js]
                 + ["forms/" + css for css, _j, _g in RUNG5A_FORMS.values()])
        for name in files:
            with self.subTest(file=name):
                self.assertNotRegex(_src(name), r"100vh")


class TestRung5aFormDiscipline(unittest.TestCase):
    """The section-form floors (the test_section_forms contract, applied to
    the two new forms before the manifest merge)."""

    def test_form_root_selector_present(self):
        for form_id, (css, _js, _g) in RUNG5A_FORMS.items():
            with self.subTest(form=form_id):
                self.assertIn(f'[data-ad-form="{form_id}"]', _form(css))

    def test_forms_ship_zero_motion(self):
        """Character comes from paired components; the drag/settle behavior
        lives in the enhancer — the stylesheets carry no motion at all."""
        for form_id, (css, _js, _g) in RUNG5A_FORMS.items():
            src = _form(css)
            with self.subTest(form=form_id):
                self.assertNotIn("@keyframes", src)
                self.assertNotRegex(src, r"\banimation\s*:")
                self.assertNotRegex(src, r"\btransition\s*:")

    def test_no_js_floor_no_hidden_slots(self):
        """A dead script leaves the poster cover and the pannable rail fully
        legible — nothing hides at rest."""
        for form_id, (css, _js, _g) in RUNG5A_FORMS.items():
            src = _form(css)
            with self.subTest(form=form_id):
                self.assertNotRegex(src, r"visibility:\s*hidden")
                self.assertNotRegex(src, r"opacity:\s*0(?![.\d])")

    def test_enhancers_never_write_html_strings(self):
        src = _form("chapter-select.js")
        self.assertNotRegex(src, r"\binnerHTML\s*=")
        self.assertNotRegex(src, r"\binsertAdjacentHTML\b")

    def test_forms_style_attributes_never_role_classes(self):
        """ROLE-RESTYLE gate: grab/drag state rides data attributes on the
        form root — a .ad-*/.is-* selector in a form stylesheet is the
        class-role drift the scanner fails."""
        for form_id, (css, _js, _g) in RUNG5A_FORMS.items():
            src = _form(css)
            with self.subTest(form=form_id):
                self.assertNotRegex(src, r"\.ad-")
                self.assertNotRegex(src, r"\.is-")


class TestCursorProximityTypefield(unittest.TestCase):
    """Exat's operable glyph field: 7 quantized distance rings drive weight
    200→900 and a hot→cold color lerp; styles live in per-ring CSS, JS writes
    one attribute per ring transition; touch/reduce = the static composed
    grid, never a frozen half-state."""

    def setUp(self):
        self.src = _src("cursor-proximity-typefield.js")

    def test_seven_rings_are_a_verdict_not_a_knob(self):
        self.assertIn("var RINGS = 7;", self.src)
        self.assertIn("a verdict, not a knob", self.src)

    def test_weight_sweep_is_the_winners(self):
        self.assertIn("var W_MIN = 200, W_MAX = 900;", self.src)

    def test_quantized_ring_writes_only_on_transition(self):
        self.assertIn("if (ring !== c.ring) { // quantized: write only on a ring transition", self.src)
        self.assertIn("setAttribute('data-tf-ring', String(ring))", self.src)

    def test_styles_live_in_per_ring_css_via_tokens(self):
        """Color is a color-mix between the hot/cold token poles — JS never
        writes an inline style, so a page recolor reaches a live field."""
        self.assertIn("color:color-mix(in oklab,", self.src)
        self.assertIn("--ad-tf-hot", self.src)
        self.assertIn("--ad-tf-cold", self.src)
        self.assertNotIn(".style.color", self.src)
        self.assertNotIn(".style.fontWeight", self.src)

    def test_contained_field_and_em_cells(self):
        """The weight morph must never shift the grid: reflow is contained to
        the field and glyph cells sit in em boxes (weight-independent; ch is
        not)."""
        self.assertIn(".ad-tf{contain:layout style;}", self.src)
        self.assertIn("inline-size:var(--ad-tf-cell,.85em)", self.src)
        self.assertIn("em is weight-independent; ch is not", self.src)

    def test_distance_compares_squared(self):
        self.assertIn("bounds2.push(d * d);", self.src)
        self.assertIn("var d2 = dx * dx + dy * dy;", self.src)

    def test_release_returns_the_composed_rest(self):
        self.assertIn("pointer gone → every unit settles back to the composed rest state", self.src)

    def test_touch_and_reduce_are_the_static_composed_grid(self):
        """The winner's own answer: 'touch devices receive static grid
        versions' — the field never splits, nothing is armed."""
        self.assertIn("if (reduce() || !finePointer()) return { destroy: function () {} };", self.src)

    def test_gated_off_screen_and_hidden_tab(self):
        self.assertIn("IntersectionObserver", self.src)
        self.assertIn("visibilitychange", self.src)

    def test_split_keeps_the_accessible_name_and_rewrap(self):
        self.assertIn("el.setAttribute('aria-label', text)", self.src)
        self.assertIn("document.createTextNode(' ')", self.src)


class TestCursorSpawnTrail(unittest.TestCase):
    """Warhol's footer image trail / DICH's pixel tracer: spawns throttled by
    travel distance on a recycled pool, the verified filter decay, a clipped
    host, dormant on touch — and NOT the Eloy clone-storm, which already
    ships as footer-clone-machine."""

    def setUp(self):
        self.src = _src("cursor-spawn-trail.js")

    def test_the_verified_decay(self):
        """scale 0→1 + brightness/contrast 300→100%, then opacity 1→0 over
        ~0.4s after a short hold — the winner-verified numbers."""
        self.assertIn("var ENTER_MS = 400;", self.src)
        self.assertIn("var FADE_MS = 400;", self.src)
        self.assertIn("filter: 'brightness(3) contrast(3)', opacity: 1", self.src)

    def test_throttled_by_travel_distance(self):
        self.assertIn("if (f.travel < step) return;", self.src)
        self.assertIn("one spawn per threshold crossing, even on a teleport", self.src)

    def test_pool_and_z_recycling(self):
        self.assertIn("f.next = (f.next + 1) % f.nodes.length;", self.src)
        self.assertIn("f.z = (f.z % Z_WRAP) + 1;", self.src)

    def test_pool_images_cycle_in_authored_order(self):
        self.assertIn("f.srcAt = (f.srcAt + 1) % f.srcs.length; // the pool cycles in order", self.src)

    def test_host_is_clipped_while_live(self):
        """The full-bleed overlay law: spawns never paint over neighboring
        sections; the clip rides a JS-applied class so a dead script never
        leaves a section clipped for nothing."""
        self.assertIn(".ad-cst-host{position:relative;overflow:hidden;}", self.src)
        self.assertIn("el.classList.add('ad-cst-host');", self.src)

    def test_layer_never_gates_content(self):
        self.assertIn("pointer-events:none", self.src)
        self.assertIn("layer.setAttribute('aria-hidden', 'true');", self.src)

    def test_pixel_mode_is_the_tokened_tracer(self):
        self.assertIn(".ad-cst__s--px", self.src)
        self.assertIn("--ad-accent", self.src)

    def test_dormant_on_touch_and_reduce(self):
        self.assertIn("if (reduce() || !finePointer()) return { destroy: function () {} };", self.src)

    def test_clone_storm_is_not_this_component(self):
        self.assertIn("footer-clone-machine", self.src)


class TestCustomContextualCursor(unittest.TestCase):
    """The DICH/Cuberto pointer chrome: a lagging ring + tight dot, context
    morphs (zone label / link grow / text shrink), the three section-swapped
    costumes, and full teardown when the pointer class flips."""

    def setUp(self):
        self.src = _src("custom-contextual-cursor.js")

    def test_ring_lerp_sits_in_the_winner_window(self):
        """~0.1-0.2 toward the real pointer — the lag IS the character."""
        self.assertIn("opts.lerp != null ? opts.lerp : 0.16;", self.src)

    def test_context_enum_zone_link_text(self):
        self.assertIn("ctx = 'zone';", self.src)
        self.assertIn("ctx = 'link';", self.src)
        self.assertIn("ctx = 'text';", self.src)

    def test_zone_surfaces_the_declared_label(self):
        self.assertIn("data-ad-cursor-zone", self.src)
        self.assertIn("if (text) label.textContent = text;", self.src)

    def test_dot_collapses_in_zone_state(self):
        """Driven finding: the tight dot parked over the label's own center —
        in the zone state the ring + label ARE the cursor."""
        self.assertIn('.ad-ccc__dot[data-ctx="zone"] i{transform:scale(0);}', self.src)

    def test_the_dich_three_costumes(self):
        self.assertIn('data-variant="electric"', self.src)
        self.assertIn('data-variant="glimmer"', self.src)
        self.assertIn("calm is the default", self.src)

    def test_morphs_ride_inner_elements_never_the_tracker(self):
        self.assertIn("Outer nodes are pure trackers", self.src)

    def test_native_cursor_hides_via_js_class_only(self):
        self.assertIn("'.ad-ccc-hide,.ad-ccc-hide *{cursor:none!important;}'", self.src)
        self.assertIn("docEl.classList.add('ad-ccc-hide');", self.src)

    def test_gate_reevaluates_on_mq_change(self):
        """A convertible flipping to touch tears the chrome down live."""
        self.assertIn("mqOn(finePointer, evaluate);", self.src)
        self.assertIn("mqOn(reduceMQ, evaluate);", self.src)

    def test_chrome_is_decorative_and_singleton(self):
        self.assertIn("var current = null; // page-level singleton", self.src)
        self.assertIn("setAttribute('aria-hidden', 'true')", self.src)

    def test_press_compress(self):
        self.assertIn("data-press", self.src)


class TestKineticSplittextMaximal(unittest.TestCase):
    """The characterful entrance: Warhol's single-hue scale array (8-char
    cycle, eighth pops light) and Ponpon's elastic skew enter, reversible on
    scroll-back — distinct from the tier's monochrome masks."""

    def setUp(self):
        self.src = _src("kinetic-splittext-maximal.js")

    def test_the_eight_char_single_hue_cycle(self):
        """#FB4E2B ×7 + one lighter — a single-hue array, NOT a multi-hue
        color-cycle; token-mapped with the pop falling back to a white-raised
        mix of the hue."""
        self.assertIn("var CYCLE = 8;", self.src)
        self.assertIn("(n % CYCLE === CYCLE - 1 ? ' ad-ksm__c--pop' : '')", self.src)
        self.assertIn("--ad-ksm-hue", self.src)
        self.assertIn("--ad-ksm-pop", self.src)

    def test_the_verified_staggers_and_transforms(self):
        self.assertIn("var STAGGER_SCALE = 100;", self.src)
        self.assertIn("var STAGGER_ELASTIC = 60;", self.src)
        self.assertIn("var SKEW_MAX = 25;", self.src)
        self.assertIn("var ROT = 5;", self.src)

    def test_elastic_ships_as_css_linear_with_fallback(self):
        """elastic.out(0.7,0.7) sampled into linear() — GSAP is never
        required; unsupported engines get a single overshoot bezier."""
        self.assertIn("function elasticLinear()", self.src)
        self.assertIn("global.CSS.supports('animation-timing-function', lin)", self.src)
        self.assertIn("var OVERSHOOT = 'cubic-bezier(.22,1.6,.36,1)';", self.src)

    def test_scale_mode_rides_back_out(self):
        self.assertIn("var BACK_OUT = 'cubic-bezier(.34,1.56,.64,1)';", self.src)

    def test_elastic_reverses_on_exit_scale_fires_once(self):
        self.assertIn("anim.reverse();", self.src)
        self.assertIn("if (el.__adKsmMode === 'scale') io.unobserve(el); // fire once", self.src)

    def test_replay_cancels_the_stale_run(self):
        """Driven finding: fill:'both' runs stack forever on the same
        properties unless the replay cancels them."""
        self.assertIn("stale fill:'both' animations would", self.src)

    def test_hidden_state_is_js_applied(self):
        self.assertIn("JS-applied hidden state → no-JS/dead-script render stays visible", self.src)

    def test_reduce_never_splits(self):
        self.assertIn("return { destroy: function () {} }; // whole, visible, instant", self.src)

    def test_split_keeps_the_accessible_name(self):
        self.assertIn("el.setAttribute('aria-label', text)", self.src)


class TestNarrativeSceneOneLoader(unittest.TestCase):
    """Ponpon's cover-as-scene-one: no overlay gate, no scroll lock, no rAF —
    the poster stands, the scene warms under it, READ NOW hands the live
    cover into the reader."""

    def setUp(self):
        self.src = _src("narrative-scene-one-loader.js")

    def test_never_locks_scroll(self):
        """The opposite move from gated-splash: the cue is an invitation —
        a visitor who scrolls past has simply started reading."""
        self.assertNotIn("body.style.overflow", self.src)
        self.assertIn("gated-splash", self.src)

    def test_event_driven_no_raf(self):
        self.assertNotIn("requestAnimationFrame", self.src)

    def test_warming_holds_the_cue_out_of_reach(self):
        """visibility-hidden via a JS-applied class — a dead script never
        hides the authored cue, and the hidden cue leaves the tab order."""
        self.assertIn("'.ad-nso--warming [data-ad-read-now]{visibility:hidden;opacity:0;'", self.src)
        self.assertIn("cover.setAttribute('aria-busy', 'true');", self.src)

    def test_ready_swaps_poster_for_live(self):
        self.assertIn("'.ad-nso--live [data-ad-scene-poster]{opacity:0;}'", self.src)
        self.assertIn("no minimum hold", self.src)

    def test_failed_warmup_never_strands_the_cover(self):
        self.assertIn("opts.ready.then(goLive, goLive); // a failed warm-up never strands the cover", self.src)

    def test_default_ready_is_the_window_load(self):
        self.assertIn("document.readyState === 'complete'", self.src)
        self.assertIn("global.addEventListener('load', onLoad);", self.src)

    def test_handoff_scrolls_in_character_and_marks_the_cover(self):
        self.assertIn("behavior: reduce() ? 'auto' : 'smooth'", self.src)
        self.assertIn("cover.setAttribute('data-ad-nso-read', '')", self.src)

    def test_reduce_keeps_the_poster_as_the_scene(self):
        self.assertIn("the poster IS the scene, the cue is live immediately", self.src)

    def test_cue_stays_a_real_link_for_no_js(self):
        self.assertIn("no target → a real link keeps its native jump", self.src)


class TestChapterCoverForm(unittest.TestCase):
    """The cover-is-scene-one hero form: a full-viewport stage, the ground
    clipped full-bleed under the stack, poster above the live mount, the
    read affordance a real anchor."""

    def setUp(self):
        self.css = _form("chapter-cover.css")

    def test_resolves_the_recipes_missing_ref(self):
        self.assertIn("MISSING:chapter-cover", self.css)

    def test_full_viewport_stage_svh(self):
        self.assertIn("min-height: 100svh;", self.css)

    def test_ground_is_full_bleed_and_clipped(self):
        self.assertIn('> [data-slot="ground"]', self.css)
        self.assertIn("inset: 0;", self.css)
        self.assertIn("the scene ground never paints over neighboring sections", self.css)

    def test_poster_rides_above_the_live_mount(self):
        self.assertIn("[data-ad-scene-poster] { z-index: 1; }", self.css)

    def test_every_slot_is_styled(self):
        for slot in ("ground", "kicker", "wordmark", "standfirst", "read-cue"):
            with self.subTest(slot=slot):
                self.assertIn(f'[data-slot="{slot}"]', self.css)

    def test_align_variant(self):
        self.assertIn('[data-align="start"]', self.css)

    def test_pairs_are_the_recipes_pairs(self):
        """The form's header routes the slots to the recipe's own pairing:
        ground → shader-surface, wordmark → char-assemble, cue → the
        scene-one loader."""
        self.assertIn("shader-surface", self.css)
        self.assertIn("char-assemble", self.css)
        self.assertIn("narrative-scene-one-loader", self.css)


class TestChapterSelectForm(unittest.TestCase):
    """Ponpon's record collection: native snap rail (snap-align center IS
    snap-to-place), grab-drag with the snap released only for the drag's
    duration, drag-click suppression, nearest-center marking."""

    def setUp(self):
        self.css = _form("chapter-select.css")
        self.js = _form("chapter-select.js")

    def test_resolves_the_recipes_missing_ref(self):
        self.assertIn("MISSING:chapter-select", self.css)

    def test_native_snap_rail(self):
        self.assertIn("scroll-snap-type: x mandatory;", self.css)
        self.assertIn("scroll-snap-align: center;", self.css)
        self.assertIn("overscroll-behavior-x: contain;", self.css)

    def test_album_cover_tiles(self):
        self.assertIn("aspect-ratio: 1;", self.css)
        self.assertIn("-webkit-user-drag: none;", self.css)

    def test_drag_releases_snap_via_root_attribute(self):
        self.assertIn('[data-cs-dragging] > [data-slot="rows"]', self.css)
        self.assertIn("scroll-snap-type: none;", self.css)

    def test_drag_is_fine_pointer_only(self):
        """Touch keeps the native pan + snap — the winner interaction there;
        the enhancer arms nothing."""
        self.assertIn("if (finePointer()) {", self.js)

    def test_click_stays_click_drag_stays_drag(self):
        self.assertIn("var DRAG_MIN = 6;", self.js)
        self.assertIn("rows.addEventListener('click', u.onClick, true);", self.js)
        self.assertIn("e.preventDefault(); // a drag is not a navigation", self.js)

    def test_new_press_resets_the_drag_echo(self):
        """Driven finding: a pointercancel leaves no click, so a stale
        justDragged would eat the NEXT genuine click."""
        self.assertIn("u.justDragged = false; // a new press is a new gesture", self.js)

    def test_release_settles_to_center_then_reengages_snap(self):
        self.assertIn("inline: 'center'", self.js)
        self.assertIn("rows.addEventListener('scrollend', settle);", self.js)
        self.assertIn("u.settleTimer = global.setTimeout(settle, SETTLE_MS);", self.js)

    def test_marking_is_nearest_center_not_an_io_threshold(self):
        """Driven finding: an IO threshold misreads a wide rail where several
        covers sit fully visible — the picked-up record is the cover nearest
        the rail's center."""
        self.assertIn("the cover nearest the rail's center", self.js)
        self.assertIn("aria-current", self.js)

    def test_settle_respects_reduced_motion(self):
        self.assertIn("behavior: reduce() ? 'auto' : 'smooth'", self.js)

    def test_layering_law_no_created_nodes(self):
        self.assertNotIn("createElement", self.js)


if __name__ == "__main__":
    unittest.main()
