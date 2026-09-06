---
name: claude-md
description: Create, audit or update CLAUDE.md and .claude/rules/ instructions for Claude Code. Use for instruction ownership, imports, path-scoped rules or memory configuration; use agent-creator for subagent definitions.
when_to_use: When the user wants to create, clean up, or update Claude Code memory files. Routes via `$ARGUMENTS` — `init` (scaffold minimal CLAUDE.md), `optimize` (deep cleanup of bloat), `revise` (capture session learnings). Keywords — CLAUDE.md, memory file, instructions file, .claude/rules, optimize CLAUDE, init CLAUDE, revise CLAUDE, auto memory, MEMORY.md, subagent memory. Without a subcommand, treat the argument as free-form guidance about memory files. Skip for subagent system prompts and .claude/agents/ configs — use /agent-creator.
argument-hint: "[init | optimize | revise | task description]"
license: MIT
compatibility: "Authors Claude Code instruction and memory files. Python 3 and bash are required for bundled checks; runtime loading behavior must be verified in the target Claude Code version."
metadata:
  author: coroboros
  sources: "code.claude.com/docs/en/memory; github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-md-management; github.com/Melvynx/aiblueprint"
---

# CLAUDE.md

<!-- canonical:writing-rules:start -->
## Important — Writing rules

Apply these rules to emitted prose: docs, comments, commit messages, PR bodies, and release notes.

- Match surrounding punctuation, capitalization, and formatting.
- Every sentence changes the reader's understanding. Cut it otherwise.
- Lead with the action or outcome.
- Use concrete language and lists when they improve comparison or sequence.
- Assert positively. Reserve negation for real constraints (`NEVER commit secrets`).
- No marketing words: powerful, robust, seamlessly, leverage, unlock, comprehensive, delightful.
- No AI tells: delve, tapestry, intricate, pivotal, testament, underscore, crucial, garner, showcase, additionally, moreover, furthermore, indeed.
- For substantive English prose, use `/humanize-en` if installed with the existing scope and authorization. It adds no approval stage; skip redundant passes over short status text.
<!-- canonical:writing-rules:end -->

## Core Principle

Memory files consume tokens every session. Keep high-value project conventions, commands and boundaries concise. Discoverability alone is not a reason to delete guidance that prevents a demonstrated mistake.

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
- **Combine both (hybrid)** for most projects — CLAUDE.md stays slim and indexes conditional rules with ordinary links; use eager `@` imports only for universal content. See *Workflow > Storage Strategy* below for when to pick which.

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

Optional sections and six candidate bloat categories to review (linter rules, agent-discoverable, marketing/vision, redundant specs, verbose prose, generic best-practices): [references/optimize-guide.md](references/optimize-guide.md).

## CLAUDE.md-specific writing rules

The canonical *Writing rules* block above carries the universal prose rules. The rules below add what is specific to authoring CLAUDE.md and `.claude/rules/` files — directive phrasing, emphasis discipline, HTML-comment behavior under context injection.

**Golden rule:** If someone with zero project context reads your CLAUDE.md and gets confused, Claude will too.

**Be specific, never vague:**

```
❌ "Format code properly" / "Write good tests" / "Follow best practices"
✅ "Run `pnpm lint` before committing" / "Tests in `__tests__/` using Vitest"
```

**Be directive; reserve prohibitions for real constraints:**

```
❌ "Try to use TanStack Form for forms"
✅ "Use TanStack Form for all forms (not native form/useState)"
```

Lead with the action. Keep `NEVER` for genuine constraints — secrets, data loss, breaking changes — not ordinary preferences.

**Show, don't tell:** When format matters, show a concrete example (3–5 lines max).

**HTML comments:** Block-level `<!-- comments -->` are stripped from CLAUDE.md before injection into context. Use them for human-only maintainer notes without spending tokens. Comments inside code blocks are preserved.

**Emphasis, sparingly:** Reserve **bold + a single keyword** for non-negotiable rules (`**Never commit secrets**`).

- Put critical rules **first** in each section — placement beats emphasis.
- Don't stack `CRITICAL`/`MUST`/`ALWAYS` on ordinary guidance. Current models follow instructions literally, so over-emphasis dilutes the rules that matter and can overtrigger.

See [references/prompting-techniques.md](references/prompting-techniques.md) for advanced techniques.

## Size Limits

Target **under 200 lines** per file. This official guideline is a review signal, not a measured universal adherence threshold.

When exceeding, split via `@path` imports or `.claude/rules/`:

```markdown
# API patterns
@docs/api-patterns.md

# Testing
@docs/testing-guide.md
```

Imports load eagerly at launch alongside the referencing file. Relative and absolute paths work, `~` expands to home, maximum depth is four hops. External imports (outside the project) trigger a one-time approval dialog on first encounter.

## Auto Memory

Auto memory layout, loading caps, settings keys, env overrides, and subagent memory: [references/auto-memory.md](references/auto-memory.md).

## Workflow

**Storage strategy:** Preserve the established owner and layout for an authorized update. For a new file, use the simplest layout that fits the brief: a single file for universal guidance, or a slim index plus `.claude/rules/` for conditional concerns. Ask only when a material storage migration or user-owned decision is unresolved. An audit request remains read-only; explicit memory permissions still apply.

Use ordinary links for path-scoped rules so they remain conditional. Eager `@` imports load universal content and do not provide progressive disclosure.

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
| Claude ignores instructions | Check specificity and placement first — move the rule to the top of its section; add one emphatic marker only for a genuine constraint |
| Context overflow | Use host compaction and recover task state; split conditional guidance into `.claude/rules/` |
| Instructions conflict | Consolidate, use hierarchy (root vs subtree) |
| Path rules not applying | Verify glob pattern matches target files |
| Debug which instructions load | Use the `InstructionsLoaded` hook to log files, timing, and reasons |
| Monorepo picks up irrelevant files | Add `claudeMdExcludes` glob patterns in `.claude/settings.local.json` |
| Memory files not loading from `--add-dir` | Set `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` — `--add-dir` alone gives file access, this env var adds CLAUDE.md/rules loading |
| CLAUDE.md guidance ignored for security-critical rules | CLAUDE.md is guidance, not enforcement. Use applicable permission, sandbox or hook enforcement; adding system-prompt text does not enforce a security boundary |

**Tips:**

- Set `CLAUDE_CODE_NEW_INIT=1` before `/init` for an interactive multi-phase flow (explores codebase with subagent, asks follow-up questions, presents reviewable proposal)
- Instructions survive `/compact` — **project-root** CLAUDE.md is re-read from disk and re-injected. Nested CLAUDE.md files reload on-demand the next time Claude reads a file in that subdirectory.

## Subcommands

The skill supports three argument-driven workflows via `$ARGUMENTS`. `$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing this SKILL.md elsewhere. Load the matching step file when the argument is present:

- **`init`** — Scaffold a minimal CLAUDE.md: detect the project, preserve established rules, then draft and write within the user's authorized scope. See [steps/init.md](steps/init.md). Optional layout scaffold: `bash "$SKILL_DIR"/scripts/init_structure.sh <mode>` writes starter rule stubs — use only when the user asks for a pre-seeded layout.
- **`optimize`** — Deep cleanup of a bloated CLAUDE.md. See [steps/optimize.md](steps/optimize.md). Always start with `python3 "$SKILL_DIR"/scripts/audit_claude_md.py <path>` — the JSON report contains candidates requiring semantic review. Read `references/optimize-guide.md` for the WHY behind each category.
- **`revise`** — Capture session learnings into CLAUDE.md. See [steps/revise.md](steps/revise.md).

Without a subcommand, treat the argument as free-form guidance about memory files and answer from the sections above.

## Reference Guides

- **Optimization guide**: [references/optimize-guide.md](references/optimize-guide.md) — evidence-guided bloat review, 6 removal categories, before/after examples
- **Rules directory**: [references/rules-directory-guide.md](references/rules-directory-guide.md) — complete `.claude/rules/` guide with path-scoping, YAML syntax, symlinks, migration
- **Prompting techniques**: [references/prompting-techniques.md](references/prompting-techniques.md) — emphasis strategies, clarity techniques, constraint patterns
- **Section templates**: [references/section-templates.md](references/section-templates.md) — copy-paste templates for each section type
- **Full example**: [references/full-example.md](references/full-example.md) — compact project-specific CLAUDE.md example
- **Project patterns**: [references/project-patterns.md](references/project-patterns.md) — Next.js, Express, Python, Monorepo patterns
- **Auto memory**: [references/auto-memory.md](references/auto-memory.md) — layout, loading caps, settings keys, env overrides, subagent memory
- **Script schemas**: [references/schemas.md](references/schemas.md) — JSON / RESULT shapes for the three deterministic scripts (audit, validate, init)

## Deterministic scripts

- `scripts/audit_claude_md.py` — line-count + 6-category bloat scan + `@import` resolver. Run first for optimize — the JSON output proposes review candidates; revise consults it when drift is suspected. Python 3.7+.
- `scripts/validate_rule_file.py` — frontmatter delimiter + supported YAML `paths:` glob subset validator for `.claude/rules/*.md`; other YAML keys are not validated. Quote globs beginning with `*`, `!` or other YAML indicators. Python 3.7+.
- `scripts/init_structure.sh` — idempotent scaffold for the three storage strategies (`single`, `hybrid`, `rules-only`). Preserves existing files by default; `--force` replaces them and requires applicable authorization.

## See also

- **`/agent-creator`** — subagent configuration and orchestration. A CLAUDE.md that defines project-wide instructions often pairs with `.claude/agents/*.md` files; use `/agent-creator` to author those.

## About

`claude-md` contains the substring `claude`, reserved by this repository's naming policy. The local exception covers first-party filename conventions: this skill operates directly on `CLAUDE.md`. The restriction and exception are repository policy, not agentskills.io requirements.
