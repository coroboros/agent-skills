<div align="center">

<img src="assets/logo.png" width="288" height="288" alt="Coroboros"/>

<!-- omit in toc -->
# Agent Skills

**AI agent skills for Claude Code and compatible agents**

Seven plugins — workflow, coding, design, Claude Code meta, media, productivity, writing. Tested across every skill, scanned by Cisco's `skill-scanner`.

[![latest](https://img.shields.io/github/v/release/coroboros/agent-skills?style=flat-square&label=latest&color=000000)](https://github.com/coroboros/agent-skills/releases)
[![ci](https://img.shields.io/github/actions/workflow/status/coroboros/agent-skills/ci.yml?branch=main&style=flat-square&label=ci&color=000000)](https://github.com/coroboros/agent-skills/actions/workflows/ci.yml)
[![scan](https://img.shields.io/github/actions/workflow/status/coroboros/agent-skills/scan-skills.yml?branch=main&style=flat-square&label=scan&color=000000)](https://github.com/coroboros/agent-skills/actions/workflows/scan-skills.yml)
[![branch](https://img.shields.io/badge/branch-stable-000000?style=flat-square)](https://github.com/coroboros/agent-skills)
[![license](https://img.shields.io/badge/license-MIT-000000?style=flat-square)](https://opensource.org/licenses/MIT)
[![stars](https://img.shields.io/github/stars/coroboros/agent-skills?style=flat-square&label=stars&color=000000)](https://github.com/coroboros/agent-skills)
[![coroboros.com](https://img.shields.io/badge/coroboros.com-000000?style=flat-square&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTAiLz48cGF0aCBkPSJNMiAxMmgyME0xMiAyYTE1LjMgMTUuMyAwIDAgMSA0IDEwIDE1LjMgMTUuMyAwIDAgMS00IDEwIDE1LjMgMTUuMyAwIDAgMS00LTEwIDE1LjMgMTUuMyAwIDAgMSA0LTEweiIvPjwvc3ZnPg==)](https://coroboros.com)

</div>

- [Install](#install)
- [Requirements](#requirements)
- [Skills](#skills)
  - [Workflow Skills](#workflow-skills)
  - [Coding Skills](#coding-skills)
  - [Design Skills](#design-skills)
  - [Claude Code Skills](#claude-code-skills)
  - [Media Skills](#media-skills)
  - [Productivity Skills](#productivity-skills)
  - [Writing Skills](#writing-skills)
- [Pipeline](#pipeline)
- [Testing](#testing)
- [Security](#security)
- [Standards](#standards)
- [License](#license)

---

## Install

Install via [skills.sh](https://skills.sh):

```bash
# All skills
npx skills add coroboros/agent-skills

# Individual skill
npx skills add coroboros/agent-skills --skill <name>
```

---

## Requirements

- `bash`
- `python3` (3.10+, stdlib only — no `pip install` needed)
- A filesystem

Some skills wrap external CLIs — each is declared in its SKILL.md.

---

## Skills

Skills are grouped by plugin. Each plugin collects related skills — expand any section below to see usage, flags, and behavior.

| Plugin | Skill | Model | Description | Scope |
|--------|-------|-------|-------------|-------|
| Workflow | [forge](#forge) | opus | Pre-implementation thinking — research, decide, and emit one apex-ready plan | Claude |
| Workflow | [apex](#apex) | opus | Structured implementation — Analyze, Plan, Execute, eXamine | Claude |
| Workflow | [oneshot](#oneshot) | sonnet | Single-pass Explore-Code-Test workflow | Claude |
| Workflow | [clean-output](#clean-output) | sonnet | Interactive cleanup for `~/.claude/output/` — list per-project and `_global` artifacts grouped by emitting skill, prompt before deletion, never auto-delete | Claude |
| Coding | [scaffold](#scaffold) | haiku | Bootstrap Next.js/Astro projects on Cloudflare Workers | Claude |
| Coding | [code-ultrareview](#code-ultrareview) | opus | Eight-axis judgment review — Correctness · Simplification · Tests · Documentation · Style · Intent · Design/API · Performance (+ Coherence on metadata changes). 5-phase pipeline: scope → npx/uvx tool battery → 8 parallel axis reviewers → Haiku validators on sub-80 → synthesis with A2 no-silent-drop + Conventional Comments JSONL. Closes with "What I did NOT check" — defers security to `/security-review`, runtime perf, flaky detection. Zero auto-install, graceful skip on missing native tools. Opt-in `--verify-build` / `--mutation-test` / `--reconcile` / `--apply-safe`. Distinct from Anthropic's remote `/ultrareview` | Claude |
| Design | [award-design](#award-design) | opus | Build award-winning websites — archetype, atmosphere, DESIGN.md | Claude |
| Design | [design-system](#design-system) | opus | Govern DESIGN.md — token enforcement + 7 CLI subcommands (audit/diff/export/spec/migrate/init/audit-extensions) | Claude |
| Claude Code | [claude-md](#claude-md) | opus | Create and optimize CLAUDE.md and .claude/rules/ | Claude |
| Claude Code | [agent-creator](#agent-creator) | opus | Expert guidance for creating Claude Code subagents | Claude |
| Media | [video-loop](#video-loop) | sonnet | Loop background videos with invisible cut points | Claude |
| Media | [audio-loop](#audio-loop) | sonnet | Produce gapless web-ready ambient audio loops (FLAC + Web Audio) | Claude |
| Media | [suno-produce](#suno-produce) | opus | Turn a music brief into Suno v5.5 prompt artifacts — TRACK.md / optional ALBUM.md / optional ARTIST.md, multi-type validator with copyright contract | Claude |
| Media | [markitdown](#markitdown) | sonnet | Convert PDF/Office/HTML/audio/YouTube to Markdown via Microsoft's CLI | Claude |
| Productivity | [notion](#notion) | opus | Notion access via the official MCP connector (default) or `ntn` CLI (uploads, Workers, headless/CI, raw API, shell piping) | Claude |
| Writing | [brand-voice](#brand-voice) | opus | Govern BRAND-VOICE.md — extract from URL/Notion/MD/interview, update, diff, validate, show; multi-voice via `voice.extends`; consumed by `humanize-en -f` | Claude |
| Writing | [write-clear-readme](#write-clear-readme) | opus | Author / audit / polish READMEs — clarity, structure, wording concision | Claude |
| Writing | [humanize-en](#humanize-en) | sonnet | Strip AI tells from English prose — em-dashes, rule of three, AI vocabulary, hedging; brand-aware via `-f BRAND-VOICE.md` (deterministic prescan + post-rewrite validation gate + auto-iteration) | Claude |

**About the Model column.** Each skill declares its own `model:` in frontmatter — `opus` for deep-judgment work (strategy, design, complex implementation), `sonnet` for bounded reasoning, `haiku` for deterministic scripted flows. The tier is forced per skill, regardless of session default — predictable results across runs. Opus-tier skills consume more tokens; override with the Claude Code `--model` flag, or skip those skills on a tight plan.

**About the Scope column.** Skills labeled `Claude` are optimized for Claude Code CLI per the [Agent Skills spec](https://agentskills.io) — they use Claude Code-specific frontmatter extensions (`$ARGUMENTS`, `argument-hint`, `when_to_use`, `paths`, `hooks`, inline shell) and degrade gracefully in Claude.ai, Claude desktop, and other agents supporting the open standard. `All agents` means the skill uses only open-standard fields (`name`, `description`, `license`, `compatibility`, `metadata`) and is fully portable. Each SKILL.md declares its intended environment via the spec-canonical top-level `compatibility:` field.

---

### Workflow Skills

Strategic thinking, planning, implementation, and cleanup — `forge`, `apex`, `oneshot`, `clean-output`.

<details>
<summary><em>forge · apex · oneshot · clean-output</em></summary>

<br>

#### forge

Pre-implementation thinking — research the problem space, weigh approaches with devil's-advocate rigor, decide every engineering call within scope, and emit one apex-ready plan. The "think" half; `apex` is the "build" half.

**Usage**

```bash
# Pure-strategy decision (no code)
/forge should we use Neon or Supabase for our serverless Postgres?

# Plan a feature, save the artifact
/forge -s add user authentication with OAuth and email/password

# Auto mode + create GitHub issues
/forge -s -a -i migrate from REST to GraphQL
```

**Flags**

| Flag | Description |
|------|-------------|
| `-s` / `-S` | Save artifact to `~/.claude/output/{project}/forge/forge-{slug}.md` / force no-save |
| `-i` / `-I` | Create GitHub issues from workstreams (requires `-s`) / disable |
| `-a` / `-A` | Auto mode — skip Q&A, decide reasonable forks / disable |
| `-e` / `-E` | Economy mode — no subagents / disable |
| `-f` | Load prior context (forge plan, RFC, GitHub issue `#N` or URL) |

Uppercase forms disable the ambient default when the skill runs with a pre-set mode. Requires `gh` authenticated when using `-i` or passing a GitHub URL/`#N` to `-f`.

**What it does**

1. **Hunt** — frames and reframes the real problem, then researches wide via parallel subagents; cross-references sources rather than picking one
2. **Judge** — diverges ≥3 structurally distinct approaches, then stress-tests with premortem + steelman of the runner-up
3. **Decide** — resolves every engineering judgment call (architecture, library, decomposition, trade-offs); escalates only the few irreversible/costly or genuinely user-owned forks
4. **Forge** — emits one artifact: the decision + assumption ledger, and when there's code to build, 3-7 workstreams (priority, complexity, dependencies, Given/When/Then AC), validated by `scripts/validate_spec.py`

Code-bearing artifacts (H1 `# Spec:` + `## Workstreams`) bridge to `/apex -f <abs forge path> implement WS-1`; with `-i`, workstreams also become GitHub issues. Pure-strategy artifacts (H1 `# Decision:`) conclude the discussion — no apex handoff.

**Sources**

- [anthropics/knowledge-work-plugins — product-brainstorming](https://github.com/anthropics/knowledge-work-plugins/tree/main/product-management/skills/product-brainstorming) — divergent/convergent ideation modes and frameworks
- [anthropics/knowledge-work-plugins — write-spec](https://github.com/anthropics/knowledge-work-plugins/tree/main/product-management/skills/write-spec) — PRD structure, acceptance-criteria craft, ruthless prioritization
- [Melvynx/aiblueprint — ultrathink](https://github.com/Melvynx/aiblueprint) — craftsman simplification discipline

---

#### apex

Systematic implementation using the APEX methodology — Analyze, Plan, Execute, eXamine — with parallel subagents and self-validation.

**Usage**

```bash
# Autonomous + save outputs
/apex -a -s implement user registration

# From a GitHub issue
/apex -f "#42" implement what issue 42 describes

# From a prior forge plan
/apex -f ~/.claude/output/{project}/forge/forge-{slug}.md implement WS-1

# Resume a previous task
/apex -r 01-auth-middleware
```

**Flags**

| Flag | Description |
|------|-------------|
| `-a` / `-A` | Autonomous mode — skip confirmations / disable |
| `-s` / `-S` | Save outputs to `~/.claude/output/{project}/apex/{task-id}/` / force no-save |
| `-e` / `-E` | Economy mode — no subagents / disable |
| `-b` / `-B` | Branch mode — verify not on main, create branch if needed / disable |
| `-g` / `-G` | Wire `/goal` to loop step-04 until AC verified (auto-on under `claude -p`; requires Claude Code v2.1.139+) / disable |
| `-f` | Load prior context (GitHub issue `#N`, forge plan, RFC) |
| `-r` | Resume a previous task by ID |
| `-i` | Interactive flag configuration |

Uppercase forms disable the ambient default when the skill runs with a pre-set mode.

**What it does**

- **Analyze** — launches 1–10 parallel subagents based on task complexity. Infers acceptance criteria in Given/When/Then form with explicit `## Not Included` negative scope. When `-f` points to a spec (H1 `# Spec:` + `## Workstreams`), accepts the spec's AC verbatim (closure rule) instead of re-inferring.
- **Plan** — file-by-file implementation strategy with AC mapping. Inline Challenge mini-phase (premortem + alternative consideration) stress-tests the plan. Surgical-scope advisory fires when the plan touches >5 files, >2 systems, or introduces cross-cutting concerns — advisory only, never blocks.
- **Execute** — todo-driven implementation with progressive step loading.
- **eXamine** — derivation lens (code↔plan reconciliation, classifying each divergence as GAP / SCOPE-ADD / DECISION-OVERRIDE / CONSISTENT) runs before typecheck/lint/tests. GAP blocks completion; SCOPE-ADD advisory unless declared in negative scope; DECISION-OVERRIDE surfaces for user judgment. Optional `/goal` integration via `-g` loops the session until AC verified — transcript-only Haiku evaluator, requires Claude Code v2.1.139+; auto-on under `claude -p`.
- **Resume** — `-r` auto-validates state via `validate_state.sh` before restoration; partial or corrupt task dirs fail loud rather than cascade.

Accepts output from `forge` via `-f`. Works standalone.

**Trust model**

Analyze fetches third-party content into the workflow — web research via `general-purpose` subagents, library docs via Context7, GitHub issue bodies via `-f #N`, any file passed to `-f`. An adversarial document hosted at a fetched URL, or pasted into an issue body, can attempt indirect prompt injection. User review of the analysis report before approving the plan is the trust boundary — confirm the surfaced files, patterns, and acceptance criteria match intent. Pass `-e` (economy mode) to disable subagents and remove the third-party surface entirely. Full disclosure in `skills/apex/SKILL.md` § *Trust model*.

**Sources**

- [Melvynx/aiblueprint — apex](https://github.com/Melvynx/aiblueprint) — APEX methodology (Analyze, Plan, Execute, eXamine) reference implementation

---

#### oneshot

Single-pass feature implementation — Explore, Code, Test. Ship now, iterate later.

**Usage**

```bash
/oneshot add dark mode toggle to the navbar
/oneshot #42
```

**What it does**

1. **Resolve** — if input is a GitHub issue (`#N` or URL), fetches via `gh` and uses the title/body
2. **Explore** — finds 2–3 key files, searches for patterns (no tours)
3. **Complexity check** — if >5 files or multiple systems, suggests `/apex` or `/forge` instead
4. **Code** — follows existing codebase patterns exactly
5. **Test** — runs lint and typecheck, fixes only what it broke

One task only. No tangential improvements, no refactoring outside scope. Stops after 2 failed attempts.

**Sources**

- [Melvynx/aiblueprint — oneshot](https://github.com/Melvynx/aiblueprint) — Explore/Code/Test loop with complexity escalation to `apex` or `forge`

---

#### clean-output

Interactive cleanup for `~/.claude/output/` — the global scratch directory where emitting skills (forge, apex, code-ultrareview, markitdown, audio-loop, brand-voice) accumulate artifacts. Lists every artifact under the current project bucket plus the cross-project `_global` bucket, grouped by emitting skill, with size and mtime per row. Asks before deleting anything; never auto-prunes; no TTL.

**Usage**

```bash
/clean-output                          # interactive — current project + _global
/clean-output -l                       # list only — never deletes
/clean-output -A                       # every project bucket + _global
/clean-output -p my-app                # one specific project + _global
/clean-output -d                       # delete-all flow — single count+size confirmation
```

**Flags**

| Flag | Description |
|------|-------------|
| `-A` / `--all-projects` | List every `~/.claude/output/<project>/` bucket plus `_global`. Mutually exclusive with `-p` |
| `-p <name>` / `--project` | Restrict to one named project (always includes `_global`) |
| `-l` / `--list` | Read-only listing — never invokes `delete_artifact.py`; exits 0 after reporting |
| `-d` / `--delete-all` | Skip the action menu; prompt once with total count + size; on confirmation, delete everything in scope |
| `-D` / `--no-delete-all` | Explicit override — disable an ambient `delete-all` mode |

`-A` uses capital A because lowercase `-a` is reserved for `auto` across the skill family (forge, apex, oneshot). All flags default OFF.

**What it does**

1. **Resolve scope** — current `{project}` + `_global` (default), every project (`-A`), or one named project (`-p NAME`)
2. **List** via `scripts/list_artifacts.py` — JSON array of `{bucket, project, skill, path, size_bytes, mtime_iso}`; apex task directories report cumulative size and most-recent mtime
3. **Action menu** via `AskUserQuestion` (skipped under `-l` or `-d`) — Keep everything · Delete everything · Pick per bucket · Pick at a finer grain
4. **Delete** via `scripts/delete_artifact.py` per selected path — guard via `Path(p).resolve().is_relative_to(<root>)`; anything outside `~/.claude/output/` exits 2 and the file is unchanged
5. **Report** — total artifacts deleted, total bytes freed, any failures

The path-resolution guard is the script's single chokepoint — `delete_artifact.py` never invokes shell `rm` and refuses every path that escapes the sandbox, including via `..` traversal or symlinks pointing outside the root.

</details>

---

### Coding Skills

Bootstrap projects and review changes before commit — `scaffold`, `code-ultrareview`.

<details>
<summary><em>scaffold · code-ultrareview</em></summary>

<br>

#### scaffold

Scaffold new web projects with an opinionated stack on Cloudflare Workers.

**Strict opinion** — no Vercel/Netlify, no ESLint/Prettier. Use a different scaffold for any other stack.

**Requirements**

- `pnpm` — enable via Corepack: `corepack enable && corepack prepare pnpm@latest --activate`
- Node.js ≥ 22

**Usage**

```bash
/scaffold next-cloudflare my-saas
/scaffold astro-cloudflare landing-page
/scaffold next-cf                        # alias
```

**Scaffolds**

| Scaffold | Framework | Infra | Key stack |
|----------|-----------|-------|-----------|
| `next-cloudflare` | Next.js 16 (App Router) | Cloudflare Workers (OpenNext) | Drizzle + Neon, Better-Auth, shadcn/ui, Vitest, Playwright |
| `astro-cloudflare` | Astro 6 (SSG-first) | Cloudflare Workers | Zero JS default, Content Collections, SEO rules |

Shared: TypeScript strict, pnpm, Biome, Tailwind CSS, Node.js 22.

**What it does**

1. Runs the official framework CLI (`create-next-app` / `create astro`)
2. Overlays opinionated config — Biome, Cloudflare Workers, CLAUDE.md, `.worktreeinclude` (copies dev-critical gitignored files into Claude Code worktrees)
3. Adds pnpm scripts (dev, build, deploy, check, typecheck, db, test)
4. Installs the full dependency stack
5. Suggests `/award-design` for visual design tokens

Optionally chains to `award-design` and `design-system`.

---

#### code-ultrareview

Eight-axis judgment code review at full strength, in-session. Pinned to `model: opus` and `effort: max` — every invocation gets the deepest reasoning budget regardless of session defaults. The 8 always-on axes — Correctness, Simplification, Tests, Documentation, Style, Intent, Design/API, Performance — run as 8 parallel `Explore` subagents fed by a deterministic tool battery. Coherence joins as a 9th axis when manifest / `SKILL.md` / `tsconfig.json` / `pyproject.toml` / `Cargo.toml` / `go.mod` / root `README.md` appears in the diff. Sub-80 findings re-pass through Haiku validators against the verbatim Anthropic rubric — promoted to ≥80 or demoted with explicit reason; A2 no-silent-drop preserves every finding in `### ⚠️ Unverified` when neither path lands. Tool battery prefers `npx` / `uvx` wrappers (zero-install for the JS + Python majority) with PATH-binary fallback for native tools (`oasdiff`, `atlas`, Go tools, `cargo-machete`, `vale`); missing tools surface install commands in the report. Every report closes with `What I did NOT check` (security → `/security-review`; runtime perf; flaky detection; any skipped tools). Distinct from Anthropic's remote `/ultrareview` — same goal, in-session on the user's subscription.

**Usage**

```bash
/code-ultrareview                              # full 8-axis review, print report
/code-ultrareview -s                           # save the report + JSONL for /apex -f
/code-ultrareview -b origin/main               # review HEAD against an explicit base
/code-ultrareview --verify-build               # promote sub-80 findings via real build verification
/code-ultrareview --mutation-test              # add Stryker / Pitest / mutmut on changed files
/code-ultrareview --reconcile @auto            # add Intent-axis derivation sub-mode
/code-ultrareview --apply-safe                 # full review + gated low-risk fixes
/code-ultrareview --preflight                  # list tools the battery would run, no review
/code-ultrareview --axes correctness,tests     # subset of axes
```

**Flags**

| Flag | Description |
|------|-------------|
| `-s` / `-S` | Save the report + JSONL to `~/.claude/output/{project}/code-ultrareview/code-ultrareview-{slug}.{md,jsonl}` / force no-save |
| `-b <ref>` | Override the review base (skip auto-detection) |
| `--repo-kind <kind>` | Override the scope classifier. `<kind>` ∈ `skills`, `app`, `library`, `docs`, `monorepo`, `python`, `rust`, `go`, `unknown`. Persistent per-repo at `.code-ultrareview.yaml`; the flag wins on conflict. Invalid value exits 2 |
| `--reconcile <input>` | Activate the Intent-axis derivation sub-mode. `<input>` ∈ `@auto`, `@pr`, an explicit path or directory, `gh:pr:<N>`, `gh:issue:<owner>/<repo>#<N>`, or a GitHub issue URL |
| `--verify-build` | Phase 3.5 — run build verification on sub-80 axis findings BEFORE Haiku validators. Confirmed findings promote +30 confidence and skip the validator pass |
| `--mutation-test` | Stryker (JS/TS), Pitest (JVM), or mutmut (Python) on changed files only. Surviving mutants route to the Tests axis as 🟠 Medium |
| `--apply-safe` | Opt-in writers — manifest version sync, structured-field description sync (full-agreement guard), one failing test per confirmed bug. Diff preview + per-file confirmation |
| `--include-prose` | Coherence axis compares README freeform paragraphs (default: structured fields only) |
| `--axes <list>` | Comma-separated axes subset (e.g. `correctness,tests`). Default: all 8 + Coherence when triggered |
| `--preflight` | List detected tools per repo_kind + install commands for missing ones. Informational, no install |

**The five phases**

1. **Scope** — `scripts/scope.py`. Deterministic, no LLM. Resolves diff (clean → `resolve_base.sh` ladder; dirty → `git diff HEAD` + untracked files inlined), classifies repo into one of 9 kinds, reads the CLAUDE.md chain, detects languages, decides whether the conditional Coherence axis activates. Emits `scope.json`.
2. **Tool battery** — `scripts/run_battery.sh`. Per-language dispatch over the 14-tool matrix below. `npx`/`uvx` preferred; PATH binary fallback; missing tools emit `WARN: <tool> not found — install: <cmd>` + land in `scope.json["tools_skipped"]`. The battery NEVER auto-installs. Every finding carries `confidence: 100` and skips the validator phase.
3. **Axis review** — 8 parallel `Explore` subagents (9 with Coherence). Each receives `scope.json`, `tool-findings.jsonl` filtered to its own axis, the diff, and its axis brief (`references/axes/<axis>.md`). Each emits findings with 0–100 confidence per `references/anthropic-verbatim.md`.
4. **Validation** — One Haiku validator per sub-80 finding, batched ≤10 parallel. Re-scores against the rubric + re-checks that the cited CLAUDE.md rule actually exists in `claude_md_chain`. A2 no-silent-drop: promoted (≥80), demoted-with-reason, or `### ⚠️ Unverified` — never omitted. `--verify-build` runs at Phase 3.5 BEFORE this step.
5. **Synthesis** — Dedup by `(file, line_range, finding_hash)`. Inter-axis precedence `correctness > design-api > simplification > tests > documentation > style > intent > performance > coherence`. Verdict ∈ `Ship` / `Fix-then-ship` / `Needs work`. Markdown report to terminal + `~/.claude/output/{project}/code-ultrareview/code-ultrareview-{slug}.md`; JSONL alongside with Conventional Comments labels (`issue` / `suggestion` / `nitpick` / `question`). Mandatory `What I did NOT check` closing section.

**Tool battery — Tool → Axis → Install command**

The skill prefers `npx` / `uvx` (zero-install, cached after first run at `~/.npm/_npx` / `~/.cache/uv`). Native binaries are PATH-only. The skill skips missing tools gracefully — install only if you want the axis coverage they provide.

| Tool | Axis | Wrapper | Install (if no wrapper, or to avoid first-run cold start) |
|------|------|---------|-----------------------------------------------------------|
| `knip` | Simplification (JS/TS dead code) | `npx` | `npm i -D knip` |
| `jscpd` | Simplification (cross-language duplication) | `npx` | `npm i -D jscpd` |
| `markdownlint-cli2` | Documentation (Markdown lint) | `npx` | `npm i -D markdownlint-cli2` |
| `api-extractor` | Design/API (TS public surface) | `npx` | `npm i -D @microsoft/api-extractor` |
| `lizard` | Simplification (cyclomatic complexity) | `uvx` | `pipx install lizard` |
| `vulture` | Simplification (dead Python code) | `uvx` | `pipx install vulture` |
| `semgrep` | Correctness (generic) + Performance (bundled perf-rules) | `uvx` | `pipx install semgrep` |
| `vale` | Documentation (prose lint) | — (Go binary) | `brew install vale` |
| `oasdiff` | Design/API (OpenAPI breaking changes) | — | `brew install oasdiff` |
| `atlas` | Design/API (DB migration lint) | — | `brew install ariga/tap/atlas` |
| `deadcode` | Simplification (Go unreachable) | — | `go install golang.org/x/tools/cmd/deadcode@latest` |
| `gocyclo` | Simplification (Go complexity) | — | `go install github.com/fzipp/gocyclo/cmd/gocyclo@latest` |
| `dupl` | Simplification (Go duplication) | — | `go install github.com/mibk/dupl@latest` |
| `cargo-machete` | Simplification (Rust unused deps) | — | `cargo install cargo-machete` |

Bundled Semgrep rules at `skills/code-ultrareview/references/perf-rules/`: `n-plus-one-sqlalchemy.yml`, `n-plus-one-sequelize.yml`, `sync-io-async-py.yml` — route to the Performance axis when triggered.

Run `/code-ultrareview --preflight` to see exactly what would run on the current repo + install commands for the missing ones.

**Rules**

- **Zero auto-install** — the battery never runs `brew install`, `cargo install`, `go install`, `pip install`, `npm install -g`. Users install natives explicitly.
- **A2 no-silent-drop** — every sub-80 finding either gets promoted (≥80), demoted with explicit reason, or surfaces in `### ⚠️ Unverified`.
- **`What I did NOT check`** — every report closes with this section listing security (defers to `/security-review`), runtime perf (non-goal), flaky detection (non-goal), and any tools from `scope.json["tools_skipped"]`.
- **Cite precisely** — every finding carries `file:line`; CLAUDE.md findings quote the violated rule verbatim; permalinks use `https://github.com/<owner>/<repo>/blob/<full-sha>/<path>#L<n>-L<m>`.

**Sources**

- [anthropics/claude-plugins-official — code-review](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-review) — verbatim 0/25/50/75/100 rubric, HIGH SIGNAL criteria, false-positive taxonomy, agent-assumption rule, parallel-reviewer + Haiku-validator pattern
- [anthropics/claude-plugins-official — code-simplifier](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-simplifier) — Simplification axis precedent (nested ternaries forbidden, "fewer lines over readability" forbidden)
- [Anthropic — Code Review docs](https://code.claude.com/docs/en/code-review) — Managed Code Review severity tiers (Important / Nit / Pre-existing) adopted in synthesis
- [Anthropic — `/ultrareview` docs](https://code.claude.com/docs/en/ultrareview) — remote sandbox + multi-agent fleet + per-finding independent verification (the upstream this skill distinguishes itself from — in-session vs remote, distinct namespace)

</details>

---

### Design Skills

Recommend design archetypes and enforce DESIGN.md tokens across UI — `award-design`, `design-system`.

<details>
<summary><em>award-design · design-system</em></summary>

<br>

#### award-design

Build award-winning websites that target Awwwards SOTD 7.5+, FWA, CSSDA. Recommends a design archetype, calibrates atmosphere, and produces a complete DESIGN.md following the [Google DESIGN.md open standard](https://github.com/google-labs-code/design.md) — YAML frontmatter design tokens plus eight prose sections, validated by the `@google/design.md` CLI.

**Usage**

```bash
/award-design landing page for a sustainable coffee brand
/award-design -u https://linear.app portfolio for a motion designer
```

`-u <url>` reverse-engineers a DESIGN.md from a live site as the archetype seed. The extracted observation informs the recommendation but doesn't constrain it — the brief is still the destination.

**Archetypes**

Each archetype is anchored to an article-credentialed canonical reference. The reference file splits DNA (non-negotiable identity, mood-agnostic) from common expressions (2–4 named stacks per archetype) so the same DNA admits multiple valid styles — Immersive can be cinematic-dark *or* editorial-portrait *or* daylight-automotive without losing identity.

| Archetype | Canonical reference | Ideal for |
|-----------|---------|-----------|
| Minimalist | Terminal Industries (SOTM Sept 2025) | SaaS, luxury, architecture, portfolios |
| Brutalist | FlowFest 2025 (SOTD July 2025) | Creative agencies, indie tech, festivals |
| Editorial | Siena Film Foundation (SOTM April 2025) | Media, fashion, cultural institutions |
| Bold / Maximal | Ponpon Mania (SOTM Oct 2025) | Entertainment, music, Gen Z brands |
| Immersive / Cinematic | Lando Norris (Site of the Year 2025) | Automotive, luxury, gaming, athlete portfolios |
| Experimental | Bruno Simon (SOTM Jan 2026) | Developer portfolios, art institutions |
| Corporate Luxury | Cartier WAW 2025 (SOTM Aug 2025) | Fashion, hotels, jewelry, wealth, watchmaking |
| Bento / Card | Anime.js v4 (SOTM May 2025) | SaaS product pages, AI products, feature comparisons |
| Spatial Organic | *trend-credentialed (Arc, Granola)* | Sustainability, wellness, post-2025 creative studios |

**Key features**

- **DNA + common expressions** — each archetype reference splits non-negotiable identity from 2–4 named expressions (e.g., Immersive: cinematic-dark / editorial-portrait / daylight-automotive). Prevents force-fitting a single style lock onto an archetype that admits multiple valid expressions.
- **Brief signal → first-pass routing** — vocabulary lookup table for the recommendation step (`luxury` → Corporate Luxury, `bento`/`feature grid` → Bento, `bespoke nav` → Experimental, etc.) with the user validating before commit
- **Atmosphere Calibration** — Density, Variance, Motion scores (1–10) make design measurable, with concrete CSS heuristics per band (`Density 2-3` → `py-32` to `py-48`; `Motion 7-10` → GSAP ScrollTrigger pin/scrub on hero)
- **Pre-DESIGN.md plan block** — five-bullet pre-plan (brief, archetype + expression, atmosphere, signature moment, photography/copy register) is the contract for the file; if it doesn't ring true, restart from step 1
- **Anti-AI tells** — 12 axiomatic rejections (any hit is stop-and-fix) + full catalog of patterns that betray AI generation (visual, typography, layout, content, technical)
- **Output discipline** — banned-phrase list (`// TODO`, `// ...`, "for brevity", "let me know if you want me to continue", `[remaining sections similar]`) plus continuation marker (`[PAUSED — N of 8 sections complete]`) for clean token-ceiling splits
- **Premium patterns** — Doppelrand nested architecture, Button-in-Button trailing icons, eyebrow tags, hero 2-line iron rule + Hero Scale taxonomy, mobile-collapse mandates, performance locks, **Liquid Glass Refraction** (Apple WWDC 2025 register), **Inline Typography Images** (image-as-glyph signature pattern), **Perpetual Micro-Interactions** (Motion ≥ 5 mandate)
- **Audit rubric** — quantitative 0–10 scoring across 7 dimensions (Hierarchy, Spacing, Typography, Color, Motion, Accessibility, Anti-slop) with P0/P1 punch list and CSS fixes
- **Exemplars** — canonical-from-article reference + 4–5 substitutable peers per archetype (Terminal, Lando, Siena, Bruno Simon, Cartier WAW, Anime.js, Ponpon, FlowFest…) shared during recommendation
- **Composition variety mandates** — across multi-section pages, ≥3 different composition anchors, varied background mode per section, CTA shape varied at least once, mixed section ambition (large/mini/medium)
- **Creativity escalation** — push at least three axes beyond the generic SaaS template (composition, typography, hero scale, image treatment, section rhythm, framing); if the design could pass for default Tailwind output, escalate
- **Spring physics canonical values** — `stiffness: 100, damping: 20` pinned in `motion.*` tokens; ad-hoc spring values per component betray the system
- **Archetype remixing** — arbitration framework for briefs that refuse a single archetype (parent DNA percentage, arbitration rules, worked example)
- **Brand extraction from URL** — `-u <url>` reverse-engineers a DESIGN.md observation from a live site as the archetype seed
- **Retrofit playbook** — when `-u <url>` is the user's own legacy site and the intent is "upgrade without rebuilding", a seven-step priority order (font swap → color cleanup → hover/active → layout → component replacement → empty/error/loading → typography polish) lifts targeted scores without re-architecting
- **Brutalist syntax decoration** — Grid Determinism (`gap: 1px` reveal-through), ASCII brackets, registration symbols, process strings, faux machine-readable as structural geometry, plus Bimodal Density Oscillation as DNA bullet
- **Production hardening** — iOS Safari + cross-browser shipping for video, scroll-driven cinematic, full-screen heroes (viewport units, autoplay belt-and-suspenders, scroll-restoration, fail-safe reveal logic)
- **UX quality rules** — touch targets, safe areas, form behavior, animation precision
- **Judging criteria** — Design 40%, Usability 30%, Creativity 20%, Content 10%
- **Performance targets** — LCP < 1.5s, CLS < 0.05, INP < 100ms
- **Modern stack** — OKLCH, Scroll-Driven Animations, View Transitions API, GSAP + Lenis, WebGPU (Three.js r171+)
- **Visual review** — optional `dev-browser` CLI integration for screenshot-based iteration

**Sources**

- [Award-winning websites 2025-2030 (Coroboros Research)](https://github.com/coroboros/research/blob/main/articles/award-winning-websites-2025-2030/award-winning-websites-2025-2030.md) — judging criteria, SOTD/SOTY patterns, studio analysis (Locomotive, Active Theory, Resn, Immersive Garden, Cuberto)
- [Vercel Web Interface Guidelines](https://github.com/vercel-labs/web-interface-guidelines) — UX quality rules
- [Google DESIGN.md](https://github.com/google-labs-code/design.md) — canonical format for the DESIGN.md produced by this skill; `@google/design.md` CLI lints the output
- [Google Stitch Skills](https://github.com/google-labs-code/stitch-skills) (`taste-design`) — Atmosphere Calibration (Density / Variance / Motion)
- [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) — taste-driven design heuristics complementing the atmosphere axes
- [rohitg00/awesome-claude-design](https://github.com/rohitg00/awesome-claude-design) (MIT) — exemplars taxonomy, audit rubric format, remix arbitration framework, brand-extraction prompt
- [dev-browser](https://github.com/SawyerHood/dev-browser) — CLI visual review

Produces `DESIGN.md` consumed by `design-system` for ongoing governance. Token-level changes go through `/design-system` — this skill is for initial creation and complete re-architecting only.

---

#### design-system

Govern `DESIGN.md` — the [Google DESIGN.md open standard](https://github.com/google-labs-code/design.md) (YAML frontmatter tokens + eight prose sections). Auto-activates during UI edits to enforce token-only sourcing, and exposes seven CLI-backed subcommands for the full DESIGN.md lifecycle. `audit-extensions` closes the bidirectional drift loop between DESIGN.md extension namespaces (motion, shadows, aspect-ratios, heights, containers, breakpoints, z-index, border-widths, opacity, scroll-triggers — see `references/extended-tokens.md`) and the `globals.css` `@theme` mirror.

**Requirements**

- `npx` (for the `@google/design.md` CLI wrapped by `audit`, `diff`, `export`, `spec`). Missing → subcommands fall back to manual validation against the bundled spec.

**Usage**

Auto-activates when editing:
- `src/components/**`, `src/app/**`, `src/pages/**`, `src/layouts/**`, `src/styles/**`
- `src/features/*/components/**`
- `DESIGN.md`, `tailwind.config.*`

Also invocable directly via `/design-system` with one of seven subcommands:

```bash
/design-system audit                                # lint ./DESIGN.md, report with fix proposals
/design-system audit ./docs/DESIGN.md -s            # save the report under ~/.claude/output/
/design-system diff                                 # diff ./DESIGN.md vs HEAD (git-aware)
/design-system diff old.md new.md                   # two-file diff
/design-system export tailwind                      # → tailwind.theme.json
/design-system export dtcg -o tokens.json           # W3C DTCG format
/design-system spec --rules                         # emit canonical spec + lint rules
/design-system migrate ./legacy-DESIGN.md           # Stitch 9-section → Google standard
/design-system init editorial                       # scaffold a minimal DESIGN.md
/design-system audit-extensions                     # YAML ↔ prose ↔ globals.css drift check
/design-system audit-extensions --strict            # promote orphan warnings to errors
```

**Subcommands**

| Subcommand | Purpose | Output |
|------------|---------|--------|
| `audit` (aliases `check`, `lint`) | Lint DESIGN.md + produce fix proposals per finding | Markdown report |
| `diff` | Regression check between versions — git-aware default | Markdown report |
| `export` | Convert tokens to Tailwind theme or W3C DTCG | `tailwind.theme.json` / `tokens.json` |
| `spec` | Emit the canonical spec from the installed CLI | Markdown or JSON |
| `migrate` | Port legacy Stitch 9-section DESIGN.md → Google standard | New DESIGN.md + backup + migration report |
| `init` | Scaffold a minimal valid DESIGN.md (fallback from `/award-design`) | New DESIGN.md |
| `audit-extensions` | Bidirectional drift check between DESIGN.md extension YAML, prose refs, and `globals.css` `@theme` | Markdown report |

**Flags**

| Flag | Subcommand | Description |
|------|------------|-------------|
| `-s` | `audit`, `diff`, `audit-extensions` | Save the report to `~/.claude/output/{project}/design-system/{sub}/report.md` |
| `-o <path>` | `export`, `spec`, `migrate`, `init` | Output file (defaults vary by subcommand) |
| `--json` | `audit`, `diff`, `spec`, `audit-extensions` | Raw JSON instead of the formatted report |
| `--strict` | `audit`, `audit-extensions` | `audit`: cross-check the DESIGN.md against `/award-design`'s anti-patterns catalog. `audit-extensions`: promote `extension-orphan-css` warnings to errors |
| `--rules` | `spec` | Append the active lint rules table |
| `--rules-only` | `spec` | Output only the lint rules |
| `--format tailwind\|dtcg` | `export` | Target format (default: `tailwind`) |
| `--base <ref>` | `diff` | Git comparison base (default: `HEAD`) |
| `--css <path>` | `audit-extensions` | Path to `globals.css` (auto-detected when omitted) |

When `dev-browser` is installed globally (`pnpm add -g dev-browser` / `npm i -g dev-browser` / `bun add -g dev-browser`), `audit` auto-suggests visual verification in its Next steps — no flag needed. Skip silently otherwise.

**What it does**

- Reads `DESIGN.md` before writing any UI code
- Enforces colors, fonts, spacing, and corner radius come exclusively from DESIGN.md YAML tokens
- Maps tokens to CSS custom properties and `tailwind.config.ts theme.extend` — or generates via `/design-system export tailwind`
- Prevents arbitrary Tailwind values (`text-[13px]`) when a token exists
- Handles dark mode, framework detection, shared brand across projects
- Maps award-design archetype output to each of the eight DESIGN.md sections
- **Post-edit invariant**: after any DESIGN.md mutation (token update, `migrate`, `init`), runs `audit` and surfaces findings — a mutation that leaves errors behind is never done

**DESIGN.md structure**

A DESIGN.md has two layers: YAML frontmatter (normative design tokens) + eight ordered prose sections (rationale).

Canonical YAML token groups (validated by the Google CLI): `colors`, `typography`, `rounded`, `spacing`, `components` — with `{path.to.token}` cross-references. Components bind ONLY to the closed set of 8 property tokens (`backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`).

Extension YAML namespaces (preserved-but-unvalidated per the Google spec, validated by `audit-extensions` against the `globals.css` `@theme` mirror): `motion`, `shadows`, `aspectRatios`, `heights`, `containers`, `breakpoints`, `zIndex`, `borderWidths`, `opacity`, `scrollTriggers`. Extension tokens are referenced from prose only — never as `components:` keys (the empirical lint-failure mode). See `references/extended-tokens.md` for the full convention and the 1:1 CSS-mirror mapping table.

Section order:

1. **Overview** (alias: *Brand & Style*)
2. **Colors** — `colors:` tokens
3. **Typography** — `typography:` tokens
4. **Layout** (alias: *Layout & Spacing*) — `spacing:` tokens + responsive strategy + extension `breakpoints`, `containers`, `heights`, `aspectRatios`, `motion`, `scrollTriggers`
5. **Elevation & Depth** — shadow system + extension `shadows`, `borderWidths`, `opacity`
6. **Shapes** — `rounded:` tokens
7. **Components** — `components:` tokens, variants as related keys (`button-primary`, `button-primary-hover`) + extension `zIndex`
8. **Do's and Don'ts** — testable guardrails

**CLI-backed lint rules** — eight rules run by `audit` (and `diff` for regression detection): `broken-ref` (error), `missing-primary`, `contrast-ratio` (WCAG AA 4.5:1), `orphaned-tokens`, `token-summary`, `missing-sections`, `missing-typography`, `section-order`. **Project-side rules** added by `audit-extensions`: `extension-missing-css` (error), `extension-orphan-css` (warning, error under `--strict`), `extension-broken-ref` (error). See `references/cli-reference.md` for severities and fix strategies; `references/subcommand-audit.md` and `references/subcommand-audit-extensions.md` for the per-rule fix-proposal logic.

Ships with a condensed spec (`references/design-md-spec.md`), the CLI reference (`references/cli-reference.md`), seven subcommand reference files (`references/subcommand-*.md`), the extended-tokens convention (`references/extended-tokens.md`), four deterministic scripts (`scripts/{audit,diff,export,audit-extensions}.sh` plus `audit_extensions.py`), and two complete example DESIGN.md files (`references/example-claude.md` — warm editorial with extension showcase, `references/example-stripe.md` — minimalist gradient). Delegates to `/award-design` when a DESIGN.md needs to be created from a brief.

**Sources**

- [Google DESIGN.md](https://github.com/google-labs-code/design.md) — the canonical open standard this skill enforces; `@google/design.md` CLI for `lint`, `diff`, `export`, `spec`
- [W3C Design Token Format](https://www.designtokens.org/) — token schema inspiration; `export --format dtcg` produces a compatible `tokens.json`

</details>

---

### Claude Code Skills

Meta skills for configuring Claude Code itself — `claude-md`, `agent-creator`.

<details>
<summary><em>claude-md · agent-creator</em></summary>

<br>

#### claude-md

Create and optimize CLAUDE.md memory files and `.claude/rules/` modular rules for Claude Code projects.

**Usage**

```bash
/claude-md init        # Scaffold a new CLAUDE.md
/claude-md optimize    # Deep cleanup of existing CLAUDE.md
/claude-md revise      # Capture session learnings
```

**What it does**

- **`init`** — detects stack, scripts, and architecture-critical files. Generates a minimal CLAUDE.md (20–50 lines)
- **`optimize`** — research-backed cleanup using 6 bloat categories (ETH Zurich study). Target: < 100 lines
- **`revise`** — reviews the current session for commands, patterns, and corrections. Drafts additions with diffs for approval

**Key features**

- File hierarchy (enterprise > project > user > local)
- Modular `.claude/rules/` with path-scoped YAML frontmatter
- Size limits guidance (< 100 ideal, < 150 max, > 200 = directives get lost)
- Writing rules — prohibitions over positive guidance, emphasis hierarchy, show don't tell

**Sources**

- [Anthropic — Memory and CLAUDE.md docs](https://code.claude.com/docs/en/memory) — official memory system architecture and file resolution
- [anthropics/claude-plugins-official — claude-md-management](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-md-management) — canonical scaffolding and optimization patterns
- [Melvynx/aiblueprint — claude-memory](https://github.com/Melvynx/aiblueprint) — bloat categorization (ETH Zurich study) and revision workflow

---

#### agent-creator

Expert guidance for creating, configuring, and orchestrating Claude Code subagents.

**Usage**

```bash
/agent-creator
```

**What it does**

- Walks through creating new agents with proper YAML frontmatter (`name`, `description`, `tools`, `model`)
- Covers tool restrictions, model selection, permission modes, hooks, memory, isolation
- Explains the execution model (subagents are black boxes — no user interaction)
- Provides system prompt writing guidelines with anti-patterns
- Documents scope and priority resolution (managed > CLI > project > user > plugin)
- Background execution patterns for parallel agent workflows
- Includes reference files for orchestration, evaluation, error handling, context management, and debugging

**Sources**

- [Anthropic — Claude Code sub-agents docs](https://code.claude.com/docs/en/sub-agents) — official spec for subagent frontmatter, model selection, tool restrictions
- [Melvynx/aiblueprint — subagent-creator](https://github.com/Melvynx/aiblueprint) — orchestration patterns and system-prompt anti-patterns

</details>

---

### Media Skills

Media conversion, polishing, and production — `video-loop`, `audio-loop`, `suno-produce`, `markitdown`.

<details>
<summary><em>video-loop · audio-loop · suno-produce · markitdown</em></summary>

<br>

#### video-loop

Loop background videos for the web — crossfade the cut point, optimize, multi-format encode. The ffmpeg pipeline runs via a bundled `scripts/video-loop.sh` for deterministic, typo-proof execution.

**Requirements**

- `ffmpeg` and `ffprobe` on PATH
  - macOS: `brew install ffmpeg`
  - Debian/Ubuntu: `sudo apt install ffmpeg`
  - Windows: https://ffmpeg.org/download.html

**Usage**

```bash
/video-loop hero.mp4                    # Crossfade + optimize + encode MP4/WebM
/video-loop hero.mp4 -d 2.0             # Custom crossfade duration (default: 1.5s)
/video-loop hero.mp4 -q 23 -w 28        # Higher quality (lower CRF = bigger file)
/video-loop hero.mp4 -p                 # Also extract poster frame
/video-loop hero.mp4 -n                 # Skip crossfade — optimize/encode only
/video-loop hero.mp4 -o public/videos/  # Custom output directory
```

**Flags**

| Flag | Default | Description |
|------|---------|-------------|
| `-d` | `1.5` | Crossfade duration (seconds) |
| `-q` | `26` | H.264 CRF (18 = high, 28 = small) |
| `-w` | `32` | VP9 WebM CRF |
| `-o` | input dir | Output directory |
| `-p` | off | Extract poster frame (JPEG) |
| `-n` | off | No crossfade, encode only |

**What it does**

1. Validates ffmpeg and reads source metadata
2. Extracts first/last frames to assess loop visibility (VLM decides whether crossfade is warranted)
3. Invokes `scripts/video-loop.sh`, which builds a lossless intermediate with `xfade` crossfade at the **start** — the loop point (`end → start`) lands on identical frames, making the transition invisible
4. Encodes optimized H.264 MP4 (`-movflags +faststart`, audio stripped)
5. Encodes VP9 WebM as an alternative format
6. Optionally extracts a poster frame
7. Parses `RESULT: key=value` lines from the script and reports a size table + suggested HTML `<video>` markup

Output duration = original − crossfade duration (e.g. 8s video with 2s fade → 6s loop). Rejects `-d >= duration/2` with a hard error.

**Sources**

- [FFmpeg](https://ffmpeg.org) — the video pipeline this skill orchestrates

---

#### audio-loop

Produce a gapless web-ready ambient audio loop from a source clip — auto-balance stereo, normalize loudness, encode lossless FLAC, emit the Web Audio JS pattern that unlocks playback on the first user gesture. The ffmpeg pipeline runs via a bundled `scripts/audio-loop.sh` for deterministic, typo-proof execution.

**Requirements**

- `ffmpeg` and `ffprobe` on PATH
  - macOS: `brew install ffmpeg`
  - Debian/Ubuntu: `sudo apt install ffmpeg`
  - Windows: https://ffmpeg.org/download.html

**Usage**

```bash
/audio-loop breeze.wav                  # Balance + normalize + FLAC encode
/audio-loop breeze.wav -t -24           # Louder target (default -28 LUFS)
/audio-loop breeze.wav -v 0.4           # Lower volume in the emitted JS snippet
/audio-loop breeze.wav -B               # Skip stereo balance auto-correction
/audio-loop breeze.wav -o public/audio/ # Custom output directory
/audio-loop -s breeze.wav               # Save under ~/.claude/output/{project}/audio-loop/breeze/
```

**Flags**

| Flag | Default | Description |
|------|---------|-------------|
| `-t <LUFS>` | `-28` | Integrated loudness target |
| `-v <0..1>` | `0.6` | Target volume baked into the emitted JS snippet |
| `-o <dir>` | input dir | Output directory |
| `-s` / `-S` | off | Save to `~/.claude/output/{project}/audio-loop/{slug}/` / force no-save |
| `-B` | off | Disable stereo balance auto-correction |

**What it does**

1. Validates ffmpeg and probes the source (duration, sample rate, channels, per-channel RMS)
2. Measures stereo imbalance — if the L/R delta exceeds 1 dB, wires a `pan` filter that attenuates the louder channel (skipped below 0.3 dB as jitter, or with `-B`)
3. Invokes `scripts/audio-loop.sh` which chains `pan` (if needed) → `loudnorm=I=<target>:TP=-2:LRA=7` → `aresample=<source_rate>` → FLAC encode
4. Parses `RESULT: key=value` lines from the script and reports size, final loudness, per-channel balance
5. Emits a drop-in `<script>` snippet implementing the Web Audio unlock-on-first-gesture pattern with fade-in, tuned to the `-v` target

**Why FLAC and not AAC.** Web Audio's `AudioBufferSourceNode{loop:true}` loops sample-accurate by spec, but it loops the buffer that `decodeAudioData` returned — AAC's priming samples are baked into that buffer on most browser decoders, producing an audible gap at the loop boundary. FLAC is lossless with no priming, so the decoded buffer is byte-identical to the source WAV. Trade: FLAC is ~6–8× larger than AAC 128 kbps on noise-heavy content, but still modest for typical ambient loops (a few hundred KB to low MB).

**No crossfade flag.** If the user reports a lingering bump and a crossfade fix makes it *worse*, the discontinuity is at the codec layer, not the signal — the fix is format (FLAC), not masking. The skill's absence of a crossfade flag enforces this diagnostic.

Ships with `references/scroll-tied-pattern.md` documenting the multiplicative factors architecture (`gain = TARGET × fadeInFactor × scrollVolumeFactor`) for cases where audio should track a visual transition like a hero video contracting out of view.

**Sources**

- [FFmpeg](https://ffmpeg.org) — the audio pipeline this skill orchestrates
- [MDN Web Audio API](https://developer.mozilla.org/docs/Web/API/Web_Audio_API) — `AudioContext`, `AudioBufferSourceNode`, `GainNode` reference

---

#### suno-produce

Turn a music brief into Suno v5.5-ready prompt artifacts. Artifact-emit-only — the user copy-pastes the prompt block into Suno's Web/iOS/Android UI, listens, then iterates via `revise`. No API integration (Suno has no official public API; reverse-engineered wrappers are degrading — PiAPI dropped V5, the WMG settlement signals tighter enforcement).

Three artifact tiers, scaffolded progressively:

- **TRACK.md** — always emitted. The unit of Suno generation: copy-paste-ready Style of Music + Lyrics + Exclude Styles + Sliders, plus rationale and iteration log.
- **ALBUM.md** — emitted only when album mode is detected from the brief. Holds concept, arc, tracklist with BPM/key flow, transitions.
- **ARTIST.md** — optional artist-identity layer, **artist-scoped** (one file referenced from many album folders via `-f`). Declares Voice profile, Custom Model, recurring instrumentation, rights/compliance posture. The filename is `ARTIST.md` rather than the alternative `MUSIC.md` because the contents describe an artist persona, not music — a deliberate evolution of the open standard.

**Usage**

```bash
/suno-produce indie folk track about a long winter
/suno-produce melodic-trap EP about leaving home
/suno-produce -f ~/artists/studio-a/ARTIST.md cinematic single
/suno-produce revise tracks/01-midnight-letter "chorus too dry, vocals washed out"
/suno-produce validate projects/quiet-rooms/
```

**Subcommands**

| Subcommand | Purpose |
|------------|---------|
| `create` (default) | Synthesise TRACK.md from brief; ALBUM.md when multi-track; reads bound ARTIST.md if `-f` |
| `revise <path> "<feedback>"` | Archive current TRACK.md to `versions/v{N+1}.md`, emit refined TRACK.md |
| `validate <path>` (aliases `lint`, `check`) | Run multi-type linter — TRACK.md / ALBUM.md / ARTIST.md, auto-dispatch by filename |

**Flags**

| Flag | Description |
|------|-------------|
| `-f <path/to/ARTIST.md>` | Bind the artifact to an artist identity (Voice / Custom Model / instrumentation defaults flow in) |

**What it does**

1. Detects album mode from brief language (`EP`, `album`, `4-track`, …) and confirms before scaffolding
2. Auto-detects "sufficiently specified" — skips the AskUserQuestion interview when the brief covers ≥ 3 of: genre, mood, vocal direction, length, references
3. Synthesises Style of Music (4–7 descriptors, 5 classes), Lyrics (Tier 1 bracket metatags, parenthetical performance cues), Exclude Styles (cap 3), Sliders (per-genre defaults from the operator reference)
4. Adjusts for Voice / Custom Model — drops vocal descriptors and redundant style cues; raises Audio Influence to 70–90%
5. Validates every write through `scripts/validate.py` — RED never reaches disk
6. Archives prior takes under `versions/v{N}.md` on `revise`; keeps the audio takes (`audio/`) gitignored

**Validator (multi-type)**

`scripts/validate.py` auto-dispatches by filename and runs the matching check set. Verdicts: GREEN (zero issues), YELLOW (warnings only), RED (errors — blocks the write). Exit codes: 0 / 2 / 1.

| Artifact | RED checks | YELLOW checks |
|----------|-----------|---------------|
| TRACK.md | Style/Lyrics/Title length, slider out of range, BPM in Lyrics, SFX bracket, **artist-citation patterns in Style or Lyrics** (`in the style of X`, `voice of/like X`, `sounds like X`, `à la X`, `X's sound/style/voice/era`) | descriptor count, genre count, conflicting eras, Tier 3 brackets, voice/style conflict, exclude > 3, **title-case proper-noun pair in Style outside the safe-phrase whitelist** |
| ALBUM.md | invalid release_format, missing Concept/Arc/Tracklist/Transitions, track_count mismatch | arc-label missing, malformed tracklist line, bad ISO date |
| ARTIST.md | voice_profile without voice_consent, slider_bias out of range, missing required sections, empty artist | bad consent format, custom_model without training-set posture, bad rights_posture |

**Bundled references**

- `references/style-and-lyrics.md` — descriptor stack, **never name artists or copyrighted entities** (the legal + functional rationale, with a translation table), bracket metatag canon, lyric flow, languages, SFX warning, **section length / bar counts belong in Studio**, consolidated pitfalls
- `references/sliders-and-personalization.md` — three sliders, voice-aware prompting, custom-model-aware prompting, **My Taste — the silent fourth slider**
- `references/genre-templates.md` — 8 copy-paste recipes (cinematic, melodic techno, melodic trap, alt rock, ambient drone, indie pop, ritual industrial, lo-fi hip-hop)
- `references/track-schema.md` — TRACK / ALBUM / ARTIST schemas with worked example, plus a migrating-from-MUSIC.md note
- `references/rights-and-deprecation.md` — **plan tiers + v5.5 access**, **output specs**, **post-generation pipeline (Suno Sounds + Studio 1.2)**, WMG settlement, copyright vesting (license, not vested rights), voice-cloning consent, v6 deprecation cliff

Loaded on-demand per Pattern 2 (domain-specific organisation) from Anthropic's [skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

**Sources**

- [Coroboros Research — Suno v5.5 Operator Reference](https://github.com/coroboros/research/blob/main/articles/suno-v5-5-operator-reference.md) — the canonical operator reference distilled into the bundled refs
- [Suno v5.5 release post](https://suno.com/blog/v5-5) and [help center](https://help.suno.com) — official documentation
- [Spidy88/suno-claude-skill](https://github.com/Spidy88/suno-claude-skill) — community schema convergence (Title / Style / Lyrics / Sliders / Tips)
- [Blake Crosley — Suno V5.5 reference](https://blakecrosley.com/guides/suno) and [Stoke McToke — Suno meta tags guide](https://stokemctoke.com/the-complete-suno-ai-meta-tags-guide/) and [suno.wiki metatags](https://www.suno.wiki/faq/metatags/) — community-validated prompt-engineering frameworks

---

#### markitdown

Convert any document to Markdown using [Microsoft's `markitdown` CLI](https://github.com/microsoft/markitdown) — PDF, DOCX, PPTX, XLSX, HTML, CSV, JSON, XML, ZIP, EPub, images (OCR/EXIF), audio (transcription), and YouTube URLs.

**Requirements**

- Python ≥ 3.10 with the `markitdown` CLI on PATH:
  - Full install: `pip install 'markitdown[all]'`
  - Selective: `pip install 'markitdown[pdf,docx,pptx,xlsx]'` (groups: `pdf`, `docx`, `pptx`, `xlsx`, `xls`, `outlook`, `audio-transcription`, `youtube-transcription`, `az-doc-intel`)
- For Azure Document Intelligence (`-d`): export `MARKITDOWN_DOCINTEL_ENDPOINT=https://<resource>.cognitiveservices.azure.com/`

**Usage**

```bash
/markitdown ~/Downloads/report.pdf            # convert and print to terminal
/markitdown -s ~/Downloads/report.pdf         # convert + save under ~/.claude/output/{project}/markitdown/report/
/markitdown -s -p deck.pptx                   # use third-party plugins (e.g. markitdown-ocr)
/markitdown -d invoice.pdf                    # Azure Document Intelligence
/markitdown -k brand.html                     # keep base64 images inline
/markitdown https://youtu.be/dQw4w9WgXcQ      # YouTube transcript
/markitdown -l                                # list installed plugins, then exit
```

**Flags**

| Flag | Default | Description |
|------|---------|-------------|
| `-s` | off | Save Markdown to `~/.claude/output/{project}/markitdown/{slug}/{stem}.md` |
| `-S` | — | Force no-save (override an ambient save mode) |
| `-d` | off | Use Azure Document Intelligence (needs `MARKITDOWN_DOCINTEL_ENDPOINT`) |
| `-p` | off | Enable installed third-party `markitdown` plugins |
| `-k` | off | Keep data URIs (base64 images) inline in the output |
| `-l` | — | List installed plugins and exit |

**What it does**

1. Validates that `markitdown` is installed; if not, prints the install command and stops (never auto-installs)
2. Detects whether the input is a local file or an `http(s)://` URL (YouTube etc.) and validates the file exists
3. Composes the right `markitdown` invocation based on the flags above
4. Streams the converted Markdown to the terminal, or — when `-s` — writes it under `~/.claude/output/{project}/markitdown/{slug}/{stem}.md` for downstream skills to consume via `-f`
5. Reports a one-line summary: `markitdown: <input> → <bytes> bytes of Markdown`

The deterministic work (install check, validation, slug, save path, command composition) runs in `scripts/markitdown.sh`, which emits `RESULT: key=value` lines parsed by the skill — same pattern as `video-loop`.

**Sources**

- [Microsoft `markitdown`](https://github.com/microsoft/markitdown) (MIT) — the CLI this skill wraps

</details>

---

### Productivity Skills

External knowledge and workflow integrations — `notion` (with future room for Linear, Slack, calendars).

<details>
<summary><em>notion</em></summary>

<br>

#### notion

Notion access from Claude Code. Default path is the [official Notion MCP connector](https://developers.notion.com/page/changelog) — covers ~95% of intents (pages, databases, views, comments, search, blocks, users, teams). The [`ntn` CLI](https://developers.notion.com/cli/get-started/installation) is optional and used only for: file uploads, Notion Workers, headless/CI scripts, raw API discovery, and shell piping.

**Requirements**

- The Notion MCP connector enabled at https://claude.ai/settings/connectors (account-level toggle, powers the default path).
- The `ntn` CLI on PATH — only when one of the five CLI-required cases applies. Install + auth: https://developers.notion.com/cli/get-started/installation, https://developers.notion.com/cli/get-started/authentication. Set `NOTION_API_TOKEN` (prefix `ntn_…` or `secret_…`) in `.envrc` (gitignored, `chmod 600`) for headless / CI use; never commit it.

**Usage**

The skill auto-triggers from prose intent — there are no flags. Examples of trigger phrases:

```
create a Notion database called Demo Tasks in the Engineering page
fetch the Notion page about Q4 strategy and summarize it
add a Status column with options Todo / Doing / Done to my Sprint DB
upload screenshot.png to my Notion page about Q4 mockups
build a Notion Worker that listens for new database rows
script a daily Notion sync from a GitHub Actions workflow
list every Notion API endpoint that touches comments
```

**What it does**

1. **Routes** the user's intent to the right transport — MCP for ~95% of cases (pages, DBs, views, comments, search), `ntn` CLI for the five exceptions (uploads, Workers, headless/CI, raw API discovery, shell piping).
2. **Pre-flights** before any content write — reads the `notion://docs/enhanced-markdown-spec` MCP resource for Markdown rules, and `notion-fetch`es target data sources to retrieve the current SQLite-style schema (case-sensitive property names, expanded date / place keys, `__YES__` / `__NO__` checkboxes, `userDefined:` prefix for properties literally named `id` or `url`).
3. **Applies the gotchas** that aren't surfaced by tool descriptions or `ntn --help` — `selection_with_ellipsis` matches rendered Markdown verbatim; new databases land at the bottom of the parent page; `notion-create-pages` batches up to 100 rows per call; the MCP gains tools roughly monthly so check the changelog when something looks missing; writes fail with `archived ancestor` if any parent is in the trash (pre-flight masks this — verify with `notion-fetch` and check the `deleted` attribute on the `<page>` tag).
4. **Defers everything else** — per-tool DSL syntax goes through the tool description in the live session; CLI commands through `ntn --help`; capability evolution through the changelog. A new MCP tool or `ntn` subcommand needs no skill update.

**Sources**

- [Notion MCP overview](https://developers.notion.com/guides/mcp/overview) — start here for setup and first-call walkthroughs
- [Notion MCP changelog](https://developers.notion.com/page/changelog) — capability evolution, monthly cadence
- [`ntn` CLI command reference](https://developers.notion.com/cli/reference/commands) — authoritative for CLI surface
- [Notion REST API reference](https://developers.notion.com/reference) — when neither MCP nor CLI covers an action

</details>

---

### Writing Skills

Structural and prose writing for project documentation — `brand-voice`, `write-clear-readme`, `humanize-en`.

<details>
<summary><em>brand-voice · write-clear-readme · humanize-en</em></summary>

<br>

#### brand-voice

Govern `BRAND-VOICE.md` — the canonical writing voice document for a brand. Mirrors the `design-system` pattern: a canonical file at the project root, five CLI-style subcommands. Produces a YAML frontmatter (machine-readable rules) plus eleven prose sections (human rationale). Multi-voice via `voice.extends` — a child file inherits a parent's rules and overrides only what differs (founder voice on top of corporate, persona on top of institutional, multi-host media brand). Optional `lexical_exceptions: { acronyms, compound_idioms }` whitelists let a voice admit `BPM`, `MIDI`, `in-your-face` and similar tokens without false positives in `humanize-en`. Consumed by writing skills via `-f`.

**Usage**

```bash
/brand-voice extract -u https://example.com/about               # ingest URL → ./BRAND-VOICE.md
/brand-voice extract -f ~/notes/style.md                        # ingest a local MD file
/brand-voice extract -d ~/style-archive/                        # ingest a folder of MDs
/brand-voice extract -n <notion-page-id>                        # ingest a Notion page (MCP)
/brand-voice extract                                            # interview mode (8 questions)
/brand-voice extract -u https://x.com -f ./notes.md             # combine multiple sources
/brand-voice extract -o ./assets/voice.md -u https://x.com      # override output path

/brand-voice update -u https://example.com/v2                   # refresh from new sources
/brand-voice diff HEAD~5 HEAD                                   # show what changed (git-aware)
/brand-voice diff BRAND-VOICE-FOUNDER.md                        # single-arg: child vs resolved parent (multi-voice)
/brand-voice validate                                           # lint ./BRAND-VOICE.md against canonical format
/brand-voice lint ./assets/voice.md                             # alias on a custom path
/brand-voice show --rules                                       # print testable rules
/brand-voice show --chain                                       # print the resolved inheritance chain
/brand-voice show --explain                                     # annotate each rule with origin file
/brand-voice show --all                                         # rules + examples + counter-examples

/brand-voice extract --extends ./BRAND-VOICE.md \
                     -o ./BRAND-VOICE-FOUNDER.md                # scaffold a child voice (multi-voice)
```

**Subcommands**

| Subcommand | Purpose |
|------------|---------|
| `extract` | Ingest sources, synthesise canonical voice doc, write to `./BRAND-VOICE.md` |
| `update` | Refresh an existing voice doc; preserves manual sections; shows diff before write |
| `diff` | Read-only — what changed between two versions or two refs (git-aware) |
| `validate` (aliases: `lint`, `check`) | Lint a voice doc against the canonical format — verdict + errors + warnings + fix suggestions, CI-friendly exit codes |
| `show` | Print the flat list of testable rules from the voice doc |

**Flags**

| Flag | Meaning |
|------|---------|
| `-u <url>` | URL source — `WebFetch` direct, fallback to `/markitdown -s <url>` |
| `-n <id\|url>` | Notion page — via `mcp__claude_ai_Notion__notion-fetch` |
| `-d <dir>` | Folder of MD/MDX — `Glob` aggregate |
| `-f <file>` | Single MD/MDX/TXT file |
| `-o <path>` | Output path (default: `./BRAND-VOICE.md`) |
| `-s` / `-S` | Save / disable save under `~/.claude/output/{project}/brand-voice/brand-voice-{slug}.md` |
| `--extends <parent>` | (`extract`) scaffold a child voice inheriting from `<parent>`; pre-flight lints the parent (refuses on RED) |
| `--raw` | (`show`) skip `voice.extends` chain resolution; print child-only rules |
| `--chain` | (`show`) print the resolution chain root → child |
| `--explain` / `--explain-json` | (`show`) annotate each rule with origin file (text or structured JSON) |
| `--resolved` | (`diff`) compare merged outputs (chain-aware) instead of files-as-written |
| `--full` / `--legacy` | full output (default; adds `core_attributes` + `contexts` + `source_urls`) vs v1 minimal output for back-compat consumers |

**What it does**

1. **Ingests** sources from URL, Notion, MD file, MD directory, or interactive interview
2. **Synthesises** the canonical format — YAML normative rules (forbidden lexicon, rewrite rules with stable `rule_id`s, sentence norms, forbidden patterns, contexts, pronouns) plus eleven prose sections explaining each rule
3. **Lints** every write through `voice_lint.py` — RED never reaches disk
4. **Diffs** semantically — shows added/removed lexicon, modified rules, prose changes, manual-section preservation
5. **Surfaces** the rules — `show --rules` emits a flat rule block consumed by `humanize-en -f` and pipeable to other tooling
6. **Inheritance** — a child file declaring `voice.extends: ./BRAND-VOICE.md` inherits the parent's rules and overrides only what differs. `_replace` and `_remove` suffixes give surgical control. Cycle detection uses inode identity so case-insensitive filesystems do not mask cycles. See `references/example-multi-voice.md`.

**Pipeline**

```
/brand-voice extract -u https://example.com/about
      |
/humanize-en -f ./BRAND-VOICE.md draft.md
      → universal AI-tells + brand-specific rewrite rules applied
```

**Audit (CI / pre-merge)**

```bash
python3 ~/.claude/skills/brand-voice/scripts/lint_all.py .
```

Globs every `BRAND-VOICE*.md` under the root and lints each. Exit 1 on any RED. Catches parent-change regressions across all children in one command — recommended for CI on every PR that touches a voice file.

**Sources**

- [Google DESIGN.md](https://github.com/google-labs-code/design.md) — the architectural pattern this skill mirrors (canonical project-root file, lifecycle subcommands)
- [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) — overlap with universal AI-tells; `humanize-en` consumes the brand voice rules in addition

---

#### write-clear-readme

Author, audit, or polish a project README — clarity, scannable structure (Pattern A per-section collapse / Pattern B grouped / Pattern C per-entry), wording concision, anchor integrity. Reads the repo first; proposes diffs and applies on approval.

**Usage**

```bash
/write-clear-readme                      # Default — audit if README.md exists, author if not
/write-clear-readme author               # Create or fully restructure README.md
/write-clear-readme audit                # Review existing README for structure + clarity issues
/write-clear-readme polish               # Wording-only pass — structure stays, prose tightens
/write-clear-readme audit docs/GUIDE.md  # Audit a specific file
```

**What it does**

1. **Inspects the repo** — `package.json`, top-level folders, entry points, `CLAUDE.md` — to understand what the README must cover
2. **Maps audiences and content shape** — identifies the implicit reader per section, flags multi-audience files, and surfaces content-reshape opportunities (cut, merge, split tables) BEFORE any collapse pattern is picked
3. **Picks the pattern** — Pattern A (per-section collapse) for long human-facing multi-audience docs; Pattern B (grouped collapse) for 5+ peer items in ≤7 groups; Pattern C (per-entry collapse) for reference docs with dozens of API entries; no collapse for short docs
4. **Drafts (author mode)** — overview table at top with anchors, Install / Quick Start uncollapsed, chosen pattern applied uniformly across peers; applies the canonical *Writing rules* + *README-specific style* as it writes
5. **Audits (audit mode)** — runs the structural script (anchors, nested `<details>`, `<br>` after `<summary>`, bloat tokens, `Expand —` prefixes, stale counts adjacent to nouns, h3-above-details redundancy, visual-rhythm signal) AND scores prose against the canonical *Writing rules* + *README-specific style*. Names the silent assumption: audit checks structure, not whether the right content is in the file
6. **Polishes (polish mode)** — wording-only pass; structure stays, prose tightens. Drops filler, replaces marketing voice, splits compound sentences, backticks code-like tokens, swaps numeric content-counts for qualitative descriptors
7. **Verifies the rendered output** before declaring done — source-only checks miss visual monotony and inconsistent collapse
8. **Applies on approval** — edits `README.md` only after explicit user approval

**Key rules**

- Group / section anchors go OUTSIDE `<details>` — GitHub auto-expands parent collapsibles on hash navigation
- Install / Quick Start / Requirements never inside `<details>`
- One level of `<details>` max — nested collapsibles confuse navigation
- **One rule per level** — every peer at the chosen collapse level collapses or none does; selective collapse driven by per-section judgment turns the page into a minefield
- **No `Expand —` prefix** in `<summary>` text — the disclosure triangle is the affordance
- **No h3 directly above `<details>` that repeats the `<summary>` label** — duplicate signal; drop the h3 and let the summary carry the label
- **No numeric content-counts** adjacent to maintainable nouns (`25 symlinks`, `14 tasks`) — counts rot the moment a row is added; use qualitative descriptors
- Signature-first `<summary>` for Pattern C so `Ctrl+F` hits the right entry
- One idea per sentence; front-load the verb; drop filler (`in order to`, `it's important to note that`)
- No marketing voice (`powerful`, `robust`, `leverage`, `seamlessly`)

---

#### humanize-en

Strip AI writing tells from English prose — em-dash overuse, rule of three, negative parallelisms, AI vocabulary (*delve*, *tapestry*, *crucial*, *pivotal*, *underscore*, *showcase*), vague attributions, promotional tone, conjunctive padding (*moreover*, *furthermore*, *indeed*), hedging, signposting, chatbot artifacts. Preserves meaning, structure, code blocks, links, anchors, and frontmatter — rewrites only the flagged phrasing.

Under `-f <BRAND-VOICE.md>` the skill raises the bar: the brand voice becomes the primary contract. A deterministic brand-aware prescan flags every mechanically detectable rule (forbidden lexicon, `rewrite_rules[*].reject`, all-caps emphasis, pronoun violations, signposting, negative parallelism, rule-of-three headings, rhetorical questions, emoji), the LLM walks the full catalogue plus brand rules, then `validate.py` re-runs the checks after the edit and classifies the outcome (`clean` / `residuals` / `regression`). Auto-iterates up to three passes by default.

**Usage**

```bash
/humanize-en README.md                              # file — propose diff, apply on approval
/humanize-en "paste any text to humanize"           # inline — return rewritten text
/humanize-en                                        # ask for input
/humanize-en -f BRAND-VOICE.md draft.md             # brand-aware: prescan + validate + auto-iterate
/humanize-en -f BRAND-VOICE-FOUNDER.md draft.md     # multi-voice (resolves voice.extends chain)
/humanize-en --iterate 1 -f BRAND-VOICE.md draft.md # disable auto-iteration (single pass)
/humanize-en --iterate 5 -f BRAND-VOICE.md draft.md # raise the iteration cap to 5 rounds
/humanize-en --strict-code-only README.md           # treat every fenced block as code (legacy masking)
```

**Flags**

| Flag | Default | Effect |
|---|---|---|
| `-f <voice-doc>` | off | Load a `BRAND-VOICE.md` and apply its rules deterministically (prescan + validate + auto-iterate). |
| `--iterate <N>` | `3` under `-f`, `1` without | Iteration cap. Each round runs `detect → rewrite → validate`; the loop exits early when residuals reach 0 or a regression is detected. `--iterate 1` keeps the legacy single-pass behaviour. |
| `--strict-code-only` | off | Blank every fenced block (legacy masking). Default behaviour scans pseudo-blocks (fences with no info-string or `text`) for prose patterns. |

**What it does**

1. **Detects** against a 32-pattern universal catalogue grouped into six families. Under `-f`, also runs `prescan.py --brand` which flags every mechanically detectable brand rule — fences with no info-string or `text` are pseudo-blocks (scanned), language-hinted fences (`python`, `bash`, etc.) stay verbatim
2. **Rewrites** flagged phrasing with direct, specific alternatives — preserves code, links, anchors, quoted material, technical terms; pseudo-table column alignment is preserved across edits
3. **Validates** — under `-f`, `validate.py` re-runs prescan + brand checks on the rewritten file and surfaces residuals or regressions; auto-iterates up to three rounds
4. **Self-audits** rule-by-rule under `-f`: every `forbidden_pattern`, every `forbidden_lexicon` entry, every `pronouns.forbid` rule appears in the *Coverage report* — even with 0 hits — so a future pass can verify the prior one actually checked the rule
5. **Reports** which patterns (by number for universal, by `rule_id` for brand) were touched, with per-rule hit counts and residuals

Invoked as a subroutine by [`write-clear-readme`](#write-clear-readme) after clarity edits, before presenting the diff. Other skills that produce substantial English prose can invoke it the same way.

**Scope**

- **In** — neutral pattern removal on docs, READMEs, release notes, blog drafts, PR bodies, commentary
- **Out** — voice/personality injection (only on explicit request, via opt-in `references/voice.md`); structural restructuring (use `write-clear-readme`); non-English text

**Sources**

- [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) (maintained by WikiProject AI Cleanup) — canonical pattern taxonomy
- [`blader/humanizer`](https://github.com/blader/humanizer) (MIT) — pattern extensions (filler phrases, hedging, signposting, authority tropes, fragmented headers) and the voice-calibration approach used in `references/voice.md`

</details>

---

## Pipeline

Skills chain together by design. Each works standalone; chaining covers longer workflows without extra tooling.

### Thinking → Planning → Building

```
/forge -s "<question or idea>"               think, decide, and plan
      |
/apex -f <abs forge path> "<task>"           implement systematically
      |
/code-ultrareview -s                       review the change (adaptive, report-only)
      |
/apex -f <abs code-ultrareview path>       fix the findings
```

Or skip ahead: `/forge` → `/apex` for planned work, or `/oneshot` for trivial tasks. Run `/code-ultrareview` after any change for an adaptive fresh-eyes pass before committing.

### Design → Develop

Happy path, new project:

```
/scaffold next-cloudflare              bootstrap project
      |
/award-design "brief"                  create DESIGN.md with archetype + extension namespaces
      |
/design-system audit                   lint canonical tokens, fix findings
      |
/design-system export tailwind         generate tailwind.theme.json (canonical)
      |
/design-system audit-extensions        verify YAML extensions ↔ globals.css @theme are in sync
      |
/design-system                         enforce tokens going forward (auto-activate on UI edits)
```

Legacy project with a Stitch 9-section DESIGN.md:

```
/design-system migrate ./DESIGN.md     port to Google standard (auto-audits, writes backup)
      |
/design-system                         enforce tokens going forward
```

### Voice → Write

Define a brand voice once; apply it on every prose draft.

```
/brand-voice extract -u <brand-url>      ingest sources → ./BRAND-VOICE.md (lints automatically)
      |
/humanize-en -f BRAND-VOICE.md draft.md  apply universal AI-tells + brand-specific rules
      |
/brand-voice update -u <new-source>      refresh as the voice evolves; diff before merge
```

`/brand-voice extract` accepts URL (`-u`), Notion (`-n`), MD file (`-f`), MD directory (`-d`), or interview mode when no source is provided.

Multi-voice via inheritance — when a brand has a founder voice on top of corporate, a persona on top of institutional, or multi-host channels, scaffold a child voice that inherits the parent and overrides only what differs:

```
/brand-voice extract --extends ./BRAND-VOICE.md \
                     -o ./BRAND-VOICE-FOUNDER.md   scaffold child; pre-flights the parent
      |
/humanize-en -f BRAND-VOICE-FOUNDER.md draft.md    chain auto-resolved; merged rules applied
      |
python3 ~/.claude/skills/brand-voice/scripts/lint_all.py .   audit every BRAND-VOICE*.md in CI
```

<details>
<summary><strong>Dependency Graph</strong></summary>

<br>

All dependencies are optional — each skill works standalone.

```mermaid
graph LR
  forge -->|"-f"| apex
  forge -->|"-i"| issues(GitHub Issues)
  issues -->|"-f #N"| apex

  scaffold --> award-design
  award-design <-->|DESIGN.md| design-system

  brand-voice -->|"BRAND-VOICE.md / -f"| humanize-en
  write-clear-readme -.->|if installed| humanize-en

  style issues fill:#2d333b,stroke:#8b949e,stroke-dasharray: 5 5
```

`oneshot` optionally escalates to `apex` or `forge` when a task is too complex. `markitdown -s` produces a file consumable by any skill accepting `-f`. `write-clear-readme` invokes `humanize-en` as a final pass on English output when the skill is installed; otherwise it falls back to a manual pattern check. `brand-voice` produces `BRAND-VOICE.md` consumed by `humanize-en -f` for brand-aware rewriting; both work standalone. All remaining skills (`claude-md`, `agent-creator`, `video-loop`, `markitdown`) are standalone too.

</details>

---

## Testing

Python `unittest` suite under `tests/` covers bundled scripts across every skill.

```bash
# Run everything
python3 -m unittest discover tests/ -v

# Run one skill
python3 -m unittest discover tests/<skill-name>/ -v
```

Stdlib only. See [`.claude/rules/skill-authoring.md`](./.claude/rules/skill-authoring.md) for the testing requirement.

---

## Security

Every push and PR scans the `skills/` tree with [`cisco-ai-defense/skill-scanner`](https://github.com/cisco-ai-defense/skill-scanner) — policy `balanced`, fail-on `critical`. The reusable workflow is SHA-pinned to a tagged release; Dependabot opens a PR when a new version lands.

---

## Standards

This repo follows the [agentskills.io](https://agentskills.io) open standard. Each skill uses the canonical frontmatter fields (`name`, `description`, `license`, `metadata`) plus Claude Code extensions (`when_to_use`, `argument-hint`, `model`, `disable-model-invocation`, `allowed-tools`, `paths`) where applicable.

Authoring conventions live in [`.claude/rules/`](./.claude/rules/):

- [`agentskills-spec.md`](./.claude/rules/agentskills-spec.md) — canonical frontmatter, folder anatomy, size budget
- [`claude-code-skills.md`](./.claude/rules/claude-code-skills.md) — Claude Code extensions and string substitutions
- [`skill-authoring.md`](./.claude/rules/skill-authoring.md) — mandatory use of Anthropic's official `skill-creator`, and the testing requirement that ships with any script change
- [`repo-conventions.md`](./.claude/rules/repo-conventions.md) — flag model, output paths, install, plugin marketplace, test placement
- [`skill-prose-rules.md`](./.claude/rules/skill-prose-rules.md) — canonical writing-rules block embedded in every prose-emitting skill

### Canonical writing rules

Prose-emitting skills (`agent-creator`, `apex`, `award-design`, `brand-voice`, `claude-md`, `code-ultrareview`, `forge`, `oneshot`, `suno-produce`, `write-clear-readme`) carry an identical *Writing rules* block immediately after their H1. The block ships inside the skill folder so the rules travel on independent install — plugins cannot reference files outside their own directory, and `~/.claude/rules/*` is not propagated by `npx skills add`.

The canonical source is [`.claude/rules/skill-prose-rules.md`](./.claude/rules/skill-prose-rules.md). Run `scripts/sync_writing_rules.py` after editing it to propagate changes. The parity test `tests/_meta/test_skill_writing_rules.py` enforces byte-level conformity and blocks merge if any declared skill drifts.

---

## License

[MIT](LICENSE.md)
