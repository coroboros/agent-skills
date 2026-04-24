---
name: brainstorm
description: Strategic analysis and deep thinking before implementation. Researches the problem space, challenges assumptions, weighs tradeoffs, and produces a written strategic brief with a recommendation. Use this whenever the user needs to explore options, compare approaches, or pressure-test an idea before committing — even when they don't say "brainstorm" (e.g. "should we", "what's the best way", "evaluate", "pros and cons", "think through"). Not for implementation.
when_to_use: When the user needs to explore options before deciding. Architecture decisions, technology comparisons, strategy questions, "should we vs. should we not". When the user says "should we", "what's the best approach", "compare", "evaluate", "think through", "pros and cons", or asks an open-ended question that needs weighing. NOT for breaking down work into tasks — use `/spec`. NOT for implementation — use `/apex` or `/oneshot`.
argument-hint: "[-s] <question or topic>"
model: opus
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
metadata:
  author: coroboros
---

# Brainstorm

Strategic pre-implementation thinking for: $ARGUMENTS

## Parameters

| Flag | Behavior |
|------|----------|
| `-s` | Save the brief to `.claude/output/brainstorm/{slug}/brainstorm.md` |

Flags are removed from input; remainder becomes `{topic}`. `{slug}` = kebab-case from the topic (max 5 words).

## Rules

- **Never implement.** No code changes, no file creation other than the brief when `-s` is used.
- **Ask before assuming.** If scope, constraints, or success criteria are unclear from `$ARGUMENTS`, ask focused questions before researching.
- **End with discussion.** Present findings, state the recommendation and the top risk, then wait for user direction.

## Workflow

### Phase 1 — Frame the problem

Before any research, establish clarity:

- What is being decided or explored?
- What does success look like?
- What constraints exist (technical, budget, timeline, regulatory)?
- What does the user already know or suspect?

If `$ARGUMENTS` is vague, ask focused questions in a single message. Don't proceed on assumptions that could flip the recommendation.

### Phase 2 — Research (parallel subagents)

Investigate from multiple angles. Launch subagents in parallel and scale the count to complexity — exploration output is typically large and noisy, and subagents keep that noise out of the main context.

| Complexity | Agents | When |
|------------|--------|------|
| Trivial | 0 | The answer is already clear from Phase 1 — don't waste tokens |
| Simple A-vs-B | 1-2 | Well-scoped comparison in a known space |
| Moderate | 2-3 | New technology or pattern in a familiar ecosystem |
| Complex | 3-5 | Unfamiliar domain, multiple dimensions to compare |
| Major | 5-7 | Architecture-level question, many unknowns |

**Agent types:**

- `Explore` — find existing patterns in the codebase, related code, prior decisions (via `git log`). Read-only, fast, context-isolated.
- `general-purpose` — library docs, ecosystem research, post-mortems, comparative analyses via WebSearch/WebFetch.

**Launch all chosen agents in one message.** Parallel is the whole point — sequential defeats the purpose.

Cover what's relevant:

- **Codebase context** (if a codebase exists) — patterns, architecture, constraints, prior decisions
- **Technical best practices** — how best-in-class solutions approach this, pitfalls, security, performance
- **External evidence** (when needed) — comparative analyses, real-world experience reports, docs for unfamiliar technologies

### Phase 3 — Challenge

Before writing the brief, stress-test the emerging recommendation:

- What could go wrong?
- What hidden costs exist (complexity, maintenance, vendor lock-in)?
- What assumptions might be wrong?
- Is there a simpler path that gets 80% of the value at 20% of the cost?
- Does this align with the user's stack and constraints?

Be rigorous, not contrarian. Surface risks the user hasn't considered.

### Phase 4 — Synthesize

Produce the strategic brief. Output in conversation by default, or save to `.claude/output/brainstorm/{slug}/brainstorm.md` when `-s` is set.

Use the canonical format in `references/brief-template.md` (read it from `{skill_dir}/references/brief-template.md` before writing).

### Phase 5 — Discuss

After the brief:

1. State the recommendation and the top risk in plain language.
2. Surface the open questions that need answers.
3. **Stop and wait** — do not implement anything.

## Bridge to next steps

If the brainstorm leads to work that requires code, suggest the path forward based on scope:

**Complex work** (multiple workstreams, needs planning):

```
/spec -s -f .claude/output/brainstorm/{slug}/brainstorm.md
```

`/spec` turns the brainstorm into a structured execution spec with prioritized workstreams, dependencies, and acceptance criteria, then bridges to `/apex` or creates GitHub issues.

**Focused work** (single clear task, ready to implement):

```
/apex -f .claude/output/brainstorm/{slug}/brainstorm.md {description}
```

`-f` passes the brainstorm as foundational context — `/apex` skips redundant research and focuses its analyze phase on implementation specifics.

If the brainstorm is purely strategic (tech choice, architecture decision, process change) with no immediate code to write, simply conclude the discussion — no bridging needed.

> **Dependency:** these bridges require the `spec` and/or `apex` skills. If unavailable, tell the user and suggest installing them, or proceed manually based on the brief.
