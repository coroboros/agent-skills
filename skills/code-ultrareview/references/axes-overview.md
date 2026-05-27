# Axes overview

Eight always-on axes + one conditional axis (`coherence`) comprise the code-ultrareview lens taxonomy. Each axis maps 1:1 to an LLM subagent during Phase 3. Per-axis briefs live at `references/axes/<axis-name>.md`.

## The 8 always-on axes

| # | Axis | Scope | Brief |
|---|------|-------|-------|
| 1 | `correctness` | Bugs, logic errors, type errors, regressions, unhandled edges | `references/axes/correctness.md` |
| 2 | `simplification` | Over-engineering (single-use abstractions, premature factories), dead-code judgment, redundancy beyond duplication, nested ternaries, speculative generality, >3-parameter functions | `references/axes/simplification.md` |
| 3 | `tests` | Coverage of changed lines, test smells (no-asserts, magic sleeps, `.skip` / `xit` in diff), strictness flags | `references/axes/tests.md` |
| 4 | `documentation` | Public API doc completeness, README drift on public-surface changes, ADR drift, prose hygiene over PR body + commits + user-facing `*.md` | `references/axes/documentation.md` |
| 5 | `style` | CLAUDE.md violations, linter-deferred concerns, formatter delegation | `references/axes/style.md` |
| 6 | `intent` | PR description vs diff, code vs comment drift, code vs spec drift, lockfile drift, generator drift; optional planning-artifact reconciliation via `--reconcile` | `references/axes/intent.md` |
| 7 | `design-api` | Public API breaking (oasdiff / api-extractor input), DB schema breaking (atlas input), type-strictness regression, error-handling boundaries, race conditions | `references/axes/design-api.md` |
| 8 | `performance` | N+1 patterns (semgrep input), sync I/O in async, bundle-size delta, allocation hot paths; explicit non-goals — no benchmarks, no flamegraphs, no memory profiling | `references/axes/performance.md` |

## The conditional 9th axis

| # | Axis | Activation | Brief |
|---|------|-----------|-------|
| 9 | `coherence` | Any of `package.json`, `.claude-plugin/marketplace.json`, `marketplace.json`, `SKILL.md`, root `README.md`, `tsconfig.json`, `pyproject.toml`, `Cargo.toml`, `go.mod` appears in the diff. Decided by `scripts/scope.py:activates_coherence`. | `references/axes/coherence.md` |

When active, Phase 3 launches 9 parallel subagents (still within the 10 concurrency cap). When inactive, the report header surfaces `Coherence axis: inactive` so the absence is visible.

The Coherence axis owns 6 sub-graphs by default: manifest, GitHub About, topics, README structured fields, SKILL.md frontmatter, plus a 6th depending on repo_kind. `--include-prose` extends to README freeform paragraphs.

## Inter-axis precedence

When 2+ axes flag the same `file:line`, highest severity wins; ties resolve via this precedence (encoded in `scripts/synthesis_core.py:AXIS_PRIORITY`):

```
correctness > design-api > simplification > tests > documentation > style > intent > performance > coherence
```

Rationale for the order:

- **correctness** wins everything — a real bug beats every other concern at the same line.
- **design-api** comes next — breaking changes propagate to every downstream consumer.
- **simplification** before **tests** — over-engineering blocks understanding; weak tests are recoverable.
- **performance** below **intent** — perf is rarely the limiting concern on a code-review pass; `/code-ultrareview` defers benchmarks anyway.
- **coherence** last — metadata drift is visible but rarely user-blocking.

## What "axis" means here

An axis is one category of code-review concern, mapped 1:1 to an LLM subagent that owns that concern. Each subagent receives:

- `scope.json` — repo kind, languages, CLAUDE.md chain, files touched.
- `tool-findings.jsonl` filtered to its own axis — deterministic tool output (confidence 100) from Phase 2.
- The diff itself (clean tree → `git diff <base> <target>`; dirty tree → `git diff HEAD` + untracked).
- Its axis brief (`references/axes/<axis-name>.md`) defining repo-kind branches and HIGH SIGNAL criteria.

It emits findings with 0-100 confidence per the verbatim rubric in `references/anthropic-verbatim.md`.

## Cross-references

- 5-phase pipeline: `../SKILL.md` § The five phases.
- Verbatim rubric, HIGH SIGNAL criteria, false-positive taxonomy: `references/anthropic-verbatim.md`.
- A2 routing + verdict algorithm: `../scripts/synthesis_core.py`.
- Scope detection (where `activates_coherence` is decided): `../scripts/scope.py`.
- Per-axis briefs: `references/axes/<axis-name>.md`.
