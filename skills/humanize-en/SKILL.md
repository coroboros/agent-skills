---
name: humanize-en
description: Strip AI writing tells from English prose — em-dash overuse, rule of three, negative parallelisms, AI vocabulary (delve, tapestry, crucial, pivotal, underscore, showcase), vague attributions, promotional tone, conjunctive padding (moreover, furthermore, indeed), hedging, signposting, chatbot artifacts. Preserves meaning, structure, code blocks, links, anchors, and frontmatter — rewrites only the flagged phrasing. Operates on inline text or a prose file path. Based on Wikipedia's Signs of AI writing (canonical taxonomy) with pattern extensions and the voice-calibration approach from github.com/blader/humanizer.
when_to_use: Invoke whenever English prose needs to sound less machine-generated — READMEs, docs, release notes, blog drafts, PR bodies, marketing copy, commit messages, commentary. Triggers on phrases like "humanize this", "remove AI tells", "clean up the AI slop", "sounds like ChatGPT", "make this less AI-sounding", "polish the English", "strip AI patterns". Also invoked as a subroutine by other writing skills (e.g., `/write-clear-readme`) to scrub drafts before shipping. Skip for grammar-only fixes (use `/fix-grammar` instead), structural restructuring of a README (use `/write-clear-readme` instead), non-English text, or content where AI-authored tone is intentional (transcripts, dataset labels).
argument-hint: "[file-path | inline text]"
model: sonnet
allowed-tools: Read Write Edit Grep Glob
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
metadata:
  author: coroboros
  sources:
    - en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
    - github.com/blader/humanizer
---

# Humanize EN

Strip AI writing tells from English prose. Preserves meaning, structure, code blocks, links, anchors, and frontmatter — rewrites only the flagged phrasing.

Additional context from the user: $ARGUMENTS

## Scope

This skill **removes** AI slop. It does not **inject** personality — that can break technical documentation, formal specs, and any neutral-voice register. The goal is a clean, direct, human-edited register, not an opinionated blog post. If the source is an opinion piece and the user explicitly asks for voice, `references/voice.md` covers the optional voice-calibration pass.

## Input modes

Resolve `$ARGUMENTS` as follows:

| Input shape | Behavior |
|-------------|----------|
| Empty | Ask the user to paste text or provide a file path. Do not guess. |
| Prose file path | `Read` the file. Audit, propose a diff, apply only on explicit approval via `Edit`. |
| Non-prose file path | Refuse: *"Non-prose file — this skill targets prose documents, not structured data or source code."* Direct the user to `/fix-grammar` for docstring grammar, or to rewrite comments manually. |
| Inline text (anything else) | Humanize in place and return the rewritten text in the chat. |

**Prose extensions** (treat as file): `.md`, `.mdx`, `.txt`, `.rst`, `.tex`, `.html`, `.adoc`.

**Non-prose extensions** (refuse as file): `.json`, `.yaml`, `.yml`, `.toml`, `.csv`, `.tsv`, `.xml`, and any source-code file (`.py`, `.ts`, `.js`, `.rs`, `.go`, `.java`, …). Rewriting data or code files would break parsing or semantics even when the rewrite looks harmless.

Classify the first token (use `Glob` to verify the path exists — stay within `allowed-tools`, do not shell out):

- resolves to an existing file AND extension on the prose list → *Prose file path* (process it)
- resolves to an existing file AND extension on the non-prose list → *Non-prose file path* (refuse per the table above)
- resolves to an existing file AND extension on neither list → ask the user whether to process it as prose or refuse it as non-prose. Do not guess — real cases like `CHANGELOG` (no extension) or `notes.log` go here.
- does not resolve → treat the whole input as inline text

The two middle branches are what actually prevent data / source-code / unknown files from being silently humanized as inline strings.

## Process

1. **Read fully** — the whole text, not one paragraph at a time. Patterns compound across sentences (rule-of-three + synonym cycling + promotional tone often ride together).
2. **Prescan mechanically** — for file inputs, run `${CLAUDE_SKILL_DIR}/scripts/prescan.py <file>` (or pipe inline text via `-`). It emits a JSON hit-list for the 8 highest-signal mechanical patterns (#1, #4, #7, #8, #9, #14, #23, #28). Start the rewrite from the flagged lines. Subjective patterns (tone, rule-of-three in context, vague attributions) stay LLM-only.
3. **Full detect pass** — scan against the 32 patterns in [`references/patterns.md`](./references/patterns.md). The prescan catches roughly 60-70% of real hits; the full catalog catches the rest.
4. **Draft rewrite** — replace flagged phrasing with direct, specific alternatives. Keep sentence-level meaning intact. See *Preservation rules* below for what stays verbatim and what may still be adjusted.
5. **Self-audit** — ask: *"What still reads as obviously AI-generated?"* List remaining tells in 2–4 bullets. Revise.
6. **Report** — present the final rewrite plus a short changelog of which patterns were touched (by number from the catalog). For file inputs, propose the diff and wait for approval before `Edit`.

## Quick reference — the 10 highest-signal tells

Roughly 90% of real AI slop comes from this subset. Full catalog with before/after examples is in [`references/patterns.md`](./references/patterns.md) — consult it when a hit needs context or you are unsure whether to flag.

| # | Pattern | Instead |
|---|---------|---------|
| 1 | *Significance inflation* — "pivotal moment", "testament to", "evolving landscape" | State the fact directly. |
| 3 | *Superficial -ing* — "…reflecting broader trends", "…underscoring the importance" | End the sentence; drop the participial coda. |
| 4 | *Promotional* — "nestled", "breathtaking", "vibrant", "stunning" | Neutral description with a concrete detail. |
| 7 | *AI vocabulary* — delve, tapestry, intricate, pivotal, testament, underscore, crucial, garner, showcase, vibrant, interplay, align with, additionally, moreover, furthermore, indeed | Plain-English equivalent or delete. |
| 8 | *Copula avoidance* — "serves as", "stands as", "features", "boasts" | Use `is`/`are`/`has`. |
| 9 | *Negative parallelism* — "It's not just X, it's Y" | Direct affirmative sentence. |
| 10 | *Rule of three* — three-item lists where two or four would be honest | Use the real count. |
| 14 | *Em-dash overuse* | Prefer commas or periods unless the dash does real work. |
| 23 | *Filler phrases* — "in order to", "it is important to note that", "at this point in time" | Delete or contract. |
| 28 | *Signposting* — "Let's dive in", "Here's what you need to know", "Without further ado" | Just say the thing. |

## Preservation rules

The rewrite must NOT change:

- **Code** — anything inside backticks, fenced code blocks, or `<code>…</code>`.
- **URLs and anchors** — the `(url)` portion of `[text](url)`, `#anchor` refs, image paths.
- **Frontmatter** — YAML/TOML blocks at file top.
- **Quoted material** — text inside `"…"` attributed to a person or source.
- **Technical terms, proper nouns, product names** — even when they match an "AI vocabulary" flag in other contexts (e.g., a product literally named "Tapestry" is not a pattern-7 hit).
- **Structural markers** — heading levels, list depth, table columns, HTML tag syntax (tag names and attribute names). Rewrite the *prose inside* the structure; do not restructure.
- **Factual claims** — if a sentence states a number, date, or attribution, preserve it verbatim even when the surrounding clause is rewritten.

**May be adjusted** — link text inside `[…]` is prose and can be rewritten when it carries AI tells (e.g., `[delve into the transformative landscape]` → `[read more]`). HTML attributes that contain prose (`alt`, `title`, `aria-label`) follow the same principle.

When in doubt, keep the original token and only adjust the connective tissue around it.

## Output format

### For inline text

```
## Rewrite

<humanized text>

## Patterns removed

- #N <pattern name> — <short note, e.g., "4 instances, em-dashes converted to commas">
- ...
```

### For file paths

```
## Diff preview

<unified-diff-style or before/after blocks for changed passages>

## Patterns removed

- #N <pattern name> — <count>
- ...

Apply? (yes/no)
```

Apply only on explicit `yes` **from the user**. When another skill invokes `/humanize-en` on a file, the approval prompt still flows to the end user — a parent skill must not auto-answer on their behalf.

## Rules

Everything not listed below is already enforced by *Process* and *Preservation rules* above.

- **Never** inject first-person voice, opinions, or colloquial hedges into neutral registers (docs, specs, formal READMEs, release notes). The source voice wins; only the AI tells go.
- **Never** drop a sentence entirely unless it is pure chatbot artifact (e.g., "I hope this helps!", "Let me know if you'd like me to expand on any section"). Every other sentence gets rewritten, not deleted.
- **One pass only** — do not recurse. If the user wants a second round, they ask.
- **Match the source register** — a commit message stays terse, a release note stays bulleted, a README paragraph stays prose.

## When to defer to another skill

- Pure spelling or grammar errors → `/fix-grammar`.
- Structural problems (wrong headings, missing TOC, collapse patterns) → `/write-clear-readme`.
- The text is in a non-English language → stop and tell the user; this skill is English-only by design.

## Reference

- `references/patterns.md` — full 32-pattern catalogue with before/after examples. Load when a hit needs context or a reviewer asks *why* a phrase was flagged.
- `references/voice.md` — optional voice calibration for opinion pieces or personal writing. Load only when the user explicitly asks for voice, personality, or a sample-matching pass.
- `scripts/prescan.py` — regex-based pre-scan emitting a JSON hit-list for the 8 highest-signal mechanical patterns. Python 3.7+, no third-party deps. Called in Process step 2 above.
