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
  extends: string                 # optional — relative or absolute path to a parent BRAND-VOICE.md (see § Inheritance)
  source_urls: [string]           # optional — URLs/paths of ingested sources (no internal IDs in committed examples)
  last_updated: string            # optional — ISO date "YYYY-MM-DD"
  source: string                  # optional — "extract" | "interview" | "manual"

core_attributes:                  # optional but recommended
  - attribute_id: string          # kebab-case stable ID; required when voice.extends is set, recommended otherwise
    name: string                  # display label (e.g. "Authoritative")
    failure_mode: string          # what failure looks like

forbidden_lexicon: [string]       # required — list of words/phrases to reject
required_lexicon: [string]        # optional — words the brand owns

rewrite_rules:                    # required
  - reject: string                # the bad pattern
    accept: string                # the good replacement (placeholder allowed: "<…>")
    rule_id: string               # stable identifier, kebab-case
    override: boolean             # optional — when true, silences `rewrite-rule-overridden-by-child` warning under inheritance

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

# When `voice.extends` is set, the file may also declare these inheritance overrides.
# Mutually exclusive with the canonical field of the same root name. See § Inheritance.
forbidden_lexicon_replace: [string]      # full replacement of parent's
forbidden_lexicon_remove:  [string]      # surgical removal from parent's
required_lexicon_replace:  [string]
required_lexicon_remove:   [string]
forbidden_patterns_replace: [string]
forbidden_patterns_remove:  [string]
rewrite_rules_replace:     [object]      # full replacement
rewrite_rules_remove:      [string]      # list of rule_ids to remove
core_attributes_replace:   [object]
core_attributes_remove:    [string]      # list of attribute_ids to remove
sentence_norms_replace:    object
contexts_replace:          object
pronouns_replace:          object
---
```

### Field types and constraints

- **`voice.name`** — non-empty string, max 80 chars.
- **`voice.extends`** — optional string. Relative path resolves against the child file's directory; absolute paths allowed; must end in `.md`, `.mdx`, or `.markdown`. Single parent only. See § Inheritance for chain semantics.
- **`forbidden_lexicon`** — non-empty list. Each entry lowercase unless the term is intrinsically capitalised (e.g. brand names). Substring matching is case-insensitive at scan time.
- **`rewrite_rules[].rule_id`** — kebab-case (`[a-z0-9-]+`), unique across the list. `voice_lint` rejects duplicates.
- **`rewrite_rules[].override`** — optional boolean. When `true`, silences the `rewrite-rule-overridden-by-child` warning that fires when a child's `rule_id` collides with a parent's.
- **`core_attributes[].attribute_id`** — kebab-case (`[a-z0-9-]+`). **Required** on every entry. Stable merge key for inheritance and a stable ID for tooling. Lint emits `core-attribute-missing-id` (RED) when absent. The merge engine falls back to a normalised `name` only as a defensive measure for malformed input; do not rely on it.
- **`sentence_norms.word_count_min`** — must be ≥ 1 and ≤ `word_count_max`.
- **`sentence_norms.word_count_max`** — must be ≤ `sentence_max_hard`.
- **`sentence_norms.em_dash_spacing`** — `spaced` (` — `, the British/French convention), `tight` (`—` no spaces, the US convention), or `forbid` (no em-dashes at all).
- **`forbidden_patterns`** — recognised values: `rule_of_three`, `rhetorical_questions`, `emoji`, `all_caps_emphasis`, `marketing_analogies`, `negative_parallelism`, `signposting`, `superficial_ing`. Custom values are tolerated.
- **`contexts.<name>`** — object, free-form keys. Recommended keys above are not enforced.
- **`<field>_replace`** / **`<field>_remove`** — see § Inheritance. Permitted only when `voice.extends` is set in the same file. Whitelisted fields only.

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

## Inheritance via `extends:`

A child file declares a parent and inherits its rules, overriding only what differs. Use cases: founder voice on top of corporate, multi-host media brands, persona on top of an institutional voice.

```yaml
voice:
  name: "Founder"
  extends: "./BRAND-VOICE.md"
```

### Chain rules

- **Single parent** — one `voice.extends` per file. No list, no glob, no URL.
- **Path resolution** — relative paths resolve against the child file's directory (not CWD); absolute paths allowed.
- **Depth limit** — `MAX_EXTENDS_DEPTH = 5`. Typical chains are 1-2 levels; 5 covers nested orgs (group → brand → product → persona → channel).
- **Cycle detection** — identity is `(st_dev, st_ino)` from `os.stat()`, not path string. macOS HFS+/APFS is case-insensitive by default and `Path.resolve()` would otherwise miss `./brand-voice.md` ↔ `./BRAND-VOICE.md` cycles. Falls back to lowercased canonical path on Windows.
- **Path containment** — warning `extends-path-outside-skill` if the resolved parent escapes the skill directory (prevents accidental coupling to user-specific paths like `~/Desktop/...`). Pass `--allow-extends-outside-skill` to silence.

### Default merge policy

When the child declares a canonical field, it merges with the parent's value per the policy below. Order is parent-first then child-appended; list dedup uses `dict.fromkeys()` so output is stable across `PYTHONHASHSEED` values.

| Field | Type | Policy |
|---|---|---|
| `voice.name`, `voice.last_updated`, `voice.source` | str | child wins |
| `voice.source_urls` | list[str] | child wins (each voice owns its provenance) |
| `voice.extends` | str | not inherited (resolved at load) |
| `core_attributes` | list[obj keyed by `attribute_id`] | merge by ID; child overrides on collision; new entries appended |
| `forbidden_lexicon`, `required_lexicon`, `forbidden_patterns` | list[str] | union, deduplicated |
| `rewrite_rules` | list[obj keyed by `rule_id`] | merge by `rule_id`; child wins; appends new. Warning `rewrite-rule-overridden-by-child` unless rule has `override: true` |
| `sentence_norms` | object | shallow merge (key-by-key), child wins |
| `contexts` | object (free-form keys) | deep merge by context name; per-context shallow merge; child wins on collision |
| `pronouns` | object | shallow merge, child wins. `pronouns.forbid` is replaced (not unioned) when child declares it — personas legitimately *invert* parent rules |

### `<field>_replace` — full replacement

When the merge policy is wrong for the case (e.g. a persona that needs a fundamentally different lexicon), declare `<field>_replace` instead of the canonical field. The child's value fully replaces the parent's.

```yaml
voice:
  name: "Persona"
  extends: "./BRAND-VOICE.md"

forbidden_lexicon_replace:        # replaces parent's entirely
  - "persona-only banned word"

pronouns_replace:                 # replaces parent's entirely
  default: "first-person singular"
  forbid: []
```

Whitelisted fields (the constant `REPLACE_ALLOWED_FIELDS` in `scripts/utils.py`):
`forbidden_lexicon`, `required_lexicon`, `forbidden_patterns`, `rewrite_rules`, `core_attributes`, `sentence_norms`, `contexts`, `pronouns`.

### `<field>_remove` — surgical removal

When the override is "remove this single inherited entry", `_replace` is too heavy (forces re-listing every kept entry). Use `_remove` to subtract specific items from the merged result.

```yaml
forbidden_lexicon_remove:         # parent forbids these; this voice allows them
  - "passionate"
  - "delightful"

rewrite_rules_remove:             # remove parent rules by rule_id
  - "no-hedging-imperative"
```

Whitelisted fields (the constant `REMOVE_ALLOWED_FIELDS`, subset of replace whitelist):
`forbidden_lexicon`, `required_lexicon`, `forbidden_patterns`, `rewrite_rules`, `core_attributes`. List-of-objects fields (`rewrite_rules`, `core_attributes`) take a list of stable IDs; list-of-string fields take exact entries.

### Mutex

For any field `X`, the following combinations are valid:

- `X` alone — canonical, additive merge with parent.
- `X_replace` alone — full replacement (drops parent's value entirely).
- `X_remove` alone — subtractive on parent's value (list fields only).
- **`X` + `X_remove`** — additive merge plus selective subtraction. This is the common case: a child adds a few entries to the parent's list and explicitly removes a couple of inherited entries. Both apply.

The following combinations are invalid (`replace-conflict-with-extending`, RED):

- `X` + `X_replace` — contradictory: `_replace` already drops parent's value; the canonical field's union semantic has nothing to merge against.
- `X_replace` + `X_remove` — contradictory: `_replace` already drops parent's value; `_remove` would target a list that no longer exists.

`_replace` and `_remove` keys require `voice.extends` set in the same file — declaring them in a parent that does not extend triggers `replace-without-extends` / `remove-without-extends`. The lint enforces this on every file regardless of whether something currently inherits from it (prevents footguns where the suffix activates the moment a child appears).

### Why suffix and not YAML tags

YAML tags (`!replace`) and anchors are intentionally unsupported by `parse_yaml_minimal` (`scripts/utils.py:72-73`) — keeping the parser dependency-free is a non-goal-stated rule. Suffix conventions are parser-friendly, human-readable, and grep-friendly.

### Validation order

`voice_lint.py` walks the chain in this order. Without it, a `duplicate-rule-id` on the merged dict would be indistinguishable from a child-internal duplicate.

1. **Lint child** syntactically. If RED → return early; chain not resolved.
2. **Resolve chain** via `resolve_extends_chain`. Surface `extends-cycle`, `extends-depth-exceeded`, `extends-parent-not-found`.
3. **Recursively lint each parent.** Parent failures aggregate as `extends-parent-invalid` with a nested `parent_errors` array on the child's error object.
4. **Lint the merged dict.** Errors carry `source: "merged"` discriminator. Required fields (`forbidden_lexicon`, `rewrite_rules`, `sentence_norms`) are validated here — children may omit them locally and inherit.

Each error/warning gains optional `source` (`"child"` / `"parent:<relpath>"` / `"merged"`) and `source_path` fields so authors trace cascade failures to their origin.

### Lint relaxation for child files

When `voice.extends` is set, the child-isolated lint relaxes three checks because the missing values come from the parent:

- `missing-required-field` for `forbidden_lexicon`, `rewrite_rules`, `sentence_norms` — only `voice.name` is required locally on a child.
- `empty-required-lexicon` warning — does not fire on a child (parent's lexicon will be unioned in).
- `recommended-section-missing` warning — does not fire on a child (sections 5-11 are inherited from the parent's prose; child must still declare its own required sections 1-4).

These checks all run normally at the merged level (step 4), so a chain that fails to provide a required field anywhere is caught — just not redundantly on every child file.

### Prose inheritance

**Out of scope.** A child file must declare its own required prose sections (1-4 per § *Prose section order*) — they explain the *child's* voice. Recommended sections (5-11) may be omitted entirely; the existing `recommended-section-missing` warning fires per-file. Merging paragraphs across parent and child is semantically nonsensical; the YAML carries the testable contract, prose carries the rationale, and rationale is per-locuteur. The `<!-- inherits-from-parent -->` HTML comment is a recommended doc convention when an author wants to make inheritance visible to readers, but it is not enforced.

### Adding new mergeable fields (PR checklist)

Every new mergeable field requires deciding three things at PR time:

1. Merge policy (union, deep merge, shallow merge, child-wins, merge-by-key).
2. Whether the field belongs in `REPLACE_ALLOWED_FIELDS`.
3. Whether the field belongs in `REMOVE_ALLOWED_FIELDS` (list fields with stable identity only).

The constants in `scripts/utils.py` are the source of truth; PRs that add fields must update both, add fixtures under `tests/brand-voice/fixtures/`, and a corresponding test in `tests/brand-voice/test_replace_remove.py`.
