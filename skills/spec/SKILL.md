---
name: spec
description: Transform ideas into structured execution specs with prioritized workstreams, complexity ratings, dependencies, and acceptance criteria. Use this whenever the user needs to decompose work before building — even when they don't explicitly say "spec" (e.g. "break this down", "plan this out", "create issues for", "what are the steps"). The bridge between thinking and building.
when_to_use: When work needs to be structured into actionable workstreams before implementation. After brainstorming when the direction is clear but the work needs shape. When the user asks to "plan", "break down", "spec out", "create issues for", or "map out the steps" of a feature. NOT for exploring options — use /brainstorm. NOT for direct implementation — use /apex or /oneshot.
argument-hint: "[-s] [-i] [-a] [-e] [-f <path>] <idea>"
model: opus
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
metadata:
  author: coroboros
---

# Spec

Structured execution spec for: $ARGUMENTS

## Objective

Transform any starting point — raw text, a brainstorm report, a GitHub issue, a conversation — into a structured execution spec. Produces 3-7 prioritized workstreams with complexity ratings, dependencies, and testable acceptance criteria. Optionally creates GitHub issues from the workstreams.

## Parameters

### Flags

| Flag | Inverse | Behavior |
|------|---------|----------|
| `-s` / `--save` | `-S` / `--no-save` | Save spec to `.claude/output/spec/{slug}/spec.md` |
| `-i` / `--issues` | `-I` / `--no-issues` | Create GitHub issues from workstreams (implies `-s`) |
| `-a` / `--auto` | `-A` / `--no-auto` | Skip Q&A, make reasonable assumptions |
| `-e` / `--economy` | `-E` / `--no-economy` | No subagents, direct tools only |
| `-f <path>` / `--from <path>` | — | Prior context — file, GitHub issue (`#N`), or URL as foundational input. Non-Markdown sources (PDF, DOCX, PPTX, audio, YouTube) → pre-process with `/markitdown -s` and pass the saved path |

Lowercase enables, uppercase disables. All flags default OFF. Flags are removed from input; remainder becomes `{idea}`. `{slug}` is kebab-case from `{idea}`, max 5 words.

### Examples

```bash
/spec -s add user authentication with OAuth
/spec -s -f .claude/output/brainstorm/auth-strategy/brainstorm.md
/spec -s -f "#42"                                 # from GitHub issue
/spec -s -a redesign the billing system           # skip Q&A
/spec -s -a -i migrate from REST to GraphQL       # auto + create issues
/spec -s -e add search functionality              # no subagents
```

## Pipeline

```
/brainstorm -s "topic"              → brainstorm.md
/spec -s -f brainstorm.md "..."     → spec.md  ← you are here
/apex -f spec.md implement WS-1     → code
```

Spec is the structural bridge. It reads context (a brainstorm, an issue, a conversation), produces workstreams with acceptance criteria, and hands off to `/apex` — which then implements one workstream at a time.

## Output

When `{save_mode}` = true:

```
.claude/output/spec/{slug}/
└── spec.md    # The structured spec document
```

If `{issues_mode}` = true, a `## GitHub Issues` section is appended to `spec.md` after creation, mapping each workstream to its issue number.

## Subagent strategy

Discovery (step-01) uses **adaptive agent launching** unless `{economy_mode}` = true.

**Available subagent types:**

- `Explore` — find existing patterns, files, architecture (read-only, fast, context-isolated)
- `general-purpose` — research approaches, library docs, web search

**Launch count scales with context:**

| Scenario | Agents | Composition |
|----------|--------|-------------|
| Simple idea, no codebase | 0-1 | Model handles directly; 1x general-purpose only if external research needed |
| Feature in existing codebase | 2-3 | 1x Explore (related code) + 1x Explore (patterns) |
| Complex feature, multiple areas | 3-5 | 2x Explore (different areas) + 1-2x general-purpose |
| Major system, many unknowns | 4-6 | 2x Explore + 2-3x general-purpose |

**Why subagents matter here:** exploration reports typically produce far more raw output than the final spec needs. Running exploration in subagents keeps the main context clean — the skill sees only the distilled findings, not the file contents scanned to produce them. Launch all chosen agents in a single message so they run in parallel.

Don't over-launch. If the idea is simple or the codebase is small, skip subagents entirely — direct tool use is faster.

## State variables

Persist throughout all steps:

| Variable | Type | Description |
|----------|------|-------------|
| `{idea}` | string | Feature/idea description (flags removed) |
| `{slug}` | string | Kebab-case identifier, max 5 words |
| `{auto_mode}` | boolean | Skip Q&A |
| `{save_mode}` | boolean | Save spec to file |
| `{issues_mode}` | boolean | Create GitHub issues (forces save) |
| `{economy_mode}` | boolean | No subagents |
| `{from_file}` | string | Path to prior context (if `-f` provided) |
| `{output_dir}` | string | `.claude/output/spec/{slug}/` |
| `{output_file}` | string | `{output_dir}spec.md` |

## Entry point

**FIRST ACTION:** parse flags and proceed. Do not load step-01 until init is done.

1. **Parse flags** — lowercase enables, uppercase disables, `-f` consumes next arg as `{from_file}`, remainder becomes `{idea}`.
2. **Apply implications** — if `{issues_mode}` = true, force `{save_mode}` = true.
3. **Generate identifiers** — `{slug}` = kebab-case from `{idea}` (max 5 words); `{output_dir}` = `.claude/output/spec/{slug}/`; `{output_file}` = `{output_dir}spec.md`.
4. **Create output dir** — if `{save_mode}` = true, `mkdir -p {output_dir}`.
5. **Show compact summary** — one line + one table, then proceed immediately:

```
> Spec: {idea}

| Variable | Value |
|----------|-------|
| `{slug}` | {slug} |
| `{from_file}` | {path or —} |
| `{auto_mode}` | true/false |
| `{save_mode}` | true/false |
| `{issues_mode}` | true/false |
| `{economy_mode}` | true/false |

→ Discovering...
```

Keep output minimal: no verbose parsing logs, no separators, no explanations. Load `steps/step-01-discover.md` immediately after the table.

## Steps

Progressive loading — load only the current step file:

| Step | File | Purpose |
|------|------|---------|
| 01 | `steps/step-01-discover.md` | Context gathering: prior docs, codebase, Q&A |
| 02 | `steps/step-02-specify.md` | Write the structured spec document |
| 03 | `steps/step-03-issues.md` | Create GitHub issues from workstreams (only with `-i`) |

## Supporting files

- `templates/spec.md` — the canonical spec document format used by step-02
- `scripts/setup-labels.sh` — idempotent GitHub label creation (used by step-03)
- `scripts/validate_spec.py` — schema + dependency-graph validator (used by step-02; requires Python 3.7+)

## Rules

- **Never implement.** Spec produces a document, not code changes.
- **Load one step at a time.** Each step file declares its `next_step`.
- **Persist state variables** across all steps.
- **ULTRA THINK** before decomposing work into workstreams.
- **Always include concrete acceptance criteria** — every workstream, every time.
- **Validate before finalizing.** Run `bash ${CLAUDE_SKILL_DIR}/scripts/validate_spec.py {output_file}` after writing — exit 0 required. Rewrite flagged workstreams until the schema clears (3-7 workstreams; Priority/Complexity set; deps resolve; no cycles).

## Success criteria

- Spec document produced in the canonical format (see `templates/spec.md`)
- 3-7 workstreams with priority, complexity, tasks, and acceptance criteria
- Dependencies mapped, execution order defined
- Output saved if `{save_mode}` enabled
- GitHub issues created if `{issues_mode}` enabled
- Clear bridge commands to `/apex` shown at the end
