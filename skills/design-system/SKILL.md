---
name: design-system
description: Govern DESIGN.md tokens during UI edits, or audit, diff, export, inspect, migrate and initialize a design system. Enforce the existing token contract when present; absent DESIGN.md does not block ordinary UI work. Canonical CLI operations require their declared validator and report exact remediation when unavailable.
when_to_use: When the user asks to change colors, typography, spacing, corner radius, shadows, component styles, layout, or any visual aspect of the UI. When creating new components or pages. When editing existing UI files. When the user changes the theme or references visual tokens in an existing DESIGN.md. Full redesigns / new visual direction → /award-design. Everyday UI work with no DESIGN.md → /frontend-dev when installed. When linting, diffing, exporting, porting, or initializing a DESIGN.md file. When DESIGN.md uses extension namespaces (motion, shadows, etc.) — run `audit-extensions` to validate them against the globals.css `@theme` mirror. Keywords — audit, check, lint, diff, export, spec, migrate, init, audit-extensions, DESIGN.md, tokens, extended tokens. For empty directories, run `/scaffold` first (then `/award-design` for a DESIGN.md) before invoking this skill.
argument-hint: "[audit|diff|export|spec|migrate|init|audit-extensions] [flags] [path]"
paths:
  - src/components/**
  - src/app/**
  - src/pages/**
  - src/layouts/**
  - src/styles/**
  - src/features/*/components/**
  - DESIGN.md
  - tailwind.config.*
license: MIT
compatibility: "Requires filesystem and shell access with Python 3.10+. CLI-backed audit, diff, export and spec require the declared canonical design.md validator; unavailable or malformed output blocks those verdicts with exact remediation."
allowed-tools: Read Write Edit Grep Glob Bash(command *) Bash(bash *) Bash(git *) Bash(mktemp *) Bash(wc *) Bash(tr *)
metadata:
  author: coroboros
  sources: "github.com/google-labs-code/design.md; www.designtokens.org"
---

# Design System

Two modes for governing a project's visual identity:

1. **Auto-activate** — when editing UI files (components, pages, layouts, styles, `DESIGN.md`, `tailwind.config.*`) **and a `DESIGN.md` is present**, the skill reads it first and enforces token-only sourcing for colors, typography, spacing, and corner radius. No `DESIGN.md`? It stays out of the way — a one-line pointer to `/award-design` or `/frontend-dev`, no enforcement, no block on the edit.
2. **Subcommands** — `/design-system <verb> [path]` exposes the full DESIGN.md lifecycle, built on the canonical `@google/design.md` CLI.

## Subcommand routing

Parse the first positional invocation argument. If it matches a verb below, load the referenced file and follow its workflow. Otherwise proceed with the token-enforcement workflow at the end of this document.

| First token | Mode | Reference |
|-------------|------|-----------|
| `audit` (aliases: `check`, `lint`) | Lint + fix proposals, human-readable report | `references/subcommand-audit.md` |
| `diff` | Regression check between versions (git-aware) | `references/subcommand-diff.md` |
| `export` | Tokens → Tailwind theme or W3C DTCG `tokens.json` | `references/subcommand-export.md` |
| `spec` | Emit the canonical spec from the installed CLI | `references/subcommand-spec.md` |
| `migrate` | Port legacy Stitch 9-section DESIGN.md → Google standard | `references/subcommand-migrate.md` |
| `init` | Scaffold a minimal valid DESIGN.md (fallback from `/award-design`) | `references/subcommand-init.md` |
| `audit-extensions` | Bidirectional drift check — DESIGN.md extension YAML ↔ prose refs ↔ `globals.css` `@theme` | `references/subcommand-audit-extensions.md` |
| (none, or a UI file path) | Token enforcement — see the default workflow at the end | (this file) |

## Source of truth

When a `DESIGN.md` exists at the project root, read it **before** writing any UI code: every color, font, spacing value, corner radius, and component style comes from this file — the YAML frontmatter tokens (normative values) or the prose explaining when and why to apply them.

**No `DESIGN.md`? Step aside.** The default governance mode neither requires nor creates one. It never blocks an edit for lack of a DESIGN.md and never invents a design direction — that is `/award-design`'s job (it forces a universe, writes the DESIGN.md up front, then builds the frontend under it). So:

- Building or editing UI with no file → proceed. For a designed build, point to `/award-design`, which authors the DESIGN.md up front and builds the frontend under it; everyday UI work belongs to `/frontend-dev` when installed.
- A bare token scaffold is needed now and `/award-design` is unavailable or not selected → `/design-system init [archetype]` is a minimal fallback, not the primary path.

Phrase the pointer as an optional handoff, never as a prerequisite: "Design System imposes no prerequisite here; use `/award-design` if you want it to define and build the new visual direction, or `/frontend-dev` for everyday UI work, if installed." Do not say the user must create DESIGN.md before editing.

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

- **Colors**: any valid quoted CSS color; hex is the portable default — `primary: "#1A1C1E"`, `accent: "oklch(0.7 0.2 200)"`
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
- Use existing DESIGN.md tokens in code. An authorized token change updates DESIGN.md first, then propagates to code through the workflow below; do not invent inline values.
- **Extended tokens** — values outside the canonical 5 namespaces (`motion`, `shadows`, `aspectRatios`, `heights`, `containers`, `breakpoints`, `zIndex`, `borderWidths`, `opacity`, `scrollTriggers`) live as top-level YAML namespaces, are validated by convention via `/design-system audit-extensions`, and are mirrored to `globals.css` `@theme`. Upstream accepts unknown component properties with a warning, but this skill deliberately forbids using them to bind extension semantics because exporters and consumers do not share a contract for those keys. Reference extensions in prose instead (for example, `{motion.duration-reveal-slow}`). See `references/extended-tokens.md`
- Dark mode: the Google spec has no dedicated mode concept. Use **semantic tokens** in a single DESIGN.md (e.g., `surface`, `on-surface`, `inverse-surface`, `inverse-on-surface`) and let the framework's CSS custom properties map each semantic name to the right value per mode. The Google-published `atmospheric-glass` example follows this pattern — one file, both modes via semantic naming. Avoid dual-file setups (DESIGN.md + DESIGN.dark.md) unless the brand truly diverges between modes
- Shared brand across projects: same DESIGN.md, framework-specific implementation. Distribution patterns — pick one and document it in the applicable project instructions (`AGENTS.md`, `CLAUDE.md`, or equivalent):
  - **Monorepo** — `packages/brand/DESIGN.md` consumed by all apps; single PR for cross-cutting changes
  - **Git submodule** — canonical brand repo included as submodule; atomic updates via submodule bump
  - **Published package** — `@org/design-tokens` on npm with DESIGN.md + build outputs; versioned, works cross-repo
  - **Copy + periodic `/design-system diff`** — copies in each repo; periodic diff against the canonical catches drift; simplest tooling, highest drift risk
- Monorepo: the spec and this skill assume a single root `DESIGN.md` per project. For monorepos with per-package brand variations, keep each package's DESIGN.md at the package root and pass the intended file explicitly (`/design-system audit packages/web/DESIGN.md`)
- **Post-edit invariant** — after any DESIGN.md mutation (token update during the enforcement flow, `migrate`, `init`, or manual edit via this skill), run `/design-system audit <path>` and surface findings. A mutation that leaves errors behind is not done
- Duplicate section headings are a spec error — reject the file
- Unknown section headings are preserved. Unknown component properties receive an upstream warning and fail this skill's portability convention; `broken-ref` applies only when a token reference does not resolve. Top-level keys resembling schema typos emit `unknown-key` warnings

## CLI validator

The canonical `@google/design.md` CLI powers `audit`, `diff`, `export`, and `spec`. Install it once with `npm install --global --ignore-scripts @google/design.md`, then verify `designmd --version`.

Agent operations use the bundled wrappers, which resolve one `designmd` binary from `PATH`, preflight its version, and validate operation output before reporting success. They never inspect project package manifests, invoke a package manager, or download at runtime.

The current CLI exposes eleven rules: `broken-ref` (error), `missing-primary`, `contrast-ratio`, `orphaned-tokens`, `token-summary`, `missing-sections`, `missing-typography`, `section-order`, `unknown-key`, `token-like-ignored`, and `omitted-rules`. Full semantics and severities: `references/cli-reference.md`.

For any non-`ok` wrapper status, surface `remediation` and `rerun`, then stop. A manual structural read is not an equivalent lint, diff, export, or spec result.

## Framework behavior

Detect framework from config files (`astro.config.*`, `next.config.*`, etc.), then follow project instructions (`AGENTS.md`, `CLAUDE.md`, or equivalent) for implementation specifics (component library, font loading, file structure).

## Default workflow — token enforcement

When no subcommand is matched — either activated from its description during a UI edit, or invoked directly to discuss enforcement — follow this workflow.

### When there is no DESIGN.md

The default governance mode does not author a design file from scratch. When the user explicitly wants a DESIGN.md, it is born one of two ways:

1. **`/award-design` authors it** (preferred) — it forces a universe and writes the full DESIGN.md up front, then builds the frontend under it. design-system governs the result from there.
2. **`/design-system init [archetype]`** — a minimal token scaffold, only when `/award-design` is unavailable or not selected and a bare file is needed now.

Either way, once the file exists, the change flow below applies. Atmosphere scores (Density, Variance, Motion) live in Overview prose, not YAML.

**How award-design's universe maps to DESIGN.md:**

| award-design output | DESIGN.md section | YAML tokens |
|---------------------|-------------------|-------------|
| Archetype + atmosphere (Density/Variance/Motion) + signature moment + photography direction + copy register | 1. Overview (prose) | — |
| Color palette + photography colour guidance | 2. Colors | `colors:` |
| Typography + kinetic typography intent | 3. Typography | `typography:` |
| Spacing, grid, scroll choreography, responsive system | 4. Layout | `spacing:` + ext: `breakpoints:`, `containers:`, `heights:`, `aspectRatios:`, `motion:`, `scrollTriggers:` |
| Shadow language + depth narrative | 5. Elevation & Depth | ext: `shadows:`, `borderWidths:`, `opacity:` |
| Corner radius language | 6. Shapes | `rounded:` |
| Component specs + variants + micro-interactions + motion philosophy | 7. Components | `components:` (8 property tokens only) + ext: `zIndex:` |
| Archetype guardrails + AI-tell rejections + production-hardening rules | 8. Do's and Don'ts | — |

Extension namespaces (`ext:` rows above) live as top-level YAML per `references/extended-tokens.md`. Components bind only to the eight canonical property tokens — extension tokens are referenced in prose, never as `components:` keys.

Once the file exists (authored or scaffolded), wire it into the project:

1. **Audit** — run `/design-system audit <path>` (post-edit invariant). Fix errors before proceeding.
2. **Wire into the framework**: `/design-system export tailwind` → merge the result into `tailwind.config.ts theme.extend` (v3) or `globals.css` `@theme` block (v4); set up CSS custom properties in the global stylesheet.
3. **Validate the mirror** — `/design-system audit-extensions <path>` confirms every extension token in the YAML has its CSS custom property and every prose reference resolves. Run after every export.

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
5. **Shared brand** — identify affected consumers. Propagate and run step 4 only in projects covered by the user's authorization; report other consumers and the change they need without editing them.

Examples of token-affecting changes:
- "Change CTA color" → `colors.*` + Colors prose + every `components:` entry referencing the old color
- "Make cards more rounded" → `rounded.*` + Shapes prose + `components.card.rounded`
- "Darker theme" → `colors.*` + Overview + Elevation & Depth prose
- "New badge component" → `components.*` + Components prose
- "Increase section spacing" → `spacing.*` + Layout prose

### Re-architecting

A fundamental visual change (new archetype, different atmosphere, complete restyle) is a new design, not a token update. Recommend or hand off to `/award-design` when the user wants that designed build — it writes a fresh DESIGN.md and builds under it. If `/award-design` is unavailable or not selected, design-system steps aside and does not block the edit. Any existing DESIGN.md is replaced whole, never patched in place.

## Gotchas

1. **Unknown component properties are not portable.** The upstream parser accepts them with a warning, but downstream exporters and agents only share the eight canonical properties (`backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`). Treat an extension key such as `shadow` as a skill-level failure even when upstream lint does not. Reference extension tokens in prose and mirror them to CSS instead.
2. **Duplicate `##` section heading breaks spec parsing silently.** Two `## Colors` sections (from a botched re-architect) cause the parser to read only the first; YAML in the second is dropped without warning. Each of the 8 sections must appear exactly once. Fix: prescan for heading duplicates; fail hard with the duplicated name.
3. **`export tailwind` emits Tailwind v3 configuration JSON.** Semantic token names are preserved and valid, but Tailwind v4 projects use CSS-first `@theme` declarations instead of `theme.extend`. Translate the exported entries into the global stylesheet and regenerate that mirror after DESIGN.md changes; do not paste the JSON into a v4 stylesheet.
4. **Multiple DESIGN.md files make the target ambiguous.** A monorepo may contain both `./DESIGN.md` and files such as `packages/*/DESIGN.md`. Fix: when multiple candidates are detected, ask which one to govern. Never silently pick the root.
