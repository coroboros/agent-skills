---
name: apex
description: Systematic implementation using APEX methodology (Analyze-Plan-Execute-eXamine) with parallel subagents and self-validation. Use when implementing features, fixing bugs, or making code changes that benefit from structured workflow.
when_to_use: When the task is non-trivial and benefits from analysis before coding. When multiple files are involved, the codebase is unfamiliar, or thoroughness matters more than speed. When the user says "implement", "build", "add feature" for anything beyond a quick fix. NOT for trivial single-file changes — use `/oneshot` for those. NOT for exploration or planning only — use `/forge`.
argument-hint: "[-a] [-s] [-e] [-b] [-i] [-g] [-f <context>] [-r <task-id>] <task description>"
model: opus
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
metadata:
  author: coroboros
  sources:
    - github.com/Melvynx/aiblueprint
---

# Apex

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

### Flags

**Enable flags (turn ON):**

| Short | Long | Description |
|-------|------|-------------|
| `-a` | `--auto` | Autonomous mode: skip confirmations, auto-approve plans |
| `-s` | `--save` | Save mode: output each step to `~/.claude/output/{project}/apex/` |
| `-e` | `--economy` | Economy mode: no subagents, save tokens (for limited plans) |
| `-r` | `--resume` | Resume mode: continue from a previous task |
| `-b` | `--branch` | Branch mode: verify not on main, create branch if needed |
| `-i` | `--interactive` | Interactive mode: configure flags via AskUserQuestion |
| `-g` | `--goal` | Wire `/goal` to loop step-04 until AC verified (auto-on under `claude -p`; v2.1.139+ required) |
| `-f` | `--from` | Prior context: GitHub issue (`#N`, URL), forge plan, or any file as foundational input for analysis. Non-Markdown sources (PDF, DOCX, PPTX, audio, YouTube) → pre-process with `/markitdown -s` and pass the saved path |

**Disable flags (turn OFF):**

| Short | Long | Description |
|-------|------|-------------|
| `-A` | `--no-auto` | Disable auto mode |
| `-S` | `--no-save` | Disable save mode |
| `-E` | `--no-economy` | Disable economy mode |
| `-B` | `--no-branch` | Disable branch mode |
| `-G` | `--no-goal` | Disable `/goal` integration (overrides headless auto-on) |

### Examples

```bash
# Basic
/apex add auth middleware

# Autonomous (skip confirmations)
/apex -a add auth middleware

# Save outputs
/apex -a -s add auth middleware

# Resume previous task
/apex -r 01-auth-middleware
/apex -r 01  # Partial match

# From a GitHub issue
/apex -f "#42" implement what issue 42 describes

# From a prior forge plan (or RFC) — pass the explicit path the producer printed
/apex -f ~/.claude/output/{project}/forge/forge-{slug}.md implement WS-1

# Economy mode (save tokens)
/apex -e add auth middleware

# Interactive flag config
/apex -i add auth middleware

# Disable flags (uppercase)
/apex -A add auth middleware  # Disable auto
```

### Parsing Rules

1. Defaults loaded from `steps/step-00-init.md` `## Default Configuration` section
2. Command-line flags override defaults (enable with lowercase `-x`, disable with uppercase `-X`)
3. Flags removed from input, remainder becomes `{task_description}`
4. Task ID generated as `NN-kebab-case-description`

For the detailed parsing algorithm, see `steps/step-00-init.md`.

## Compatibility

`-g` (the `/goal` integration) requires **Claude Code v2.1.139 or later**. On older versions, Claude Code rejects the unknown slash command and the flag becomes a no-op without halting apex.

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

All outputs saved under the global user dir, keyed by `{project}` (kebab-cased basename of the git toplevel, else the cwd outside a git repo) — see `.claude/rules/repo-conventions.md` § Output paths:

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

Resolve the partial ID deterministically, then **auto-validate state** before restoring:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/resume_lookup.sh {partial_id}
# → resolves to {task_dir}
bash ${CLAUDE_SKILL_DIR}/scripts/validate_state.sh {task_id} {step_num}
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

## Workflow

**Standard flow:**

1. Parse flags and task description
2. If `-r`: Execute resume workflow
3. If `-s`: Create output folder and `00-context.md`
4. Load `step-01-analyze.md` → gather context
5. Load `step-02-plan.md` → create strategy
6. Load `step-03-execute.md` → implement
7. Load `step-04-examine.md` → verify and complete

## State Variables

**Persist throughout all steps:**

| Variable                | Type    | Description                                            |
| ----------------------- | ------- | ------------------------------------------------------ |
| `{task_description}`    | string  | What to implement (flags removed)                      |
| `{feature_name}`        | string  | Kebab-case name without number (e.g., `add-auth-middleware`) |
| `{task_id}`             | string  | Full identifier with number (e.g., `01-add-auth-middleware`) |
| `{acceptance_criteria}` | list    | Success criteria (inferred or explicit)                |
| `{negative_acceptance}` | list    | Negative scope — explicit must-NOT criteria (inferred or accepted verbatim from a spec via `-f`) |
| `{auto_mode}`           | boolean | Skip confirmations, use recommended options            |
| `{save_mode}`           | boolean | Save outputs to `~/.claude/output/{project}/apex/`     |
| `{economy_mode}`        | boolean | No subagents, direct tool usage only                   |
| `{branch_mode}`         | boolean | Verify not on main, create branch if needed            |
| `{interactive_mode}`    | boolean | Configure flags interactively                          |
| `{goal_mode}`           | boolean | Emit `/goal` directive at start of step-04 (auto-on under `claude -p`) |
| `{from_file}`           | string  | Path to prior context file (if `-f` provided)          |
| `{resume_task}`         | string  | Task ID to resume (if `-r` provided)                   |
| `{output_dir}`          | string  | Full path to output directory                          |
| `{branch_name}`         | string  | Created branch name (if branch_mode)                   |

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

- **Load one step at a time** — only load the current step file
- **ULTRA THINK** before major decisions
- **Persist state variables** across all steps
- **Follow next_step directive** at end of each step
- **Save outputs** if `{save_mode}` = true (append to step file)
- **Use parallel agents** for independent exploration tasks
- **Third-party content runs through user review** — see § *Trust model*. Web research, library docs, GitHub issue bodies, and `-f` files reach Execute only after the user approves the analysis report.

### Smart Agent Strategy in Analyze Phase

The analyze phase (step-01) uses **adaptive agent launching** (unless economy_mode):

**Available subagent types (built-in):**

- `Explore` — find existing patterns, files, utilities (read-only, fast)
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

## Success Criteria

- Each step loaded progressively
- All examination checks passing
- Outputs saved if `{save_mode}` enabled
- Clear completion summary provided
