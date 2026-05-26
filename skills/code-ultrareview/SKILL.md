---
name: code-ultrareview
description: In-session fresh-eyes code review at full strength — seven parallel lens subagents (rules, bugs-drift with A1 spec triggers, docs-version, tests-blindspots, coherence-graph, derivation via `--reconcile`, prose-hygiene over PR body + commits + user-facing docs with `--no-prose-hygiene` opt-out), repo-kind-aware heuristics (skills/app/library/docs/monorepo/python/rust/go, override via `--repo-kind` or `.code-ultrareview.yaml`), iteration on sub-80 findings with build verification, property-fuzz harness, gated `--apply-safe` writers. Every report ends with a seven-lens summary (🔴 / 🟠 / 🟢), a deterministic verdict (Ship / Fix-then-ship / Needs work), and per-cluster action-plan prompts routed to the most-specialized installed skill (falling back to `/apex`). Report-only by default; defers security/performance/simplification to owning skills. Distinct from Anthropic's remote `/ultrareview` — same lenses, in-session.
when_to_use: 'User-invoked at the end of a coding session, before a commit, or before opening a PR. Always runs the full lens fan-out — no tiers, `effort: max`. Audit phase surfaces Scope + estimated wall-clock in the report header. Invoke when you''d say "review my changes", "ultrathink review", "did I miss anything", "check before I commit", "drift / gaps / blind spots", "manifest coherence", "spec conformance". NOT a security audit (use /security-review); NOT performance/simplification (use /simplify); NOT Anthropic''s remote billed command (use /ultrareview).'
argument-hint: "[-b <ref>] [--reconcile <input>] [--repo-kind <kind>] [--apply-safe] [--include-prose] [--no-prose-hygiene] [--remote] [-s] [-S]"
model: opus
effort: max
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

Fresh-eyes pass over the diff, at full strength. Seven lens subagents run in
parallel; criteria come from the project's rule hierarchy at runtime, not a
baked checklist. Findings score 0–100 and surface verbatim — sub-80 route
to the Unverified sub-section (A2 contract). Out-of-lane work (security,
performance, simplification) emits a single pointer line, never a finding.
Operational detail follows in `## How it runs` and per-lens references.

## Parameters

| Flag | Behavior |
|------|----------|
| `-s` | Save the report to `~/.claude/output/{project}/code-ultrareview/code-ultrareview-{slug}.md` (global; `{slug}` = kebab of the branch or a short description, ≤5 words) |
| `-S` | Force no-save (override an ambient save mode) |
| `-b <ref>` | Override the review base (skip auto-detection) |
| `--reconcile <input>` | Activate the derivation lens. `<input>` may be `@auto` (auto-detect forge + apex plan + PR body), `@pr`, an explicit path or directory of `.md` files, `gh:pr:<N>`, `gh:issue:<owner>/<repo>#<N>`, or a GitHub issue URL. Comma-separate multiple inputs. Findings classify as GAP / SCOPE-ADD / DECISION-OVERRIDE / CONSISTENT with freshness-capped severity |
| `--repo-kind <kind>` | Override the audit-phase classifier. `<kind>` is one of `skills`, `app`, `library`, `docs`, `monorepo`, `python`, `rust`, `go`, `unknown`. Persistent per-repo override lives at `.code-ultrareview.yaml` (`repo_kind: <kind>`); the flag wins on conflict. Invalid value exits 2. See `references/audit-phase.md` § *Repo-kind detection* |
| `--apply-safe` | Opt-in writers: auto-apply low-risk fixes (manifest version sync, structured-field description sync with full-agreement guard, one failing test per confirmed bug). Diff preview + per-file confirmation prompt before any write. Never modifies production logic |
| `--include-prose` | Coherence-graph lens compares README freeform paragraphs as well (default: structured fields only — `package.json`, `marketplace.json`, SKILL.md frontmatter, GitHub About, topics) |
| `--no-prose-hygiene` | Skip the prose-hygiene lens (PR body, commits, user-facing `*.md` checks). Lens runs by default; the row reads `— skipped (--no-prose-hygiene)` in the lens summary when set |
| `--remote` | Reserved for phase-2 remote-sandbox escalation; current MVP is in-session |

Output path per `.claude/rules/repo-conventions.md` § Output paths (`{slug}` = kebab of the branch name or short description, ≤5 words). Lowercase enables, uppercase disables — repo-wide convention. No `-f`: this skill is a producer, not a consumer.

```bash
/code-ultrareview                              # full review, print report
/code-ultrareview -s                           # save the report for /apex -f
/code-ultrareview -b origin/main               # review HEAD against an explicit base
/code-ultrareview --reconcile @auto            # add derivation lens with auto-detected planning artifacts
/code-ultrareview --reconcile @pr,gh:issue:owner/repo#42  # PR body + a specific issue
/code-ultrareview --apply-safe                 # full review + gated low-risk fixes
/code-ultrareview --include-prose              # also compare README freeform prose
/code-ultrareview --no-prose-hygiene           # skip the prose-hygiene lens
```

## What it reviews

Resolve the target deterministically, and always print it in the report header so the scope is never silent:

1. **Dirty working tree** → everything not yet committed: tracked changes vs `HEAD` (`git diff HEAD` — staged and unstaged) **plus** untracked files (`git ls-files --others --exclude-standard`, each read in full). A new file written this session but not yet `git add`-ed is part of the session — never skip untracked, or the review silently misses whole new modules.
2. **Clean tree** → branch-vs-base. Read the project's rule files (below) first; if a source/base branch is declared there (e.g., a `Source branch` line in `CLAUDE.md` or `.claude/rules/git-conventions.md`), pass it as `-b` to the resolver. Otherwise run `scripts/resolve_base.sh` and use its ladder.

The review set every lens examines: **clean tree** → `git diff <base> <target>` (two-dot — the resolver guarantees `base` is a diffable ancestor or the empty tree, so this is always correct, with no noise from commits the base gained in parallel); **dirty tree** → `git diff HEAD` plus the untracked files above.

```bash
# Clean tree
bash "${CLAUDE_SKILL_DIR}/scripts/resolve_base.sh" [-b <ref>]
# → RESULT: base=<ref> target=<ref> rule=<rung>   (exit 0)
# → RESULT: rule=unresolvable hint=<text>          (exit 2 — report it, do not guess)

# Dirty tree — skip the resolver; audit-phase reads HEAD + untracked directly
python3 "${CLAUDE_SKILL_DIR}/scripts/audit_signals.py" --dirty-tree --json

# Override the detected repo_kind (one-off)
python3 "${CLAUDE_SKILL_DIR}/scripts/audit_signals.py" --dirty-tree --repo-kind skills --json
# Details in references/audit-phase.md (signal schema + Repo-kind detection + override).
```

The audit phase also resolves `repo_kind` (see Parameters table for values
and overrides) and surfaces it on a `Repo: <kind>` header line. Each lens
reads its `## Repo-kind branches` section before applying heuristics — so
a skills repo is reviewed as a skills repo, not as code-with-docstrings.

The **rule hierarchy** every lens reviews against, read fresh each run:

- Repo `CLAUDE.md` chain (root + any nested `CLAUDE.md` in changed directories)
- `.claude/rules/*.md` (project)
- `~/.claude/rules/*.md` (global)

## The seven lenses

One read-only subagent per lens. Each lens has a `references/lens-<key>.md`
brief with its operational definition; `references/lenses.md` owns the
dispatch protocol, confidence rubric, exclusion contract, and graceful
degradation.

| Key | One-line | Brief |
|-----|----------|-------|
| `rules` | New violations of the rule hierarchy | `references/lens-rules.md` |
| `bugs-drift` | Logic errors + drift + single-source-of-truth (A1 spec triggers, sub-80 iteration always-on) | `references/lens-bugs-drift.md` |
| `docs-version` | User-visible behavior changed without doc/version update | `references/lens-docs-version.md` |
| `tests-blindspots` | Test gaps, weak tests, unstated assumptions | `references/lens-tests-blindspots.md` |
| `coherence-graph` | Cross-artifact drift across 6 sub-graphs; `--include-prose` extends to README freeform | `references/lens-coherence-graph.md` |
| `derivation` | Reconcile planning artifacts against the diff; activates on `--reconcile` | `references/lens-derivation.md` |
| `prose-hygiene` | PR body + commits + user-facing `*.md`; `--no-prose-hygiene` opt-out | `references/lens-prose-hygiene.md` |

These seven keys are canonical — the report table, the evals, and the
pipeline contract (`tests/_pipeline/_contracts.py`) all key off them.

## How it runs

Three phases: **AUDIT** (~30–60s, 1 Haiku subagent — extracts signals into
the header), **DISPATCH** (6-7 lens subagents in parallel + execution
layer for iteration, spec fetch, fuzz harness, opt-in `--apply-safe`
writers), **AGGREGATION** (1 synthesizer — dedupe, severity tiers, A2
routing).

Detail references:

- `references/audit-phase.md` — signal schema + report-header formatting
- `references/lenses.md` — dispatch protocol + scoring rubric + contracts
- `references/lens-<key>.md` — per-lens briefs (one per canonical lens key above)
- `references/aggregation.md` — A2 no-silent-drop + dedup
- `references/ultra-execution.md` — build / fuzz / `--apply-safe`
- `references/remote-escalation-design.md` — `--remote` phase-2 escalation
- `references/skill-routing.md` — action-plan routing
- `references/verdict-logic.md` — Ship / Fix-then-ship / Needs work algorithm

1. Resolve the target (above); read the rule hierarchy; run the audit phase to extract signals (including `repo_kind` + `repo_kind_signals`) and format the Scope + Estimated wall-clock header.
2. Launch the lens subagents **in one message** (parallel, read-only). Each is given the resolved `base`/`target` (or "dirty tree"), the rule-hierarchy paths, AND the resolved `repo_kind` + `repo_kind_signals` from the audit phase. Each lens reads the `## Repo-kind branches` section in its `references/lens-<key>.md` brief and applies the relevant rules before evaluating findings.
3. Aggregate findings via `scripts/aggregation.py`; score each 0–100 (rubric in `references/lenses.md`); sub-80 routed to the report's Unverified sub-section (never silent-dropped — A2).
4. Re-pass sub-80 findings with build verification (one iteration per finding); synthesize a property-fuzz harness when `fast-check` / `hypothesis` is present, run the canonical test command from `build_detect.py`, feed the verdict into the iteration phase.
5. With `--apply-safe`: invoke the three writers (`version_sync`, `description_sync` with full-agreement guard, `failing_test_writer`) — diff preview + per-file confirmation prompt before any write.
6. Emit the report from `templates/code-ultrareview.md`. Save to the `-s` path when set, and report its fully-expanded absolute path to the user (no tilde, no magic).

## Final report layout

The template at `templates/code-ultrareview.md` is the canonical wire format — every `##` section renders verbatim in template order with its emoji prefix; section names are not rewritten, merged, or reordered.

**Terminal echo is mandatory.** The full canonical report prints to the chat-terminal on every invocation. The `-s` flag is purely additive: it writes the same bytes to `~/.claude/output/{project}/code-ultrareview/code-ultrareview-{slug}.md` — terminal output and saved file are byte-for-byte identical. Severity marker mapping (🔴 High blocks ship · 🟠 Medium fix-soon · 🟢 Low nit · ⚠️ Unverified sub-80), per-section IDs, and dict-key schema: `references/aggregation.md`.

No section beyond the template's list — `Dropped`, `Derivation reconciliation`, `Per-ask verification`, and similar improvised headings are out of contract; debug data stays out of the user-facing report by design.

## Deferral spine

Out-of-lane findings are never reported as findings — emit a single pointer line and move on:

- Security → `/security-review`
- Performance / optimization / simplification → `/simplify`
- Cases where the in-session execution is inadequate (need remote multi-agent fleet with build-and-run) → Anthropic's `/ultrareview` (distinct from this skill; remote sandbox, billed per run)
- Reliance on possibly-stale library/API knowledge → `/find-docs`

## Graceful degradation

No `CLAUDE.md`, no `.claude/rules`, no `~/.claude/rules` → skip lens 1, state `Lens 1 (rules): skipped — no rules baseline found` in the report header, run the other always-on lenses (2-7). The skill stays useful on any repo.

Coherence-graph lens degrades sub-graph by sub-graph: if `gh` CLI is unavailable, the description / topics sub-graphs are skipped and the header notes the skip; if `WebFetch` is unavailable for the spec-conformance sub-graph, the finding surfaces as `[unverified — needs network]` rather than dropping.

Unknown `repo_kind` → every lens runs at full strength with its `unknown` branch (pre-classifier behavior preserved); the header line surfaces the unspecialized status. Misclassification → override via `--repo-kind` or `.code-ultrareview.yaml` (Parameters table).

## Report-only by default

This skill writes no code by default. After the report, bridge to the fix pass:

- `/apex -f ~/.claude/output/{project}/code-ultrareview/code-ultrareview-{slug}.md` — structured fix pass (requires `-s`; pass the absolute path the report printed).
- `/oneshot "<finding>"` — single quick fix (manual; `/oneshot` takes a description, not a file).

Opt-in `--apply-safe` writes only:
- Manifest version sync (mechanical, idempotent — aligns all structured version sources to the most-recently-touched value).
- Structured-field description sync (full-agreement guard — refuses unless every present source agrees on the new value).
- One focused failing test per confirmed bug (additive — never modifies existing tests).

Every write shows a diff preview and prompts for confirmation per file. Production logic is never modified — that belongs to `/simplify` and future `/modernize`.

## Rules

- **Only new findings.** Issues the diff introduces, not pre-existing ones (Pre-existing tier accepted for context).
- **No silent drop.** Sub-80 findings surface as `[unverified]` with the rationale `Sub-80 confidence ({score}) — verify locally before action.` — never omitted (A2).
- **Fail loud.** A lens that cannot run (unresolvable base, missing baseline, fetch failure) is stated in the header or surfaced as a finding, never silently skipped.
- **Cite precisely.** Every finding carries `file:line`; rule findings quote the violated rule line verbatim; spec-conformance findings quote the governing clause.
- **Full report in chat every time.** Print the complete canonical report — header, every `##` section, every finding sub-section — to the chat-terminal on every invocation. `-s` is additive: it writes the same bytes to disk; it does not gate, truncate, or summarise the chat-terminal output. Terminal output and saved file are byte-for-byte identical. (Mirrored in `## Final report layout` and `templates/code-ultrareview.md` — enforced by `test_section_emoji_drift.TestTerminalEchoRuleMirroredInThreePlaces`.)

Report-only default + deferral spine + canonical sections live in their own
sections above — not restated here.

## Gotchas

1. **Sub-80 findings can be dropped instead of surfaced in `### ⚠️ Unverified`.** The contract (lines above + `scripts/aggregation.py:31-34`, `CONFIDENCE_THRESHOLD = 80`, `PROMOTION_BONUS = 30`) is no-silent-drop: sub-80 lands in the Unverified sub-section with `[unverified]` rationale. The model sometimes treats the sub-80 score as a rejection signal and omits the finding entirely. Fix: scan the `### ⚠️ Unverified` section explicitly on every report; compare finding count to lens output to catch drops.
2. **Lens routing falls back to `/apex` when the specialized skill is not installed.** `references/skill-routing.md` defines the per-finding routing chain; absent skills fall through to `/apex`. Symptom: an Action plan prompt that should route to `/simplify` or `/security-review` lists `/apex` instead. Fix: install the routed skills before running review; or manually re-route by invoking the specialist with the finding ID.
3. **`--reconcile @auto` fails on invalid forge/apex frontmatter.** `scripts/derivation/auto_detect.py` scans `~/.claude/output/{project}/` for plans and tasks; a `# Spec:` or `# Decision:` header with malformed YAML frontmatter (unclosed `---`, tab indentation, unquoted colons in values) breaks discovery silently. Verify with `head -20 ~/.claude/output/{project}/forge/forge-*.md` before relying on `@auto`.
4. **Dirty-tree review pulls untracked files into scope.** Per § What it reviews: untracked files (`git ls-files --others --exclude-standard`) are read in full and counted. A new module written this session but not yet `git add`-ed inflates diff size and the wall-clock estimate. Fix: run on a clean tree (`git add` first) when scope tightness matters; or accept the dirty-tree behavior and verify the Scope line lists the untracked files.
