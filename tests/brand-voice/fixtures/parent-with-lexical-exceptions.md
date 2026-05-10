---
voice:
  name: "ParentWithLex"
  source_urls:
    - https://example.com
  last_updated: "2026-04-27"
  source: "manual"

core_attributes:
  - attribute_id: precise
    name: "Precise"
    failure_mode: "vague claims, hedging"

forbidden_lexicon:
  - "game-changing"

rewrite_rules:
  - reject: "It might be worth considering..."
    accept: "Use X."
    rule_id: no-hedging-imperative

sentence_norms:
  word_count_min: 8
  word_count_max: 22
  sentence_max_hard: 30
  contractions: "allow"
  oxford_comma: true
  em_dash_spacing: "spaced"
  exclamation_marks: "forbid"

lexical_exceptions:
  acronyms:
    - "BPM"
    - "MIDI"
  compound_idioms:
    - "in-your-face"
---

# Brand Voice — ParentWithLex

Parent voice with lexical_exceptions whitelists.

## 1. Core voice attributes

Stub stub stub stub stub stub stub stub stub stub.

## 2. Rewrite rules — do/don't

Stub stub stub stub stub stub stub stub stub stub.

## 3. Forbidden lexicon and patterns

Stub stub stub stub stub stub stub stub stub stub.

## 4. Sentence-level norms

Stub stub stub stub stub stub stub stub stub stub.
