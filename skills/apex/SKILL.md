---
name: apex
description: Systematic implementation using APEX methodology (Analyze-Plan-Execute-eXamine) with parallel subagents and self-validation. Use when implementing features, fixing bugs, or making code changes that benefit from structured workflow.
when_to_use: When the task is non-trivial and benefits from analysis before coding. When multiple files are involved, the codebase is unfamiliar, or thoroughness matters more than speed. When the user says "implement", "build", "add feature" for anything beyond a quick fix. NOT for trivial single-file changes — use /oneshot for those. NOT for exploration or planning only — use /brainstorm or /spec.
argument-hint: "[-a] [-s] [-e] [-b] [-i] [-f <context>] [-r <task-id>] <task description>"
model: opus
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
metadata:
  author: coroboros
---

# Apex

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
- `-s` (save): Save outputs to `.claude/output/apex/`
- `-e` (economy): No subagents, save tokens

See **Parameters** below for the complete flag list.

## Parameters

### Flags

**Enable flags (turn ON):**

| Short | Long | Description |
|-------|------|-------------|
| `-a` | `--auto` | Autonomous mode: skip confirmations, auto-approve plans |
| `-s` | `--save` | Save mode: output each step to `.claude/output/apex/` |
| `-e` | `--economy` | Economy mode: no subagents, save tokens (for limited plans) |
| `-r` | `--resume` | Resume mode: continue from a previous task |
| `-b` | `--branch` | Branch mode: verify not on main, create branch if needed |
| `-i` | `--interactive` | Interactive mode: configure flags via AskUserQuestion |
| `-f` | `--from` | Prior context: GitHub issue (`#N`, URL), spec, brainstorm report, or any file as foundational input for analysis |

**Disable flags (turn OFF):**

| Short | Long | Description |
|-------|------|-------------|
| `-A` | `--no-auto` | Disable auto mode |
| `-S` | `--no-save` | Disable save mode |
| `-E` | `--no-economy` | Disable economy mode |
| `-B` | `--no-branch` | Disable branch mode |

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
/apex -f "#42"

# From prior analysis (spec, brainstorm report, RFC)
/apex -f .claude/output/spec/auth-system/spec.md implement WS-1
/apex -f .claude/output/brainstorm/neon-setup/brainstorm.md implement Neon database

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

## Output Structure

**When `{save_mode}` = true:**

All outputs saved to PROJECT directory (where Claude Code is running):

```
.claude/output/apex/{task-id}/
├── 00-context.md # Params, user request, timestamp
├── 01-analyze.md # Analysis findings
├── 02-plan.md # Implementation plan
├── 03-execute.md # Execution log
└── 04-examine.md  # Examination results
```

**`00-context.md` structure** — see `templates/00-context.md` for the canonical template (populated by `scripts/setup-templates.sh`).

## Resume Workflow

**Resume mode (`-r {task-id}`):**

When provided, step-00 will:

1. Locate the task folder in `.claude/output/apex/`
2. Restore state from `00-context.md`
3. Find the last completed step
4. Continue from the next step

Supports partial matching (e.g., `-r 01` finds `01-add-auth-middleware`).

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
| `{auto_mode}`           | boolean | Skip confirmations, use recommended options            |
| `{save_mode}`           | boolean | Save outputs to `.claude/output/apex/`                 |
| `{economy_mode}`        | boolean | No subagents, direct tool usage only                   |
| `{branch_mode}`         | boolean | Verify not on main, create branch if needed            |
| `{interactive_mode}`    | boolean | Configure flags interactively                          |
| `{from_file}`           | string  | Path to prior context file (if `-f` provided)          |
| `{resume_task}`         | string  | Task ID to resume (if `-r` provided)                   |
| `{output_dir}`          | string  | Full path to output directory                          |
| `{branch_name}`         | string  | Created branch name (if branch_mode)                   |

## Entry Point

**FIRST ACTION:** Load `steps/step-00-init.md`.

Step 00 handles:

- Flag parsing (`-a`, `-x`, `-s`, `-r`, `--test`)
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
