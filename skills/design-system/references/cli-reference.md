# `@google/design.md` CLI Reference

The canonical validator for DESIGN.md files. Read this before running the CLI or interpreting its output.

- **Package**: [`@google/design.md`](https://github.com/google-labs-code/design.md/tree/main/packages/cli)
- **Invocation**: `npx @google/design.md <command>` (zero-install) or install first (`pnpm add @google/design.md` / `npm install @google/design.md` / `bun add @google/design.md`) and run `design.md <command>`
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

**Exit codes**: `0` when the lint reports zero errors (warnings and info findings are allowed). `1` when one or more errors are present. `1` also when the CLI itself fails (bad input, malformed YAML). Direct CI gate: `npx @google/design.md lint DESIGN.md || exit 1`. The `scripts/audit.sh` wrapper preserves this exit semantics.

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

Reports added/removed/modified tokens per group and sets `regression: true` if the "after" file has more errors or warnings than the "before" file. **Exit codes**: `0` when there's no regression, `1` on regression (usable as a CI gate: `npx @google/design.md diff main.md head.md || exit 1`). The `scripts/diff.sh` wrapper preserves this exit semantics.

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

### GitHub Actions gate

A minimal workflow that blocks PRs with a broken or regressing DESIGN.md:

```yaml
# .github/workflows/design-md.yml
name: DESIGN.md
on:
  pull_request:
    paths: [DESIGN.md]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0            # need history for the diff step
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - name: Lint DESIGN.md
        run: npx -y @google/design.md@latest lint DESIGN.md
      - name: Diff against base branch
        run: |
          git fetch origin ${{ github.base_ref }} --depth=1
          git show origin/${{ github.base_ref }}:DESIGN.md > /tmp/DESIGN.base.md
          npx -y @google/design.md@latest diff /tmp/DESIGN.base.md DESIGN.md
```

The `lint` step fails on `broken-ref` errors. The `diff` step fails when the PR introduces a regression (more errors or warnings than the base). Combine both for a full safety gate on any DESIGN.md-touching PR.

### Pre-commit hook

Block local commits that leave the DESIGN.md broken:

```bash
# .git/hooks/pre-commit (chmod +x)
#!/usr/bin/env bash
if git diff --cached --name-only | grep -q '^DESIGN\.md$'; then
  npx -y @google/design.md@latest lint DESIGN.md || {
    echo "DESIGN.md has errors — fix before committing."
    exit 1
  }
fi
```

Or use a hook manager like `husky` / `lefthook` / `pre-commit` to wire the same check across a team.
