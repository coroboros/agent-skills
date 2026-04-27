# JSON schemas — `voice_lint.py` and `extract_rules.py`

Stable contracts. Other skills consume these outputs; changes here are breaking changes.

## `voice_lint.py` output

```json
{
  "path": "BRAND-VOICE.md",
  "verdict": "GREEN" | "YELLOW" | "RED",
  "errors": [
    {
      "code": "frontmatter-invalid-yaml" | "missing-required-field" | "invalid-field-value" | "duplicate-rule-id" | "missing-section" | "section-out-of-order" | "duplicate-section" | "extends-cycle" | "extends-depth-exceeded" | "extends-parent-not-found" | "extends-parent-invalid" | "replace-without-extends" | "remove-without-extends" | "replace-conflict-with-extending" | "replace-on-unsupported-field" | "remove-on-unsupported-field" | "core-attribute-missing-id",
      "field": "voice.name" | "rewrite_rules[3].rule_id" | "section:1.core voice attributes" | null,
      "message": "human-readable explanation",
      "line": 42,
      "source": "child" | "parent:<relpath>" | "merged",
      "source_path": "BRAND-VOICE.md",
      "parent_errors": [ /* nested error objects, only on extends-parent-invalid */ ]
    }
  ],
  "warnings": [
    {
      "code": "empty-required-lexicon" | "no-source-urls" | "outdated-last-updated" | "recommended-section-missing" | "section-light-content" | "extends-path-outside-skill" | "rewrite-rule-overridden-by-child",
      "field": "...",
      "message": "...",
      "line": 17,
      "source": "child" | "parent:<relpath>" | "merged"
    }
  ],
  "stats": {
    "frontmatter_lines": 47,
    "prose_lines": 184,
    "total_lines": 231,
    "rule_count": 11,
    "forbidden_lexicon_count": 25,
    "section_count": 11
  },
  "chain": ["BRAND-VOICE.md", "BRAND-VOICE-FOUNDER.md"],
  "merged_stats": {
    "rule_count": 14,
    "forbidden_lexicon_count": 31
  }
}
```

`source`, `source_path`, and `parent_errors` are optional on every error/warning. `chain` and `merged_stats` are top-level optionals — present only when `voice.extends` resolved successfully. Order in `chain` is root-first.

### Verdict semantics

- **GREEN** — zero errors, zero warnings. Ship it.
- **YELLOW** — zero errors, one or more warnings. Acceptable but flag to the user.
- **RED** — one or more errors. Block.

### Exit codes

- `0` — verdict is GREEN or YELLOW.
- `1` — verdict is RED (errors present).
- `2` — input file not found, unreadable, or not UTF-8.

### Error codes — fix strategy

| Code | Severity | Fix |
|---|---|---|
| `frontmatter-invalid-yaml` | error | YAML did not parse. Fix syntax. The `line` field points to the first parse error. |
| `missing-required-field` | error | A required field (`voice.name`, `forbidden_lexicon`, `rewrite_rules`, `sentence_norms`) is absent. Add it. |
| `invalid-field-value` | error | A field's value violates its constraint (e.g. `word_count_min > word_count_max`, non-kebab-case `rule_id`). |
| `duplicate-rule-id` | error | Two `rewrite_rules` entries share a `rule_id`. Rule IDs must be unique. |
| `missing-section` | error | One of the 11 required H2 sections is absent. |
| `section-out-of-order` | error | A required section appears in the wrong order. |
| `duplicate-section` | error | The same H2 heading appears twice. |
| `extends-cycle` | error | `voice.extends` chain forms a cycle. Identity is detected via `(st_dev, st_ino)` so case-insensitive filesystems do not mask cycles. |
| `extends-depth-exceeded` | error | Chain length exceeds `MAX_EXTENDS_DEPTH` (5). Flatten or restructure. |
| `extends-parent-not-found` | error | Parent path does not resolve. Path is relative to the child file's directory unless absolute. |
| `extends-parent-invalid` | error | Parent itself fails its own lint. Carries a nested `parent_errors` array with the actual failures. |
| `replace-without-extends` | error | A `<field>_replace` key is declared in a file that does not set `voice.extends`. Suffix is meaningless without a parent. |
| `remove-without-extends` | error | A `<field>_remove` key is declared in a file that does not set `voice.extends`. |
| `replace-conflict-with-extending` | error | Same field declares two of `X` / `X_replace` / `X_remove`. Pick one. |
| `replace-on-unsupported-field` | error | `<field>_replace` is on a field outside the `REPLACE_ALLOWED_FIELDS` whitelist. |
| `remove-on-unsupported-field` | error | `<field>_remove` is on a field outside the `REMOVE_ALLOWED_FIELDS` whitelist. |
| `core-attribute-missing-id` | error | A `core_attributes` entry lacks `attribute_id`. Always RED — the field is required on every entry as the stable merge key. |
| `empty-required-lexicon` | warning | `forbidden_lexicon` is `[]`. Tolerated but unusual. |
| `no-source-urls` | warning | `voice.source_urls` is empty. The doc is interview-only or hand-authored. |
| `outdated-last-updated` | warning | `voice.last_updated` is more than 180 days old. Consider running `update`. |
| `recommended-section-missing` | warning | A recommended H2 section (sections 5–11 per `canonical-format.md`) is absent. The doc is still valid; the missing section is information the brand chose not to encode. |
| `section-light-content` | warning | A canonical section (required or recommended, when present) has fewer than 50 characters of prose. |
| `extends-path-outside-skill` | warning | The resolved parent path escapes the skill directory. Pass `--allow-extends-outside-skill` to silence. Prevents accidental coupling to user-specific paths. |
| `rewrite-rule-overridden-by-child` | warning | A child's `rewrite_rules` entry collides with a parent's `rule_id` without `override: true`. Silent overrides regress tone surgically; mark the override or rename the rule. |

## `extract_rules.py` output

Plain text, line-oriented, designed for `cat | grep | head` pipelines and for inclusion in a downstream LLM prompt without JSON parsing.

### CLI flags

| Flag | Default | Effect |
|---|---|---|
| `--full` | on | Emit the full output (legacy fields + `core_attributes`, `contexts`, `source_urls`). Required for `humanize-en`'s `-f` parity. |
| `--legacy` | off | Emit the v1 minimal output. **Byte-identical** to the pre-extends shape — for any external consumer pinned to it. Mutually exclusive with `--full`. |
| `--resolve-extends` | on (when `voice.extends` is set) | Walk the chain and emit merged rules. |
| `--no-resolve-extends` | off | Skip chain resolution; emit child-only rules. |
| `--explain` | off | Annotate each line with `# from <relpath>` suffix. Default output stays byte-stable so LLM-prompt determinism is preserved. |
| `--explain-json` | off | Emit structured provenance as JSON instead of plain text. For tooling. |
| `--allow-extends-outside-skill` | off | Suppress the `extends-path-outside-skill` warning. |

### Full output shape (`--full`, default)

```
voice: <voice.name>
last_updated: <voice.last_updated>
source_urls:
  - <voice.source_urls[0]>
  - …

core_attributes:
  - [<attribute_id>] <name>: <failure_mode>
  - …

forbidden:
  - <forbidden_lexicon[0]>
  - …

required:
  - <required_lexicon[0]>
  - …

sentence_norms:
  word_count: <min>-<max> (hard max: <sentence_max_hard>)
  contractions: <allow|forbid>
  oxford_comma: <true|false>
  em_dash_spacing: <spaced|tight|forbid>
  exclamation_marks: <allow|forbid>

forbidden_patterns:
  - <forbidden_patterns[0]>
  - …

rewrite_rules:
  - [<rule_id>] <reject> -> <accept>
  - …

contexts:
  <context_name>:
    <key>: <value>
  …

pronouns: <pronouns.default> (forbid: <pronouns.forbid>)
```

### Legacy output shape (`--legacy`)

Byte-identical to the pre-extends shape (no `source_urls`, no `core_attributes`, no `contexts`):

```
voice: <voice.name>
last_updated: <voice.last_updated>

forbidden: …
required: …
sentence_norms: …
forbidden_patterns: …
rewrite_rules: …
pronouns: …
```

### `--explain` annotations

Each line gains a trailing `# from <relpath>` comment when `--explain` is set. Default output is unchanged (no comments). Example:

```
forbidden:
  - game-changing  # from BRAND-VOICE.md
  - corporate-jargon  # from BRAND-VOICE-FOUNDER.md
```

`--explain-json` emits structured provenance:

```json
{
  "forbidden_lexicon": [
    {"value": "game-changing", "source": "BRAND-VOICE.md"},
    {"value": "corporate-jargon", "source": "BRAND-VOICE-FOUNDER.md"}
  ],
  "rewrite_rules": [...]
}
```

### Output size

Full mode: 50–150 lines for a typical voice doc; longer for richly contextual brands. Legacy mode: 30–80 lines. Empty fields are omitted entirely (no `forbidden: (none)` placeholders).

### Exit codes

- `0` — extraction succeeded; output written to stdout.
- `1` — file not found, unreadable, YAML invalid, or chain resolution failed (cycle, depth, missing parent). Error on stderr.

### Why plain text and not JSON

The downstream consumer is `humanize-en` running through Claude. Claude reads the rules as text in its prompt. JSON would force a parse step that adds no information — the rules are the contract, not the structure.

Tooling that needs structure can run `voice_lint.py` (which emits JSON) or `extract_rules.py --explain-json` and read the same fields from there.

## Stability

These schemas are the public surface of `brand-voice`. Adding optional fields is a non-breaking change; removing a field, renaming a field, or changing a verdict definition is a breaking change. Breaking changes go through the repo's normal release process.

### `_replace` and `_remove` blast radius

Every new mergeable frontmatter field requires deciding three things at PR time:

1. **Merge policy** (union, deep merge, shallow merge, child-wins, or merge-by-key).
2. **Whether the field belongs in `REPLACE_ALLOWED_FIELDS`** (any field that is structurally complex enough to warrant full replacement under inheritance).
3. **Whether it belongs in `REMOVE_ALLOWED_FIELDS`** (list fields where surgical subtraction makes sense — list-of-strings or list-of-objects-with-stable-IDs).

Scalar fields (string, int, bool) never need `_replace` — child-wins is total replacement already. The `REPLACE_ALLOWED_FIELDS` and `REMOVE_ALLOWED_FIELDS` constants in `scripts/utils.py` are the source of truth; PRs that add new mergeable fields must update both, add fixtures under `tests/fixtures/`, and a corresponding test in `tests/test_replace_remove.py`.
