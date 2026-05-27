---
name: clean-output
description: Interactive listing + prompted deletion of accumulated artifacts under `~/.claude/output/{project}/...` (per-project) and `~/.claude/output/_global/...` (cross-project). Never auto-deletes — every group or file gets an explicit confirmation. Default scope is the current project bucket plus `_global`. `-A` widens to every per-project bucket; `-p <name>` narrows to one named project; `-l` lists without deleting; `-d` deletes everything in scope after a single count+size confirmation. The single user-invoked sweep for global skill outputs (forge plans, apex task workspaces, markitdown conversions, code-ultrareview reports, audio loops, brand-voice extracts).
when_to_use: When the user wants to clean up the global skill-output directory — review what's accumulated, delete a few directories, or empty a project's bucket. Triggers on "clean output", "clean up skill output", "purge artifacts", "free up `~/.claude/output`", "what's in my output dir", "delete old forge plans", "delete old apex tasks", "/clean-output", "cleanup". Skip when the target lives inside a working tree — `~/.claude/output/` is the global scratch directory, never in-repo content. Skip when the user wants to inspect a single artifact — they should `Read` it directly. Skip when the user wants a TTL or scheduled-prune policy — this skill is single-shot and user-invoked by design (see Rules).
argument-hint: "[-A] [-l] [-d] [-D] [-p <project>]"
model: sonnet
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
metadata:
  author: coroboros
---

# Clean-output

Interactive cleanup for `~/.claude/output/`. Lists artifacts under both buckets — the current project (`~/.claude/output/{project}/...`) and the cross-project bucket (`~/.claude/output/_global/...`) — grouped by emitting skill, with size and mtime per row. Prompts before any deletion. Never auto-deletes.

## Parameters

| Short | Long | Behavior |
|-------|------|----------|
| `-A` | `--all-projects` | List every `~/.claude/output/<project>/` bucket plus `_global`. Mutually exclusive with `-p`. Default: current project + `_global` only |
| `-p <name>` | `--project <name>` | Restrict the per-project listing to one named project (kebab-cased basename). Always includes `_global`. Mutually exclusive with `-A` |
| `-l` | `--list` | Read-only listing — never invokes `delete_artifact.py`; exits 0 after reporting |
| `-d` | `--delete-all` | Skip the action menu; prompt once with total count + total size; on confirmation, delete every artifact in scope |
| `-D` | `--no-delete-all` | Explicit override — disable an ambient `delete-all` mode if set elsewhere |

Lowercase enables, uppercase disables. `-A` uses capital A by convention — lowercase `-a` is reserved for `auto` across the skill family (forge, apex, oneshot). All flags default OFF.

### Requirements

- `python3` 3.10+, stdlib only — no `pip install` needed
- Read+delete permissions on `~/.claude/output/`

### Examples

```bash
/clean-output                          # interactive — current project + _global
/clean-output -l                       # list only — never deletes
/clean-output -A                       # every project bucket + _global
/clean-output -p my-app                # one specific project + _global
/clean-output -d                       # delete-all flow — single count+size confirmation
```

## Workflow

1. **Resolve scope.** Default → current `{project}` + `_global`. `-A` → every project + `_global`. `-p NAME` → that project + `_global`. `{project}` resolves via `git rev-parse --show-toplevel 2>/dev/null || pwd` → kebab-case basename → fallback `unnamed`, per `.claude/rules/repo-conventions.md` § Output paths.

2. **List artifacts.** Run `python3 ${CLAUDE_SKILL_DIR}/scripts/list_artifacts.py [--all-projects | --project NAME]`. The script emits a JSON array of `{bucket, project, skill, path, size_bytes, mtime_iso}`, where `bucket ∈ {"project", "_global"}`.

3. **Empty-scope branch.** If the listing is empty, report `no artifacts to clean` and exit 0. No prompts.

4. **Display listing.** Group by `(bucket, skill)`. For each group, print: bucket label, skill name, count, total size; then per-artifact rows with path / size / mtime ISO. Display before any prompt.

5. **Action menu** — skip if `-l` (read-only mode) or `-d` (delete-all bypass). Use `AskUserQuestion` (single-select; 4 options — the harness caps the question at 4):
   - **Keep everything** (recommended default)
   - **Delete everything in scope**
   - **Pick per bucket** — choose buckets, delete their full contents
   - **Pick at a finer grain** — opens a follow-up to pick per skill group or per individual file

6. **Branch on selection:**
   - **Keep everything** → exit 0 with `listing preserved — 0 files deleted`.
   - **Delete everything in scope** (or `-d`) → second `AskUserQuestion`: `Confirm delete: <N> artifacts, <total_size>?`. On confirmation, iterate the listing and call `delete_artifact.py` per path. On decline, exit 0.
   - **Pick per bucket** → `AskUserQuestion` (multi-select) with bucket names; iterate selected and delete.
   - **Pick at a finer grain** → second `AskUserQuestion` (single-select): **By skill group** (one row per `(bucket, skill)` pair) or **By individual file**. Then a third `AskUserQuestion` (multi-select) at the chosen granularity. If the candidate list exceeds 4 entries — the `AskUserQuestion` cap — page through it 4 at a time, accumulating selections across pages; delete the accumulated set once the listing is exhausted.

7. **Per-path deletion.** For every artifact, run `python3 ${CLAUDE_SKILL_DIR}/scripts/delete_artifact.py <abs-path>`. Expected exit 0. Exit 2 means the path failed the resolution guard — surface the stderr and halt (this is a script bug, not user input). Exit 1 means the path was missing or unwritable — log and continue with the next.

8. **Final report.** Total artifacts deleted, total bytes freed, any failures. Format:
   ```
   deleted N artifacts (M MB) · skipped K (reasons) · scope preserved: <list>
   ```

## Rules

- **Never auto-delete.** Every destructive path goes through `AskUserQuestion`. `-d` skips only the *action menu*, never the final count+size gate.
- **Never delete outside `~/.claude/output/`.** `delete_artifact.py` resolves every path with `Path(p).resolve().is_relative_to(<root>)` and exits 2 on violation. The script is the single chokepoint — the skill never invokes `rm` or `shutil.rmtree` directly.
- **No TTL, no SessionEnd auto-prune.** Repo policy in `.claude/rules/repo-conventions.md` § Cleanup. The user owns retention; the skill is single-shot and user-invoked.
- **Listing before prompts.** Step 4 always runs before step 5 — the user sees what they're about to act on.
- **`-l` and `-d` conflict — `-l` always wins.** Passing both keeps the read-only listing as a fail-safe — never silently switch to destructive behavior on a malformed invocation. Surface a one-line warning naming the conflict, then proceed as if only `-l` had been passed. Pinned by `tests/clean-output/test_skill_md.py::test_l_d_conflict_resolution_documented`.
- **`AskUserQuestion` 4-option cap — page multi-selects 4-at-a-time.** Any candidate list with more than 4 entries pages through 4 at a time, accumulating selections across pages before any deletion. Applies to step 6's finer-grain skill-group / per-file multi-select. Pinned by `tests/clean-output/test_skill_md.py::test_ask_user_question_cap_resolution_documented`.

## Bucket layout

The `~/.claude/output/` directory has two top-level layouts:

- `~/.claude/output/<project>/<skill>/...` — per-project (the default for every emitting skill)
- `~/.claude/output/_global/<skill>/...` — cross-project (opt-in for skills whose output is intentionally repo-agnostic)

`_global` is the literal directory name. `{project}` basenames never start with `_` after the kebab-case scrub in `.claude/rules/repo-conventions.md` § Output paths, so the sentinel is collision-safe.

## Gotchas

1. **`-p NAME` takes the kebab-case basename, not a path.** A working tree at `~/Desktop/Dev/my-org/my-app` resolves to project `my-app` — pass `-p my-app`, not the full path. Mismatch → empty listing for that bucket.
2. **Apex task directories count as one artifact.** A `~/.claude/output/<project>/apex/01-feature/` workspace bundles multiple step files; `list_artifacts.py` sums the file sizes and reports the most recent mtime. Deletion removes the whole tree atomically.
3. **`AskUserQuestion` caps at 4 options (single or multi-select).** Step 5 collapses to a 4-option menu. Step 6's multi-select pages 4-at-a-time when the candidate list exceeds 4, accumulating selections across pages before deletion. If the harness ever lifts the cap, both steps can re-expand inline.
4. **Stale `_global` listings after a skill is uninstalled.** If a skill that wrote to `_global` is removed but its artifacts remain, the listing reports `_global / <skill> / ...` with the orphan skill name. Treat as ordinary cleanup candidates — the path-resolution guard doesn't care which skill produced them.
5. **`--root <path>` is a test-fixture override.** Both bundled scripts accept `--root` to retarget the entire enumeration / guard under a temp dir. Never pass `--root` in production — that disarms the home-directory anchor.

## Scripts

- `scripts/list_artifacts.py` — stdlib enumeration; emits JSON `[{bucket, project, skill, path, size_bytes, mtime_iso}, ...]`. Flags: `--all-projects` / `--project NAME` / `--root PATH`.
- `scripts/delete_artifact.py` — stdlib path-guarded deletion. Argument: one absolute path. Flag: `--root PATH` (test override). Exit codes: 0 (deleted), 1 (missing or unwritable), 2 (guard violation — path outside root).

## Success criteria

- Listing shows both buckets (project + `_global`) grouped by skill, with size and mtime, before any prompt.
- `-l` exits 0 without ever calling the delete script.
- Default interactive flow asks once at the action menu; the **Delete everything** path asks a second time naming count + total size.
- `-d` skips the action menu but still asks the count + size confirmation.
- `-A` lists every per-project bucket plus `_global`; `-p NAME` lists one project plus `_global`.
- Path-resolution guard refuses paths outside `~/.claude/output/` with exit 2.
- Empty scope reports `no artifacts to clean` and exits 0 with no prompts.
