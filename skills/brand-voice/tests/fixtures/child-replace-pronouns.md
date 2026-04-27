---
voice:
  name: "ReplacePersona"
  extends: "./parent-corp.md"
  last_updated: "2026-04-27"

core_attributes:
  - attribute_id: stub
    name: "Stub"
    failure_mode: "n/a"

forbidden_lexicon: []

pronouns_replace:
  default: "first-person plural"
  forbid:
    - "second-person 'you' as command"

rewrite_rules:
  - reject: "stub"
    accept: "stub"
    rule_id: stub-rule

sentence_norms:
  word_count_min: 8
  word_count_max: 22
  sentence_max_hard: 30
---

# Brand Voice — ReplacePersona

## 1. Core voice attributes

A persona that fully replaces the parent's pronouns block. After merging, the inherited `forbid: ["first-person singular"]` is gone — the child's `pronouns_replace` value is the merged value.

## 2. Rewrite rules — do/don't

Stub.

## 3. Forbidden lexicon and patterns

Empty here; inherits parent's via merge.

## 4. Sentence-level norms

Inherits parent.
