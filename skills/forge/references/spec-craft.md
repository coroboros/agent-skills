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
