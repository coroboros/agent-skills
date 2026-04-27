# Example — multi-voice brand via `extends:`

A worked example of inheritance for a fictional founder-led startup. Two files: the institutional `BRAND-VOICE.md` (parent) and the founder's `BRAND-VOICE-FOUNDER.md` (child) that extends it.

The example brand is **Helio** — fictional, generic. The point is the *mechanism*; readers adapt to their own brand.

---

## Layout

```
helio/
├── BRAND-VOICE.md            # parent — institutional voice
└── BRAND-VOICE-FOUNDER.md    # child — founder's personal voice
```

The child sits next to the parent. Cross-skill consumption (`/humanize-en -f BRAND-VOICE-FOUNDER.md draft.md`) auto-resolves the chain.

---

## Parent — `BRAND-VOICE.md` (institutional)

Abbreviated frontmatter. Required prose sections 1-4 omitted from this excerpt for space; in a real file they are mandatory.

```yaml
---
voice:
  name: "Helio"
  source_urls:
    - https://helio.example.com
  last_updated: "2026-04-27"
  source: "manual"

core_attributes:
  - attribute_id: precise
    name: "Precise"
    failure_mode: "vague claims, hedging, fuzzy comparisons"
  - attribute_id: institutional
    name: "Institutional"
    failure_mode: "first-person, salesperson openers, brand-pose"
  - attribute_id: technical
    name: "Technical"
    failure_mode: "dumbing down, hand-holding, marketing analogies"

forbidden_lexicon:
  - "game-changing"
  - "revolutionary"
  - "passionate"
  - "delightful"
  - "we believe"
  - "we feel"
  - "synergies"

required_lexicon: []

rewrite_rules:
  - rule_id: no-hedging-imperative
    reject: "It might be worth considering..."
    accept: "Use X."
  - rule_id: specific-over-abstract-speed
    reject: "significantly faster"
    accept: "<cite a number — e.g. 3.2× faster>"
  - rule_id: no-salesperson-opener
    reject: "Great question — let me explain."
    accept: "<delete entire opener>"

sentence_norms:
  word_count_min: 8
  word_count_max: 22
  sentence_max_hard: 30
  contractions: "allow"
  oxford_comma: true
  em_dash_spacing: "spaced"
  exclamation_marks: "forbid"

forbidden_patterns:
  - rule_of_three
  - rhetorical_questions
  - emoji
  - marketing_analogies

contexts:
  rfc:
    density: "max"
    numbered_sections: true
  readme:
    tagline_first: true
    marketing_pitch: false

pronouns:
  default: "third-person institutional"
  forbid:
    - "first-person singular"
    - "first-person plural in marketing"
---
```

---

## Child — `BRAND-VOICE-FOUNDER.md` (founder's voice)

Same brand, different speaker. Helio's founder writes blog posts, conference talks, and DMs — first-person, more conversational, allowed to use some warmer words the institutional voice forbids.

```yaml
---
voice:
  name: "Helio — Founder"
  extends: "./BRAND-VOICE.md"
  source_urls:
    - https://helio.example.com/blog
  last_updated: "2026-04-27"
  source: "manual"

# Add one founder-specific banned word; rest of forbidden_lexicon inherits from parent
forbidden_lexicon:
  - "thought leader"

# Founder is allowed to say "passionate" and "delightful" — explicitly remove from parent's bans
forbidden_lexicon_remove:
  - "passionate"
  - "delightful"

# Founder voice fully replaces pronouns — first-person allowed; the institutional rule inverts here
pronouns_replace:
  default: "first-person singular"
  forbid:
    - "second-person 'you' as command in marketing"

# One new rewrite rule specific to the founder voice
rewrite_rules:
  - rule_id: founder-no-third-person-self
    reject: "The founder believes..."
    accept: "I think..."

# Add a `blog` context for register adjustments (parent doesn't define one)
contexts:
  blog:
    open_with_anecdote: true
    closing_signature: true

# Required prose sections 1-4 must be present in the child too — they explain the founder's voice.
# Recommended sections 5-11 may be omitted; lint emits per-section warnings (acceptable for child files).
---

# Brand Voice — Helio (Founder)

The founder's writing voice for Helio. Inherits from the institutional voice and adapts where personal voice is appropriate.

## 1. Core voice attributes

… (required, child-specific prose)

## 2. Rewrite rules — do/don't

… (required)

## 3. Forbidden lexicon and patterns

… (required)

## 4. Sentence-level norms

… (required)
```

---

## Merged result

What `extract_rules.py --full` emits when run against the child:

```
voice: Helio — Founder
last_updated: 2026-04-27
source_urls:
  - https://helio.example.com/blog

core_attributes:
  - [precise] Precise: vague claims, hedging, fuzzy comparisons
  - [institutional] Institutional: first-person, salesperson openers, brand-pose
  - [technical] Technical: dumbing down, hand-holding, marketing analogies

forbidden:
  - game-changing
  - revolutionary
  - we believe
  - we feel
  - synergies
  - thought leader

# `passionate` and `delightful` removed via forbidden_lexicon_remove

required:

sentence_norms:
  word_count: 8-22 (hard max: 30)
  contractions: allow
  oxford_comma: true
  em_dash_spacing: spaced
  exclamation_marks: forbid

forbidden_patterns:
  - rule_of_three
  - rhetorical_questions
  - emoji
  - marketing_analogies

rewrite_rules:
  - [no-hedging-imperative] It might be worth considering... -> Use X.
  - [specific-over-abstract-speed] significantly faster -> <cite a number — e.g. 3.2× faster>
  - [no-salesperson-opener] Great question — let me explain. -> <delete entire opener>
  - [founder-no-third-person-self] The founder believes... -> I think...

contexts:
  rfc:
    density: max
    numbered_sections: true
  readme:
    tagline_first: true
    marketing_pitch: false
  blog:
    open_with_anecdote: true
    closing_signature: true

pronouns: first-person singular (forbid: second-person 'you' as command in marketing)
```

What changed vs. the parent:
- `forbidden_lexicon` — additive: adds `thought leader`, removes `passionate` / `delightful`.
- `pronouns` — fully replaced: founder may use first-person; parent's `forbid: ["first-person singular", ...]` is gone.
- `rewrite_rules` — additive: parent's three rules inherited + one new founder rule.
- `contexts` — additive: parent's `rfc` and `readme` inherited + new `blog` context.
- Everything else — inherited verbatim.

---

## When to use which mechanism

| Need | Mechanism | Example |
|---|---|---|
| Add new entries to a list | declare the canonical field | `forbidden_lexicon: ["new-banned-word"]` |
| Remove specific inherited entries | `_remove` suffix | `forbidden_lexicon_remove: ["passionate"]` |
| Replace the whole list/object | `_replace` suffix | `pronouns_replace: { default: "first-person singular" }` |
| Override one merge-by-key entry | declare it under the canonical field with the same `rule_id` / `attribute_id` | `rewrite_rules: [{rule_id: existing-id, ...}]` |
| Silence the override warning | add `override: true` to the entry | `{rule_id: x, override: true, ...}` |

If a need is not covered above, the answer is probably "use a separate `BRAND-VOICE.md` rather than extends" — fundamentally different voices benefit from being independent.

---

## Tooling

```bash
# Validate the child (walks the chain)
/brand-voice validate BRAND-VOICE-FOUNDER.md

# Show the merged rules (default when extends is set)
/brand-voice show BRAND-VOICE-FOUNDER.md

# Show the child's declarations only (debugging)
/brand-voice show BRAND-VOICE-FOUNDER.md --raw

# Annotate each rule with its origin file
/brand-voice show BRAND-VOICE-FOUNDER.md --explain

# Print the resolution chain
/brand-voice show BRAND-VOICE-FOUNDER.md --chain

# Diff child vs. resolved parent (single-arg form when extends is set)
/brand-voice diff BRAND-VOICE-FOUNDER.md

# Humanize a draft using the merged voice
/humanize-en -f BRAND-VOICE-FOUNDER.md draft.md
```

The `lint_all.py` script (run from the directory containing both files) catches parent-change regressions across every child:

```bash
python3 ~/.claude/skills/brand-voice/scripts/lint_all.py .
```
