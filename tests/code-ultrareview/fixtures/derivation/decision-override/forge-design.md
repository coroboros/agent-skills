# Forge — decision-override fixture

A forge plan that resolves decisions; the diff (out of band) overrides one.

## Decisions resolved

- **Storage backend**: SQLite (single-file, embedded).
- **Concurrency**: single-writer queue (no locks).
- **Auth**: token-bearer headers only, no cookies.
