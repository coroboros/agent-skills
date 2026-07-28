# Foundations

Cross-cutting technical reference for award-winning web design. Read alongside the chosen archetype reference.

## Tokenization boundary

Code samples in this file (CSS custom properties, animation values, scroll patterns) are illustrative — the *concrete numeric values* belong in the DESIGN.md tokens, not authored ad-hoc in component CSS. Canonical 5 namespaces (`colors`, `typography`, `rounded`, `spacing`, `components`) cover most surface; for motion durations, shadow scales, aspect ratios, viewport heights, container widths, breakpoints, z-index layers, border weights, opacity ramps, and scroll triggers, use the spec-blessed extension namespaces documented in [design-system's extended-tokens reference](https://github.com/coroboros/agent-skills/blob/main/skills/design-system/references/extended-tokens.md). Components bind only to the 8 canonical property tokens (`backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`) — in the DESIGN.md; extension tokens are referenced from prose only. The CSS-side mirror is generated and validated by `/design-system audit-extensions`.

## Stack — lock the craft, key the framework

Lock the craft layer; derive the framework from the archetype; adapt to existing projects; keep hosting orthogonal.

- **Locked universal craft** (every build, every framework): GSAP + CSS scroll-driven animations + View Transitions API + variable fonts + OKLCH. These run identically anywhere. Lenis is the tier norm where the archetype's palette line commits wheel smoothing — never universal: Bento's canon is native scroll, and the archetype line governs (`award-imperatives.md` #3).
- **Framework by archetype**: Astro for content/perf archetypes (Minimalist, Editorial, Corporate-Luxury, Bento) — zero-JS by default is the LCP win; TanStack Start (React on Vite + Nitro) for motion/3D archetypes (Immersive, Experimental, Bold, Spatial-Organic) — React Three Fiber and Motion are native there. Motion (Framer) and R3F belong to the TanStack path only; on Astro, motion is GSAP + CSS scroll-driven inside islands.
- **Existing project's stack wins** — adapt, never migrate. A content archetype whose signature is sustained interactive 3D promotes to the TanStack path (the signature outranks the perf default).
- **Pin** the TanStack Start version — resolve the current release line before scaffolding (`external-truth.md`'s ladder; `stack-facts.md` holds the row and says why it is not carried as a number). Vite-path replacements for `next/*`: fonts via Fontsource / unplugin-fonts, images via vite-imagetools / unpic or a host image loader.
- **Host orthogonal** via Nitro (40+ deploy presets). `/scaffold` is one optional Cloudflare deploy preset, never assumed.

## Typography Systems

### Fluid scales

Eliminate breakpoint-based sizing. Continuous scaling across all viewports:

```css
:root {
  --fs-sm:   clamp(0.8rem, 0.73rem + 0.36vw, 1rem);
  --fs-base: clamp(1rem, 0.91rem + 0.45vw, 1.25rem);
  --fs-lg:   clamp(1.56rem, 1.42rem + 0.73vw, 1.95rem);
  --fs-xl:   clamp(1.95rem, 1.77rem + 0.91vw, 2.44rem);
  --fs-xxl:  clamp(2.44rem, 2.21rem + 1.14vw, 3.05rem);
  --fs-hero: clamp(3.05rem, 2.76rem + 1.43vw, 3.81rem);
}
```

### Variable fonts

Single file containing all weights, widths, styles — real-time animation of `font-variation-settings` on hover and scroll.

**Sans-serif**: PP Neue Montreal, ABC Diatype, Inter (body/fallback only — never the display face), GT Flexa, Fragment
**Serif display**: GT Super, GT Sectra, Editorial New
**Extended/display**: Monument Extended, Sharp Grotesk, Druk Wide

### Font pairing strategies

1. **Contrast**: Serif + sans-serif with dramatically different qualities
2. **Outline + solid**: Outline typefaces mixed with solid weights for visual layering
3. **Weight extremes**: Ultra-thin body (300) with ultra-bold display (800+)
4. **Monospace accents**: Monospace for technical details, metadata, labels
5. **Editorial mixing**: 3+ typefaces in Swiss-inspired layouts

### Kinetic typography

GSAP SplitText is the standard. Executable form — `SplitText.create`, `autoSplit`, `mask: 'lines'`, and the returned-tween `onSplit` that survives a late font swap — is `skeletons.md` §D; licensing and version facts are `stack-facts.md`.

## Color Theory

### OKLCH

Perceptually uniform color manipulation. Eliminates "muddy middle" in gradients:

```css
.gradient { background: linear-gradient(in oklch, oklch(70% 0.15 240), oklch(50% 0.15 340)); }

:root { --brand: oklch(65% 0.2 250); }
.lighter { background: oklch(from var(--brand) calc(l + 0.15) c h); }
.muted   { background: oklch(from var(--brand) l calc(c - 0.08) h); }
```

Derive the neutrals too: surfaces, borders, and shadows carry the brand hue at low chroma (`oklch(from var(--brand) 0.96 0.01 h)` for a surface, shadows tinted with the surface hue). A foreign gray border or a pure-black shadow on a warm page is the mismatch tell — the page has one light, and light has a temperature.

### Dark mode

82% of mobile users prefer dark. Never pure black (#000) or pure white (#FFF):
- Backgrounds: #121212, #1E1E1E, or deep navies (#14213D)
- Text: off-whites (#E0E0E0)
- Design tokens via CSS custom properties for clean light/dark switching

### Dominant color strategies

1. Dark base + single vibrant accent (most common on winners)
2. Monochromatic depth via OKLCH lightness variations
3. Earthy muted pastels (sustainability/wellness brands)
4. Neon micro-glow accents against dark surfaces — authored, never the GitHub-dark default (uniform `#0D1117` + generic cyan/purple glow; see anti-patterns)
5. OKLCH multi-hue gradients replacing flat sRGB

## Layout

### Viewport units

| Unit | What it is | iOS URL-bar toggle |
|------|------------|--------------------|
| `vh`  | Legacy. In iOS = `lvh` (largest) | Too tall when bar shown → content clipped |
| `svh` | 1% of **smallest** viewport | **Constant** — stable for scroll math |
| `lvh` | 1% of **largest** viewport | **Constant** — rarely the right choice |
| `dvh` | 1% of **current** viewport | **Changes** smoothly with the bar |

- Scroll-driven elements (spacers, pinned sections, fold triggers) → `svh`. Stable `document.scrollHeight`.
- Fixed-position full-screen containers → `dvh`. Tracks the visible area smoothly.
- Must-see-now content (hero text, CTA) → `svh`. Always fits the smallest viewport.
- Never use `vh` in new code. Never mix units on related elements.

For cross-browser production gotchas (scroll-restoration traps in Chrome/Firefox/Safari, bfcache style preservation, fail-safe reveal logic, iOS-specific `clientHeight = 0` on first tick), see `production-hardening.md`.

### Broken grids

An asymmetric column ramp (`1fr 2fr 10fr 3fr 3fr …`, eleven-ish uneven tracks) with content spanning arbitrary `grid-column` / `grid-row` ranges and deliberate overlap via `z-index`. The break out of the 12-column default is the point — even tracks read as a template no matter what sits in them.

### CSS Subgrid

Nested elements inherit parent grid tracks — essential for aligned card layouts:

```css
.card-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; }
.card { display: grid; grid-template-rows: subgrid; grid-row: span 3; }
```

### Whitespace tokens

```css
:root {
  --space-s:  clamp(1rem, 0.75rem + 1.25vw, 1.5rem);
  --space-m:  clamp(1.5rem, 1rem + 2.5vw, 3rem);
  --space-l:  clamp(2rem, 1rem + 5vw, 6rem);
  --space-xl: clamp(4rem, 2rem + 8vw, 10rem);
}
section { padding-block: var(--space-xl); }
```

### Full-bleed pattern

```css
.wrapper {
  display: grid;
  grid-template-columns: 1fr min(65ch, 100%) 1fr;
}
.wrapper > * { grid-column: 2; }
.full-bleed { grid-column: 1 / -1; }
```

### Composition variety mandates

A multi-section page that lands every section on the same anchor, the same surface, the same CTA shape, and the same ambition reads as templated even when each section is individually strong. The cure is per-section variety, applied as four independent rules across the page.

- **Composition Anchor diversity** — across all sections, at least **3 different anchor positions** must appear (centered statement, top-left lead, bottom-left over image, bottom-right CTA cluster, left-third + right-two-thirds, off-grid editorial offset, image-as-canvas). Hero must vary away from the AI default of left-text / right-image.
- **Background Mode variation** — pick one per section; vary across the page so no two consecutive sections share the same surface treatment (solid + inline asset, subtle texture/paper/grid, full-bleed image + overlay, editorial side-image, flat color block + detail crop, cinematic tonal gradient, color-blocked diptych).
- **CTA variation** — vary the call-to-action shape at least once across the site. Default pill on every section is templated. Mix in: outline/ghost, underlined inline link, banner-style full-width, oversized headline + tiny hint, CTA as caption.
- **Section size variety** — mix section ambition deliberately across the page. Some large/rich (full-bleed hero, immersive feature stage), some mini/minimalist (single-line statement, tight detail block), some medium editorial. Uniform section heights produce slab-rhythm; mixed ambition produces premium scrollscape.

Apply on multi-section landing pages and product narratives where a default rhythm would otherwise dominate. Not applicable to single-fold portfolios or pure docs. Cross-references: `premium-patterns.md` Hero Architecture options, `anti-patterns.md` predictable symmetric layouts.

### Density bias

Bias toward slightly more whitespace between sections than feels natural. Default AI design under-spaces — a 96px gap between sections that "looks right on the screenshot" reads as cramped on a 13-inch laptop in a real reading session. When uncertain, push section padding one band higher than the dial would suggest (Density 4 → use the band-3 spacing; Density 7 → use the band-6 spacing). The cost of over-spacing is a longer scroll; the cost of under-spacing is a templated rhythm.

## Animation Toolkit

These are the wirings a build reproduces wrong from memory. Each whole-file form, with the failure it closes, is in `skeletons.md` — load the section, not the file. Every version, bundle size, and support number they depend on is in `stack-facts.md`.

| Mechanic | What it is | Skeleton |
|---|---|---|
| GSAP + ScrollTrigger | the pin/scrub choreography engine | §B |
| Lenis | smooth scroll on native `scrollTo`, so `position: sticky` and Intersection Observer keep working (it replaced Locomotive) | §A — with the GSAP ticker wiring |
| GSAP SplitText | line/word/char splitting that survives a late font swap | §D |
| Three.js | the 3D signature, WebGPU path with the WebGL fallback | §E |
| View Transitions API | native page and element morphs, both document scopes | §F |
| IntersectionObserver reveal | the fire-once content reveal that persists | §G |

### CSS Scroll-Driven Animations (off the main thread)

`animation-timeline: view()` / `scroll()` with `animation: <name> linear both` and an `animation-range` — the right tool for *decorative* motion, reversible for free because progress *is* scroll position. The canonical code and the load-bearing details (`linear` deliberate, `both` fill, stagger by range not delay, `view()` vs `scroll(root block)`) are `motion-palette.md`; content reveals never scrub — bound to visibility they re-hide on scroll-up — and route to `skeletons.md` §G. The emerging `animation-trigger` primitive and every support figure: `stack-facts.md`.

### Signature scroll skeletons

Two choreographies cover most signature moments, both GSAP.

- **Sticky-stack** — panels pin and stack as you scroll. `pinSpacing: false` is what makes them share scroll space instead of pushing the page taller; it is the defining detail of the pattern.
- **Horizontal-pan** — vertical scroll drives horizontal travel. `ease: 'none'` with an `end` equal to the travel distance locks the pan to the scrollbar, and the wrapper is pinned while the track moves; pinning the element you animate produces jitter and offset drift (the official GSAP caveat).

Both, with the full pin-gotcha list — `'top top'` and nothing else, one cleanup path, `ScrollTrigger.refresh()` after any late layout move, no nesting inside a parent timeline, `scrub` never sharing a trigger with `toggleActions`, no shipped markers, one sticky per stacking context — are `skeletons.md` §B and §C.

Reach for GSAP only when the signature needs it; default to CSS scroll-driven animations for routine *decorative* motion, and route content reveals to the fire-once IntersectionObserver. No library is mandated and no build-time author step is introduced; GSAP loads at runtime only when a signature moment calls for it.

### Signature easing lexicon

The easing IS the personality. Generic `ease` / `ease-in-out` is the motion equivalent of Inter on an H1.

- `back.out(1.7)` — overshoot-and-settle; entrances with character.
- `elastic.out(1, 0.3)` — springy bounce; playful, Bold / Maximal.
- `expo.out` / `power4.out` — fast-then-glide; cinematic reveals.
- `CustomEase.create('signature', 'M0,0 C0.2,1 0.3,1 1,1')` — a bespoke curve when the brand owns its motion.

CSS-native equivalent, no library — `linear()` interpolates a spring or curve as a CSS string:

```css
:root {
  --ease-spring:   linear(0, 0.13 3%, 0.5 9%, 0.9 18%, 1.04 26%, 0.99 42%, 1);
  --ease-out-expo: linear(0, 0.6 8%, 0.86 16%, 0.96 24%, 1 40%);
}
.card { transition: transform 0.6s var(--ease-spring); }
```

Pin durations and eases to `motion.*` extension tokens; never author easings ad-hoc per component. Linear (constant-velocity) easing stays banned for UI transitions — see anti-patterns; `ease: 'none'` above is the deliberate exception for scrubbed scroll.

Exits run at 60–70% of their entrance duration — leaving is acknowledgment, arriving is the event. Motion direction encodes hierarchy: forward navigation slides one way, back reverses it; siblings share an axis.

### Reduced-motion gate (GSAP)

Wrap every GSAP timeline in `gsap.matchMedia()` so reduced-motion users get the reduced branch and everyone else the full one — set up and torn down automatically on the media-query flip.

```javascript
const mm = gsap.matchMedia();
mm.add('(prefers-reduced-motion: no-preference)', () => {
  const tl = gsap.timeline({ scrollTrigger: { trigger: '.hero', start: 'top top', scrub: 1, pin: true } });
  tl.from('.headline', { yPercent: 20, autoAlpha: 0 });
  return () => tl.kill();   // cleanup runs on flip
});
mm.add('(prefers-reduced-motion: reduce)', () => {
  gsap.set('.headline', { autoAlpha: 1, clearProps: 'all' });
});
```

This is the JS counterpart to the CSS `@media (prefers-reduced-motion)` block in *Accessibility* — both must be present when GSAP drives the signature moment.

## Premium component patterns

Concrete component techniques (Doppelrand nested architecture, Button-in-Button trailing icon, eyebrow tags, hero 2-line iron rule, mobile-collapse mandates, perpetual-animation isolation, magnetic-physics performance lock, backdrop-filter scope, grain-overlay isolation) live in `premium-patterns.md`. Load that reference when component architecture matters — particularly for Corporate Luxury, Spatial Organic, Bento (motion-engine variant), and Bold/Maximal projects. The patterns lift Hierarchy and Spacing audit scores by 1–2 points each and apply across archetypes.

### Micro-interactions

**Inline image typography** (hero signature technique):

Small contextual photos embedded between words at type-height, acting as visual punctuation. The images sit inline with text, match the line height, and use rounded corners. Text never overlaps images — each element occupies its own spatial zone.

```css
.hero-text img.inline-photo {
  display: inline-block;
  height: 1em;
  width: auto;
  aspect-ratio: 3/2;
  object-fit: cover;
  border-radius: 0.2em;
  vertical-align: baseline;
  margin-inline: 0.1em;
}
```

Best for high-Variance archetypes (Editorial, Bold/Maximal, Experimental). Avoid on Minimalist or Corporate Luxury where it competes with whitespace.

**Custom cursors** (creative agency staple): a lerped follower — pointer position read on `pointermove`, the visual eased toward it inside one rAF, written as `transform` only, `aria-hidden`, and disabled under `(hover: none)`. Shipped implementations rather than a re-derivation: `assets/components/custom-contextual-cursor.js`, `magnetic-cursor.js`, `minimal-cursor-signature.js`.

**Magnetic buttons**: Distance from cursor to element center → proportional displacement.

**Hover underlines**: `scaleX(0)` → `scaleX(1)` on `::after`, transform-origin varies by direction.

### Image techniques

**Clip-path reveals**: an `inset()` curtain transitioned from one edge, fired once by IntersectionObserver. Cheap because the clip's parameters are not tracked per input frame — a `clip-path` that chases the pointer repaints every frame instead (`motion-palette.md`, moving windows). Shipped: `assets/components/clip-reveal.js`, `image-curtain.js`.

**Mix-blend-mode**: `difference` on text overlaying images.

### Advanced CSS

**Container queries** for self-aware components: `container-type: inline-size` on the wrapper, `@container (min-width: …)` on the child. A card that reads its own slot beats one that reads the viewport.

**`:has()` for conditional styling** without JS: the count-aware grid (`.grid:has(:nth-child(4):last-child)`), the state-driven root (`:root:has(#dark-mode:checked)`), the sibling dim on a hovered row.

**`@property` for animatable gradients**:

```css
@property --angle { syntax: "<angle>"; inherits: false; initial-value: 0deg; }
.gradient-bg {
  background: linear-gradient(var(--angle), var(--c1), var(--c2));
  animation: rotate 4s ease infinite;
}
@keyframes rotate { 50% { --angle: 180deg; } }
```

### WebGL

**Three.js** for maximum control. **React Three Fiber + Drei** for React. **OGL** for lightweight shaders. The WebGPU renderer is the current path for object counts a WebGL scene cannot hold; it falls back to WebGL2 on its own, and the bootstrap is `skeletons.md` §E. Every revision number, package name, and bundle size for this row and the motion libraries below it: `stack-facts.md` — none of them is stable enough to carry here.

Locked universal layer (every framework): GSAP + CSS scroll-driven + View Transitions + variable fonts + OKLCH; Lenis joins where the archetype's palette line commits wheel smoothing (Bento's canon is native scroll — the archetype line governs). Motion (Framer) and React Three Fiber are React-path (TanStack Start) only — never on Astro paths; see *Stack* above.

### Spring physics — canonical values

Every Framer Motion spring on a premium surface uses the same two numbers. Pin them in `motion.*` extension tokens and reference them everywhere; ad-hoc spring values authored per component betray the system.

```yaml
# DESIGN.md fragment
motion:
  spring-stiffness-default: 100
  spring-damping-default: 20
  spring-stiffness-snappy: 180
  spring-damping-snappy: 18
```

```javascript
// Framer Motion — the canonical premium spring
<motion.div
  animate={{ scale: 1.05 }}
  transition={{ type: 'spring', stiffness: 100, damping: 20 }}
/>

// CSS-side equivalent for elements outside React
:root {
  --ease-spring-out:  cubic-bezier(0.34, 1.56, 0.64, 1);  /* overshoot */
  --ease-out-expo:    cubic-bezier(0.16, 1, 0.3, 1);      /* cinematic */
  --ease-smooth-inout: cubic-bezier(0.25, 0.1, 0.25, 1);  /* default */
}
```

`stiffness: 100, damping: 20` is the weight-and-mass register that reads as "premium" rather than "snappy". Buttons, cards, and modal entries default to this. The snappier variant (`180 / 18`) belongs to active-state feedback (press, drag) where the extra responsiveness is felt as control. Linear easing is banned across the system — see anti-patterns.

## Copy

Judges read the headline before they see the grid — the words are half the design, written in the universe's register, never filled in after.

- **The swap test**: if the H1 pastes cleanly onto a competitor's site, it is not a headline, it is a category label. "Design without limits" fails; "The yard, run by software" (Terminal Industries) passes.
- **Concrete noun + verb beats abstract benefit.** Pull the noun from the product's actual world (the yard, the ledger, the kiln) — abstraction is the default the model reaches for when it hasn't decided what the product is.
- **The subhead does the explaining.** The H1 lands the world in ≤6 words; the subhead earns the claim in ≤20. Inverting that (explanatory H1, poetic subhead) is the amateur order.
- **Numbers only when true** — a real metric beats an adjective; an invented one fails the copy audit (`preflight.md` §6).
- **One register, held.** The DESIGN.md Overview names the copy register; every string on the page speaks it — buttons, empty states, error messages, `alt` text included.
- Sentence case reads more refined than Title Case On Every Header — see anti-patterns Content tells.
- **Scrub via the copy audit, not a generic humanizer.** Site copy is voice-locked diegetic writing; run it against the AI-vocabulary list and the pre-flight copy audit (§6) — a general-purpose tell-scrubber flattens the register it took a universe to build.

## Performance

### GPU compositing

Only animate `transform`, `opacity`, `filter`, `backdrop-filter`. Never `width` / `height` / `top` / `left` — a hover that moves an element `left: 100px` relayouts the page every frame; the same move as `transform: translateX(100px)` never leaves the compositor.

`will-change` only on elements actively animating — blanket `will-change`/`force3D` "just in case" costs memory and repaints. Kill or pause tweens the moment their element leaves the viewport.

### Lazy loading

- `content-visibility: auto` on below-fold sections
- Intersection Observer for images and animation init (the observer shape is `skeletons.md` §G — `disconnect()` or `unobserve()` on first intersection, always)
- Dynamic imports for heavy libraries when the section enters the viewport: `import('gsap').then(…)` inside that observer, so the bundle is fetched on approach rather than on load

### Image optimization

AVIF > WebP > JPEG via `<picture>`. AVIF ~50% smaller than JPEG. Font loading: `font-display: swap` + `<link rel="preload">`. Self-host the files (or the framework's font module) — a Google Fonts `<link>` in production is a third-party request on the critical path and a GDPR exposure.

### Prerendering

```html
<script type="speculationrules">
{ "prerender": [{ "where": { "selector_matches": ".prerender-link" }, "eagerness": "moderate" }] }
</script>
```

### Targets

LCP < 1.5s · CLS < 0.05 · INP < 100ms · ≥55fps sustained · critical path lean, heavy assets streamed — no byte cap, signature fidelity never traded (`award-imperatives.md` #7)

## UX Quality

Rules that directly impact the Usability score (30% of Awwwards judging). Judges test these — missing them tanks scores regardless of visual quality.

### Touch & interaction

```css
/* Eliminate 300ms double-tap delay on all interactive elements */
button, a, [role="button"] { touch-action: manipulation; }

/* Prevent scroll bleed from modals and drawers into page */
.modal, .drawer { overscroll-behavior: contain; }

/* Intentional tap highlight — never rely on browser default */
* { -webkit-tap-highlight-color: transparent; }
button, a { -webkit-tap-highlight-color: rgba(0,0,0,0.05); }
```

Minimum touch targets: 44×44px. Disable text selection during drag operations (`user-select: none`), restore after.

### Safe areas

Full-bleed layouts on notched/dynamic-island devices:

```css
body {
  padding: env(safe-area-inset-top) env(safe-area-inset-right)
           env(safe-area-inset-bottom) env(safe-area-inset-left);
}
```

### Forms

- Never block paste (`onPaste` + `preventDefault` is a usability violation)
- Labels must be clickable (`htmlFor` or wrapping `<label>`)
- Use correct `type` (`email`, `tel`, `url`) and `inputmode` for mobile keyboards
- Submit button stays enabled until the request actually starts
- Display errors inline next to the field; focus first error on submit
- Disable `spellcheck` on emails, codes, and usernames
- Warn before navigation with unsaved changes
- `autocomplete` + meaningful `name` on every input; never `autocomplete="off"` on non-auth fields. Checkbox/radio: label and control share one hit target. Placeholders show a real example and end with `…` — never restate the label.
- Validate on blur, never per keystroke; error text below the field with `min-height: 1lh` reserved so the layout doesn't jump.
- Input states change color, never border-width (width shifts move the layout); the focus ring is an `outline`, not a border swap; input height matches the adjacent button's height; disabled is a full treatment, never opacity alone.

### Typography micro-rules

```css
/* Tabular numbers for aligned columns (prices, stats, tables) */
.numeric { font-variant-numeric: tabular-nums; }

/* Balanced wrapping on headings — no orphaned words */
h1, h2, h3 { text-wrap: balance; }
p { text-wrap: pretty; }
```

Use `…` (U+2026) not `...`. Use curly quotes `"` `"` not straight quotes. Non-breaking spaces for units: `10&nbsp;MB`, `⌘&nbsp;K`.

### State & navigation

- URL must reflect visible state (filters, tabs, pagination, open panels) — judges test deep-linking
- `<a>`/`<Link>` for navigation (Cmd/Ctrl+click must work), `<button>` for actions — never `<div onClick>`
- Destructive actions need confirmation dialog or undo window
- Anchor targets carry `scroll-margin-top` matching the fixed nav height, or the nav eats every anchored heading

### Dark mode

```css
html { color-scheme: dark light; }
```

```html
<meta name="theme-color" content="#121212" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
```

Native `<select>` elements need explicit `background-color` and `color` in dark mode — they don't inherit.

### Animation precision

- Never use `transition: all` — list properties explicitly (`transition: transform 0.3s, opacity 0.3s`)
- Animations must be interruptible (user starts a new action mid-animation → animation redirects)
- Set correct `transform-origin` — default center is wrong for most reveals
- SVG transforms: `transform-box: fill-box; transform-origin: center`

### Performance UX

- Lists with 50+ items: virtualize (use `virtua`, or `content-visibility: auto` for simpler cases)
- `<link rel="preconnect">` for CDN and asset domains
- Critical fonts: `<link rel="preload" as="font" crossorigin>` with `font-display: swap`
- Above-fold images: `fetchpriority="high"`. Below-fold: `loading="lazy"`
- All `<img>` must have explicit `width` and `height` to prevent CLS

### Anti-patterns (flag these)

- `user-scalable=no` or `maximum-scale=1` on viewport meta — accessibility violation
- `outline-none` / `outline: 0` without `:focus-visible` replacement
- Inline `onClick` navigation without `<a>` — breaks Cmd+click, right-click, screen readers
- Images without dimensions — causes CLS
- Hardcoded date/number formats — use `Intl.DateTimeFormat` and `Intl.NumberFormat`

## Accessibility

### prefers-reduced-motion

Zero the durations — never kill transforms. A `transform: none !important` wildcard destroys transform-carried *state* (the nav's `translateY(-100%)` hidden position, an open panel's resting offset); reduced motion strips transitions and keeps state, so everything still flips, it just snaps (navigation-patterns.md, interaction-signatures.md):

```css
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
```

For JS: detect preference, disable smooth scroll, reduce particles, simplify transitions.

### Non-negotiables

- Skip links, `:focus-visible` styling, semantic HTML under creative layouts
- `aria-hidden="true"` on custom cursors and decorative elements
- `aria-label` on parent of split-character text animations
- WCAG 4.5:1 contrast (glassmorphism often fails — test explicitly)
- European Accessibility Act (effective mid-2025) — overlay widgets are not a substitute

## Studios Reference

| Studio | Signature | Key wins |
|--------|-----------|----------|
| **Locomotive** (Montreal) | Smooth scroll pioneers, Lenis/GSAP | Agency of Year 7x consecutive |
| **Active Theory** (LA) | Cinematic WebGL, pitch-black canvases | Emmy nominations, LCP ~1.3s despite shaders |
| **Resn** (Wellington) | Gooey interactions, game design | 60 SOTD, 11 SOTM, 2 SOTY |
| **Immersive Garden** (Paris) | Luxury brand immersion | Agency of Year 2025, Louis Vuitton |
| **Cuberto** | Sharp micro-interactions, custom cursors | Consistent SOTD |

**Meta-pattern**: Custom tooling, performance as design constraint from day one, no design/dev handoff model, intentional award strategy from project kickoff.
