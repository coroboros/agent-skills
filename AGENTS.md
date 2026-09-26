# Agent Skills

Public collection of installable AI agent skills for Claude Code and compatible agents. Each skill is a self-contained folder in `skills/` with a `SKILL.md` at its root.

## Project constraints

- Bundled scripts use Bash and Python 3 (stdlib only); the org-wide Bun preference does not apply. Skills declare external CLI prerequisites in `SKILL.md` and fail with exact install and rerun guidance when an applicable tool is missing. They do not resolve tool packages at runtime. Skills that create projects or packages may install the requested dependencies.
- Skills install independently. Do not assume sibling skills are installed; follow `.agents/rules/repo-conventions.md` for cross-skill cooperation. User documentation lives in the root README, with no per-skill root README.

<!-- behavior-rules:start -->
## Rule index

Read the rules relevant to the task before acting. Reuse unchanged guidance already read in this session.

- `.agents/rules/behavior.md` - canonical behavior discipline: production-grade, size budget, surgical, fail-loud, never-invent.
- `.agents/rules/behavior-frontier.md` - Frontier addendum — model scope stated in the file.
<!-- behavior-rules:end -->

The behavior rules above govern every task within their stated scope.

- **Authoring or evaluating a skill:** read `.agents/rules/skill-authoring.md` and use the official Anthropic `skill-creator`.
- **Frontmatter, layout, or portability:** read `.agents/rules/agentskills-spec.md`; read `.agents/rules/claude-code-skills.md` for Claude Code extensions and substitutions.
- **Flags, output paths, installation, marketplace, or CI changes:** read `.agents/rules/repo-conventions.md`.
- **Adding, changing, or removing tests:** read [Testing](.agents/rules/repo-conventions.md#testing) for regression value, coverage preservation, and execution limits.
- **Shared skill instructions:** edit the owning `.agents/rules/skill-{prose,label-hygiene,execution-discipline,adversarial-verification}-rules.md` block or `.agents/rules/skill-quality-lens-rules.md`. These sources declare their recipients; the sync script updates the bundled copies.

## Validation

- Run `python3 -m unittest discover tests/` before reporting done and before commit. Report failures, skips and their reasons, and unavailable external checks; passing tests alone do not establish skill behavior or host compatibility.
- After editing a canonical `skill-*-rules.md` block, run `python3 scripts/sync_writing_rules.py` and review the propagated diff.

## Release

Use branch `main`. Release notes belong only in the `gh release create` body; there is no `CHANGELOG.md`. Versions live only in git tags and `.claude-plugin/marketplace.json` `metadata.version`. There is no root `package.json` or `pnpm version` step. All other rules in `~/.agents/rules/git-conventions.md` apply.
