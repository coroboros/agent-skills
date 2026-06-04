# Axis: Design/API (key `design-api`)

Public API breakage, DB schema breaking changes, type-strictness regressions, error-handling boundary changes, race conditions in concurrency-sensitive code, and shallow-module / wide-interface smells. The axis catches changes that propagate to downstream consumers — the cost of getting it wrong is high — and interfaces that cost a caller more than the behavior behind them.

## In scope (HIGH SIGNAL)

- **Public API breaking** — removed export, changed signature, renamed type, removed enum variant, narrowed return type. Tool inputs come from `api-extractor` (TS) and `oasdiff` (OpenAPI).
- **DB schema breaking** — dropped column / table, narrowed type without backfill, renamed column without alias, missing migration where the codebase expects one. Tool input from `atlas migrate lint`.
- **Type-strictness regression** — `any`, `as unknown`, `@ts-ignore`, `# type: ignore` on a new line in a strict file.
- **Error-handling boundary** — a thrown error that the caller does not catch, an error swallowed silently, a `Promise.catch` that returns nothing meaningful.
- **Race conditions** — unprotected shared mutable state, missing await, double-fetch, missing lock around critical section.
- **Concurrency-sensitive code** — `Promise.all` with N+1 underneath, sync I/O inside async, missing back-pressure on a stream.
- **Public-surface declared in CLAUDE.md** — a rule like "Never break the public API" is High severity when violated.
- **Shallow module** — a new or widened public interface fronting little behavior: many parameters, a thin pass-through, a wrapper that only forwards. Detect with the deletion test — if the module were inlined at its call sites, does the codebase get simpler? If yes, the interface adds surface without leverage. Deep modules (a small interface over substantial hidden complexity) are the goal; shallow ones are the smell.

## Out of scope (false positives — silence at source)

Anchor: `references/anthropic-verbatim.md` § False-positive taxonomy.

- **Internal API changes** that have no downstream consumer — refactors of private functions.
- **API additions** (new exported function, new endpoint) — additive, not breaking.
- **Schema additions** (new column with default) — additive, not breaking.
- **Type-strictness regressions in test files** — tests sometimes need looser typing; not a finding unless CLAUDE.md says otherwise.
- **Error-handling style preferences** (try/catch vs `.catch()`) without a CLAUDE.md rule.
- **Deep single-use internals** — a module called once but hiding real complexity behind a narrow interface is deep, not shallow. Not a finding.
- **Small focused modules** — depth is the interface-to-behavior ratio, not line count; a short module with a narrow interface is fine.

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
- Shallow-module smell — 🟢 Low on a cold or rarely-imported path; 🟠 Medium on a hot or widely-imported path, where the wide interface taxes every caller. Never High — a design smell, not a breakage.

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
