---
voice:
  name: "MissingAttrId"
  extends: "./parent-corp.md"
  last_updated: "2026-04-27"

core_attributes:
  - name: "Authoritative"
    failure_mode: "marketing softness"
# attribute_id missing — RED when extends is set

forbidden_lexicon: []
rewrite_rules:
  - reject: "stub"
    accept: "stub"
    rule_id: stub-rule
sentence_norms:
  word_count_min: 8
  word_count_max: 22
  sentence_max_hard: 30
---

# Brand Voice — MissingAttrId

## 1. Core voice attributes

Has `core_attributes` entry without `attribute_id`. Because `voice.extends` is set, this should be RED.

## 2. Rewrite rules — do/don't

Stub.

## 3. Forbidden lexicon and patterns

Stub.

## 4. Sentence-level norms

Stub.
