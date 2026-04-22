---
name: step-01-analyze
description: Pure context gathering - explore codebase to understand WHAT EXISTS
next_step: steps/step-02-plan.md
---

# Step 1: Analyze (Context Gathering)

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER plan or design solutions - that's step 2
- 🛑 NEVER create todos or implementation tasks
- 🛑 NEVER decide HOW to implement anything
- ✅ ALWAYS focus on discovering WHAT EXISTS
- ✅ ALWAYS report findings with file paths and line numbers
- 📋 YOU ARE AN EXPLORER, not a planner
- 💬 FOCUS on "What is here?" NOT "What should we build?"
- 🚫 FORBIDDEN to suggest implementations or approaches

## 🧠 SMART AGENT STRATEGY

<critical>
**ADAPTIVE AGENT LAUNCHING** (unless economy_mode is true)

Before exploring, THINK about what information you need and launch the RIGHT agents - between 0 and 10 depending on task complexity.

**WHEN TO SPAWN:**
- ✅ Fanning out across independent items (multiple unrelated files, libraries, or concerns)
- ✅ Reading/searching enough material that it would flood the main context
- ✅ Research on an unfamiliar library where current docs matter

**WHEN NOT TO SPAWN (do it directly):**
- ❌ Work you can complete in a single response (e.g., the target file is already known, pattern is obvious, or prior context from `-f` already covers it)
- ❌ A single Glob/Grep/Read would answer the question
- ❌ The task touches one file or one tight cluster of files you can open directly

**DO NOT blindly launch all agents. BE SMART.** Prefer direct tools when they suffice — the overhead of spawning only pays off when the work is genuinely parallel or context-heavy.
</critical>

## EXECUTION PROTOCOLS:

- 🎯 Launch parallel exploration agents (unless economy_mode)
- 💾 Append findings to output file (if save_mode)
- 📖 Document patterns with specific file:line references
- 🚫 FORBIDDEN to proceed until context is complete

## CONTEXT BOUNDARIES:

- Variables from step-00-init are available
- No implementation decisions have been made yet
- Codebase state is unknown - must be discovered
- Don't assume knowledge about the codebase

## YOUR TASK:

Gather ALL relevant context about WHAT CURRENTLY EXISTS in the codebase related to the task.

---

<available_state>
From step-00-init:

| Variable | Description |
|----------|-------------|
| `{task_description}` | What to implement |
| `{task_id}` | Kebab-case identifier |
| `{auto_mode}` | Skip confirmations |
| `{save_mode}` | Save outputs to files |
| `{economy_mode}` | No subagents, direct tools |
| `{from_file}` | Path to prior context file (if -f provided) |
| `{output_dir}` | Path to output (if save_mode) |
</available_state>

---

## EXECUTION SEQUENCE:

### 0. Load Prior Context (if from_file)

**If `{from_file}` is set:**

**Detect input type and load accordingly:**

**GitHub issue reference** (`{from_file}` matches `#N`, `owner/repo#N`, or a GitHub URL like `https://github.com/.../issues/N`):
1. Fetch via `gh issue view <number> --json title,body,labels,assignees,comments,milestone`
2. Extract: title as task context, body as requirements, labels as constraints, comments as discussion
3. If the issue body contains acceptance criteria or task lists, carry them forward as `{acceptance_criteria}`
4. Use the issue content as foundational context — skip re-researching topics already described in the issue

**Local file** (brainstorm report, spec, RFC, design doc, etc.):
1. **Read the file** using the Read tool
2. **Extract key findings**: recommendation, constraints, risks, decisions already made
3. **Skip redundant research**: do NOT re-research topics already covered in the file — focus agents on implementation-specific questions (existing code patterns, file structure, utilities) that the prior analysis doesn't cover
4. **Carry forward open questions**: flag any unresolved items from the prior analysis

The prior context (whether from an issue or a file) replaces the need for web research on topics it already covers. Codebase exploration subagents are still valuable since the prior context typically doesn't map implementation details.

### 1. Initialize Save Output (if save_mode)

**If `{save_mode}` = true:**

```bash
bash {skill_dir}/scripts/update-progress.sh "{task_id}" "01" "analyze" "in_progress"
```

Append findings to `{output_dir}/01-analyze.md` as you work.

### 2. Extract Search Keywords

From the task description, identify:
- **Domain terms**: auth, user, payment, etc.
- **Technical terms**: API, route, component, etc.
- **Action hints**: create, update, fix, add, etc.

These keywords guide exploration - NOT planning.

### 3. Explore Codebase

**If `{economy_mode}` = true:**
→ Use direct tools (see step-00b-economy.md for rules)

```
1. Glob to find files: **/*{keyword}*
2. Grep to search content in likely locations
3. Read the most relevant 3-5 files
4. Skip web research unless stuck
```

**If `{economy_mode}` = false:**
→ Use SMART agent strategy below

---

### 🧠 STEP 3A: ANALYZE TASK COMPLEXITY

**Before launching agents, THINK:**

```
Task: {task_description}

1. SCOPE: How many areas of the codebase are affected?
   - Single file/function → Low
   - Multiple related files → Medium
   - Cross-cutting concerns → High

2. LIBRARIES: Which external libraries are involved?
   - None or well-known basics → Skip docs
   - Unfamiliar library or specific API needed → Need docs
   - Multiple libraries interacting → Need multiple doc agents

3. PATTERNS: Do I need to understand existing patterns?
   - Simple addition → Maybe skip codebase exploration
   - Must integrate with existing code → Need codebase exploration

4. UNCERTAINTY: What am I unsure about?
   - Clear requirements, known approach → Fewer agents
   - Unclear approach, unfamiliar territory → More agents
```

---

### 🎯 STEP 3B: CHOOSE YOUR SUBAGENTS (1-10)

**Available Subagent Types (built-in):**

| Type | Use When |
|------|----------|
| `Explore` | Need to find existing patterns, related files, utilities (read-only, fast) |
| `general-purpose` | Need library docs, web research, approaches, gotchas (full tool access) |

**Decision Matrix:**

| Task Type | Subagents Needed | Example |
|-----------|------------------|---------|
| **Trivial / already-contextual** | 0 | Rename a function you already see, or task fully covered by `-f` context → use Read/Grep directly |
| **Simple fix** | 1-2 | Bug fix in known file → 1x Explore |
| **Add feature (familiar stack)** | 2-3 | Add button → 1x Explore + 1x general-purpose (web research) |
| **Add feature (unfamiliar library)** | 3-5 | Add Stripe → 1x Explore + 1x general-purpose (Stripe docs) + 1x general-purpose (web research) |
| **Complex integration** | 5-8 | Auth + payments → 2x Explore (different areas) + 2-3x general-purpose (docs + research) |
| **Major feature (multiple systems)** | 6-10 | Full e-commerce → Multiple Explore + multiple general-purpose |

---

### 🚀 STEP 3C: LAUNCH SUBAGENTS IN PARALLEL

**Launch ALL chosen subagents in ONE message using the Agent tool.**

**Subagent Prompts:**

**`Explore`** — codebase discovery (read-only, fast):
```
Find existing code related to: {specific_area}

Report:
1. Files with paths and line numbers
2. Patterns used for similar features
3. Relevant utilities
4. Test patterns

DO NOT suggest implementations.
```

**`general-purpose`** — library docs or web research:
```
Research {library_name} documentation for: {specific_question}
Find current API, code examples, and configuration needed.
```
```
Search the web for: {specific_question_or_approach}
Find common patterns, best practices, and pitfalls.
```

---

### 📋 EXAMPLE SUBAGENT LAUNCHES

**Simple task** (fix button styling) → 1 subagent:
```
[Explore: find button components and styling patterns]
```

**Medium task** (add user profile page) → 3 subagents:
```
[Explore: find user-related components and data fetching patterns]
[Explore: find page layout and routing patterns]
[general-purpose: search web for profile page best practices in this framework]
```

**Complex task** (add Stripe subscriptions) → 6 subagents:
```
[Explore: find existing payment/billing code]
[Explore: find user account and settings patterns]
[general-purpose: research Stripe subscription API and webhooks docs]
[general-purpose: research Stripe Customer Portal integration docs]
[general-purpose: search web for Stripe subscriptions implementation patterns]
[general-purpose: search web for Stripe webhook security best practices]
```

### 4. Synthesize Findings

Combine results into structured context:

```markdown
## Codebase Context

### Related Files Found
| File | Lines | Contains |
|------|-------|----------|
| `src/auth/login.ts` | 1-150 | Existing login implementation |
| `src/utils/validate.ts` | 20-45 | Email validation helper |

### Patterns Observed
- **Route pattern**: Uses Next.js App Router with `route.ts`
- **Validation**: Uses zod schemas in `schemas/` folder
- **Error handling**: Throws custom ApiError classes

### Utilities Available
- `src/lib/auth.ts` - JWT sign/verify functions
- `src/lib/db.ts` - Prisma client instance

### Similar Implementations
- `src/auth/login.ts:42` - Login flow (reference for patterns)

### Test Patterns
- Tests in `__tests__/` folders
- Uses vitest with testing-library

## Documentation Insights

### Libraries Used
- **jose**: JWT library - uses `SignJWT` class
- **prisma**: ORM - uses `prisma.user.create()` pattern

## Research Findings

### Common Approaches
- Registration: validate → hash → create → issue token
- Use httpOnly cookies for tokens
```

**If `{save_mode}` = true:** Append synthesis to 01-analyze.md

### 5. Infer Acceptance Criteria

Based on task and context, infer success criteria:

```markdown
## Inferred Acceptance Criteria

Based on "{task_description}" and existing patterns:

- [ ] AC1: [specific measurable outcome]
- [ ] AC2: [specific measurable outcome]
- [ ] AC3: [specific measurable outcome]

_These will be refined in the planning step._
```

**If `{save_mode}` = true:** Update 00-context.md with acceptance criteria

### 6. Present Context Summary

**Always (regardless of auto_mode):**

Present summary and proceed directly to planning:

```
**Context Gathering Complete**

**Files analyzed:** {count}
**Patterns identified:** {count}
**Utilities found:** {count}

**Key findings:**
- {summary of relevant files}
- {patterns that will guide implementation}

→ Proceeding to planning phase...
```

<critical>
Do NOT ask for user confirmation here - always proceed directly to step-02-plan.
</critical>

### 7. Complete Save Output (if save_mode)

**If `{save_mode}` = true:**

Append summary to `{output_dir}/01-analyze.md` then:

```bash
bash {skill_dir}/scripts/update-progress.sh "{task_id}" "01" "analyze" "complete"
bash {skill_dir}/scripts/update-progress.sh "{task_id}" "02" "plan" "in_progress"
```

---

## SUCCESS METRICS:

✅ Related files identified with paths and line numbers
✅ Existing patterns documented with specific examples
✅ Available utilities noted
✅ Dependencies listed
✅ Acceptance criteria inferred
✅ NO planning or implementation decisions made
✅ Output saved (if save_mode)
✅ Task complexity analyzed BEFORE launching agents
✅ Right NUMBER of agents launched (0-10 based on complexity — zero is valid when direct tools suffice)
✅ Right TYPE of agents chosen for the task
✅ All agents launched in PARALLEL (single message)

## FAILURE MODES:

❌ Starting to plan or design (that's step 2!)
❌ Suggesting implementations or approaches
❌ Missing obvious related files
❌ Not documenting patterns with file:line references
❌ Launching agents sequentially instead of parallel
❌ Using subagents when economy_mode is true
❌ **CRITICAL**: Blocking workflow with unnecessary confirmation prompts
❌ Launching too many agents for a simple task (wasteful)
❌ Launching too few agents for a complex task (insufficient context)
❌ Not analyzing task complexity before choosing agents
❌ Skipping documentation research when genuinely unfamiliar with a library API

## ANALYZE PROTOCOLS:

- This step is ONLY about discovery
- Report what EXISTS, not what SHOULD BE
- Include file paths and line numbers for all findings
- Don't assume - verify by reading files
- In economy mode, use direct tools only

---

## NEXT STEP:

Always proceed directly to `./step-02-plan.md` after presenting context summary.

<critical>
Remember: Analysis is ONLY about "What exists?" - save all planning for step-02!
Do NOT ask for confirmation - proceed directly!
</critical>
