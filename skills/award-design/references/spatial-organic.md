# Spatial Organic

The post-grid, dimensionally-aware aesthetic for 2026–2027. Fuses visionOS spatial depth, organic natural forms, and native web APIs (View Transitions, Scroll-Driven Animations, WebGPU). The counter-reaction to bento saturation, blanding minimalism, and heavy parallax. The article's *Trends Shaping 2025–2030* section credentials the constituent moves (Liquid Glass, dark glassmorphism, organic shapes, procedural noise); the award record since supplies the reference sites — Igloo Inc (Site of the Year 2024) at the head of a verified winner corpus (see *Effect palette* below).

**Anchor note.** The article anchored this line to its trend section and to emerging brands (Arc Browser, Granola, Apple Vision Pro); the awarded corpus now anchors it directly — Igloo Inc (Site of the Year 2024), Cyd Stumpel (SOTD 2025-03-09), OceanX 2025 (SOTD 2026-02-23), Iventions (Awwwards SOTD + CSSDA Website of the Month, October 2025), Minh Pham (Awwwards SOTD). Arc and Granola stay style anchors, not winners; the *Effect palette* below reads the recipes from the winners' own CSS.

Tier 1 (DNA, anti-signals, macrostructures, reflexes) is `references/archetype/spatial-organic.md`, pushed into context by `scripts/direction_roll.py`. This file is tier 2: it loads at the design_plan commit, BY HEADING, never whole.

## Contents

- [Reference brands](#reference-brands) · [DNA — non-negotiable](#dna--non-negotiable) · [Common expressions](#common-expressions)
- [Typography](#typography) · [Color](#color) · [Layout](#layout) · [Glass surfaces](#glass-surfaces) · [Motion](#motion) · [WebGPU](#webgpu-when-3d-is-needed)
- [What makes it award-worthy](#what-makes-it-award-worthy) · [Ideal for](#ideal-for) · [Cross-references](#cross-references)
- [Effect palette — what this line's winners ship](#effect-palette--what-this-lines-winners-ship) — per-element-class recipes, the grammar, tap/focus/dormancy
- [Mid-page life](#mid-page-life) · [Scroll texture](#scroll-texture) · [Idle band](#idle-band) · [Channel calibration](#channel-calibration)
- [Page recipe — how this line's winners build the page](#page-recipe--how-this-lines-winners-build-the-page) — anatomy, hero, footer, arrival, copy, imagery, section chain, mobile, variation
- [Spectacle menu](#spectacle-menu) — the hero beat, the continuation beats, the peak law
- [Component index](#component-index) — the library ids this archetype reaches for

## Reference brands

- `arc.net` — Arc Browser. Frosted pastels, radial gradients, "frosted from 2035" character.
- `granola.ai` — Granola. Warm cream glass, PP Editorial New serif, premium paper feel.
- `apple.com/vision-pro` — Apple Vision Pro. Spatial-UI aesthetic, depth through blur and scale.
- `linear.app/method` — Linear (2026 rebrand hints). Organic shapes appearing inside a disciplined grid.

## DNA — non-negotiable

- Depth comes from z-axis layering, not from flat decorative shadows
- Shapes flow rather than snap to grids — soft `clip-path` curves, organic clip-paths, anti-grid layouts
- Textures are procedural and animated, not static overlays — Canvas or WebGL noise, not PNG grain
- Native web APIs (View Transitions, CSS Scroll-Driven Animations, WebGPU) drive effects that previously demanded heavy JS
- Earthy and muted palette — never neon, never corporate blue. Colors feel found in nature

The archetype keeps its identity across dark glassmorphism (Apple Vision Pro, deep dark with ambient orbs), warm cream glass (Granola), pastel-frosted (Arc), and editorial-organic (Linear's 2026 hints).

## Common expressions

Three stacks fit the DNA.

### Dark glassmorphism — Apple Vision Pro / "Liquid Glass" profile

Rich darks (`#0D1117`, `#111827`, deep forest `#0A1628`) with glass surfaces (`rgba(255,255,255,0.05)` with `backdrop-filter: blur(24px) saturate(1.2)`). Ambient OKLCH gradient orbs drift slowly behind glass surfaces (`opacity: 0.15–0.25`, large radius, 15–25s drift cycles). Apple's "Liquid Glass" announced at WWDC 2025 validates the approach. Ideal for premium AI products, spatial-computing brands, vision-tier hardware.

### Warm cream glass — Granola profile

Cream foundation (`#F8F5F0` to `#F5F1E8`) with paper-feel glass surfaces. PP Editorial New or similar premium serif at display. Subtle warm-tinted shadows. The "premium paper" register. Ideal for productivity tools with personality, knowledge work, premium DTC, lifestyle wellness.

### Pastel-frosted — Arc Browser profile

Mid-tone neutral foundation with frosted pastel gradient orbs (sage green `#87A98F`, terracotta `#C67D5B`, deep ocean `#1E3A5F`). Generous rounded geometry. Future-warmth atmosphere. Ideal for browser-tier UX, post-OS surfaces, identity-shifting products.

## Typography

Variable fonts animated on scroll/hover serve the "alive" quality.

- **Headlines**: Fragment, GT Flexa, Editorial New, PP Editorial New, bespoke typefaces — variable weight and width animated on scroll
- **Body**: rounded warm sans-serifs — Outfit, General Sans, Satoshi — 16–18px, weight 400 (General Sans/Satoshi are overexposed kit picks — rotate or justify, `inspiration.md`)
- **Display technique**: oversized kinetic type as primary design element, not just communication
- **Cross-cultural**: "Lingua-Lettering" — unified visual rhythm across Latin, Arabic, CJK when applicable

```javascript
gsap.to('.hero-title', {
  fontVariationSettings: "'wght' 800, 'wdth' 125",
  ease: 'none',
  scrollTrigger: { trigger: '.hero', scrub: true }
});
```

The native equivalent — a registered axis interpolated across a scroll view-range under `animation-timeline` — is the archetype's own signature move and runs off the main thread; see `vf-scroll-morph` in the *Effect palette*.

## Color

Earthy and muted. Colors feel found in nature.

- **Backgrounds**: rich darks `#0D1117`, `#111827`, deep forest `#0A1628`; warm creams `#F8F5F0`
- **Text**: warm off-white `#E8E4DF`, cream `#F0EDE8`
- **Nature accents**: sage green `#87A98F`, terracotta `#C67D5B`, deep ocean `#1E3A5F`
- **Ambient orbs**: OKLCH gradient orbs at low opacity (`0.15–0.25`), large radius, slow-moving
- **Glass surfaces**: `rgba(255,255,255,0.05)` with `backdrop-filter: blur(24px)`

```css
:root {
  --bg-deep: oklch(15% 0.02 250);
  --text-warm: oklch(90% 0.01 80);
  --accent-sage: oklch(62% 0.06 155);
  --accent-terra: oklch(60% 0.12 55);
  --glass: oklch(100% 0 0 / 0.05);
}
```

The accent does not have to be earth-toned to belong: Cyd Stumpel's authoritative palette is periwinkle `#8082F8` over cream `#FFF5EE` (Awwwards, re-verified), and the organic reading comes from the clip-path geometry the accent fills, not from the hue.

## Layout

Anti-grid. Flowing organic positioning. Generous negative space. Soft `clip-path` curves replace rectangular sections.

```css
.section-organic {
  clip-path: ellipse(80% 100% at 50% 0%);
  padding: clamp(6rem, 12vw, 14rem) clamp(2rem, 5vw, 8rem);
}

.organic-layout {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  gap: clamp(2rem, 4vw, 6rem);
}
.organic-content {
  grid-column: 2;
  transform: translateX(clamp(-2rem, -3vw, -4rem));
}
```

`organic-section-edge` is the library form of this boundary — `data-ad-edge="top|bottom"` carving a soft quadratic arc via `clip-path: shape()`, degrading to a straight edge with no support.

## Glass surfaces

The "Liquid Glass" treatment validated by Apple WWDC 2025. Glass over dark backgrounds with ambient gradient orbs.

```css
.glass-card {
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(24px) saturate(1.2);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.06),
    0 20px 40px -15px rgba(0, 0, 0, 0.3);
}

.ambient-orb {
  position: fixed;
  width: 40vw;
  height: 40vw;
  border-radius: 50%;
  background: radial-gradient(circle, var(--accent-sage) 0%, transparent 70%);
  opacity: 0.15;
  filter: blur(80px);
  pointer-events: none;
  animation: drift 20s ease-in-out infinite alternate;
}
@keyframes drift {
  from { transform: translate(0, 0) scale(1); }
  to { transform: translate(5vw, 3vh) scale(1.1); }
}
```

The Doppelrand technique (nested concentric containers — outer shell with hairline border, inner core with smaller radius and inner highlight) sharpens glass cards into "machined hardware" rather than flat tiles. See `premium-patterns.md` pattern 1 (Doppelrand) and pattern 9 (Liquid Glass Refraction). The Liquid Glass pattern is the canonical Spatial Organic glass register — apply it on every glass surface in this archetype, not as an optional flourish. `glass-card` ships the frost end (backdrop-blur, inset highlight, nested radii, opaque fallback); `liquid-glass-refraction` ships the refraction end, an SVG `feDisplacementMap` lens that bends the backdrop, fine-pointer and high-power only with `glass-card` as its fallback.

**Performance lock**: `backdrop-filter` belongs only on fixed or sticky elements (navbars, modal overlays). Applying it to scrolling containers triggers continuous GPU repaints and collapses mobile frame rate. Ambient orbs sit on `position: fixed; pointer-events: none` layers — never on scrolling surfaces.

## Motion

Native-first. Browser APIs over JS libraries where possible.

### CSS Scroll-Driven (off main thread, guaranteed 60fps)

```css
/* Base state: fully visible — the pre-animation state lives only inside the
   guard, so no-timeline browsers and reduced-motion users get revealed content
   (motion-palette.md). */
@supports (animation-timeline: view()) {
  .organic-reveal {
    animation: emerge linear both;
    animation-timeline: view();
    animation-range: entry 0% entry 80%;
  }
  @keyframes emerge {
    from { opacity: 0; transform: translateY(40px) scale(0.97); filter: blur(4px); }
    to   { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
  }
}
```

### View Transitions (seamless page navigation)

```css
@view-transition { navigation: auto; }
::view-transition-old(root) { animation: fade-out 0.4s ease; }
::view-transition-new(root) { animation: fade-in 0.4s ease; }
```

### Procedural noise / texture (Canvas or WebGL, never static PNG)

```javascript
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');
function renderGrain() {
  const imageData = ctx.createImageData(canvas.width, canvas.height);
  for (let i = 0; i < imageData.data.length; i += 4) {
    const v = Math.random() * 20;
    imageData.data[i] = imageData.data[i+1] = imageData.data[i+2] = v;
    imageData.data[i+3] = 12;
  }
  ctx.putImageData(imageData, 0, 0);
  requestAnimationFrame(renderGrain);
}
```

Procedural noise applies to a fixed `pointer-events: none` layer at high z-index, never to scrolling containers. Static PNG grain is the AI-tell version; procedural Canvas noise is the credentialed alternative.

### Motion philosophy

Organic easing — nothing linear, nothing mechanical.

```css
:root {
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-spring:   cubic-bezier(0.34, 1.56, 0.64, 1);
  --ease-smooth:   cubic-bezier(0.25, 0.1, 0.25, 1);
}
```

- Spring physics for interactive elements
- Slow ambient motion (15–25s cycles) for background orbs and drifts
- Fast response (200–400ms) for user interactions
- Blur transitions (`filter: blur(4px)` → `blur(0)`) for depth perception

## WebGPU (when 3D is needed)

Three.js r171+ with automatic WebGL fallback. TSL (Three Shading Language) for shader logic in JS/TS:

```javascript
import { WebGPURenderer } from 'three/webgpu';
const renderer = new WebGPURenderer({ antialias: true });
```

Use for: organic particle systems, noise-based terrain, flowing abstract shapes. Skip when image or video would carry the message at lower cost.

## What makes it award-worthy

A spatial-organic site scores 8+ when the depth feels physical rather than decorative — when glass surfaces refract instead of frost, when ambient orbs drift slowly enough to feel atmospheric rather than animated, when procedural noise breathes against the canvas. The technical depth (View Transitions, Scroll-Driven, WebGPU) signals developer sophistication; the organic restraint signals taste.

The archetype loses identity when "spatial" becomes a backdrop-blur effect bolted onto a SaaS template, when the organic shapes are static SVG decorations rather than animated procedural elements, or when the dark glassmorphism fails WCAG 4.5:1 contrast (a common failure — the article flags glassmorphism for contrast violations explicitly).

## Ideal for

Sustainability brands, wellness and health tech, post-2025 creative studios, premium direct-to-consumer with story, environmental organizations, artisan and craft brands, knowledge-work productivity tools, AI products with warmth, brands wanting premium without corporate coldness.

## Cross-references

Read alongside `foundations.md` (OKLCH, native scroll-driven animations, WebGPU framework selection), `premium-patterns.md` (Doppelrand nested architecture for glass cards), `production-hardening.md` (backdrop-filter scope, mobile performance), `anti-patterns.md` (glassmorphism contrast failures are common — test explicitly), `audit-rubric.md` (Color 9+, Motion 8+, Accessibility 8+ are entry bars), `exemplars.md` (Arc Browser, Granola, Apple Vision Pro, Linear).

Provenance for every claim below — the researcher rounds and the fresh-context refutations that corrected them — lives in the public deep-research corpus of `github.com/coroboros/research`, under `articles/award-winning-websites-2025-2030/deep-research/`: `archetypes/spatial-organic.md`, refutations folded under its `## Refuted` heading, the raw reports preserved verbatim at commit `fd5d1b6`.

## Effect palette — what this line's winners ship

Corpus — Igloo Inc (Awwwards SOTD 2024-07 + Site of the Year 2024 + Developer Site of the Year 2024 + FWA, Animations/Transitions 9.60; Three.js + Svelte + GSAP + Vite, studio abeto), Cyd Stumpel Portfolio 2025 (SOTD 2025-03-09, 7.22, Developer Award 7.74; View Transitions + native Scroll-Driven Animations, no WebGL), OceanX 2025 Year in Review (SOTD 2026-02-23, 7.44; Three.js/WebGL/Blender, Awwwards-tagged Horizontal Layout, Unseen Studio + PROPAGANDE), Iventions (Awwwards SOTD + Developer Award + CSSDA Website of the Month October 2025, judges 8.43), Minh Pham (Awwwards SOTD, developer 7.77; Three.js/GSAP/Webpack), Exo Ape (13 Awwwards SOTD + 12 Developer Awards on the studio profile — the studio homepage's own dated SOTD was not pinned this run) with its Fluid Glass build (SOTD 2026-03-30, 7.77; GSAP + Nuxt, Horizontal Layout + Unusual Navigation — an edge exemplar whose organic fit is inferred from the studio's register, not from the site's own grade), Sculpting Harmony (SOTM Nov 2023 + FWA, media-only, carried from the reference and not re-verified this run, outside the preferred 2024–2026 window — the kinetic-type continuity anchor). Arc and Granola stay CSS-verified style anchors, not winners.

**The grammar** — cohesion is one shared substrate under class-specific mechanisms. Fix one accent token, one easing table, one radius language, one display face; then vary the *mechanism* per element class — displacement for buttons, a drawn line for links, a shape morph for images, silence or glass for nav. Cyd Stumpel glues it all with a named easing family, `--default-duration: 1.3s`, `--default-ease: cubic-bezier(0.25,1,0.5,1)` (ease-out-quart), `--bouncy-ease: cubic-bezier(0.34,1.56,0.64,1)` for interactives — the family is winner-verified, the exact numerics carry from a prior reference read and were not re-read from the shipped SPA this run. The AI failure is the inverse — one mechanism (a pale fill) copied onto every class over an ad-hoc palette.

**Buttons / CTA**
- **Accent-displacement push** — base surface barely moves; the button translates a few px and a hard, un-blurred offset shadow in the accent color appears on the opposite side, a card lifting off a colored underlayer. Cyd Stumpel `.button:hover`: `background: color-mix(in srgb, var(--color-background) 95%, var(--color-accent))` (a deliberate 5% tint), `color: var(--color-accent)`, `transform: translate(-2px, 2px)`, `box-shadow: -1px 1px 0 0 var(--color-accent)`, `64px` pill. Default button on a warm editorial ground. The displacement is the response, the tint is set-dressing — a tint-only state with no geometry move still fails the pale-hover gate (interaction-signatures.md). (Cyd Stumpel, SOTD 2025-03-09; mechanic winner-verified, the exact px and shadow offsets illustrative — carried from the prior reference read, not re-read this run.)
- **Committed same-family fill** — for a fill, swap to a defined `-hover` token one step within the brand family, never a pale pastel: Granola resolves to `--color-fill-accent-hover` / `oats-green-300 → 400`, one warm step darker. (Granola, style anchor, not a winner.)
- **The 80% primary fill** — reserve the strong fill for the single primary submit per view: Cyd Stumpel form submit `background: color-mix(in srgb, var(--color-accent) 80%, var(--color))`. Never spray it on every button. (Cyd Stumpel, SOTD 2025-03-09; ratio illustrative, same read provenance.)

**Links**
- **Underline draw** — a pseudo-element scaling `0→1`, not a `text-decoration` toggle: Exo Ape runs one `:hover::after { transform: scaleX(1) }` across nav, list, footer and body links (color also shifts to `--color-light-grey`). This is where the accent line belongs — on links, never as nav chrome. (Exo Ape, mechanic winner-verified; the studio holds 13 Awwwards SOTD, the homepage's own award date unpinned this run.)
- **Accent wash + arrow nudge** — for inline/utility links, a 10% accent wash + a 1px lift + a diagonal arrow shove. Cyd Stumpel `.platform-link:hover`: `background: color-mix(in srgb, var(--color-accent), transparent 90%)`, `transform: translateY(-1px)`, arrow child `translate(2px, -2px)`. Arrow nudge corroborated by Arc; the 10% wash single-source. Same arbitration: the lift and shove are the response, the wash is set-dressing — wash alone fails the pale-hover gate (interaction-signatures.md). (Cyd Stumpel, SOTD 2025-03-09; amplitudes illustrative.)

**Figures / cards**
- **Border-radius morph + crossfade** — the tile's radius animates rounder while a resting graphic crossfades to the full image and the caption slides up; no accent, the geometry carries it. Cyd Stumpel `.work-thumb:hover`: `.img-container { border-radius: var(--hover-radius) }`, circle overlay `opacity 1→0` / full image `0→1`, title `translateY(0)`; timing `opacity .2s .1s ease-out, border-radius .2s .1s var(--default-ease)`. Organic-shape-native and cheaper than a WebGL displacement. Library form: `morph-tile-grid`, which owns the staggered two-column anti-grid layout as well as the hover. (Cyd Stumpel, SOTD 2025-03-09; mechanic winner-verified, durations illustrative.)
- **Spotlight sharpen** — in the spotlit-installation register the hovered figure sharpens while siblings blur and dim (`focus-defocus`), the Three.js lighting rig doing the separating rather than an accent. (Iventions, Awwwards SOTD + CSSDA WOTM Oct 2025; Minh Pham, Awwwards SOTD — concept verified from the award pages, per-element amplitudes not CSS-read.)

**Nav** — three verified surface patterns, never the AI accent border-bottom:
- **Transparent → same-family glass** — transparent over the hero, then a low-alpha same-family tint + `backdrop-filter: blur()` once content scrolls under. The only line is a same-family hairline (Granola holds `#E3E3E3` at `0px` width at the top), not an accent bar. (Arc, Granola — style anchors.)
- **Solid same-cream sticky bar** — `position: sticky`, `background` set to the exact page cream (`#FFF5EE`), `border-bottom: none`. A glass-free option when the palette is one warm ground. (Cyd Stumpel, SOTD 2025-03-09.) Nav items ride the same underline-draw as body links — never give them a fill.
- **Diegetic steering instead of a bar** — in the WebGL nature/engine register the primary navigation can be an in-world object the visitor moves along a path: OceanX embeds an exploration ship guiding a free-scroll timeline the visitor runs forwards or backwards at any point, Awwwards-tagged Unusual Navigation and Horizontal Layout; Fluid Glass carries the same Unusual Navigation tag. It replaces the bar, it does not decorate one, and it degrades to an anchored nav + progress indicator on touch. Library id: `diegetic-nav`. (OceanX 2025, SOTD 2026-02-23; Fluid Glass, SOTD 2026-03-30.)

**Text**
- **Bespoke display as the artwork** — the typeface + scale is the signature before any motion: Exo Ape in Times, Granola in Melange, Cyd Stumpel in condensed Bueno, Arc in Marlin. Rotate off the overexposed kit sans. (≥4 sites.)
- **Variable-font optical-axis scroll-morph** — the archetype's signature text move and its cheapest continuation channel: bind a REGISTERED variable axis (`wght`, `opsz`) to an element's scroll view-range through native `animation-timeline`, so `font-variation-settings` interpolates across `animation-range: entry X entry Y` — a display heading morphs on its own named timeline, the footer wordmark runs the axis on another. Reversible by construction, off the main thread, degrading to the static authored axis with no timeline support and under reduced motion. Library id: `vf-scroll-morph` — nothing else in the library executes it (`kinetic-reveal`, `char-assemble`, `text-emphasis-fill` and `semantic-accent` are discrete or opacity effects). Cyd Stumpel carries it on its display title and its footer wordmark (mechanic winner-verified; the axis and amplitudes are unverified — pick a registered axis and tune the range to the face). The generic technique is verified through Codrops and Carmen Ansio.
- **Per-char scrub reveal** (hero only) — SplitText chars stagger in on scroll: `stagger: 0.02`, `duration: 0.25→0.2`, `ease: power2.out` (enter) / `power2.in` (exit), section hold `0.5–1.0`, section scrub `0.5`. Reserve for one or two hero lines. (Codrops build params; corroborated by Sculpting Harmony's kinetic type, SOTM Nov 2023, media-only.)
- **Cinematic scroll scrub** — a pinned scene scrubbed to scroll on hand-tuned eases: `cinematicSilk 0.45,0.05,0.55,0.95`, `cinematicSmooth 0.25,0.1,0.25,1`, `ScrollSmoother { smooth: 4, smoothTouch: 0.1 }`, container `500vh–900vh`, text-overlay scrub `0.5–0.8`. Only when a real 3D/WebGL scene carries the story. (Igloo Inc, SOTY 2024 + Codrops.)

**Cursor** — a choice, not a reflex. Custom follower on image/scene-forward builds (Exo Ape and Granola carry a DOM cursor element); a deliberate system cursor on a text/editorial build — Cyd Stumpel, an SOTD winner, ships no follower and leans on the button displacement + View Transitions. In the WebGL register the pointer drives the ground itself rather than a DOM layer: Igloo's particle simulation answers the pointer, and a fluid mouse-ripple is the medium's own pointer channel (`raycast-object-state` carries per-object hover and tap states inside a scene). Don't add a follower by reflex. Magnetic pull is JS-driven and unverified on any corpus site — optional, not default.

**Loader / intro** — two answers, split by asset weight. A SINGLE real-time scene needs no boundary: Igloo's intro shader flows straight into the outdoor scene with HUD chrome from frame ~0 and no loader DOM (winner-verified) — and so does the no-3D register, which paints instantly and lets `animation-timeline: view()` reveals carry the entrance (Cyd, winner-verified absence; Arc, Granola). Asset-heavy Three.js does NOT start at frame zero and must not pretend to: OceanX enters through a designed "Intro Transition WebGL" (verified Awwwards feature), and Minh Pham and Iventions load models and textures behind a designed enter-gate. The gate tracks real asset progress, resolves into the scene through a designed transition rather than a hard cut, and doubles as the first spectacle beat — library id `branded-preloader`. The no-boundary answer is Igloo-specific, not an archetype law; what stays banned is the undesigned spinner and the bare `0→100%` gate that cuts.

Native-API reality: scroll-driven `animation-timeline: view()`, View Transitions (Cyd Stumpel animates route changes with `::view-transition-old(...) { clip-path: inset(0 round var(--border-radius-from)) }` — mechanic winner-verified, the exact declaration carried from the prior read), `backdrop-filter`, and organic `clip-path` section edges are all verified in winners' authored CSS — real here, not aspirational.

**Element states — tap, focus, dormancy.** The pointer layer is one costume of the state; the tap and focus answers are not optional and not a degraded copy.
- **CTA** — `:active` collapses the offset back to `translate(0,0)` with the shadow at zero, 90–160ms; on touch the pointer displacement is dormant, so `:active` carries the whole answer. `:focus-visible` fires the same displacement and offset shadow plus a visible ring.
- **Link** — the underline sits drawn and the arrow settled on `:active` (90–160ms flash). `:focus-visible` runs the scaleX draw plus a visible ring, accessible name preserved.
- **Figure** — hover morphs the radius and crossfades to the full image; `:focus-within` mirrors it so keyboard users reach the full image and caption; tap gives the morphed state or enlarges (the `swipe-snap-gallery` Mobile Excellence line), and the resting caption is a complete rest look on its own. Contained zoom to 1.1 is the fallback, never a 1.02–1.03 twitch.
- **Index row** — hovered row lights an accent rule and surfaces metadata while siblings dim to ~45% via `:has()`. The surfaced metadata lives in the resting DOM so touch reaches it; `:focus-within` lights the row identically.
- **Heading / prose** — no pointer response anywhere in the read corpus. Text motion rides scroll and time: the variable-axis scroll-morph plus a per-line or per-char masked reveal firing once. Native timelines run on touch, so there is no separate tap answer; keep a clean accessible name via `aria-label` when the mark is split for the reveal.
- **Nav** — per-link underline draw, never a fill and never an accent border-bottom; the bar itself is transparent-then-glass or a borderless solid. The menu toggle answers the tap; a diegetic nav degrades to an anchored nav + progress indicator. `:focus-visible` shows the draw plus a ring and the bar stays keyboard-reachable.
- **Cursor** — the follower and every pointer class go dormant on touch, the press-class element answering the tap instead. Keyboard users get the finished state without the pointer choreography.

**Anti-signals** — absent from every winner examined: the pale/washed-out pastel tint fill sweep on buttons (Cyd's mix is a negligible 5%, carried by displacement; real fills are committed same-family tokens at 80–100%); the contrasting accent `border-bottom` under the nav on scroll (zero — Arc and Exo Ape carry none, Granola a same-family hairline, Cyd a borderless solid bar); one universal hover copied across every element class; a reflexive circle-follower cursor with magnetic-everything; an undesigned full-screen spinner or a bare `0–100%` gate that hard-cuts into the page; a blanket 40px+ fade-up parallax on every section; static PNG grain for depth.

## Mid-page life

The substrate is the mid-page answer: one persistent spatial ground running under every section, plus a reversible vocabulary layered over it. In the WebGL register the ground carries the seams themselves — Igloo's ice-block sections are separated by chromatic-aberration, tech-displacement and frost transitions, so the substrate IS the transition and no section ever falls to a static frame (Igloo Inc, winner-verified). In the no-3D register the reversible layer is native rather than a GSAP scrub: display type morphs a registered variable-font axis as it crosses its view-range on `animation-timeline`, and the footer wordmark runs the axis on its own timeline (Cyd Stumpel, 7.22 SOTD, mechanic winner-verified; the axis name and amplitudes are unverified and genericized — see `vf-scroll-morph`). Even the quiet SaaS register builds its mid-page motion on 13 `animation-timeline` declarations, `scroll(root)` shrink-and-parallax plus named `--hiw-step-N` step-fills (Granola, live CSS, style anchor — not a winner). Per-block entrances fire once (`toggleActions:"play"` on Cyd Stumpel; `once:` on Exo Ape) while the native timelines reverse by construction, and between inputs the idle band stays in character — a folder image breathing `translate: 0 -0.15em` on a `5s` infinite loop, a wordmark ticker at `20s linear` (Cyd Stumpel, mechanic winner-verified, durations carried from the prior read). Text motion rides scroll and time, never the pointer: hover-on-text stays link-scoped — one underline scale-draw across nav, list, and footer registers (Exo Ape, winner-verified), a gradient underline material grown from `--initial-underline-height: 0.1em` to a full highlight (Cyd Stumpel, winner-verified) — with no heading, prose, or number hover anywhere in the read corpus. Wheel smoothing is register-dependent, not universal — portfolio and experience builds smooth (Cyd Stumpel: Lenis, 28 refs, with ScrollSmoother alongside; Exo Ape: a custom lerp, zero Lenis) while the quiet register keeps the native wheel and lets the `scroll()`/`view()` timelines do the work (Granola ships no smoothing library — live CSS, verified absence). The verdict test is blunt: if a section's base is static and only a decorative overlay moves, the substrate was not built.

## Scroll texture

A wordmark marquee overflowing the viewport edge and drifting under scroll (Cyd Stumpel, winner-verified), or WebGL scroll-scrub through the scene (Igloo, shipped). A third carry is lateral: a pinned full-viewport section whose track translates horizontally as vertical scroll is consumed, the substrate riding the horizontal axis and the seams becoming horizontal wipes — both OceanX 2025 and Fluid Glass carry the Awwwards Horizontal Layout tag, and on touch the chain degrades to native horizontal swipe-snap. Library id: `horizontal-scroll-chain`. A fourth is velocity rather than position: on the smooth-scroll foundation, map instantaneous scroll speed to a capped transform on scrolling media — skew, a slight scale, an RGB split — damped back to rest when the scroll stops (`scroll-speed-oscillator`, shift mode). Igloo's particles "change colour based on their speed", so velocity as a live input is winner-verified; the specific skew mechanic is the GSAP/Lenis pattern at medium confidence, not pinned to a corpus screenshot. The design_plan names one — the organic ground still needs a directed carry down the page, never drift alone.

## Idle band

The ambient DNA itself: orbs on 15–25s drifts, snow drift, a node-graph, procedural noise — multiple channels running between inputs (multiple, winner-verified/shipped). This is the one line where several idle channels are the canon; commit them by name so the atmosphere is authored, not accidental. In the no-WebGL register the ground is `ambient-orb-field`: a fixed `pointer-events: none` layer of two or three large-radius OKLCH radial-gradient orbs at `0.15–0.25` opacity under `blur(80px)`, each drifting on its own 15–25s ease-in-out alternate cycle, compositor-only, paused off-screen and on hidden tabs, static under `prefers-reduced-motion`. Cyd Stumpel's breathing folder image and wordmark ticker are the object-scale companions to it (winner-verified mechanics).

## Channel calibration

Channel calibration — this line's winners run 4–5 distinct interaction channels (per-class states, display-type effects, cursor, idle, scroll texture, replayable spectacle); the pre-emit critique's Aliveness axis reads against that band, never against bare coverage.

## Page recipe — how this line's winners build the page

Corpus — Igloo Inc (SOTD 2024-07, Animations/Transitions 9.60, Site of the Year 2024 + Developer Site of the Year 2024 + FWA — live; copy evolved since award), Cyd Stumpel (SOTD 2025-03-09, 7.22, Developer Award 7.74 — live), OceanX 2025 (SOTD 2026-02-23, 7.44 — Awwwards feature tags + case study), Iventions (Awwwards SOTD + Developer Award + CSSDA WOTM Oct 2025, judges 8.43 — award pages), Minh Pham (Awwwards SOTD, developer 7.77 — award page), Exo Ape (live; studio profile 13 SOTD, the homepage's own award date unpinned) and Fluid Glass (SOTD 2026-03-30, 7.77 — Awwwards tags + Codrops spotlight), Sculpting Harmony (SOTM Nov 2023 + FWA, media-only, not re-verified this run).

**Anatomy** — *`engine-world`, scroll-scrubbed* (Igloo, winner-verified): 220-char `body`, zero text nodes, `overflow: hidden` — the fold's UI is in-engine HUD chrome, scroll scrubs a real-time simulation, ice-block sections are separated by frost / chromatic-aberration / displacement seams; attention and understanding fuse; the dominant climax lands LATE on an interactive particle-simulation links section (particles form the target model, colour-shift by speed, glow on shape-shift, synced to sound); rest is ambient drift; the close is a standard DOM footer with nav and links. `scrollHeight` may pin at ~1vh. Requires a committed WebGL path. *`studio-reel`, climax at the fold* (Cyd, winner-verified): marquee hero [attention] → role band [understanding] → morph-tile grid [proof] → blogs [rest] → services → contact footer [close]; the cinematic variant (Exo Ape) runs photo hero → studio → work + reel [proof; 8 videos] → media/story [rest] → contact footer; the spotlit-installation variant (Iventions, Minh Pham, verified) replaces the grid with a Three.js lighting rig walking the visitor past one lit project at a time, GSAP pacing the reveals so scroll reads as a curated walk rather than a grid. *`chapter-world`, documentary rise-and-release* (OceanX, winner-verified): a diegetic exploration ship guides a free-scroll WebGL timeline over one continuous depth-layered ocean, each chapter a hero-moment that peaks and releases, the environment always in motion beneath the copy, the axis horizontal. (Sculpting Harmony runs the media-only kinetic-type variant.) *`type-index` edges, climax on click* (executable pattern, UNVERIFIED — no dated winner corroborates the mechanic; Aristide Benoist's Awwwards win is Portfolio 2021 / Site of the Month June 2021, outside the window, and no dated Obys site corroborates it): no hero headline, a dense giant-type index over a living ground IS the page [proof-by-density], the climax is a route morph on click, the About overlay doubles as the close. The two shapes on record: a 19-entry index carrying the whole fold, and a two-canvas dark hero under a horizontal wordmark feeding an index numbered 01–30 → clients wall → awards ledger.

Route on the brief's declared inputs, never on a taste read: a real 3D or nature scene the visit moves THROUGH plus a committed WebGL path → `engine-world` (a brand world) or `chapter-world` (chaptered material) or the spotlit-installation `studio-reel` (a work portfolio); a solo, studio, or editorial-commerce brand with NO WebGL path → warm-organic `studio-reel`, where an ambient orb field is the substrate instead of a scene; a studio whose density is the argument → `type-index` (unverified pattern). Pick exactly one and never blend engine-world with warm-organic. Then pick the scroll axis once: vertical, or a `horizontal-scroll-chain` where a pinned section translates its track as vertical scroll is consumed.

**Hero architectures** — *In-engine fold* (`in-engine-hud-fold`; Igloo, shipped): the fold is the live scene; monospace HUD corners (wordmark, mission, scroll cue, sound toggle, node-graph) from frame ~0; no CTA. *Wordmark-marquee + portrait fold* (`marquee-hero`; Cyd, winner-verified): repeating Bueno-VF wordmark strip overflowing the viewport edge → utility row + serif nav → portrait mounted on a periwinkle `#8082F8` clip-path blob + serif role headline; beats: badge sticker `scale-in` .4s @.2s `--bouncy-ease`; a second sticker scroll-retimed via `animation-timeline` (mechanics winner-verified, the ranges and durations illustrative). *Full-bleed photo + bottom-display fold* (Exo Ape, winner-verified): transparent nav → intro upper-left → stacked `Digital/Design/Experience` H1 (authored `25.6vw`) → "Scroll to explore" + custom cursor. *Designed WebGL enter* (OceanX, verified tag; Minh Pham, Iventions): asset-heavy scenes enter through an "Intro Transition WebGL" that resolves into the world instead of cutting. Shared law: no filled fold CTA — the call is a scroll cue or an email link. Either branch must be ALIVE at rest once entered — a running shader, drifting orbs, a breathing idle — because a motion-dead, pointer-dead spatial hero is this archetype's first-impression defect.

**Section chain** — the winner-verified order with its intensity map and the state each section owes. Pick forms by role; never hand-write hero or section layout CSS.

| role | form | pairs | intensity | state it owes |
|---|---|---|---|---|
| hero | `marquee-hero` (warm-organic); `in-engine-hud-fold` (WebGL); `type-index-grid` (density) | mark `char-assemble` \| `kinetic-reveal`; media `clip-reveal`; ground `shader-surface` \| `ambient-orb-field`; sticker `vf-scroll-morph` | 8 | the substrate is alive on the fold — a running scene, drifting orbs, or procedural noise, never a static frame; no filled CTA (scroll cue or email link); the warm register overflows the wordmark strip and mounts the portrait on a clip-path blob; the WebGL register runs HUD corners from frame ~0 for a single scene, or a designed enter-gate for asset-heavy Three.js |
| continuation-substrate | `shader-surface` (WebGL ground); `ambient-orb-field` (no-3D ground); `organic-section-edge`; `horizontal-scroll-chain` | `vf-scroll-morph`; `smooth-scroll`; `ambient-idle`; wordmark-marquee drift; `scroll-speed-oscillator` | 7 | the persistent layer running UNDER every section, reversible and compositor-only: the WebGL scene drifts and its transitions ARE the seams; the no-3D ground drifts 2–3 large-radius OKLCH orbs on 15–25s cycles behind glass while the variable-axis morph rides scroll view-ranges |
| proof / work-grid | `morph-tile-grid`; `index-list` (spotlight); `card-list`; `swipe-snap-gallery` (mobile) | `figure-hover` (fallback zoom 1.1); `index-row-hover`; `focus-defocus` (spotlit register) | 7 | figure hover is a radius morph rounder plus a resting graphic crossfading to the full image and a caption slide-up — geometry carries it, no accent, never a 1.02–1.03 twitch; the spotlit register sharpens the hovered figure while siblings blur and dim; index rows light an accent rule and surface metadata, siblings to ~45% |
| feature / understanding | `editorial-split`; `type-as-image` (role band) | h2 `char-assemble`; prose `text-emphasis-fill`; terms `semantic-accent`; media `clip-reveal` \| `image-curtain` | 5 | the rest beat — but the substrate behind it still moves, the orbs drift, the scene does not park; headings enter masked or per-char ONCE; key terms carry the accent on first view; no pointer hover on prose |
| spectacle peak | `webgl-scene` (delegated); `morph-tile-grid` (warm fold-peak) | `shader-surface`; `dolly-zoom`; `scramble-decode` (engine chrome) | 10 | the ONE dominant moment — Igloo's interactive particle simulation (colour-by-speed, glow on shape-shift, sound-synced), a documentary's deepest chapter, or the unverified type-index route morph on click; capped at one, placed LATE in the engine and documentary registers and at the FOLD in warm-organic; fully driven, never a static frame |
| close / footer | `close-panel` + `organic-section-edge` (contact-first) | ask `kinetic-reveal`; wordmark `vf-scroll-morph`; channels `accent-link` + `masked-label-swap` | 6 | contact-first with a clip-path organic edge and an offset shadow riding the accent; the footer wordmark's axis morph is the quiet second peak; never a fat sitemap |

**Footer** — a contact-first moment, never a fat sitemap (winner-verified). Cyd (`close-panel` + `organic-section-edge`, contact-first): project prompt + availability + copy-email pill, offset shadow riding the periwinkle accent `#8082F8`, over a clip-path edge. Exo Ape: address + email + phone + socials. Igloo: a standard DOM footer carrying nav and links — the engine hands the close back to the DOM. A typeset tabular-index close (statement + email + ©; socials + clients wall + awards ledger) belongs to the `type-index` pattern and stays unverified, as does an in-world HUD sign-off — no corpus winner confirms a footer rendered inside the engine.

**Arrival** — the Loader row holds (`ingredients/preloaders.md`): no boundary for a single real-time scene — the intro shader flows into the world, HUD from frame one, no loader DOM (Igloo, winner-verified); instant paint + `animation-timeline` reveals, no `0→100%` gate (Cyd, winner-verified absence); a `P.intro` sentence over the hero photo (Exo Ape); a real-time Gehry sketch (Sculpting Harmony, media-only); a designed asset-tracking enter-gate resolving into the scene for asset-heavy Three.js (OceanX's "Intro Transition WebGL", verified tag; `branded-preloader`). Routes (`ingredients/page-transitions.md`): View Transitions, `.work-thumb` shared-element morph, `--thumb-radius: 50%` (Cyd, winner-verified mechanic, exact token illustrative); the type-index view toggle is within-page with no route curtain (unverified pattern).

**Copy voice** — Quoted to calibrate, never to ship — imitate the specificity (the named place, the count, the refusal), never the wording. Person: product → first-person-plural manifesto; studio → third-person, process-as-offer; solo → first person + all-caps labels. One long intro sentence, then noun-phrase labels — the substrate carries the mood, the words name the nouns. Warm verbs, never transactional. Terminal marks (`//`) in the engine register, slash-indexing in portfolios. Refuses hype, pricing, feature lists, exclamation marks.
- "Our mission is to create the largest onchain community, driving the consumer crypto revolution." (Igloo, winner-verified via igloo.inc and Founders-Fund coverage) — names its noun and its frontier; no button follows.
- "Available October 2026" · "Have a project in mind?" (Cyd) — availability as fact, contact as a question.
- The third-person process-as-offer register has no verified corpus quote this run; write it from the brief's own nouns rather than from a borrowed line.

**Imagery art direction** — one grade page-wide or one deliberate split; never stock. Igloo: synthetic luminous ice over greyscale snow in fog. OceanX: deep-ocean grade, depth-layered, an environment rather than a backdrop (Africa's deep-sea frontiers, the Coral Triangle). Exo Ape: architecture photo + film, blue-hour desaturated, full-bleed, sand frame. Cyd: warm real portrait on periwinkle `#8082F8` clip-path shapes, split with pixel-art, stickers, type-as-image. Iventions and Minh Pham: the lighting is the art direction — each project lit as an installation, the grade coming from the rig. Sculpting Harmony (media-only): archival + 3D, pop-color chapters. In the unverified type-index register, greyscale photography in thin vertical bands over pure black (Aristide Benoist, out-of-window).

**Mobile / touch** — pointer-driven classes go dormant on touch (pointer-parallax, `conic-border-shine`, `focus-defocus`, magnetic, the DOM follower, `liquid-glass-refraction`), and depth arrives by SCROLL instead: native `animation-timeline` reveals and the variable-axis morph both run on touch, as do the clip-path reveals, so the archetype keeps its identity without a pointer. Horizontal-Layout chains convert to native horizontal swipe-snap rather than a pinned scrub; a diegetic ship or path nav degrades to an anchored nav + progress indicator. The WebGL substrate is reconsidered, not dropped — lower poly, fewer orbs, progressive quality, a static frame under low power. Glass keeps its opaque fallback and `backdrop-filter` stays only on fixed and sticky surfaces; ambient orbs sit on fixed `pointer-events: none` layers, never on scrolling ones. Press-class controls answer the tap with a 90–160ms flash floor, since the pointer displacement is dormant. Galleries become `swipe-snap-gallery` tracks riding OS momentum with tap-to-enlarge, the scored Mobile Excellence line. No follower cursor. `prefers-reduced-motion` freezes the scene and orbs to a legible frame and swaps scrubbed media to a poster — Cyd ships its whole motion set on View Transitions + native `animation-timeline`, mobile-safe by construction.

**Variation** — this section chain is one legal costume of the archetype, never THE skeleton. Structure is story-native: the body's sections derive from the universe's spine, then check against these roles for coverage — never the reverse. The axes serial winners measurably rotate between builds (21-artifact corpus, 5 studios): body content archetype and item counts, the ONE signature device (never reused across builds), the close mechanism, the hero medium, the index/HUD costume. What persists as DNA: type grammar, the motion register (the register itself, never the named reading/interaction kit — that kit is a device, rotated per build like the signature), annotation grammar as a form, engineering architecture. The same content archetype + item count + close mechanism recurring across two different-brand builds has zero winner precedent.

**Anti-signals** — page-level absences (winner-verified): no bento/card-grid fold; no undesigned `0→100%` preloader cutting into the page; no accent nav `border-bottom`; no fat sitemap; no filled fold CTA; no stock; no neon/corporate-blue; no single hover across classes (Effect palette); no flat, rectangular, pointer-dead section after the hero — the substrate is not optional.

## Spectacle menu

*Igloo, the scroll-grown ice world* (winner-verified): scroll grows procedural blocks into an assembled dome under a live node-graph, each section seam a frost / chromatic-aberration / displacement transition in the substrate, and the payoff is an interactive particle-simulation links section — particles form the target model, colour-shift by speed, glow on shape-shift, synced to sound; the Animations/Transitions 9.60 centerpiece. *OceanX, the guided descent* (winner-verified): a diegetic exploration ship carries a free-scroll WebGL timeline through a depth-layered ocean on a horizontal axis, each chapter rising and releasing at documentary pace. *Sculpting Harmony, type dancing to the orchestra* (media-only): scroll a chapter → condensed type stretches to LA Phil extracts, chapter colors shift → the cursor trails Gehry quotes.

**The hero beat.** The first viewport commits the SPATIAL SUBSTRATE, never a filled CTA — the call is a scroll cue or an email link. WebGL register: the fold IS the live scene, with in-engine HUD corners from frame ~0 for a single real-time scene (Igloo), or a designed enter-gate that resolves into the world for asset-heavy Three.js (OceanX, Minh Pham, Iventions). Warm-organic register: a composed organic fold — a repeating variable-font wordmark strip over a real portrait mounted on a periwinkle `#8082F8` clip-path blob, a badge sticker scaling in on the bouncy ease and a second sticker scroll-retimed on `animation-timeline`. Either branch is ALIVE at rest once entered.

**The continuation beats** — the page is diffed against these, section by section.
- *substrate* — MANDATORY, EVERY SECTION: the WebGL scene drifts and its transitions are the seams (Igloo, winner-verified), or the no-3D ground drifts its orbs while the variable-axis morph and the marquee drift carry the read (Cyd, winner-verified). Never a static base with a decorative overlay on top.
- *proof / work grid* — the organic geometry does the work: radius morph plus crossfade per tile (Cyd), or one spotlit project after another under a continuously running lighting rig (Iventions, Minh Pham, verified).
- *rest beat* — the role band and the editorial split drop to intensity 5, and the substrate keeps moving underneath. Rest is amplitude, never silence.
- *chapter release* (documentary only) — each chapter peaks then releases over an ocean that never stops moving, so the release beats stay driven (OceanX, winner-verified).
- *route transition* (multi-view only) — View Transitions carry a shared-element morph from tile to detail; the navigation is a momentum beat, not a cut (Cyd, winner-verified).
- *footer* — QUIET SECOND PEAK: the footer wordmark runs its variable axis on its own timeline over a clip-path organic edge, an offset shadow riding the accent (Cyd, winner-verified).

**The peak law** — verdict REFINED, from the winner evidence. Keep peaks capped, make the continuation MANDATORY, and register the late peak: ship a PERSISTENT SPATIAL SUBSTRATE spanning hero to footer — a living ground (a WebGL scene, an ambient OKLCH orb field, or procedural noise) plus a reversible motion vocabulary (organic clip-path geometry, a variable-font optical-axis scroll-morph, a named idle band) — and cap the amplitude peaks at ONE dominant plus an optional quiet second at the footer. The dominant peak is NOT required to sit at the hero: the hero commits the SUBSTRATE, and the peak may land late — Igloo's particle sim, a documentary's deepest chapter, or the unverified type-index's on-click route morph. The failure to forbid is SILENCE: a section where the substrate goes static, or the page reads flat, rectangular and pointer-dead, is "no depth", the defect. Peaks are scarce; the substrate is not optional; a flat section is the sin. Distinct from immersive, where peaks may multiply — here the warm-organic register genuinely caps them and lets the continuation stay ambient.

Evidence: Igloo Inc runs one WebGL substrate from the frame-one intro shader through ice-block sections whose seams are frost, chromatic-aberration and displacement transitions, to the interactive particle-simulation links section where the dominant peak lands LATE — the hero is not the climax and no section between them is silent; this is the Animations/Transitions 9.60 centerpiece (winner-verified), and it contradicts "one wow at the hero, then quiet". Cyd Stumpel caps peaks genuinely at one dominant (the fold) plus a quiet second (the footer wordmark morph), while the substrate vocabulary — organic clip-path geometry, the variable-axis scroll-morph, marquee drift, idle breathing — is mandatory every section and never multiplied into more peaks: the warm-organic proof that continuation is ambient and reversible rather than a stack of spectacles (winner-verified). OceanX 2025 runs a chaptered multi-rise over one continuous ocean on a horizontal axis, intensity peaking and releasing per chapter above a ground that is never static (SOTD 2026-02-23, 7.44). Iventions and Minh Pham win with a persistent driven ground and no loud peak at all — the lighting rig IS the continuation, "WebGL used for atmosphere instead of spectacle" — which refutes the idea that this archetype needs a hero wow to hold (Awwwards SOTD; CSSDA WOTM Oct 2025 judges 8.43). Across the corpus the substrate is the identity: spatial-organic's premise is continuous depth, not a single dimensional moment.

## Component index

Generated from `assets/components/manifest.json` — the authority for slots, variants, tokens, deps and `init` signatures, and the only place 11 of the 103 components record facts their file headers omit. Each row is the id plus the opening of its `whenToUse`, clipped: enough to pick, never enough to build. Grep the manifest for the chosen id to get its contract. Forms are the page skeletons (CSS, slots, variants); components are the behaviours that mount into their slots.

**Forms** (8) — page skeletons
- `bare-cue` — The gallery-stack's minimal close (Contassot / Vitasovic): no footer chrome, just a back-to-top cue ('SCROLL UP') and a year/edition mark on one slim baseline…
- `card-list` — Release/journal/blog cards in a 2-3 column grid: media 3/2, kicker/title/date at fixed rhythm; minmax(0,1fr) columns so a long title wraps instead of blowing…
- `in-engine-hud-fold` — The WebGL-register hero: HUD chrome at the four corners — wordmark TL, sound toggle TR, mission line BL, scroll cue bottom-centre, live node-graph BR…
- `index-list` — The row-list body under index-reel-header: index/title/meta/thumb locked to one shared grid so column edges cannot drift and the meta cannot sprawl.
- `marquee-hero` — The warm-organic fold: a repeating variable-font wordmark strip OVERFLOWING the viewport edge (authored repeated, aria-hidden — the h1 names the fold…
- `morph-tile-grid` — The Cyd work grid: repeated tile links on a staggered 2-column grid (even tiles drop — the anti-grid flow), each pairing a radius MORPH with a CROSSFADE.
- `swipe-snap-gallery` — The mobile-first image gallery: native scroll-snap track riding OS momentum (zero JS physics), next-cell peek, enhancer-fed snap dots.
- `type-index-grid` — No marketing hero, no prose — the 100svh fold IS a dense index of oversized title rows locked to ONE shared grid (--_cols defined once, every row locks to it)…

**Components** (17) — behaviours
- `ambient-orb-field` — The WebGL-free living ground for the warm/dark-glass registers: a FIXED pointer-events:none layer of 2-3 large-radius OKLCH radial-gradient orbs at .15-.25…
- `border-glow-bloom` — The blurred accent under-glow that lifts a card — breathes up on hover/focus; the blur never animates, only opacity (compositor-clean).
- `conic-border-shine` — The cursor-tracked border light: an accent glow masked to the card's 1px edge follows the pointer.
- `diegetic-nav` — In-world steering as the primary nav: the builder's real <nav> of anchor links becomes a fixed rail with the gap's four slots — a moving avatar/vehicle…
- `dolly-zoom` — The scroll dive: a pinned full-bleed media scales toward a targeted focal point (the moon, the product, the plate) as the track scrolls — reversible…
- `fill-invert-cta` — The universal primary-CTA move: full-token flood + label inversion on hover/focus — fill (direct pole swap) or wipe (a panel rises from the bottom edge).
- `glass-card` — The spatial-organic signature surface: backdrop-blur glass with the inset highlight and concentric nested radii (Doppelrand); opaque fallback keeps text…
- `horizontal-scroll-chain` — The chained lateral macrostructure: a pinned full-viewport section whose track translates horizontally as vertical scroll is consumed — a PURE function of…
- `liquid-glass-refraction` — The refraction end of the glass register: an SVG feDisplacementMap lens (red/green ramp map, objectBoundingBox primitives so one filter serves every pane)…
- `nav-hero-surface` — The SURFACE axis for a minimal PERSISTENT bar (the winner-norm nav that never hides): floats transparent over the hero, gains owned --ad-ground when the…
- `organic-section-edge` — The anti-grid flow boundary: data-ad-edge="top|bottom|top bottom" carves a soft quadratic arc into a section edge via clip-path: shape() — apex at the box…
- `pointer-parallax` — Multi-layer depth under the pointer: [data-depth] layers shift a few px at differential rates (lerp 0.1, ~20px max — depth, never drift; negative depth moves…
- `raycast-object-state` — Per-object hover/tap/hit states for interactive meshes INSIDE a WebGL scene — the axis the DOM-element canon omits.
- `scroll-camera-dive` — The true-3D camera dive: scroll progress scrubs a real camera PATH — position + lookAt (+ optional FOV) keyframes, linearly interpolated, inertially eased so…
- `shader-surface` — The token-driven WebGL texture layer — gradient-mesh, noise-field, or pointer-ripple painted from the DESIGN.md palette.
- `smooth-scroll` — Smoothed-scroll foundation for scrubbed/pinned reveals.
- `vf-scroll-morph` — The archetype's signature text move and cheapest continuation channel — NOTHING else in the manifest executes it…
