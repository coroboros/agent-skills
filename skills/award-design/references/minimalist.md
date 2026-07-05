# Minimalist

Two to three colors maximum. Every element justifies its existence. Typography carries the design where decoration would otherwise smuggle in. The archetype's discipline is subtraction — what remains is what matters.

## Canonical reference — Terminal Industries

**Site.** Terminal Industries
**URL.** `terminal-industries.com`
**Award.** Awwwards Site of the Month, September 2025 (+ Developer Award)
**Studio.** REJOUICE® and PROPAGANDE.

Operates a B2B yard-management OS. The textbook minimalist reference for 2025: two-color system, type-driven, generous whitespace, scroll-driven storytelling carried by a single cinematic photograph (a black truck silhouette against amber sky). One of the rare logistics-SaaS sites to crack SOTM tier — proof that restraint outperforms decoration in a category prone to overdesign. Substitutable peers: `linear.app` (Swiss-grid airy minimalism), `stripe.com` (off-white pages with surgical purple), `vercel.com` (pure grayscale with single emphasis weight), `mintlify.com` (reading-optimized Inter with green accent).

## DNA — non-negotiable

- Two to three colors maximum carry the entire system
- Macro whitespace (120–200px+ section padding on desktop) is active design, not absence
- Typography carries hierarchy through scale, weight, and color — never through chrome
- Single accent functions as punctuation — present once per viewport, never twice
- Every element answers the question "what would break if this disappeared"

The archetype keeps its identity across airy-Swiss (Linear, Stripe, Vercel), warm editorial-light (Notion, Anthropic adjacency), cinematic photography-led (Terminal Industries), and dark monochrome (Linear's dark mode). Background register is an expression choice, not a definition.

## Common expressions

Three stacks fit the DNA. Pick the one matching brand voice and content type.

### Airy Swiss-grid — Linear / Stripe / Vercel profile

Off-white foundation (`#FAFAFA`, `#F7F6F3`, `#FBFBFA`). Swiss typographic discipline — Geist, Söhne, or PP Neue Montreal at 48–96px headlines with surgical letter-spacing. Single accent (Linear violet, Stripe purple, Vercel pure grayscale with weight contrast only). Hairline dividers (`#EAEAEA`) where structure demands. Ideal for SaaS, developer tooling, design platforms, technical product marketing.

### Cinematic photography-led — Terminal Industries profile

Off-white or warm cream foundation (`#FAFAF5`, `#E8E4DF`) with one dominant cinematic photograph occupying full viewport — golden-hour silhouette, industrial scale, dramatic light. Glass-pill nav with one CTA in a single saturated hue (Terminal uses lime green). Type holds a supporting role; the photograph is the hero. Ideal for industrial brands, logistics, architecture studios, automotive marketing pages, single-product showcases.

### Dark monochrome — Linear dark / portfolio profile

Near-black foundation (`#0A0A0A`, `#0E0E12`) with off-white type, single saturated accent. Same Swiss discipline inverted. Ideal for high-end portfolios, design tool dark themes, technical documentation, developer-focused launch pages.

## Typography

Single family with weight contrast, or geometric sans (display) paired with humanist sans (body).

- **Headlines**: Suisse Int'l, Neue Haas Grotesk, Söhne, PP Neue Montreal, Geist — 48–120px, weight 500–700
- **Body**: same family at 16–18px, weight 300–400, line-height 1.6–1.7
- **Tracking**: tight on display (`-0.02em`), neutral on body
- **Variable-font features**: `tnum` for tabular numbers in dashboards and pricing, `ss01`–`ss04` where the typeface offers stylistic alternates

The "Inter everywhere" anti-pattern lives in this archetype's failure mode — pick a face with character. Terminal Industries uses Söhne; Linear uses Inter (paired with discipline that earns it); Anthropic uses Tiempos for warmth. Inter as default H1 tells judges that no type decision was made.

## Color

Two to three colors carry the entire system.

- **Foundation**: warm neutrals (`#FAFAF5`, `#E8E4DF`, `#F7F6F3`) or cool neutrals (`#F5F5F0`, `#F8FAFC`) or near-black (`#0A0A0A`, `#0E0E12`)
- **Text primary**: `#2D2D2D` to `#111111` on light, `#E0E0E0` to `#FAFAFA` on dark
- **Text secondary**: warm gray `#787774` or cool gray `#6B7280`
- **Single accent**: electric blue `#007BFF`, sage `#87A98F`, terracotta `#C67D5B`, lime green (Terminal Industries), Linear's violet, Stripe's purple, sustainability sage
- **Borders**: `rgba(0,0,0,0.06)` or `#EAEAEA`

If you can remove a color and nothing breaks, remove it.

## Layout

Single-column or asymmetric broken-grid. One bold focal point per viewport. Generous macro-whitespace.

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

The Josh W. Comeau full-bleed pattern is the standard for long-form content with breakout sections. Section padding pulls from `containers.section-padding` and scales through `clamp()`. The reading measure binds to `containers.read-measure` (typically 65ch).

## Motion

Restraint extends to motion — opacity-led, never showy.

- Fade-ins: opacity 0→1 with `translateY(20→0)`, 0.6–0.8s, `cubic-bezier(0.16, 1, 0.3, 1)`
- `Lenis` smooth scroll
- `GSAP Flip` for state transitions
- Hover: gentle opacity shifts (0.7→1), scale 1.02–1.05 on cards
- Optional: variable-font weight micro-shift on hover (`wght` 400→500)

```css
.minimal-card {
  transition: opacity var(--duration-hover) var(--ease-standard),
              transform var(--duration-hover) var(--ease-standard);
}
.minimal-card:hover { opacity: 1; transform: scale(1.02); }
```

Durations bind to `motion.duration-*`, easings to `motion.ease-*`. The Motion atmosphere score sits at 3 by default (±2 per the brief); pushing higher means the archetype is leaning toward Editorial or Immersive, and the recommendation should be revisited.

## What makes it award-worthy

A minimalist site scores 8+ when restraint reads as decision rather than emptiness — when the single accent is placed with surgical precision, when the type pairing is felt before it's noticed, when the whitespace itself signals confidence. Terminal Industries succeeds because the cinematic photograph and the lime CTA are anchored against generous void; the page is composed, not arranged.

The archetype loses identity in two failure modes: blanding (cookie-cutter geometric sans with safe muted palette — actively rejected by judges in 2025–2026), and cargo-cult Swiss (Inter at default tracking with no character behind the choice). Restraint without conviction collapses into corporate template.

## Ideal for

SaaS (Linear, Stripe, Vercel adjacency), luxury brands with quiet voice, architecture and design studios, high-end portfolios, design-tool landing pages, technical documentation, developer marketing, founder-led product launches.

## Cross-references

Read alongside `foundations.md` (typography systems, OKLCH single-accent strategy, animation toolkit), `anti-patterns.md` (blanding is rejected; pure `#FFF` with no character is rejected; Inter as display font is rejected), `audit-rubric.md` (Hierarchy 9+, Color 9+ are entry bars in this archetype), `exemplars.md` (Linear, Stripe, Vercel, Mintlify).
