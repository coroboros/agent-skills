# Subagent orchestration patterns

Choose a pattern for dependencies and available tools. Inherit the user's model selection; a model-tier table is not evidence of the best allocation. Schedule work within the active host's concurrency, nesting and permission limits.

## Sequential dependencies

When analysis determines the implementation, pass its evidence to the implementer before dependent edits. A security review can proceed after the relevant artifact exists. Do independent local work while waiting; do not fabricate a downstream input.

## Independent parallel work

Split work only when each delegate has a concrete deliverable that can proceed independently. Assign disjoint file ownership where possible. Each brief carries the accepted scope, relevant inputs, user corrections and acceptance checks. Avoid simultaneous edits to shared files.

The lead continues integration, investigation or verification while delegates run. A routing-only coordinator is appropriate only when that role was explicitly chosen, not as a universal restriction.

## Hierarchy and fallback

Use nesting only when the actual tool schema and depth permit it. Current Claude Code supports bounded nesting; other hosts may expose different semantics. Omit `tools` to inherit in a Claude definition instead of writing the undocumented `tools: all`.

Without independent agents, inspect the result against the acceptance criteria and report reduced review independence. Sequential self-criticism is not fresh-context verification.

## Evidence and convergence

Give reviewers the accepted brief, actual artifact and supporting evidence. Ask them to find a counterexample; allow zero findings. Resolve disagreements by reproduction, source contracts and impact, never by a majority vote or the author's confidence score.

After a demonstrated defect is repaired, rerun the affected checks. Preserve pre-existing user changes and distinguish unrelated baseline failures. Close all accepted outcomes against the final integrated result.
