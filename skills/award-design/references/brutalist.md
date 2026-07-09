# Brutalist / Neo-Brutalist

Deliberate rejection of polish. Typography is the design — carrying scale, character, and emotion that decoration would otherwise smuggle in. Flat fills, raw geometry, and unconcealed structure replace gradient-and-shadow softness.

## Canonical reference — FlowFest 2025

**Site.** FlowFest 2025
**URL.** `flowfest.co.uk`
**Award.** Awwwards Site of the Day, July 29 2025 (score 7.36) + GSAP Site of the Week
**Credits.** Community build — Dennis Snellenberg, Isabel Edwards, Osmo, Ilja van Eck. Animation by Dennis and Ilja from Osmo.

The honest answer in this archetype. No SOTM or SOTY winner in the 2024–2026 window cleanly hits the saturated Gumroad-style neo-brutalist profile. FlowFest 2025 carries a flat `#F3A20F`/`#F97028` palette, chunky display type, and a raw illustrative aesthetic — the closest credentialed match. Substitutable upgrade: `animejs.com` at SOTM tier carries the brutalist palette in a more austere monochrome flavor, but it serves the Bento archetype better.

## DNA — non-negotiable

- Typography is the dominant compositional element — display sizes are 80–200px+, never decoration around imagery
- Flat fills hold the surface; shadows carry no blur, gradients do not interpolate
- Geometry is hard and structural — borders, rules, hard-edged shapes mark divisions explicitly
- The composition reads as built rather than rendered — no liquid blends, no soft glows
- **Bimodal density oscillation** — layouts swing between extreme data density (tightly packed monospace clusters, full-bleed dashboards) and vast calculated negative space. The contrast is binary, not gradual. A brutalist page that holds steady mid-density reads as restraint without conviction

The archetype keeps its identity across saturated black-on-white (Gumroad), warm illustrated (FlowFest), industrial monochrome (Anime.js fragments), and zine-aesthetic (Pitchfork). Color register is an expression choice, not a definition.

## Common expressions

Three stacks fit the DNA. Pick the one matching brand voice and audience.

### Saturated Gumroad — flat hot pink on white

Reference brand: Gumroad. Off-white base (`#FCFCFC`) with hot pink (`#FF90E8`), neon green (`#00FF41`), or electric yellow (`#FFF000`) as the dominant flat fill. 2–4px solid black borders around cards, chunky 4–8px hard-edged shadows on primary elements (zero blur), Monument Extended or Archivo Black at 80–200px+. The textbook neo-brutalist profile. Ideal for indie tech, digital products with attitude, conferences.

### Warm illustrated — FlowFest profile

Cream foundation (`#F8F0E0`-ish butter) with rainbow warm accents — orange (`#F3A20F`), peach (`#F97028`), coral, mustard. Chunky condensed display type (Druk Wide, Reckless), small expressive marks (rainbow arches, hand-illustrated stickers — drawn SVG motifs, never emoji glyphs). Round buttons are permitted when the type does the brutalist work. Ideal for festivals, creative communities, design-conference microsites.

### Industrial monochrome — terminal-aesthetic

Black or off-white base (`#0A0A0A` or `#FAFAFA`) with monospace body (Space Mono, JetBrains Mono, IBM Plex Mono) and a single saturated accent that lives only as a 2px rule or full-bleed band. Mechanical noise overlays, ASCII brackets, registration marks. Ideal for developer portfolios, technical labels, indie record labels.

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

Durations bind to `motion.duration-*`. Step easings (`steps(2)`) stay on the glitch layer — hero text and micro-toggles; reveals and fills ride smooth curves (FlowFest presses its buttons on `0.25s cubic-bezier(0.625, 0.05, 0, 1)`).

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

A brutalist site scores 8+ when typography genuinely carries the design (not when it's loud sans-serif over a generic layout), when the rejection of polish reads as deliberate craft (not as un-finished work), and when the Usability score holds despite the visual aggression — keyboard navigation, focus states, contrast, and mobile reconsideration. FlowFest succeeds because the chunky type and warm palette are choreographed, not chaotic.

The archetype loses identity when neo-brutalism becomes pure aesthetic surface — black borders applied to a generic centered-hero layout, "raw" treatment as decoration around stock-feeling content. Brutalism without typographic conviction collapses into novelty.

## Ideal for

Creative agencies with attitude, indie tech (Gumroad, Figma Config), streetwear, design conferences, developer portfolios, festivals and music microsites, zines, independent publications.

## Cross-references

Read alongside `foundations.md` (typography systems, kinetic type, OKLCH for the saturated stack), `anti-patterns.md` (axiomatic rejections still apply — pure `#000`/`#FFF` stays out, off-blacks and off-whites are the floor), `audit-rubric.md` (typography 8+ is the entry bar in this archetype), `exemplars.md` (Gumroad, The Verge, Pitchfork, Cuberto, Balenciaga).

## Effect palette — what this line's winners ship

Corpus: FlowFest 2025 (Awwwards SOTD 7.36 + GSAP SotW), Eloy Benoffi (GSAP SotD + CSSDA best UI/UX/Innovation + Awwwards HM), Naked City Films (Awwwards SOTD 2026), Sui Overflow 2025 (Awwwards SOTD 7.48), Treize Grammes (Awwwards HM 2024), Joffrey Spitzer (Codrops 2026). Four read live from computed CSS; the rest from builder case studies.

**The grammar** — no winner shares one hover trick; each element class earns a distinct response, and the system coheres through a single physical metaphor plus one easing family and one border/shadow/radius system. FlowFest binds every transform to `0.25s cubic-bezier(0.625,0.05,0,1)` (an Osmo expo-out) under an "objects on a table" metaphor; Sui unifies through a 2px `#000F1D` border, radius `0`, and a `background-color 0.3s` switch. When a control fills, it takes the **full saturated accent, never a pale tint**.

**Buttons / CTA**
- **Hard-shadow press** — button sits on `box-shadow: 0 4px 0 rgba(0,0,0,0.15)`; hover `transform: translateY(0.25em)` and the shadow collapses to `0` — no fill, no color change · warm-illustrated / saturated stacks where the button reads as a physical object · (FlowFest, Awwwards SOTD 2025).
- **Full-accent structural fill** — bordered zero-radius control fills with the full accent on active, label color holds — `border: 2px solid #000F1D`, `border-radius: 0`, `background: #4DA2FF`, `background-color 0.3s` · nav pills, filter chips, segmented toggles · (Sui Overflow, Awwwards SOTD 2025) (single-source).

**Links**
- **Underline draw from the leading edge** — 2px `currentColor` pseudo-element, `transform: scaleX(0→1)` with `transform-origin: left`, text color unchanged; gate behind `@media (hover: hover) and (prefers-reduced-motion: no-preference)` · the default link treatment in every stack · (FlowFest + Sui Overflow, both Awwwards SOTD).
- **Color dim / shift, no underline** — link shifts toward a `muted` token over `transition: color 0.35s`, no decoration · dense text menus (director lists, indexes) where underlines clutter · (Naked City, Awwwards SOTD 2026) (single-source).

**Figures / cards**
- **Rotate-tilt by parity** — cards tilt `±3°` on hover, sign alternating per `nth-child` so a grid reads like scattered paper; stickers peel in at `±5°` with scale · warm-illustrated / zine stacks · (FlowFest, Awwwards SOTD 2025) (single-source).
- **RGB channel-split / CRT dissolve** — image dissolves into brand-tinted offset channels via a shader, then a buffered video autoplays under it · industrial/terminal stacks that already run a WebGL layer · (Naked City, Awwwards SOTD 2026) (single-source, WebGL — not CSS-inspectable). CSS-only fallback: `filter: invert(100%)` kept instant or ≤`0.2s` (DesignThinkers, observed, implementation unverified).

**Nav** — all four live-read winners run the same rest state: `position: fixed`, `background: transparent`, `border-bottom: none`, `backdrop-filter: none`, text painted in the page's off-black or off-white token — the type and the fixed corner placement carry it. No winner hangs a colored border-bottom under the nav or takes a solid surface at rest; scrolled-state surface change was not captured, so treat "gains a bar on scroll" as unverified. (FlowFest + Eloy Benoffi + Naked City + Sui Overflow, 4 sites.)

**Text** — the signature move is scramble/glitch, not fade.
- **Character-diff swap** — text mutates character-by-character between two strings via the GSAP Text plugin `type: "diff"`, `0.3s`, `preserveSpaces` · location tags, status strings, hero sub-lines · (Eloy Benoffi, GSAP SotD / CSSDA) (single-source).
- **RGB split on hero type** — display type splits into offset color channels, one moment per page — keep it to the hero, never scattered across body · (Eloy Benoffi + Naked City, ≥2 sites).
- **Layer split** — ease the scroll reveals: masked per-char / per-line lines rise out of `overflow: hidden` on `expo.out` / `power3` / `bounce.inOut`, staged per content type (scale assembly, scrub sliders, stacked-copy ratchets). Reserve the jarring/step register for hero text and micro-toggles, not scroll reveals · (Joffrey Spitzer verified params; Treize + Eloy carry SplitText — supporting, shared across archetypes).

**Cursor** — swap the bitmap or keep the default; never a lerped follower-blob. `body { cursor: url(cursor.svg) 2 0, auto }` matched to the type for terminal/glitch stacks (Eloy Benoffi, verified), or keep the OS pointer and let unstyled anchors stay browser-default blue `rgb(0,0,238)` (Naked City, verified). The `mix-blend-mode: difference` follower belongs to the smooth-agency archetype, not this one.

**Loader / intro** — split by WPO budget.
- **Stepped counter** — the number ratchets `0 → 100 in 14 steps`, `3s`, easing `steps(14)`, then a `clip-path: inset()` wipe hands off to content; the `steps()` is the brutalist tell · (Joffrey Spitzer, verified params, single-source).
- **Near-instant first paint** — no preloader ceremony; the hero animates in on first paint · content-first festival / product / conference sites where a loader would tax WPO · (FlowFest + Sui Overflow, observed).

**Anti-signals** — absent from every winner examined: a pale `color-mix(accent, white)` wash on a primary control (fills are the full accent, or the button presses); one hover rule reused across button/link/card/nav; a scrolled nav that grows a solid surface plus a different-colored border-bottom, or a `backdrop-filter: blur()` frosted bar (all four navs stay transparent, borderless, un-blurred at rest); a smooth lerped `mix-blend-mode: difference` follower cursor; pure `#000`/`#fff` (even Sui ships `#000F1D` on `#F7F7F7`); a uniform `fade-up 0.6s` on every section; rounded soft-shadow cards — radius is `0` or a committed pill, shadows are hard offset `0 4px 0`, never blurred.
