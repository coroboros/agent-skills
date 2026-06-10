---
name: step-04-examine
description: Self-check - run tests, verify AC, audit implementation quality, complete workflow
prev_step: steps/step-03-execute.md
next_step: null
---

# Step 4: eXamine (Self-Check)

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER claim checks pass when they don't
- 🛑 NEVER skip any validation step
- ✅ ALWAYS run typecheck, lint, and tests
- ✅ ALWAYS verify each acceptance criterion
- ✅ ALWAYS fix failures before proceeding
- 📋 YOU ARE A VALIDATOR, not an implementer
- 💬 FOCUS on "Does it work correctly?"
- 🚫 FORBIDDEN to proceed with failing checks

## EXECUTION PROTOCOLS:

- 🎯 Run all validation commands
- 💾 Log results to output (if save_mode)
- 📖 Check each AC against implementation
- 🚫 FORBIDDEN to mark complete with failures

## CONTEXT BOUNDARIES:

- Implementation from step-03 is complete
- Tests may or may not pass yet
- Type errors may exist
- Focus is on verification, not new implementation

## YOUR TASK:

Examine the implementation by running checks, verifying acceptance criteria, and ensuring quality.

---

<available_state>
From previous steps:

| Variable | Description |
|----------|-------------|
| `{task_description}` | What was implemented |
| `{task_id}` | Kebab-case identifier |
| `{acceptance_criteria}` | Success criteria |
| `{negative_acceptance}` | Negative scope (must-NOT criteria) — read by derivation lens |
| `{goal_mode}` | Emit `/goal` directive at start of this step |
| `{auto_mode}` | Skip confirmations |
| `{save_mode}` | Save outputs to files |
| `{economy_mode}` | No subagents mode |
| `{output_dir}` | Path to output (if save_mode) |
| Implementation | Completed in step-03 |
</available_state>

---

## EXECUTION SEQUENCE:

### 0. Emit /goal directive (if `{goal_mode}`)

**If `{goal_mode}` = true**, emit the `/goal` directive AT THE START of this step (before save initialization), populated with the discovered check commands from § 2 below and the acceptance criteria from step-01:

```
/goal All AC verified: <AC list one per line from {acceptance_criteria}>.
Proof: <typecheck cmd> exits 0, <lint cmd> exits 0, <test cmd> exits 0.
Derivation lens returns CONSISTENT or only DECISION-OVERRIDE with documented rationale.
No file outside the planned scope is modified.
Stop after 15 turns.
```

Resolve `<typecheck cmd>`, `<lint cmd>`, `<test cmd>` from § 2 "Discover Available Commands" before emission. If `{acceptance_criteria}` is empty (trivial task), substitute `(none — task trivially completes when checks pass)`.

Command tokens must land verbatim in the transcript — the Haiku evaluator behind `/goal` only judges what it sees, so paraphrases like "tests pass" defeat the gate.

If `{goal_mode}` = false, skip this step entirely. If `/goal` is unavailable in your harness, skip the goal gate and proceed.

### 1. Initialize Save Output (if save_mode)

**If `{save_mode}` = true:**

`$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing the skill's SKILL.md elsewhere.

```bash
bash "$SKILL_DIR"/scripts/update-progress.sh "{task_id}" "04" "examine" "in_progress"
```

Append results to `{output_dir}/04-examine.md` as you work.

### 2. Discover Available Commands

Check `package.json` scripts and CLAUDE.md for the project's exact command names.
Look for: `typecheck`, `lint`, `test`, `build`, `format` (or equivalents).

### 3. Run Validation Suite

**3.0 Derivation lens**

Load `references/derivation-lens.md` and run the lens — code-ultrareview's Python orchestrator if detected, else the inline fallback. Compare the diff against `{output_dir}/02-plan.md` and classify each divergence.

**Gating:**

- **GAP** findings → **MUST PASS**. Workflow blocks; surface planned-but-missing items; user resolves each (implement OR amend plan + AC) before completion.
- **SCOPE-ADD** findings → continue (advisory). Escalate to **Medium and require user acknowledgement** when the addition matches a `## Not Included` entry from the plan's negative scope.
- **DECISION-OVERRIDE** findings → continue. Surface for user judgment.
- **CONSISTENT** → no finding; counted in coverage.

Log a one-line summary to `04-examine.md`:

```
**Derivation lens:** GAP: <n> · SCOPE-ADD: <n> (advisory) · DECISION-OVERRIDE: <n> · CONSISTENT: <n>
```

**3.1 Typecheck**

Run the project's typecheck command.

**MUST PASS.** If fails:
1. Read error messages
2. Fix type issues
3. Re-run until passing

**3.2 Lint**

Run the project's lint command.

**MUST PASS.** If fails:
1. Try auto-fix variant first (e.g., `--fix` or `--write`)
2. Manually fix remaining
3. Re-run until passing

**3.3 Tests**

Run the project's test command (scoped to affected area if possible).

**MUST PASS.** If fails:
1. Identify failing test
2. Determine if code bug or test bug
3. Fix the root cause
4. Re-run until passing

**If `{save_mode}` = true:** Log each result

**3.4 Adversarial self-check (non-trivial changes only)**

Per the `## Critical — Adversarial verification` block in SKILL.md, the context that wrote the change cannot reliably clear it. After the suite passes, spawn one fresh-context skeptic — a `general-purpose` subagent — on the diff, tasked to refute: find the bug, the missed edge case, the spec deviation. Keep it bounded; this is an in-loop self-check, not code-ultrareview's full multi-axis gate.

**Stakes gate:**

- Trivial or mechanical changes (formatting, a rename, a one-line fix, a doc edit) → skip; the suite is enough.
- Non-trivial changes (new logic, control flow, a boundary, anything a reviewer would pause on) → run the skeptic.
- `{economy_mode}` = true → skip the subagent; self-refute inline instead.
- Harness without subagents → same fallback: self-refute inline.

**No silent drop.** Each skeptic finding either gets fixed (re-run the suite), is refuted in writing here, or is filed as a known limitation in the completion summary. A finding that vanishes without a verdict is a defect. Don't re-litigate settled, already-tested behavior — spend the effort on what the change actually puts at risk.

### 4. Self-Audit Checklist

Verify each item:

**Tasks Complete:**
- [ ] All todos from step-03 marked complete
- [ ] No tasks skipped without reason
- [ ] Any blocked tasks have explanation

**Tests Passing:**
- [ ] All existing tests pass
- [ ] New tests written for new functionality
- [ ] No skipped tests without reason

**Patterns Followed:**
- [ ] Code follows existing patterns
- [ ] Error handling consistent
- [ ] Naming conventions match

**Deliverable Hygiene** — checklist gate for the `## Critical — Label hygiene` canonical block in SKILL.md and the expanded rule in `step-03-execute.md`. All three must stay in sync.
- [ ] No internal labels (workstream `WS-N`, task IDs, plan phase names) in code, comments, commit/PR text, or docs the change ships
- [ ] No references to the plan, spec, postmortem, APEX phases, or scratch-file paths in shipped artifacts
- [ ] Comments explain a why the code cannot — no comment that merely restates the next line

### 5. Format Code

Run the project's format command if available.

### 6. Final Verification

Re-run typecheck and lint commands. Both MUST pass.

### 7. Present Validation Results

```
**Validation Complete**

**Typecheck:** ✓ Passed
**Lint:** ✓ Passed
**Tests:** ✓ {X}/{X} passing
**Format:** ✓ Applied
**Adversarial self-check:** ✓ {N findings resolved | skipped — trivial change}

**Derivation lens:** GAP: 0 · SCOPE-ADD: {n} (advisory) · DECISION-OVERRIDE: {n} (surfaced) · CONSISTENT: {n}

**Files Modified:** {list}

**Summary:** All checks passing, ready for next step.
```

### 8. Complete Workflow

**Show final summary:**

```
✅ APEX Workflow Complete

**Task:** {task_description}
**Task ID:** {task_id}

**Validation Results:**
- Typecheck: ✓ Passed
- Lint: ✓ Passed
- Tests: ✓ Passed

**Derivation lens:** GAP: 0 · SCOPE-ADD: {n} (advisory) · DECISION-OVERRIDE: {n} (surfaced) · CONSISTENT: {n}

**Files Modified:** {list}

🎉 Implementation complete and examined!
```

### 9. Complete Save Output (if save_mode)

**If `{save_mode}` = true:**

Append to `{output_dir}/04-examine.md`:
```markdown
---
## Step Complete
**Status:** ✓ Complete
**Typecheck:** ✓
**Lint:** ✓
**Tests:** ✓
**Workflow:** Complete
**Timestamp:** {ISO timestamp}
```

Run: `bash "$SKILL_DIR"/scripts/update-progress.sh "{task_id}" "04" "examine" "complete"`

---

## SUCCESS METRICS:

✅ Typecheck passes
✅ Lint passes
✅ All tests pass
✅ All AC verified
✅ Code formatted
✅ User informed of status
✅ Workflow completed

## FAILURE MODES:

❌ Claiming checks pass when they don't
❌ Not running all validation commands
❌ Skipping tests for modified code
❌ Missing AC verification
❌ Proceeding with failures

## VALIDATION PROTOCOLS:

- Run EVERY validation command
- Fix failures IMMEDIATELY
- Don't proceed until all green
- Verify EACH acceptance criterion
- Document all results

---

## WORKFLOW COMPLETE

This is the final step. After validation passes, the APEX workflow is complete.

<critical>
Remember: NEVER claim completion with failing checks - fix everything first!
</critical>
