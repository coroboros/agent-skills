---
name: oneshot
description: Single-pass feature implementation using Explore → Code → Test. Ships focused changes at maximum speed, with a built-in circuit breaker that stops and recommends `/apex` or `/forge` when the task turns out more complex than it looked. Use this whenever the user wants a quick win on a single, focused task — even when they don't say "oneshot" (e.g. "just", "quickly", "small change", "#42", or a GitHub issue URL for a small fix).
when_to_use: When the task is simple, focused, and well-defined. Quick fixes, small features, single-concern changes. When the user says "quickly", "just do", "simple change", provides a GitHub issue reference for a small fix, or describes a clearly scoped task. NOT for multi-file refactors or unfamiliar codebases — use `/apex`. NOT for planning or weighing approaches — use `/forge`.
argument-hint: "<description or #issue>"
license: MIT
compatibility: "Optimized for Claude Code; degrades gracefully on any agent implementing the Agent Skills standard."
metadata:
  author: coroboros
  sources:
    - github.com/Melvynx/aiblueprint
---

# OneShot

<!-- canonical:execution-discipline:start -->
## Important — Engineering discipline

These rules govern how this skill changes code — apply them whenever it writes, edits, or proposes a fix.

- Minimal scope. Only what's directly requested or clearly necessary — no extra files, no abstraction for one use, no configurability nobody asked for, no error handling for states that can't happen. Validate at system boundaries; trust internal code.
- General solution, not the test cases. Implement the real logic for all valid inputs; never hard-code to inputs or bolt on workaround scripts to make a test pass. Tests verify the solution; they don't define it. A test is wrong? Say so — don't bend correct code to a broken test.
- Investigate before claiming. Never speculate about code you haven't opened; read the referenced file before answering. Ground every claim in what you actually read, not a plausible guess.
<!-- canonical:execution-discipline:end -->

<!-- canonical:label-hygiene:start -->
## Critical — Label hygiene

Internal planning labels are author coordinates, not reader coordinates. Strip them from every shipped artifact this skill emits — code, comments, commit subjects/bodies, PR titles/descriptions, release notes, doc paragraphs, non-trivial comments.

- **Workstream and task labels** — `WS-N`, `Phase-A`, `Step-3`, issue or ticket numbers, plan phase names from the source spec, issue body, or planning artifact. Translate to the domain noun (`Runs the battery script (WS-2)` → `Runs the battery script`). <!-- noqa: internal-label -->
- **Process language** — "the rebuild", "the prior `<file>`", "carried verbatim from", "the cleanup pass", "the audit", "spec AC" standalone. Replace with the concrete fact (`carries the routing from the prior aggregation` → `routes via the merge keys in the synthesis module`). <!-- noqa: internal-label -->
- **Plan-internal references** — "as the brief says", "per the workstream", "from the forge artifact". Drop the reference; state the fact directly.

Carve-outs — literal `WS-N` is legitimate where the skill IS the format authority (forge templates, apex rule documentation). Reviewer-facing dev docs (e.g. `MIGRATION.md` under `tests/<skill>/`) may reference deleted artifacts by their author-time names.
<!-- canonical:label-hygiene:end -->

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

Implement `$ARGUMENTS` at maximum speed. Ship fast, iterate later.

## Workflow

### 0. Resolve input

If the input looks like a GitHub issue reference (`#N`, `owner/repo#N`, or a GitHub URL like `https://github.com/.../issues/N`):

1. Fetch the issue:
   - `#N` → `gh issue view <N> --json title,body,labels` (current repo).
   - `owner/repo#N` or full URL → `gh issue view <N> --repo owner/repo --json title,body,labels`.
2. Use the issue title + body as the task description.
3. If the issue body has task lists or acceptance criteria, use them as the implementation checklist.

Then proceed to EXPLORE with the resolved description.

### 1. Explore (minimal)

Gather the minimum context needed to identify the edit target. Direct tools first — no subagent overhead on the happy path:

- `Glob` for 2-3 files by pattern.
- `Grep` for specific symbols or strings.
- Quick `WebSearch` only if library-specific API knowledge is missing.

**When to spawn an `Explore` subagent instead:** if one or two direct searches don't locate the edit target, stop searching and spawn a single `Explore` subagent (or your harness's equivalent) with a specific question ("find the file that handles {X}"). Reason: multiple rounds of Glob/Grep pollute the main context with file contents you'll never edit — a subagent returns just the answer. This is an exception path, not the default. If your harness has no subagents, explore inline.

No exploration tours. As soon as the edit target is identified, move on.

### 1b. Complexity check (circuit breaker)

After exploring, assess whether this task actually fits oneshot. Flag if any of these signals appear:

- **> 5 files** need modification
- **> 2 distinct systems/domains** involved (auth + billing + notifications, etc.)
- **Cross-cutting concerns** (database migrations, API changes with client updates, etc.)
- **Unclear requirements** — the task seemed simple but the codebase reveals hidden complexity

**If triggered:** stop and warn the user before coding.

```
This task is more complex than it looks:
- {specific reason: e.g., "touches 8 files across 3 modules"}
- {specific reason}

Recommendations:
- /apex {task}        — structured implementation with analysis and planning
- /forge -s {task}    — think, decide, and plan first

Continue with /oneshot anyway? (results may be incomplete)
```

Wait for user confirmation. Their call — if they continue, proceed. If not, stop.

**If not triggered:** proceed directly to CODE. No delay on the happy path.

### 2. Code

Execute the changes immediately:

- Follow existing codebase patterns exactly.
- Clear variable and method names over comments.
- Stay strictly in scope — change only what the task requires.

### 3. Test

Run the project's lint and typecheck commands — discover them from project instructions (`CLAUDE.md`, `AGENTS.md`, or equivalent), `package.json` scripts for JS/TS, `pyproject.toml` / `Cargo.toml` / `go.mod` for other ecosystems.

- If they fail, fix only what you broke and re-run.
- No full test suite unless the user explicitly asks.

## Output

### On success

```
## Done

**Task:** {what was implemented}
**Files changed:** {list}
**Validation:** ✓ lint ✓ typecheck
```

### On blocker (stuck after 2 attempts, or circuit breaker declined)

```
## Blocked

**Task:** {what was attempted}
**Attempts:** {N}
**Blocker:** {specific failure or unknown}
**Recommendation:** /apex {task}   ← restart with structured analysis
```

## Constraints

- **One task only** — no tangential improvements, no "while I'm here" additions.
- **No comments** unless the logic is genuinely non-obvious.
- **No refactoring** outside the immediate scope.
- **No documentation files** unless the user asks.
- **Stuck after 2 attempts** — report the blocker and stop. Don't thrash.

## Gotchas

1. **Circuit-breaker after Explore needs explicit user approval to continue.** When the task spans >5 files, >2 systems, or hits cross-cutting concerns, the skill stops post-Explore and surfaces the complexity check. The model sometimes treats the "Recommendation: /apex" line as a verdict and auto-restarts instead of asking. Fix: when the breaker trips, present the scope to the user and wait. Re-entry into oneshot for a complex task tends to thrash.
2. **`gh` unauthenticated = silent issue-ref fail.** A `#42` or `owner/repo#42` reference is fetched via `gh issue view`; an unauthenticated `gh` returns empty output, and the model proceeds with no task context. Fix: run `gh auth status` before invoking with an issue ref; or paste the issue body directly as the task description.
3. **Stuck-after-2-attempts is NOT auto-escalated to `/apex`.** The Blocked output names the recommendation but does not invoke it. The model sometimes interprets the recommendation as "the agent should run it next." Fix: when oneshot reports Blocked, the user manually runs `/apex {task}` (or `/forge` first for ambiguity). Escalation is a user action, not an automatic handoff.
