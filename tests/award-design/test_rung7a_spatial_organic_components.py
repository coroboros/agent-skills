"""award-design completeness program — rung 7A (spatial-organic, first half).

Six builds: four shipped as components (ambient-orb-field, diegetic-nav,
horizontal-scroll-chain, liquid-glass-refraction) and two as SECTION FORMS
(in-engine-hud-fold — the MISSING in-engine-fold form of
engine-world-igloo-scrubbed; marquee-hero — the MISSING fold form of
studio-reel-cyd). MISSING refs resolved: in-engine-hud-fold and
marquee-hero. Alias rulings on evidence, written into each header:
marquee-hero is a FORM, DISTINCT from hero-masthead (cannot express the
strip, the blob mount, or the retimed sticker — the recipe's own
annotation), divided-capability-strip (mid-page band, marquee only under
768px) and continuous-idle-carry (time-driven décor channel — the Cyd
strip is scroll-WELDED and IS the fold); horizontal-scroll-chain is
DISTINCT from infinite-scroll-loop (drag/wheel carousel recycling modulo a
copy width vs a finite sticky-pinned track welded to consumed page
scroll), pinned-filmstrip (native grab row, no pin) and swipe-snap-gallery
(the chain's own touch floor, not its mechanic); in-engine-hud-fold is a
DISTINCT form sharing in-engine-hero's stage LAW (poster-first LCP + the
mount gate, mirrored with its own guard — the hero enhancer holds one
handle per root); ambient-orb-field and liquid-glass-refraction are
pre-ruled by their gaps (ambient-idle cannot compose the multi-orb layer;
glass-card ships frost, no displacement — and stays the declared floor).
What the tests lock is each build's LOAD-BEARING driven distinction: the
orb field drifts at rest (orb 0 translate 24.6->31.6px over 1.2s) and
leans per-depth to the pointer (-43.7/+30.6/-19.7px at the three rates),
dormant on touch and static under reduce; the diegetic nav never
intercepts a click (driven: anchor -> #abyss at top), publishes
aria-current zero-flip (0->1->3 down, ->0 back), and its avatar drag maps
1:1 onto document scroll (rail .8/.5/.2 -> y 2046/1279/512 exact); the
chain's translateX is a pure function of consumed scroll (y-810 ==
-translateX at every station, identical both directions, sticky pin held,
release at both ends) with the native swipe-snap touch/reduce floor; the
refraction's displacement is READ in a still frame at the 0.16 default
(0.055 tested imperceptible — beams kink at the rim) with the frost floor
on ?coarse; the HUD fold's poster stood at opacity 1 from t=59ms then
faded to data-engine='live' (under ?rm the mount never fires); the
marquee fold's strip drifts -105/-245/-420px at y 300/700/1200 reversing
exactly, the badge lands at rotate(-8deg) scale(1), the retimed badge
rides 7->-15deg / 0->-26px, page overflow-x 0 (grid blowout drive-caught
and pinned in the CSS)."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
COMPONENTS = REPO_ROOT / "skills" / "award-design" / "assets" / "components"
FORMS = COMPONENTS / "forms"

# interaction component file → the global its IIFE must export
RUNG7A_GLOBALS = {
    "ambient-orb-field.js": "awardAmbientOrbField",
    "diegetic-nav.js": "awardDiegeticNav",
    "horizontal-scroll-chain.js": "awardHorizontalScrollChain",
    "liquid-glass-refraction.js": "awardLiquidGlassRefraction",
}

# form id → (css, enhancer js, enhancer global)
RUNG7A_FORMS = {
    "in-engine-hud-fold": ("in-engine-hud-fold.css", "in-engine-hud-fold.js",
                           "awardInEngineHudFold"),
    "marquee-hero": ("marquee-hero.css", "marquee-hero.js", "awardMarqueeHero"),
}


def _src(name):
    return (COMPONENTS / name).read_text(encoding="utf-8")


def _form(name):
    return (FORMS / name).read_text(encoding="utf-8")


class TestRung7aLibraryContract(unittest.TestCase):
    """The structural contract every library component keeps (the
    test_component_library floor, applied before the manifest merge)."""

    def test_files_exist(self):
        for name in RUNG7A_GLOBALS:
            with self.subTest(file=name):
                self.assertTrue((COMPONENTS / name).is_file())
        for form_id, (css, js, _g) in RUNG7A_FORMS.items():
            with self.subTest(form=form_id):
                self.assertTrue((FORMS / css).is_file())
                self.assertTrue((FORMS / js).is_file())

    def test_iife_and_global_export(self):
        everything = dict(RUNG7A_GLOBALS)
        for _id, (_css, js, g) in RUNG7A_FORMS.items():
            everything["forms/" + js] = g
        for name, g in everything.items():
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("(function (global)", src)
                self.assertRegex(src, r"global\." + re.escape(g) + r"\s*=")

    def test_exposes_init_and_destroy(self):
        files = list(RUNG7A_GLOBALS) + ["forms/" + js for _c, js, _g in RUNG7A_FORMS.values()]
        for name in files:
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("function init", src)
                self.assertIn("destroy", src)

    def test_has_reduced_motion_path(self):
        files = list(RUNG7A_GLOBALS) + ["forms/" + js for _c, js, _g in RUNG7A_FORMS.values()]
        for name in files:
            with self.subTest(component=name):
                self.assertIn("prefers-reduced-motion", _src(name))

    def test_has_doc_comment_header(self):
        files = (list(RUNG7A_GLOBALS)
                 + ["forms/" + js for _c, js, _g in RUNG7A_FORMS.values()]
                 + ["forms/" + css for css, _j, _g in RUNG7A_FORMS.values()])
        for name in files:
            with self.subTest(file=name):
                self.assertTrue(_src(name).lstrip().startswith("/*"))

    def test_namespaced_stylesheet_injection(self):
        """One namespaced stylesheet per interaction component. The form
        enhancers inject nothing — their states live in the linked CSS."""
        for name in RUNG7A_GLOBALS:
            with self.subTest(component=name):
                self.assertRegex(_src(name), r"CSS_ID = 'ad-[a-z-]+-css'")
        for _id, (_css, js, _g) in RUNG7A_FORMS.items():
            with self.subTest(form=_id):
                self.assertNotIn("createElement('style')", _src("forms/" + js))

    def test_form_enhancers_create_no_nodes(self):
        """The layering law: a form enhancer toggles attributes/styles on
        slot elements only (the hud-fold's WebGL probe canvas is created
        but never appended)."""
        for _id, (_css, js, _g) in RUNG7A_FORMS.items():
            src = _src("forms/" + js)
            with self.subTest(form=_id):
                self.assertNotRegex(src, r"\bappendChild\b")
                self.assertNotRegex(src, r"\binnerHTML\s*=")
                self.assertNotRegex(src, r"\binsertAdjacentHTML\b")

    def test_no_bare_100vh(self):
        """svh/lvh/dvh only — a bare 100vh jumps under mobile chrome
        collapse."""
        files = (list(RUNG7A_GLOBALS)
                 + ["forms/" + js for _c, js, _g in RUNG7A_FORMS.values()]
                 + ["forms/" + css for css, _j, _g in RUNG7A_FORMS.values()])
        for name in files:
            with self.subTest(file=name):
                self.assertNotRegex(_src(name), r"100vh")


class TestRung7aFormDiscipline(unittest.TestCase):
    """The section-form floors (the test_section_forms contract, applied to
    both rung-7A forms before the manifest merge)."""

    def test_form_root_selector_present(self):
        for form_id, (css, _js, _g) in RUNG7A_FORMS.items():
            with self.subTest(form=form_id):
                self.assertIn('[data-ad-form="' + form_id + '"]', _form(css))

    def test_form_ships_zero_motion(self):
        for form_id, (css, _js, _g) in RUNG7A_FORMS.items():
            src = _form(css)
            with self.subTest(form=form_id):
                self.assertNotIn("@keyframes", src)
                self.assertNotRegex(src, r"\banimation\s*:")
                self.assertNotRegex(src, r"\btransition\s*:")

    def test_no_js_floor_no_hidden_states(self):
        """A dead script leaves both folds fully legible — no stylesheet
        ever hides a slot (the poster's live-state hide is the enhancer's
        inline write)."""
        for form_id, (css, _js, _g) in RUNG7A_FORMS.items():
            src = _form(css)
            with self.subTest(form=form_id):
                self.assertNotRegex(src, r"opacity:\s*0(?![.\d])")
                self.assertNotIn("visibility: hidden", src)
                self.assertNotIn("display: none", src)

    def test_form_styles_attributes_never_role_classes(self):
        """class-role uniformity rule: form state rides data attributes — a
        .ad-*/.is-* selector in a form stylesheet is class-role drift."""
        for form_id, (css, _js, _g) in RUNG7A_FORMS.items():
            src = _form(css)
            with self.subTest(form=form_id):
                self.assertNotRegex(src, r"\.ad-")
                self.assertNotRegex(src, r"\.is-")

    def test_svh_stage_never_dvh(self):
        """The shared stage law: svh deliberately (dvh re-rasterizes an
        engine target on mobile URL-bar collapse); the marquee fold keeps
        the same floor."""
        for form_id, (css, _js, _g) in RUNG7A_FORMS.items():
            with self.subTest(form=form_id):
                self.assertIn("min-height: 100svh", _form(css))


class TestAmbientOrbField(unittest.TestCase):
    """The WebGL-free living ground: 2-3 blurred OKLCH orbs drifting on
    their own clocks, a soft per-depth pointer lean on fine pointers."""

    def setUp(self):
        self.src = _src("ambient-orb-field.js")

    def test_the_alias_ruling_rides_in_the_header(self):
        self.assertIn("Ruled DISTINCT", self.src)
        self.assertIn("ambient-idle", self.src)
        self.assertIn("shader-surface", self.src)
        self.assertIn("WebGL-free", self.src)

    def test_the_gap_spec_numbers(self):
        """blur(80px), low opacities .15-.25, 15-25s alternate cycles,
        translate a few vw + scale to 1.1 — the gap's own contract."""
        self.assertIn("filter:blur(80px)", self.src)
        for o in ("0.22", "0.18", "0.15"):
            self.assertIn("opacity: " + o, self.src)
        self.assertIn("'ad-orb-a 17s'", self.src)
        self.assertIn("'ad-orb-b 23s'", self.src)
        self.assertIn("animation-direction:alternate;", self.src)
        self.assertIn("scale(1.1)", self.src)

    def test_compositor_only_and_gated(self):
        """Authored paused; IO flips is-drifting per layer; a hidden tab
        re-pauses everything (driven: drifting=false off the gates)."""
        self.assertIn("animation-play-state:paused", self.src)
        self.assertIn("is-drifting", self.src)
        self.assertIn("IntersectionObserver", self.src)
        self.assertIn("visibilitychange", self.src)

    def test_pointer_lean_is_fine_pointer_only_and_lerped(self):
        """Driven: -43.7/+30.6/-19.7px at the three depth rates toward a
        bottom-left pointer; dormant on touch."""
        self.assertIn("(hover: hover) and (pointer: fine)", self.src)
        self.assertIn("orb.tx = nx * amplitude * orb.rate;", self.src)
        self.assertIn("var LERP = 0.06;", self.src)

    def test_reduce_is_the_composed_static_field(self):
        """Driven under ?rm: transforms frozen at rest, no drift class, no
        pointer channel — the field still stands."""
        self.assertIn("'@media (prefers-reduced-motion: reduce){'", self.src)
        self.assertIn(".ad-orbfield__i{animation:none;will-change:auto;}", self.src)


class TestDiegeticNav(unittest.TestCase):
    """OceanX's steering rail: an in-world object moves the visit along a
    path — and the element never stops being a real nav."""

    def setUp(self):
        self.src = _src("diegetic-nav.js")

    def test_the_winner_evidence_rides_in_the_header(self):
        self.assertIn("OceanX 2025", self.src)
        self.assertIn("Fluid Glass", self.src)
        self.assertIn("Unusual Navigation", self.src)

    def test_it_stays_a_nav_no_click_interception(self):
        """Driven: a real click on a stop navigated to #abyss natively —
        the component binds no click handler anywhere."""
        self.assertNotIn("addEventListener('click'", self.src)
        self.assertNotIn("preventDefault", self.src.split("var onDown")[0])

    def test_publish_is_zero_flip_aria_current(self):
        """Driven: 0->1->3 down, ->0 back; a pure accumulator of scroll,
        attributes written only on change."""
        self.assertIn("if (idx !== u.active) {", self.src)
        self.assertIn("u.stops[idx].setAttribute('aria-current', 'true');", self.src)
        self.assertIn("data-ad-dnav-active", self.src)

    def test_drag_scrubs_the_document_one_to_one(self):
        """Driven: rail fractions .8/.5/.2 -> y 2046/1279/512, exact, both
        directions at any point (the free-scroll timeline)."""
        self.assertIn("u.avatar.setPointerCapture(e.pointerId);", self.src)
        self.assertIn("global.scrollTo(0, p * docMax());", self.src)

    def test_steering_is_fine_pointer_only(self):
        """Driven under touch emulation: is-steerable absent, the SAME rail
        reads as anchored nav + progress (fill .248 kept tracking)."""
        self.assertIn("if (finePointer() && !still) {", self.src)
        self.assertIn("is-steerable", self.src)

    def test_reduce_keeps_the_indicator_instant(self):
        """Driven under ?rm: avatar snapped without glide (243.27px =
        .3801 x rail), no steering channel."""
        self.assertIn("if (still) u.x = u.tx;", self.src)

    def test_measures_recover_from_late_loads(self):
        """Drive-caught: plates finishing after init moved the section
        anchors — one settled re-measure on window load."""
        self.assertIn("global.addEventListener('load', onResize, { once: true });", self.src)


class TestHorizontalScrollChain(unittest.TestCase):
    """The chained lateral macrostructure: consumed vertical scroll becomes
    lateral travel, 1:1, reversible, never a hijack."""

    def setUp(self):
        self.src = _src("horizontal-scroll-chain.js")

    def test_the_alias_ruling_rides_in_the_header(self):
        self.assertIn("Ruled DISTINCT", self.src)
        self.assertIn("infinite-scroll-loop", self.src)
        self.assertIn("pinned-filmstrip", self.src)
        self.assertIn("swipe-snap-gallery", self.src)
        self.assertIn("Horizontal", self.src)

    def test_the_pin_is_sticky_under_clip_never_hidden(self):
        """overflow hidden makes a scroll container and kills the pin —
        driven: stickyTop held 0 through the whole 4320px run."""
        self.assertIn("position:sticky", self.src)
        self.assertIn("overflow:clip", self.src)
        self.assertIn("clip, not hidden: hidden creates a scroll container and breaks sticky",
                      self.src)

    def test_translate_is_a_pure_function_of_consumed_scroll(self):
        """ease:none — driven: y-810 == -translateX at every quarter
        station, identical values down and back up."""
        self.assertIn("ease:none", self.src)
        self.assertIn(
            "var p = Math.min(1, Math.max(0, (global.scrollY - u.top) / u.travel));", self.src)
        self.assertIn("var x = -(p * u.travel);", self.src)

    def test_consumed_distance_equals_travel(self):
        """Section height = travel + one viewport, so consumed vertical px
        equal lateral px 1:1 (driven: 4320 travel -> 5220px section)."""
        self.assertIn("u.el.style.height = (u.travel + global.innerHeight) + 'px';", self.src)

    def test_wayfinding_publish_is_discrete(self):
        """Driven: panel 0->1->2->3 down and back — a write on change
        only."""
        self.assertIn("if (idx !== u.panel) {", self.src)
        self.assertIn("data-ad-hchain-panel", self.src)

    def test_touch_and_reduce_get_the_native_swipe_snap_floor(self):
        """The gap's own degrade — driven under touch emulation: snap x
        mandatory, page scroll free mid-pan (vertical intent escapes)."""
        self.assertIn("if (reduce() || coarse())", self.src)
        self.assertIn("ad-hchain--swipe", self.src)
        self.assertIn("scroll-snap-type:x mandatory", self.src)
        self.assertIn("touch-action:pan-x pan-y", self.src)

    def test_offscreen_and_hidden_tabs_park_the_chain(self):
        self.assertIn("IntersectionObserver", self.src)
        self.assertIn("visibilitychange", self.src)

    def test_measures_recover_from_late_loads(self):
        self.assertIn("global.addEventListener('load', onResize, { once: true });", self.src)


class TestLiquidGlassRefraction(unittest.TestCase):
    """The refraction end of the glass register: a displacement lens that
    visibly bends the backdrop, over the Doppelrand shell."""

    def setUp(self):
        self.src = _src("liquid-glass-refraction.js")

    def test_the_alias_ruling_rides_in_the_header(self):
        """glass-card is the frost END and the declared floor — never an
        alias, never co-inited on the same element."""
        self.assertIn("Ruled DISTINCT", self.src)
        self.assertIn("glass-card", self.src)

    def test_genuine_displacement_never_just_blur(self):
        """An feDisplacementMap lens through backdrop-filter:url() — driven
        over a real night plate: the laser beams kink and S-bend inside
        the pane and break at the rim."""
        self.assertIn("'feDisplacementMap'", self.src)
        self.assertIn("'primitiveUnits', 'objectBoundingBox'", self.src)
        self.assertIn("mix-blend-mode:screen", self.src)

    def test_the_default_strength_is_the_visible_bend_floor(self):
        """Drive-verified: 0.055 imperceptible at a glance, 0.16 reads in a
        still frame."""
        self.assertIn("var strength = opts.strength != null ? opts.strength : 0.16;", self.src)

    def test_doppelrand_shell_concentric_radii(self):
        """Outer hairline at 22px, inner core inset highlight at 18px —
        outer minus the 4px inset (the glass-card rule, restated)."""
        self.assertIn("border-radius:22px", self.src)
        self.assertIn("inset:4px;border-radius:18px", self.src)

    def test_the_floors_route_to_frost(self):
        """Fine-pointer/high-power only (the gap's order) — driven:
        ?coarse landed ad-lgr--frost, no defs, blur(24px) saturate(1.2);
        no backdrop-filter at all raises the ground mix."""
        self.assertIn("supportsRefraction() && finePointer() && !saveData()", self.src)
        self.assertIn("ad-lgr--frost", self.src)
        self.assertIn("blur(24px) saturate(1.2)", self.src)
        self.assertIn("' 82%,transparent);}}'", self.src)

    def test_still_material_no_perframe_work(self):
        """No rAF, no scroll listener, no pointer tracking — the refraction
        is a material, not a motion channel."""
        self.assertNotIn("requestAnimationFrame", self.src)
        self.assertNotIn("addEventListener('scroll'", self.src)
        self.assertNotIn("pointermove", self.src)


class TestInEngineHudFold(unittest.TestCase):
    """Igloo's HUD fold: corner chrome over a live scene, no CTA, no h1,
    no loader boundary — the shared stage law under its own guard."""

    def setUp(self):
        self.css = _form("in-engine-hud-fold.css")
        self.js = _form("in-engine-hud-fold.js")

    def test_resolves_the_recipes_missing_ref(self):
        self.assertIn("MISSING:in-engine-hud-fold", self.css)
        self.assertIn("engine-world-igloo-scrubbed", self.css)

    def test_the_alias_ruling_rides_in_the_header(self):
        """DISTINCT from in-engine-hero (the editorial engine hero) — the
        stage LAW is shared, the identity is not."""
        self.assertIn("in-engine-hero", self.css)
        self.assertIn("DISTINCT", self.css)

    def test_the_corner_grammar_no_cta_no_h1(self):
        """Driven: wordmark TL, sound TR, mission BL, cue bottom-centre,
        graph BR — at 51/45px insets; and no h1/CTA slot exists."""
        for slot in ("wordmark", "sound", "mission", "cue", "graph"):
            self.assertIn('[data-slot="' + slot + '"]', self.css)
        self.assertNotIn('[data-slot="h1"]', self.css)
        self.assertNotIn('[data-slot="cta"]', self.css)

    def test_hud_chrome_is_monospace(self):
        self.assertIn("--ad-font-mono", self.css)

    def test_stage_layers_and_the_pointer_gate(self):
        """Poster under mount under chrome; the mount earns the pointer
        only live (driven: none -> auto on data-engine='live')."""
        self.assertIn('[data-slot="mount"]', self.css)
        self.assertIn("pointer-events: none", self.css)
        self.assertIn('[data-engine="live"]', self.css)
        self.assertIn("pointer-events: auto", self.css)

    def test_enhancer_floors_mirror_the_shared_gate_law(self):
        """Reduce / Save-Data / no WebGL -> the poster fold stands (driven
        under ?rm: no canvas, no data-engine, poster at opacity 1)."""
        self.assertIn("if (!mount || reduce() || saveData() || !webgl()) {", self.js)

    def test_the_live_hide_is_an_inline_write(self):
        """Driven fold sequence: poster 1.00 from t=59ms, decelerating
        fade, then the enhancer's inline visibility write — never a
        stylesheet state."""
        self.assertIn("poster.style.visibility = 'hidden';", self.js)
        self.assertIn("section.setAttribute('data-engine', 'live');", self.js)

    def test_own_guard_never_the_heros(self):
        """The hero enhancer holds one handle per root — a page carrying
        both forms needs both enhancers, so the guard key is its own."""
        self.assertIn("__adInEngineHudFold", self.js)
        self.assertNotIn("__adInEngineHero", self.js)


class TestMarqueeHero(unittest.TestCase):
    """Cyd's warm-organic fold: the overflowing wordmark strip as scroll
    texture, the portrait on the accent blob, the sticker pair."""

    def setUp(self):
        self.css = _form("marquee-hero.css")
        self.js = _form("marquee-hero.js")

    def test_resolves_the_recipes_missing_ref(self):
        self.assertIn("MISSING:marquee-hero", self.css)
        self.assertIn("studio-reel-cyd", self.css)

    def test_the_alias_ruling_rides_in_the_header(self):
        self.assertIn("DISTINCT", self.css)
        self.assertIn("hero-masthead", self.css)
        self.assertIn("divided-capability-strip", self.css)
        self.assertIn("continuous-idle-carry", self.css)

    def test_grid_blowout_is_pinned(self):
        """Drive-caught: a max-content strip sized the twelve fr tracks to
        6000px — width 0 / min-width 100% keeps the glyphs painting past
        the box while the fold's clip owns them (page overflow-x driven
        0)."""
        self.assertIn("width: 0;", self.css)
        self.assertIn("min-width: 100%;", self.css)
        self.assertIn("overflow: clip", self.css)
        self.assertNotIn("width: max-content", self.css)

    def test_portrait_rides_the_accent_blob(self):
        """The winner's periwinkle shape, read from the build's own accent
        token — organic border-radius on both the shape and the plate."""
        self.assertIn('[data-slot="portrait"]::before', self.css)
        self.assertIn("var(--ad-accent", self.css)
        self.assertIn("62% 38% 54% 46% / 46% 56% 44% 54%", self.css)

    def test_no_filled_fold_cta(self):
        """The winner's order: a scroll cue or email link only."""
        self.assertNotIn('[data-slot="cta"]', self.css)
        self.assertIn('[data-slot="cue"]', self.css)

    def test_strip_drift_is_a_pure_clamped_function_of_scroll(self):
        """Driven: -105/-245/-420px at y 300/700/1200 (rate .35), identical
        back up; clamped so the far edge never enters the viewport."""
        self.assertIn("var x = Math.min(global.scrollY * rate, u.max);", self.js)
        self.assertIn("u.max = Math.max(0, u.strip.scrollWidth - u.section.clientWidth);", self.js)

    def test_badge_entrance_is_the_winners_timing(self):
        """.4s at .2s delay on the bouncy ease, WAAPI fill:backwards so a
        dead script leaves the badge standing (driven: landed at
        rotate(-8deg) scale(1))."""
        self.assertIn("duration: 400, delay: 200, easing: BOUNCE, fill: 'backwards'", self.js)
        self.assertIn("cubic-bezier(.34,1.56,.64,1)", self.js)

    def test_retimed_badge_rides_inline_var_writes(self):
        """The animation-timeline idiom as enhancer var writes (driven:
        tilt 7 -> -15deg, shift 0 -> -26px, reversing exactly); the CSS
        composes them in its resting transform."""
        self.assertIn("data-retime", self.js)
        self.assertIn("--ad-mh-badge-tilt", self.js)
        self.assertIn("--ad-mh-badge-tilt", self.css)
        self.assertIn("--ad-mh-badge-shift", self.css)

    def test_reduce_is_the_authored_fold(self):
        """Driven under ?rm: no live attr, no drift, no entrance, no var
        writes — every slot visible at rest."""
        self.assertIn("if (reduce()) return { destroy: function () {} };", self.js)

    def test_measures_recover_from_late_fonts(self):
        self.assertIn("global.addEventListener('load', onResize, { once: true });", self.js)


if __name__ == "__main__":
    unittest.main()
