# Agent Skills

Public collection of installable AI agent skills for Claude Code and compatible agents. Each skill is a self-contained folder in `skills/` with a `SKILL.md` at its root.

No build step, no tests, no dependencies, no package manager. Pure Markdown + shell scripts.

## Canonical rules

Repo-specific authoring rules — source of truth for authoring, structure, conventions. Read before editing any skill or adding a new one.

@.claude/rules/agentskills-spec.md
@.claude/rules/claude-code-skills.md
@.claude/rules/skill-authoring.md
@.claude/rules/repo-conventions.md

Global rules (`~/.claude/rules/*`) inherit automatically — tech-standards, writing, find-docs, git-conventions, privacy, overrides. The path-scoped `@~/.claude/rules/changelog.md` never applies (no `CHANGELOG.md` in this repo). Git-conventions divergences are stated inline under `## At a glance` below.

## At a glance

- **Standard**: [agentskills.io](https://agentskills.io) open standard (frontmatter, folder anatomy) + Claude Code extensions for Claude Code-scoped skills.
- **Authoring tool**: the official Anthropic `skill-creator` skill is mandatory for creating/updating skills. We do not build our own.
- **Layout**: `skills/{name}/SKILL.md` + optional `steps/`, `templates/`, `scripts/`, `references/`. No per-skill `README.md`.
- **Install**: `npx skills add coroboros/agent-skills --skill <name>` via [skills.sh](https://skills.sh).
- **Git** — branch `main`; no `CHANGELOG.md` (release notes live in the `gh release create` body only); version lives only in git tags and in `.claude-plugin/marketplace.json` `metadata.version` — there is no `package.json`, so no `pnpm version` bump. All other rules in `@~/.claude/rules/git-conventions.md` apply.

## When creating or updating a skill

1. Read the relevant rules above.
2. Invoke the official skill-creator: *"Use the skill-creator skill to help me build/update a skill for [use case]"*.
3. Conform the output to this repo's shape — see `.claude/rules/skill-authoring.md` for the post-generation checklist.
4. Update the root `README.md` skills table and per-skill details.
5. Verify pipeline chaining (`-f` contracts, output paths) across related skills.
6. **Audit before PR** — for any refactor touching more than one skill, spawn an Explore-agent audit with the skill-creator checklist + repo rules. Require GREEN per skill. See `.claude/rules/skill-authoring.md` → *Audit before PR*.
7. Open a PR — significant changes only; minor tweaks can go straight to `main`.

## Reference docs in the monorepo

Up-to-date mirrors of the official Anthropic documentation:

- `coroboros/archivist/docs/insights/skills-complete-guide-to-building-skills-for-claude.md` — authoring guide
- `coroboros/archivist/docs/insights/skills-how-anthropic-uses-skills.md` — skill categories + internal patterns
- `coroboros/archivist/docs/developer/developer-agents-and-tools-agent-skills-*.md` — API spec + best practices
- `coroboros/archivist/docs/code/code-skills.md` — Claude Code skill features
