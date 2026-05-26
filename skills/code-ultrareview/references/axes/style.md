# Axis: Style (key `style`)

New violations of the project rule hierarchy (CLAUDE.md, `.claude/rules/`, `~/.claude/rules/`) introduced by the diff. Linter-deferred concerns sit here too — the axis surfaces what a human reviewer would call out, not what the linter would.

## In scope (HIGH SIGNAL)

Anchor: `references/anthropic-verbatim.md` § HIGH SIGNAL review criteria (Agent #1 — CLAUDE.md compliance).

- **CLAUDE.md rule violations on changed lines** — quote the exact rule line verbatim. CLAUDE.md is guidance for Claude as it writes code — apply judgment about which rules are review criteria vs writing-only.
- **Linter-deferred concerns** — patterns the linter cannot catch but the project explicitly rejects (e.g., banned import paths in CLAUDE.md, naming conventions the linter does not enforce).
- **Repo conventions in CLAUDE.md / .claude/rules/** — single source of truth, conformance over taste, file-layout conventions, banned vocabulary.

## Out of scope (false positives — silence at source)

Anchor: `references/anthropic-verbatim.md` § False-positive taxonomy.

- **Anything the linter / formatter would catch** — formatting, import ordering, quote style. CI runs these separately (per Agent assumption rule).
- **Rules that are not in CLAUDE.md or `.claude/rules/`** — stylistic preferences without a rule are out. The Documentation axis owns AI vocabulary; the Simplification axis owns over-engineering.
- **Rules called out in CLAUDE.md but explicitly silenced** in the code (e.g., a lint-ignore comment, an `# noqa`).
- **Pre-existing violations on unchanged lines** — out of scope; the diff did not cause them.
- **General code-quality complaints** (test coverage, security, naming) unless CLAUDE.md explicitly requires them.

## Tool inputs (Phase 2)

No deterministic tool findings route to this axis. The Style axis is pure LLM judgment against the CLAUDE.md chain.

## CLAUDE.md chain

From `scope.json["claude_md_chain"]` — ordered root-to-deepest. The validator (Phase 4) re-checks the deepest matching rule first.

Resolution order:
1. `~/.claude/rules/*.md` (user-global)
2. Repo `CLAUDE.md`
3. Repo `.claude/rules/*.md`
4. Nested `CLAUDE.md` in changed directories (per-subtree overrides)

A finding citing a CLAUDE.md rule MUST quote the rule text verbatim and include the path. The validator demotes with "CLAUDE.md rule not found at <path>" when the cited rule is absent.

## Severity calibration

- 🔴 High — CLAUDE.md rule explicitly marked `MANDATORY`, `NEVER`, `CRITICAL`, or equivalent strong term, violated on a changed line.
- 🟠 Medium — CLAUDE.md rule violated, no strong language but the rule is unambiguous.
- 🟢 Low — heuristic violation (the rule is judgment-call language), or a rule the file marks "guidance".

## Repo-kind branches

No branches — rule files are repo-agnostic. The axis reads the CLAUDE.md chain uniformly across all `repo_kind` values.

## Graceful degradation

When the CLAUDE.md chain is empty (`scope.json["claude_md_chain"] == []`), the Style axis runs without a baseline and emits zero findings. The report header surfaces `Style axis: skipped — no rules baseline found`.

## Subagent inputs

- `scope.json` — repo kind, files touched, CLAUDE.md chain (root-to-deepest).
- `tool-findings.jsonl` filtered to `axis: style` — always empty.
- The diff itself.
- This brief.
- `references/anthropic-verbatim.md` — rubric + false-positive list.
- The full text of each CLAUDE.md / rules file in the chain.
