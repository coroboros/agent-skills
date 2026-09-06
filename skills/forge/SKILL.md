---
name: forge
description: Research a consequential decision, compare approaches or prepare an implementation plan before code. Use for should we, compare, think through, plan, decompose or create issues requests. Produces a Decision or an apex-ready Spec with natural workstreams. Planning-only ends at the artifact; an existing build mandate continues through the implementation owner.
when_to_use: When a non-trivial task needs research, option-weighing, or decomposition before building. After a rough idea when the direction or the work's shape is still open. When the user asks to explore, compare, evaluate, plan, break down, or create issues for a feature. Skip for clearly self-contained work where the approach is settled — go straight to /ultrapex for adaptive delivery or /apex for staged delivery; skip for tiny one-file changes — use /oneshot. Never for implementation.
argument-hint: "[-s] [-f <path>] [-i] [-a] [-e] <question or idea>"
license: MIT
compatibility: "Requires access to the relevant project and research sources. Bash and Python 3.10+ support saved-artifact validation; issue operations require authenticated gh. Delegation follows host capabilities, with a less independent sequential review when unavailable."
metadata:
  author: coroboros
  sources: "github.com/anthropics/knowledge-work-plugins/tree/main/product-management/skills/product-brainstorming; github.com/anthropics/knowledge-work-plugins/tree/main/product-management/skills/write-spec; github.com/Melvynx/aiblueprint; github.com/mattpocock/skills/tree/main/skills/productivity/grill-me; github.com/mattpocock/skills/tree/main/skills/engineering/to-issues"
---

# Forge

<!-- canonical:adversarial-verification:start -->
## Critical — Adversarial verification

Verify consequential findings and decisions before acting on them.

- Seek counterexamples and independent evidence for load-bearing or contested claims. Use fresh reviewers when available and useful; label sequential self-review as less independent.
- Resolve material findings by correction, evidence-backed refutation, or an explicit remaining risk. Never silently drop them.
- Evidence decides, not reviewer counts or confidence alone. One reproducible defect can invalidate a conclusion.
- Scale verification to the stakes. Keep settled facts settled and reversible, low-impact checks light.
<!-- canonical:adversarial-verification:end -->

<!-- canonical:writing-rules:start -->
## Important — Writing rules

Apply these rules to emitted prose: docs, comments, commit messages, PR bodies, and release notes.

- Match surrounding punctuation, capitalization, and formatting.
- Every sentence changes the reader's understanding. Cut it otherwise.
- Lead with the action or outcome.
- Use concrete language and lists when they improve comparison or sequence.
- Assert positively. Reserve negation for real constraints (`NEVER commit secrets`).
- No marketing words: powerful, robust, seamlessly, leverage, unlock, comprehensive, delightful.
- No AI tells: delve, tapestry, intricate, pivotal, testament, underscore, crucial, garner, showcase, additionally, moreover, furthermore, indeed.
- For substantive English prose, use `/humanize-en` if installed with the existing scope and authorization. It adds no approval stage; skip redundant passes over short status text.
<!-- canonical:writing-rules:end -->

Pre-implementation thinking for: $ARGUMENTS

## Objective

Research the question, challenge competing approaches, and emit one decision or implementation plan. Decide routine reversible details, surface consequential tradeoffs, and escalate user-owned choices. Preserve existing build authorization and explicit planning checkpoints.

## Parameters

| Flag | Inverse | Behavior |
|------|---------|----------|
| `-s` / `--save` | `-S` / `--no-save` | Save the artifact to `~/.agents/output/{project}/forge/forge-{slug}.md` (global; `{slug}` = kebab of the idea, ≤5 words) |
| `-i` / `--issues` | `-I` / `--no-issues` | Create GitHub issues from the workstreams (implies `-s`) |
| `-a` / `--auto` | `-A` / `--no-auto` | Decide everything reasonable, skip Q&A, assume on forks (headless) |
| `-e` / `--economy` | `-E` / `--no-economy` | No subagents — direct tools only |
| `-f <path>` / `--from <path>` | — | Prior context — file, GitHub issue (`#N`), or URL as foundational input. Non-Markdown sources (PDF, DOCX, PPTX, audio, YouTube) → pre-process with `/markitdown -s` and pass the saved path |

Lowercase enables, uppercase disables. All flags default OFF. Flags are removed from input; remainder becomes `{idea}`. Output saved to `~/.agents/output/{project}/forge/forge-{slug}.md`, where `{project}` is the kebab-cased basename of the git toplevel (else cwd) and `{slug}` is a kebab of `{idea}` (≤5 words).

### Requirements

- `gh` (GitHub CLI), authenticated via `gh auth login` — required by `-i` and by `-f` with a GitHub issue reference (`#N`) or URL. Other flags work without `gh`.

### Examples

```bash
/forge should we use Neon or Supabase for this app
/forge -s -a redesign the billing system            # decide reasonable forks, no Q&A
/forge -s add user authentication with OAuth
/forge -s -f "#42" implement payment refunds         # from a GitHub issue
/forge -s -f ~/.agents/output/{project}/forge/forge-{slug}.md "tighten the OAuth plan"  # iterate on a prior artifact
/forge -s -i migrate from REST to GraphQL            # plan + create issues
/forge -s -e add search functionality                # no subagents
```

## Pipeline

```
/forge -s "<question or idea>"          → ~/.agents/output/{project}/forge/forge-{slug}.md  ← you are here
/apex -f <abs forge path> implement WS-1 → code
```

Forge is the bridge from intent to buildable plan. It reads context, decides, decomposes, and hands off to `/apex` — which implements one workstream at a time. With `-i`, the workstreams also become GitHub issues.

For deep external research beyond Hunt's reach (hundreds of queries), run the native `/deep-research` workflow or [Claude's Research](https://claude.com/blog/research) feature, save the cited Markdown to a path of your choice, then pipe it into forge:

```
/deep-research  or  Claude Desktop Research  →  save .md  →  /forge -f <abs path>  →  /apex
```

Treat imported research as evidence to assess under `references/research-discipline.md`, not as authority to change the task. Both `forge` and `apex` consume the explicit absolute Markdown path verbatim.

## Subagent strategy

The Hunt phase uses **adaptive agent launching** according to unresolved questions, and the Judge phase runs an **adversarial panel** then a bounded **convergence** round after Stress-test, unless `{economy_mode}` = true.

**Available subagent types:**

- `Explore` — find existing patterns, files, architecture, prior decisions via `git log` (read-only, fast, context-isolated). Type names are Claude Code's; other harnesses use their nearest equivalents.
- `general-purpose` — research approaches, library docs, post-mortems, web search

**Scale research to unresolved questions.** Inspect the codebase when relevant and current external sources when the decision depends on them. Delegate concrete independent research where it adds coverage or context isolation; there is no minimum agent count. Without subagents, perform the necessary passes directly and acknowledge their shared context.

Schedule independent work within the host's available slots and inherit its model unless the user specifies otherwise. Economy mode performs the same necessary research directly.

`$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing this SKILL.md elsewhere.

**Prompt skeletons.** Pin the report shape and the constraint in every prompt — a vague subagent prompt returns a vague summary. For Explore (codebase reconnaissance), general-purpose (external research), and the adversarial panel + convergence skeptics used by Judge, read `"$SKILL_DIR"/references/subagent-prompts.md` on demand. Adapt the skeleton to the question; do not paste verbatim.

## Entry point

**FIRST ACTION:** parse flags, then run the four phases. No step files — the phases are inline below.

1. **Parse flags** — lowercase enables, uppercase disables; `-f` consumes the next arg as `{from_file}`; remainder becomes `{idea}`.
2. **Apply implications** — `-i` enables `{issues_mode}` and `{save_mode}`; explicit `-S` overrides persistent saving. `-a` and `-e` set `{auto_mode}` and `{economy_mode}` respectively.
3. **Generate identifiers** — derive `{slug}` and `{project}` per § Parameters; `{output_dir}` = `~/.agents/output/{project}/forge/`; `{output_file}` = `{output_dir}forge-{slug}.md`.
4. **Create output dir** — if `{save_mode}` = true, `mkdir -p` the `$HOME`-expanded `{output_dir}`; report the fully-expanded absolute `{output_file}` (no tilde, no magic).
5. State the intended outcome and any consequential assumption briefly, then proceed to Hunt. Do not print internal state tables.

## Rules

- **Planning scope.** Forge itself produces the decision or spec and authorized issues. When selected inside an existing implementation mandate, hand back the artifact and continue authorized delivery using the appropriate implementation workflow.
- **Three tiers in Decide.** Reversible and conventional → decide and record the rationale. Load-bearing → surface the call with the pick, the runner-up, and what would flip it. User-owned → escalate. Auto-deciding a load-bearing call is the overengineering tell — see Phase 3.
- **Cross-reference, don't cherry-pick.** Triangulate sources for convergence and contradiction; never adopt the first plausible answer.
- **Ground the decision.** Investigate the evidence needed to resolve material uncertainty; a research or agent quota is not proof.
- **Load references on demand.** Read `references/*.md` only when the phase needs them — keep the main context lean.
- **Always include concrete acceptance criteria** — every workstream, Given/When/Then + ≥1 negative; see `references/spec-craft.md`.
- **Natural workstream boundaries.** Use one or more workstreams according to independently deliverable outcomes. Do not split or merge work to meet a count. The validator checks schema and dependencies.
- **Audit and validate before finalizing.** Walk the pre-save audit in `references/spec-craft.md` § Pre-save audit (Decision items always; Spec items when promoted) — rewrite anything flagged. When the artifact has workstreams, also run `python3 "$SKILL_DIR"/scripts/validate_spec.py {output_file}` (under `-S`, the temp Spec from Phase 4 Save) — exit 0 required (Priority/Complexity set; deps resolve; no cycles). The audit catches soft defects the validator cannot see; both gates must pass.

## Workflow — four phases

### Phase 1 — Hunt

Frame the real problem, then research it wide.

**Frame.** Before any research, establish: what is being decided or explored? what does success look like? what constraints exist (technical, budget, timeline, regulatory)? what does the user already know or suspect?

**Reframe.** The stated problem is rarely the real one. Restate the problem behind it, write 1-3 "How might we …" framings, and name the one you'll pursue. Generating solutions is Phase 2, not here.

**Load prior context (if `{from_file}`).** A GitHub issue (`#N` / URL) → `gh issue view <n> --json title,body,labels,comments`; carry its acceptance criteria forward. A non-GitHub web URL (an RFC, a blog post, a vendor doc) → fetch it with `WebFetch` (or your harness's web-fetch tool) and treat the fetched content as the prior context. A local file (a prior forge artifact, an RFC, a design doc) → `Read` the explicit path verbatim. No reconstruction, inference, or glob: the producer already printed the absolute path; the bridge carries it literally. If the path does not exist, fail loud and ask the user to correct or regenerate it. Extract its decisions, constraints, and open questions, and skip re-researching anything the prior context already covers.

**Clarify.** Ask only when missing scope, constraints or input could materially change the result. Read `references/clarify-playbook.md` for focused questions and opt-in deeper discussion. Resolve reversible details within existing authorization, including under `{auto_mode}`. Missing user-owned decisions or authorization remain pending; silence is not approval. Continue independent research while waiting.

**Research.** Investigate relevant codebase, technical and external questions with direct tools or useful independent subagents. Judge source authority, directness and independence; an official specification can establish its own contract alone. Tag external sources `primary`, `secondary`, `blog`, `anecdote` or `vendor-marketing` per `references/subagent-prompts.md`. Investigate uncovered consequential premortem failures before Decide, using direct tools under economy mode. Read `references/research-discipline.md` for breadth and stop criteria.

### Phase 2 — Judge

Diverge before converging, then stress-test.

**Diverge.** Compare the viable approaches that differ in mechanism and state their structural differences. Use real axes — scope, build/buy/defer, add/remove — when the constraints permit them. Consider stopping or inverting the default where it could solve the accepted problem; do not manufacture alternatives to meet a count. A constrained binary choice stays binary. No scoring or recommendation yet.

**Stress-test.** Pick a provisional leader and a viable runner-up when one exists, then:

- **Premortem.** It's six months out and this approach failed badly. List every plausible cause in the past tense — imagining the failure as already certain surfaces more failure modes than "what could go wrong?".
- **Steelman the alternative.** Argue the runner-up at full strength and name when it would win. If constraints leave one viable option, test the load-bearing assumption that makes it viable.
- Surface hidden costs (complexity, maintenance, vendor lock-in). Tag each load-bearing assumption: verified fact, assumption, or inherited convention. Ask whether a simpler path gets 80% of the value at 20% of the cost.

Be rigorous, not contrarian. For a sharper angle — first-principles, inversion, reverse-brainstorm, elimination — read `references/thinking-tools.md` on demand.

**Adversarial panel + convergence.** Challenge material uncertainty with independent critics when available. Economy mode uses a shared-context self-check with lower independence.

- **Round 1 — panel.** Assign independent critics when material uncertainty warrants them, each given the original user brief, constraints, source artifacts and evidence, the leader and runner-up summaries, and a distinct relevant lens, in priority order: overengineering/simplicity, load-bearing-assumption audit, the do-nothing/defer case, the runner-up's hidden-dimension win, and the premortem gaps. Select lenses for the actual risks. If subagents are unavailable or economy mode is selected, perform a separate self-check and report its lower independence.
- **Barrier.** Merge findings by common cause and consequence. Resolve each with a demonstrated correction, cited counterevidence, or an explicit unresolved risk; the author's score cannot clear it.
- **Round 2 — convergence.** Recheck consequential unresolved findings where another pass can add evidence. Use a fresh skeptic when available and useful; economy mode or an unavailable agent uses a disclosed shared-context check. Correct, refute with evidence, or preserve the finding as unresolved with its decision consequence. Stop when no useful evidence remains or after two rounds; Forge emits a bounded plan, not code.

Every finding flips the leader, is refuted with evidence, or is filed in Risks / Open questions — never silently dropped. For the lens skeletons and the convergence skeleton read `"$SKILL_DIR"/references/subagent-prompts.md`; for the panel roster, the dedup rule, the bounded-convergence loop, and the `{economy_mode}` skip, read `"$SKILL_DIR"/references/adversarial-panel.md`.

### Phase 3 — Decide

Resolve judged options according to the user's intent and authority. Three tiers: decide, surface, escalate.

**Decide** what's reversible and conventional — and record a one-line rationale for each:

- naming, file layout, test strategy;
- library, framework, or tool picks where one option is clearly better;
- decomposition order, dependency edges;
- any call that is reversible and cheap to change later.

**Surface** structurally load-bearing choices with the recommended option, runner-up and evidence that would flip the decision:

- a data-shape decision that constrains every future feature;
- an architecture pattern that shapes the next twelve months of work;
- a vendor pick with real exit cost;
- a convention choice that the team will live with for a long time.

Keep these choices visible; pause only for a user-owned decision or an explicit checkpoint.

**Escalate** the few forks the user genuinely owns — keep these to a handful:

- **Irreversible and costly** — data-migration shape, a public API contract, a dependency with a real exit cost. (Often both surfaced AND escalated.)
- **Product, business, or taste** — pricing, brand, scope-cut, deadline trade-offs; matters of taste with no engineering-correct answer.
- **A balanced fork where being wrong is expensive** — two options that are truly even *and* costly to reverse.

**Rule of thumb.** Reversible and conventional → DECIDE. Load-bearing → SURFACE with rationale. User-owned → ESCALATE.

### Phase 4 — Forge

Emit one artifact containing the decision, supporting evidence and disposition of material findings.

**Choose the shape first.** Default = `# Decision:` (no workstreams, present and pause for deliberation-only requests; continue an existing build mandate). Promote to `# Spec:` (with one or more workstreams) **only** when at least one of these holds:

- `{auto_mode}` = true — the user opted into commit-and-emit.
- `{issues_mode}` = true — `-i` forces issue creation, which needs workstreams; record the forced promotion as a one-line note in the Assumption ledger.
- `{from_file}` is a prior Spec artifact (H1 `# Spec:` and `## Workstreams`) — iteration preserves the shape; "tighten the plan" without a Spec body produces a near-empty Decision.
- `{idea}` contains an unambiguous build verb in active sense: `build`, `add`, `implement`, `create`, `migrate`, `refactor`, `port`, `replace`, `wire up`, `set up` (or an obvious synonym).
- `{idea}` contains an explicit decomposition signal: `plan`, `break down`, `spec out`, `decompose`, `workstreams`, `issues`, `roadmap`.
- The Decision is "build {X}" and the implementation plan IS the decision — splitting them would emit two near-identical artifacts.

Otherwise: write the Decision, present it, then ask the user whether to decompose into workstreams and wait. This keeps the discuss-then-build seam intact for exploratory questions where the user came for thinking, not for plumbing.

**Promotion implies `-s`.** When the shape lands on `# Spec:`, `{save_mode}` turns on — the validation gate and the `/apex` bridge both need the file on disk — the same way `-i` implies `-s`. A plain `# Decision:` without `-s` still saves nothing. Explicit `-S` wins: `{save_mode}` stays off and the Spec uses a temporary file for validation and any authorized implementation handoff (see Present and route).

**Write the artifact** using `templates/forge-artifact.md` (read `"$SKILL_DIR"/templates/forge-artifact.md` before writing):

1. **Decision header** — chosen approach + rationale, runner-up + what would flip it, escalated forks (or "none").
2. **Assumption ledger** — every load-bearing assumption tagged verified fact / assumption / inherited convention. Fold the panel + convergence findings here — each finding either flipped the leader, was refuted with evidence, or filed in Risks / Open questions. Silent drops are a defect.
3. **Research findings** — the cited, quality-tagged evidence that grounded the call, capped at the top findings by load-bearingness. Prominent in the Decision shape (the user came to see the thinking); a 2-3 bullet digest in the Spec shape. This is the research made visible, not buried in the ledger.
4. **Kill criteria** — 2-3 measurable tripwires, each a state + a date or milestone ("if {state} by {date}, abandon and revisit"), pre-committed before sunk cost clouds the call. "none" is valid for a pure tech choice with no commitment to abort.
5. **Spec shape only (promoted)** — H1 `# Spec: {title}`, one or more workstreams (Priority, Complexity, Depends on, Tasks, Acceptance criteria), a dependency graph with no cycles, and an execution order. Apply the AC and priority discipline in `references/spec-craft.md`.
6. **Decision shape (default)** — H1 `# Decision: {title}`. Omit workstreams, dependencies, and execution order. After Save, use the user's existing mandate to decide whether to stop at deliberation or continue delivery.

**Pre-save audit.** Before save, walk the audit checklist in `"$SKILL_DIR"/references/spec-craft.md` § Pre-save audit. The Decision-shape items apply always; the Spec-shape items apply when promoted. Rewrite anything flagged and re-walk the list. This is the layer the schema validator does not catch — vague AC, goals stated as outputs, greedy P0, untagged non-goals, XL workstreams that need splitting, surfaced forks left empty when load-bearing calls exist.

**Save** (if `{save_mode}` — promotion implies `-s`, so always true for the Spec shape unless `-S`) to the `$HOME`-expanded `{output_file}`; report the fully-expanded absolute path. If promotion turned `{save_mode}` on after the entry point, `mkdir -p` the `$HOME`-expanded `{output_dir}` first. Under `-S`, write the Spec to a temp file instead — the validator needs a file on disk; nothing lands in `{output_dir}`.

**Validate** (when workstreams exist) — `python3 "$SKILL_DIR"/scripts/validate_spec.py {output_file}` (under `-S`, the temp file from Save), exit 0 required. Rewrite until it clears.

**Revision pause** (Spec shape AND `{auto_mode}` = false, only when the user requested a planning checkpoint or has not authorized implementation). After Save + Validate, present a one-paragraph summary of the spec and ask the user: *"Spec is ready. Want to revise anything before /apex implements WS-1?"* Wait. Apply revisions inline, re-save, re-run the audit, re-validate. Skip under `{auto_mode}` = true or an existing implementation mandate; neither grants new authorization.

**Issues** (if `{issues_mode}`) — read `"$SKILL_DIR"/references/issue-creation.md` and follow it to create labels, an epic, and workstream issues in dependency order, then append the `## GitHub Issues` section.

**Present and route.** Present the decision in plain language — chosen approach, runner-up + what would flip it, top risk.

- **Spec shape** — inline the **fully-expanded absolute path** in the apex bridge (placeholder shown here; emit the resolved path at runtime):

  ```
  /apex -f ~/.agents/output/{project}/forge/forge-{slug}.md implement WS-1
  ```

  Under `-S`, pass the validated temporary Spec's absolute path to `/apex -f` for already-authorized implementation. Keep it available until the consumer finishes reading it; no persistent output is required. A planning-only request ends with the Spec and its temporary-path limitation. Do not require a `-s` rerun to continue an existing build mandate.

- **Decision shape (default)** — no apex bridge for deliberation-only requests. Ask whether to decompose and wait only when implementation is not already authorized. Under an existing build mandate, proceed with the Spec and delivery. If they opt in, re-enter Phase 4 with the Spec shape — a saved Decision's path is reused and the file overwritten with the promoted version; an unsaved one saves fresh to `{output_file}` (promotion implies `-s`; under `-S`, the temp-file route above applies instead). If they opt out, the discussion concludes here.

> **Dependency:** the bridge requires the `apex` skill. If unavailable, tell the user and suggest installing it, or proceed manually from the artifact.

## Gotchas

1. **Malformed workstream headings do not register.** Use `### WS-N:` and validate the resulting schema and dependency graph; workstream count follows actual scope.
2. **Dependency cycle halts save with exit 2** (`scripts/validate_spec.py:100-138`, DFS with path reconstruction). Run the validator manually before save; rewrite **Depends on** to break any cycle.
3. **Missing Priority or Complexity in any workstream blocks exit 0** (`scripts/validate_spec.py:63-66`). Values strict: `P0`/`P1`/`P2` and `S`/`M`/`L`/`XL`. Every workstream needs both rows.
4. **`-i` silently fails when `gh` is unauthenticated** — artifact saves, `## GitHub Issues` section appends with empty numbers. Run `gh auth status` before `-i`.

## Completion

Complete when the selected artifact meets Phase 4's audit and applicable validation, each material finding has a disposition, and the report preserves actual authorization and evidence limits. Planning-only requests end here; the implementation owner continues an existing build mandate.
