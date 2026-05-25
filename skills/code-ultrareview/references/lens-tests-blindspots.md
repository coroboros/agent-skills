# Lens: Tests + blind spots (key `tests-blindspots`)

- **Gap** — a code path the surrounding convention implies should have a test, error path, or doc, but doesn't.
- **Weak test** — a test that cannot fail when the business logic it covers changes (asserts a constant, mocks the unit under test, no meaningful assertion).
- **Blind spot** — an unstated assumption in the diff: an unhandled input class, a concurrency assumption, or reliance on possibly-stale library/API knowledge (→ `/find-docs` pointer, not a finding).

## Repo-kind branches

The lens reads `repo_kind` to pick the right test-location convention
before applying its gap-detection heuristic.

| `repo_kind` | Test-location convention |
|-------------|--------------------------|
| `skills` | Tests live at `tests/<skill-name>/` (repo-level), NEVER beside source — see `.claude/rules/repo-conventions.md` § Testing. The "missing test beside changed file" heuristic reframes to "missing `tests/<changed-skill-name>/` directory". `evals/evals.json` per skill is the LLM eval — orthogonal; do not double-flag a skill that has evals but no unit tests. |
| `app`, `library` | Existing behavior — tests beside source, in `__tests__/`, `tests/`, or files matching `*.test.*` / `*.spec.*`. |
| `python` | `tests/` directory at repo or `src/` root; `pytest` conventions. |
| `rust` | `tests/` at crate root + inline `#[cfg(test)] mod tests` blocks. |
| `go` | `_test.go` files beside source. |
| `docs` | Tests rarely apply. Link-validity routes to `coherence-graph`'s cross-reference sub-graph (no double-flag). Lens emits zero findings; summary row renders 🟢 — the `Repo: docs` header line signals the lens did not specialize. |
| `monorepo` | Per-sub-project test convention. Lens emits zero findings at the repo root (per-workspace specialization is parked for MVP); summary row renders 🟢 with the `Repo: monorepo` header carrying context. |
| `unknown` | Existing behavior. |
