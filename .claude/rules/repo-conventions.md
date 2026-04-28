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
/brainstorm -s "topic"              → .claude/output/brainstorm/topic/brainstorm.md
/spec -s -f brainstorm.md "..."     → .claude/output/spec/topic/spec.md
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

## Testing

Unit tests live at the repo root in `tests/<skill-name>/`, **never** inside skill folders. Rationale: `skills.sh` and Claude Code's plugin marketplace copy the entire `skills/<name>/` directory to the user's machine on install — tests inside that tree become install bloat the user pays for and never runs.

```
tests/
├── _meta/                      # Universal cross-skill tests
│   ├── _helpers.py
│   ├── test_skill_frontmatter.py
│   ├── test_skill_structure.py
│   ├── test_marketplace.py
│   └── test_readme_parity.py
└── <skill-name>/
    ├── __init__.py             # Empty marker
    ├── fixtures/               # Optional test inputs
    └── test_*.py
```

**Run all**: `python3 -m unittest discover tests/ -v`
**Run one**: `python3 -m unittest discover tests/<skill-name>/ -v`

Stdlib `unittest` only — no pytest, no third-party deps. Shell scripts are tested via `subprocess.run`. Tests requiring optional CLIs (`ffmpeg`, `pnpm`, `markitdown`) use `@unittest.skipUnless(shutil.which("…"), …)` so the suite passes on any contributor's machine regardless of installed tooling.

**Distinction from `evals/`** — the `skill-creator` flow places LLM behavioral evaluations (`evals/evals.json`) inside the skill folder; that's user-facing documentation of expected behavior. Unit tests of bundled scripts are dev infrastructure and live outside, never installed.

## CI

`.github/workflows/ci.yml` runs the full `unittest` suite on every pull request to `main` and every push to `main`. Branch protection on `main` requires the `tests` status check — red CI blocks merge.

## Skill scope declaration

In the root README skills table, mark each skill:

- **`All agents`** — portable, uses only the open-standard frontmatter and no Claude Code-specific features (`$ARGUMENTS`, `argument-hint`, `paths`, etc.).
- **`Claude Code`** — relies on Claude Code extensions. Won't work as-is in Claude.ai or the API.

## Context efficiency

- Every line of SKILL.md costs tokens for every invocation. Be dense, not verbose.
- Offload detail to `steps/`, `references/`, `templates/`, `scripts/`.
- Trust the model's prior knowledge — don't re-explain well-known concepts.
