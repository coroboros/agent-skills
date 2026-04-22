# Spec: {title}

**Date:** {YYYY-MM-DD}
**Status:** Draft

## Overview

[2-4 sentences. What this is, why it matters, what it enables. Written for someone who has no prior context.]

## Goals

- [Goal 1: specific, measurable]
- [Goal 2: specific, measurable]
- [Goal 3: specific, measurable]

## Non-goals

- [Explicit exclusion 1 — and briefly why it's excluded]
- [Explicit exclusion 2]

## Background

[What exists today. What problem this solves. If from a brainstorm, reference it. If a codebase exists, summarize relevant architecture. 3-5 sentences max.]

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

**Acceptance criteria:**
- [ ] {specific, testable criterion 1}
- [ ] {specific, testable criterion 2}

**Technical notes:** [Optional. Only when there are specific codebase references, patterns to follow, or non-obvious implementation hints. Omit entirely if nothing genuinely helpful to add.]

---

### WS-2: {workstream title}

[Same structure as WS-1. Repeat for each workstream.]

---

## Dependencies

[Only include if workstreams have dependencies on each other.]

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

## Assumptions

[Only include if `{auto_mode}` was used OR if specific assumptions were necessary.]

- {Assumption 1 — what was assumed and why}
- {Assumption 2}

## Open questions

[Only include if there are genuinely unresolved items that need human decision before implementation can begin.]

- [ ] {Question requiring human decision}

## Execution order

Recommended implementation sequence:

1. **WS-{N}** (P0) — {one-line rationale for why this is first}
2. **WS-{N}** (P0) — {rationale}
3. **WS-{N}** (P1) — {rationale}
4. **WS-{N}** (P2) — {rationale}
