# `@google/design.md` CLI Reference

The canonical validator for DESIGN.md files. Read this before running the CLI or interpreting its output.

- **Package**: [`@google/design.md`](https://github.com/google-labs-code/design.md/tree/main/packages/cli)
- **Invocation**: `npx @google/design.md <command>` (zero-install) or `npm install @google/design.md` + `design.md <command>`
- **Status**: alpha — commands, flags, and rules may change between releases

Before running, verify availability:

```bash
command -v npx && npx @google/design.md --help
```

If unavailable (offline, restricted environment), fall back to manual validation against `references/design-md-spec.md`.

## Commands

All commands accept a file path or `-` for stdin. Output defaults to JSON.

### `lint` — validate a DESIGN.md

```bash
npx @google/design.md lint DESIGN.md
npx @google/design.md lint --format json DESIGN.md
cat DESIGN.md | npx @google/design.md lint -
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `file` | positional | required | Path to DESIGN.md (or `-` for stdin) |
| `--format` | `json` | `json` | Output format |

Exit code `1` if errors are found, `0` otherwise — usable in CI gates.

Output shape:

```json
{
  "findings": [
    {
      "severity": "warning",
      "path": "components.button-primary",
      "message": "textColor (#ffffff) on backgroundColor (#1A1C1E) has contrast ratio 15.42:1 — passes WCAG AA."
    }
  ],
  "summary": { "errors": 0, "warnings": 1, "info": 1 }
}
```

### `diff` — detect regressions between versions

```bash
npx @google/design.md diff DESIGN.md DESIGN-v2.md
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `before` | positional | required | "Before" DESIGN.md |
| `after` | positional | required | "After" DESIGN.md |
| `--format` | `json` | `json` | Output format |

Reports added/removed/modified tokens per group and sets `regression: true` if the "after" file has more errors or warnings. Exit code `1` on regression, `0` otherwise.

### `export` — convert to other token formats

```bash
npx @google/design.md export --format tailwind DESIGN.md > tailwind.theme.json
npx @google/design.md export --format dtcg DESIGN.md > tokens.json
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `file` | positional | required | Path to DESIGN.md |
| `--format` | `tailwind` \| `dtcg` | required | Target format |

`tailwind` produces a theme config ready to merge into `tailwind.config.ts theme.extend`. `dtcg` produces a W3C Design Tokens Community Group tokens.json.

### `spec` — emit the format specification

Useful for injecting the canonical spec into agent prompts — keeps agents aligned with the exact CLI version.

```bash
npx @google/design.md spec
npx @google/design.md spec --rules
npx @google/design.md spec --rules-only --format json
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--rules` | boolean | `false` | Append the active linting rules table |
| `--rules-only` | boolean | `false` | Output only the linting rules |
| `--format` | `markdown` \| `json` | `markdown` | Output format |

## Linting rules

Eight rules run against a parsed DESIGN.md. Each produces findings at a fixed severity.

| Rule | Severity | What it checks |
|------|----------|----------------|
| `broken-ref` | **error** | Token references (`{colors.primary}`) that don't resolve to any defined token |
| `missing-primary` | warning | Colors are defined but no `primary` exists — agents auto-generate one, causing drift |
| `contrast-ratio` | warning | Component `backgroundColor` / `textColor` pairs below WCAG AA (4.5:1 for normal text) |
| `orphaned-tokens` | warning | Color tokens defined but never referenced by any component |
| `token-summary` | info | Summary count of tokens defined per section |
| `missing-sections` | info | Optional sections absent when other tokens exist (e.g. `rounded:` with no `spacing:`) |
| `missing-typography` | warning | Colors defined but no typography tokens — agents fall back to defaults |
| `section-order` | warning | Sections appear out of the canonical order defined by the spec |

Only `broken-ref` is an error — the rest are warnings or info. A clean DESIGN.md (all errors resolved, warnings reviewed) lints with `summary.errors: 0`.

### Interpreting findings

- **Fix every `error`** — broken references break token resolution at runtime and produce unpredictable output.
- **Review every `warning`** — most are genuine issues. The two you may accept intentionally:
  - `orphaned-tokens` when you define palette colors that components don't consume yet (reserved for future use)
  - `missing-typography` on a colors-only partial file in flight
- **`info` findings** are observational — use them to spot structural drift (e.g. a component added without the matching prose section).

### Programmatic API

The linter is also a library:

```typescript
import { lint } from '@google/design.md/linter';

const report = lint(markdownString);
console.log(report.findings);       // Finding[]
console.log(report.summary);        // { errors, warnings, info }
console.log(report.designSystem);   // Parsed DesignSystemState
```

Use this when embedding validation in a custom tool or CI script rather than shelling out to `npx`.

## Recipes

**Pre-commit gate.** Block commits that introduce broken token references:

```bash
npx @google/design.md lint DESIGN.md || exit 1
```

**Release gate.** Fail a PR if a token regression is introduced against the base branch:

```bash
npx @google/design.md diff origin/main:DESIGN.md DESIGN.md || exit 1
```

**Tailwind pipeline.** Regenerate theme config after any DESIGN.md edit:

```bash
npx @google/design.md export --format tailwind DESIGN.md > tailwind.theme.json
```

**Agent prompt injection.** Keep agents aligned with the installed spec version:

```bash
npx @google/design.md spec --rules > .claude/context/design-md-spec.md
```
