# Bento / Card-Based

Modular asymmetric tiles inspired by Japanese bento boxes, popularized at scale by Apple keynotes. Each tile is a self-contained information unit with its own visual treatment, behavior, and state. Container queries enable self-aware cards that adapt to their own dimensions rather than the viewport. The structure teaches itself.

## Canonical reference — Anime.js v4

**Site.** Anime.js v4
**URL.** `animejs.com`
**Award.** Awwwards Site of the Month, May 2025 (+ Developer Award, Product Honors)
**Studio.** None — open-source library project led by Julian Garnier.

A canonical modern bento layout. A modular asymmetric grid of self-contained feature cards, each demoing one capability — scroll scrubber, lightweight modular core, complete animator's toolbox, layout-grid demos that morph between bento configurations. Consistent corner radii. Neutral palette. The Notion / Linear / Apple-iOS lineage executed at SOTM tier. The site is genuinely a hybrid — brutalist palette, bento structure — which is why some sources tag it brutalist. The structural logic is bento. Substitutable peers: `apple.com` (canonical bento on product detail pages), `linear.app` feature grid (minimalist bento with discipline), `vercel.com` platform features (monochromatic bento with subtle depth).

## DNA — non-negotiable

- Modular asymmetric tiles — never uniform 3-equal-cards-in-a-row (the "feature row" cliché)
- Each tile is a self-contained information unit with its own visual treatment
- Every tile *demonstrates* its claim — live, animated, or visual — never a mini spec-sheet of labels and rows; describing is the failure this archetype exists to avoid (the canonical reference demos every card)
- Container queries (`container-type: inline-size`) make tiles self-aware
- Consistent corner radii across the grid; equal gutter widths (12–24px) — visual rhythm holds
- Hero cards (2×2 spans, or `col-span: 2 row-span: 2`) carry primary features

The archetype keeps its identity across structural-pure (Apple, Linear), motion-engine premium (Bento 2.0, Vercel feature grids), brutalist-bento hybrid (Anime.js v4), and gradient-bento (Linear's atmospheric variant).

## Common expressions

Three stacks fit the DNA. Pick the one matching product type and personality.

### Structural-pure — Apple / Linear feature grid profile

Light foundation (`#F9FAFB` to `#FCFCFC`) or dark foundation (`#0A0A0F` to `#12121A`). Cards in off-white (`#FCFCFC`) or `#1A1A24`. Hairline borders (`#E5E7EB` light / `rgba(255,255,255,0.08)` dark). Per-card accent colors for visual differentiation. Content-first, motion restrained. Ideal for SaaS product pages, feature comparison, dashboard previews, technical product marketing.

### Motion-engine premium — Bento 2.0 (Vercel-core meets Dribbble) profile

Light foundation (`#F9FAFB`) with off-white cards (`#FCFCFC`), 1px borders at `border-slate-200/50`, generous `rounded-[2.5rem]` corners, "diffusion shadow" (`box-shadow: 0 20px 40px -15px rgba(0,0,0,0.05)` — wide, low-opacity, tinted). Labels (titles, descriptions) sit OUTSIDE and BELOW the cards in a gallery-style presentation. Cards contain perpetual micro-interactions — every tile is "alive". Uses Geist, Satoshi, or Cabinet Grotesk with `tracking-tight`. Padding `p-8` to `p-10`. Ideal for premium SaaS, AI products, modern dashboards, agency-built marketing pages.

### Brutalist-bento hybrid — Anime.js profile

Dark foundation (`#0A0A0A` to `#0E0E12`) with white display type at large scale, central rainbow visualization or feature demo as the focal point of the hero card. Cards inherit the brutalist palette discipline (one accent per tile, flat fills) inside the bento structure. Ideal for developer tools, animation libraries, technical content where the demo IS the product.

## Bento 2.0 — motion-engine paradigm

When the project calls for the premium motion-rich expression, follow the Bento 2.0 architecture and choreography rules.

### Architecture

- **Background**: `#F9FAFB` (light) or `#0A0A0F` (dark)
- **Card surface**: `#FCFCFC` (light) or `#1A1A24` (dark) with 1px hairline border at `rgba(0,0,0,0.05)` (light) or `rgba(255,255,255,0.06)` (dark)
- **Corner radius**: `rounded-[2.5rem]` (40px) for major containers; nested elements use concentric smaller radii (`rounded-[calc(2.5rem-0.375rem)]`) — the Doppelrand pattern, see `premium-patterns.md`
- **Diffusion shadow**: wide, low-opacity, tinted to background hue — `box-shadow: 0 20px 40px -15px rgba(0,0,0,0.05)`. Creates depth without clutter
- **Padding**: `p-8` or `p-10` (32–40px) inside cards
- **Labels**: titles and descriptions OUTSIDE the card, below — gallery-style presentation. Avoids cards-inside-cards-inside-cards
- **Typography**: Geist, Satoshi, or Cabinet Grotesk with `tracking-tight` for section headers

### The 5-card archetypes

Each Bento 2.0 grid mixes these tile-types. The goal is variance — never all five-of-the-same.

1. **The Intelligent List** — vertical stack of items with infinite auto-sorting loop. Items swap positions via Framer Motion `layoutId`, simulating real-time prioritization.
2. **The Command Input** — search or AI bar with multi-step typewriter effect. Cycles through complex prompts, blinking cursor, "processing" shimmer state.
3. **The Live Status** — scheduling or telemetry interface with "breathing" status indicators. Pop-up notification badge emerges with overshoot-spring, holds 3 seconds, vanishes.
4. **The Wide Data Stream** — horizontal infinite carousel of data cards or metrics. Gapless loop via `x: ["0%", "-100%"]`. Speed feels effortless.
5. **The Contextual UI (Focus Mode)** — document view animating staggered text-block highlight, followed by float-in floating action toolbar with micro-icons.

### Choreography

- **Spring physics** (Framer Motion): `type: "spring", stiffness: 100, damping: 20` for premium weight. Linear easing reads as cheap.
- **Layout transitions**: heavy use of `layout` and `layoutId` props for re-ordering, resizing, shared element transitions.
- **Perpetual micro-interactions**: every card carries one infinite loop (Pulse, Typewriter, Float, Carousel, Shimmer). Dashboard feels alive. The loops share one physics and one focal hierarchy — two may reinforce one focal point, never compete (the premium-patterns.md one-per-fold cap applies outside the grid).
- **Performance lock**: any perpetual motion or infinite loop MUST be memoized (`React.memo`) and isolated in its own microscopic Client Component. Re-rendering the parent layout from a perpetual animation breaks 60fps on mid-range mobile.
- **Magnetic micro-physics** for hover: never use React `useState` for magnetic hover or continuous animation. Use exclusively Framer Motion's `useMotionValue` and `useTransform` outside the React render cycle.

## Layout

Consistent border-radius (12–20px structural, up to 40px on Bento 2.0). Equal gutters (12–24px). Container queries for self-aware tiles.

```css
.bento-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-auto-flow: dense;
  gap: var(--space-bento-gutter);
}
.bento-card {
  background: var(--surface-card);
  border-radius: var(--radius-bento);
  padding: var(--space-bento-padding);
  border: 1px solid var(--border-hairline);
  container-type: inline-size;
}
.bento-card.large { grid-column: span 2; grid-row: span 2; }
.bento-card.wide  { grid-column: span 2; }

@container (min-width: 400px) {
  .card-content { display: flex; gap: 1rem; }
}
```

`grid-auto-flow: dense` is mandatory — it prevents the empty-cell failure mode where LLMs leave dead cells in CSS grids. Verify mathematically that `col-span` and `row-span` values interlock perfectly. No grid ships with a missing corner or empty void.

Container widths bind to `containers.bento-grid`. Card sizes bind to `aspectRatios.bento-square` (`1/1`), `aspectRatios.bento-wide` (`2/1`), `aspectRatios.bento-hero` (`2/2`). Border weights bind to `borderWidths.hairline` (`1px`).

## Typography

- **Headlines**: Geist, Cabinet Grotesk, PP Neue Montreal — 24–48px, weight 600, `tracking-tight`. Satoshi works but is an overexposed kit pick — rotate or justify (`inspiration.md`)
- **Body**: same family at 14–16px, weight 400
- **Metrics and data**: monospace (Geist Mono, JetBrains Mono) for numbers and data points; `font-variant-numeric: tabular-nums`
- **Per-tile contrast**: each tile can shift typographic register — one tile uses display serif, another monospace metric — variance signals that each tile is its own world

## Color

Per-card accent colors for visual differentiation. The grid as a whole stays restrained; each tile claims one accent role — primary action, semantic state, brand color rotation. Apple's bento examples use a different photographic background per cell to differentiate while holding the structural rhythm.

```css
.bento-card[data-accent="success"] { --accent: oklch(70% 0.18 150); }
.bento-card[data-accent="info"]    { --accent: oklch(70% 0.15 240); }
.bento-card[data-accent="warning"] { --accent: oklch(78% 0.15 70); }
```

OKLCH from a single brand token enables consistent saturation and lightness across hue rotations — see `foundations.md`.

## Saturation warning

The bento pattern reached oversaturation in 2025. Designers report bento fatigue. The article's anti-patterns section flags "bento grid layouts have reached oversaturation" alongside heavy parallax and static gradients. To differentiate when the project genuinely calls for bento:

- Vary card sizes dramatically (1×1, 2×1, 2×2, 3×1, 1×3) — never uniform
- Add internal motion / animation — cards that feel alive, not static (Bento 2.0 paradigm)
- Use real content and data, not abstract shapes or placeholder copy
- Break the grid occasionally — one element that escapes the tile boundary (`overflow: visible`, illustration that protrudes)
- Consider Spatial Organic as a fresher alternative for 2026–2027 if the brief allows

## What makes it award-worthy

A bento site scores 8+ when the asymmetric grid teaches the product (Anime.js demos one capability per tile), when each tile carries weight (variance, not uniform repetition), and when the motion engine — if applied — earns the "alive" quality without burning the performance budget. Anime.js succeeds because every tile demos the library it documents; the structure is the product.

The archetype loses identity when bento becomes "3 equal cards in a row" with rounded corners, when every tile uses the same archetype (5× The Intelligent List = noise), or when perpetual motion is applied without memoization isolation and the page drops below 60fps on mid-range mobile.

## Ideal for

SaaS product pages (Notion, Linear, Supabase, Vercel adjacency), feature comparison pages, product launches with multiple capabilities to demo, dashboard previews, AI-product feature grids, developer-tooling marketing.

## Cross-references

Read alongside `foundations.md` (container queries, OKLCH per-card accents, animation toolkit), `premium-patterns.md` (Doppelrand for nested card architecture, button-in-button trailing icon, eyebrow tags above cards), `anti-patterns.md` (3-equal-cards-in-a-row is axiomatic; bento fatigue is real), `audit-rubric.md` (Hierarchy 8+, Spacing 9+ are entry bars), `exemplars.md` (Apple product pages, Linear feature grid, Vercel platform features).

## Effect palette — what this line's winners ship

The one hard-awarded whole-site anchor is Anime.js v4 (Awwwards SOTD May 6 + Site of the Month, May 2025; Animations/Transitions 9.00). The rest of the repertoire is drawn from design-canonical feature grids — Vercel, Supabase, Linear (design-canonical, award unverified) — where bento lives as a *section*, not a whole site.

**The grammar** — cohesion is a single through-line expressed differently across element classes, never one gesture stamped everywhere. Anime.js binds everything with *motion* — the button presses, the link brightens, the tile animates, the demo scrubs, all anime.js primitives. Vercel binds everything with *edge-catching light* — the same streak rides the card border, glints the CTA, frosts the nav. Button, card, and nav differ in mechanism yet obey one physics. One hover on every tile is sameness mistaken for consistency — the failure to break.

**Buttons / CTA**
- **Ghost outline + transform-press** — hairline border at a mid-neutral token (Anime.js `#625d5b` on `#252423`), background never fills; animate `transform` only — a sub-pixel mechanical press, `transition: transform 0.125s ease-out`, radius `4px`. Pick for brutalist and dev-tool grids where restraint is the brand. (Anime.js, SOTM May 2025 — live)
- **Token-step solid / inversion** — a solid pill (`border-radius: 100px`) advances one full step through the ramp or inverts fg/bg on hover, never a translucent tint — a crisp `~0.15s` token change. Pick for premium SaaS with a disciplined color system. (Vercel/Geist, design-canonical, award unverified; corroborated by Anime.js solid-accent button — live)

**Links**
- **Underline draw** — pseudo-element underline scales `scaleX(0)→1` from the left over `~0.3s` with an expo-out ease. (single-source for the exact mechanism; the effect itself is near-universal)
- **Neutral→foreground brighten** — muted links (`--fg-3`, Anime.js `#b4b1af`) lift to `--fg-1` on hover, `transition: all`, no underline. Pick for dense link lists, footers, in-card links. (Anime.js — live)

**Cards** — the heart: one hover affordance per grid, never a universal lift; let tiles differ by content.
- **Cursor-tracked conic border-shine** — a conic gradient in the border via `mask` + `mask-composite: intersect`; JS drives `--x/--y` (plus a `--start` angle) so a light streak rides the edge under the pointer. Pick for dark, flat panel grids. (Vercel + Supabase, design-canonical, award unverified)
- **Spotlight expand + reveal** — hovered tile expands across its row, siblings reflow, a de-saturated preview restores to color, copy fades up — layout-aware, not a scale. Verified Codrops params: GSAP paused timeline, `ease: power2.inOut`; siblings shift `2.5vw` inward; a 12-point clip-path cross morphs open; preview scales `(dim − 5vw)/dim`. Pick for feature grids with real imagery per tile. (Vercel spotlight + Codrops technique)
- **Border-glow bloom** — a blurred accent gradient in a pseudo-element behind the card fades `opacity 0→1` as a soft under-glow, not a hard shadow; accent = the tile's own OKLCH token. Pick for dark grounds (`--bg` ~`#0A0A0F`). (Supabase + Linear, design-canonical, award unverified)
- **Live-demo tile (no lift at all)** — the tile is a running canvas/WebGL demo; hover or drag drives the actual animation, so the content reacts and there is no card chrome. Pick when the demo IS the product. (Anime.js — live; single-source but the anchor's core claim)

The AI-default `translateY(-4px) scale(1.02)` + grey `box-shadow` on every tile is the flattening trick to break.

**Nav**
- **Transparent overlay, unchanged on scroll** — header stays fully transparent (`background: rgba(0,0,0,0)`, `backdrop-filter: none`, `border-bottom: 0`) at the top and scrolled — works over one flat ground. (Anime.js — live-verified)
- **Transparent→frosted hairline on scroll** — gains `backdrop-filter: blur()` over a semi-opaque surface plus a same-family hairline (`rgba(255,255,255,0.06)` dark / `rgba(0,0,0,0.05)` light), never a contrasting accent line. Pick for light/product bento over shifting sections. This row is the ONE sanctioned exception path to the zero-nav-`border-bottom` gate — reusing it takes a written override in the design_plan citing this row; same-family at ≤5–6% alpha only, never a contrasting line. (Apple + Vercel — documented)
- Nav items brighten muted→foreground; no background pill.

**Text**
- **Per-char / per-word stagger — signature, gated to motion brands** — split the display headline and stagger it in only when motion IS the product; elsewhere it fights the content. (Anime.js — live; single-source by design)
- **Tight-tracked static display** — the supporting default: sentence-case headline, weight `600`, negative tracking (Vercel `-2.4px` / `tracking-tight`), no animation beyond the section reveal. (Vercel documented + Anime.js — live)
- **Mono eyebrow + tabular metrics** — labels and in-tile numbers in mono (Geist Mono / JetBrains Mono) with `font-variant-numeric: tabular-nums`; numbers can count-up on reveal. The per-tile register shift is the effect.

**Cursor** — keep the native pointer deliberately (`body { cursor: auto }`); the grid is scan-and-click and a laggy dot fights it. A custom cursor appears only inside an interactive demo tile, never sitewide. The pointer powers surface effects — feeding `--x/--y` into border-shine or glow — rather than being dressed up. (Anime.js — live)

**Loader / intro** — instant first paint; no preloader element (Anime.js ships none in the DOM — live-verified). The entrance IS the card stagger — `opacity 0→1` + a short `translateY`, `40–80ms` per tile — so the page assembles itself. A blocking curtain with a `0→100%` counter is an anti-signal here; reserve it for immersive/WebGL archetypes.

**Anti-signals** — absent from every winner examined: the washed pale-tint button fill (`accent @ ~10% alpha` fading in, reads as a disabled hover); a contrasting-colored `border-bottom` under the nav (winners' borders, when present, are same-family hairlines); one universal card hover on every tile; a global custom cursor (lagging dot/ring sitewide); a per-letter kinetic headline on a non-motion brand; heavy hero parallax (substitute lag-based grid scroll); and uniform `fade-up-on-everything` with linear per-element delays.
