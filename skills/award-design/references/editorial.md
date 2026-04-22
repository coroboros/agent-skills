# Editorial / Magazine

Serif headlines over sans-serif body. Multi-column grids, pull quotes, and full-bleed imagery. The web as print.

## Typography

**Headlines**: GT Sectra, Playfair Display, Editorial New, GT Super — 60-120px, weight 600-700
**Body**: Inter, Neue Haas Grotesk, ABC Diatype — 16-18px, weight 400, line-height 1.6
**Pull quotes**: Headline serif at xl size, italic, with border-left accent
**Metadata**: Monospace (Geist Mono, JetBrains Mono) for dates, categories, reading time
**Pairing**: High-contrast serif/sans-serif — the defining characteristic of this archetype

Serifs are making a strong comeback in 2025-2026 (Burberry's return to serif signaled the broader shift).

## Color

| Role | Values |
|------|--------|
| Background | #FFFFFF or warm off-white #F8F5F0 |
| Text | Off-black #111111 (primary), warm gray #787774 (secondary) |
| Accent | Restrained: deep red #8B0000, navy #1B365D, or ink black |
| Dividers | Ultra-light #EAEAEA, hairline rules |
| Image treatment | High-contrast B&W, duotone, or desaturation with one accent color |

## Layout

6-12 column grids with asymmetric column widths. Pull quotes break the flow. Full-bleed heroes alternate with text-heavy sections.

```css
.editorial-layout {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 1.5rem;
}
.feature-article { grid-column: 1 / 8; }
.sidebar { grid-column: 9 / 13; }
.pull-quote {
  grid-column: 3 / 11;
  font-style: italic;
  font-size: var(--fs-xl);
  border-left: 3px solid currentColor;
  padding-left: 2rem;
}
.full-bleed-image { grid-column: 1 / -1; }
```

## Animation

Understated and content-respectful:

- Gentle scroll reveals (opacity + translateY 12px, 0.6-0.8s, `cubic-bezier(0.16, 1, 0.3, 1)`)
- Image reveals via clip-path
- Subtle parallax on images only (5-10% differential)
- Page transitions via View Transitions API (morph article thumbnails into heroes)
- Staggered list reveals (80ms cascade delay)

**Forbidden**: Kinetic type on body text, scroll hijacking, heavy WebGL, anything that competes with reading.

## Ideal for

Media and publishing, fashion brands, cultural institutions, luxury e-commerce, long-form storytelling, online magazines.
