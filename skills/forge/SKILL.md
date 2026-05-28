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

Two artifact shapes:

- **Code-bearing** — H1 `# Spec: {title}`, with `## Workstreams`. This shape triggers `/apex`'s spec-closure: apex accepts the acceptance criteria verbatim. Emit it whenever the outcome is work to build.
- **Pure-strategy** — H1 `# Decision: {title}`, no workstreams. Emit it when the outcome is a choice with no immediate code (a tech pick, an architecture call, a process change). Terminal — no apex bridge.

If `{issues_mode}` = true, a `## GitHub Issues` section is appended after creation, mapping each workstream to its issue number.

## Subagent strategy

The Hunt phase uses **adaptive agent launching** unless `{economy_mode}` = true.

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

Emit ONE artifact — never a brainstorm brief and a spec concatenated. Research stays in the subagents; only the conclusion lands.

Write the artifact using `templates/forge-artifact.md` (read `${CLAUDE_SKILL_DIR}/templates/forge-artifact.md` before writing):

1. **Decision header** — the chosen approach with its rationale, the runner-up and what would flip it, and the few escalated forks (or "none").
2. **Assumption ledger** — every load-bearing assumption, tagged verified fact / assumption / inherited convention.
3. **When there is code to build** — 3-7 workstreams (Priority, Complexity, Depends on, Tasks, Acceptance criteria), a dependency graph with no cycles, and an execution order. Apply the AC and priority discipline in `references/spec-craft.md`. Use H1 `# Spec: {title}`.
4. **When the outcome is pure strategy** — stop at the decision. Use H1 `# Decision: {title}`, omit workstreams, dependencies, and execution order.

**Save** (if `{save_mode}`) to the `$HOME`-expanded `{output_file}`; report the fully-expanded absolute path.

**Validate** (when workstreams exist) — `python3 ${CLAUDE_SKILL_DIR}/scripts/validate_spec.py {output_file}`, exit 0 required. Rewrite until it clears.

**Issues** (if `{issues_mode}`) — read `${CLAUDE_SKILL_DIR}/references/issue-creation.md` and follow it to create labels, an epic, and workstream issues in dependency order, then append the `## GitHub Issues` section.

**Bridge.** Present the decision, the runner-up and what would flip it, and the top risk in plain language. Then inline the **fully-expanded absolute path** in the next command (placeholder shown here; emit the resolved path at runtime):

```
/apex -f ~/.claude/output/{project}/forge/forge-{slug}.md implement WS-1
```

For a pure-strategy outcome, conclude the discussion — no bridge.

> **Dependency:** the bridge requires the `apex` skill. If unavailable, tell the user and suggest installing it, or proceed manually from the artifact.

## Supporting files

- `templates/forge-artifact.md` — the canonical artifact format used by Phase 4
- `references/research-discipline.md` — three-angle breadth + triangulation discipline; read on demand by Hunt
- `references/clarify-playbook.md` — five decision-forcing question lenses + when-to-ask gate; read on demand by Hunt
- `references/thinking-tools.md` — first-principles, inversion, reverse-brainstorm, elimination; read on demand by Judge
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
- When there's code: 3-7 workstreams with priority, complexity, dependencies, and testable acceptance criteria; dependency graph resolves with no cycles; validator exits 0.
- Escalated forks held to a handful — everything else decided and recorded.
- Artifact saved if `{save_mode}`; GitHub issues created if `{issues_mode}`.
- Bridge command to `/apex` shown (code-bearing) or discussion concluded (pure strategy).
- No code implemented.
