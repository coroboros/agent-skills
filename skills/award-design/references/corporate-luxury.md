# Corporate Luxury

Quiet luxury. Sophisticated restraint where generosity of whitespace signals exclusivity. Custom serifs at display, refined sans-serifs at body, palette anchored in neutral foundations punctuated by jewel tones or muted golds. Animation curves are long; nothing hurries. The voice is inherited rather than chosen.

## Canonical reference — Cartier Watches & Wonders 2025

**Site.** Cartier Watches & Wonders 2025
**URL.** `cartier-waw-0225.dev.60fps.fr`
**Award.** Awwwards Site of the Month, August 2025 (+ Developer Award)
**Studio.** Immersive Garden, with `60fps` and `Mooders`, for Cartier.

Built around Cartier's Geneva pavilion. Six contemplative 3D alcove universes around iconic timepieces. Slow tasteful motion. Refined typography. Hidden gestures. Bespoke cinematic soundscape. The platonic case for quiet-luxury restraint with sumptuous detail. The URL lives on the build studio's `dev.60fps.fr` subdomain rather than a Cartier-owned domain — unusual, but the canonical Awwwards-referenced location. Substitutable peers: `hermes.com` (orange and ivory with custom serif), `rolex.com` (dark greens and golds, editorial photography, slow pacing), `aesop.com` (warm neutrals, single custom serif, product-as-still-life), `bugatti.com` (deep blues and chrome, automotive gravitas), `immersive-g.com` (agency-as-luxury-brand).

## DNA — non-negotiable

- Generous whitespace (200px+ section padding) signals exclusivity, not waste
- Custom or premium serif at display sizes is the typographic mark of the archetype
- Color rests on neutral foundations punctuated by jewel tones, muted golds, or single deep brand color
- Motion uses long easing curves (1–1.5s, `cubic-bezier(0.16, 1, 0.3, 1)`) — nothing rushes
- Photography is treated and considered — every shot frames the product as object, not commodity

The archetype keeps its identity across flat editorial luxury (Hermès, Aesop), cinematic 3D pavilion (Cartier WAW), dark luxury (Rolex, Bugatti), and warm neutral lifestyle (Aesop, Loro Piana). Background register is an expression choice, not a definition.

## Common expressions

Three stacks fit the DNA. Pick the one matching brand voice and product type.

### Flat editorial luxury — Hermès / Aesop profile

Warm white or cream foundation (`#F8F5F0`, `#FAF8F5`) with custom serif headlines (Didot, Bodoni-adjacent), considered photography, generous gutters. Single jewel-tone accent (Hermès orange, Aesop sage, Loro Piana camel). Asymmetric image-text pairs. Hover is a 1.05 scale, opacity 0.7→1. Ideal for fashion houses, fragrance, premium lifestyle, artisan and craft brands.

### Cinematic 3D pavilion — Cartier WAW profile

Cream or warm-neutral foundation (`#F2EBDC` to `#FAF7F0`) with rendered 3D pavilion architecture as the immersive surface. Type is engraved or embossed (chunky serif "WATCHES & WONDERS" rendered as 3D objects). Slow tasteful motion through 3D alcoves. Hidden gestures reveal product detail. Bespoke soundscape. Ideal for luxury launches, watchmaking, automotive concept reveals, jewelry openings, premium architecture and hotels.

### Dark luxury — Rolex / Bugatti profile

Deep neutral foundation (`#1A1A1A`, `#0E1A1B`) with custom serif in cream type, gold accent (`#C5A572`), or chrome silver. Editorial photography lit dramatically. Long easing on every transition. Ideal for premium automotive, fine timepieces, premium spirits, private banking and wealth management.

## Typography

The serif is the mark.

- **Display serif**: Didot, Bodoni, GT Sectra, Tiempos Headline, Editorial New, custom commissioned serifs at weight 400–600 — 60–120px, tight tracking (`-0.02em` to `-0.04em`)
- **Body sans**: Apercu, Founders Grotesk, PP Neue Montreal, Söhne — 16–18px, weight 400, line-height 1.6
- **Casing**: uppercase sparingly — navigation labels, category tags, metadata. Title Case avoided in headers (sentence case reads more refined)
- **Micro-typography**: tabular numbers (`tnum`) for prices, sizes, edition numbers; non-breaking spaces in unit pairs (`10&nbsp;mm`, `750&nbsp;ml`)

Inter, Roboto, Arial as display fonts signal "no type decision". This archetype either commissions a custom serif or pairs a known premium serif (Tiempos, Sectra) with discipline. The luxury is in the choice and its execution, not the budget.

## Color

Color rests on neutral foundations.

- **Backgrounds**: warm whites `#F8F5F0`, `#FAF8F5`, cream `#FAF7F0`; deep neutrals `#1A1A1A`, `#0E1A1B`
- **Text primary**: charcoal `#2D2D2D` on cream, off-white `#E8E0D0` on dark
- **Text secondary**: warm gray `#8B8580`
- **Accent — jewel tones**: muted gold `#C5A572`, deep emerald `#006D5B`, sapphire `#1B365D`, ruby `#8B2E2E`
- **Signature 2025**: Pantone Mocha Mousse `#A47764`
- **Borders**: `#E8E4DF` or `rgba(0,0,0,0.06)`

Colors feel inherited — neither neon nor primary, never high saturation. One accent per surface, used as signal rather than decoration.

## Layout

Generous whitespace, content centered or asymmetrically paired within constrained widths.

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

Content widths bind to `containers.luxury-page` (~1200–1280px) and `containers.read-measure` (~65ch). Section spacing pulls from `spacing.section-luxury` (the largest scale step). The Doppelrand technique (nested concentric containers — outer shell with hairline border, inner core with tighter radius) lifts cards from "flat tile" to "machined hardware" — see `premium-patterns.md`.

## Motion

Long, deliberate curves. Nothing hurried.

- Easing: `cubic-bezier(0.16, 1, 0.3, 1)`, duration 1–1.5s
- Subtle parallax (5% maximum differential)
- Hover: gentle opacity shifts (0.7→1) and scale 1.05 over 600–800ms
- Image reveals: clip-path inset with long duration (0.8–1.2s)
- Page transitions: View Transitions API with slow cross-fades (400–600ms)
- 3D alcove archetype: scroll-controlled camera moves through architectural scenes (Cartier WAW)

```css
.luxury-card {
  transition: opacity 800ms var(--ease-luxury),
              transform 800ms var(--ease-luxury);
}
.luxury-image-reveal {
  clip-path: inset(0 100% 0 0);
  transition: clip-path 1200ms cubic-bezier(0.77, 0, 0.175, 1);
}
.luxury-image-reveal.visible { clip-path: inset(0 0 0 0); }
```

Durations bind to `motion.duration-luxury-*`. Easings to `motion.ease-luxury` (long-ease curve).

## E-commerce patterns

When the archetype carries commerce, the buying experience is intentional rather than transactional.

- Storytelling product pages (Apple model) — narrative before price
- Cart as slide-in panel, no page navigation
- Every visible product is shoppable
- Generous spacing signals exclusivity — products never packed tight
- No modals on page load
- Radical transparency for materials and pricing (Everlane model) where brand voice supports it
- Real-time customization previews (configurators) for premium hardware and watchmaking
- Aspirational imagery where the product is contextual (worn, placed, lit) rather than catalog-flat

## What makes it award-worthy

A corporate-luxury site scores 8+ when the restraint feels chosen rather than generic — when the serif is felt before it's noticed, when the whitespace itself signals confidence, when the photography frames every product as an object worth looking at. Cartier WAW succeeds because the 3D pavilion and the slow tasteful motion are the brand's voice, not a layer of polish over a stock template.

The archetype loses identity at three failure modes: cookie-cutter minimalism (the safe muted geometric default that every brand adopted, actively rejected by judges), corporate sterility (whitespace without warmth, serif without conviction), and luxury costume (premium fonts bolted onto a generic SaaS template). Quiet luxury without the underlying craft reads as expensive theater.

## Ideal for

High-end fashion, luxury hotels, fine jewelry, premium automotive, wealth management, private banking, premium real estate, fragrance, watchmaking, artisan and craft brands, lifestyle direct-to-consumer with story.

## Cross-references

Read alongside `foundations.md` (typography systems, OKLCH for jewel tones, animation toolkit), `premium-patterns.md` (Doppelrand nested containers, button-in-button trailing icons, eyebrow tags), `anti-patterns.md` (no neon, no high saturation; jewel tones only), `audit-rubric.md` (Spacing 9+, Typography 9+, Motion 8+ are entry bars), `exemplars.md` (Hermès, Rolex, Aesop, Bugatti, Immersive Garden).
