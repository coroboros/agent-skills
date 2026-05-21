# Spec — stale-artifact fixture

The fixture exists so the test can backdate its mtime to >90 days. The
derivation lens should emit only the artifact summary, no per-claim
finding rows.

## Acceptance criteria

- [ ] AC1: legacy claim from a stale spec — should not produce a finding
- [ ] AC2: another stale claim
