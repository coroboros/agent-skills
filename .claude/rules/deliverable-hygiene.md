# Deliverable Hygiene

Shipped skill source lives under `skills/<name>/` and is installed verbatim onto users' machines via `npx skills add coroboros/agent-skills --skill <name>`. Anyone reading it has no access to the author's planning artifacts, scratch files, or session history. Two recurring patterns leak that context. Both have CI gates; the principle is stated here so it applies to every contributor surface, not just `/apex`-driven sessions.

## Author-coordinate language

Workstream labels, spec-process vocabulary, and rebuild-history breadcrumbs require the reader to share the author's mental model. Translate to domain facts before shipping — describe the behavior the prose addresses, not the planning artifact it originated from. The same discipline applies to PR titles and bodies, which become the permanent squash-merge commit message.

Enforcement:
- `tests/_meta/test_no_internal_label_leak.py` — scans `skills/<name>/` source.
- `.github/workflows/ci.yml` `scan-pr-body` job — scans PR title and body on every pull request.

Opt-out (legitimate prose that names the anti-pattern): `# noqa: internal-label` in Python/shell/JSON, `<!-- noqa: internal-label -->` in Markdown.

## Bare cross-skill install paths

A reference inside `skills/<a>/...` to `skills/<b>/...` is a dead link on partial install — `npx skills add ... --skill a` lands only `~/.claude/skills/a/`. The bulletproof pattern has three forms by context:
- Documentation citation → `https://github.com/coroboros/agent-skills/blob/main/skills/<b>/...`.
- Runtime dispatch → slash command `/<b>` for skill invocation; triple-fallback for direct script (`${CLAUDE_SKILL_DIR}/../<b>/...` → `~/.claude/skills/<b>/...` → `~/.agents/skills/<b>/...`).
- Parity contract → GitHub URL plus the phrase "parity counterpart".

Enforcement:
- `tests/_meta/test_no_cross_skill_install_path_leak.py` — scans `skills/<name>/` source; recognises the allowed prefixes above.

Opt-out: `# noqa: cross-skill-path` or `<!-- noqa: cross-skill-path -->`.

## Scope

The rule binds every contributor surface that ships under `skills/<name>/` or appears in a PR title or body. `/apex`'s step-04 checklist is one enforcement point; the CI gates are the others. Manual edits to a SKILL.md outside `/apex` fall under the same discipline.
