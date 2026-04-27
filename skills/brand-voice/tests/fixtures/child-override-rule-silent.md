---
voice:
  name: "SilentOverride"
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

sentence_norms:
  word_count_min: 8
  word_count_max: 22
  sentence_max_hard: 30
---

# Brand Voice — SilentOverride

## 1. Core voice attributes

Overrides parent's rule WITHOUT the `override: true` flag → expect a `rewrite-rule-overridden-by-child` warning.

## 2. Rewrite rules — do/don't

Silent overrides regress tone surgically. The lint warning surfaces the collision so reviewers catch unintended drift.

## 3. Forbidden lexicon and patterns

Empty; inherits parent.

## 4. Sentence-level norms

Inherits parent.
