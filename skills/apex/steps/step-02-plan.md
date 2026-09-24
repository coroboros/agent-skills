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

- Context from step-01 (files, patterns, utilities) is available
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
| Utilities | From step-01 utility discovery |
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
- Walk the build ladder in `references/quality-lens.md` for each capability, starting from Analyze's `Reuse inventory`
- Identify all files that need changes
- Determine logical order (dependencies first)
- Consider the edge cases real callers produce and where each error is handled
- Plan test coverage

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

**Structure by FILE, not by feature.** Each file entry binds the quality lens to that change: what it reuses, what it leaves out, and the control that applies there. The example is reuse-first on purpose; a new file or abstraction appears only with a recorded reason.

```markdown
## Implementation Plan: {task_description}

### Overview
[1-2 sentences: strategy and the lowest build-ladder rung that meets the criteria]

### Prerequisites
- [ ] Prerequisite (if any)

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
New files 0 · exported symbols 1 · abstractions 0 · dependencies 0 · config keys 0 · est. net lines +25
Count production code; tests follow the Testing Strategy. Justify each non-zero item in one clause.

### Skills
- `<installed skill>` — load before editing `<file>` (from Analyze's `Applicable skills`), or `none`

---

### Testing Strategy

One focused test per accepted criterion or changed behavior, sized like the neighboring tests. No tests that mirror the implementation; scratch checks stay uncommitted.
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

After writing the plan but before verification, stress-test it inline. Write directly to `02-plan.md`:

- **Premortem** — one bullet: "6 months out, this plan failed AC1 because ___." Imagine the failure as already certain — surfaces more failure modes than "what could go wrong?".
- **Alternative** — name a simpler file-change path concretely. Adopt it when it meets every AC; keep the leading plan only for a named criterion or risk the alternative misses.

No `AskUserQuestion` here — this is model reasoning in the artifact, not a user prompt. Interactive mode (`-i`) handles user pauses separately.

### 4b. Surgical-scope check (advisory)

Use these rough scope heuristics to notice when replanning could help; they are not capability limits or automatic stop gates:

- **Files** — > 5 modified or added → flag.
- **Systems / domains** — > 2 distinct (e.g., auth + billing + notifications) → flag.
- **Cross-cutting concerns** — database migration, API + client coupled changes, auth/permission rewrite → flag any.

If any threshold trips, append a `⚠️ Scope advisory` block to `02-plan.md`:

```
⚠️ Scope advisory
- Files: <count> (threshold 5)
- Systems: <list> (threshold 2)
- Cross-cutting: <list or none>

This is within apex's design scope. Consider `/forge` for explicit decomposition if scope is unclear.
```

Advisory only — never blocks step-02. The check is the dogfood for solo apex runs without an upstream forge plan; apex documents its own scope when it grows.

### 4c. Kill council

The author defends its own plan; a reviewer that did not write it, and never proposes additions, catches the reinvented helper and the speculative layer before any code exists. Skip the council when the plan touches one file and adds no file, exported symbol, dependency or config key; record `Council: skipped — minimal plan`.

Give one fresh-context `general-purpose` subagent the prompt below, without your deliberation:

```
You are the kill council for an implementation plan you did not write.
Never propose features, checks or abstractions; report an uncovered
criterion as GAP.

<brief>{task, accepted criteria, negative scope}</brief>
<reuse_inventory>{Analyze's Reuse inventory}</reuse_inventory>
<plan>{file entries and Design budget}</plan>
<lens>{Build ladder and Minimum structure from references/quality-lens.md}</lens>

You have read access. Verify every reuse claim in code or docs before reporting it.
Lenses, in order:
1. Kill — which criterion needs no new code (existing behavior, configuration, nothing)?
2. Reuse — for each new function, module, type, dependency or config key, does a lower rung already provide it?
3. Shrink — which planned file, symbol, parameter or branch can go while every criterion holds?

One line per finding:
KILL|REUSE|SHRINK <plan element> → <replacement | remove> — evidence: <file:line | doc | criterion>
GAP <criterion> — no planned change satisfies it
End with `budget: files N→M, symbols N→M, deps N→M` or `Plan is minimal.`
Zero findings is valid. No style, naming or robustness suggestions.
```

Disposition — record each finding under `## Kill council` in `02-plan.md`:

- **Apply before approval:** REUSE and SHRINK findings with verified evidence that keep every criterion; every GAP.
- **User-owned:** a KILL of an element that carries a criterion, or any finding that changes the approach or negative scope. Present it at the plan checkpoint. With `{auto_mode}`, record it and deliver the requested outcome with the simplest compliant plan, unless proceeding conflicts with a documented constraint or makes the work unsafe or useless; then pause for the user.
- **Rejected:** one line of evidence each. No finding disappears without a verdict.

Economy mode or no subagents: run the same three lenses yourself in the same format and label the section `shared-context self-check`.

### 5. Verify Plan Completeness

Checklist:
- [ ] All files identified - nothing missing
- [ ] Logical order - dependencies handled first
- [ ] Clear actions - every step specific and actionable
- [ ] Test coverage - all paths have test strategy
- [ ] In scope - no scope creep
- [ ] AC mapped - every criterion has implementation
- [ ] Reuse bound - every file entry names its rung; every non-zero budget item has a reason
- [ ] Council resolved - every finding applied, user-owned, or rejected with evidence (or the skip recorded)

### 6. Present Plan for Approval

```
**Implementation Plan Ready**

**Overview:** [1 sentence summary]

**Files to modify:** {count} files
**New files:** {count} files
**Tests:** {count} test files
**Design budget:** files {n} · symbols {n} · abstractions {n} · deps {n} · config {n}
**Kill council:** {applied} applied · {user_owned} for your decision · {rejected} rejected (or skipped — minimal plan)

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
✅ Test strategy defined
✅ Design budget set and kill council findings dispositioned
✅ User approved plan (or auto-approved)
✅ NO code written or modified
✅ Output saved (if save_mode)

## FAILURE MODES:

❌ Organizing by feature instead of file
❌ Vague actions like "add feature" or "fix issue"
❌ Missing test strategy
❌ A new file, abstraction or dependency without a recorded rung and reason
❌ Not mapping to acceptance criteria
❌ Starting to write code (that's step 3!)
❌ **CRITICAL**: Not using AskUserQuestion for approval (when it is available)

## PLANNING PROTOCOLS:

- Structure by FILE - each file is a section
- Include line number references from analysis
- Every action must be specific and actionable
- Map every AC to specific file changes
- Plan tests alongside implementation

---

## NEXT STEP:

After user approves via AskUserQuestion (or auto-proceed), load `./step-03-execute.md`

<critical>
Remember: Planning is ONLY about designing the approach - save all implementation for step-03!
</critical>
