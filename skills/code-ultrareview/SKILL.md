---
name: code-ultrareview
description: In-session fresh-eyes code review at full strength — six parallel lens subagents (rules, bugs-drift with spec-claim triggering, docs-version, tests-blindspots, coherence-graph for cross-artifact drift, derivation for code↔planning-artifact reconciliation via `--reconcile`), iteration on sub-80 findings with build verification, property-fuzz harness synthesis, gated `--apply-safe` writers. Report-only by default; defers security/performance/simplification to owning skills. Distinct from Anthropic's built-in `/ultrareview` remote billed command — same lens family, in-session, on your subscription.
when_to_use: User-invoked at the end of a coding session, before a commit, or before opening a PR. Always runs the full lens fan-out — no tiers. The audit phase reads diff signals (LOC, public-API touches, normative-spec mentions, manifest delta, security paths) and surfaces a Scope summary + estimated wall-clock in the report header. Invoke when you'd say "review my changes", "did I miss anything", "check before I commit", "drift / gaps / blind spots", "manifest coherence", "spec conformance", "does this follow the rules". NOT a security audit (use /security-review); NOT performance / simplification (use /simplify); NOT Anthropic's remote billed command (use /ultrareview). Report-only by default; opt-in `--apply-safe` writes manifest-version sync, structured-field description sync (full-agreement guard), and one failing test per confirmed bug — never production logic.
argument-hint: "[-b <ref>] [--reconcile <input>] [--apply-safe] [--include-prose] [--remote] [-s] [-S]"
model: opus
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
disable-model-invocation: true
metadata:
  author: coroboros
  sources:
    - github.com/anthropics/knowledge-work-plugins/tree/main/engineering/skills/code-review
    - github.com/anthropics/claude-plugins-official/tree/main/plugins/code-review
    - code.claude.com/docs/en/ultrareview
    - code.claude.com/docs/en/code-review
    - code.claude.com/docs/en/commands
    - x.com/trq212/status/2033949937936085378
---

# Code ultrareview

> **In-session fresh-eyes code review at full strength.** Always runs the full lens fan-out — no tiers, no calibration choice. Distinct from Anthropic's built-in `/ultrareview` remote command — different namespace (skill vs built-in), different posture (in-session on your subscription vs remote sandbox + billed).

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

A fresh-eyes pass over what changed, at full strength every time. The audit phase reads deterministic signals from the diff (LOC, public-API touch, normative-spec claims, manifest delta, test-coverage delta, pre-1.0 proximity, security surface) and surfaces a Scope summary + estimated wall-clock in the report header — informational context only, no tier routing. Five lens subagents (`rules`, `bugs-drift`, `docs-version`, `tests-blindspots`, `coherence-graph`) run in parallel; sub-80 findings re-pass with build verification when feasible; spec-conformance fetches and quotes named normative specs (RFC, WHATWG, ISO/IEC, OpenAPI); property-fuzz harness synthesis from spec grammar when `fast-check` / `hypothesis` is present; opt-in `--apply-safe` writers gate write semantics. Findings are confidence-scored 0–100 and surfaced — sub-80 are routed to the Unverified sub-section rather than silent-dropped. The skill writes no code by default and owns no checklist of its own — every criterion is read at runtime from the project. Anything outside its lane (security, performance, simplification) becomes a one-line pointer to the skill that owns it, never a finding.

## Parameters

| Flag | Behavior |
|------|----------|
| `-s` | Save the report to `~/.claude/output/{project}/code-ultrareview/code-ultrareview-{slug}.md` (global; `{slug}` = kebab of the branch or a short description, ≤5 words) |
| `-S` | Force no-save (override an ambient save mode) |
| `-b <ref>` | Override the review base (skip auto-detection) |
| `--reconcile <input>` | Activate the derivation lens. `<input>` may be `@auto` (auto-detect brainstorm + spec + apex plan + PR body), `@pr`, an explicit path or directory of `.md` files, `gh:pr:<N>`, `gh:issue:<owner>/<repo>#<N>`, or a GitHub issue URL. Comma-separate multiple inputs. Findings classify as GAP / SCOPE-ADD / DECISION-OVERRIDE / CONSISTENT with freshness-capped severity |
| `--apply-safe` | Opt-in writers: auto-apply low-risk fixes (manifest version sync, structured-field description sync with full-agreement guard, one failing test per confirmed bug). Diff preview + per-file confirmation prompt before any write. Never modifies production logic |
| `--include-prose` | Coherence-graph lens compares README freeform paragraphs as well (default: structured fields only — `package.json`, `marketplace.json`, SKILL.md frontmatter, GitHub About, topics) |
| `--remote` | Reserved for phase-2 remote-sandbox escalation; current MVP is in-session |

`{slug}` = kebab of the branch name or a short description (≤5 words); `{project}` = kebab-cased basename of the git toplevel (else cwd) — see `.claude/rules/repo-conventions.md` § Output paths. Lowercase enables, uppercase disables — repo-wide convention. No `-f`: this skill is a producer, not a consumer.

```bash
/code-ultrareview                              # full review, print report
/code-ultrareview -s                           # save the report for /apex -f
/code-ultrareview -b origin/main               # review HEAD against an explicit base
/code-ultrareview --reconcile @auto            # add derivation lens with auto-detected planning artifacts
/code-ultrareview --reconcile @pr,gh:issue:owner/repo#42  # PR body + a specific issue
/code-ultrareview --apply-safe                 # full review + gated low-risk fixes
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

## The six lenses

One read-only subagent per lens. Operational definitions, subagent briefs, and the confidence rubric live in `references/lenses.md` — read it before dispatching.

1. **Rules compliance** (key `rules`) — new violations of the rule hierarchy, citing the exact rule line.
2. **Bugs + drift** (key `bugs-drift`) — logic errors on changed lines; code no longer matching its own doc/comment/claim or a sibling pattern. When the diff/README/CLAUDE.md cites a named normative spec (RFC, WHATWG, ISO/IEC, OpenAPI), the lens fetches the spec, quotes the governing clause, and diffs the code against it (A1).
3. **Docs + version** (key `docs-version`) — user-visible behavior changed without a doc/version update.
4. **Tests + blind spots** (key `tests-blindspots`) — missing tests the convention implies, tests that can't fail, unstated assumptions.
5. **Coherence-graph** (key `coherence-graph`) — cross-artifact drift across six sub-graphs: description, version, capability, cross-reference, example, spec-conformance. Default to structured fields only; `--include-prose` extends to README freeform. Sub-graph briefs and the `.coherence-ignore` allowlist format live in `references/coherence-graph.md`.
6. **Derivation** (key `derivation`) — reconciles planning artifacts (brainstorm, spec, apex plan, PR body, issue body) against the diff. Activates on `--reconcile <input>`. Classifies each claim as GAP (planning said X, code missing), SCOPE-ADD (code has X, planning silent), DECISION-OVERRIDE (planning resolved X, code does Y), or CONSISTENT. Severity capped by artifact freshness (>30d → Low; >90d → coverage-summary only). Per-repo `.derivation-ignore` allowlist. Brief, classification taxonomy, and auto-detection set live in `references/derivation.md`.

These six keys are canonical — the report table, the evals, and the pipeline contract (`tests/_pipeline/_contracts.py`) all key off them.

## How it runs

```
Phase 1 — AUDIT  (always-on, ~30–60s, 1 Haiku subagent)
  signals: LOC, files, public-API touched, spec claims, manifest delta,
           pre-1.0 proximity, test-coverage delta, security surface
  output:  Scope summary + estimated wall-clock for the report header
           (deterministic context — no tier routing, no gate)

Phase 2 — DISPATCH  (5 or 6 lens subagents in parallel + execution layer)
  Lenses:    rules + bugs-drift (with A1 spec fetch) + docs-version
             + tests-blindspots + coherence-graph (6 sub-graphs)
             + derivation (when --reconcile resolves to non-empty input)
  Iteration: sub-80 findings re-passed with build verification (1/finding)
  Spec fetch: WebFetch + 7-day ETag cache; quotes governing clause
  Fuzz:      harness synthesis when fast-check / hypothesis present
  Writers:   opt-in via --apply-safe — version_sync, description_sync,
             failing_test_writer

Phase 3 — AGGREGATION  (1 synthesizer subagent)
  dedupe by (location, finding-key); severity tiers
  (Important / Nit / Pre-existing); sub-80 surfaced as
  "unverified — recommend Deep pass" (never silent-dropped — A2)
```

Audit-phase signal schema and report-header formatting live in `references/audit-phase.md`. Lens briefs and the no-silent-drop (A2) contract live in `references/lenses.md` and `references/aggregation.md`. Coherence-graph sub-graphs and the `.coherence-ignore` allowlist live in `references/coherence-graph.md`. Derivation lens — classification taxonomy, auto-detection set, `.derivation-ignore` format, interactive launch prompt — lives in `references/derivation.md`. Build / fuzz / `--apply-safe` details live in `references/ultra-execution.md`. The `--remote` phase-2 escalation design lives in `references/remote-escalation-design.md`.

1. Resolve the target (above); read the rule hierarchy; run the audit phase to extract signals and format the Scope + Estimated wall-clock header.
2. Launch the lens subagents **in one message** (parallel, read-only). Each is given the resolved `base`/`target` (or "dirty tree") and the rule-hierarchy paths, then reconstructs its own review set read-only per `references/lenses.md` (never skipping untracked files), with its lens brief and the exclusion contract.
3. Aggregate findings via `scripts/aggregation.py`; score each 0–100 (rubric in `references/lenses.md`); sub-80 routed to the report's Unverified sub-section (never silent-dropped — postmortem A2).
4. Re-pass sub-80 findings with build verification (one iteration per finding); synthesize a property-fuzz harness when `fast-check` / `hypothesis` is present, run the canonical test command from `build_detect.py`, feed the verdict into the iteration phase.
5. With `--apply-safe`: invoke the three writers (`version_sync`, `description_sync` with full-agreement guard, `failing_test_writer`) — diff preview + per-file confirmation prompt before any write.
6. Emit the report from `templates/code-ultrareview.md`. Save to the `-s` path when set, and report its fully-expanded absolute path to the user (no tilde, no magic).

## Deferral spine

Out-of-lane findings are never reported as findings — emit a single pointer line and move on:

- Security → `/security-review`
- Performance / optimization / simplification → `/simplify`
- Cases where the in-session execution is inadequate (need remote multi-agent fleet with build-and-run) → Anthropic's `/ultrareview` (distinct from this skill; remote sandbox, billed per run)
- Reliance on possibly-stale library/API knowledge → `/find-docs`

## Graceful degradation

No `CLAUDE.md`, no `.claude/rules`, no `~/.claude/rules` → skip lens 1, state `Lens 1 (rules): skipped — no rules baseline found` in the report header, run the other four. The skill stays useful on any repo.

Coherence-graph lens degrades sub-graph by sub-graph: if `gh` CLI is unavailable, the description / topics sub-graphs are skipped and the header notes the skip; if `WebFetch` is unavailable for the spec-conformance sub-graph, the finding surfaces as `[unverified — needs network]` rather than dropping.

## Report-only by default

This skill writes no code by default. After the report, bridge to the fix pass:

- `/apex -f ~/.claude/output/{project}/code-ultrareview/code-ultrareview-{slug}.md` — structured fix workstream (requires `-s`; pass the absolute path the report printed).
- `/oneshot "<finding>"` — single quick fix (manual; `/oneshot` takes a description, not a file).

Opt-in `--apply-safe` writes only:
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
