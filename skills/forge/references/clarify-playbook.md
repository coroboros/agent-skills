# Clarify playbook

On-demand template for Hunt's Clarify step. Read this when `{auto_mode}` is false and the framing has gaps that could flip the outcome. Skip on every other run — clarification asked when the answer is already obvious is friction the user resents.

## When to ask, when not to

Ask only when at least one of these holds:

- scope is unclear and the size of the answer changes (MVP vs full build);
- a hard constraint is unknown and would foreclose options (deadline, stack lock-in, regulatory);
- success criteria are missing and "done" cannot be defined;
- a load-bearing dependency is undeclared.

Otherwise: make the reasonable assumption, tag it `assumption` in the ledger, surface the shakiest as an open question. A recorded assumption the user can veto beats an open question that stalls.

Under `{auto_mode}` = true, decide reversible details within existing authorization. User-owned decisions and missing authorization still require explicit input; silence supplies neither. Continue independent work while waiting.

## The five lenses

Pick the **1-3 most relevant** — not all five. Ask them in a **single message**, numbered, and **no follow-up rounds**. One Q&A, then proceed.

1. **Scope** — what is the minimum viable version, and what is explicitly out of scope? Use this when the idea spans build-it-all vs build-the-core, or when "and X and Y and Z" piled up.
2. **Users** — who uses this, and what is their primary workflow? Use this when the user experience drives the shape (e.g. self-serve vs admin-driven, mobile-first vs desktop).
3. **Constraints** — hard constraints? Timeline, tech stack, compatibility, third-party services, budget ceiling, regulatory. Use this when the stack or deadline could flip the chosen approach.
4. **Success criteria** — how will you know this is done? What numbers or observable states define success? Use this when the goal phrasing risks an output ("ship the wizard") rather than an outcome ("cut TTFV from 9 min to 3").
5. **Dependencies** — does this depend on or block anything else in progress? Use this when other work is in flight and the order matters.

## Prior context attenuates

If `{from_file}` carried a brainstorm, an RFC, a GitHub issue, or a prior forge artifact, ask only about **gaps** — what the prior doc does not answer. One or two questions, not five. The carry-forward Assumption ledger usually settles Scope and Constraints already.

## Deep grill (opt-in)

The default above is deliberately light — 1-3 questions, one message, no second round. Escalate to a relentless grill **only** when the user signals it ("grill me", "interview me", "I want to think this through") or an irreversible, high-cost decision warrants resolving every branch before committing.

The deep grill inverts the default rhythm:

- **One question at a time.** Ask, read the answer, ask the next — walk the decision tree branch by branch instead of batching.
- **Carry a recommended answer with each question.** State the call you would make and why, so the user confirms fast or redirects. A grill that only asks is slower than one that proposes.
- **Follow each fork before backtracking.** When an answer opens a new branch, resolve it in order. Stop when every branch is closed, not at a fixed count.
- **Read the code, not the user, when the answer is discoverable.** A question the codebase already answers gets explored, not asked.

The deep grill is the exception, never the default. Without an explicit signal, stay light.

## Anti-patterns

- Asking five questions when one matters.
- Asking before reading prior context.
- Multiple Q&A rounds — the user spent the budget for thinking on answering procedural questions. The opt-in deep grill above is the deliberate exception, gated by an explicit user signal.
- Asking yes/no questions disguised as open-ended — "should we use OAuth?" should be a decided call surfaced as an assumption, not a question.
- Asking what the model can decide — taste calls, library picks, file layout, naming. Those are the engineering judgment calls Phase 3 owns.
