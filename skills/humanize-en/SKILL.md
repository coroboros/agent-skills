---
name: humanize-en
description: Remove AI writing tells from English prose while preserving meaning, structure, code, links and quotations. Use for humanize this, remove AI slop and polish the English on inline text or prose files. Optional -f BRAND-VOICE.md applies brand rules with explicit mechanical and semantic coverage. Inherit authorized rewrite scope; audit/propose remains read-only. Structural README work belongs to write-clear-readme.
when_to_use: Also invoked as a subroutine by other writing skills (e.g., `/write-clear-readme`) to scrub drafts before shipping. Skip for structural restructuring of a README (use `/write-clear-readme` instead), non-English text, or content where AI-authored tone is intentional (transcripts, dataset labels).
argument-hint: "[-f <voice-doc>] [--iterate <N>] [--strict-code-only] [file-path | inline text]"
allowed-tools: Read Write Edit Grep Glob Bash(python3 *)
license: MIT
compatibility: "Requires file access and Python 3.10+ for mechanical scans. Inherited brand rules additionally require brand-voice's resolver or its pre-resolved JSON output. Local-only brand scans work standalone; unresolved inheritance fails with extraction/install guidance."
metadata:
  author: coroboros
  sources: "en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing; github.com/blader/humanizer"
---

# Humanize EN

Strip AI writing tells from English prose. Preserves meaning, structure, code blocks, links, anchors, and frontmatter — rewrites only the flagged phrasing.

Additional context from the user: $ARGUMENTS

## Scope

This skill **removes** AI slop. Default mode (no `-f`): the goal is a clean, direct, human-edited register that preserves the source voice — universal AI tells stripped, no opinion injected. If the source is an opinion piece and the user explicitly asks for voice, `references/voice.md` covers the optional voice-calibration pass.

Under `-f <voice-doc>`, the brand voice is the primary contract. Prescan and validation enforce mechanically detectable rules; the LLM reviews the remaining semantic rules. A mechanical `clean` result covers only those detectors, not every brand rule. Preserve source facts, code and quotations throughout.

## Brand voice integration (optional)

When `$ARGUMENTS` starts with `-f <voice-doc>`, load a `BRAND-VOICE.md` (typically produced by [`/brand-voice`](https://github.com/coroboros/agent-skills/blob/main/skills/brand-voice/SKILL.md)) and treat its rules as the primary contract on top of the universal 32 patterns.

`$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing this SKILL.md elsewhere.

Workflow:

1. Strip `-f <voice-doc>` from the head of `$ARGUMENTS`. The remainder follows the *Input modes* table below as usual.
2. Verify `<voice-doc>` exists and is readable. Missing explicit brand input blocks brand-aware completion; report the exact path/error instead of silently substituting universal-only success.
3. **Resolve once.** Find the installed brand-voice skill through the harness, then its `scripts/extract_rules.py`; known fallback locations are the sibling skill and `~/.agents/skills/brand-voice` or `~/.claude/skills/brand-voice`. Run `python3 <extract_rules.py> --resolved-json <voice-doc> > <temporary-rules.json>` and read that JSON as the LLM's rule contract. It resolves `voice.extends` and `_replace`/`_remove` through the existing resolver. On failure, preserve stderr and stop brand-aware completion. If the resolver is absent and the voice has no inheritance, read its local YAML and use `--brand <voice-doc>` for both checks. Inherited input requires the resolver: report `npx skills add coroboros/agent-skills --skill brand-voice`, then the exact extraction and rerun commands; never claim parent coverage from child-only input.
4. **Run the brand-aware prescan**: `python3 "$SKILL_DIR"/scripts/prescan.py --rules-json <temporary-rules.json> <file>`. Use the same resolved JSON for the LLM and both mechanical checks; do not rescan the original child path. Local-only fallback uses `--brand` instead. Brand hits carry `source: "brand"` and a `rule_id` alongside the 8 mechanically detectable universal patterns.
5. **Cite per source.** Name each hit by source: pattern numbers for universal (`#14`), brand `rule_id`s for brand (`[no-hedging-imperative]`, `[forbidden_lexicon:game-changing]`, `[all_caps_emphasis]`). Brand rules win on direct conflict — a voice that *requires* em-dashes overrides pattern #14.
6. **Validate the authorized edit** with `python3 "$SKILL_DIR"/scripts/validate.py --rules-json <temporary-rules.json> [--baseline <pre-rewrite-hits.json>] <file>` (or the local-only `--brand` input selected above). `clean` ends the mechanical pass; include semantic coverage before completion. `residuals` → surface and iterate within the cap; `regression` → repair the offending edit. Audit-only may validate a temporary proposed rewrite, leaving the target unchanged.
7. Pseudo-tables (` ```text ` or unspecified-language fences) are scanned the same as prose under `-f` — see *Preservation rules*. Real code (` ```python `, ` ```bash `, etc.) stays verbatim.

If the user wants brand-aware rewriting and no voice doc exists, defer: *"No `BRAND-VOICE.md` at `<path>`. Run `/brand-voice extract` first."*

### Iteration model

Default: one pass. Under `-f`, auto-iterate `detect → rewrite → validate` up to 3 rounds (stop on `clean` or `regression`). `--iterate <N>` overrides — `1` disables the loop, `5` raises the cap. Each pass emits the residual coverage table.

## Input modes

Resolve `$ARGUMENTS` (after stripping any leading `-f <voice-doc>`) as follows:

| Input shape | Behavior |
|-------------|----------|
| Empty | Use the target and mode already authorized in the session. Ask only when the target or requested action is unclear. |
| Prose file path | Read the file. An authorized rewrite/polish edits it; audit/propose remains read-only. A path alone does not authorize an edit. |
| Non-prose file path | Refuse: *"Non-prose file — this skill targets prose documents, not structured data or source code."* Rewrite docstring or comment grammar manually. |
| Inline text (anything else) | Humanize in place and return the rewritten text in the chat. |

**Prose extensions** (treat as file): `.md`, `.mdx`, `.txt`, `.rst`, `.tex`, `.html`, `.adoc`.

**Non-prose extensions** (refuse as file): `.json`, `.yaml`, `.yml`, `.toml`, `.csv`, `.tsv`, `.xml`, and any source-code file (`.py`, `.ts`, `.js`, `.rs`, `.go`, `.java`, …). Rewriting data or code files would break parsing or semantics even when the rewrite looks harmless.

Classify the first token via `Glob` (stay in `allowed-tools`, no shell-out): existing file + prose extension → process; + non-prose extension → refuse per the table; + unknown extension (e.g., `CHANGELOG`, `notes.log`) → ask before guessing; nonexistent path → treat as inline text. The middle two branches prevent silent humanizing of data and source-code files.

## Process

1. **Read fully** — the whole text, not one paragraph at a time. Patterns compound across sentences (rule-of-three + synonym cycling + promotional tone often ride together).
2. **Prescan mechanically** — for file inputs, run `python3 "$SKILL_DIR"/scripts/prescan.py <file>` (or pipe inline text via `-`). It detects 8 universal patterns (#1, #4, #7, #8, #9, #14, #23, #28). Under `-f`, use the resolved `--rules-json` or local-only `--brand` input selected in Brand voice integration. Subjective patterns (tone, rule-of-three in body prose, vague attributions) stay LLM-only.
3. **Capture the baseline** — when `-f` is set and the input is a file, save the prescan output to a temp path before any rewrite. The validation gate consumes it via `--baseline` to detect regressions.
4. **Full detect pass** — walk the 32 patterns in [`references/patterns.md`](./references/patterns.md) AND every YAML rule from the brand doc. Do not anchor on the prescan output — the catalogue walk catches what regex cannot, and under `-f` the catalogue is *both* the universal list and the brand rules.
5. **Draft rewrite** — replace flagged phrasing with direct, specific alternatives. Keep sentence-level meaning intact. See *Preservation rules* below for what stays verbatim and what may still be adjusted.
6. **Self-audit** —
   - Default mode: ask *"What still reads as obviously AI-generated?"* List remaining tells in 2–4 bullets. Revise.
   - Under `-f`: walk every `forbidden_pattern`, every `forbidden_lexicon` entry, every `pronouns.forbid` rule, and every `rewrite_rules[*].reject` from the loaded voice doc. Emit the *Coverage report* (see *Output format*) — missing rows are a hard failure, not a stylistic choice.
7. **Validate** — use the same brand input as prescan with `python3 "$SKILL_DIR"/scripts/validate.py --baseline <prescan.json> <file>`. Validate the edited target or the temporary proposal according to the authorized mode. On `residuals`, iterate within the cap; on `regression`, repair the affected passage; on `clean`, finish the semantic review before reporting completion.
8. **Report** — present the rewrite/diff plus the *Coverage report* (count-only by default, rule-by-rule under `-f`). Carry the user's existing target and mode through nested skill calls; do not reopen consent for an authorized edit. For audit/propose, report the proposal and leave the target unchanged.

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

Default mode emits the rewrite and patterns removed. Under `-f`, add coverage for every resolved brand rule, separating mechanical results from semantic review. File edits include their diff and validation result (`clean | residuals | regression`). Audit/propose includes a diff preview without applying it. An invoking skill inherits the user's existing authorization for this target and mode; it cannot create authority for a new target or action.

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
- `scripts/prescan.py` — 8 universal detectors; `--rules-json <rules.json>` adds resolved brand rules, or `--brand <voice-doc>` adds local-only rules. Brand hits carry `source` and `rule_id`. `--strict-code-only` protects every fenced block.
- `scripts/brand_prescan.py` — shared brand detectors and rule-input loading. Local YAML works standalone; inherited rules require the resolver's JSON. Reads `lexical_exceptions.{acronyms,compound_idioms}` to extend the default whitelists.
- `scripts/validate.py` — post-rewrite gate. Re-runs prescan + brand checks on the rewritten file, classifies the outcome (`clean` / `residuals` / `regression`), and writes a JSON report. Exit 0 on clean+residuals, 1 on regression, 2 on argument or I/O errors. Required step under `-f` (Process step 7).
- `scripts/utils.py` — shared I/O helpers (`read_text`, `read_json`, `write_json`, `mask_protected_regions`, `seeded_rng`). `mask_protected_regions` delegates to `prescan.py` so the two stay byte-identical.
- `scripts/eval_patterns.py` — runs prescan over the eval corpus (`eval-corpus/samples/*.json` for universal, `eval-corpus/brand-voice/*.json` with `--brand` for brand). Scores per-sample pass/fail, emits a JSON report per `references/schemas.md` § *eval result*. Exit 0 on full pass, 1 on any failure. Run before editing detection patterns to baseline current coverage, then re-run to confirm no regression.

## Gotchas

1. **Missing resolver:** local-only rules still work through `--brand`; inherited rules stop with exact extraction/install guidance. Discover the installed skill path before using the known fallback locations. Never replace an explicitly requested brand pass with an unlabeled universal-only result.
2. **One rule representation:** read the resolver's JSON and pass that same file to both scripts with `--rules-json`. Scanning the original child via `--brand` is rejected; do not flatten or mutate the user's source voice file to bypass the error.
3. **Pseudo-tables (` ```text ` or no language tag) are prose-eligible.** Use a real code/data language tag such as `python` or `json`, or `--strict-code-only`, to preserve every fenced block. Do not rewrite quoted transcripts merely because their fence lacks a language.
4. **Failed extraction:** preserve the resolver's exact stderr and exit code for cycles, depth or missing parents. A failed command's empty/partial output is not usable resolved rules; do not continue brand-aware completion with it.
