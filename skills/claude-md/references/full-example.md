# Compact project instruction example

This is an illustrative project with the named files and commands already present. Verify every path and command before adapting it; do not invent the structure to fit the example.

```markdown
# Catalog service

A catalog API used by the storefront and import worker.

## Commands

- `pnpm check` validates formatting and types.
- `pnpm test` runs the local fixture suite without production access.

## Ownership

- `src/catalog/service.ts` owns catalog updates; callers share its validation.
- `docs/catalog.md` defines the import format and compatibility policy.

## Rules

- Preserve existing import fields when changing the parser.
- Keep credentials in the documented local environment; exclude them from git.
- Read the relevant implementation and callers before editing.
- Run affected behavioral tests and the required project checks after changes.
- Publish only within the user's explicit authorization.
```

For a repository whose shared owner is `AGENTS.md`, keep this content there and make `CLAUDE.md` contain only `@AGENTS.md`. Use separate path-scoped rules only when a conditional concern actually exists; list them with ordinary links instead of eagerly importing them.
