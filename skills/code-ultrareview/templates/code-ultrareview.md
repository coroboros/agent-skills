# Code ultrareview — {slug}

**Base:** {base} · **Target:** {target} · **Rule:** {rung}
**Scope:** {feature summary from audit_summary.py — e.g., "12 files · public API · normative spec (RFC 6874) · manifest"} · **Estimated wall-clock:** {Nm Ss}
**Rules baseline:** {CLAUDE.md chain + N rule files | skipped — no rules baseline found}
**Reviewed:** {N} changed files{, or: unresolvable — <hint>}
**Findings:** {severity_counts.🔴} 🔴 · {severity_counts.🟠} 🟠 · {severity_counts.🟢} 🟢 (verified) · {unverified count} unverified

_Omit the **Findings** line on a fully clean review._

## Lens summary

Per-lens status snapshot — all six canonical lenses appear, including clean ones. The derivation lens row reads `— skipped (no --reconcile)` when the conditional lens is not run. Status reflects the highest verified severity within the lens: 🔴 if any verified High, else 🟠 if any verified Medium, else 🟢.

| Lens | Status | Verified | Unverified | Top finding |
|------|--------|----------|------------|-------------|
| rules | {lens_summary[0].status} | {N} | {N} | {top_finding or —} |
| bugs-drift | {lens_summary[1].status} | {N} | {N} | {top_finding or —} |
| docs-version | {lens_summary[2].status} | {N} | {N} | {top_finding or —} |
| tests-blindspots | {lens_summary[3].status} | {N} | {N} | {top_finding or —} |
| coherence-graph | {lens_summary[4].status} | {N} | {N} | {top_finding or —} |
| derivation | {lens_summary[5].status} | {N} | {N} | {top_finding or — skipped (no --reconcile)} |

## Findings

### Verified

Findings with confidence ≥ 80, ordered by severity then confidence. Each row carries the visual severity marker (🔴 / 🟠 / 🟢) and the Anthropic tier (Important / Nit / Pre-existing).

| # | Lens | Severity | Tier | Location | Conf | Finding | Recommendation |
|---|------|----------|------|----------|------|---------|----------------|
| 1 | rules | 🔴 High | Important | `path:line` | 95 | What is wrong | What to do — rule: "{verbatim rule line}" |
| 2 | bugs-drift | 🟠 Medium | Important | `path:line` | 85 | … | … |

### Unverified

Findings with confidence < 80 surfaced per A2 (no silent drop). Severity always renders 🟢 — A2 downgrades to Low at routing time. Each row's recommendation states the score so the reader can decide whether to verify locally, strengthen the test, or drop.

| # | Lens | Severity | Location | Conf | Finding | Recommendation |
|---|------|----------|----------|------|---------|----------------|
| 1 | tests-blindspots | 🟢 Low | `path:line` | 65 | `[unverified]` … | Sub-80 confidence (65) — verify locally before action. … |

_If a lens found nothing:_ **Lens N (name): clean.**

## Deferred to sibling skills

Out-of-lane observations — pointers only, not reviewed here.

- **Security:** {one line} → `/security-review`
- **Performance / simplification:** {one line} → `/simplify`
- **Depth / regression risk:** {one line} → `/ultrareview`
- **Possibly-stale API knowledge:** {one line} → `/find-docs`

_Omit any bullet with nothing to point at._

## What looks good

- {Specific positive — a correct edge-case handled, a test that encodes intent}

## Coherence-graph status

Per-sub-graph pass/fail summary when the coherence-graph lens ran. Each row reports `pass`, `fail (N findings)`, or `skipped — <reason>` (e.g. `gh unavailable`, `WebFetch unavailable`).

| Sub-graph | Status |
|-----------|--------|
| description | pass · fail (N) · skipped — <reason> |
| version | pass · fail (N) · skipped — <reason> |
| capability | pass · fail (N) · skipped — <reason> |
| cross-reference | pass · fail (N) · skipped — <reason> |
| example | pass · fail (N) · skipped — <reason> |
| spec-conformance | pass · fail (N) · skipped — <reason> |

## Derivation coverage

_Present only when the derivation lens ran (`--reconcile` resolved to non-empty input). Reports artifact coverage + classification counts._

| Field | Value |
|-------|-------|
| Artifacts compared | {N} ({list with freshness — e.g. `brainstorm-foo.md (2d)`, `spec-bar.md (5d)`}) |
| AC coverage | {verified}/{total} acceptance criteria |
| GAP | {N} ({N high-confidence}) |
| SCOPE-ADD | {N} |
| DECISION-OVERRIDE | {N} |
| CONSISTENT | {N} |

**Notable callouts:** {top 1–3 highest-severity findings, one line each}

_When freshness > 90 days for an artifact, only the row above shows it — no per-claim findings emit. Per-repo `.derivation-ignore` overrides supply finer control._

## Verdict

**{verdict.label}** — {verdict.rationale}

_When `verdict.drivers` has ≥ 2 entries, render as a bullet list below the line above:_

Drivers:
- {driver 1}
- {driver 2}

Algorithm: any 🔴 + Important → Needs work; else any 🟠 + Important → Fix-then-ship; else Ship. Unverified findings are excluded. Full spec: `references/verdict-logic.md`.

## Action plan

_When `action_plan.zero_findings` is true, render a single line in place of this section:_

🟢 All clear — no action plan needed.

_Otherwise render one block per cluster in `action_plan.clusters`, in the order returned (🔴 → 🟠 → 🟢 cross-lens). When `cluster.fallback_used` is true, prepend the blockquote note shown below._

### {cluster.severity_label}

> No specialized skill installed for {cluster.lens} — routed to {cluster.command}.

```
{cluster.prompt_text}
```

_When `action_plan.unverified_block` is non-null, render a separate sub-section after all clusters:_

### Unverified follow-up

```
{action_plan.unverified_block.prompt_text}
```

Routing chain (preferred → fallback) lives in `references/skill-routing.md`. Final fallback is always `/apex`.

## --apply-safe summary

_Present only when `--apply-safe` was used._

| Writer | Status | Targets |
|--------|--------|---------|
| version_sync | applied · skipped · no-op · refusing | `package.json`, `marketplace.json` |
| description_sync | applied · skipped · no-op · refusing: partial-agreement | `package.json`, `marketplace.json` |
| failing_test_writer | applied · skipped · refusing: existing-test | `tests/<bug-id>.{py,ts}` |

---

_Report-only by default. To fix: `/apex -f ~/.claude/output/{project}/code-ultrareview/code-ultrareview-{slug}.md` or `/oneshot "<finding>"`. Opt-in `--apply-safe` writes manifest sync + failing tests with diff preview + per-file confirmation._
