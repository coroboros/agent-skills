# Code review — add-rate-limiter

**Base:** 49d9a32 · **Target:** HEAD · **Rule:** feature-merge-base
**Rules baseline:** instruction chain + 3 rule files

## Findings

| # | Lens | Severity | Location | Conf | Finding | Recommendation |
|---|------|----------|----------|------|---------|----------------|
| 1 | bugs-drift | High | `src/api/limiter.ts:41` | 90 | Off-by-one on the window boundary | Use `>` not `>=` |

## What looks good

- Token-bucket refill is correct.

<!-- Malformed on purpose: missing the "Deferred to sibling skills" and
     "Verdict" required sections — the schema check must fail loudly. -->
