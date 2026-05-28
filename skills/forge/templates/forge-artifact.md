# Decision: {title}

<!-- DEFAULT shape: # Decision — keep this H1, Decision header, Assumption ledger,
     Overview, and (when relevant) Risks + Open questions. Omit Workstreams,
     Dependencies, and Execution order. Present and pause for the decompose
     question after Save.

     PROMOTED shape: # Spec — retitle the H1 to `# Spec: {title}` and include the
     full structure below (Workstreams, Dependencies, Execution order). Promote
     only when the routing rule in SKILL.md Phase 4 fires (the six promotion
     conditions are enumerated there — never enumerate a subset here, the two
     lists drift). -->

**Date:** {YYYY-MM-DD}
**Status:** Draft

## Decision

- **Chosen:** {approach} — {1-2 sentence rationale}
- **Runner-up:** {alternative} — {the condition under which it would win}
- **Surfaced forks:** {load-bearing calls — name each, the pick, the runner-up, what would flip it. The user came for thinking, not plumbing; do not bury these in the ledger. Or "none" when the artifact has no structurally load-bearing forks}
- **Escalated forks:** {the few user-owned questions, or "none"}

## Assumption ledger

Tag each as **verified fact**, **assumption**, or **inherited convention**. Flag the shakiest — it becomes an open question or a risk.

- [verified fact] {what is known, and the source}
- [assumption] {what was assumed, and why}
- [inherited convention] {what was taken as given from existing code or prior docs}

## Overview

[2-4 sentences. What this is, why it matters, what it enables. Written for someone with no prior context.]

## Goals

[Outcomes, not outputs — "cut X from N to M", not "build the wizard". Each answers "how do we know it worked?". See `references/spec-craft.md`.]

- [Goal 1: measurable outcome]
- [Goal 2: measurable outcome]

## Non-goals

- [Explicit exclusion — tag the rationale: not enough impact / too complex for now / separate initiative / premature]

## Background

[What exists today. What problem this solves. If from prior context, reference it. 3-5 sentences max.]

---

## Workstreams

### WS-1: {workstream title}

| Field | Value |
|-------|-------|
| Priority | P0 / P1 / P2 |
| Complexity | S / M / L / XL |
| Depends on | — / WS-N |

**Description:** [1-2 sentences on what this workstream delivers]

**Tasks:**
- [ ] {concrete task 1}
- [ ] {concrete task 2}
- [ ] {concrete task 3}

**Acceptance criteria:** [Given/When/Then inside each `- [ ]` item; cover happy + error + edge; ≥1 negative. See `references/spec-craft.md`.]
- [ ] {Given <precondition>, when <action>, then <observable outcome>}
- [ ] {negative — what must NOT happen}

**Technical notes:** [Optional. Only when there are specific codebase references, patterns to follow, or non-obvious hints. Omit entirely if nothing genuinely helpful to add.]

---

### WS-2: {workstream title}

[Same structure as WS-1. Repeat for each workstream — 3-7 total.]

---

## Dependencies

[Only include if workstreams depend on each other.]

```
WS-1 --> WS-3
WS-2 --> WS-4
WS-3 --> WS-5
```

## Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| {risk 1} | High / Medium / Low | High / Medium / Low | {specific mitigation} |
| {risk 2} | ... | ... | ... |

[Only genuine risks — not generic "things might change" filler.]

## Open questions

[Only genuinely unresolved items needing human decision — the escalated forks. Split by whether they block a workstream start.]

**Blocking** — must be answered before the dependent workstream starts:
- [ ] {question} → blocks WS-{N}

**Non-blocking** — can be resolved during implementation:
- [ ] {question}

## Parking lot

[Good ideas surfaced but deliberately out of scope — captured so they neither get lost nor creep into the workstreams. Omit if empty.]

- {idea} — revisit when {trigger}

## Execution order

Recommended implementation sequence:

1. **WS-{N}** (P0) — {one-line rationale for why this is first}
2. **WS-{N}** (P0) — {rationale}
3. **WS-{N}** (P1) — {rationale}
