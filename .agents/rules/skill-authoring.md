# Skill Authoring Workflow

Use the **official Anthropic `skill-creator` skill** when creating, updating, or evaluating a skill in this repository. It owns the authoring and evaluation workflow; the review requirements below are additional **maintainer policy**, not an Anthropic rubric.

## Source of truth

- Official skill: [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
- Typical installation: `~/.agents/skills/skill-creator/`
- Official [Agent Skills specification](https://agentskills.io/specification) and [Claude Code skills reference](https://code.claude.com/docs/en/skills)
- Use `/ask-archivist` for the Anthropic documentation mirror. Check each file's source URL and snapshot freshness; a filename alone does not establish which product it describes.

## Authoring and review

1. Read the existing skill, relevant bundled files, callers, and applicable repository rules. Define the behavior being changed and concrete acceptance checks.
2. Apply the edit and its conformance changes together, including README and evaluation cases where affected.
3. Invoke the official `skill-creator` for a fresh review of the final changed behavior before commit. Provide the absolute skill path and changes since the previous pass. Specify a full audit, regression check, fresh-eyes read, or description evaluation. Include these rules: `agentskills-spec.md`, `claude-code-skills.md`, `skill-authoring.md`, `repo-conventions.md`.
4. Review the findings on their merits. Fix demonstrated in-scope defects, refute false positives with evidence, and report material limitations. A subjective preference or out-of-scope suggestion is not automatically a required edit.
5. After a correction, review the affected behavior and its interactions again. Reuse unchanged evidence; a new spelling edit does not invalidate an unrelated runtime check.

**Exit criterion:** the final artifact meets the accepted scope, required checks pass, and no demonstrated in-scope defect remains unresolved. A user-accepted limitation must remain visible; do not label it verified or silently defer it.

The local review rubric covers eight axes: description and triggering, progressive disclosure, rule clarity, internal consistency, size, spec conformance, pattern coverage, and example quality. GREEN / YELLOW / RED may summarize evidence, but colors do not substitute for findings and do not force cosmetic unanimity. Use fresh context for independent review of consequential changes when the host supports it; disclose the limitation otherwise.

## Frontmatter and layout

- Use canonical fields from [agentskills-spec.md](./agentskills-spec.md), plus documented Claude Code extensions where applicable. Custom fields belong under `metadata`.
- Set `metadata.author: coroboros`. Omit per-skill versions; history and repository releases own versioning.
- Declare actual environment requirements in `compatibility` when needed (1–500 characters). Name required tools, host features, and limited fallback behavior. Omit it only when no special environment requirement needs stating. Do not promise universal graceful degradation.
- Keep metadata values strings. Cite external work in `metadata.sources` as one quoted string, separating multiple references with semicolons:
  ```yaml
  metadata:
    author: coroboros
    sources: "https://github.com/microsoft/markitdown"
  ```
- Inherit the session model and effort; do not pin either in skill frontmatter.
- Use plain Markdown headings. Keep the skill entrypoint under 500 lines and approximately 5,000 tokens; move detail into clearly routed supporting files.
- Embed the declared canonical prose, label-hygiene, execution, and verification blocks. Edit their owning `skill-*-rules.md` files, then run `scripts/sync_writing_rules.py`; independent installs need their own copies.
- Keep user documentation in the root README, not per-skill READMEs. Do not add `.skill` packages or per-skill install instructions.

## Repository integration

Check the root README table, per-skill details, examples, requirements, and pipeline diagram against the final behavior. Update only affected claims. Verify flag names, output paths, explicit `-f` handoffs, and standalone installation without assumed sibling files.

## Verification

Tests of bundled scripts live in `tests/<skill-name>/`; cross-skill invariants live in `tests/_meta/`. Behavioral examples in `skills/<name>/evals/` describe expected skill behavior and do not prove it was executed.

- For deterministic behavior changes, add or update a regression test when existing checks cannot distinguish the defect from the fix. Reuse adequate tests for refactors; do not add tests that only mirror implementation.
- Test thin wrappers' own contracts: arguments, exit codes, output paths, and overwrite guards. Use applicable installed CLIs for integration evidence.
- For instruction changes, exercise representative prompts and near misses with the official creator's evaluation workflow. Use its viewer and benchmark scripts for measured comparisons; do not build a replacement framework.
- Record the actual model, host, snapshot, and available tools for behavioral runs. Static checks and same-model councils are not cross-model benchmarks. Compare outcomes and scope, not just prose length.
- Use the official description optimization loop only with a model and runtime it actually supports. Do not pass another provider's model name to the Claude CLI.

Run `python3 -m unittest discover tests/` before reporting done and before commit. Report skips and their reasons, baseline failures, and unavailable external checks. Required failures block a complete verification claim; passing tests do not replace behavioral evidence.

## Independent review before a multi-skill PR

For a refactor touching multiple skills, run a fresh read-only review before opening the PR. Use the host's isolated reviewer capability, or explicitly report its absence. Provide the exact diff or snapshot, modified skills, request and corrections, accepted scope, the four canonical rules above, and verification evidence.

Ask the reviewer to find contradictions, missed defects, stale README claims, broken standalone references, and unnecessary mechanisms. Resolve substantive findings as above and recheck any resulting edits. Review completion does not authorize commit, push, merge, or publication.

## Avoid duplicated infrastructure

Use the official creator and its evaluation tools directly. Do not build a custom wrapper, copy its packaging workflow into this git-distributed repository, or add an orchestration layer solely to enforce this policy.
