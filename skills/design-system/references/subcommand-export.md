# `export` subcommand

Convert DESIGN.md tokens to other token formats — Tailwind theme config or W3C DTCG `tokens.json`.

## Invocation

```bash
/design-system export                              # tailwind, ./DESIGN.md, default output
/design-system export tailwind                     # same, explicit format
/design-system export dtcg                         # DTCG tokens.json instead
/design-system export tailwind ./path/DESIGN.md    # custom source
/design-system export dtcg -o tokens.json          # custom output path
```

## Flags

| Flag | Meaning |
|------|---------|
| `-o <path>` | Output file. Defaults: `tailwind.theme.json` for tailwind, stdout for dtcg |
| `<format>` positional | `tailwind` or `dtcg` (default: `tailwind`) |
| `<path>` positional | DESIGN.md source (default: `./DESIGN.md`) |

## Workflow

1. **Resolve format** (first positional, default `tailwind`).
2. **Resolve source** (second positional, default `./DESIGN.md`).
3. **Resolve output**:
   - `-o <path>` always wins.
   - Else for `tailwind`: `tailwind.theme.json` next to the source.
   - Else for `dtcg`: stdout (pipe-friendly).
4. **Run the script**:
   ```bash
   bash ${CLAUDE_SKILL_DIR}/scripts/export.sh <format> <source> [output]
   ```
5. **Report** size + path + format-specific integration note.

## Tailwind integration

`export --format tailwind` produces a JSON config shaped for Tailwind's `theme.extend`. It fits naturally into Tailwind CSS v3's JS-config model:

```typescript
// tailwind.config.ts (Tailwind v3)
import theme from './tailwind.theme.json';

export default {
  content: ['./src/**/*.{astro,tsx,ts,jsx,js}'],
  theme: {
    extend: theme,
  },
};
```

Tailwind **v4** uses a CSS-first `@theme` block instead of a JS config object, so the JSON isn't consumed directly. For v4, use the exported JSON as a reference when writing the `@theme` declaration, or run the DTCG export (`--format dtcg`) and transform via Style Dictionary into a v4-compatible CSS file. Either way, DESIGN.md stays the single source of truth.

For v3, merging under `extend` preserves Tailwind's defaults (responsive utilities, grayscale, built-in spacing) and layers DESIGN.md tokens on top. Replacing `theme:` directly (strict token-only) breaks those defaults — keep `extend` unless the user explicitly wants the strict path.

**Regenerate after edits.** Every DESIGN.md mutation should be followed by a re-export if Tailwind is consumed downstream:

```bash
/design-system export tailwind      # regenerate tailwind.theme.json
```

Commit the output alongside DESIGN.md — `tailwind.theme.json` is build-time input, belongs in git.

## DTCG integration

`export --format dtcg` produces a W3C Design Tokens Community Group `tokens.json`, the standard format consumed by:

- Style Dictionary
- Figma Tokens plugin (Tokens Studio)
- Other design-token tooling

Useful when a design team works in Figma and a Tokens Studio file needs to stay in sync with the DESIGN.md source. Pipeline shape:

```bash
/design-system export dtcg -o .tokens/design-tokens.json
# design team imports into Figma Tokens plugin
```

Currently one-way (DESIGN.md → DTCG). Round-tripping from DTCG back to DESIGN.md is not in the Google CLI yet.

## Post-export rule

After `export`, if the output is a Tailwind theme:
- Confirm the file path and size in the report.
- Remind the user to commit `tailwind.theme.json` if it's new.
- If `tailwind.config.ts` already exists and doesn't import the theme file yet, suggest the merge pattern above.

After `export`, if the output is DTCG JSON:
- Confirm path and size.
- Note the consumers (Figma Tokens plugin, Style Dictionary) — no automatic integration.

## Edge cases

- **Format typo** (`export twilwind`): script returns `RESULT: status=invalid-format`. Suggest the two valid options.
- **Source missing**: `RESULT: status=file-not-found`. Suggest `/design-system init` to bootstrap.
- **Output path writable?** If `-o <path>` points to a non-writable directory, the script surfaces the shell error. Report it verbatim.
- **Empty DESIGN.md** (no tokens): the CLI still produces a valid but minimal output file. Surface a warning that the export is mostly empty and suggest running `/design-system audit` to see what's missing.
