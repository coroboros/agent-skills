# Optimize project instructions

Use the [official Claude Code memory guidance](https://code.claude.com/docs/en/memory) for loading behavior and current recommendations. The under-200-line target is a guideline; this skill does not predict a percentage improvement from shortening a file.

## Establish the accepted scope

An audit returns findings. An authorized optimization edits the existing owner files and verifies them. Preserve explicit review checkpoints and persistent-memory permissions. Do not migrate a personal rule into shared instructions solely to shorten the root.

Read the target and instructions it actually routes to. Inspect relevant commands, configuration and callers before removing a rule. A repository-wide instruction audit needs broader coverage than a correction to one paragraph.

## Review candidates semantically

The deterministic audit reports six categories, not automatic deletion instructions:

| Candidate | Decision to verify |
| --- | --- |
| Linter-enforced rule | Does configured tooling enforce the same behavior? Keep the command or tool choice if it is needed to invoke that enforcement. |
| Obvious repository information | Does the pointer prevent a likely mistake or expensive rediscovery? Keep useful entry points; remove redundant inventories. |
| Marketing or vision | Does it affect product or writing decisions in this repository? Move business prose to its owner rather than losing an accepted constraint. |
| Redundant specification | Keep one authoritative source and a useful pointer; verify the source contains the fact before deleting the copy. |
| Verbose explanation | Preserve the reason and exception in fewer words. |
| Generic best practice | Replace with a concrete project decision when one exists; otherwise remove the empty slogan. |

A mention of Biome, ESLint or Prettier does not prove bloat. A scanner match is a candidate whose validity depends on meaning and project configuration.

## Shape the result

Include only sections the project needs: purpose, relevant commands, ownership pointers, constraints and nonstandard workflow. Retain the minimal `CLAUDE.md` adapter when `AGENTS.md` owns shared instructions. Use ordinary links for conditional `.claude/rules/` files; eager `@` imports load immediately and should be reserved for universal content.

Explain material removals or changed behavior in the diff report. Preserve genuine user approvals and required checks while removing repeated requests for permission already granted.

## Example

Before: a paragraph repeats every formatter setting and also identifies the repository's required formatter command.

After: retain the verified command and point to the actual configuration. Remove only settings that the command enforces. This reduces duplication; no task-quality or cost percentage is inferred.

## Verify

Resolve imports outside literal code, validate scoped-rule frontmatter and globs, and check commands against the repository. Exercise a representative task and a near miss when routing or scope changes. Report behavioral checks separately from static conformance. A shorter file with a lost boundary is a regression.
