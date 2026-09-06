# Skill Label-Hygiene Rules

Canonical block embedded verbatim in every skill whose primary outputs are shipped artifacts — code, comments, commits, PR bodies, review prose. Each skill carries its own copy so the rule travels on independent install (plugins cannot reference files outside their own directory). The `tests/_meta/test_skill_writing_rules.py` test enforces byte-level parity across declared skills; the `scripts/sync_writing_rules.py` script propagates canonical changes.

## Canonical block

The block below — including the two HTML-comment markers — is inserted verbatim into each declared SKILL.md, placed immediately after the H1 title and before any other `##` section. The `## Critical` header follows the canonical guidance on placement of critical instructions for maximum adherence.

```markdown
<!-- canonical:label-hygiene:start -->
## Critical — Label hygiene

Remove private planning labels and process narration from shipped code and prose. State the domain behavior directly.

- **Planning labels** — replace `WS-N`, `Phase-A`, `Step-3`, and private plan names with domain terms. <!-- noqa: internal-label -->
- **Process narration** — remove authoring history and references that require private planning context. Explain the resulting behavior or constraint.

Keep useful issue links, public ticket identifiers, user-requested traceability, and labels where the artifact defines that format. Reviewer-facing migration docs may name deleted artifacts.
<!-- canonical:label-hygiene:end -->
```

## Why this is a separate canonical block

Writing rules (`skill-prose-rules.md`) govern *style* — front-load verbs, no marketing words, no AI tells. Label hygiene governs *vocabulary leakage* — author coordinates slipping into reader-facing artifacts. Different concerns, different declared skill scopes, different failure modes. Co-located in adjacent canonical blocks; never merged.

## Declared label-hygiene skills

The sync script and the parity test read this list:

- apex
- ultrapex
- code-ultrareview
- frontend-dev
- oneshot
- award-design

Scope rule — skills whose primary output is shared external surface (code, commits, PR bodies, review prose, fix patches). Skills whose primary output is a per-project content artifact (DESIGN.md, BRAND-VOICE.md, CLAUDE.md, README.md, TRACK.md, forge planning files) are deliberately excluded because (a) the user owns the vocabulary in those files and (b) the leak patterns rarely appear there.

## Excluded skills (with reason)

- `agent-creator` — emits agent config files in `.claude/agents/` (per-project / global infrastructure); not a code-or-commit emitter. Low leak risk; add later if drift shows it.
- `brand-voice` — emits BRAND-VOICE.md (per-project content artifact).
- `claude-md` — emits CLAUDE.md (per-project content artifact).
- `forge` — emits per-project planning artifact whose format vocabulary IS `WS-N`; carve-out applies file-wide.
- `suno-produce` — emits TRACK.md / ALBUM.md (per-project content artifact).
- `write-clear-readme` — emits README.md (per-project content artifact).
- `humanize-en` — text-scrubber skill; different scope entirely.
- `audio-loop` — tooling skill emitting short status reports, not code or commits.
- `video-loop` — tooling skill emitting short status reports, not code or commits.
- `markitdown` — tooling skill emitting short status reports, not code or commits.
- `download-media` — tooling skill emitting short status reports, not code or commits.
- `scaffold` — tooling skill emitting short status reports, not code or commits.
- `design-system` — tooling skill emitting short status reports, not code or commits.
- `notion` — tooling skill routing to MCP/CLI and emitting short status reports, not code or commits.

## Rules for skill authors

- Insert the Canonical block (markers included) immediately after the SKILL.md H1 title. With the adversarial-verification, execution-discipline, and writing-rules blocks also present, the natural order — produced by `scripts/sync_writing_rules.py` — places adversarial-verification closest to H1, then execution-discipline, label-hygiene, writing-rules.
- The HTML-comment markers must remain unchanged — they are the extraction contract for `scripts/sync_writing_rules.py` and `tests/_meta/test_skill_writing_rules.py`.
- Never inject personal paths or brand-voice paths into the canonical block — `tests/_meta/test_skill_writing_rules.py` privacy assertions block it.
- Run `scripts/sync_writing_rules.py` after editing this file to propagate changes.

## Enforcement layers

The canonical block is guidance loaded into the skill's context window — high-prominence reminder at authoring time. The repo backstop lives at `tests/_meta/test_no_internal_label_leak.py`, which scans shipped skill source for the same patterns and fails CI red on any unallowlisted match. Per-line opt-out: `# noqa: internal-label` (Python / shell), `<!-- noqa: internal-label -->` (Markdown).
