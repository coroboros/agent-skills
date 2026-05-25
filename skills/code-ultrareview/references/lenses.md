# Lenses — dispatch, scoring, contracts

Read this before dispatching. This file owns the dispatch protocol,
confidence rubric, exclusion contract, graceful-degradation rules, and
aggregation pointer. Per-lens briefs live in seven sibling files —
`lens-<key>.md`.

## Canonical lenses

| Key | File |
|-----|------|
| `rules` | `lens-rules.md` |
| `bugs-drift` | `lens-bugs-drift.md` |
| `docs-version` | `lens-docs-version.md` |
| `tests-blindspots` | `lens-tests-blindspots.md` |
| `coherence-graph` | `lens-coherence-graph.md` |
| `derivation` | `lens-derivation.md` |
| `prose-hygiene` | `lens-prose-hygiene.md` |

These seven keys are the canonical `lens` field values. The report
table, the evals, and `tests/_pipeline/_contracts.py` all key off them.

## Dispatch protocol

Launch read-only subagents in one message (`Explore` type — read-only,
fast, context-isolated). The fan-out is unconditional: six always-on
lenses (`rules`, `bugs-drift`, `docs-version`, `tests-blindspots`,
`coherence-graph`, `prose-hygiene`) run in parallel on every invocation.
The seventh — `derivation` — joins when `--reconcile` resolves to
non-empty input. `--no-prose-hygiene` is the only opt-out — when set,
the dispatcher skips the prose-hygiene subagent and marks its
lens-summary row `— skipped (--no-prose-hygiene)`. A1 spec-claim
triggering, iteration on sub-80 findings, spec-conformance fetch,
property-fuzz harness synthesis, and `--apply-safe` writers are
always-on. The audit phase informs the report header; it does not gate
dispatch.

Each subagent receives:

- the resolved `base`/`target` (or `dirty tree`) — the subagent reconstructs the review set itself, read-only: clean tree → `git diff <base> <target>` (two-dot); dirty tree → `git diff HEAD` **and** every path from `git ls-files --others --exclude-standard`, each read in full;
- the rule-hierarchy file paths (repo `CLAUDE.md` chain, `.claude/rules/*.md`, `~/.claude/rules/*.md`);
- the resolved `repo_kind` (str) and `repo_kind_signals` (dict), surfaced by the audit phase — the subagent reads the `## Repo-kind branches` section in its lens brief and applies the relevant rules before evaluating the diff;
- its lens brief (the corresponding `lens-<key>.md`);
- the exclusion contract (below);
- the confidence rubric (below);
- the routing rule for sub-80 findings (no silent drop — see *Aggregation*).

Each subagent returns findings shaped `{lens, severity (High/Medium/Low),
location (file:line), finding, recommendation, rule (lens 1 only),
confidence 0–100}`. Subagents never modify files.

Severity ↔ marker mapping: **🔴 High** blocks ship; **🟠 Medium** fix
soon; **🟢 Low** nit. Markers attach via `aggregation.py::_attach_marker`
after A2 routing — unverified findings (downgraded to Low) render as 🟢.
The verdict algorithm reads markers + Anthropic tier
(`verdict-logic.md`); the action plan groups by `(lens, marker)` for
delegation (`skill-routing.md`).

## Confidence rubric (0–100)

Score every finding. **Sub-80 findings are surfaced, not dropped.** The
orchestrator routes them to `### ⚠️ Unverified` with the prefix
`[unverified]` on the finding text and the rationale
`Sub-80 confidence ({score}) — verify locally before action.`

- **0** — false positive, pre-existing on unchanged lines, or anything a
  linter/typechecker/compiler catches; documented rationale, then drop.
- **25** — maybe real, could not verify.
- **50** — real but minor; a nit relative to the change.
- **75** — verified, will be hit in practice, materially impacts
  correctness/maintainability.
- **100** — certain: evidence directly confirms it and it happens often.

A1 guidance: a verifiable divergence between the diff and the quoted
spec clause scores at least **80** — the spec is the evidence.

## Exclusion contract

Findings whose primary nature is below are **never** reported. Emit one
pointer line in the report's `## 🧭 Deferred to sibling skills` section
and stop:

| Primary nature | Pointer |
|----------------|---------|
| Security (injection, authz, secret exposure, SSRF, …) | `/security-review` |
| Performance, optimization, or simplification/dedup | `/simplify` |
| Warrants a deep multi-agent remote pass (Anthropic billed) | `/ultrareview` |
| Relies on possibly-stale library/API knowledge | `/find-docs` |

In doubt whether something is "primarily" security/perf, defer it. Do
not double-report.

## Graceful degradation

No repo `CLAUDE.md`, no `.claude/rules`, no `~/.claude/rules` → skip
lens 1, state `Lens 1 (rules): skipped — no rules baseline found` in
the report header, run lenses 2–7. Fail loud, not silent.

`WebFetch` unavailable (A1 spec lookup) → finding surfaces with prefix
`[unverified — needs network]` and confidence 50; routed per A2 to the
Unverified sub-section rather than dropped. Same for `gh` CLI gaps in
the coherence-graph lens (description, version sub-graphs).

## Aggregation

Detail: `aggregation.md`. Summary:

- Deduplicate findings reported by more than one lens — keep the
  highest confidence; note the secondary lens.
- Order findings by severity (High → Low), then confidence (high → low).
- A lens that returns nothing contributes a "clean" note, not silence.
- **No silent drop.** Sub-80 findings route to `### ⚠️ Unverified`,
  never omitted (the A2 contract).
