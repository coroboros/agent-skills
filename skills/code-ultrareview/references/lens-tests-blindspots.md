# Lens: Tests + blind spots (key `tests-blindspots`)

- **Gap** — a code path the surrounding convention implies should have a test, error path, or doc, but doesn't.
- **Weak test** — a test that cannot fail when the business logic it covers changes (asserts a constant, mocks the unit under test, no meaningful assertion).
- **Blind spot** — an unstated assumption in the diff: an unhandled input class, a concurrency assumption, or reliance on possibly-stale library/API knowledge (→ `/find-docs` pointer, not a finding).
