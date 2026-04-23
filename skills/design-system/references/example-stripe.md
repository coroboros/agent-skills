---
version: alpha
name: Precision Gradient
description: Minimalist SaaS archetype with a signature iridescent gradient — cool neutrals, Inter at fine-tuned weights, a single gradient moment, pixel-honest spacing.
colors:
  primary: "#635BFF"
  secondary: "#0A2540"
  tertiary: "#00D4FF"
  neutral: "#FFFFFF"
  surface: "#FFFFFF"
  surface-container: "#F6F9FC"
  surface-container-high: "#EBEFF3"
  on-surface: "#0A2540"
  on-surface-variant: "#425466"
  on-primary: "#FFFFFF"
  primary-container: "#EEEDFF"
  on-primary-container: "#3C34CC"
  outline: "#E3E8EE"
  outline-variant: "#CBD2D9"
  error: "#DF1B41"
  on-error: "#FFFFFF"
  gradient-start: "#635BFF"
  gradient-mid: "#00D4FF"
  gradient-end: "#11EFE3"
typography:
  display:
    fontFamily: "Inter, -apple-system, sans-serif"
    fontSize: 80px
    fontWeight: 600
    lineHeight: 1.0
    letterSpacing: -0.03em
  headline-lg:
    fontFamily: "Inter, -apple-system, sans-serif"
    fontSize: 48px
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: -0.025em
  headline-md:
    fontFamily: "Inter, -apple-system, sans-serif"
    fontSize: 28px
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: -0.015em
  body-lg:
    fontFamily: "Inter, -apple-system, sans-serif"
    fontSize: 18px
    fontWeight: 400
    lineHeight: 1.55
  body-md:
    fontFamily: "Inter, -apple-system, sans-serif"
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.6
  mono:
    fontFamily: "JetBrains Mono, monospace"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.5
  label-sm:
    fontFamily: "Inter, -apple-system, sans-serif"
    fontSize: 13px
    fontWeight: 500
    lineHeight: 1
    letterSpacing: 0.01em
rounded:
  none: 0px
  sm: 4px
  md: 8px
  lg: 12px
  xl: 16px
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 48px
  xxl: 96px
  gutter: 24px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label-sm}"
    rounded: "{rounded.md}"
    height: 40px
    padding: 0 16px
  button-primary-hover:
    backgroundColor: "{colors.on-primary-container}"
  button-secondary:
    backgroundColor: "{colors.surface-container}"
    textColor: "{colors.secondary}"
    typography: "{typography.label-sm}"
    rounded: "{rounded.md}"
    height: 40px
    padding: 0 16px
  button-secondary-hover:
    backgroundColor: "{colors.surface-container-high}"
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.lg}"
    padding: 24px
  card-feature:
    backgroundColor: "{colors.surface-container}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.xl}"
    padding: 32px
  input-field:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    height: 40px
    padding: 0 12px
  code-block:
    backgroundColor: "{colors.surface-container}"
    textColor: "{colors.on-surface}"
    typography: "{typography.mono}"
    rounded: "{rounded.md}"
    padding: 16px
  badge:
    backgroundColor: "{colors.primary-container}"
    textColor: "{colors.on-primary-container}"
    typography: "{typography.label-sm}"
    rounded: "{rounded.full}"
    padding: 4px 10px
  nav-link:
    textColor: "{colors.on-surface-variant}"
    typography: "{typography.body-md}"
  nav-link-active:
    textColor: "{colors.secondary}"
---

## Overview

A payments-industry minimalism: pristine white surfaces, navy primary text, and one signature iridescent gradient that appears exactly twice — once in the hero, once in the final CTA. Everything else is quiet. The gradient is earned, not sprayed.

**Atmosphere**: Density 5/10 (information-rich without feeling cluttered) · Variance 3/10 (disciplined grid, predictable rhythm) · Motion 4/10 (smooth, precise, never cinematic).

**Visual DNA**: full-width hero with a single gradient moment, fixed-max-width content grid (1080px), geometric corners, pixel-honest spacing on a 4px base unit.

## Colors

The palette is almost monochromatic — cool neutrals and navy text — except for the iridescent accent and its gradient stops. Color restraint makes the gradient feel rare.

- **Primary — Stripe Purple (#635BFF)**: the indigo accent. Used for primary CTAs, links, and the start of every gradient.
- **Secondary — Deep Navy (#0A2540)**: body text, headlines, nav. Warmer than pure black, pairs with the cool neutrals.
- **Tertiary — Electric Cyan (#00D4FF)**: gradient midpoint, loading states, progress indicators. Never used as a solid fill.
- **Neutral — Pure White (#FFFFFF)**: the page foundation. Pristine, not warm — the cool tone is intentional.
- **Surface hierarchy**: White (page) → Cold Gray (`#F6F9FC`, cards) → Slate Gray (`#EBEFF3`, elevated). Each step is a 2% shift in lightness — subtle, never muddy.
- **Gradient**: linear `135deg`, stops `{colors.gradient-start}` → `{colors.gradient-mid}` → `{colors.gradient-end}`. Used twice per page, maximum.

## Typography

Inter at fine-tuned weights, with JetBrains Mono reserved for code snippets. Negative letter spacing at display sizes mimics the precision of a typeset headline.

- **Display and headlines**: Inter at 600, negative letter spacing from `-0.015em` (h2) to `-0.03em` (display). The tightness matters — Inter at tracking 0 reads soft; the negative tracking sharpens the voice.
- **Body**: Inter 400 at 15px with line-height 1.6. 15px (not 16px) signals "this is precise — we chose every value".
- **Mono**: JetBrains Mono for code blocks, API responses, and inline `code`. Sets programming content apart from prose.
- **Labels**: Inter 500 at 13px for button text, badges, and metadata. Weight lifts the label above body text without shifting size dramatically.

## Layout

Fixed-max-width grid (1080px) centered in the viewport, with full-width backgrounds reserved for the hero and the final CTA. A 4px base unit (tighter than most systems) supports pixel-honest alignment.

- **Grid**: 12-column with 24px gutters; collapses to 6-column at 960px, single-column at 640px
- **Section rhythm**: `{spacing.xxl}` (96px) between major sections, `{spacing.xl}` (48px) between related blocks
- **Responsive breakpoints**: `sm` 640px · `md` 768px · `lg` 1024px · `xl` 1280px. Hero type scales from `headline-lg` (mobile) to `display` (desktop)
- **Touch targets**: 40px minimum on mobile, matching button height — tap regions extend 8px beyond visible bounds

## Elevation & Depth

Elevation is conveyed through surface color + a single precise shadow at the elevated tier. No chromatic shadows, no glass effects — the aesthetic is clinical clarity.

- **Base**: Pure white (`{colors.surface}`)
- **Cards**: `{colors.surface}` with a 1px `{colors.outline}` border — the border is the elevation signal, not a shadow
- **Feature cards**: `{colors.surface-container}` with no border — surface color shift replaces the border
- **Elevated / modals**: White with `box-shadow: 0 12px 24px rgba(10, 37, 64, 0.08)` — a single navy-tinted shadow at low opacity. The tint matters; pure black feels foreign here
- **Focus rings**: 3px `{colors.primary}` at 40% opacity, inset — contained inside the element to avoid layout shift

## Shapes

Geometric corners, restrained curvature. Pills reserved for badges and status indicators.

- **Buttons and inputs**: `{rounded.md}` (8px) — softens edges without feeling rounded
- **Cards**: `{rounded.lg}` (12px) · feature cards bump to `{rounded.xl}` (16px) for emphasis
- **Badges and status dots**: `{rounded.full}` — signals "label / state" unambiguously
- **Images**: `{rounded.md}` (8px) — matches inputs, keeps visual rhythm consistent

## Components

### Buttons

Primary buttons use `{colors.primary}` with white text at 40px height. Hover darkens to `{colors.on-primary-container}` — a subtle drop rather than a color shift. Secondary buttons are filled with `{colors.surface-container}` and navy text; hover lifts to `{colors.surface-container-high}`. Never use ghost / outline buttons — they disappear on white surfaces.

### Cards

Base cards are pure white with a 1px `{colors.outline}` border at 24px padding. Feature cards use `{colors.surface-container}` with no border at 32px padding — the surface shift IS the elevation. Never combine border + shadow + color shift; pick one signal.

### Inputs

40px height, no filled background, 1px `{colors.outline}` border. Focus swaps to a 1px `{colors.primary}` border with a 3px `{colors.primary}` / 40% opacity inset ring — no layout shift. Label sits above at `{typography.label-sm}`.

### Code blocks

Reserved for API responses and code samples. `{colors.surface-container}` background, JetBrains Mono, 16px padding. Inline `code` uses the same typography at the current font size with a `{colors.surface-container}` background and 2px horizontal padding.

### Badges

Pill-shaped, `{colors.primary-container}` background with `{colors.on-primary-container}` text. Small (4×10px padding) to signal "label", never "button".

### Navigation

Top nav uses `nav-link` tokens. Active link states swap variant to secondary color; no underline. A 2px `{colors.primary}` accent bar below the active item marks the current section — the bar is the only chrome.

## Do's and Don'ts

- **Do** restrict the iridescent gradient to exactly two moments per page — hero and final CTA
- **Do** use `{colors.primary}` for primary CTAs, links, and focus rings — one consistent accent
- **Do** prefer surface color shifts over shadows for most elevation — shadows are reserved for the elevated tier only
- **Do** run `npx @google/design.md lint DESIGN.md` before committing; export Tailwind via `npx @google/design.md export --format tailwind` after token changes
- **Don't** introduce a second gradient direction or additional gradient stops — the signature gradient is fixed at `135deg` with three stops
- **Don't** use pure black (`#000`) anywhere — Deep Navy (`{colors.secondary}`) replaces it for text, shadows, and dividers
- **Don't** layer multiple elevation signals (border + shadow + surface shift) — pick one per element
- **Don't** use ghost / outline buttons over white surfaces — they vanish; use secondary buttons instead
- **Don't** round corners beyond `{rounded.xl}` (16px) — the aesthetic is geometric precision, not rounded-everything
