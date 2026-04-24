# Repo Conventions

UX and structural conventions specific to `coroboros/agent-skills`, layered on top of the [open standard](./agentskills-spec.md) and [Claude Code extensions](./claude-code-skills.md).

## Flag convention

Skills that accept flags use a consistent lowercase/uppercase pattern parsed from `$ARGUMENTS`:

| Flag | Meaning |
|------|---------|
| `-s` | **S**ave output to `.claude/output/{skill}/{slug}/` |
| `-S` | Disable save (override any ambient save mode) |
| `-f <path>` | **F**eed — consume another skill's output as input (pipeline chaining) |
| `-a`, `-b`, `-e`, `-i`, `-r` | Skill-specific — document in the skill's `## Parameters` section |

Pattern: lowercase flag enables, uppercase flag disables. Keep the convention consistent across skills so users can rely on the shorthand.

## Output paths

- Default save location: `.claude/output/{skill-name}/{slug}/`
- `{slug}` is kebab-case, derived from the argument (max 5 words).
- Skills that produce multiple outputs write sibling files under the same `{slug}/` directory.

## Pipeline chaining

Skills are composable via the `-f` flag. A skill passes its saved output to the next skill:

```bash
/brainstorm -s "topic"              → .claude/output/brainstorm/topic/brief.md
/spec -s -f brief.md "..."          → .claude/output/spec/topic/spec.md
/apex -f spec.md                    → implementation
```

Contract: producer saves a single canonical file under `{slug}/`. Consumer reads it via the path passed to `-f`.

## Install model

Distribution is git-based via [skills.sh](https://skills.sh):

```bash
# All skills
npx skills add coroboros/agent-skills

# Individual skill
npx skills add coroboros/agent-skills --skill <name>
```

No `.skill` packages, no bespoke installer. The installer copies the skill folder into the user's Claude Code skills directory.

## Plugin marketplace

The repo ships a Claude Code plugin marketplace manifest at `.claude-plugin/marketplace.json`. It groups skills into **plugins**, and `skills.sh` uses the plugin `name` (title-cased) as the skill's category label in `npx skills list` and on the directory site.

**Current plugins:**

| Plugin | Category label |
|--------|----------------|
| `workflow-skills` | Workflow Skills |
| `design-skills` | Design Skills |
| `claude-code-skills` | Claude Code Skills |
| `media-skills` | Media Skills |
| `writing-skills` | Writing Skills |

See `.claude-plugin/marketplace.json` for the authoritative per-plugin skill list.

**Rules:**

- **Every skill must belong to a plugin.** No "General" bucket — that's how lambda skill repos look, and it's the exact thing we avoid by declaring plugins explicitly.
- When adding a new skill: either append it to an existing plugin's `skills` array, or create a new plugin if it genuinely represents a new category (≥2 skills justifies the split).
- Plugin `name` is kebab-case and ends with `-skills` (e.g., `workflow-skills`).
- Plugin `description` is one line, under ~120 chars.
- After editing `marketplace.json`, verify locally with `npx skills add /absolute/path/to/agent-skills -l` — the listing should show the title-cased plugin names as category headers with no "General" section.

## Repo layout

```
coroboros/agent-skills/
├── README.md              # User-facing — install, skills table, pipeline
├── CLAUDE.md              # Agent-facing — imports .claude/rules/
├── LICENSE.md
├── .claude/
│   └── rules/             # Canonical repo-specific rules, imported by CLAUDE.md
├── .claude-plugin/        # Plugin marketplace manifest (category grouping)
│   └── marketplace.json
├── assets/                # Shared brand assets (logo, icons)
└── skills/
    └── {skill-name}/
        ├── SKILL.md       # Required — agent instructions + user-readable workflow
        ├── steps/         # Optional — progressive step files
        ├── templates/     # Optional — output templates
        ├── scripts/       # Optional — automation scripts
        └── references/    # Optional — reference material
```

**No `README.md` at the skill root.** User documentation for each skill lives in the root `README.md` per-skill details section. Subfolders (`templates/`, `scripts/`, `references/`) may contain a `README.md` for maintainer-facing internal documentation when it genuinely earns its place.

## Skill scope declaration

In the root README skills table, mark each skill:

- **`All agents`** — portable, uses only the open-standard frontmatter and no Claude Code-specific features (`$ARGUMENTS`, `argument-hint`, `paths`, etc.).
- **`Claude Code`** — relies on Claude Code extensions. Won't work as-is in Claude.ai or the API.

## Context efficiency

- Every line of SKILL.md costs tokens for every invocation. Be dense, not verbose.
- Offload detail to `steps/`, `references/`, `templates/`, `scripts/`.
- Trust the model's prior knowledge — don't re-explain well-known concepts.
