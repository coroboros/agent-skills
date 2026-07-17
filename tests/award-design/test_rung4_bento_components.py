"""award-design completeness program — rung 4 (bento).

Six builds from the bento playbook's `gaps` plus the two recipes.json MISSING
refs, pinned by filename ahead of the manifest merge: four interaction
components and two SECTION FORMS (both MISSING refs sit in recipe `form`
slots). The strip alias is resolved here: the playbook gap
'divided-capability-strip' names the recipes ref 'MISSING:divided-strip' as
its own — one Endex mechanic under two names, built ONCE as the
divided-capability-strip form. What the tests lock is each build's
LOAD-BEARING distinction: the live tile mounts an OPERABLE canvas demo (the
builder's draw function — never a faked recording) with drive-specific
inputs, a tile-scoped cursor whose cursor:none rides a JS-applied class, and
a poster that stands under reduce; the five machines are structured content
loops (FLIP list, typewriter, overshoot pop with the 3s hold, gapless −50%
stream, staggered focus) gated the ambient-idle way; the spotlight expand is
transform/clip-path only — a 12-point cross morph, the (dim−grow)/dim rest
scale, pre-tap state deciding the touch expand; section-scale momentum morphs
the ground through color-mix custom props and ships the static-end-color
reduce; the pinned panels form pins via enhancer-applied classes with
absolute boundary parks and publishes the per-panel accent; the strip form
ships divide-x with zero motion of its own, the marquee living in the
enhancer as one WAAPI loop over enhancer-owned clones."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
COMPONENTS = REPO_ROOT / "skills" / "award-design" / "assets" / "components"
FORMS = COMPONENTS / "forms"

# interaction component file → the global its IIFE must export
RUNG4_GLOBALS = {
    "live-demo-tile.js": "awardLiveDemoTile",
    "perpetual-tile-machines.js": "awardPerpetualTileMachines",
    "section-scale-momentum.js": "awardSectionScaleMomentum",
    "spotlight-expand-tile.js": "awardSpotlightExpandTile",
}

# form id → (css, enhancer js, enhancer global)
RUNG4_FORMS = {
    "pinned-demo-panels": ("pinned-demo-panels.css", "pinned-demo-panels.js",
                           "awardPinnedDemoPanels"),
    "divided-capability-strip": ("divided-capability-strip.css",
                                 "divided-capability-strip.js",
                                 "awardDividedCapabilityStrip"),
}


def _src(name):
    return (COMPONENTS / name).read_text(encoding="utf-8")


def _form(name):
    return (FORMS / name).read_text(encoding="utf-8")


class TestRung4LibraryContract(unittest.TestCase):
    """The structural contract every library component keeps (the
    test_component_library floor, applied before the manifest merge)."""

    def test_files_exist(self):
        for name in RUNG4_GLOBALS:
            with self.subTest(file=name):
                self.assertTrue((COMPONENTS / name).is_file())
        for form_id, (css, js, _g) in RUNG4_FORMS.items():
            with self.subTest(form=form_id):
                self.assertTrue((FORMS / css).is_file())
                self.assertTrue((FORMS / js).is_file())

    def test_iife_and_global_export(self):
        everything = dict(RUNG4_GLOBALS)
        for _id, (_css, js, g) in RUNG4_FORMS.items():
            everything["forms/" + js] = g
        for name, g in everything.items():
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("(function (global)", src)
                self.assertRegex(src, r"global\." + re.escape(g) + r"\s*=")

    def test_exposes_init_and_destroy(self):
        files = list(RUNG4_GLOBALS) + ["forms/" + js for _c, js, _g in RUNG4_FORMS.values()]
        for name in files:
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("function init", src)
                self.assertIn("destroy", src)

    def test_has_reduced_motion_path(self):
        files = list(RUNG4_GLOBALS) + ["forms/" + js for _c, js, _g in RUNG4_FORMS.values()]
        for name in files:
            with self.subTest(component=name):
                self.assertIn("prefers-reduced-motion", _src(name))

    def test_has_doc_comment_header(self):
        files = (list(RUNG4_GLOBALS)
                 + ["forms/" + js for _c, js, _g in RUNG4_FORMS.values()]
                 + ["forms/" + css for css, _j, _g in RUNG4_FORMS.values()])
        for name in files:
            with self.subTest(file=name):
                self.assertTrue(_src(name).lstrip().startswith("/*"))

    def test_namespaced_stylesheet_injection(self):
        """One namespaced stylesheet per interaction component."""
        for name in RUNG4_GLOBALS:
            with self.subTest(component=name):
                self.assertRegex(_src(name), r"CSS_ID = 'ad-[a-z-]+-css'")

    def test_no_bare_100vh(self):
        """svh/dvh only — a bare 100vh jumps under mobile chrome collapse."""
        files = (list(RUNG4_GLOBALS)
                 + ["forms/" + js for _c, js, _g in RUNG4_FORMS.values()]
                 + ["forms/" + css for css, _j, _g in RUNG4_FORMS.values()])
        for name in files:
            with self.subTest(file=name):
                self.assertNotRegex(_src(name), r"100vh")


class TestRung4FormDiscipline(unittest.TestCase):
    """The section-form floors (the test_section_forms contract, applied to the
    two new forms before the manifest merge)."""

    def test_form_root_selector_present(self):
        for form_id, (css, _js, _g) in RUNG4_FORMS.items():
            with self.subTest(form=form_id):
                self.assertIn(f'[data-ad-form="{form_id}"]', _form(css))

    def test_forms_ship_zero_motion(self):
        """The marquee/cross-fade live in the enhancer — never the stylesheet."""
        for form_id, (css, _js, _g) in RUNG4_FORMS.items():
            src = _form(css)
            with self.subTest(form=form_id):
                self.assertNotIn("@keyframes", src)
                self.assertNotRegex(src, r"\banimation\s*:")
                self.assertNotRegex(src, r"\btransition\s*:")

    def test_no_js_floor_no_hidden_slots(self):
        """A dead script leaves every band legible — nothing hides at rest."""
        for form_id, (css, _js, _g) in RUNG4_FORMS.items():
            src = _form(css)
            with self.subTest(form=form_id):
                self.assertNotRegex(src, r"visibility:\s*hidden")
                self.assertNotRegex(src, r"opacity:\s*0(?![.\d])")

    def test_enhancers_never_write_html_strings(self):
        for form_id, (_css, js, _g) in RUNG4_FORMS.items():
            src = _form(js)
            with self.subTest(form=form_id):
                self.assertNotRegex(src, r"\binnerHTML\s*=")
                self.assertNotRegex(src, r"\binsertAdjacentHTML\b")

    def test_forms_style_attributes_never_role_classes(self):
        """Driven finding (ROLE-RESTYLE gate): live/park/marquee state rides
        data attributes on the form root — a .ad-*/.is-primary selector in a
        form stylesheet is the class-role drift the scanner fails."""
        for form_id, (css, _js, _g) in RUNG4_FORMS.items():
            src = _form(css)
            with self.subTest(form=form_id):
                self.assertNotRegex(src, r"\.ad-")
                self.assertNotRegex(src, r"\.is-")


class TestLiveDemoTile(unittest.TestCase):
    """The #1 bento gap: the tile IS the product demo — an operable canvas the
    BUILDER's draw function renders, drive inputs owned by the component, no
    card chrome, a tile-scoped cursor, and a poster that stands under reduce."""

    def setUp(self):
        self.src = _src("live-demo-tile.js")

    def test_builder_supplies_the_real_demo(self):
        self.assertIn("demos     object            name → draw(ctx, w, h, state)", self.src)
        self.assertIn("never a faked screen recording", self.src)

    def test_four_drives(self):
        for needle in ("'auto'", "'hover'", "'scroll'", "unit.dragging"):
            with self.subTest(drive=needle):
                self.assertIn(needle, self.src)

    def test_scroll_drive_is_a_pure_scroll_function(self):
        self.assertIn("unit.progress = clamp01((vh - r.top) / (vh + r.height));", self.src)

    def test_no_card_chrome_by_contract(self):
        """The tile reacts because the demo reacts — no lift, no shadow."""
        self.assertIn("no chrome by contract", self.src)
        self.assertNotIn("box-shadow", self.src)
        self.assertNotIn("scale(1.0", self.src)

    def test_cursor_none_is_js_applied_and_tile_scoped(self):
        self.assertIn(".ad-ldt-hide,.ad-ldt-hide *{cursor:none!important;}", self.src)
        self.assertIn("classList.add('ad-ldt-hide')", self.src)
        self.assertNotIn("[data-ad-live-demo]{cursor:none", self.src)

    def test_poster_is_the_rest_truth(self):
        """Hidden only under the JS-applied live class; reduce never arms."""
        self.assertIn(".ad-ldt--live [data-demo-poster]{opacity:0;visibility:hidden;}", self.src)
        self.assertIn("if (reduce()) return { destroy: function () {} };", self.src)

    def test_keyboard_operates_the_drag_tile(self):
        self.assertIn("tile.setAttribute('tabindex', '0')", self.src)
        self.assertIn("'ArrowRight'", self.src)

    def test_touch_keeps_the_vertical_pan(self):
        self.assertIn("touch-action:pan-y pinch-zoom", self.src)

    def test_gated_off_screen_and_hidden_tab(self):
        self.assertIn("IntersectionObserver", self.src)
        self.assertIn("visibilitychange", self.src)

    def test_tokens_rerail_under_a_page_recolor(self):
        """Driven finding: a pinned-demo-panels recolor must reach a mounted
        demo — tokens re-resolve on a slow clock, never per frame."""
        self.assertIn("re-resolve at ~2Hz, never per frame", self.src)
        self.assertIn("if (++unit.frames % 30 === 0) tokens();", self.src)

    def test_dpr_capped_canvas(self):
        self.assertIn("Math.min(2, global.devicePixelRatio || 1)", self.src)


class TestPerpetualTileMachines(unittest.TestCase):
    """The five structured content machines, one mode enum — distinct from
    ambient-idle's unstructured glow/float/shimmer/pulse."""

    def setUp(self):
        self.src = _src("perpetual-tile-machines.js")

    def test_the_five_machine_enum(self):
        self.assertIn("list: listMachine, command: commandMachine, status: statusMachine,", self.src)
        self.assertIn("stream: streamMachine, focus: focusMachine", self.src)

    def test_corpus_honesty_a_default_not_a_law(self):
        self.assertIn("a strong default, not award law", self.src)

    def test_list_is_flip_transform_only(self):
        self.assertIn("el.getBoundingClientRect(); // commit the inverted pose", self.src)
        self.assertIn("the new entry arrives at the top", self.src)

    def test_command_pins_the_accessible_name(self):
        self.assertIn("pin the accessible name before the typing mutates the text nodes", self.src)
        self.assertIn("text.setAttribute('aria-label', authored)", self.src)

    def test_status_holds_three_seconds_on_an_overshoot_spring(self):
        self.assertIn("var HOLD_MS = 3000; // the verified status hold", self.src)
        self.assertIn("cubic-bezier(.34,1.56,.64,1)", self.src)

    def test_stream_wraps_gapless_at_minus_half(self):
        self.assertIn("@keyframes ad-ptm-stream{to{transform:translate3d(-50%,0,0);}}", self.src)
        self.assertIn("linear infinite", self.src)
        self.assertIn("data-ad-ptm-clone", self.src)

    def test_animations_authored_paused_and_io_gated(self):
        """The ambient-idle gating pattern: paused by default, is-running by
        observer, a hidden tab outranks everything."""
        self.assertIn("infinite paused", self.src)
        self.assertIn("is-running", self.src)
        self.assertIn("IntersectionObserver", self.src)
        self.assertIn("visibilitychange", self.src)

    def test_rest_dom_is_never_hidden_by_stylesheet(self):
        """Hides are machine-start writes (JS), so reduce/no-JS keeps the
        authored chip and toolbar visible."""
        self.assertIn("JS-applied — the rest DOM keeps the chip visible", self.src)
        self.assertIn("JS-applied — rest keeps the toolbar visible", self.src)

    def test_reduce_nothing_starts(self):
        self.assertIn("// Reduced motion: no machine ever starts — the authored tile stands.", self.src)


class TestSectionScaleMomentum(unittest.TestCase):
    """Sui's two section-scale channels: the scroll-driven ground morph and
    the footer as a live surface."""

    def setUp(self):
        self.src = _src("section-scale-momentum.js")

    def test_ground_morph_rides_color_mix_props(self):
        self.assertIn("color-mix(in oklab,", self.src)
        self.assertIn("--ad-ssm-from", self.src)
        self.assertIn("--ad-ssm-to", self.src)
        self.assertIn("--ad-ssm-p", self.src)

    def test_morph_is_a_pure_scroll_function(self):
        self.assertIn("var center = global.pageYOffset + global.innerHeight / 2;", self.src)

    def test_footer_glow_is_presentation_only_and_promoted(self):
        self.assertIn("glow.setAttribute('aria-hidden', 'true');", self.src)
        self.assertIn("pointer-events:none", self.src)
        self.assertIn("transform:translateZ(0)", self.src)

    def test_arrival_scrub_is_reversible(self):
        self.assertIn("identity at fully-in-view, reversible on the way out", self.src)

    def test_raf_self_parks_when_settled(self):
        self.assertIn("if (scrolled || !settled) raf = global.requestAnimationFrame(frame);", self.src)

    def test_reduce_is_the_static_end_color(self):
        self.assertIn("each declaring section takes its", self.src)
        self.assertIn("sec.style.backgroundColor = sec.getAttribute('data-ad-ssm-bg');", self.src)

    def test_gated_off_screen_and_hidden_tab(self):
        self.assertIn("IntersectionObserver", self.src)
        self.assertIn("visibilitychange", self.src)


class TestSpotlightExpandTile(unittest.TestCase):
    """The layout-AWARE expand that never reflows layout: 12-point clip cross,
    (dim−grow)/dim rest scale, row-aware yields, pre-tap touch decision."""

    def setUp(self):
        self.src = _src("spotlight-expand-tile.js")

    def test_twelve_point_cross_morph(self):
        """Equal point counts keep the morph interpolable; the open state's arm
        reaches the layer edges."""
        self.assertEqual(self.src.count("polygon("), 2)
        self.assertIn("'100% 70%,calc(100% - var(--_arm)) 70%,'", self.src)
        self.assertIn("Equal point counts keep the morph interpolable", self.src)

    def test_rest_scale_is_the_verified_ratio(self):
        self.assertIn("resting preview = (dim − grow)/dim", self.src)
        self.assertIn("media.style.setProperty('--_ps', (tileW / mediaW).toFixed(4));", self.src)

    def test_expansion_is_composited_never_layout(self):
        """Oversized media layer sized once; only transform/clip-path/filter
        move — the grid never reflows."""
        self.assertIn("a static layout fact, never animated", self.src)
        self.assertIn("transition:clip-path", self.src)
        self.assertNotIn("grid-template-columns", self.src)

    def test_rows_are_measured_not_assumed(self):
        self.assertIn("Math.round(t.offsetTop / 8) * 8", self.src)

    def test_siblings_yield_by_side(self):
        self.assertIn("is-yield-l", self.src)
        self.assertIn("is-yield-r", self.src)
        self.assertIn("calc(var(--_grow,5vw)/-2)", self.src)

    def test_desaturation_is_fine_pointer_only(self):
        """Coarse keeps the complete color surface — pointer vocabulary
        dormant, the archetype's mobile answer."""
        self.assertIn("@media (hover:hover) and (pointer:fine){", self.src)

    def test_touch_decision_reads_the_pre_tap_state(self):
        """Driven finding: the tap's own focusin spots the tile before click
        fires — the first-tap-expands rule must read pointerdown state."""
        self.assertIn("reads the PRE-tap state (pointerdown)", self.src)
        self.assertIn("unit.tapArmed = !!tile && unit.active === tile;", self.src)
        self.assertIn("keyboard activation — Enter on a focused link navigates", self.src)

    def test_keyboard_focus_expands_escape_collapses(self):
        self.assertIn("'focusin'", self.src)
        self.assertIn("e.key === 'Escape'", self.src)

    def test_reduce_stands_aside_completely(self):
        self.assertIn("full color,", self.src)
        self.assertIn("if (reduce()) return { destroy: function () {} };", self.src)

    def test_one_tile_cannot_expand(self):
        self.assertIn("if (tiles.length < 2) return; // one tile has no row to expand across", self.src)


class TestPinnedDemoPanelsForm(unittest.TestCase):
    """The specimen-tour peak as a section form: native-scroll scrub over
    enhancer-pinned layers, absolute boundary parks, per-panel accent."""

    def setUp(self):
        self.css = _form("pinned-demo-panels.css")
        self.js = _form("pinned-demo-panels.js")

    def test_resolves_the_recipes_missing_ref(self):
        self.assertIn("already flagged MISSING:pinned-demo-panels in recipes.json", self.css)

    def test_native_scroll_no_smoother(self):
        self.assertIn("NATIVE scroll only", self.js)

    def test_live_mode_is_enhancer_applied(self):
        """A dead script never gets the pinned layout — stacked panels stand;
        the state is an attribute on the form root, never a role class."""
        self.assertIn("enhancer-applied data-pdp-live; a dead script never gets", self.css)
        self.assertIn("section.setAttribute('data-pdp-live', '');", self.js)

    def test_crossfade_is_a_pure_scroll_function(self):
        self.assertIn("var P = clamp01(-rect.top / travel);", self.js)
        self.assertIn("var o = clamp01(1 - Math.abs(x - k) * fade);", self.js)

    def test_boundary_parks_swap_fixed_for_absolute(self):
        """The clip/overlay law: the pinned layer never paints over the
        neighboring sections."""
        self.assertIn('[data-pdp-park="start"]', self.css)
        self.assertIn('[data-pdp-park="end"]', self.css)
        self.assertIn("rect.top > 0", self.js)
        self.assertIn("rect.bottom < vh", self.js)

    def test_only_the_active_demo_stays_operable(self):
        self.assertIn("only the active demo stays operable — the peak keeps replaying", self.js)

    def test_publishes_the_panel_accent_page_wide(self):
        self.assertIn("data-panel-accent", self.js)
        self.assertIn("setProperty('--ad-pdp-accent', accent)", self.js)

    def test_layering_law_no_created_nodes(self):
        self.assertIn("toggles state ATTRIBUTES on the form root", self.js)
        self.assertNotIn("createElement", self.js)

    def test_reduce_is_the_stacked_rest_state(self):
        self.assertIn("// Reduced motion: stacked static panels — the rest state IS the section.", self.js)

    def test_one_panel_cannot_crossfade(self):
        self.assertIn("if (panels.length < 2) return; // one panel has nothing to cross-fade", self.js)


class TestDividedCapabilityStripForm(unittest.TestCase):
    """Endex's divide-x strip — ONE build answering both names (the playbook's
    divided-capability-strip and the recipes ref MISSING:divided-strip)."""

    def setUp(self):
        self.css = _form("divided-capability-strip.css")
        self.js = _form("divided-capability-strip.js")

    def test_the_alias_is_documented_in_the_form(self):
        self.assertIn("MISSING:divided-", self.css)
        self.assertIn("ONE mechanic", self.css)

    def test_divide_x_is_between_cells_only(self):
        self.assertIn("[data-cell] + [data-cell]", self.css)
        self.assertIn("a hairline BETWEEN cells, never around the strip", self.css)

    def test_distinct_from_stat_band_and_logo_wall(self):
        self.assertIn("no big numbers", self.css)
        self.assertIn("words, not logos", self.css)

    def test_mobile_static_answer_is_a_native_pan(self):
        self.assertIn("overflow-x: auto", self.css)

    def test_marquee_is_waapi_in_the_enhancer(self):
        self.assertIn("unit.cells.animate(", self.js)
        self.assertIn("iterations: Infinity, easing: 'linear'", self.js)
        self.assertIn("{ transform: 'translate3d(-50%,0,0)' }", self.js)

    def test_tempo_is_constant_px_per_second(self):
        self.assertIn("duration: (half / speed) * 1000", self.js)

    def test_clones_are_enhancer_owned_and_marked(self):
        self.assertIn("data-ad-dcs-clone", self.js)
        self.assertIn("setAttribute('aria-hidden', 'true')", self.js)

    def test_desktop_stands_aside(self):
        self.assertIn("Desktop is untouched", self.js)
        self.assertIn("var MOBILE_MQ = '(max-width: 768px)';", self.js)

    def test_gated_off_screen_and_hidden_tab(self):
        self.assertIn("IntersectionObserver", self.js)
        self.assertIn("visibilitychange", self.js)

    def test_reduce_keeps_the_pannable_strip(self):
        self.assertIn("// Reduced motion: the static pannable strip is the complete mobile answer.", self.js)


if __name__ == "__main__":
    unittest.main()
