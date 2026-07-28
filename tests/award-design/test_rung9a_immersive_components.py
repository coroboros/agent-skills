"""award-design completeness program — rung 9A (immersive cluster, first half).

Five builds, all components: telemetry-readout, nav-context-ink,
procession-wayfinding, brand-object-assembly-loader, pointer-scene-reveal.
Two are corpse-derived (the campaign's own record, not winner citations):
telemetry-readout is the scroll-progress HUD three dead builds each
re-invented (MARE alt/phase readers, CALDERA acquiring-fix HUD, AVALANCHE
signal rail — the library-quality boundary verdict promotes the recurring
invention); nav-context-ink is the section-driven nav ink swap (CALDERA
footerNavSwap is-over-light, AVALANCHE data-nav-phase), IO-based and
zero-flip compliant with show-on-scroll-up-nav's accumulator — it PUBLISHES
data-ad-nav-ink and never touches the hide/show machine. Alias rulings on
evidence, written into each header: procession-wayfinding is DISTINCT from
diegetic-nav (steering instrument with a dragged avatar scrubbing the scroll
vs read-only orientation + jump links), from telemetry-readout (continuous
instrument vs discrete index) and from the corpses' trace rails (riding
readout, no jump targets); brand-object-assembly-loader is DISTINCT from
branded-preloader (mark beside a readout, recedes), svg-path-fill-loader
(fill-as-gauge, dissolves in place) and flip-handoff-loader (mark travels
into the header) — here the parts ARE the instrument, the exit is an
ellipse WIPE and the node UNMOUNTS; pointer-scene-reveal is DISTINCT from
raycast-object-state (per-MESH verbs — the object axis) and pointer-parallax
(DOM-layer depth) — one continuous scene-wide parameter drives the medium.

What the tests lock is each build's LOAD-BEARING driven distinction. The
telemetry HUD was scrubbed through a full descent with values sampled at
stations p=0/.25/.5/.75/1 (alt 2,400→1,733→1,066→400→0 on the piecewise map;
phase Approach→Descent→Contact; the coordinate resolve completing at p≥0.7;
the rail read's dip map 100→72→44→64→96) and back up (identical values at
identical stations — welded both directions); ?rm rendered final statics
(alt 0, Contact, rail full) that scrolling never moved. Two drive-caught
fixes are locked: the rail carries NO overflow clip (it ate the riding
'SIGNAL n%' read whole) and its defaults sit in :where() (a bare
position:relative, injected late, beat the harness's position:absolute and
dropped the rail a viewport out of place). The ink swap was driven across
real section boundaries UNDER the accumulator nav: a 121-frame ±3px jitter
burst straddling a boundary produced ZERO ink flips and ZERO hide/show
flips (the two-line agreement machine holds inside its 2·hys dead zone);
the glide back up committed exactly one write ('dark'); the published
attribute retargets the whole costume — ink AND the is-scrolled ground
(drive-caught: ink alone left dark text on the dark grounded bar over a
light chapter). The wayfinding advanced 0→1→2→3→4 (counter 01/05→05/05,
fill 0.086→0.886) and receded symmetrically to identical station values; a
native click on LASERS glided to #lasers with active=3 and no intercepted
handler; links are real tab stops; ?rm still tracks instantly. The assembly
loader's 271-frame flight log: part0 at t=297ms measured -13px against the
-13.6px eased prediction, aria-valuenow 14→100, the ellipse wipe collapsing
from ellipse(142% 142%) over 48 frames from t=2298, the node GONE from the
DOM at t=3098 with scroll restored and onDone at 3171ms; ?rm removed the
node at 76ms. The pointer reveal seated the lens exactly at entry
(NDC -0.5,+0.5), held the registration invariant lensX+detailX=0.00 at
every sweep sample while the lerp trailed 82→125px, settled to center on
leave (550.3 vs 550 expected) with the rAF loop verifiably stopped, stayed
fully dormant under ?touch and ?rm, and the engine channel emitted 94
lerped points ending (0.001,-0.001,engaged=false) before stopping."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
COMPONENTS = REPO_ROOT / "skills" / "award-design" / "assets" / "components"

# component file → the global its IIFE must export
RUNG9A_GLOBALS = {
    "telemetry-readout.js": "awardTelemetryReadout",
    "nav-context-ink.js": "awardNavContextInk",
    "procession-wayfinding.js": "awardProcessionWayfinding",
    "brand-object-assembly-loader.js": "awardBrandObjectAssemblyLoader",
    "pointer-scene-reveal.js": "awardPointerSceneReveal",
}

# the painters — one namespaced stylesheet each; nav-context-ink paints nothing
RUNG9A_CSS_IDS = {
    "telemetry-readout.js": "ad-telemetry-readout-css",
    "procession-wayfinding.js": "ad-procession-wayfinding-css",
    "brand-object-assembly-loader.js": "ad-brand-object-assembly-loader-css",
    "pointer-scene-reveal.js": "ad-pointer-scene-reveal-css",
}


def _src(name):
    return (COMPONENTS / name).read_text(encoding="utf-8")


class TestRung9aLibraryContract(unittest.TestCase):
    """The structural contract every library component keeps (the
    test_component_library floor, applied before the manifest merge)."""

    def test_files_exist(self):
        for name in RUNG9A_GLOBALS:
            with self.subTest(file=name):
                self.assertTrue((COMPONENTS / name).is_file())

    def test_iife_and_global_export(self):
        for name, g in RUNG9A_GLOBALS.items():
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("(function (global)", src)
                self.assertRegex(src, r"global\." + re.escape(g) + r"\s*=")

    def test_exposes_init_and_destroy(self):
        for name in RUNG9A_GLOBALS:
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("function init", src)
                self.assertIn("destroy", src)

    def test_has_reduced_motion_contract(self):
        """Every artifact names its reduce answer — static finals (telemetry),
        state-still-runs (ink, wayfinding), never-shows (loader), or fully
        dormant (pointer reveal)."""
        for name in RUNG9A_GLOBALS:
            with self.subTest(component=name):
                self.assertIn("reduced-motion", _src(name))

    def test_has_doc_comment_header(self):
        for name in RUNG9A_GLOBALS:
            with self.subTest(file=name):
                self.assertTrue(_src(name).lstrip().startswith("/*"))

    def test_namespaced_stylesheet_injection(self):
        """Painters inject ONE namespaced stylesheet; nav-context-ink only
        publishes an attribute the builder's CSS consumes — it never paints,
        so it never injects."""
        for name, css_id in RUNG9A_CSS_IDS.items():
            with self.subTest(component=name):
                self.assertIn("CSS_ID = '" + css_id + "'", _src(name))
        self.assertNotIn("createElement('style')", _src("nav-context-ink.js"))

    def test_no_bare_100vh(self):
        """svh/lvh/dvh only — a bare 100vh jumps under mobile chrome
        collapse."""
        for name in RUNG9A_GLOBALS:
            with self.subTest(file=name):
                self.assertNotRegex(_src(name), r"100vh")


class TestTelemetryReadout(unittest.TestCase):
    """The corpse-derived HUD instrument: piecewise maps, phase thresholds,
    the acquiring-fix resolve, and a transform-only rail welded to progress."""

    def setUp(self):
        self.src = _src("telemetry-readout.js")

    def test_corpse_derived_evidence_in_header(self):
        for token in ("MARE", "CALDERA", "AVALANCHE", "promotes a pattern into the library"):
            self.assertIn(token, self.src)

    def test_piecewise_map_and_phase_grammar(self):
        self.assertIn("data-tel-map", self.src)
        self.assertIn("data-tel-phases", self.src)
        self.assertIn("data-tel-resolve", self.src)

    def test_resolve_masks_alphanumerics_only(self):
        """CALDERA's law: acquiring a fix, not noise — punctuation and
        spacing always stand."""
        self.assertIn("/[0-9a-zA-Z]/", self.src)

    def test_locale_int_format_is_the_mare_fmt(self):
        self.assertIn("toLocaleString('en-US')", self.src)

    def test_rail_is_transform_only(self):
        """The corpses wrote style.height/top; the component promotes the
        rail to compositor-clean transforms — and never writes height."""
        self.assertIn("scaleY(", self.src)
        self.assertIn("translate3d(", self.src)
        self.assertNotRegex(self.src, r"style\.height\s*=")
        self.assertNotRegex(self.src, r"style\.top\s*=")

    def test_rail_has_no_overflow_clip(self):
        """Drive-caught: overflow:hidden on the rail ate the riding
        'SIGNAL n%' read whole. The fill (inset:0, scale ≤ 1) needs no clip."""
        self.assertNotRegex(self.src, r"data-tel-rail[^{]*\]\{[^}]*overflow")

    def test_rail_defaults_are_zero_specificity(self):
        """Drive-caught: a bare [data-tel-rail]{position:relative}, injected
        after the page stylesheet, beat the builder's position:absolute at
        equal specificity — the defaults live in :where()."""
        self.assertIn(":where([data-tel-rail])", self.src)

    def test_writes_are_dirty_checked(self):
        self.assertIn("!== last", self.src)

    def test_reduce_renders_final_static_values(self):
        """The build order's imposed verdict: under reduce the HUD stands at
        its destination — apply(1) once, no scroll binding."""
        self.assertIn("apply(inst, 1)", self.src)

    def test_off_screen_instruments_park(self):
        self.assertIn("IntersectionObserver", self.src)
        self.assertIn("parked", self.src)


class TestNavContextInk(unittest.TestCase):
    """The publish-only ink swap: IO-based, zero-flip by the two-line
    agreement machine, never touching the accumulator's axes."""

    def setUp(self):
        self.src = _src("nav-context-ink.js")

    def test_corpse_derived_evidence_in_header(self):
        for token in ("CALDERA", "footerNavSwap", "is-over-light",
                      "AVALANCHE", "data-nav-phase"):
            self.assertIn(token, self.src)

    def test_publishes_the_attribute_only(self):
        self.assertIn("setAttribute('data-ad-nav-ink'", self.src)

    def test_never_writes_a_class(self):
        """The accumulator machine owns is-hidden / is-scrolled; this
        component must not carry a single classList write."""
        self.assertNotIn("classList.add", self.src)
        self.assertNotIn("classList.remove", self.src)
        self.assertNotIn("classList.toggle", self.src)

    def test_io_based_with_two_line_hysteresis(self):
        """Two 1px-line observers, hys px apart; the ink commits only when
        both lines agree — the dead zone that made the ±3px jitter burst
        produce zero flips."""
        self.assertIn("IntersectionObserver", self.src)
        self.assertIn("ioLow", self.src)
        self.assertIn("ioHigh", self.src)
        self.assertIn("--ad-ink-hys", self.src)
        self.assertIn("tl && tl === th", self.src)

    def test_sync_seed_for_first_paint(self):
        """A deep link paints the correct ink before any observer callback."""
        self.assertIn("getBoundingClientRect", self.src)

    def test_destroy_removes_the_attribute(self):
        self.assertIn("removeAttribute('data-ad-nav-ink')", self.src)

    def test_header_documents_the_whole_costume(self):
        """Drive-caught: retargeting ink alone leaves the accumulator's dark
        is-scrolled ground under dark ink — the header must show the surface
        swap too."""
        self.assertIn("is-scrolled", self.src)


class TestProcessionWayfinding(unittest.TestCase):
    """The discrete orientation index for the scroll-jacked procession:
    real links, mounted chrome, a zero-flip active accumulator."""

    def setUp(self):
        self.src = _src("procession-wayfinding.js")

    def test_winner_evidence_in_header(self):
        self.assertIn("Cartier", self.src)
        self.assertIn("Primland", self.src)

    def test_alias_rulings_in_header(self):
        for token in ("diegetic-nav", "telemetry-readout", "trace-rail"):
            self.assertIn(token, self.src)

    def test_stays_a_nav_never_intercepts(self):
        """Real anchors jump natively — drive-verified: the LASERS click
        navigated by hash with no handler in the way."""
        self.assertNotIn("preventDefault", self.src)
        self.assertNotIn("addEventListener('click'", self.src)

    def test_active_is_viewport_center_accumulator(self):
        """The diegetic-nav law: active = the last stop whose target the
        viewport CENTER has passed — a pure function of scrollY."""
        self.assertIn("innerHeight / 2", self.src)
        self.assertIn("setAttribute('data-ad-wf-active'", self.src)
        self.assertIn("setAttribute('aria-current', 'true')", self.src)

    def test_mounted_chrome_is_decor(self):
        self.assertIn("setAttribute('data-wf-rail'", self.src)
        self.assertIn("setAttribute('aria-hidden', 'true')", self.src)

    def test_rail_defaults_are_zero_specificity(self):
        self.assertIn(":where([data-wf-rail])", self.src)

    def test_counter_is_zero_padded(self):
        self.assertIn("padStart", self.src)

    def test_reduce_strips_the_one_transition(self):
        self.assertIn("@media (prefers-reduced-motion:reduce)", self.src)


class TestBrandObjectAssemblyLoader(unittest.TestCase):
    """The Lando loader: parts assemble as the instrument, ellipse wipe,
    true unmount — distinct from all three sibling loaders."""

    def setUp(self):
        self.src = _src("brand-object-assembly-loader.js")

    def test_resolves_the_recipes_missing_ref(self):
        self.assertIn("MISSING:brand-object-assembly-loader", self.src)
        self.assertIn("Lando Norris", self.src)
        self.assertIn("portrait-procession", self.src)

    def test_alias_rulings_against_all_three_loaders(self):
        for token in ("branded-preloader", "svg-path-fill-loader",
                      "flip-handoff-loader"):
            self.assertIn(token, self.src)

    def test_honest_progress_law(self):
        """Eases toward 90%, holds until the real window load (and the
        optional track source), then settles — the library's loader law."""
        self.assertIn("EASE_TO = 0.9", self.src)
        self.assertIn("'load'", self.src)
        self.assertIn("onProgress", self.src)

    def test_ellipse_wipe(self):
        self.assertIn("ellipse(142% 142% at 50% 50%)", self.src)
        self.assertIn("ellipse(0% 0% at 50% 50%)", self.src)

    def test_the_unmount(self):
        """Drive-verified gone from the DOM at t=3098ms — removed, never
        hidden."""
        self.assertIn("scene.remove()", self.src)

    def test_no_js_floor_authored_hidden(self):
        """The scene is authored `hidden`; JS un-hides it — a dead script
        never covers the page."""
        self.assertIn("removeAttribute('hidden')", self.src)

    def test_scroll_lock_is_restored(self):
        self.assertIn("prevOverflow", self.src)
        self.assertIn("overflow = 'hidden'", self.src)

    def test_deterministic_scatter(self):
        """The same mark assembles the same way every load — no randomness."""
        self.assertNotRegex(self.src, r"Math\.random\s*\(")
        self.assertIn("data-part-from", self.src)

    def test_raf_clock_pauses_when_hidden(self):
        self.assertIn("visibilitychange", self.src)

    def test_session_storage_never_throws(self):
        self.assertIn("try {", self.src)
        self.assertIn("sessionStorage", self.src)


class TestPointerSceneReveal(unittest.TestCase):
    """The pointer driving the medium: lens channel registered to the base
    plate, engine channel in NDC, dormant on touch and under reduce."""

    def setUp(self):
        self.src = _src("pointer-scene-reveal.js")

    def test_winner_evidence_in_header(self):
        self.assertIn("Hubtown", self.src)
        self.assertIn("ERA", self.src)

    def test_alias_rulings_in_header(self):
        self.assertIn("raycast-object-state", self.src)
        self.assertIn("pointer-parallax", self.src)

    def test_fine_pointer_gate(self):
        self.assertIn("(any-hover: hover) and (pointer: fine)", self.src)

    def test_dormant_ladder(self):
        """Touch and reduce never bind — drive-verified: no lens, hidden
        detail, zero onPoint emits under both profiles."""
        self.assertIn("if (!fine() || reduce())", self.src)

    def test_engine_channel_is_ndc_y_up(self):
        """The Three raycaster convention — drive-verified enter at exactly
        (-0.5, +0.5) for a (150,100) pointer in a 600x400 root."""
        self.assertIn("-((inst.y / inst.h) * 2 - 1)", self.src)

    def test_lens_counter_translate_registration(self):
        """The compositor-clean reveal: the detail counter-translates so the
        plates stay registered — drive-verified lensX+detailX=0.00 at every
        sweep sample."""
        self.assertIn("radius - inst.x", self.src)
        self.assertIn("radius - inst.y", self.src)

    def test_root_is_clipped(self):
        """The clip law — the lens never bleeds past the hero's bound."""
        self.assertIn("[data-ad-psr]{position:relative;overflow:hidden;}", self.src)

    def test_detail_authored_hidden_and_restored(self):
        """Content-visible at rest: the detail is authored `hidden`, the
        component un-hides it into the lens, destroy re-hides and reseats it."""
        self.assertIn("detail.removeAttribute('hidden')", self.src)
        self.assertIn("setAttribute('hidden', '')", self.src)

    def test_loop_runs_only_engaged_or_settling(self):
        """Drive-verified: the transform froze 300ms after settle — zero
        idle work."""
        self.assertIn("inst.running = false", self.src)


if __name__ == "__main__":
    unittest.main()
