---
voice:
  name: "RemovePersona"
  extends: "./parent-corp.md"
  last_updated: "2026-04-27"

core_attributes:
  - attribute_id: stub
    name: "Stub"
    failure_mode: "n/a"

forbidden_lexicon_remove:
  - "passionate"
  - "synergies"

rewrite_rules:
  - reject: "stub"
    accept: "stub"
    rule_id: stub-rule

sentence_norms:
  word_count_min: 8
  word_count_max: 22
  sentence_max_hard: 30
---

# Brand Voice — RemovePersona

## 1. Core voice attributes

Removes 'passionate' and 'synergies' from parent's forbidden_lexicon. Merged result keeps only 'game-changing'.

## 2. Rewrite rules — do/don't

Stub.

## 3. Forbidden lexicon and patterns

The remove operation subtracts inherited entries — useful when a persona is allowed warmth the corporate voice forbids.

## 4. Sentence-level norms

Inherits parent.
