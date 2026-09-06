# Project-specific instruction patterns

Use these patterns to locate the owning conventions. They do not prescribe a stack migration or add dependencies.

## Frontend application

Read the current framework and package configuration, relevant component and design-system owner. Document shared tokens and architectural boundaries that are not obvious from a single component. Match the project's server/client conventions instead of inserting generic React prohibitions.

## API service

Find the entry point, shared validation, persistence boundary and existing error contract. Point to the owner. Document required local checks and external-service prerequisites without copying the schema into instructions.

## Python or other language project

Use the actual environment and test commands declared by the project. Do not transplant JavaScript commands, package-manager preferences or linter rules from a template.

## Monorepo

Keep universal decisions at the root and component-specific guidance near its owner. Verify how the active host loads nested instruction files. A concise root index helps route work without requiring an exhaustive repository read for every edit.

## Multiple agent hosts

When `AGENTS.md` is the shared owner, `CLAUDE.md` can import it with `@AGENTS.md`. Keep Claude-specific mechanics in the adapter or scoped references when needed. Host capabilities, permissions and persistent-memory rules still differ; an import does not make enforcement portable.
