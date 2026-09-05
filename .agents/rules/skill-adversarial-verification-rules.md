# Skill Adversarial-Verification Rules

Canonical block embedded verbatim in every skill that must verify its own findings before acting on them. Each skill carries its own copy so the rule travels on independent install (plugins cannot reference files outside their own directory). The `tests/_meta/test_skill_writing_rules.py` test enforces byte-level parity across declared skills; the `scripts/sync_writing_rules.py` script propagates canonical changes.

## Canonical block

The block below — including the two HTML-comment markers — is inserted verbatim into each declared SKILL.md, placed immediately after the H1 title and before any other `##` section. The `## Critical` header follows the canonical guidance on placement of critical instructions for maximum adherence.

```markdown
<!-- canonical:adversarial-verification:start -->
## Critical — Adversarial verification

Verify consequential findings and decisions before acting on them.

- Seek counterexamples and independent evidence for load-bearing or contested claims. Use fresh reviewers when available and useful; label sequential self-review as less independent.
- Resolve material findings by correction, evidence-backed refutation, or an explicit remaining risk. Never silently drop them.
- Evidence decides, not reviewer counts or confidence alone. One reproducible defect can invalidate a conclusion.
- Scale verification to the stakes. Keep settled facts settled and reversible, low-impact checks light.
<!-- canonical:adversarial-verification:end -->
```

## Why this is a separate canonical block

Writing rules (`skill-prose-rules.md`) govern *style* of the prose a skill emits. Label hygiene (`skill-label-hygiene-rules.md`) governs *vocabulary leakage* into shipped artifacts. Execution discipline (`skill-execution-discipline-rules.md`) governs *how the skill changes code*. Adversarial verification governs *how the skill trusts its own findings* — refute-by-default, no-silent-drop, and the discipline to not manufacture doubt on settled facts. Different concern, different declared scope (claim/finding/decision emitters), different failure modes. Co-located in adjacent canonical blocks; never merged.

The block defines evidence handling without a scoring scale. Each skill owns its review mechanics: forge challenges decisions, code-ultrareview validates observations in context, and implementation skills verify accepted outcomes. Local confidence rubrics do not establish factual certainty.

## Declared adversarial-verification skills

The sync script and the parity test read this list:

- forge
- apex
- ultrapex
- award-design
- code-ultrareview

Scope rule — skills whose primary output is a claim, a finding, or a decision that drives expensive or irreversible action, and that already run a verification loop. forge decides; code-ultrareview surfaces defects; apex self-validates in eXamine; ultrapex refutes before reporting; award-design refutes its own committed direction and the built site in its review mode.

## Excluded skills (with reason)

- oneshot — deliberately single-pass with a complexity circuit breaker; a refute-by-default loop contradicts its fast-path design. Correctness is governed by its execution-discipline and label-hygiene blocks.
- frontend-dev — the frontend builder; ordinary work uses the fresh-pixels sweep and ship checklist, while a supplied award-design chunk carries its own verification and design-review gates. Correctness is governed by its execution-discipline and label-hygiene blocks; no separate blanket review loop is added.
- agent-creator — emits agent config (`.claude/agents/`), not findings or decisions to verify.
- design-system — governs DESIGN.md tokens; tooling/status output, not findings.
- claude-md — emits CLAUDE.md (per-project content artifact), not findings.
- brand-voice — emits BRAND-VOICE.md (per-project content artifact), not findings.
- write-clear-readme — emits README.md (per-project content artifact), not findings.
- suno-produce — emits TRACK.md / ALBUM.md (per-project content artifact), not findings.
- scaffold — runs a fixed bootstrap and emits a short status report, not findings.
- markitdown — wraps a converter CLI and emits a short status report, not findings.
- download-media — wraps a downloader CLI and emits a short status report, not findings.
- notion — routes to MCP/CLI and emits a short status report, not findings.
- audio-loop — media tooling emitting short status reports, not findings.
- video-loop — media tooling emitting short status reports, not findings.
- humanize-en — text scrubber; different scope entirely.

## Rules for skill authors

- Insert the Canonical block (markers included) immediately after the SKILL.md H1 title. The sync script inserts a new block right after H1, so adversarial-verification lands closest to H1; the other canonical blocks (execution-discipline, label-hygiene, writing-rules) sit below it in that order.
- The HTML-comment markers must remain unchanged — they are the extraction contract for `scripts/sync_writing_rules.py` and `tests/_meta/test_skill_writing_rules.py`.
- Never inject personal paths or brand-voice paths into the canonical block — `tests/_meta/test_skill_writing_rules.py` privacy assertions block it.
- Run `scripts/sync_writing_rules.py` after editing this file to propagate changes.
