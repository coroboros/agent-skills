---
name: brand-voice
description: Create, refresh, compare and validate BRAND-VOICE.md from web, Notion, local prose or an interview. Use for brand voice, writing style guide, founder/persona voice and voice.extends inheritance. Preserve manual sections and resolve source conflicts. Applying an existing voice to prose belongs to humanize-en -f.
when_to_use: Routes via `$ARGUMENTS` first token — `extract` (sources → BRAND-VOICE.md; `--extends <parent>` scaffolds a child), `update` (refresh from new sources), `diff` (regression check; single-arg form when child has `voice.extends`), `validate` / `lint` / `check` (walks chain), `show` (testable rules; `--chain`/`--explain`/`--raw` for inheritance). Skip when the user wants to apply or check prose against an existing voice (rewrite, humanize, "does this match") — invoke `/humanize-en -f BRAND-VOICE.md` instead.
argument-hint: "[extract|update|diff|validate|show] [-s] [-o <path>] [-u <url>] [-n <id|url>] [-d <dir>] [-f <file>] [refs|paths]"
license: MIT
compatibility: "Requires filesystem access and Python 3.10+ for bundled validation and inheritance tools. Web and Notion sources require corresponding read capabilities. Interviews use the host's supported question mechanism; local-source work does not require those connectors."
allowed-tools: Read Write Edit Grep Glob WebFetch AskUserQuestion Bash(jq *) Bash(test *) Bash(wc *) Bash(find *) Bash(python3 *) Bash(git *) Bash(mktemp *)
metadata:
  author: coroboros
  sources: "github.com/google-labs-code/design.md; en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing; every.to/on-every/introducing-spiral-v3-an-ai-writing-partner-with-taste"
---

# Brand Voice

<!-- canonical:writing-rules:start -->
## Important — Writing rules

Apply these rules to emitted prose: docs, comments, commit messages, PR bodies, and release notes.

- Match surrounding punctuation, capitalization, and formatting.
- Every sentence changes the reader's understanding. Cut it otherwise.
- Lead with the action or outcome.
- Use concrete language and lists when they improve comparison or sequence.
- Assert positively. Reserve negation for real constraints (`NEVER commit secrets`).
- No marketing words: powerful, robust, seamlessly, leverage, unlock, comprehensive, delightful.
- No AI tells: delve, tapestry, intricate, pivotal, testament, underscore, crucial, garner, showcase, additionally, moreover, furthermore, indeed.
- For substantive English prose, use `/humanize-en` if installed with the existing scope and authorization. It adds no approval stage; skip redundant passes over short status text.
<!-- canonical:writing-rules:end -->

Govern `BRAND-VOICE.md` — the canonical writing voice document for a brand. Two layers: YAML frontmatter (machine-readable normative rules consumed by writing skills) plus eleven prose sections (human-readable rationale). Same split as `DESIGN.md` and the same `design-system` skill pattern: a canonical file at the project root, CLI-style subcommands for the lifecycle.

Additional context from the user: $ARGUMENTS

## Subcommand routing

Parse the first positional token of `$ARGUMENTS`. If it matches a verb below, load the referenced file and follow its workflow. Otherwise fall through to the default workflow at the end of this document.

| First token | Mode | Reference |
|-------------|------|-----------|
| `extract` | Ingest sources, synthesise canonical voice doc, write to `./BRAND-VOICE.md` | [`steps/extract.md`](./steps/extract.md) |
| `update` | Refresh an existing voice doc from new sources, preserve manual sections | [`steps/update.md`](./steps/update.md) |
| `diff` | Show what changed between two versions of the voice doc (git-aware) | [`steps/diff.md`](./steps/diff.md) |
| `validate` (aliases: `lint`, `check`) | Lint a voice doc against `canonical-format.md` — verdict + errors + warnings + fix suggestions, CI-friendly exit codes | [`steps/validate.md`](./steps/validate.md) |
| `show` | Print the flat list of testable rules from the voice doc | [`steps/show.md`](./steps/show.md) |
| (none) | See *Default workflow* below | (this file) |

There is no `apply` subcommand. Application of the voice — rewriting prose to match it — is the consumer skill's job. `humanize-en -f BRAND-VOICE.md` uses `scripts/extract_rules.py --resolved-json` so its semantic and mechanical passes share the effective mapping. Other consumers follow the same contract. Direct YAML is sufficient only for local rules without `voice.extends`; unavailable resolution of an inherited voice remains an explicit gap.

## Canonical file location

The voice doc lives at `./BRAND-VOICE.md` by default — at the project root, versioned in git, alongside `DESIGN.md`, `README.md`, `LICENSE.md`. Override the path with `-o <path>` when the voice is multi-project.

`extract` refuses to overwrite an existing file. To refresh, use `update`. To replace, delete first.

When `-s` is passed alongside `extract`, the skill also writes a copy to `~/.agents/output/{project}/brand-voice/brand-voice-{slug}.md` for pipeline-history consumers (`{slug}` = kebab of `voice.name`; `{project}` = kebab-cased basename of the git toplevel, else cwd) and reports its fully-expanded absolute path (no tilde, no magic). The canonical file at `./BRAND-VOICE.md` remains the single source of truth.

### Cross-repo distribution

When a brand spans repositories, choose a shared-source pattern and document it in each authorized project's active instruction entrypoint (AGENTS.md, CLAUDE.md or its local equivalent). Identify other consumers without editing projects outside the request:

- **Brand workspace canonical** — keep `BRAND-VOICE.md` at the brand workspace root (e.g. `~/<brand>/BRAND-VOICE.md`). Each subproject references it via absolute path: `/humanize-en -f ~/<brand>/BRAND-VOICE.md draft.md`. Simplest. Best when subprojects share a local workspace.
- **Monorepo** — `packages/brand/BRAND-VOICE.md` consumed by every app in the monorepo. Single PR for cross-cutting voice changes.
- **Git submodule** — canonical brand repo included as a submodule. Atomic updates via submodule bump. Best when the brand is owned by a separate team.
- **Published package** — `@<org>/brand-voice` on npm with `BRAND-VOICE.md` plus the bundled scripts (`extract_rules.py`, `voice_lint.py`). Versioned, works cross-repo without a shared filesystem.
- **Copy + periodic `/brand-voice diff`** — a copy in each repo; periodic `diff <canonical> <local>` catches drift. Simplest tooling, highest drift risk. Pair with a CI check.

Notion-as-source-of-truth is its own pattern: keep the spec in Notion, refresh local `BRAND-VOICE.md` periodically via `/brand-voice update -n <page-id>`. Notion stays the editorial surface; the local file is the executable artifact.

### Multi-target: one file or many?

The default and recommended pattern is **one `BRAND-VOICE.md` per brand**. Within that file, `contexts:` handles register variation across document types (RFC vs landing page vs press release), audience segments (B2B vs consumer, technical vs lay), or channels (long-form vs social vs email):

```yaml
contexts:
  rfc:      { density: max, numbered_sections: true }
  landing:  { sentence_count: 1 }
  social:   { shorter_form: true, formality_preserved: true }
```

Different contexts share the same lexicon, the same forbidden patterns, the same pronouns — what changes is the register, the sentence rhythm, the example openers.

**Multiple voice files are warranted only when** the brand has genuinely separate sub-brands with separate voices: a luxury group that owns Maison X Couture (institutional, French-rooted) and Maison X Beauty (more accessible, broader audience). Each sub-brand gets its own `BRAND-VOICE.md`. The skills consume each independently — `humanize-en -f maison-x-couture.md` for one, `humanize-en -f maison-x-beauty.md` for the other.

**Inheritance via `voice.extends`** — when sub-voices share a common substrate (founder voice on top of corporate, persona on top of institutional, multi-host media brand), declare `voice.extends: ./BRAND-VOICE.md` on the child file. The child inherits the parent's rules and overrides only what differs. Per-field merge policy, `_replace` / `_remove` overrides, cycle detection, and validation order live in [`references/canonical-format.md`](./references/canonical-format.md) § Inheritance; a worked example sits in [`references/example-multi-voice.md`](./references/example-multi-voice.md).

When in doubt, start with one file. Adding `contexts.foo` later is cheaper than splitting two files later. Adding `voice.extends` later, when a real second voice emerges, is cheaper than over-engineering inheritance up front.

## Source resolution

Sources are combinable — pass any number of `-u`, `-n`, `-d`, `-f`. The skill aggregates all sources into a working draft, then synthesises the canonical format once.

| Flag | Source | Mechanism |
|------|--------|-----------|
| `-u <url>` | URL | `WebFetch` (or your harness's web-fetch tool) direct → fallback `/markitdown -s <url>` if binary/error |
| `-n <id\|url>` | Notion page | Notion MCP fetch tool (page + linked sub-pages, depth 1) — no MCP: export to Markdown and use `-d` |
| `-d <dir>` | Folder of MD/MDX | `Glob <dir>/**/*.md` → aggregate |
| `-f <file>` | Single MD/MDX/TXT | `Read` direct |
| (none, with `extract`) | Interview | Use the question bank for consequential gaps not already answered by the brief |

Full resolution rules — including failure handling, conflicts, MCP unavailability, large-folder fan-out, and contribution summary — live in [`references/source-resolution.md`](./references/source-resolution.md).

The Notion MCP is authorised through Claude Code's permission layer, not via this skill's `allowed-tools`. If the MCP is not installed, `-n` errors with a clear install pointer and the workaround (export Notion → MD, then `-d`).

## Canonical format

`BRAND-VOICE.md` has two parts:

1. **YAML frontmatter** — machine-readable normative rules. Required fields: `voice.name`, `forbidden_lexicon`, `rewrite_rules`, `sentence_norms`. Optional: `core_attributes`, `required_lexicon`, `forbidden_patterns`, `contexts`, `pronouns`, `voice.source_urls`, `voice.last_updated`, `voice.source`.
2. **Eleven prose sections** in this exact order:
   1. Core voice attributes
   2. Rewrite rules — do/don't
   3. Forbidden lexicon and patterns
   4. Sentence-level norms
   5. Tone by context
   6. Pronouns and self-reference
   7. Format conventions
   8. Visual pairing
   9. Quick diagnostic
   10. Counter-examples
   11. Reference texts

Full schema, field constraints, manual-section markers, and section-heading normalisation rules: [`references/canonical-format.md`](./references/canonical-format.md). A complete reference example: [`references/example-chanel.md`](./references/example-chanel.md).

The split is deliberate. Tooling reads YAML; humans read prose. Consumers like `humanize-en -f BRAND-VOICE.md` load the complete effective mapping via `extract_rules.py --resolved-json`, while `--full` is the readable inspection format. The source doc can carry richer explanations without requiring every consumer to load all prose.

## Pipeline integration

Brand voice is consumed by writing skills via `-f`. The current consumer is `humanize-en`:

```bash
/brand-voice extract -u https://example.com/about
  → ./BRAND-VOICE.md

/humanize-en -f ./BRAND-VOICE.md draft.md
  → draft humanized against universal AI tells + brand-specific rules
```

`$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing this SKILL.md elsewhere.

Two ways for a consumer to read the rules:

- **Invoke `extract_rules.py --resolved-json`** when semantic and mechanical consumers must share rules, including `humanize-en -f`. It resolves `voice.extends`, `_replace` and `_remove` once; read and validate against that same mapping. `--full` remains the human-readable format for inspection.

  ```bash
  python3 "$SKILL_DIR"/scripts/extract_rules.py --resolved-json ./BRAND-VOICE.md
  ```

- **Read local YAML directly** when no resolver is available and no inheritance is declared. This path does not resolve `voice.extends`; inherited input requires resolved output before a consumer can claim full rule coverage. A local semantic read is not a mechanical validation result.

Both shapes are documented in [`references/schemas.md`](./references/schemas.md) § extract_rules.py. The `--legacy` flag emits the v1 minimal output (byte-identical to the pre-inheritance shape) for any external consumer pinned to it.

When a brand voice rule conflicts with a universal AI-tell pattern (e.g., the voice *requires* em-dashes vs pattern #14), the brand rule wins — it is the user's contract. Conflicts are logged in the consumer's report.

## Validation — `voice_lint.py`

Every doc the skill writes (or the user authors) is validated by [`scripts/voice_lint.py`](./scripts/voice_lint.py):

```bash
python3 "$SKILL_DIR"/scripts/voice_lint.py ./BRAND-VOICE.md
```

Verdicts: `GREEN` (zero errors, zero warnings), `YELLOW` (warnings only — acceptable but flagged), `RED` (errors — block). Output is JSON per [`references/schemas.md`](./references/schemas.md) § voice_lint.py.

`extract` and `update` lint before writing. RED → fix and re-lint. YELLOW → proceed with the authorized write and report warnings; acceptable warnings do not reopen consent. Audit/diff/validate remain read-only.

## Default workflow (no subcommand)

When the first token of `$ARGUMENTS` does not match `extract|update|diff|validate|lint|check|show`, the skill behaves as follows:

1. **No `BRAND-VOICE.md` at the target** → suggest `/brand-voice extract` with the sources the user mentions inline. Do not silently extract.
2. **`BRAND-VOICE.md` exists** → run `show --rules` and print the testable rules. Useful when the user types `/brand-voice` to glance at the current contract.
3. **The argument looks like a URL** → suggest `/brand-voice extract -u <url>` (or `/brand-voice update -u <url>` if a doc exists).
4. **The argument looks like a file path** → suggest the corresponding `-f` invocation.

The default workflow exists to avoid silent state-modifying actions. Every write goes through an explicit subcommand.

## Rules

- **Canonical file is git-versioned.** Treat `./BRAND-VOICE.md` as a code asset. Diff before merge. The git history is the audit trail.
- **Lint before write.** Every `extract` and `update` validates candidate content with `voice_lint.py --target-path <destination>` before the authorized write. RED never reaches the canonical target; audit/propose remains read-only.
- **Respect the requested mode.** `extract` refuses an existing target and routes a requested refresh to `update`. An authorized `update` applies a validated diff while preserving manual sections; audit/propose and `diff` remain read-only. A source path alone grants no write authority.
- **Manual sections are sacred.** A section marked `<!-- manual: true -->` is preserved verbatim by `update`. Do not re-synthesise.
- **Resolve by source authority.** Apply the user's explicit correction or designated authoritative source and report the resolution. Ask only for materially different identities or rules whose authority remains unresolved; a routine requested value refresh needs no second confirmation.
- **Output paths follow the repo contract.** Default canonical at `./BRAND-VOICE.md`. Pipeline copies under `~/.agents/output/{project}/brand-voice/brand-voice-{slug}.md` only when `-s` is passed.

## When to defer to another skill

- **Apply the voice on a prose draft** → `/humanize-en -f BRAND-VOICE.md <draft>`. This skill never humanises.
- **Convert a non-Markdown source to MD first** → `/markitdown -s <source>`, then `/brand-voice extract -f <markitdown-output>`.
- **Extract design tokens, not voice** → `/award-design` and `/design-system`. Brand voice is prose; brand visuals are tokens. Different docs, different lifecycles.

## Reference

- [`steps/extract.md`](./steps/extract.md), [`steps/update.md`](./steps/update.md), [`steps/diff.md`](./steps/diff.md), [`steps/validate.md`](./steps/validate.md), [`steps/show.md`](./steps/show.md) — per-subcommand workflows, flags, edge cases.
- [`references/canonical-format.md`](./references/canonical-format.md) — full schema, required vs recommended sections, section ordering, manual-section markers, inheritance via `voice.extends`. The contract.
- [`references/example-chanel.md`](./references/example-chanel.md) — complete reference voice doc, anchored on chanel.com primary sources (Métiers d'art savoir-faire page, House of Chanel history, founder page) plus Met Museum and Wikipedia as cross-references. Use as a structural template.
- [`references/example-multi-voice.md`](./references/example-multi-voice.md) — worked example of `voice.extends`: a fictional founder-led startup with parent + child + merged result side-by-side, plus when to use `_replace` vs `_remove` vs default merge.
- [`references/source-resolution.md`](./references/source-resolution.md) — how each `-u/-n/-d/-f` flag resolves, failure modes, conflict handling.
- [`references/interview-questions.md`](./references/interview-questions.md) — eight canonical questions for `extract` with no source flag.
- [`references/schemas.md`](./references/schemas.md) — JSON shape for `voice_lint.py`, plain-text shape for `extract_rules.py`. Stable contract for downstream consumers.
- [`scripts/voice_lint.py`](./scripts/voice_lint.py) — validates a `BRAND-VOICE.md`, walks `voice.extends` chain, emits `chain` and `merged_stats` when inheritance applies. Python 3.7+, no third-party deps.
- [`scripts/extract_rules.py`](./scripts/extract_rules.py) — resolves inheritance; `--full` prints readable rules, `--legacy` the v1 format, and `--resolved-json` the shared model/mechanical mapping consumed by humanize-en.
- [`scripts/measure_corpus.py`](./scripts/measure_corpus.py) — measures stylometric stats from a prose corpus; `--as-sentence-norms` emits a `sentence_norms` dict (or `null` below the 30-sentence threshold) for `extract` to use in place of estimated bounds. stdlib only.
- [`scripts/lint_all.py`](./scripts/lint_all.py) — globs every `BRAND-VOICE*.md` under a root and lints each. Single-command audit for the parent-change blast-radius problem: a parent edit that breaks N children surfaces as N RED verdicts. CI-friendly; recommended in pre-merge hooks.
- [`scripts/utils.py`](./scripts/utils.py) — shared I/O helpers, chain resolution (`resolve_extends_chain`), merge engine (`merge_voice_dicts`, `apply_replace_overrides`, `apply_remove_overrides`). Not invoked directly.

## Gotchas

1. **Child `_replace` directives win over parent rules even when `--chain` shows the parent.** `scripts/utils.py:resolve_extends_chain` walks parent → child; merge applies overrides last. Verify final state with `voice_lint.py` (chain state is in its JSON output; `--chain` is a `show` flag) before merging.
2. **A structurally invalid parent passes chain resolution but fails lint when linted directly.** Fix: lint every file in the chain via `scripts/lint_all.py`, not just the target; block writes if any ancestor is RED.
3. **`_replace` / `_remove` only apply to fields in `REPLACE_ALLOWED_FIELDS` / `REMOVE_ALLOWED_FIELDS`** (`scripts/utils.py:334-352`). Overrides on other fields (e.g., `voice`, `source_urls`, `signature_traits`) no-op at merge and surface only at lint time. Always run `voice_lint.py` on the child after override edits.
4. **Chains over 5 hops fail with `extends-depth-exceeded`** (`scripts/utils.py:332`: `MAX_EXTENDS_DEPTH = 5`). Fix: keep chains short (≤3 hops); flatten when a child needs more than 2 ancestors.
5. **Resolver discovery:** consumers should find the installed skill through the host before trying known paths. humanize-en accepts local rules standalone but rejects unresolved inheritance; use `--resolved-json` and the exact extraction/rerun guidance instead of copying the resolver or dropping parent rules.
