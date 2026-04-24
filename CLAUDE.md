# Agent Skills

Public collection of installable AI agent skills for Claude Code and compatible agents. Each skill is a self-contained folder in `skills/` with a `SKILL.md` at its root.

No build step, no tests, no dependencies, no package manager. Pure Markdown + shell scripts.

## Canonical rules

@.claude/rules/agentskills-spec.md
@.claude/rules/claude-code-skills.md
@.claude/rules/skill-authoring.md
@.claude/rules/repo-conventions.md

## At a glance

- **Standard**: [agentskills.io](https://agentskills.io) open standard (frontmatter, folder anatomy) + Claude Code extensions for Claude Code-scoped skills.
- **Authoring tool**: the official Anthropic `skill-creator` skill is mandatory for creating/updating skills. We do not build our own.
- **Layout**: `skills/{name}/SKILL.md` + optional `steps/`, `templates/`, `scripts/`, `references/`. No per-skill `README.md`.
- **Install**: `npx skills add coroboros/agent-skills --skill <name>` via [skills.sh](https://skills.sh).
- **Git** — branch `main`; no `CHANGELOG.md` (release notes live in the `gh release create` body only); version lives only in git tags and in `.claude-plugin/marketplace.json` `metadata.version` — there is no `package.json`, so no `pnpm version` bump. All other rules in `~/.claude/rules/git-conventions.md` apply.
