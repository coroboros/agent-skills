# Bold / Maximal

Every viewport inch filled with organized chaos. Layered compositions, 4-6+ saturated colors, kinetic typography as art.

## Typography

**Display**: Monument Extended, Clash Display, Satoshi — 100-300px+, variable font weight animation
**Body**: Satoshi, PP Neue Montreal — 16-18px, weight 400
**Kinetic**: GSAP SplitText for splitting and reforming, weight/width interpolation on scroll
**Scale**: Extreme contrast between display (200-300px) and body (16px)

## Color

| Role | Values |
|------|--------|
| Background | Dark: #0A0A0A, #1A1A2E · Or any saturated base |
| Primaries | 4-6+ simultaneous high-saturation colors |
| Neon accents | Electric lime #CCFF00, hot magenta #FF00FF, cyan #00FFFF |
| Gradients | OKLCH multi-hue, animated via `@property` |

**Rule**: More is more — but organized. Every color has a role in the hierarchy.

## Layout

Layered compositions mixing photography, illustration, and 3D. Intentional overlap, z-index choreography.

```css
.maximal-hero {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  grid-template-rows: repeat(8, 1fr);
  min-height: 100dvh;
}
.hero-image { grid-area: 1/1/9/8; z-index: 1; }
.hero-title {
  grid-area: 3/4/7/13;
  z-index: 2;
  mix-blend-mode: difference;
  font-size: clamp(4rem, 10vw, 15rem);
}
.hero-tag { grid-area: 7/9/9/13; z-index: 3; }
```

## Animation

Constant, choreographed motion:

- Stagger: 200-400ms between elements in sequences
- Variable font animation on scroll (weight 100→900, width 75→150)
- Multi-layer parallax at different speeds
- GSAP timelines with pinned scroll sections
- `@property` animated gradients

```javascript
gsap.to('.display-text', {
  fontVariationSettings: "'wght' 900, 'wdth' 150",
  scrollTrigger: { trigger: '.section', scrub: 1 }
});
```

```css
@property --hue { syntax: "<number>"; inherits: false; initial-value: 0; }
.shifting-bg {
  background: oklch(50% 0.2 var(--hue));
  animation: hue-shift 8s linear infinite;
}
@keyframes hue-shift { to { --hue: 360; } }
```

## Ideal for

Creative agencies, entertainment, music festivals, Gen Z brands, campaign microsites, event landing pages.
