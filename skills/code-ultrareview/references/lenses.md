# Lenses — briefs, dispatch, scoring

Read this before dispatching. It defines the five review lenses, the
multi-tier subagent protocol, the confidence rubric, the exclusion contract,
and the routing rules for sub-80 findings. Aggregation details live in
`references/aggregation.md`.

## Dispatch protocol

Launch **read-only subagents in one message** (`Explore` type — read-only,
fast, context-isolated). The lens fan-out is unconditional: the five always-on
lenses (rules, bugs-drift, docs-version, tests-blindspots, coherence-graph)
run in parallel on every invocation. The sixth lens — `derivation` — joins
the fan-out when `--reconcile` resolves to non-empty input. A1 spec-claim
triggering, iteration on sub-80 findings, spec-conformance fetch,
property-fuzz harness synthesis, and `--apply-safe` writers are folded in
as always-on behavior. The audit phase informs the report header (Scope +
Estimated wall-clock); it does not gate dispatch.

Each subagent receives:

- the resolved `base`/`target` (or "dirty tree") — the subagent reconstructs the review set itself, read-only: clean tree → `git diff <base> <target>` (two-dot); dirty tree → `git diff HEAD` **and** every path from `git ls-files --others --exclude-standard`, each read in full. Never skip untracked — a new file is part of the session;
- the rule-hierarchy file paths (repo `CLAUDE.md` chain, `.claude/rules/*.md`, `~/.claude/rules/*.md`);
- its lens brief (below);
- the exclusion contract (below);
- the confidence rubric (below);
- the routing rule for sub-80 findings (no silent drop — see *Aggregation*).

Each subagent returns a list of findings, each with: `lens`, `severity`
(High / Medium / Low), `location` (`file:line`), `finding`, `recommendation`,
`rule` (the quoted rule line — lens 1 only), and a self-assigned
`confidence` 0–100. Subagents never modify files.

Severity ↔ marker mapping (canonical, surfaced in every report):
**🔴 High** — blocks ship, must fix; **🟠 Medium** — fix soon, won't break
ship; **🟢 Low** — nit / informational, noted. Markers attach via
`aggregation.py::_attach_marker` after A2 routing, so unverified findings
(severity downgraded to Low) render as 🟢. The verdict algorithm
(`references/verdict-logic.md`) reads markers + Anthropic tier; the action
plan (`references/skill-routing.md`) groups by `(lens, marker)` for
delegation.

**Canonical lens keys** (the `lens` field value — used by the report table
and `tests/_pipeline/_contracts.py`): `rules`, `bugs-drift`, `docs-version`,
`tests-blindspots`, `coherence-graph`, `derivation`. The coherence-graph
lens has its own sub-graph keys defined in `references/coherence-graph.md`;
the derivation lens has classification tags + freshness rules defined in
`references/derivation.md`.

## The six lenses

### Lens 1 — Rules compliance (key `rules`)

New violations of the rule hierarchy introduced by the diff. Cite the exact
rule line verbatim. A rule written as guidance for *writing* code is not
always a review criterion — apply judgment. Pre-existing violations on
unchanged lines are out of scope. If no rule file exists anywhere, this lens
is skipped (see *Graceful degradation*).

### Lens 2 — Bugs + drift (key `bugs-drift`)

- **Bug** — a logic error on a changed line: wrong condition, off-by-one, unhandled `null`/empty, mishandled error, race, resource leak.
- **Drift** — code that no longer matches its own docstring, inline comment, README claim, or `CLAUDE.md` statement; or a change that diverges from an established sibling pattern in the same module without cause.
- **Single source of truth** — a literal that must stay equal across sites (path, URL, endpoint, constant, version, env-var name) introduced or duplicated by the diff in two or more places. A change to one copy silently diverges from the others, so report it as drift and cite both sites. Distinct from cosmetic dedup (→ `/simplify`): report only when divergence would break behavior, never for stylistic repetition.

**A1 — spec-claim triggering (always on).** When the diff,
README, or `CLAUDE.md` cites a named normative spec (`RFC 6874`, `WHATWG`,
`ISO/IEC 7816`, `OpenAPI`, etc. — same regex as `scripts/audit_signals.py`),
the lens fetches the spec via `WebFetch`, quotes the governing clause
verbatim in the finding's `recommendation`, and diffs the code against the
quoted clause. The cache at `~/.claude/cache/code-ultrareview/specs/` is
shared with the spec-conformance lens; ETag refresh ≥7 days. A
verifiable divergence scores **≥80** confidence — the quoted spec clause
is the evidence.

**Iteration on sub-80 findings (always on).** Sub-80 bug/drift findings are re-passed with
`--iterate`: the subagent attempts a build (`npm test --no-coverage`,
`pytest -x`, `cargo test`, or `go test` — auto-detected) on the changed
file's nearest test neighbor. If the build confirms the bug, confidence
promotes to ≥80; if the build disproves it, the finding is dropped with the
build output in the rationale. Cap: one iteration per finding.

### Lens 3 — Docs + version (key `docs-version`)

User-visible behavior changed without the matching update: public API/flag/CLI
without doc, behavior change without README/CHANGELOG where the repo expects
one, a version artifact not bumped per the repo's release rule, or (for skill
repos) README / marketplace parity broken by the change.

### Lens 4 — Tests + blind spots (key `tests-blindspots`)

- **Gap** — a code path the surrounding convention implies should have a test, error path, or doc, but doesn't.
- **Weak test** — a test that cannot fail when the business logic it covers changes (asserts a constant, mocks the unit under test, no meaningful assertion).
- **Blind spot** — an unstated assumption in the diff: an unhandled input class, a concurrency assumption, or reliance on possibly-stale library/API knowledge (→ `/find-docs` pointer, not a finding).

### Lens 5 — Coherence-graph (key `coherence-graph`)

Cross-artifact drift across six sub-graphs: description, version, capability,
cross-reference, example, spec-conformance. Default to structured fields
only; `--include-prose` extends to README freeform. Per-repo
`.coherence-ignore` allowlist. Full brief: `references/coherence-graph.md`.

### Lens 6 — Derivation (key `derivation`)

Reconciles planning artifacts (brainstorm, spec, apex plan, PR body, issue
body) against the diff. Activates on `--reconcile <input>` — without it, the
lens does not dispatch. Classification taxonomy: GAP (planning said X, code
missing), SCOPE-ADD (code has X, planning silent), DECISION-OVERRIDE
(planning resolved X, code does Y), CONSISTENT (claim verified — counted in
coverage, no finding row). Severity capped by artifact freshness: >30 days
→ Low; >90 days → coverage summary only. Per-repo `.derivation-ignore`
allowlist (path / kind / claim text). The Python orchestrator extracts
claims (AC items, Goals, Decisions, Tasks) and emits one UNCLASSIFIED
finding per claim — the subagent rewrites the classification at dispatch
time. Cap of 5 findings per artifact bounds noise (Risk #2 — LLM
overcorrection guard, per arXiv 2603.00539); `--strict` lifts the cap.
Full brief: `references/derivation.md`.

## Confidence rubric (0–100)

Score every finding; **sub-80 findings are surfaced, not dropped.** The
orchestrator routes them to the `### Unverified` sub-section of
the report with the prefix `[unverified]` on the finding text and the
rationale `Sub-80 confidence ({score}) — verify locally before action.`
in the recommendation.

- **0** — false positive: doesn't survive light scrutiny, or is pre-existing (not introduced by the diff). Score 0 = drop, with rationale documented.
- **25** — maybe real, could not verify.
- **50** — real but minor; a nit relative to the rest of the change.
- **75** — highly confident: verified, will be hit in practice, materially impacts correctness/maintainability.
- **100** — certain: the evidence directly confirms it and it will happen frequently.

Score **0** (drop, with rationale) for: pre-existing issues on unchanged lines; anything a linter / typechecker / compiler catches (assume CI runs them); pedantic nits a senior engineer would not raise; changes that are intentional and related to the broader change; a rule "violation" the code explicitly silences (e.g., a lint-ignore with cause).

A1 confidence guidance: a verifiable divergence between the diff and the
quoted spec clause is at least **80** (evidence is the spec itself).

## Exclusion contract

A finding whose primary nature is below is **never** reported as a finding.
Emit one pointer line in the "Deferred to sibling skills" section and stop:

| Primary nature | Pointer |
|----------------|---------|
| Security (injection, authz, secret exposure, SSRF, …) | `/security-review` |
| Performance, optimization, or code simplification/dedup | `/simplify` |
| Warrants a deep multi-agent remote pass (Anthropic billed) | `/ultrareview` |
| Relies on possibly-stale library/API knowledge | `/find-docs` |

This is what keeps the skill in its lane. When in doubt whether something
is "primarily" security/perf, defer it — do not double-report.

## Graceful degradation

If none of repo `CLAUDE.md`, `.claude/rules`, `~/.claude/rules` exist, skip
lens 1, state `Lens 1 (rules): skipped — no rules baseline found` in the
report header, and run lenses 2–5. Never fail silently.

`WebFetch` unavailable (A1 spec lookup) → finding surfaces with prefix
`[unverified — needs network]` and confidence 50; routed per A2 to the
Unverified sub-section rather than dropped. Same for `gh` CLI gaps in the
coherence-graph lens (description, version sub-graphs).

## Aggregation

Detailed contract in `references/aggregation.md`. Summary:

- Deduplicate findings reported by more than one lens — keep the one with the highest confidence, note the secondary lens.
- Order findings by severity (High → Low), then confidence (high → low).
- A lens that returns nothing contributes a "clean" note, not silence.
- **No silent drop.** Sub-80 findings are routed to `### Unverified`, never omitted.
