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

## Post-edit rule

After any DESIGN.md mutation performed by this skill (explicit subcommands like `migrate` / `init`, or implicit updates during the token-enforcement workflow), re-run `audit` and surface the findings. A mutation that leaves errors behind is never "done".

## Edge cases

- **Empty DESIGN.md**: CLI will succeed with `missing-primary`, `missing-typography`, `missing-sections` info. Report as `⚠️ <n> warnings — review`; suggest running `/design-system init` or `/award-design` if starting fresh.
- **Non-existent path**: script emits `RESULT: status=file-not-found`. Ask the user for the right path; suggest `find . -name DESIGN.md`.
- **Stitch-format legacy file**: the CLI will likely fire `missing-primary` and `missing-typography` (no YAML frontmatter at all). Detect by checking for section headings like "Visual Theme & Atmosphere" or "Agent Prompt Guide" — if present, suggest `/design-system migrate <path>` instead of treating as a bug.
- **`--json` mode**: skip report composition entirely; print the CLI JSON pass-through. Useful for CI scripts.
