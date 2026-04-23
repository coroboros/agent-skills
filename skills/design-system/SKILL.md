---
name: design-system
description: Govern the DESIGN.md — Google's open standard for design tokens (YAML frontmatter + eight prose sections). Auto-activates during UI edits to enforce token-only sourcing for colors, typography, spacing, and corner radius. Also exposes six CLI-backed subcommands — audit (lint + fix proposals), diff (regression check), export (Tailwind / DTCG), spec (canonical spec emission), migrate (port from legacy Stitch format), init (minimal scaffold). When a UI/UX change is requested, DESIGN.md is updated first, audited, then code propagates.
when_to_use: When the user asks to change colors, typography, spacing, corner radius, shadows, component styles, layout, or any visual aspect of the UI. When creating new components or pages. When editing existing UI files. When the user says "redesign", "restyle", "update the look", "change the theme", or references visual tokens. When linting, diffing, exporting, porting, or initializing a DESIGN.md file. Keywords — audit, check, lint, diff, export, spec, migrate, init, DESIGN.md, tokens.
argument-hint: "[audit|diff|export|spec|migrate|init] [path]"
paths:
  - src/components/**
  - src/app/**
  - src/pages/**
  - src/layouts/**
  - src/styles/**
  - src/features/*/components/**
  - DESIGN.md
  - tailwind.config.*
model: opus
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
allowed-tools: Read Write Edit Grep Glob Bash(npx *) Bash(command *) Bash(bash *) Bash(git *) Bash(mktemp *) Bash(wc *) Bash(tr *)
metadata:
  author: coroboros
  sources:
    - github.com/google-labs-code/design.md
    - designtokens.org
---

# Design System

Two modes for governing a project's visual identity:

1. **Auto-activate** — when editing UI files (components, pages, layouts, styles, `DESIGN.md`, `tailwind.config.*`), the skill reads `DESIGN.md` first and enforces token-only sourcing for colors, typography, spacing, and corner radius.
2. **Subcommands** — `/design-system <verb> [path]` exposes the full DESIGN.md lifecycle, built on the canonical `@google/design.md` CLI.

## Subcommand routing

Parse the first positional token of `$ARGUMENTS`. If it matches a verb below, load the referenced file and follow its workflow. Otherwise proceed with the token-enforcement workflow at the end of this document.

| First token | Mode | Reference |
|-------------|------|-----------|
| `audit` (aliases: `check`, `lint`) | Lint + fix proposals, human-readable report | `references/subcommand-audit.md` |
| `diff` | Regression check between versions (git-aware) | `references/subcommand-diff.md` |
| `export` | Tokens → Tailwind theme or W3C DTCG `tokens.json` | `references/subcommand-export.md` |
| `spec` | Emit the canonical spec from the installed CLI | `references/subcommand-spec.md` |
| `migrate` | Port legacy Stitch 9-section DESIGN.md → Google standard | `references/subcommand-migrate.md` |
| `init` | Scaffold a minimal valid DESIGN.md (fallback from `/award-design`) | `references/subcommand-init.md` |
| (none, or a UI file path) | Token enforcement — see the default workflow at the end | (this file) |

## Source of truth

Read `DESIGN.md` at the project root **before** writing any UI code. Every color, font, spacing value, corner radius, and component style must come from this file — either the YAML frontmatter tokens (the normative values) or the prose sections that explain when and why to apply them.

If no `DESIGN.md` exists:
- `/award-design` available → delegate (preferred — archetype + atmosphere + complete DESIGN.md)
- `/award-design` unavailable → `/design-system init [archetype]` for a minimal scaffold

If a legacy Stitch-format `DESIGN.md` is detected (9 numbered sections, `## Agent Prompt Guide` heading, no YAML frontmatter): suggest `/design-system migrate <path>` to port it before proceeding.

## The standard

DESIGN.md is Google's open format for describing a design system to coding agents. Canonical source: [github.com/google-labs-code/design.md](https://github.com/google-labs-code/design.md). A file has two layers:

1. **YAML frontmatter** — machine-readable design tokens (`colors`, `typography`, `rounded`, `spacing`, `components`). Normative values.
2. **Markdown body** — eight `##` sections explaining rationale. Present sections must appear in order:

| # | Section | Aliases | YAML tokens |
|---|---------|---------|-------------|
| 1 | **Overview** | Brand & Style | — |
| 2 | **Colors** | — | `colors:` |
| 3 | **Typography** | — | `typography:` |
| 4 | **Layout** | Layout & Spacing | `spacing:` |
| 5 | **Elevation & Depth** | Elevation | — |
| 6 | **Shapes** | — | `rounded:` |
| 7 | **Components** | — | `components:` |
| 8 | **Do's and Don'ts** | — | — |

Full schema, token types, reference syntax, and consumer behavior for unknown content: `references/design-md-spec.md`. Concrete examples: `references/example-claude.md` (warm editorial), `references/example-stripe.md` (minimalist gradient).

## Token references and schema (at a glance)

- **Colors**: hex (sRGB) quoted — `primary: "#1A1C1E"`
- **Dimensions**: `px` / `em` / `rem` — `48px`, `-0.02em`, `1.5rem`
- **Typography**: object — `fontFamily`, `fontSize`, `fontWeight`, `lineHeight`, `letterSpacing`, `fontFeature`, `fontVariation`
- **Token references**: `{path.to.token}` wrapped in braces — `"{colors.tertiary}"`, `"{rounded.sm}"`
- **Component property tokens** (the only accepted set): `backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`
- **Variants** (hover, active, pressed): separate entries with related keys — `button-primary`, `button-primary-hover`

Recommended but non-normative names: `primary`, `secondary`, `tertiary`, `neutral`, `surface`, `on-surface`, `error`; `headline-lg`, `body-md`, `label-sm`; `none`, `sm`, `md`, `lg`, `xl`, `full`.

## Writing principles

DESIGN.md is written for both agents and humans. These principles govern every section:

- **Tokens are normative, prose is context.** YAML values are what agents render. Prose tells them *when* and *why*. Both are required — prose without values is a mood board; values without prose is a spreadsheet.
- **Descriptive over technical.** Write "whisper-soft shadow" alongside the exact value. Translate CSS into spatial language — `rounded-full` → "pill-shaped".
- **Every value has a role.** `#5e5d59` alone is meaningless; `Olive Gray (#5e5d59): secondary body text — warm medium-dark gray` is actionable.
- **Name tokens semantically.** `primary`, `tertiary`, `button-primary-hover` — not `blue-500`, `shadow-sm`.
- **Show the personality in Overview.** Section 1 sets the tone; every later section should feel written by the same person.
- **Exact values are non-negotiable.** Every color, dimension, component property is a concrete token.

## Rules

- Colors, fonts, spacing, corner radius come **only** from DESIGN.md YAML tokens
- Map tokens to CSS custom properties in the global stylesheet
- Map tokens to `tailwind.config.ts theme.extend` — or generate via `/design-system export tailwind`
- Never use arbitrary Tailwind values (`text-[13px]`, `bg-[#abc]`) when a token exists
- Never introduce values absent from DESIGN.md — use the closest token and flag to the user
- Dark mode: the Google spec has no dedicated mode concept. Use **semantic tokens** in a single DESIGN.md (e.g., `surface`, `on-surface`, `inverse-surface`, `inverse-on-surface`) and let the framework's CSS custom properties map each semantic name to the right value per mode. The Google-published `atmospheric-glass` example follows this pattern — one file, both modes via semantic naming. Avoid dual-file setups (DESIGN.md + DESIGN.dark.md) unless the brand truly diverges between modes
- Shared brand across projects: same DESIGN.md, framework-specific implementation
- Monorepo: the spec and this skill assume a single root `DESIGN.md` per project. For monorepos with per-package brand variations, keep each package's DESIGN.md at the package root and adjust the invocation path (`/design-system audit packages/web/DESIGN.md`). The `paths:` auto-activation matches the root file by default
- **Post-edit invariant** — after any DESIGN.md mutation (token update during the enforcement flow, `migrate`, `init`, or manual edit via this skill), run `/design-system audit <path>` and surface findings. A mutation that leaves errors behind is not done
- Duplicate section headings are a spec error — reject the file
- Unknown section headings are preserved (don't error); unknown component properties are accepted with a warning

## CLI validator — shared surface

The canonical `@google/design.md` CLI powers the `audit`, `diff`, `export`, and `spec` subcommands. Each subcommand wraps one CLI invocation with richer UX (fix proposals, git-awareness, human-readable reports). Raw invocations:

```bash
npx @google/design.md lint DESIGN.md                    # validate
npx @google/design.md diff before.md after.md           # regression check (exit 1 on regression)
npx @google/design.md export --format tailwind DESIGN.md
npx @google/design.md spec --rules                      # emit spec + lint rules
```

Eight linting rules: `broken-ref` (error), `missing-primary`, `contrast-ratio`, `orphaned-tokens`, `token-summary`, `missing-sections`, `missing-typography`, `section-order`. Full table with severity, interpretation, and fix strategies: `references/cli-reference.md`.

Every subcommand verifies CLI availability first (`command -v npx` + a dry `--help` probe). When unavailable or offline: fall back to manual validation against `references/design-md-spec.md`. The skill still enforces the spec without the CLI — it loses only the deterministic check.

## Framework behavior

Detect framework from config files (`astro.config.*`, `next.config.*`, etc.), then follow project instructions (`CLAUDE.md`, `AGENTS.md`, or equivalent) for implementation specifics (component library, font loading, file structure).

## Default workflow — token enforcement

When no subcommand is matched — either auto-activated via `paths:` during a UI edit, or invoked directly to discuss enforcement — follow this workflow.

### Creating a new DESIGN.md

1. **Check for an existing file.** If present → use the change flow below. If absent:
   - `/award-design` available → delegate (preferred)
   - `/award-design` unavailable → `/design-system init [archetype]`
2. **Establish foundations** from `/award-design` output if used. Atmosphere scores (Density, Variance, Motion) go into Overview prose, not YAML.

**How award-design feeds into DESIGN.md:**

| award-design output | DESIGN.md section | YAML tokens |
|---------------------|-------------------|-------------|
| Archetype + atmosphere (Density/Variance/Motion) | 1. Overview (prose) | — |
| Color palette | 2. Colors | `colors:` |
| Typography | 3. Typography | `typography:` |
| Spacing, grid, responsive breakpoints | 4. Layout | `spacing:` |
| Shadow system, surface material | 5. Elevation & Depth | — |
| Corner radius language | 6. Shapes | `rounded:` |
| Component specs (buttons, cards, inputs, nav) | 7. Components | `components:` |
| Archetype guardrails + AI-tell rejections | 8. Do's and Don'ts | — |

3. **Audit** — run `/design-system audit <path>` (post-edit invariant). Fix errors before proceeding.
4. **Wire into the framework**: `/design-system export tailwind` → merge the result into `tailwind.config.ts theme.extend`; set up CSS custom properties in the global stylesheet.

### When UI/UX changes are requested

Any visual change — colors, typography, spacing, radius, shadows, component styles, layout, responsive behavior — follows this flow.

1. **Check whether the change affects tokens.** New value, modified value, or altered visual system → DESIGN.md first. Pure layout bugs, alt text, content reordering → code only.
2. **Update DESIGN.md first.**
   - Open DESIGN.md, locate the affected YAML tokens and prose sections
   - Update values, semantic names, reference paths
   - Cascade — if the primary color changes, update every `components:` entry referencing it
   - Sync Do's and Don'ts if the change contradicts an existing guardrail
3. **Audit** — `/design-system audit <path>` to verify no broken references or contrast regressions (post-edit invariant).
4. **Propagate to code**:
   - Re-export Tailwind theme (`/design-system export tailwind`) or update `theme.extend` by hand
   - Update CSS custom properties in the global stylesheet
   - Update components using raw values — components referencing tokens by name pick up the new value automatically
5. **Shared brand** — if the DESIGN.md is shared across projects, propagate to all, then step 4 in each.

Examples of token-affecting changes:
- "Change CTA color" → `colors.*` + Colors prose + every `components:` entry referencing the old color
- "Make cards more rounded" → `rounded.*` + Shapes prose + `components.card.rounded`
- "Darker theme" → `colors.*` + Overview + Elevation & Depth prose
- "New badge component" → `components.*` + Components prose
- "Increase section spacing" → `spacing.*` + Layout prose

### Re-architecting

A fundamental visual change (new archetype, different atmosphere, complete restyle) is a new design, not a token update. Use `/award-design` to restart the archetype selection and produce a new DESIGN.md. The old file is replaced entirely; do not patch it.
