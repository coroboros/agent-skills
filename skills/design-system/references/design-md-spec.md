# DESIGN.md Spec Reference

Condensed reference for the Google DESIGN.md open standard. Read this when authoring a new DESIGN.md, re-architecting an existing one, or auditing one for spec conformance.

- **Canonical source**: [github.com/google-labs-code/design.md](https://github.com/google-labs-code/design.md) — `docs/spec.md`
- **Version**: `alpha` (v0.1.x) — format may still change
- **Live spec via CLI**: `npx @google/design.md spec` — always reflects the installed CLI version

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

### Token types

| Type | Format | Example |
|------|--------|---------|
| **Color** | `#` + hex (sRGB), quoted string | `"#1A1C1E"` |
| **Dimension** | number + unit (`px`, `em`, `rem`) | `48px`, `-0.02em`, `1.5rem` |
| **Typography** | object | see below |
| **Token reference** | `{path.to.token}` wrapped in braces | `{colors.primary}`, `{rounded.sm}` |

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

## Interoperability

DESIGN.md tokens are inspired by the [W3C Design Token Format](https://www.designtokens.org/) and convert cleanly:

- **Tailwind theme config** — `npx @google/design.md export --format tailwind DESIGN.md`
- **DTCG tokens.json** — `npx @google/design.md export --format dtcg DESIGN.md`
