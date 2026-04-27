# Canonical `BRAND-VOICE.md` format

The format is a YAML frontmatter (machine-readable normative rules) followed by 11 prose sections (human-readable rationale). Frontmatter is consumed by downstream skills via `scripts/extract_rules.py`; prose is consumed by humans and by Claude when context calls for nuance.

This document is the contract. `voice_lint.py` validates against it.

## File-level rules

- File starts with `---\n` (YAML frontmatter open delimiter on line 1).
- Frontmatter closes with `---\n` on its own line.
- First H1 (`# Brand Voice — <name>`) appears on the line after the closing delimiter.
- Eleven H2 sections in the exact order documented below. Missing sections fail lint. Extra sections are tolerated and preserved at the end.

## Frontmatter schema

```yaml
---
voice:                            # required
  name: string                    # required — brand name
  source_urls: [string]           # optional — URLs/paths of ingested sources (no internal IDs in committed examples)
  last_updated: string            # optional — ISO date "YYYY-MM-DD"
  source: string                  # optional — "extract" | "interview" | "manual"

core_attributes:                  # optional but recommended
  - name: string                  # short identifier (e.g. "authoritative")
    failure_mode: string          # what failure looks like

forbidden_lexicon: [string]       # required — list of words/phrases to reject
required_lexicon: [string]        # optional — words the brand owns

rewrite_rules:                    # required
  - reject: string                # the bad pattern
    accept: string                # the good replacement (placeholder allowed: "<…>")
    rule_id: string               # stable identifier, kebab-case

sentence_norms:                   # required
  word_count_min: integer
  word_count_max: integer
  sentence_max_hard: integer
  contractions: "allow" | "forbid"
  oxford_comma: boolean
  em_dash_spacing: "spaced" | "tight" | "forbid"
  exclamation_marks: "allow" | "forbid"

forbidden_patterns: [string]      # optional — high-level pattern names
                                  # (rule_of_three, rhetorical_questions, emoji,
                                  #  all_caps_emphasis, marketing_analogies, …)

contexts:                         # optional — register adjustments per context
  rfc:      { density: string, numbered_sections: boolean, ... }
  readme:   { tagline_first: boolean, marketing_pitch: boolean, ... }
  landing:  { sentence_count: integer, ... }
  blog:     { open_with_claim: boolean, ... }
  doc:      { mood: string, ... }
  internal: { match: string, ... }

pronouns:                         # optional but recommended
  default: string                 # e.g. "third-person institutional"
  forbid: [string]                # e.g. ["first-person singular"]
---
```

### Field types and constraints

- **`voice.name`** — non-empty string, max 80 chars.
- **`forbidden_lexicon`** — non-empty list. Each entry lowercase unless the term is intrinsically capitalised (e.g. brand names). Substring matching is case-insensitive at scan time.
- **`rewrite_rules[].rule_id`** — kebab-case (`[a-z0-9-]+`), unique across the list. `voice_lint` rejects duplicates.
- **`sentence_norms.word_count_min`** — must be ≥ 1 and ≤ `word_count_max`.
- **`sentence_norms.word_count_max`** — must be ≤ `sentence_max_hard`.
- **`sentence_norms.em_dash_spacing`** — `spaced` (` — `, the British/French convention), `tight` (`—` no spaces, the US convention), or `forbid` (no em-dashes at all).
- **`forbidden_patterns`** — recognised values: `rule_of_three`, `rhetorical_questions`, `emoji`, `all_caps_emphasis`, `marketing_analogies`, `negative_parallelism`, `signposting`, `superficial_ing`. Custom values are tolerated.
- **`contexts.<name>`** — object, free-form keys. Recommended keys above are not enforced.

## Prose section order

Eleven canonical sections. Sections **1–4 are required** — without them the doc has no executable contract. Sections **5–11 are recommended** — `voice_lint.py` warns if they are absent but does not block. When present, all canonical sections must appear in this order.

| # | Section heading | Status | Purpose |
|---|----------------|--------|---------|
| 1 | `## 1. Core voice attributes` | **required** | The 3-5 non-negotiable principles. Mirror the `core_attributes:` YAML. |
| 2 | `## 2. Rewrite rules — do/don't` | **required** | Tables matching `rewrite_rules:` YAML, with examples expanded. |
| 3 | `## 3. Forbidden lexicon and patterns` | **required** | Rationale for each entry in `forbidden_lexicon` and `forbidden_patterns`. Example sentences showing why. |
| 4 | `## 4. Sentence-level norms` | **required** | Expanded explanation of `sentence_norms:` (length, voice, hedging) with counter-examples. |
| 5 | `## 5. Tone by context` | recommended | One row per context in `contexts:`, with example openers. Skip if the voice is uniform across all contexts. |
| 6 | `## 6. Pronouns and self-reference` | recommended | When to use first-person, third-person, impersonal — backed by `pronouns:`. Skip if the brand has no fixed pronoun convention. |
| 7 | `## 7. Format conventions` | recommended | Numbers, dates, units, punctuation, code-in-prose. Skip if the brand follows the host platform's defaults. |
| 8 | `## 8. Visual pairing` | recommended | Typography stack, color affordances, what the voice presupposes about the visual environment. Skip if the brand owns no visual identity. |
| 9 | `## 9. Quick diagnostic` | recommended | 3-5 pre-publish checks the user runs by hand. |
| 10 | `## 10. Counter-examples` | recommended | Real bad rewrites — what the rules prevent. Three to five entries minimum when present. |
| 11 | `## 11. Reference texts` | recommended | URLs / file paths of canonical exemplars. |

Section heading text is matched case-insensitively, with the leading numbering optional. `## 1. Core voice attributes`, `## Core voice attributes`, and `## 1 Core voice attributes` all match section 1.

When recommended sections are present, they must appear in canonical order — a doc with only sections 1, 2, 3, 4, and 7 (skipping 5 and 6) is valid; a doc with sections 1, 4, 2, 3 (out of order) is not.

## Manual-section preservation

Sections the user adds by hand outside the canonical 11 are preserved by `update`. The marker is an HTML comment immediately under the heading:

```markdown
## 12. Brand mythology
<!-- manual: true -->
…
```

`update` reads this marker and never overwrites the section. The marker travels with the section if it moves.

## Why the format is split (YAML + prose)

- **Tooling reads YAML.** `humanize-en -f BRAND-VOICE.md` invokes `extract_rules.py` which only reads the frontmatter. 30–80 lines of structured rules are enough to enforce the voice deterministically.
- **Humans read prose.** The 11 sections explain *why* each rule exists. Without rationale, the YAML degrades into a deny-list and rules drift. Prose is the brand's voice talking about itself.
- **Versioning is git.** The whole file is a single artefact, plain text. `/brand-voice diff` is `git diff` plus presentation. No external state, no proprietary format.

## Why no `apply` in the schema

The schema is descriptive (what the voice *is*), not procedural (how to apply it). Application is the consumer's job — `humanize-en -f` decides which rules to apply and when. A `apply_strategy:` field would conflate the two and force every consumer to honour the same dispatch logic. The current split keeps consumers independent.
