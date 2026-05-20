# Code ultrareview — {slug}

**Base:** {base} · **Target:** {target} · **Rule:** {rung}
**Scope:** {feature summary from audit_summary.py — e.g., "12 files · public API · normative spec (RFC 6874) · manifest"} · **Estimated wall-clock:** {Nm Ss}
**Rules baseline:** {CLAUDE.md chain + N rule files | skipped — no rules baseline found}
**Reviewed:** {N} changed files{, or: unresolvable — <hint>}

## Findings

### Verified

Findings with confidence ≥ 80, ordered by severity then confidence. Each row also carries the Anthropic tier (Important / Nit / Pre-existing) in the synthesizer's metadata.

| # | Lens | Severity | Tier | Location | Conf | Finding | Recommendation |
|---|------|----------|------|----------|------|---------|----------------|
| 1 | rules | High | Important | `path:line` | 95 | What is wrong | What to do — rule: "{verbatim rule line}" |
| 2 | bugs-drift | Medium | Important | `path:line` | 85 | … | … |

### Unverified — recommend Deep pass

Findings with confidence < 80 surfaced per A2 (no silent drop). Each is prefixed `[unverified — recommend Deep pass]`; rerun with `-t deep` to verify via build iteration.

| # | Lens | Severity | Location | Conf | Finding | Recommendation |
|---|------|----------|----------|------|---------|----------------|
| 1 | tests-blindspots | Low | `path:line` | 65 | `[unverified — recommend Deep pass]` … | Sub-80 confidence (65) — re-run with -t deep to verify. … |

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

## Verdict

**{Ship | Fix-then-ship | Needs work}** — {one-line rationale}

## --apply-safe summary

_Present only when `--apply-safe` was used._

| Writer | Status | Targets |
|--------|--------|---------|
| version_sync | applied · skipped · no-op · refusing | `package.json`, `marketplace.json` |
| description_sync | applied · skipped · no-op · refusing: partial-agreement | `package.json`, `marketplace.json` |
| failing_test_writer | applied · skipped · refusing: existing-test | `tests/<bug-id>.{py,ts}` |

---

_Report-only by default. To fix: `/apex -f ~/.claude/output/{project}/code-ultrareview/code-ultrareview-{slug}.md` or `/oneshot "<finding>"`. Opt-in `--apply-safe` writes manifest sync + failing tests with diff preview + per-file confirmation._
