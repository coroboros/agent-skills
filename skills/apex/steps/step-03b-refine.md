---
name: step-03b-refine
description: Refine - remove what the task did not need before examination
prev_step: steps/step-03-execute.md
next_step: steps/step-04-examine.md
---

# Step 3b: Refine

Refine only deletes, reuses or shrinks the task's code; every accepted behavior survives. One pass, no questions.

## Inputs

- The task's own changes since the starting revision recorded in Analyze: commits, staged and unstaged hunks, and untracked task files. Pre-existing user edits stay out of scope.
- The plan's `Design budget` and `Leave out` lists.
- `references/quality-lens.md`.
- `{acceptance_criteria}` and `{negative_acceptance}`.

Skip a mechanical change as the lens defines it: record the reason, then run the Complete calls so the progress row closes.

## 1. Initialize (if save_mode)

Progress calls in this step apply when the table has a `03b-refine` row; tasks saved before Refine existed have none.

`$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing the skill's SKILL.md elsewhere.

```bash
bash "$SKILL_DIR"/scripts/update-progress.sh "{task_id}" "03b" "refine" "in_progress"
```

## 2. Tools

Run the dead-code or duplication tools the project already declares on changed files, if any, and pass their findings to the reviewer. Never install or resolve a package to run a check.

## 3. Review

Give one fresh-context reviewer (a `general-purpose` subagent) the prompt below with the task's hunks, not the author's reasoning. Economy mode or no subagents: run the same prompt yourself, count call sites with search instead of judging from memory, and label the record `shared-context`.

```text
Review a finished diff you did not write. Remove what the task did not need;
never add features, checks, tests or comments.

<criteria>{acceptance criteria and negative scope}</criteria>
<budget>{Design budget and Leave out lists}</budget>
<lens>{references/quality-lens.md}</lens>
<diff>{the task's hunks only}</diff>
<tools>{findings from the Tools step, or none}</tools>

Work read-only. Read the surrounding code to verify every reuse or duplicate
claim. Report only lines this task added or changed; ignore bugs and
formatter-owned style.

One line per finding:
<tag> <file:line> — <lens rule> → <exact replacement | delete> (−N lines)
Tags: delete · reuse · shrink · dry · efficiency · comment · prose

End with the estimated net line change or `No justified simplification found.` Zero findings is valid; verification belongs to Examine.
```

## 4. Apply

- Verify each proposed replacement against its callers and the lens's `Never simplified away` list before applying it; record the evidence for each rejection. Signatures, options, files and tests the task itself introduced may shrink, merge or move with the code when their accepted contracts survive.
- Report a finding that would change pre-existing code outside the task to Examine instead of applying it.

## 5. Re-check

Rerun checks invalidated by an applied refinement; retain still-valid results from Execute. If a refinement causes a failure, restore only that refinement and recheck. Report unrelated or baseline failures separately. With no edits, carry the existing evidence into Examine.

## 6. Record

With `{save_mode}`, append a `## Refine` section to `{output_dir}/03-execute.md`; otherwise state it in the conversation for Examine:

```text
Backend: subagent | shared-context
Applied: <tag file:line> …
Rejected: <finding> — <reason>
Reported to Examine: <finding> …
Net: ±N lines
```

## 7. Complete

With `{save_mode}`:

```bash
bash "$SKILL_DIR"/scripts/update-progress.sh "{task_id}" "03b" "refine" "complete"
bash "$SKILL_DIR"/scripts/update-progress.sh "{task_id}" "04" "examine" "in_progress"
```

Proceed to `./step-04-examine.md`.
