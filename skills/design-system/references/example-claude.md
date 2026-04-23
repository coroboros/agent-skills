---
version: alpha
name: Parchment Press
description: Editorial archetype, warm literary palette inspired by Claude's brand language — parchment canvas, ink headlines, terracotta accent, custom serif at weight 500.
colors:
  primary: "#1F1E1B"
  secondary: "#5e5d59"
  tertiary: "#a84828"
  neutral: "#f5f4ed"
  surface: "#f5f4ed"
  surface-container: "#eeede4"
  surface-container-high: "#e4e2d5"
  on-surface: "#1F1E1B"
  on-surface-variant: "#5e5d59"
  on-tertiary: "#ffffff"
  tertiary-container: "#f5d4c4"
  on-tertiary-container: "#6a2a15"
  outline: "#bfbdae"
  outline-variant: "#d7d5c7"
  error: "#a5281a"
  on-error: "#ffffff"
typography:
  display:
    fontFamily: "Copernicus, Georgia, serif"
    fontSize: 72px
    fontWeight: 500
    lineHeight: 1.05
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: "Copernicus, Georgia, serif"
    fontSize: 44px
    fontWeight: 500
    lineHeight: 1.1
    letterSpacing: -0.015em
  headline-md:
    fontFamily: "Copernicus, Georgia, serif"
    fontSize: 32px
    fontWeight: 500
    lineHeight: 1.2
  body-lg:
    fontFamily: "Styrene B, -apple-system, sans-serif"
    fontSize: 18px
    fontWeight: 400
    lineHeight: 1.6
  body-md:
    fontFamily: "Styrene B, -apple-system, sans-serif"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
  body-sm:
    fontFamily: "Styrene B, -apple-system, sans-serif"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.5
  label-sm:
    fontFamily: "Styrene B, -apple-system, sans-serif"
    fontSize: 12px
    fontWeight: 500
    lineHeight: 1
    letterSpacing: 0.08em
rounded:
  none: 0px
  sm: 4px
  md: 8px
  lg: 12px
  full: 9999px
spacing:
  unit: 8px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 32px
  xl: 64px
  gutter: 24px
  page-padding: 24px
components:
  button-primary:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.on-tertiary}"
    typography: "{typography.label-sm}"
    rounded: "{rounded.sm}"
    padding: 14px 24px
    height: 48px
  button-primary-hover:
    backgroundColor: "{colors.on-tertiary-container}"
  button-ghost:
    backgroundColor: transparent
    textColor: "{colors.primary}"
    typography: "{typography.label-sm}"
    rounded: "{rounded.sm}"
    padding: 14px 24px
    height: 48px
  button-ghost-hover:
    backgroundColor: "{colors.surface-container}"
  card:
    backgroundColor: "{colors.surface-container}"
    textColor: "{colors.primary}"
    rounded: "{rounded.md}"
    padding: 24px
  card-elevated:
    backgroundColor: "{colors.surface-container-high}"
    textColor: "{colors.primary}"
    rounded: "{rounded.md}"
    padding: 32px
  input-field:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.primary}"
    typography: "{typography.body-md}"
    rounded: "{rounded.sm}"
    padding: 12px 16px
    height: 44px
  chip:
    backgroundColor: "{colors.tertiary-container}"
    textColor: "{colors.on-tertiary-container}"
    typography: "{typography.label-sm}"
    rounded: "{rounded.full}"
    padding: 6px 12px
  chip-hover:
    backgroundColor: "{colors.surface-container-high}"
  nav-link:
    textColor: "{colors.on-surface-variant}"
    typography: "{typography.body-md}"
  nav-link-active:
    textColor: "{colors.primary}"
---

## Overview

A literary salon reimagined as a product page. The canvas is warm parchment (#f5f4ed), headlines are set in a custom serif at weight 500 — no heavier — and a single terracotta accent drives every call-to-action. Reading the page should feel closer to a book than a dashboard.

**Atmosphere**: Density 3/10 (gallery airy, generous whitespace) · Variance 4/10 (asymmetric where it earns its keep, predictable elsewhere) · Motion 3/10 (opacity-only reveals, no parallax, no WebGL).

**Visual DNA**: contained width, sharp framing, rigid underlying grid that tolerates occasional indulgences (pull quotes, marginalia, drop caps).

## Colors

The palette pairs high-contrast ink with a single evocative accent. Backgrounds are never pure white — the warm limestone foundation sets the literary tone.

- **Primary — Deep Ink (#1F1E1B)**: headlines, body text, focus rings. The darkest value in the system; used wherever legibility is paramount.
- **Secondary — Olive Gray (#5e5d59)**: secondary body text, metadata, captions. A warm medium-dark that never competes with primary.
- **Tertiary — Terracotta (#a84828)**: the sole interaction color. Primary CTAs, active link states, critical accents. One signature color beats five competing ones; the deeper tone gives white text WCAG AA contrast on the button surface.
- **Neutral — Parchment (#f5f4ed)**: the page foundation. Warmer than pure white; softens every surface above it.
- **Surface hierarchy**: Parchment (page) → `surface-container` (cards) → `surface-container-high` (elevated/modals). Light-to-dark progression creates depth without shadows.

## Typography

The type system pairs a custom serif with a neutral humanist sans. Serif weight is capped at 500 — heavier feels heavy-handed against the warm palette.

- **Display and headlines**: Copernicus (or Georgia fallback) at weight 500 with negative letter spacing (`-0.02em` at display, `-0.015em` at h1). The serif does the emotional work; weight 500 keeps the voice calm.
- **Body**: Styrene B (or system sans fallback) at 16px regular, line-height 1.6 for long-form readability.
- **Labels**: Same sans at 12px, weight 500, uppercase with `0.08em` letter spacing. Reserved for metadata, breadcrumbs, and button text.

## Layout

Contained width (max 1200px) with generous page padding (`{spacing.page-padding}`) that grows to `{spacing.xl}` at viewport widths above 1200px. An 8px base scale governs all spacing.

- **Grid**: 12-column with 24px gutters on desktop, collapses to single-column at 720px
- **Section rhythm**: `{spacing.xl}` (64px) between major sections, `{spacing.lg}` (32px) between related blocks, `{spacing.md}` (16px) inside components
- **Responsive breakpoints**: `sm` 640px · `md` 768px · `lg` 1024px · `xl` 1280px. Touch targets ≥ 44×44px everywhere
- **Asymmetric moments**: pull quotes break the right margin; chapter numbers sit in the left gutter. Used sparingly — one per screen maximum

## Elevation & Depth

Depth is conveyed through tonal layering, not shadows. The warm palette makes shadows feel heavy-handed; light-to-dark surface progression does the work.

- **Base**: Parchment (`{colors.neutral}`) with a subtle paper-grain overlay (`background-image: url(...grain.svg); opacity: 0.04`)
- **Cards**: `{colors.surface-container}` — half a step darker than the base
- **Elevated / modals**: `{colors.surface-container-high}` — another half step. A 1px `{colors.outline-variant}` border, never a shadow
- **Focus rings**: 2px `{colors.tertiary}` offset 2px from the element — announces interactivity without visual weight

## Shapes

Restrained curvature. Sharpness matches the editorial voice; pills are reserved for chips and tags.

- **Cards and inputs**: `{rounded.sm}` (4px) — subtle softening, not decorative
- **Buttons**: `{rounded.sm}` (4px) — matches cards; the serif voice rejects pill buttons
- **Chips and tags**: `{rounded.full}` — signals "this is a label, not an action"
- **Images**: no rounding — photos are treated as editorial plates, not UI chrome

## Components

### Buttons

Primary actions use Terracotta on Parchment with the `label-sm` typography token. Hover darkens the fill to `{colors.on-tertiary-container}`. Ghost buttons use the same typography and padding but transparent background with primary text — hover reveals a `surface-container` fill. Height is fixed at 48px for both variants; horizontal padding is 24px.

### Cards

Base cards use `{colors.surface-container}` with 24px padding and `{rounded.md}`. Elevated cards (used for feature highlights and modals) bump to `{colors.surface-container-high}` with 32px padding. Never combine a card with a shadow — the surface tint is the elevation signal.

### Inputs

44px height, 12px vertical padding, 16px horizontal. Focus state swaps the default `{colors.outline-variant}` border for `{colors.tertiary}` plus a 2px offset ring. No filled-background variant — always transparent over Parchment.

### Navigation

Top nav uses `nav-link` tokens. Active link states swap secondary to primary color; no underline, no background pill. The active state is a typographic weight shift, not a chrome addition.

### Chips

Always pill-shaped (`rounded.full`). Used for tags, filters, and categories. Active filter chips invert — `{colors.tertiary}` background with `{colors.on-tertiary}` text.

## Do's and Don'ts

- **Do** keep Terracotta exclusive to primary CTAs, active link states, and focus rings — at most one Terracotta element per viewport
- **Do** cap serif weight at 500 — Copernicus at 600+ fights the warm palette
- **Do** use surface tint progression for elevation (Parchment → container → container-high) — never add shadows on a parchment background
- **Do** run `npx @google/design.md lint DESIGN.md` before committing — catch broken token references and contrast violations before review
- **Don't** use pure white (`#ffffff`) as a background — the Parchment base is part of the brand; pure white breaks the warmth
- **Don't** use shadows for elevation — surface color does the work
- **Don't** use more than one font weight per typography role — serif stays at 500, sans stays at 400 for body
- **Don't** introduce a second accent color — if you need a secondary emphasis, use weight, scale, or whitespace, not color
- **Don't** round buttons beyond `rounded.sm` (4px) — pill buttons clash with the editorial voice
