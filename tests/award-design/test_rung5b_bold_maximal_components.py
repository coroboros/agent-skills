"""award-design completeness program — rung 5B (bold-maximal, second half).

Six builds: four bold-maximal playbook `gaps` shipped as components
(page-transition-choreography, scroll-speed-oscillator,
section-accent-rotation, sound-channel — the ledger's 'sound-channel + mute
affordance' is ONE build, the affordance integral) plus the two
specimen-tour-exat MISSING refs, both in `form` fields, shipped as SECTION
FORMS (specimen-grid CSS-only, type-tester with an enhancer). Alias rulings
on evidence: the choreography is DISTINCT from the three shipped transition
tools (shader mix between two live scenes / morphing-edge wipe vs quiet
crossfade, flat bar, shared-element morph); the rung-7/8 velocity orders are
other archetypes' rulings, not folded. What the tests lock is each build's
LOAD-BEARING distinction, all driven in-browser before pinning: the
choreography's lip morph is velocity-shaped (swells at launch, flat at
arrival — the first flat-edge build was refuted in-browser and re-geometried
to origin center), reduce is an instant cut and the coarse mix degrade is a
fast crossfade; the oscillator reads VELOCITY not position (slow sweep 2.3px
vs flick 17.5px, driven), rests off-screen units, keeps Ponpon's 0.01
factor, clips the shift host by JS, and never splits under reduce; the
rotation swaps ONE role's value (accent) with ink never rotating, zero-flip
via the center band, never invents color, and scopes statically per section
under reduce; the sound channel resumes ONLY inside a real gesture (driven:
persisted ON survived a reload muted until the next gesture), ramps instead
of cutting, and never auto-restores under calm signals; the specimen grid
rests at weight 200 = the sweep's outermost ring; the tester writes the
gap's own axis vars from native controls and takes real typed keys."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
COMPONENTS = REPO_ROOT / "skills" / "award-design" / "assets" / "components"
FORMS = COMPONENTS / "forms"

# interaction component file → the global its IIFE must export
RUNG5B_GLOBALS = {
    "page-transition-choreography.js": "awardPageTransitionChoreography",
    "scroll-speed-oscillator.js": "awardScrollSpeedOscillator",
    "section-accent-rotation.js": "awardSectionAccentRotation",
    "sound-channel.js": "awardSoundChannel",
}

# form id → (css, enhancer js or None, enhancer global or None)
RUNG5B_FORMS = {
    "specimen-grid": ("specimen-grid.css", None, None),
    "type-tester": ("type-tester.css", "type-tester.js", "awardTypeTester"),
}


def _src(name):
    return (COMPONENTS / name).read_text(encoding="utf-8")


def _form(name):
    return (FORMS / name).read_text(encoding="utf-8")


class TestRung5bLibraryContract(unittest.TestCase):
    """The structural contract every library component keeps (the
    test_component_library floor, applied before the manifest merge)."""

    def test_files_exist(self):
        for name in RUNG5B_GLOBALS:
            with self.subTest(file=name):
                self.assertTrue((COMPONENTS / name).is_file())
        for form_id, (css, js, _g) in RUNG5B_FORMS.items():
            with self.subTest(form=form_id):
                self.assertTrue((FORMS / css).is_file())
                if js:
                    self.assertTrue((FORMS / js).is_file())

    def test_iife_and_global_export(self):
        everything = dict(RUNG5B_GLOBALS)
        for _id, (_css, js, g) in RUNG5B_FORMS.items():
            if js:
                everything["forms/" + js] = g
        for name, g in everything.items():
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("(function (global)", src)
                self.assertRegex(src, r"global\." + re.escape(g) + r"\s*=")

    def test_exposes_init_and_destroy(self):
        files = list(RUNG5B_GLOBALS) + ["forms/" + js for _c, js, _g in RUNG5B_FORMS.values() if js]
        for name in files:
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("function init", src)
                self.assertIn("destroy", src)

    def test_has_reduced_motion_path(self):
        files = list(RUNG5B_GLOBALS) + ["forms/" + js for _c, js, _g in RUNG5B_FORMS.values() if js]
        for name in files:
            with self.subTest(component=name):
                self.assertIn("prefers-reduced-motion", _src(name))

    def test_has_doc_comment_header(self):
        files = (list(RUNG5B_GLOBALS)
                 + ["forms/" + js for _c, js, _g in RUNG5B_FORMS.values() if js]
                 + ["forms/" + css for css, _j, _g in RUNG5B_FORMS.values()])
        for name in files:
            with self.subTest(file=name):
                self.assertTrue(_src(name).lstrip().startswith("/*"))

    def test_namespaced_stylesheet_injection(self):
        """One namespaced stylesheet per interaction component. The form
        enhancer injects nothing — its states live in the linked form CSS."""
        for name in RUNG5B_GLOBALS:
            with self.subTest(component=name):
                self.assertRegex(_src(name), r"CSS_ID = 'ad-[a-z-]+-css'")
        self.assertNotIn("createElement('style')", _src("forms/type-tester.js"))

    def test_no_bare_100vh(self):
        """svh/lvh/dvh only — a bare 100vh jumps under mobile chrome
        collapse (the choreography's rail rides lvh by construction)."""
        files = (list(RUNG5B_GLOBALS)
                 + ["forms/" + js for _c, js, _g in RUNG5B_FORMS.values() if js]
                 + ["forms/" + css for css, _j, _g in RUNG5B_FORMS.values()])
        for name in files:
            with self.subTest(file=name):
                self.assertNotRegex(_src(name), r"100vh")


class TestRung5bFormDiscipline(unittest.TestCase):
    """The section-form floors (the test_section_forms contract, applied to
    the two new forms before the manifest merge)."""

    def test_form_root_selector_present(self):
        for form_id, (css, _js, _g) in RUNG5B_FORMS.items():
            with self.subTest(form=form_id):
                self.assertIn(f'[data-ad-form="{form_id}"]', _form(css))

    def test_forms_ship_zero_motion(self):
        for form_id, (css, _js, _g) in RUNG5B_FORMS.items():
            src = _form(css)
            with self.subTest(form=form_id):
                self.assertNotIn("@keyframes", src)
                self.assertNotRegex(src, r"\banimation\s*:")
                self.assertNotRegex(src, r"\btransition\s*:")

    def test_no_js_floor_no_hidden_slots(self):
        """A dead script leaves the composed specimen and the static grid
        fully legible — nothing hides at rest."""
        for form_id, (css, _js, _g) in RUNG5B_FORMS.items():
            src = _form(css)
            with self.subTest(form=form_id):
                self.assertNotRegex(src, r"visibility:\s*hidden")
                self.assertNotRegex(src, r"opacity:\s*0(?![.\d])")

    def test_enhancers_never_write_html_strings(self):
        src = _form("type-tester.js")
        self.assertNotRegex(src, r"\binnerHTML\s*=")
        self.assertNotRegex(src, r"\binsertAdjacentHTML\b")

    def test_forms_style_attributes_never_role_classes(self):
        """class-role uniformity rule: form state rides data attributes — a
        .ad-*/.is-* selector in a form stylesheet is the class-role drift
        the scanner fails."""
        for form_id, (css, _js, _g) in RUNG5B_FORMS.items():
            src = _form(css)
            with self.subTest(form=form_id):
                self.assertNotRegex(src, r"\.ad-")
                self.assertNotRegex(src, r"\.is-")


class TestPageTransitionChoreography(unittest.TestCase):
    """The between-view spectacle: Ponpon's delegated shader-mix clock and
    21 TSI's morphing-edge wipe — ruled distinct from the three shipped
    transition tools, and degrading exactly as the gap orders."""

    def setUp(self):
        self.src = _src("page-transition-choreography.js")

    def test_distinct_from_the_shipped_transition_tools(self):
        """The alias ruling rides in the header: crossfade carrier, flat
        curtain, shared-element morph are all named as NOT this build."""
        self.assertIn("route-view-transition-carrier", self.src)
        self.assertIn("curtain-transition", self.src)
        self.assertIn("continuous-work-transition", self.src)
        self.assertIn("NOT an alias", self.src)

    def test_mix_mounts_first_then_blends(self):
        """The Ponpon shape: both scenes live, fn mounts the incoming scene
        BEFORE the blend drives 0->1."""
        self.assertIn("// The Ponpon shape: mount the incoming scene, then blend 0 -> 1.", self.src)

    def test_failed_mount_never_blends_into_garbage(self):
        self.assertIn("if (r.error) { state.playing = null; throw r.error; }", self.src)

    def test_mix_honors_the_css_ease_token(self):
        """The tween solves the same cubic-bezier the wipe rides — no GSAP
        dependency."""
        self.assertIn("function bezier(", self.src)
        self.assertIn("--ad-ptc-ease", self.src)
        self.assertIn("--ad-ease-signature", self.src)

    def test_coarse_mix_degrades_to_fast_crossfade(self):
        """The gap's own order: never a sub-30fps blocking blend on touch."""
        self.assertIn("if (coarse()) {", self.src)
        self.assertIn("var FAST_FADE = 0.35;", self.src)

    def test_reduce_is_an_instant_cut(self):
        self.assertIn("// The gap's degrade order: reduced motion is an instant cut.", self.src)

    def test_lip_morph_is_velocity_shaped(self):
        """Driven finding: a lip riding the decelerating rail ease is flat
        by mid-travel — the morph reads only when the bulge swells at launch
        and relaxes at arrival (three keyframes, peak at the launch phase)."""
        self.assertIn("var LIP_PEAK = 0.25;", self.src)
        self.assertIn("offset: LIP_PEAK", self.src)

    def test_lip_anchored_on_the_edge(self):
        """Driven finding: origin center-bottom collapsed the bulge under
        the body — the lip centers ON the edge so the morph stays visible."""
        self.assertIn("transform-origin:center;", self.src)
        self.assertIn("never dipping under the body", self.src)

    def test_panel_inert_at_rest_blocks_only_live(self):
        self.assertIn("pointer-events:none;visibility:hidden;", self.src)
        self.assertIn("[data-live]{visibility:visible;pointer-events:auto;}", self.src)

    def test_panel_decorative_and_js_created(self):
        self.assertIn("panel.setAttribute('aria-hidden', 'true');", self.src)

    def test_timeout_cap_and_error_surfacing(self):
        """A hung fetch never strands a covered view; fn errors surface
        AFTER the view is whole again."""
        self.assertIn("var DEFAULT_TIMEOUT = 2000;", self.src)
        self.assertIn("go() re-throws after the view is whole again", self.src)

    def test_destroy_snaps_a_mid_blend_mix_to_one(self):
        self.assertIn("if (state.destroyed) { mix(1); state.raf = 0; resolve(); return; }", self.src)


class TestScrollSpeedOscillator(unittest.TestCase):
    """The velocity décor channel: Exat's speed-tracking sine, Ponpon's
    0.01 feedback, 21 TSI's displacement — reads velocity, not position."""

    def setUp(self):
        self.src = _src("scroll-speed-oscillator.js")

    def test_ponpons_factor_is_the_winners_number(self):
        self.assertIn("var NUDGE = 0.01;", self.src)
        self.assertIn("the winner's factor", self.src)

    def test_velocity_is_smoothed_and_settles(self):
        """v lerps toward the instantaneous read and the loop parks only
        when velocity AND every unit have settled to rest."""
        self.assertIn("v += (inst - v) * SMOOTH;", self.src)
        self.assertIn("if (live || unsettled) raf = global.requestAnimationFrame(frame);", self.src)

    def test_wave_amplitude_tracks_speed(self):
        self.assertIn("var a = Math.abs(v01) * amp;", self.src)
        self.assertIn("Math.sin(t + i * STRIDE)", self.src)

    def test_shift_host_is_clipped_by_js(self):
        """The full-bleed overlay law: a stretched figure never paints over
        neighboring sections; the clip is JS-applied so a dead script leaves
        nothing clipped."""
        self.assertIn("'.ad-sso-frame{overflow:hidden;}'", self.src)
        self.assertIn("f.frame.classList.add('ad-sso-frame');", self.src)

    def test_offscreen_units_rest_never_freeze(self):
        self.assertIn("if (!f.on) rest(f); // never re-enter frozen mid-wave", self.src)

    def test_live_on_touch_scroll_is_the_input(self):
        """NOT pointer-gated — the archetype's mobile answer: depth that
        came from the pointer comes from scroll."""
        self.assertNotIn("pointer: fine", self.src)
        self.assertIn("stays live on touch", self.src)

    def test_dormant_under_reduce_never_splits(self):
        self.assertIn("if (reduce()) return { destroy: function () {} };", self.src)
        self.assertIn("the text is never split", self.src)

    def test_split_keeps_the_accessible_name_and_rewrap(self):
        self.assertIn("el.setAttribute('aria-label', text)", self.src)
        self.assertIn("document.createTextNode(' ')", self.src)

    def test_transform_only_writes(self):
        self.assertNotIn(".style.left", self.src)
        self.assertNotIn(".style.top", self.src)
        self.assertNotIn(".style.filter", self.src)


class TestSectionAccentRotation(unittest.TestCase):
    """DICH's color-temperature chapters as a token scope swap: one role's
    VALUE rotates, jobs never re-deal, one owner at a time."""

    def setUp(self):
        self.src = _src("section-accent-rotation.js")

    def test_saturated_register_only_never_default(self):
        """One corpus winner — the header carries the never-default warning
        the playbook's unverified bucket demands."""
        self.assertIn("SINGLE corpus winner", self.src)
        self.assertIn("never on a kinetic-register build", self.src)

    def test_the_role_law_is_the_contract(self):
        self.assertIn("THE ROLE LAW", self.src)
        self.assertIn("ink never rotates", self.src)

    def test_writes_the_shared_tokens(self):
        self.assertIn("target.style.setProperty('--ad-accent', s.accent);", self.src)
        self.assertIn("target.style.setProperty('--ad-ground', s.ground);", self.src)

    def test_zero_flip_center_band(self):
        """The viewport-center band owns activation; writes happen only on
        a real owner change."""
        self.assertIn("rootMargin: '-50% 0% -50% 0%'", self.src)
        self.assertIn("if (s === active) return; // zero-flip: write only on a real owner change", self.src)

    def test_never_invents_color(self):
        self.assertIn("if (!accent && !ground) return; // never invent color", self.src)

    def test_state_rides_data_attributes(self):
        self.assertIn("data-ad-sar-active", self.src)

    def test_ground_eases_via_js_applied_class(self):
        self.assertIn("body.classList.add('ad-sar-ground');", self.src)
        self.assertIn("--ad-dur-reveal", self.src)

    def test_reduce_scopes_each_section_statically(self):
        """The section-scale-momentum static-end answer: hue-per-section
        identity survives with zero global mutation."""
        self.assertIn("s.el.style.setProperty('--ad-accent', s.accent);", self.src)
        self.assertIn("s.el.style.backgroundColor = s.ground;", self.src)

    def test_destroy_restores_prior_inline_tokens(self):
        self.assertIn("var prevAccent = target.style.getPropertyValue('--ad-accent');", self.src)


class TestSoundChannel(unittest.TestCase):
    """21 TSI's opt-in channel under the web-audio.md law: the unlock gate,
    off-by-default, the ramp, the persisted designed affordance."""

    def setUp(self):
        self.src = _src("sound-channel.js")

    def test_the_unlock_gate_is_law(self):
        """Resume only inside a real gesture — pointerdown/keydown/click,
        never mousemove or scroll; never autoplay."""
        self.assertIn("THE UNLOCK GATE IS LAW", self.src)
        self.assertIn("document.addEventListener('pointerdown', prime, true);", self.src)
        self.assertIn("document.addEventListener('keydown', prime, true);", self.src)
        self.assertNotIn("addEventListener('mousemove'", self.src)
        self.assertNotIn("addEventListener('scroll'", self.src)

    def test_off_by_default_lazy_behind_opt_in(self):
        """Nothing loads, decodes, or plays before the opt-in; play() while
        muted is a silent no-op that never queues."""
        self.assertIn("if (!on || !ctx || ctx.state !== 'running') return; // silent no-op", self.src)
        self.assertIn("if (!buf) return; // not loaded (yet) — never queue, never throw", self.src)

    def test_mute_ramps_never_cuts_then_suspends(self):
        self.assertIn("var MUTE_RAMP = 0.4;", self.src)
        self.assertIn("// ramp, never cut — then park the context after the tail", self.src)
        self.assertIn("ctx.suspend()", self.src)

    def test_bed_gain_sits_in_the_felt_band(self):
        self.assertIn("var BED_GAIN = 0.1;    // the 0.05-0.15 band", self.src)

    def test_preference_persists_across_visits(self):
        self.assertIn("global.localStorage", self.src)
        self.assertIn("var STORE_DEFAULT = 'ad-sound-on';", self.src)

    def test_calm_signals_never_auto_restore(self):
        """Driven: stored=1 under reduced-motion loads muted — the choice is
        the visitor's, made again this visit. Save-Data is the same signal."""
        self.assertIn("if (store(key) === '1' && !reduce() && !saveData()) {", self.src)

    def test_persisted_on_still_waits_for_this_pages_gesture(self):
        self.assertIn("A persisted ON still waits for THIS page's first gesture", self.src)

    def test_the_designed_affordance(self):
        """A real button: aria-pressed state, action-naming label, dancing
        bars on-state, static under reduce."""
        self.assertIn("btn.type = 'button';", self.src)
        self.assertIn("'Enable sound'", self.src)
        self.assertIn("'Mute sound'", self.src)
        self.assertIn("aria-pressed", self.src)
        self.assertIn("@keyframes ad-sc-dance", self.src)
        self.assertIn("animation:none!important", self.src)

    def test_analyser_level_is_the_verification_readout(self):
        self.assertIn("analyser.getByteTimeDomainData(data);", self.src)
        self.assertIn("function getState()", self.src)

    def test_cues_and_bed_accept_synth_factories(self):
        """A factory cue/bed plays zero bytes of network audio — the
        in-world material path."""
        self.assertIn("if (typeof src === 'function') { src(ctx, sfxBus); return; }", self.src)
        self.assertIn("if (typeof bed === 'function') {", self.src)


class TestSpecimenGridForm(unittest.TestCase):
    """Exat's specimen climax as a stage: the form owns layout only; the
    mechanic is the paired typefield's."""

    def setUp(self):
        self.css = _form("specimen-grid.css")

    def test_resolves_the_recipes_missing_ref(self):
        self.assertIn("MISSING:specimen-grid", self.css)

    def test_full_stage_variant_svh(self):
        self.assertIn('[data-stage="full"]', self.css)
        self.assertIn("min-height: 100svh;", self.css)

    def test_field_rests_at_the_sweeps_outermost_ring(self):
        """Weight 200 = the typefield's outer ring, so the no-JS/touch
        render IS the winner's static composed grid — one shared rest."""
        self.assertIn("font-weight: 200;", self.css)
        self.assertIn("rest weight 200 = the sweep's outermost ring", self.css)

    def test_every_slot_is_styled(self):
        for slot in ("kicker", "h2", "field", "caption"):
            with self.subTest(slot=slot):
                self.assertIn(f'[data-slot="{slot}"]', self.css)

    def test_pairs_route_to_the_typefield(self):
        self.assertIn("cursor-proximity-typefield", self.css)
        self.assertIn("scroll-speed-oscillator", self.css)

    def test_authored_units_supported(self):
        self.assertIn("[data-tf-unit]", self.css)


class TestTypeTesterForm(unittest.TestCase):
    """Exat's operable proof: native controls write the gap's own axis vars
    onto the preview; the sample takes real typed keys."""

    def setUp(self):
        self.css = _form("type-tester.css")
        self.js = _form("type-tester.js")

    def test_resolves_the_recipes_missing_ref(self):
        self.assertIn("MISSING:type-tester", self.css)

    def test_preview_reads_the_gaps_axis_vars(self):
        """--ff/--fs/--fw/--lh/--ls are the gap's own names; the fallbacks
        ARE the composed rest a dead script shows."""
        for var in ("--ff", "--fs", "--fw", "--lh", "--ls"):
            with self.subTest(var=var):
                self.assertIn(f"var({var},", self.css)

    def test_enhancer_writes_vars_and_readouts(self):
        self.assertIn("preview.style.setProperty('--' + axis, value);", self.js)
        self.assertIn("[data-tester-value]", self.js)

    def test_controls_sync_at_init(self):
        self.assertIn("apply(control); // sync: authored control positions drive the rest state", self.js)

    def test_editable_sample_plaintext_only_with_fallback(self):
        """Real keys drive the sample; plaintext-only avoids paste
        formatting, engines without it fall back to plain contenteditable."""
        self.assertIn("preview.setAttribute('contenteditable', 'plaintext-only');", self.js)
        self.assertIn("if (preview.contentEditable !== 'plaintext-only') {", self.js)
        self.assertIn("'Type your own sample'", self.js)

    def test_state_rides_data_attributes(self):
        self.assertIn("data-tester-live", self.js)
        self.assertNotRegex(self.js, r"classList\.add")

    def test_accent_color_is_the_committed_token(self):
        self.assertIn("accent-color: var(--ad-accent", self.css)

    def test_layering_law_no_created_nodes(self):
        self.assertNotIn("createElement", self.js)

    def test_destroy_restores_the_preview(self):
        self.assertIn("if (f.priorEditable == null) f.preview.removeAttribute('contenteditable');", self.js)


if __name__ == "__main__":
    unittest.main()
