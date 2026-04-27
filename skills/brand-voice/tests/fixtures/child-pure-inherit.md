---
voice:
  name: "PurePersona"
  extends: "./parent-corp.md"
  last_updated: "2026-04-27"
  source: "manual"

core_attributes:
  - attribute_id: laconic
    name: "Laconic"
    failure_mode: "expansion, defense, justification"

forbidden_lexicon: []

rewrite_rules:
  - reject: "this is a stub rule"
    accept: "stub"
    rule_id: stub-rule

sentence_norms:
  word_count_min: 8
  word_count_max: 22
  sentence_max_hard: 30
  contractions: "allow"
---

# Brand Voice — PurePersona

Child voice that inherits everything from ParentCorp without overrides.

## 1. Core voice attributes

This child adds a single attribute and lets every other rule cascade from the parent. The extends mechanism ensures the parent's lexicon, rewrite_rules, sentence_norms, and pronouns are present at consumption time.

## 2. Rewrite rules — do/don't

The single stub rule above is enough to satisfy lint requirements; the parent's two rewrite_rules will merge in.

## 3. Forbidden lexicon and patterns

The empty forbidden_lexicon list emits a warning here, by design — the merged result inherits the parent's three banned terms.

## 4. Sentence-level norms

Norms mirror the parent. The minimal declaration here exists only to satisfy the schema's required-field check on the child file in isolation.
