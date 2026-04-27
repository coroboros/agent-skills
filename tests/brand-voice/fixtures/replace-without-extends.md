---
voice:
  name: "BadReplace"
  last_updated: "2026-04-27"

forbidden_lexicon: []
forbidden_lexicon_replace:
  - "this is invalid because no voice.extends"

rewrite_rules:
  - reject: "stub"
    accept: "stub"
    rule_id: stub-rule
sentence_norms:
  word_count_min: 8
  word_count_max: 22
  sentence_max_hard: 30
---

# Brand Voice — BadReplace

## 1. Core voice attributes

A `_replace` key without `voice.extends` is invalid; lint emits `replace-without-extends`.

## 2. Rewrite rules — do/don't

Stub.

## 3. Forbidden lexicon and patterns

Stub.

## 4. Sentence-level norms

Stub.
