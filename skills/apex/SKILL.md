---
name: apex
description: Systematic implementation using APEX methodology (Analyze-Plan-Execute-eXamine) with parallel subagents and self-validation. Use when implementing features, fixing bugs, or making code changes that benefit from structured workflow.
when_to_use: When the task is non-trivial and benefits from analysis before coding. When multiple files are involved, the codebase is unfamiliar, or thoroughness matters more than speed. When the user says "implement", "build", "add feature" for anything beyond a quick fix. NOT for trivial single-file changes — use `/oneshot` for those. NOT for exploration or planning only — use `/forge`. On a Fable-class or newer frontier session, prefer `/ultrapex`; apex is the pick for step-gated checkpoints and resumable state.
argument-hint: "[-a] [-s] [-e] [-b] [-i] [-g] [-f <context>] [-r <task-id>] <task description>"
license: MIT
compatibility: "Optimized for Claude Code; degrades gracefully on any agent implementing the Agent Skills standard."
metadata:
  author: coroboros
  sources:
    - github.com/Melvynx/aiblueprint
---

# Apex

<!-- canonical:adversarial-verification:start -->
## Critical — Adversarial verification

These rules govern how this skill trusts its own output — apply them whenever it verifies a claim, a defect, a source, or a decision before acting on it.

- Refute by default. Treat each non-trivial finding as unproven until a fresh-context check fails to refute it — the context that produced a claim cannot reliably clear it.
- No silent drop. Every finding flips the conclusion, is refuted in writing, or is filed as a risk or open question. A finding that vanishes without a verdict is a defect.
- Don't re-litigate settled facts. Spend adversarial effort on load-bearing or contested claims; let established facts pass. Over-refutation manufactures false doubt — it does not add rigor.
- Stay selective and cost-aware. Scale verification to the stakes; reversible, low-impact work gets a light touch, not a full adversarial sweep.
- Concede only to a strong rebuttal. A weak counter folds into the finding or gets filed; it does not overturn it.
<!-- canonical:adversarial-verification:end -->

<!-- canonical:execution-discipline:start -->
## Important — Engineering discipline

These rules govern how this skill changes code — apply them whenever it writes, edits, or proposes a fix.

- Minimal scope. Only what's directly requested or clearly necessary — no extra files, no abstraction for one use, no configurability nobody asked for, no error handling for states that can't happen. Validate at system boundaries; trust internal code.
- General solution, not the test cases. Implement the real logic for all valid inputs; never hard-code to inputs or bolt on workaround scripts to make a test pass. Tests verify the solution; they don't define it. A test is wrong? Say so — don't bend correct code to a broken test.
- Investigate before claiming. Never speculate about code you haven't opened; read the referenced file before answering. Ground every claim in what you actually read, not a plausible guess.
<!-- canonical:execution-discipline:end -->

<!-- canonical:label-hygiene:start -->
## Critical — Label hygiene

Internal planning labels are author coordinates, not reader coordinates. Strip them from every shipped artifact this skill emits — code, comments, commit subjects/bodies, PR titles/descriptions, release notes, doc paragraphs, non-trivial comments.

- **Workstream and task labels** — `WS-N`, `Phase-A`, `Step-3`, issue or ticket numbers, plan phase names from the source spec, issue body, or planning artifact. Translate to the domain noun (`Runs the battery script (WS-2)` → `Runs the battery script`). <!-- noqa: internal-label -->
- **Process language** — "the rebuild", "the prior `<file>`", "carried verbatim from", "the cleanup pass", "the audit", "spec AC" standalone. Replace with the concrete fact (`carries the routing from the prior aggregation` → `routes via the merge keys in the synthesis module`). <!-- noqa: internal-label -->
- **Plan-internal references** — "as the brief says", "per the workstream", "from the forge artifact". Drop the reference; state the fact directly.

Carve-outs — literal `WS-N` is legitimate where the skill IS the format authority (forge templates, apex rule documentation). Reviewer-facing dev docs (e.g. `MIGRATION.md` under `tests/<skill>/`) may reference deleted artifacts by their author-time names.
<!-- canonical:label-hygiene:end -->

<!-- canonical:writing-rules:start -->
## Important — Writing rules

These rules govern every prose artifact this skill emits — READMEs, CHANGELOGs, commit messages, PR bodies, release notes, doc paragraphs, non-trivial comments. Apply them at draft time, verify before output.

- Match the surrounding style — punctuation, capitalization, backtick conventions, em-dash vs parens, bullet style.
- Every sentence changes the reader's understanding. Cut it otherwise.
- Front-load the verb — "Creates", not "This helps you create".
- Concrete over abstract. Lists for ≥3 enumerable items.
- Assert positively. Reserve negation for real constraints (`NEVER commit secrets`).
- No marketing words: powerful, robust, seamlessly, leverage, unlock, comprehensive, delightful.
- No AI tells: delve, tapestry, intricate, pivotal, testament, underscore, crucial, garner, showcase, additionally, moreover, furthermore, indeed.
- After drafting English prose, invoke `/humanize-en` if installed.
<!-- canonical:writing-rules:end -->

## Objective

Execute systematic implementation workflows using the APEX methodology. This skill uses progressive step loading to minimize context usage and supports saving outputs for review and resumption.

## Quick Start

**Basic usage:**

```bash
/apex add authentication middleware
```

**Recommended workflow (autonomous with save):**

```bash
/apex -a -s implement user registration
```

**Flags:**

- `-a` (auto): Skip confirmations
- `-s` (save): Save outputs to `~/.claude/output/{project}/apex/`
- `-e` (economy): No subagents, save tokens

See **Parameters** below for the complete flag list.

## Parameters

| Short | Long | Off | Long-off | Behavior |
|-------|------|-----|----------|----------|
| `-a` | `--auto` | `-A` | `--no-auto` | Skip confirmations, auto-approve plans |
| `-s` | `--save` | `-S` | `--no-save` | Save outputs to `~/.claude/output/{project}/apex/` |
| `-e` | `--economy` | `-E` | `--no-economy` | No subagents, direct tools only |
| `-b` | `--branch` | `-B` | `--no-branch` | Verify not on main; create branch if needed |
| `-i` | `--interactive` | — | — | Configure flags via AskUserQuestion |
| `-g` | `--goal` | `-G` | `--no-goal` | Wire `/goal` to loop step-04 until AC verified (v2.1.139+; auto-on under `claude -p`) |
| `-r` | `--resume` | — | — | Continue from a previous task (takes `<task-id>`) |
| `-f` | `--from` | — | — | Prior context: GitHub issue (`#N`, URL), forge plan (e.g. `~/.claude/output/{project}/forge/forge-{slug}.md`), or any file as foundational input. Non-Markdown → pre-process via `/markitdown -s` |

Parsing algorithm, defaults, examples, and override semantics (lowercase enables, uppercase disables): `steps/step-00-init.md`.

## Compatibility

`-g` (the `/goal` integration) requires **Claude Code v2.1.139 or later**. On older versions, Claude Code rejects the unknown slash command and the flag becomes a no-op without halting apex. If `/goal` is unavailable in your harness, skip the goal gate and proceed.

The `/goal` evaluator is **transcript-only** — it cannot run tools or read files independently. The emitted condition therefore forces command output into the transcript verbatim (e.g. `npm test exits 0`, not "tests pass") so the evaluator has a deterministic signal to judge.

`-g` is **orthogonal to `-a`**: `-a` skips per-tool prompts within a turn; `-g` skips per-turn prompts across turns. Recommended together for unattended `claude -p "/apex …"` runs.

## Trust model

Analyze can fetch third-party content into the workflow:

- **Web research** — `general-purpose` subagents run web searches and `WebFetch`.
- **Library docs** — `/find-docs` or Context7 lookups pull current API references.
- **GitHub issues** — `-f #N` ingests title, body, and comments verbatim.
- **Any `-f <path>`** — forge plan, RFC, design doc, markitdown output of a PDF — read literally.

Fetched content feeds the analysis report that Plan and Execute work from. An adversarial document hosted at a fetched URL, or pasted into an issue body, can attempt **indirect prompt injection** — instructions disguised as data that the model could misread as directives.

**User review is the trust boundary.** Apex returns the analysis report and proposed plan for explicit approval before Execute begins (unless `-a` is set). Confirm the surfaced files, patterns, and acceptance criteria match intent before approving — anything fetched during Analyze passes through that review.

**To remove the surface entirely**, pass `-e` (economy mode): no subagents, no web fetches, direct tools only. Trade-off: less depth on unfamiliar libraries.

## Output Structure

The output path is `~/.claude/output/{project}/apex/{task-id}/`, where `{project}` is the repo basename and `{task-id}` is `NN-feature-name` (e.g., `01-add-auth`). The numbered prefix is intentional — it preserves task ordering for the `-r` resume lookup. This is a deliberate divergence from the single-file `{skill}-{slug}.md` shape (`~/.claude/output/{project}/{skill}/{skill}-{slug}.md`): apex is a multi-file task workspace and resume needs ordered task dirs, which one canonical file cannot carry.

**When `{save_mode}` = true:**

All outputs saved under `~/.claude/output/{project}/apex/{task-id}/`, where `{project}` is the kebab-cased basename of the git toplevel (else the cwd outside a git repo):

```
~/.claude/output/{project}/apex/{task-id}/
├── 00-context.md # Params, user request, timestamp
├── 01-analyze.md # Analysis findings
├── 02-plan.md # Implementation plan
├── 03-execute.md # Execution log
└── 04-examine.md  # Examination results
```

**`00-context.md` structure** — see `templates/00-context.md` for the canonical template (populated by `scripts/setup-templates.sh`).

## Resume Workflow

**Resume mode (`-r {task-id}`):**

`$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing this SKILL.md elsewhere.

Resolve the partial ID deterministically, then **auto-validate state** before restoring:

```bash
bash "$SKILL_DIR"/scripts/resume_lookup.sh {partial_id}
# → resolves to {task_dir}
bash "$SKILL_DIR"/scripts/validate_state.sh {task_id} {step_num}
# → exit 0: state consistent, continue restoration
# → non-zero: halt with the script's stderr findings; do NOT restore
```

`resume_lookup.sh`:
- Exit 0 → absolute task path on stdout; continue.
- Exit 1 → ambiguous; candidates print on stderr. Show them to the user, ask which one.
- Exit 2 → no match; halt with a clear error.

`validate_state.sh` (auto-runs on every resume):
- Exit 0 → prior steps complete and consistent; safe to enter `{step_num}`.
- Non-zero → state is corrupt or partial (missing task folder, missing step file, prior step not marked complete). Halt and surface findings.

Step-00 reads `{task_dir}/00-context.md` to determine the next pending step, invokes `validate_state.sh` against that step, then restores state variables and continues.

For implementation details, see `steps/step-00-init.md`.

## State Variables

Step state persists across steps. **Strings:** `{task_description}` `{feature_name}` `{task_id}` `{output_dir}` `{branch_name}` `{from_file}` `{resume_task}`. **Lists:** `{acceptance_criteria}` `{negative_acceptance}` (must-NOT criteria, inferred or accepted verbatim from a spec via `-f`). **Booleans:** `{auto_mode}` `{save_mode}` `{economy_mode}` `{branch_mode}` `{interactive_mode}` `{goal_mode}`. Full definitions: `steps/step-00-init.md`.

## Entry Point

**FIRST ACTION:** Load `steps/step-00-init.md`.

Step 00 handles:

- Flag parsing (`-a`, `-s`, `-e`, `-b`, `-i`, `-g`, `-f`, `-r`)
- Resume mode detection and task lookup
- Output folder creation (if `save_mode`)
- `00-context.md` creation (if `save_mode`)
- State variable initialization

After initialization, step-00 loads `step-01-analyze.md`.

## Step Files

**Progressive loading — only load the current step:**

| Step | File                         | Purpose                                              |
| ---- | ---------------------------- | ---------------------------------------------------- |
| 00   | `steps/step-00-init.md`      | Parse flags, create output folder, initialize state  |
| 01   | `steps/step-01-analyze.md`   | Smart context gathering with 1-10 parallel agents based on complexity |
| 02   | `steps/step-02-plan.md`      | File-by-file implementation strategy                 |
| 03   | `steps/step-03-execute.md`   | Todo-driven implementation                           |
| 04   | `steps/step-04-examine.md`   | Self-check, examination, and workflow completion     |

## Execution Rules

- **ULTRA THINK** before major decisions
- **Follow next_step directive** at end of each step
- **Use parallel agents** for independent exploration tasks

### Smart Agent Strategy in Analyze Phase

The analyze phase (step-01) uses **adaptive agent launching** (unless economy_mode):

**Available subagent types (built-in):**

- `Explore` — find existing patterns, files, utilities (read-only, fast). Type names are Claude Code's; other harnesses use their nearest equivalents.
- `general-purpose` — research library docs, web search, approaches, gotchas

**Launch 0-10 agents based on task complexity:**

| Complexity | Agents | When |
|------------|--------|------|
| Trivial / pre-contextual | 0 | Target already known, or `-f` context covers it — use direct tools |
| Simple | 1-2 | Bug fix, small tweak |
| Medium | 2-4 | New feature in familiar stack |
| Complex | 4-7 | Unfamiliar libraries, integrations |
| Major | 6-10 | Multiple systems, many unknowns |

**BE SMART:** Analyze what you actually need before launching. Don't spawn a subagent for work you can complete directly in a single response. Spawn multiple subagents in the same turn when fanning out across items or reading multiple files.

If your harness has no subagents, apply the economy-mode overrides (`steps/step-00b-economy.md`) — direct tools, run the explorations sequentially yourself.

## Save Output Pattern

**When `{save_mode}` = true:**

Step-00 runs `scripts/setup-templates.sh` to initialize all output files from the `templates/` directory.

**Each step then:**

1. Run `scripts/update-progress.sh {task_id} {step_num} {step_name} "in_progress"`
2. Append findings/outputs to the pre-created step file
3. Run `scripts/update-progress.sh {task_id} {step_num} {step_name} "complete"`

`scripts/validate_state.sh` auto-runs on every `-r` resume (see § Resume Workflow). It is also available manually for ad-hoc state verification — invoke it on demand against any task to confirm consistency.

**Template system benefits:**

- Reduces token usage by ~75% (1,350 tokens saved per workflow)
- Templates in `templates/` directory (not inline in steps)
- Scripts handle progress tracking automatically
- See `templates/README.md` for details

## Gotchas

1. **Progress-table mismatch halts `-r` resume with exit 3.** `scripts/validate_state.sh:66` requires the row in `00-context.md`'s `## Progress` table to match the step filename exactly (`| 01-analyze | ✓ Complete |`). A hand-renamed step file or a half-applied `update-progress.sh` invocation leaves the table out of sync; `tests/apex/test_validate_state.py:102-107` pins this. Fix: always run `scripts/update-progress.sh` after step completion; never rename step files post-creation.
2. **`-f` is an injection surface for indirect prompt attacks.** A GitHub issue body, a `WebFetch`-pulled doc, or a `-f` file written by an upstream skill can embed instructions disguised as data. Trust model (§ above) requires user review of the analysis report before Execute. Auto-mode (`-a`) skips per-tool confirmations but does not skip plan approval. Drop the surface entirely for sensitive tasks: pass `-e` (no subagents, no fetches).
3. **Step-00 context overwrite when `-f` mismatches resumed `-r` task ID.** `setup-templates.sh` recreates `00-context.md` on first setup; resuming with `-r 01-foo` but `-f ~/.claude/output/{project}/forge/forge-bar.md` mixes two intents: state variables get the `-f` content, progress table reads the resumed task. Always match the IDs: `-r 01-foo` pairs with `-f ~/.claude/output/{project}/apex/01-foo/02-plan.md` or a fresh forge plan for that task.
4. **Structured `{NN-feature}/` collisions across parallel worktrees.** Two worktrees of the same repo share the same kebab-cased `{project}` basename → both write under `~/.claude/output/{project}/apex/`. Auto-numbering scans the dir at script invocation, so two near-simultaneous `setup-templates.sh` calls can land on the same `NN` prefix. Fix: serialize apex setup across worktrees of the same repo, or rename one worktree's basename to differentiate.

## Success Criteria

- Each step loaded progressively
- All examination checks passing
- Outputs saved if `{save_mode}` enabled
- Clear completion summary provided
