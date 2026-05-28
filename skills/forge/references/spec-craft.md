# Spec craft

Hardening techniques for the Forge phase. Read this when writing acceptance criteria, setting priorities, or phrasing goals — not on every run. The discipline here is what separates a plan `/apex` can execute blind from one it has to guess at.

## Acceptance criteria

Each criterion stays a `- [ ]` checklist item (the validator requires it) and reads as a testable assertion, not a wish.

- Phrase as Given/When/Then inside the item: `- [ ] Given <precondition>, when <action>, then <observable outcome>`.
- Cover the happy path, the error path, and one edge or boundary case per workstream.
- Add at least one negative criterion — what must NOT happen: `- [ ] Failed auth never creates a session`.
- Ban vague words: fast, intuitive, user-friendly, robust, seamless. Replace each with the measurable behavior — "p95 under 200ms", not "fast".

Reach for this whenever a criterion could pass or fail depending on who reads it — that ambiguity is the defect.

## Goals as outcomes

A goal states the change in the world, not the artifact shipped.

- Outcome: "cut median time-to-first-value from 9 min to under 3". Output: "build the onboarding wizard".
- Each goal answers "how do we know it worked?" with a number or an observable state.
- A goal that gets marked done by merging a PR is a task — move it into a workstream.

Reach for this when a goal restates a workstream title.

## Non-goal rationale

An unexplained non-goal gets relitigated mid-build. Tag each with why it is out:

- **not enough impact** — real but low-leverage
- **too complex for now** — defer past this spec's scope
- **separate initiative** — owned elsewhere
- **premature** — depends on something not yet decided

Reach for this when a non-goal reads like an apology rather than a decision.

## P0 ruthlessness

If everything is P0, nothing is. For each P0 workstream, ask one question: would we genuinely refuse to ship without this?

- If the feature still solves its core problem without the workstream, it is P1, not P0.
- A tight P0 set ships sooner and learns sooner — protect it.
- P2 is architectural insurance: not built now, but the design must not foreclose it.

Reach for this when more than half the workstreams are marked P0.

## Pre-save audit

Walk this checklist before save. The validator catches schema violations (count, Priority/Complexity set, deps resolve, no cycles); the audit catches the softer defects the validator cannot see. Rewrite anything flagged and re-walk the list. Both shapes (Decision and Spec) get the items that apply.

**Decision shape (always):**

- [ ] Decision header complete — chosen approach with rationale, runner-up with what would flip it.
- [ ] Surfaced forks named with the pick, the runner-up, and what would flip it (or "none" if no load-bearing call).
- [ ] Adversarial-critique findings folded — every finding either flipped the leader, was refuted in writing, or filed in Risks / Open questions. No silent drops.
- [ ] Assumption ledger tags each load-bearing claim verified fact / assumption / inherited convention. The shakiest is surfaced as a risk or open question, not buried.

**Spec shape (also):**

- [ ] Every workstream has Priority (P0/P1/P2), Complexity (S/M/L/XL), Description, Tasks, Acceptance criteria.
- [ ] Acceptance criteria use Given/When/Then inside each `- [ ]` item, cover happy + error + edge, include ≥1 negative. No vague words (fast, intuitive, user-friendly, robust, seamless).
- [ ] Goals are outcomes (measurable change in the world), not outputs (artifacts built). A goal markable done by merging a PR is a task — move it into a workstream.
- [ ] P0 set is ruthless. Would the feature still solve its core problem without each P0? If yes, the workstream is P1.
- [ ] Non-goals are tagged with the rationale (not enough impact / too complex for now / separate initiative / premature). An apology-shaped non-goal is a defect.
- [ ] No XL workstream. If one feels XL, split it. XL means the workstream cannot be implemented by a single `/apex` run.
- [ ] Dependencies are explicit and consistent across "Depends on" rows and the dependency graph. Execution order respects the graph.
- [ ] Tasks are concrete enough to implement without guessing. "Implement feature" and "Add functionality" are not tasks.
- [ ] Blocking open questions are flagged and linked to the workstream they block. Non-blocking ones live in the non-blocking split.

Reach for this checklist at the end of writing, before save, every time. The validator runs after — both must pass.
