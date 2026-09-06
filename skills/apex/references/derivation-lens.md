# Derivation lens — accepted outcomes against the final artifact

Compare every accepted criterion with the final implementation and its evidence. This review is self-contained: it requires no sibling skill or analyzer.

## Source and change coverage

1. Read the accepted plan (`02-plan.md` when saved, otherwise the conversation), later user corrections, and negative scope. Keep every accepted criterion; do not cap the list.
2. Use the starting revision and initial worktree status recorded during Analyze to identify this task's changes. Inspect committed changes since that revision, staged and unstaged changes, and relevant untracked files (`git status --short`, `git diff --cached`, `git diff`, and file reads). A branch diff alone does not cover unfinished work.
3. Preserve unrelated pre-existing edits. If no baseline was recorded, reconstruct ownership from available evidence and disclose uncertainty rather than attributing all dirty files to this task.
4. Read the final artifact, relevant callers, and check results. A criterion already satisfied before the change can be CONSISTENT: absence from the diff alone is not a GAP.

## Classifications and response

| Tag | Evidence | Response |
| --- | --- | --- |
| `GAP` | An accepted outcome remains unmet or unverified | Complete the authorized work or verification. If blocked, report the missing outcome and cause; do not claim completion. |
| `SCOPE-ADD` | A change does not serve an accepted outcome | Remove task-owned unnecessary changes. If useful but outside authorization or expressly excluded, surface the concrete decision for the user. |
| `DECISION-OVERRIDE` | Implementation differs from the plan | Record the reason and evidence. Continue for reversible implementation details within scope; escalate only a user-owned decision or authorization boundary. |
| `CONSISTENT` | Final behavior and evidence satisfy the criterion | Record the supporting file or check. |

Necessary test helpers and scaffolding are covered by the outcome they support. Never lower acceptance criteria solely to make an implementation pass.

## Output

Record the criterion, classification, supporting evidence, and unresolved limitation in the existing Examine output. Report counts only after reviewing the complete set. Repeat only evidence invalidated by later changes. Completion requires every accepted outcome satisfied, with material findings resolved or explicitly reported as blocking.
