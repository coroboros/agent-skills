---
name: step-00b-economy
description: Economy mode overrides - no subagents, direct tool usage to save tokens
load_condition: economy_mode = true
---

# Economy Mode Overrides

**This file is ONLY loaded when `-e` or `--economy` flag is active.** Harnesses without subagents load it too — the same overrides apply regardless of the flag.

These instructions OVERRIDE the default behavior in all steps to save tokens by avoiding subagent launches.

---

<why_economy_mode>
**Purpose:** Reduce token usage for users on limited plans.

**Trade-offs:**
- Avoids subagent overhead; actual cost depends on the task
- ✅ Faster execution (no agent overhead)
- Preserve the same accepted outcomes and required evidence
- ⚠️ No parallel research
- ⚠️ May miss some context

**When to use:**
- Limited monthly token budget
- Simple, well-defined tasks
- Familiar codebase
- Quick fixes or small features
</why_economy_mode>

---

<override_rules>

## CRITICAL: Apply These Overrides to ALL Steps

**When `{economy_mode}` = true, these rules OVERRIDE the default instructions:**

---

### Override 1: No Subagent Launches

**DEFAULT behavior (when economy_mode = false):**
```
Launch parallel built-in subagents:
- Explore: codebase patterns, files, utilities
- general-purpose: library docs, web research, approaches
```

**ECONOMY behavior (when economy_mode = true):**
```
Use direct tools instead:
- Glob to find files
- Grep to search content
- Read to examine files
- WebSearch only if absolutely necessary
```

**NEVER use Task tool with subagent_type in economy mode.**

---

### Override 2: Direct Tool Usage Pattern

Instead of launching exploration agents, use this pattern:

```
1. Glob to find relevant files:
   - Glob: "**/*auth*" or "**/*{keyword}*"
   - Glob: "src/**/*.ts" for specific areas

2. Grep to find specific code:
   - Grep: "function login" or "class Auth"
   - Grep: pattern in specific directory

3. Read to examine found files:
   - Read relevant files, callers, and dependencies until the change is understood
   - Focus on files matching the task

4. WebSearch ONLY if:
   - Library documentation needed
   - Unknown API or pattern
   - Follow the host's current-documentation requirements
```

---

### Override 3: Reduced Exploration Scope

**DEFAULT:** Explore comprehensively, find all related code
**ECONOMY:** Focus on most likely locations only

```
Economy exploration strategy:
1. Start with obvious paths (src/auth/, src/api/, etc.)
2. Search for exact keywords from task
3. Read only files directly related to task
4. Skip "nice to have" context
5. Stop exploring when you have enough to proceed
```

---

### Override 4: Skip Optional Steps

**In economy mode, skip or minimize:**
- Redundant documentation reads after a current authoritative source resolves the question
- Optional background research unrelated to the accepted outcomes

**Always do:**
- Find the files to modify
- Understand existing patterns (quick read)
- Identify dependencies
- Create the plan

---

### Override 5: Leaner Validation

**DEFAULT:** Comprehensive examination via step-04 (Bash typecheck/lint, full test runs, self-audit)
**ECONOMY:** Self-review without exhaustive runs

```
Economy validation:
1. Run typecheck and lint (required)
2. Run affected tests (required)
3. Quick self-review checklist:
   - [ ] No obvious bugs
   - [ ] Follows existing patterns
   - [ ] Error handling present
   - [ ] No security issues
4. Run full-suite checks when the repository requires them or changed behavior warrants them
```

</override_rules>

---

<step_specific_overrides>

## Step-by-Step Economy Overrides

### Step 01: Analyze (Economy)
```
INSTEAD OF: parallel Explore + general-purpose subagents
DO:
1. Glob "**/*{keyword}*" for task-related files
2. Grep for specific patterns in src/
3. Read relevant files and their affected callers
4. Look up current documentation whenever required or uncertainty affects the change
```

### Step 02: Plan (Economy)
```
Same as default - planning doesn't use agents
```

### Step 03: Execute (Economy)
```
Same as default - execution doesn't use agents
```

### Step 04: eXamine (Economy)
```
INSTEAD OF: Comprehensive examination
DO:
1. Run typecheck + lint
2. Run affected tests and repository-required checks
3. Quick manual review
4. Skip coverage analysis
```

</step_specific_overrides>

---

<economy_indicator>
**When economy mode is active, start each step with:**

```
⚡ ECONOMY MODE - Using direct tools, no subagents
```

This reminds both the agent and the user that economy mode is active.
</economy_indicator>

---

<success_metrics>
Economy mode is successful when:
- No Task tool calls with subagent_type
- Direct Glob/Grep/Read usage instead
- Required current-documentation questions resolved
- Implementation still correct and working
- Tests pass for affected files
</success_metrics>
