# Spatial Organic

The post-grid, dimensionally-aware aesthetic for 2026–2027. Fuses visionOS spatial depth, organic natural forms, and native web APIs (View Transitions, Scroll-Driven Animations, WebGPU). The counter-reaction to bento saturation, blanding minimalism, and heavy parallax. The article's *Trends Shaping 2025–2030* section credentials the constituent moves (Liquid Glass, dark glassmorphism, organic shapes, procedural noise); the award record since supplies the reference sites — Igloo Inc (Site of the Year 2024) at the head of a verified winner corpus (see *Effect palette* below).

**Anchor note.** The article anchored this line to its trend section and to emerging brands (Arc Browser, Granola, Apple Vision Pro); the awarded corpus now anchors it directly — Igloo Inc (Site of the Year 2024), Cyd Stumpel (SOTD Mar 2025), Exo Ape (SOTD May 2022), Sculpting Harmony (SOTM Nov 2023). Arc and Granola stay style anchors, not winners; the *Effect palette* below reads the recipes from the winners' own CSS.

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

The Doppelrand technique (nested concentric containers — outer shell with hairline border, inner core with smaller radius and inner highlight) sharpens glass cards into "machined hardware" rather than flat tiles. See `premium-patterns.md` pattern 1 (Doppelrand) and pattern 9 (Liquid Glass Refraction). The Liquid Glass pattern is the canonical Spatial Organic glass register — apply it on every glass surface in this archetype, not as an optional flourish.

**Performance lock**: `backdrop-filter` belongs only on fixed or sticky elements (navbars, modal overlays). Applying it to scrolling containers triggers continuous GPU repaints and collapses mobile frame rate. Ambient orbs sit on `position: fixed; pointer-events: none` layers — never on scrolling surfaces.

## Motion

Native-first. Browser APIs over JS libraries where possible.

### CSS Scroll-Driven (off main thread, guaranteed 60fps)

```css
.organic-reveal {
  animation: emerge linear both;
  animation-timeline: view();
  animation-range: entry 0% entry 80%;
}
@keyframes emerge {
  from { opacity: 0; transform: translateY(40px) scale(0.97); filter: blur(4px); }
  to   { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
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

## Effect palette — what this line's winners ship

The awarded corpus carrying this DNA: Igloo Inc (SOTY 2024), Exo Ape (SOTD May 2022), Cyd Stumpel (SOTD Mar 2025), Sculpting Harmony (SOTM Nov 2023), Obys (SOTM + CSSDA Studio of the Year), Aristide Benoist (SOTM Jun 2021). Arc and Granola stay as CSS-verified style anchors — not winners.

**The grammar** — cohesion is one shared substrate under class-specific mechanisms. Fix one accent token, one easing table, one radius language, one display face; then vary the *mechanism* per element class — displacement for buttons, a drawn line for links, a shape morph for images, silence or glass for nav. Cyd Stumpel glues it all with `--default-duration: 1.3s`, `--default-ease: cubic-bezier(0.25,1,0.5,1)` (ease-out-quart), `--bouncy-ease: cubic-bezier(0.34,1.56,0.64,1)` for interactives. The AI failure is the inverse — one mechanism (a pale fill) copied onto every class over an ad-hoc palette.

**Buttons / CTA**
- **Accent-displacement push** — base surface barely moves; the button translates a few px and a hard, un-blurred offset shadow in the accent color appears on the opposite side, a card lifting off a colored underlayer. Cyd Stumpel `.button:hover`: `background: color-mix(in srgb, var(--color-background) 95%, var(--color-accent))` (a deliberate 5% tint), `color: var(--color-accent)`, `transform: translate(-2px, 2px)`, `box-shadow: -1px 1px 0 0 var(--color-accent)`, `64px` pill. Default button on a warm editorial ground. (Cyd Stumpel, SOTD Mar 2025; exact 1px-accent-shadow variant single-source.)
- **Committed same-family fill** — for a fill, swap to a defined `-hover` token one step within the brand family, never a pale pastel: Granola resolves to `--color-fill-accent-hover` / `oats-green-300 → 400`, one warm step darker. (Granola, style anchor, not a winner.)
- **The 80% primary fill** — reserve the strong fill for the single primary submit per view: Cyd Stumpel form submit `background: color-mix(in srgb, var(--color-accent) 80%, var(--color))`. Never spray it on every button. (Cyd Stumpel, SOTD Mar 2025.)

**Links**
- **Underline draw** — a pseudo-element scaling `0→1`, not a `text-decoration` toggle: Exo Ape runs one `:hover::after { transform: scaleX(1) }` across nav, list, footer and body links (color also shifts to `--color-light-grey`). This is where the accent line belongs — on links, never as nav chrome. (Exo Ape, SOTD May 2022.)
- **Accent wash + arrow nudge** — for inline/utility links, a 10% accent wash + a 1px lift + a diagonal arrow shove. Cyd Stumpel `.platform-link:hover`: `background: color-mix(in srgb, var(--color-accent), transparent 90%)`, `transform: translateY(-1px)`, arrow child `translate(2px, -2px)`. Arrow nudge corroborated by Arc; the 10% wash single-source. (Cyd Stumpel, SOTD Mar 2025.)

**Figures / cards**
- **Border-radius morph + crossfade** — the tile's radius animates rounder while a resting graphic crossfades to the full image and the caption slides up; no accent, the geometry carries it. Cyd Stumpel `.work-thumb:hover`: `.img-container { border-radius: var(--hover-radius) }`, circle overlay `opacity 1→0` / full image `0→1`, title `translateY(0)`; timing `opacity .2s .1s ease-out, border-radius .2s .1s var(--default-ease)`. Organic-shape-native and cheaper than a WebGL displacement. (Cyd Stumpel, SOTD Mar 2025; exact recipe single-source.)

**Nav** — two verified surface patterns, never the AI accent border-bottom:
- **Transparent → same-family glass** — transparent over the hero, then a low-alpha same-family tint + `backdrop-filter: blur()` once content scrolls under. The only line is a same-family hairline (Granola holds `#E3E3E3` at `0px` width at the top), not an accent bar. (Arc, Granola — style anchors.)
- **Solid same-cream sticky bar** — `position: sticky`, `background` set to the exact page cream (`#FFF5EE`), `border-bottom: none`. A glass-free option when the palette is one warm ground. (Cyd Stumpel, SOTD Mar 2025.) Nav items ride the same underline-draw as body links — never give them a fill.

**Text**
- **Bespoke display as the artwork** — the typeface + scale is the signature before any motion: Exo Ape in Times, Granola in Melange, Cyd Stumpel in condensed Bueno, Arc in Marlin. Rotate off the overexposed kit sans. (≥4 sites.)
- **Per-char scrub reveal** (hero only) — SplitText chars stagger in on scroll: `stagger: 0.02`, `duration: 0.25→0.2`, `ease: power2.out` (enter) / `power2.in` (exit), section hold `0.5–1.0`, section scrub `0.5`. Reserve for one or two hero lines. (Codrops build params; corroborated by Sculpting Harmony's kinetic type, SOTM Nov 2023.)
- **Cinematic scroll scrub** — a pinned scene scrubbed to scroll on hand-tuned eases: `cinematicSilk 0.45,0.05,0.55,0.95`, `cinematicSmooth 0.25,0.1,0.25,1`, `ScrollSmoother { smooth: 4, smoothTouch: 0.1 }`, container `500vh–900vh`, text-overlay scrub `0.5–0.8`. Only when a real 3D/WebGL scene carries the story. (Igloo Inc, SOTY 2024 + Codrops.)
- Variable-font `wght/wdth` scroll-morph is not verified on any winner this pass — ship as a supporting flourish, not a headline claim.

**Cursor** — a choice, not a reflex. Custom follower on image/scene-forward builds (Exo Ape and Granola carry a DOM cursor element); a deliberate system cursor on a text/editorial build — Cyd Stumpel, an SOTD winner, ships no follower and leans on the button displacement + View Transitions. Don't add a follower by reflex. Magnetic pull is JS-driven and unverified on any corpus site — optional, not default.

**Loader / intro** — fold the intro into the scene (Igloo Inc's real-time intro flows into the experience — single-source, WebGL) or paint instantly and let `animation-timeline: view()` reveals carry the entrance (Arc, Granola). No full-screen spinner, no `0→100%` gate.

Native-API reality: scroll-driven `animation-timeline: view()`, View Transitions (Cyd Stumpel animates route changes with `::view-transition-old(...) { clip-path: inset(0 round var(--border-radius-from)) }`), `backdrop-filter`, and organic `clip-path` section edges are all verified in winners' authored CSS — real here, not aspirational.

**Anti-signals** — absent from every winner examined: the pale/washed-out pastel tint fill sweep on buttons (Cyd's mix is a negligible 5%, carried by displacement; real fills are committed same-family tokens at 80–100%); the contrasting accent `border-bottom` under the nav on scroll (zero — Arc and Exo Ape carry none, Granola a same-family hairline, Cyd a borderless solid bar); one universal hover copied across every element class; a reflexive circle-follower cursor with magnetic-everything; a full-screen spinner or `0–100%` preloader gate; a blanket 40px+ fade-up parallax on every section; static PNG grain for depth.
