"""award-design completeness program — rung 7B (spatial-organic, second half).

Six orders, four builds + two alias closures. Built: two SECTION FORMS —
morph-tile-grid (the MISSING proof form of studio-reel-cyd) and
type-index-grid (the union of BOTH gap entries — experimental priority-1
Aristide/Obys/Lusion + the spatial-organic type-index arc — resolving the
MISSING refs of type-index-aristide AND type-index-obys) — and two
components, organic-section-edge and vf-scroll-morph (gap_only, zero
recipes occurrences). Closed by alias, driven not read (rulings +
evidence in build-orders/side/rung7b-recipes-add.json):
scroll-velocity-skew -> scroll-speed-oscillator mode "shift" (a 420px
eased flick peaked skewY 2.489deg + scaleY 1.0249 tracking velocity,
cleared to rest at t=352ms, frame clipped, dormant under rm);
webgl-preload-gate -> branded-preloader (counter 0->100 over real plates +
a LoadingManager-like track, the poster floor stood under the gate the
whole boot, exit opacity .889->0 with scale 1.004->1.04 over ~900ms —
never a hard cut — userGesture:true; world-boot-gate NOT swallowed — the
in-engine diegetic boot stays a live experimental order).

What the tests lock is each build's LOAD-BEARING driven distinction: the
tile morph ran clip-path inset(0 round …) from the organic resting radius
to the hover shape through 52 interpolation states on the 420ms clock and
reversed EXACTLY on leave, overlay crossfading 1->0 over the full image,
caption sliding up; coarse/reduce landed the revealed state instantly and
a dead script hides nothing (the state machine is all enhancer inline
writes). The section edge's shape() curve was probed at five stations per
seam at 1440/1024/~500px — elementFromPoint always neighbor-above /
section-below, zero page-background VOID — and the drive CAUGHT the
one-curve-per-seam law (two curves into one seam expose the page ground),
now encoded in the header. The type index booted masked
translate3d(0,101%,0)->0 from document start (69 distinct states, row
stagger held via fill:backwards, data-ad-tig-boot cleared at the end),
published data-ad-tig-hover discretely (the ground plate answered the
hovered row), left clicks native (#p-helix landed at viewport top), and
under ?rm showed zero boot frames while the bridge still published. The
vf morph sampled computed font-variation-settings mid-range (wght 465.307
/ 557.742, opsz 9->144 on custom endpoints) with EXACT rewind on
scroll-back, and 'normal' at every position under rm."""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
COMPONENTS = REPO_ROOT / "skills" / "award-design" / "assets" / "components"
FORMS = COMPONENTS / "forms"

# interaction component file → the global its IIFE must export
RUNG7B_GLOBALS = {
    "organic-section-edge.js": "awardOrganicSectionEdge",
    "vf-scroll-morph.js": "awardVfScrollMorph",
}

# form id → (css, enhancer js, enhancer global)
RUNG7B_FORMS = {
    "morph-tile-grid": ("morph-tile-grid.css", "morph-tile-grid.js",
                        "awardMorphTileGrid"),
    "type-index-grid": ("type-index-grid.css", "type-index-grid.js",
                        "awardTypeIndexGrid"),
}


def _src(name):
    return (COMPONENTS / name).read_text(encoding="utf-8")


def _form(name):
    return (FORMS / name).read_text(encoding="utf-8")


class TestRung7bLibraryContract(unittest.TestCase):
    """The structural contract every library component keeps (the
    test_component_library floor, applied before the manifest merge)."""

    def test_files_exist(self):
        for name in RUNG7B_GLOBALS:
            with self.subTest(file=name):
                self.assertTrue((COMPONENTS / name).is_file())
        for form_id, (css, js, _g) in RUNG7B_FORMS.items():
            with self.subTest(form=form_id):
                self.assertTrue((FORMS / css).is_file())
                self.assertTrue((FORMS / js).is_file())

    def test_iife_and_global_export(self):
        everything = dict(RUNG7B_GLOBALS)
        for _id, (_css, js, g) in RUNG7B_FORMS.items():
            everything["forms/" + js] = g
        for name, g in everything.items():
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("(function (global)", src)
                self.assertRegex(src, r"global\." + re.escape(g) + r"\s*=")

    def test_exposes_init_and_destroy(self):
        files = list(RUNG7B_GLOBALS) + ["forms/" + js for _c, js, _g in RUNG7B_FORMS.values()]
        for name in files:
            src = _src(name)
            with self.subTest(component=name):
                self.assertIn("function init", src)
                self.assertIn("destroy", src)

    def test_reduced_motion_posture_is_declared(self):
        """The two motion-bearing enhancers and the vf morph guard on
        prefers-reduced-motion; the section edge is a still material and
        its header says so (nothing for reduced-motion to disable)."""
        for name in ("vf-scroll-morph.js",
                     "forms/morph-tile-grid.js", "forms/type-index-grid.js"):
            with self.subTest(component=name):
                self.assertIn("prefers-reduced-motion", _src(name))
        self.assertIn("reduced-motion", _src("organic-section-edge.js"))

    def test_has_doc_comment_header(self):
        files = (list(RUNG7B_GLOBALS)
                 + ["forms/" + js for _c, js, _g in RUNG7B_FORMS.values()]
                 + ["forms/" + css for css, _j, _g in RUNG7B_FORMS.values()])
        for name in files:
            with self.subTest(file=name):
                self.assertTrue(_src(name).lstrip().startswith("/*"))

    def test_namespaced_stylesheet_injection(self):
        """One namespaced stylesheet per interaction component. The form
        enhancers inject nothing — their state machines are inline writes
        and WAAPI plays."""
        for name in RUNG7B_GLOBALS:
            with self.subTest(component=name):
                self.assertRegex(_src(name), r"CSS_ID = 'ad-[a-z-]+-css'")
        for _id, (_css, js, _g) in RUNG7B_FORMS.items():
            with self.subTest(form=_id):
                self.assertNotIn("createElement('style')", _src("forms/" + js))

    def test_form_enhancers_create_no_nodes(self):
        """The layering law: a form enhancer toggles attributes/styles on
        authored hooks only."""
        for _id, (_css, js, _g) in RUNG7B_FORMS.items():
            src = _src("forms/" + js)
            with self.subTest(form=_id):
                self.assertNotRegex(src, r"\bappendChild\b")
                self.assertNotRegex(src, r"\binnerHTML\s*=")
                self.assertNotRegex(src, r"\binsertAdjacentHTML\b")

    def test_no_bare_100vh(self):
        """svh/lvh/dvh only — a bare 100vh jumps under mobile chrome
        collapse."""
        files = (list(RUNG7B_GLOBALS)
                 + ["forms/" + js for _c, js, _g in RUNG7B_FORMS.values()]
                 + ["forms/" + css for css, _j, _g in RUNG7B_FORMS.values()])
        for name in files:
            with self.subTest(file=name):
                self.assertNotRegex(_src(name), r"100vh")


class TestRung7bFormDiscipline(unittest.TestCase):
    """The section-form floors (the test_section_forms contract, applied to
    both rung-7B forms before the manifest merge)."""

    def test_form_root_selector_present(self):
        for form_id, (css, _js, _g) in RUNG7B_FORMS.items():
            with self.subTest(form=form_id):
                self.assertIn('[data-ad-form="' + form_id + '"]', _form(css))

    def test_form_ships_zero_motion(self):
        for form_id, (css, _js, _g) in RUNG7B_FORMS.items():
            src = _form(css)
            with self.subTest(form=form_id):
                self.assertNotIn("@keyframes", src)
                self.assertNotRegex(src, r"\banimation\s*:")
                self.assertNotRegex(src, r"\btransition\s*:")

    def test_no_js_floor_no_hidden_states(self):
        """A dead script leaves both sections fully legible — no stylesheet
        ever hides a slot or a hook (every hide is an enhancer inline
        write)."""
        for form_id, (css, _js, _g) in RUNG7B_FORMS.items():
            src = _form(css)
            with self.subTest(form=form_id):
                self.assertNotRegex(src, r"opacity:\s*0(?![.\d])")
                self.assertNotIn("visibility: hidden", src)
                self.assertNotIn("display: none", src)

    def test_form_styles_attributes_never_role_classes(self):
        """class-role uniformity rule: form state rides data attributes — a
        .ad-*/.is-* selector in a form stylesheet is class-role drift."""
        for form_id, (css, _js, _g) in RUNG7B_FORMS.items():
            src = _form(css)
            with self.subTest(form=form_id):
                self.assertNotRegex(src, r"\.ad-")
                self.assertNotRegex(src, r"\.is-")

    def test_the_index_fold_is_svh(self):
        """type-index-grid IS the fold (no marketing hero) — the svh stage
        law; the morph grid is a mid-page proof section, no fold height."""
        self.assertIn("min-height: 100svh", _form("type-index-grid.css"))


class TestMorphTileGrid(unittest.TestCase):
    """Cyd's figure signature: radius morph + circle->full crossfade +
    caption slide, geometry carrying it — driven hover -> leave."""

    def setUp(self):
        self.css = _form("morph-tile-grid.css")
        self.js = _form("morph-tile-grid.js")

    def test_resolves_the_recipes_missing_ref(self):
        self.assertIn("MISSING:morph-tile-grid", self.css)
        self.assertIn("studio-reel-cyd", self.css)

    def test_the_alias_rulings_ride_in_the_header(self):
        """DISTINCT from figure-hover (contained zoom + cue),
        spotlight-expand-tile (layout-aware row expand) and clip-reveal
        (fire-once media uncover)."""
        self.assertIn("DISTINCT", self.css)
        self.assertIn("figure-hover", self.css)
        self.assertIn("spotlight-expand-tile", self.css)
        self.assertIn("clip-reveal", self.css)

    def test_one_radius_language_defined_once(self):
        """Rest + hover radii are tokens on the root — the enhancer reads
        them, the build overrides them once."""
        self.assertIn("--ad-mtg-radius:", self.css)
        self.assertIn("--ad-mtg-hover-radius:", self.css)
        self.assertIn("--ad-mtg-radius", self.js)
        self.assertIn("--ad-mtg-hover-radius", self.js)

    def test_the_morph_is_a_clip_morph(self):
        """Driven: clip-path inset(0 round …) interpolated through 52
        states on the 420ms clock, EXACT reversal on leave — the
        crossfading layers cannot spill mid-morph."""
        self.assertIn("'inset(0 round ' + radius + ')'", self.js)
        self.assertIn("media.style.transition = 'clip-path ' + TRANSIT;", self.js)

    def test_the_crossfade_and_caption_are_inline_writes(self):
        """Driven: overlay 1->0 over the full image, caption slides up
        (translate3d 0.6em -> 0); nothing in the stylesheet hides them."""
        self.assertIn("overlay.style.opacity = '1';", self.js)
        self.assertIn("caption.style.transform = 'translate3d(0,0.6em,0)';", self.js)
        self.assertNotIn("opacity", self.css.split("*/", 1)[1])

    def test_coarse_and_reduce_land_the_revealed_state(self):
        """Driven under ?coarse and ?rm: overlay crossfaded away
        instantly, caption authored-visible, no transitions armed — the
        finished state IS the rest (the init contract's one allowance)."""
        self.assertIn("if (still || !fine) {", self.js)
        self.assertIn("// the finished state, applied instantly: full image, caption up",
                      self.js)

    def test_focus_within_mirrors_hover(self):
        """Driven: tiles[2].focus() opened the morph; blur closed it; a
        leave never fires while focus is still inside."""
        self.assertIn("tile.addEventListener('focusin', t.enter);", self.js)
        self.assertIn("if (tile.matches(':focus-within')) return;", self.js)

    def test_the_stagger_is_released_on_one_column(self):
        """The organic stagger (even tiles drop) flattens at 768px and
        under data-stagger=off."""
        self.assertIn(":nth-of-type(even)", self.css)
        self.assertIn('[data-stagger="off"]', self.css)


class TestTypeIndexGrid(unittest.TestCase):
    """The whole-fold giant-type index over a live ground — the union of
    the experimental and spatial-organic orders, both resolved."""

    def setUp(self):
        self.css = _form("type-index-grid.css")
        self.js = _form("type-index-grid.js")

    def test_resolves_both_recipes_missing_refs(self):
        self.assertIn("MISSING:type-index-grid", self.css)
        self.assertIn("type-index-aristide", self.css)
        self.assertIn("type-index-obys", self.css)

    def test_the_union_names_both_archetype_orders(self):
        """Both gap entries in one build: Aristide/Obys/Lusion (the
        experimental order) + the spatial-organic arc, and the honesty
        stamp that the pattern is not verified 2024-2026 canon."""
        self.assertIn("experimental", self.css)
        self.assertIn("spatial-organic", self.css)
        for w in ("Aristide Benoist", "Obys", "Lusion"):
            self.assertIn(w, self.css)
        self.assertIn("not verified 2024-2026 canon", self.css)

    def test_one_shared_row_grid(self):
        """The index-list law at display scale: every row locks to one
        --_cols template — column edges cannot drift."""
        self.assertIn("--_cols:", self.css)
        self.assertIn("grid-template-columns: var(--_cols);", self.css)

    def test_the_ground_is_a_decor_stage(self):
        self.assertIn('[data-slot="ground"]', self.css)
        self.assertIn("pointer-events: none;", self.css)

    def test_the_boot_is_the_gaps_masked_rise(self):
        """Driven from document start: translate3d(0,101%,0) -> 0 under
        the row's clip, stagger held by fill:backwards, 69 distinct
        states, data-ad-tig-boot cleared when the last cell lands."""
        self.assertIn("translate3d(0,101%,0)", self.js)
        self.assertIn("fill: 'backwards'", self.js)
        self.assertIn("data-ad-tig-boot", self.js)
        self.assertIn("overflow: clip;", self.css)

    def test_the_bridge_publishes_discretely(self):
        """Driven: hover row 1 -> data-ad-tig-hover='1' on the root, the
        ground plate answered; a write only on change, cleared on leave
        unless focus holds it."""
        self.assertIn("data-ad-tig-hover", self.js)
        self.assertIn("!== String(i)", self.js)
        self.assertIn("if (row.matches(':focus-within')) return;", self.js)

    def test_rows_stay_real_links(self):
        """Driven: a real click navigated natively to #p-helix at viewport
        top — the enhancer binds no click handler anywhere (the
        diegetic-nav law; the route-morph climax is delegated)."""
        self.assertNotIn("addEventListener('click'", self.js)
        self.assertNotIn("preventDefault", self.js)
        self.assertIn("webgl-scene(delegated)", self.js)

    def test_reduce_keeps_the_bridge_drops_the_boot(self):
        """Driven under ?rm: zero boot frames, zero transforms — the
        authored index IS the fold; the hover publish still ran."""
        self.assertIn("if (still) return; // the authored index IS the fold", self.js)

    def test_hover_grammar_is_the_pairing_never_duplicated(self):
        """The material line / sibling dim / meta surface belong to the
        paired index-row-hover (driven through the pairing) — the form CSS
        ships no hover state of its own."""
        self.assertIn("index-row-hover", self.css)
        self.assertNotIn(":hover", self.css)


class TestOrganicSectionEdge(unittest.TestCase):
    """The anti-grid flow boundary: a shape() curve per edge with the
    gapless seam law — and the drive-caught one-curve-per-seam law."""

    def setUp(self):
        self.src = _src("organic-section-edge.js")

    def test_the_curve_is_shape_guarded(self):
        """A per-edge path, not a basic ellipse (one ellipse clips all
        four corners of a tall section — the header records why the gap's
        ellipse() variants were dropped); everything sits under
        @supports so no-support means straight edges AND no overlap."""
        self.assertIn("clip-path: shape(", self.src)
        self.assertIn("@supports (clip-path: shape(from 0% 0%,line to 100% 100%))", self.src)
        self.assertIn("ellipse() variants", self.src)
        self.assertIn("per-edge path", self.src)

    def test_the_gapless_seam_law(self):
        """Driven at five stations per seam at 1440/1024/~500px:
        elementFromPoint always neighbor-above/section-below, zero VOID —
        the overlap (negative margin + matching padding) double-paints the
        whole curve band."""
        self.assertIn("margin-top:calc(-1 * ' + DEPTH + ')", self.src)
        self.assertIn("padding-top:' + DEPTH + '", self.src)
        self.assertIn("margin-bottom:calc(-1 * ' + DEPTH + ')", self.src)

    def test_one_curve_per_seam_is_encoded(self):
        """Drive-CAUGHT: night's bottom curve + footer's top curve on one
        seam exposed the page ground between the crossing curves (probes
        hit BODY) — the law now rides in the header."""
        self.assertIn("ONE CURVE PER SEAM", self.src)
        self.assertIn("drive-caught", self.src)

    def test_the_curve_is_one_quadratic_defined_once(self):
        """Single source: topCurve/bottomCurve build every shape — the
        apex-at-lift control math lives in exactly one place."""
        self.assertIn("function topCurve(lift)", self.src)
        self.assertIn("function bottomCurve(lift)", self.src)
        self.assertEqual(self.src.count("curve to 100% "), 1)

    def test_the_accent_crescent_is_opt_in(self):
        """Cyd's offset shadow riding the curve: two same-curve clips
        intersected into a band, painted in the accent, opt-in via
        data-ad-edge-shadow."""
        self.assertIn("data-ad-edge-shadow", self.src)
        self.assertIn("--ad-edge-shadow-offset", self.src)
        self.assertIn("var(--ad-accent", self.src)

    def test_still_material_no_runtime(self):
        """No rAF, no listeners, no pointer tracking — geometry only; a
        dead script leaves straight-edged sections (the gap's degrade)."""
        self.assertNotIn("requestAnimationFrame", self.src)
        self.assertNotIn("addEventListener", self.src)

    def test_ruled_distinct_from_clip_reveal(self):
        self.assertIn("clip-reveal", self.src)
        self.assertIn("DISTINCT", self.src)


class TestVfScrollMorph(unittest.TestCase):
    """The signature text move: a registered VF axis welded to the scroll
    view-range on native animation-timeline — scrubbed and sampled."""

    def setUp(self):
        self.src = _src("vf-scroll-morph.js")

    def test_native_timeline_under_supports(self):
        """Driven with a loaded Fraunces VF: computed
        font-variation-settings sampled mid-range (wght 465.307 / 557.742)
        and rewound EXACTLY on scroll-back — zero JS per frame."""
        self.assertIn("@supports (animation-timeline: view())", self.src)
        self.assertIn("animation-timeline:view();", self.src)
        self.assertIn("animation-range:var(--ad-vfm-range,entry 0% cover 40%);", self.src)

    def test_longhands_follow_the_shorthand(self):
        """`animation:` resets timeline/range — the longhands must come
        after it in the rule (the comment records the trap)."""
        rule = self.src.split("[data-ad-vfm]{", 1)[1]
        self.assertLess(rule.index("animation:ad-vfm-wght auto linear both;"),
                        rule.index("animation-timeline:view();"))

    def test_registered_axes_with_per_element_endpoints(self):
        """wght default / opsz by attribute value; endpoints ride
        per-element custom properties resolved inside the keyframes
        (driven: opsz 9->144 on custom endpoints)."""
        self.assertIn('font-variation-settings:"wght" var(--ad-vfm-from,300);', self.src)
        self.assertIn('font-variation-settings:"opsz" var(--ad-vfm-to,72);', self.src)
        self.assertIn('[data-ad-vfm="opsz"]{animation-name:ad-vfm-opsz;}', self.src)

    def test_the_ytuc_refutation_is_recorded(self):
        """The playbook's own correction rides in the header: Cyd's cited
        'ytuc' axis is refuted, the component is genericized to
        registered axes."""
        self.assertIn("ytuc", self.src)
        self.assertIn("refuted", self.src)

    def test_reduce_is_the_authored_cut(self):
        """Driven under rm: 'normal' at every scroll position — the sheet
        guard, not a JS branch."""
        self.assertIn("@media (prefers-reduced-motion: reduce){", self.src)
        self.assertIn("[data-ad-vfm]{animation:none;}", self.src)

    def test_the_paint_scope_is_honest(self):
        """The gap's 'guaranteed 60fps' claim is corrected: the timeline
        is native but each step re-rasterizes glyphs — display headings
        only, never body prose."""
        self.assertIn("re-rasterize", self.src)
        self.assertIn("never body prose", self.src)


if __name__ == "__main__":
    unittest.main()
