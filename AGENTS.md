# Agent Skills

<!-- agents-config:behave:start -->
## Rule Index

_Project-level behavior reinforcement installed by `behave`; re-run `behave` to refresh this managed block._

Before planning or editing, read this rule first:

- `.agents/rules/behavior.md` - canonical behavior discipline: production-grade, surgical, fail-loud, never-invent.
- `.agents/rules/behavior-fable.md` - Fable addendum — model scope stated in the file.
<!-- agents-config:behave:end -->

Public collection of installable AI agent skills for Claude Code and compatible agents. Each skill is a self-contained folder in `skills/` with a `SKILL.md` at its root.

Markdown + bash + Python 3 (stdlib only). No build step. No package manager.

## Canonical rules

Read the matching rule before planning or editing:

- `.agents/rules/agentskills-spec.md` — canonical frontmatter, folder anatomy, size budget
- `.agents/rules/claude-code-skills.md` — Claude Code extensions and string substitutions
- `.agents/rules/skill-authoring.md` — mandatory `skill-creator` flow + the testing requirement
- `.agents/rules/repo-conventions.md` — flags, output paths, install, plugin marketplace, test placement
- `.agents/rules/skill-{prose,label-hygiene,execution-discipline,adversarial-verification}-rules.md` — canonical blocks synced into declaring SKILL.md bodies by `scripts/sync_writing_rules.py`

## At a glance

- **Standard**: [agentskills.io](https://agentskills.io) open standard (frontmatter, folder anatomy) + Claude Code extensions for Claude Code-scoped skills.
- **Authoring tool**: the official Anthropic `skill-creator` skill is mandatory for creating/updating skills. We do not build our own.
- **Layout**: `skills/{name}/SKILL.md` + optional `steps/`, `templates/`, `scripts/`, `references/`. No per-skill `README.md`.
- **Install**: `npx skills add coroboros/agent-skills --skill <name>` via [skills.sh](https://skills.sh).
- **Runtime**: bash + Python 3 (stdlib only) for bundled scripts. Works anywhere with bash + `python3` and a filesystem. Skills ship via `npx skills add` and run without setup; the org-wide Bun preference does not apply. Some skills wrap external CLIs — each is declared in its SKILL.md.
- **Git** — branch `main`; no `CHANGELOG.md` (release notes live in the `gh release create` body only); version lives only in git tags and in `.claude-plugin/marketplace.json` `metadata.version` — there is no `package.json`, so no `pnpm version` bump. All other rules in `~/.agents/rules/git-conventions.md` apply.
- **Security** — `cisco-ai-defense/skill-scanner` scans the `skills/` tree on every push and PR via `.github/workflows/scan-skills.yml` (policy `balanced`, fail-on `critical`). SHA-pinned to a tagged release; Dependabot auto-PRs new versions weekly.
- **Validation** — `python3 -m unittest discover tests/` before reporting done; `scripts/sync_writing_rules.py` after editing a canonical `skill-*-rules.md` block.
