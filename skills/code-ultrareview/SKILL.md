---
name: code-ultrareview
description: In-session adaptive code review — audit-first three tiers (Standard / Deep / Ultra, never light), parallel lens subagents, coherence-graph lens for cross-artifact drift (README ↔ package.json ↔ marketplace ↔ About ↔ topics ↔ CHANGELOG ↔ git tag), and gated `--apply-safe` remediation at the Ultra tier. Report-only by default; defers security/performance/simplification to owning skills. Use before a commit or PR for a fresh-eyes pass calibrated to the diff's risk profile.
when_to_use: User-invoked (via /code-ultrareview) at the end of a coding session, before a commit, or before opening a PR. The audit phase auto-calibrates tier (Standard floor; Deep adds spec-conformance + iteration; Ultra adds build + execute + property-fuzz + `--apply-safe` writers); user can override with `-t`. Invoke when you'd say "review my changes", "did I miss anything", "check before I commit", "drift / gaps / blind spots", "manifest coherence", "spec conformance", "does this follow CLAUDE.md / the rules". NOT a security audit (use /security-review); NOT performance or simplification (use /simplify); NOT Anthropic's remote billed command (use /ultrareview for that — distinct namespace, distinct posture). Report-only by default; opt-in `--apply-safe` at Ultra tier writes manifest-version sync, structured-field description sync (full-agreement guard), and one failing test per confirmed bug — never production logic.
argument-hint: "[-t auto|standard|deep|ultra] [-b <ref>] [--apply-safe] [--include-prose] [--remote] [-s] [-S]"
model: opus
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
disable-model-invocation: true
metadata:
  author: coroboros
  sources:
    - github.com/anthropics/knowledge-work-plugins/tree/main/engineering/skills/code-review
    - github.com/anthropics/claude-plugins-official/tree/main/plugins/code-review
---

# Code ultrareview

> **In-session adaptive code review.** Audit-first calibration picks Standard / Deep / Ultra (never light). Distinct from Anthropic's built-in `/ultrareview` remote command — different namespace (skill vs built-in), different posture (in-session on your subscription vs remote sandbox + billed).

<!-- canonical:writing-rules:start -->
## Important — Writing rules

These rules govern every prose artifact this skill emits — READMEs, CHANGELOGs, commit messages, PR bodies, release notes, doc paragraphs, non-trivial comments. Apply them at draft time, verify before output.

- Match the surrounding style — punctuation, capitalization, backtick conventions, em-dash vs parens, bullet style.
- Every sentence changes the reader's understanding. Cut it otherwise.
- Front-load the verb — "Creates", not "This helps you create".
- Concrete over abstract. Lists for ≥3 enumerable items.
- Assert positively. Reserve negation for real constraints (`NEVER commit secrets`).
- No marketing words: powerful, robust, seamlessly, leverage, unlock, comprehensive, delightful.
- No AI tells: delve, tapestry, intricate, pivotal, testament, underscore, crucial, garner, showcase, additionally, moreover, furthermore, indeed.
- After drafting English prose, invoke `/humanize-en` if installed.
<!-- canonical:writing-rules:end -->

## Objective

A fresh-eyes pass over what changed, calibrated to the diff's risk profile. An audit phase extracts signals from the diff (LOC, public-API touch, normative-spec claims, manifest delta, test-coverage delta, pre-1.0 proximity, security surface) and routes to one of three tiers — Standard, Deep, or Ultra. Standard runs five lens subagents in parallel (`rules`, `bugs-drift`, `docs-version`, `tests-blindspots`, `coherence-graph`); Deep adds spec-conformance plus iteration on sub-80 findings; Ultra adds build + execute verification, property-fuzz harness synthesis from spec grammar, and `--apply-safe` writers. Findings are confidence-scored 0–100 and surfaced — sub-80 are routed to a deeper pass rather than silent-dropped. The skill writes no code by default and owns no checklist of its own — every criterion is read at runtime from the project. Anything outside its lane (security, performance, simplification) becomes a one-line pointer to the skill that owns it, never a finding.

## Parameters

| Flag | Behavior |
|------|----------|
| `-t auto\|standard\|deep\|ultra` | Tier selection. `auto` (default) runs the audit phase to pick; explicit values override |
| `-s` | Save the report to `~/.claude/output/{project}/code-ultrareview/code-ultrareview-{slug}.md` (global; `{slug}` = kebab of the branch or a short description, ≤5 words) |
| `-S` | Force no-save (override an ambient save mode) |
| `-b <ref>` | Override the review base (skip auto-detection) |
| `--apply-safe` | Ultra tier only: auto-apply low-risk fixes (manifest version sync, structured-field description sync with full-agreement guard, one failing test per confirmed bug). Diff preview + per-file confirmation prompt before any write. Never modifies production logic |
| `--include-prose` | Coherence-graph lens compares README freeform paragraphs as well (default: structured fields only — `package.json`, `marketplace.json`, SKILL.md frontmatter, GitHub About, topics) |
| `--remote` | Reserved for phase-2 remote-sandbox escalation; current MVP is in-session |

`{slug}` = kebab of the branch name or a short description (≤5 words); `{project}` = kebab-cased basename of the git toplevel (else cwd) — see `.claude/rules/repo-conventions.md` § Output paths. Lowercase enables, uppercase disables — repo-wide convention. No `-f`: this skill is a producer, not a consumer.

```bash
/code-ultrareview                              # auto tier from audit phase, report
/code-ultrareview -s                           # save the report for /apex -f
/code-ultrareview -b origin/main               # review HEAD against an explicit base
/code-ultrareview -t ultra                     # force Ultra tier
/code-ultrareview -t ultra --apply-safe        # Ultra + low-risk fixes (gated)
/code-ultrareview --include-prose              # also compare README freeform prose
```

## What it reviews

Resolve the target deterministically, and always print it in the report header so the scope is never silent:

1. **Dirty working tree** → everything not yet committed: tracked changes vs `HEAD` (`git diff HEAD` — staged and unstaged) **plus** untracked files (`git ls-files --others --exclude-standard`, each read in full). A new file written this session but not yet `git add`-ed is part of the session — never skip untracked, or the review silently misses whole new modules.
2. **Clean tree** → branch-vs-base. Read the project's rule files (below) first; if a source/base branch is declared there (e.g., a `Source branch` line in `CLAUDE.md` or `.claude/rules/git-conventions.md`), pass it as `-b` to the resolver. Otherwise run `scripts/resolve_base.sh` and use its ladder.

The review set every lens examines: **clean tree** → `git diff <base> <target>` (two-dot — the resolver guarantees `base` is a diffable ancestor or the empty tree, so this is always correct, with no noise from commits the base gained in parallel); **dirty tree** → `git diff HEAD` plus the untracked files above.

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/resolve_base.sh" [-b <ref>]
# → RESULT: base=<ref> target=<ref> rule=<rung>   (exit 0)
# → RESULT: rule=unresolvable hint=<text>          (exit 2 — report it, do not guess)
```

The **rule hierarchy** every lens reviews against, read fresh each run:

- Repo `CLAUDE.md` chain (root + any nested `CLAUDE.md` in changed directories)
- `.claude/rules/*.md` (project)
- `~/.claude/rules/*.md` (global)

## The five lenses

One read-only subagent per lens. Operational definitions, subagent briefs, and the confidence rubric live in `references/lenses.md` — read it before dispatching.

1. **Rules compliance** (key `rules`) — new violations of the rule hierarchy, citing the exact rule line.
2. **Bugs + drift** (key `bugs-drift`) — logic errors on changed lines; code no longer matching its own doc/comment/claim or a sibling pattern. When the diff/README/CLAUDE.md cites a named normative spec (RFC, WHATWG, ISO/IEC, OpenAPI), the lens fetches the spec, quotes the governing clause, and diffs the code against it (A1).
3. **Docs + version** (key `docs-version`) — user-visible behavior changed without a doc/version update.
4. **Tests + blind spots** (key `tests-blindspots`) — missing tests the convention implies, tests that can't fail, unstated assumptions.
5. **Coherence-graph** (key `coherence-graph`) — cross-artifact drift across six sub-graphs: description, version, capability, cross-reference, example, spec-conformance. Default to structured fields only; `--include-prose` extends to README freeform.

These five keys are canonical — the report table, the evals, and the pipeline contract (`tests/_pipeline/_contracts.py`) all key off them.

## How it runs

```
Phase 1 — AUDIT  (always-on, ~30–60s, 1 Haiku subagent)
  signals: LOC, files, public-API touched, spec claims, manifest delta,
           pre-1.0 proximity, test-coverage delta, security surface
  output:  tier (standard | deep | ultra) + rationale + token estimate
  user can override with -t

Phase 2 — DISPATCH  (parallel lens subagents per tier)
  Standard:  rules + bugs-drift + docs-version + tests-blindspots + coherence-graph
  Deep:      Standard + spec-conformance + iteration on sub-80 findings
  Ultra:     Deep + property-fuzz harness + build/execute + --apply-safe writers

Phase 3 — AGGREGATION  (1 synthesizer subagent)
  dedupe by (location, finding-key); severity tiers
  (Important / Nit / Pre-existing); sub-80 surfaced as
  "unverified — recommend Deep pass" (never silent-dropped — A2)
```

Audit-phase dispatch, JSON signal schema, weight table, and tier thresholds live in `references/audit-phase.md` — read before invoking. Lens briefs live in `references/lenses.md`.

1. Resolve the target (above); read the rule hierarchy; run the audit phase to pick the tier (unless `-t` is set).
2. Launch the lens subagents **in one message** (parallel, read-only). Each is given the resolved `base`/`target` (or "dirty tree") and the rule-hierarchy paths, then reconstructs its own review set read-only per `references/lenses.md` (never skipping untracked files), with its lens brief and the exclusion contract.
3. Aggregate findings; score each 0–100 (rubric in `references/lenses.md`); sub-80 routed (not dropped) — per A2 in the postmortem.
4. At Ultra tier with `--apply-safe`, optionally write manifest version sync, structured-field description sync (full-agreement guard), and one failing test per confirmed bug — diff preview + per-file confirmation prompt before any write.
5. Emit the report from `templates/code-ultrareview.md`. Save to the `-s` path when set, and report its fully-expanded absolute path to the user (no tilde, no magic).

## Deferral spine

Out-of-lane findings are never reported as findings — emit a single pointer line and move on:

- Security → `/security-review`
- Performance / optimization / simplification → `/simplify`
- Cases where in-session Ultra is inadequate (need remote multi-agent fleet with build-and-run) → Anthropic's `/ultrareview` (distinct from this skill; remote sandbox, billed per run)
- Reliance on possibly-stale library/API knowledge → `/find-docs`

## Graceful degradation

No `CLAUDE.md`, no `.claude/rules`, no `~/.claude/rules` → skip lens 1, state `Lens 1 (rules): skipped — no rules baseline found` in the report header, run the other four. The skill stays useful on any repo.

Coherence-graph lens degrades sub-graph by sub-graph: if `gh` CLI is unavailable, the description / topics sub-graphs are skipped and the header notes the skip; if `WebFetch` is unavailable for the spec-conformance sub-graph at Deep/Ultra, the finding surfaces as `[unverified — needs network]` rather than dropping.

## Report-only by default

This skill writes no code by default. After the report, bridge to the fix pass:

- `/apex -f ~/.claude/output/{project}/code-ultrareview/code-ultrareview-{slug}.md` — structured fix workstream (requires `-s`; pass the absolute path the report printed).
- `/oneshot "<finding>"` — single quick fix (manual; `/oneshot` takes a description, not a file).

Opt-in `--apply-safe` at Ultra tier writes only:
- Manifest version sync (mechanical, idempotent — aligns all structured version sources to the most-recently-touched value).
- Structured-field description sync (full-agreement guard — refuses unless every present source agrees on the new value).
- One focused failing test per confirmed bug (additive — never modifies existing tests).

Every write shows a diff preview and prompts for confirmation per file. Production logic is never modified — that belongs to `/simplify` and future `/modernize`.

## Rules

- **Report-only by default.** No code changes unless `--apply-safe` is set; even then, only the three write classes above.
- **Stay in lane.** Security, performance, simplification → pointer only, never a finding.
- **Only new findings.** Issues the diff introduces, not pre-existing ones (Pre-existing tier accepted for context).
- **No silent drop.** Sub-80 findings surface as `[unverified — recommend Deep pass]` with rationale — never omitted (A2).
- **Fail loud.** A lens that cannot run (unresolvable base, missing baseline, fetch failure) is stated in the header or surfaced as a finding, never silently skipped.
- **Cite precisely.** Every finding carries `file:line`; rule findings quote the violated rule line verbatim; spec-conformance findings quote the governing clause.
