---
name: code-ultrareview
description: Eight-axis judgment code review for the current diff — Correctness, Simplification, Tests, Documentation, Style, Intent, Design/API, Performance (+ Coherence on metadata changes). Five-phase pipeline scope → atomic deterministic tool battery (project-declared or installed PATH tools; no runtime package resolution) → 8 parallel LLM axis reviewers → fresh-context validators on sub-80 findings (verbatim rubric, ≥80 threshold) → synthesis with no-silent-drop + Conventional Comments JSONL. Missing or failed applicable analyzers block before a verdict and print exact remediation. Every report closes with "What I did NOT check" (security → /security-review, runtime perf, flaky detection). Opt-in flags `--verify-build`, `--mutation-test`, `--reconcile`, `--apply-safe`. Invoke before a commit or PR — "review my changes", "deep review", "did I miss anything", "check before I commit", "audit this PR", "drift / gaps / blind spots".
license: MIT
compatibility: "Optimized for Claude Code; degrades gracefully on any agent implementing the Agent Skills standard."
allowed-tools: Read Grep Glob Bash Task WebFetch
metadata:
  author: coroboros
  sources:
    - github.com/anthropics/claude-plugins-official/tree/main/plugins/code-review
    - github.com/anthropics/claude-plugins-official/tree/main/plugins/code-simplifier
    - code.claude.com/docs/en/code-review
    - code.claude.com/docs/en/ultrareview
    - github.com/mattpocock/skills/tree/main/skills/engineering/improve-codebase-architecture
---

# Code ultrareview

<!-- canonical:adversarial-verification:start -->
## Critical — Adversarial verification

These rules govern how this skill trusts its own output — apply them whenever it verifies a claim, a defect, a source, or a decision before acting on it.

- Refute by default. Treat each non-trivial finding as unproven until a fresh-context check fails to refute it — the context that produced a claim cannot reliably clear it.
- No silent drop. Every finding flips the conclusion, is refuted in writing, or is filed as a risk or open question. A finding that vanishes without a verdict is a defect.
- Don't re-litigate settled facts. Spend adversarial effort on load-bearing or contested claims; let established facts pass. Over-refutation manufactures false doubt — it does not add rigor.
- Stay selective and cost-aware. Scale verification to the stakes; reversible, low-impact work gets a light touch, not a full adversarial sweep.
- Concede only to a strong rebuttal. A weak counter folds into the finding or gets filed; it does not overturn it.
<!-- canonical:adversarial-verification:end -->

<!-- canonical:execution-discipline:start -->
## Important — Engineering discipline

These rules govern how this skill changes code — apply them whenever it writes, edits, or proposes a fix.

- Minimal scope. Only what's directly requested or clearly necessary — no extra files, no abstraction for one use, no configurability nobody asked for, no error handling for states that can't happen. Validate at system boundaries; trust internal code.
- General solution, not the test cases. Implement the real logic for all valid inputs; never hard-code to inputs or bolt on workaround scripts to make a test pass. Tests verify the solution; they don't define it. A test is wrong? Say so — don't bend correct code to a broken test.
- Investigate before claiming. Never speculate about code you haven't opened; read the referenced file before answering. Ground every claim in what you actually read, not a plausible guess.
<!-- canonical:execution-discipline:end -->

<!-- canonical:label-hygiene:start -->
## Critical — Label hygiene

Internal planning labels are author coordinates, not reader coordinates. Strip them from every shipped artifact this skill emits — code, comments, commit subjects/bodies, PR titles/descriptions, release notes, doc paragraphs, non-trivial comments.

- **Workstream and task labels** — `WS-N`, `Phase-A`, `Step-3`, issue or ticket numbers, plan phase names from the source spec, issue body, or planning artifact. Translate to the domain noun (`Runs the battery script (WS-2)` → `Runs the battery script`). <!-- noqa: internal-label -->
- **Process language** — "the rebuild", "the prior `<file>`", "carried verbatim from", "the cleanup pass", "the audit", "spec AC" standalone. Replace with the concrete fact (`carries the routing from the prior aggregation` → `routes via the merge keys in the synthesis module`). <!-- noqa: internal-label -->
- **Plan-internal references** — "as the brief says", "per the workstream", "from the forge artifact". Drop the reference; state the fact directly.

Carve-outs — literal `WS-N` is legitimate where the skill IS the format authority (forge templates, apex rule documentation). Reviewer-facing dev docs (e.g. `MIGRATION.md` under `tests/<skill>/`) may reference deleted artifacts by their author-time names.
<!-- canonical:label-hygiene:end -->

> **Eight-axis judgment code review.** Five-phase pipeline scope → tool battery → 8 parallel axis reviewers → fresh-context validators → synthesis. The default runs at full strength — every axis, full applicable battery, no sampling; `--axes` is an explicitly scoped review with no repository verdict. Distinct from Anthropic's remote `/ultrareview` — same goal, in-session on the user's subscription.

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

By default, run the 8 axes — Correctness, Simplification, Tests, Documentation, Style, Intent, Design/API, Performance — as 8 parallel LLM subagents fed by deterministic tool findings from `scripts/run_battery.sh`. Coherence joins as a 9th axis when metadata files change. Sub-80 axis findings get re-scored by fresh-context validators (Haiku on Claude Code) against the verbatim rubric in `references/anthropic-verbatim.md`. Findings synthesize into one report with deterministic dedup, inter-axis precedence, A2 no-silent-drop, and a verdict (Ship / Fix-then-ship / Needs work). The report ends with "What I did NOT check" so the coverage limits are explicit. `--axes` intentionally narrows both analyzers and LLM review and emits scoped findings without a repository verdict.

## Parameters

| Flag | Behavior |
|------|----------|
| `-s` | Save the report + JSONL to `~/.agents/output/{project}/code-ultrareview/code-ultrareview-{slug}.{md,jsonl}` |
| `-S` | Force no-save (overrides any ambient save mode) |
| `-b <ref>` | Override the review base (skip auto-detection via `scripts/resolve_base.sh`) |
| `--repo-kind <kind>` | Override the scope classifier. Values: `skills`, `app`, `library`, `docs`, `monorepo`, `python`, `rust`, `go`, `unknown`. Persistent per-repo override at `.code-ultrareview.yaml` (`repo_kind: <kind>`); the flag wins on conflict. Invalid value exits 2 |
| `--reconcile <input>` | Activate the Intent-axis derivation sub-mode. `<input>` may be `@auto`, `@pr`, an explicit path or directory, `gh:pr:<N>`, `gh:issue:<owner>/<repo>#<N>`, or a GitHub issue URL. Findings classify as GAP / SCOPE-ADD / DECISION-OVERRIDE / CONSISTENT |
| `--verify-build` | Run the repository's canonical test command as an atomic gate before fresh-context validators. Missing command/runner exits 3; failure or timeout exits 4. A generic build result never changes finding confidence |
| `--mutation-test` | Run Stryker (JS/TS), Pitest (JVM), or mutmut (Python). JS/TS execution targets changed files; project-configured Python/JVM execution is filtered to changed-file findings. Surviving mutants route to the Tests axis as 🟠 Medium |
| `--apply-safe` | Opt-in writers: auto-apply low-risk fixes (manifest version sync, structured-field description sync with full-agreement guard, one failing test per confirmed bug). Diff preview + per-file confirmation before any write |
| `--include-prose` | Coherence axis compares README freeform paragraphs as well (default: structured fields only) |
| `--axes <list>` | Comma-separated subset of axes to run (e.g. `correctness,tests`). Produces scoped findings only, never a repository-wide Ship / Fix-then-ship / Needs work verdict. Default: all 8 + Coherence when triggered |
| `--preflight` | Runs `scripts/preflight_tools.sh --scope <scope.json>` — validates applicable analyzers and prints exact install commands for missing ones. Exits 3 when coverage is incomplete; never installs |

Lowercase enables, uppercase disables. No `-f` — this skill is a producer, not a consumer.

```bash
/code-ultrareview                              # full 8-axis review, print report
/code-ultrareview -s                           # save the report + JSONL for /apex -f
/code-ultrareview -b origin/main               # review HEAD against an explicit base
/code-ultrareview --verify-build               # require the canonical project test gate to pass
/code-ultrareview --mutation-test              # require configured mutation coverage on changed code
/code-ultrareview --reconcile @auto            # add Intent derivation sub-mode with auto-detect
/code-ultrareview --apply-safe                 # full review + gated low-risk fixes
/code-ultrareview --preflight                  # list tools the battery would run, no review
/code-ultrareview --axes correctness,tests     # subset of axes
```

## The five phases

### Phase 1 — Scope

Runs `scripts/scope.py`. Deterministic, no LLM. Outputs `scope.json`:

- **Diff resolution** — clean tree → `scripts/resolve_base.sh` ladder; dirty tree → `git diff HEAD` + every untracked file inlined as added lines. `changed_line_ranges` records the target-side added/modified hunks for deterministic finding scope. Recipe for producing the `diff.patch` fed to Phase 3's `prepare --diff` (two-dot against the resolved base; untracked files via `git diff --no-index /dev/null <file>`): `references/orchestration.md` § *Produce the diff*.
- **Repo-kind classification** — 8 kinds (`skills` / `app` / `library` / `docs` / `monorepo` / `python` / `rust` / `go`) + `unknown`. Override via `--repo-kind` or `.code-ultrareview.yaml`.
- **Instruction chain** — effective `AGENTS.override.md` / `AGENTS.md`, the shared `.agents/rules/**/*.md` they reference, and Claude-specific `CLAUDE.md` / `.claude/CLAUDE.md` / `CLAUDE.local.md` / `.claude/rules/**/*.md` across user, project, and changed-directory scopes. Ordered broadest-to-most-specific in `scope.json["instruction_chain"]`. Read by axis reviewers and validators.
- **Coherence activation** — any of `package.json`, `.claude-plugin/marketplace.json`, `marketplace.json`, `SKILL.md`, root `README.md`, `tsconfig.json`, `pyproject.toml`, `Cargo.toml`, `go.mod` in the diff → `scope.json["activates_coherence"] = true`.
- **Languages detection** — from changed-file extensions; drives Phase 2 dispatch.

The output also feeds the report header lines `Repo: <kind>`, `Base: <ref>`, `Files: <N>`.

### Phase 2 — Tool battery

Runs `scripts/run_battery.sh`. Deterministic CLIs feed `tool-findings.jsonl` tagged by axis with `confidence: 100`. Tools dispatch by changed files, detected languages, selected axes, and tool-specific config; line-aware reports are filtered to target-side changed hunks, while manifest/API analyzers remain path-scoped. JavaScript tools (`knip` / `jscpd` / `markdownlint-cli2` / `@microsoft/api-extractor`) prefer the repository's directly declared `node_modules/.bin`, support directly declared Yarn Plug'n'Play binaries through `yarn run -B`, then check `PATH`; Python and native tools use `PATH`. The battery never invokes a package resolver. Bundled `references/perf-rules/` carries the universal N+1 and sync-I/O semgrep rules. Markdownlint uses a project-overridable neutral base: no arbitrary line-length limit and compact table spacing instead of fixed-width visual alignment. `jscpd` reports structural clones at 15 lines / 100 tokens by default; `JSCPD_MIN_LINES` and `JSCPD_MIN_TOKENS` can make a run stricter. Per-tool axis routing lives in `scripts/battery_ingest.py`. Full Tool → Axis table in `README.md`.

**Atomic preflight.** The battery resolves every analyzer applicable to the selected scope before running the first one. At run start it marks `scope.json["tool_coverage"]` incomplete and removes any prior public findings; new findings stay private until every report validates. A missing analyzer exits 3, records `tool-preflight.json` plus `scope.json["tools_missing"]`, and prints its exact project-aware install command plus the exact script command that preserves the current arguments for the rerun. An analyzer runtime or invalid-report failure exits 4 with repair guidance and the same exact rerun command. In both cases, stop: do not launch axis reviewers and do not emit a verdict. The battery NEVER installs or resolves packages.

**Phase 2 extension — `--mutation-test`.** `scripts/run_mutation.sh` preflights every applicable language before starting any mutation process. Stryker targets changed JS/TS files. mutmut and Pitest execute the project's declared mutation scope, then emit surviving, uncovered, or suspicious results only for changed Python/JVM files. Findings stage in a private file and publish only after every applicable language succeeds. Missing tool or project config exits 3 with exact remediation; runtime, timeout, empty-evaluation, incomplete, or malformed-report failure exits 4. The script persists `scope.json["mutation_coverage"]`; Phase 3 and synthesis reject incomplete requested coverage even if a caller ignores the exit code. Mutation findings route to the Tests axis as 🟠 Medium with `confidence: 100` (skips Phase 4 validators). Default timeout is 600 s, overridable via `MUTATION_TIMEOUT`. Details: `references/ultra-execution.md`.

### Phase 3 — Axis review

The orchestrator prepares 8 per-axis bundles (+ Coherence when active) via `scripts/axis_dispatch.py prepare`, then launches every bundle as a parallel `Explore` `Task` (or your harness's equivalent) in one message. Each subagent reads its axis brief, the rubric in `references/anthropic-verbatim.md`, the diff, and its filtered tool findings. Each emits canonical-schema JSONL on stdout. Prepare and ingest invalidate prior axis/validator coverage before work; ingest publishes merged findings only after every requested result validates. Subagents cannot spawn other subagents — the main thread launches both axis reviewers AND validators. No subagent primitive in the harness? Run the axes sequentially and adversarially self-refute each finding in a fresh pass against the verbatim rubric before reporting — same phases, same contracts, no fan-out.

The 8 always-on axes: **Correctness** · **Simplification** · **Tests** · **Documentation** · **Style** · **Intent** · **Design/API** · **Performance**. Each maps to `references/axes/<name>.md` for scope + repo-kind branches. Coherence is the conditional 9th — added when `scope.json["activates_coherence"]` is true; when inactive, the header surfaces `Coherence axis: inactive` so the absence is visible. Full axis map, inter-axis precedence, and orchestration details (prepare CLI, bundle schema, no-silent-failure contract): `references/axes-overview.md` + `references/orchestration.md`.

### Phase 4 — Validation

The orchestrator prepares per-finding validator bundles via `scripts/run_validators.py prepare`, then launches one fresh-context validator per finding in the same message — Haiku `Task` on Claude Code, or the harness's isolated-agent equivalent — batched ≤10 parallel. Prepare requires complete axis coverage. Validator ingest invalidates any prior successful state and output before validating the exact prepared count, then publishes atomically. Each validator receives the finding + diff context + the deepest applicable instruction snippet + the verbatim rubric, re-scores 0-100, and re-checks that a cited project rule exists in `instruction_chain` (demotes with `Instruction rule not found at <path>` if not). Confidence `0` is valid and must pass through this validation path. Without an isolated-agent primitive, validate sequentially in a fresh pass and keep the same ingest and no-silent-drop contracts.

Confidence threshold = 80 (`scripts/synthesis_core.py:CONFIDENCE_THRESHOLD`). Tool-battery findings (confidence 100) skip the validator phase — they are deterministic. Validators stay read-only — no Write / Edit / Bash, no nested subagent spawn.

**Typical runtime.** 5-15 sub-80 findings → one batch → ~30-60s. 25+ findings spread over 2-3 batches stay under ~2 min. Latency is dominated by isolated-validator launch overhead, not inference.

**A2 contract.** No sub-80 finding silently dropped. Each one is promoted to ≥80, demoted with reason, or surfaced in `### ⚠️ Unverified` with the validator's reason text.

Validator prepare CLI, bundle schema, ingest pass details: `references/orchestration.md`.

**Phase 3.5 — `--verify-build`.** `scripts/run_build_verify.py` marks build coverage incomplete and removes prior build artifacts before it reads the current findings, then detects and runs the repository's canonical test command before validators whenever the flag is requested. It never treats a generic failure as proof of a specific finding and never changes confidence. JavaScript repositories qualify only when `package.json` declares a non-empty `scripts.test`; Python qualifies only through declared pytest configuration/dependencies or a collectable unittest suite. The detector never invents a test command from a manifest alone. Missing command/runner exits 3 with project-aware install guidance; a missing/malformed input, failed command, zero-test suite, timeout, or execution error exits 4. Every blocked path prints the exact command to rerun and prevents synthesis. Details: `references/orchestration.md`.

### Phase 5 — Synthesis

Runs `scripts/synthesize.py` on top of `scripts/synthesis_core.py` primitives:

1. **Dedup** by `(location, finding-text)`.
2. **Inter-axis precedence** — when 2+ axes flag the same `file:line` with the same finding wording, highest severity wins; ties resolve via `Correctness > Design/API > Simplification > Tests > Documentation > Style > Intent > Performance > Coherence` (`scripts/synthesis_core.py:AXIS_PRIORITY`). Distinct findings at coincident lines (a Correctness null-deref and a Tests missing-assert on the same line) survive as separate entries.
3. **A2 routing** — sub-80 stays in Unverified with the validator's reason.
4. **Verdict** — `Ship` / `Fix-then-ship` / `Needs work` (`scripts/synthesis_core.py:compute_verdict`).
5. **Report emission** — markdown to terminal + `~/.agents/output/{project}/code-ultrareview/code-ultrareview-{slug}.md`. JSONL alongside with Conventional Comments labels (`issue` / `suggestion` / `nitpick` / `question`).

The closing **"What I did NOT check"** section is mandatory and always present — it lists security (defers to `/security-review`), runtime performance / benchmarks (explicit non-goal), and flaky test detection (explicit non-goal). Missing applicable analyzers never reach synthesis.

## Final report layout

`templates/code-ultrareview.md` is the canonical wire format — every `##` section renders verbatim in template order with its emoji prefix; no rename, merge, reorder, or improvise. **Terminal echo is mandatory** — the full canonical report prints to the chat-terminal on every invocation; `-s` is purely additive (writes the same bytes to `~/.agents/output/{project}/code-ultrareview/code-ultrareview-{slug}.md`, byte-for-byte identical to terminal output). Severity marker mapping (🔴 High blocks ship · 🟠 Medium fix-soon · 🟢 Low nit · ⚠️ Unverified sub-80) lives in `scripts/synthesize.py:SEVERITY_MARKERS`.

## Trust model

The skill ingests third-party content — project instruction files, PR bodies, planning artifacts (`--reconcile`), GitHub issue bodies — which can carry indirect prompt-injection. Axis reviewers and validators are read-only (no Write / Edit / Bash mutation). User review of the report is the trust boundary before any `--apply-safe` write; `--apply-safe` itself gates writes behind diff preview + per-file confirmation.

## Rules

- **Only new findings.** Issues the diff introduces. Pre-existing findings carry the `Pre-existing` tier for context, never flip the verdict.
- **No silent drop (A2).** Positive sub-80 findings surface in `### ⚠️ Unverified` with the score and validator reason. Validator score `0` rejects the finding during synthesis.
- **Fail loud.** An unresolvable base, missing prerequisite, analyzer failure, or invalid report stops the review before a verdict.
- **Cite precisely.** Every finding carries `file:line`; instruction-rule findings quote the violated rule verbatim and name its source file; permalinks use `https://github.com/<owner>/<repo>/blob/<full-sha>/<path>#L<n>-L<m>` (full SHA via `git rev-parse HEAD`).
- **Full report in chat every time.** The complete report prints to the terminal on every invocation. `-s` writes the same bytes to disk; it never gates or summarises chat output.
- **NEVER auto-install tools.** Missing tools surface exact install commands in preflight stderr and `tool-preflight.json`. The user installs them, then reruns the review.
- **NEVER modify code without `--apply-safe`.** Default is read-only review. `--apply-safe` writers are surgical and per-file confirmed.

## Deferrals

The closing "What I did NOT check" section always names these — explicit user-facing calibration of coverage:

- **Security** → `/security-review` or Anthropic's `claude-code-security-review`. Security is a distinct concern with its own deeper review pattern.
- **Runtime performance / benchmarks** → not covered. The Performance axis catches static patterns (N+1, sync I/O) but not runtime profiling.
- **Flaky test detection** → not covered. The Tests axis catches structural smells, not flake.

## Degradation and hard stops

- **No project instruction chain** — when no effective AGENTS or Claude instruction file exists, Style still runs but may report only changed-line violations backed by repeated observable neighboring repository evidence. The report states that no project-specific rules baseline was available; Style is not marked skipped.
- **No project or PATH analyzer** — hard stop with exit 3 and an exact install command. A generic manual code review is a different workflow; it must not claim this skill's full-strength verdict.
- **Analyzer runtime, timeout, analyzer-reported error, or invalid report** — hard stop with exit 4, captured stderr/report paths, exact repair/install guidance, and a rerun instruction.
- **Unresolvable base** — fail loud with the resolver's hint line. Do not guess.
- **Unknown repo_kind** — axes run with their `unknown` branch (no specialization).
- **Coherence inactive** — when no metadata files change, the 9th axis simply does not launch. The report header says `Coherence axis: inactive` so the absence is visible.

## Composition

Bridge to the fix pass after the report ships:

- `/apex -f ~/.agents/output/{project}/code-ultrareview/code-ultrareview-{slug}.md` — structured fix pass (requires `-s`; pass the absolute path the report prints).
- `/oneshot "<finding>"` — single-finding quick fix (takes a description, not a file).

### Opt-in flag composition

The four opt-in flags layer orthogonally on the always-on pipeline: mutation tests feed the Tests axis and final synthesis through their own run manifest; `--verify-build` adds Phase 3.5; `--reconcile` enriches the Intent axis in Phase 3; `--apply-safe` writers run post-synthesis with diff preview + per-file confirmation. Without a flag, its feature is off. Full composition matrix and per-flag details: `references/ultra-execution.md`.

## What this skill is NOT

- **Not a security audit.** Defers to `/security-review`. The closing section makes this explicit on every report.
- **Not a linter or formatter.** The deterministic tool battery handles linting and dead-code detection through declared or installed CLIs. The skill layers LLM judgment on top of those signals.
- **Not Anthropic's remote `/ultrareview`.** Distinct surface — this skill runs in-session on the user's subscription; `/ultrareview` runs in a remote sandbox and bills per run.
- **Not a fix tool.** Report-only by default. `--apply-safe` covers three surgical writers; everything else routes to `/apex` or `/oneshot`.

## References

- **Reviewer primitives** — `references/anthropic-verbatim.md` (rubric + HIGH SIGNAL + false-positive taxonomy), `references/axes-overview.md` (8 axes + Coherence + inter-axis precedence), `references/axes/<name>.md` (per-axis briefs), `references/orchestration.md` (Phase 3 + 4 + 3.5 prepare CLIs and bundle schemas).
- **Opt-in flags** — `references/ultra-execution.md` covers `--verify-build`, `--mutation-test`, `--reconcile`, `--apply-safe` in full.
- **Scripts** — `scope.py` (Phase 1), `run_battery.sh` + `battery_ingest.py` (Phase 2), `axis_dispatch.py` (Phase 3), `run_validators.py` (Phase 4), `synthesize.py` + `synthesis_core.py` + `findings_to_jsonl.py` (Phase 5). Opt-in: `run_build_verify.py`, `run_mutation.sh`, `derivation/run.py`, `preflight_tools.sh` (`--preflight`), `apply_safe/{version_sync,description_sync,failing_test_writer}.py`.

## Gotchas

1. **Sub-80 findings can be dropped instead of surfaced in `### ⚠️ Unverified`.** The A2 contract (`scripts/synthesis_core.py:apply_a2`) is no-silent-drop. The model sometimes treats a sub-80 score as a rejection signal and omits the finding entirely. Fix: scan the `### ⚠️ Unverified` section explicitly on every report; compare finding count to axis output to catch drops.
2. **Missing CLIs block the review.** Run `--preflight`, execute every printed install/config command through the environment's maintenance path, then rerun. Never reinterpret exit 3 or 4 as a partial Code Ultrareview verdict.
3. **Coherence activates silently on metadata changes.** A single `package.json` touch triggers the 9th subagent automatically. Watch for the `Coherence axis: active` line in the report header — it tells you the axis ran without you asking.
4. **`--reconcile` is atomic for resolved sources.** Invoke `derivation/run.py` with the Phase 1 `--scope` and a run-local `--output`. A missing explicit path or GitHub source exits 3; an unreadable, malformed, or claim-free explicit artifact exits 4. Successful output is written atomically and hashed in `scope.json["reconcile_coverage"]`; Phase 3 verifies that hash and adds the payload only to the Intent bundle. Repair the source and rerun with the same `--reconcile` value; never continue with reduced Intent coverage.
