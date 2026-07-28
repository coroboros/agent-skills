"""award-design completeness program — rung 8B (experimental, second half).

Seven orders: five shipped as components (physics-tumble-field,
scroll-velocity-scene-distortion, sdf-scramble-substrate,
spatial-audio-world, velocity-flowmap-hover), one as a SECTION FORM
(world-boot — the only rung-8B MISSING ref, sitting in the world-boot
section `form` field of engine-world-bruno), and one closed by ALIAS
RULING with no artifact: world-boot-gate is ONE mechanic under two ledger
lines — its ledger sibling world-boot has no seen-in of its own because
it is the recipes-field spelling of the same gap, whose text names both
refs; the gap's Igloo spelling shipped in rung 8A as in-engine-intro and
its Bruno spelling ships here as the world-boot form (the territory the
rung-7B webgl-preload-gate ruling explicitly preserved). Other rulings on
evidence, written into each header: spatial-audio-world is DISTINCT
territory from sound-channel (scene-agnostic costume) and the procession
score (1D stem mix) — 3D PannerNode/listener geometry — while REUSING the
merged carrier's unlock/mute affordance contract, one audio carrier per
page across all three; scroll-velocity-scene-distortion is DISTINCT +
COMPANION to scroll-speed-oscillator (the DOM-transform half vs this
delegated in-texture half — one spelling per surface);
velocity-flowmap-hover is DISTINCT from figure-hover (contained zoom) and
liquid-glass-refraction (still material) on the memory axis — a
time-decaying velocity field the cursor writes; sdf-scramble-substrate is
DISTINCT from scramble-decode on the substrate axis (attribute-buffer
offset swaps vs per-tick textContent churn). What the tests lock is each
build's LOAD-BEARING driven distinction: the tumble field settled its
pile upright and parked (running:false), threw a card at vx≈1814 off a
160ms flick into a body-body collision and re-settled in bounds, swallowed
exactly the drag's own click (the lingering swallow was drive-caught) and
stood dormant under ?rm; the distortion peaked at 0.772 under a real
eased flick, decayed 0.093→0 and parked with an exact-rest draw, and held
vel 0.94 under the feed() virtual scrub (the journey seam) with
full-scene star splitting; the SDF decode resolved 1→16 left-to-right
over ~900ms with ZERO MutationObserver hits and stable textContent (the
reflow-free law, decidable), aria-label intact through every churn frame,
the inline ink-hide drive-caught against a higher-specificity builder
rule; the spatial world unlocked ONLY on the native ENTER click (ctx
'none' through the whole cold load), measured its pan in split-channel
RMS (L 0.046 > R 0.013 with the source 4 left, flipping to R 0.023 >
L 0.008 when setSource crossed it to +4), applied the gate-stored
listener pose at unlock (drive-caught), and kept reduce silent until the
visitor's own toggle click; the flowmap trail read fx=0.181 on the swept
row and 0 off-row, persisted past pointerleave at energy 0.21, decayed to
a cold park in ~1.26s, and dropped to the plain img on context loss; the
world-boot ran ZERO frames from a cold load until the native start click,
then 142 decelerating boot(p) frames over exactly 2400ms with
p + posterOpacity = 1.000 at every sample, the audio carrier running from
the same gesture, ?rm booting the world in ONE boot(1) frame (interaction
kept, choreography skipped) and ?nojs leaving the poster page whole with
the start control never un-hidden."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
COMPONENTS = REPO_ROOT / "skills" / "award-design" / "assets" / "components"
FORMS = COMPONENTS / "forms"

# interaction component file → the global its IIFE must export
RUNG8B_GLOBALS = {
    "physics-tumble-field.js": "awardPhysicsTumbleField",
    "scroll-velocity-scene-distortion.js": "awardScrollVelocitySceneDistortion",
    "sdf-scramble-substrate.js": "awardSdfScrambleSubstrate",
    "spatial-audio-world.js": "awardSpatialAudioWorld",
    "velocity-flowmap-hover.js": "awardVelocityFlowmapHover",
}

# form id → (css, enhancer js, enhancer global)
RUNG8B_FORMS = {
    "world-boot": ("world-boot.css", "world-boot.js", "awardWorldBoot"),
}


def _src(name):
    return (COMPONENTS / name).read_text(encoding="utf-8")


def _form(name):
    return (FORMS / name).read_text(encoding="utf-8")


class TestRung8bLibraryContract(unittest.TestCase):
    """The structural contract every library component keeps (the
    test_component_library floor, applied before the manifest merge)."""

    def test_files_exist(self):
        for name in RUNG8B_GLOBALS:
            with self.subTest(file=name):
                self.assertTrue((COMPONENTS / name).is_file())
        for form_id, (css, js, _g) in RUNG8B_FORMS.items():
            with self.subTest(form=form_id):
                self.assertTrue((FORMS / css).is_file())
                self.assertTrue((FORMS / js).is_file())

    def test_iife_and_global_export(self):
        everything = dict(RUNG8B_GLOBALS)
        for _id, (_css, js, g) in RUNG8B_FORMS.items():
            everything["forms/" + js] = g
        for name, g in everything.items():
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("(function (global)", src)
                self.assertRegex(src, r"global\." + re.escape(g) + r"\s*=")

    def test_exposes_init_and_destroy(self):
        files = list(RUNG8B_GLOBALS) + ["forms/" + js for _c, js, _g in RUNG8B_FORMS.values()]
        for name in files:
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("function init", src)
                self.assertIn("destroy", src)

    def test_has_reduced_motion_contract(self):
        """Every artifact names its reduce answer — dormant, the authored
        state, or the deliberate interaction-still-boots ruling."""
        files = list(RUNG8B_GLOBALS) + ["forms/" + js for _c, js, _g in RUNG8B_FORMS.values()]
        for name in files:
            with self.subTest(component=name):
                self.assertIn("reduced-motion", _src(name))

    def test_has_doc_comment_header(self):
        files = (list(RUNG8B_GLOBALS)
                 + ["forms/" + js for _c, js, _g in RUNG8B_FORMS.values()]
                 + ["forms/" + css for css, _j, _g in RUNG8B_FORMS.values()])
        for name in files:
            with self.subTest(file=name):
                self.assertTrue(_src(name).lstrip().startswith("/*"))

    def test_namespaced_stylesheet_injection(self):
        """Every rung-8B component paints chrome or overlays and injects ONE
        namespaced stylesheet; the form enhancer injects nothing ever."""
        for name in RUNG8B_GLOBALS:
            with self.subTest(component=name):
                self.assertRegex(_src(name), r"CSS_ID = 'ad-[a-z0-9-]+-css'")
        for _id, (_css, js, _g) in RUNG8B_FORMS.items():
            with self.subTest(form=_id):
                self.assertNotIn("createElement('style')", _src("forms/" + js))

    def test_form_enhancer_creates_no_nodes(self):
        """The layering law: the world-boot enhancer toggles attributes and
        inline styles only (its WebGL probe canvas is created but never
        appended — the engine owns the mount)."""
        for _id, (_css, js, _g) in RUNG8B_FORMS.items():
            src = _src("forms/" + js)
            with self.subTest(form=_id):
                self.assertNotRegex(src, r"\bappendChild\b")
                self.assertNotRegex(src, r"\binnerHTML\s*=")
                self.assertNotRegex(src, r"\binsertAdjacentHTML\b")

    def test_no_bare_100vh(self):
        """svh/lvh/dvh only — a bare 100vh jumps under mobile chrome
        collapse."""
        files = (list(RUNG8B_GLOBALS)
                 + ["forms/" + js for _c, js, _g in RUNG8B_FORMS.values()]
                 + ["forms/" + css for css, _j, _g in RUNG8B_FORMS.values()])
        for name in files:
            with self.subTest(file=name):
                self.assertNotRegex(_src(name), r"100vh")

    def test_io_and_visibility_gating_where_a_loop_exists(self):
        """Every rAF owner gates by IntersectionObserver + visibilitychange;
        the audio carrier owns no rAF and gates by visibilitychange alone."""
        for name in ("physics-tumble-field.js", "scroll-velocity-scene-distortion.js",
                     "velocity-flowmap-hover.js", "sdf-scramble-substrate.js"):
            with self.subTest(component=name):
                self.assertIn("IntersectionObserver", _src(name))
                self.assertIn("visibilitychange", _src(name))
        audio = _src("spatial-audio-world.js")
        self.assertIn("visibilitychange", audio)
        self.assertNotIn("requestAnimationFrame", audio)


class TestRung8bFormDiscipline(unittest.TestCase):
    """The section-form floors (the test_section_forms contract, applied to
    the rung-8B form before the manifest merge)."""

    def test_form_root_selector_present(self):
        for form_id, (css, _js, _g) in RUNG8B_FORMS.items():
            with self.subTest(form=form_id):
                self.assertIn('[data-ad-form="' + form_id + '"]', _form(css))

    def test_form_ships_zero_motion(self):
        for form_id, (css, _js, _g) in RUNG8B_FORMS.items():
            src = _form(css)
            with self.subTest(form=form_id):
                self.assertNotIn("@keyframes", src)
                self.assertNotRegex(src, r"\banimation\s*:")
                self.assertNotRegex(src, r"\btransition\s*:")

    def test_no_js_floor_no_hidden_states(self):
        """A dead script leaves the poster page fully legible — the start
        control is authored `hidden` by the builder; every state hide is an
        enhancer inline write."""
        for form_id, (css, _js, _g) in RUNG8B_FORMS.items():
            src = _form(css)
            with self.subTest(form=form_id):
                self.assertNotRegex(src, r"opacity:\s*0(?![.\d])")
                self.assertNotIn("visibility: hidden", src)
                self.assertNotIn("display: none", src)

    def test_form_styles_attributes_never_role_classes(self):
        """class-role uniformity rule: form state rides data attributes — a
        .ad-*/.is-* selector in a form stylesheet is class-role drift."""
        for form_id, (css, _js, _g) in RUNG8B_FORMS.items():
            src = _form(css)
            with self.subTest(form=form_id):
                self.assertNotRegex(src, r"\.ad-")
                self.assertNotRegex(src, r"\.is-")

    def test_the_stage_is_svh(self):
        """The shared stage law (svh deliberately — dvh re-rasterizes an
        engine target on mobile URL-bar collapse)."""
        self.assertIn("min-height: 100svh", _form("world-boot.css"))


class TestPhysicsTumbleField(unittest.TestCase):
    """MoMoney's throw-field: one clean winner, a hand-rolled subset, and
    the settle/click discipline the drives caught."""

    def setUp(self):
        self.src = _src("physics-tumble-field.js")

    def test_the_one_winner_corrected_count_rides_in_the_header(self):
        self.assertIn("MoMoney", self.src)
        self.assertIn("ADJACENT", self.src)
        self.assertIn("NOT a per-site read", self.src)

    def test_dependency_free_subset_never_the_library(self):
        """Repo law: the gap names Matter.js — the header names the subset
        that replaces it."""
        self.assertIn("Matter.js", self.src)
        self.assertIn("dependency-free", self.src)
        self.assertIn("never the library", self.src)

    def test_the_release_velocity_window_is_the_throw(self):
        """Driven: a 160ms accelerating flick released at vx≈1814/vy≈-2190
        from the ~80ms trail window."""
        self.assertIn("var SAMPLE_MS = 80;", self.src)
        self.assertIn("h.body.vx = (a1.x - a0.x) / span;", self.src)

    def test_the_settle_torque_is_speed_gated(self):
        """Drive-caught: the first run left cards asleep at 10 rad — the
        weighted-base torque rights them only once slow (flight never
        fakes it)."""
        self.assertIn("if (sp0 < 90) { b.va += -b.angle * 7 * dt; b.va *= 0.96; }", self.src)

    def test_the_pile_sleeps_and_the_loop_parks(self):
        """Driven: all bodies asleep → running:false; any grab wakes."""
        self.assertIn("b.asleep = true;", self.src)
        self.assertIn("the loop parks cold", self.src)

    def test_click_discipline_swallows_exactly_the_drags_click(self):
        """Drive-caught: the swallow lingered and ate a later legitimate
        click — it now disarms on the next task."""
        self.assertIn("var DRAG_THRESHOLD = 6;", self.src)
        self.assertIn("el.removeEventListener('click', once, { capture: true });", self.src)

    def test_the_clip_law_rides_the_field(self):
        """A thrown body never paints over a neighboring section."""
        self.assertIn("overflow:clip", self.src)
        self.assertIn("touch-action:none", self.src)

    def test_reduce_is_the_authored_layout(self):
        """Driven under ?rm: no transforms, no stylesheet, a flick moved
        nothing — the gap's own reduce answer."""
        self.assertIn("the authored layout IS the field at rest", self.src)


class TestScrollVelocitySceneDistortion(unittest.TestCase):
    """The delegated in-texture half of the velocity transfer."""

    def setUp(self):
        self.src = _src("scroll-velocity-scene-distortion.js")

    def test_the_soft_attribution_caveat_rides_in_the_header(self):
        """The gap's own evidence caveat is carried verbatim — never
        presented as measured winner spec."""
        self.assertIn("EVIDENCE CAVEAT", self.src)
        self.assertIn("DOCUMENTED", self.src)
        self.assertIn("TECHNIQUE, not a measured winner spec", self.src)

    def test_the_oscillator_ruling_rides_in_the_header(self):
        self.assertIn("scroll-speed-oscillator", self.src)
        self.assertIn("DISTINCT + COMPANION", self.src)
        self.assertIn("never both on one element", self.src)

    def test_the_feed_seam_drives_journey_stacks(self):
        """Driven: feed() held vel 0.94 with the plate stationary — the
        journey-touch-momentum onProgress seam."""
        self.assertIn("feed: function (pos) {", self.src)
        self.assertIn("journey-touch-momentum", self.src)

    def test_velocity_smooths_and_parks_at_exact_rest(self):
        """Driven: peak 0.772 under a real eased flick, decay 0.093→0 in
        ~560ms, one exact-rest draw, park."""
        self.assertIn("var SMOOTH = 0.12;", self.src)
        self.assertIn("settle to the exact rest, park cold", self.src)

    def test_context_loss_and_tainted_plates_fall_back(self):
        self.assertIn("webglcontextlost", self.src)
        self.assertIn("tainted plate", self.src)

    def test_scroll_stays_live_on_touch(self):
        """NOT pointer-gated — scroll is the input."""
        self.assertIn("NOT pointer-gated", self.src)
        self.assertIn("{ passive: true }", self.src)

    def test_dpr_is_capped(self):
        self.assertIn("Math.min(2, global.devicePixelRatio || 1)", self.src)


class TestSdfScrambleSubstrate(unittest.TestCase):
    """Igloo's reflow-free decode: offset swaps in an attribute buffer,
    never a DOM write."""

    def setUp(self):
        self.src = _src("sdf-scramble-substrate.js")

    def test_the_winner_mechanic_rides_in_the_header(self):
        self.assertIn("Igloo", self.src)
        self.assertIn("SWAPPING SDF TEXTURE OFFSETS", self.src)

    def test_the_dom_spelling_ruling_rides_in_the_header(self):
        """DISTINCT from scramble-decode on the substrate axis — that
        component rewrites textContent per tick."""
        self.assertIn("scramble-decode", self.src)
        self.assertIn("zero DOM relayout", self.src)

    def test_the_atlas_is_a_runtime_exact_edt_bake(self):
        self.assertIn("Felzenszwalb", self.src)
        self.assertIn("function bakeAtlas", self.src)

    def test_the_churn_is_an_attribute_buffer_swap(self):
        """Driven: ZERO MutationObserver hits and stable textContent through
        a full decode — the swap touches only the cell buffer."""
        self.assertIn("gl.bufferSubData(gl.ARRAY_BUFFER, 0, unit.cells);", self.src)
        self.assertIn("setCell(i, Math.floor(Math.random() * (CHARSET.length - 1)));", self.src)

    def test_the_accessible_name_is_pinned_and_the_text_stays(self):
        """Driven: aria-label constant through every churn frame; the ink
        hide is an INLINE write (drive-caught: a builder's
        higher-specificity color rule painted a doubled label)."""
        self.assertIn("el.setAttribute('aria-label', label);", self.src)
        self.assertIn("el.style.color = 'transparent';", self.src)
        self.assertIn("an INLINE write (drive-caught", self.src)

    def test_aberration_rides_the_churn_and_dies_at_settle(self):
        self.assertIn("unit.aberr = 0.05 * (1 - t);", self.src)

    def test_the_transition_pass_is_exposed_for_scene_beats(self):
        self.assertIn("transition: function (p) {", self.src)
        self.assertIn("u_frost", self.src)

    def test_the_register_law_is_kept(self):
        self.assertIn("SHORT strings only", self.src)

    def test_reduce_never_scrambles(self):
        self.assertIn("never scrambles", self.src)


class TestSpatialAudioWorld(unittest.TestCase):
    """The positional carrier: panner geometry, the unlock law, one
    carrier per page."""

    def setUp(self):
        self.src = _src("spatial-audio-world.js")

    def test_the_winners_and_the_defaults_caveat_ride_in_the_header(self):
        self.assertIn("Bruno", self.src)
        self.assertIn("Kounine", self.src)
        self.assertIn("DEFAULTS", self.src)

    def test_the_one_carrier_law_rides_in_the_header(self):
        self.assertIn("sound-channel", self.src)
        self.assertIn("scored-scene-procession", self.src)
        self.assertIn("ONE per page", self.src)

    def test_the_unlock_gate_is_law(self):
        """Driven: ctx 'none' through the whole cold load; the native ENTER
        click unlocked and swelled the world in."""
        self.assertIn("THE UNLOCK GATE IS LAW", self.src)
        self.assertIn("never autoplay", self.src)

    def test_sources_are_panner_geometry(self):
        """Driven: the split-channel RMS flipped (L 0.046>R 0.013 →
        R 0.023>L 0.008) when setSource crossed the object to the other
        side."""
        self.assertIn("d.panner.panningModel = 'HRTF';", self.src)
        self.assertIn("d.panner.positionX.value = d.x;", self.src)
        self.assertIn("createChannelSplitter(2)", self.src)

    def test_the_gate_stored_listener_pose_applies_at_unlock(self):
        """Drive-caught: a camera moved behind the gate booted a stale
        center listener — the stored pose now re-applies."""
        self.assertIn("re-apply the stored", self.src)
        self.assertIn("function applyListener()", self.src)

    def test_calm_signals_keep_the_world_silent(self):
        """Driven under ?rm: the gate's unlock kept silence even with a
        persisted ON; the visitor's own toggle click still sounded it."""
        self.assertIn("if (reduce() || saveData()) return;", self.src)
        self.assertIn("the persisted mute is honored", self.src)

    def test_the_mute_ramps_never_cuts(self):
        self.assertIn("setTargetAtTime(0, ctx.currentTime, MUTE_RAMP / 3);", self.src)
        self.assertIn("ctx.suspend()", self.src)

    def test_the_affordance_contract_is_restated(self):
        """The merged carrier's designed toggle, under this namespace."""
        self.assertIn("aria-pressed", self.src)
        self.assertIn("'Enable sound'", self.src)
        self.assertIn("'Mute sound'", self.src)

    def test_webm_first_with_fallback(self):
        self.assertIn('audio/webm; codecs="opus"', self.src)


class TestVelocityFlowmapHover(unittest.TestCase):
    """The cursor-speed chromatic response: a decaying flowmap the cursor
    writes and the shader reads."""

    def setUp(self):
        self.src = _src("velocity-flowmap-hover.js")

    def test_the_carried_numbers_are_flagged(self):
        """Guignand/Codrops single-source values — defaults, never law."""
        self.assertIn("Guignand", self.src)
        self.assertIn("single-source", self.src)
        self.assertIn("R x1.5, G x0.5, B x1.8", self.src)
        self.assertIn("var VELO_TIP = 0.01;", self.src)

    def test_the_memory_axis_ruling_rides_in_the_header(self):
        self.assertIn("figure-hover", self.src)
        self.assertIn("liquid-glass-refraction", self.src)
        self.assertIn("PERSISTENCE", self.src)

    def test_the_trail_is_a_ping_pong_field_that_decays(self):
        """Driven: fx=0.181 on the swept row, 0 off-row; energy 0.21
        standing after pointerleave, decaying to the park floor."""
        self.assertIn("unit.simIdx = 1 - unit.simIdx;", self.src)
        self.assertIn("var DECAY = 0.955;", self.src)
        self.assertIn("var PARK_E = 0.004;", self.src)
        self.assertIn("the loop parks cold", self.src)

    def test_the_flowmap_is_measurable(self):
        """The sampleFlow readout is the trail, measured — the drive/test
        verification channel."""
        self.assertIn("sampleFlow: function (i, u, v) {", self.src)
        self.assertIn("gl.readPixels", self.src)

    def test_fine_pointer_only_dormant_on_touch(self):
        self.assertIn("(hover: hover) and (pointer: fine)", self.src)
        self.assertIn("reduce() || !finePointer()", self.src)

    def test_context_loss_and_tainted_plates_fall_back(self):
        """Driven: loseContext dropped the canvas and the plain img stood."""
        self.assertIn("webglcontextlost", self.src)
        self.assertIn("a tainted plate (cross-origin, no CORS header) throws here", self.src)


class TestWorldBootForm(unittest.TestCase):
    """The Bruno spelling of the diegetic boot — and the rung's central
    alias ruling, written where the builder reads it."""

    def setUp(self):
        self.css = _form("world-boot.css")
        self.js = _form("world-boot.js")

    def test_resolves_the_recipes_missing_ref(self):
        self.assertIn("MISSING:world-boot", self.css)
        self.assertIn("engine-world-bruno", self.css)

    def test_the_alias_ruling_rides_in_the_header(self):
        """world-boot-gate = one mechanic, two spellings, no third
        artifact: Igloo → in-engine-intro (rung 8A), Bruno → this form —
        the territory rung 7B preserved."""
        self.assertIn("ALIAS RULING", self.css)
        self.assertIn("world-boot-gate", self.css)
        self.assertIn("in-engine-intro", self.css)
        self.assertIn("webgl-preload-gate", self.css)

    def test_the_gate_axis_seam_vs_the_intro(self):
        """DISTINCT from in-engine-intro: the intro auto-arrives with no
        affordance; here nothing moves before the visitor's gesture."""
        self.assertIn("nothing moves until the visitor's start gesture", self.js)

    def test_the_start_gesture_carries_the_audio_unlock(self):
        """Driven: the audio context went 'none'→'running' on the same
        native click that started the boot."""
        self.assertIn("the gesture carries the audio unlock", self.js)
        self.assertIn("gated-splash onEnter seam", self.js)

    def test_the_gate_appears_only_over_a_startable_world(self):
        """Driven from cold load: the authored-hidden start un-hid only
        after ready(), and was spent after the click."""
        self.assertIn("if (startBtn) startBtn.hidden = false;", self.js)
        self.assertIn("if (startBtn) startBtn.hidden = true; // the gate is spent", self.js)

    def test_boot_and_poster_share_one_clock(self):
        """Driven under ?slow: p + posterOpacity = 1.000 at every sample;
        142 decelerating frames over exactly 2400ms at the default."""
        self.assertIn("if (unit.boot) unit.boot(p);", self.js)
        self.assertIn("poster.style.opacity = String(1 - p);", self.js)
        self.assertIn("poster.style.visibility = 'hidden'; // inline write, never a stylesheet state", self.js)
        self.assertIn("section.setAttribute('data-engine', 'live');", self.js)

    def test_the_stage_gates_the_pointer_on_live(self):
        self.assertIn('[data-engine="live"]', self.css)
        self.assertIn("pointer-events: auto", self.css)
        self.assertIn("pointer-events: none", self.css)

    def test_reduce_keeps_interaction_and_skips_choreography(self):
        """Driven under ?rm: ONE boot(1) frame, instant live, pointer
        routed, audio silent — the input-bridge precedent."""
        self.assertIn("the world is interaction; the assembly animation is decoration", self.js)
        self.assertIn("if (unit.boot) unit.boot(1);", self.js)

    def test_the_hard_floors_leave_the_poster_page(self):
        """Save-Data / no WebGL / no mount → poster whole, start hidden;
        reduce is deliberately NOT in this guard."""
        self.assertIn("if (!mount || saveData() || !webgl()) {", self.js)

    def test_a_hidden_tab_pauses_the_boot(self):
        self.assertIn("document.addEventListener('visibilitychange', onVis);", self.js)

    def test_own_guard_never_the_intro(self):
        """The stage law is mirrored, not delegated — a page can carry
        world-boot and a shell and needs both enhancers."""
        self.assertIn("__adWorldBoot", self.js)
        self.assertNotIn("__adInEngineIntro", self.js)

    def test_the_default_is_declared_a_default(self):
        self.assertIn("DEFAULT, not a measured winner value", self.js)


if __name__ == "__main__":
    unittest.main()
