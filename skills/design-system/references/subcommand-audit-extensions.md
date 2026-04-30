# `audit-extensions` subcommand

Bidirectional drift check between DESIGN.md extension namespaces (`motion`, `shadows`, `aspectRatios`, `heights`, `containers`, `breakpoints`, `zIndex`, `borderWidths`, `opacity`, `scrollTriggers`), the prose references that name them, and the `globals.css` `@theme` block that mirrors them. Closes the gap left by `/design-system audit` (the Google CLI preserves extensions but does not validate references into them).

See `references/extended-tokens.md` for the full convention this subcommand enforces.

## Invocation

```bash
/design-system audit-extensions [path]                    # default path: ./DESIGN.md
/design-system audit-extensions ./DESIGN.md --css path    # explicit CSS layer location
/design-system audit-extensions ./DESIGN.md --strict      # promote orphan warnings to errors
/design-system audit-extensions ./DESIGN.md -s            # save the report
/design-system audit-extensions ./DESIGN.md --json        # emit JSON instead of report
```

## Flags

| Flag | Meaning |
|------|---------|
| `--css <path>` | Path to the `globals.css` (or other CSS file holding the `@theme` block). Auto-detected when omitted (see *CSS auto-detection* below). |
| `--strict` | Promote `extension-orphan-css` warnings to errors. CI gate when authoring discipline is mandatory. |
| `-s` | Save the formatted report to `.claude/output/design-system/audit-extensions/{slug}/report.md` |
| `-S` | Force no-save (override ambient save mode) |
| `--json` | Emit JSON instead of the human-readable report |

`{slug}` follows the same rule as `audit` — strip `.md` and kebab-case (`./DESIGN.md` → `design`).

The script exits `0` when zero errors, `1` when any errors are present (warnings alone do not fail). Usable as a CI gate.

## Workflow

1. **Resolve DESIGN.md path.** Default to `./DESIGN.md`.
2. **Auto-detect or accept explicit CSS layer.** Order of probing (first match wins):
   - `--css <path>` if passed
   - `src/app/globals.css`
   - `src/styles/globals.css`
   - `src/style.css`
   - `app/globals.css`
   - `src/app/global.css`
3. **Run the script.**
   ```bash
   bash ${CLAUDE_SKILL_DIR}/scripts/audit-extensions.sh <path> [--css <css-path>] [--strict]
   ```
   Emits `RESULT: key=value` lines and per-finding `FINDING:` lines.
4. **Compose the report** using the template below.
5. **Save** under `.claude/output/design-system/audit-extensions/{slug}/report.md` if `-s`.
6. **Return summary line**: `✅ clean` or `⚠️ <n> warnings (acceptable)` or `❌ <n> errors — fix before shipping`.

## Drift-detection rules

Three rules, mirrored to the bidirectional contract in `extended-tokens.md`:

### `extension-missing-css` (error)

Every extension token in DESIGN.md YAML must have a matching CSS custom property in `globals.css` `@theme`, per the 1:1 mapping table in `extended-tokens.md`. Missing → error.

```
YAML:  shadows.lifted
CSS:   --shadow-lifted   ← must exist in @theme block
```

**Fix proposal**: run `/design-system export tailwind <path> > <css-path>` (or merge the export into the existing `@theme`) to regenerate the mirror. Re-audit.

### `extension-orphan-css` (warning, error under `--strict`)

CSS custom properties matching the extension prefixes (`--shadow-*`, `--duration-*`, `--ease-*`, `--aspect-*`, `--height-*`, `--container-*`, `--breakpoint-*`, `--z-*`, `--border-*`, `--opacity-*`, `--scroll-*`) without a corresponding YAML extension token are orphans. Either drift (the YAML deleted a token, the CSS wasn't refreshed) or hand-authored CSS that bypassed the YAML.

**Fix proposal**: either remove the orphan from CSS (drift cleanup) or add the corresponding YAML token (formalize the brand decision in DESIGN.md, then re-export to confirm).

### `extension-broken-ref` (error)

Every prose reference to an extension token (`{motion.duration-reveal-slow}` or backticked `` `motion.duration-reveal-slow` ``) must resolve to a token defined in the YAML extension namespaces.

**Fix proposal**: define the missing token under the named namespace, or correct the reference to an existing token. The error message includes the source line number.

## CSS auto-detection

Probes the project tree below the DESIGN.md path for the first matching file:

| Order | Path |
|-------|------|
| 1 | `--css <path>` argument |
| 2 | `src/app/globals.css` |
| 3 | `src/styles/globals.css` |
| 4 | `src/style.css` |
| 5 | `app/globals.css` |
| 6 | `src/app/global.css` |

When none match, exits `1` with `RESULT: status=css-not-found`. The user must pass `--css <path>` explicitly, or scaffold the CSS layer (`/design-system export tailwind <path> > src/app/globals.css`).

## Report template

```markdown
# DESIGN.md extension audit — <path>

**CSS layer**: `<css-path>`
**Status**: <icon> <summary line>

## Errors (<n>)

<per-finding block>

## Warnings (<n>)

<per-finding block>

## Next steps

- [ ] Fix every error before shipping
- [ ] Review warnings — fix or accept
- [ ] Re-run `/design-system audit-extensions <path>` after changes
```

Per-finding block shape:

```markdown
### `<rule-name>`

**Token**: `<namespace>.<token-name>` (or **CSS variable**: `--<prefix>-<name>` for orphans)
**Where**: <DESIGN.md prose line N | YAML | CSS @theme>

<message>

**Fix proposal**:
<concrete option(s) per the rule>
```

Status icon convention:

- `✅ clean` — 0 errors, 0 warnings
- `⚠️ <n> warnings — review` — 0 errors, ≥1 orphan or non-standard
- `❌ <n> errors — fix before shipping` — any errors present

## Output schema (`--json`)

```json
{
  "summary": { "errors": 0, "warnings": 0, "infos": 0 },
  "findings": {
    "errors": [
      {
        "rule": "extension-broken-ref",
        "namespace": "motion",
        "token": "duration-reveal-extra-slow",
        "line": 142,
        "message": "Prose references `motion.duration-reveal-extra-slow` (line 142) but token not defined under `motion:` YAML"
      }
    ],
    "warnings": [],
    "infos": []
  }
}
```

## When to run

- After `/design-system export tailwind <path>` — confirm the mirror is in sync.
- Before opening a PR that touched DESIGN.md or `globals.css`.
- In CI alongside `/design-system audit` — both must pass.

## Edge cases

- **No extension namespaces in DESIGN.md.** Exits `0` with all-zero findings — there is nothing to audit. Skip silently.
- **No CSS file found.** Exits `1` with `RESULT: status=css-not-found`. Suggest `--css <path>` or running export to scaffold.
- **CSS file has no `@theme` block.** Treats as empty mirror — every YAML extension token will report `extension-missing-css`. Suggest merging the export output into the file.
- **Custom namespace names not in the curated list.** The script's mapping table is fixed (10 namespaces). A future namespace (e.g., `dimensionality:` for spatial-organic projects) requires updating the script and `extended-tokens.md` together — declare it intentionally rather than letting it slip in unaudited.

## Post-edit invariant

After any edit to DESIGN.md extension YAML or `globals.css` `@theme`, re-run `audit-extensions` and confirm exit 0. A mutation that leaves orphans or broken refs is not done.
