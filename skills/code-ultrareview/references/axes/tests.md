# Axis: Tests (key `tests`)

Coverage of changed lines, test smells, weak assertions, strictness flags. The axis catches structural test gaps — it does NOT detect flakes (deferred, explicit non-goal in "What I did NOT check").

## Definitions

- **Gap** — a code path the surrounding test convention implies should have a test, error path, or doc, but doesn't.
- **Weak test** — a test that cannot fail when the business logic it covers changes. Asserts a constant, mocks the unit under test, or has no meaningful assertion.
- **Test smell** — test code that drifts from the project's strictness contract. Examples below.

## In scope (HIGH SIGNAL)

- **Missing test for new public surface** — a new exported function / class / endpoint / CLI flag without a matching test, in a repo that already tests similar surface.
- **Weak assertions** — `expect(x).toBeTruthy()` when `expect(x).toBe(<value>)` is testable; `assert` with no comparison; `.toMatchSnapshot()` on dynamic data.
- **Magic sleeps** — `setTimeout(…, <ms>)` / `time.sleep(…)` in tests without a justified reason (race-condition test, retry verification). Use deterministic waits.
- **`.skip` / `xit` / `xdescribe` in the diff** — disabled tests landed without rationale.
- **`Math.random` in tests** — flake guaranteed; use a seeded RNG.
- **Strictness flag drift** — a new test added with `--no-strict`, `// @ts-nocheck`, or `# type: ignore` on the file.
- **Test runs in production code** — `if (process.env.NODE_ENV === 'test')` branch in non-test code without justification.

## Out of scope (false positives — silence at source)

Anchor: `references/anthropic-verbatim.md` § False-positive taxonomy.

- "Add more test coverage" without a concrete missing case — generic coverage complaints are noise.
- Pre-existing test gaps on unchanged code paths — out of scope; the diff did not cause them.
- Style preferences in test files (BDD vs AAA, test naming) — defer to project convention.
- Test framework choice (jest vs vitest, pytest vs unittest) — not a review concern.
- Flake detection — explicit non-goal; surface in "What I did NOT check".

## Tool inputs (Phase 2)

No deterministic tool findings route to this axis from the standard battery. The `--mutation-test` opt-in runs `Stryker` / `Pitest` / `mutmut` and routes surviving mutants here as 🟠 Medium.

## Severity calibration

- 🔴 High — `.skip` / `xit` in the diff, weak assertion on a code path that just changed, missing test for a code path with a known bug-class history.
- 🟠 Medium — magic sleep, `Math.random` in tests, strictness flag dropped on a new file.
- 🟢 Low — missing test for a new helper with no existing test convention for similar helpers, snapshot test on stable data.

## Repo-kind branches

| `repo_kind` | Test-location convention |
|-------------|--------------------------|
| `skills` | Tests live at `tests/<skill-name>/` (repo level), NEVER beside source — `skills/<name>/` gets copied verbatim to user installs, so in-tree tests become install bloat. The "missing test beside changed file" heuristic reframes to "missing `tests/<changed-skill>/` directory". Skills with `evals/evals.json` and no unit tests are not double-flagged — evals cover LLM behavior; the universal `tests/_meta/` suite covers structural invariants. |
| `app`, `library` | Tests beside source, in `__tests__/`, `tests/`, or files matching `*.test.*` / `*.spec.*`. |
| `python` | `tests/` at repo or `src/` root; `pytest` conventions. |
| `rust` | `tests/` at crate root + inline `#[cfg(test)] mod tests` blocks. |
| `go` | `_test.go` files beside source. |
| `docs` | Tests rarely apply — link validity routes to the Coherence cross-reference sub-graph (no double-flag). Axis emits zero findings. |
| `monorepo` | Per-sub-project test convention. Axis emits zero findings at the repo root (per-workspace specialization parked for MVP). |
| `unknown` | Existing behavior — heuristics based on `*.test.*` / `*.spec.*` naming. |

## Subagent inputs

- `scope.json` — repo kind, files touched, languages.
- `tool-findings.jsonl` filtered to `axis: tests` — empty by default; populated by `--mutation-test`.
- The diff itself.
- This brief.
- `references/anthropic-verbatim.md` — rubric + false-positive list.
