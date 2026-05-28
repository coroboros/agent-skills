# Subagent prompts

Prompt skeletons for the subagents forge spawns. Read this when launching a subagent and the prompt is not already obvious from the phase context. The skeletons are starting points — adapt the specific instructions to the question, do not paste them verbatim.

## Why prompt shape matters

Subagents start fresh: no parent conversation, no tool results from this skill so far. The only channel is the prompt string. A vague prompt returns a vague summary; a prompt that names what to look for, how to report it, and what *not* to do returns usable findings.

The model already knows how to search a codebase or read docs. The skeleton's job is to **pin the report shape and the constraint**, not to teach search.

## Explore — codebase reconnaissance (Hunt)

Read-only, fast, context-isolated. Use for "what exists in this repo that touches {X}", "what convention is in use", "what prior decision is recorded in git history".

```
Find existing code related to: {specific_area}.

Report:
1. Files with paths and line numbers for the matches you consider load-bearing.
2. Patterns in use (routing, data fetching, validation, error handling, etc.) — name them, do not just paste code.
3. Relevant utilities and shared code that anything new would compose with.
4. Architecture and conventions worth respecting, with the file or commit that establishes them.
5. Any contradictions between files — flag rather than smooth over.

Do not suggest implementations. Do not propose a design. Findings only.
```

## general-purpose — external research (Hunt)

Use for "how do best-in-class solutions approach this", "what are the pitfalls of vendor X", "is this pattern still alive in {ecosystem}".

```
Research approaches for: {specific_question}.

Find:
- current best practices, with the source (docs version or post date, not training-data recall);
- common pitfalls, security or perf considerations, vendor lock-in shape;
- comparative analyses or real-world experience reports where two or more sources can be triangulated.

Report at most 5 findings, ranked by load-bearingness. Mark each finding with its source and the date if available. Where sources diverge, surface the divergence — it is more informative than the convergence.

Skip: generic best practices the question did not ask about, training-data recall without a current source, single-source claims dressed up as consensus.
```

## general-purpose — fresh-eyes adversarial critic (Judge)

Used by the Adversarial step in Phase 2. The point is a clean context that did NOT produce the leader, so the critique is not auto-justification.

```
You are an adversarial reviewer. You have not seen the research or
deliberation that led to the leading approach. Your job is to find
the overengineering, the unquestioned assumption, and the simpler
path that was overlooked.

The leading approach: {one-paragraph summary}.
The runner-up: {one-paragraph summary}.
The premortem failures already listed: {bulleted list}.

Critique:
1. Where is the overengineering? Name the component or step that could be removed without losing the core outcome.
2. What load-bearing assumption is unquestioned? Look at the leader's premise, not its mechanics.
3. Is the simplest answer to NOT build this? Argue the case for doing nothing or doing it later — at full strength, not as a strawman.
4. What did the premortem miss? Name failure modes that are not on the list.
5. Where does the runner-up beat the leader on a dimension the leader's framing hides?

Be specific. Generic "this is complex" or "consider trade-offs" is not a critique. Cite the component, the assumption, the alternative — by name.

Return: 3-7 findings, ranked by severity. For each, one sentence on the issue and one sentence on what the leader's authors should reconsider.
```

## Anti-patterns

- Pasting the skeleton without filling in `{specific_area}` or `{specific_question}` — the subagent has no context to scope itself.
- Asking the subagent to "decide" or "recommend" — subagents return findings, the main context decides.
- Launching a subagent on a question already answered by framing — exploration is cheap, but a subagent on a settled question burns budget for no gain.
- Launching agents sequentially when their queries are independent — parallel is the whole point.
