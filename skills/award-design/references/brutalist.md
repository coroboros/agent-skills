# Brutalist / Neo-Brutalist

Deliberate rejection of polish. Typography is the design — carrying scale, character, and emotion that decoration would otherwise smuggle in. Flat fills, raw geometry, and unconcealed structure replace gradient-and-shadow softness.

Tier 1 (DNA, anti-signals, macrostructures, reflexes) is `references/archetype/brutalist.md`, pushed into context by `scripts/direction_roll.py`. This file is tier 2: it loads at the design_plan commit, by heading, never whole.

## Contents

- [Canonical reference — Eloy Benoffi](#canonical-reference--eloy-benoffi)
- [DNA — non-negotiable](#dna--non-negotiable)
- [Common expressions](#common-expressions)
- [Typography](#typography) · [Color](#color) · [Layout](#layout) · [Motion](#motion) · [Texture](#texture)
- [What makes it award-worthy](#what-makes-it-award-worthy) · [Ideal for](#ideal-for) · [Cross-references](#cross-references)
- [Effect palette — what this line's winners ship](#effect-palette--what-this-lines-winners-ship) — per-element-class recipes, the grammar, tap/focus/dormancy
- [Mid-page life](#mid-page-life) · [Scroll texture](#scroll-texture) · [Idle band](#idle-band) · [Channel calibration](#channel-calibration)
- [Page recipe — how this line's winners build the page](#page-recipe--how-this-lines-winners-build-the-page) — anatomy, hero, section chain, footer, arrival, copy, imagery, mobile, variation
- [Spectacle menu](#spectacle-menu) — the hero beat, the continuation beats, the peak law

## Canonical reference — Eloy Benoffi

**Site.** Eloy Benoffi — Portfolio
**URL.** `eloyb.design`
**Award.** Awwwards Honorable Mention + GSAP Site of the Day + CSSDA Best UI / Best UX / Best Innovation / Special Kudos
**Source.** Codrops case study 2025-10-15, "From Blank Canvas to Mayhem: … Brutalist, Glitchy Portfolio".

The one corpus member an external source explicitly calls brutalist, and the primary source for the continuous-carry momentum model. Industrial/terminal glitch: ASCII flowers, ALL-CAPS `>>>`-prefixed terminal copy, char-diff identity tags, a forced-open scramble nav, scramble-on-hover labels, loader-into-navbar. Its single spectacle peak is deferred to the footer clone machine while a scrubbed flower-pluck field and different-speed title rows shear the whole scroll — the `studio-index` / peak-at-the-bottom exemplar, and the best-sourced mechanic set in the corpus, every parameter Codrops-confirmed to the number.

Scored corroborators at SOTD tier: **Sui Overflow 2025** (Awwwards SOTD 2025-04-15 + Developer Award, 7.48 overall — Design 7.64 / Usability 7.19 / Creativity 7.73 / Content 7.24, Dev 7.14, by Holographik) proves the DNA holds in two-tone industrial monochrome with no illustration; **Naked City Films** (Awwwards SOTD 2026-01-23, 7.34 overall — Design 7.51 / Usability 6.99 / Creativity 7.43 / Content 7.50, Developer Award 7.49, Nuxt/Vue + custom Canvas3) is the restrained register, its Codrops study naming a section "Brutalist Influence as a Foundation".

**FlowFest 2025** (Awwwards SOTD 2025-07-29, 7.36) is brutalist-adjacent, not canonical: Awwwards tags it Art & Illustration, Events, Animation, Colorful, Illustration, Microinteractions — brutalist is absent — and no external source, Osmo's own framing included, calls it brutalist. Its hard-press buttons, drawn-SVG type-as-image slab, tilt-parity sticker cards and marquee are reusable technique for the `argument-scroll` spine; none of it proves a brutalist law. No SOTM or SOTY winner in the 2024–2026 window cleanly hits the saturated Gumroad-style profile. Substitutable peers: `animejs.com` (Awwwards SOTD 2025-05-06, 7.62 — industrial-monochrome bento-brutalist hybrid that serves the Bento archetype better), `13g.fr` (Treize Grammes, Awwwards HM 2024-10-11 — the warm French branding-agency edge, soft-fit), `gumroad.com` (the saturated flat profile, no award credential in window).

## DNA — non-negotiable

- Typography is the dominant compositional element — display sizes are 80–200px+, never decoration around imagery
- Flat fills hold the surface; shadows carry no blur, gradients do not interpolate
- Geometry is hard and structural — borders, rules, hard-edged shapes mark divisions explicitly
- The composition reads as built rather than rendered — no liquid blends, no soft glows
- **Bimodal density oscillation** — layouts swing between extreme data density (tightly packed monospace clusters, full-bleed dashboards) and vast calculated negative space. The contrast is binary, not gradual. A brutalist page that holds steady mid-density reads as restraint without conviction
- **Continuous motion at rest** — the divergence from Minimalist. The page never collapses into a bank of fire-once IntersectionObserver reveals with dead silence between them. Amplitude is a per-brief choice, from Eloy's maximalist shear to Naked City's single perpetual rAF loop; the continuity is the law, the loudness is not

The archetype keeps its identity across saturated black-on-white (Gumroad), warm illustrated (FlowFest), industrial monochrome (Anime.js fragments), and zine-aesthetic (Pitchfork). Color register is an expression choice, not a definition.

## Common expressions

Three stacks fit the DNA. Pick the one matching brand voice and audience.

### Saturated Gumroad — flat hot pink on white

Reference brand: Gumroad. Off-white base (`#FCFCFC`) with hot pink (`#FF90E8`), neon green (`#00FF41`), or electric yellow (`#FFF000`) as the dominant flat fill. 2–4px solid black borders around cards, chunky 4–8px hard-edged shadows on primary elements (zero blur), Monument Extended or Archivo Black at 80–200px+. The textbook neo-brutalist profile. Ideal for indie tech, digital products with attitude, conferences.

### Warm illustrated — FlowFest profile

Cream foundation (`#F8F0E0`-ish butter) with rainbow warm accents — orange (`#F3A20F`), peach (`#F97028`), coral, mustard. Chunky condensed display type (Druk Wide, Reckless), small expressive marks (rainbow arches, hand-illustrated stickers — drawn SVG motifs, never emoji glyphs). Round buttons are permitted when the type does the brutalist work. Ideal for festivals, creative communities, design-conference microsites. The grounding site here is brutalist-adjacent, so watch the warmth: it tips the palette out of the brutalist system faster than any other expression.

### Industrial monochrome — terminal-aesthetic

Black or off-white base (`#0A0A0A` or `#FAFAFA`) with monospace body (Space Mono, JetBrains Mono, IBM Plex Mono) and a single saturated accent that lives only as a 2px rule or full-bleed band. Mechanical noise overlays, ASCII brackets, registration marks. Sui Overflow ships the two-tone proof at `#000F1D` on `#F7F7F7` (Awwwards SOTD 2025, 7.48). Ideal for developer portfolios, technical labels, indie record labels.

## Typography

Display faces carry the design. Choose by stack.

- **Saturated Gumroad / industrial monochrome**: Monument Extended, Archivo Black, Reckless, GT America Mono — 80–200px+, weight 700–900, often uppercase
- **Warm illustrated**: Druk Wide, Reckless, Cooper Black, Recoleta in heavy weights — same scale, often title case for warmth
- **Body / metadata**: monospace at 14–16px (Space Mono, JetBrains Mono, IBM Plex Mono) for the terminal-chic register; rounded sans (Cooper Hewitt, Polysans) for warm illustrated

Tracking sits tight on display (`-0.03em` to `-0.06em`) and generous on monospace body (`0.05em`). Leading is compressed on display (`0.85`–`0.95`).

## Color

Background spans three families per stack:

- **Saturated Gumroad**: off-white (`#FCFCFC`) or near-black (`#0A0A0A`) with one hot accent
- **Warm illustrated**: cream / butter (`#F8F0E0` to `#FAF5E8`) with a rainbow of warm flats
- **Industrial monochrome**: hard contrast — `#FCFCFC` on `#0A0A0A` or vice versa, with one saturated rule

Accents stay singular per viewport (one moment of color), never blended through gradients. Border colors are strict — typically near-black (`#0A0A0A`), occasionally a single saturated hue used as a structural element.

## Layout

Strict grids with visible borders or rules. Elements anchor precisely to grid tracks; intentional overlap signals composition rather than accident.

```css
.brutalist-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0;
  border: 3px solid var(--border-strong);
}
.brutalist-cell {
  border: 2px solid var(--border-strong);
  padding: var(--space-m);
}
.brutalist-cell.feature {
  grid-column: span 2;
  box-shadow: 6px 6px 0 var(--border-strong);
}
```

Border weights bind to `borderWidths.*`. Hard shadows bind to `shadows.*` extension tokens — `shadows.hard-md: 6px 6px 0 ...`.

### Grid determinism

When the grid itself must read as the design (industrial monochrome, terminal-aesthetic), use the contrasting-background technique to produce mathematically perfect, razor-thin dividers without authoring any border declarations:

```css
.brutalist-grid-deterministic {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
  background-color: var(--border-strong); /* shows through gap */
}
.brutalist-grid-deterministic > * {
  background-color: var(--surface);       /* fills cell */
  padding: var(--space-m);
}
```

The `gap: 1px` reveals the parent's background as a 1px line through every cell intersection. Result: pixel-perfect rules with no border math, no half-pixel rendering quirks at responsive breakpoints, no inconsistencies at the corners. Particularly useful for data tables, dashboards, and feature grids in the industrial-monochrome stack.

### Syntax decoration — industrial markers

The brutalist composition treats syntax as structural geometry, not decorative metadata. Lift these patterns into the design system; they're the equivalent of registration marks on a printed sheet.

- **ASCII brackets** as section labels — `[ DELIVERY SYSTEMS ]`, `[ ROUTING TABLE ]`, `[ MANIFEST 04 ]`. Set in monospace at 10–14px with `0.05em` to `0.1em` tracking. Read as utilitarian section flags, not as decorative borders.
- **Directional markers** — `>>>`, `<<<`, `▶`, `■`, `▢` as inline navigation cues or list bullets — never as scroll indicators (the scroll-cue ban holds even here). Avoid emoji or icon font equivalents; the typographic primitives are the brutalist register.
- **Registration symbols as structural geometry** — `®`, `©`, `™`, `§`, `¶`, `‡` placed at grid intersections, in the top-right of frame edges, or as a typographic motif across the page. Function as a print-shop reference mark, not as legal text.
- **Process strings** — `REV 2.6`, `UNIT / D-01`, `BATCH 0042/A`, ISO-style timestamps (`2026-01-15T14:32:00Z`), checksum-style monospace identifiers. Simulate active mechanical processes; the page reads as a runtime artifact rather than marketing copy.
- **Barcodes / faux machine-readable** — Code 39 or Code 128 SVG barcodes placed at footer edges or as ID strips on cards. Decorative-functional; readers don't need to scan them, the *signal* is what reads as industrial.

Bind these patterns to `typography.label-mono` and `typography.label-machine` extension token slots so the entire system shares one register.

**Declared archetype override.** Indexed ASCII flags (`[ MANIFEST 04 ]`) and process strings (`REV 2.6`) are legitimate Brutalist grammar and override the global meta-label and version-string bans — declare the override in the pre-flight verdict (`--archetype brutalist` suppresses the META-LABEL scanner rule). The emoji axiom, the scroll-cue ban, and the pure-`#000`/`#FFF` axiom hold with no exception. Crosshairs at grid intersections (`+` glyphs at exact `1fr` boundaries) work as a tertiary marker layer.

## Motion

Motion stays intentional and splits by layer: scroll reveals ride smooth eased curves (`expo.out`, `power3` — verified across the line's winners); the jarring/step register belongs to hero text (scramble, RGB-split) and micro-toggles.

- Glitch effects and RGB channel splitting on hero text
- Kinetic type that bounces, rotates, or scrambles on hover
- Hard cuts over crossfades; instant color swaps without easing
- Marquee text bands at the section breaks
- Text mask reveals with video backgrounds

```css
.glitch:hover {
  animation: rgb-split 0.2s steps(2) infinite;
}
@keyframes rgb-split {
  0%   { text-shadow: 2px 0 #ff00ff, -2px 0 #00ffff; }
  100% { text-shadow: -2px 0 #ff00ff, 2px 0 #00ffff; }
}
```

Durations bind to `motion.duration-*`. Step easings (`steps(2)`) stay on the glitch layer — hero text and micro-toggles; reveals and fills ride smooth curves (FlowFest presses its buttons on `0.25s cubic-bezier(0.625, 0.05, 0, 1)`, a CustomEase carried from a prior read of the site's Slater JS, not re-read).

## Texture

Simulated analog degradation lives at the texture layer.

```css
.scanlines::after {
  content: '';
  position: fixed;
  inset: 0;
  background: repeating-linear-gradient(
    0deg, transparent, transparent 2px,
    rgba(0,0,0,0.1) 2px, rgba(0,0,0,0.1) 4px
  );
  pointer-events: none;
  z-index: 999;
}
```

Halftone dot patterns via SVG filters, mechanical noise overlays, 1-bit dithering on images. Procedural noise via Canvas or WebGL outperforms static PNG overlays — see `foundations.md`.

## What makes it award-worthy

A brutalist site scores 8+ when typography genuinely carries the design (not when it's loud sans-serif over a generic layout), when the rejection of polish reads as deliberate craft (not as un-finished work), and when the Usability score holds despite the visual aggression — keyboard navigation, focus states, contrast, and mobile reconsideration. That last clause is where the line measurably bleeds: Naked City's Usability 6.99 is the corpus's lowest sub-score, half a point under its own Design 7.51. Eloy Benoffi succeeds because the terminal metaphor is rendered to the number — the glitch is a system, not a filter — and because the loudest interaction is withheld until the footer.

The archetype loses identity when neo-brutalism becomes pure aesthetic surface — black borders applied to a generic centered-hero layout, "raw" treatment as decoration around stock-feeling content. Brutalism without typographic conviction collapses into novelty.

## Ideal for

Creative agencies with attitude, indie tech (Gumroad, Figma Config), streetwear, design conferences, developer portfolios, festivals and music microsites, zines, independent publications.

## Cross-references

Read alongside `foundations.md` (typography systems, kinetic type, OKLCH for the saturated stack), `anti-patterns.md` (axiomatic rejections still apply — pure `#000`/`#FFF` stays out, off-blacks and off-whites are the floor), `audit-rubric.md` (typography 8+ is the entry bar in this archetype), `exemplars.md` (Gumroad, The Verge, Pitchfork, Cuberto, Balenciaga).

Provenance for every claim below — the researcher rounds and the fresh-context refutations that corrected them — lives in the public research corpus of `github.com/coroboros/research`, under `articles/award-winning-websites-2025-2030/`: `archetypes/brutalist.md`.

## Effect palette — what this line's winners ship

Corpus — Eloy Benoffi (Awwwards HM + GSAP Site of the Day + CSSDA Best UI / Best UX / Best Innovation / Special Kudos; Codrops 2025-10-15, params confirmed to the number), Naked City Films (Awwwards SOTD 2026-01-23, 7.34 overall, Design 7.51 / Usability 6.99 / Creativity 7.43 / Content 7.50, Developer Award 7.49; Nuxt/Vue + custom Canvas3), Sui Overflow 2025 (Awwwards SOTD 2025-04-15 + Developer Award, 7.48 overall, Design 7.64 / Usability 7.19 / Creativity 7.73 / Content 7.24; Holographik), FlowFest 2025 (Awwwards SOTD 2025-07-29, 7.36 overall, Design 7.47 / Usability 7.19 / Creativity 7.51 / Content 7.16, Animations/Transitions 8.20 its top dev sub-score; Osmo — brutalist-adjacent, see the Canonical reference), Treize Grammes (Awwwards HM 2024-10-11, Thomas Carré + 13G — soft-fit edge), Anime.js v4 (Awwwards SOTD 2025-05-06, 7.62 overall, Developer Award 7.84 — boundary member, serves Bento better), Joffrey Spitzer (Codrops 2026-02-18 — technique source, no award verified this run). Four read live from computed CSS; the rest from builder case studies.

**The grammar** — no winner shares one hover trick; each element class earns a distinct response, and the system coheres through a single physical metaphor plus one easing family and one border/shadow/radius system. FlowFest binds every transform to `0.25s cubic-bezier(0.625,0.05,0,1)` (an Osmo expo-out, reference-carried) under an "objects on a table" metaphor; Sui unifies through a 2px `#000F1D` border, radius `0`, and a `background-color 0.3s` switch. When a control fills, it takes the **full saturated accent, never a pale tint**. The collision rule is deterministic rather than a taste call: each element class owns a distinct (trigger × property) pair, and where two classes would animate the same property on the same trigger, one moves to a different trigger (scroll-scrub / hover / idle) or a different property (transform / opacity / filter).

**Buttons / CTA**
- **Hard-shadow press** — button sits on `box-shadow: 0 4px 0 rgba(0,0,0,0.15)`; hover `transform: translateY(0.25em)` and the shadow collapses to `0` — no fill, no color change · warm-illustrated / saturated stacks where the button reads as a physical object · (FlowFest, Awwwards SOTD 2025-07-29 — brutalist-adjacent; the `0.25s` CustomEase is reference-carried).
- **Full-accent structural fill** — bordered zero-radius control fills with the full accent on active, label color holds — `border: 2px solid #000F1D`, `border-radius: 0`, `background: #4DA2FF`, `background-color 0.3s` · nav pills, filter chips, segmented toggles · (Sui Overflow, Awwwards SOTD 2025-04-15 — award and palette verified; the CSS timings are reference-carried, the awarded build is no longer live at the URL) (single-source).

**Links**
- **Underline draw from the leading edge** — 2px `currentColor` pseudo-element, `transform: scaleX(0→1)` with `transform-origin: left`, text color unchanged; gate behind `@media (hover: hover) and (prefers-reduced-motion: no-preference)` · the default link treatment in every stack · (FlowFest + Sui Overflow, both Awwwards SOTD).
- **Color dim / shift, no underline** — link shifts toward a `muted` token over `transition: color 0.35s`, no decoration · dense text menus (director lists, indexes) where underlines clutter · (Naked City, Awwwards SOTD 2026-01-23) (single-source).

**Figures / cards**
- **Rotate-tilt by parity** — cards rest at alternating `±3°` (sign per `nth-child`) so a grid reads like scattered paper, and straighten on hover; stickers peel in at `±5°` with scale · warm-illustrated / zine stacks · (FlowFest, Awwwards SOTD 2025 — brutalist-adjacent) (single-source).
- **RGB channel-split / CRT dissolve** — a shader dissolves the still into brand-tinted offset channels, then a buffered video autoplays under it once the transition completes · industrial/terminal stacks that already run a WebGL layer · (Naked City, Awwwards SOTD 2026-01-23; the hover behaviour is Codrops-verified, the shader uniforms and channel offsets are WebGL-internal and not CSS-inspectable). CSS-only fallback: `filter: invert(100%)` kept instant or ≤`0.2s` (technique-class, no winner attribution).

**Nav** — all four live-read winners run the same rest state: `position: fixed`, `background: transparent`, `border-bottom: none`, `backdrop-filter: none`, text painted in the page's off-black or off-white token — the type and the fixed corner placement carry it. No winner hangs a colored border-bottom under the nav or takes a solid surface at rest; scrolled-state surface change was not captured, so treat "gains a bar on scroll" as unverified. Reveal on scroll-up and hide on scroll-down is the safe behaviour. (FlowFest + Eloy Benoffi + Naked City + Sui Overflow, 4 sites.)

**Text** — the signature move is scramble/glitch, not fade.
- **Character-diff swap** — text mutates character-by-character between two strings via the GSAP Text plugin `type: "diff"`, `0.3s`, `preserveSpaces` · location tags, status strings, hero sub-lines · (Eloy Benoffi, GSAP SotD / CSSDA, Codrops-verified to the number) (single-source).
- **RGB split on hero type** — display type splits into offset color channels, one moment per page — keep it to the hero, never scattered across body; ship it in bursts, never as a continuous loop · (Eloy Benoffi + Naked City, ≥2 sites).
- **Layer split** — ease the scroll reveals: masked per-char / per-line lines rise out of `overflow: hidden` on `expo.out` / `power3` / `bounce.inOut`, staged per content type (scale assembly, scrub sliders, stacked-copy ratchets). Reserve the jarring/step register for hero text and micro-toggles, not scroll reveals · (Joffrey Spitzer verified params, technique-class — award unverified; Treize + Eloy carry SplitText — supporting, shared across archetypes).

**Cursor** — swap the bitmap or keep the default; never a lerped follower-blob. `body { cursor: url(cursor.svg) 2 0, auto }` matched to the type for terminal/glitch stacks (Eloy Benoffi, verified), or keep the OS pointer and let unstyled anchors stay browser-default blue `rgb(0,0,238)` (Naked City, verified). The `mix-blend-mode: difference` follower belongs to the smooth-agency archetype, not this one.

**Loader / intro** — no winner in this line ships zero-intro instant paint; the line signs the intro's *character* (typed chat, stepped count, loader-into-navbar), never skips it.
- **Loader-into-navbar** — the progress bar grows into the nav, so the loading UI *becomes* the page chrome instead of dissolving; pairs with the char-diff identity hero and no in-fold CTA · (Eloy Benoffi, Codrops-verified — the `studio-index` default).
- **Stepped counter** — the number ratchets `0 → 100 in 14 steps`, `3s`, easing `steps(14)`, then a `clip-path: inset()` wipe hands off to content; the `steps()` is the brutalist tell · (Joffrey Spitzer, verified params, technique-class — no award verified) (single-source).
- **Chat-cloud typing loader** — the mascot's chat cloud types `"..."` → "Hi Friends!" → "We are back..." → the hero's resident line (GSAP TextPlugin, all `ease: none`) while `.loading-screen` fades `autoAlpha: 0` over `0.3s` · (FlowFest — the site does ship a ~3s `initLoader` intro, correcting any "near-instant first paint" read; the beat order and timings are reference-carried from a prior read of its Slater JS, not re-read, and the site is brutalist-adjacent).

**Element states — tap, focus, dormancy.** The pointer layer is one costume of the state; the tap and focus answers are not optional and not a degraded copy.
- **CTA** — `:active` is the tap answer: the hard shadow collapses or the accent floods on press, 90–160ms, no hover intermediary on touch. `:focus-visible` mirrors hover (shadow collapse / accent fill) plus a visible ring.
- **Link** — plain tap target on touch; the underline draw and the color shift are `@media (hover: hover)`-gated so no content is trapped behind a hover. `:focus-visible` fires the draw or the shift, accessible name preserved.
- **Figure** — the parity tilt straightens on tap, or the CRT figure reveals its video; `focus-within` mirrors the hover so keyboard users reach the state; swipe-snap cells enlarge on tap.
- **Index row** — hovered row lights an accent rule and surfaces metadata while siblings dim to ~45%, plus either a cursor-attached image preview or a scramble-decode on the label. On touch it is a plain tap target — the dim and the scramble both read as broken without a pointer — and the preview variant flips the index vertical, revealing each row's image as the row centers under scroll. `:focus-visible` lights the row identically and reveals the preview.
- **Heading / prose** — near-zero by design; the effect is the entrance (type-as-image draw, char-diff swap, masked per-char rise). RGB split is one moment on the hero type only; scramble runs on labeled elements only, never on prose or headings. No touch answer, no focus state beyond default.
- **Nav** — rests transparent, borderless, un-blurred, text in the off-black/off-white token; link hover is a per-char rollover or a scramble on the label, and the primary pill answers with the hard press. Pills answer `:active` on touch. `:focus-visible` shows the rollover or scramble plus a ring, source order preserved.
- **Cursor** — the swapped bitmap is a pointer-only costume: on `pointer: coarse` it is absent, and the OS-pointer stacks lose nothing by it. Never focus-driven, and no affordance rides on it alone.

**Anti-signals** — absent from every winner examined: a pale `color-mix(accent, white)` wash on a primary control (fills are the full accent, or the button presses); one hover rule reused across button/link/card/nav; a scrolled nav that grows a solid surface plus a different-colored border-bottom, or a `backdrop-filter: blur()` frosted bar (all four navs stay transparent, borderless, un-blurred at rest); a smooth lerped `mix-blend-mode: difference` follower cursor; pure `#000`/`#fff` (even Sui ships `#000F1D` on `#F7F7F7`); a uniform `fade-up 0.6s` on every section; rounded soft-shadow cards — radius is `0` or a committed pill, shadows are hard offset `0 4px 0`, never blurred.

## Mid-page life

Layered, never single-channel, and the amplitude is set by the brief rather than by the archetype. The floor is one décor texture welded to global scroll: Eloy's pixel/flower field plucks path-by-path at `scrub: 8`, `stagger {each: 0.1, from: 'random'}`, opacity `0`, `bounce.inOut`, while different-speed title rows shear past at `yPercent -300`, `scrub: 0.6` under staggered `power3.in` / `power2.in` / `power1.in` (Eloy Benoffi, Codrops-verified to the number; the companion décor layers at `scrub: 6` / `1` / `0.5` are reference-carried); FlowFest's DrawSVG rainbow arches do the same job at `scrub: 0` (reference-carried, brutalist-adjacent). Over that floor sit typed per-block entrances firing once via `scrub: false` — Eloy's paragraph assembles char-by-char out of `#` noise in random order, `stagger each: 0.05` (Codrops-verified). The third channel is one idle loop in character, optional by register: the loud end runs a cursor-tracked mascot (`gsap.quickTo`, `0.4s power3`) beside a marquee (FlowFest, reference-carried params, brutalist-adjacent), the restrained end a single perpetual rAF loop binding smooth scroll, Three.js render, element entry and page transitions so no section is fully motionless (Naked City Films 7.34, Codrops-verified). Hover on non-link text is near-absent; the register's one signature is the JS scramble on labeled elements, the original string restored on mouseout (Eloy, mechanic verified — the charset and the ~100ms interval are illustrative, the Codrops study does not detail them), applied to labeled elements only, never to prose or headings. The dead middle is the build that ships entrance reveals with nothing scrubbed behind them — always weld one texture layer to the scrollbar.

## Scroll texture

Scrubbed cross-section transformations, never drifting parallax: a vertical case slider whose active panel scales up under scroll (Joffrey Spitzer, technique), a CRT-shader dissolve scrubbed by scroll position (Naked City, technique), a photo-shuffle carousel dealing images as the page moves (FlowFest, brutalist-adjacent), the sheared different-speed title rows that carry Eloy's whole scroll (Codrops-verified). The design_plan names one — the carry is a mechanism the scrollbar drives, not a background layer that floats. Wheel smoothing is the substrate this texture rides on: FlowFest `1.3.1`, Eloy `1.3.3` and Treize `1.1.13` load Lenis (winner-verified); Sui's `1.1.14` is reference-carried since the awarded build is no longer reachable; Naked City rolls its own inertial smoothing inside its rAF loop (technique). The scrub-numbered timelines lerp against the eased scroll value.

## Idle band

The amplitude is a per-brief choice and both ends are award-winning — the correction that matters most in this line, since "brutalist" reads as a licence to be loud. **Restrained** register: a single perpetual rAF loop keeps every section subtly in motion with no marquee at all, framed by its own makers as "restraint paired with intensity … movement without chaos" (Naked City Films, Awwwards SOTD 2026-01-23, 7.34, Codrops-verified). **Loud** register: a marquee band plus one in-character idle loop — a self-drawing arch and a cursor-tracked mascot (FlowFest, reference-carried params, brutalist-adjacent). Commit one or two idle loops that render the stack's physical metaphor, never a field of drifting décor, and never force a marquee onto a restraint brief. When a marquee is in register, couple its speed and skew to scroll velocity — proxy the skew through `gsap.quickSetter`, drive it from `ScrollTrigger`'s `onUpdate` with a `velocity / -300` clamp easing back to `0` — rather than a fixed px/s band; the velocity-reactive variant is the documented house technique of FlowFest's studio and it survives touch as a scroll-driven channel, while the constant px/s band is the tamer fallback (technique-class, from GSAP reference demos, not re-read from an awarded build). Pause on `visibilitychange` and off-screen.

## Channel calibration

Channel calibration — this line's winners run 3–5 distinct interaction channels (per-class states, display-type effects, cursor, idle, scroll texture, replayable spectacle); the pre-emit critique's Aliveness axis reads against that band, never against bare coverage.

## Page recipe — how this line's winners build the page

Corpus — Eloy Benoffi (live + Codrops), Naked City Films (Awwwards + Codrops), Sui Overflow (live, CSS params reference-carried), FlowFest 2025 (live HTML + a prior read of its Slater JS), Treize Grammes (live DOM), Joffrey Spitzer (media-only, Codrops).

**Anatomy** — *The Studio Index* (`studio-index`; Eloy winner-verified brutalist, Treize supporting, Naked City restrained-register technique): loader-into-navbar (progress becomes UI) or char-diff identity terminal hero, no in-fold CTA · attention → about · understanding → hover-charged work index · proof → footer-as-finale where the single spectacle peak lands last · close. Peak at the bottom; the index carries the middle. The archetype's primary spine — the one grounded in a source that explicitly calls its site brutalist. *The Community Scroll* (`argument-scroll`; FlowFest SOTD-verified order, brutalist-adjacent; Sui shipped): chat-cloud loader → type-as-image hero + date · attention → "What is FlowFest?" · understanding → lineup · proof (the capped peak ~40%) → what-to-expect · understanding → community band · proof → FAQ · rest → oversized invitation · close; 9 `<section>` elements live, ~24 = finer scroll beats (observed). *The Stepped Reel* (`studio-reel`; Joffrey, technique / single-source, award-unverified): counter loader → Flip showreel hero · attention → vertical case slider · proof → contact · close.

Route on the brief's declared inputs, never on a taste read: a studio, portfolio or agency where the work is the argument → `studio-index`, terminal-ironic voice, no in-fold CTA, footer-as-finale peak. An event, festival, conference, or a product with a bill to show → `argument-scroll`, warm-communal voice, the lineup as the ~40% proof peak, oversized reprise close — and hold that spine's warmth back from the palette, since its grounding member is a colorful-illustration site. A reel or showreel is the product → `studio-reel`, the stepped counter Flipping into the showreel. Deterministic by brief type; never blend two spines.

**Hero architectures** — *Identity-tag terminal hero* (`studio-index`; Eloy, Codrops-verified): corner tags `>>>based in madrid, spain` char-diff swap to `>>>born in mar del plata, arg` via TextPlugin `type:"diff"`, `0.3s`, `preserveSpaces`; a forced-open scramble nav; no in-fold CTA — the withheld CTA defers activation to the footer finale.

*Type-as-image slab* (`argument-scroll`; FlowFest, SOTD-verified, brutalist-adjacent): the H1 is drawn — inline `<svg><path>` in `.welcome__h1` — tagline "FlowFest is back.", "Friday 8th August, Manchester, UK"; the only in-fold CTA is the nav "Buy Tickets" pill. Entrance below is reference-carried from a prior read of `initLoader`, not re-read this run.

| element | order | transform | duration | easing |
|---|---|---|---|---|
| mascot | 1 | y→0 | `"< -1"` | `cubic-default` |
| nav-bar | 2 | `yPercent -102→0` | `"<"` | default |
| welcome cards | 3 | y 3em→0, stagger −0.025 | 1s | `Expo.easeOut` |
| H1 spans | 4 | `yPercent 100→0`, stagger −0.025 | 1s | `Expo.easeOut` |

**Section chain** — the role order with its intensity map and the state each section owes. Build each role as its row describes; never improvise the hero or a section layout outside the chain.

| role | form | pairs | intensity | state it owes |
|---|---|---|---|---|
| hero | identity-tag terminal hero (studio-index); drawn-SVG type-as-image slab (argument) | mark character-diff swap (`type:'diff'` .3s) \| inline-SVG `<path>` spans rising; caption scrubbed word brighten; loader loader-into-navbar \| chat-cloud typing loader \| stepped counter | 8 | a committed in-character scene, never a quiet opener; the one in-fold CTA (nav pill) answers with the hard-shadow press on argument, none at all on studio-index; on touch the entrance still plays and the pill answers `:active`; no zero-intro instant paint |
| understanding (what-is / about) | text/media split | h2 char-by-char assembly out of noise; prose scrubbed word brighten + key-term accent ignition | 5 | masked reveals fire once while the continuous carry runs under them at the brief's register — the scrubbed décor field always, the marquee and idle loop only in the loud register; standalone headings carry near-zero hover; rests relative to the peak, never silent |
| proof (lineup / work-index) | lineup grid of sticker cards (argument); index header + hover-charged row list (studio-index) | rows spotlight-dim + cursor image preview \| scramble-decode label; cards rotate-tilt by parity; h2 masked line rise | 9 | for `argument-scroll` **this** is the capped spectacle peak (~40%) — rows spotlight-dim, labels scramble, sticker cards straighten; for `studio-index` the index escalates toward the footer instead of peaking here; on touch rows are plain tap targets (the preview flips to a scroll-centered reveal) and cards rest at their parity tilt |
| community band / rest | static logo wall; text/media split (what-to-expect) | wall static, grayscale → colour on hover | 5 | the designed rest — a static wall, never a marquee; the carry stays audible behind it; hover recolors a single logo; static on touch |
| FAQ | FAQ accordion | — | 4 | the lowest-intensity beat before the close; the scrubbed décor layer still runs the full page height welded to the scrollbar; rows answer `:active` on touch |
| close / footer | closing panel + oversized CTA-reprise invitation (argument); footer clone machine (studio-index) | ask masked line rise; channels underline draw + colour shift; clone-field mousemove ×200 @~200px, `mix-blend-mode:difference`, exit opacity 0 / scale 0.6 / 0.2s / `back.in(1.7)`, stagger `{amount:0.4, from:'random'}` | 9 | argument: the page's largest type + reprised primary CTA + flanking illustrations; studio-index: the single spectacle peak lands **here**; the palette holds and the carry persists to the last frame; on touch the clone field is dormant and the reprised CTA answers `:active` |

**Footer** — a designed finale, never chrome. CTA-reprise (argument): oversized invitation + newsletter + reprised primary CTA + flanking illustrations, two-column — `.footer__h2` "See you there!" (FlowFest, SOTD-verified, brutalist-adjacent). Footer-as-spectacle (`studio-index`): the clone machine is the deferred peak (Eloy, Codrops-verified to the number). Contact-first activation (Treize, winner-verified): "Prenez rendez-vous avec l'un de nos associés" (curly ’, live DOM). CSS-level: reprise the primary CTA, set the page's largest type, host one interaction moment. Never a functional link-list.

**Arrival** — no zero-intro instant paint; the loader signs its character. Loader by macrostructure (`ingredients/preloaders.md`): family 4, progress-as-brand-element — the bar grows into the nav — or the char-diff identity tags for `studio-index` (Eloy, Codrops-verified); family 5, narrative scene-one — the chat-cloud typing loader — for `argument-scroll` (FlowFest, reference-carried, brutalist-adjacent); family 1, numeric counter in its `steps(n)` form, for `studio-reel` — `steps(14)` `0→100` over ~3s, then a `clip-path: inset()` wipe, optionally Flipping the background image onto the showreel video (Joffrey, technique). Author the loader hidden so no-JS never blocks the page. FlowFest globals `staggerDefault 0.07` / `durationDefault 1.47` / `CustomEase "0.625, 0.05, 0, 1"` (reference-carried). Route transitions (`ingredients/page-transitions.md`) rhyme with the loader: Barba 2.10.3 — `initLoader` on first load vs `initLoaderShort` internal fade, no chat replay (FlowFest, reference-carried); Swup + Flip menu-link→page-title morph 0.9s `expo.inOut` (Joffrey, technique / single-source). Pace: `argument-scroll` climaxes ~40% at the lineup and rests at the FAQ before the oversized invitation; `studio-index` builds evenly through identity hero, about and the hover-charged work index, and peaks at the bottom.

**Copy voice** — Quoted to calibrate, never to ship — imitate the specificity (the named place, the count, the refusal), never the wording. Terminal-ironic is the canonical brutalist voice: lowercase, `>>>` prefixes, ALL-CAPS verbs, `//` `#` fences. Warm-communal belongs to the adjacent event spine: first-plural, exclamatory, hot imperatives, trailing ellipses. Both refuse corporate distance, hedging, and quiet CTAs — the button is always a verb. Indexed ASCII flags (`[ MANIFEST 04 ]`) and process strings (`REV 2.6`) are legitimate grammar here, not meta-label noise.
- ">>>based in madrid, spain" → ">>>born in mar del plata, arg" (Eloy) — identity as a diffed terminal string.
- "##########COPY EMAIL##" (Eloy) — the CTA as terminal command.
- "Webflow chat, festival vibes, good times." (FlowFest H1) — the pitch in three noun phrases.
- "Hi Friends!" → "We are back..." (FlowFest loader) — the loader speaks in character.
- "Reach out to Isabel at isabel@designsie.co.uk if you have any questions." (FlowFest) — a named human, a real address.

**Imagery art direction** — drawn/typographic primitives or degraded media, never stock gloss; one treatment page-wide. ASCII/vector-only (Eloy): no photography; ASCII + drawn eye-flower SVG, `mix-blend-mode: difference` on runtime clones. Degraded-media-shader (Naked City): film stills through a CRT GLSL shader into brand-tinted RGB channels — electric blue `#0004EB` on gray `#979797`. Illustrated-drawn (FlowFest, adjacent): candid photo shuffle carousel subordinate to the SVG headline; marks are drawn SVG — rainbows, sun mascot — never emoji. Crop: full-bleed or hard-framed; grade: flat-saturated or high-contrast-limited.

**Mobile / touch** — carry-by-scroll, register-aware. The continuous carry is what a brief fears losing on mobile, and it survives, because its channels are scroll-driven rather than pointer-driven: the marquee keeps running (velocity-coupled or constant), the scrubbed décor field plucks and shuffles by scroll position, the case slider scrubs, the restraint-register rAF loop keeps rendering. The one pointer-dependent idle channel — the cursor-tracked mascot on `quickTo` — degrades to a time- or scroll-driven idle so the character still moves. Pointer-only states go dormant behind `@media (hover: hover)` so nothing is trapped: underline draw, tilt straighten, scramble-on-hover, per-char rollover, RGB-split hover, CRT dissolve, hover image-preview, and the custom bitmap cursor (→ OS pointer). For the hover-preview index, the documented mobile fallback flips the index vertical and reveals each row's image as the row centers under scroll. Press-class elements — hard-press buttons, full-accent chips, nav pills — answer the tap with a 90–160ms `:active` flash; the press is the tap answer. Image sets swap any desktop hold-drag strip for a native scroll-snap swipe gallery (OS momentum, tap-to-enlarge — the scored Mobile Excellence line). Under `prefers-reduced-motion`: every component snaps to its finished state, the marquee pauses, the décor goes static, scramble resolves to the final string, glitch and CRT freeze to a static frame, the stepped counter jumps instantly — and the static frame still reads as deliberately composed.

**Variation** — this section chain is one legal costume of the archetype, never *the* skeleton. Structure is story-native: the body's sections derive from the universe's spine, then check against these roles for coverage — never the reverse. The axes serial winners measurably rotate between builds (21-artifact corpus, 5 studios): body content archetype and item counts, the one signature device (never reused across builds), the close mechanism, the hero medium, the index/HUD costume. What persists as DNA: type grammar, the motion register (the register itself, never the named reading/interaction kit — that kit is a device, rotated per build like the signature), annotation grammar as a form, engineering architecture. The same content archetype + item count + close mechanism recurring across two different-brand builds has zero winner precedent.

**Anti-signals** — no winner in this line opens on a card/bento grid; none leads with a product-shot carousel; none ships a functional link-list footer; no route transition is a generic cross-fade.

## Spectacle menu

*Eloy clone machine*: mousemove in the footer → one CTA clones up to 200 copies (~200px steps), `mix-blend-mode: difference`, exiting on opacity `0` / scale `0.6` / `0.2s` / `back.in(1.7)`, stagger `{amount: 0.4, from: 'random'}`; payoff — an unbounded interference field where the loudest interaction lands last (Codrops "Ending with a Critical Error", verified to the number). *FlowFest chat-cloud reveal*: load → typed chat beats → mascot slides to rest, nav drops, cards stagger; payoff — a conversation becomes the hero (SOTD-verified as a scene, param-level reference-carried, brutalist-adjacent). *Naked City CRT dissolve*: a film still dissolves through the shader into brand-tinted offset channels and hands off to buffered video; payoff — the archive plays itself, at the restrained register.

**The hero beat.** A committed in-character scene, never a quiet opener — no genuine brutalist winner ships zero-intro instant paint. The loader signs its character (the loader-into-navbar with char-diff identity tags, chat-cloud typed beats, or a `steps(14)` stepped counter) and hands off to a type-as-image or identity reveal. The only in-fold CTA is the nav pill on `argument-scroll`; `studio-index` withholds it entirely. Hero intensity is ~8, deliberately sub-peak.

**The continuation beats** — the page is diffed against these, section by section.
- *what-is / about* — **continues**: masked line and char reveals fire once while the continuous carry runs under them at the brief's register amplitude — the maximalist end sheared by a scrubbed pluck field and different-speed title rows (Eloy, winner-verified), the restrained end by a single perpetual rAF loop (Naked City). Never a hard silence, and not necessarily loud.
- *lineup / work-index* — for `argument-scroll` **the one capped peak** at ~40%, intensity 9: spotlight-dim rows, parity-tilted cards at ±3°, scramble-on-hover labels. For `studio-index` the index is the hover-charged build that escalates toward the footer rather than peaking itself (Eloy).
- *what-to-expect / community band* — **rest**: a quieter text/media split plus a static logo wall, grayscale → colour on hover as the only micro-state; the carry stays audible, the section rests relative to the peak.
- *FAQ* — **the designed rest**: an accordion, the lowest-intensity beat before the close; the scrubbed décor layer still runs the full page height welded to the scrollbar.
- *footer* — either the CTA reprise at the page's largest type with flanking illustrations (argument), or the clone machine where the single spectacle peak lands last (`studio-index`). The palette holds and the carry persists to the last frame.

**The peak law** — verdict refined, from the winner evidence. The hero commits an in-character scene at intensity ~8, sub-peak. Cap the spectacle peak at **one** and place it at the proof (work-index / lineup ~40%) or the footer (clone machine / oversized reprise) — rarely the hero. Between and around it, run a continuous carry hero→footer so the page never becomes a bank of fire-once reveals with dead silence: at minimum one scrubbed décor field welded to global scroll, plus, register-dependent, a marquee and one in-character idle loop. The carry's amplitude is a per-brief choice, not a universal loudness — the maximalist register and the restrained register are both award-winning, so never force a loud marquee onto a restraint brief. When a marquee is in register, couple its speed and skew to scroll velocity rather than a fixed px/s. The divergence from Minimalist is that the continuous motion renders the archetype's physical metaphor in character, not that it is loud. The failure mode is the dead middle; a second spectacle peak equal to the first dilutes.

Evidence: Eloy Benoffi, the canonical brutalist anchor, defers the single spectacle peak to the footer clone machine while a scrubbed flower-pluck field at `scrub: 8` and different-speed title rows at `yPercent -300`, `scrub: 0.6` shear the entire scroll — the carry is continuous and the one spectacle lands at the bottom, not the hero (Codrops-verified to the number). Naked City Films takes SOTD 2026-01-23 at 7.34 on a single rAF loop binding smooth scroll, Three.js render, element entry and page transitions so no section is fully motionless, and its makers frame that as "restraint paired with intensity … movement without chaos" — continuous is not the same as loud, and the CRT-shader dissolve on the film grid is its operable peak. FlowFest sits at the loud end of the carry with a marquee, a mascot idle loop and a self-drawing arch, but Awwwards tags it Colorful/Illustration rather than brutalist and its idle-band params were not re-read, so it grounds the loud register as technique and never as law. Across the genuine-fit members the peak count caps at one: Eloy stacks no second peak equal to the footer machine.
