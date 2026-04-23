---
name: claude-md
description: Create and optimize CLAUDE.md memory files or .claude/rules/ modular rules for Claude Code projects. Covers file hierarchy, content structure, path-scoped rules, best practices, and anti-patterns. Use when working with CLAUDE.md files, .claude/rules directories, setting up new projects, or improving Claude Code's context awareness — even when the user just says "memory file" or mentions Claude instructions without naming the filename.
when_to_use: When the user wants to create, clean up, or update Claude Code memory files. Routes via `$ARGUMENTS` — `init` (scaffold minimal CLAUDE.md), `optimize` (deep cleanup of bloat), `revise` (capture session learnings). Keywords — CLAUDE.md, memory file, instructions file, .claude/rules, optimize CLAUDE, init CLAUDE, revise CLAUDE. Without a subcommand, treat the argument as free-form guidance about memory files.
argument-hint: [init | optimize | revise | task description]
model: opus
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
metadata:
  author: coroboros
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

Memory files consume tokens from the context window. ~100–150 instruction slots available for your customizations. Keep files minimal — only include what the agent cannot discover on its own.

**Two approaches:**

- **CLAUDE.md** — Single file, best for small projects (< 100 lines)
- **.claude/rules/** — Modular files with optional path-scoping, best for large projects

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

- Press `#` during a session to add memory items quickly
- Use `/memory` to open CLAUDE.md in your editor

## File Hierarchy

| Priority | Location | Scope |
|----------|----------|-------|
| 1 (Highest) | Enterprise policy (managed by IT) | All org users |
| 2 | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team via git |
| 2 | `./.claude/rules/*.md` | Team via git |
| 3 | `~/.claude/CLAUDE.md` | All your projects |
| 3 | `~/.claude/rules/*.md` | All your projects |
| 4 (Lowest) | `./CLAUDE.local.md` (auto-gitignored) | Just you |

Claude recurses UP from current directory, loading all CLAUDE.md files found. Also discovers CLAUDE.md in subtrees when reading files in those directories.

**Monorepo strategy:** Root file defines WHEN; subtree files define HOW.

```
root/CLAUDE.md           # Universal: tech stack, git workflow
apps/web/CLAUDE.md       # Frontend-specific
apps/api/CLAUDE.md       # Backend-specific
```

## Rules Directory

The `.claude/rules/` directory splits instructions into focused markdown files.

- **Use `.claude/rules/` when:** many concerns, different rules for different file types, team maintains different areas
- **Use CLAUDE.md when:** small project, universal rules, single source of truth

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

- **Ideal:** < 100 lines
- **Maximum:** 150 lines before performance degrades
- **Over 200 lines:** directives start getting lost

When exceeding limits, split into `.claude/rules/` files or link to separate docs:

```markdown
- **API patterns**: See [docs/api-patterns.md](docs/api-patterns.md)
- **Testing guide**: See [docs/testing-guide.md](docs/testing-guide.md)
```

CLAUDE.md supports importing: `@docs/coding-standards.md` (relative/absolute paths, `~` expansion, up to 5 levels deep, not evaluated inside code blocks).

## Workflow

**ALWAYS ASK FIRST: Storage Strategy**

Before creating or updating memory files, use AskUserQuestion:

- **Option 1: Single CLAUDE.md** — < 100 lines, simple project, universal rules
- **Option 2: Modular .claude/rules/** — 100+ lines, different rules for different files

**Creating new memory:**

1. Start with `/init` or minimal template
2. Add tech stack and commands first
3. Add rules only as you encounter friction
4. Test with real tasks, iterate based on Claude's behavior

**Maintaining:**

1. Review quarterly or when project changes significantly
2. Remove outdated instructions
3. Add patterns that required repeated explanation
4. Use `#` for quick additions during work

**Troubleshooting:**

| Problem | Solution |
|---------|----------|
| Claude ignores instructions | Reduce file size, add emphasis (CRITICAL, NEVER) |
| Context overflow | Use `/clear`, split into `.claude/rules/` |
| Instructions conflict | Consolidate, use hierarchy (root vs subtree) |
| Path rules not applying | Verify glob pattern matches target files |
| Debug which instructions load | Use the `InstructionsLoaded` hook to log files, timing, and reasons |
| Monorepo picks up irrelevant files | Add `claudeMdExcludes` glob patterns in `.claude/settings.local.json` |

**Tips:**

- Set `CLAUDE_CODE_NEW_INIT=1` before `/init` for an interactive multi-phase flow (explores codebase with subagent, asks follow-up questions, presents reviewable proposal)
- Instructions survive `/compact` — CLAUDE.md is re-read from disk and re-injected after compaction

## Subcommands

The skill supports three argument-driven workflows via `$ARGUMENTS`. Load the matching step file when the argument is present:

- **`init`** — Scaffold a minimal CLAUDE.md. See [steps/init.md](steps/init.md).
- **`optimize`** — Deep cleanup of a bloated CLAUDE.md. See [steps/optimize.md](steps/optimize.md). **Always read `references/optimize-guide.md` first.**
- **`revise`** — Capture session learnings into CLAUDE.md. See [steps/revise.md](steps/revise.md).

Without a subcommand, treat the argument as free-form guidance about memory files and answer from the sections above.

## Reference Guides

- **Optimization guide**: [references/optimize-guide.md](references/optimize-guide.md) — research-backed bloat checklist, 6 removal categories, before/after examples
- **Rules directory**: [references/rules-directory-guide.md](references/rules-directory-guide.md) — complete `.claude/rules/` guide with path-scoping, YAML syntax, symlinks, migration
- **Prompting techniques**: [references/prompting-techniques.md](references/prompting-techniques.md) — emphasis strategies, clarity techniques, constraint patterns
- **Section templates**: [references/section-templates.md](references/section-templates.md) — copy-paste templates for each section type
- **Comprehensive example**: [references/comprehensive-example.md](references/comprehensive-example.md) — full production SaaS CLAUDE.md
- **Project patterns**: [references/project-patterns.md](references/project-patterns.md) — Next.js, Express, Python, Monorepo patterns
