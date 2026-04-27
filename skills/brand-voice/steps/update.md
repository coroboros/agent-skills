# `update` subcommand

Refresh an existing `BRAND-VOICE.md` from new sources without losing manual edits.

## Invocation

```bash
/brand-voice update -u https://example.com/v2          # add a new URL source
/brand-voice update -d ~/style-2026/                   # add a new folder source
/brand-voice update -f ./assets/voice.md               # default target ./BRAND-VOICE.md
/brand-voice update -o ./assets/voice.md -u <url>      # custom target
```

## Flags

Same as `extract`:

| Flag | Meaning |
|------|---------|
| `-u <url>` | URL source |
| `-n <id\|url>` | Notion page |
| `-d <dir>` | Directory of MDs |
| `-f <file>` | Single MD file |
| `-o <path>` | Target voice doc (default: `./BRAND-VOICE.md`) |

At least one source flag is required — `update` does not enter interview mode (use `extract` for that).

## Workflow

### 1. Read existing doc

- Resolve target path. Default `./BRAND-VOICE.md`.
- If the target does not exist, abort: *"No `BRAND-VOICE.md` at `<path>`. Use `/brand-voice extract` first."*
- `Read` the full file. `split_frontmatter` to separate YAML from prose. Parse YAML via `python3 ${CLAUDE_SKILL_DIR}/scripts/extract_rules.py <path>` for a flat view.
- **Inheritance check** — if the target declares `voice.extends`, `update` operates on the *child file's delta only*. The parent is not modified, and the merge described in step 4 applies to the child's declarations against new sources — not against the inherited parent values. Authors who want to update the parent run `/brand-voice update <parent_path>` separately.

### 2. Detect manual sections

A section is *manual* if its first line under the H2 is the HTML comment `<!-- manual: true -->`. Track these and never touch them.

### 3. Resolve new sources

Per `references/source-resolution.md`. Aggregate into a working draft.

### 4. Compute the merge

For each YAML field:

- **`voice.source_urls`** — append new entries, deduplicate.
- **`voice.last_updated`** — bump to today's ISO date.
- **`forbidden_lexicon`** — union of old and new. Surface conflicts (a term in old's `required_lexicon` and new's `forbidden_lexicon`) via `AskUserQuestion`.
- **`required_lexicon`** — union, dedupe.
- **`rewrite_rules`** — match by `rule_id`. New rules with new IDs are added. Rules with the same ID but different `reject`/`accept` trigger a conflict — surface via `AskUserQuestion`.
- **`sentence_norms`** — keys present in both: surface conflict if values differ. Keys only in new: add. Keys only in old: keep.
- **`forbidden_patterns`** — union, dedupe.
- **`contexts`** — merge per context name. Conflicts at the leaf-key level surface via `AskUserQuestion`.
- **`pronouns`** — same as `sentence_norms`.

For each prose section:

- **Manual sections** — preserved verbatim. Marker stays.
- **Required sections** (1–11) — re-synthesise from the merged data. The new prose draws from both old and new sources; the user reviews the diff.
- **Custom non-manual sections** — re-synthesised if they map to one of the canonical sections (e.g., user added `## 12. Voice in code reviews` with no marker → re-synthesise). Otherwise preserved.

### 5. Show diff

Build a unified-style prose diff between old and new prose, plus a YAML diff for the frontmatter. Format:

```
Frontmatter changes
-------------------
+ source_urls: + 1 (https://example.com/v2)
+ last_updated: 2026-04-27 (was: 2026-01-12)
+ forbidden_lexicon: + 3 (utopia, frictionless, holistic)
~ rewrite_rules: 1 modified (specific-over-abstract-speed: accept text changed)

Prose changes
-------------
Section 1 (Core voice attributes): unchanged
Section 2 (Rewrite rules): + 1 row in 'Specific over abstract' table
Section 10 (Counter-examples): + 1 entry
Section 11 (Reference texts): + 1 line

Manual sections preserved
-------------------------
Section 12 (Brand mythology) — unchanged

Apply? (yes/no)
```

The user must answer `yes` explicitly.

### 6. Lint and write

- Build the merged file in a temp file.
- `voice_lint.py` — must return 0 (GREEN/YELLOW). RED → fix and re-lint.
- On user `yes`: `Edit` (not `Write`) the target file in place. `Edit` preserves any uncommitted manual tweaks the user made between read and write.

### 7. Post-write report

```
✓ BRAND-VOICE.md updated at ./BRAND-VOICE.md
  → 11 forbidden lexicon terms added (was 23, now 26)
  → 1 rewrite rule modified, 1 added (was 10, now 11)
  → Source: + https://example.com/v2

Audit:
- /brand-voice show --rules     # confirm the rules look right
- /brand-voice diff HEAD~1 HEAD # see exactly what changed
- /humanize-en -f BRAND-VOICE.md draft.md  # apply on a draft
```

## Edge cases

- **Target exists but lint fails (corrupted before update)** — surface the lint errors. Offer to abort or to overwrite with the new synthesis (loses the corruption fix; user must confirm).
- **Conflict the user can't decide** — record both interpretations as `<old>` and `<new-from-source>` comments in YAML. Mark `voice.source: "extract:unresolved"`. The user resolves later.
- **No actual change** — if the merge produces a file byte-identical to the original (sources contributed nothing new), report *"No changes — sources contributed nothing not already in the doc"* and exit without writing.
- **User added a manual section that conflicts with a re-synthesised one** — preserve the manual section, surface the conflict, suggest moving it (e.g., rename `## 1. Core voice attributes` to `## 1bis. Internal note on attributes` if both want section 1).
- **Target declares `voice.extends`** — `update` operates only on the child's declarations. New sources contribute to the child's `forbidden_lexicon`, `rewrite_rules`, etc.; they do not pull parent values into the child file. Manual `<!-- manual: true -->` sections in the child take precedence over re-synthesis at the merged level. To propagate a change up the chain, run `/brand-voice update <parent_path>` against the ancestor.
