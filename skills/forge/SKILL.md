---
name: forge
description: Pre-implementation thinking — research the problem space, weigh approaches with devil's-advocate rigor, decide what's reversible and conventional while surfacing the load-bearing forks for the user, and emit one apex-ready plan. Use whenever a non-trivial task needs thinking, comparison, or decomposition before code — even when the user doesn't say "forge" (e.g. "should we", "what's the best way", "compare", "evaluate", "pros and cons", "think through", "plan this", "break this down", "spec out", "create issues for", "map out the steps"). Produces a Decision by default (terminal — discuss-then-build); promotes to a Spec with prioritized workstreams when the build path is clear. NOT implementation (→ /apex or /oneshot).
when_to_use: When a non-trivial task needs research, option-weighing, or decomposition before building. After a rough idea when the direction or the work's shape is still open. When the user asks to explore, compare, evaluate, plan, break down, or create issues for a feature. Skip for clearly self-contained work where the approach is settled — go straight to /apex; skip for tiny one-file changes — use /oneshot. Never for implementation.
argument-hint: "[-s] [-f <path>] [-i] [-a] [-e] <question or idea>"
license: MIT
compatibility: "Optimized for Claude Code; degrades gracefully on any agent implementing the Agent Skills standard."
metadata:
  author: coroboros
  sources:
    - github.com/anthropics/knowledge-work-plugins/tree/main/product-management/skills/product-brainstorming
    - github.com/anthropics/knowledge-work-plugins/tree/main/product-management/skills/write-spec
    - github.com/Melvynx/aiblueprint
    - github.com/mattpocock/skills/tree/main/skills/productivity/grill-me
    - github.com/mattpocock/skills/tree/main/skills/engineering/to-issues
---

# Forge

<!-- canonical:adversarial-verification:start -->
## Critical — Adversarial verification

These rules govern how this skill trusts its own output — apply them whenever it verifies a claim, a defect, a source, or a decision before acting on it.

- Refute by default. Treat each non-trivial finding as unproven until a fresh-context check fails to refute it — the context that produced a claim cannot reliably clear it.
- No silent drop. Every finding flips the conclusion, is refuted in writing, or is filed as a risk or open question. A finding that vanishes without a verdict is a defect.
- Don't re-litigate settled facts. Spend adversarial effort on load-bearing or contested claims; let established facts pass. Over-refutation manufactures false doubt — it does not add rigor.
- Stay selective and cost-aware. Scale verification to the stakes; reversible, low-impact work gets a light touch, not a full adversarial sweep.
- Concede only to a strong rebuttal. A weak counter folds into the finding or gets filed; it does not overturn it.
<!-- canonical:adversarial-verification:end -->

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

Pre-implementation thinking for: $ARGUMENTS

## Objective

Take any starting point — a question, a rough idea, a brainstorm, a GitHub issue — research it wide, stress-test the options, decide every call inside the engineering mandate, and emit one artifact `/apex` can build from. Forge is the "think" half; `apex` is the "build" half. The seam between them carries the one human checkpoint that matters: review the plan before any code.

The discriminator is the Decide phase, in three tiers: forge **decides** the reversible and conventional calls, **surfaces** the structurally load-bearing forks for the user (named with the pick, the runner-up, and what would flip it), and **escalates** the few forks the user genuinely owns. Surfacing is the thinking the user asked for, made visible rather than buried in the Assumption ledger.

## Parameters

| Flag | Inverse | Behavior |
|------|---------|----------|
| `-s` / `--save` | `-S` / `--no-save` | Save the artifact to `~/.claude/output/{project}/forge/forge-{slug}.md` (global; `{slug}` = kebab of the idea, ≤5 words) |
| `-i` / `--issues` | `-I` / `--no-issues` | Create GitHub issues from the workstreams (implies `-s`) |
| `-a` / `--auto` | `-A` / `--no-auto` | Decide everything reasonable, skip Q&A, assume on forks (headless) |
| `-e` / `--economy` | `-E` / `--no-economy` | No subagents — direct tools only |
| `-f <path>` / `--from <path>` | — | Prior context — file, GitHub issue (`#N`), or URL as foundational input. Non-Markdown sources (PDF, DOCX, PPTX, audio, YouTube) → pre-process with `/markitdown -s` and pass the saved path |

Lowercase enables, uppercase disables. All flags default OFF. Flags are removed from input; remainder becomes `{idea}`. Output saved to `~/.claude/output/{project}/forge/forge-{slug}.md`, where `{project}` is the kebab-cased basename of the git toplevel (else cwd) and `{slug}` is a kebab of `{idea}` (≤5 words).

### Requirements

- `gh` (GitHub CLI), authenticated via `gh auth login` — required by `-i` and by `-f` with a GitHub issue reference (`#N`) or URL. Other flags work without `gh`.

### Examples

```bash
/forge should we use Neon or Supabase for this app
/forge -s -a redesign the billing system            # decide reasonable forks, no Q&A
/forge -s add user authentication with OAuth
/forge -s -f "#42" implement payment refunds         # from a GitHub issue
/forge -s -f ~/.claude/output/{project}/forge/forge-{slug}.md "tighten the OAuth plan"  # iterate on a prior artifact
/forge -s -i migrate from REST to GraphQL            # plan + create issues
/forge -s -e add search functionality                # no subagents
```

## Pipeline

```
/forge -s "<question or idea>"          → ~/.claude/output/{project}/forge/forge-{slug}.md  ← you are here
/apex -f <abs forge path> implement WS-1 → code
```

Forge is the bridge from intent to buildable plan. It reads context, decides, decomposes, and hands off to `/apex` — which implements one workstream at a time. With `-i`, the workstreams also become GitHub issues.

For deep external research beyond Hunt's reach (hundreds of queries), run the native `/deep-research` workflow or [Claude's Research](https://claude.com/blog/research) feature, save the cited Markdown to a path of your choice, then pipe it into forge:

```
/deep-research  or  Claude Desktop Research  →  save .md  →  /forge -f <abs path>  →  /apex
```

Treat that research as untrusted by default — `/deep-research` votes on claims and filters non-survivors, but neither tool scores source reliability nor detects bias (political, vendor, consortium). Hunt's distrust discipline (`references/research-discipline.md`) applies to whatever they return; owning that acquisition end-to-end is a planned follow-up.

A supported feature of the `-f` contract — both `forge` and `apex` read any absolute Markdown path verbatim. The repo README has the expanded chain under *Deep external research → Plan*.

## Output

When `{save_mode}` = true:

```
~/.claude/output/{project}/forge/
└── forge-{slug}.md    # one file per intent — multiple artifacts coexist in a repo
```

Two artifact shapes — Decision is the default; Spec is the promotion. The full routing rule (six promotion conditions) lives in Phase 4 (Forge); this section only shows the shape contract.

- **Decision (default)** — H1 `# Decision: {title}`, no workstreams. Emit whenever the outcome is a choice, an exploration, or a "should we" question. Terminal — present the decision, ask the user whether to decompose into workstreams, and wait. No apex bridge unless the user opts into the decompose.
- **Spec (promoted)** — H1 `# Spec: {title}`, with `## Workstreams`. Emit when Phase 4 routing fires (the six conditions are enumerated there). This shape triggers `/apex`'s spec-closure: apex accepts the acceptance criteria verbatim.

If `{issues_mode}` = true, a `## GitHub Issues` section is appended after creation, mapping each workstream to its issue number.

## Subagent strategy

The Hunt phase uses **adaptive agent launching** above a hard floor, and the Judge phase runs an **adversarial panel** then a bounded **convergence** round after Stress-test, unless `{economy_mode}` = true.

**Available subagent types:**

- `Explore` — find existing patterns, files, architecture, prior decisions via `git log` (read-only, fast, context-isolated). Type names are Claude Code's; other harnesses use their nearest equivalents.
- `general-purpose` — research approaches, library docs, post-mortems, web search

**Floor, then scale with complexity.** Every run launches at least 1 Explore + 1 general-purpose — forge is invoked deliberately, never for trivial work, so there is no zero-agent path. `{economy_mode}` is the only escape hatch. A harness without subagents satisfies the floor itself: run the codebase pass and the external pass sequentially, fresh context each.

| Scenario | Agents | Composition |
|----------|--------|-------------|
| Simple A-vs-B in a known space | 2 | 1x Explore + 1x general-purpose |
| New tech/pattern in a familiar ecosystem | 2-3 | 1x Explore (related code) + 1-2x general-purpose (docs) |
| Unfamiliar domain, multiple dimensions | 3-5 | 2x Explore + 1-2x general-purpose |
| Architecture-level, many unknowns | 6-10 | 3-4x Explore + 3-4x general-purpose |

Exploration output is large and noisy; subagents keep that noise out of the main context — only the distilled findings return. Launch all chosen agents in one message so they run in parallel. Scale up from the floor with the stakes; never drop below it unless `{economy_mode}` = true (no subagents in the harness → same floor, run both passes yourself).

`$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing this SKILL.md elsewhere.

**Prompt skeletons.** Pin the report shape and the constraint in every prompt — a vague subagent prompt returns a vague summary. For Explore (codebase reconnaissance), general-purpose (external research), and the adversarial panel + convergence skeptics used by Judge, read `"$SKILL_DIR"/references/subagent-prompts.md` on demand. Adapt the skeleton to the question; do not paste verbatim.

## State variables

Persist throughout:

| Variable | Type | Description |
|----------|------|-------------|
| `{idea}` | string | Question or feature description (flags removed) |
| `{project}` | string | Repo basename (git toplevel, else cwd) — keys the output dir |
| `{slug}` | string | Kebab of `{idea}` (≤5 words) — the intent; names the file |
| `{auto_mode}` | boolean | Decide reasonable forks, skip Q&A |
| `{save_mode}` | boolean | Save artifact to file |
| `{issues_mode}` | boolean | Create GitHub issues (forces save) |
| `{economy_mode}` | boolean | No subagents |
| `{from_file}` | string | Path to prior context (if `-f` provided) |
| `{output_dir}` | string | `~/.claude/output/{project}/forge/` (expanded to an absolute path for writes) |
| `{output_file}` | string | `{output_dir}forge-{slug}.md` |

## Entry point

**FIRST ACTION:** parse flags, then run the four phases. No step files — the phases are inline below.

1. **Parse flags** — lowercase enables, uppercase disables; `-f` consumes the next arg as `{from_file}`; remainder becomes `{idea}`.
2. **Apply implications** — if `{issues_mode}` = true, force `{save_mode}` = true.
3. **Generate identifiers** — derive `{slug}` and `{project}` per § Parameters; `{output_dir}` = `~/.claude/output/{project}/forge/`; `{output_file}` = `{output_dir}forge-{slug}.md`.
4. **Create output dir** — if `{save_mode}` = true, `mkdir -p` the `$HOME`-expanded `{output_dir}`; report the fully-expanded absolute `{output_file}` (no tilde, no magic).
5. **Show a compact summary** — one line + one table — then proceed to Hunt:

```
> Forge: {idea}

| Variable | Value |
|----------|-------|
| `{project}` | {project} |
| `{slug}` | {slug} |
| `{from_file}` | {path or —} |
| `{auto_mode}` | true/false |
| `{save_mode}` | true/false |
| `{issues_mode}` | true/false |
| `{economy_mode}` | true/false |

→ Hunting...
```

Keep it minimal — no verbose parsing logs, no separators.

## Rules

- **Never implement.** Forge produces a document (and optionally issues), not code changes. No edits or writes beyond the artifact.
- **Three tiers in Decide.** Reversible and conventional → decide and record the rationale. Load-bearing → surface the call with the pick, the runner-up, and what would flip it. User-owned → escalate. Auto-deciding a load-bearing call is the overengineering tell — see Phase 3.
- **Cross-reference, don't cherry-pick.** Triangulate sources for convergence and contradiction; never adopt the first plausible answer.
- **Think hardest at Judge and Decide — never skim Hunt.** Every run grounds the call in ≥1 codebase + ≥1 external agent unless `{economy_mode}`; perceived clarity is where un-audited assumptions hide.
- **Load references on demand.** Read `references/*.md` only when the phase needs them — keep the main context lean.
- **Always include concrete acceptance criteria** — every workstream, Given/When/Then + ≥1 negative; see `references/spec-craft.md`.
- **3-7 workstreams.** Code-bearing artifacts have between 3 and 7 workstreams. Fewer means one task — go straight to `/oneshot` or `/apex`. More means re-decompose. Enforced by `scripts/validate_spec.py`.
- **Audit and validate before finalizing.** Walk the pre-save audit in `references/spec-craft.md` § Pre-save audit (Decision items always; Spec items when promoted) — rewrite anything flagged. When the artifact has workstreams, also run `python3 "$SKILL_DIR"/scripts/validate_spec.py {output_file}` — exit 0 required (Priority/Complexity set; deps resolve; no cycles). The audit catches soft defects the validator cannot see; both gates must pass.

## Workflow — four phases

### Phase 1 — Hunt

Frame the real problem, then research it wide.

**Frame.** Before any research, establish: what is being decided or explored? what does success look like? what constraints exist (technical, budget, timeline, regulatory)? what does the user already know or suspect?

**Reframe.** The stated problem is rarely the real one. Restate the problem behind it, write 1-3 "How might we …" framings, and name the one you'll pursue. Generating solutions is Phase 2, not here.

**Load prior context (if `{from_file}`).** A GitHub issue (`#N` / URL) → `gh issue view <n> --json title,body,labels,comments`; carry its acceptance criteria forward. A local file (a prior forge artifact, an RFC, a design doc) → `Read` the explicit path verbatim. No reconstruction, inference, or glob: the producer already printed the absolute path; the bridge carries it literally. If the path does not exist, fail loud and ask the user to correct or regenerate it. Extract its decisions, constraints, and open questions, and skip re-researching anything the prior context already covers.

**Clarify (if vague and not `{auto_mode}`).** If scope, constraints, success criteria, or a load-bearing dependency is unclear and could flip the outcome, ask the 1-3 most relevant decision-forcing questions in a single message before researching — never five when one matters, never a second round, unless the user opts into a deep grill (relentless, one-question-at-a-time; see the playbook). For the question set, the when-to-ask gate, the prior-context attenuation rule, and the opt-in deep grill, read `"$SKILL_DIR"/references/clarify-playbook.md` on demand. Under `{auto_mode}`, never ask — decide, tag the call `assumption` in the ledger, surface the shakiest as an open question.

**Research.** Investigate from multiple angles via parallel subagents above the research floor, scaled to complexity (see Subagent strategy). Cover the three angles that apply — codebase context, technical best practices, external evidence — and **triangulate**: a single source is anecdote, convergence across two or three is signal, divergence is the more informative finding. Every cited external source carries a quality tag (`primary` / `secondary` / `blog` / `anecdote` / `vendor-marketing`) per the prompt contract in `"$SKILL_DIR"/references/subagent-prompts.md` § *general-purpose — external research* — downstream readers discount lower-quality sources before fusion. When the Phase 2 premortem surfaces a failure mode no source covered, launch one more research agent before Decide — the second round is automatic, not optional. For breadth, stop-criteria, and the rule of when to widen the net, read `"$SKILL_DIR"/references/research-discipline.md` on demand.

### Phase 2 — Judge

Diverge before converging, then stress-test.

**Diverge.** Produce **≥3 approaches that differ in mechanism**, not three variants of one. State why each is structurally distinct. Vary them along a real axis — scope (small tweak vs. big bet), strategy (build vs. buy vs. defer), direction (add vs. remove). Include one approach that **removes or stops** something rather than adding, and one that **inverts the obvious default** ("what if we did the opposite?"). No scoring, no "recommended" yet.

**Stress-test.** Pick a provisional leader and a runner-up, then:

- **Premortem.** It's six months out and this approach failed badly. List every plausible cause in the past tense — imagining the failure as already certain surfaces more failure modes than "what could go wrong?".
- **Steelman the runner-up.** Argue the second-best approach at full strength; name the condition under which it would win.
- Surface hidden costs (complexity, maintenance, vendor lock-in). Tag each load-bearing assumption: verified fact, assumption, or inherited convention. Ask whether a simpler path gets 80% of the value at 20% of the cost.

Be rigorous, not contrarian. For a sharper angle — first-principles, inversion, reverse-brainstorm, elimination — read `references/thinking-tools.md` on demand.

**Adversarial panel + convergence.** ON by default; skipped only under `{economy_mode}`. The critique must come from contexts that did NOT produce the leader — the same conversation cannot reliably argue against the plan it just shipped.

- **Round 1 — panel.** Launch 3-5 `general-purpose` critics in one parallel message, each a clean context fed only the leader summary, the runner-up summary, and the premortem failures, and each assigned ONE distinct lens, in priority order: overengineering/simplicity, load-bearing-assumption audit, the do-nothing/defer case, the runner-up's hidden-dimension win, and the premortem gaps. Use the first 3 lenses for a focused call, all 5 for an architecture-level one. If your harness has no subagents, run each critic lens yourself sequentially in fresh adversarial passes.
- **Barrier.** Merge the returned findings, dedup by target, and score each rebuttal 1–5 on the Concession Threshold — concede only at ≥ 4; below that the finding survives.
- **Round 2 — convergence.** Launch one fresh skeptic per surviving finding to kill it (refute in writing) or confirm it (escalate to a flip condition or a risk). Stop when findings degrade to nitpicks, or after 2 rounds total — forge emits a bounded plan, not code.

Every finding flips the leader, is refuted in writing at ≥ 4, or is filed in Risks / Open questions — never silently dropped. For the lens skeletons and the convergence skeleton read `"$SKILL_DIR"/references/subagent-prompts.md`; for the panel roster, the dedup rule, the bounded-convergence loop, and the `{economy_mode}` skip, read `"$SKILL_DIR"/references/adversarial-panel.md`.

### Phase 3 — Decide

Convert the judged options into resolved calls — but read the user's intent first. The discriminator between a clean call and an overengineered artifact is whether the user came for plumbing or for thinking. Three tiers: decide, surface, escalate.

**Decide** what's reversible and conventional — and record a one-line rationale for each:

- naming, file layout, test strategy;
- library, framework, or tool picks where one option is clearly better;
- decomposition order, dependency edges;
- any call that is reversible and cheap to change later.

**Surface** what's structurally load-bearing — even if a competent senior engineer would just pick one. When the user came to think through a problem, the load-bearing call IS the thinking; burying it in the Assumption ledger as a fait accompli is the move that returns as "this got overengineered":

- a data-shape decision that constrains every future feature;
- an architecture pattern that shapes the next twelve months of work;
- a vendor pick with real exit cost;
- a convention choice that the team will live with for a long time.

Name the option you would pick, the runner-up, and what would flip it. Then let the user agree or redirect. This is not escalation — it is the thinking the user asked for, made visible.

**Escalate** the few forks the user genuinely owns — keep these to a handful:

- **Irreversible and costly** — data-migration shape, a public API contract, a dependency with a real exit cost. (Often both surfaced AND escalated.)
- **Product, business, or taste** — pricing, brand, scope-cut, deadline trade-offs; matters of taste with no engineering-correct answer.
- **A balanced fork where being wrong is expensive** — two options that are truly even *and* costly to reverse.

**Rule of thumb.** Reversible and conventional → DECIDE. Load-bearing → SURFACE the call with rationale. User-owned → ESCALATE. When in doubt, prefer surfacing over auto-deciding — the user came for thinking, and a load-bearing decision recorded as an assumption the user can theoretically veto, but which they will never see because it lives 200 lines down the ledger, is a defect.

### Phase 4 — Forge

Emit ONE artifact. Research and adversarial findings stay in the subagents — only the conclusion lands.

**Choose the shape first.** Default = `# Decision:` (no workstreams, terminal — present the decision and pause for the user). Promote to `# Spec:` (with 3-7 workstreams) **only** when at least one of these holds:

- `{auto_mode}` = true — the user opted into commit-and-emit.
- `{issues_mode}` = true — `-i` forces issue creation, which needs workstreams; record the forced promotion as a one-line note in the Assumption ledger.
- `{from_file}` is a prior Spec artifact (H1 `# Spec:` and `## Workstreams`) — iteration preserves the shape; "tighten the plan" without a Spec body produces a near-empty Decision.
- `{idea}` contains an unambiguous build verb in active sense: `build`, `add`, `implement`, `create`, `migrate`, `refactor`, `port`, `replace`, `wire up`, `set up` (or an obvious synonym).
- `{idea}` contains an explicit decomposition signal: `plan`, `break down`, `spec out`, `decompose`, `workstreams`, `issues`, `roadmap`.
- The Decision is "build {X}" and the implementation plan IS the decision — splitting them would emit two near-identical artifacts.

Otherwise: write the Decision, present it, then ask the user whether to decompose into workstreams and wait. This keeps the discuss-then-build seam intact for exploratory questions where the user came for thinking, not for plumbing.

**Write the artifact** using `templates/forge-artifact.md` (read `"$SKILL_DIR"/templates/forge-artifact.md` before writing):

1. **Decision header** — chosen approach + rationale, runner-up + what would flip it, escalated forks (or "none").
2. **Assumption ledger** — every load-bearing assumption tagged verified fact / assumption / inherited convention. Fold the panel + convergence findings here — each finding either flipped the leader, was refuted in writing at score ≥ 4 per the Concession Threshold Protocol, or filed in Risks / Open questions. Silent drops are a defect.
3. **Research findings** — the cited, quality-tagged evidence that grounded the call, capped at the top findings by load-bearingness. Prominent in the Decision shape (the user came to see the thinking); a 2-3 bullet digest in the Spec shape. This is the research made visible, not buried in the ledger.
4. **Kill criteria** — 2-3 measurable tripwires, each a state + a date or milestone ("if {state} by {date}, abandon and revisit"), pre-committed before sunk cost clouds the call. "none" is valid for a pure tech choice with no commitment to abort.
5. **Spec shape only (promoted)** — H1 `# Spec: {title}`, 3-7 workstreams (Priority, Complexity, Depends on, Tasks, Acceptance criteria), a dependency graph with no cycles, and an execution order. Apply the AC and priority discipline in `references/spec-craft.md`.
6. **Decision shape (default)** — H1 `# Decision: {title}`. Omit workstreams, dependencies, and execution order. After Save, present and pause for the decompose question described above.

**Pre-save audit.** Before save, walk the audit checklist in `"$SKILL_DIR"/references/spec-craft.md` § Pre-save audit. The Decision-shape items apply always; the Spec-shape items apply when promoted. Rewrite anything flagged and re-walk the list. This is the layer the schema validator does not catch — vague AC, goals stated as outputs, greedy P0, untagged non-goals, XL workstreams that need splitting, surfaced forks left empty when load-bearing calls exist.

**Save** (if `{save_mode}`) to the `$HOME`-expanded `{output_file}`; report the fully-expanded absolute path.

**Validate** (when workstreams exist) — `python3 "$SKILL_DIR"/scripts/validate_spec.py {output_file}`, exit 0 required. Rewrite until it clears.

**Revision pause** (Spec shape AND `{auto_mode}` = false). After Save + Validate, present a one-paragraph summary of the spec and ask the user: *"Spec is ready. Want to revise anything before /apex implements WS-1?"* Wait. Apply revisions inline, re-save, re-run the audit, re-validate. Skip under `{auto_mode}` = true — the user opted into commit-and-emit.

**Issues** (if `{issues_mode}`) — read `"$SKILL_DIR"/references/issue-creation.md` and follow it to create labels, an epic, and workstream issues in dependency order, then append the `## GitHub Issues` section.

**Present and route.** Present the decision in plain language — chosen approach, runner-up + what would flip it, top risk.

- **Spec shape** — inline the **fully-expanded absolute path** in the apex bridge (placeholder shown here; emit the resolved path at runtime):

  ```
  /apex -f ~/.claude/output/{project}/forge/forge-{slug}.md implement WS-1
  ```

- **Decision shape (default)** — no apex bridge. Ask the user whether to decompose the decision into workstreams and wait. If they opt in, re-enter Phase 4 with the Spec shape (the existing artifact path is reused; the file is overwritten with the promoted version). If they opt out, the discussion concludes here.

> **Dependency:** the bridge requires the `apex` skill. If unavailable, tell the user and suggest installing it, or proceed manually from the artifact.

## Supporting files

- `templates/forge-artifact.md` — the canonical artifact format used by Phase 4
- `references/research-discipline.md` — three-angle breadth + triangulation discipline; read on demand by Hunt
- `references/clarify-playbook.md` — five decision-forcing question lenses, when-to-ask gate, opt-in deep grill; read on demand by Hunt
- `references/subagent-prompts.md` — prompt skeletons for Explore, general-purpose, and the adversarial critic; read on demand whenever launching a subagent
- `references/thinking-tools.md` — first-principles, inversion, reverse-brainstorm, elimination; read on demand by Judge
- `references/adversarial-panel.md` — panel + bounded-convergence methodology: lenses, dedup, when to skip, how to integrate findings; read on demand by Judge
- `references/spec-craft.md` — acceptance-criteria, priority, and goal-hardening technique; read on demand by Forge
- `references/issue-creation.md` — GitHub issue orchestration; read only when `-i` is set
- `scripts/validate_spec.py` — schema + dependency-graph validator (Forge; requires Python 3.7+)
- `scripts/setup-labels.sh` — idempotent GitHub label creation (used by issue creation)

## Gotchas

1. **Workstream count outside 3-7 fails `scripts/validate_spec.py:158-161`.** Headings that don't match `### WS-N:` (`### WS1`, `### WS-1.5`) silently skip. Under 3 → use `/oneshot` or `/apex` directly; over 7 → re-group.
2. **Dependency cycle halts save with exit 2** (`scripts/validate_spec.py:100-138`, DFS with path reconstruction). Run the validator manually before save; rewrite **Depends on** to break any cycle.
3. **Missing Priority or Complexity in any workstream blocks exit 0** (`scripts/validate_spec.py:63-66`). Values strict: `P0`/`P1`/`P2` and `S`/`M`/`L`/`XL`. Every workstream needs both rows.
4. **`-i` silently fails when `gh` is unauthenticated** — artifact saves, `## GitHub Issues` section appends with empty numbers. Run `gh auth status` before `-i`.

## Success criteria

- A decision with a clear rationale, the runner-up, and what would flip it.
- Adversarial panel + convergence findings each flipped, refuted in writing at ≥ 4, or filed — never silently dropped; convergence bounded to ≤ 2 rounds.
- Research floor honored — ≥1 codebase + ≥1 external research pass (subagents when available) unless `-e`; a second research round fired if the premortem surfaced an unresearched failure mode.
- Kill criteria emitted (measurable tripwire + date, or "none"); research-findings section present and quality-tagged.
- Shape routing respected: Decision by default; Spec only when `{auto_mode}`, a build verb, an explicit decomposition signal, or `{issues_mode}` fires.
- Surfaced forks named for any load-bearing call (or "none" when there genuinely are none) — three-tier Decide upheld.
- Pre-save audit cleared (Decision items always; Spec items when promoted) — the validator passes only after the audit does.
- When Spec shape is emitted: 3-7 workstreams with priority, complexity, dependencies, and testable acceptance criteria; dependency graph resolves with no cycles; validator exits 0.
- Escalated forks held to a handful — everything else decided or surfaced.
- Artifact saved if `{save_mode}`; GitHub issues created if `{issues_mode}`.
- Revision pause shown for Spec shape under non-auto; decompose question shown for Decision shape under non-auto. Neither under `{auto_mode}`.
- Spec → `/apex` bridge shown. Decision → decompose question asked and waited on.
- No code implemented.
