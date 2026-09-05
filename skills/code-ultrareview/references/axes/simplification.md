# Axis: Simplification (key `simplification`)

Over-engineering and complexity beyond what the task requires. The dedicated axis exists because bug-focused review misses code that works but should not have been written. Carries the `code-simplifier` plugin's canonical anti-patterns.

## In scope (HIGH SIGNAL)

- **Single-use abstractions** — a class, factory, or helper introduced for one call site. Inline it.
- **Premature configurability** — flags, options, or strategy patterns added without a second consumer.
- **Speculative generality** (Fowler) — generic types, abstract base classes, registry patterns introduced "for future use" with no concrete future use in the diff.
- **Long parameter lists** — `> 3` parameters per the Microsoft heuristic; routed through `lizard` when CCN/params exceed thresholds.
- **Nested ternaries** — `> 1` level. Per `code-simplifier` plugin (canonical anti-pattern, quoted below).
- **Dead code judgment** — code the deterministic tools (`knip`, `vulture`, `cargo-machete`, `deadcode`) flagged as unused. The LLM decides whether to remove (truly unused) or wire it up (forgotten integration).
- **Redundancy beyond duplication** — code that re-implements an existing helper in the same module or a documented utility. Distinct from `jscpd` mechanical duplication.
- **"Fewer lines over readability"** — golfing a clear 5-line block into a dense one-liner. Per `code-simplifier` plugin (canonical anti-pattern).
- **Cyclomatic complexity > 10** — from `lizard` / `gocyclo`. The function is too branchy; split.

## Quoted from `code-simplifier`

> **Nested ternaries: FORBIDDEN.** Replace with `if/else` blocks.
>
> **"Fewer lines over readability": FORBIDDEN.** Readability wins.

Source: `sources/claude-plugins-official/plugins/code-simplifier/agents/code-simplifier.md:29,38`. Last verified: 2026-05-26.

## Out of scope (false positives — silence at source)

Anchor: `references/anthropic-verbatim.md` § False-positive taxonomy.

- A senior engineer would not call it out — pedantic micro-rewrites of clear code.
- "This could be DRYer" without a concrete duplicate — purely aesthetic.
- Refactor suggestions that change behavior. Simplification is shape-preserving.
- Style preferences (single vs double quotes, brace placement). The Style axis defers to the formatter.
- Anything the formatter would re-shape on the next run.

## Tool inputs (Phase 2)

From `scripts/battery_ingest.py:TOOL_TO_AXIS`:

- `knip` — unused JS/TS exports, files, dependencies.
- `jscpd` — code duplication (mechanical, AST-based).
- `lizard` — cyclomatic complexity > 10 + parameter count > 5.
- `vulture` — dead Python code.
- `deadcode` — dead Go code.
- `gocyclo` — Go cyclomatic complexity > 10.
- `dupl` — Go duplication.
- `cargo-machete` — unused Rust dependencies.

Tool observations carry `confidence: 0` until contextual validation establishes whether removal, wiring, or no change is warranted.

## Severity calibration

- 🔴 High — never. Simplification is shape-preserving; nothing here blocks ship.
- 🟠 Medium — clear over-engineering with a concrete fix (single-use factory, premature config flag, `> 3` parameters, nested ternary).
- 🟢 Low — stylistic preference, `> 10` CCN without a concrete refactor in mind, dead code with ambiguous removal cost.

Cap severity at 🟠 Medium for stylistic simplification calls (over-engineering is judgment-heavy — keep it out of the High tier).

## Repo-kind branches

| `repo_kind` | Behavior |
|-------------|----------|
| `skills` | Bundled `scripts/` get full simplification review. Prompt-only skills receive review for redundant instructions, contradictory gates, unnecessary workflow steps, and complexity without outcome benefit. |
| `app`, `library` | Full review. |
| `python` | Full review; `vulture` findings feed in. |
| `rust` | Full review; `cargo-machete` findings feed in. Inline `#[cfg(test)]` modules are not dead code. |
| `go` | Full review; `deadcode` / `gocyclo` / `dupl` feed in. |
| `docs` | Review duplication and unnecessary complexity that materially obscure the document's purpose. |
| `monorepo` | Per-workspace specialization parked; subagent treats as a code repo. |
| `unknown` | Full review with all available tool inputs. |

## Subagent inputs

- `scope.json` — repo kind, languages, files touched.
- `tool-findings.jsonl` filtered to `axis: simplification` — knip, jscpd, lizard, vulture, deadcode, gocyclo, dupl, cargo-machete.
- The diff itself.
- This brief.
- `references/anthropic-verbatim.md` — rubric + false-positive list.
