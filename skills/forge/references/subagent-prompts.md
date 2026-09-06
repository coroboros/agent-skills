# Subagent prompts

Prompt skeletons for the subagents forge spawns. Read this when launching a subagent and the prompt is not already obvious from the phase context. The skeletons are starting points — adapt the specific instructions to the question, do not paste them verbatim.

## Why prompt shape matters

Subagents start fresh: no parent conversation, no tool results from this skill so far. The only channel is the prompt string. A vague prompt returns a vague summary; a prompt that names what to look for, how to report it, and what *not* to do returns usable findings.

The model already knows how to search a codebase or read docs. The skeleton's job is to **pin the report shape and the constraint**, not to teach search.

When you inject multi-line content — a summary, a findings list, a file excerpt — wrap it in an XML tag (`<brief_and_evidence>
{original brief, constraints, source artifacts and evidence paths}
</brief_and_evidence>

<leading_approach>…</leading_approach>`) so the subagent reads it as data, not as part of your instructions. Short inline values (`{specific_area}`) need no tag.

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

Explore reads the codebase, not the web — the source-quality tagging contract in the next section does not apply here.

## general-purpose — external research (Hunt)

Use for "how do best-in-class solutions approach this", "what are the pitfalls of vendor X", "is this pattern still alive in {ecosystem}".

```
Research approaches for: {specific_question}.

Find:
- current best practices, with the source (docs version or post date, not training-data recall);
- common pitfalls, security or perf considerations, vendor lock-in shape;
- comparative analyses or real-world experience reports where two or more sources can be triangulated.

Report at most 5 findings, ranked by load-bearingness. Mark each finding with its source and the date if available. Where sources diverge, surface the divergence — it is more informative than the convergence.

Source quality. Tag every cited source with exactly one of:
- `primary` — original source (research paper, official docs, vendor spec, government report);
- `secondary` — analysis of primary (review article, news citing a primary source);
- `blog` — independent post or opinion piece;
- `anecdote` — single-person experience report (forum reply, single tweet);
- `vendor-marketing` — content pitched by the company selling the thing.

Skip: generic best practices the question did not ask about, training-data recall without a current source, single-source claims dressed up as consensus.
```

## general-purpose — adversarial panel lens (Judge, Round 1)

Used by the panel in Phase 2. Launch one critic per lens in a single parallel message — each a clean context that did NOT produce the leader, so the critique is not auto-justification. Fill `{lens_instruction}` from the roster below; everything else is identical across critics.

```
You are an adversarial reviewer. Read the original brief, constraints, and source evidence supplied below.
You have not seen the author's deliberation. Critique it through
ONE lens only — do not range across the others.

<brief_and_evidence>
{original brief, constraints, source artifacts and evidence paths}
</brief_and_evidence>

<leading_approach>
{one-paragraph summary}
</leading_approach>

<runner_up>
{one-paragraph summary}
</runner_up>

<premortem_failures>
{bulleted list}
</premortem_failures>

Your lens: {lens_instruction}

Be specific. Generic "this is complex" or "consider trade-offs" is not a critique. Cite the component, the assumption, the alternative — by name.

Return substantiated findings under your lens, ranked by consequence; zero findings is valid. For each, one sentence on the issue and one sentence on what the leader's authors should reconsider.
```

Lens roster — choose those relevant to unresolved risks:

- **overengineering / simplicity** — Where is the overengineering? Name the component or step removable without losing the core outcome. Is the simplest answer to NOT build this?
- **load-bearing-assumption audit** — What load-bearing assumption is unquestioned? Look at the leader's premise, not its mechanics.
- **do-nothing / defer** — Argue the case for doing nothing or doing it later, at full strength, never as a strawman.
- **runner-up's hidden win** — Where does the runner-up beat the leader on a dimension the leader's framing hides?
- **premortem gaps** — What failure modes are missing from the premortem list?

## general-purpose — convergence skeptic (Judge, Round 2)

One per surviving finding. Give the skeptic the original brief, relevant constraints, source artifacts and evidence paths, plus its assigned finding and rebuttal. Omit the panel's other findings and the author's deliberation.

```
A panel surfaced this finding against the leading approach, and the
plan's author rebutted it. Read the original brief and inspect the relevant source artifacts before judging whether the rebuttal holds. Treat both claims as unverified until checked against that evidence.

<brief_and_evidence>
{original brief, constraints, source artifacts and evidence paths}
</brief_and_evidence>

<finding>
{one finding}
</finding>

<rebuttal>
{the author's rebuttal}
</rebuttal>

Verdict — one of:
- KILL: the rebuttal holds; the finding is materially wrong. Refute it in one sentence citing the rebuttal's evidence.
- CONFIRM: the finding stands; the rebuttal does not nullify it. Say in one sentence whether it flips the leader, or belongs in Risks / Open questions.

If evidence is insufficient, return UNRESOLVED and name the missing evidence. Generic agreement is not a verdict.
```

## Anti-patterns

- Pasting the skeleton without filling in `{specific_area}` or `{specific_question}` — the subagent has no context to scope itself.
- Asking the subagent to "decide" or "recommend" — subagents return findings, the main context decides.
- Assigning one critic two lenses, or two critics the same lens — the panel's value is one distinct angle per clean context.
- Running a convergence skeptic with the panel's full output instead of just its one finding — that leaks the cross-finding context the round exists to keep out.
- Launching agents sequentially when their queries are independent — parallel is the whole point.
