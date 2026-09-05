# Agent Skills Open Standard

Skills in this repo use the [Agent Skills specification](https://agentskills.io/specification), with documented Claude Code extensions and local authoring policies below. Extension support depends on the target loader; strict upload and packaging paths may reject them.

## Required

- **`SKILL.md`** at the folder root. Only required file.
- **Folder name** matches `name` frontmatter field (kebab-case, `[a-z0-9-]`, max 64 chars, no leading/trailing hyphen, no `--`).

## Frontmatter fields (canonical spec — 6 fields only)

| Field | Required | Constraint |
|-------|----------|------------|
| `name` | Yes | Matches folder name. Kebab-case. Max 64 chars. |
| `description` | Yes | 1–1024 chars. Covers *what* + *when to use*. |
| `license` | No | License name or bundled file reference. |
| `compatibility` | No | Max 500 chars. Environment requirements. |
| `metadata` | No | Arbitrary string→string map. Namespace your keys. |
| `allowed-tools` | No | Space-separated pre-approved tools. Experimental. |

**Custom fields go under `metadata:`** — never at the top level. Example: `metadata.author`, `metadata.dependencies`.

## Local naming and markup policy

- Avoid names containing `anthropic` or `claude` to prevent first-party confusion. This is repository policy, not a restriction in the open specification.
- Do not use XML markup in frontmatter. Argument placeholders such as `<path>` are allowed. This is an authoring convention, not a YAML format constraint.

### Narrow exception — first-party filename conventions

A skill name MAY include a reserved substring when the skill operates directly on a first-party Claude filename or path convention and any alternative loses essential semantic clarity. Example: `claude-md` (operates on `CLAUDE.md`). Declare the exception in the skill's `## Rules` or `## About` section, not silently. Do not invent new exceptions — these are case-by-case and reviewed in PR.

## Body

No format restrictions. Plain Markdown is the norm — matches the reference implementations in [anthropics/skills](https://github.com/anthropics/skills) and [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills).

## Size budget

- Keep SKILL.md under 500 lines and approximately 5,000 tokens as repository policy, informed by the specification's progressive-disclosure guidance.
- Descriptions load during discovery. Lead with the distinguishing trigger; the specification's approximate 100-token metadata estimate is guidance, not a universal loader limit.

Exceed the budget only when genuinely needed. Offload detail into `references/`, `scripts/`, `assets/`, or `steps/` via progressive disclosure.

## Optional folders

- `scripts/` — executable code
- `references/` — docs loaded on demand
- `assets/` — templates, images, data
- Any additional file/directory is tolerated but should earn its place.
