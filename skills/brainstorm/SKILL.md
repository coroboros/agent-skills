---
name: brainstorm
description: Strategic analysis and deep thinking before implementation. Researches the problem space, challenges assumptions, weighs tradeoffs, and produces a written strategic brief with a recommendation. Use this whenever the user needs to explore options, compare approaches, or pressure-test an idea before committing — even when they don't say "brainstorm" (e.g. "should we", "what's the best way", "evaluate", "pros and cons", "think through"). Not for implementation.
when_to_use: When the user needs to explore options before deciding. Architecture decisions, technology comparisons, strategy questions, "should we vs. should we not". When the user says "should we", "what's the best approach", "compare", "evaluate", "think through", "pros and cons", or asks an open-ended question that needs weighing. NOT for breaking down work into tasks — use `/spec`. NOT for implementation — use `/apex` or `/oneshot`.
argument-hint: "[-s] [-S] <question or topic>"
model: opus
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
metadata:
  author: coroboros
  sources:
    - github.com/anthropics/knowledge-work-plugins/tree/main/product-management/skills/product-brainstorming
    - github.com/Melvynx/aiblueprint
---

# Brainstorm

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

Strategic pre-implementation thinking for: $ARGUMENTS

## Parameters

| Flag | Behavior |
|------|----------|
| `-s` | Save the brief to `.claude/output/brainstorm/{slug}/brainstorm.md` |
| `-S` | Force no-save (override any ambient save mode) |

Flags are removed from input; remainder becomes `{topic}`. `{slug}` = kebab-case from the topic (max 5 words). Lowercase enables, uppercase disables — matches the repo-wide convention.

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

**Reframe before researching.** The stated problem is rarely the real one. Restate the problem behind it, then write 1-3 "How might we …" framings and name the one you'll pursue. Generating solutions here is out of scope — that's Phase 3.

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

### Phase 3 — Diverge

Generate the option set before judging any of it. Early convergence is the failure mode here.

- Produce **≥3 approaches that differ in mechanism**, not three variants of one. State why each is structurally distinct.
- Vary them along a real axis — scope (small tweak vs. big bet), strategy (build vs. buy vs. defer), direction (add vs. remove).
- Include one approach that removes or stops something rather than adding.
- Include one that inverts the obvious default — "what if we did the opposite?".
- No scoring, no "recommended", no hedging here. Evaluation is Phase 4.

Circling one idea? Pull a technique from `references/thinking-tools.md` (first-principles, inversion, reverse-brainstorm, elimination) — read it on demand, don't inline it.

### Phase 4 — Challenge

Pick a provisional leading approach and a runner-up from the Phase 3 set — first ranking allowed here. Then stress-test the leader before it becomes the recommendation.

- **Premortem.** It is six months out and this approach failed badly. List every plausible cause in the past tense — imagining the failure as already certain surfaces more failure modes than asking "what could go wrong".
- **Steelman the runner-up.** Argue the second-best approach at full strength. Name the condition under which it would win.
- What hidden costs exist (complexity, maintenance, vendor lock-in)?
- Which assumptions does the recommendation carry — fact, assumption, or inherited convention?
- Is there a simpler path that gets 80% of the value at 20% of the cost?

Be rigorous, not contrarian. Surface risks the user hasn't considered — for a sharper angle (inversion, first-principles), `references/thinking-tools.md` serves Challenge too.

### Phase 5 — Synthesize

Produce the strategic brief. Output in conversation by default, or save to `.claude/output/brainstorm/{slug}/brainstorm.md` when `-s` is set.

Use the canonical format in `references/brief-template.md` (read `${CLAUDE_SKILL_DIR}/references/brief-template.md` before writing).

### Phase 6 — Discuss

After the brief:

1. State the recommendation, the runner-up and what would flip it, and the top risk — in plain language.
2. Surface the open questions that need answers.
3. **Stop and wait** — do not implement anything.

## Bridge to next steps

If the brainstorm leads to work that requires code, suggest the path forward based on scope:

**Complex work** (multiple workstreams, needs planning):

```
/spec -s -f .claude/output/brainstorm/{slug}/brainstorm.md "{topic}"
```

`/spec` turns the brainstorm into a structured execution spec with prioritized workstreams, dependencies, and acceptance criteria, then bridges to `/apex` or creates GitHub issues.

**Focused work** (single clear task, ready to implement):

```
/apex -f .claude/output/brainstorm/{slug}/brainstorm.md {description}
```

`-f` passes the brainstorm as foundational context — `/apex` skips redundant research and focuses its analyze phase on implementation specifics.

If the brainstorm is purely strategic (tech choice, architecture decision, process change) with no immediate code to write, simply conclude the discussion — no bridging needed.

> **Dependency:** these bridges require the `spec` and/or `apex` skills. If unavailable, tell the user and suggest installing them, or proceed manually based on the brief.
