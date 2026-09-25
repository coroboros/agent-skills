---
name: step-03b-refine
description: Refine - remove what the task did not need before examination
prev_step: steps/step-03-execute.md
next_step: steps/step-04-examine.md
---

# Step 3b: Refine

The code works; now make it the diff a senior engineer would ship. Refine only deletes, reuses or shrinks, and every accepted behavior survives it. The context that wrote the code judges it generously, so a reviewer that did not write it, and may only remove work, provides the counterweight. Examine then validates the refined code.

## Inputs

- The task's own changes since the starting revision recorded in Analyze: commits, staged and unstaged hunks, and untracked task files. Pre-existing user edits stay out of scope.
- The plan's `Design budget` and `Leave out` lists.
- `references/quality-lens.md`.
- `{acceptance_criteria}` and `{negative_acceptance}`.

Skip a mechanical change as the lens defines it: record the reason, then run § 7 so the progress row still closes.

## 1. Initialize (if save_mode)

Progress calls in this step apply when the table has a `03b-refine` row; tasks saved before Refine existed have none.

`$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing the skill's SKILL.md elsewhere.

```bash
bash "$SKILL_DIR"/scripts/update-progress.sh "{task_id}" "03b" "refine" "in_progress"
```

## 2. Measure

- Compare the task diff with the `Design budget`: new files, exported symbols, abstractions, dependencies, config keys, net lines.
- Count the comment lines the task added.
- Run the project's lint on changed files, plus dead-code or duplication tools only when the project already declares them. Never install or resolve a package to run a check.

## 3. Review

Give one fresh-context reviewer (a `general-purpose` subagent) the prompt below with the task's hunks, not the author's reasoning. Economy mode or no subagents: run the same prompt yourself, count call sites with search instead of judging from memory, and label the record `shared-context`.

```
Review a finished diff you did not write. Remove what the task did not need;
never add features, checks, tests or comments.

<criteria>{acceptance criteria and negative scope}</criteria>
<budget>{Design budget and Leave out lists}</budget>
<lens>{references/quality-lens.md}</lens>
<diff>{the task's hunks only}</diff>

Work read-only. Read the surrounding code to verify every reuse or duplicate
claim. Report only lines this task added or changed; ignore bugs and
formatter-owned style.

One line per finding:
<tag> <file:line> — <lens rule> → <exact replacement | delete> (−N lines)
Tags: delete · reuse · stdlib · native · yagni · dry · shrink · efficiency ·
altitude · comment · prose (prose includes planning labels and process
narration in shipped text)

End with `net: −N lines` or `Lean already. Ship.` Zero findings is valid.
```

## 4. Apply

- Apply findings that keep every accepted behavior, the public signatures that existed before the task, and the assertions that test accepted criteria. Signatures, options, files and tests the task itself introduced may shrink, merge or move with the code.
- Reject a finding that removes an item on the lens's `Never simplified away` list or breaks a `Readability guards` rule; record the reason.
- Report a finding that would change an accepted behavior or pre-existing code to Examine instead of applying it.
- Leave pre-existing code outside the task's hunks untouched, except to call the existing owner a finding names.

## 5. Re-check

Run typecheck, lint and the affected tests. A failure reverts the finding that caused it; Refine never fixes forward. Step-04 runs the full validation afterwards.

## 6. Record

With `{save_mode}`, append to `## Refine` in `{output_dir}/03-execute.md`; otherwise state it in the conversation for Examine:

```
Backend: subagent | shared-context
Applied: <tag file:line> …
Rejected: <finding> — <guard or evidence>
Reported to Examine: <behavior-changing finding> …
Net: −N lines · comments added: N (each with its why) · budget: files a/b, symbols a/b, abstractions a/b, deps a/b, config a/b
```

Run one pass. Repeated review churns code and costs more than it removes.

## 7. Complete

With `{save_mode}`:

```bash
bash "$SKILL_DIR"/scripts/update-progress.sh "{task_id}" "03b" "refine" "complete"
bash "$SKILL_DIR"/scripts/update-progress.sh "{task_id}" "04" "examine" "in_progress"
```

Proceed to `./step-04-examine.md`, pausing first only for a checkpoint the user requested before validation; Refine asks no questions.
