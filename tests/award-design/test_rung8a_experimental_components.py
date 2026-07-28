"""award-design completeness program — rung 8A (experimental, first half).

Seven builds: four shipped as components (idle-attract-auto-demo,
in-3d-dom-input-bridge, journey-touch-momentum, living-presence-layer) and
three as SECTION FORMS — all three rung-8A MISSING refs sit in section
`form` fields: about-overlay-footer (the about-overlay form of
type-index-aristide), corner-counter-boot (the counter-boot form of
type-index-aristide), in-engine-intro (the intro form of
engine-world-igloo). Alias rulings on evidence, written into each header:
corner-counter-boot is DISTINCT from every merged loader on the OVERLAY
axis (counter-loader / stepped-counter-loader / branded-preloader /
type-forward-intro-loader are full-viewport curtains that cover the page
and lock scroll — the corner boot is DIEGETIC in-page chrome over a
visible index, sharing only the skip contract); in-engine-intro is ruled
on the seams (narrative-scene-one-loader is the story-cover handoff with
a READ-NOW boundary; in-engine-hero / in-engine-hud-fold are stage shells
whose poster swap is a state CUT — the intro is the engine's own arrival
CHOREOGRAPHY on one shared clock, stage law mirrored under its own
guard); idle-attract-auto-demo is an INPUT-state machine driving the
primary verb, DISTINCT from the décor idle channels, and a design-logic
gap by the playbook's own flag (NOT winner-canon — its header says so);
in-3d-dom-input-bridge is DISTINCT + COMPANION to raycast-object-state
(object axis vs world axis, both directions); journey-touch-momentum is
DISTINCT from smooth-scroll / horizontal-scroll-chain / drag-scrub-video
(a virtual scrub with fling momentum — no native scroll exists);
living-presence-layer is DISTINCT from the décor channels (live peer
data, capped 30, never faked). What the tests lock is each build's
LOAD-BEARING driven distinction: the overlay opened over the live index
(role=dialog, 6 inert siblings, Tab cycle close→mail→social→close, Esc
restoring flow/scroll/focus) while ?nojs left the footer standing in
flow; the corner boot rolled 21→99, held 99 for the real load, settled
100 + data-boot, digits exited translate3d(-110%,0,0) with scroll never
locked; the intro fed 121 arrive() frames 0.022→1 over ~2s with the
poster crossfading on the same clock, chrome live from frame one, ?rm
leaving the poster whole; the attract pass engaged at t≈5.06-5.09s of
real idle, drove a full 2π lap, and a real keydown cancelled a pass at
2.47s of 3s; the bridge drove the rover 450,300→466,308 from arrow taps
(the tap-nudge fix was drive-caught), saturated the touch joystick at
x=1 under the emulated touch device, and reflected a real mouse-over of
the scene beacon into cursor/attribute/status DOM state; the journey
flick carried 87→1397px with exponential decay and the position standing,
End gliding 0→4000 through 89 lerp frames, ?rm stepping 120/240 with
zero glide; the presence layer held the cap at exactly 30 of 40 offered
joins, drifted at rest, and degraded 30→0 marks on feed death (dead
ws:// endpoint = silent solo world)."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
COMPONENTS = REPO_ROOT / "skills" / "award-design" / "assets" / "components"
FORMS = COMPONENTS / "forms"

# interaction component file → the global its IIFE must export
RUNG8A_GLOBALS = {
    "idle-attract-auto-demo.js": "awardIdleAttractAutoDemo",
    "in-3d-dom-input-bridge.js": "awardIn3dDomInputBridge",
    "journey-touch-momentum.js": "awardJourneyTouchMomentum",
    "living-presence-layer.js": "awardLivingPresenceLayer",
}

# form id → (css, enhancer js, enhancer global)
RUNG8A_FORMS = {
    "about-overlay-footer": ("about-overlay-footer.css", "about-overlay-footer.js",
                             "awardAboutOverlayFooter"),
    "corner-counter-boot": ("corner-counter-boot.css", "corner-counter-boot.js",
                            "awardCornerCounterBoot"),
    "in-engine-intro": ("in-engine-intro.css", "in-engine-intro.js",
                        "awardInEngineIntro"),
}


def _src(name):
    return (COMPONENTS / name).read_text(encoding="utf-8")


def _form(name):
    return (FORMS / name).read_text(encoding="utf-8")


class TestRung8aLibraryContract(unittest.TestCase):
    """The structural contract every library component keeps (the
    test_component_library floor, applied before the manifest merge)."""

    def test_files_exist(self):
        for name in RUNG8A_GLOBALS:
            with self.subTest(file=name):
                self.assertTrue((COMPONENTS / name).is_file())
        for form_id, (css, js, _g) in RUNG8A_FORMS.items():
            with self.subTest(form=form_id):
                self.assertTrue((FORMS / css).is_file())
                self.assertTrue((FORMS / js).is_file())

    def test_iife_and_global_export(self):
        everything = dict(RUNG8A_GLOBALS)
        for _id, (_css, js, g) in RUNG8A_FORMS.items():
            everything["forms/" + js] = g
        for name, g in everything.items():
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("(function (global)", src)
                self.assertRegex(src, r"global\." + re.escape(g) + r"\s*=")

    def test_exposes_init_and_destroy(self):
        files = list(RUNG8A_GLOBALS) + ["forms/" + js for _c, js, _g in RUNG8A_FORMS.values()]
        for name in files:
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("function init", src)
                self.assertIn("destroy", src)

    def test_has_reduced_motion_contract(self):
        """Every artifact names its reduce answer — dormant, instant, or the
        deliberate state-machine-still-runs ruling."""
        files = list(RUNG8A_GLOBALS) + ["forms/" + js for _c, js, _g in RUNG8A_FORMS.values()]
        for name in files:
            with self.subTest(component=name):
                self.assertIn("reduced-motion", _src(name))

    def test_has_doc_comment_header(self):
        files = (list(RUNG8A_GLOBALS)
                 + ["forms/" + js for _c, js, _g in RUNG8A_FORMS.values()]
                 + ["forms/" + css for css, _j, _g in RUNG8A_FORMS.values()])
        for name in files:
            with self.subTest(file=name):
                self.assertTrue(_src(name).lstrip().startswith("/*"))

    def test_namespaced_stylesheet_injection(self):
        """Components that paint inject ONE namespaced stylesheet; the
        attract mode paints nothing (the scene owns the verb) and so
        injects nothing. Form enhancers inject nothing ever — their states
        live in the linked CSS."""
        for name in ("in-3d-dom-input-bridge.js", "journey-touch-momentum.js",
                     "living-presence-layer.js"):
            with self.subTest(component=name):
                self.assertRegex(_src(name), r"CSS_ID = 'ad-[a-z0-9-]+-css'")
        self.assertNotIn("createElement('style')", _src("idle-attract-auto-demo.js"))
        for _id, (_css, js, _g) in RUNG8A_FORMS.items():
            with self.subTest(form=_id):
                self.assertNotIn("createElement('style')", _src("forms/" + js))

    def test_form_enhancers_create_no_nodes(self):
        """The layering law: a form enhancer toggles attributes/styles on
        slot elements only (the intro's WebGL probe canvas is created but
        never appended)."""
        for _id, (_css, js, _g) in RUNG8A_FORMS.items():
            src = _src("forms/" + js)
            with self.subTest(form=_id):
                self.assertNotRegex(src, r"\bappendChild\b")
                self.assertNotRegex(src, r"\binnerHTML\s*=")
                self.assertNotRegex(src, r"\binsertAdjacentHTML\b")

    def test_no_bare_100vh(self):
        """svh/lvh/dvh only — a bare 100vh jumps under mobile chrome
        collapse."""
        files = (list(RUNG8A_GLOBALS)
                 + ["forms/" + js for _c, js, _g in RUNG8A_FORMS.values()]
                 + ["forms/" + css for css, _j, _g in RUNG8A_FORMS.values()])
        for name in files:
            with self.subTest(file=name):
                self.assertNotRegex(_src(name), r"100vh")


class TestRung8aFormDiscipline(unittest.TestCase):
    """The section-form floors (the test_section_forms contract, applied to
    all three rung-8A forms before the manifest merge)."""

    def test_form_root_selector_present(self):
        for form_id, (css, _js, _g) in RUNG8A_FORMS.items():
            with self.subTest(form=form_id):
                self.assertIn('[data-ad-form="' + form_id + '"]', _form(css))

    def test_form_ships_zero_motion(self):
        for form_id, (css, _js, _g) in RUNG8A_FORMS.items():
            src = _form(css)
            with self.subTest(form=form_id):
                self.assertNotIn("@keyframes", src)
                self.assertNotRegex(src, r"\banimation\s*:")
                self.assertNotRegex(src, r"\btransition\s*:")

    def test_no_js_floor_no_hidden_states(self):
        """A dead script leaves every form fully legible — no stylesheet
        ever hides a slot (the overlay close is authored `hidden` by the
        builder; every state hide is an enhancer inline write)."""
        for form_id, (css, _js, _g) in RUNG8A_FORMS.items():
            src = _form(css)
            with self.subTest(form=form_id):
                self.assertNotRegex(src, r"opacity:\s*0(?![.\d])")
                self.assertNotIn("visibility: hidden", src)
                self.assertNotIn("display: none", src)

    def test_form_styles_attributes_never_role_classes(self):
        """class-role uniformity rule: form state rides data attributes — a
        .ad-*/.is-* selector in a form stylesheet is class-role drift."""
        for form_id, (css, _js, _g) in RUNG8A_FORMS.items():
            src = _form(css)
            with self.subTest(form=form_id):
                self.assertNotRegex(src, r"\.ad-")
                self.assertNotRegex(src, r"\.is-")

    def test_the_intro_stage_is_svh(self):
        """The shared stage law (svh deliberately — dvh re-rasterizes an
        engine target on mobile URL-bar collapse). The other two forms are
        not stages: the overlay costume is inset 0, the boot is corner
        chrome."""
        self.assertIn("min-height: 100svh", _form("in-engine-intro.css"))


class TestAboutOverlayFooter(unittest.TestCase):
    """Aristide's About-overlay-as-footer: real page content in flow, the
    overlay costume an enhancer promotion over the live index."""

    def setUp(self):
        self.css = _form("about-overlay-footer.css")
        self.js = _form("about-overlay-footer.js")

    def test_resolves_the_recipes_missing_ref(self):
        self.assertIn("MISSING:about-overlay-footer", self.css)
        self.assertIn("type-index-aristide", self.css)

    def test_the_alias_ruling_rides_in_the_header(self):
        self.assertIn("DISTINCT", self.css)
        self.assertIn("close-panel", self.css)
        self.assertIn("valediction-footer", self.css)
        self.assertIn("gated-splash", self.css)

    def test_dual_mode_is_a_data_attribute_state(self):
        """Driven: data-mode='overlay' -> position:fixed inset 0 over the
        live index; the resting form is the in-flow footer (?nojs drove
        the anchor to it)."""
        self.assertIn('[data-ad-form="about-overlay-footer"][data-mode="overlay"]', self.css)
        self.assertIn("position: fixed", self.css)
        self.assertIn("section.setAttribute('data-mode', 'overlay');", self.js)

    def test_dialog_semantics_are_enhancer_writes(self):
        """Driven: role=dialog + aria-modal while open, removed on close —
        footer mode keeps plain section semantics."""
        self.assertIn("section.setAttribute('role', 'dialog');", self.js)
        self.assertIn("section.setAttribute('aria-modal', 'true');", self.js)
        self.assertIn("section.removeAttribute('aria-modal');", self.js)

    def test_siblings_go_inert_and_come_back(self):
        """Driven: 6 inert siblings while open, 0 after Esc."""
        self.assertIn("el.inert = true; inerted.push(el);", self.js)
        self.assertIn("inerted.forEach(function (el) { el.inert = false; });", self.js)

    def test_focus_trap_esc_and_focus_return(self):
        """Driven: Tab cycled close→mail→social→close; Esc closed and focus
        returned to the About trigger."""
        self.assertIn("e.key === 'Escape'", self.js)
        self.assertIn("if (e.shiftKey && document.activeElement === first) {", self.js)
        self.assertIn("lastTrigger.focus", self.js)

    def test_scroll_lock_is_scoped_to_the_overlay(self):
        """Driven: body overflow hidden while open, restored on close."""
        self.assertIn("document.body.style.overflow = 'hidden';", self.js)
        self.assertIn("document.body.style.overflow = prevBodyOverflow;", self.js)

    def test_close_is_authored_hidden_and_unhidden_by_js(self):
        """The gated-splash law inverted onto one control: the close means
        nothing in footer flow, so the builder authors it `hidden` and the
        enhancer un-hides it only for the overlay costume."""
        self.assertIn('<button data-slot="close" type="button" hidden>', self.css)
        self.assertIn("closeBtn.hidden = false;", self.js)
        self.assertIn("closeBtn.hidden = true;", self.js)

    def test_typeset_walls_never_split_an_entry(self):
        """Drive-caught: the ledger's column flow split 'Site of the Month
        ×4' across columns — break-inside pins every wall entry."""
        self.assertIn("break-inside: avoid", self.css)
        self.assertIn("columns: 2", self.css)


class TestCornerCounterBoot(unittest.TestCase):
    """Aristide's diegetic corner boot: the count is HUD chrome over a
    visible index — never a curtain."""

    def setUp(self):
        self.css = _form("corner-counter-boot.css")
        self.js = _form("corner-counter-boot.js")

    def test_resolves_the_recipes_missing_ref(self):
        self.assertIn("MISSING:corner-counter-boot", self.css)
        self.assertIn("type-index-aristide", self.css)

    def test_the_overlay_axis_ruling_rides_in_the_header(self):
        """DISTINCT from all four merged loaders — they cover the page;
        this covers nothing."""
        self.assertIn("DIEGETIC", self.css)
        self.assertIn("counter-loader", self.css)
        self.assertIn("stepped-counter-loader", self.css)
        self.assertIn("branded-preloader", self.css)
        self.assertIn("type-forward-intro-loader", self.css)

    def test_diegetic_means_no_overlay_and_no_scroll_lock(self):
        """Driven: the index stayed visible and scroll unlocked through the
        whole roll — the chrome is pointer-events:none and the enhancer
        never touches body overflow."""
        self.assertIn("pointer-events: none", self.css)
        self.assertNotIn("body.style.overflow", self.js)

    def test_the_honest_roll_holds_for_the_real_load(self):
        """Driven: eased 21→99 over the floor, held at 99 (two samples)
        until window load, then 100."""
        self.assertIn("Math.min(99, Math.round(eased * 99))", self.js)
        self.assertIn("if (t >= 1 && loaded) { rafId = 0; exit(); return; }", self.js)
        self.assertIn("count.textContent = '100';", self.js)

    def test_the_digit_exit_is_the_carried_aristide_read(self):
        """translate3d(-110%,0,0) — the reference's winner-verified read,
        playbook-flagged unverified, encoded as the default; the count line
        clips so the exit leaves the frame, not the page."""
        self.assertIn("translate3d(-110%,0,0)", self.js)
        self.assertIn("overflow: clip", self.css)

    def test_the_settle_hide_is_an_inline_write(self):
        self.assertIn("el.style.visibility = 'hidden';", self.js)
        self.assertIn("section.setAttribute('data-boot', 'done');", self.js)

    def test_skip_contract_and_resting_truth(self):
        """Driven under ?rm: the authored '100' stood, data-boot='done',
        onDone at once — the authored text is the resting truth a dead
        script shows."""
        self.assertIn("var skipped = reduce() ||", self.js)
        self.assertIn("count.textContent = restingText;", self.js)

    def test_corner_variants(self):
        for corner in ("tl", "tr", "bl", "br"):
            self.assertIn('[data-corner="' + corner + '"]', self.css)


class TestInEngineIntro(unittest.TestCase):
    """Igloo's arrival: one clock drives the engine's choreography and the
    poster's crossfade — no cut, no loader boundary."""

    def setUp(self):
        self.css = _form("in-engine-intro.css")
        self.js = _form("in-engine-intro.js")

    def test_resolves_the_recipes_missing_ref(self):
        self.assertIn("MISSING:in-engine-intro", self.css)
        self.assertIn("engine-world-igloo", self.css)

    def test_the_seam_rulings_ride_in_the_header(self):
        self.assertIn("DISTINCT", self.css)
        self.assertIn("narrative-scene-one-loader", self.css)
        self.assertIn("in-engine-hero", self.css)
        self.assertIn("in-engine-hud-fold", self.css)

    def test_the_shared_mount_gate_law(self):
        """Reduce / Save-Data / no WebGL -> the poster fold stands (driven
        under ?rm: no canvas, no data-engine, zero arrive calls, poster at
        opacity 1)."""
        self.assertIn("if (!mount || reduce() || saveData() || !webgl()) {", self.js)

    def test_ready_hands_over_an_arrive_driver(self):
        """The seam vs the stage shells: ready(arrive), not ready() — the
        engine maps one progress value onto its own choreography (driven:
        121 frames, 0.022→1)."""
        self.assertIn("unit.arrive = typeof arrive === 'function' ? arrive : null;", self.js)
        self.assertIn("if (unit.arrive) unit.arrive(p);", self.js)

    def test_poster_and_choreography_share_one_clock(self):
        """Driven: poster opacity decayed 0.816→0.001 across the same
        window the arrive frames advanced — then the inline hide and the
        live state."""
        self.assertIn("unit.poster.style.opacity = String(1 - p);", self.js)
        self.assertIn("unit.poster.style.visibility = 'hidden';", self.js)
        self.assertIn("unit.section.setAttribute('data-engine', 'live');", self.js)
        self.assertIn("setAttribute('data-engine', 'arriving');", self.js)

    def test_the_stage_gates_the_pointer_on_live(self):
        self.assertIn('[data-engine="live"]', self.css)
        self.assertIn("pointer-events: auto", self.css)
        self.assertIn("pointer-events: none", self.css)

    def test_a_hidden_tab_pauses_the_arrival(self):
        self.assertIn("document.addEventListener('visibilitychange', onVis);", self.js)

    def test_own_guard_never_the_shells(self):
        """The stage law is mirrored, not delegated — a page carrying the
        intro and a shell needs both enhancers."""
        self.assertIn("__adInEngineIntro", self.js)
        self.assertNotIn("__adInEngineHudFold", self.js)
        self.assertNotIn("__adInEngineHero", self.js)

    def test_the_default_is_declared_a_default(self):
        """arriveMs 2000 is a default, not a measured winner value — the
        header says so (Igloo's timings were never published)."""
        self.assertIn("DEFAULT, not a measured winner value", self.js)


class TestIdleAttractAutoDemo(unittest.TestCase):
    """The verb-teaching attract mode: an input-state machine, not a décor
    loop — and a design-logic gap, presented as such."""

    def setUp(self):
        self.src = _src("idle-attract-auto-demo.js")

    def test_the_non_canon_flag_rides_in_the_header(self):
        """The playbook's own lower-confidence flag is preserved — never
        presented as winner law."""
        self.assertIn("NOT winner-canon", self.src)
        self.assertIn("30% Usability", self.src)

    def test_the_alias_ruling_rides_in_the_header(self):
        self.assertIn("ambient-idle", self.src)
        self.assertIn("perpetual-tile-machines", self.src)
        self.assertIn("INPUT-STATE MACHINE", self.src)

    def test_real_input_cancels_a_running_pass(self):
        """Driven: a keydown at 2.47s into a 3s pass ended it with
        completed:false — the visitor always wins the wheel."""
        self.assertIn(
            "var INPUT_EVENTS = ['pointerdown', 'pointermove', 'wheel', 'keydown', "
            "'touchstart', 'scroll'];", self.src)
        self.assertIn("if (running) settle(false);", self.src)

    def test_engagement_is_capped_and_re_armed(self):
        """Driven: two passes then silence (maxRuns default 2 — teach
        twice, then trust)."""
        self.assertIn("opts.maxRuns != null ? +opts.maxRuns : 2;", self.src)
        self.assertIn("runs >= maxRuns", self.src)

    def test_gated_by_io_and_visibility(self):
        """A hidden tab or off-screen scene never performs; going hidden
        mid-pass cancels."""
        self.assertIn("IntersectionObserver", self.src)
        self.assertIn("if (document.hidden && running) settle(false);", self.src)

    def test_reduce_is_fully_dormant(self):
        """Unrequested motion is exactly what reduce forbids — the static
        anchor carries discoverability alone."""
        self.assertIn("if (reduce()) return { destroy: function () {} };", self.src)


class TestIn3dDomInputBridge(unittest.TestCase):
    """Bruno's recreated DOM input: the world axis, both directions."""

    def setUp(self):
        self.src = _src("in-3d-dom-input-bridge.js")

    def test_the_winner_and_companion_ruling_ride_in_the_header(self):
        self.assertIn("Bruno", self.src)
        self.assertIn("raycast-object-state", self.src)
        self.assertIn("COMPANION", self.src)

    def test_the_application_focus_contract(self):
        """A real tab stop with role=application — keys act only while the
        surface holds focus."""
        self.assertIn("surface.setAttribute('role', 'application');", self.src)
        self.assertIn("if (document.activeElement !== surface) return;", self.src)

    def test_a_discrete_key_tap_still_nudges(self):
        """Drive-caught: a down+up inside one frame produced ZERO frames
        until the immediate nudge landed (then driven: 3 right + 2 down
        taps moved the rover 450,300→466,308)."""
        self.assertIn("if (!e.repeat) {", self.src)
        self.assertIn("onFrame({ x: KEYS[e.code][0], y: KEYS[e.code][1] });", self.src)

    def test_touch_drag_is_the_virtual_joystick(self):
        """Touch pointers only (mouse drags are engine territory) — driven
        under the emulated touch device: a 48px drag saturated x=1."""
        self.assertIn("if (e.pointerType !== 'touch' || !armed || drag) return;", self.src)
        self.assertIn("try { surface.setPointerCapture(e.pointerId); } catch (err) {}", self.src)

    def test_the_world_owns_the_wheel(self):
        self.assertIn("surface.addEventListener('wheel', onWheel, { passive: false });", self.src)
        self.assertIn("if (e.deltaMode === 1) d *= 16;", self.src)

    def test_gamepad_polls_with_a_dead_zone(self):
        self.assertIn("var DEAD_ZONE = 0.15;", self.src)
        self.assertIn("getGamepads", self.src)
        self.assertIn("gamepadconnected", self.src)

    def test_the_reverse_direction_reaches_the_dom(self):
        """Driven: a real mouse move over the scene beacon landed
        data-ad-bridge-hover + cursor:pointer + the status text."""
        self.assertIn("data-ad-bridge-hover", self.src)
        self.assertIn("statusEl.textContent", self.src)

    def test_the_engine_settles_on_one_zero_frame(self):
        """The last channel dying emits exactly one {0,0} frame, then the
        loop sleeps — zero per-frame work at rest."""
        self.assertIn("if (!wasZero) { onFrame({ x: 0, y: 0 }); wasZero = true; }", self.src)

    def test_the_discoverable_anchor_arms_the_bridge(self):
        self.assertIn("data-ad-bridge-start", self.src)
        self.assertIn("surface.focus({ preventScroll: true });", self.src)


class TestJourneyTouchMomentum(unittest.TestCase):
    """The no-native-scroll journey scrub: wheel, touch and keyboard feed
    one position; a fling becomes decaying momentum."""

    def setUp(self):
        self.src = _src("journey-touch-momentum.js")

    def test_the_winners_and_the_defaults_caveat_ride_in_the_header(self):
        self.assertIn("Lusion v3", self.src)
        # the studio name wraps across header lines — match the tail
        self.assertIn("Development Studio", self.src)
        self.assertIn("a DEFAULT, not a measured", self.src)

    def test_the_alias_ruling_rides_in_the_header(self):
        self.assertIn("smooth-scroll", self.src)
        self.assertIn("horizontal-scroll-chain", self.src)
        self.assertIn("drag-scrub-video", self.src)

    def test_no_native_scroll_exists_and_none_is_created(self):
        """touch-action:none + wheel/touchmove preventDefault — the journey
        owns the gesture; there is nothing to fall back to."""
        self.assertIn("touch-action:none", self.src)
        self.assertIn("surface.addEventListener('wheel', onWheel, { passive: false });", self.src)
        self.assertIn("surface.addEventListener('touchmove', onTouchMove, { passive: false });",
                      self.src)

    def test_touch_feeds_the_same_scrub_as_the_wheel(self):
        """Driven: the position tracked the finger 0→87px through the
        gesture — the same clamp/target the wheel writes."""
        self.assertIn("target = clamp(target + dy * touchRate);", self.src)
        self.assertIn("target = clamp(target + d * wheelRate);", self.src)

    def test_the_fling_becomes_decaying_momentum(self):
        """Driven: release at 87px carried to 1397px over ~1.9s, deltas
        +207/+416/+294/+178/+102/+56/+31/+17/+7/+2 — exponential decay
        from the ~80ms release-velocity window."""
        self.assertIn("var SAMPLE_MS = 80;", self.src)
        self.assertIn("v *= Math.pow(decay, f);", self.src)
        self.assertIn("the scrub position survives the gesture", self.src)

    def test_the_camera_lerp_is_time_corrected(self):
        """Driven: End glided 0→4000 through 89 decelerating frames."""
        self.assertIn("pos += (target - pos) * (1 - Math.pow(1 - lerp, f));", self.src)

    def test_keyboard_rides_the_same_scrub(self):
        self.assertIn("e.code === 'PageDown'", self.src)
        self.assertIn("target = length", self.src)

    def test_reduce_steps_but_stays_navigable(self):
        """Driven under ?rm: two ArrowDown -> exactly 120/240, zero glide
        frames — interaction is not decoration."""
        self.assertIn("pos = target; v = 0; emit();", self.src)

    def test_hidden_freezes_the_scrub_in_place(self):
        """The position survives a hidden tab — never resets."""
        self.assertIn("if (!onScreen || document.hidden) return;", self.src)
        self.assertIn("IntersectionObserver", self.src)


class TestLivingPresenceLayer(unittest.TestCase):
    """Bruno's Whispers as machinery: live peer data, capped, degradable —
    never faked."""

    def setUp(self):
        self.src = _src("living-presence-layer.js")

    def test_the_winners_ride_in_the_header(self):
        self.assertIn("Whispers", self.src)
        self.assertIn("Resn", self.src)
        self.assertIn("Messenger", self.src)

    def test_the_alias_ruling_rides_in_the_header(self):
        self.assertIn("ambient-idle", self.src)
        self.assertIn("perpetual-tile-machines", self.src)
        self.assertIn("LIVE PEER DATA", self.src)

    def test_the_cap_is_the_bruno_read(self):
        """Driven: 40 joins offered, exactly 30 marks stood."""
        self.assertIn("opts.max != null ? +opts.max : 30;", self.src)
        self.assertIn("count >= max", self.src)

    def test_presence_is_never_faked(self):
        """The feed dying clears to the solo world (driven: kill -> 30→0
        marks; a dead ws:// endpoint left a silent solo world)."""
        self.assertIn("presence is never faked", self.src)
        self.assertIn("clearPeers(); // the solo world", self.src)

    def test_the_source_contract_can_report_its_own_death(self):
        """connect(onMessage, onDown) — an injected feed degrades like a
        socket close (the gap surfaced driving the harness feed-kill)."""
        self.assertIn("socket = opts.source.connect(onMessage, function () {", self.src)

    def test_feed_text_is_content_never_markup(self):
        """Moderation is a server duty; the client never parses markup."""
        self.assertIn("tag.textContent = [p.flag, p.label].filter(Boolean).join(' ');", self.src)
        self.assertNotIn("innerHTML", self.src)

    def test_the_layer_is_decor(self):
        self.assertIn("layer.setAttribute('aria-hidden', 'true');", self.src)
        self.assertIn("pointer-events:none", self.src)

    def test_socket_and_drift_are_gated(self):
        """Socket connects only on-screen + visible; hidden closes it; the
        drift rAF runs only while marks exist."""
        self.assertIn("IntersectionObserver", self.src)
        self.assertIn("if (document.hidden) disconnect();", self.src)

    def test_reduce_places_instantly_and_never_wanders(self):
        """Driven under ?rm: transforms frozen over 1.3s, updates landing
        instantly — presence is information, the drift is decoration."""
        self.assertIn("if (still) return;", self.src)
        self.assertIn("if (still) place(q, true);", self.src)


if __name__ == "__main__":
    unittest.main()
