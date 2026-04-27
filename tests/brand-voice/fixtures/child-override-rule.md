---
voice:
  name: "OverrideRule"
  extends: "./parent-corp.md"
  last_updated: "2026-04-27"

core_attributes:
  - attribute_id: stub
    name: "Stub"
    failure_mode: "n/a"

forbidden_lexicon: []

rewrite_rules:
  - reject: "It might be worth considering..."
    accept: "Just do X."
    rule_id: no-hedging-imperative
    override: true

sentence_norms:
  word_count_min: 8
  word_count_max: 22
  sentence_max_hard: 30
---

# Brand Voice — OverrideRule

## 1. Core voice attributes

Overrides the parent's `no-hedging-imperative` rule with a different `accept` clause. The `override: true` flag suppresses the `rewrite-rule-overridden-by-child` warning.

## 2. Rewrite rules — do/don't

The override is intentional — the child voice prefers a more terse imperative.

## 3. Forbidden lexicon and patterns

Empty; inherits parent.

## 4. Sentence-level norms

Inherits parent.
