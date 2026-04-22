# Corporate Luxury

"Quiet luxury" — sophisticated restraint where generosity of whitespace signals exclusivity.

## Typography

**Headlines**: Custom serifs with sharp edges — Didot, Bodoni, GT Sectra — weight 400-600
**Body**: Refined sans-serifs — Apercu, Founders Grotesk, PP Neue Montreal — 16-18px, weight 400
**Tracking**: Very tight on headlines (-0.02em to -0.04em), standard on body
**Casing**: Uppercase sparingly — navigation labels, category tags, metadata

## Color

| Role | Values |
|------|--------|
| Background | Warm whites #F8F5F0, cream #FAF8F5 |
| Text | Charcoal #2D2D2D (primary), warm gray #8B8580 (secondary) |
| Accent | Muted gold #C5A572, deep emerald #006D5B, sapphire #1B365D |
| Signature | Pantone 2025 Mocha Mousse #A47764 |
| Borders | #E8E4DF or rgba(0,0,0,0.06) |

**Rule**: No neon, no high saturation. Colors should feel inherited, not chosen. Jewel tones only.

## Layout

Generous whitespace — 200px+ section padding. Content centered within 1200px max-width. Asymmetric image/text pairs.

```css
.luxury-section {
  padding-block: clamp(6rem, 12vw, 14rem);
  max-width: 1200px;
  margin-inline: auto;
}
.luxury-split {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: clamp(3rem, 6vw, 8rem);
  align-items: center;
}
```

## Animation

Long, deliberate curves — nothing hurried:

- Easing: `cubic-bezier(0.16, 1, 0.3, 1)`, duration 1-1.5s
- Subtle parallax (5% maximum differential)
- Hover: gentle opacity shifts (0.7→1) and scale 1.05
- Image reveals: clip-path inset with long duration (0.8-1.2s)
- Page transitions: View Transitions API with slow cross-fades (400-600ms)

**Forbidden**: Fast animations, glitch effects, kinetic type, scroll hijacking, anything that feels "loud" or urgent.

## E-commerce patterns

- Storytelling product pages (Apple model) — narrative before price
- Cart as slide-in panel, no page navigation
- Every visible product is shoppable
- Generous spacing signals exclusivity — never pack products tight
- No modals on page load — ever
- "Radical transparency" for materials/pricing breakdowns (Everlane model)
- Delayed interactions: never interrupt browsing

## Ideal for

High-end fashion, luxury hotels, fine jewelry, premium automotive, wealth management, premium real estate.

## Reference studios

Immersive Garden (Paris) — Louis Vuitton, Longines. Monogrid (Italy) — Prada, Gucci, Netflix.
