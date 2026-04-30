# Extended tokens — beyond the canonical five

The Google spec defines five token groups (`colors`, `typography`, `rounded`, `spacing`, `components`) and eight component property tokens (`backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`). Award-grade work needs more — motion durations, shadow scales, aspect ratios, viewport heights, container widths, breakpoints, z-index layers, border weights, opacity ramps, scroll triggers.

The spec anticipates this. `references/design-md-spec.md:141-176` documents top-level **custom YAML namespaces** as a first-class extension mechanism: `motion:` and `breakpoints:` are listed as worked examples; `z-index:` and `elevation-scale:` are named in the rules. The Google CLI **preserves** these namespaces (the linter ignores them, the YAML parser reads them) but does not validate references into them. `/design-system audit-extensions` closes that gap.

## Why this convention exists

Without a shared boundary, agents reinvent it — usually wrongly. A field deployment surfaced this empirically: 73 errors and 84 warnings on the first lint pass when the agent extended the YAML *and* re-bound 27 components to extension tokens via non-canonical property names (`modal.shadow: "{shadows.lifted}"`). Two fixes tangled into one failure. The extension namespaces were fine. The component bindings were not.

This convention separates the two:

- Top-level custom namespaces are spec-blessed and lint-clean.
- Components MUST stay within the closed set of 8 canonical property tokens. Extension tokens are referenced from prose only — never from `components:` keys or values.

## Curated namespace list

The ten namespaces below cover award-grade work end-to-end. The list is curated, not exhaustive — the spec permits any non-conflicting custom namespace.

```yaml
motion:
  duration-instant: 0ms
  duration-micro: 150ms
  duration-hover: 250ms
  duration-reveal-fast: 600ms
  duration-reveal: 800ms
  duration-reveal-slow: 1200ms
  duration-image-zoom: 1600ms
  ease-standard: cubic-bezier(0.16, 1, 0.3, 1)
  ease-enter: cubic-bezier(0, 0, 0.2, 1)
  ease-exit: cubic-bezier(0.4, 0, 1, 1)

shadows:
  none: none
  whisper: 0 1px 0 0 rgb(0 0 0 / 0.04)
  lifted: 0 20px 40px -16px rgb(0 0 0 / 0.08)
  cinematic: 0 40px 80px -32px rgb(0 0 0 / 0.15)

aspectRatios:
  square: 1 / 1
  listing: 3 / 2
  banner: 16 / 9
  portrait: 3 / 4
  cinema: 21 / 9

heights:
  hero: 100svh
  banner-desktop: 70svh
  banner-mobile: 50svh
  nav-desktop: 72px
  nav-mobile: 56px
  button: 48px
  input-touch: 44px

containers:
  wide: 1440px
  content: 1200px
  reading: 720px
  form: 500px

breakpoints:
  sm: 640px
  md: 768px
  lg: 1024px
  xl: 1280px

zIndex:
  base: 0
  raised: 10
  nav-sticky: 50
  dropdown: 60
  drawer: 70
  modal: 80
  lightbox: 90
  toast: 100

borderWidths:
  hairline: 1px
  hairline-strong: 2px

opacity:
  hairline: 0.08
  overlay-soft: 0.40
  overlay-modal: 0.70
  overlay-lightbox: 0.92

scrollTriggers:
  nav-backdrop: 80px
  reveal-fold: 100vh
```

Each namespace solves a recurring drift problem at award-grade register:

- **`motion`** — durations and easings repeated across components silently desync. One canonical curve, four to seven durations, all named.
- **`shadows`** — beyond the spec's silent treatment of elevation. Tone the shadow to the brand register (whisper for editorial, cinematic for immersive).
- **`aspectRatios`** — image and video grids; CSS `aspect-ratio` declarations multiply otherwise.
- **`heights`** — full-bleed heroes, sticky navs, banners, touch targets. Viewport units (`svh`, `lvh`, `dvh`) belong here, not scattered.
- **`containers`** — page widths and reading measures. One per editorial role.
- **`breakpoints`** — the spec folds these into Layout prose; tokens make them tooling-addressable.
- **`zIndex`** — layering hierarchy; arithmetic on raw numbers is an anti-pattern.
- **`borderWidths`** — hairline rules and accent strokes; rare but worth a token.
- **`opacity`** — overlay ramps, tonal washes; the difference between 0.7 and 0.85 is a brand call.
- **`scrollTriggers`** — pixel offsets that activate scroll-driven UI (navbar backdrop swap, reveal folds). Magic numbers in JS desync from CSS otherwise.

## Rules

1. **Top-level YAML namespaces, never nested inside `components:`.** The spec's "map-of-strings convention" (line 175) means each namespace value is a flat map. Two-level nesting (e.g. `motion: { durations: { ... }, easings: { ... } }`) breaks the spec's reference grammar — token paths are dot-delimited, agents resolve `motion.duration-reveal-slow`, not `motion.durations.reveal-slow`.

2. Components bind ONLY to the 8 canonical property tokens. This is the closed set: `backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`. Anything else (e.g. `shadow`, `motion`, `aspect`) is rejected by the lint as an unknown property — that is the field-tested failure mode and the reason this convention exists.

3. **Reference extension tokens from prose, not from `components:`.** Prose can name them by canonical path:
   > "Hero reveals on scroll using `{motion.duration-reveal-slow}` with `{motion.ease-standard}`. Modal scrim sits at `{opacity.overlay-modal}` over the listing image at `{aspectRatios.listing}`."

   Wrap in braces to mirror the spec's reference syntax — agents read both forms (`{motion.x}` and bare `motion.x`); braces make grep-ability tighter.

4. **Document namespace intent in Overview or Do's and Don'ts.** Per spec line 176: maintainers shouldn't have to guess whether a custom namespace is intentional or drift.

5. **`globals.css` `@theme` mirrors YAML 1:1.** The CSS layer is downstream — generated by `/design-system export tailwind` (preferred) or hand-mirrored. Never authored independently. `/design-system audit-extensions` enforces this.

## Tailwind v4 `@theme` mirror

The 1:1 token-name → CSS-custom-property mapping. Tailwind v4 consumes `@theme` blocks as runtime CSS custom properties; the prefix is fixed by Tailwind for native utilities, free-form for custom namespaces.

| YAML namespace | CSS prefix | Example |
|----------------|------------|---------|
| `motion.duration-<n>` | `--duration-<n>` | `--duration-reveal-slow: 1200ms` |
| `motion.ease-<n>` | `--ease-<n>` | `--ease-standard: cubic-bezier(...)` |
| `shadows.<n>` | `--shadow-<n>` | `--shadow-lifted: ...` |
| `aspectRatios.<n>` | `--aspect-<n>` | `--aspect-listing: 3 / 2` |
| `heights.<n>` | `--height-<n>` | `--height-hero: 100svh` |
| `containers.<n>` | `--container-<n>` | `--container-wide: 1440px` |
| `breakpoints.<n>` | `--breakpoint-<n>` | `--breakpoint-md: 768px` |
| `zIndex.<n>` | `--z-<n>` | `--z-modal: 80` |
| `borderWidths.<n>` | `--border-<n>` | `--border-hairline: 1px` |
| `opacity.<n>` | `--opacity-<n>` | `--opacity-overlay-modal: 0.70` |
| `scrollTriggers.<n>` | `--scroll-<n>` | `--scroll-nav-backdrop: 80px` |

Tailwind v4 then exposes utilities derived from these prefixes (`shadow-lifted`, `aspect-listing`, `z-modal`, etc.) without further config.

## Anti-patterns

- **Components bound to extensions.** `modal.shadow: "{shadows.lifted}"` — `shadow` is not in the 8. Lint rejects, errors cascade. Solution: drop the `shadow` line from `modal:`; describe the modal's shadow in Components prose using `{shadows.lifted}`. The shadow ships via `globals.css` and a class on the modal element.
- **Values authored only in `globals.css`.** Drift risk: prose names `motion.duration-reveal-slow`, CSS only defines `--duration-reveal`, agent renders `0s`. DESIGN.md is the source of truth; CSS is the mirror.
- **Nested namespace structures.** `motion: { durations: { ... }, easings: { ... } }` breaks the map-of-strings convention. Use flat keys: `duration-reveal-slow`, `ease-standard`.
- **Custom names that shadow the canonical 5.** `colors:` is reserved; pick a different namespace (`palette-extended:` if you really need a sibling). Per spec line 174.
- **One-off magic numbers in JSX/CSS.** `transition-duration: 1200ms` written inline contradicts the namespace's purpose. Use `var(--duration-reveal-slow)` or the Tailwind utility.

## Verification

After authoring or editing extensions:

1. `/design-system audit DESIGN.md` — Google CLI lint. Must exit 0. Extensions are preserved-but-unvalidated; the lint fails only when components reference unknown properties or canonical tokens are broken.
2. `/design-system export tailwind DESIGN.md > src/app/globals.css` (or merge into the existing `@theme` block) — generates the mirror.
3. `/design-system audit-extensions DESIGN.md` — bidirectional check between YAML extensions, prose references, and the CSS mirror. Must exit 0.

The full pre-ship gate: both audits clean.

## Worked example

A minimal extension block in DESIGN.md, lint-clean and audit-clean:

```yaml
---
version: alpha
name: Editorial Heritage
description: Editorial archetype with extension namespaces — illustrative fixture.
colors:
  primary: "#1a1c1e"
  surface: "#f7f5f1"
  on-surface: "#1a1c1e"
  tertiary: "#c9a071"
typography:
  display:
    fontFamily: "Editorial Serif, Georgia, serif"
    fontSize: 88px
    fontWeight: 400
    lineHeight: 1
    letterSpacing: -0.02em
rounded:
  none: 0px
  sm: 2px
  md: 4px
spacing:
  unit: 8px
  sm: 8px
  md: 16px
  lg: 32px
components:
  modal:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.md}"
    padding: 32px
motion:
  duration-reveal-slow: 1200ms
  ease-standard: cubic-bezier(0.16, 1, 0.3, 1)
shadows:
  whisper: 0 1px 0 0 rgb(28 26 22 / 0.08)
  lifted: 0 20px 40px -16px rgb(28 26 22 / 0.08)
aspectRatios:
  listing: 3 / 2
heights:
  hero: 100svh
  nav-desktop: 72px
zIndex:
  modal: 80
opacity:
  overlay-modal: 0.70
---
```

Components bind to canonical tokens only (no `shadow:` line on `modal:`). Prose names extensions:

```markdown
## Elevation & Depth

Modals lift on `{shadows.lifted}` — a 20px-blur warm shadow that respects the parchment surface. The scrim layers at `{opacity.overlay-modal}` over `{colors.primary}`. Hero listings sit at `{aspectRatios.listing}` (3:2) and reveal on scroll with `{motion.duration-reveal-slow}` paced by `{motion.ease-standard}`.
```

The mirrored `src/app/globals.css`:

```css
@import "tailwindcss";

@theme {
  --color-primary: #1a1c1e;
  --color-surface: #f7f5f1;
  --color-on-surface: #1a1c1e;
  --color-tertiary: #c9a071;

  --duration-reveal-slow: 1200ms;
  --ease-standard: cubic-bezier(0.16, 1, 0.3, 1);

  --shadow-whisper: 0 1px 0 0 rgb(28 26 22 / 0.08);
  --shadow-lifted: 0 20px 40px -16px rgb(28 26 22 / 0.08);

  --aspect-listing: 3 / 2;

  --height-hero: 100svh;
  --height-nav-desktop: 72px;

  --z-modal: 80;

  --opacity-overlay-modal: 0.70;
}
```

DESIGN.md says `{motion.duration-reveal-slow}` in prose; the modal component carries a class that reads `var(--duration-reveal-slow)` in CSS. One mental mapping, two artifacts, zero drift.
