---
voice:
  name: "ParentCorp"
  source_urls:
    - https://example.com
  last_updated: "2026-04-27"
  source: "manual"

core_attributes:
  - attribute_id: precise
    name: "Precise"
    failure_mode: "vague claims, hedging"
  - attribute_id: technical
    name: "Technical"
    failure_mode: "dumbing down, hand-holding"

forbidden_lexicon:
  - "game-changing"
  - "passionate"
  - "synergies"

required_lexicon:
  - "branch-stable"

rewrite_rules:
  - reject: "It might be worth considering..."
    accept: "Use X."
    rule_id: no-hedging-imperative
  - reject: "significantly faster"
    accept: "<cite a number>"
    rule_id: specific-over-abstract-speed

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
  - emoji

contexts:
  rfc:
    density: "max"
    numbered_sections: true
  readme:
    tagline_first: true

pronouns:
  default: "third-person institutional"
  forbid:
    - "first-person singular"
---

# Brand Voice — ParentCorp

Synthetic parent voice used by inheritance fixtures.

## 1. Core voice attributes

The institutional voice is precise and technical. No hedging, no marketing taxonomy. Statements stand on their own weight without qualifier or apology.

## 2. Rewrite rules — do/don't

Each rejected pattern has a concrete replacement. Authors apply the table mechanically; reviewers cite rule_ids in feedback.

## 3. Forbidden lexicon and patterns

The forbidden list captures terms drained of meaning by overuse. The forbidden patterns capture rhythmic tells of AI authorship, including rule of three and emoji decoration.

## 4. Sentence-level norms

Most sentences run between eight and twenty-two words. Compound sentences are reserved for explaining causality. The hard ceiling sits at thirty words; longer sentences are split.
