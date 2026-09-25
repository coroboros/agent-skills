# Skill Quality Lens

Canonical review instrument for the implementation workflows. Each declared skill carries a byte-identical copy at `references/quality-lens.md`, so the lens travels on independent install and loads only when a step needs it. The `tests/_meta/test_skill_writing_rules.py` test enforces parity; the `scripts/sync_writing_rules.py` script writes the copies.

## Canonical block

The block below, markers included, is the entire file.

```markdown
<!-- canonical:quality-lens:start -->
# Quality lens — the change a senior engineer would ship

Scope: lines the task adds or changes. Pre-existing code outside the task stays untouched unless the plan reuses it.

Code, including scripts and tests, takes every section; its design budget counts new files, exported symbols, abstractions, dependencies, config keys and net lines. Docs, prose and instruction files take Mechanical changes, One owner, Names and prose, Security floor, Never simplified away and Reviewing; configuration also takes Minimum structure. Their budget counts new files, sections, config keys and net lines.

## Mechanical changes

Formatting, a rename that changes no public contract, a one-line fix that changes no control flow, or a typo fix that changes no documented behavior, instruction or configuration value needs no design budget, council or refine pass; its checks suffice. A trust-boundary change is never mechanical.

## Build ladder

Stop at the first rung that meets every accepted criterion.

1. Not needed — no criterion requires it.
2. An existing owner in the codebase.
3. The standard library.
4. A platform or framework built-in.
5. A dependency already installed.
6. One line at the call site.
7. Minimal new code.

A new dependency is justified only when it replaces substantial owned code; name it in the plan and respect the project's package maturity and cooldown policy. Violation: new code or a new dependency where a lower rung serves and no reason is recorded.

## One owner (DRY)

- Violation: a second definition of a rule, constant, schema, type or path that must change with the first. Cite both locations.
- Violation: a copied literal, list or type that could derive from its owner.
- Not a violation: similar code with independent reasons to change. A DRY claim without a concrete duplicate is not a finding.

## Minimum structure (KISS, YAGNI)

Violations:

- An interface, abstract class or generic with one implementation or one type argument.
- A helper with one call site, unless its name states a domain concept the inline code hides or it keeps a decision apart from I/O.
- A wrapper that only delegates or renames.
- An option, flag, environment variable or parameter without a second consumer or an accepted criterion. Injected dependencies are exempt.
- A branch for input no criterion or real caller produces.
- A factory, registry or plugin point without two concrete variants in the diff.
- A compatibility shim where the direct change meets the contract.
- Debug output or temporary scaffolding no criterion requested, left in shipped code.

## Responsibilities (pragmatic SOLID)

- Violation: one function that parses, decides and persists. Keep I/O at the edges and decisions pure.
- Violation: a hidden global or service locator. Pass dependencies explicitly.
- Violation: inheritance where composition or a plain function serves.
- Violation: logic at the wrong altitude — a domain rule inside a route or UI handler, or a caller-specific branch inside a shared module.

## Boundaries and errors

- Validate external input where it enters: user input, network, files, environment, third-party responses, and the public API arguments of a published package.
- Violation: re-checking a value the type system, framework or caller already guarantees.
- Violation: swallowed errors, catch-and-continue, silent fallback defaults, log-and-ignore.
- Handle an error where a caller can act on it; otherwise let it propagate.

## Comments

Default: none added. A comment carries a why the code cannot state: a non-obvious constraint, the cause of a workaround, a spec or upstream-bug reference, a security or performance tradeoff. Docstrings the project's conventions require on public symbols follow those conventions.

Violations: restating the code or its name; history or process words (new, now, updated, previously, added for, per the plan); banners and section dividers; commented-out code; docstrings or annotations on otherwise untouched code; TODO without an owner or issue.

## Names and prose

- Violation: a name without domain meaning (`data`, `info`, `manager`, `util`) or with process meaning (`new`, `v2`, `temp`, `fixed`).
- Messages, logs and docs state one fact per sentence. Violation: a sentence removable without loss, or wording the skill's Writing rules ban.
- In a code task, docs change only when behavior, configuration or a public contract changes.

## Efficiency

Violation: evident waste with a concrete replacement — a query or request per loop iteration, repeated I/O, recomputation of an unchanged value. Micro-optimizations without a measured need are not findings.

## Security floor

A trust-boundary change touches authentication or authorization, parsing of external input, SQL, shell, HTML, path or redirect construction, secrets or cryptography, uploads, cookies or CORS.

No secrets in code, logs or client bundles. Parameterized queries. Shell commands, HTML and file paths built from untrusted input only through escaping or allow-listing APIs. Server-side authorization for every protected action. Least-privilege credentials. A violation here is a defect to fix, never a simplification to apply.

## Never simplified away

- Validation of external input at trust boundaries.
- Error handling that prevents data loss or reports a real failure.
- Security controls and accessibility attributes, including keyboard paths.
- Behavior an accepted criterion or the user requested.
- Tests that distinguish correct behavior from the defect.
- Public signatures that existed before the task.
- Readability: no nested ternaries, logic denser than its neighbors, or code that needs a comment to be understood.

## Reviewing

A verification reviewer (skeptic, refuter) reports defects only: a failing input, an unmet criterion or a trust-boundary gap, each with file:line and a reproduction or concrete execution trace. A missing handler for a failure real callers hit is a defect. A simplification reviewer (council, refine) reports only removals, reuses and shrinks. Neither proposes robustness additions, validation of internal values, new abstractions or style.
<!-- canonical:quality-lens:end -->
```

## Declared quality-lens skills

The sync script and the parity test read this list:

- apex
- ultrapex
- oneshot

Scope rule — process skills that own an implementation workflow end to end. Skills that implement under one of them inherit the lens from the process skill.

## Excluded skills (with reason)

- frontend-dev — owns the visual floor; when it builds under `/oneshot`, `/apex` or `/ultrapex`, the process skill carries the lens.
- award-design — directs the design and reviews the rendered result; frontend-dev builds under a process skill.
- code-ultrareview — user-invoked review with its own simplification axis and severity model.
- forge — thinking-only; never implements.
- agent-creator — emits agent config, not code.
- design-system — governs DESIGN.md tokens, not code.
- claude-md — emits CLAUDE.md, not code.
- brand-voice — emits BRAND-VOICE.md, not code.
- write-clear-readme — emits README.md, not code.
- suno-produce — emits TRACK.md / ALBUM.md, not code.
- scaffold — runs a fixed bootstrap and emits a short status report.
- markitdown — wraps a converter CLI and emits a short status report.
- download-media — wraps a downloader CLI and emits a short status report.
- notion — routes to MCP/CLI and emits a short status report.
- audio-loop — media tooling emitting short status reports.
- video-loop — media tooling emitting short status reports.
- humanize-en — text scrubber; different scope entirely.

## Rules for skill authors

- Edit the lens here, then run `scripts/sync_writing_rules.py`; never edit a skill's copy directly.
- Reference it from each declared skill as `references/quality-lens.md` at the checkpoints that apply it.
- Keep the HTML-comment markers unchanged — they are the extraction contract for the sync script and the parity test.
