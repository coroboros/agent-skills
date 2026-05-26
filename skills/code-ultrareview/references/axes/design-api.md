# Axis: Design/API (key `design-api`)

Public API breakage, DB schema breaking changes, type-strictness regressions, error-handling boundary changes, race conditions in concurrency-sensitive code. The axis catches changes that propagate to downstream consumers — the cost of getting it wrong is high.

## In scope (HIGH SIGNAL)

- **Public API breaking** — removed export, changed signature, renamed type, removed enum variant, narrowed return type. Tool inputs come from `api-extractor` (TS) and `oasdiff` (OpenAPI).
- **DB schema breaking** — dropped column / table, narrowed type without backfill, renamed column without alias, missing migration where the codebase expects one. Tool input from `atlas migrate lint`.
- **Type-strictness regression** — `any`, `as unknown`, `@ts-ignore`, `# type: ignore` on a new line in a strict file.
- **Error-handling boundary** — a thrown error that the caller does not catch, an error swallowed silently, a `Promise.catch` that returns nothing meaningful.
- **Race conditions** — unprotected shared mutable state, missing await, double-fetch, missing lock around critical section.
- **Concurrency-sensitive code** — `Promise.all` with N+1 underneath, sync I/O inside async, missing back-pressure on a stream.
- **Public-surface declared in CLAUDE.md** — a rule like "Never break the public API" is High severity when violated.

## Out of scope (false positives — silence at source)

Anchor: `references/anthropic-verbatim.md` § False-positive taxonomy.

- **Internal API changes** that have no downstream consumer — refactors of private functions.
- **API additions** (new exported function, new endpoint) — additive, not breaking.
- **Schema additions** (new column with default) — additive, not breaking.
- **Type-strictness regressions in test files** — tests sometimes need looser typing; not a finding unless CLAUDE.md says otherwise.
- **Error-handling style preferences** (try/catch vs `.catch()`) without a CLAUDE.md rule.

## Tool inputs (Phase 2)

From `scripts/battery_ingest.py:TOOL_TO_AXIS`:

- `api-extractor` — TS public API surface diff. Warnings → 🟠 Medium; Errors → 🔴 High.
- `oasdiff` — OpenAPI breaking-change detector. Levels: `3 = ERR` (🔴 High) · `2 = WARN` (🟠 Medium) · `1 = INFO` (🟢 Low).
- `atlas` — DB migration lint. All atlas diagnostics → 🔴 High by default.

All tool findings carry `confidence: 100` and skip validators.

## Severity calibration

- 🔴 High — public API breaking (oasdiff ERR, api-extractor Error), DB schema breaking (atlas any-level), unhandled error on a hot path, race condition on shared state.
- 🟠 Medium — type-strictness regression on a new file in a strict codebase, error-handling boundary that may swallow silently, oasdiff WARN.
- 🟢 Low — additive type narrowing that may surprise consumers, defensive `?` introduced where it was not before.

## Repo-kind branches

| `repo_kind` | Behavior |
|-------------|----------|
| `skills` | "Public API" = SKILL.md flags + emitted output schema. A removed flag or changed output shape is a breaking change. Bundled `scripts/` internals are not public API. |
| `app` | Full review — UI, route handlers, public types. |
| `library` | Strictest review — every exported symbol is public API. Semver implications drive severity. |
| `python`, `rust`, `go` | Full review using the language's native public-surface rules (`__all__`, `pub`, capitalization). |
| `docs` | No executable surface — axis emits zero findings. |
| `monorepo` | Per-workspace specialization parked; subagent applies the most-permissive ruleset. |
| `unknown` | Existing behavior. |

## Subagent inputs

- `scope.json` — repo kind, files touched, languages.
- `tool-findings.jsonl` filtered to `axis: design-api` — api-extractor, oasdiff, atlas findings.
- The diff itself.
- This brief.
- `references/anthropic-verbatim.md` — rubric + false-positive list.
