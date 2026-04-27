# `diff` subcommand

Show what changed between two versions of a `BRAND-VOICE.md`. Read-only.

## Invocation

```bash
/brand-voice diff                                # working tree vs HEAD
/brand-voice diff HEAD~5 HEAD                    # 5 commits back vs HEAD
/brand-voice diff old.md new.md                  # two file paths
/brand-voice diff origin/main HEAD               # vs remote main
/brand-voice diff -o ./assets/voice.md           # custom file path, working tree vs HEAD
```

## Flags

| Flag | Meaning |
|------|---------|
| `-o <path>` | Target voice doc (default: `./BRAND-VOICE.md`) |
| (positional refs/paths) | One or two — git refs or file paths |

## Workflow

### 1. Resolve the two sides

The two positional arguments determine what to compare:

| Args | Left | Right |
|------|------|-------|
| (none) | `git show HEAD:<target>` | working tree `<target>` |
| `<ref>` | `git show <ref>:<target>` | working tree `<target>` |
| `<ref-a> <ref-b>` | `git show <ref-a>:<target>` | `git show <ref-b>:<target>` |
| `<path-a> <path-b>` | `Read` `<path-a>` | `Read` `<path-b>` |

If `<target>` is not under git, error: *"`<target>` is not tracked by git. Pass two file paths to diff."*

### 2. Parse both sides

For each side:

- `split_frontmatter` to separate YAML from prose.
- `parse_yaml_minimal` to load the frontmatter as data.
- `list_h2_sections` to enumerate prose sections.

If parsing one side fails, surface the error and degrade to `git diff --no-prefix` output (raw diff, no semantic interpretation).

### 3. Compute semantic diff

#### YAML changes

For each frontmatter field:

- **List fields** (`forbidden_lexicon`, `required_lexicon`, `forbidden_patterns`, `voice.source_urls`) — show added (`+`), removed (`-`), unchanged count.
- **Object fields** (`sentence_norms`, `pronouns`, `contexts.*`) — show key-by-key adds, removes, modifications.
- **`rewrite_rules`** — match by `rule_id`. Show:
  - `+ rule_id` for new rules
  - `- rule_id` for removed rules
  - `~ rule_id (reject/accept changed)` for modifications
- **Scalar fields** (`voice.name`, `voice.last_updated`) — show old → new.

#### Prose changes

For each section:

- *unchanged* — bytes-identical (after normalising trailing whitespace).
- *prose changed* — same heading, different content. Show a high-level summary (e.g., "+ 1 row in 'No hedging' table") rather than full unified diff. Full diff goes under a `<details>` collapsible.
- *added* — section present in right, absent in left.
- *removed* — section present in left, absent in right.
- *renamed* — the H2 heading text changed.

#### Manual sections

Manual sections (with `<!-- manual: true -->`) are diffed but flagged as `(manual)` in the output so the reviewer knows they were authored by hand, not synthesised.

### 4. Output format

```
BRAND-VOICE.md — diff <left-ref> → <right-ref>
==============================================

Frontmatter
-----------
+ source_urls: + 1 (https://example.com/v2)
+ last_updated: 2026-04-27 (was: 2026-01-12)
- forbidden_lexicon: - 1 (game-changer); + 3 (utopia, frictionless, holistic)
~ rewrite_rules:
    + no-marketing-cliche (reject: "world-class")
    ~ specific-over-abstract-speed (accept: changed)

Prose
-----
✓ Section 1 (Core voice attributes)         — unchanged
✓ Section 2 (Rewrite rules)                 — + 1 table row
✓ Section 3 (Forbidden lexicon and patterns) — + 3 lines
✓ Section 10 (Counter-examples)             — + 1 entry
✓ Section 12 (Brand mythology, manual)      — unchanged

Stats
-----
Lines:       231 → 246  (+15)
Rules:        10 →  11  (+1)
Lexicon:      23 →  26  (+3)
Sections:     11 →  11  (unchanged)
```

### 5. Verdict line

The last line is a single-word verdict for tooling:

- `verdict: clean` — no changes.
- `verdict: minor` — additions only, no removals.
- `verdict: major` — removals or modifications to existing rules. Suggests the user re-test downstream prose.

## Why diff matters

A brand voice that drifts silently produces inconsistent prose. `/brand-voice diff` is the audit trail. Run it before merging a `update` PR. Run it monthly against the previous quarter to spot voice creep. The verdict line is grep-friendly for CI integration.

## Edge cases

- **Both sides identical** — output the verdict line `verdict: clean` and nothing else (above-the-fold UX).
- **Heading reordered** — surface as a *renamed*/*reordered* warning. Section order is normative; reordering changes the doc's contract for downstream consumers.
- **YAML field added** that does not exist in `canonical-format.md` — diff shows the addition with a `(custom field)` annotation; downstream consumers may ignore it.
- **Both sides have YAML parse errors** — fall back to raw `git diff` output. The diff is still informational.
