# Adversarial panel + convergence

Methodology for the adversarial step that runs after Stress-test in Phase 2 (Judge). The prompt skeletons live in `subagent-prompts.md`; this file covers the panel roster, the dedup-and-score barrier, the bounded convergence loop, when to skip, and how to integrate findings.

Forge runs a perspective-diverse panel in one parallel round, then converges on the survivors — bounded to ≤2 rounds because forge produces a plan, not code.

## Why a panel, not one critic

Premortem and steelman in Stress-test are run by the same context that produced the leader. The model that just argued for an approach is structurally biased toward justifying it — "look how thoroughly I considered the alternatives". A subagent that did NOT see the deliberation cannot auto-justify. That is the point.

One critic carries one blind spot. A panel where each critic holds a single distinct lens catches failure modes redundancy cannot — the overengineering hunter and the assumption auditor surface different defects, and neither is the do-nothing advocate. Each critic gets the leader (one paragraph), the runner-up (one paragraph), and the premortem failures (bulleted) — nothing else. Not the framing, not the research, not the deliberation. The clean context is what makes the critique informative.

## Round 1 — the panel

ON by default, after Stress-test, before Decide. Launch the critics in one parallel message — one `general-purpose` per lens, each clean-context. If your harness has no subagents, run each critic lens yourself sequentially in fresh passes — one lens at a time, nothing carried over between them.

Lenses, in priority order:

1. **Overengineering / simplicity** — name the component or step removable without losing the core outcome; is the simplest answer to NOT build this?
2. **Load-bearing-assumption audit** — the leader's premise, not its mechanics; what unquestioned assumption is it inheriting?
3. **Do-nothing / defer** — argue at full strength for doing nothing or doing it later, never as a strawman.
4. **Runner-up's hidden win** — where does the runner-up beat the leader on a dimension the leader's framing hides?
5. **Premortem gaps** — failure modes not already on the premortem list.

Scale the lens count to stakes: 3 lenses for a focused call (overengineering, assumption audit, do-nothing), 5 for an architecture-level one. Each critic returns 3-7 findings, ranked by severity — one sentence on the issue, one on what to reconsider.

## Barrier — dedup and score

Merge every panel finding. Dedup by target — two lenses naming the same component collapse to one finding carrying both angles. Then score each rebuttal against each finding on the 1–5 Concession Threshold below.

A finding conceded at ≥4 is closed. Every other finding survives into convergence.

## Round 2 — convergence

Launch one fresh skeptic per surviving finding. Each gets the single finding plus the orchestrator's rebuttal and its score, and returns a verdict: **kill** (the rebuttal holds — refute in writing) or **confirm** (the finding stands — escalate it to a flip condition, a risk, or an open question).

Stop when the survivors degrade to nitpicks, or after 2 rounds total — whichever comes first. Forge emits a bounded plan; an unbounded refute loop is the waste a thinking skill must not introduce.

## When to skip

Skip only under `{economy_mode}` = true — the user opted out for token / latency reasons. There is no "Judge already converged" skip: a wide-gap leader is exactly where an unexamined assumption hides, and forge is invoked deliberately for thinking, not triage. When skipped, note it in the Assumption ledger as a one-liner: `[assumption] adversarial panel skipped because economy mode`. The user can challenge the skip.

## How to integrate findings

For each finding that survives convergence as confirmed, do one of three things:

- **Fold into the Decision header.** If the finding flips the leader, change the chosen approach. If it sharpens the runner-up's flip condition, update the "what would flip it" line.
- **Refute with a one-line rationale.** If the rebuttal scored ≥4 and the convergence skeptic killed it, record in the Decision section that the panel surfaced it and why it was rejected. Do not silently drop a finding.
- **Surface in Risks or Open questions.** If the finding identifies a real concern that does not flip the leader but should not be lost, file it in Risks (with mitigation) or Open questions (blocking vs non-blocking).

Unaddressed findings are a defect. Either the critique was wrong (record the refutation) or the artifact is wrong (revise the leader).

## Concession Threshold Protocol

Refuting a finding has a quality bar. The protocol applies on the **consumer side** — the forge orchestrator scoring its own rebuttal — and again on the convergence skeptic, which scores whether the rebuttal holds.

For each finding, score the rebuttal against it on this 1–5 rubric:

- **1** — does not address the finding (changes the subject, restates the leader's case).
- **2** — tangential (addresses an adjacent concern, not the cited one).
- **3** — partial (addresses the finding but leaves the core objection live).
- **4** — substantive refutation with evidence (the finding is materially wrong, and the evidence is in the artifact in writing).
- **5** — full refutation that nullifies the finding (the premise is false; a cited fact contradicts the finding directly).

Concession — treating the finding as refuted, dropping it without filing — is allowed only at score ≥ 4. Below 4: fold the finding into the Decision (revise the leader) or file in Risks / Open questions (preserve the concern). Silently dropping a finding scored ≤ 3 is a defect.

**Frame-lock detection.** If three consecutive findings are rebutted at score ≤ 2, flag for re-examination. The leader may be in motivated rationalization, or the critic context may be wrong. Re-examine = re-read the findings cold, re-score, and decide whether the artifact needs revision or whether the critic was off-target. Record either outcome — never let the rebuttal chain stand without scrutiny.

## Anti-patterns

- Letting a critic decide. Critics surface findings; the main context decides.
- Asking a critic for a recommendation. The recommendation is the leader; each critic's job is the case against it.
- Running a critic with the full deliberation history. That recreates the auto-justification bias the clean-context step exists to avoid.
- Running the panel sequentially. One parallel message is the whole point — sequential defeats it. (Harnesses without subagents excepted — there, sequential fresh passes are the fallback.)
- Exceeding 2 convergence rounds. The bound is the difference between a plan and an unbounded refute loop.
- Silently dropping findings that don't fit the artifact. Every finding flips the plan, is refuted in writing, or is filed in Risks / Open questions.

## Why runtime invocation, not wired agent files

Claude Code supports filesystem-based subagents under `.claude/agents/` (project), `~/.claude/agents/` (user), and the plugin `agents/` directory. The panel critics could live as those — static system prompts with `tools: Read, Grep, Glob` and `model: opus`, invocable by name. Forge does not take that path. Two reasons:

- **Install-path portability.** The repo ships skills two ways: the `npx skills add` installer (skills-only, no agents) and the Claude Code plugin marketplace (skills + plugin agents). Wiring critics as plugin agent files would silently make the panel absent for `npx skills add` users and present for plugin users — a feature drift the user cannot see until invocation. This is also why the panel uses Agent/Task subagents rather than the Workflow tool, which a standalone install may not carry.
- **Runtime data has nowhere to live in a static system prompt.** Each critic needs the leader summary, the runner-up summary, and the premortem failures *for this specific invocation*. Those pass through the Agent tool's prompt parameter regardless. A wired file would carry only boilerplate ("you are the overengineering lens"); the load-bearing content still travels at runtime through the skeleton in `subagent-prompts.md`.

Future authors who want tool restriction on the panel can add `agents/forge-critic-*.md` at the plugin root and have Phase 2 invoke them by name, falling back to `general-purpose` + skeleton when unavailable. That hybrid is a deliberate enhancement, not the default — and it carries the install-path-drift cost this note exists to make visible.
