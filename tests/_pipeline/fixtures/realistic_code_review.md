# Code review — add-rate-limiter

**Base:** 49d9a32 · **Target:** HEAD · **Rule:** feature-merge-base
**Rules baseline:** CLAUDE.md chain + 3 rule files
**Reviewed:** 6 changed files

## Findings

Ordered by severity, then confidence. Findings below the confidence threshold are dropped, not listed.

| # | Lens | Severity | Location | Conf | Finding | Recommendation |
|---|------|----------|----------|------|---------|----------------|
| 1 | rules | High | `src/api/limiter.ts:24` | 95 | New module uses `console.log` for request logging | Use the project logger — rule: "NEVER use console.* in src/api (.claude/rules/logging.md)" |
| 2 | bugs-drift | High | `src/api/limiter.ts:41` | 90 | Window resets on every request — off-by-one on the boundary check `>=` vs `>` | Use `>` so the Nth request in the window is allowed |
| 3 | docs-version | Medium | `README.md:1` | 85 | New `RATE_LIMIT_RPM` env var is undocumented | Add it to the Configuration table |
| 4 | tests-blindspots | Medium | `src/api/limiter.ts:55` | 88 | No test for the concurrent-burst path; empty-IP input unhandled | Add a burst test and guard `ip === ""` |

## Deferred to sibling skills

Out-of-lane observations — pointers only, not reviewed here.

- **Security:** the limiter keys on a client-supplied `X-Forwarded-For` header → `/security-review`
- **Performance / simplification:** the in-memory map grows unbounded → `/simplify`

## What looks good

- The token-bucket refill is correct and the unit on `refillRate` matches the docstring.
- Error responses follow the existing `ApiError` pattern in `src/api/errors.ts`.

## Verdict

**Fix-then-ship** — two High findings (logging rule, boundary off-by-one) must land before merge; the rest can follow.

---

_Report-only. To fix: `/apex -f code-review.md` or `/oneshot "<finding>"`._
