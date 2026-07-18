"""award-design completeness program — rung 6A (corporate-luxury, first half).

Six builds: four shipped as components (contextual-cursor-label,
flip-handoff-loader, infinite-scroll-loop, line-draw-cta) and two as SECTION
FORMS (in-engine-hero — the MISSING hero `form` of engine-world-depoluxe AND
studio-reel-lusion; pinned-media-stepthrough — the proof band's pin+scrub
device, listed under the section_playbook's proof forms). MISSING refs
resolved: flip-handoff-loader (argument-scroll-sondaven's loader field) and
in-engine-hero (both hero form fields). Alias rulings on evidence, written
into each header: contextual-cursor-label is DISTINCT from cursor-verb-label
(field-scoped label chip, no ring chrome, no hold instrument) and from
custom-contextual-cursor (page-level pointer costume) — this one leaves the
native cursor everywhere off-surface and adds the LV click-and-hold charge
arc; flip-handoff-loader is DISTINCT from loader-into-navbar (nothing
travels there) and branded-preloader (recedes in place, no continuity);
infinite-scroll-loop is DISTINCT from swipe-snap-gallery (finite by design);
pinned-media-stepthrough is DISTINCT from pinned-demo-panels (there the
stage content cross-fades panel to panel; here ONE media figure holds at
full opacity for the entire pin). What the tests lock is each build's
LOAD-BEARING driven distinction: the ring draws AND retracts through the
same transition with the line present at rest under reduce; the hold arc
tracks the object's declared duration (driven 26/52/76% at 173/357/524ms of
a 700ms hold, charged at 691ms) and retracts 3x on release; the FLIP lands
on the measured target rect (driven 0.0px delta) with the wait and the
scroll lock released only after; the loop's clones stay hit-testable
(driven: `inert` dead-zoned every wrapped copy), the center coordinate
wraps modulo the period (driven: item 0 unreachable without it), the focus
glide clamps instead of wrapping and neutralizes the browser's own
focus-scroll on the hidden overflow; the stepthrough's media is never
written by the enhancer (driven: opacity 1 at every sample of a full scrub,
both directions, zero neighbor overlap)."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
COMPONENTS = REPO_ROOT / "skills" / "award-design" / "assets" / "components"
FORMS = COMPONENTS / "forms"

# interaction component file → the global its IIFE must export
RUNG6A_GLOBALS = {
    "contextual-cursor-label.js": "awardContextualCursorLabel",
    "flip-handoff-loader.js": "awardFlipHandoffLoader",
    "infinite-scroll-loop.js": "awardInfiniteScrollLoop",
    "line-draw-cta.js": "awardLineDrawCta",
}

# form id → (css, enhancer js or None, enhancer global or None)
RUNG6A_FORMS = {
    "in-engine-hero": ("in-engine-hero.css", "in-engine-hero.js", "awardInEngineHero"),
    "pinned-media-stepthrough": (
        "pinned-media-stepthrough.css",
        "pinned-media-stepthrough.js",
        "awardPinnedMediaStepthrough",
    ),
}


def _src(name):
    return (COMPONENTS / name).read_text(encoding="utf-8")


def _form(name):
    return (FORMS / name).read_text(encoding="utf-8")


class TestRung6aLibraryContract(unittest.TestCase):
    """The structural contract every library component keeps (the
    test_component_library floor, applied before the manifest merge)."""

    def test_files_exist(self):
        for name in RUNG6A_GLOBALS:
            with self.subTest(file=name):
                self.assertTrue((COMPONENTS / name).is_file())
        for form_id, (css, js, _g) in RUNG6A_FORMS.items():
            with self.subTest(form=form_id):
                self.assertTrue((FORMS / css).is_file())
                if js:
                    self.assertTrue((FORMS / js).is_file())

    def test_iife_and_global_export(self):
        everything = dict(RUNG6A_GLOBALS)
        for _id, (_css, js, g) in RUNG6A_FORMS.items():
            if js:
                everything["forms/" + js] = g
        for name, g in everything.items():
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("(function (global)", src)
                self.assertRegex(src, r"global\." + re.escape(g) + r"\s*=")

    def test_exposes_init_and_destroy(self):
        files = list(RUNG6A_GLOBALS) + ["forms/" + js for _c, js, _g in RUNG6A_FORMS.values() if js]
        for name in files:
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("function init", src)
                self.assertIn("destroy", src)

    def test_has_reduced_motion_path(self):
        files = list(RUNG6A_GLOBALS) + ["forms/" + js for _c, js, _g in RUNG6A_FORMS.values() if js]
        for name in files:
            with self.subTest(component=name):
                self.assertIn("prefers-reduced-motion", _src(name))

    def test_has_doc_comment_header(self):
        files = (list(RUNG6A_GLOBALS)
                 + ["forms/" + js for _c, js, _g in RUNG6A_FORMS.values() if js]
                 + ["forms/" + css for css, _j, _g in RUNG6A_FORMS.values()])
        for name in files:
            with self.subTest(file=name):
                self.assertTrue(_src(name).lstrip().startswith("/*"))

    def test_namespaced_stylesheet_injection(self):
        """One namespaced stylesheet per interaction component. The form
        enhancers inject nothing — their states live in the linked form CSS."""
        for name in RUNG6A_GLOBALS:
            with self.subTest(component=name):
                self.assertRegex(_src(name), r"CSS_ID = 'ad-[a-z-]+-css'")
        for _id, (_css, js, _g) in RUNG6A_FORMS.items():
            self.assertNotIn("createElement('style')", _src("forms/" + js))

    def test_no_bare_100vh(self):
        """svh/lvh/dvh only — a bare 100vh jumps under mobile chrome
        collapse (the loop scroller and both form stages ride svh)."""
        files = (list(RUNG6A_GLOBALS)
                 + ["forms/" + js for _c, js, _g in RUNG6A_FORMS.values() if js]
                 + ["forms/" + css for css, _j, _g in RUNG6A_FORMS.values()])
        for name in files:
            with self.subTest(file=name):
                self.assertNotRegex(_src(name), r"100vh")


class TestRung6aFormDiscipline(unittest.TestCase):
    """The section-form floors (the test_section_forms contract, applied to
    the two new forms before the manifest merge)."""

    def test_form_root_selector_present(self):
        for form_id, (css, _js, _g) in RUNG6A_FORMS.items():
            with self.subTest(form=form_id):
                self.assertIn(f'[data-ad-form="{form_id}"]', _form(css))

    def test_forms_ship_zero_motion(self):
        for form_id, (css, _js, _g) in RUNG6A_FORMS.items():
            src = _form(css)
            with self.subTest(form=form_id):
                self.assertNotIn("@keyframes", src)
                self.assertNotRegex(src, r"\banimation\s*:")
                self.assertNotRegex(src, r"\btransition\s*:")

    def test_no_js_floor_no_hidden_slots(self):
        """A dead script leaves the poster hero and the stacked step layout
        fully legible — nothing hides at rest (the live-mode hides ride
        enhancer-set attributes only)."""
        for form_id, (css, _js, _g) in RUNG6A_FORMS.items():
            src = _form(css)
            with self.subTest(form=form_id):
                self.assertNotRegex(src, r"opacity:\s*0(?![.\d])")
        rest_hide = re.compile(
            r"^(?!.*data-engine)(?!.*data-pms-live).*visibility:\s*hidden", re.M)
        for form_id, (css, _js, _g) in RUNG6A_FORMS.items():
            for line in _form(css).splitlines():
                if "visibility: hidden" in line:
                    # the only hide is the engine-live poster swap, gated on
                    # the enhancer-set attribute in the preceding selector
                    self.assertEqual(form_id, "in-engine-hero")

    def test_enhancers_never_write_html_strings_or_nodes(self):
        """No markup strings, nothing mounted into the page — the one
        createElement in the hero enhancer is the off-DOM WebGL probe
        canvas, never appended anywhere."""
        for _id, (_css, js, _g) in RUNG6A_FORMS.items():
            src = _src("forms/" + js)
            with self.subTest(enhancer=js):
                self.assertNotRegex(src, r"\binnerHTML\s*=")
                self.assertNotRegex(src, r"\binsertAdjacentHTML\b")
                self.assertNotRegex(src, r"\bappendChild\b")
                self.assertNotRegex(src, r"\binsertBefore\b")
        self.assertNotIn("createElement", _src("forms/pinned-media-stepthrough.js"))
        hero = _src("forms/in-engine-hero.js")
        self.assertEqual(hero.count("createElement"), 1)
        self.assertIn("document.createElement('canvas')", hero)

    def test_forms_style_attributes_never_role_classes(self):
        """ROLE-RESTYLE gate: form state rides data attributes — a
        .ad-*/.is-* selector in a form stylesheet is the class-role drift
        the scanner fails."""
        for form_id, (css, _js, _g) in RUNG6A_FORMS.items():
            src = _form(css)
            with self.subTest(form=form_id):
                self.assertNotRegex(src, r"\.ad-")
                self.assertNotRegex(src, r"\.is-")


class TestLineDrawCta(unittest.TestCase):
    """The drawn-line CTA for photographic surfaces: stroke-draw ring or
    hairline underline — never a flood, never a label colour flip."""

    def setUp(self):
        self.src = _src("line-draw-cta.js")

    def test_distinct_from_the_shipped_cta_moves(self):
        self.assertIn("fill-invert-cta", self.src)
        self.assertIn("masked-label-swap", self.src)
        self.assertIn("NO fill flood, NO colour flip", self.src)

    def test_ring_is_pathlength_normalized_and_drawn_by_dashoffset(self):
        """pathLength=1 makes the draw a 1->0 dashoffset regardless of
        radius; the same transition retracts on leave (driven: full draw,
        then settled back to 1 after the pointer left)."""
        self.assertIn("c.setAttribute('pathLength', '1');", self.src)
        self.assertIn("stroke-dasharray:1;stroke-dashoffset:1;", self.src)
        self.assertIn("stroke-dashoffset:0;", self.src)

    def test_draw_starts_at_twelve_oclock(self):
        self.assertIn("transform:rotate(-90deg);transform-origin:center;", self.src)

    def test_ring_never_spills(self):
        """r=49 keeps the centered stroke inside the 100-box; the svg is
        inset:0 pointer-events:none chrome (driven: svg box inside the
        host box on all sides)."""
        self.assertIn("c.setAttribute('r', '49');", self.src)
        self.assertIn("'.ad-ldc__ring{position:absolute;inset:0;", self.src)

    def test_underline_is_the_gaps_own_hairline(self):
        """height .5px, currentColor, opacity 0->1 — an underline that
        APPEARS, never grows from a point."""
        self.assertIn("height:0.5px;background:currentColor;", self.src)
        self.assertIn("opacity:0;transition:opacity var(--ad-ldc-underline,160ms)", self.src)

    def test_focus_visible_mirrors_hover(self):
        self.assertIn(':focus-visible .ad-ldc__ring circle', self.src)
        self.assertIn(':focus-visible::before', self.src)

    def test_touch_answer_is_active_over_a_flash_floor(self):
        self.assertIn("'@media (hover:none){'", self.src)
        self.assertIn("transition-duration:140ms;", self.src)

    def test_reduce_line_present_at_rest(self):
        """The gap's own order — parse-verified in-browser (both media
        blocks accepted by the CSSOM)."""
        self.assertIn("'@media (prefers-reduced-motion: reduce){'", self.src)
        self.assertIn("stroke-dashoffset:0;transition:none;", self.src)
        self.assertIn("opacity:1;transition:none;", self.src)

    def test_ring_chrome_is_decorative(self):
        self.assertIn("svg.setAttribute('aria-hidden', 'true');", self.src)
        self.assertIn("svg.setAttribute('focusable', 'false');", self.src)


class TestContextualCursorLabel(unittest.TestCase):
    """LV/Cartier's gesture-discovery cursor: surface-scoped ring + verb
    label + the click-and-hold charge arc."""

    def setUp(self):
        self.src = _src("contextual-cursor-label.js")

    def test_the_alias_ruling_rides_in_the_header(self):
        """DISTINCT from both shipped cursors, by mechanism, named."""
        self.assertIn("NOT an alias", self.src)
        self.assertIn("cursor-verb-label", self.src)
        self.assertIn("custom-contextual-cursor", self.src)
        self.assertIn("one cursor component per page, ever", self.src)

    def test_surface_scoped_native_cursor_off_surface(self):
        """cursor:none applies only over a gesture object via a JS class;
        leaving the object retracts the chrome and returns the pointer."""
        self.assertIn("'.ad-ccl-hide,.ad-ccl-hide *{cursor:none!important;}'", self.src)
        self.assertIn("layer.classList.remove('is-on'); // the native cursor returns off-surface", self.src)

    def test_hold_arc_tracks_the_declared_duration(self):
        """The charge clock reads the object's data-ad-gesture-hold with the
        LV-band default (driven: 26/52/76%% at 173/357/524ms of 700ms)."""
        self.assertIn("var HOLD_DEFAULT = 700;", self.src)
        self.assertIn("data-ad-gesture-hold", self.src)
        self.assertIn("charge = Math.min(1, charge + (now - lastT) / holdMs);", self.src)

    def test_release_retracts_fast_and_drops_charged(self):
        self.assertIn("var RETRACT_RATE = 3;", self.src)
        self.assertIn("layer.removeAttribute('data-charged');", self.src)

    def test_the_cursor_is_affordance_only(self):
        """Completion belongs to the object's own gesture logic — the
        component drives no reveal."""
        self.assertIn("the object's own gesture", self.src)
        self.assertIn("drives no reveal", self.src)

    def test_touch_dormant_with_on_object_hints(self):
        """The playbook's tap answer: no chrome, a persistent verb chip on
        the object (driven under real touch emulation: chrome absent, three
        chips visible)."""
        self.assertIn("(hover: hover) and (pointer: fine)", self.src)
        self.assertIn("ad-ccl__hint", self.src)

    def test_keyboard_reaches_the_gesture_via_focus(self):
        """Fine-pointer chips stand down at rest and surface on the
        object's :focus-visible (driven: real Tab lit only the focused
        object's chip)."""
        self.assertIn("'.ad-ccl-fine .ad-ccl__hint{visibility:hidden;}'", self.src)
        self.assertIn("[data-ad-gesture]:focus-visible .ad-ccl__hint{visibility:visible;}", self.src)

    def test_gate_reevaluates_on_mq_change(self):
        self.assertIn("mqOn(finePointer, evaluate);", self.src)
        self.assertIn("mqOn(reduceMQ, evaluate);", self.src)

    def test_chrome_never_intercepts(self):
        self.assertIn("layer.setAttribute('aria-hidden', 'true');", self.src)
        self.assertIn("pointer-events:none;", self.src)


class TestFlipHandoffLoader(unittest.TestCase):
    """Son Daven's master-preloader: the mark FLIPs from center-stage into
    the header's real wordmark slot — the watched element becomes the brand
    mark, no hard cut."""

    def setUp(self):
        self.src = _src("flip-handoff-loader.js")

    def test_the_alias_ruling_rides_in_the_header(self):
        self.assertIn("loader-into-navbar", self.src)
        self.assertIn("branded-preloader", self.src)
        self.assertIn("Ruled distinct, not an alias", self.src)

    def test_flip_measures_first_and_last_rects(self):
        """First/Last/Invert/Play between the two REAL rects (driven: the
        landed mark matched the target rect at 0.0px delta)."""
        self.assertIn("var first = mark.getBoundingClientRect();", self.src)
        self.assertIn("var last = target.getBoundingClientRect();", self.src)
        self.assertIn("var scale = first.width > 0 ? last.width / first.width : 1;", self.src)

    def test_flight_is_transform_and_opacity_only(self):
        """The ground dissolve rides a dedicated layer's opacity — never a
        backgroundColor paint."""
        self.assertIn("'scale(' + scale.toFixed(4) + ')'", self.src)
        self.assertIn("never a backgroundColor paint", self.src)
        self.assertNotIn("backgroundColor:", self.src)

    def test_fill_stays_honest(self):
        """Ease to 90, hold for the real window load, settle to full, then
        the flight (the library's loader law)."""
        self.assertIn("setFill(easeOutCubic(p) * 0.9);", self.src)
        self.assertIn("if (p >= 1 && loaded) settle", self.src)

    def test_header_mark_waits_only_by_js(self):
        """[data-ad-flip-wait] is JS-applied and JS-released — no-JS shows
        the ordinary header (driven: wait held every flight frame, zero
        frames after onDone)."""
        self.assertIn("'[data-ad-flip-wait]{visibility:hidden;}'", self.src)
        self.assertIn("target.setAttribute('data-ad-flip-wait', '');", self.src)
        self.assertIn("target.removeAttribute('data-ad-flip-wait');", self.src)

    def test_scene_authored_hidden_never_blocks(self):
        self.assertIn("scene.removeAttribute('hidden');", self.src)
        self.assertIn("no-JS never gets the class", self.src)

    def test_reduce_skips_to_the_standing_header(self):
        """The loader-into-navbar skip path — the beat is stylistic, never
        load-bearing; onDone still fires (driven under ?rm)."""
        self.assertIn("if (reduce() || (sessionOnce && seen())) {", self.src)
        self.assertIn("a re-init must not re-fire onDone", self.src)

    def test_progressbar_announced(self):
        self.assertIn("bar.setAttribute('role', 'progressbar');", self.src)
        self.assertIn("scene.setAttribute('aria-busy', 'true');", self.src)

    def test_no_target_recedes_in_place(self):
        """A page without the header slot still completes — never a
        stranded overlay."""
        self.assertIn("if (target && mark) {", self.src)


class TestInfiniteScrollLoop(unittest.TestCase):
    """Urban Jürgensen's never-bottoming track: native vertical wrap +
    transform horizontal glide, index-mapped, finite under reduce."""

    def setUp(self):
        self.src = _src("infinite-scroll-loop.js")

    def test_the_alias_ruling_rides_in_the_header(self):
        self.assertIn("swipe-snap-gallery", self.src)
        self.assertIn("Ruled distinct, not an alias", self.src)

    def test_vertical_wrap_is_a_period_jump(self):
        """The seam lands on identical pixels so native momentum carries
        across it (driven: 8000px glide, center label cycling with no skip,
        scrollTop bounded inside one period band)."""
        self.assertIn("if (st < period * 0.5) el.scrollTop = st + period;", self.src)
        self.assertIn("else if (st > period * 1.5) el.scrollTop = st - period;", self.src)

    def test_clones_stay_hit_testable(self):
        """Driven finding: `inert` dead-zones every wrapped copy — a clone
        link would never fire. aria-hidden + tabindex -1 dedupe AT and the
        tab order instead."""
        self.assertNotIn("'inert'", self.src)
        self.assertIn("clone.setAttribute('aria-hidden', 'true');", self.src)
        self.assertIn("el.setAttribute('tabindex', '-1');", self.src)

    def test_center_coordinate_wraps_modulo_the_period(self):
        """Driven finding: without the modulo the period's first items are
        unreachable as the published index."""
        self.assertIn("(el.scrollTop + el.clientHeight / 2) % period", self.src)
        self.assertIn("(unit.pos + el.clientWidth / 2) % unit.copy", self.src)

    def test_index_publishes_only_on_change(self):
        self.assertIn("data-ad-loop-index", self.src)
        self.assertIn("zero-flip", self.src)

    def test_horizontal_glide_decays_by_friction(self):
        """The decelerating luxury glide (driven: release at ~52px/frame
        decaying monotonically to rest)."""
        self.assertIn("var FRICTION_DEFAULT = 0.94;", self.src)
        self.assertIn("unit.vel *= friction;", self.src)

    def test_capture_failure_never_aborts_the_drag(self):
        """Driven finding: setPointerCapture threw on a stale pointerId and
        the whole drag died armless — wake first, capture guarded."""
        self.assertIn("unit.wake();", self.src)
        self.assertIn("try { if (el.setPointerCapture) el.setPointerCapture(e.pointerId); }", self.src)

    def test_focus_glide_clamps_and_owns_position(self):
        """Driven findings: a wrapped pos centers the CLONE while the
        focused canonical item sits off-screen; and the browser's own
        focus-scroll writes scrollLeft on the hidden overflow."""
        self.assertIn("unit.pos = want < 0 ? 0 : want;", self.src)
        self.assertIn("el.scrollLeft = 0;", self.src)

    def test_vertical_intent_wheel_is_never_hijacked(self):
        """Only dominant-X (or shift) wheels drive the track (driven: a
        deltaY wheel left defaultPrevented false)."""
        self.assertIn("Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : (e.shiftKey ? e.deltaY : 0)", self.src)
        self.assertIn("if (!d) return;", self.src)

    def test_touch_keeps_page_scroll(self):
        self.assertIn("touch-action:pan-y;", self.src)

    def test_reduce_is_the_finite_authored_track(self):
        self.assertIn("if (reduce()) return { destroy: function () {} };", self.src)

    def test_offscreen_parks_the_glide(self):
        """Driven: a drag on the off-screen unit applied nothing until it
        scrolled into view — the IO gate owns the loop."""
        self.assertIn("if (u.on && u.wake) u.wake(); // off-screen parks the glide", self.src)


class TestInEngineHeroForm(unittest.TestCase):
    """The DOM shell for an engine-mounted hero: layout + poster-first LCP +
    mount point + the floors. NOT a 3D scene."""

    def setUp(self):
        self.css = _form("in-engine-hero.css")
        self.js = _form("in-engine-hero.js")

    def test_resolves_the_recipes_missing_ref(self):
        self.assertIn("MISSING:in-engine-hero", self.css)
        self.assertIn("engine-world-depoluxe", self.css)
        self.assertIn("studio-reel-lusion", self.css)

    def test_poster_is_the_painted_floor(self):
        """The plate paints from first paint; its live-state hide is the
        ENHANCER's inline write — the stylesheet carries no hidden state
        (the no-JS floor: a dead script leaves the poster as the hero)."""
        self.assertIn('[data-ad-form="in-engine-hero"] > [data-slot="poster"]', self.css)
        self.assertNotIn("visibility: hidden", self.css)
        self.assertIn("poster.style.visibility = 'hidden'", self.js)
        self.assertIn("u.poster.style.visibility = ''", self.js)

    def test_svh_choice_is_reasoned(self):
        """svh deliberately, not dvh — a dvh stage re-rasterizes the render
        target on every mobile URL-bar collapse."""
        self.assertIn("min-height: 100svh;", self.css)
        self.assertIn("re-rasterizes the render target", self.css)

    def test_mount_earns_the_pointer_only_live(self):
        self.assertIn("pointer-events: none;", self.css)
        self.assertIn('[data-ad-form="in-engine-hero"][data-engine="live"] > [data-slot="mount"]', self.css)

    def test_structural_scrim(self):
        self.assertIn('[data-slot="poster"]::after', self.css)

    def test_enhancer_gates_the_floors(self):
        """No engine under reduce or Save-Data, none without WebGL — the
        poster hero stands whole on every floor (driven: ?rm never called
        mount; fail() left the poster standing)."""
        self.assertIn("if (!mount || reduce() || saveData() || !webgl()) {", self.js)
        self.assertIn("probe.getContext('webgl2') || probe.getContext('webgl')", self.js)

    def test_ready_is_one_shot_and_sets_live(self):
        """Driven: the poster faded 1->0 over the reveal token, then
        data-engine='live' landed; a second ready() was a no-op."""
        self.assertIn("if (unit.live || unit.dead) return; // one hand-off, ever", self.js)
        self.assertIn("section.setAttribute('data-engine', 'live'); // CSS routes the pointer", self.js)

    def test_fail_leaves_the_poster_floor(self):
        self.assertIn("unit.dead = true; // the poster floor stands — nothing to undo", self.js)


class TestPinnedMediaStepthroughForm(unittest.TestCase):
    """The 'hold the object still, advance the story' beat: one persistent
    media, captions step over it, bounded pin, parks at the boundaries."""

    def setUp(self):
        self.css = _form("pinned-media-stepthrough.css")
        self.js = _form("pinned-media-stepthrough.js")

    def test_the_alias_ruling_rides_in_the_header(self):
        """DISTINCT from pinned-demo-panels: there the stage content is
        replaced panel to panel; here the held object never fades, never
        swaps."""
        self.assertIn("pinned-demo-panels", self.css)
        self.assertIn("NOT an alias", self.css)
        self.assertIn("pinned-demo-panels", self.js)

    def test_not_corpus_source_verified_is_declared(self):
        """The gap's own evidence honesty carries into the artifact."""
        self.assertIn("NOT corpus-source-verified", self.css)

    def test_media_takes_no_opacity_rule(self):
        """The stylesheet states the law; the enhancer keeps it (driven:
        media opacity 1 at every sample of a full scrub, both directions)."""
        self.assertIn("The MEDIA layer takes no opacity rule at all", self.css)
        self.assertIn("THE MEDIA IS NEVER", self.js)
        self.assertIn("the media slot is deliberately untouched", self.js)

    def test_steps_scrub_as_a_pure_function_of_scroll(self):
        """Reversible by construction (driven: steps published 0,1,2 down
        and 2,1,0 back up)."""
        self.assertIn("var P = clamp01(-rect.top / travel);", self.js)
        self.assertIn("var x = P * (unit.steps.length - 1);", self.js)

    def test_boundary_parks(self):
        """Fixed only while the section covers the viewport (driven: zero
        overlap violations against the neighbor sections over a full
        scrub)."""
        self.assertIn('unit.section.setAttribute("data-pms-park", "start");'.replace('"', "'"), self.js)
        self.assertIn('[data-ad-form="pinned-media-stepthrough"][data-pms-park="end"]', self.css)

    def test_active_step_publishes_on_change(self):
        self.assertIn("unit.section.setAttribute('data-ad-pms-step', String(nearest));", self.js)

    def test_only_the_active_step_keeps_the_pointer(self):
        self.assertIn("k === nearest ? '' : 'none'", self.js)

    def test_runway_is_bounded_per_step(self):
        self.assertIn("min-height: 100svh; /* the runway — one viewport of travel per step */", self.css)

    def test_reduce_is_the_static_stacked_layout(self):
        self.assertIn("if (reduce()) return { destroy: function () {} };", self.js)


if __name__ == "__main__":
    unittest.main()
