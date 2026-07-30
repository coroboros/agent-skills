# Bento / Card-Based

Modular asymmetric tiles inspired by Japanese bento boxes, popularized at scale by Apple keynotes. Each tile is a self-contained information unit with its own visual treatment, behavior, and state. Container queries enable self-aware cards that adapt to their own dimensions rather than the viewport. The structure teaches itself.

Tier 1 (DNA, anti-signals, macrostructures, reflexes) is `references/archetype/bento-card.md`, pushed into context by `scripts/direction_roll.py`. This file is tier 2: it loads at the design_plan commit, BY HEADING, never whole.

## Contents

- [Canonical reference — Anime.js v4](#canonical-reference--animejs-v4)
- [DNA — non-negotiable](#dna--non-negotiable)
- [Common expressions](#common-expressions)
- [Bento 2.0 — motion-engine paradigm](#bento-20--motion-engine-paradigm)
- [Layout](#layout) · [Typography](#typography) · [Color](#color) · [Saturation warning](#saturation-warning)
- [What makes it award-worthy](#what-makes-it-award-worthy) · [Ideal for](#ideal-for) · [Cross-references](#cross-references)
- [Effect palette — what this line's winners ship](#effect-palette--what-this-lines-winners-ship) — per-element-class recipes, the grammar, tap/focus/dormancy
- [Mid-page life](#mid-page-life) · [Scroll texture](#scroll-texture) · [Idle band](#idle-band) · [Channel calibration](#channel-calibration)
- [Page recipe — how this line's winners build the page](#page-recipe--how-this-lines-winners-build-the-page) — anatomy, hero, section chain, footer, arrival, copy, imagery, mobile, variation
- [Spectacle menu](#spectacle-menu) — the hero beat, the continuation beats, the peak law
- [Component index](#component-index) — the library ids this archetype reaches for

## Canonical reference — Anime.js v4

**Site.** Anime.js v4
**URL.** `animejs.com`
**Award.** Awwwards Site of the Day 2025-05-06 — 7.62 overall, plus the Developer Award at 7.84 with Animations/Transitions 9.00
**Studio.** None — open-source library project led by Julian Garnier.

A canonical modern bento layout. A modular asymmetric grid of self-contained feature cards, each demoing one capability — scroll scrubber, lightweight modular core, complete animator's toolbox, layout-grid demos that morph between bento configurations. Consistent corner radii. Neutral palette. The Notion / Linear / Apple-iOS lineage executed at award tier. The site is genuinely a hybrid — brutalist palette, bento structure — which is why some sources tag it brutalist. The structural logic is bento. Substitutable peers: `apple.com` (canonical bento on product detail pages), `linear.app` feature grid (minimalist bento with discipline), `vercel.com` platform features (monochromatic bento with subtle depth).

## DNA — non-negotiable

- Modular asymmetric tiles — never uniform 3-equal-cards-in-a-row (the "feature row" cliché)
- Each tile is a self-contained information unit with its own visual treatment
- Every tile *demonstrates* its claim in one of three proof registers — a running demo (`live-demo-tile`), a slice of the real product UI, or a custom illustration or diagram where the product has no UI to slice (Sui, a blockchain); a label-and-body stamp that never shows its claim is the failure this archetype exists to avoid
- Container queries (`container-type: inline-size`) make tiles self-aware
- Consistent corner radii across the grid; equal gutter widths (12–24px) — visual rhythm holds
- Hero cards (2×2 spans, or `col-span: 2 row-span: 2`) carry primary features

The archetype keeps its identity across structural-pure (Apple, Linear), motion-engine premium (Bento 2.0, Vercel feature grids), brutalist-bento hybrid (Anime.js v4), illustrated-module decomposition (Sui), and gradient-bento (Linear's atmospheric variant).

## Common expressions

Three stacks fit the DNA. Pick the one matching product type and personality.

### Structural-pure — Apple / Linear feature grid profile

Light foundation (`#F9FAFB` to `#FCFCFC`) or dark foundation (`#0A0A0F` to `#12121A`). Cards in off-white (`#FCFCFC`) or `#1A1A24`. Hairline borders (`#E5E7EB` light / `rgba(255,255,255,0.08)` dark). Per-card accent colors for visual differentiation. Content-first, motion restrained. Ideal for SaaS product pages, feature comparison, dashboard previews, technical product marketing. The illustrated-module variant belongs here: where the product has no UI to slice, each tile carries a bespoke illustration of one named module (Sui's six-tile stack, Awwwards SOTD 2026-06-23).

### Motion-engine premium — Bento 2.0 (Vercel-core meets Dribbble) profile

Light foundation (`#F9FAFB`) with off-white cards (`#FCFCFC`), 1px borders at `border-slate-200/50`, generous `rounded-[2rem]` corners at the top of the verified 12–32px trend band, "diffusion shadow" (`box-shadow: 0 20px 40px -15px rgba(0,0,0,0.05)` — wide, low-opacity, tinted). Labels (titles, descriptions) sit OUTSIDE and BELOW the cards in a gallery-style presentation. Cards carry micro-interactions — the grid is "alive". Uses Geist, Satoshi, or Cabinet Grotesk with `tracking-tight`. Padding `p-8` to `p-10`. Ideal for premium SaaS, AI products, modern dashboards, agency-built marketing pages.

### Brutalist-bento hybrid — Anime.js profile

Dark foundation (`#0A0A0A` to `#0E0E12`) with white display type at large scale, central rainbow visualization or feature demo as the focal point of the hero card. Cards inherit the brutalist palette discipline (one accent per tile, flat fills) inside the bento structure. Ideal for developer tools, animation libraries, technical content where the demo IS the product.

## Bento 2.0 — motion-engine paradigm

When the project calls for the premium motion-rich expression, follow the Bento 2.0 architecture and choreography rules. Published Bento 2.0 sources define the trend by three verified constants — exaggerated corner rounding (12–32px), container-query self-aware tiles, and subtle "alive" micro-interaction. Everything below that line is a corpus-generalized pattern (drawn mainly from Anime.js) plus internal reference: a strong default to build against, not award-canon law.

### Architecture

- **Background**: `#F9FAFB` (light) or `#0A0A0F` (dark)
- **Card surface**: `#FCFCFC` (light) or `#1A1A24` (dark) with 1px hairline border at `rgba(0,0,0,0.05)` (light) or `rgba(255,255,255,0.06)` (dark)
- **Corner radius**: `rounded-[2rem]` (32px, the top of the verified trend band) for major containers; nested elements use concentric smaller radii (`rounded-[calc(2rem-0.375rem)]`) — the Doppelrand pattern, see `premium-patterns.md`
- **Diffusion shadow**: wide, low-opacity, tinted to background hue — `box-shadow: 0 20px 40px -15px rgba(0,0,0,0.05)`. Creates depth without clutter
- **Padding**: `p-8` or `p-10` (32–40px) inside cards
- **Labels**: titles and descriptions OUTSIDE the card, below — gallery-style presentation. Avoids cards-inside-cards-inside-cards
- **Typography**: Geist, Satoshi, or Cabinet Grotesk with `tracking-tight` for section headers

### The 5-card archetypes

Each Bento 2.0 grid mixes these tile-types; `perpetual-tile-machines` ships them as the library form. The goal is variance — never all five-of-the-same.

1. **The Intelligent List** — vertical stack of items with infinite auto-sorting loop. Items swap positions via Framer Motion `layoutId`, simulating real-time prioritization.
2. **The Command Input** — search or AI bar with multi-step typewriter effect. Cycles through complex prompts, blinking cursor, "processing" shimmer state.
3. **The Live Status** — scheduling or telemetry interface with "breathing" status indicators. Pop-up notification badge emerges with overshoot-spring, holds 3 seconds, vanishes.
4. **The Wide Data Stream** — horizontal infinite carousel of data cards or metrics. Gapless loop via `x: ["0%", "-100%"]`. Speed feels effortless.
5. **The Contextual UI (Focus Mode)** — document view animating staggered text-block highlight, followed by float-in floating action toolbar with micro-icons.

### Choreography

- **Spring physics** (Framer Motion): `type: "spring", stiffness: 100, damping: 20` for premium weight. Linear easing reads as cheap.
- **Layout transitions**: heavy use of `layout` and `layoutId` props for re-ordering, resizing, shared element transitions.
- **Perpetual micro-interactions**: most proof tiles carry one infinite loop (Pulse, Typewriter, Float, Carousel, Shimmer) so the grid rarely goes fully silent. The loops share one physics and one focal hierarchy — two may reinforce one focal point, never compete (the premium-patterns.md one-per-fold cap applies outside the grid). Per-tile loops are one carrier channel, not the only one: section-scale devices (`section-scale-momentum`) are co-equal.
- **Performance lock**: any perpetual motion or infinite loop MUST be memoized (`React.memo`) and isolated in its own microscopic Client Component. Re-rendering the parent layout from a perpetual animation breaks 60fps on mid-range mobile.
- **Magnetic micro-physics** for hover: never use React `useState` for magnetic hover or continuous animation. Use exclusively Framer Motion's `useMotionValue` and `useTransform` outside the React render cycle.

## Layout

Consistent border-radius (12–20px structural, up to 32px for the rounded Bento 2.0 look — the verified trend range). Equal gutters (12–24px). Container queries for self-aware tiles.

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

`grid-auto-flow: dense` backfills gaps by reordering placement, which reduces holes — it does NOT guarantee zero empty cells when an item cannot fit. Verify mathematically that `col-span` and `row-span` values interlock: no grid ships with a missing corner or an empty void, and dense flow alone will not prove that for you.

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

The bento pattern reached oversaturation in 2025. Designers report bento fatigue. The article's anti-patterns section flags "bento grid layouts have reached oversaturation" alongside heavy parallax and static gradients. The pattern still takes fresh hard awards when it is built rather than stamped — Sui takes SOTD 2026-06-23 (7.38) carried by three card grids. To differentiate when the project genuinely calls for bento:

- Vary card sizes dramatically (1×1, 2×1, 2×2, 3×1, 1×3) — never uniform
- Add internal motion / animation — cards that feel alive, not static (Bento 2.0 paradigm)
- Use real content and data, not abstract shapes or placeholder copy
- Break the grid occasionally — one element that escapes the tile boundary (`overflow: visible`, illustration that protrudes)
- Consider Spatial Organic as a fresher alternative for 2026–2027 if the brief allows

## What makes it award-worthy

A bento site scores 8+ when the asymmetric grid teaches the product (Anime.js demos one capability per tile), when each tile carries weight (variance, not uniform repetition), and when the motion engine — if applied — earns the "alive" quality without burning the performance budget. Anime.js succeeds because every tile demos the library it documents; the structure is the product.

The archetype loses identity when bento becomes "3 equal cards in a row" with rounded corners, when every tile uses the same archetype (5× The Intelligent List = noise), when the grid goes dead — proof tiles whose only motion is a one-shot on-scroll reveal and no section-scale momentum anywhere — or when perpetual motion is applied without memoization isolation and the page drops below 60fps on mid-range mobile.

## Ideal for

SaaS product pages (Notion, Linear, Supabase, Vercel adjacency), feature comparison pages, product launches with multiple capabilities to demo, dashboard previews, AI-product feature grids, developer-tooling marketing, platforms decomposable into named modules.

## Cross-references

Read alongside `foundations.md` (container queries, OKLCH per-card accents, animation toolkit), `premium-patterns.md` (Doppelrand for nested card architecture, button-in-button trailing icon, eyebrow tags above cards), `anti-patterns.md` (3-equal-cards-in-a-row is axiomatic; bento fatigue is real), `audit-rubric.md` (Hierarchy 8+, Spacing 9+ are entry bars), `exemplars.md` (Apple product pages, Linear feature grid, Vercel platform features).

Provenance for every claim below — the researcher rounds and the fresh-context refutations that corrected them — lives in the public deep-research corpus of `github.com/coroboros/research`, under `articles/award-winning-websites-2025-2030/deep-research/`: `archetypes/bento-card.md`, refutations folded under its `## Refuted` heading, the raw reports preserved verbatim at commit `fd5d1b6`.

## Effect palette — what this line's winners ship

Corpus — Anime.js v4 (Awwwards SOTD 2025-05-06, 7.62 overall; Developer Award 7.84 with Animations/Transitions 9.00; Julian Garnier, no studio), Endex (Awwwards Honorable Mention 2025-03-24, "AI Built For Excel", Together (Pro) + Will Beeching, 15/17 jury votes), Sui (Awwwards SOTD 2026-06-23, 7.38 overall, Animations/Transitions 7.40; HOLOGRAPHIK + AKKA Studio + Sui Foundation Design), Attio (Awwwards HM 2021-04-06 for an earlier design — the current bento feature grid is design-canonical, and the fresh award weight of a 2021 HM is nil), Vercel (Vercel Ship 2025 took an HM 2025-05-22 as an event microsite; the platform feature grids cited here are design-canonical, whole-site award unverified), Linear and Supabase (design-canonical, whole-site award unverified), Apple (design-canonical, never an Awwwards submission). Anime.js and Endex and Sui carry the hard awards; the rest supply mechanics that are shipped and observed, not jury-verified.

**The grammar** — cohesion is a single through-line expressed differently across element classes, never one gesture stamped everywhere. Anime.js binds everything with *motion* — the button presses, the link brightens, the tile animates, the demo scrubs, the footer link fill-swipes, all one animation engine's primitives. Vercel binds everything with *edge-catching light* — the same streak rides the card border, glints the CTA, frosts the nav. Supabase binds with *border-glow* — the blurred accent under-glow on the card, the tinted CTA, the panel bloom. Button, card, and nav differ in mechanism yet obey one physics. One hover on every tile is sameness mistaken for consistency — the failure to break.

**Buttons / CTA**
- **Ghost outline + transform-press** — hairline border at a mid-neutral token (Anime.js `#625d5b` on `#252423`), background never fills; animate `transform` only — a sub-pixel mechanical press, `transition: transform 0.125s ease-out`, radius `4px`. Pick for brutalist and dev-tool grids where restraint is the brand. (Anime.js, Awwwards SOTD 2025-05-06 — mechanic winner-verified, the hex and duration observed in a prior winner read and not re-executed this run)
- **Token-step solid / inversion** — a solid pill (`border-radius: 100px`) advances one full step through the ramp or inverts fg/bg on hover, never a translucent tint — a crisp `~0.15s` token change. Pick for premium SaaS with a disciplined color system. (Vercel/Geist, design-canonical, award unverified; corroborated by Anime.js's solid-accent button)

**Links**
- **Underline draw** — pseudo-element underline scales `scaleX(0)→1` from the left over `~0.3s` with an expo-out ease. (single-source for the exact mechanism; the effect itself is near-universal)
- **Neutral→foreground brighten** — muted links (`--fg-3`, Anime.js `#b4b1af`) lift to `--fg-1` on hover, `transition: all`, no underline. Pick for dense link lists, footers, in-card links. (Anime.js — mechanic winner-verified, hex observed in a prior read)

**Cards** — the heart: one hover affordance per grid, never a universal lift; let tiles differ by content.
- **Cursor-tracked conic border-shine** — a conic gradient in the border via `mask` + `mask-composite: intersect`; JS drives `--x/--y` (plus a `--start` angle) so a light streak rides the edge under the pointer. Pick for dark, flat panel grids. Library id: `conic-border-shine`. (Vercel + Supabase, design-canonical, award unverified)
- **Spotlight expand + reveal** — hovered tile expands across its row, siblings reflow, a de-saturated preview restores to color, copy fades up — layout-aware, not a scale. Verified Codrops params: GSAP paused timeline, `ease: power2.inOut`; siblings shift `2.5vw` inward; a 12-point clip-path cross morphs open; preview scales `(dim − 5vw)/dim`. Pick for feature grids with real imagery per tile. Library id: `spotlight-expand-tile`. (Vercel spotlight + Codrops technique)
- **Border-glow bloom** — a blurred accent gradient in a pseudo-element behind the card fades `opacity 0→1` as a soft under-glow, not a hard shadow; accent = the tile's own OKLCH token, and the blur never animates. Pick for dark grounds (`--bg` ~`#0A0A0F`). Library id: `border-glow-bloom`. (Supabase + Linear, design-canonical, award unverified)
- **Live-demo tile (no lift at all)** — the tile is a running canvas/WebGL demo; hover or drag drives the actual animation, so the content reacts and there is no card chrome. Pick when the demo IS the product. Library id: `live-demo-tile`. (Anime.js — winner-verified, single-source but the anchor's core claim)
- **Expand in place** — the card grows and reveals its content where it stands, corner radius held; distinct from the row-reflow spotlight and from a contained zoom. Pick for audience segmentation. (Sui's four industry cards — institutions, AI, DeFi, gaming — winner-verified, submission-highlighted)

The AI-default `translateY(-4px) scale(1.02)` + grey `box-shadow` on every tile is the flattening trick to break.

**Nav**
- **Transparent overlay, unchanged on scroll** — header stays fully transparent (`background: rgba(0,0,0,0)`, `backdrop-filter: none`, `border-bottom: 0`) at the top and scrolled — works over one flat ground. (Anime.js — mechanic winner-verified, the CSS values observed in a prior read)
- **Transparent→frosted hairline on scroll** — gains `backdrop-filter: blur()` over a semi-opaque surface plus a same-family hairline (`rgba(255,255,255,0.06)` dark / `rgba(0,0,0,0.05)` light), never a contrasting accent line. Pick for light/product bento over shifting sections. This row is the ONE sanctioned exception path to the zero-nav-`border-bottom` gate — reusing it takes a written override in the design_plan citing this row; same-family at ≤5–6% alpha only, never a contrasting line. (Apple + Vercel + Sui — documented)
- Nav items brighten muted→foreground; no background pill.

**Text**
- **Per-char / per-word stagger — signature, gated to motion brands** — split the display headline and stagger it in only when motion IS the product; elsewhere it fights the content. (Anime.js — winner-verified, single-source by design)
- **Tight-tracked static display** — the supporting default: sentence-case headline, weight `600`, negative tracking (Vercel `-2.4px` / `tracking-tight`), no animation beyond the section reveal. (Vercel documented + Anime.js)
- **Mono eyebrow + tabular metrics** — labels and in-tile numbers in mono (Geist Mono / JetBrains Mono) with `font-variant-numeric: tabular-nums`; numbers can count up on reveal (`counter-odometer`). The per-tile register shift is the effect.

**Cursor** — keep the native pointer deliberately (`body { cursor: auto }`); the grid is scan-and-click and a laggy dot fights it. A custom cursor appears only inside an interactive demo tile, never sitewide. The pointer powers surface effects — feeding `--x/--y` into border-shine or glow — rather than being dressed up. (Anime.js)

**Loader / intro** — two legal families. None/instant: no preloader element, and the entrance IS the card stagger — `opacity 0→1` + a short `translateY`, `40–80ms` per tile — so the page assembles itself (Anime.js ships zero preloader; Endex SSR-paints copy pre-hydration, both winner-verified). Or a designed intro loader carrying a `0→100%` counter ahead of the hero, which is award-viable in this line: Sui runs one and takes SOTD 2026-06-23 (winner-verified, submission-highlighted).

**Element states — tap, focus, dormancy.** The pointer layer is one costume of the state; the tap and focus answers are not optional and not a degraded copy.
- **CTA** — hover is a full-token flood + label inversion (`fill-invert-cta` — direct pole swap, or a panel wiping up from the bottom edge, `~.15s`), the ghost-outline sub-pixel transform-press, or a token-step solid advancing one full ramp step; never a pale `~10%` accent tint, which reads as a disabled hover. `:active` IS the touch answer — hard-press offset-shadow collapse or the fill flood, 90–160ms flash floor, replacing hover entirely. `:focus-visible` mirrors hover plus a same-family ring, reachable in tab order.
- **Link** — hover draws the underline `scaleX(0→1)` from the left at `~.3s` expo-out, or brightens muted `--fg-3` to `--fg-1` with no background pill. Tap gets a `~120ms` brighten flash; in footers the instant fill-swipe (`transition-duration:0s`) doubles as the tap cue. `:focus-visible` fires the underline plus the accent recolor (`accent-link`).
- **Figure / tile** — ONE affordance per grid: contained inner zoom to 1.1 plus a companion cue — tint, scrim lift, caption rise — as the default (`figure-hover`, felt, never a 1–3% twitch), else conic border-shine, spotlight expand, border-glow bloom, or live-demo reaction with no chrome at all. Tap navigates after a brief `:active` depress (scale `~.98` or an opacity dip, 90–160ms) — a tile that navigates with no press feedback reads unresponsive. The pointer-tracked classes go dormant on touch and the static hairline is the complete rest look. `focus-within` lifts the same cue hover uses, so keyboard reaches hover-revealed content.
- **Index row / expandable** — hovered row lights an accent rule and surfaces metadata while siblings dim to `~45%` (`index-row-hover`), or the card expands in place with its corner radius held. On touch the expand answers the tap and there is no dim-siblings state. `:focus-visible` lifts identically; reduced-motion skips the sibling dim and jumps to the final state.
- **Heading / prose / metrics** — nothing on hover, corpus-wide. The effect is the entrance: `kinetic-reveal`'s masked line, a per-char or per-word stagger ONLY on motion brands, else tight-tracked static display; metrics count up on reveal.
- **Nav** — items brighten muted→foreground, no pill; tap gets a brighten flash; `:focus-visible` adds a same-family ring. The bar is a transparent overlay unchanged on scroll over one flat ground, or transparent→frosted with a same-family hairline at ≤5–6% alpha over shifting sections.
- **Cursor** — the native pointer stays. A custom cursor is scoped inside a live-demo tile and nowhere else; the pointer's only other job is feeding `--x/--y` into the border-shine or glow, and that job is simply absent on touch.

**Anti-signals** — absent from every winner examined: the washed pale-tint button fill (`accent @ ~10% alpha` fading in, reads as a disabled hover); a contrasting-colored `border-bottom` under the nav (winners' borders, when present, are same-family hairlines); one universal card hover on every tile; a global custom cursor (lagging dot/ring sitewide); a per-letter kinetic headline on a non-motion brand; heavy hero parallax (substitute lag-based grid scroll); and uniform `fade-up-on-everything` with linear per-element delays.

## Mid-page life

The prose zone between hero and footer is carried by non-text engines, never by animated headings or scroll-scrubbed paragraphs. Four are winner-attested. The pinned demo reel — a run of `100lvh` panels over a persistent `position:fixed` demo layer, copy cross-fading against it, page-wide `--hex-current-*` recolor per section (Anime.js 7.62, Animations 9.00, winner-verified structure; the exact panel count is not re-executable from a fetch and static markup surfaced 6 feature blocks on re-read, so build to N panels and not to a number). Ambient perpetual objects — a WebGL sphere, a footer globe, logo marquees, a drag-parallax Swiper — over enter-once IntersectionObserver reveals (Meridian 8.05, winner-verified). Concrete proof tiles with near-zero décor — one `.4s` reveal class in the whole build, density and rhythm carrying it (Endex, Awwwards HM 2025-03-24, 15/17 jury votes, community averages spanning 6.5–10 across axes). And section-scale momentum — a scroll-driven gradient transition morphing the ground between sections plus an interactive footer (`section-scale-momentum`; Sui SOTD 2026-06-23, winner-verified, submission-highlighted), the co-equal channel beside the per-tile loops. Proof tiles that show their claim through product-UI slices, live demos, or custom illustrations are three registers of one requirement, not a ban on icons; an icon beside a tile that also shows its claim is fine, an icon standing in for the proof is not. Hover-on-text stays a three-move vocabulary — link/nav brighten to foreground or accent, underline/bar draw `0→1` at `~0.3–0.5s`, icon nudge `~.125rem` — headings, paragraphs, and metrics get nothing on hover (winner-verified across the corpus).

## Scroll texture

What carries the eye down the page between interactions: pinned `100lvh` demo panels cross-fading as scroll advances, each panel holding while its demo runs before handing off (Anime.js, winner-verified); a scroll-driven gradient transition morphing the page ground continuously as sections advance, full-width and tied to scroll progress (Sui, winner-verified, submission-highlighted); or lag-based grid scroll — columns easing at offset rates so the grid itself has drag. The design_plan names one; without a carry between tiles the grid reads as a static poster. The tier does NOT smooth the wheel — native scroll is the canon: 0/3 winners ship a smoother (Anime.js reads native scroll through its own ScrollObserver; Meridian and Endex carry no Lenis/Locomotive string in any served bundle, winner-verified) — adding Lenis fights the scan-and-click grid.

## Idle band

Perpetual micro-loops inside the tiles: the red-dot period loop, the clockwork counter — small machines that never stop (Anime.js, winner-verified mechanism; the loop CSS is observed in a prior winner read, not re-executed this run). `perpetual-tile-machines` ships the five structured forms — auto-sorting list, typewriter command input, breathing status badge, gapless data stream, focus-mode highlight — as distinct from `ambient-idle`'s unstructured glow, float, shimmer and pulse. Commit one or two; the idle life lives inside the tiles, never on the page ground. Every loop ships memoized and isolated with `visibilitychange` and IntersectionObserver pause, because a grid that stutters below 60fps on mid-range mobile scores worse than a static one.

## Channel calibration

Channel calibration — this line's winners run 3–4 distinct interaction channels (per-class states, display-type effects, cursor into surfaces, idle tile loops, scroll texture, replayable spectacle); the pre-emit critique's Aliveness axis reads against that band, never against bare coverage.

## Page recipe — how this line's winners build the page

Corpus — Anime.js v4 (SOTD 2025-05-06 + Developer Award, live), Endex (HM 2025-03-24, live), Sui (SOTD 2026-06-23, submission captures + live), Apple MacBook Air, Vercel, Linear (live, shipped/design-canonical). The first three carry hard awards.

**Anatomy** — *Pinned demo reel* (`specimen-tour`; Anime.js, winner-verified): left-copy/right-demo hero [attention] → toolbox grid [understanding] → a run of pinned `100lvh` demo panels over a persistent fixed demo layer [proof, climax] → modules bento, `24.50 KB` bundle stat [proof] → sponsors [rest] → get-started [close] → newsletter footer; 12–16 viewport-heights. *Editorial 12-col feature grid* (`capability-grid`; Endex, winner-verified; Vercel/Linear shipped): dark hero [attention] → divided capability strip (`divide-x`, marquee on mobile) [understanding] → `lg:grid-cols-12` cards carrying concrete proof [proof] → CTA close [close] → compact footer [rest]; climax diffuse. The 12-col product-UI grid is the awarded artifact's shape — live endex.ai on re-read runs a copy-led hero, an enterprise carousel, a value triad, testimonials and a text feature list, so build the arc from the award, not from today's page. *Module decomposition* (`structural-decomposition`; Sui, winner-verified): intro loader + `0%` counter → "Build full stack" hero [attention] → partner logo carousel → value triad [understanding] → the six-tile named-module stack rendered as custom illustrations [proof] → builder/user benefit split → four expandable industry cards [proof] → four-tile CTA hub [close] → interactive footer. *Highlights bento + deep-dive* (`highlights-bento`; Apple, shipped): render hero [attention] → "Get the highlights." 6-tile bento, six claims in one screen [understanding] → per-theme full-bleed long-form [proof] → mega-footer [close]; climax diffuse.

Route on the brief's declared inputs, never on a taste read: a developer tool, library or API whose artifact can run itself → `specimen-tour`, one capability per pinned panel; a SaaS or AI product with real product UI to show → `capability-grid`, editorial 12-col with real UI slices where a UI exists; a platform decomposable into named modules → `structural-decomposition`, custom illustrations where there is nothing to slice; a product with N discrete highlights → `highlights-bento`, all claims in one screen plus deep-dives. Pick exactly one, never blend two arcs, and never open on a card-grid fold — the grid is always a mid-page proof layer and the anchors all open copy-led.

**Hero architectures** — *Left-copy / right-demo split* (Anime.js, winner-verified): the visible headline is an `<h2>` at `--text-xxxxl` — the `<h1>` is the logo; the sticky header's same-family hairline ships only via the Effect palette Nav row's written override; the red `:before` pill marks the Sponsor item, not Docs (the token hexes here are observed in a prior winner read, not re-executed this run). Entrance beats (shipped; durations not read): headline chars stagger → red-dot period color/scale loop → "the web" swap loop — these ARE the intro. *Centered display over dark* (Endex, winner-verified): H1 `text-[88px] leading-[0.92] text-white`, one-line subhead, dual CTA "Request Demo" / "Join Waitlist". *Claim over a card-preview stack* (Sui, winner-verified): a three-word imperative over a preview of the tiles the page is about to decompose, preceded by the intro loader.

**Section chain** — the winner-verified order with its intensity map and the state each section owes. Pick forms by role; never hand-write hero or section layout CSS.

| role | form | pairs | intensity | state it owes |
|---|---|---|---|---|
| hero | `hero-masthead(media:right)` — live-demo anchor; `hero-masthead(media:none)` — statement | h1 `kinetic-reveal`; standfirst `text-emphasis-fill`; cta-row `masked-label-swap`+`fill-invert-cta`; media `scrub-film` \| `live-demo-tile` | 7 | MANDATORY dual commitment — the ≤7-word claim reads in one beat AND one live anchor is already running (right-side demo animating, or the headline's own micro-loop). No card-grid fold. Nav transparent over the hero. Per-char stagger on motion brands only, else a kinetic line mask. An optional intro loader may precede it |
| understanding | `feature-card-grid(toolbox)`; `divided-capability-strip`; `stat-band` / value triad | `figure-hover`; `text-emphasis-fill`; `counter-odometer` | 5 | a light layer between hero and grid — a toolbox of perpetual micro-demos, a `divide-x` strip that becomes a marquee on mobile, or a three-item triad. Low amplitude: it sets up the grid, it is not the grid |
| proof | `feature-card-grid` — concrete proof tiles: UI slices, live demos, or custom illustrations | `figure-hover` (passive); `counter-odometer` (stat); `conic-border-shine` \| `border-glow-bloom` (fine-pointer); `live-demo-tile`; `perpetual-tile-machines` | 7 | THE HEART — most proof tiles carry an aliveness carrier (infinite micro-loop, live demo, or interaction-driven response), or section-scale momentum runs around the grid. Spans vary 4–12 under dense backfill. ONE hover affordance for the grid, never a universal lift. Tiles whose only motion is a single-run reveal, with nothing at section scale either, are the dead grid |
| peak (optional) | `pinned-demo-panels`; `spotlight-expand-tile` | copy `text-emphasis-fill` | 9 | OPTIONAL and capped at one — pinned `100lvh` panels over a persistent fixed demo layer with copy cross-fading and a page-wide recolor, driven by drag or scroll-scrub so it replays; or a spotlight expand with row reflow and grayscale→color restore. Many winners omit it entirely; do not force it |
| deep-dive / audience segment | `editorial-split`; expand-in-place cards | h2 `char-assemble`; prose `text-emphasis-fill`+`semantic-accent`; rows `index-row-hover` | 6 | per-theme full-bleed long-form, or audience-segmented cards that open in place with the corner radius held — a distinct mechanic from `figure-hover`, the card grows and reveals content where it stands |
| rest | `logo-wall` | — | 4 | the designed rest before the close: a static wrapped wall, grayscale at rest → color on hover as the only micro-state; never a marquee, never autoplay |
| close | `close-panel`; four-tile CTA hub | ask `kinetic-reveal`; channels `fill-invert-cta`+`masked-label-swap` | 6 | one imperative and decisive channel rows, or a four-tile hub (Sui: build / code / earn / community). CTA fill-inverts on hover and tap, never a pale tint. No media slot, so the close cannot become a mood reel |
| footer | `tabular-index` (product variant); interactive footer; `oversized-wordmark` reprise | `accent-link`; `masked-label-swap` | 4 | functional link-column chrome whose designed moment is a wordmark reprise, a newsletter capture, or a live reactive surface. One designed micro-cue, not spectacle |

**Footer** — functional link-column chrome; the designed moment is a wordmark reprise, a newsletter capture, or a live interactive surface. Anime.js (winner-verified): sponsor-first — "Platinum sponsors" + "Become a sponsor" — then Site/Socials columns, "Stay in the loop", "© 2026 Julian Garnier"; footer links hover into a monochrome current-token fill (`color:var(--hex-current-1);background-color:var(--hex-current-7)`, `transition-duration:0s`, arrow nudge `translate(.125rem)`), the red-1/red-6 fill belonging to the Sponsor link alone — the CSS-level values observed in a prior winner read, not re-executed this run. The recipes name that shape `tabular-index`, product variant: sponsor-first block, instant fill-swipe hovers, newsletter. Endex (winner-verified): compact 3-col legal/contact + ©, with the `oversized-wordmark` reprise as the Linear-shipped alternative. Sui ships an interactive footer reacting to pointer and scroll (winner-verified, submission-highlighted) — a reactive footer is award-viable in this line, not only a link column.

**Arrival** — two legal Loader families (`ingredients/preloaders.md`). None/instant, letting the card stagger be the entrance: Anime.js ships zero preloader and the hero stagger IS the intro (winner-verified); Endex SSR-paints copy pre-hydration (winner-verified). Or a designed intro loader with a `0→100%` progress counter ahead of the hero — Sui ships one and takes SOTD 2026-06-23 with it (winner-verified, submission-highlighted). Routes (`ingredients/page-transitions.md`): none — the anchors are one-pagers; multi-page members use plain framework navigation (observed, implementation unverified).

**Copy voice** — Quoted to calibrate, never to ship — imitate the specificity (the named place, the count, the refusal), never the wording. Product-as-subject declaratives plus second-person imperatives; never "we" in headlines. Hero = a noun phrase or ≤7-word claim; subhead = one sentence naming what it is and who it's for; section heads 2–6 words. Each tile names ONE capability and the tile shows it. Verbs cool — animate, accelerate, reason, audit. Terminal period on fragment headlines is the house tic; zero exclamation. Refuses hype adjectives; states the capability and stops.
- "All-in-one animation engine." (Anime.js) — the category claimed in four words; the period is the animated red dot.
- "AI Built For Excel" (Endex) — the wedge in four words.
- "Hire your AI Excel Agent" (Endex) — the close names the product's job.
- "Build full stack" (Sui) — the imperative names the job, three words, no object.
- "Ownable by design" / "Verifiable by default" (Sui) — the value triad as two-beat property claims.
- "Get the highlights." (Apple) — the bento's own section head is an imperative.
- "M5. The chip that zips." (Apple) — a spec turned into rhyme.

**Imagery art direction** — the asset is the product surface; no stock, no portraits. Subject: live demo (Anime.js), product-UI slices (Endex's awarded artifact, Linear, Attio — Endex's live page carries a text feature list on re-read, so the slice register rests on the award), hardware render (Apple), custom illustration per named module where the product has no UI to slice (Sui). Grade: neutral, true-to-UI, one dark ground page-wide (Anime.js `#252423`; Endex dark hero with one paper-white capability strip); Apple splits per cell — each tile its own render-on-gradient, radius and gutter rhythm holding; Sui holds one illustration system across the six module tiles. (Anime.js/Endex/Sui winner-verified; Apple shipped)

**Mobile / touch** — bento holds its identity on touch better than any hover-dependent archetype, because its aliveness is autonomous loops plus scroll-driven section devices rather than hover. Pointer-driven card classes go dormant — conic border-shine, spotlight expand, magnetic pull, 3D tilt all off — and the static hairline surface is the complete touch appearance, not a gap. Press-class elements answer the tap: the CTA fill-invert or hard-press `:active` collapse IS the tap answer at a 90–160ms flash floor, and proof tiles that navigate get the same brief depress (scale `~.98` or an opacity dip) before the route change — the tactile acknowledgment Awwwards Mobile Excellence rewards. The perpetual per-tile loops continue on mobile and the scroll-driven gradient transition survives touch, which is the archetype's mobile advantage and also why perf is the hard gate: every loop ships `React.memo`-isolated in its own micro client component driving continuous or pointer motion through `useMotionValue`/`useTransform`, never `useState`, or the grid drops below 60fps on mid-range mobile and scores worse than a static one. The grid reflows to a 1-col stack or 2-col with spans collapsing; the divided capability strip becomes a marquee (Endex, winner-verified); any horizontal card track becomes a native scroll-snap swipe with next-cell peek and tap-to-enlarge (`swipe-snap-gallery` — the scored Mobile Excellence line). Cross-device parity is weighted heavily: a desktop-only alive grid that goes static on mobile fails Usability.

**Variation** — this section chain is one legal costume of the archetype, never THE skeleton. Structure is story-native: the body's sections derive from the universe's spine, then check against these roles for coverage — never the reverse. The axes serial winners measurably rotate between builds (21-artifact corpus, 5 studios): body content archetype and item counts, the ONE signature device (never reused across builds), the close mechanism, the hero medium, the index/HUD costume. What persists as DNA: type grammar, the motion register (the register itself, never the named reading/interaction kit — that kit is a device, rotated per build like the signature), annotation grammar as a form, engineering architecture. The same content archetype + item count + close mechanism recurring across two different-brand builds has zero winner precedent.

**Anti-signals** — no card-grid fold; the anchors open copy-led and the grid is a mid-page proof layer. No route curtain — the anchors are one-pagers. No stock and no portraits. No uniform tile treatment: spans vary and each tile keeps its own register. No tile that describes its claim without showing it. 2025 winners lean editorial 12-col over the saturated tile wall — the bento-fatigue correction.

## Spectacle menu

*Anime.js pinned feature gallery* (winner-verified structure): scroll into any of the `feature-section{height:100lvh}` panels → copy at `position:fixed;opacity:0` cross-fades while a persistent demo runs the heading's claim — drag and throw the Draggable panel, the Scroll Observer scrubs your scroll → the demo proves the heading; interactive and looping, so it replays. Build to N panels, not to a number: the site's JS is not executable from a fetch and static markup surfaced 6 feature blocks on re-read. *Sui distributed set* (winner-verified, submission-highlighted captures): an intro loader with a `0%` counter → per-tile hover across the six-tile module stack → a scroll-driven gradient transition morphing the ground between sections → four expandable industry cards → an interactive footer. *Apple highlights reveal* (shipped): the "Get the highlights." tiles scrub into place after the fold.

**The hero beat.** COPY-LED CLARITY WITH ONE LIVE ANCHOR — not a full-bleed spectacle, and never a card-grid fold. The commitment is dual: legible in one beat (a ≤7-word category claim) and alive in one beat (the anchor is already running, pointer- or autoplay-armed). `specimen-tour`: left-copy / right-demo split, the demo animating before any input, the headline's own micro-loop as the intro. `capability-grid`: a dark centered statement with dual CTAs over an armed ground. `structural-decomposition`: the claim over a card-preview stack, optionally preceded by an intro loader. The bento hero under-commits on purpose — the spectacle budget is spent downstream, in the tiles and at section scale.

**The continuation beats** — the page is diffed against these, section by section.
- *understanding layer* — LIGHT SET-UP at ~5: a toolbox card grid of perpetual micro-demos, a `divide-x` capability strip (`divided-capability-strip`, marquee on mobile), or a three-item value triad. It sets up the grid; it is not the grid.
- *proof grid* — THE HEART at ~7: most proof tiles carry an aliveness carrier, and the grid holds ONE hover affordance across every tile.
- *peak* (optional) — THE ONE DESIGNED SPECTACLE at ~9: pinned `100lvh` demo panels over a persistent fixed demo layer, or a spotlight expand across the row. Many winners omit it and a diffuse climax is legal.
- *deep-dive / audience segment* — CONTINUES QUIET at ~6: per-theme full-bleed long-form, or audience-segmented cards that open in place.
- *rest* — a sponsors or logo wall at ~4: the designed rest before the close, grayscale at rest → color on hover as its only micro-state.
- *close* — ~6: one imperative and decisive channel rows, or a four-tile CTA hub.
- *footer* — ~4: link-column chrome whose designed moment is a wordmark reprise, a newsletter capture, or a live reactive surface.

**The peak law** — verdict REFINED, from the winner evidence. "Exactly one climax" becomes a DISTRIBUTED-ALIVENESS law: momentum spreads across many small carriers rather than being spent in one hero peak. Commit at least one of two carrier channels — (1) PER-TILE LOOPS, most proof tiles running one infinite micro-loop (pulse, typewriter, float, gapless carousel, auto-sort, breathing badge), memoized and isolated; (2) SECTION-SCALE DEVICES, a scroll-driven gradient transition morphing color between sections and/or an interactive footer (`section-scale-momentum`; Sui ships both). On top of the carriers place AT MOST ONE designed peak, made interactive and looping so it replays rather than spends. A diffuse climax with no peak at all is legal and common. The failure to avoid is the DEAD GRID: proof tiles whose only animation is a single-run on-scroll reveal that then holds static, with no section-scale momentum either — the bento-fatigue tile wall. DECIDABLE CHECK, mechanical and not taste: for each proof tile, does it carry any animation that is infinite/looping OR interaction-driven (hover, drag, scroll-scrub) rather than only a one-shot reveal? If ZERO proof tiles do AND the page carries no section-scale momentum device, the aliveness channel is unbuilt — fix before proceeding. The binder physics spans every element class; one universal card hover is the flattening tell. The perf lock is part of the law: every perpetual loop ships memoized (`React.memo`) in its own micro client component and drives continuous or pointer motion through `useMotionValue`/`useTransform`, never `useState` — aliveness that stutters scores worse than a static grid.

Evidence: Anime.js runs ONE designed peak, the pinned demo reel, and it is capped — but it sits over a spine of perpetual per-tile micro-loops (the red-dot period pulse, the clockwork counter) running hero-to-footer, and the peak itself is interactive and looping so it replays rather than spending (winner-verified structure; the loop CSS is observed in a prior winner read, not re-executed this run). Endex carries NO single climax at all — the feature grid carries even, sustained proof — and it took an Awwwards Honorable Mention (2025-03-24, 15/17 jury votes) that way, so the archetype has an award-winning page with zero spectacle peak on record. Sui distributes the aliveness across its module tiles, the expandable industry cards, the scroll-driven gradient transition and the interactive footer, taking SOTD 2026-06-23 at 7.38 (Animations/Transitions 7.40) on the submission's own highlighted captures. The five-machine perpetual-loop set is a corpus-generalized pattern drawn mainly from Anime.js plus internal reference: published Bento 2.0 sources define the trend as exaggerated corner rounding (12–32px) plus container-query self-aware tiles plus subtle alive micro-interaction, so the five machines carry as a strong default rather than as law. Cross-archetype counter-evidence: the restraint line's own anchor, Terminal Industries, caps at one loud mid-page peak plus an optional quiet footer peak — bento's inversion is that it often has no hero wow to be quiet after, because the spectacle was never front-loaded.

## Component index

Generated from `assets/components/manifest.json` — the authority for slots, variants, tokens, deps and `init` signatures, and the only place 11 of the 103 components record facts their file headers omit. Each row is the id plus the opening of its `whenToUse`, clipped: enough to pick, never enough to build. Grep the manifest for the chosen id to get its contract. Forms are the page skeletons (CSS, slots, variants); components are the behaviours that mount into their slots.

**Forms** (8) — page skeletons
- `close-panel` — The funnel's close: one imperative (18ch cap), decisive channel rows, a quiet trust line a full rest below — no media slot exists, so the close cannot become a…
- `divided-capability-strip` — The understanding-layer band between hero and the proof grid: 3-5 capability cells in one row divided by hairline rules (the divide-x tell), capability COPY…
- `feature-card-grid` — The 12-col asymmetric feature grid — cards carry REAL product-UI slices (never icons), spans 4-12 with dense backfill; the bento-fatigue correction.
- `logo-wall` — The restrained proof strip: a static wrapped wall of height-capped, quieted logos (grayscale at rest, colour on hover — the one micro-state the form owns).
- `oversized-wordmark` — The argument-scroll / minimalist footer where the page's ONE deferred <h1> finally lands (Terminal's close): a viewport-height sticky holder with an oversized…
- `pinned-demo-panels` — The specimen-tour peak: N viewport panels of scroll runway under enhancer-pinned copy/demo layers — NATIVE scroll scrubs each panel's cross-fade as a pure…
- `stat-band` — The standalone big-number strip: display-scale tabular values over mono captions, hairline-divided columns that never crowd (8ch floors).
- `swipe-snap-gallery` — The mobile-first image gallery: native scroll-snap track riding OS momentum (zero JS physics), next-cell peek, enhancer-fed snap dots.

**Components** (13) — behaviours
- `ambient-idle` — The third channel — the page breathes at rest: glow, float, shimmer, or pulse at ambient amplitude, paused off-screen and on hidden tabs.
- `border-glow-bloom` — The blurred accent under-glow that lifts a card — breathes up on hover/focus; the blur never animates, only opacity (compositor-clean).
- `conic-border-shine` — The cursor-tracked border light: an accent glow masked to the card's 1px edge follows the pointer.
- `counter-odometer` — Stat/counter roll on scroll-into-view — the markup carries the true final value (visible with no JS), tabular-nums, format-preserving (1,344 · 99.7% · +412 yr).
- `figure-hover` — The default figure response: contained zoom to 1.1 (felt, never a 1-3% twitch) + a companion cue — tint, scrim lift, or caption rise — on hover and…
- `fill-invert-cta` — The universal primary-CTA move: full-token flood + label inversion on hover/focus — fill (direct pole swap) or wipe (a panel rises from the bottom edge).
- `glass-card` — The spatial-organic signature surface: backdrop-blur glass with the inset highlight and concentric nested radii (Doppelrand); opaque fallback keeps text…
- `hard-press-button` — The physical press: hard offset shadow that lifts on hover and collapses on press — 125ms linear, a mechanism not a gesture.
- `live-demo-tile` — The bento DNA 'every tile shows its claim' made executable: the tile's content is a RUNNING canvas demo the builder supplies as a draw function — a working…
- `perpetual-tile-machines` — The five structured content machines that keep a bento grid alive at rest — distinct from ambient-idle's unstructured glow/float/shimmer/pulse.
- `scramble-decode` — Short labels/links/data-chrome decode from charset noise to the true string (entrance once; hover replay variant).
- `section-scale-momentum` — Momentum at SECTION scale — the co-equal channel beside the per-tile loops.
- `spotlight-expand-tile` — The layout-AWARE row expand — not a contained zoom, not a lift: the hovered tile's oversized preview opens through a 12-point clip-path cross across its row…
