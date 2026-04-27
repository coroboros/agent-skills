# `validate` subcommand (aliases: `lint`, `check`)

Lint a `BRAND-VOICE.md` against the canonical format. Read-only. Use to verify a hand-edited doc, a doc imported from another repo, or to check existing files when the canonical format evolves.

## Invocation

```bash
/brand-voice validate                          # check ./BRAND-VOICE.md
/brand-voice validate path/to/voice.md         # check a specific file
/brand-voice lint ./assets/voice.md            # alias
/brand-voice check                             # alias
/brand-voice validate --json                   # raw JSON output (CI)
/brand-voice validate -o ./assets/voice.md     # explicit -o path
```

## Flags

| Flag | Meaning |
|------|---------|
| `[path]` positional | Target voice doc (default: `-o` value, else `./BRAND-VOICE.md`) |
| `-o <path>` | Same target as the positional, kebab-aligned with the rest of the skill |
| `--json` | Emit raw JSON per `references/schemas.md` § voice_lint.py instead of the human-readable report |

## Workflow

### 1. Resolve target path

In order of precedence: positional argument, `-o <path>` flag, `./BRAND-VOICE.md`. If the resolved path does not exist, exit with a clear error: *"`<path>` not found. Run `/brand-voice extract` first."*

### 2. Run the linter

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/voice_lint.py <path>
```

The script returns JSON per [`references/schemas.md`](../references/schemas.md) § voice_lint.py. Three verdicts: `GREEN` (zero errors, zero warnings), `YELLOW` (warnings only), `RED` (errors).

### 3. Format the report

If `--json` was passed, stream the raw JSON to stdout and exit with the script's exit code (0 for GREEN/YELLOW, 1 for RED).

Otherwise, format human-readably:

```
BRAND-VOICE.md — validation report
==================================
Verdict: GREEN | YELLOW | RED
Path:    <resolved path>
Stats:   <N> sections (<N> required, <N> recommended), <N> rules, <N> forbidden lexicon

Errors (<N>):
  ✗ <code> [<field>] — <message>
    line: <N>

Warnings (<N>):
  ⚠ <code> [<field>] — <message>
    line: <N>
```

Sort errors before warnings. Within each, sort by line number ascending. Cap the report at 30 errors + 30 warnings; if exceeded, append a final line *"… and N more (run with `--json` for the full list)"*.

### 4. Surface fix suggestions

For each error code, append a one-line suggested fix per [`references/schemas.md`](../references/schemas.md) § "Error codes — fix strategy":

| Code | Suggested fix |
|---|---|
| `frontmatter-invalid-yaml` | Fix YAML syntax at the line cited. |
| `missing-required-field` | Add the missing field to the frontmatter. |
| `invalid-field-value` | Update the value to satisfy the constraint. |
| `duplicate-rule-id` | Rename one of the duplicates (rule_ids must be unique). |
| `missing-section` | Add the required H2 section. |
| `section-out-of-order` | Reorder the sections to canonical order. |
| `duplicate-section` | Merge or rename duplicate H2 headings. |

For warnings, no suggested fix (warnings are informational). The user decides whether to address them.

### 5. Exit code

- `0` if verdict is GREEN or YELLOW.
- `1` if verdict is RED.
- `2` if the file does not exist or is not readable.

CI-friendly: a pre-commit hook can run `/brand-voice validate` and fail the commit if exit > 0.

## Use cases

- **Hand-edits** — the user added a section by hand and wants to confirm the doc still parses.
- **Spec evolution** — the canonical format moved from 11 to 4-required-7-recommended sections; an existing strict-format doc still passes validation; a future format change can be detected by re-running validate.
- **Cross-repo import** — pulling a `BRAND-VOICE.md` from a sister repo (per the cross-repo distribution patterns in `SKILL.md`); validate confirms the file is compatible.
- **Pre-commit hook** — CI runs `/brand-voice validate --json` on every PR that touches `BRAND-VOICE.md`. Exit code gates merge.
- **Drift detection over time** — pair with `/brand-voice diff <ref> HEAD` to see what changed; pair with `/brand-voice validate` to see if the changes still parse.

## Output examples

### GREEN

```
BRAND-VOICE.md — validation report
==================================
Verdict: GREEN
Path:    ./BRAND-VOICE.md
Stats:   11 sections (4 required, 7 recommended), 12 rules, 27 forbidden lexicon

(no errors, no warnings)
```

### YELLOW (minimal doc — 4 required sections only)

```
BRAND-VOICE.md — validation report
==================================
Verdict: YELLOW
Path:    ./BRAND-VOICE.md
Stats:   4 sections (4 required, 0 recommended), 1 rule, 2 forbidden lexicon

(no errors)

Warnings (7):
  ⚠ recommended-section-missing [section:tone by context] — recommended H2 section is missing
  ⚠ recommended-section-missing [section:pronouns and self-reference]
  ⚠ recommended-section-missing [section:format conventions]
  ⚠ recommended-section-missing [section:visual pairing]
  ⚠ recommended-section-missing [section:quick diagnostic]
  ⚠ recommended-section-missing [section:counter-examples]
  ⚠ recommended-section-missing [section:reference texts]

Verdict YELLOW: doc is valid but missing 7 recommended sections. To address, run /brand-voice update with new sources, or hand-edit the missing sections.
```

### RED (broken doc)

```
BRAND-VOICE.md — validation report
==================================
Verdict: RED
Path:    ./BRAND-VOICE.md
Stats:   8 sections (3 required, 5 recommended), 11 rules, 0 forbidden lexicon

Errors (3):
  ✗ missing-required-field [forbidden_lexicon] — required frontmatter field 'forbidden_lexicon' is missing or wrong type
    Fix: Add the missing field to the frontmatter.
  ✗ duplicate-rule-id [rewrite_rules[3].rule_id] — rule_id 'no-hedging' duplicates rewrite_rules[1]
    Fix: Rename one of the duplicates (rule_ids must be unique).
  ✗ missing-section [section:rewrite rules — do/don't] — required H2 section is missing
    Fix: Add the required H2 section.

Warnings (1):
  ⚠ recommended-section-missing [section:visual pairing]

Verdict RED: 3 errors block the doc from being considered valid. Fix the errors before running /humanize-en -f against this file.
```

## Edge cases

- **Empty file** — exit 2 with *"`<path>` is empty"*. Don't lint, don't crash.
- **File is not UTF-8** — exit 2 per `voice_lint.py` exit code spec. Surface the encoding error.
- **YAML parses but is not a mapping** (e.g., it's a list) — `frontmatter-invalid-yaml` error. Reported by the script.
- **No frontmatter at all** — `frontmatter-invalid-yaml` error with line 1 ("file must start with `---`"). Reported by the script.
- **Path does not exist** — exit 2 with the suggestion to run `/brand-voice extract`.
- **`--json` and human-format both requested** — `--json` wins. The flag toggles output mode.
