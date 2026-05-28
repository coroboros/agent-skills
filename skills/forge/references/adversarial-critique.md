# Adversarial critique

Methodology for the fresh-eyes step that runs after Stress-test in Phase 2 (Judge). The prompt skeleton lives in `subagent-prompts.md`; this file covers when to run, when to skip, and how to integrate findings.

Anthropic documents the underlying pattern as `adversarial-review` in *Lessons from Building Claude Code: How We Use Skills* — a fresh-eyes subagent that critiques, iterates, and degrades findings to nitpicks. Forge's version runs once per artifact rather than to convergence, because forge produces a plan, not code.

## Why fresh-eyes

Premortem and steelman in Stress-test are run by the same context that produced the leader. The model that just argued for an approach is structurally biased toward justifying it — "look how thoroughly I considered the alternatives". A subagent that did NOT see the deliberation cannot auto-justify. That is the point.

The fresh-eyes critic gets:

- the leader (one paragraph),
- the runner-up (one paragraph),
- the premortem failures already listed (bulleted).

Nothing else. Not the framing, not the research, not the deliberation. The clean context is what makes the critique informative.

## When to run

ON by default, after Stress-test, before Decide.

The critic answers five questions: where is the overengineering, what unquestioned assumption did the leader inherit, is the simplest answer to NOT build this, what did the premortem miss, where does the runner-up beat the leader on a hidden dimension.

## When to skip

Skip if any of these holds:

- `{economy_mode}` = true (explicit user opt-out for token / latency reasons);
- the Judge phase converged on a leader with a wide gap over the runner-up AND no load-bearing assumption is tagged `assumption` or `inherited convention` — the critique has nothing to bite on;
- the question is pure-strategy and the Decision already names a single dominant option (e.g. "use the same database the rest of the org uses").

When skipped, note the skip in the artifact's Assumption ledger as a one-liner: `[assumption] adversarial critique skipped because <reason>`. The user can challenge the skip.

## How to integrate findings

The critic returns 3-7 findings, ranked by severity. Each finding is one sentence on the issue + one sentence on what the leader's authors should reconsider.

For each finding, do one of three things:

- **Fold into the Decision header.** If the finding flips the leader, change the chosen approach. If it sharpens the runner-up's flip condition, update the "what would flip it" line.
- **Refute with a one-line rationale.** If the finding does not flip the leader, write the rationale in the Decision section — record that the critique surfaced it and why it was rejected. Do not silently drop a finding.
- **Surface in Risks or Open questions.** If the finding identifies a real concern that does not flip the leader but should not be lost, file it in Risks (with mitigation) or Open questions (blocking vs non-blocking per the existing split).

Unaddressed findings are a defect. Either the critique was wrong (record the refutation) or the artifact is wrong (revise the leader).

## Anti-patterns

- Letting the critic decide. Critics surface findings; the main context decides.
- Asking the critic for a recommendation. The recommendation is the leader; the critic's job is the case against it.
- Running the critic with the full deliberation history. That recreates the auto-justification bias the fresh-eyes step exists to avoid.
- Silently dropping findings that don't fit the artifact. Every finding either flips the plan, is refuted in writing, or is filed in Risks / Open questions.
- Running the critic on every invocation when Judge has already converged. Burning tokens to confirm a settled call is the kind of waste a thinking skill should not introduce.

## Why runtime invocation, not a wired agent file

Claude Code supports filesystem-based subagents under `.claude/agents/` (project), `~/.claude/agents/` (user), and the plugin `agents/` directory. The critic could live as one of those — a static system prompt with `tools: Read, Grep, Glob` and `model: opus`, invocable as `@fresh-eyes-critic`. Forge does not take that path. Two reasons:

- **Install-path portability.** The repo ships skills two ways: the `npx skills add` installer (skills-only, no agents) and the Claude Code plugin marketplace (skills + plugin agents). Wiring the critic as a plugin agent file would silently make the critic absent for `npx skills add` users and present for plugin users — a feature drift the user cannot see until invocation.
- **Runtime data has nowhere to live in a static system prompt.** The critic needs the leader summary, the runner-up summary, and the premortem failures *for this specific invocation*. Those have to pass through the Agent tool's prompt parameter regardless of whether the agent is wired or built-in. A wired file would only carry boilerplate ("you are an adversarial reviewer"); the load-bearing content still travels at runtime through the skeleton in `subagent-prompts.md`. The wired file would add discovery and tool restriction without adding specialization.

Future authors who want tool restriction on the critic can add an `agents/fresh-eyes-critic.md` at the plugin root and have Phase 2 invoke it by name, falling back to `general-purpose` + skeleton when unavailable. That hybrid is a deliberate enhancement, not the default — and it carries the install-path-drift cost that this note exists to make visible.
