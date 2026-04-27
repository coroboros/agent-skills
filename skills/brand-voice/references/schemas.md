# JSON schemas — `voice_lint.py` and `extract_rules.py`

Stable contracts. Other skills consume these outputs; changes here are breaking changes.

## `voice_lint.py` output

```json
{
  "path": "BRAND-VOICE.md",
  "verdict": "GREEN" | "YELLOW" | "RED",
  "errors": [
    {
      "code": "frontmatter-invalid-yaml" | "missing-required-field" | "invalid-field-value" | "duplicate-rule-id" | "missing-section" | "section-out-of-order" | "duplicate-section",
      "field": "voice.name" | "rewrite_rules[3].rule_id" | "section:1.core voice attributes" | null,
      "message": "human-readable explanation",
      "line": 42
    }
  ],
  "warnings": [
    {
      "code": "empty-required-lexicon" | "no-source-urls" | "outdated-last-updated" | "section-light-content",
      "field": "...",
      "message": "...",
      "line": 17
    }
  ],
  "stats": {
    "frontmatter_lines": 47,
    "prose_lines": 184,
    "total_lines": 231,
    "rule_count": 11,
    "forbidden_lexicon_count": 25,
    "section_count": 11
  }
}
```

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
| `empty-required-lexicon` | warning | `forbidden_lexicon` is `[]`. Tolerated but unusual. |
| `no-source-urls` | warning | `voice.source_urls` is empty. The doc is interview-only or hand-authored. |
| `outdated-last-updated` | warning | `voice.last_updated` is more than 180 days old. Consider running `update`. |
| `recommended-section-missing` | warning | A recommended H2 section (sections 5–11 per `canonical-format.md`) is absent. The doc is still valid; the missing section is information the brand chose not to encode. |
| `section-light-content` | warning | A canonical section (required or recommended, when present) has fewer than 50 characters of prose. |

## `extract_rules.py` output

Plain text, line-oriented, designed for `cat | grep | head` pipelines and for inclusion in a downstream LLM prompt without JSON parsing.

```
voice: <voice.name>
last_updated: <voice.last_updated>

forbidden:
  - <forbidden_lexicon[0]>
  - <forbidden_lexicon[1]>
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
  - [<rule_id>] <reject> → <accept>
  - …

pronouns: <pronouns.default> (forbid: <pronouns.forbid>)
```

Output is 30–80 lines for a typical voice doc (a comprehensive reference example with 10–15 rewrite rules and a long forbidden lexicon may run longer). Empty fields are omitted entirely (no `forbidden: (none)` placeholders).

### Exit codes

- `0` — extraction succeeded; output written to stdout.
- `1` — file not found, unreadable, or YAML invalid. Error on stderr.

### Why plain text and not JSON

The downstream consumer is `humanize-en` running through Claude. Claude reads the rules as text in its prompt. JSON would force a parse step that adds no information — the rules are the contract, not the structure.

Tooling that needs structure can run `voice_lint.py` (which emits JSON) and read the same fields from there.

## Stability

These schemas are the public surface of `brand-voice`. Adding optional fields is a non-breaking change; removing a field, renaming a field, or changing a verdict definition is a breaking change. Breaking changes go through the repo's normal release process.
