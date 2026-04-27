# `show` subcommand

Print a flat list of testable rules from the voice doc — no prose, no rationale, no headings. Designed for inclusion in another skill's prompt.

## Invocation

```bash
/brand-voice show                              # default: --rules, target ./BRAND-VOICE.md
/brand-voice show --rules                      # only the testable rules
/brand-voice show --examples                   # only the rewrite_rules examples
/brand-voice show --all                        # rules + examples + counter-examples
/brand-voice show --raw                        # child-only — skip extends chain resolution
/brand-voice show --chain                      # print the resolution chain (root → child)
/brand-voice show --explain                    # annotate each rule with its origin file
/brand-voice show --legacy                     # v1 minimal output (back-compat)
/brand-voice show -o ./assets/voice.md         # custom target
```

## Flags

| Flag | Meaning |
|------|---------|
| `-o <path>` | Target voice doc (default: `./BRAND-VOICE.md`) |
| `--rules` | Print the testable rule block (default) |
| `--examples` | Print only the `rewrite_rules` `reject → accept` table |
| `--all` | Print rules, rewrite_rules examples, and counter-examples section |
| `--raw` | Skip `voice.extends` chain resolution; print child-only rules |
| `--chain` | Print the resolution chain instead of rules: `child.md → parent.md → grandparent.md (depth N)` |
| `--explain` | Annotate each rule with `# from <relpath>` origin file |
| `--explain-json` | Emit structured provenance JSON instead of plain text |
| `--legacy` | Emit the v1 minimal output (no `core_attributes`, `contexts`, `source_urls`) for back-compat consumers |
| `--allow-extends-outside-skill` | Suppress the `extends-path-outside-skill` warning when resolving the chain |

## Workflow

### `--rules` (default)

Run `python3 ${CLAUDE_SKILL_DIR}/scripts/extract_rules.py <target>`. Stream stdout directly to the user. Output shape per `references/schemas.md` § extract_rules.py.

This is the same path `humanize-en -f` uses internally. `show --rules` is the human-readable verification: "what rules will downstream skills see?"

By default, when the target declares `voice.extends`, the chain is resolved automatically and the rules block reflects the merged voice. Pass `--raw` to inspect the child file's declarations only.

### `--chain`

Print the resolved inheritance chain, root-first:

```
target: ./BRAND-VOICE-FOUNDER.md
chain (depth 1):
  ./BRAND-VOICE.md            (root)
  ./BRAND-VOICE-FOUNDER.md    (this)
```

Files that declare no `voice.extends` print a single line: *"target has no inheritance chain."*

### `--explain` / `--explain-json`

`--explain` runs `extract_rules.py --explain` and streams the result. Each merged rule gains a `# from <relpath>` suffix so the author sees which file in the chain contributed it. Useful for audit ("why is this rule here?") and review ("did the override land where I wanted?").

`--explain-json` emits structured provenance for tooling. See `references/schemas.md` § extract_rules.py for the schema.

### `--examples`

Read the target file, parse the frontmatter, emit the `rewrite_rules` as a Markdown table:

```
| Rule | Reject | Accept |
|------|--------|--------|
| no-hedging-imperative | It might be worth considering... | Use X. |
| specific-over-abstract-speed | significantly faster | <cite a number — e.g. 3.2× faster> |
| ... | ... | ... |
```

Sorted alphabetically by `rule_id`. No truncation — even long entries print in full.

### `--all`

In order:

1. The `--rules` block.
2. The `--examples` table.
3. The `## 10. Counter-examples` prose section, verbatim.

Concatenated with `---` separators between blocks. Designed for "give me the whole executable contract in one screen."

### Output formatting

- Default: plain text to stdout (no JSON wrapper, no headers).
- The user can redirect to a file (`/brand-voice show > rules.txt`) or pipe to clipboard.
- No `-s` flag — `show` is read-only and ephemeral by design. To save, the user redirects.

## Why `show` is its own subcommand

`humanize-en` calls `extract_rules.py` directly under the hood. `show` exists for the user, not the toolchain:

- **Verification** — *"did my voice doc end up looking like I expected?"* — without scrolling through 230 lines of prose.
- **Sharing** — paste the rules into a Slack thread, a code review, an instructions section.
- **Integration** — drop the rules block into another tool's config (`.eslintrc`, custom linter, AI prompt) without writing a parser.

The output is line-oriented and stable. Tooling can grep it.

## Edge cases

- **Target file missing** — error: *"`<path>` not found. Run `/brand-voice extract` first."*
- **Target frontmatter invalid** — error from `extract_rules.py` (exit 1). Surface the error message to the user and suggest `/brand-voice` lint check (or just re-running `voice_lint.py` directly).
- **`--examples` but `rewrite_rules` is empty** — print *"No rewrite_rules in `<target>`."* and exit 0. Empty is a legal state.
- **`--all` but section 10 is missing** — `voice_lint.py` should have caught this earlier. Print the rules and examples blocks; for section 10 print *"(section 10 missing — re-run `/brand-voice update` or fix manually)"*.
- **Chain resolution fails** (`extends-cycle`, `extends-depth-exceeded`, `extends-parent-not-found`) — `extract_rules.py` exits 1 with the error code on stderr. Surface the error and suggest `/brand-voice validate <target>` for the full diagnostic. `--raw` is the workaround when the user wants to inspect the broken child anyway.
- **`--explain` on a target without `voice.extends`** — equivalent to default `--rules`; no provenance to annotate. Print the rules block as usual.
