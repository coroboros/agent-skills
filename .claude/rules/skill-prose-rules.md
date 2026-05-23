# Skill Prose Rules

Canonical writing rules embedded verbatim in every prose-emitting skill in this repo. Skills must carry the *Canonical block* (below) inside their SKILL.md so the rules travel on independent install — plugins cannot reference files outside their own directory, so each skill bundles its own copy. The `tests/_meta/test_skill_writing_rules.py` test enforces byte-level parity across declared skills; the `scripts/sync_writing_rules.py` script propagates canonical changes.

## Canonical block

The block below — including the two HTML-comment markers — is inserted verbatim into each declared SKILL.md, placed immediately after the H1 title and before any other `##` section. The `## Important` header follows the canonical guidance on placement of critical instructions for maximum adherence.

```markdown
<!-- canonical:writing-rules:start -->
## Important — Writing rules

These rules govern every prose artifact this skill emits — READMEs, CHANGELOGs, commit messages, PR bodies, release notes, doc paragraphs, non-trivial comments. Apply them at draft time, verify before output.

- Match the surrounding style — punctuation, capitalization, backtick conventions, em-dash vs parens, bullet style.
- Every sentence changes the reader's understanding. Cut it otherwise.
- Front-load the verb — "Creates", not "This helps you create".
- Concrete over abstract. Lists for ≥3 enumerable items.
- Assert positively. Reserve negation for real constraints (`NEVER commit secrets`).
- No marketing words: powerful, robust, seamlessly, leverage, unlock, comprehensive, delightful.
- No AI tells: delve, tapestry, intricate, pivotal, testament, underscore, crucial, garner, showcase, additionally, moreover, furthermore, indeed.
- After drafting English prose, invoke `/humanize-en` if installed.
<!-- canonical:writing-rules:end -->
```

## Scope boundary — `/humanize-en` vs skill source

The canonical block's `/humanize-en` line governs prose a skill *emits* (the documents it generates) and external docs (README, CHANGELOG, PR/issue/commit/release bodies) — never the skill's own authoring files (`SKILL.md`, `steps/`, `references/`, `templates/`, `evals/`). Those are model instructions, not prose deliverables; `/skill-creator` is their sole quality authority. Running `/humanize-en` on skill source contaminates the canonical state the review loop reasons from.

## Declared prose-emitting skills

The sync script and the parity test read this list:

- agent-creator
- apex
- award-design
- brand-voice
- claude-md
- code-ultrareview
- forge
- oneshot
- suno-produce
- write-clear-readme

## Excluded skills (with reason)

- `fix-grammar` — explicit no-rephrasing contract; embedding "concision" rules conflicts with the skill's scope.
- `humanize-en` — IS the scrubber; circular dependency.
- `audio-loop` — tooling skill emitting short status reports, not prose artifacts.
- `video-loop` — tooling skill emitting short status reports, not prose artifacts.
- `markitdown` — tooling skill emitting short status reports, not prose artifacts.
- `scaffold` — tooling skill emitting short status reports, not prose artifacts.
- `design-system` — tooling skill emitting short status reports, not prose artifacts.
- `notion` — tooling skill routing to MCP/CLI and emitting short status reports, not prose artifacts.

## Rules for skill authors

- Insert the Canonical block (markers included) immediately after the SKILL.md H1 title and before any other `##` section.
- Skill-specific style additions (e.g., `write-clear-readme`'s "Headings as questions or commands") live in a separate `## <Skill-name>-specific style` section adjacent to the canonical block.
- The HTML-comment markers must remain unchanged — they are the extraction contract for `scripts/sync_writing_rules.py` and `tests/_meta/test_skill_writing_rules.py`.
- Never inject brand-voice paths or maintainer-specific paths into the canonical block — that would leak per-author config into public artifacts.
- Run `scripts/sync_writing_rules.py` after editing this file to propagate changes.
