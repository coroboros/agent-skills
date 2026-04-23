# `audit` subcommand

Lint a DESIGN.md against the canonical Google spec and produce a human-readable report with fix proposals per finding.

## Invocation

```bash
/design-system audit [path]              # default path: ./DESIGN.md
/design-system audit ./DESIGN.md -s      # save the report
/design-system audit --json              # raw CLI JSON (skip the formatted report)
```

Aliases: `check`, `lint` — route to this same workflow.

## Flags

| Flag | Meaning |
|------|---------|
| `-s` | Save the formatted report to `.claude/output/design-system/audit/{slug}/report.md` |
| `-S` | Force no-save (override ambient save mode) |
| `--json` | Skip report composition; print the raw CLI JSON |
| `--strict` | Cross-check against `/award-design`'s anti-patterns catalog and surface exemplar suggestions when the CLI lint is clean (see *Strict mode* below) |

`{slug}` — strip the `.md` extension from the file basename, then kebab-case the remainder:
- `./DESIGN.md` → `design`
- `./docs/custom-design.md` → `custom-design`
- `./brand/Theme.md` → `theme`

The script exits `0` when the lint has zero errors, `1` when errors are present — usable directly as a CI gate (`bash scripts/audit.sh DESIGN.md || exit 1`). This matches the underlying `@google/design.md lint` exit semantics.

## Workflow

1. **Resolve path.** Default to `./DESIGN.md` if no positional argument.
2. **Run the script.**
   ```bash
   bash ${CLAUDE_SKILL_DIR}/scripts/audit.sh <path>
   ```
   The script emits `RESULT: key=value` lines and writes the raw CLI JSON to a temp file. Parse `RESULT: json=<tmp-path>` and `Read` that file to get `findings[]` and `summary`.
3. **Handle CLI unavailability.** If `RESULT: status=npx-missing`, fall back to manual validation against `references/design-md-spec.md` — without a parser we can only check structural invariants (YAML present, eight sections in canonical order, no duplicate headings). Report what was checked and what was not.
4. **Compose the report** using the template below.
5. **Save** under `.claude/output/design-system/audit/{slug}/report.md` if `-s`.
6. **Return summary line** to the user: `✅ clean` or `⚠️ <n> warnings (acceptable)` or `❌ <n> errors — fix before shipping`.

## Report template

```markdown
# DESIGN.md audit — <path>

**Status**: <icon> <summary line>

## Errors (<n>)

<per-finding block — see Fix proposal logic below>

## Warnings (<n>)

<per-finding block>

## Info (<n>)

<per-finding block — usually token-summary only>

## Next steps

- [ ] Fix every error before shipping
- [ ] Review warnings — fix, accept, or justify
- [ ] Re-run `/design-system audit <path>` after changes
```

Per-finding block shape:

```markdown
### `<rule-name>` — <path>

<message from CLI>

**Fix proposal**:
<one or more concrete options, per the rule>
```

Status icon convention:

- `✅ clean` — 0 errors, 0 warnings
- `⚠️ <n> warnings (acceptable)` — 0 errors, warnings are only `orphaned-tokens` or `missing-sections` info
- `⚠️ <n> warnings — review` — 0 errors but warnings include `contrast-ratio`, `section-order`, or `missing-*`
- `❌ <n> errors — fix before shipping` — any errors present

## Fix proposal logic

For each `findings[i]`, compose a fix proposal based on `rule`:

**`broken-ref`** (error).
The message names the broken path. Parse the referenced token name from the YAML frontmatter, then suggest the closest valid token name in the same group (simple substring or Levenshtein match against `Object.keys(colors)` etc.). Show a diff:

```diff
- <property>: "{colors.primry}"
+ <property>: "{colors.primary}"
```

If no close match exists, suggest defining the missing token or removing the reference.

**`contrast-ratio`** (warning, WCAG AA 4.5:1).
The CLI message includes both colors and the measured ratio. The target ratio is 4.5:1 for normal text, 3:1 for large text (≥18pt / 24px, or ≥14pt / 18.66px bold).

Propose concrete candidate fixes — don't hand-wave. The model isn't expected to compute WCAG luminance exactly; instead, **suggest two or three candidate hex values that are plausibly darker or lighter than the offending color, and tell the user to re-run `audit` to verify**. The CLI reports the new ratio deterministically.

Pragmatic heuristic for candidate generation:

- **Darken** (lower each RGB channel): subtract 32 or 48 from each channel, floored at 0. A measured ratio of 3.90:1 typically recovers to ≥4.5:1 after darkening by ~15–20% (subtract ~40 per channel).
- **Lighten** (raise each RGB channel): add 32 or 48, capped at 255.
- Direction depends on the palette: for light backgrounds (warm / minimalist), darken the accent or switch to dark text. For dark backgrounds (cinematic), lighten the accent or switch to light text.

Propose at minimum two options:

1. **Darken the background color**. Example: current `#c96442` on `#ffffff` text measures 3.90:1. Candidate: `#a84828` (each channel dropped ~15%). Likely ≥5:1. Tell the user to re-audit.
2. **Switch the text color**. Use the palette's darkest defined color (`colors.primary` if dark, `colors.on-surface`, or `#000000` as a last resort).

When proposing, include the trade-off: darkening the background changes the brand accent tone; switching text may fight the design voice (editorial warm palettes rarely use pure white on terracotta — dark ink is more idiomatic).

WCAG 2.1 formula (reference only — don't compute inline, let the CLI verify):

- Relative luminance `L` of an sRGB color: normalize each channel `C` to `[0, 1]` via `C / 255`, apply linearization (`C' = C/12.92` if `C ≤ 0.03928`, else `C' = ((C + 0.055)/1.055)^2.4`), then `L = 0.2126*R' + 0.7152*G' + 0.0722*B'`.
- Contrast ratio: `(L_lighter + 0.05) / (L_darker + 0.05)`.

The model should trust the CLI's measurement, propose candidates, and require the user to re-audit. Never claim a candidate passes AA without verification.

**`missing-primary`** (warning).
The palette has colors but no `primary`. Suggest promoting the first-defined color to `primary`, or picking from common candidates (`tertiary`, `brand`, `accent`) that often carry the primary role.

```diff
  colors:
-   brand: "#635BFF"
+   primary: "#635BFF"
```

**`missing-typography`** (warning).
No typography tokens defined. Suggest a minimal block with canonical names:

```yaml
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
```

**`orphaned-tokens`** (warning).
Group all orphaned tokens in a single report block. Present three options:

1. **Accept** — palette-reserved for future use; documented as acceptable (see `references/cli-reference.md`).
2. **Remove** — tighten the palette by deleting unused tokens.
3. **Consume** — add a component that uses them. Example:
   ```yaml
   components:
     alert-error:
       backgroundColor: "{colors.error}"
       textColor: "{colors.on-error}"
       rounded: "{rounded.sm}"
       padding: 12px 16px
   ```

**`section-order`** (warning).
The message names the section that's out of order. Compute the canonical position and show a diff of the section-header reordering. Don't touch the section bodies.

**`missing-sections`** (info).
List the missing sections. No fix is strictly required — sections are optional. Suggest adding them when the project reaches a stage where they're needed (e.g., `spacing:` once layout work begins).

**`token-summary`** (info).
Relay the counts verbatim. No fix.

## Strict mode — `--strict`

Extends the default audit with cross-checks against the broader Coroboros design toolkit. The Google CLI validates spec conformance; `--strict` layers design-quality checks that live in `/award-design`'s reference catalog. Requires `/award-design` installed as a sibling skill.

### What `--strict` adds

1. **Anti-slop scan**. Reads `/award-design`'s `references/anti-patterns.md` catalog and cross-checks the DESIGN.md prose for patterns that betray AI-generated design — generic gradient heroes, pure-white "clean" backgrounds without rationale, `Inter` claimed as the display face without intent, 4-color palettes with no signature accent, symmetric centered layouts with no asymmetric moments, `border-radius: 16px` everywhere without tonal variation. Findings append to the report as `Strict findings` at severity `warning`.

2. **Exemplar suggestion**. When the CLI lint is clean (zero errors), reads `/award-design`'s `references/exemplars.md` and appends a one-block "For inspiration" section pointing to the catalog. Non-actionable, pedagogical — anchors the user's aesthetic judgment against 30+ real-world brand references across nine archetypes.

### Probe logic

Locate `/award-design`'s reference files via this order:

1. `${CLAUDE_SKILL_DIR}/../award-design/references/anti-patterns.md` (sibling install — the standard case when both skills come from `coroboros/agent-skills`)
2. `.claude/skills/award-design/references/anti-patterns.md` (project-local install)
3. `~/.claude/skills/award-design/references/anti-patterns.md` (user install)

Use `Glob` to check each location. First match wins. Same probe pattern for `exemplars.md`.

If neither anti-patterns.md nor exemplars.md is found at any location, report to the user:

> `--strict` requires `/award-design` installed. Install with `npx skills add coroboros/agent-skills --skill award-design`, or run the standard audit (drop `--strict`).

Then fall back to the standard audit flow — do not silently ignore the flag.

### Strict findings block

Add a new section between the CLI findings and Next steps when anti-patterns surface:

```markdown
## Strict findings — anti-slop cross-check (from /award-design)

### Generic gradient hero detected
**Location**: Overview prose
**Pattern**: "linear-gradient from-purple-500 to-pink-500" — flagged by anti-patterns.md as a generic AI-generated hero motif without brand specificity.
**Fix proposal**: Ground the gradient in the brand's specific atmosphere. Either (a) constrain to two brand-owned stops from `colors:` rather than generic utility names, (b) replace with a single brand accent on a warm/cool neutral, or (c) use an asymmetric compositional device instead of a gradient.

### Inter as display face without intent
**Location**: Typography prose + `typography:` block
**Pattern**: `fontFamily: Inter` on display, headline, and body levels without a stated design reason.
**Fix proposal**: Pair Inter with a contrasting face for display (serif or geometric sans) to create hierarchy, OR state the intent explicitly ("Inter across all levels — precision + performance optimized for scanning") in Typography prose.
```

Compose findings from the actual catalog hits — don't invent patterns that aren't in anti-patterns.md.

### Exemplar block (when lint is clean)

Append after the Next steps:

```markdown
## For inspiration — `/award-design`'s exemplars catalog

This design lints clean against the Google spec. For aesthetic calibration, `/award-design` catalogs 30+ real-world brands across nine archetypes. See `references/exemplars.md` in that skill — Linear (restrained Minimalist), Hermès (Corporate Luxury), Anthropic (warm Editorial), Arc (Bento), and more.

Pick the one or two exemplars closest to your archetype and compare: how do they handle primary-color restraint, typography pairing, whitespace, signature moments?
```

### When `--strict` is the right call

- Before shipping a new DESIGN.md to production — catches AI-tells the CLI can't see.
- When the CLI lint is clean but the design "feels generic" — exemplar lookup grounds the aesthetic against real benchmarks.
- For design reviews: the Strict findings block gives reviewers testable critique anchors.

Skip `--strict` for quick WIP checks or when `/award-design` isn't installed — the Google-spec-only audit is already rigorous for spec conformance.

## Visual review — auto-suggested when `dev-browser` is installed

After composing the report, probe `command -v dev-browser`. If `dev-browser` is on PATH, append to the Next steps:

> **Visual verification** — `dev-browser` is installed. To check the rendered output matches DESIGN.md's Components section, run the dev server and screenshot each component state (default / hover / active) via `dev-browser screenshot <url> <selector>`. See [github.com/SawyerHood/dev-browser](https://github.com/SawyerHood/dev-browser) for usage.

This is a suggestion, not an auto-invocation — `dev-browser` needs a running dev server which audit can't assume. Skip silently if `dev-browser` is absent.

## Post-edit rule

After any DESIGN.md mutation performed by this skill (explicit subcommands like `migrate` / `init`, or implicit updates during the token-enforcement workflow), re-run `audit` and surface the findings. A mutation that leaves errors behind is never "done".

## Edge cases

- **Empty DESIGN.md**: CLI will succeed with `missing-primary`, `missing-typography`, `missing-sections` info. Report as `⚠️ <n> warnings — review`; suggest running `/design-system init` or `/award-design` if starting fresh.
- **Non-existent path**: script emits `RESULT: status=file-not-found`. Ask the user for the right path; suggest `find . -name DESIGN.md`.
- **Stitch-format legacy file**: the CLI will likely fire `missing-primary` and `missing-typography` (no YAML frontmatter at all). Detect by checking for section headings like "Visual Theme & Atmosphere" or "Agent Prompt Guide" — if present, suggest `/design-system migrate <path>` instead of treating as a bug.
- **`--json` mode**: skip report composition entirely; print the CLI JSON pass-through. Useful for CI scripts.
