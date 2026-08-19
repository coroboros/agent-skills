# Axis: Performance (key `performance`)

Static-pattern performance concerns — N+1 queries, sync I/O in async paths, bundle-size delta, allocation hot paths. The axis does NOT run benchmarks, flamegraphs, or memory profilers (explicit non-goal, surfaces in "What I did NOT check").

## In scope (HIGH SIGNAL)

- **N+1 patterns** — loop calling a database query / network request per iteration. Tool input from semgrep with the bundled `references/perf-rules/n-plus-one-*.yml` rules.
- **Sync I/O in async paths** — `time.sleep` in `asyncio`, `requests.get` in async Python, `fs.readFileSync` inside a request handler. Tool input from `references/perf-rules/sync-io-async-py.yml`.
- **Bundle-size delta** — a new heavy dependency (`moment`, `lodash`, `chart.js`) imported into a hot path of a frontend repo. LLM judgment; no automatic threshold.
- **Allocation hot paths** — large object created per iteration of a hot loop, string concatenation in a tight loop, regex compiled per call.
- **Unnecessary work on the request path** — synchronous JSON parsing of a megabyte payload, eager hydration of an unused field, missing pagination on a large query.

## Out of scope (false positives — silence at source)

Anchor: `references/anthropic-verbatim.md` § False-positive taxonomy.

- **Runtime benchmarks** — explicit non-goal. Surface in "What I did NOT check".
- **Flamegraphs / profilers** — explicit non-goal.
- **Memory profiling** — explicit non-goal.
- **Micro-optimizations** — `Array.from` vs `[...x]`, `for` vs `forEach`. The Simplification axis defers; the Performance axis defers.
- **Pre-existing patterns on unchanged lines** — out of scope.
- **Patterns in test files** — tests are not the request path.

## Tool inputs (Phase 2)

From `scripts/battery_ingest.py:_semgrep_axis`:

- `semgrep` findings route here only when `check_id` starts with `code-ultrareview-` AND `metadata.axis == "performance"`.
- Bundled rules in `references/perf-rules/`:
  - `n-plus-one-sqlalchemy.yml` — Python SQLAlchemy N+1.
  - `n-plus-one-sequelize.yml` — JS Sequelize N+1.
  - `sync-io-async-py.yml` — sync I/O in Python async.

All tool findings carry `confidence: 100` and skip validators.

## Severity calibration

- 🔴 High — N+1 confirmed on the request path of a production endpoint, sync I/O blocking an event loop, memory leak (object retained per request).
- 🟠 Medium — N+1 on a non-hot path, sync I/O in a script that could be async, bundle bloat from a fat import on a critical-path page.
- 🟢 Low — micro-allocation in a non-hot loop, regex compiled per call in a low-traffic path.

## Repo-kind branches

| `repo_kind` | Behavior |
|-------------|----------|
| `skills` | Review executable scripts and long-running commands normally. For instruction-only diffs with no executable surface, emit the canonical `{"axis":"performance","no_findings":true}` marker. |
| `app` | Full review — request path, page load, hydration. |
| `library` | Full review — library consumers care about allocations. |
| `python`, `rust`, `go` | Full review with language-native patterns (Python async, Rust allocations, Go goroutine leaks). |
| `docs` | No executable surface — axis emits zero findings. |
| `monorepo` | Per-workspace specialization parked; subagent applies the most-permissive ruleset. |
| `unknown` | Full review. |

## Subagent inputs

- `scope.json` — repo kind, files touched, languages.
- `tool-findings.jsonl` filtered to `axis: performance` — bundled-perf-rules semgrep findings.
- The diff itself.
- This brief.
- `references/anthropic-verbatim.md` — rubric + false-positive list.
