# `diff` subcommand

Compare two DESIGN.md versions to detect token-level and lint-finding regressions.

## Invocation

```bash
/design-system diff                               # ./DESIGN.md vs HEAD (git)
/design-system diff ./DESIGN.md                   # same as above, explicit path
/design-system diff old.md new.md                 # two-file diff
/design-system diff -s                            # save the report
/design-system diff --json                        # raw CLI JSON
```

Smart defaults keep the common case (reviewing local changes before commit) a single-word invocation.

## Flags

| Flag | Meaning |
|------|---------|
| `-s` | Save the formatted report to `.claude/output/design-system/diff/{slug}/report.md` |
| `-S` | Force no-save |
| `--json` | Skip report composition; print raw CLI JSON |
| `--base <ref>` | Git comparison base for the single-arg mode (default: `HEAD`) |

## Workflow

**Two-file mode** (2 positional args):

1. Verify both files exist.
2. Run the script:
   ```bash
   bash ${CLAUDE_SKILL_DIR}/scripts/diff.sh <before> <after>
   ```
3. Parse `RESULT: regression=true|false` and the JSON at `RESULT: json=<tmp>`.
4. Compose the report.

**Git-aware mode** (0 or 1 positional args):

1. Resolve target path (default `./DESIGN.md` or the single arg).
2. Verify the file is tracked by git (`git ls-files --error-unmatch <path>`). If untracked, fall back to the two-file mode with an explanatory error.
3. Extract the base version to a temp file:
   ```bash
   base_ref="${--base:-HEAD}"
   git show "${base_ref}:${path}" > /tmp/design-diff-base-XXXXXX.md
   ```
4. Run the script with the temp file as `<before>` and the working-tree file as `<after>`.
5. Clean up the temp file after parsing.

## Report template

```markdown
# DESIGN.md diff — <before> → <after>

**Regression**: <icon> <regression line>

## Token changes

### Colors
- Added: `<list>`
- Removed: `<list>`
- Modified: `<list>` (show before → after)

### Typography / Rounded / Spacing / Components
<same structure per group>

## Lint-finding delta

- New errors: <list — each with the finding message>
- New warnings: <list>
- Resolved findings: <list>

## Next steps

- [ ] Review each token change — is it intentional?
- [ ] If regression=true, address the new errors/warnings before shipping
- [ ] Re-run audit on <after> to confirm lint status
```

**Regression icon convention**:
- `✅ no regression` — same or fewer errors/warnings in `<after>`
- `⚠️ regression detected` — more errors/warnings in `<after>`

The CLI's `diff` command sets `regression: true` when the "after" file has more errors or warnings than the "before" file. This is stricter than "any token change" — a benign palette expansion that adds tokens without breaking references is NOT a regression.

## Interpreting token changes

**Added tokens**: usually intentional expansion. Flag if the palette grows without new component consumers — may trigger `orphaned-tokens` in a subsequent audit.

**Removed tokens**: check for broken references in `<after>`. The lint-finding delta will surface any `broken-ref` the removal introduced.

**Modified tokens**: the most common regression vector. A color value change might silently alter every component that references it — review the downstream impact explicitly.

## Use cases

**PR review.** Reviewer runs `/design-system diff` against the PR base to understand what changed semantically, not just textually. `git diff` shows YAML lines; `design-system diff` shows token-level deltas.

**Migration verification.** After `/design-system migrate <old>`, run `diff` between the backup (`<old>.legacy.*`) and the new file to confirm the intended tokens were preserved.

**Release gate.** Wire into CI:
```bash
npx @google/design.md diff origin/main:DESIGN.md DESIGN.md || exit 1
```
The skill's `diff` wraps this with a human-readable summary — useful locally, the raw CLI is better for CI.

## Edge cases

- **`<before>` not tracked by git** (git-aware mode): surface the error, ask the user to provide an explicit `<before>` path.
- **Identical files**: report `✅ no regression` with empty change lists; suggest no action.
- **Brand-new file** (no `<before>` in git): suggest running `audit` on the new file instead of `diff`.
