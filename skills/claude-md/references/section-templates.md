# Optional instruction sections

Select sections that serve the project. These examples are placeholders to replace with verified facts, not a mandatory document shape.

## Purpose

State what the repository produces and who uses it in one or two sentences. Keep product positioning in its owner document unless it changes implementation decisions.

## Commands

Name the actual package script and its purpose, including whether it uses disposable fixtures or external services. Copy commands from the project configuration. A required command is useful even if it can be discovered.

## Ownership pointers

Link the small number of files that own non-obvious behavior. Describe why the file matters. Do not paste the whole directory tree or require reading unrelated files before every edit.

## Project constraints

Record accepted boundaries such as source preservation, compatibility, credentials and publication. A tool choice can belong here; repeated formatter syntax usually belongs in its config. Use plain instructions rather than repeated capitalized emphasis.

## Conditional rules

A rule for TypeScript source may declare:

```yaml
---
paths:
  - "src/**/*.{ts,tsx}"
---
```

Put only guidance relevant to those matching files below it. List the rule in the root using an ordinary link. Eager imports make the guidance unconditional.

## Verification

Describe checks required by the repository and what they establish. Choose additional behavioral checks for the actual change. Do not invent a fixed coverage percentage, number of examples or mandatory failing test for every prose edit.
