# Code ultrareview — add-rate-limiter

**Base:** 49d9a32 · **Target:** HEAD · **Rule:** feature-merge-base
**Tier:** deep (chosen by audit phase) · **Tier rationale:** public-API touched + manifest delta + test gap
**Token estimate:** 150000 (tier budget) · **Rules baseline:** CLAUDE.md chain + 3 rule files
**Reviewed:** 6 changed files

## Findings

### Verified

Findings with confidence ≥ 80, ordered by severity then confidence.

| # | Lens | Severity | Tier | Location | Conf | Finding | Recommendation |
|---|------|----------|------|----------|------|---------|----------------|
| 1 | rules | High | Important | `src/api/limiter.ts:24` | 95 | New module uses `console.log` for request logging | Use the project logger — rule: "NEVER use console.* in src/api (.claude/rules/logging.md)" |
| 2 | bugs-drift | High | Important | `src/api/limiter.ts:41` | 90 | Window resets on every request — off-by-one on the boundary check `>=` vs `>` | Use `>` so the Nth request in the window is allowed |
| 3 | docs-version | Medium | Important | `README.md:1` | 85 | New `RATE_LIMIT_RPM` env var is undocumented | Add it to the Configuration table |
| 4 | tests-blindspots | Medium | Important | `src/api/limiter.ts:55` | 88 | No test for the concurrent-burst path; empty-IP input unhandled | Add a burst test and guard `ip === ""` |

### Unverified — recommend Deep pass

| # | Lens | Severity | Location | Conf | Finding | Recommendation |
|---|------|----------|----------|------|---------|----------------|
| 1 | coherence-graph | Low | `package.json ↔ marketplace.json` | 70 | `[unverified — recommend Deep pass]` Description divergence | Sub-80 confidence (70) — re-run with -t deep to verify. |

## Deferred to sibling skills

Out-of-lane observations — pointers only, not reviewed here.

- **Security:** the limiter keys on a client-supplied `X-Forwarded-For` header → `/security-review`
- **Performance / simplification:** the in-memory map grows unbounded → `/simplify`

## What looks good

- The token-bucket refill is correct and the unit on `refillRate` matches the docstring.
- Error responses follow the existing `ApiError` pattern in `src/api/errors.ts`.

## Coherence-graph status

| Sub-graph | Status |
|-----------|--------|
| description | fail (1) |
| version | pass |
| capability | pass |
| cross-reference | pass |
| example | pass |
| spec-conformance | skipped — no normative-spec mentions |

## Verdict

**Fix-then-ship** — two High findings (logging rule, boundary off-by-one) must land before merge; the rest can follow.

---

_Report-only. To fix: `/apex -f code-ultrareview.md` or `/oneshot "<finding>"`._
