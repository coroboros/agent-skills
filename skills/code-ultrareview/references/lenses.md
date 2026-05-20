# Lenses — briefs, dispatch, scoring

Read this before dispatching. It defines the four review lenses, the subagent
protocol, the confidence rubric, the exclusion contract, and aggregation.

## Dispatch protocol

Launch **four read-only subagents in one message** (`Explore` type — read-only,
fast, context-isolated). Each receives:

- the resolved `base`/`target` (or "dirty tree") — the subagent reconstructs the review set itself, read-only: clean tree → `git diff <base> <target>` (two-dot); dirty tree → `git diff HEAD` **and** every path from `git ls-files --others --exclude-standard`, each read in full. Never skip untracked — a new file is part of the session;
- the rule-hierarchy file paths (repo `CLAUDE.md` chain, `.claude/rules/*.md`, `~/.claude/rules/*.md`);
- its lens brief (below);
- the exclusion contract (below);
- the confidence rubric (below).

Lenses run as `Explore` subagents (fast, read-only). The orchestrator only resolves the target, dispatches, aggregates, scores, and filters — there is no second heavy reasoning pass. That is the cost posture: parallel light review, thin orchestration.

Each subagent returns a list of findings, each with: `lens`, `severity`
(High / Medium / Low), `location` (`file:line`), `finding`, `recommendation`,
`rule` (the quoted rule line — lens 1 only), and a self-assigned
`confidence` 0–100. Subagents never modify files.

**Canonical lens keys** (the `lens` field value — used by the report table and
`tests/_pipeline/_contracts.py`): `rules`, `bugs-drift`, `docs-version`,
`tests-blindspots`.

## The four lenses

### Lens 1 — Rules compliance

New violations of the rule hierarchy introduced by the diff. Cite the exact
rule line verbatim. A rule written as guidance for *writing* code is not always
a review criterion — apply judgment. Pre-existing violations on unchanged lines
are out of scope. If no rule file exists anywhere, this lens is skipped (see
Graceful degradation).

### Lens 2 — Bugs + drift

- **Bug** — a logic error on a changed line: wrong condition, off-by-one, unhandled `null`/empty, mishandled error, race, resource leak.
- **Drift** — code that no longer matches its own docstring, inline comment, README claim, or `CLAUDE.md` statement; or a change that diverges from an established sibling pattern in the same module without cause.

### Lens 3 — Docs + version

User-visible behavior changed without the matching update: public API/flag/CLI
without doc, behavior change without README/CHANGELOG where the repo expects
one, a version artifact not bumped per the repo's release rule, or (for skill
repos) README / marketplace parity broken by the change.

### Lens 4 — Tests + blind spots

- **Gap** — a code path the surrounding convention implies should have a test, error path, or doc, but doesn't.
- **Weak test** — a test that cannot fail when the business logic it covers changes (asserts a constant, mocks the unit under test, no meaningful assertion).
- **Blind spot** — an unstated assumption in the diff: an unhandled input class, a concurrency assumption, or reliance on possibly-stale library/API knowledge (→ `/find-docs` pointer, not a finding).

## Confidence rubric (0–100)

Score every finding; the orchestrator drops anything below **80**.

- **0** — false positive: doesn't survive light scrutiny, or is pre-existing (not introduced by the diff).
- **25** — maybe real, could not verify.
- **50** — real but minor; a nit relative to the rest of the change.
- **75** — highly confident: verified, will be hit in practice, materially impacts correctness/maintainability, or directly violates a quoted rule.
- **100** — certain: the evidence directly confirms it and it will happen frequently.

Score **0** (drop) for: pre-existing issues on unchanged lines; anything a linter / typechecker / compiler catches (assume CI runs them); pedantic nits a senior engineer would not raise; changes that are intentional and related to the broader change; a rule "violation" the code explicitly silences (e.g., a lint-ignore with cause).

## Exclusion contract

A finding whose primary nature is below is **never** reported as a finding.
Emit one pointer line in the "Deferred to sibling skills" section and stop:

| Primary nature | Pointer |
|----------------|---------|
| Security (injection, authz, secret exposure, SSRF, …) | `/security-review` |
| Performance, optimization, or code simplification/dedup | `/simplify` |
| Warrants a deep multi-agent / regression pass | `/ultrareview` |
| Relies on possibly-stale library/API knowledge | `/find-docs` |

This is what keeps the skill in its lane. When in doubt whether something is
"primarily" security/perf, defer it — do not double-report.

## Graceful degradation

If none of repo `CLAUDE.md`, `.claude/rules`, `~/.claude/rules` exist, skip
lens 1, state `Lens 1 (rules): skipped — no rules baseline found` in the report
header, and run lenses 2–4. Never fail silently.

## Aggregation

- Deduplicate findings reported by more than one lens — keep the one with the highest confidence, note the secondary lens.
- Order findings by severity (High → Low), then confidence (high → low).
- A lens that returns nothing contributes a "clean" note, not silence.
