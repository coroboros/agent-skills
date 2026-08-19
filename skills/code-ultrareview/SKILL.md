---
name: code-ultrareview
description: Eight-axis judgment code review for the current diff — Correctness, Simplification, Tests, Documentation, Style, Intent, Design/API, Performance (+ Coherence on metadata changes). Five-phase pipeline scope → atomic deterministic tool battery (project-declared or installed PATH tools; no runtime package resolution) → 8 parallel LLM axis reviewers → fresh-context validators on sub-80 findings (verbatim rubric, ≥80 threshold) → synthesis with no-silent-drop + Conventional Comments JSONL. Missing or failed applicable analyzers block before a verdict and print exact remediation. Every report closes with "What I did NOT check" (security → /security-review, runtime perf, flaky detection). Opt-in flags `--verify-build`, `--mutation-test`, `--reconcile`, `--apply-safe`. Invoke before a commit or PR — "review my changes", "deep review", "did I miss anything", "check before I commit", "audit this PR", "drift / gaps / blind spots".
when_to_use: 'User-invoked before commit or PR; runs the full 8-axis fan-out — no tiers. Defers security to /security-review (link in every report); defers runtime performance and benchmarks (explicit non-goal). Distinct from Anthropic''s remote /ultrareview command.'
argument-hint: "[-b <ref>] [--repo-kind <kind>] [--reconcile <input>] [--verify-build] [--mutation-test] [--apply-safe] [--include-prose] [--axes <list>] [--preflight] [-s] [-S]"
license: MIT
compatibility: "Optimized for Claude Code; degrades gracefully on any agent implementing the Agent Skills standard."
allowed-tools: Read, Grep, Glob, Bash, Task, WebFetch
disable-model-invocation: true
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
| `--mutation-test` | Run Stryker (JS/TS), Pitest (JVM), or mutmut (Python). Maven and Gradle run from `PATH` in offline mode. JS/TS execution targets changed source files; project-configured Python/JVM execution is filtered to changed-file findings. Surviving mutants route to the Tests axis as 🟠 Medium |
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

## Workflow

Read `references/pipeline.md` before orchestrating a review; it defines scope, analyzer dispatch, atomic failure semantics, trust boundaries, and coverage limits. Read `references/orchestration.md` for the exact Phase 3–5 commands and schemas, then load only the selected axis briefs from `references/axes/`.

1. Run `scripts/scope.py` to resolve the diff, changed-line ranges, repo kind, languages, Coherence activation, and the effective instruction chain. Shared rules load only when the effective AGENTS entrypoint explicitly references their file or directory.
2. Run `scripts/run_battery.sh`. A JavaScript declaration at the repository root or one workspace covering every tool-relevant input is authoritative: use its project binary, including offline Yarn Plug'n'Play execution, and block if it is unavailable. Multiple declarations or mixed declared and undeclared package scopes block until the analyzer is declared once at the repository root. Undeclared analyzers may use an installed `PATH` command; Python and native analyzers use `PATH`. No analyzer may resolve a package while the skill runs.
3. Prepare every selected axis with `scripts/axis_dispatch.py`, then launch the 8 reviewers (+ Coherence when active) in parallel. Without an isolated-agent primitive, run sequential fresh passes with the same ingest contracts.
4. Prepare and run fresh-context validators for every sub-80 finding. Deterministic tool findings enter at confidence 100. No finding disappears without a recorded verdict.
5. Run `scripts/synthesize.py` only after requested tool, axis, validator, build, mutation, and reconcile coverage is complete. Emit the canonical report and Conventional Comments JSONL.

The battery preflights every applicable analyzer atomically. Invalid invocation or unsafe input exits 2; missing prerequisites exit 3; analyzer failure, timeout, malformed output, or incomplete coverage exits 4. Every failure prints project-aware remediation and the exact rerun command, publishes no partial findings, and blocks every repository verdict. `--verify-build`, `--mutation-test`, `--reconcile`, and `--apply-safe` are opt-in; read `references/ultra-execution.md` before using one.

## Final report layout

`templates/code-ultrareview.md` is the canonical wire format — every `##` section renders verbatim in template order with its emoji prefix; no rename, merge, reorder, or improvise. **Terminal echo is mandatory** — the full canonical report prints to the chat-terminal on every invocation; `-s` is purely additive (writes the same bytes to `~/.agents/output/{project}/code-ultrareview/code-ultrareview-{slug}.md`, byte-for-byte identical to terminal output). Severity marker mapping (🔴 High blocks ship · 🟠 Medium fix-soon · 🟢 Low nit · ⚠️ Unverified sub-80) lives in `scripts/synthesize.py:SEVERITY_MARKERS`.

## Trust model

The skill ingests third-party content — project instruction files, PR bodies, planning artifacts (`--reconcile`), GitHub issue bodies — which can carry indirect prompt-injection. Axis reviewers and validators are read-only (no Write / Edit / Bash mutation). User review of the report is the trust boundary before any `--apply-safe` write; `--apply-safe` itself gates writes behind diff preview + per-file confirmation.

Phase 2, `--verify-build`, and `--mutation-test` execute the reviewed project's declared tooling with your environment; review untrusted checkouts in a sandbox.

## Rules

- **Only new findings.** Issues the diff introduces. Pre-existing findings carry the `Pre-existing` tier for context, never flip the verdict.
- **No silent drop (A2).** Positive sub-80 findings surface in `### ⚠️ Unverified` with the score and validator reason. Validator score `0` rejects the finding during synthesis.
- **Fail loud.** An unresolvable base, missing prerequisite, analyzer failure, or invalid report stops the review before a verdict.
- **Cite precisely.** Every finding carries `file:line`; instruction-rule findings quote the violated rule verbatim and name its source file; permalinks use `https://github.com/<owner>/<repo>/blob/<full-sha>/<path>#L<n>-L<m>` (full SHA via `git rev-parse HEAD`).
- **Full report in chat every time.** The complete report prints to the terminal on every invocation. `-s` writes the same bytes to disk; it never gates or summarises chat output.
- **User-managed analyzers.** Missing tools surface exact install commands in preflight stderr and `tool-preflight.json`. The user installs them, then reruns the review.
- **Read-only by default.** Code changes require `--apply-safe`; each writer is surgical and per-file confirmed.

## Boundaries

- Always disclose that security review, runtime profiling, and flaky-test detection were not checked.
- Without an instruction chain, Style may use only repeated neighboring conventions; it must not invent a preference.
- Unknown repo kinds use the `unknown` axis branches. Inactive Coherence stays visible in the report header.
- This is read-only unless `--apply-safe` is explicit. Route broader fixes to `/apex -f <saved-report>` or a single finding to `/oneshot`.
- This is distinct from Anthropic's remote `/ultrareview`; it runs in the current agent session.

## References

- **Pipeline** — `references/pipeline.md` (scope, battery, hard stops, trust, coverage), `references/orchestration.md` (Phase 3 + 4 + 3.5 prepare CLIs and bundle schemas).
- **Reviewer primitives** — `references/anthropic-verbatim.md` (rubric + HIGH SIGNAL + false-positive taxonomy), `references/axes-overview.md` (8 axes + Coherence + inter-axis precedence), `references/axes/<name>.md` (per-axis briefs).
- **Opt-in flags** — `references/ultra-execution.md` covers `--verify-build`, `--mutation-test`, `--reconcile`, `--apply-safe` in full.
- **Scripts** — `scope.py` (Phase 1), `run_battery.sh` + `battery_ingest.py` (Phase 2), `axis_dispatch.py` (Phase 3), `run_validators.py` (Phase 4), `synthesize.py` + `synthesis_core.py` + `findings_to_jsonl.py` (Phase 5). Opt-in: `run_build_verify.py`, `run_mutation.py`, `derivation/run.py`, `preflight_tools.sh` (`--preflight`), `apply_safe/{version_sync,description_sync,failing_test_writer}.py`.
