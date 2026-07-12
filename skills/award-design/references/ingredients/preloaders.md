# Preloaders

The first beat of the arrival layer. Preloaders are archetype-conditional, never default — of 19 winners read live, 7 ship none and 12 earn one. Every verified loader carries a **handoff** into the hero; a loader with no handoff appears in zero winners. The loader is the universe's first sentence — numerals, curtain, and exit gesture pre-state the `DESIGN.md` palette and signature, never decorate a wait. Load at Phase 3/4; commit the family together with `page-transitions.md` — one arrival language per site.

Tags — (winner-verified) live CSS/DOM read; (shipped) observed, not read; (technique) documented, no winner verified; (heuristic) asserted in the record, never measured.

## Loader families — beat tables

### 1. Numeric counter — Terminal Industries (winner-verified)

| Beat | What shows · value / easing |
|---|---|
| Count | rolling odometer digits, mono, masked columns — `letter-spacing:.14625rem`, `will-change:transform` |
| Recolor | numerals climb through the accent — `color-transition{0%{light-gray} 30%{lime} to{dark-green}}` |
| Exit | split-curtain retract — JS-driven; total ≤2.8s (heuristic — never frame-timed) |

- **Bare accelerating `1→100`** — the counter *is* the intro; minimalist floor. Gabriel Contassot (technique).
- **Asset-gated diegetic ratio** — Bruno Simon: climbs in `#ffceca`, recolors to `#d5ff95` on complete, prints the real elapsed time — the load, never a timer. (winner-verified)
- **Roman-numeral variant**, dimmed on the line — Depo Luxe, luxury register. (winner-verified)
- **`steps(n)` concept numerals** carrying the brand — Naya, GT America. (technique)

### 2. Split-curtain — Terminal (winner-verified)

| Beat | What shows · value / easing |
|---|---|
| Cover | fixed full-viewport panels, `z-index:999`, `pointer-events:none` |
| Split | two panels, top and bottom — `height:50svh` each |
| Retract | panels pull apart over an **already-painted** hero — JS/GSAP-driven |

- **Single-panel wipe** — Gabriel: `origin-bottom scale-y-0` grey curtain, reused for intro and route. (winner-verified)

### 3. Wordmark / logo assembly — Depo Luxe + Son Daven

| Beat | What shows · value / easing |
|---|---|
| Build | logo draws as progress advances — `svg path{opacity:0}` → paths fill (Depo, winner-verified) |
| Drive | progress line scales behind the mark — `scaleY(var(--progress))`, data-driven (Depo, winner-verified) |
| Handoff | mark Flips into the header logo — bottom-pinned `.preloader_logo` → `header_logo` (Son Daven; position winner-verified, Flip observed) |

- **Brand-object assembly** — Lando Norris builds the helmet in WebGL + Rive, revealed via a top-anchored `clip-path: ellipse(100% 120% at 50% 0%)`. (value winner-verified)

### 4. Progress-as-brand-element

- **Hero top-bar → nav** — thin primary-fill bar pinned to the hero top. Eloy Benoffi (bar winner-verified; becomes-navbar single-source).
- **WebGL scene meter** — progress gates on real scene readiness. Son Daven (winner-verified).
- **SVG ring + bar** — stroke ring + `scaleX(0)`→1 bar. Ponpon Mania (winner-verified).

### 5. Narrative scene-one

The loader is the story's first frame, not a gate in front of it.

- **Mascot as scene one** — enters `scale(0) rotate(-120deg)` under a `cursor:wait` shell. Ponpon Mania (winner-verified).
- **Full-bleed video + slide-up enter button** — `translateY(200%)` in an `overflow:clip` wrap. Siena Film Foundation (winner-verified).
- **Full-screen intro overlay** over the kinetic type hero. Mat Voyce (winner-verified).
- **Loader becomes the homepage slider** — Bisous. (technique)

### 6. None / instant

Winner-verified absences — Anthropic (light editorial), Stefan Vitasović (minimalist), Anime.js and Vercel (bento — the card stagger is the entrance), Arc (spatial-organic), Delvaux (corporate-luxury), FlowFest (brutalist). Truekind is not among them: it ships a progress-tracked full-screen white preloader (fixed, `100dvh`, a growing 1px line) — light editorial can still earn a quiet loader. (winner-verified)

## The handoff patterns

The craft lever — every verified loader exits through one.

1. **Curtain retract over a pre-composed fold** — retract uncovers a finished frame. Terminal, Gabriel. (winner-verified)
2. **Counter recolors into the accent** — numerals resolve on the hero color, pre-stating it. Terminal, Bruno. (winner-verified)
3. **Loader element morphs into persistent UI** — Son Daven's logo → header (Flip); Depo's one logo class across preloader/header/footer; Eloy's bar → nav (single-source). The watched element becomes furniture.
4. **Clip-path reveal over the live hero** — Lando's top-anchored ellipse. (value winner-verified)
5. **Logo assembly seats into the hero** — Depo's path-fill mark. (winner-verified)
6. **Narrative continuation** — the subject persists into section one: Ponpon's mascot, Siena's video, Bisous's slider.

**A loader with no handoff choreography is the disqualifier** — no retract, recolor, Flip, reveal geometry, or narrative carry means a curtain dropped in front of an unrelated page. Zero winners.

## Repeat visits and reduced motion — record gaps

- **Session skip.** No winner skips its loader on revisit (Ponpon keys nothing on it — it replays every visit). Adopt it anyway: a `sessionStorage` flag → full skip or a ~600–900ms shortened replay. Build decision; cite no winner.
- **Reduced motion.** No winner ships a loader-specific `prefers-reduced-motion` path — a record gap, not a license. Under `reduce`: paint the hero immediately; the ceremony collapses to a sub-200ms fade or nothing.

## The LCP interaction

A loader masking a slow LCP is a lie the perf trace catches — late LCP over an idle network = theater; LCP gated behind real asset requests = honest.

- **Honest asset-gating** — Bruno prints the elapsed time; Depo drives a real `--progress` var; Son Daven gates on scene readiness. The loader overlaps real streaming, never invents latency.
- **Pre-composed-fold trick** — light hero, zero LCP cost: Terminal paints the hero *under* the curtain while the odometer counts.
- **Fixed-duration theater** — a timed counter over a DOM-only hero delays LCP for ceremony. Keep it ≤2.8s (heuristic); prefer gating or the pre-composed fold.

## Archetype-fit map

| Archetype | Family — record |
|---|---|
| Minimalist | bare counter, curtain over a pre-composed fold, or none — Terminal, Gabriel; Stefan (none) |
| Brutalist | none; route transitions carry the motion — FlowFest |
| Editorial | dark: video/narrative; light: none or quiet progress — Siena; Anthropic (none); Truekind |
| Bold / maximal | scene-one, progress-as-brand, `steps(n)` counter — Ponpon, Eloy, Mat Voyce, Exat |
| Immersive / cinematic | asset-gated WebGL intro; clip-path reveal — Lando; Active Theory (observed) |
| Experimental | in-engine intro; start button = audio-unlock — Bruno; Igloo (single-source) |
| Corporate-luxury | real progress + logo Flip / path-fill, or instant — Son Daven, Depo; Delvaux (none) |
| Bento / card | none; the card stagger is the entrance — Anime.js, Vercel |
| Spatial-organic | intro folded into the scene, or instant `view()` reveals — Arc (none) |

## Anti-signals

1. **Spinner** — the clearest tell of a non-designed loader. Zero winners.
2. **Blocking splash with no handoff** — a brand-color card that fades to an unrelated page.
3. **>3s ceremony** — beyond the ≤2.8s heuristic, only genuine asset-gating with reported progress earns time.
4. **Decorative counter over a static hero** — a `0→100` gate before a light DOM hero; delays LCP for theater.
5. **Numerals untethered from the concept** — the counter carries the brand register or it decorates.
6. **Copying the record's gaps** — no reduced-motion path, no session skip; close both.

## Cross-references

- `page-transitions.md` — the route sibling; its loader-coherence rule binds both.
- `../motion-palette.md` — Physics of motion times the loader exit.
- `../atmosphere-calibration.md` — the Motion dial sets how much ceremony the archetype affords.
