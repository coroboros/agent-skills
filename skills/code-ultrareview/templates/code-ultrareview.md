# Code ultrareview — {slug}

**Base:** `{base}` · **Target:** `{target}` · **Rule:** {rung}
**Repo:** {repo_kind} · **Languages:** {languages}
**Rules baseline:** {instruction chain + N files | none — Style used observable repository conventions}
**Reviewed:** {N} changed file(s)
**Coherence axis:** {active | inactive}
**Findings:** {n_red} 🔴 · {n_orange} 🟠 · {n_green} 🟢 (verified) · {n_unverified} unverified

> **Section discipline (mandatory).** Every `##` heading below is canonical — render it verbatim, including the emoji prefix and the `---` separator above it. Do not rename, merge, reorder, or invent sections. Every severity sub-section inside `## 🔎 Findings` renders even when its count is `0` (body: `_None._`). The model is a formatter here, not an editor.
>
> **Terminal echo is mandatory.** The full report below prints to the chat-terminal on every invocation. The `-s` flag is purely additive — it writes the same bytes to `~/.agents/output/{project}/code-ultrareview/code-ultrareview-{slug}.md`. It does not gate, truncate, or summarise what the user sees in chat. Terminal output and saved file are byte-for-byte identical.

---

## 📋 Axis summary

Per-axis status snapshot — all 8 canonical axes appear, including clean ones. The Coherence row reads `— inactive (no metadata in diff)` when the conditional axis did not launch. Status reflects the highest verified severity in the axis (🔴 → 🟠 → 🟢).

| Axis | Status | Verified | Unverified | Top finding |
|------|--------|----------|------------|-------------|
| correctness | {🔴\|🟠\|🟢} | {N} | {N} | {top_finding_or_dash} |
| simplification | {…} | {N} | {N} | {…} |
| tests | {…} | {N} | {N} | {…} |
| documentation | {…} | {N} | {N} | {…} |
| style | {…} | {N} | {N} | {…} |
| intent | {…} | {N} | {N} | {…} |
| design-api | {…} | {N} | {N} | {…} |
| performance | {…} | {N} | {N} | {…} |
| coherence | {🔴\|🟠\|🟢\|— inactive (no metadata in diff)} | {N} | {N} | {…} |

---

## 🔎 Findings

Verified findings split by severity into three sub-sections, each prefixed by its canonical emoji. Row IDs carry a per-section prefix (`H1`, `H2`, …, `M1`, …, `L1`, …). Unverified findings (confidence < 80, A2-routed) render as a fourth sub-section, prefixed `⚠️` and ID-prefixed `U1`, `U2`, …

Render every sub-section in this exact order, including when the count is zero (body: `_None._`). The Severity column is dropped from the row tables — severity lives in the sub-section heading.

### 🔴 High ({count} findings)

| # | Axis | Tier | Location | Conf | Finding | Recommendation |
|---|------|------|----------|------|---------|----------------|
| H1 | correctness | Important | `path:line` | 95 | What is wrong | What to do — rule: "{verbatim rule line}" |

### 🟠 Medium ({count} findings)

| # | Axis | Tier | Location | Conf | Finding | Recommendation |
|---|------|------|----------|------|---------|----------------|
| M1 | design-api | Important | `path:line` | 85 | … | … |

### 🟢 Low ({count} findings)

| # | Axis | Tier | Location | Conf | Finding | Recommendation |
|---|------|------|----------|------|---------|----------------|
| L1 | documentation | Nit | `path:line` | 85 | … | … |

### ⚠️ Unverified ({count} findings)

Findings with confidence < 80 surfaced per A2 (no silent drop). Severity is downgraded to Low at routing time. Each row's recommendation states the score so the reader can decide whether to verify locally, strengthen the test, or drop.

| # | Axis | Location | Conf | Finding | Recommendation |
|---|------|----------|------|---------|----------------|
| U1 | tests | `path:line` | 65 | `[unverified]` … | Sub-80 confidence (65) — verify locally before action. Validator: … |

---

## ✅ What looks good

- {Specific positive — a correct edge-case handled, a test that encodes intent}

_Body reads `_None surfaced this run._` when the positives feed is empty._

---

## ⚖️ Verdict

**{verdict.label}** — {verdict.rationale}

Drivers:
- {driver 1}
- {driver 2}

Algorithm: any 🔴 + Important → Needs work; else any 🟠 + Important → Fix-then-ship; else Ship. Unverified findings are excluded.

---

## 🧰 Tools skipped

- `{tool}` — {reason}

_Body reads `_None — every applicable analyzer completed successfully._` when no analyzer was recorded as not applicable._

---

## 🛡️ What I did NOT check

Coverage boundaries — explicit by design.

- **Security** — Defers to `/security-review` or `https://github.com/anthropics/claude-code-security-review`. Distinct concern with its own deeper review pattern.
- **Runtime performance** — Static patterns only (N+1, sync I/O). No benchmarks, no flamegraphs, no memory traces.
- **Flaky test detection** — Structural smells only. Flake requires repeated runs the skill does not perform.

---

## 📐 Derivation coverage

_Present only with a verified `--reconcile` artifact. Synthesis generates this section from the artifact bound to the axis run; a separate summary file is unnecessary._

| Artifact | Freshness (days) | Claims extracted |
| --- | --- | --- |
| {artifact path} | {days or unknown} | {N} |

Artifacts supplied: {N}. Claims extracted: {N}. Claims submitted to Intent: {N}.

| Retained finding classification | Count |
| --- | --- |
| GAP | {N} |
| SCOPE-ADD | {N} |
| DECISION-OVERRIDE | {N} |

Extraction and submission counts are input coverage. Per-claim verified and CONSISTENT totals are unavailable from the axis result schema; zero retained findings does not measure those totals.

---

## 🪛 --apply-safe summary

_Present only when `--apply-safe` was used._

| Writer | Status | Targets |
|--------|--------|---------|
| version_sync | applied · skipped · no-op · refusing | `package.json`, `marketplace.json` |
| description_sync | applied · skipped · no-op · refusing: partial-agreement | `package.json`, `marketplace.json` |
| failing_test_writer | applied · skipped · refusing | {reviewed project-relative test path} |

---

_Report-only by default. To fix: `/apex -f ~/.agents/output/{project}/code-ultrareview/code-ultrareview-{slug}.md` or `/oneshot "<finding>"`. Opt-in `--apply-safe` writes manifest sync + failing tests with diff preview + per-file confirmation._
