---
name: step-01-discover
description: Context gathering — prior docs, codebase reconnaissance, interactive Q&A
next_step: steps/step-02-specify.md
---

# Step 1: Discover

## Role

You are a researcher. Gather all the context needed for step-02 to write a comprehensive spec for `{idea}`. Do not structure workstreams, decide priorities, or write the spec itself — those are step-02's job. Do not create GitHub issues — that's step-03.

Focus on the question "What do I need to know?" not "What should we build?".

## Available state

From SKILL.md entry point:

| Variable | Description |
|----------|-------------|
| `{idea}` | The feature description |
| `{slug}` | Kebab-case identifier |
| `{auto_mode}` | Skip Q&A |
| `{save_mode}` | Save spec to file |
| `{issues_mode}` | Create GitHub issues |
| `{economy_mode}` | No subagents |
| `{from_file}` | Path to prior context file |
| `{output_dir}` | Path to output directory |
| `{output_file}` | Path to spec.md |

## Execution

### 1. Load prior context (if `{from_file}` is set)

Read `{from_file}` and detect type:

**Brainstorm report** (contains `# Brainstorm:` header):
- Extract Summary, Recommendation, Alternatives, Risks, Open questions, Next steps.
- Treat as foundational — skip re-researching topics already covered.
- Focus remaining research on implementation specifics the brainstorm doesn't cover.

**GitHub issue reference** (matches `#N`, `owner/repo#N`, or a GitHub URL):
- Fetch via `gh issue view <number> --json title,body,labels,assignees,comments,milestone`.
- Extract requirements from body, constraints from labels, discussion from comments.
- Carry forward acceptance criteria if present.

**RFC or design doc** (generic markdown):
- Extract key decisions, constraints, requirements, architecture notes.
- Note what's decided vs. what's still open.

**Plain text** (fallback):
- Treat as raw supplementary input.

When prior context exists, reduce Q&A to gaps only and keep subagents focused on what the prior doc doesn't answer.

### 2. Detect GitHub issue as direct input

If `{idea}` itself looks like a GitHub issue reference (`#123`, `org/repo#123`, or a URL):

1. Fetch via `gh issue view`.
2. Use the title as the idea, body as requirements.
3. Extract labels, milestone, assignees as constraints.
4. Note existing comments as context.
5. Update `{idea}` with the extracted title for step-02.

### 3. Codebase reconnaissance

First, check whether a meaningful codebase exists — look for source dirs (`src/`, `app/`, `lib/`, `packages/`), configuration (`package.json`, `CLAUDE.md`, `README.md`), build tools.

**If no codebase exists** (fresh scaffold, pre-code planning):

- Note explicitly that the spec will be architecture-first.
- Skip codebase subagents entirely.
- Focus research on approaches, patterns, and technology choices.
- step-02 will define what to build from scratch.

**If a codebase exists and `{economy_mode}` = true:**

Use direct tools only:

1. Read `CLAUDE.md`, `package.json`, `README.md` for project context.
2. Glob for files related to the idea keywords.
3. Grep for relevant patterns, functions, types.
4. Read the 3-5 most relevant files.

**If a codebase exists and `{economy_mode}` = false:**

Launch subagents according to complexity (see SKILL.md § Subagent strategy). Key point: exploration produces far more raw output than the spec needs — subagents keep that noise out of the main context.

**Explore agent prompt:**

```
Find existing code related to: {specific_area}
Report:
1. Files with paths and line numbers
2. Patterns used (routing, data fetching, validation, etc.)
3. Relevant utilities and shared code
4. Architecture and conventions
Do not suggest implementations.
```

**general-purpose agent prompt:**

```
Research approaches for: {specific_question}
Find current best practices, common patterns, and pitfalls.
Focus on: {specific_technology_or_library}
```

**Launch all chosen subagents in ONE message.** Parallel execution is the whole point.

### 4. Interactive Q&A

**If `{auto_mode}` = true:**

Skip Q&A. Make reasonable assumptions favoring simplicity and convention. Document them explicitly — step-02 will list them under "Assumptions".

**If `{auto_mode}` = false AND prior context exists:**

Ask only about gaps — 1-2 focused questions about what the prior context doesn't cover. Example: "The brainstorm recommends X. Are there constraints or preferences that would change this?"

**If `{auto_mode}` = false AND no prior context:**

Ask up to 5 focused, decision-forcing questions in a single message. Pick the most relevant — not all 5:

1. **Scope** — "What is the minimum viable version? What's explicitly out of scope?"
2. **Users** — "Who uses this? What's their primary workflow?"
3. **Constraints** — "Hard constraints? (timeline, tech stack, compatibility, third-party services)"
4. **Success criteria** — "How will you know this is done? What does success look like?"
5. **Dependencies** — "Does this depend on or block anything else in progress?"

Format as a numbered list. Wait for answers, then proceed — no follow-up rounds. One Q&A round maximum.

### 5. Synthesize discovery

Combine everything into an internal summary. This is raw material for step-02, not the spec output.

```
## Discovery Summary

### Problem Statement
[What needs to be built and why]

### Requirements
- Functional: [what it must do]
- Non-functional: [performance, security, UX constraints]

### Codebase Context
[Existing architecture, patterns, related code — or "No existing codebase"]

### Constraints
[Technical, timeline, budget, compatibility]

### Prior Context
[Key findings from brainstorm/RFC/issue, if any]

### Assumptions Made
[Only if auto_mode — explicit list of what was assumed]

### Risks Identified
[Potential issues spotted during discovery]
```

Present a brief summary to the user, then proceed directly to step-02:

```
**Discovery Complete**

**Sources:** {codebase, brainstorm, Q&A, research}
**Key findings:** {2-3 bullet points}

→ Specifying...
```

Do not ask for confirmation here. Proceed to step-02.

## Success

- Prior context loaded and integrated if `-f` was set
- Codebase patterns documented with file paths if codebase exists
- Q&A completed with focused questions if not auto_mode; assumptions documented if auto_mode
- No workstream structure or prioritization decisions made (that's step-02)
- Context synthesis ready for step-02

## Common failure modes

- Structuring workstreams or prioritizing in this step — step-02's job
- Multiple Q&A rounds — one maximum
- Over-launching subagents for a simple idea — wasteful
- Missing `{from_file}` when `-f` is set
- Re-researching topics the prior context already covers
- Asking the user for confirmation before proceeding — just proceed

## Next step

Always load `./step-02-specify.md` after presenting the discovery summary.
