---
name: forge
description: Pre-implementation thinking — research the problem space, weigh approaches with devil's-advocate rigor, decide every engineering call within scope, and emit one apex-ready plan. Use whenever a non-trivial task needs thinking, comparison, or decomposition before code — even when the user doesn't say "forge" (e.g. "should we", "what's the best way", "compare", "evaluate", "pros and cons", "think through", "plan this", "break this down", "spec out", "create issues for", "map out the steps"). Produces a decision and, when there's code to build, prioritized workstreams with dependencies and acceptance criteria. NOT implementation (→ /apex or /oneshot).
when_to_use: When a non-trivial task needs research, option-weighing, or decomposition before building. After a rough idea when the direction or the work's shape is still open. When the user asks to explore, compare, evaluate, plan, break down, or create issues for a feature. Skip for clearly self-contained work where the approach is settled — go straight to /apex; skip for tiny one-file changes — use /oneshot. Never for implementation.
argument-hint: "[-s] [-f <path>] [-i] [-a] [-e] <question or idea>"
model: opus
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
metadata:
  author: coroboros
  sources:
    - github.com/anthropics/knowledge-work-plugins/tree/main/product-management/skills/product-brainstorming
    - github.com/anthropics/knowledge-work-plugins/tree/main/product-management/skills/write-spec
    - github.com/Melvynx/aiblueprint
---

# Forge

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

The discriminator is the Decide phase. Forge resolves the judgment calls a senior engineer would just make, and escalates only the few forks the user genuinely owns — turning "too many open questions" into "a few sharp ones."

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

## Output

When `{save_mode}` = true:

```
~/.claude/output/{project}/forge/
└── forge-{slug}.md    # one file per intent — multiple artifacts coexist in a repo
```

Two artifact shapes — Decision is the default; Spec is the promotion. The routing rule lives in Phase 4 (Forge):

- **Decision (default)** — H1 `# Decision: {title}`, no workstreams. Emit by default whenever the outcome is a choice, an exploration, or a "should we" question. Terminal — present the decision, ask the user whether to decompose into workstreams, and wait. No apex bridge unless the user opts into the decompose.
- **Spec (promoted)** — H1 `# Spec: {title}`, with `## Workstreams`. Emit when `{auto_mode}` = true, OR when the idea carries an unambiguous build verb (`build`, `add`, `implement`, `migrate`, `refactor`, `create`, `port`, `replace`, …), OR when the idea carries an explicit decomposition signal (`plan`, `break down`, `spec out`, `decompose`, `workstreams`, `issues`, `roadmap`). This shape triggers `/apex`'s spec-closure: apex accepts the acceptance criteria verbatim.

If `{issues_mode}` = true, a `## GitHub Issues` section is appended after creation, mapping each workstream to its issue number. `{issues_mode}` implies the Spec shape — if the routing did not promote, force-promote with a one-line note in the Assumption ledger.

## Subagent strategy

The Hunt phase uses **adaptive agent launching** and the Judge phase runs one **adversarial fresh-eyes critic** after Stress-test, unless `{economy_mode}` = true.

**Available subagent types:**

- `Explore` — find existing patterns, files, architecture, prior decisions via `git log` (read-only, fast, context-isolated)
- `general-purpose` — research approaches, library docs, post-mortems, web search

**Launch count scales with complexity:**

| Scenario | Agents | Composition |
|----------|--------|-------------|
| Answer already clear from framing | 0 | Decide directly — don't waste tokens |
| Simple A-vs-B in a known space | 1-2 | 1x Explore or 1x general-purpose |
| New tech/pattern in a familiar ecosystem | 2-3 | 1x Explore (related code) + 1x general-purpose (docs) |
| Unfamiliar domain, multiple dimensions | 3-5 | 2x Explore + 1-2x general-purpose |
| Architecture-level, many unknowns | 5-7 | 2x Explore + 2-3x general-purpose |

Exploration output is large and noisy; subagents keep that noise out of the main context — only the distilled findings return. Launch all chosen agents in one message so they run in parallel. Don't over-launch: if the idea is simple or the codebase is small, skip subagents and use direct tools.

**Prompt skeletons.** Pin the report shape and the constraint in every prompt — a vague subagent prompt returns a vague summary. For Explore (codebase reconnaissance), general-purpose (external research), and the adversarial critic used by Judge, read `${CLAUDE_SKILL_DIR}/references/subagent-prompts.md` on demand. Adapt the skeleton to the question; do not paste verbatim.

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
- **Decide, don't defer.** Resolve every engineering judgment call (see Phase 3). Escalate only the few forks the user genuinely owns.
- **Cross-reference, don't cherry-pick.** Triangulate sources for convergence and contradiction; never adopt the first plausible answer.
- **Think hardest at Judge and Decide.** Don't overthink Hunt-phase triage — gathering is cheap.
- **Load references on demand.** Read `references/*.md` only when the phase needs them — keep the main context lean.
- **Always include concrete acceptance criteria** — every workstream, Given/When/Then + ≥1 negative; see `references/spec-craft.md`.
- **3-7 workstreams.** Code-bearing artifacts have between 3 and 7 workstreams. Fewer means one task — go straight to `/oneshot` or `/apex`. More means re-decompose. Enforced by `scripts/validate_spec.py`.
- **Validate before finalizing.** When the artifact has workstreams, run `python3 ${CLAUDE_SKILL_DIR}/scripts/validate_spec.py {output_file}` — exit 0 required (Priority/Complexity set; deps resolve; no cycles). Rewrite flagged workstreams until it clears.

## Workflow — four phases

### Phase 1 — Hunt

Frame the real problem, then research it wide.

**Frame.** Before any research, establish: what is being decided or explored? what does success look like? what constraints exist (technical, budget, timeline, regulatory)? what does the user already know or suspect?

**Reframe.** The stated problem is rarely the real one. Restate the problem behind it, write 1-3 "How might we …" framings, and name the one you'll pursue. Generating solutions is Phase 2, not here.

**Load prior context (if `{from_file}`).** A GitHub issue (`#N` / URL) → `gh issue view <n> --json title,body,labels,comments`; carry its acceptance criteria forward. A local file (a prior forge artifact, an RFC, a design doc) → `Read` the explicit path verbatim. No reconstruction, inference, or glob: the producer already printed the absolute path; the bridge carries it literally. If the path does not exist, fail loud and ask the user to correct or regenerate it. Extract its decisions, constraints, and open questions, and skip re-researching anything the prior context already covers.

**Clarify (if vague and not `{auto_mode}`).** If scope, constraints, success criteria, or a load-bearing dependency is unclear and could flip the outcome, ask the 1-3 most relevant decision-forcing questions in a single message before researching — never five when one matters, never a second round. For the question set, the when-to-ask gate, and the prior-context attenuation rule, read `${CLAUDE_SKILL_DIR}/references/clarify-playbook.md` on demand. Under `{auto_mode}`, never ask — decide, tag the call `assumption` in the ledger, surface the shakiest as an open question.

**Research.** Investigate from multiple angles via parallel subagents scaled to complexity (see Subagent strategy). Cover the three angles that apply — codebase context, technical best practices, external evidence — and **triangulate**: a single source is anecdote, convergence across two or three is signal, divergence is the more informative finding. For breadth, stop-criteria, and the rule of when to widen the net, read `${CLAUDE_SKILL_DIR}/references/research-discipline.md` on demand.

### Phase 2 — Judge

Diverge before converging, then stress-test.

**Diverge.** Produce **≥3 approaches that differ in mechanism**, not three variants of one. State why each is structurally distinct. Vary them along a real axis — scope (small tweak vs. big bet), strategy (build vs. buy vs. defer), direction (add vs. remove). Include one approach that **removes or stops** something rather than adding, and one that **inverts the obvious default** ("what if we did the opposite?"). No scoring, no "recommended" yet.

**Stress-test.** Pick a provisional leader and a runner-up, then:

- **Premortem.** It's six months out and this approach failed badly. List every plausible cause in the past tense — imagining the failure as already certain surfaces more failure modes than "what could go wrong?".
- **Steelman the runner-up.** Argue the second-best approach at full strength; name the condition under which it would win.
- Surface hidden costs (complexity, maintenance, vendor lock-in). Tag each load-bearing assumption: verified fact, assumption, or inherited convention. Ask whether a simpler path gets 80% of the value at 20% of the cost.

Be rigorous, not contrarian. For a sharper angle — first-principles, inversion, reverse-brainstorm, elimination — read `references/thinking-tools.md` on demand.

**Adversarial fresh-eyes.** ON by default; skipped under `{economy_mode}` = true, or when Judge has already converged with a wide leader/runner-up gap and no load-bearing assumption is tagged `assumption` or `inherited convention`. Launch one `general-purpose` subagent with a clean context — leader summary, runner-up summary, and the premortem failures only. The point is that the critique comes from a context that did NOT produce the leader: the same conversation cannot reliably argue against the plan it just shipped. For the prompt skeleton, read `${CLAUDE_SKILL_DIR}/references/subagent-prompts.md`; for when to skip and how to integrate findings (fold into Decision, refute in writing, or file in Risks / Open questions — never silently drop), read `${CLAUDE_SKILL_DIR}/references/adversarial-critique.md`.

### Phase 3 — Decide

The heart of forge. Convert the judged options into resolved calls.

**Decide everything that is an engineering judgment call** — and record a one-line rationale for each:

- architecture and structure, library/framework/tool selection, design pattern;
- how to decompose the work into workstreams, their order and dependencies;
- naming, file layout, test strategy;
- any trade-off where one option is clearly better, and anything reversible and cheap to change later.

**Escalate only** — and keep these to a handful:

- **Irreversible and costly** — data-migration shape, a public API contract, a dependency with a real exit cost.
- **Genuinely the user's to own** — product, business, brand, pricing, scope-cut, or deadline trade-offs; matters of taste with no engineering-correct answer.
- **A balanced fork where being wrong is expensive** — two options that are truly even *and* costly to reverse.

**Rule of thumb:** a competent senior engineer would just pick one and move on → **DECIDE**. It needs the product owner, or it would be expensive to reverse → **ESCALATE**. When in doubt, decide and record the assumption — a recorded assumption the user can veto beats an open question that stalls the build.

### Phase 4 — Forge

Emit ONE artifact. Research and adversarial findings stay in the subagents — only the conclusion lands.

**Choose the shape first.** Default = `# Decision:` (no workstreams, terminal — present the decision and pause for the user). Promote to `# Spec:` (with 3-7 workstreams) **only** when at least one of these holds:

- `{auto_mode}` = true — the user opted into commit-and-emit.
- `{idea}` contains an unambiguous build verb in active sense: `build`, `add`, `implement`, `create`, `migrate`, `refactor`, `port`, `replace`, `wire up`, `set up` (or an obvious synonym).
- `{idea}` contains an explicit decomposition signal: `plan`, `break down`, `spec out`, `decompose`, `workstreams`, `issues`, `roadmap`.
- The Decision is "build {X}" and the implementation plan IS the decision — splitting them would emit two near-identical artifacts.

Otherwise: write the Decision, present it, then ask the user whether to decompose into workstreams and wait. This restores the discuss-then-build seam for exploratory questions where the user came for thinking, not for plumbing — the same posture the pre-merge brainstorm carried in its Discuss phase.

**Write the artifact** using `templates/forge-artifact.md` (read `${CLAUDE_SKILL_DIR}/templates/forge-artifact.md` before writing):

1. **Decision header** — chosen approach + rationale, runner-up + what would flip it, escalated forks (or "none").
2. **Assumption ledger** — every load-bearing assumption tagged verified fact / assumption / inherited convention. Fold the adversarial-critique findings here — each finding either flipped the leader, was refuted in writing, or filed in Risks / Open questions; never silently dropped.
3. **Spec shape only (promoted)** — H1 `# Spec: {title}`, 3-7 workstreams (Priority, Complexity, Depends on, Tasks, Acceptance criteria), a dependency graph with no cycles, and an execution order. Apply the AC and priority discipline in `references/spec-craft.md`.
4. **Decision shape (default)** — H1 `# Decision: {title}`. Omit workstreams, dependencies, and execution order. After Save, present and pause for the decompose question described above.

**Save** (if `{save_mode}`) to the `$HOME`-expanded `{output_file}`; report the fully-expanded absolute path.

**Validate** (when workstreams exist) — `python3 ${CLAUDE_SKILL_DIR}/scripts/validate_spec.py {output_file}`, exit 0 required. Rewrite until it clears.

**Issues** (if `{issues_mode}`) — read `${CLAUDE_SKILL_DIR}/references/issue-creation.md` and follow it to create labels, an epic, and workstream issues in dependency order, then append the `## GitHub Issues` section.

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
- `references/clarify-playbook.md` — five decision-forcing question lenses + when-to-ask gate; read on demand by Hunt
- `references/subagent-prompts.md` — prompt skeletons for Explore, general-purpose, and the adversarial critic; read on demand whenever launching a subagent
- `references/thinking-tools.md` — first-principles, inversion, reverse-brainstorm, elimination; read on demand by Judge
- `references/adversarial-critique.md` — fresh-eyes methodology: when to run, when to skip, how to integrate findings; read on demand by Judge
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
- Adversarial-critique findings folded into the artifact (or refuted in writing) — never silently dropped.
- Shape routing respected: Decision by default; Spec only when `{auto_mode}`, a build verb, an explicit decomposition signal, or `{issues_mode}` fires.
- When Spec shape is emitted: 3-7 workstreams with priority, complexity, dependencies, and testable acceptance criteria; dependency graph resolves with no cycles; validator exits 0.
- Escalated forks held to a handful — everything else decided and recorded.
- Artifact saved if `{save_mode}`; GitHub issues created if `{issues_mode}`.
- Spec → `/apex` bridge shown. Decision → decompose question asked and waited on.
- No code implemented.
