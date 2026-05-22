# Code ultrareview — add-rate-limiter

**Base:** 49d9a32 · **Target:** HEAD · **Rule:** feature-merge-base
**Scope:** 6 files · public API · manifest · 2 planning artifacts (1d fresh) · **Estimated wall-clock:** 4m 30s
**Rules baseline:** CLAUDE.md chain + 3 rule files
**Reviewed:** 6 changed files
**Findings:** 3 🔴 · 2 🟠 · 0 🟢 (verified) · 1 unverified

## Lens summary

| Lens | Status | Verified | Unverified | Top finding |
|------|--------|----------|------------|-------------|
| rules | 🔴 | 1 | 0 | console.log for request logging in src/api |
| bugs-drift | 🔴 | 1 | 0 | Window resets on every request — boundary off-by-one |
| docs-version | 🟠 | 1 | 0 | RATE_LIMIT_RPM env var undocumented |
| tests-blindspots | 🟠 | 1 | 0 | No test for concurrent-burst path |
| coherence-graph | 🟢 | 0 | 1 | — |
| derivation | 🔴 | 1 | 0 | AC4 (per-IP allowlist override) GAP |

## Findings

### Verified

Findings with confidence ≥ 80, ordered by severity then confidence.

| # | Lens | Severity | Tier | Location | Conf | Finding | Recommendation |
|---|------|----------|------|----------|------|---------|----------------|
| 1 | rules | High | Important | `src/api/limiter.ts:24` | 95 | New module uses `console.log` for request logging | Use the project logger — rule: "NEVER use console.* in src/api (.claude/rules/logging.md)" |
| 2 | bugs-drift | High | Important | `src/api/limiter.ts:41` | 90 | Window resets on every request — off-by-one on the boundary check `>=` vs `>` | Use `>` so the Nth request in the window is allowed |
| 3 | docs-version | Medium | Important | `README.md:1` | 85 | New `RATE_LIMIT_RPM` env var is undocumented | Add it to the Configuration table |
| 4 | tests-blindspots | Medium | Important | `src/api/limiter.ts:55` | 88 | No test for the concurrent-burst path; empty-IP input unhandled | Add a burst test and guard `ip === ""` |

### Unverified

| # | Lens | Severity | Location | Conf | Finding | Recommendation |
|---|------|----------|----------|------|---------|----------------|
| 1 | coherence-graph | Low | `package.json ↔ marketplace.json` | 70 | `[unverified]` Description divergence | Sub-80 confidence (70) — verify locally before action. |

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

## Derivation coverage

| Field | Value |
|-------|-------|
| Artifacts compared | 2 (`brainstorm-rate-limiter.md` (1d), `spec-rate-limiter.md` (0d)) |
| AC coverage | 3/4 acceptance criteria |
| GAP | 1 (1 high-confidence) |
| SCOPE-ADD | 0 |
| DECISION-OVERRIDE | 0 |
| CONSISTENT | 3 |

**Notable callouts:** AC4 (per-IP allowlist override) — spec mandates the flag; diff omits it. GAP / High.

## Verdict

**Needs work** — 3 🔴 Important (1 in rules, 1 in bugs-drift, 1 in derivation) — fix red before ship.

Drivers:
- 1 in rules
- 1 in bugs-drift
- 1 in derivation

## Action plan

### 🔴 Fix now (3 findings)

```
/apex apply rules fixes (1 finding):
  - src/api/limiter.ts:24 — console.log used for request logging in src/api
      → Use the project logger; rule: "NEVER use console.* in src/api"
```

```
/apex apply bugs-drift fixes (1 finding):
  - src/api/limiter.ts:41 — Window resets on every request (boundary off-by-one on `>=`)
      → Use `>` so the Nth request in the window is allowed
```

```
/apex apply derivation fixes (1 finding):
  - src/api/limiter.ts (GAP) — AC4 (per-IP allowlist override) missing; spec mandates the flag
      → Implement the allowlist override behind the documented env var
```

### 🟠 Fix soon (2 findings)

> No specialized skill installed for docs-version 🟠 — routed to /apex.

```
/apex apply docs-version fixes (1 finding):
  - README.md:1 — RATE_LIMIT_RPM env var undocumented
      → Add it to the Configuration table
```

```
/apex apply tests-blindspots fixes (1 finding):
  - src/api/limiter.ts:55 — No test for concurrent-burst path; empty-IP input unhandled
      → Add a burst test and guard `ip === ""`
```

### Unverified follow-up

```
/apex investigate and decide on the following unverified findings:
  - package.json ↔ marketplace.json — Description divergence [coherence-graph]
```

---

_Report-only. To fix: `/apex -f code-ultrareview.md` or `/oneshot "<finding>"`._
