---
name: step-04-examine
description: Self-check - run tests, verify AC, audit implementation quality, complete workflow
prev_step: steps/step-03b-refine.md
next_step: null
---

# Step 4: eXamine (Self-Check)

Verify the final deliverable against every accepted criterion using `references/quality-lens.md`. Fix task-caused failures, preserve unrelated work and report baseline failures separately. Missing required evidence blocks a claim of complete verification.

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

If `{goal_mode}` is true and the host supports `/goal`, resolve the checks in § 2 and emit:

```
/goal All AC verified: <AC list one per line from {acceptance_criteria}>.
Proof: <required checks and evidence appropriate to the deliverable>.
Derivation lens returns CONSISTENT or only DECISION-OVERRIDE with documented rationale.
Task-owned changes stay within the accepted scope; unrelated initial work is preserved.
Continue while a concrete authorized step can improve closure; report a blocker when no such step remains.
```

If `{acceptance_criteria}` is empty (trivial task), substitute `(none — task trivially completes when checks pass)`.

Record actual command output and exit status. For other checks, state the observed result and supporting evidence in the transcript, with a source or artifact citation; the goal gate cannot inspect files itself.

If `{goal_mode}` = false, skip this step entirely. If `/goal` is unavailable in your harness, skip the goal gate and proceed.

### 1. Initialize Save Output (if save_mode)

**If `{save_mode}` = true:**

`$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing the skill's SKILL.md elsewhere.

```bash
bash "$SKILL_DIR"/scripts/update-progress.sh "{task_id}" "04" "examine" "in_progress"
```

Append results to `{output_dir}/04-examine.md` as you work.

### 2. Select Applicable Checks

Read project instructions, the plan and relevant manifests for required checks. Apply the lens's `Correctness` checks to the deliverable: sources, calculations, links, instructions and rendered output as relevant. Use installed domain skills and tools. Run typecheck, lint, tests or build only where applicable; distinguish a missing required tool from an inapplicable check.

### 3. Run Validation Suite

Reuse successful checks from Execute or Refine when their inputs and environment are unchanged. Run missing checks and rerun those invalidated by later edits or unresolved failures; the sections below name required evidence, not repeated commands.

**3.0 Derivation lens**

Load `references/derivation-lens.md` and run its self-contained review. Compare the diff against `{output_dir}/02-plan.md` and classify each divergence. With `{save_mode}` = false there is no `02-plan.md` — reconcile against the approved plan from the step-02 conversation instead.

**Gating:**

- **GAP** findings → **MUST PASS**. Completion blocks until the authorized missing work is implemented or a concrete blocker is reported. Do not ask again for already authorized fixes.
- **SCOPE-ADD** findings → remove unnecessary task-owned additions under `references/derivation-lens.md`; preserve unrelated pre-existing work. An addition outside the accepted mandate remains a scope decision for the user.
- **DECISION-OVERRIDE** findings → apply the owner's disposition: record justified reversible implementation decisions; leave user-owned decisions pending.
- **CONSISTENT** → no finding; counted in coverage.

Log a one-line summary to `04-examine.md` (when `{save_mode}`):

```
**Derivation lens:** GAP: <n> · SCOPE-ADD: <n> (disposition recorded) · DECISION-OVERRIDE: <n> · CONSISTENT: <n>
```

**3.1 Typecheck**

When applicable, run the project's typecheck command. Fix task-caused failures and rerun the affected check.

**3.2 Lint**

When applicable, run the project's lint command. Scope any fixes to task-owned changes.

**3.3 Artifact and behavior checks**

Run the remaining checks selected in § 2, including focused tests for changed code. Inspect the actual result, not just the commands or source that produced it. Record what each check proves and any unverified criterion.

**3.4 Adversarial self-check (skipped for mechanical changes)**

Give a fresh-context skeptic (a `general-purpose` subagent) the accepted criteria, changes, final artifact and evidence. Ask it to find defects using the lens's `Correctness` and `Reviewing` rules. Keep the review bounded to the task.

**Stakes gate:**

- Mechanical changes as `references/quality-lens.md` defines them → skip; applicable checks suffice.
- Any other change (new logic, control flow, a boundary, anything a reviewer would pause on) → run the skeptic.
- `{economy_mode}` = true → skip the subagent; perform a separate shared-context self-check instead; do not call it independent verification.
- Harness without subagents → same shared-context fallback; disclose the reduced independence.

**Defects only.** Give the skeptic the lens's `Reviewing` rule. Fix a confirmed defect within the accepted scope with the smallest change `references/quality-lens.md` allows.

**No silent drop.** Each skeptic finding either gets fixed (rerun affected checks), is refuted in writing here, or is filed as a known limitation in the completion summary. A finding that vanishes without a verdict is a defect. Don't re-litigate settled, already-tested behavior — spend the effort on what the change actually puts at risk.

**3.5 Security check (trust-boundary changes only)**

For a trust-boundary change as the lens's `Security floor` defines it, add that section to the skeptic's refutation targets (in economy mode or without subagents, to the shared-context self-check). Security findings are fixed or reported, never dropped.

### 4. Self-Audit Checklist

Verify each item:

**Tasks Complete:**
- [ ] All todos from step-03 marked complete
- [ ] No tasks skipped without reason
- [ ] Any blocked tasks have explanation

**Verification:**

- [ ] Required and affected checks pass; baseline failures and unavailable checks are identified
- [ ] Evidence covers each changed behavior or content claim
- [ ] No skipped tests without reason

**Quality Evidence** — each line cites its artifact; `references/quality-lens.md` defines the rules:

- [ ] Budget: each Design budget item planned vs actual from the task diff, or `mechanical change`; each excess removed or classified by the derivation lens
- [ ] Refine: the record identifies the reviewer or self-review, findings and dispositions, or its skip reason
- [ ] Skills: each skill Analyze listed was applied, with any deviation recorded
- [ ] Conventions: structure and presentation fit the surrounding material and applicable domain rules

**Deliverable Hygiene** — checklist gate for the `## Critical — Label hygiene` canonical block in SKILL.md and the expanded rule in `step-03-execute.md`. All three must stay in sync.
- [ ] No internal labels (workstream `WS-N`, task IDs, plan phase names) in code, comments, commit/PR text, or docs the change ships
- [ ] No private plan, spec, postmortem, APEX-phase or scratch-path references in shipped artifacts; preserve public sources and requested traceability
- [ ] Comments explain a why the code cannot — no comment that merely restates the next line

### 5. Format and Recheck

Apply required formatting to task-owned changes. After the last edit, rerun checks it invalidates, including rendered inspection when presentation changes. Reuse still-valid results.

### 6. Report the Outcome

State the result, changed files, checks and what they proved. Include material budget deviations, unresolved findings and unavailable required evidence. Report statuses as passed, failed, unavailable or not applicable, with the reason; never prefill success. Omit empty sections and routine counters.

### 7. Complete Save Output (if save_mode)

**If `{save_mode}` = true:**

Append to `{output_dir}/04-examine.md`:
```markdown
---
## Step Complete
**Status:** ✓ Complete
**Verification:** {actual checks and results}
**Timestamp:** {ISO timestamp}
```

Mark complete only after every accepted criterion and required check is verified:

`bash "$SKILL_DIR"/scripts/update-progress.sh "{task_id}" "04" "examine" "complete"`
