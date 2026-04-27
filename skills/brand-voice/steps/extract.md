# `extract` subcommand

Ingest one or more sources, synthesise the canonical voice doc, write to disk.

## Invocation

```bash
/brand-voice extract -u https://example.com/about              # URL only
/brand-voice extract -f ~/notes/style.md                       # local MD only
/brand-voice extract -d ~/style-archive/                       # folder of MDs
/brand-voice extract -n <notion-page-id>                       # Notion via MCP
/brand-voice extract                                           # interview mode
/brand-voice extract -u https://x.com -f ./notes.md            # combined sources
/brand-voice extract -u https://x.com -o ./assets/voice.md     # custom output path
/brand-voice extract -s -u https://x.com                       # also save under .claude/output/
```

## Flags

| Flag | Meaning |
|------|---------|
| `-u <url>` | URL source — `WebFetch` direct, fallback to `/markitdown -s <url>` |
| `-n <id\|url>` | Notion page — via `mcp__claude_ai_Notion__notion-fetch` |
| `-d <dir>` | Directory of MD files — `Glob`, then aggregate |
| `-f <file>` | Single MD/MDX/TXT file — `Read` direct |
| `-o <path>` | Output path (default: `./BRAND-VOICE.md`) |
| `-s` | Also save a copy under `.claude/output/brand-voice/{slug}/voice.md` for pipeline history |
| `-S` | Disable `-s` if it was set ambiently |

If no source flag is given, the skill enters interview mode (8 questions per `references/interview-questions.md`).

## Workflow

### 1. Pre-flight

- If `-o <path>` is omitted, target = `./BRAND-VOICE.md` at the current working directory.
- If the target exists, abort with:
  > "`<path>` already exists. To refresh it, use `/brand-voice update`. To replace it, delete it first."
  Do not overwrite. The canonical file is git-versioned — letting `extract` overwrite breaks history.
- If the parent directory of `-o` does not exist, abort with a clear `mkdir -p` suggestion.

### 2. Source resolution

Resolve each `-u`, `-n`, `-d`, `-f` per `references/source-resolution.md`. Aggregate into a working draft.

If zero sources, dispatch interview mode:

1. Read `references/interview-questions.md`.
2. Ask each question via `AskUserQuestion`, one at a time. Question 1 (identity) and at least one of question 2 or question 5 are required — without those there is nothing to write.
3. Stitch answers into the working draft with one H2 per question.

### 3. Synthesis

Read `references/canonical-format.md` for the schema, `references/example-chanel.md` for a complete reference example.

Synthesise the working draft into the canonical format:

- **YAML frontmatter** — fill `voice.name`, `voice.source_urls`, `voice.last_updated` (today's date in ISO), `voice.source` (`extract` or `interview`). Populate `forbidden_lexicon`, `rewrite_rules` (with kebab-case `rule_id`s), `sentence_norms` (numeric where possible, fall back to defaults from interview if absent), `forbidden_patterns`, `contexts`, `pronouns`.
- **Eleven prose sections** — write each section drawing from the working draft. For `## 10. Counter-examples`, generate 3-5 real bad rewrites showing what the rules prevent (do not skip — this section makes the doc actionable for downstream skills).

Apply the synthesised voice to the prose itself: the doc must pass its own filter (no marketing voice if the brand forbids it, no rule-of-three if `forbidden_patterns` lists it, etc.). The brand voice doc is its own first reader.

### 4. Lint before write

Write the synthesised content to a temp file under `/tmp/`. Run:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/voice_lint.py /tmp/<file>.md
```

- Exit 0 (GREEN/YELLOW) → proceed.
- Exit 1 (RED) → fix the errors and re-lint. Do not write to disk with errors.
- Exit 2 (I/O) → surface the error, abort.

### 5. Source contribution summary

Print to the user before writing:

```
Source contribution summary
---------------------------
URL  https://example.com/about           → 12 rules, 24 lexicon terms, 5 attributes
File ~/notes/style.md                    → 4 rules, 8 lexicon terms, 1 context
                                            (skipped: 2 entries that conflicted with primary URL)

Lint: GREEN (0 errors, 0 warnings)
File: ./BRAND-VOICE.md (231 lines, 11 sections, 11 rules, 26 forbidden lexicon)

Apply? (yes/no)
```

The user must answer `yes` explicitly. No silent write.

### 6. Write

On `yes`:

- `Write` to `-o <path>` (default `./BRAND-VOICE.md`).
- If `-s` is set, also `Write` to `.claude/output/brand-voice/{slug}/voice.md`. The slug is derived from `voice.name` (kebab-case, max 5 words).

### 7. Post-write report

```
✓ BRAND-VOICE.md created at ./BRAND-VOICE.md
  → 231 lines, 11 sections, 11 rewrite rules, 26 forbidden terms
  → Source: extract from <list of sources>

Next:
- Run `/brand-voice show --rules` to confirm the rules look right.
- Apply on a draft: `/humanize-en -f ./BRAND-VOICE.md <your-draft.md>`
- Update later: `/brand-voice update -u <new-source>`
```

## Edge cases

- **All sources fail** — abort with the list of errors. Suggest interview mode (`/brand-voice extract` with no flags) or correcting the failed sources.
- **One source fails, others succeed** — proceed with the survivors. Print the failure inline. The user can re-run later.
- **Lint returns RED on first synthesis** — fix the synthesis without bothering the user. Common cause: missing `## 10. Counter-examples` (LLM forgot to include the section). Re-synthesise.
- **Lint returns YELLOW after fix attempt** — present warnings to the user but proceed. YELLOW is acceptable per `references/schemas.md`.
- **Conflict between sources (e.g., one says 'we' is forbidden, another says it's OK)** — surface via `AskUserQuestion`, never silent override. Record the user's choice in the doc.
- **Notion MCP not installed when `-n` is passed** — error per `references/source-resolution.md`. Suggest exporting Notion → MD and using `-d`.
- **Source contributes zero rules** — proceed but warn: "`<source>` contributed nothing useful — typo, empty page, or non-prose content."
