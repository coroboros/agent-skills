# Anti-Patterns

Validation checklist for the Validate step. Read before submitting or requesting review. Grouped by the kind of failure mode they create.

## Axiomatic rejections

Non-negotiable. If the design contains any of these, stop and fix — don't argue the edge case. These are the fingerprints of AI-generated work that every experienced judge recognizes in under three seconds. A single axiomatic violation is enough to score below Honorable Mention, no matter how strong the rest is.

1. **Never use the AI-purple gradient.** `linear-gradient(135deg, #a855f7|#8b5cf6, #ec4899|#6366f1)` — any variant pairing purple with pink or purple with blue. The moment judges see it, they stop looking.
2. **Never use Inter, Roboto, Arial, or system fonts as the display face.** They work as fallbacks and body. At the hero, they signal "no type decision was made". Pick deliberately — a custom face, a quality paid font (Söhne, Tiempos, GT, Apoc), or a distinctive free one (Instrument Serif, Geist, PP Editorial New). Don't ship `font-family: 'Inter'` on an H1.
3. **Never use pure black (`#000`) or pure white (`#FFF`).** Off-black (`#0a0a0a`, `#141413`, `#1a1a1a`) and off-white (`#fafafa`, `#f5f4ed`, `#faf9f5`). The shift is 1% on a color picker and 100% of the atmosphere.
4. **Never use placeholder names or fake statistics.** "John Doe", "Sarah Chen", "Acme Corp", "99.99% uptime", "10,000+ happy customers", "50% faster". If content isn't real, write something specific and plausible — or keep the placeholder honest (`[client name]`, `[metric]`).
5. **Never ship the centered-hero-over-dark-image-with-generic-headline template.** The canonical AI landing page. Break one of those three: off-center the layout, use flat color or typographic hero, or write a headline that couldn't apply to another product.
6. **Never ship 3 equal cards in a row as your feature section.** The "feature row" is the most recognized AI template. Vary card sizes, move to editorial or bento layouts, or use a dominant card with supporting detail — not equal thirds.
7. **Never use emojis as UI icons.** Icon sets exist (Phosphor, Radix, Lucide, Iconify, custom SVG). Emojis in UI signal no design system.
8. **Never ship without a signature moment.** One interaction, one visual, one typographic decision that someone will remember after 30 seconds. Scattered micro-animations fail; one choreographed hero reveal succeeds. If you can remove every effect and the page reads the same, there is no signature.

Run this list first when validating. Anything it catches is stop-and-fix, not nice-to-have.

## Design failures

- **Template / AI layouts** — judges are working professionals who recognize these instantly. Single fastest way to fail.
- **Inconsistent systems** — polished homepage but weaker inner pages signals incomplete craft.
- **Stock photography** — signals generic thinking and tanks scores.
- **Desktop-first** — judges check mobile first. Usability is 30% of the score.
- **Cookie-cutter minimalism ("blanding")** — the safe muted geometric sans default everyone adopted is being actively rejected.

## Performance failures

- LCP > 2s, total weight > 3MB, animation dropping below 60fps.
- Videos loaded without lazy loading, 20+ font file requests.
- Images loaded twice due to poor `<picture>` implementation.
- Award-winner targets: **LCP < 1.5s**, **CLS < 0.05**, **INP < 100ms**.

## AI Tells (patterns that betray AI generation)

### Visual

- Purple/blue gradients on white — the "AI purple" aesthetic.
- Pure black (#000) or pure white (#FFF) — use off-blacks and off-whites.
- Outer glow box-shadows, oversaturated neon accents.
- Gradient text on large headers.
- Static gradients as primary design elements (no longer differentiated).

### Typography

- Inter, Roboto, Arial, system fonts as primary choices.
- Space Grotesk (converging AI default) — vary between generations.
- Oversized H1 that screams — control hierarchy with weight and color, not just scale.
- Serif on dashboards/software UI (serif is for editorial/luxury only).

### Layout

- Centered hero with generic headline over dark image.
- 3 equal cards in a row (the "feature row" cliché).
- Predictable symmetric layouts at every section.
- `h-screen` instead of `min-h-[100dvh]` (breaks on mobile).

### Content

- Generic names: "John Doe", "Sarah Chen", "Acme Corp".
- Fake round numbers: "99.99%", "10,000+", "50% faster".
- AI copywriting clichés: "Elevate", "Seamless", "Unleash", "Next-Gen", "Game-changer".
- Emojis in UI — use icons (Phosphor, Radix, or custom SVG).
- Broken Unsplash links — use `picsum.photos/seed/{context}/W/H` or SVG placeholders.

### Technical

- Mixing GSAP and Framer Motion in the same component tree.
- `window.addEventListener('scroll')` for scroll effects — use ScrollTrigger or CSS Scroll-Driven.
- Complex flexbox percentage math — use CSS Grid.
- Animating `width`, `height`, `top`, `left` — use `transform` and `opacity` only.

## UX anti-patterns disguised as creativity

- **Scroll hijacking** on text-heavy content — use scroll-*triggered* animations instead (user retains speed control).
- **Experimental navigation** requiring discovery — tanks usability even when creativity scores high.
- **Illusion of completeness** — scroll animations that pause, making users think they've reached the end.
- **Style over substance** — beautiful animations that slow task completion, custom cursors that obscure click targets, impressive loading screens covering 10+ second loads.
