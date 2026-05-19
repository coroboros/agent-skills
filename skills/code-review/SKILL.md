---
name: code-review
description: Report-only session-end code review with fresh eyes. Surfaces bugs, drift, gaps, doc/version staleness, missing tests, blind spots, and CLAUDE.md + local/global rule violations introduced by the working tree or branch. Dispatches parallel read-only review subagents, confidence-scores findings, and defers security/performance/simplification to their owning skills. Use before a commit or PR, or whenever you want an independent audit of a session's changes.
when_to_use: User-invoked (via /code-review) at the end of a coding session, before a commit, or before opening a PR — for an independent fresh-eyes pass over what changed. Invoke when you'd say "review my changes", "did I miss anything", "check before I commit", "drift / gaps / blind spots", "does this follow CLAUDE.md / the rules". NOT a security audit (use /security-review), NOT performance or simplification (use /simplify), NOT a deep multi-agent pre-merge pass (use /ultrareview). Report-only — never edits code; hand findings to /apex or /oneshot.
argument-hint: "[-s] [-S] [-b <ref>]"
model: opus
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
disable-model-invocation: true
metadata:
  author: coroboros
  sources:
    - "knowledge-work-plugins — engineering/skills/code-review (review-dimension framing, report shape)"
    - "Anthropic Claude Code — plugins/code-review (parallel independent agents + 0–100 confidence scoring engine)"
---

# Code review

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

A fresh-eyes pass over what a session changed. Four read-only subagents review the diff against the project's own rule hierarchy and conventions, findings are confidence-scored and filtered, and a prioritized report is emitted. The skill writes no code and owns no checklist of its own — every criterion is read at runtime from the project, so it stays current with zero maintenance. Anything outside its lane (security, performance, simplification) becomes a one-line pointer to the skill that owns it, never a finding.

## Parameters

| Flag | Behavior |
|------|----------|
| `-s` | Save the report to `.claude/output/code-review/{slug}/code-review.md` |
| `-S` | Force no-save (override an ambient save mode) |
| `-b <ref>` | Override the review base (skip auto-detection) |

`{slug}` is kebab-case from the branch or a short description (max 5 words). Lowercase enables, uppercase disables — repo-wide convention. No `-f`: this skill is a producer, not a consumer.

```bash
/code-review                 # auto-detect what changed, report
/code-review -s              # also save the report for /apex -f
/code-review -b origin/main  # review HEAD against an explicit base
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

## The four lenses

One read-only subagent per lens. Operational definitions, subagent briefs, and the confidence rubric live in `references/lenses.md` — read it before dispatching.

1. **Rules compliance** (key `rules`) — new violations of the rule hierarchy, citing the exact rule line.
2. **Bugs + drift** (key `bugs-drift`) — logic errors on changed lines; code no longer matching its own doc/comment/claim or a sibling pattern.
3. **Docs + version** (key `docs-version`) — user-visible behavior changed without a doc/version update.
4. **Tests + blind spots** (key `tests-blindspots`) — missing tests the convention implies, tests that can't fail, unstated assumptions.

These four keys are canonical — the report table, the evals, and the pipeline contract (`tests/_pipeline/_contracts.py`) all key off them.

## How it runs

1. Resolve the target (above); read the rule hierarchy.
2. Launch the four lens subagents **in one message** (parallel, read-only). Each is given the resolved `base`/`target` (or "dirty tree") and the rule-hierarchy paths, then reconstructs its own review set read-only per `references/lenses.md` (never skipping untracked files), with its lens brief and the exclusion contract.
3. Aggregate findings; score each 0–100 (rubric in `references/lenses.md`); drop everything below the threshold.
4. Emit the report from `templates/code-review.md`. Save to the `-s` path when set.

## Deferral spine

Out-of-lane findings are never reported as findings — emit a single pointer line and move on:

- Security → `/security-review`
- Performance / optimization / simplification → `/simplify`
- Depth or regression risk warranting a deep pass → `/ultrareview`
- Reliance on possibly-stale library/API knowledge → `/find-docs`

## Graceful degradation

No `CLAUDE.md`, no `.claude/rules`, no `~/.claude/rules` → skip lens 1, state `Lens 1 (rules): skipped — no rules baseline found` in the report header, run the other three. The skill stays useful on any repo.

## Report-only

This skill never edits code. After the report, bridge to the fix pass:

- `/apex -f .claude/output/code-review/{slug}/code-review.md` — structured fix workstream (requires `-s`).
- `/oneshot "<finding>"` — single quick fix (manual; `/oneshot` takes a description, not a file).

## Rules

- **Report-only.** No code changes, no file writes other than the saved report under `-s`.
- **Stay in lane.** Security, performance, simplification → pointer only, never a finding.
- **Only new findings.** Issues the diff introduces, not pre-existing ones.
- **Fail loud.** A lens that cannot run (unresolvable base, missing baseline) is stated in the header, never silently skipped.
- **Cite precisely.** Every finding carries `file:line`; rule findings quote the violated rule line.
