# Axis: Style (key `style`)

New violations of the effective project instruction hierarchy or repeated nearby repository conventions introduced by the diff. Linter-deferred concerns sit here too: the axis surfaces what a human reviewer would call out, not what the linter already proves.

## In scope (HIGH SIGNAL)

Anchor: `references/anthropic-verbatim.md` section HIGH SIGNAL review criteria. Anthropic's source names `CLAUDE.md`; this implementation applies the same check to the cross-agent `instruction_chain`.

- **Instruction-rule violations on changed lines** — quote the exact rule line and name its source file. Apply judgment about which instructions govern review versus agent workflow only.
- **Linter-deferred concerns** — patterns an applicable project instruction rejects but deterministic tooling cannot catch, such as banned import paths or file-layout conventions.
- **Repeated neighboring conventions** — only when no instruction baseline exists and at least two nearby examples establish the same convention.

## Out of scope (silenced per Anthropic false-positive taxonomy)

- **Pre-existing violations** on unchanged lines.
- **Rules explicitly silenced in code** through an applicable ignore directive.
- **General code-quality complaints** owned by another axis, unless a project instruction makes the style constraint explicit.
- **Single-example preferences** — one neighboring file never establishes a project convention.
- **Formatting already enforced by an applicable formatter or linter** — deterministic tooling owns it.

## Tool inputs (Phase 2)

No deterministic tool findings route to this axis. Style uses the instruction chain and, only when that chain is empty, concrete neighboring repository evidence.

## Instruction chain

Read `scope.json["instruction_chain"]`, ordered broadest-to-most-specific. It may contain:

1. User-level AGENTS and Claude instruction files.
2. The effective `AGENTS.override.md` or `AGENTS.md` at each relevant project directory, plus the shared `.agents/rules/**/*.md` it references.
3. Claude-specific `CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md`, and `.claude/rules/**/*.md` files.

At one directory, `AGENTS.override.md` replaces `AGENTS.md`; both never apply together. A nested instruction applies only to findings in its subtree. Honor `paths` frontmatter on `.agents/rules` and `.claude/rules` before citing a rule.

A rule-based finding MUST quote the rule text verbatim and include its source path. The validator demotes with `Instruction rule not found at <path>` when the cited rule is absent from the applicable chain.

## Severity calibration

- 🔴 High — an applicable instruction explicitly marked `MANDATORY`, `NEVER`, `CRITICAL`, or equivalent is violated on a changed line.
- 🟠 Medium — an unambiguous applicable instruction is violated without strong severity language.
- 🟢 Low — a changed line violates a repeated neighboring convention while no instruction baseline exists.

## Repo-kind branches

No branches. Instruction files are repo-agnostic, so the axis reads the same chain across every `repo_kind`.

## Graceful degradation

When `scope.json["instruction_chain"] == []`, the Style axis still runs. It may report only a changed-line violation backed by repeated neighboring repository evidence; otherwise it emits zero findings. The report header states `Rules baseline: none — Style used observable repository conventions`; the axis is never marked skipped.

## Subagent inputs

- `scope.json` — repo kind, files touched, and instruction chain.
- `tool-findings.jsonl` filtered to `axis: style` — normally empty.
- The diff itself.
- This brief.
- `references/anthropic-verbatim.md` — rubric and false-positive list.
- Full text of each instruction file in the applicable chain.
