# Skill Authoring Workflow

Creating, updating, or evaluating a skill in this repo requires the **official Anthropic `skill-creator` skill**. It is the canonical authoring tool, covers the full [best practices guide](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf), and includes the eval/iteration loop we do not reimplement.

## Source of truth

- Official skill: `github.com/anthropics/skills/skills/skill-creator`
- Installed path (typical): `~/.agents/skills/skill-creator/`
- Reference docs: invoke skill `/ask-analyst` if present

## When to invoke skill-creator — strict loop

**Every edit to a `SKILL.md` or any of its bundled files (`references/`, `scripts/`, `templates/`, `assets/`) triggers a fresh `/skill-creator` invocation before commit.** No exceptions. No trivial-change carve-out. If the edit was not worth a review pass, it was not worth making.

### The loop

1. **Edit** — apply the draft or fix.
2. **Invoke `/skill-creator`** with four fields, every time:
   - *Skill path* — absolute path to the folder.
   - *What changed* — the fixes applied since the previous pass (or *"initial draft"* on first call).
   - *Specific ask* — one of: full audit / regression check / fresh-eyes read / description optimisation. Pick per the table below.
   - *Rules to verify against* — `agentskills-spec.md`, `claude-code-skills.md`, `skill-authoring.md`, `repo-conventions.md`.
3. **Read the verdict** — GREEN / YELLOW / RED on each of the 8 canonical axes (description & triggering, progressive disclosure, rule clarity, internal consistency, size & budget, spec conformance, pattern coverage, example quality), with `file:line` findings and a priority action list.
4. **Apply every non-GREEN finding** in the current PR. RED and YELLOW both block commit — there is no "follow-up" bucket.
5. **Restart at step 1** for any further edit, including fix-to-a-fix. Fresh invocation every iteration is how regressions surface.

**Exit criterion.** Commit only when `/skill-creator` returns **GREEN on every axis**. Two-to-three iterations to GREEN is normal.

The loop exists because single-shot edits routinely leave stale cross-references, self-flagging examples, unreachable branches, and cross-section contradictions that only surface under fresh-eyes review. Skipping the invocation consistently costs more in downstream regressions than it saves upfront.

### Ask, by situation

| Situation | Ask |
|-----------|-----|
| New skill from scratch | Full audit on the 8 canonical axes |
| Adding a feature or pattern | Regression audit of the diff against prior state |
| Fixing a finding from the previous pass | Regression check — did the fix hold? Any new drift? |
| Wording polish or de-duplication | Fresh-eyes read end-to-end |
| Optimising description for triggering | `run_loop.py` description optimisation |
| Evaluating quantitatively (objective outputs only) | Eval viewer + benchmark pipeline |

A vague ask returns vague feedback.

## Post-generation conformance

Once the loop returns GREEN, align the skill with this repo before committing:

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

1. The branch name and the modified skills — point it at `git log main..<branch>` for the commits.
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

**Merge gate.** GREEN per skill → proceed with the PR. YELLOW → fix in a follow-up step before merge. RED → block the PR and re-work.

## What NOT to do

- Do not build a custom skill-creator wrapper. The official one is comprehensive.
- Do not copy the skill-creator's `.skill` packaging into this repo — we distribute via git + `npx skills add`.
- Do not duplicate skill-creator's eval infrastructure. Invoke it directly when needed.
