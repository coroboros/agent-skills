# `init` subcommand

Scaffold a minimal valid DESIGN.md from scratch. Fallback path for projects where `/award-design` isn't installed or the user wants a bare-bones starter.

## Invocation

```bash
/design-system init                              # generic minimal template at ./DESIGN.md
/design-system init minimalist                   # Minimalist archetype starter
/design-system init bento-card -o docs/DESIGN.md # custom path
```

## Flags

| Flag | Meaning |
|------|---------|
| `<archetype>` positional | Optional hint — if given, recommend `/award-design` for archetype-aware creation instead of a generic scaffold (see *On archetype flavors* below) |
| `-o <path>` | Output path (default: `./DESIGN.md`) |

## Priority — use `/award-design` when available

If `/award-design` is installed, the best init path is:

```bash
/award-design <brief>                 # full archetype recommendation + atmosphere + DESIGN.md
```

`init` is the lighter fallback: a starter file without a full art-direction exercise. An explicit `init` already selects this mode; proceed without renewed confirmation. Mention `award-design` only when its richer direction would help, without blocking the requested init.

## Workflow

`$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing the skill's SKILL.md elsewhere.

1. **Check if target path exists**. If a `DESIGN.md` is already at the target:
   - Abort by default — don't silently overwrite.
   - Offer three options: overwrite (with backup), run `/design-system audit` on the existing file instead, or run `/design-system migrate` if the existing file looks like Stitch format.
2. **Check `/award-design` availability**. If present and user hasn't opted into `init`, surface the suggestion.
3. **Select template**:
   - No archetype → generic minimal template (primary neutral palette, Inter typography, 4px radius scale, 8px spacing base, button + card + input components)
   - Archetype given → explain that init produces the generic template, then perform the explicit init; use `/award-design` only when the user requests the richer direction
4. **Preflight the canonical CLI before any write**. Source `scripts/designmd-runtime.sh` and call `require_designmd` with the intended audit rerun command. On failure, surface `remediation` and `rerun`, then stop. Do not create a partial target or substitute a manual audit.
5. **Write a candidate temp file** next to the requested destination. Never write the final path yet.
6. **Run audit on the candidate**: `bash "$SKILL_DIR"/scripts/audit.sh <candidate>`. A minimal template should lint with ≤ 2 warnings (`orphaned-tokens`, `missing-sections` is acceptable for placeholders). Any CLI, schema, or audit failure deletes the candidate and leaves the final path untouched.
7. **Commit atomically** by renaming the validated candidate to `-o <path>` or `./DESIGN.md`. If a target appeared after preflight, stop rather than overwrite it.
8. **Report** to the user:
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

## On archetype flavors

`init` ships only the generic template above. Archetype-flavored starters — Minimalist, Brutalist, Editorial, Bold / Maximal, Immersive / Cinematic, Experimental, Corporate Luxury, Bento / Card, Spatial Organic — are `/award-design`'s job. The accepted kebab-case slugs are `minimalist`, `brutalist`, `editorial`, `bold-maximal`, `immersive-cinematic`, `experimental`, `corporate-luxury`, `bento-card`, `spatial-organic`. That skill already has per-archetype reference files, atmosphere calibration, and brief-aware prose; duplicating its templating here would drift over time.

If a user runs `/design-system init <archetype>`, treat the archetype argument as a hint and recommend the richer path:

> `/design-system init` creates the generic starter requested. `/award-design` is available for a complete archetype-specific direction.

Proceed with the explicit init and the template above. If the user redirects to `/award-design`, load and execute that skill within the revised scope.

## Post-init guidance

After creating the file, tell the user:

1. **Fill in the TODOs** — the prose sections, especially Overview and Do's and Don'ts, need domain-specific content.
2. **Refine the palette** — the default colors are placeholders; update them to match the brand.
3. **Run `/design-system audit`** after each editing session to catch drift early.
4. **Consider `/award-design`** if stuck — it can recommend an archetype and fill in the creative direction.

## Edge cases

- **Target path exists**: always abort by default. Offer overwrite (with `.legacy.<timestamp>` backup), `audit`, or `migrate` depending on what's already there.
- **Archetype given but `/award-design` not installed**: proceed with the generic template and note that archetype flavor would have required `/award-design`.
- **Directory doesn't exist** (e.g., `-o docs/DESIGN.md` with no `docs/`): surface the error, suggest `mkdir -p` or a different path.
- **CLI or audit failure**: remove the candidate, preserve the final destination byte-for-byte, and print the exact repair plus init rerun commands.
