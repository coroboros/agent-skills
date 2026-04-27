# Interview mode — eight canonical questions

Used when `extract` is invoked with no source flag. The skill asks each question via `AskUserQuestion`, one at a time. Answers are stitched into a complete `BRAND-VOICE.md` with `voice.source: "interview"`.

The questions are ordered from structural (cheap to answer, high signal) to subjective (hard to answer, calibrating). Stop asking once enough signal has been captured — questions 7 and 8 are optional if the user is fatigued or short on time.

## Question 1 — Identity

> What is the brand name, what sector does it operate in, and who is the audience? One sentence each.

Captures `voice.name`, contributes to `## 1. Core voice attributes` prose.

## Question 2 — Three absolute adjectives

> Pick three adjectives that describe how the brand sounds. Maximum five words per adjective, no synonyms. (Examples: authoritative, sparse, menacing.)

Each adjective becomes one entry in `core_attributes:`. Aim for 3–5 attributes total — adding two more if the user volunteers.

## Question 3 — Three forbidden adjectives

> Pick three adjectives the brand is *not*. What's the failure mode you most want to avoid? (Examples: chatty, hedging, marketing-pitch.)

Each becomes a `failure_mode` entry on the corresponding attribute (or its own attribute when negative-only). Surfaces what to forbid in prose.

## Question 4 — Owned vocabulary

> Five words or phrases the brand uses on purpose — words you'd be sad to lose. (Examples: branch-stable, temporal coherence, monorepo.)

Populates `required_lexicon:`. Skip if the user has nothing — the field is optional.

## Question 5 — Banned vocabulary

> Five words or phrases the brand never uses. (Examples: game-changing, leverage, journey, solution.)

Seeds `forbidden_lexicon:`. The skill expands the list with common AI-tells (em-dash crutch, marketing taxonomy, hedge words) after the user's input — confirm before saving.

## Question 6 — Pronouns and address

> Default voice — first-person we, third-person institutional ("Acme builds…"), or impersonal passive? And how does the brand address the reader — "you", or indirect statements about the world?

Populates `pronouns.default` and `pronouns.forbid`.

## Question 7 — Punctuation tells

> Three forced choices, one second each.
>
> a. Em-dashes: spaced ` — `, tight `—`, or forbid?
> b. Exclamation marks: allowed or forbidden?
> c. Emoji in prose: allowed (with limits) or forbidden?

Populates `sentence_norms.em_dash_spacing`, `sentence_norms.exclamation_marks`, and adds `emoji` to `forbidden_patterns` when forbidden.

## Question 8 — Three reference texts

> Paste or link three pieces of writing that exemplify the voice. Could be a paragraph, a tweet, a doc page, a competitor's about page — anything where the voice lands. The skill will extract patterns from these.

Adds entries to `voice.source_urls` (or notes inline samples in `## 11. Reference texts`). If the user provides URLs, the skill silently runs `extract -u` on each and merges the result — interview becomes a multi-source extract on the fly.

## After the interview

The skill drafts `BRAND-VOICE.md`, presents the YAML frontmatter and section headings only (not the full prose), and asks for approval before writing.

If approved, the skill writes the file and prints next steps: *"Review prose sections, fill in counter-examples (section 10), then run `/brand-voice show` to confirm the rules look right."*

## Skipping questions

The user can answer "skip" to any question. Question 1 (identity) and at least one of questions 2/5 (attributes or forbidden lexicon) are required — without those there is nothing concrete to write. The rest fall back to defaults documented in `canonical-format.md`.

## Default values when skipped

| Question | Default if skipped |
|---|---|
| 4 — owned vocabulary | `required_lexicon: []` |
| 6 — pronouns | `pronouns.default: "third-person institutional"`, `pronouns.forbid: ["first-person singular"]` |
| 7a — em-dash | `em_dash_spacing: "spaced"` |
| 7b — exclamation | `exclamation_marks: "forbid"` |
| 7c — emoji | adds `emoji` to `forbidden_patterns` |
| 8 — reference texts | `voice.source_urls: []`, `## 11. Reference texts` left as TODO |

The defaults are conservative — they err on the side of restraint, which matches the typical reason a user invokes `brand-voice` (to enforce a less-AI register).
