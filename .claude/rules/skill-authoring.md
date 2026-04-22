# Skill Authoring Workflow

Creating, updating, or evaluating a skill in this repo requires the **official Anthropic `skill-creator` skill**. It is the canonical authoring tool, covers the full [best practices guide](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf), and includes the eval/iteration loop we do not reimplement.

## Source of truth

- Official skill: `github.com/anthropics/skills/skills/skill-creator`
- Installed path (typical): `~/.agents/skills/skill-creator/`
- Reference docs in this monorepo:
  - `coroboros/archivist/docs/insights/skills-complete-guide-to-building-skills-for-claude.md` — the full guide
  - `coroboros/archivist/docs/insights/skills-how-anthropic-uses-skills.md` — category taxonomy + patterns
  - `coroboros/archivist/docs/developer/developer-agents-and-tools-agent-skills-*.md` — API/platform spec
  - `coroboros/archivist/docs/code/code-skills.md` — Claude Code extensions

## When to invoke skill-creator

| Situation | Command |
|-----------|---------|
| New skill from scratch | "Use the skill-creator skill to help me build a skill for [use case]" |
| Improving an existing skill | Point skill-creator at the skill folder — it has explicit handling for updates |
| Optimizing a description | Use skill-creator's `run_loop.py` description optimization |
| Evaluating a skill quantitatively | Use skill-creator's eval viewer + benchmark pipeline |

## Post-generation conformance

After skill-creator produces a skill, align it with this repo before committing:

1. **Frontmatter**
   - Keep only: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` (from [agentskills-spec](./agentskills-spec.md)), plus Claude Code extensions (from [claude-code-skills](./claude-code-skills.md)) if the skill is Claude Code-scoped.
   - Any custom fields go under `metadata:`.
   - Add `metadata.author: coroboros`. Do **not** add `metadata.version` — skills are co-versioned through the repo tags and the `marketplace.json` version. Per-skill versions create drift (every release, only touched skills get bumped, others lag behind — confusing to readers). `git log skills/<name>/` is the authoritative change history.

2. **Body**
   - Plain Markdown headings only. No XML sections (`<objective>`, `<workflow>`, etc.).
   - Reference supporting files (`steps/`, `references/`, `scripts/`) from SKILL.md with clear guidance on when to read them.
   - Under 500 lines, under 5,000 tokens.

3. **File layout**
   - No `README.md` inside the skill folder. User-facing docs live in the root `README.md` only.
   - No trailing `.skill` package, no per-skill install instructions.

4. **Repo integration**
   - Update the root `README.md` skills table and per-skill details section.
   - **Audit the README section for staleness** — every touch on a SKILL.md must verify that the README's listed flags, usage examples, workflow steps, and requirements still match. README drift is easy to miss when focus is on the skill itself; it's the cheapest bug to introduce and the easiest to catch at this step.
   - Update the pipeline diagram if the skill chains with others.
   - Verify cross-references (flag names, output paths, `-f` contracts) are consistent.

## Audit before PR

For any refactor touching more than one skill, run an Explore-agent audit before opening the PR. This catches frontmatter drift, description staleness, and bug regressions before they land.

Brief the agent with:

1. The branch name and the modified skills — point it at `git log main..<branch>` for the atomic commits.
2. The optimization axes taken (progressive disclosure, description triggers, subagents, bug fixes, etc.).
3. Axes intentionally NOT taken, with rationale (no subagents, no flag convention, no extraction) — helps the agent avoid false positives.
4. The four canonical rules to verify against: `agentskills-spec.md`, `claude-code-skills.md`, `skill-authoring.md`, `repo-conventions.md`.
5. Per-skill checks:
   - Frontmatter correctness (canonical fields only + Claude Code extensions as applicable, `metadata.author: coroboros`, **no `metadata.version`**, no reserved names)
   - Description quality (WHAT + WHEN, triggers discoverable, not generic)
   - `when_to_use` where applicable (keywords, skip conditions, return value)
   - Workflow correctness (step order, no hardcoded assumptions that break across project configs)
   - Size budget (<500 lines, <5000 tokens)
   - Cross-skill consistency (shared sections align across the refactored set)
6. Expected verdict format: `GREEN` / `YELLOW` / `RED` per skill with 2–4 bullet findings (file:line when applicable), plus a one-line overall verdict. Keep the report under ~500 words.

**Merge gate.** GREEN per skill → proceed with the PR. YELLOW → fix in a follow-up commit before merge. RED → block the PR and re-work.

## What NOT to do

- Do not build a custom skill-creator wrapper. The official one is comprehensive.
- Do not copy the skill-creator's `.skill` packaging into this repo — we distribute via git + `npx skills add`.
- Do not duplicate skill-creator's eval infrastructure. Invoke it directly when needed.
