---
voice:
  name: "ParentCorp — Founder"
  extends: "./parent-corp.md"
  last_updated: "2026-04-27"
  source: "manual"

core_attributes:
  - attribute_id: warm
    name: "Warm"
    failure_mode: "corporate detachment, third-person about self"

forbidden_lexicon:
  - "thought leader"

forbidden_lexicon_remove:
  - "passionate"

pronouns_replace:
  default: "first-person singular"
  forbid: []

rewrite_rules:
  - reject: "The founder believes..."
    accept: "I think..."
    rule_id: founder-no-third-person-self

sentence_norms:
  word_count_min: 8
  word_count_max: 22
  sentence_max_hard: 30
  contractions: "allow"

contexts:
  blog:
    open_with_anecdote: true
    closing_signature: true
---

# Brand Voice — ParentCorp Founder

The founder voice for ParentCorp. Inherits the institutional voice and adapts pronouns and one banned word.

## 1. Core voice attributes

Adds a Warm attribute on top of parent's Precise and Technical.

## 2. Rewrite rules — do/don't

The founder rule joins the parent's two rules at consumption time.

## 3. Forbidden lexicon and patterns

Adds 'thought leader' and lifts the parent's ban on 'passionate' so the founder can use the word in conversational writing.

## 4. Sentence-level norms

Norms mirror the parent; the founder voice does not adjust word counts.
