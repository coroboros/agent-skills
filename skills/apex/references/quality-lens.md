# Quality lens — the code a senior engineer would ship

The review instrument for Plan (kill council), Refine and Examine. Each rule names a violation a reviewer can point to on a specific line. Scope: lines the task adds or changes. Pre-existing code outside the task stays untouched unless the plan reuses it.

## Build ladder

Stop at the first rung that meets every accepted criterion; the plan records the rung per file.

1. Not needed — no criterion requires it.
2. An existing owner in the codebase.
3. The standard library.
4. A platform or framework built-in.
5. A dependency already installed.
6. One line at the call site.
7. Minimal new code.

A new dependency is justified only when it replaces substantial owned code; name it in the plan and respect the project's package maturity and cooldown policy. Violation: new code or a new dependency where a lower rung serves and the plan records no reason.

## One owner (DRY)

- Violation: a second definition of a rule, constant, schema, type or path that must change with the first. Cite both locations.
- Violation: a copied literal, list or type that could derive from its owner.
- Not a violation: similar code with independent reasons to change. A DRY claim without a concrete duplicate is not a finding.

## Minimum structure (KISS, YAGNI)

Violations:

- An interface, abstract class or generic with one implementation or one type argument.
- A helper with one call site, unless its name states a domain concept the inline code hides.
- A wrapper that only delegates or renames.
- An option, flag, environment variable or parameter without a second consumer or an accepted criterion. Injected dependencies are exempt.
- A branch for input no criterion or real caller produces.
- A factory, registry or plugin point without two concrete variants in the diff.
- A compatibility shim where the direct change meets the contract.
- Debug output or temporary scaffolding left in shipped code.

## Responsibilities (pragmatic SOLID)

- Violation: one function that parses, decides and persists. Keep I/O at the edges and decisions pure.
- Violation: a hidden global or service locator. Pass dependencies explicitly.
- Violation: inheritance where composition or a plain function serves.
- Violation: logic at the wrong altitude — a domain rule inside a route or UI handler, or a caller-specific branch inside a shared module.

## Boundaries and errors

- Validate at trust boundaries: user input, network, files, environment, third-party responses, and the public API arguments of a published package.
- Violation: re-checking a value the type system, framework or caller already guarantees.
- Violation: swallowed errors, catch-and-continue, silent fallback defaults, log-and-ignore.
- Handle an error where a caller can act on it; otherwise let it propagate.

## Comments

Default: none added. A comment carries a why the code cannot state: a non-obvious constraint, the cause of a workaround, a spec or upstream-bug reference, a security or performance tradeoff. Docstrings the project's conventions require on public symbols follow those conventions.

Violations: restating the code or its name; history or process words (new, now, updated, previously, added for, per the plan); banners and section dividers; commented-out code; docstrings or annotations on otherwise untouched code; TODO without an owner or issue.

## Names and prose

- Violation: a name without domain meaning (`data`, `info`, `manager`, `util`) or with process meaning (`new`, `v2`, `temp`, `fixed`).
- Messages, logs and docs state one fact per sentence. Violation: a sentence removable without loss, or wording banned by SKILL.md § Writing rules.
- Docs change only when behavior, configuration or a public contract changes.

## Efficiency

Violation: evident waste with a concrete replacement — a query or request per loop iteration, repeated I/O, recomputation of an unchanged value. Micro-optimizations without a measured need are not findings.

## Security floor

No secrets in code, logs or client bundles. Parameterized queries. Shell commands, HTML and file paths built from untrusted input only through escaping or allow-listing APIs. Server-side authorization for every protected action. Least-privilege credentials. A violation here is a defect to fix, never a simplification to apply.

## Never simplified away

- Validation at trust boundaries.
- Error handling that prevents data loss or reports a real failure.
- Security controls and accessibility attributes, including keyboard paths.
- Behavior an accepted criterion or the user requested.
- Tests that distinguish correct behavior from the defect.

## Readability guards

Reject a simplification that nests ternaries, packs logic denser than its neighbors, changes accepted behavior or a pre-existing public signature, or needs a comment to be understood. Readability wins over line count.
