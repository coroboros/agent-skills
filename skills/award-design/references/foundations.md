# Foundations

Cross-cutting technical reference for award-winning web design. Read alongside the chosen archetype reference.

## Tokenization boundary

Code samples in this file (CSS custom properties, animation values, scroll patterns) are illustrative — the *concrete numeric values* belong in tokens (the inline token block, or a DESIGN.md when one exists), not authored ad-hoc in component CSS. Canonical 5 namespaces (`colors`, `typography`, `rounded`, `spacing`, `components`) cover most surface; for motion durations, shadow scales, aspect ratios, viewport heights, container widths, breakpoints, z-index layers, border weights, opacity ramps, and scroll triggers, use the spec-blessed extension namespaces documented in [design-system's extended-tokens reference](https://github.com/coroboros/agent-skills/blob/main/skills/design-system/references/extended-tokens.md). Components bind only to the 8 canonical property tokens (`backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`) — in the inline block or a DESIGN.md; extension tokens are referenced from prose only. The CSS-side mirror is generated and validated by `/design-system audit-extensions`.

## Typography Systems

### Fluid scales

Eliminate breakpoint-based sizing. Seamless scaling across all viewports:

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

**Sans-serif**: PP Neue Montreal, ABC Diatype, Inter, GT Flexa, Fragment
**Serif display**: GT Super, GT Sectra, Editorial New
**Extended/display**: Monument Extended, Sharp Grotesk, Druk Wide

### Font pairing strategies

1. **Contrast**: Serif + sans-serif with dramatically different qualities
2. **Outline + solid**: Outline typefaces mixed with solid weights for visual layering
3. **Weight extremes**: Ultra-thin body (300) with ultra-bold display (800+)
4. **Monospace accents**: Monospace for technical details, metadata, labels
5. **Editorial mixing**: 3+ typefaces in Swiss-inspired layouts

### Kinetic typography

GSAP SplitText (free since Webflow acquisition) — the standard:

```javascript
SplitText.create(".headline", {
  type: "lines, words",
  mask: "lines",
  autoSplit: true,
  onSplit(self) {
    return gsap.from(self.words, {
      y: 100, autoAlpha: 0, stagger: 0.05,
      duration: 1, ease: "power3.out",
      scrollTrigger: { trigger: self.elements[0], start: "top 80%" }
    });
  }
});
```

## Color Theory

### OKLCH

Perceptually uniform color manipulation. Eliminates "muddy middle" in gradients:

```css
.gradient { background: linear-gradient(in oklch, oklch(70% 0.15 240), oklch(50% 0.15 340)); }

:root { --brand: oklch(65% 0.2 250); }
.lighter { background: oklch(from var(--brand) calc(l + 0.15) c h); }
.muted   { background: oklch(from var(--brand) l calc(c - 0.08) h); }
```

### Dark mode

82% of mobile users prefer dark. Never pure black (#000) or pure white (#FFF):
- Backgrounds: #121212, #1E1E1E, or deep navies (#14213D)
- Text: off-whites (#E0E0E0)
- Design tokens via CSS custom properties for seamless light/dark switching

### Dominant color strategies

1. Dark base + single vibrant accent (most common on winners)
2. Monochromatic depth via OKLCH lightness variations
3. Earthy muted pastels (sustainability/wellness brands)
4. Neon micro-glow accents against dark surfaces
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

```css
.broken-grid {
  display: grid;
  grid-template-columns: 1fr 2fr 10fr 3fr 3fr 3fr 3fr 3fr 6fr 6fr 3fr;
}
.hero-image { grid-column: 3/9; grid-row: 2/7; }
.overlay-text { grid-column: 4/11; grid-row: 4/6; z-index: 2; }
```

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
- **Section size variety** — mix section ambition deliberately across the page. Some large/rich (full-bleed hero, immersive showcase), some mini/minimalist (single-line statement, tight detail block), some medium editorial. Uniform section heights produce slab-rhythm; mixed ambition produces premium scrollscape.

Apply on multi-section landing pages and product narratives where a default rhythm would otherwise dominate. Not applicable to single-fold portfolios or pure docs. Cross-references: `premium-patterns.md` Hero Architecture options, `anti-patterns.md` predictable symmetric layouts.

### Density bias

Bias toward slightly more whitespace between sections than feels natural. Default AI design under-spaces — a 96px gap between sections that "looks right on the screenshot" reads as cramped on a 13-inch laptop in a real reading session. When uncertain, push section padding one band higher than the dial would suggest (Density 4 → use the band-3 spacing; Density 7 → use the band-6 spacing). The cost of over-spacing is a longer scroll; the cost of under-spacing is a templated rhythm.

## Animation Toolkit

### GSAP + ScrollTrigger (industry standard)

```javascript
const tl = gsap.timeline({
  scrollTrigger: {
    trigger: '.section', start: 'top top', end: '+=1000',
    scrub: 1, pin: true
  }
});
tl.to('.title', { opacity: 1, y: 0 })
  .to('.image', { scale: 1.2 })
  .to('.text', { opacity: 1 });
```

### Lenis (~2KB, smooth scrolling)

Replaced Locomotive Scroll. Uses native `scrollTo`, preserves `position: sticky` and Intersection Observer:

```javascript
const lenis = new Lenis({ autoRaf: true });
lenis.on('scroll', ScrollTrigger.update);
gsap.ticker.add((time) => lenis.raf(time * 1000));
gsap.ticker.lagSmoothing(0);
```

### View Transitions API (native page transitions)

Cross-document transitions:

```css
@view-transition { navigation: auto; }
```

Named element morph (thumbnail → full hero):

```css
.thumbnail { view-transition-name: product-hero; }
.full-image { view-transition-name: product-hero; }
```

Scoped transitions (Chrome 140+), React `<ViewTransition />` integration.

### CSS Scroll-Driven Animations (off main thread, guaranteed 60fps)

```css
.card {
  animation: fade-in linear forwards;
  animation-timeline: view();
  animation-range: entry 0% entry 100%;
}
@keyframes fade-in {
  from { opacity: 0; transform: translateY(50px); }
  to { opacity: 1; transform: translateY(0); }
}
```

`animation-trigger` (Chrome 145) enables scroll-triggered time-based animations.

### Signature scroll skeletons

Two scroll choreographies cover most signature moments. Both are GSAP — reach for it only when the signature needs it; default to CSS Scroll-Driven Animations (above) for routine reveals. No library is mandated and no build-time `npx` step is introduced; GSAP loads at runtime only when a signature moment calls for it.

**Sticky-stack** (panels pin and stack as you scroll):

```javascript
ScrollTrigger.create({
  trigger: '.panel',
  start: 'top top',          // pin the moment its top hits the viewport top
  end: '+=100%',
  pin: true,
  pinSpacing: false,         // stacked panels share scroll space — no taller page
});
```

`pinSpacing: false` is what makes panels stack instead of pushing the page taller — the defining detail of the pattern.

**Horizontal-pan** (vertical scroll drives horizontal travel):

```javascript
gsap.to('.track', {
  x: () => -(track.scrollWidth - innerWidth),
  ease: 'none',              // 1:1 with scroll, never an eased curve
  scrollTrigger: {
    trigger: '.track',
    pin: true,
    scrub: 1,
    end: () => '+=' + (track.scrollWidth - innerWidth),  // distance == travel
  },
});
```

`ease: 'none'` with an `end` equal to the travel distance keeps the pan locked to the scrollbar.

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

**Custom cursors** (creative agency staple):

```javascript
const lerp = (a, b, n) => (1 - n) * a + n * b;
let mouseX = 0, mouseY = 0, cursorX = 0, cursorY = 0;
document.addEventListener('mousemove', (e) => { mouseX = e.clientX; mouseY = e.clientY; });
function animate() {
  cursorX = lerp(cursorX, mouseX, 0.15);
  cursorY = lerp(cursorY, mouseY, 0.15);
  cursor.style.transform = `translate(${cursorX}px, ${cursorY}px)`;
  requestAnimationFrame(animate);
}
```

**Magnetic buttons**: Distance from cursor to element center → proportional displacement.

**Hover underlines**: `scaleX(0)` → `scaleX(1)` on `::after`, transform-origin varies by direction.

### Image techniques

**Clip-path reveals** (hardware-accelerated):

```css
.image-reveal {
  clip-path: inset(0 100% 0 0);
  transition: clip-path 0.8s cubic-bezier(0.77, 0, 0.175, 1);
}
.image-reveal.visible { clip-path: inset(0 0 0 0); }
```

**Mix-blend-mode**: `difference` on text overlaying images.

### Advanced CSS

**Container queries** for self-aware components:

```css
.card-container { container-type: inline-size; }
@container (min-width: 400px) { .card { display: flex; gap: 1rem; } }
```

**`:has()` for conditional styling** without JS:

```css
.grid:has(:nth-child(4):last-child) { grid-template-columns: repeat(2, 1fr); }
:root:has(#dark-mode:checked) { color-scheme: dark; --bg: #111; }
```

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

**Three.js** for maximum control (~150KB). **React Three Fiber + Drei** for React. **OGL** (29KB) for lightweight shaders. **WebGPU** (Three.js r171+): 200K objects at 60fps vs 15K at 15fps with WebGL.

| Library | Size | Best for |
|---------|------|----------|
| GSAP | ~23KB | Complex timelines, scroll |
| Motion (Framer) | 34KB / 4.6KB lazy | React UI transitions |
| Lenis | ~2KB | Smooth scrolling |
| Locomotive v5 | 9.4KB | Parallax + detection |
| Motion One | 3.8KB | Lightweight vanilla |

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

## Performance

### GPU compositing

Only animate: `transform`, `opacity`, `filter`, `backdrop-filter`:

```css
/* Never */ .box:hover { width: 200px; left: 100px; }
/* Always */ .box:hover { transform: translateX(100px) scale(1.05); }
```

### Lazy loading

- `content-visibility: auto` on below-fold sections
- Intersection Observer for images and animation init
- Dynamic imports for heavy libraries when section enters viewport

```javascript
const observer = new IntersectionObserver(([entry]) => {
  if (entry.isIntersecting) {
    import('gsap').then(({ gsap }) => { /* init */ });
    observer.disconnect();
  }
});
```

### Image optimization

AVIF > WebP > JPEG via `<picture>`. AVIF ~50% smaller than JPEG. Font loading: `font-display: swap` + `<link rel="preload">`.

### Prerendering

```html
<script type="speculationrules">
{ "prerender": [{ "where": { "selector_matches": ".prerender-link" }, "eagerness": "moderate" }] }
</script>
```

### Targets

LCP < 1.5s · CLS < 0.05 · INP < 100ms · Total weight < 3MB · 60fps sustained

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

Replace motion with opacity — never remove all animation:

```css
@media (prefers-reduced-motion: reduce) {
  * { transition: opacity 0.2s ease !important; transform: none !important; animation-duration: 0.01ms !important; }
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
