# claude-md init

Create the instruction file requested by the user. Preserve an existing `AGENTS.md` owner and use a thin `CLAUDE.md` adapter when appropriate. Use `scripts/init_structure.sh` only when the user requests starter layout files.

## Detect the project

Read its package/build configuration and relevant existing instructions. Identify actual commands, non-obvious owner files and accepted constraints. Do not fabricate authentication, schema or utility paths from a template.

## Draft and write

Choose only useful sections from `references/section-templates.md`. A compact file can state the purpose, commands, ownership pointers and a few project constraints. Include already-established rules rather than forcing an empty Rules section.

Write within the user's authorized scope and show the concrete result. Ask before an unresolved material storage migration or unapproved persistent-memory change; do not ask again for an already-authorized file creation. Assessment-only requests return a draft without writing.

## Verify

Resolve references, check commands against configuration and validate any scoped rules. Use ordinary links for conditional rules rather than eager imports. Report what was written, verified and still uncertain.
