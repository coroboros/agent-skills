---
name: oneshot
description: Ultra-fast feature implementation using Explore → Code → Test. Ships focused changes at maximum speed, with a built-in circuit breaker that stops and recommends `/apex` or `/spec` when the task turns out more complex than it looked. Use this whenever the user wants a quick win on a single, focused task — even when they don't say "oneshot" (e.g. "just", "quickly", "small change", "#42", or a GitHub issue URL for a small fix).
when_to_use: When the task is simple, focused, and well-defined. Quick fixes, small features, single-concern changes. When the user says "quickly", "just do", "simple change", provides a GitHub issue reference for a small fix, or describes a clearly scoped task. NOT for multi-file refactors or unfamiliar codebases — use `/apex`. NOT for planning — use `/spec`. NOT for exploring options or weighing approaches — use `/brainstorm`.
argument-hint: "<description or #issue>"
model: sonnet
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
metadata:
  author: coroboros
  sources:
    - github.com/Melvynx/aiblueprint/tree/main/claude-code-config/skills/oneshot
---

# OneShot

Implement `$ARGUMENTS` at maximum speed. Ship fast, iterate later.

## Workflow

### 0. Resolve input

If the input looks like a GitHub issue reference (`#N`, `owner/repo#N`, or a GitHub URL like `https://github.com/.../issues/N`):

1. Fetch via `gh issue view <number> --json title,body,labels`.
2. Use the issue title + body as the task description.
3. If the issue body has task lists or acceptance criteria, use them as the implementation checklist.

Then proceed to EXPLORE with the resolved description.

### 1. Explore (minimal)

Gather the minimum context needed to identify the edit target. Direct tools first — no subagent overhead on the happy path:

- `Glob` for 2-3 files by pattern.
- `Grep` for specific symbols or strings.
- Quick `WebSearch` only if library-specific API knowledge is missing.

**When to spawn an `Explore` subagent instead:** if one or two direct searches don't locate the edit target, stop searching and spawn a single `Explore` subagent with a specific question ("find the file that handles {X}"). Reason: multiple rounds of Glob/Grep pollute the main context with file contents you'll never edit — a subagent returns just the answer. This is an exception path, not the default.

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
- /spec -s {task}     — plan and decompose into workstreams first

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

Run the project's lint and typecheck commands — discover them from `package.json` scripts or project instructions (`CLAUDE.md`, `AGENTS.md`, or equivalent).

- If they fail, fix only what you broke and re-run.
- No full test suite unless the user explicitly asks.

## Output

When complete, return:

```
## Done

**Task:** {what was implemented}
**Files changed:** {list}
**Validation:** ✓ lint ✓ typecheck
```

## Constraints

- **One task only** — no tangential improvements, no "while I'm here" additions.
- **No comments** unless the logic is genuinely non-obvious.
- **No refactoring** outside the immediate scope.
- **No documentation files** unless the user asks.
- **Stuck after 2 attempts** — report the blocker and stop. Don't thrash.
