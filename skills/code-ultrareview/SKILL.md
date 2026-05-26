---
name: code-ultrareview
description: Eight-axis judgment code review for the current diff — Correctness, Simplification, Tests, Documentation, Style, Intent, Design/API, Performance (+ Coherence on metadata changes). Five-phase pipeline scope → deterministic tool battery (npx/uvx-preferred, zero-install for the JS + Python majority) → 8 parallel LLM axis reviewers → Haiku validators on sub-80 findings (verbatim rubric, ≥80 threshold) → synthesis with no-silent-drop + Conventional Comments JSONL. Every report closes with "What I did NOT check" (security → /security-review, runtime perf, flaky detection). Opt-in flags `--verify-build`, `--mutation-test`, `--reconcile`, `--apply-safe`. Public-skill posture — zero auto-install, graceful skip on missing native tools.
when_to_use: 'User-invoked before commit or PR. Runs the full 8-axis fan-out at max effort — no tiers. Invoke when the user would say "review my changes", "deep review", "did I miss anything", "check before I commit", "drift / gaps / blind spots", "audit this PR". Defers security to /security-review (link in every report); defers runtime performance and benchmarks (explicit non-goal). Distinct from Anthropic''s remote /ultrareview command.'
argument-hint: "[-b <ref>] [--repo-kind <kind>] [--reconcile <input>] [--verify-build] [--mutation-test] [--apply-safe] [--include-prose] [--axes <list>] [--preflight] [-s] [-S]"
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
allowed-tools: Read, Grep, Glob, Bash, Task, WebFetch
model: opus
effort: max
disable-model-invocation: true
metadata:
  author: coroboros
  sources:
    - github.com/anthropics/claude-plugins-official/tree/main/plugins/code-review
    - github.com/anthropics/claude-plugins-official/tree/main/plugins/code-simplifier
    - code.claude.com/docs/en/code-review
    - code.claude.com/docs/en/ultrareview
---

# Code ultrareview

> **Eight-axis judgment code review.** Five-phase pipeline scope → tool battery → 8 parallel axis reviewers → Haiku validators → synthesis. Always runs at full strength. Distinct from Anthropic's remote `/ultrareview` — same goal, in-session on the user's subscription.

<!-- canonical:writing-rules:start -->
## Important — Writing rules

These rules govern every prose artifact this skill emits — READMEs, CHANGELOGs, commit messages, PR bodies, release notes, doc paragraphs, non-trivial comments. Apply them at draft time, verify before output.

- Match the surrounding style — punctuation, capitalization, backtick conventions, em-dash vs parens, bullet style.
- Every sentence changes the reader's understanding. Cut it otherwise.
- Front-load the verb — "Creates", not "This helps you create".
- Concrete over abstract. Lists for ≥3 enumerable items.
- Assert positively. Reserve negation for real constraints (`NEVER commit secrets`).
- No marketing words: powerful, robust, seamlessly, leverage, unlock, comprehensive, delightful.
- No AI tells: delve, tapestry, intricate, pivotal, testament, underscore, crucial, garner, showcase, additionally, moreover, furthermore, indeed.
- After drafting English prose, invoke `/humanize-en` if installed.
<!-- canonical:writing-rules:end -->

## Objective

Run the 8 axes — Correctness, Simplification, Tests, Documentation, Style, Intent, Design/API, Performance — as 8 parallel LLM subagents fed by deterministic tool findings (`scripts/run_battery.sh` from WS-2). Coherence joins as a 9th axis when metadata files change. Sub-80 axis findings get re-scored by Haiku validators against the verbatim rubric in `references/anthropic-verbatim.md`. Findings synthesize into one report with deterministic dedup, inter-axis precedence, A2 no-silent-drop, and a verdict (Ship / Fix-then-ship / Needs work). The report ends with "What I did NOT check" so the coverage limits are explicit.

## Parameters

| Flag | Behavior |
|------|----------|
| `-s` | Save the report + JSONL to `~/.claude/output/{project}/code-ultrareview/code-ultrareview-{slug}.{md,jsonl}` |
| `-S` | Force no-save (overrides any ambient save mode) |
| `-b <ref>` | Override the review base (skip auto-detection via `scripts/resolve_base.sh`) |
| `--repo-kind <kind>` | Override the scope classifier. Values: `skills`, `app`, `library`, `docs`, `monorepo`, `python`, `rust`, `go`, `unknown`. Persistent per-repo override at `.code-ultrareview.yaml` (`repo_kind: <kind>`); the flag wins on conflict. Invalid value exits 2 |
| `--reconcile <input>` | Activate the Intent-axis derivation sub-mode. `<input>` may be `@auto`, `@pr`, an explicit path or directory, `gh:pr:<N>`, `gh:issue:<owner>/<repo>#<N>`, or a GitHub issue URL. Findings classify as GAP / SCOPE-ADD / DECISION-OVERRIDE / CONSISTENT |
| `--verify-build` | Run build verification on sub-80 axis findings BEFORE Haiku validators (Phase 3.5). Builds + runs the test command detected by `scripts/build_detect.py`; confirmed findings get promoted (+30 confidence) and skip the validator phase |
| `--mutation-test` | Run Stryker (JS/TS), Pitest (JVM), or mutmut (Python) on changed files only. Surviving mutants route to the Tests axis as 🟠 Medium |
| `--apply-safe` | Opt-in writers: auto-apply low-risk fixes (manifest version sync, structured-field description sync with full-agreement guard, one failing test per confirmed bug). Diff preview + per-file confirmation before any write |
| `--include-prose` | Coherence axis compares README freeform paragraphs as well (default: structured fields only) |
| `--axes <list>` | Comma-separated subset of axes to run (e.g. `correctness,tests`). Default: all 8 + Coherence when triggered |
| `--preflight` | List detected tools per repo_kind + print install commands for missing ones. Informational only, no install |

Lowercase enables, uppercase disables. No `-f` — this skill is a producer, not a consumer.

```bash
/code-ultrareview                              # full 8-axis review, print report
/code-ultrareview -s                           # save the report + JSONL for /apex -f
/code-ultrareview -b origin/main               # review HEAD against an explicit base
/code-ultrareview --verify-build               # promote sub-80 findings via real build verification
/code-ultrareview --reconcile @auto            # add Intent derivation sub-mode with auto-detect
/code-ultrareview --apply-safe                 # full review + gated low-risk fixes
/code-ultrareview --preflight                  # list tools the battery would run, no review
/code-ultrareview --axes correctness,tests     # subset of axes
```

## The five phases

### Phase 1 — Scope

Runs `scripts/scope.py`. Deterministic, no LLM. Outputs `scope.json`:

- **Diff resolution** — clean tree → `scripts/resolve_base.sh` ladder; dirty tree → `git diff HEAD` + every untracked file inlined as added lines.
- **Repo-kind classification** — 8 kinds (`skills` / `app` / `library` / `docs` / `monorepo` / `python` / `rust` / `go`) + `unknown`. Override via `--repo-kind` or `.code-ultrareview.yaml`.
- **CLAUDE.md chain** — root `CLAUDE.md` + nested `CLAUDE.md` in changed directories + `.claude/rules/*.md` + `~/.claude/rules/*.md`. Ordered root-to-deepest. Read by axis reviewers and validators.
- **Coherence activation** — any of `package.json`, `.claude-plugin/marketplace.json`, `marketplace.json`, `SKILL.md`, root `README.md`, `tsconfig.json`, `pyproject.toml`, `Cargo.toml`, `go.mod` in the diff → `scope.json["activates_coherence"] = true`.
- **Languages detection** — from changed-file extensions; drives Phase 2 dispatch.

The output also feeds the report header lines `Repo: <kind>`, `Base: <ref>`, `Files: <N>`.

### Phase 2 — Tool battery

Runs `scripts/run_battery.sh` (WS-2). Deterministic CLIs feed `tool-findings.jsonl` tagged by axis with `confidence: 100`. Tools dispatched per `scope.json["languages"]`:

- **JS/TS** — `npx knip` (dead code), `npx jscpd` (duplication), `npx markdownlint-cli2`, optional `npx @microsoft/api-extractor`.
- **Python** — `uvx lizard` (complexity), `uvx vulture` (dead code), `uvx semgrep --config=auto`, `npx jscpd` (cross-language).
- **Go** — `deadcode`, `gocyclo`, `dupl`, `npx jscpd`, `uvx lizard`.
- **Rust** — `cargo-machete`, `npx jscpd`, `uvx lizard -l rust`.
- **Universal** — `uvx semgrep` with bundled `references/perf-rules/` (N+1 and sync-I/O rules).
- **API** — `oasdiff` when an OpenAPI file appears in the diff.
- **DB** — `atlas migrate lint` when `migrations/` appears in the diff.
- **Prose** — `uvx vale` when `.vale.ini` is present.

Per-tool axis routing lives in `scripts/battery_ingest.py` (WS-2).

**Graceful skip.** Missing tools (no `npx`, no `uvx`, no PATH binary) emit `WARN: <tool> not found — install: <command>` to stderr and append to `scope.json["tools_skipped"]`. The skill continues. The battery NEVER auto-installs — no `brew install`, no `cargo install`, no `go install`, no `pip install`, no `npm install -g`.

### Phase 3 — Axis review

The orchestrator (main thread) prepares 8 per-axis bundles + 1 conditional Coherence bundle via `scripts/axis_dispatch.py prepare`, then launches every bundle as a parallel `Explore` subagent in one message. Subagents cannot spawn other subagents — the main thread always launches both axis reviewers AND validators.

```bash
python3 scripts/axis_dispatch.py prepare \
  --scope <scope.json> \
  --findings <tool-findings.jsonl> \
  --diff <diff.patch> \
  --output-dir <run-dir>
```

The script emits a JSON map `{axis: {input_path, prompt_path, findings_count}}`. The orchestrator reads each axis's `prompt_path`, then fans out one `Task` call per axis in the same message.

Each subagent receives via its bundle (`axis-input/{axis}.json`):

- `scope` — repo kind, languages, CLAUDE.md chain, files touched.
- `findings` — tool findings filtered to its own axis only (`scripts/battery_ingest.py` axis routing). Other axes' findings are excluded so the subagent's context stays lean.
- `diff_text` — the diff itself.
- `brief_path` — its axis brief at `references/axes/{axis}.md`.
- `anthropic_verbatim_path` — `references/anthropic-verbatim.md` carrying the 0-100 rubric, HIGH SIGNAL criteria, false-positive taxonomy, and agent-assumption rule.

Each subagent emits findings as JSONL on stdout, one finding per line, against the canonical schema (`axis`, `severity`, `location`, `finding`, `recommendation`, `confidence`).

| # | Axis | Scope | Brief |
|---|------|-------|-------|
| 1 | Correctness | Bugs, logic errors, type errors, regressions, unhandled edges | `references/axes/correctness.md` |
| 2 | Simplification | Over-engineering, single-use abstractions, dead-code judgment, nested ternaries | `references/axes/simplification.md` |
| 3 | Tests | Coverage of changed lines, test smells, weak assertions, strictness flags | `references/axes/tests.md` |
| 4 | Documentation | Public API docs, README drift, ADR drift, prose hygiene | `references/axes/documentation.md` |
| 5 | Style | CLAUDE.md violations, linter-deferred concerns | `references/axes/style.md` |
| 6 | Intent | PR description vs diff, code vs comment drift, lockfile drift, optional `--reconcile` | `references/axes/intent.md` |
| 7 | Design/API | Public API breaking, DB schema breaking, race conditions | `references/axes/design-api.md` |
| 8 | Performance | N+1 patterns, sync I/O in async, bundle-size delta | `references/axes/performance.md` |

**Conditional 9th — Coherence.** `references/axes/coherence.md`. `axis_dispatch.prepare` adds it to the bundle list when `scope.json["activates_coherence"]` is true (still within the soft 10-parallel concurrency cap). When inactive, the report header surfaces `Coherence axis: inactive`.

**No silent failure.** If any axis subagent returns no output (timeout, error, malformed JSON), the orchestrator emits a 🔴 High finding for that axis citing the failure mode — never a silent skip.

Full axis map and inter-axis precedence: `references/axes-overview.md`.

### Phase 4 — Validation

The orchestrator (main thread) prepares per-finding validator bundles via `scripts/run_validators.py prepare`, then launches one Haiku `Task` per finding in the same message — batched ≤10 parallel. Each validator receives the finding + diff context + the deepest matching CLAUDE.md snippet + the verbatim rubric.

```bash
python3 scripts/run_validators.py prepare \
  --scope <scope.json> \
  --findings <axis-findings.jsonl> \
  --diff <diff.patch> \
  --output-dir <run-dir>
```

The script emits `{count, batches: [[idx, ...], ...], bundles: {idx: {input_path, prompt_path}}}`. The orchestrator reads each batch's `prompt_path`, fans out one `Task` per index in one message, collects stdout as `{index, score, reason}` lines, then runs `scripts/run_validators.py ingest` to apply A2-preserving promote/demote logic on top of `scripts/synthesis_core.py` primitives.

Each validator:

1. Re-scores 0-100 against the verbatim rubric.
2. Re-checks that the cited CLAUDE.md rule actually exists in `claude_md_chain`. Demotes with explicit reason if not found (`CLAUDE.md rule not found at <path>`).
3. Stays read-only — no Write/Edit/Bash, no nested subagent spawn.

Confidence threshold = 80 (`scripts/synthesis_core.py:CONFIDENCE_THRESHOLD`). Tool-battery findings (confidence 100) skip the validator phase — they are deterministic.

**A2 contract.** No sub-80 finding silently dropped. Each one is promoted to ≥80, demoted with reason, or surfaced in `### ⚠️ Unverified` with the validator's reason text.

**Phase 3.5 — `--verify-build`.** Build verification runs BEFORE validators. Confirmed findings get +30 confidence (capped at 95, floor at the 80 threshold) and skip the validator phase. Implementation: `scripts/build_detect.py` returns the canonical test command; the loop runs one iteration per sub-80 finding.

### Phase 5 — Synthesis

Runs `scripts/synthesize.py` (WS-5) on top of `scripts/synthesis_core.py` primitives:

1. **Dedup** by `(file, line_range, finding_hash)`.
2. **Inter-axis precedence** — when 2+ axes flag the same `file:line`, highest severity wins; ties resolve via `Correctness > Design/API > Simplification > Tests > Documentation > Style > Intent > Performance > Coherence` (`scripts/synthesis_core.py:AXIS_PRIORITY`).
3. **A2 routing** — sub-80 stays in Unverified with the validator's reason.
4. **Verdict** — `Ship` / `Fix-then-ship` / `Needs work` (`scripts/synthesis_core.py:compute_verdict`).
5. **Report emission** — markdown to terminal + `~/.claude/output/{project}/code-ultrareview/code-ultrareview-{slug}.md`. JSONL alongside with Conventional Comments labels (`issue` / `suggestion` / `nitpick` / `question`).

The closing **"What I did NOT check"** section is mandatory and always present, even when nothing was skipped — it lists security (defers to `/security-review`), runtime performance / benchmarks (explicit non-goal), flaky test detection (explicit non-goal), and any tools from `scope.json["tools_skipped"]`.

## Final report layout

The template at `templates/code-ultrareview.md` is the canonical wire format — every `##` section renders verbatim in template order with its emoji prefix; section names are not rewritten, merged, or reordered.

**Terminal echo is mandatory.** The full canonical report prints to the chat-terminal on every invocation. The `-s` flag is purely additive: it writes the same bytes to `~/.claude/output/{project}/code-ultrareview/code-ultrareview-{slug}.md` — terminal output and saved file are byte-for-byte identical. Severity marker mapping (🔴 High blocks ship · 🟠 Medium fix-soon · 🟢 Low nit · ⚠️ Unverified sub-80) and the dict-key schema live in `scripts/synthesis_core.py:SEVERITY_MARKERS`.

No section beyond the template's list — improvised headings like `Dropped`, `Per-ask verification`, or `Debug` are out of contract; debug data stays out of the user-facing report by design.

## Trust model

This skill ingests third-party content: CLAUDE.md files, PR bodies (`--reconcile @pr`), external planning artifacts (`--reconcile <path>`), GitHub issue bodies. These can carry indirect prompt-injection attempts.

- Axis reviewers and validators are read-only — no Write/Edit/Bash mutation beyond the controlled scope.
- The synthesis phase emits the report; user review is the trust boundary before any `--apply-safe` write.
- `--apply-safe` writes go through diff preview + per-file confirmation. No silent modifications.

## Rules

- **Only new findings.** Issues the diff introduces, not pre-existing ones. Pre-existing findings carry the `Pre-existing` tier for context but never flip the verdict.
- **No silent drop (A2).** Sub-80 findings surface in `### ⚠️ Unverified` with the rationale `Sub-80 confidence ({score}) — verify locally before action.` Never omitted.
- **Fail loud.** A phase that cannot run (unresolvable base, missing tool with no graceful skip path, dependency failure) is stated in the header or surfaced as a finding. Never silently skipped.
- **Cite precisely.** Every finding carries `file:line`; CLAUDE.md findings quote the violated rule verbatim; permalinks use `https://github.com/<owner>/<repo>/blob/<full-sha>/<path>#L<n>-L<m>` with the full SHA resolved via `git rev-parse HEAD`.
- **Full report in chat every time.** Print the complete report — header + every section + every finding — to the terminal on every invocation. `-s` is additive: it writes the same bytes to disk; it does NOT gate, truncate, or summarize the chat output.
- **NEVER auto-install tools.** Missing native tools surface install commands in the report and `scope.json["tools_skipped"]`. The user installs them.
- **NEVER modify code without `--apply-safe`.** Default is read-only review. `--apply-safe` writers are surgical and per-file confirmed.

## Deferrals

The closing "What I did NOT check" section always names these — explicit user-facing calibration of coverage:

- **Security** → `/security-review` or Anthropic's `claude-code-security-review`. Security is a distinct concern with its own deeper review pattern.
- **Runtime performance / benchmarks** → not covered. The Performance axis catches static patterns (N+1, sync I/O) but not runtime profiling.
- **Flaky test detection** → not covered. The Tests axis catches structural smells, not flake.
- **Tools from `scope.json["tools_skipped"]`** → listed explicitly so the user sees what they sacrificed by not installing the native binaries.

## Graceful degradation

- **No CLAUDE.md / no `.claude/rules`** — Style axis runs without baseline; the report says `Style axis: skipped — no rules baseline found`.
- **No `npx` / no `uvx`** — every wrappable tool skips; only PATH binaries run.
- **Missing native binary** (`oasdiff`, `atlas`, `cargo-machete`, Go tools) — emits to stderr + `scope.json["tools_skipped"]`. The relevant axis loses its tool input but still runs LLM judgment.
- **Unresolvable base** — fail loud with the resolver's hint line. Do not guess.
- **Unknown repo_kind** — axes run with their `unknown` branch (no specialization).
- **Coherence inactive** — when no metadata files change, the 9th axis simply does not launch. The report header says `Coherence axis: inactive` so the absence is visible.

## Composition

After the report ships, bridge to the fix pass:

- `/apex -f ~/.claude/output/{project}/code-ultrareview/code-ultrareview-{slug}.md` — structured fix pass (requires `-s`; pass the absolute path the report prints).
- `/oneshot "<finding>"` — single-finding quick fix (manual; `/oneshot` takes a description, not a file).

## What this skill is NOT

- **Not a security audit.** Defers to `/security-review`. The closing section makes this explicit on every report.
- **Not a linter or formatter.** The deterministic tool battery (npx/uvx-wrapped CLIs) handles linting and dead-code detection. The skill layers LLM judgment on top of those signals.
- **Not Anthropic's remote `/ultrareview`.** Distinct surface — this skill runs in-session on the user's subscription; `/ultrareview` runs in a remote sandbox and bills per run.
- **Not a fix tool.** Report-only by default. `--apply-safe` covers three surgical writers; everything else routes to `/apex` or `/oneshot`.

## References

- `references/anthropic-verbatim.md` — verbatim rubric, HIGH SIGNAL criteria, false-positive taxonomy, agent-assumption rule.
- `references/axes-overview.md` — 8 axes + Coherence conditional + inter-axis precedence rule.
- `references/axes/<name>.md` — per-axis briefs (WS-3, one file per axis).
- `scripts/scope.py` — Phase 1 deterministic scope output.
- `scripts/synthesis_core.py` — A2 routing + severity markers + verdict algorithm.
- `scripts/resolve_base.sh` — clean-tree base resolution ladder.
- `scripts/build_detect.py` — gated by `--verify-build`; detects the canonical test command per repo type.

## Gotchas

1. **Sub-80 findings can be dropped instead of surfaced in `### ⚠️ Unverified`.** The A2 contract (`scripts/synthesis_core.py:apply_a2`) is no-silent-drop. The model sometimes treats a sub-80 score as a rejection signal and omits the finding entirely. Fix: scan the `### ⚠️ Unverified` section explicitly on every report; compare finding count to axis output to catch drops.
2. **First-run `npx` / `uvx` downloads add latency.** Cold start adds ~5s per tool the first time the battery touches it; subsequent runs are fast (cached at `~/.npm/_npx` / `~/.cache/uv`). The README install table documents this so users don't fear repeated downloads.
3. **Coherence activates silently on metadata changes.** A single `package.json` touch triggers the 9th subagent automatically. Watch for the `Coherence axis: active` line in the report header — it tells you the axis ran without you asking.
4. **`--reconcile @auto` skips silently on malformed planning artifacts.** A forge or apex file with broken YAML frontmatter (unclosed `---`, tab indentation, unquoted colons) is dropped from the auto-detect list. Verify with `head -20 ~/.claude/output/{project}/forge/forge-*.md` before relying on `@auto`.
