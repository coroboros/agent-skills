# Code ultrareview — add-rate-limiter

**Base:** `49d9a32` · **Target:** `HEAD` · **Rule:** feature-merge-base
**Repo:** app · **Languages:** typescript, json
**Rules baseline:** instruction chain + 3 files
**Reviewed:** 6 changed file(s)
**Coherence axis:** active
**Findings:** 3 🔴 · 2 🟠 · 0 🟢 (verified) · 1 unverified

> **Section discipline (mandatory).** Every `##` heading below is canonical — render it verbatim, including the emoji prefix and the `---` separator above it. Do not rename, merge, reorder, or invent sections. Every severity sub-section inside `## 🔎 Findings` renders even when its count is `0` (body: `_None._`). The model is a formatter here, not an editor.
>
> **Terminal echo is mandatory.** The full report below prints to the chat-terminal on every invocation. The `-s` flag is purely additive — it writes the same bytes to `~/.agents/output/{project}/code-ultrareview/code-ultrareview-{slug}.md`. It does not gate, truncate, or summarise what the user sees in chat. Terminal output and saved file are byte-for-byte identical.

---

## 📋 Axis summary

Per-axis status snapshot — all 8 canonical axes appear, including clean ones. The Coherence row reads `— inactive (no metadata in diff)` when the conditional axis did not launch.

| Axis | Status | Verified | Unverified | Top finding |
|------|--------|----------|------------|-------------|
| correctness | 🔴 | 1 | 0 | Window resets on every request — off-by-one on the boundary check |
| simplification | 🟢 | 0 | 0 | — |
| tests | 🟠 | 1 | 0 | No test for the concurrent-burst path; empty-IP input unhandled |
| documentation | 🟠 | 1 | 0 | New `RATE_LIMIT_RPM` env var is undocumented in the Configuration table |
| style | 🔴 | 1 | 0 | New module uses `console.log` for request logging in src/api |
| intent | 🔴 | 1 | 0 | Per-IP allowlist override absent from diff — spec mandated it |
| design-api | 🟢 | 0 | 0 | — |
| performance | 🟢 | 0 | 0 | — |
| coherence | 🟢 | 0 | 1 | — |

---

## 🔎 Findings

Verified findings split by severity into three sub-sections, each prefixed by its canonical emoji. Row IDs carry a per-section prefix (`H1`, `H2`, …, `M1`, …, `L1`, …). Unverified findings (confidence < 80, A2-routed) render as a fourth sub-section, prefixed `⚠️` and ID-prefixed `U1`, `U2`, …

### 🔴 High (3 findings)

| # | Axis | Tier | Location | Conf | Finding | Recommendation |
|---|------|------|----------|------|---------|----------------|
| H1 | correctness | Important | `src/api/limiter.ts:41` | 90 | Window resets on every request — off-by-one on the boundary check `>=` vs `>` | Use `>` so the Nth request in the window is allowed |
| H2 | style | Important | `src/api/limiter.ts:24` | 95 | New module uses `console.log` for request logging | Use the project logger — rule: "NEVER use console.* in src/api (.claude/rules/logging.md)" |
| H3 | intent | Important | `src/api/limiter.ts` | 90 | Per-IP allowlist override absent from diff — spec mandates the flag | Implement the allowlist override behind the documented env var |

### 🟠 Medium (2 findings)

| # | Axis | Tier | Location | Conf | Finding | Recommendation |
|---|------|------|----------|------|---------|----------------|
| M1 | tests | Important | `src/api/limiter.ts:55` | 88 | No test for the concurrent-burst path; empty-IP input unhandled | Add a burst test and guard `ip === ""` |
| M2 | documentation | Important | `README.md:1` | 85 | New `RATE_LIMIT_RPM` env var is undocumented in the Configuration table | Add it to the Configuration table |

### 🟢 Low (0 findings)

_None._

### ⚠️ Unverified (1 finding)

Findings with confidence < 80 surfaced per A2 (no silent drop). Severity is downgraded to Low at routing time. Each row's recommendation states the score so the reader can decide whether to verify locally, strengthen the test, or drop.

| # | Axis | Location | Conf | Finding | Recommendation |
|---|------|----------|------|---------|----------------|
| U1 | coherence | `package.json:5` | 70 | `[unverified]` Description divergence between `package.json` and `marketplace.json` | Sub-80 confidence (70) — verify locally before action. |

---

## ✅ What looks good

- The token-bucket refill is correct and the unit on `refillRate` matches the docstring.
- Error responses follow the existing `ApiError` pattern in `src/api/errors.ts`.

---

## ⚖️ Verdict

**Needs work** — 3 🔴 Important (1 in correctness, 1 in style, 1 in intent) — fix red before ship.

Drivers:
- 1 in correctness
- 1 in style
- 1 in intent

Algorithm: any 🔴 + Important → Needs work; else any 🟠 + Important → Fix-then-ship; else Ship. Unverified findings are excluded.

---

## 🧰 Tools skipped

_None — every applicable analyzer completed successfully._

---

## 🛡️ What I did NOT check

Coverage boundaries — explicit by design.

- **Security** — Defers to `/security-review` or `https://github.com/anthropics/claude-code-security-review`. Distinct concern with its own deeper review pattern. The limiter keys on a client-supplied `X-Forwarded-For` header — worth a security pass.
- **Runtime performance** — Static patterns only (N+1, sync I/O). No benchmarks, no flamegraphs, no memory traces. The in-memory map grows unbounded; profile under load.
- **Flaky test detection** — Structural smells only. Flake requires repeated runs the skill does not perform.

---

_Report-only by default. To fix: `/apex -f ~/.agents/output/{project}/code-ultrareview/code-ultrareview-{slug}.md` or `/oneshot "<finding>"`. Opt-in `--apply-safe` writes manifest sync + failing tests with diff preview + per-file confirmation._
