---
name: brand-voice
description: Govern the BRAND-VOICE.md — extract a brand's writing voice from external sources (URL, Notion page, MD file or directory, optional interview when no source is provided) into a structured, executable doc; update it incrementally; diff two versions; validate against the canonical format; show its testable rules. The doc is the single source of truth consumed by writing skills (e.g. `humanize-en -f BRAND-VOICE.md`) to enforce voice on prose. Mirrors the design-system pattern — canonical file at the project root, five CLI-style subcommands.
when_to_use: When the user wants to define, ingest, refresh, validate, or inspect a brand's writing voice. Triggers on "create a brand voice doc", "extract voice from this site", "extract voice from a Notion page", "update the brand voice", "validate / lint / check the brand voice doc", "what's our voice", "voice guidelines", "tone of voice", "writing style guide", "BRAND-VOICE.md". Routes via `$ARGUMENTS` first token — `extract` (ingest sources → BRAND-VOICE.md), `update` (incremental refresh from new sources), `diff` (regression check between versions), `validate` / `lint` / `check` (lint against canonical format), `show` (print testable do/don't rules). Skip when the user wants to *humanize* a text against an existing voice — invoke `/humanize-en -f BRAND-VOICE.md` instead.
argument-hint: "[extract|update|diff|validate|show] [-s] [-o <path>] [-u <url>] [-n <id|url>] [-d <dir>] [-f <file>] [refs|paths]"
model: opus
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
allowed-tools: Read Write Edit Grep Glob WebFetch AskUserQuestion Bash(jq *) Bash(test *) Bash(wc *) Bash(find *) Bash(python3 *) Bash(git *) Bash(mktemp *)
metadata:
  author: coroboros
  sources:
    - github.com/google-labs-code/design.md
    - en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
---

# Brand Voice

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

There is no `apply` subcommand. Application of the voice — rewriting prose to match it — is the consumer skill's job. Today that consumer is `humanize-en -f BRAND-VOICE.md`. Tomorrow it can be any skill that reads the YAML frontmatter via `scripts/extract_rules.py`.

## Canonical file location

The voice doc lives at `./BRAND-VOICE.md` by default — at the project root, versioned in git, alongside `DESIGN.md`, `README.md`, `LICENSE.md`. Override the path with `-o <path>` when the voice is multi-project.

`extract` refuses to overwrite an existing file. To refresh, use `update`. To replace, delete first.

When `-s` is passed alongside `extract`, the skill also writes a copy to `.claude/output/brand-voice/{slug}/voice.md` for pipeline-history consumers. The slug is derived from `voice.name` (kebab-case, max 5 words). The canonical file at `./BRAND-VOICE.md` remains the single source of truth.

### Cross-repo distribution

When a brand spans multiple repositories (a www repo, an iOS repo, a docs repo, a marketing site), the same `BRAND-VOICE.md` should govern all of them. Pick one pattern and document it in each project's `CLAUDE.md`:

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

When in doubt, start with one file. Adding `contexts.foo` later is cheaper than splitting two files later.

## Source resolution

Sources are combinable — pass any number of `-u`, `-n`, `-d`, `-f`. The skill aggregates all sources into a working draft, then synthesises the canonical format once.

| Flag | Source | Mechanism |
|------|--------|-----------|
| `-u <url>` | URL | `WebFetch` direct → fallback `/markitdown -s <url>` if binary/error |
| `-n <id\|url>` | Notion page | `mcp__claude_ai_Notion__notion-fetch` (page + linked sub-pages, depth 1) |
| `-d <dir>` | Folder of MD/MDX | `Glob <dir>/**/*.md` → aggregate |
| `-f <file>` | Single MD/MDX/TXT | `Read` direct |
| (none, with `extract`) | Interview | 8 canonical questions via `AskUserQuestion` |

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

The split is deliberate. Tooling reads YAML; humans read prose. `humanize-en -f BRAND-VOICE.md` only loads the frontmatter (~50 lines via `extract_rules.py`), not the full doc, so the voice doc can be richly explained without bloating downstream contexts.

## Pipeline integration

Brand voice is consumed by writing skills via `-f`. The current consumer is `humanize-en`:

```bash
/brand-voice extract -u https://example.com/about
  → ./BRAND-VOICE.md

/humanize-en -f ./BRAND-VOICE.md draft.md
  → draft humanized against universal AI tells + brand-specific rules
```

Two ways for a consumer to read the rules:

- **`Read` the YAML frontmatter directly** — preferred when the consumer's `allowed-tools` does not include `Bash`. The consumer parses the YAML and uses `forbidden_lexicon`, `rewrite_rules`, `sentence_norms`, `forbidden_patterns`, `pronouns` directly. This is what `humanize-en -f` does.
- **Invoke `extract_rules.py`** — when the consumer has Bash and wants the canonical flat-text view:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/extract_rules.py ./BRAND-VOICE.md
```

Output is line-oriented plain text (30–80 lines for a typical voice doc). Schema in [`references/schemas.md`](./references/schemas.md) § extract_rules.py. Used by the `show` subcommand of this skill.

When a brand voice rule conflicts with a universal AI-tell pattern (e.g., the voice *requires* em-dashes vs pattern #14), the brand rule wins — it is the user's contract. Conflicts are logged in the consumer's report.

## Validation — `voice_lint.py`

Every doc the skill writes (or the user authors) is validated by [`scripts/voice_lint.py`](./scripts/voice_lint.py):

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/voice_lint.py ./BRAND-VOICE.md
```

Verdicts: `GREEN` (zero errors, zero warnings), `YELLOW` (warnings only — acceptable but flagged), `RED` (errors — block). Output is JSON per [`references/schemas.md`](./references/schemas.md) § voice_lint.py.

`extract` and `update` lint before writing. RED → fix and re-lint without prompting the user. YELLOW → present warnings to the user and proceed on confirmation.

## Default workflow (no subcommand)

When the first token of `$ARGUMENTS` does not match `extract|update|diff|validate|lint|check|show`, the skill behaves as follows:

1. **No `BRAND-VOICE.md` at the target** → suggest `/brand-voice extract` with the sources the user mentions inline. Do not silently extract.
2. **`BRAND-VOICE.md` exists** → run `show --rules` and print the testable rules. Useful when the user types `/brand-voice` to glance at the current contract.
3. **The argument looks like a URL** → suggest `/brand-voice extract -u <url>` (or `/brand-voice update -u <url>` if a doc exists).
4. **The argument looks like a file path** → suggest the corresponding `-f` invocation.

The default workflow exists to avoid silent state-modifying actions. Every write goes through an explicit subcommand.

## Rules

- **Canonical file is git-versioned.** Treat `./BRAND-VOICE.md` as a code asset. Diff before merge. The git history is the audit trail.
- **Lint before write.** Every `extract` and `update` runs `voice_lint.py` on the synthesised content before the user is asked to approve. RED never reaches disk.
- **Never overwrite.** `extract` refuses to overwrite an existing file. `update` always shows a diff and asks for explicit `yes`. `diff` is read-only by definition.
- **Manual sections are sacred.** A section marked `<!-- manual: true -->` is preserved verbatim by `update`. Do not re-synthesise.
- **Conflicts surface, never override.** When two sources disagree, surface via `AskUserQuestion`. When a source contradicts the existing doc during `update`, surface. No silent picks.
- **Output paths follow the repo contract.** Default canonical at `./BRAND-VOICE.md`. Pipeline copies under `.claude/output/brand-voice/{slug}/voice.md` only when `-s` is passed.

## When to defer to another skill

- **Apply the voice on a prose draft** → `/humanize-en -f BRAND-VOICE.md <draft>`. This skill never humanises.
- **Convert a non-Markdown source to MD first** → `/markitdown -s <source>`, then `/brand-voice extract -f <markitdown-output>`.
- **Extract design tokens, not voice** → `/award-design` and `/design-system`. Brand voice is prose; brand visuals are tokens. Different docs, different lifecycles.
- **Pure grammar fix on the voice doc** → `/fix-grammar BRAND-VOICE.md`. This skill governs structure and content, not typos.

## Reference

- [`steps/extract.md`](./steps/extract.md), [`steps/update.md`](./steps/update.md), [`steps/diff.md`](./steps/diff.md), [`steps/validate.md`](./steps/validate.md), [`steps/show.md`](./steps/show.md) — per-subcommand workflows, flags, edge cases.
- [`references/canonical-format.md`](./references/canonical-format.md) — full schema, required vs recommended sections, section ordering, manual-section markers. The contract.
- [`references/example-chanel.md`](./references/example-chanel.md) — complete reference voice doc, anchored on chanel.com primary sources (Métiers d'art savoir-faire page, House of Chanel history, founder page) plus Met Museum and Wikipedia as cross-references. Use as a structural template.
- [`references/source-resolution.md`](./references/source-resolution.md) — how each `-u/-n/-d/-f` flag resolves, failure modes, conflict handling.
- [`references/interview-questions.md`](./references/interview-questions.md) — eight canonical questions for `extract` with no source flag.
- [`references/schemas.md`](./references/schemas.md) — JSON shape for `voice_lint.py`, plain-text shape for `extract_rules.py`. Stable contract for downstream consumers.
- [`scripts/voice_lint.py`](./scripts/voice_lint.py) — validates a `BRAND-VOICE.md`. Python 3.7+, no third-party deps.
- [`scripts/extract_rules.py`](./scripts/extract_rules.py) — emits flat testable rules. Consumed by `humanize-en -f`.
- [`scripts/utils.py`](./scripts/utils.py) — shared I/O helpers (mirrors `humanize-en/scripts/utils.py`). Not invoked directly.
