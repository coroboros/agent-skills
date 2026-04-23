# `init` subcommand

Scaffold a minimal valid DESIGN.md from scratch. Fallback path for projects where `/award-design` isn't installed or the user wants a bare-bones starter.

## Invocation

```bash
/design-system init                          # generic minimal template at ./DESIGN.md
/design-system init minimalist               # Minimalist archetype starter
/design-system init bento -o docs/DESIGN.md  # custom path
```

## Flags

| Flag | Meaning |
|------|---------|
| `<archetype>` positional | Optional — one of: `minimalist`, `brutalist`, `editorial`, `bold`, `cinematic`, `experimental`, `corporate-luxury`, `bento`, `spatial-organic` |
| `-o <path>` | Output path (default: `./DESIGN.md`) |

## Priority — use `/award-design` when available

If `/award-design` is installed, the best init path is:

```bash
/award-design <brief>                 # full archetype recommendation + atmosphere + DESIGN.md
```

`init` is explicitly the lighter fallback — no brief discussion, no archetype debate, just a starter file the user can fill in. If the user invokes `init` when `award-design` is installed, suggest the richer path once, then proceed with `init` if the user confirms.

## Workflow

1. **Check if target path exists**. If a `DESIGN.md` is already at the target:
   - Abort by default — don't silently overwrite.
   - Offer three options: overwrite (with backup), run `/design-system audit` on the existing file instead, or run `/design-system migrate` if the existing file looks like Stitch format.
2. **Check `/award-design` availability**. If present and user hasn't opted into `init`, surface the suggestion.
3. **Select template**:
   - No archetype → generic minimal template (primary neutral palette, Inter typography, 4px radius scale, 8px spacing base, button + card + input components)
   - Archetype given → archetype-flavored template (see mapping below)
4. **Write** the file to `-o <path>` or `./DESIGN.md`.
5. **Run audit** on the new file: `bash ${CLAUDE_SKILL_DIR}/scripts/audit.sh <output>`. A minimal template should lint with ≤ 2 warnings (`orphaned-tokens`, `missing-sections` is acceptable for placeholders).
6. **Report** to the user:
   - Path created
   - Audit status
   - Next step: "Fill in the TODOs, then run `/design-system audit` again to track progress"

## Generic minimal template

```yaml
---
version: alpha
name: <TODO: project name>
description: <TODO: one sentence about the visual identity>
colors:
  primary: "#000000"
  neutral: "#FFFFFF"
  surface: "#FFFFFF"
  on-surface: "#000000"
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: 600
    lineHeight: 1.1
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
  label-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: 500
    lineHeight: 1
rounded:
  sm: 4px
  md: 8px
  full: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 32px
  xl: 64px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.neutral}"
    typography: "{typography.label-sm}"
    rounded: "{rounded.sm}"
    padding: 12px 24px
    height: 44px
---

## Overview

<TODO: describe the brand personality, target audience, and emotional response the UI should evoke.>

## Colors

<TODO: describe each color role — when to use primary, when to use surface, etc.>

## Typography

<TODO: describe the type strategy — serif vs sans, weight philosophy, hierarchy logic.>

## Layout

<TODO: describe the grid strategy, spacing scale rationale, and responsive breakpoints.>

## Elevation & Depth

<TODO: describe how visual hierarchy is conveyed — shadows, tonal layers, borders.>

## Shapes

<TODO: describe the corner radius language and shape philosophy.>

## Components

<TODO: describe each component's styling guidance. Start with button-primary; add more as the project grows.>

## Do's and Don'ts

- Do <TODO: one specific rule>
- Don't <TODO: one specific rule>
```

The template is intentionally sparse — enough to lint green with info-level findings, but no more. It exists to give the user a valid shape to fill in, not to prescribe design.

## Archetype templates

For each archetype, the template follows the generic shape but with archetype-appropriate defaults:

- **minimalist** — monochrome palette (`#000`, `#fff`, 1-2 grays), Inter or system sans, radius 4px, generous spacing (`xl: 96px`), 4 components
- **brutalist** — flat palette with one saturated accent, sans-serif at heavy weights, radius 0, tight spacing, borders everywhere (no shadows)
- **editorial** — serif display + sans body, warm parchment surface, radius `sm`, terracotta accent
- **bold** — 4-6 saturated colors, heavy display weights, radius `lg` to `full`
- **cinematic** — dark base (surface `#0a0a0a`), single bright accent, large display sizes, shadow-heavy
- **experimental** — placeholder tokens with explicit "customize me" comments, loose component definitions
- **corporate-luxury** — restrained neutrals, custom serif placeholder, radius 0-4px, tight spacing
- **bento** — modular component-first, radius `lg` to `xl`, generous padding inside each tile
- **spatial-organic** — organic spacing (no rigid scale), `rounded.full` for organic corners, soft gradients

Each archetype template mirrors the tone of the corresponding `/award-design` reference file — the goal is that a user running `init <archetype>` gets a starting point consistent with what `/award-design` would produce, minus the brief and archetype debate.

## Post-init guidance

After creating the file, tell the user:

1. **Fill in the TODOs** — the prose sections, especially Overview and Do's and Don'ts, need domain-specific content.
2. **Refine the palette** — the default colors are placeholders; update them to match the brand.
3. **Run `/design-system audit`** after each editing session to catch drift early.
4. **Consider `/award-design`** if stuck — it can recommend an archetype and fill in the creative direction.

## Edge cases

- **Target path exists**: always abort by default. Offer overwrite (with `.legacy.<timestamp>` backup), `audit`, or `migrate` depending on what's already there.
- **Invalid archetype name**: suggest the nine valid options; don't silently fall back to generic.
- **Directory doesn't exist** (e.g., `-o docs/DESIGN.md` with no `docs/`): surface the error, suggest `mkdir -p` or a different path.
