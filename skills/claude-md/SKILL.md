---
name: claude-md
description: Create and optimize CLAUDE.md memory files or .claude/rules/ modular rules for Claude Code projects. Covers file hierarchy, content structure, path-scoped rules, best practices, and anti-patterns. Use when working with CLAUDE.md files, .claude/rules directories, setting up new projects, or improving Claude Code's context awareness — even when the user just says "memory file" or mentions Claude instructions without naming the filename.
when_to_use: When the user wants to create, clean up, or update Claude Code memory files. Routes via `$ARGUMENTS` — `init` (scaffold minimal CLAUDE.md), `optimize` (deep cleanup of bloat), `revise` (capture session learnings). Keywords — CLAUDE.md, memory file, instructions file, .claude/rules, optimize CLAUDE, init CLAUDE, revise CLAUDE, auto memory, MEMORY.md, subagent memory. Without a subcommand, treat the argument as free-form guidance about memory files.
argument-hint: [init | optimize | revise | task description]
model: opus
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
metadata:
  author: coroboros
  sources:
    - code.claude.com/docs/en/memory
    - github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-md-management
    - github.com/Melvynx/aiblueprint/tree/main/claude-code-config/skills/claude-memory
---

# CLAUDE.md

<!--
Name exception: `claude-md` contains the reserved substring `claude`. Per
`.claude/rules/agentskills-spec.md` § Reserved → "narrow exception for
first-party filename conventions", this is declared and intentional — the
skill operates directly on `CLAUDE.md`, and alternatives (`memory-md`,
`ctx-md`) lose essential semantic clarity.
-->

## Core Principle

Memory files consume tokens every session. Keep them minimal — include only what the agent cannot discover on its own or what a tool doesn't already enforce (linter, TypeScript, tests).

Three mechanisms carry knowledge across sessions:

- **CLAUDE.md** — single-file instructions you write. Always loaded.
- **`.claude/rules/`** — modular rule files, optionally path-scoped. Load alongside CLAUDE.md.
- **Auto memory** — notes Claude writes itself per project. See *Auto Memory* below.

For most projects, CLAUDE.md and rules combine (hybrid pattern). See *Workflow > Storage Strategy* for the pick-which decision.

## Quick Start

Run `/init` to auto-generate a CLAUDE.md. Or create manually:

```markdown
# Project Name

## Tech Stack
- [Primary framework]
- [Key non-obvious libraries]

## Commands
- `npm run dev` - Dev server
- `npm test` - Run tests
- `npm run build` - Build

## Rules
- [2-3 critical project-specific rules]
```

- Run `/memory` to view all loaded files (CLAUDE.md, CLAUDE.local.md, rules), toggle auto memory, and open any file in your editor

## File Hierarchy

| Location | Scope | Notes |
|----------|-------|-------|
| Managed policy (OS-specific path managed by IT) | All org users | Cannot be excluded by individual settings |
| `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team via git | Project-wide |
| `./.claude/rules/*.md` | Team via git | Modular, optionally path-scoped |
| `~/.claude/CLAUDE.md` | All your projects | Personal, applies everywhere |
| `~/.claude/rules/*.md` | All your projects | Personal rules, loaded before project rules |
| `./CLAUDE.local.md` | Just you (this project) | Add to `.gitignore` yourself (or use `/init` personal option) |

All discovered files are concatenated, not overridden. More specific locations take precedence in conflicts. Within a directory, `CLAUDE.local.md` loads after `CLAUDE.md`, so personal notes win over team instructions at the same level.

Claude recurses UP from the CWD, loading all files found. Subtree `CLAUDE.md` files load on-demand when Claude reads files in those directories.

`AGENTS.md` is **not** read directly. If your repo uses it for other agents, import it from CLAUDE.md with `@AGENTS.md` so both tools share one source.

**Managed CLAUDE.md ≠ managed settings.** Enterprise deployments can push both, and they serve different purposes. Settings enforce (blocked tools, sandbox, auth, env); CLAUDE.md guides (coding standards, compliance reminders, behavioral instructions). Security-critical rules belong in settings — CLAUDE.md shapes Claude's behavior but is *not* a hard enforcement layer.

**Monorepo strategy:** Root file defines WHEN; subtree files define HOW.

```
root/CLAUDE.md           # Universal: tech stack, git workflow
apps/web/CLAUDE.md       # Frontend-specific
apps/api/CLAUDE.md       # Backend-specific
```

## Rules Directory

The `.claude/rules/` directory splits instructions into focused markdown files.

- **Use `.claude/rules/` when:** many concerns, different rules for different file types, team maintains different areas
- **Use CLAUDE.md when:** tiny project, universal rules, single source of truth
- **Combine both (hybrid)** for most projects — CLAUDE.md stays slim and `@`-imports the active rules, giving humans a visible TOC while the rules carry the content. See *Workflow > Storage Strategy* below for when to pick which.

Path-scoped rules use YAML frontmatter:

```yaml
---
paths:
  - "src/api/**/*.ts"
---
# API Rules
- All endpoints must include input validation
```

Supported patterns: `**/*.ts`, `src/**/*`, `src/**/*.{ts,tsx}`, `{src,lib}/**/*.ts`

Rules without `paths` frontmatter load unconditionally.

See [references/rules-directory-guide.md](references/rules-directory-guide.md) for the complete guide including symlinks, user-level rules, and migration.

## Content Structure

Structure CLAUDE.md with only these sections:

1. **Project purpose** (1–3 lines) — What the project is
2. **Tech stack** (compact) — Only non-obvious technologies
3. **Commands** — Non-obvious dev, build, and test commands
4. **Important files** — Architecture-critical, non-obvious files only
5. **Rules** — Prohibitions and constraints that prevent mistakes (highest-value lines)
6. **Workflow** (optional) — Only if non-standard

**Do NOT include** — the 6 bloat categories. Any line matching one of these pays tokens for zero behavioral gain, because the agent either discovers the information directly or a tool enforces it:

1. **Linter-enforced rules** (ESLint, Prettier, Biome, TypeScript strict) — the tool enforces it, the agent doesn't need a reminder
2. **Marketing / goals / vision** — zero code value
3. **Obvious info the agent discovers itself** — directory structure, framework defaults, deps from config files
4. **Verbose explanations** — paragraphs where one line suffices, tutorials, history
5. **Redundant specs** — copies of config files, schema descriptions, env var lists
6. **Generic best practices** — "write clean code", "DRY", "SOLID"

Full examples for each category live in [references/optimize-guide.md](references/optimize-guide.md). Use them both when *writing* new CLAUDE.md files and when *optimizing* existing ones — the list is the same.

See [references/section-templates.md](references/section-templates.md) for ready-to-use templates, and [references/project-patterns.md](references/project-patterns.md) for framework-specific patterns.

## Writing Rules

**Golden rule:** If someone with zero project context reads your CLAUDE.md and gets confused, Claude will too.

**Be specific, never vague:**

```
❌ "Format code properly" / "Write good tests" / "Follow best practices"
✅ "Run `pnpm lint` before committing" / "Tests in `__tests__/` using Vitest"
```

**Prohibitions > positive guidance:**

```
❌ "Try to use TanStack Form for forms"
✅ "NEVER use native form/useState for forms — ALWAYS use TanStack Form"
```

**Show, don't tell:** When format matters, show a concrete example (3–5 lines max).

**HTML comments:** Block-level `<!-- comments -->` are stripped from CLAUDE.md before injection into context. Use them for human-only maintainer notes without spending tokens. Comments inside code blocks are preserved.

**Emphasis hierarchy:** CRITICAL > NEVER > ALWAYS > IMPORTANT > YOU MUST

- Put critical rules **first** in each section
- Use **bold + keyword** for non-negotiable rules: `**CRITICAL**: Never commit secrets`

See [references/prompting-techniques.md](references/prompting-techniques.md) for advanced techniques.

## Size Limits

Target **under 200 lines** per file. Longer files consume more context and reduce adherence — directives start getting lost.

When exceeding, split via `@path` imports or `.claude/rules/`:

```markdown
# API patterns
@docs/api-patterns.md

# Testing
@docs/testing-guide.md
```

Imports load eagerly at launch alongside the referencing file. Relative and absolute paths work, `~` expands to home, maximum depth is 5 hops. External imports (outside the project) trigger a one-time approval dialog on first encounter.

## Auto Memory

Claude Code v2.1.59+ adds a parallel memory system: **auto memory**. Claude saves notes for itself (build commands, debugging insights, preferences) as it works. You don't write anything — Claude decides what's worth remembering.

- **Location**: `~/.claude/projects/<project>/memory/MEMORY.md` — machine-local, per git repo, shared across worktrees of the same repo
- **Loaded per session**: first 200 lines (or 25 KB) of `MEMORY.md`. Topic files (`debugging.md`, `patterns.md`, …) load on-demand when Claude reads them
- **Toggle**: `/memory` exposes an auto-memory toggle. Setting-level: `autoMemoryEnabled` (default `true`). Env: `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`
- **Custom location**: `autoMemoryDirectory` in user or local settings (rejected from project settings for safety)

Auto memory and CLAUDE.md complement each other. CLAUDE.md is for "always do X" rules you author. Auto memory is for "Claude noticed Y" notes Claude writes. Run `/memory` to see both in one place.

Subagents can maintain their own memory too — configure via `memory: user|project|local` in the subagent frontmatter. Stored at `~/.claude/agent-memory/<name>/`. See Claude Code subagent docs (`/en/sub-agents#enable-persistent-memory`) for details.

## Workflow

**ALWAYS ASK FIRST: Storage Strategy**

Before creating or updating memory files, use AskUserQuestion:

- **Option 1: Single CLAUDE.md** — tiny project, one file carries everything
- **Option 2: Hybrid (CLAUDE.md slim + `.claude/rules/`)** *(recommended default)* — CLAUDE.md stays small: intro + `@`-imports of the active rules + a short *At a glance* for repo-specific divergences. Rules carry the actual content and can be path-scoped. Zero duplication, since rules load eager and CLAUDE.md doesn't repeat them.
- **Option 3: Mostly `.claude/rules/`** — every rule is path-scoped and CLAUDE.md has nothing universal worth stating at the top level.

*CLAUDE.md and non-path-scoped `.claude/rules/*.md` load at launch; path-scoped rules (`paths:` frontmatter) load on-demand when Claude reads matching files. Either way the slim-hub pattern doesn't lose content, it places it in focused files instead of one long CLAUDE.md.*

**Creating new memory:**

1. Start with `/init` or minimal template
2. Add tech stack and commands first
3. Add rules only as you encounter friction
4. Test with real tasks, iterate based on Claude's behavior

**Maintaining:**

1. Review quarterly or when project changes significantly
2. Remove outdated instructions
3. Add patterns that required repeated explanation
4. Ask Claude to edit CLAUDE.md directly, or open it via `/memory`

**Troubleshooting:**

| Problem | Solution |
|---------|----------|
| Claude ignores instructions | Reduce file size, add emphasis (CRITICAL, NEVER) |
| Context overflow | Use `/clear`, split into `.claude/rules/` |
| Instructions conflict | Consolidate, use hierarchy (root vs subtree) |
| Path rules not applying | Verify glob pattern matches target files |
| Debug which instructions load | Use the `InstructionsLoaded` hook to log files, timing, and reasons |
| Monorepo picks up irrelevant files | Add `claudeMdExcludes` glob patterns in `.claude/settings.local.json` |
| Memory files not loading from `--add-dir` | Set `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` — `--add-dir` alone gives file access, this env var adds CLAUDE.md/rules loading |
| CLAUDE.md guidance ignored for security-critical rules | CLAUDE.md is guidance, not enforcement. Use `--append-system-prompt` for strict-compliance automation, or push rules into `permissions.deny`/`sandbox.enabled` settings |

**Tips:**

- Set `CLAUDE_CODE_NEW_INIT=1` before `/init` for an interactive multi-phase flow (explores codebase with subagent, asks follow-up questions, presents reviewable proposal)
- Instructions survive `/compact` — **project-root** CLAUDE.md is re-read from disk and re-injected. Nested CLAUDE.md files reload on-demand the next time Claude reads a file in that subdirectory.

## Subcommands

The skill supports three argument-driven workflows via `$ARGUMENTS`. Load the matching step file when the argument is present:

- **`init`** — Scaffold a minimal CLAUDE.md. See [steps/init.md](steps/init.md). Uses `bash ${CLAUDE_SKILL_DIR}/scripts/init_structure.sh <mode>` for the file layout.
- **`optimize`** — Deep cleanup of a bloated CLAUDE.md. See [steps/optimize.md](steps/optimize.md). Always start with `bash ${CLAUDE_SKILL_DIR}/scripts/audit_claude_md.py <path>` — the JSON hit-list is your fix list. Read `references/optimize-guide.md` for the WHY behind each category.
- **`revise`** — Capture session learnings into CLAUDE.md. See [steps/revise.md](steps/revise.md).

Without a subcommand, treat the argument as free-form guidance about memory files and answer from the sections above.

## Reference Guides

- **Optimization guide**: [references/optimize-guide.md](references/optimize-guide.md) — research-backed bloat checklist, 6 removal categories, before/after examples
- **Rules directory**: [references/rules-directory-guide.md](references/rules-directory-guide.md) — complete `.claude/rules/` guide with path-scoping, YAML syntax, symlinks, migration
- **Prompting techniques**: [references/prompting-techniques.md](references/prompting-techniques.md) — emphasis strategies, clarity techniques, constraint patterns
- **Section templates**: [references/section-templates.md](references/section-templates.md) — copy-paste templates for each section type
- **Comprehensive example**: [references/comprehensive-example.md](references/comprehensive-example.md) — full production SaaS CLAUDE.md
- **Project patterns**: [references/project-patterns.md](references/project-patterns.md) — Next.js, Express, Python, Monorepo patterns
- **Script schemas**: [references/schemas.md](references/schemas.md) — JSON / RESULT shapes for the three deterministic scripts (audit, validate, init)

## Deterministic scripts

- `scripts/audit_claude_md.py` — line-count + 6-category bloat scan + `@import` resolver. Run first before optimize/revise — the JSON output is your hit-list. Python 3.7+.
- `scripts/validate_rule_file.py` — YAML frontmatter + `paths:` glob validator for `.claude/rules/*.md`. Python 3.7+.
- `scripts/init_structure.sh` — idempotent scaffold for the three storage strategies (`single`, `hybrid`, `rules-only`). Never overwrites.

## See also

- **`/agent-creator`** — subagent configuration and orchestration. A CLAUDE.md that defines project-wide instructions often pairs with `.claude/agents/*.md` files; use `/agent-creator` to author those.
