# `show` subcommand

Print a flat list of testable rules from the voice doc — no prose, no rationale, no headings. Designed for inclusion in another skill's prompt.

## Invocation

```bash
/brand-voice show                              # default: --rules, target ./BRAND-VOICE.md
/brand-voice show --rules                      # only the testable rules
/brand-voice show --examples                   # only the rewrite_rules examples
/brand-voice show --all                        # rules + examples + counter-examples
/brand-voice show -o ./assets/voice.md         # custom target
```

## Flags

| Flag | Meaning |
|------|---------|
| `-o <path>` | Target voice doc (default: `./BRAND-VOICE.md`) |
| `--rules` | Print the testable rule block (default) |
| `--examples` | Print only the `rewrite_rules` `reject → accept` table |
| `--all` | Print rules, rewrite_rules examples, and counter-examples section |

## Workflow

### `--rules` (default)

Run `python3 ${CLAUDE_SKILL_DIR}/scripts/extract_rules.py <target>`. Stream stdout directly to the user. Output shape per `references/schemas.md` § extract_rules.py.

This is the same path `humanize-en -f` uses internally. `show --rules` is the human-readable verification: "what rules will downstream skills see?"

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
