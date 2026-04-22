# Spatial Organic

The post-grid, dimensionally-aware aesthetic for 2026-2027. Fuses visionOS spatial depth, organic natural forms, and native web APIs. The counter-reaction to bento saturation, "blanding" minimalism, and heavy parallax.

## Philosophy

Digital surfaces that feel physical and alive. Depth comes from z-axis layering, not flat shadows. Shapes flow instead of snapping to grids. Textures are procedural and animated, not static overlays. Technology serves tactility — WebGPU, View Transitions, and CSS Scroll-Driven Animations enable effects that were previously impossible or demanded heavy JS.

## Typography

**Headlines**: Variable fonts animated on scroll/hover — Fragment, GT Flexa, or bespoke typefaces. Weight and width shift as the user scrolls, making type feel reactive and alive.
**Body**: Rounded, warm sans-serifs — Outfit, General Sans, Satoshi — 16-18px, weight 400
**Display technique**: Typography as hero element — oversized kinetic type functioning as the primary design element, not just communication
**Cross-cultural**: "Lingua-Lettering" — unified visual rhythm across Latin, Arabic, CJK when applicable

```javascript
// Variable font weight responds to scroll position
gsap.to('.hero-title', {
  fontVariationSettings: "'wght' 800, 'wdth' 125",
  ease: 'none',
  scrollTrigger: { trigger: '.hero', scrub: true }
});
```

## Color

| Role | Values |
|------|--------|
| Background | Rich darks: #0D1117, #111827, deep forest #0A1628 |
| Text | Warm off-white #E8E4DF, cream #F0EDE8 |
| Nature accents | Sage green #87A98F, terracotta #C67D5B, deep ocean #1E3A5F |
| Ambient orbs | OKLCH gradient orbs — opacity 0.15-0.25, large radius, slow-moving |
| Glass surfaces | rgba(255,255,255,0.05) with backdrop-blur 24px |

**Palette strategy**: Earthy and muted — never neon, never corporate blue. Colors should feel found in nature, not picked from a design tool.

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

Anti-grid. Flowing, organic positioning. Elements placed with intentional asymmetry, not mathematical regularity. Generous negative space creates breathing room. Soft `clip-path` curves instead of rectangular sections.

```css
/* Organic section divider */
.section-organic {
  clip-path: ellipse(80% 100% at 50% 0%);
  padding: clamp(6rem, 12vw, 14rem) clamp(2rem, 5vw, 8rem);
}

/* Flowing content with intentional offset */
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

## Dark Glassmorphism

The "Liquid Glass" treatment — Apple WWDC 2025 validated glassmorphism as lasting. Glass over dark backgrounds with ambient gradient color orbs:

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

/* Ambient gradient orbs behind glass surfaces */
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

## Animation

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
  to { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
}
```

### View Transitions (seamless page navigation)

```css
@view-transition { navigation: auto; }
::view-transition-old(root) { animation: fade-out 0.4s ease; }
::view-transition-new(root) { animation: fade-in 0.4s ease; }
```

### Procedural noise/texture (Canvas or WebGL, never static PNG)

```javascript
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');
function renderGrain() {
  const imageData = ctx.createImageData(canvas.width, canvas.height);
  for (let i = 0; i < imageData.data.length; i += 4) {
    const v = Math.random() * 20;
    imageData.data[i] = imageData.data[i+1] = imageData.data[i+2] = v;
    imageData.data[i+3] = 12; // very subtle
  }
  ctx.putImageData(imageData, 0, 0);
  requestAnimationFrame(renderGrain);
}
```

### Motion philosophy

Organic easing — nothing linear, nothing mechanical:

```css
:root {
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
  --ease-smooth: cubic-bezier(0.25, 0.1, 0.25, 1);
}
```

- Spring physics for interactive elements
- Slow ambient motion (15-25s cycles) for background elements
- Fast response (200-400ms) for user interactions
- Blur transitions (`filter: blur(4px)` → `blur(0)`) for depth perception

## WebGPU (when 3D is needed)

Three.js r171+ with automatic WebGL fallback. TSL (Three Shading Language) for shader logic in JS/TS:

```javascript
import { WebGPURenderer } from 'three/webgpu';
const renderer = new WebGPURenderer({ antialias: true });
// Falls back to WebGL automatically if WebGPU unavailable
```

Use for: organic particle systems, noise-based terrain, flowing abstract shapes. Not for product showcases (use image/video).

## Ideal for

Sustainability brands, wellness/health tech, post-2025 creative studios, premium direct-to-consumer, environmental organizations, artisan/craft brands, brands wanting premium warmth without corporate coldness.

## What makes this archetype award-worthy

1. **Novelty**: Post-bento, post-blanding — judges haven't seen hundreds of these yet
2. **Technical depth**: Native APIs (View Transitions, Scroll-Driven, WebGPU) signal developer sophistication
3. **Accessibility path**: CSS Scroll-Driven animations degrade gracefully; organic shapes don't require motion to communicate
4. **Performance story**: Off-main-thread animations, procedural textures (no heavy asset downloads), variable fonts (one file)
5. **The tension resolved**: Visual richness through depth and texture, not through weight and complexity
