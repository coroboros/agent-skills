# `migrate` subcommand

Port a legacy Stitch 9-section DESIGN.md to the canonical Google DESIGN.md format (YAML frontmatter + 8 prose sections).

## Invocation

```bash
/design-system migrate ./DESIGN.md              # in-place (with .legacy backup)
/design-system migrate old.md -o new.md         # write to a new path, preserve old
```

## Flags

| Flag | Meaning |
|------|---------|
| `<path>` positional | Required — path to the legacy file |
| `-o <path>` | Output file (default: overwrite input with `.legacy.<ISO-timestamp>` backup) |

Migration always produces a backup. `-o` with a different path skips the backup since the original is untouched.

## Detection heuristics

Before migrating, confirm the input is actually Stitch format. Signals (any one suffices):

- Section headings match the Stitch 9-section scheme: `## Visual Theme & Atmosphere`, `## Color Palette & Roles`, `## Component Stylings`, `## Layout Principles`, `## Depth, Elevation & Material`, `## Responsive Behavior`, `## Agent Prompt Guide`
- `## Agent Prompt Guide` section is present
- No YAML frontmatter (or frontmatter without `colors:`, `typography:` groups)
- File contains phrases like "Stitch standard" or references to 9 sections

If detection fails, ask the user: "This file doesn't look like a Stitch-format DESIGN.md. Run anyway?" Default to no.

## Section mapping

| Stitch (old) | Google (new) | Notes |
|--------------|--------------|-------|
| 1. Visual Theme & Atmosphere | 1. Overview | Direct rename; atmosphere scores stay as prose |
| 2. Color Palette & Roles | 2. Colors | Direct; extract hex values into `colors:` YAML |
| 3. Typography Rules | 3. Typography | Direct; extract font properties into `typography:` YAML |
| 4. Component Stylings | 7. Components | **Reordered**; extract specs into `components:` YAML |
| 5. Layout Principles | 4. Layout | **Reordered**; extract spacing into `spacing:` YAML |
| 6. Depth, Elevation & Material | 5. Elevation & Depth | **Reordered**; rename from "Depth" to "Elevation & Depth" |
| 7. Do's and Don'ts | 8. Do's and Don'ts | **Reordered** to the end |
| 8. Responsive Behavior | *merged into 4. Layout* | No dedicated section in Google spec — breakpoints + collapsing go into Layout prose |
| 9. Agent Prompt Guide | *removed* | Tokens + section structure replace it; keep "Self-test question" as a testable Do if present |

Section 6 (Shapes) is **new** in Google spec. Extract corner radius values from the Stitch source (typically found in Component Stylings or Layout Principles) into `rounded:` YAML and write a short Shapes section.

## Token extraction from prose

The source is mostly prose with inline values. Use these patterns:

**Colors**. Look for lines matching `<Name> (#<hex>)` or `<hex>` alone with a role label. Group into palette roles (`primary`, `secondary`, `tertiary`, `neutral`, plus surface/on-surface hierarchies if present). If the source uses descriptive names ("Parchment"), keep them in the prose; the YAML token name should be the semantic role (`neutral`).

**Typography**. Look for font family declarations, size values (`px`, `rem`, `em`), weights, line heights. Group by hierarchy role (`display`, `headline-lg`, `body-md`, `label-sm`). If the source uses a "Hierarchy table", parse it column by column.

**Rounded**. Look for `border-radius` values or mentions like "4px corner radius". Map to the canonical scale: `sm`, `md`, `lg`, `full`.

**Spacing**. Look for the base unit (`4px` / `8px`) and named spacing levels (`xs`, `sm`, `md`, `lg`, `xl`). Extract the scale from Layout Principles prose.

**Components**. For each component mentioned in Component Stylings, extract its exact properties (background, text color, padding, height, radius) and express as YAML with token references where possible. Variants (hover, active) become separate entries with related key names.

Unknown or ambiguous values: fill with a concrete guess AND mention in the migration report. Never silently invent a value.

## Workflow

1. **Detect format** (see heuristics above). Abort or confirm with the user if unsure.
2. **Backup** the original as `<path>.legacy.<ISO-timestamp>`.
3. **Parse the source**:
   - Split on `##` headings to isolate sections.
   - For each section, extract tokens using the patterns above.
4. **Assemble YAML frontmatter** with `version: alpha`, `name` (infer from source H1 if present, else prompt), then all extracted tokens.
5. **Assemble the body**:
   - Overview (from Visual Theme prose, keeping atmosphere scores)
   - Colors (reformat the palette list, reference the YAML tokens)
   - Typography (reformat the hierarchy, reference YAML)
   - Layout (merge Layout Principles + Responsive Behavior prose)
   - Elevation & Depth (from the old section 6)
   - Shapes (new — compose from extracted radius values)
   - Components (reformat from old Component Stylings, reference YAML)
   - Do's and Don'ts (keep as-is; fold in anything testable from old Agent Prompt Guide)
6. **Write** the new file (overwrite input or write to `-o <path>`).
7. **Run audit** on the output: `bash ${CLAUDE_SKILL_DIR}/scripts/audit.sh <output>`.
8. **Compose migration report** — save as `<output>.migration.md` or include inline in the user-facing response.

## Migration report template

```markdown
# Migration report — <input> → <output>

## What was extracted verbatim
- <list of clean extractions, e.g., "12 colors, 7 typography levels, 4 rounded levels, 6 components">

## What was inferred (review these)
- <list of best-guess extractions with rationale — e.g., "Rounded scale inferred from a single '4px corners' prose mention; assumed sm=4px, md=8px, lg=12px">

## What was dropped intentionally
- Agent Prompt Guide section (no equivalent in Google spec; self-test question preserved as a Do if present)
- <any other discarded content>

## Audit status after migration
<paste the audit summary line — ideally ✅ clean, or the list of remaining warnings>

## Backup
Original preserved at `<path>.legacy.<timestamp>`.
```

Surface this report in the user's response. It's a trust artifact — the user should be able to verify nothing was silently lost.

## Edge cases

- **Source has partial sections** (e.g., no Typography Rules): skip the corresponding YAML group, note in the migration report, and the audit will flag `missing-typography` — expected.
- **Non-Stitch format with some matching headings**: detection heuristics may false-positive. Always confirm with the user before overwriting.
- **Values impossible to extract** (e.g., "various shades of blue" with no hex): prompt the user for each missing value; do not invent.
- **Audit fails on the output**: do not revert. Surface the errors and let the user fix them; the backup is available if they want to start over.

## When NOT to migrate

- Green-field projects → use `/award-design` or `/design-system init` to create a fresh DESIGN.md.
- Non-Stitch DESIGN.md files that just happen to lack YAML frontmatter → use `audit` to see what's missing, then add YAML tokens directly; migration is overkill.
- Files already following the Google spec → nothing to do; `audit` is sufficient.
