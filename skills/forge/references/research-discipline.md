# Research discipline

On-demand depth for the Hunt phase. Read this when launching subagents or pulling external evidence — not on every run. The point is breadth across angles + triangulation, not the first plausible source.

## Three angles to cover

Most non-trivial questions need at least two of these. Skip an angle only when it cannot apply (no codebase yet, no external precedent worth fetching).

- **Codebase context** — patterns, architecture, conventions, prior decisions. `git log` for *why* something is shaped the way it is. Read the immediate callers of anything you are about to extend, not just the symbol itself.
- **Technical best practices** — how best-in-class solutions approach the problem; common pitfalls; security, performance, data-integrity considerations. Pull from current docs (Context7, official sources), not training-data recall.
- **External evidence** — comparative analyses, real-world experience reports (post-mortems, RFC comment threads), and docs for unfamiliar technologies. Most useful when the call is "vendor X vs Y" or "is this pattern still alive".

## Triangulate, don't cherry-pick

Judge evidence by authority, directness, methodology, and independence. An official specification can establish its own contract alone; several reposts are not independent corroboration.

- Cite the evidence supporting each material claim. Seek independent corroboration for comparative or empirical claims; disclose uncertainty when corroboration is unavailable.
- Where sources diverge, record the divergence in the Assumption ledger. The divergence is more informative than the convergence.
- Newer trumps older when methodology is comparable. Methodology trumps recency when not.

## Source quality, not just count

Three converging sources only count when at least one is `primary` or `secondary`. Each cited source carries a quality tag (`primary` / `secondary` / `blog` / `anecdote` / `vendor-marketing`) per `subagent-prompts.md` § *general-purpose — external research*. Weight convergence by tag — three `primary` sources outweigh a chain of `blog` reposts of the same claim. A consensus across `blog` and `vendor-marketing` tags alone is not a consensus; it is a single source amplified.

## Provenance and lateral reading

A quality tag rates the source type; provenance rates its interest. For each load-bearing source, surface who funds, owns, or publishes it as a neutral fact — funding shapes framing more than tone reveals, and it is where political, vendor, and consortium influence hides.

- Read laterally. Judge a source by what independent sources say about it, not by reading it harder. Leave the page, check the publisher and its backers — fact-checkers who do this beat experts who deep-read the source itself.
- State the affiliation, don't adjudicate the bias. "Funded by X" lets the reader discount; "X is biased" injects your own priors and defeats the point.
- When provenance is unknown, record "provenance unverified" — never assume neutral.

## What to leave to the model

Premortem framing, generic best practices, common gotchas for well-known libraries — the model already carries these. Use research to ground the *specific* call: this codebase, this version, this constraint.

Choose research angles according to the actual unresolved questions. Do not manufacture codebase research for a non-code decision or external research for a question fully settled by repository evidence.

## When to widen the net

- Two angles converged but the answer feels too clean → add the third angle.
- The premortem in Phase 2 surfaces a failure mode no source mentioned → launch one more research agent before Decide. This second round is automatic, not optional.
- A load-bearing assumption is tagged `inherited convention` and you cannot find its origin → that is a research question worth one more subagent.

## When to stop

- Marginal new search returns marginal new information.
- The remaining uncertainty is product or business, not technical — that belongs in the escalated forks, not in more research.
- You have enough to decide *and* to record what would flip the decision.
