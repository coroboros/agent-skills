# Repo Conventions

UX and structural conventions specific to `coroboros/agent-skills`, layered on top of the [open standard](./agentskills-spec.md) and [Claude Code extensions](./claude-code-skills.md).

## Flag convention

Skills that accept flags use a consistent lowercase/uppercase pattern parsed from `$ARGUMENTS`:

| Flag | Meaning |
|------|---------|
| `-s` | **S**ave output to `~/.claude/output/{project}/{skill}/` (global — see Output paths) |
| `-S` | Disable save (override any ambient save mode) |
| `-f <path>` | **F**eed — consume another skill's output as input (pipeline chaining) |
| `-a`, `-b`, `-e`, `-i`, `-r` | Skill-specific — document in the skill's `## Parameters` section |

Pattern: lowercase flag enables, uppercase flag disables. Keep the convention consistent across skills so users can rely on the shorthand.

## Output paths

Skill scratch output is **global** — never inside a working tree, so it cannot pollute any repo and it survives parallel worktrees:

- Single-file producers save to `~/.claude/output/{project}/{skill}/{skill}-{slug}.md`. The `{skill}-` prefix makes the file self-describing — `spec-oauth-auth.md` reads as a spec at a glance, even out of context — and the `{slug}` suffix is the intent, so multiple intents coexist (`spec-oauth-auth.md` and `spec-db-migration.md` side by side). Re-running the same intent overwrites only that one file.
- `{project}` = kebab-cased basename of the git toplevel, else the cwd basename outside a git repo:

  ```bash
  root=$(git rev-parse --show-toplevel 2>/dev/null || pwd)   # identical to apex's scripts
  project=$(basename "$root" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-*//; s/-*$//')
  : "${project:=unnamed}"   # all-non-alphanumeric basename → empty kebab → fallback
  ```

  Each git worktree resolves to its own toplevel, so parallel worktrees of one repo separate by `{project}` on their own. Two distinct repos sharing a basename share a `{project}` folder — accepted limitation, not collision-proofed.
- `{slug}` = kebab of the intent (topic / idea / short description), max 5 words.
- **Structured producers keep their shape** under the same `~/.claude/output/{project}/{skill}/` prefix: apex → ordered `{NN-feature}/` task dirs (`-r` resume needs ordering); markitdown / audio-loop → per-input `{slug}/` subfolders; design-system → per-subcommand `{sub}/`. Only single-file producers take the `{skill}-{slug}.md` filename.
- **Path handoff — no magic.** A producer reports the **fully-expanded absolute path** (`$HOME` and the project root resolved) and inlines that literal path in any bridge command it suggests. Scripts compute and echo the absolute path; skills surface it verbatim. Committed artifacts (SKILL.md, README, commit/PR bodies) use the `~/.claude/output/{project}/{skill}/…` placeholder form — the privacy rule forbids a real home path in shared files; the expanded path is in-session only.

Future skills MUST adopt this scheme — it is a conformance gate in the skill-authoring loop. A skill that writes inside a working tree is a review failure.

## Pipeline chaining

Skills compose via the `-f` flag. A producer saves its file, then reports the **fully-expanded absolute path** and the exact next command with that path inlined:

```
/forge -s "oauth authentication"
  saved → /Users/<you>/.claude/output/<project>/forge/forge-oauth-authentication.md
  next  → /apex -f /Users/<you>/.claude/output/<project>/forge/forge-oauth-authentication.md
```

**`-f <path>`** — the value is an **explicit path, used verbatim**. The consumer `Read`s exactly that path. No filename reconstruction, no `{producer}`/`{project}` inference, no glob, no "latest" guess — the producer already printed the real path and the bridge carries it literally. A path that does not exist → fail loud (regenerate via the producer, or correct the path). That is the whole contract: paths are explicit, never magic.

## Cross-skill references

Skills install standalone — `npx skills add coroboros/agent-skills --skill <name>` copies one folder, so a sibling skill's bundled files are not on disk. A skill MUST NOT point the model at another skill's files by a path that assumes co-installation.

- **Forbidden** — a relative path escaping the skill folder (`../<other>/…`, `../../<other>/…`) or a raw repo path (`skills/<other>/…`). On a solo install the target does not exist and the `Read` fails.
- **Cite by external link** — point at the source of truth: the canonical upstream (the DESIGN.md format lives at `github.com/google-labs-code/design.md`) or, for our own elaboration, the blob URL `https://github.com/coroboros/agent-skills/blob/main/skills/<other>/references/<file>.md` paired with the sibling by slash-name (`/<other>`).
- **Optional runtime cooperation** — when a skill *uses* a sibling at runtime (a script, a governance handoff), detect-or-degrade: try `${CLAUDE_SKILL_DIR}/../<other>/…`, then `~/.claude/skills/<other>/…`, then `~/.agents/skills/<other>/…`, and on miss state the fallback and continue. `humanize-en` (`extract_rules.py`) and `apex` (the code-ultrareview orchestrator) are the reference implementations.

code-ultrareview's Documentation axis flags a raw `skills/<other>/…` citation — the standing audit for drift.

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
| `coding-skills` | Coding Skills |
| `design-skills` | Design Skills |
| `claude-code-skills` | Claude Code Skills |
| `media-skills` | Media Skills |
| `productivity-skills` | Productivity Skills |
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
├── _meta/                            # Universal cross-skill tests
│   ├── _helpers.py
│   ├── test_skill_frontmatter.py
│   ├── test_skill_structure.py
│   ├── test_marketplace.py
│   ├── test_readme_parity.py
│   ├── test_evals_shape.py           # JSON schema for evals/evals.json
│   ├── test_evals_content_sampling.py # refuse/escalate + reference routing
│   ├── test_helpers_contract.py      # _helpers.py public API stability
│   └── test_performance_budget.py    # hot-path runtime ceilings
├── _pipeline/                        # Cross-skill cluster integration
│   ├── _contracts.py                 # SSOT for `-f` schema keys per cluster
│   ├── fixtures/                     # Producer→consumer fixtures
│   └── test_*.py
└── <skill-name>/
    ├── __init__.py                   # Empty marker
    ├── fixtures/                     # Optional test inputs
    └── test_*.py
```

**Run all**: `python3 -m unittest discover tests/ -v`
**Run one**: `python3 -m unittest discover tests/<skill-name>/ -v`

Stdlib `unittest` only — no pytest, no third-party deps. Shell scripts are tested via `subprocess.run`. Tests requiring optional CLIs (`ffmpeg`, `pnpm`, `markitdown`) use `@unittest.skipUnless(shutil.which("…"), …)` so the suite passes on any contributor's machine regardless of installed tooling.

**Distinction from `evals/`** — the `skill-creator` flow places LLM behavioral evaluations (`evals/evals.json`) inside the skill folder; that's user-facing documentation of expected behavior. Unit tests of bundled scripts are dev infrastructure and live outside, never installed.

## CI

Two workflows trigger on every pull request and push to `main`:

- `.github/workflows/ci.yml` runs the full `unittest` suite. Branch protection on `main` requires the `tests` status check — red tests block merge.
- `.github/workflows/scan-skills.yml` calls Cisco's `skill-scanner` reusable workflow (policy `balanced`, fail-on `critical`) against the `skills/` tree. SHA-pinned to a tagged release; Dependabot opens a PR weekly when a new version lands.

## Skill scope declaration

In the root README skills table, mark each skill:

- **`All agents`** — portable, uses only the open-standard frontmatter and no Claude Code-specific features (`$ARGUMENTS`, `argument-hint`, `paths`, etc.).
- **`Claude Code`** — relies on Claude Code extensions. Won't work as-is in Claude.ai or the API.

## Context efficiency

- Every line of SKILL.md costs tokens for every invocation. Be dense, not verbose.
- Offload detail to `steps/`, `references/`, `templates/`, `scripts/`.
- Trust the model's prior knowledge — don't re-explain well-known concepts.
