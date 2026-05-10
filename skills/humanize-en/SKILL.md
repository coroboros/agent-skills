---
name: humanize-en
description: Strip AI writing tells from English prose — em-dash overuse, rule of three, negative parallelisms, AI vocabulary (delve, tapestry, crucial, pivotal, underscore, showcase), vague attributions, promotional tone, conjunctive padding (moreover, furthermore, indeed), hedging, signposting, chatbot artifacts. Preserves meaning, structure, code blocks, links, anchors, and frontmatter — rewrites only the flagged phrasing. Operates on inline text or a prose file path. Optionally loads a `BRAND-VOICE.md` via `-f` (produced by `/brand-voice`) to apply brand-specific rules on top of the universal patterns. Based on Wikipedia's Signs of AI writing (canonical taxonomy) with pattern extensions and the voice-calibration approach from github.com/blader/humanizer.
when_to_use: Invoke whenever English prose needs to sound less machine-generated — READMEs, docs, release notes, blog drafts, PR bodies, marketing copy, commit messages, commentary. Triggers on phrases like "humanize this", "remove AI tells", "clean up the AI slop", "sounds like ChatGPT", "make this less AI-sounding", "polish the English", "strip AI patterns". Also invoked as a subroutine by other writing skills (e.g., `/write-clear-readme`) to scrub drafts before shipping. Skip for grammar-only fixes (use `/fix-grammar` instead), structural restructuring of a README (use `/write-clear-readme` instead), non-English text, or content where AI-authored tone is intentional (transcripts, dataset labels).
argument-hint: "[-f <voice-doc>] [--iterate <N>] [--strict-code-only] [file-path | inline text]"
model: sonnet
allowed-tools: Read Write Edit Grep Glob Bash(python3 *)
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

This skill **removes** AI slop. Default mode (no `-f`): the goal is a clean, direct, human-edited register that preserves the source voice — universal AI tells stripped, no opinion injected. If the source is an opinion piece and the user explicitly asks for voice, `references/voice.md` covers the optional voice-calibration pass.

Under `-f <voice-doc>`: the skill raises the bar. The brand voice becomes the primary contract — every rule in the loaded `BRAND-VOICE.md` (forbidden lexicon, pronouns, rewrite rules, forbidden patterns, lexical exceptions) is enforced deterministically by `prescan.py --brand`, then by the LLM pass, then re-validated by `validate.py`. The 32 universal patterns are the floor; the brand voice is the ceiling.

## Brand voice integration (optional)

When `$ARGUMENTS` starts with `-f <voice-doc>`, load a `BRAND-VOICE.md` (typically produced by [`/brand-voice`](../brand-voice/SKILL.md)) and treat its rules as the primary contract on top of the universal 32 patterns.

Workflow:

1. Strip `-f <voice-doc>` from the head of `$ARGUMENTS`. The remainder follows the *Input modes* table below as usual.
2. Verify `<voice-doc>` exists with `Glob`. Missing or unreadable → degrade to default behavior with an explicit warning ("`<path>` not found — applying universal patterns only"). Never crash.
3. **Resolve the rules for the LLM prompt** by running `extract_rules.py --full` on the voice doc. The script flattens YAML into plain text, automatically resolves any `voice.extends` chain, applies `_replace` and `_remove` overrides, and emits the merged rule block. Resolution order for the script path:
   1. `${CLAUDE_SKILL_DIR}/../brand-voice/scripts/extract_rules.py` (sibling install)
   2. `~/.claude/skills/brand-voice/scripts/extract_rules.py` (user-installed brand-voice)
   3. `~/.agents/skills/brand-voice/scripts/extract_rules.py` (Anthropic skills directory)

   Invoke via `python3 <resolved-script> --full <voice-doc>`. Non-zero exit surfaces chain-resolution errors (`extends-cycle`, `extends-depth-exceeded`, `extends-parent-not-found`) and aborts the brand-aware pass. **Fallback** when no candidate resolves: warn *"brand-voice scripts unavailable; chain resolution skipped"* and `Read` the YAML frontmatter directly (`forbidden_lexicon`, `required_lexicon`, `rewrite_rules`, `sentence_norms`, `forbidden_patterns`, `pronouns`, `core_attributes`, `contexts`, `lexical_exceptions`). The fallback skips `voice.extends`.
4. **Run the brand-aware prescan** alongside the universal one: `python3 ${CLAUDE_SKILL_DIR}/scripts/prescan.py --brand <voice-doc> <file>`. It emits hits for every YAML rule that is mechanically detectable (forbidden lexicon, rewrite-rule rejects, all-caps emphasis, pronoun violations, signposting, negative parallelism, rule-of-three headings, rhetorical questions, emoji) plus the 8 universal patterns. Brand hits carry a `source: "brand"` discriminator and a `rule_id` so the coverage report can attribute each rewrite.
5. **Cite per source.** In the rewrite report, name each hit by source: pattern numbers for universal (`#14`), brand `rule_id`s for brand (`[no-hedging-imperative]`, `[forbidden_lexicon:game-changing]`, `[all_caps_emphasis]`). Brand rules win on direct conflict — a voice that *requires* em-dashes overrides pattern #14.
6. **Validate after Edit** with `python3 ${CLAUDE_SKILL_DIR}/scripts/validate.py --brand <voice-doc> [--baseline <pre-rewrite-hits.json>] <file>`. Outcomes drive the iteration loop:
   - `status="clean"` — emit the *Coverage report* and exit.
   - `status="residuals"` — surface the residuals; under `-f`, auto-iterate (see *Iteration model* below) up to three passes before yielding to the user.
   - `status="regression"` — at least one new hit was introduced. Revert the offending edit and try again.
7. Pseudo-tables (` ```text ` or unspecified-language fences) are scanned the same as prose under `-f` — see *Preservation rules*. Real code (` ```python `, ` ```bash `, etc.) stays verbatim.

If the user wants brand-aware rewriting and no voice doc exists, defer: *"No `BRAND-VOICE.md` at `<path>`. Run `/brand-voice extract` first."*

### Iteration model

Default: one pass (`detect → rewrite`). Under `-f` the skill auto-iterates up to three rounds: `detect → rewrite → validate`, repeating while `validate.py` reports residuals AND iteration count < 3 AND no regression appears. The user may override:

- `--iterate <N>` — explicit cap (1 disables the loop entirely, 5 raises it).
- `--iterate 1` plus `-f` keeps the legacy single-pass behaviour for users who prefer manual control.

Each iteration emits the residual coverage table so the user can stop early.

## Input modes

Resolve `$ARGUMENTS` (after stripping any leading `-f <voice-doc>`) as follows:

| Input shape | Behavior |
|-------------|----------|
| Empty | Propose the most recent prose target from session context (recent read/edit/draft) and confirm. Ask only when none is detectable. |
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
2. **Prescan mechanically** — for file inputs, run `${CLAUDE_SKILL_DIR}/scripts/prescan.py <file>` (or pipe inline text via `-`). It emits a JSON hit-list for the 8 highest-signal universal patterns (#1, #4, #7, #8, #9, #14, #23, #28). Under `-f`, add `--brand <voice-doc>` so the same script also scans for every mechanically detectable brand rule (forbidden lexicon, rewrite-rule rejects, all-caps emphasis, pronoun violations, signposting, rhetorical questions, rule-of-three headings, emoji, negative parallelism). Subjective patterns (tone, rule-of-three in body prose, vague attributions) stay LLM-only.
3. **Capture the baseline** — when `-f` is set and the input is a file, save the prescan output to a temp path before any rewrite. The validation gate consumes it via `--baseline` to detect regressions.
4. **Full detect pass** — walk the 32 patterns in [`references/patterns.md`](./references/patterns.md) AND every YAML rule from the brand doc. Do not anchor on the prescan output — the catalogue walk catches what regex cannot, and under `-f` the catalogue is *both* the universal list and the brand rules.
5. **Draft rewrite** — replace flagged phrasing with direct, specific alternatives. Keep sentence-level meaning intact. See *Preservation rules* below for what stays verbatim and what may still be adjusted.
6. **Self-audit** —
   - Default mode: ask *"What still reads as obviously AI-generated?"* List remaining tells in 2–4 bullets. Revise.
   - Under `-f`: walk every `forbidden_pattern`, every `forbidden_lexicon` entry, every `pronouns.forbid` rule, and every `rewrite_rules[*].reject` from the loaded voice doc. Emit the *Coverage report* (see *Output format*) — missing rows are a hard failure, not a stylistic choice.
7. **Validate** — for file inputs under `-f`, run `${CLAUDE_SKILL_DIR}/scripts/validate.py --brand <voice-doc> --baseline <prescan.json> <file>` after `Edit` applies. On `residuals`, iterate (up to the cap from *Iteration model*); on `regression`, revert and re-rewrite the affected passage; on `clean`, exit.
8. **Report** — present the final rewrite plus the *Coverage report* (count-only by default, rule-by-rule under `-f`). For file inputs, propose the diff and wait for approval before `Edit`.

## Quick reference — the 10 highest-signal tells

Roughly 90% of real AI slop comes from this subset. The 8 mechanical patterns (#1, #4, #7, #8, #9, #14, #23, #28) are pre-flagged by `prescan.py`; #3 and #10 stay LLM-only — too context-dependent for regex. Full catalog with before/after examples is in [`references/patterns.md`](./references/patterns.md) — consult it when a hit needs context or you are unsure whether to flag.

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

- **Real code** — anything inside backticks, or fenced blocks **with a language hint** (e.g. ` ```python `, ` ```bash `, ` ```typescript `, ` ```json `, ` ```yaml `, ` ```sql `). The info-string after the opening fence is the discriminator.
- **URLs and anchors** — the `(url)` portion of `[text](url)`, `#anchor` refs, image paths.
- **Frontmatter** — YAML/TOML blocks at file top.
- **Quoted material** — text inside `"…"` attributed to a person or source.
- **Technical terms, proper nouns, product names** — even when they match an "AI vocabulary" flag in other contexts (e.g., a product literally named "Tapestry" is not a pattern-7 hit).
- **Structural markers** — heading levels, list depth, table columns, HTML tag syntax (tag names and attribute names). Rewrite the *prose inside* the structure; do not restructure.
- **Factual claims** — if a sentence states a number, date, or attribution, preserve it verbatim even when the surrounding clause is rewritten.

**Pseudo-tables** — fenced blocks with **no info-string** or `text` (e.g. ` ``` ` alone, ` ```text `) are treated as prose, not code. They typically hold label-prefixed columns (`INSTRUMENTS   Log drum…`), terminal transcripts, or ASCII layouts. Their content is scanned and rewritten — but column alignment is preserved (auto-pad after a token-length change). To suppress pseudo-block scanning entirely (treat every fenced block as code), pass `--strict-code-only` to `prescan.py` and `validate.py`.

**May be adjusted** — link text inside `[…]` is prose and can be rewritten when it carries AI tells (e.g., `[delve into the transformative landscape]` → `[read more]`). HTML attributes that contain prose (`alt`, `title`, `aria-label`) follow the same principle.

When in doubt, keep the original token and only adjust the connective tissue around it.

## Output format

### For inline text (default mode)

```
## Rewrite

<humanized text>

## Patterns removed

- #N <pattern name> — <short note, e.g., "4 instances, em-dashes converted to commas">
- ...
```

### For inline text under `-f`

```
## Rewrite

<humanized text>

## Coverage report

| Rule | Source | Detection | Hits | Action | Residual |
|---|---|---|---|---|---|
| #14 em-dash density | universal | prescan | 8 | preserved (citation format) | 0 |
| brand:all_caps_emphasis | brand | prescan-brand | 14 | rewrite | 0 |
| brand:negative_parallelism | brand | prescan-brand | 4 | rewrite | 0 |
| brand:forbidden_lexicon (26 entries) | brand | prescan-brand | 0 | n/a | 0 |
```

Every YAML rule appears in the table — even with 0 hits — so a future pass can verify the prior pass actually checked the rule. Missing rows are a hard failure, not a stylistic choice.

### For file paths

```
## Diff preview

<unified-diff-style or before/after blocks for changed passages>

## Coverage report
<as above; count-only summary in default mode>

## Validation report (under `-f` only)

status: clean | residuals | regression
<residual hits or regression diff if any>

Apply? (yes/no)
```

Apply only on explicit `yes` **from the user**. When another skill invokes `/humanize-en` on a file, the approval prompt still flows to the end user — a parent skill must not auto-answer on their behalf.

## Rules

Everything not listed below is already enforced by *Process* and *Preservation rules* above.

- **Never** inject first-person voice, opinions, or colloquial hedges into neutral registers (docs, specs, formal READMEs, release notes). The source voice wins (default mode); under `-f`, the brand voice wins; only the AI tells and brand violations go.
- **Never** drop a sentence entirely unless it is pure chatbot artifact (e.g., "I hope this helps!", "Let me know if you'd like me to expand on any section"). Every other sentence gets rewritten, not deleted.
- **Iteration is bounded** — default 1 pass; under `-f`, auto-iterate up to 3 (`detect → rewrite → validate`). Use `--iterate <N>` to override.
- **Match the source register** — a commit message stays terse, a release note stays bulleted, a README paragraph stays prose.
- **Coverage report is the contract** under `-f` — every YAML rule has a row, even with 0 hits. Skipping a rule from the report is a hard failure: the audit either ran or it didn't.

## When to defer to another skill

- Pure spelling or grammar errors → `/fix-grammar`.
- Structural problems (wrong headings, missing TOC, collapse patterns) → `/write-clear-readme`.
- Define, update, or inspect a brand voice doc → `/brand-voice extract|update|diff|show`. This skill *consumes* the voice doc via `-f`; `/brand-voice` *produces* it.
- The text is in a non-English language → stop and tell the user; this skill is English-only by design.

## Reference

- `references/patterns.md` — full 32-pattern catalogue with before/after examples. Load when a hit needs context or a reviewer asks *why* a phrase was flagged.
- `references/voice.md` — optional voice calibration for opinion pieces or personal writing. Load only when the user explicitly asks for voice, personality, or a sample-matching pass.
- `references/schemas.md` — JSON shapes for prescan hits (universal + brand), eval samples, eval results, and validate.py output. Consult when editing any script that produces structured output.
- `scripts/prescan.py` — regex-based pre-scan emitting a JSON hit-list. Without flags: 8 universal patterns. With `--brand <voice-doc>`: also emits brand hits with `source: "brand"` and per-rule `rule_id`s. With `--strict-code-only`: blanks every fenced block (legacy behaviour). Python 3.7+, no third-party deps.
- `scripts/brand_prescan.py` — brand-aware detectors loaded by `prescan.py --brand`. Self-contained YAML parser so `humanize-en` works when `brand-voice` is not installed. Reads `voice.lexical_exceptions.{acronyms,compound_idioms}` to extend the hardcoded whitelists.
- `scripts/validate.py` — post-rewrite gate. Re-runs prescan + brand checks on the rewritten file, classifies the outcome (`clean` / `residuals` / `regression`), and writes a JSON report. Exit 0 on clean+residuals, 1 on regression, 2 on argument or I/O errors. Required step under `-f` (Process step 7).
- `scripts/utils.py` — shared I/O helpers (`read_text`, `read_json`, `write_json`, `mask_protected_regions`, `seeded_rng`). `mask_protected_regions` delegates to `prescan.py` so the two stay byte-identical.
- `scripts/eval_patterns.py` — runs prescan over the eval corpus (`eval-corpus/samples/*.json` for universal, `eval-corpus/brand-voice/*.json` with `--brand` for brand). Scores per-sample pass/fail, emits a JSON report per `references/schemas.md` § *eval result*. Exit 0 on full pass, 1 on any failure. Run before editing detection patterns to baseline current coverage, then re-run to confirm no regression.
