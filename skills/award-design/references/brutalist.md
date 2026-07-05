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

Motion stays intentional, often jarring, never smooth-default.

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

Durations bind to `motion.duration-*`. Easings stay step-based or absent. Smooth `cubic-bezier` curves belong to other archetypes.

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
