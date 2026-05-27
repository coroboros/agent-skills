# Axis: Documentation (key `documentation`)

Public API doc completeness, README drift on public-surface changes, ADR drift, and prose hygiene on PR body + commits + user-facing `*.md` files in the diff. The axis combines what `docs-version` and `prose-hygiene` covered as separate lenses — single axis, one subagent, two concerns.

## In scope (HIGH SIGNAL)

### Doc completeness + version

- **Public API change without doc update** — new exported function / class / CLI flag / config option without a matching docstring, README section, or man page entry.
- **README drift on public-surface change** — README claims a behavior the diff just changed (or removed).
- **ADR drift** — `docs/adr/` references a decision the diff overrides.
- **Version artifact not bumped** — per the repo's release rule (see Repo-kind branches below for the version-source matrix).
- **CHANGELOG missing on a user-visible change** — when the repo carries one and convention expects an entry.

### Prose hygiene (PR body, commits, user-facing `*.md`)

Apply to four input channels with a tier model:

- **Tier 1 — full prose** (`README*`, `CHANGELOG*`, `RELEASE-NOTES*`, `CONTRIBUTING*`, `docs/**/*.{md,mdx,rst}`): leak + signature + authoring-process + defensive-negation + rule-restatement + AI vocabulary + em-dash density + length overflow + CC subject shape.
- **Tier 2 — leak-only** (`SKILL.md`, `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.claude/rules/`, source files): leak + signature + authoring-process only. Style/length/vocab do not apply to model instructions or source code.
- **PR title** — leak + signature + authoring-process (one-line title escapes style checks).
- **PR body** — Tier 1 checks + length budget (≤ 5 summary bullets · ≤ 8 test plan items · ≤ 80 lines soft / > 150 hard).
- **Commit subject + body** — Tier 1 checks (subject ≤ 72 chars · body line ≤ 100 chars wrap · body ≤ 20 non-blank lines) + Conventional Commits shape on the subject.

#### Leaks (always High severity)

| Pattern | Reason |
|---------|--------|
| `/Users/<name>/`, `/home/<name>/`, `C:\Users\<name>\` | Local path leak |
| `<user>@<gmail\|icloud\|yahoo\|hotmail\|outlook\|proton\|me\|aol>.<tld>` | Personal email |
| `<Name>'s-MacBook…` style hostnames | Machine identifier |
| `Co-Authored-By: Claude` / `🤖 Generated with` / `Generated with [Cc]laude` / `As an AI…` | AI signature footer |
| Authoring-process paths (`brand-voices/`, `BRAND-VOICE*.md`) in path context | Authoring-tool leak |

#### AI vocabulary (capped 3 per term per artifact)

`delve`, `tapestry`, `intricate`, `pivotal`, `testament`, `underscore`, `crucial`, `garner`, `showcase`, `additionally`, `moreover`, `furthermore`, `indeed`.

#### Em-dash density

> 1 em-dash per 100 words → finding (only when the artifact has ≥ 100 words).

#### Defensive negations (Medium)

`(?:The|This|Our)\s+(?:lens|skill|script|tool|check|detector|orchestrator)\s+never\s+(?:names?|mentions?|references?|uses?|exposes?|hardcodes?|leaks?)` — skill-subject negation.

Allowlist on the same line suppresses the match: uppercase `\bNEVER\b`, `never fail silently`, `never break the public API`, `never aborts`, `never advertises`, `never silent-drop`.

#### Author-coordinate language (High)

Tokens that require the reader to share the author's mental model — useful at authoring time, noise to anyone consuming the shipped artifact.

| Pattern | Example | Fix |
|---------|---------|-----|
| `\bWS-[1-9][0-9]?\b` | `Runs scripts/run_battery.sh (WS-2)` | Translate to a domain fact: `Runs scripts/run_battery.sh — deterministic CLI dispatch`. |
| `the prior <file>\.(py\|sh\|bash)` | `from the prior aggregation.py` | Describe the current state, not the file it replaced. |
| `carried verbatim from` | `carried verbatim from audit_signals.py` | Same — describe what the code does now, not its lineage. |
| `\bthe rebuild\b` | `every WS-6 acceptance criterion` of `the rebuild` | Describe the architecture as it stands, not the path that got it here. |
| `\bspec AC\b` (NOT `Spec AC closure`) | `validators never see them (spec AC)` | Describe the check directly — what is verified, not the spec section that asks for it. |

The repo's `tests/_meta/test_no_internal_label_leak.py` CI gate blocks these patterns at merge. The Documentation axis is the in-PR review feedback signal — surface the same family as 🔴 High findings on the offending `file:line` so the author can fix before the CI red. Per-line opt-out `# noqa: internal-label` (or `<!-- noqa: internal-label -->` in Markdown) suppresses both layers when the prose legitimately names the anti-pattern.

Allowlist files that legitimately document the format (forge produces `### WS-N:` spec headings; apex teaches the rule with the literal `WS-3` example) — surface as informational rather than as findings.

## Out of scope (false positives — silence at source)

Anchor: `references/anthropic-verbatim.md` § False-positive taxonomy.

- Pre-existing prose issues on unchanged paragraphs.
- Markdown formatting nits the `markdownlint-cli2` tool already flags as Low — no doubling.
- Style rules the project explicitly opts out of via `.markdownlint*` or `.vale.ini`.
- AI vocabulary in fenced code blocks (those are examples, not prose).

## Tool inputs (Phase 2)

From `scripts/battery_ingest.py:TOOL_TO_AXIS`:

- `markdownlint-cli2` — Markdown lint findings.
- `vale` — prose lint when `.vale.ini` is present.

Both carry `confidence: 100` and skip validators. The prose-hygiene LLM judgment layer sits on top of these signals.

## Severity calibration

- 🔴 High — leak (local path, personal email, AI signature, authoring-process trace), missing public API doc on a new exported surface, README drift contradicting a just-changed behavior.
- 🟠 Medium — defensive negation, length-budget violation in PR body, missing CHANGELOG on a user-visible change in a repo that carries one.
- 🟢 Low — AI vocabulary occurrence, em-dash density over threshold, markdownlint Low finding, Conventional Commits subject in a repo that does not auto-adopt CC.

## Repo-kind branches

| `repo_kind` | Version sources + doc parity |
|-------------|------------------------------|
| `skills` | Version: `.claude-plugin/marketplace.json` `.metadata.version` + git tags + `gh release list`. Release notes live in the `gh release create` body — no `CHANGELOG.md` exists, so absence is NOT a finding. README skills-table ↔ marketplace skills entries is the cross-doc check. |
| `app`, `library` | `package.json` `.version` + `CHANGELOG.md` most-recent header + git tags. |
| `python` | `pyproject.toml` `[project].version` (or `setup.py`); `CHANGELOG.md` optional. |
| `rust` | `Cargo.toml` `[package].version`. |
| `go` | Git tags (Go modules use semver tags); `go.mod` for module path. |
| `docs` | Version field in the docs-site config (Docusaurus `versions.json`, MkDocs config). |
| `monorepo` | Per-workspace; axis emits zero version findings at the repo root (per-workspace specialization parked for MVP). |
| `unknown` | Skip version sub-checks; axis emits zero version findings. The `Repo: unknown` header carries the context. |

## Skill routing

When `humanize-en` is installed on the user's machine (`~/.claude/skills/humanize-en/` or `~/.agents/skills/humanize-en/`), the synthesizer appends `→ defer to /humanize-en` under each AI-vocabulary and em-dash-density finding. Otherwise the finding stands on its own.

## Subagent inputs

- `scope.json` — repo kind, languages, files touched, CLAUDE.md chain.
- `tool-findings.jsonl` filtered to `axis: documentation` — markdownlint + vale findings.
- The diff itself.
- This brief.
- `references/anthropic-verbatim.md` — rubric + false-positive list.
