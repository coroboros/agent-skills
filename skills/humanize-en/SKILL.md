---
name: humanize-en
description: Strip AI writing tells from English prose — em-dash overuse, rule of three, negative parallelisms, AI vocabulary (delve, tapestry, crucial, pivotal, underscore, showcase), vague attributions, promotional tone, conjunctive padding (moreover, furthermore, indeed), hedging, signposting, chatbot artifacts. Preserves meaning, structure, code blocks, links, anchors, and frontmatter — rewrites only the flagged phrasing. Operates on inline text or a prose file path; optionally loads a `BRAND-VOICE.md` via `-f` for brand-specific rules. Use whenever English prose needs to sound less machine-generated — "humanize this", "remove AI tells", "clean up the AI slop", "sounds like ChatGPT", "polish the English" — on READMEs, docs, release notes, blog drafts, PR bodies, or commit messages.
when_to_use: Also invoked as a subroutine by other writing skills (e.g., `/write-clear-readme`) to scrub drafts before shipping. Skip for structural restructuring of a README (use `/write-clear-readme` instead), non-English text, or content where AI-authored tone is intentional (transcripts, dataset labels).
argument-hint: "[-f <voice-doc>] [--iterate <N>] [--strict-code-only] [file-path | inline text]"
allowed-tools: Read Write Edit Grep Glob Bash(python3 *)
license: MIT
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

When `$ARGUMENTS` starts with `-f <voice-doc>`, load a `BRAND-VOICE.md` (typically produced by [`/brand-voice`](https://github.com/coroboros/agent-skills/blob/main/skills/brand-voice/SKILL.md)) and treat its rules as the primary contract on top of the universal 32 patterns.

`$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing this SKILL.md elsewhere.

Workflow:

1. Strip `-f <voice-doc>` from the head of `$ARGUMENTS`. The remainder follows the *Input modes* table below as usual.
2. Verify `<voice-doc>` exists with `Glob`. Missing or unreadable → degrade to default behavior with an explicit warning ("`<path>` not found — applying universal patterns only"). Never crash.
3. **Resolve the rules** with `python3 <extract_rules.py> --full <voice-doc>` — flattens YAML, resolves any `voice.extends` chain, applies `_replace`/`_remove`, emits the merged rule block. Try `"$SKILL_DIR"/../brand-voice/scripts/extract_rules.py`, then `~/.claude/skills/brand-voice/scripts/extract_rules.py`, then `~/.agents/skills/brand-voice/scripts/extract_rules.py`. Non-zero exit surfaces chain-resolution errors (`extends-cycle`, `extends-depth-exceeded`, `extends-parent-not-found`) and aborts. **Fallback** when no candidate resolves: warn *"brand-voice scripts unavailable; chain resolution skipped"* and `Read` the YAML directly — the fallback skips `voice.extends`.
4. **Run the brand-aware prescan** alongside the universal one: `python3 "$SKILL_DIR"/scripts/prescan.py --brand <voice-doc> <file>`. It emits hits for every mechanically detectable YAML rule (forbidden lexicon, rewrite-rule rejects, all-caps emphasis, pronoun violations, signposting, negative parallelism, rule-of-three headings, rhetorical questions, emoji) plus the 8 universal patterns. Brand hits carry `source: "brand"` and a `rule_id`.
5. **Cite per source.** Name each hit by source: pattern numbers for universal (`#14`), brand `rule_id`s for brand (`[no-hedging-imperative]`, `[forbidden_lexicon:game-changing]`, `[all_caps_emphasis]`). Brand rules win on direct conflict — a voice that *requires* em-dashes overrides pattern #14.
6. **Validate after Edit** with `python3 "$SKILL_DIR"/scripts/validate.py --brand <voice-doc> [--baseline <pre-rewrite-hits.json>] <file>`. Outcomes: `clean` → emit *Coverage report* and exit. `residuals` → surface them; auto-iterate up to 3 passes (see *Iteration model*). `regression` → revert the offending edit and re-rewrite.
7. Pseudo-tables (` ```text ` or unspecified-language fences) are scanned the same as prose under `-f` — see *Preservation rules*. Real code (` ```python `, ` ```bash `, etc.) stays verbatim.

If the user wants brand-aware rewriting and no voice doc exists, defer: *"No `BRAND-VOICE.md` at `<path>`. Run `/brand-voice extract` first."*

### Iteration model

Default: one pass. Under `-f`, auto-iterate `detect → rewrite → validate` up to 3 rounds (stop on `clean` or `regression`). `--iterate <N>` overrides — `1` disables the loop, `5` raises the cap. Each pass emits the residual coverage table.

## Input modes

Resolve `$ARGUMENTS` (after stripping any leading `-f <voice-doc>`) as follows:

| Input shape | Behavior |
|-------------|----------|
| Empty | Propose the most recent prose target from session context (recent read/edit/draft) and confirm. Ask only when none is detectable. |
| Prose file path | `Read` the file. Audit, propose a diff, apply only on explicit approval via `Edit`. |
| Non-prose file path | Refuse: *"Non-prose file — this skill targets prose documents, not structured data or source code."* Rewrite docstring or comment grammar manually. |
| Inline text (anything else) | Humanize in place and return the rewritten text in the chat. |

**Prose extensions** (treat as file): `.md`, `.mdx`, `.txt`, `.rst`, `.tex`, `.html`, `.adoc`.

**Non-prose extensions** (refuse as file): `.json`, `.yaml`, `.yml`, `.toml`, `.csv`, `.tsv`, `.xml`, and any source-code file (`.py`, `.ts`, `.js`, `.rs`, `.go`, `.java`, …). Rewriting data or code files would break parsing or semantics even when the rewrite looks harmless.

Classify the first token via `Glob` (stay in `allowed-tools`, no shell-out): existing file + prose extension → process; + non-prose extension → refuse per the table; + unknown extension (e.g., `CHANGELOG`, `notes.log`) → ask before guessing; nonexistent path → treat as inline text. The middle two branches prevent silent humanizing of data and source-code files.

## Process

1. **Read fully** — the whole text, not one paragraph at a time. Patterns compound across sentences (rule-of-three + synonym cycling + promotional tone often ride together).
2. **Prescan mechanically** — for file inputs, run `"$SKILL_DIR"/scripts/prescan.py <file>` (or pipe inline text via `-`). It emits a JSON hit-list for the 8 highest-signal universal patterns (#1, #4, #7, #8, #9, #14, #23, #28). Under `-f`, add `--brand <voice-doc>` so the same script also scans for every mechanically detectable brand rule (forbidden lexicon, rewrite-rule rejects, all-caps emphasis, pronoun violations, signposting, rhetorical questions, rule-of-three headings, emoji, negative parallelism). Subjective patterns (tone, rule-of-three in body prose, vague attributions) stay LLM-only.
3. **Capture the baseline** — when `-f` is set and the input is a file, save the prescan output to a temp path before any rewrite. The validation gate consumes it via `--baseline` to detect regressions.
4. **Full detect pass** — walk the 32 patterns in [`references/patterns.md`](./references/patterns.md) AND every YAML rule from the brand doc. Do not anchor on the prescan output — the catalogue walk catches what regex cannot, and under `-f` the catalogue is *both* the universal list and the brand rules.
5. **Draft rewrite** — replace flagged phrasing with direct, specific alternatives. Keep sentence-level meaning intact. See *Preservation rules* below for what stays verbatim and what may still be adjusted.
6. **Self-audit** —
   - Default mode: ask *"What still reads as obviously AI-generated?"* List remaining tells in 2–4 bullets. Revise.
   - Under `-f`: walk every `forbidden_pattern`, every `forbidden_lexicon` entry, every `pronouns.forbid` rule, and every `rewrite_rules[*].reject` from the loaded voice doc. Emit the *Coverage report* (see *Output format*) — missing rows are a hard failure, not a stylistic choice.
7. **Validate** — for file inputs under `-f`, run `"$SKILL_DIR"/scripts/validate.py --brand <voice-doc> --baseline <prescan.json> <file>` after `Edit` applies. On `residuals`, iterate (up to the cap from *Iteration model*); on `regression`, revert and re-rewrite the affected passage; on `clean`, exit.
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

Default mode emits `## Rewrite` + `## Patterns removed`. Under `-f`, the same shell with a `## Coverage report` table where every YAML rule appears as a row — even with 0 hits, since missing rows are a hard failure. For file paths, add a `## Diff preview` block and (under `-f`) a `## Validation report` with `status: clean | residuals | regression`, then `Apply? (yes/no)` — apply only on explicit `yes` from the end user, even when another skill invokes `/humanize-en` on their behalf.

Full templates with the canonical column order and the approval contract: [`references/output-formats.md`](./references/output-formats.md).

## Rules

Everything not listed below is already enforced by *Process* and *Preservation rules* above.

- **Never** inject first-person voice, opinions, or colloquial hedges into neutral registers (docs, specs, formal READMEs, release notes). The source voice wins (default mode); under `-f`, the brand voice wins; only the AI tells and brand violations go.
- **Never** drop a sentence entirely unless it is pure chatbot artifact (e.g., "I hope this helps!", "Let me know if you'd like me to expand on any section"). Every other sentence gets rewritten, not deleted.
- **Iteration is bounded** — default 1 pass; under `-f`, auto-iterate up to 3 (`detect → rewrite → validate`). Use `--iterate <N>` to override.
- **Match the source register** — a commit message stays terse, a release note stays bulleted, a README paragraph stays prose.
- **Coverage report is the contract** under `-f` — every YAML rule has a row, even with 0 hits. Skipping a rule from the report is a hard failure: the audit either ran or it didn't.

## When to defer to another skill

- Structural problems (wrong headings, missing TOC, collapse patterns) → `/write-clear-readme`.
- Define, update, or inspect a brand voice doc → `/brand-voice extract|update|diff|show`. This skill *consumes* the voice doc via `-f`; `/brand-voice` *produces* it.
- The text is in a non-English language → stop and tell the user; this skill is English-only by design.

## Reference

- `references/patterns.md` — full 32-pattern catalogue with before/after examples. Load when a hit needs context or a reviewer asks *why* a phrase was flagged.
- `references/voice.md` — optional voice calibration for opinion pieces or personal writing. Load only when the user explicitly asks for voice, personality, or a sample-matching pass.
- `references/output-formats.md` — canonical templates for the Rewrite, Coverage report, Diff preview, and Validation report blocks. Load before emitting the final response when the shape needs to be reproduced exactly.
- `references/schemas.md` — JSON shapes for prescan hits (universal + brand), eval samples, eval results, and validate.py output. Consult when editing any script that produces structured output.
- `scripts/prescan.py` — regex-based pre-scan emitting a JSON hit-list. Without flags: 8 universal patterns. With `--brand <voice-doc>`: also emits brand hits with `source: "brand"` and per-rule `rule_id`s. With `--strict-code-only`: blanks every fenced block (legacy behaviour). Python 3.7+, no third-party deps.
- `scripts/brand_prescan.py` — brand-aware detectors loaded by `prescan.py --brand`. Self-contained YAML parser so `humanize-en` works when `brand-voice` is not installed. Reads `lexical_exceptions.{acronyms,compound_idioms}` (top-level frontmatter key, see [brand-voice's canonical-format reference](https://github.com/coroboros/agent-skills/blob/main/skills/brand-voice/references/canonical-format.md)) to extend the hardcoded whitelists.
- `scripts/validate.py` — post-rewrite gate. Re-runs prescan + brand checks on the rewritten file, classifies the outcome (`clean` / `residuals` / `regression`), and writes a JSON report. Exit 0 on clean+residuals, 1 on regression, 2 on argument or I/O errors. Required step under `-f` (Process step 7).
- `scripts/utils.py` — shared I/O helpers (`read_text`, `read_json`, `write_json`, `mask_protected_regions`, `seeded_rng`). `mask_protected_regions` delegates to `prescan.py` so the two stay byte-identical.
- `scripts/eval_patterns.py` — runs prescan over the eval corpus (`eval-corpus/samples/*.json` for universal, `eval-corpus/brand-voice/*.json` with `--brand` for brand). Scores per-sample pass/fail, emits a JSON report per `references/schemas.md` § *eval result*. Exit 0 on full pass, 1 on any failure. Run before editing detection patterns to baseline current coverage, then re-run to confirm no regression.

## Gotchas

1. **`-f` with missing `extract_rules.py` silently degrades to universal patterns.** The 3-tier path fallback (`"$SKILL_DIR"/../brand-voice/scripts/extract_rules.py`, `~/.claude/skills/brand-voice/scripts/extract_rules.py`, `~/.agents/skills/brand-voice/scripts/extract_rules.py`) succeeds on standard installs but a non-standard layout (e.g., custom plugin dir) drops brand rules with a warning the model may overlook. Fix: pre-check the path before relying on brand-rule injection; the warning text is `brand-voice scripts unavailable; chain resolution skipped`.
2. **`voice.extends` chain not resolved before prescan when scripts degrade.** When the fallback fires (above), `brand_prescan.py` reads the YAML directly and applies child rules only; parent constraints in the chain are skipped silently. Fix: when `--brand` is critical and scripts are unavailable, flatten the chain in the source file before invoking, or install `brand-voice` scripts at one of the canonical paths.
3. **Pseudo-tables (` ```text ` with no language tag) are rewritten as prose.** Code blocks without a language hint are treated as prose-eligible content and may be rewritten; users expecting verbatim preservation get a surprise. Fix: tag every code/data block with a language hint (` ```python `, ` ```json `, ` ```text `); pass `--strict-code-only` to force preservation of all fenced blocks.
4. **`--brand` chain-resolution errors don't always surface in the user-facing output.** `extract_rules.py` exits non-zero on `extends-cycle`, `extends-depth-exceeded`, `extends-parent-not-found`; the orchestrator sometimes drops the stderr in favor of running with degraded rules. Fix: when `--brand` is set, always check `scripts/extract_rules.py`'s exit code before continuing; non-zero means brand rules will be incomplete.
