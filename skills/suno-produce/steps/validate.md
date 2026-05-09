# Step: validate

Run the deterministic linter against a `TRACK.md`, `ALBUM.md`, or `MUSIC.md` and report findings. CI-friendly exit codes. The script auto-dispatches by filename.

Aliases: `lint`, `check`. All three behave identically.

## Inputs

- `<path>` — path to a single artifact file (`TRACK.md` / `ALBUM.md` / `MUSIC.md`), a project folder containing one or more, or a directory of project folders. Glob expansion: `validate projects/album-slug/` validates every `TRACK.md`, `ALBUM.md`, and `MUSIC.md` under that tree.

## Workflow

### 1. Resolve target files

- Path ends in `TRACK.md`, `ALBUM.md`, or `MUSIC.md` → validate that one file.
- Path is a directory → recursively walk for all three filenames. Report per-file then a summary.
- Path is missing → error out with a clear message.

### 2. Run the validator

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/validate.py <path/to/artifact-or-folder>
```

The script:
- Detects artifact type from filename (TRACK / ALBUM / MUSIC).
- Parses YAML frontmatter — including block-form nested mappings (e.g., `slider_bias:` in MUSIC.md).
- Runs the type-specific check set (see `SKILL.md` § *Validation contract*).
- Writes a JSON report to stdout.

### 3. Parse the JSON

Schema (full schema in [`../references/track-schema.md`](../references/track-schema.md) § validator output):

```json
{
  "verdict": "GREEN",
  "file": "tracks/01-midnight-letter/TRACK.md",
  "errors": [],
  "warnings": [
    {"check": "descriptor_count", "line": 16, "value": 8, "expected": "4-7", "fix": "Remove 1-4 descriptors from Style"}
  ],
  "info": [
    {"check": "suno_version", "value": "v5.5", "running": "v5.5"}
  ]
}
```

### 4. Format the human report

For a single file:

```
{verdict} — {file}

Errors (RED):
  - [line {N}] {check}: {value} (expected {expected})
    fix: {fix}

Warnings (YELLOW):
  - [line {N}] {check}: {value} (expected {expected})
    fix: {fix}

Info:
  - {check}: {value} (running {running})
```

For multiple files, report per-file then end with a summary line:

```
Summary: {green_count} GREEN, {yellow_count} YELLOW, {red_count} RED across {total} files.
```

### 5. Exit codes

- 0 — all GREEN
- 2 — at least one YELLOW, no RED
- 1 — at least one RED

The skill propagates the script's exit code so this verb is CI-safe (a `git pre-commit` hook can run `python3 scripts/validate.py tracks/*/TRACK.md`).

## When to use

- After hand-editing a TRACK.md (typo fix, manual section adjustment).
- Before committing a track folder to git.
- After a Suno model upgrade to flag any v5.5 → v6 incompatibility (the future `migrate` verb will use this).
- As a sanity check on an album: `validate projects/album-slug/` walks every track in one call.

## When not to use

- For musical / aesthetic judgment (this is a syntactic linter, not a critic). Listening to the Suno output and using `revise` is the aesthetic loop.
- For Suno API quota or rate-limit checks (none of those apply — this skill never calls Suno).
- For mixing-engineer concerns (the linter knows nothing about loudness, EQ, or stereo balance — Suno's UI exposes those, and Suno Studio 1.2's Remove FX / Warp Markers handle them post-generation).
