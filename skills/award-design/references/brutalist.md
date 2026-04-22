# Brutalist / Neo-Brutalist

Deliberate rejection of polish. Thick borders, flat colors, zero gradients. Typography IS the design.

## Typography

**Headlines**: Monument Extended, Archivo Black, Space Mono — 80-200px+, uppercase
**Body**: Space Mono, JetBrains Mono, IBM Plex Mono — 14-16px
**Mixing**: Quirky display faces with monospace "terminal chic"
**Tracking**: Extremely tight on headlines (-0.03em to -0.06em), generous on mono body (0.05em)
**Leading**: Compressed on headlines (0.85-0.95)

## Color

| Role | Values |
|------|--------|
| Background | #FFFFFF or #000000 (hard contrast, no gray zones) |
| Borders | #000000, 2-4px solid |
| Accents | High-saturation, clashing: hot pink #FF90E8, neon green #00FF41, electric yellow #FFF000 |
| Shadows | Hard-edged: 4-8px offset, solid black, zero blur |

**Rule**: Gradients are banned. Shadows must be flat (zero blur radius). No border-radius — all corners 90 degrees. If it looks polished, it's wrong.

## Layout

Strict grid with visible borders and intentional overlap. Elements anchored precisely to grid tracks.

```css
.brutalist-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0;
  border: 3px solid #000;
}
.brutalist-cell {
  border: 2px solid #000;
  padding: 24px;
}
.brutalist-cell.feature {
  grid-column: span 2;
  box-shadow: 6px 6px 0 #000;
}
```

**Decorative elements**: ASCII brackets `[ SECTION ]`, directional markers `>>>`, registration symbols as geometric elements, crosshairs at grid intersections.

## Animation

Jarring and intentional — nothing smooth:

- Glitch effects, RGB channel splitting
- Kinetic type: bounce, rotate, intentionally rough
- Hard cuts over smooth transitions
- Hover: instant color swaps, no easing
- Marquee text bands, scramble effects on hover
- Text mask reveals with video backgrounds

**Forbidden**: Smooth easing, glassmorphism, soft shadows, elegant fade-ins, parallax.

## Texture

Simulated analog degradation:

```css
/* CRT scanlines */
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

Halftone dot patterns via SVG filters, mechanical noise overlays, 1-bit dithering on images.

## Ideal for

Creative agencies, indie tech (Gumroad, Figma Config), streetwear, design conferences, zines, developer portfolios with attitude.

## Reference studios

Cuberto, independent creative developers.
