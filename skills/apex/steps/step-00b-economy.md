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

### Override 5: Verification

Keep step-04's required evidence for the deliverable. Replace independent reviewers with disclosed shared-context checks; reuse passing evidence until an edit invalidates it. Economy mode does not waive required tests, source checks or rendered inspection.

</override_rules>

---

<step_specific_overrides>

## Step-by-Step Economy Overrides

### Step 01: Analyze (Economy)
```
INSTEAD OF: parallel Explore + general-purpose subagents
DO:
1. Glob "**/*{keyword}*" for task-related files
2. Search the relevant source, document or data locations
3. Read affected material and its sources or consumers
4. Identify existing owners and tools; inspect dependency manifests when code is involved
5. Look up current documentation whenever required or uncertainty affects the change
```

### Step 02: Plan (Economy)
```
Same as default; the step carries the council's shared-context fallback
```

### Step 03: Execute (Economy)
```
Same as default - execution doesn't use agents
```

### Step 03b: Refine (Economy)
```
Same as default; the step carries the reviewer's shared-context fallback
```

### Step 04: eXamine (Economy)
```
Same applicable checks as default; use a disclosed shared-context skeptic
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
- Applicable checks pass for the final deliverable
</success_metrics>
