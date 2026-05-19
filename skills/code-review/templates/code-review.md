# Code review — {slug}

**Base:** {base} · **Target:** {target} · **Rule:** {rung}
**Rules baseline:** {CLAUDE.md chain + N rule files | skipped — no rules baseline found}
**Reviewed:** {N} changed files{, or: unresolvable — <hint>}

## Findings

Ordered by severity, then confidence. Findings below the confidence threshold are dropped, not listed.

| # | Lens | Severity | Location | Conf | Finding | Recommendation |
|---|------|----------|----------|------|---------|----------------|
| 1 | rules | High | `path:line` | 95 | What is wrong | What to do — rule: "{verbatim rule line}" |
| 2 | bugs-drift | Medium | `path:line` | 85 | … | … |

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

## Verdict

**{Ship | Fix-then-ship | Needs work}** — {one-line rationale}

---

_Report-only. To fix: `/apex -f ~/.claude/output/{project}/code-review/code-review-{slug}.md` or `/oneshot "<finding>"`._
