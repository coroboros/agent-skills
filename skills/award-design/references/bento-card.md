# Bento / Card-Based

Modular asymmetric tiles inspired by Japanese bento boxes. Self-contained information units with individual visual treatment.

## Typography

**Headlines**: Geist, Satoshi, Cabinet Grotesk — 24-48px, weight 600
**Body**: Same family — 14-16px, weight 400
**Metrics/data**: Monospace (Geist Mono, JetBrains Mono) for numbers and data points

## Color

| Role | Values |
|------|--------|
| Background | Dark: #0A0A0F, #12121A · Light: #F9FAFB |
| Cards | Dark: #1A1A24 · Light: #FFFFFF |
| Borders | Dark: rgba(255,255,255,0.08) · Light: #E5E7EB |
| Accents | Per-card accent colors for visual differentiation |

## Layout

Consistent border-radius (12-20px), equal gutters (12-24px), hero cards (2x2 spans). Container queries for self-aware tiles.

```css
.bento-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}
.bento-card {
  background: #12121a;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid rgba(255,255,255,0.08);
  container-type: inline-size;
}
.bento-card.large { grid-column: span 2; grid-row: span 2; }
.bento-card.wide { grid-column: span 2; }

@container (min-width: 400px) {
  .card-content { display: flex; gap: 1rem; }
}
```

## Animation

Per-card micro-interactions — each tile feels alive:

- Staggered reveal on scroll (80-120ms cascade delay)
- Hover: subtle lift with tinted shadow
- Internal animations: auto-sorting lists (layoutId), typewriter effects, pulsing status indicators
- GSAP Flip for smooth layout transitions between filtered states
- Spring physics for interactive elements (`type: "spring", stiffness: 100, damping: 20`)

## Saturation warning

This pattern is **reaching saturation** in 2025 — designers report "bento fatigue." To differentiate:

- Vary card sizes dramatically (not just 1x1 and 2x2)
- Add internal motion/animation — cards that feel alive, not static
- Use real content and data, not abstract shapes
- Break the grid occasionally — one element that escapes the tile boundary
- Consider **Spatial Organic** as a fresher alternative for 2026-2027

## Ideal for

SaaS product pages (Notion, Linear, Supabase), feature comparisons, product launches, dashboard previews.
