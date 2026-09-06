---
name: code-ultrareview
description: Review a code or instruction diff across correctness, simplification, tests, documentation, style, intent, design/API, and performance; add coherence review for metadata changes. Use when the user requests a thorough review before a commit or PR. Validate tool observations and reviewer claims in context, preserve unresolved findings, and report coverage limits. Missing applicable analyzer evidence blocks a verdict.
when_to_use: 'User-invoked before commit or PR; runs the full 8-axis fan-out — no tiers. Defers security to /security-review (link in every report); defers runtime performance and benchmarks (explicit non-goal). Distinct from Anthropic''s remote /ultrareview command.'
argument-hint: "[-b <ref>] [--repo-kind <kind>] [--reconcile <input>] [--verify-build] [--mutation-test] [--apply-safe] [--include-prose] [--axes <list>] [--preflight] [-s] [-S]"
license: MIT
compatibility: "Requires git, bash, Python 3.10+ and the applicable project-declared or installed analyzers. Independent review requires isolated-agent support; concurrency follows the host. Missing required analyzer evidence blocks the verdict. Model and effort inherit the session."
allowed-tools: Read, Grep, Glob, Bash, Task, WebFetch
disable-model-invocation: true
metadata:
  author: coroboros
  sources: "github.com/anthropics/claude-plugins-official/tree/main/plugins/code-review; github.com/anthropics/claude-plugins-official/tree/main/plugins/code-simplifier; code.claude.com/docs/en/code-review; code.claude.com/docs/en/ultrareview; github.com/mattpocock/skills/tree/main/skills/engineering/improve-codebase-architecture"
---

# Code ultrareview

<!-- canonical:adversarial-verification:start -->
## Critical — Adversarial verification

Verify consequential findings and decisions before acting on them.

- Seek counterexamples and independent evidence for load-bearing or contested claims. Use fresh reviewers when available and useful; label sequential self-review as less independent.
- Resolve material findings by correction, evidence-backed refutation, or an explicit remaining risk. Never silently drop them.
- Evidence decides, not reviewer counts or confidence alone. One reproducible defect can invalidate a conclusion.
- Scale verification to the stakes. Keep settled facts settled and reversible, low-impact checks light.
<!-- canonical:adversarial-verification:end -->

<!-- canonical:execution-discipline:start -->
## Important — Engineering discipline

Apply these rules when writing, editing, or proposing code.

- Solve the accepted problem with the smallest complete change. Reuse existing mechanisms; preserve unrelated work. Validate external inputs and real failure states.
- Read the affected implementation, callers, and shared utilities before editing. Ground code claims in inspected evidence.
- Implement the general behavior. Tests must distinguish correct behavior from the defect; never hard-code to fixtures or preserve a demonstrably wrong test.
- Carry scope, corrections, and existing authorization through handoffs. Run applicable required checks; repeat them only for changed behavior or unresolved failures.
<!-- canonical:execution-discipline:end -->

<!-- canonical:label-hygiene:start -->
## Critical — Label hygiene

Remove private planning labels and process narration from shipped code and prose. State the domain behavior directly.

- **Planning labels** — replace `WS-N`, `Phase-A`, `Step-3`, and private plan names with domain terms. <!-- noqa: internal-label -->
- **Process narration** — remove authoring history and references that require private planning context. Explain the resulting behavior or constraint.

Keep useful issue links, public ticket identifiers, user-requested traceability, and labels where the artifact defines that format. Reviewer-facing migration docs may name deleted artifacts.
<!-- canonical:label-hygiene:end -->

> **Eight-axis judgment code review.** Five-phase pipeline scope → tool battery → 8 parallel axis reviewers → fresh-context validators → synthesis. The default runs at full strength — every axis, full applicable battery, no sampling; `--axes` is an explicitly scoped review with no repository verdict. Distinct from Anthropic's remote `/ultrareview` — same goal, in-session on the user's subscription.

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

## Objective

By default, run the 8 axes — Correctness, Simplification, Tests, Documentation, Style, Intent, Design/API, Performance — as separate LLM axis reviewers scheduled within the host's available slots fed by deterministic tool findings from `scripts/run_battery.sh`. Coherence joins as a 9th axis when metadata files change. Every axis and tool observation receives contextual validation. Inherit the host model; confidence is a local reporting rubric, not a calibrated probability or proof of correctness. Findings synthesize into one report with deterministic dedup, inter-axis precedence, A2 no-silent-drop, and a verdict (Ship / Fix-then-ship / Needs work). The report ends with "What I did NOT check" so the coverage limits are explicit. `--axes` intentionally narrows both analyzers and LLM review and emits scoped findings without a repository verdict.

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
2. Run `scripts/run_battery.sh`. Knip runs only under a covering `package.json`: none records it as not applicable, partial coverage blocks. A JavaScript declaration at the repository root or one workspace covering every tool-relevant input is authoritative: use its project binary, including offline Yarn Plug'n'Play execution, and block if it is unavailable. Multiple declarations or mixed declared and undeclared package scopes block until the analyzer is declared once at the repository root. Undeclared analyzers may use an installed `PATH` command; Python and native analyzers use `PATH`. No analyzer may resolve a package while the skill runs.
3. Prepare every selected axis with `scripts/axis_dispatch.py`, then schedule reviewers within the host's available slots. Without an isolated-agent primitive, run sequential shared-context passes with the same ingest contracts and disclose their lower independence.
4. Prepare and run contextual validators for every finding, including tool observations and high-confidence author claims. Tool observations enter at confidence 0 until assessed. No finding disappears without a recorded verdict.
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
