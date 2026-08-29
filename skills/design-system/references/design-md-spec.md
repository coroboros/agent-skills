# DESIGN.md Spec Reference

<!-- Authoring summary reconciled with github.com/google-labs-code/design.md 0.3.0 on 2026-07-18. Use /design-system spec for the exact installed artifact. -->
<!-- Refresh when Google bumps a minor: `/design-system spec -o references/design-md-spec.md` and reconcile, or fetch `docs/spec.md` raw and re-condense. -->

Condensed reference for the Google DESIGN.md open standard. Read this when authoring a new DESIGN.md, re-architecting an existing one, or auditing one for spec conformance.

- **Canonical source**: [github.com/google-labs-code/design.md](https://github.com/google-labs-code/design.md) — `docs/spec.md`
- **Version reconciled here**: `0.3.0` — use the installed CLI for newer behavior
- **Live spec via CLI**: `designmd spec` — reflects the installed CLI version
- **This file is a condensed authoring summary**, not a verbatim snapshot. Treat the installed CLI plus canonical source as authoritative when they diverge.

A DESIGN.md has two layers. YAML frontmatter holds **normative** design tokens; the markdown body holds **contextual** prose that explains when and why to apply them. Prose may use descriptive names ("Midnight Forest Green") that correspond to systematic token names (`primary`).

## YAML Frontmatter Schema

```yaml
version: <string>          # optional, current: "alpha"
name: <string>
description: <string>      # optional
colors:
  <token-name>: <Color>
typography:
  <token-name>: <Typography>
rounded:
  <scale-level>: <Dimension>
spacing:
  <scale-level>: <Dimension | number>
components:
  <component-name>:
    <token-name>: <string | token reference>
```

The frontmatter begins with a line containing exactly `---` and ends with a line containing exactly `---`. YAML inside is parsed to the schema above.

`<scale-level>` is a named level in a sizing or spacing scale. Common names include `xs`, `sm`, `md`, `lg`, `xl`, and `full`, but **any descriptive string key is valid** — `base`, `gutter`, `margin`, `container-padding` are all acceptable per the spec.

### Token types

| Type | Format | Example |
|------|--------|---------|
| **Color** (in `colors:`) | any valid CSS color string, quoted | `"#1A1C1E"`, `"oklch(0.7 0.2 200)"` |
| **Dimension** | number + unit (`px`, `em`, `rem`) | `48px`, `-0.02em`, `1.5rem` |
| **Typography** | object | see below |
| **Token reference** | `{path.to.token}` wrapped in braces | `{colors.primary}`, `{rounded.sm}` |

The `colors:` palette accepts any valid CSS color string: hex, named colors, `rgb()`, `hsl()`, `hwb()`, wide-gamut functions such as `oklch()`, and `color-mix()`. Hex remains the recommended default for portability. Inside a `components:` entry, color properties accept the same CSS color strings or token references.

### Typography object

- `fontFamily` (string)
- `fontSize` (Dimension)
- `fontWeight` (number — e.g. `400`, `700`; quoted string also accepted)
- `lineHeight` (Dimension or unitless number — a multiplier of `fontSize`, the recommended CSS practice)
- `letterSpacing` (Dimension)
- `fontFeature` (string — configures `font-feature-settings`)
- `fontVariation` (string — configures `font-variation-settings`)

### Component property tokens

Each component maps a name to a group of sub-token properties. Valid properties:

- `backgroundColor` — Color
- `textColor` — Color
- `typography` — Typography (composite reference allowed: `"{typography.label-md}"`)
- `rounded` — Dimension
- `padding` — Dimension
- `size` — Dimension
- `height` — Dimension
- `width` — Dimension

**Variants** (hover, active, pressed, disabled) are expressed as separate component entries with related key names:

```yaml
components:
  button-primary:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.on-tertiary}"
    rounded: "{rounded.sm}"
    padding: 12px
  button-primary-hover:
    backgroundColor: "{colors.tertiary-container}"
```

### Token references

References use `{path.to.token}` syntax and must resolve to a defined value. For most groups, a reference must point to a primitive (e.g. `{colors.primary}`), not a group (e.g. `{colors}`). Within `components`, references to composite values (e.g. `{typography.label-md}`) are permitted.

## Sections

All sections use `<h2>` (`##`) headings. An optional `<h1>` may appear for document titling and is not parsed as a section. Sections can be omitted if not relevant — but those present must appear in the order below.

| # | Section | Aliases | Purpose | Associated tokens |
|---|---------|---------|---------|-------------------|
| 1 | **Overview** | Brand & Style | Personality, emotional response, foundational context | — |
| 2 | **Colors** | — | Palette rationale and roles | `colors:` |
| 3 | **Typography** | — | Type strategy and hierarchy | `typography:` |
| 4 | **Layout** | Layout & Spacing | Grid, spacing scale, responsive strategy | `spacing:` |
| 5 | **Elevation & Depth** | Elevation | Shadow system, surface material (glass, matte) | — |
| 6 | **Shapes** | — | Corner radius language, shape philosophy | `rounded:` |
| 7 | **Components** | — | Per-component styling guidance | `components:` |
| 8 | **Do's and Don'ts** | — | Testable guardrails — what to do, what to avoid | — |

### Section-by-section requirements

**1. Overview.** Brand personality, target audience, emotional response. Defines whether the UI feels playful or professional, dense or spacious. Seeds high-level stylistic decisions when a specific rule isn't defined. Atmosphere scores (Density/Variance/Motion from `/award-design`) live here as prose, not YAML — the spec doesn't define atmosphere tokens.

**2. Colors.** At least `primary` must be defined. Common roles: `primary`, `secondary`, `tertiary`, `neutral`. Prose describes each role and its usage context.

**3. Typography.** Most systems define 9–15 levels. Common semantic categories: `headline`, `display`, `body`, `label`, `caption`, each with size variants (`sm`, `md`, `lg`).

**4. Layout.** Grid strategy (fluid, fixed-max-width, bento, asymmetric), spacing scale, container logic. Responsive breakpoints and collapsing strategy live here — there is no separate responsive section in the spec.

**5. Elevation & Depth.** Shadow system (neutral vs. chromatic, single vs. multi-layer), glass/matte/textured surfaces. For flat designs, explain how depth is conveyed without shadows.

**6. Shapes.** Corner radius language. `rounded:` tokens scale (`none`, `sm`, `md`, `lg`, `xl`, `full`).

**7. Components.** Style guidance for buttons, chips, lists, tooltips, checkboxes, radios, inputs, cards, modals. The spec is actively evolving; structure stays flexible for domain-specific components.

**8. Do's and Don'ts.** Practical guardrails. Each rule should be testable — "use primary only for the single most important action per screen" is testable; "make it feel premium" is not.

## Consumer behavior for unknown content

| Scenario | Behavior |
|----------|----------|
| Unknown section heading | Preserve; do not error |
| Unknown color token name | Accept if value is valid |
| Unknown typography token name | Accept as valid typography |
| Unknown spacing value | Accept; store as string if not a valid dimension |
| Unknown component property | Accept with warning |
| Duplicate section heading | **Error**; reject the file |

## Recommended token names (non-normative)

Used across many design systems. Not required but provided for consistency:

- **Colors**: `primary`, `secondary`, `tertiary`, `neutral`, `surface`, `on-surface`, `error`
- **Typography**: `headline-display`, `headline-lg`, `headline-md`, `body-lg`, `body-md`, `body-sm`, `label-lg`, `label-md`, `label-sm`
- **Rounded**: `none`, `sm`, `md`, `lg`, `xl`, `full`

## Extending the spec — custom top-level YAML keys

The spec defines five token groups (`colors`, `typography`, `rounded`, `spacing`, `components`) plus three top-level fields (`version`, `name`, `description`). Its Consumer Behavior table does not forbid unknown top-level YAML keys. Deliberate extension namespaces may remain in the source file, but the CLI reports `token-like-ignored` because canonical exports omit them. They are a project convention, not a portable schema feature.

Two deliberate spec gaps worth extending via custom namespaces:

**Motion tokens.** The spec has no `transitions:`, `durations:`, or `easings:` group, yet motion is a first-class design dimension. Add a custom namespace:

```yaml
motion:
  duration-fast: 150ms
  duration-base: 250ms
  duration-slow: 400ms
  easing-standard: cubic-bezier(0.4, 0, 0.2, 1)
  easing-enter: cubic-bezier(0, 0, 0.2, 1)
  easing-exit: cubic-bezier(0.4, 0, 1, 1)
```

These tokens remain in the file for project-aware consumers. The canonical CLI does not validate or export them, so document intended usage in prose and validate the runtime mirror with `audit-extensions`.

**Breakpoints.** The spec folds breakpoints into Layout prose. If tooling needs them as tokens:

```yaml
breakpoints:
  sm: 640px
  md: 768px
  lg: 1024px
  xl: 1280px
```

Same behavior — preserved but unvalidated.

**Rules when extending**:
- Pick distinct namespaces (`motion:`, `breakpoints:`, `z-index:`, `elevation-scale:`) — never shadow or collide with spec-defined groups.
- Keep the shape consistent with the spec's map-of-strings convention so a future DTCG or Tailwind exporter could pick them up.
- Document the namespace in the Overview or Do's and Don'ts so future maintainers know it's intentional, not drift.
- **Components stay within the closed set of 8 portable component properties.** Upstream accepts an unknown property with a warning, but other consumers and exporters have no shared meaning for it. This skill therefore references extension namespaces from prose only and treats unknown component properties as a project-level portability failure. A `broken-ref` error is separate: it means the referenced token path does not exist.
- For the curated namespace list and the canonical-vs-extension boundary used across this skill set, see `extended-tokens.md`. The `audit-extensions` subcommand validates the bidirectional contract (YAML ↔ prose ↔ `globals.css` `@theme`).

## Interoperability

DESIGN.md tokens are inspired by the [W3C Design Token Format](https://www.designtokens.org/) — specifically the concept of typed token groups and the `{path.to.token}` reference syntax. They convert cleanly to other formats:

- **Tailwind theme config** — `designmd export --format tailwind DESIGN.md`
- **DTCG tokens.json** (W3C Design Tokens Community Group) — `designmd export --format dtcg DESIGN.md`
- **Figma variables** — via the DTCG output and the Tokens Studio plugin
- **Style Dictionary** — via the DTCG output

Currently one-way (DESIGN.md → target). Round-tripping from external formats back to DESIGN.md is not in the official CLI.
