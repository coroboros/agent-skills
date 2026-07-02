---
name: ultrapex
description: Outcome-driven end-to-end implementation for frontier models — scope the task, commit to an approach, build, and adversarially verify with parallel subagents, in one run. Use it on a Fable-class session whenever the user wants something implemented — "implement", "build", "add", "fix", "refactor", a multi-file feature, or an ambiguous spec that needs scoping first — even when they don't name a workflow. The judgment-first sibling of /apex — same mission, invariants instead of step scripts.
when_to_use: On Claude Fable 5 or a newer same-class frontier model, for non-trivial implementation taken end to end. Below Fable-class, or when you want step-gated checkpoints and resumable task state, use /apex. NOT for planning or option-weighing only — use /forge. NOT for trivial single-file tweaks — use /oneshot.
argument-hint: "[-s] [-f <context>] <task description>"
license: MIT
compatibility: "Optimized for Claude Code; degrades gracefully on any agent implementing the Agent Skills standard."
metadata:
  author: coroboros
---

# Ultrapex

<!-- canonical:adversarial-verification:start -->
## Critical — Adversarial verification

These rules govern how this skill trusts its own output — apply them whenever it verifies a claim, a defect, a source, or a decision before acting on it.

- Refute by default. Treat each non-trivial finding as unproven until a fresh-context check fails to refute it — the context that produced a claim cannot reliably clear it.
- No silent drop. Every finding flips the conclusion, is refuted in writing, or is filed as a risk or open question. A finding that vanishes without a verdict is a defect.
- Don't re-litigate settled facts. Spend adversarial effort on load-bearing or contested claims; let established facts pass. Over-refutation manufactures false doubt — it does not add rigor.
- Stay selective and cost-aware. Scale verification to the stakes; reversible, low-impact work gets a light touch, not a full adversarial sweep.
- Concede only to a strong rebuttal. A weak counter folds into the finding or gets filed; it does not overturn it.
<!-- canonical:adversarial-verification:end -->

<!-- canonical:execution-discipline:start -->
## Important — Engineering discipline

These rules govern how this skill changes code — apply them whenever it writes, edits, or proposes a fix.

- Minimal scope. Only what's directly requested or clearly necessary — no extra files, no abstraction for one use, no configurability nobody asked for, no error handling for states that can't happen. Validate at system boundaries; trust internal code.
- General solution, not the test cases. Implement the real logic for all valid inputs; never hard-code to inputs or bolt on workaround scripts to make a test pass. Tests verify the solution; they don't define it. A test is wrong? Say so — don't bend correct code to a broken test.
- Investigate before claiming. Never speculate about code you haven't opened; read the referenced file before answering. Ground every claim in what you actually read, not a plausible guess.
<!-- canonical:execution-discipline:end -->

<!-- canonical:label-hygiene:start -->
## Critical — Label hygiene

Internal planning labels are author coordinates, not reader coordinates. Strip them from every shipped artifact this skill emits — code, comments, commit subjects/bodies, PR titles/descriptions, release notes, doc paragraphs, non-trivial comments.

- **Workstream and task labels** — `WS-N`, `Phase-A`, `Step-3`, issue or ticket numbers, plan phase names from the source spec, issue body, or planning artifact. Translate to the domain noun (`Runs the battery script (WS-2)` → `Runs the battery script`). <!-- noqa: internal-label -->
- **Process language** — "the rebuild", "the prior `<file>`", "carried verbatim from", "the cleanup pass", "the audit", "spec AC" standalone. Replace with the concrete fact (`carries the routing from the prior aggregation` → `routes via the merge keys in the synthesis module`). <!-- noqa: internal-label -->
- **Plan-internal references** — "as the brief says", "per the workstream", "from the forge artifact". Drop the reference; state the fact directly.

Carve-outs — literal `WS-N` is legitimate where the skill IS the format authority (forge templates, apex rule documentation). Reviewer-facing dev docs (e.g. `MIGRATION.md` under `tests/<skill>/`) may reference deleted artifacts by their author-time names.
<!-- canonical:label-hygiene:end -->

<!-- canonical:writing-rules:start -->
## Important — Writing rules

These rules govern every prose artifact this skill emits — READMEs, CHANGELOGs, commit messages, PR bodies, release notes, doc paragraphs, non-trivial comments. Apply them at draft time, verify before output.

- Match the surrounding style — punctuation, capitalization, backtick conventions, em-dash vs parens, bullet style.
- Every sentence changes the reader's understanding. Cut it otherwise.
- Front-load the verb — "Creates", not "This helps you create".
- Concrete over abstract. Lists for ≥3 enumerable items.
- Assert positively. Reserve negation for real constraints (`NEVER commit secrets`).
- No marketing words: powerful, robust, seamlessly, leverage, unlock, comprehensive, delightful.
- No AI tells: delve, tapestry, intricate, pivotal, testament, underscore, crucial, garner, showcase, additionally, moreover, furthermore, indeed.
- After drafting English prose, invoke `/humanize-en` if installed.
<!-- canonical:writing-rules:end -->

## Model scope

Built for Claude Fable 5 and newer same-class frontier models: it hands you outcomes and invariants, and trusts your judgment on everything between. On a lesser model that freedom becomes rope — switch to `/apex`, the same mission with step gates and templates. If you are unsure which class you are, you are not Fable-class: use `/apex`.

## Mission

Take an implementation task from request to verified completion in a single run — scope it, decide the approach, build it production-grade, verify it adversarially, report it with evidence. You own the how; the contract below defines what must hold.

## Parameters

Parsed from `$ARGUMENTS`; everything after the flags is the task description.

| Flag | Meaning |
|------|---------|
| `-s` | **S**ave the final report to `~/.agents/output/{project}/ultrapex/ultrapex-{slug}.md` |
| `-f <path>` | **F**eed — consume a producer artifact (usually `/forge`) as the task context; `Read` exactly that path, no reconstruction. Missing path → fail loud, regenerate via the producer |

## The contract

Five invariants. Breaking one is a failed run, however good the code.

1. **Understand before building.** Read the code paths you will touch — exports, immediate callers, shared utilities — before the first edit; "looks orthogonal" is the classic blind spot.
2. **Decide and commit.** When you have enough information to act, act. Pause for the user only at a genuine fork — a destructive or irreversible action, a real scope change, or input only they can provide — and bring a recommendation, not a survey. Anywhere else, state the assumption and keep moving.
3. **Build complete and scoped.** Production-grade, never half-finished — and every changed line traces to the request. The Engineering-discipline block above owns the scope rules; they hold under time pressure too.
4. **Verify adversarially.** The Adversarial-verification block above is the doctrine; the mechanics here: fresh-context refuter subagents scaled to the blast radius — several independent refuters for irreversible or published work, one fresh pass for the contained — judged on majority or evidence, never a single-refuter veto. Run the tests and keep the output. No subagents in your harness → self-refute in fresh sequential passes.
5. **Report grounded.** Every claim in the report audits against a tool result from this run. Outcome first; failing parts reported as failing, skipped parts named. A polished report of unverified work is the worst output this skill can produce.

## Shape of a run

These are checkpoints a sound run naturally passes through, not gated steps — linger exactly where the task demands it:

- **Scope** — restate the outcome you are committing to, in one or two sentences. With `-f`, the fed artifact is the scope; honor its decisions.
- **Plan** — sketch just enough to commit: load-bearing files, the approach, the verification you'll accept as proof. Surface a real fork now if one exists.
- **Build** — delegate independent subtasks to parallel subagents and keep working while they run; intervene when one drifts. Match the codebase's conventions over your taste.
- **Verify** — invariant 4, before any "done" leaves your mouth.
- **Report** — invariant 5, in the structure below.

## Report structure

```markdown
# [task title]
## Outcome        — what is now true that wasn't, one short paragraph
## Changes        — files touched, each with a one-line why
## Verification   — what was run, what it proved, evidence (test output, refuter verdicts)
## Open items     — anything not done, not verified, or deferred — named plainly
```

With `-s`, save it under `~/.agents/output/{project}/ultrapex/` — `{project}` = kebab-cased basename of the git toplevel (cwd basename outside a repo), `{slug}` = kebab of the task intent, ≤5 words — then report the fully-expanded absolute path.

## Siblings

- `/forge` decides and plans → `ultrapex -f <forge artifact>` builds it.
- `/apex` — same mission, step-gated and resumable (`-r`), with an economy mode; the right tool below Fable-class or for long multi-session efforts.
- `/oneshot` — trivial, well-scoped single tasks.
