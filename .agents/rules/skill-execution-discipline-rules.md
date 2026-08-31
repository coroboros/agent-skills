# Skill Execution-Discipline Rules

Canonical block embedded verbatim in every skill that writes, edits, or proposes code. Each skill carries its own copy so the rule travels on independent install (plugins cannot reference files outside their own directory). The `tests/_meta/test_skill_writing_rules.py` test enforces byte-level parity across declared skills; the `scripts/sync_writing_rules.py` script propagates canonical changes.

## Canonical block

The block below — including the two HTML-comment markers — is inserted verbatim into each declared SKILL.md, placed immediately after the H1 title and before any other `##` section. The `## Important` header follows the canonical guidance on placement of critical instructions for maximum adherence.

```markdown
<!-- canonical:execution-discipline:start -->
## Important — Engineering discipline

These rules govern how this skill changes code — apply them whenever it writes, edits, or proposes a fix.

- Minimal scope. Only what's directly requested or clearly necessary — no extra files, no abstraction for one use, no configurability nobody asked for, no error handling for states that can't happen. Validate at system boundaries; trust internal code.
- General solution, not the test cases. Implement the real logic for all valid inputs; never hard-code to inputs or bolt on workaround scripts to make a test pass. Tests verify the solution; they don't define it. A test is wrong? Say so — don't bend correct code to a broken test.
- Investigate before claiming. Never speculate about code you haven't opened; read the referenced file before answering. Ground every claim in what you actually read, not a plausible guess.
<!-- canonical:execution-discipline:end -->
```

## Why this is a separate canonical block

Writing rules (`skill-prose-rules.md`) govern *style* of the prose a skill emits. Label hygiene (`skill-label-hygiene-rules.md`) governs *vocabulary leakage* into shipped artifacts. Execution discipline governs *how the skill does the work* — scope creep, test-gaming, and ungrounded claims about code. Different concern, different declared scope (code-producing skills only), different failure modes. Co-located in adjacent canonical blocks; never merged.

## Declared execution-discipline skills

The sync script and the parity test read this list:

- apex
- ultrapex
- award-design
- code-ultrareview
- oneshot

Scope rule — skills that write, edit, or propose code (implementation, review, applied fixes). Skills whose primary output is a per-project content artifact (BRAND-VOICE.md, CLAUDE.md, README.md, TRACK.md, agent config, a forge planning file) or a short tooling status report are deliberately excluded. award-design authors a DESIGN.md and the build ladder, then builds each ladder chunk as code, so it is declared, not excluded.

## Excluded skills (with reason)

- forge — thinking-only; never implements. Overengineering is already governed by its three-tier Decide, source grounding by its triangulation discipline.
- agent-creator — emits agent config (`.claude/agents/`), not code; the general-solution and investigate-before-claiming lines do not apply.
- design-system — governs DESIGN.md tokens; tooling/status output, not code.
- claude-md — emits CLAUDE.md (per-project content artifact), not code.
- brand-voice — emits BRAND-VOICE.md (per-project content artifact), not code.
- write-clear-readme — emits README.md (per-project content artifact), not code.
- suno-produce — emits TRACK.md / ALBUM.md (per-project content artifact), not code.
- scaffold — runs a fixed bootstrap and emits a short status report, not authored code.
- markitdown — wraps a converter CLI and emits a short status report, not code.
- download-media — wraps a downloader CLI and emits a short status report, not code.
- notion — routes to MCP/CLI and emits a short status report, not code.
- audio-loop — media tooling emitting short status reports, not code.
- video-loop — media tooling emitting short status reports, not code.
- humanize-en — text scrubber; different scope entirely.

## Rules for skill authors

- Insert the Canonical block (markers included) immediately after the SKILL.md H1 title. With the adversarial-verification, label-hygiene, and writing-rules blocks also present, the natural order — produced by `scripts/sync_writing_rules.py` — places adversarial-verification closest to H1, then execution-discipline, label-hygiene, writing-rules.
- The HTML-comment markers must remain unchanged — they are the extraction contract for `scripts/sync_writing_rules.py` and `tests/_meta/test_skill_writing_rules.py`.
- Never inject personal paths or brand-voice paths into the canonical block — `tests/_meta/test_skill_writing_rules.py` privacy assertions block it.
- Run `scripts/sync_writing_rules.py` after editing this file to propagate changes.
