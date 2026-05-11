# Spatial Organic

The post-grid, dimensionally-aware aesthetic for 2026–2027. Fuses visionOS spatial depth, organic natural forms, and native web APIs (View Transitions, Scroll-Driven Animations, WebGPU). The counter-reaction to bento saturation, blanding minimalism, and heavy parallax. The article's *Trends Shaping 2025–2030* section credentials the constituent moves (Liquid Glass, dark glassmorphism, organic shapes, procedural noise) but does not yet credential a single SOTM-tier reference site for the archetype as a whole. The archetype is forward-looking — it has trend evidence, not yet a canonical site.

**Forward-archetype note.** Where the eight article-credentialed archetypes (Minimalist, Brutalist, Editorial, Bold/Maximal, Immersive, Experimental, Corporate Luxury, Bento) are anchored to specific SOTM-or-higher winners in the 2024–2026 window, Spatial Organic is anchored to the article's trend section and to emerging brands (Arc Browser, Granola, Apple Vision Pro). When a brief genuinely fits this archetype, expect the project itself to set the credentialed reference rather than copying one.

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
- **Body**: rounded warm sans-serifs — Outfit, General Sans, Satoshi — 16–18px, weight 400
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
