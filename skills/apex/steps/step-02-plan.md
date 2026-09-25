---
name: step-02-plan
description: Strategic planning - create detailed file-by-file implementation strategy
prev_step: steps/step-01-analyze.md
next_step: steps/step-03-execute.md
---

# Step 2: Plan (Strategic Design)

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER start implementing - that's step 3
- 🛑 NEVER write or modify code in this step
- ✅ ALWAYS structure plan by FILE, not by feature
- ✅ ALWAYS include specific line numbers from analysis
- ✅ ALWAYS map acceptance criteria to file changes
- 📋 YOU ARE A PLANNER, not an implementer
- 💬 FOCUS on "What changes need to be made where?"
- Use read-only inspection and the tools needed to save the plan and update progress; do not modify implementation files.

## EXECUTION PROTOCOLS:

- 🎯 ULTRA THINK before creating the plan
- 💾 Save plan to output file (if save_mode)
- 📖 Reference patterns from step-01 analysis
- Honor the plan checkpoint unless auto mode or an existing explicit approval/no-pause instruction covers execution. The latest explicit pause request still binds.

## CONTEXT BOUNDARIES:

- Context from step-01 (files, patterns, reuse inventory) is available
- Implementation has NOT started
- User has NOT approved any changes yet
- Plan must be complete before execution

## YOUR TASK:

Transform analysis findings into a comprehensive, executable, file-by-file implementation plan.

---

<available_state>
From previous steps:

| Variable | Description |
|----------|-------------|
| `{task_description}` | What to implement |
| `{task_id}` | Kebab-case identifier |
| `{acceptance_criteria}` | Success criteria from step-01 |
| `{negative_acceptance}` | Negative scope (must-NOT criteria) from step-01 |
| `{auto_mode}` | Skip confirmations |
| `{save_mode}` | Save outputs to files |
| `{output_dir}` | Path to output (if save_mode) |
| Files found | From step-01 codebase exploration |
| Patterns | From step-01 pattern analysis |
| Reuse inventory | From step-01 |
</available_state>

---

## EXECUTION SEQUENCE:

### 1. Initialize Save Output (if save_mode)

**If `{save_mode}` = true:**

`$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing the skill's SKILL.md elsewhere.

```bash
bash "$SKILL_DIR"/scripts/update-progress.sh "{task_id}" "02" "plan" "in_progress"
```

Append plan to `{output_dir}/02-plan.md` as you work.

### 2. ULTRA THINK: Design Complete Strategy

**CRITICAL: Think through ENTIRE implementation before writing any plan.**

Mental simulation:
- Walk through the implementation step by step
- Identify reuse opportunities using `references/quality-lens.md` and Analyze's `Reuse inventory`; apply the code ladder when relevant
- Identify all files that need changes
- Determine logical order (dependencies first)
- Consider the edge cases real callers produce and where each error is handled
- Plan evidence appropriate to the deliverable: tests, source checks, calculations, rendered inspection or usage checks

### 3. Clarify Ambiguities

**If `{auto_mode}` = true:**
→ Use recommended option for any ambiguity, proceed automatically

**If `{auto_mode}` = false AND multiple valid approaches exist:**
→ Ask via AskUserQuestion when available, otherwise in plain text, and wait for the reply:

```yaml
questions:
  - header: "Approach"
    question: "Multiple approaches are possible. Which should we use?"
    options:
      - label: "Approach A (Recommended)"
        description: "Description and tradeoffs of A"
      - label: "Approach B"
        description: "Description and tradeoffs of B"
      - label: "Approach C"
        description: "Description and tradeoffs of C"
    multiSelect: false
```

### 4. Create Detailed Plan

**Structure by file or deliverable.** Each entry names its change, reuse target, exclusions and verification. Adapt the code example below to the task.

```markdown
## Implementation Plan: {task_description}

### Overview
[1-2 sentences: strategy and the lowest build-ladder rung that meets the criteria]

### Prerequisites
- [ ] Prerequisite 1 (if any)
- [ ] Prerequisite 2 (if any)

---

### File Changes

#### `src/billing/invoice.ts`
- Change: add `lateFee(invoice, now)` beside `applyFee` (pattern at `fees.ts:12`)
- Reuse: rung 2 — `fees.ts:12 applyFee`, `money.ts:8 round`
- Leave out: rate config flag (one consumer), docstring
- Checks: pure calculation; I/O stays in `routes/invoice.ts`

#### `src/routes/invoice.ts`
- Change: call `lateFee` in the existing GET handler at line ~42
- Reuse: rung 2 — the `invoiceParams` schema at line 12 already validates the request
- Leave out: new endpoint, response envelope changes
- Checks: trust boundary — unknown invoice ids keep the existing 404 path

---

### Design budget
New files 0 · exported symbols 1 (`lateFee`, called from the route) · abstractions 0 · dependencies 0 · config keys 0 · est. net lines +25
Count the items `references/quality-lens.md` names for the task type; in code, count production code and let tests follow the Verification Strategy. Justify each non-zero item in one clause; a mechanical change records `mechanical change` instead.

---

### Verification Strategy

Choose evidence for each accepted criterion using the lens's `Correctness` checks. For code, cover changed behavior and handled error paths with focused tests; update existing tests where needed. Avoid tests that mirror implementation. Scratch checks stay uncommitted.
- `src/billing/invoice.test.ts` — AC1 fee after the due date; AC2 no fee before it

---

### Acceptance Criteria Mapping
- [ ] AC1: Satisfied by changes in `file1.ts`
- [ ] AC2: Satisfied by changes in `file2.ts`

---

### Risks & Considerations
- Risk 1: [potential issue and mitigation]
```

**If `{save_mode}` = true:** Append full plan to 02-plan.md

### 4a. Challenge the plan (inline, no user gate)

After writing the plan but before verification, stress-test it inline. Record this in the saved plan when `{save_mode}` is true, otherwise in the conversation:

- **Premortem** — one bullet: "6 months out, this plan failed AC1 because ___." Imagine the failure as already certain — surfaces more failure modes than "what could go wrong?".
- **Alternative** — name a simpler file-change path concretely. Adopt it when it meets every AC; keep the leading plan only for a named criterion or risk the alternative misses.

Record the decision and its evidence, not private deliberation. Interactive mode (`-i`) handles user pauses separately.

### 4b. Surgical-scope check (advisory)

Use these rough scope heuristics to notice when replanning could help; they are not capability limits or automatic stop gates:

- **Files** — > 5 modified or added → flag.
- **Systems / domains** — > 2 distinct (e.g., auth + billing + notifications) → flag.
- **Cross-cutting concerns** — database migration, API + client coupled changes, auth/permission rewrite → flag any.

If any threshold trips, append a `⚠️ Scope advisory` block to the saved plan or conversation:

```
⚠️ Scope advisory
- Files: <count> (threshold 5)
- Systems: <list> (threshold 2)
- Cross-cutting: <list or none>

This is within apex's design scope. Consider `/forge` for explicit decomposition if scope is unclear.
```

Advisory only — never blocks step-02. The check is the dogfood for solo apex runs without an upstream forge plan; apex documents its own scope when it grows.

### 4c. Kill council

Skip the council for a mechanical change as `references/quality-lens.md` defines it, or when the plan touches one file and its Design budget is zero apart from net lines; record `Council: skipped — <reason>`.

Give one fresh-context `general-purpose` subagent the prompt below, without your deliberation:

```
You are the kill council for an implementation plan you did not write.
Never propose features, checks or abstractions.

<brief>{task, accepted criteria, negative scope, Analyze's Documented constraints}</brief>
<reuse_inventory>{Analyze's Reuse inventory}</reuse_inventory>
<plan>{file entries and Design budget}</plan>
<lens>{references/quality-lens.md}</lens>

Work read-only: no edits, copies or scratch files. Verify every reuse claim in code or docs before reporting it.
Lenses, in order:
1. Kill — which criterion is already satisfied, and which planned element conflicts with a documented constraint?
2. Reuse — which existing owner, content, data or tool already serves a planned addition?
3. Shrink — which file, section, step or code element can go while every criterion holds?

One line per finding:
KILL|REUSE|SHRINK <plan element> → <replacement | remove> — evidence: <file:line | doc | criterion>
End with each changed Design budget item as `item N→M`, or `Plan is minimal.`
Zero findings is valid. No style, naming or robustness suggestions.
```

Disposition — record each finding under `Kill council` in the saved plan when `{save_mode}` is true, otherwise in the conversation:

- **Apply before approval:** REUSE and SHRINK findings with verified evidence that keep every criterion.
- **User-owned:** a KILL of an element that carries a criterion, or any finding that changes the approach or negative scope. Present it at the plan checkpoint. With `{auto_mode}`, the accepted criteria and negative scope stay fixed: adopt such a finding only when it satisfies both, otherwise record it and deliver the requested outcome. When proceeding conflicts with a documented constraint or makes the work unsafe or useless, pause for the user.
- **Rejected:** one line of evidence each. No finding disappears without a verdict.

Economy mode or no subagents: run the same three lenses yourself in the same format and label the section `shared-context self-check`.

### 5. Verify Plan Completeness

Checklist:
- [ ] All files identified - nothing missing
- [ ] Logical order - dependencies handled first
- [ ] Clear actions - every step specific and actionable
- [ ] Verification - every criterion has appropriate evidence planned
- [ ] In scope - no scope creep
- [ ] AC mapped - every criterion has implementation
- [ ] Reuse bound - each entry identifies applicable reuse; every non-zero budget item has a reason
- [ ] Council resolved - every finding applied, user-owned, or rejected with evidence (or the skip recorded)

### 6. Present Plan for Approval

```
**Implementation Plan Ready**

**Overview:** [1 sentence summary]

**Files to modify:** {count} files
**New files:** {count} files
**Tests:** {count} test files
**Design budget:** {each item with its count}
**Kill council:** {applied} applied · {user_owned} for your decision · {rejected} rejected (or skipped — {reason})

**Estimated changes:**
- `file1.ts` - Major changes (add function, handle errors)
- `file2.ts` - Minor changes (imports, single call)
- `file1.test.ts` - New test file
```

**If `{auto_mode}` = true or the user already approved this plan or explicitly authorized continuing without another pause:**
→ Skip confirmation, proceed directly to execution

**If `{auto_mode}` = false and no prior explicit approval/no-pause instruction covers execution, or the latest user instruction requests a checkpoint (including an explicit `-A`):**
→ Ask via AskUserQuestion when available, otherwise in plain text, and wait for the reply:

```yaml
questions:
  - header: "Plan"
    question: "Review the implementation plan. Ready to proceed?"
    options:
      - label: "Approve and execute (Recommended)"
        description: "Plan looks good, start implementation"
      - label: "Adjust plan"
        description: "I want to modify specific parts"
      - label: "Ask questions"
        description: "I have questions about the plan"
      - label: "Start over"
        description: "Revise the entire plan"
    multiSelect: false
```

### 7. Complete Save Output (if save_mode)

**If `{save_mode}` = true:**

Append to `{output_dir}/02-plan.md`:
```markdown
---
## Step Complete
**Status:** ✓ Complete
**Files planned:** {count}
**Tests planned:** {count}
**Next:** step-03-execute.md
**Timestamp:** {ISO timestamp}
```

then:

```bash
bash "$SKILL_DIR"/scripts/update-progress.sh "{task_id}" "02" "plan" "complete"
bash "$SKILL_DIR"/scripts/update-progress.sh "{task_id}" "03" "execute" "in_progress"
```

---

## SUCCESS METRICS:

✅ Complete file-by-file plan created
✅ Logical dependency order established
✅ All acceptance criteria mapped to changes
✅ Verification strategy defined
✅ User approved plan (or auto-approved)
✅ NO code written or modified
✅ Output saved (if save_mode)

## FAILURE MODES:

❌ Organizing by feature instead of file
❌ Vague actions like "add feature" or "fix issue"
❌ Missing verification strategy
❌ Not mapping to acceptance criteria
❌ Starting to write code (that's step 3!)
❌ **CRITICAL**: Not using AskUserQuestion for approval (when it is available)

## PLANNING PROTOCOLS:

- Structure by FILE - each file is a section
- Include line number references from analysis
- Every action must be specific and actionable
- Map every AC to specific file changes
- Plan verification alongside implementation

---

## NEXT STEP:

After user approves via AskUserQuestion (or auto-proceed), load `./step-03-execute.md`

<critical>
Remember: Planning is ONLY about designing the approach - save all implementation for step-03!
</critical>
