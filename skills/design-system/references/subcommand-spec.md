# `spec` subcommand

Emit the canonical DESIGN.md format specification — always reflects the installed CLI version.

## Invocation

```bash
/design-system spec                         # full spec, markdown, stdout
/design-system spec --rules                 # spec + active lint rules table
/design-system spec --rules-only            # lint rules only
/design-system spec --json                  # machine format
/design-system spec -o .claude/context/design-md-spec.md     # write to file
```

## Flags

| Flag | Meaning |
|------|---------|
| `--rules` | Append the active linting rules table to the spec |
| `--rules-only` | Output only the linting rules (skip the spec body) |
| `--json` | Machine-readable JSON instead of markdown |
| `-o <path>` | Write to file (default: stdout) |

All flags pass through to the underlying `designmd spec` invocation.

## Workflow

Use the bundled resolver so a project-local dependency works without adding `node_modules/.bin` to `PATH`:

```bash
bash "$SKILL_DIR/scripts/spec.sh" <flags> > <output>
```

1. **Resolve CLI availability**: nearest directly declared project `node_modules/.bin/designmd`, then `PATH`. If unavailable, return `designmd-missing` and suggest adding `@google/design.md` with the project's package manager.
2. **Compose the command** from flags.
3. **Invoke** and capture stdout.
4. **Write or print** based on `-o`.
5. **Report**: one line — `<bytes> bytes written to <path>` or `spec printed to stdout`.

## Use cases

**Agent context injection.** Drop the spec into an agent's context so it reasons from the canonical source rather than a cached understanding:

```bash
/design-system spec -o .claude/context/design-md-spec.md
# subsequent agent invocations see the always-fresh spec
```

Refresh this file when the installed upstream CLI version changes.

**Local reference refresh.** The skill ships `references/design-md-spec.md` as a concise handcrafted reference. For the raw authoritative version, `/design-system spec` beats reading the repo. Keep the local concise version for quick model reads (it's linked from `SKILL.md`); use the CLI-emitted one when you need the full normative text.

**Linting rules lookup.** When interpreting an audit finding, the rules table maps severity → rule name → check. `--rules-only --json` is compact and machine-parseable:

```bash
/design-system spec --rules-only --json | jq '.[] | select(.rule == "contrast-ratio")'
```

## When NOT to use

- **Authoring guidance**: `references/design-md-spec.md` is shorter and task-oriented. Use it when writing DESIGN.md content.
- **Sharing with humans**: link to [github.com/google-labs-code/design.md](https://github.com/google-labs-code/design.md) — the rendered GitHub page is friendlier than CLI output.

## Edge cases

- **Offline / CLI unavailable**: the wrapper returns `designmd-missing`. Use `references/design-md-spec.md` only as bundled authoring guidance; do not present it as live CLI output.
- **Old CLI installed**: if the installed binary is stale, the emitted spec will not reflect recent rule additions. Flag the maintenance gap instead of downloading an update during agent work.
