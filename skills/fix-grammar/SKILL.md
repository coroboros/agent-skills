---
name: fix-grammar
description: Fix grammar, spelling, and typos in files while preserving formatting, meaning, and technical terms. Corrections only — no rephrasing, no style improvements, no translation. Use whenever the user wants proofreading, typo fixes, or spelling/grammar corrections in prose files (Markdown, docs, copy) — even when they just say "proofread this", "fix typos", or "clean up the grammar".
when_to_use: When the user wants grammar, spelling, or typo corrections in one or more prose files. Keywords — fix grammar, proofread, typos, spelling, grammar errors, corrections, clean up, check grammar. Skip when the user wants rewriting, style edits, or translation — those are different jobs. For AI-tell stripping (em-dash overuse, rule-of-three, AI vocabulary) use /humanize-en. For README restructure or clarity pass use /write-clear-readme. Skip on code files unless the request is specifically about comment/docstring grammar.
argument-hint: "<file-path> [additional-files...]"
model: haiku
allowed-tools: Read Edit Agent
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
metadata:
  author: coroboros
---

# Fix Grammar

Fix grammar and spelling errors in: $ARGUMENTS

**Stop** if no files are specified — ask the user for file paths.

## Rules

- Fix **only** spelling and grammar errors
- **Do not** rephrase, reword, or improve style
- **Do not** translate anything — keep the language of each sentence as-is
- **Do not** modify code blocks, MDX tags, frontmatter, or custom syntax
- **Preserve** formatting, structure, meaning, technical terms, and anglicisms
- Handle multilingual content naturally (e.g., French text with English technical terms)

## Workflow

**Single file** — Read, apply corrections with Edit using minimal diffs, report the count.

**Multiple files** — Spawn one subagent per file in a single message so they run in parallel. Each subagent gets the same rules above and returns its file's correction count. Collect results when all complete and produce the combined report.

Grammar checks are per-file independent work with no shared state, so parallelism is pure latency win — N files finish in ~1× file time instead of N×.

## Examples

- English typos — "Thier cat wos hungrey" → "Their cat was hungry" (3 typos fixed)
- Multilingual + accents — "J'ai deployé la fonction useEffect" → "J'ai déployé la fonction useEffect" (accent restored; code identifier untouched)
- Code blocks stay verbatim — any fenced block is preserved even if spelling looks odd inside

## Output

One line per file, aggregated at the end for multi-file runs:

```
fix-grammar: {filename} — {n} corrections
```
