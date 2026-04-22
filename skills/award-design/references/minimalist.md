# Minimalist

Extreme whitespace, 2-3 color maximum, every element justifies its existence. Typography carries the design.

## Typography

**Headlines**: Suisse Int'l, Neue Haas Grotesk, Söhne, PP Neue Montreal — 48-120px, weight 500-700
**Body**: Same family at 16-18px, weight 300-400, line-height 1.6-1.7
**Pairing**: Single family with weight contrast, or geometric sans (headlines) + humanist sans (body)
**Tracking**: Tight on headlines (-0.02em), normal on body

## Color

| Role | Values |
|------|--------|
| Background | Warm: #FAFAF5, #E8E4DF · Cool: #F5F5F0, #F8FAFC |
| Text | #2D2D2D (primary), #6B7280 (secondary) |
| Accent | Single: electric blue #007BFF, sage #87A98F, or coral #E07A5F |
| Borders | rgba(0,0,0,0.06) or #EAEAEA |

**Rule**: If you can remove a color and nothing breaks, remove it.

## Layout

Single-column or asymmetric broken-grid. One bold focal point per viewport. Generous macro-whitespace (120-200px+ section padding).

```css
.wrapper {
  display: grid;
  grid-template-columns: 1fr min(65ch, 100%) 1fr;
  gap: clamp(3rem, 8vw, 12rem);
  padding: clamp(2rem, 5vw, 8rem);
}
.wrapper > * { grid-column: 2; }
.full-bleed { grid-column: 1 / -1; }
```

## Animation

"Less is more" philosophy:

- Fade-ins: opacity 0→1, translateY 20→0, duration 0.6-0.8s
- Easing: `cubic-bezier(0.16, 1, 0.3, 1)`
- Lenis smooth scrolling
- GSAP Flip for page transitions
- Hover: gentle opacity shifts (0.7→1), scale 1.02-1.05

**Forbidden**: Heavy parallax, kinetic type, particle effects, scroll hijacking, glitch effects.

## Ideal for

SaaS (Stripe, Linear), luxury brands, architecture studios, high-end portfolios, design tool landing pages.

## Reference studios

Locomotive (Montreal), 14islands (Stockholm).
