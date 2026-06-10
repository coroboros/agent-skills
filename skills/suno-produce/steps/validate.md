# Step: validate

Run the deterministic linter against a `TRACK.md`, `ALBUM.md`, or `ARTIST.md` and report findings. CI-friendly exit codes. The script auto-dispatches by filename.

Aliases: `lint`, `check`. All three behave identically.

## Copyright contract

The validator hard-blocks artist citations. RED on `in the style of <Name>`, `voice of/like <Name>`, `sounds like <Name>`, `à la <Name>`, `<Name>'s sound/style/voice/era` in either Style or Lyrics. YELLOW on bare title-case proper-noun pairs in Style outside the safe-phrase whitelist. Both rules trace to article §5.1.5 and SKILL.md Rules § *Never name artists or copyrighted entities in prompts*. The fix message carries the legal reasoning (rights exposure) and the functional reasoning (Suno filters/ignores), so the user sees why the rewrite is required.

## Check sets per artifact type

The script dispatches by filename. Verdicts: GREEN (zero issues), YELLOW (warnings only — write proceeds with the warning surfaced), RED (errors — block the write).

### TRACK.md — Suno v5.5 prompt-bundle rules

| Check | Verdict |
|-------|---------|
| Style of Music ≤ 1000 chars, Lyrics ≤ 5000 chars, Title ≤ 100 chars | RED on overflow |
| Style descriptor count 4–7 | YELLOW outside band |
| Slider values 0–100 | RED out of range |
| Exclude Styles ≤ 3 | YELLOW above |
| Bracket metatag canon — Tier 1 GREEN; Tier 3 community tags YELLOW; SFX brackets RED | mixed |
| BPM in Lyrics field | RED |
| Voice attached + vocal descriptors in Style | YELLOW |
| Genre count > 2, conflicting eras | YELLOW |
| **Artist citation patterns** — `in the style of X`, `voice of/like X`, `sounds like X`, `à la X`, `X's sound/style/voice/era` — in Style or Lyrics | **RED** |
| Title-case proper-noun pair in Style (e.g., `Phil Collins`) outside the safe-phrase whitelist | YELLOW |
| `suno_version` mismatch | YELLOW |

### ALBUM.md — concept + tracklist consistency

| Check | Verdict |
|-------|---------|
| `title` non-empty, ≤ 100 chars | RED |
| `release_format` ∈ {EP, Album, Mixtape, Single} | RED |
| Required sections present (Concept / Arc / Tracklist / Transitions) | RED on missing |
| Arc contains all four labels (Opening / Development / Climax / Closing) | YELLOW per missing label |
| `track_count` matches tracklist line count | RED on mismatch |
| Tracklist line shape `nn. Title — BPM — key — feel` | YELLOW per malformed line |
| `created` ISO date | YELLOW on bad format |

### ARTIST.md — artist identity + voice consent

| Check | Verdict |
|-------|---------|
| `artist` non-empty | RED |
| `voice_profile` declared → `voice_consent` required | RED |
| `voice_consent` shape ∈ {`self`, `licensed: <source>`, `public-domain: <source>`} | YELLOW on bad format |
| `custom_model` declared → `custom_model_training_set` recommended | YELLOW |
| `slider_bias.*` values in [0, 100] | RED out of range |
| `rights_posture` ∈ {license-only, licensed, public-domain, unknown} | YELLOW on bad format |
| Required sections present (Artist identity / Voice and Custom Model / Recurring instrumentation / Rights posture) | RED on missing |

## Inputs

- `<path>` — path to a single artifact file (`TRACK.md` / `ALBUM.md` / `ARTIST.md`), a project folder containing one or more, or a directory of project folders. Glob expansion: `validate projects/album-slug/` validates every `TRACK.md`, `ALBUM.md`, and `ARTIST.md` under that tree.

## Workflow

### 1. Resolve target files

- Path ends in `TRACK.md`, `ALBUM.md`, or `ARTIST.md` → validate that one file.
- Path is a directory → recursively walk for all three filenames. Report per-file then a summary.
- Path is missing → error out with a clear message.

### 2. Run the validator

`$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing this SKILL.md elsewhere.

```bash
python3 "$SKILL_DIR"/scripts/validate.py <path/to/artifact-or-folder>
```

The script:
- Detects artifact type from filename (TRACK / ALBUM / ARTIST).
- Parses YAML frontmatter — including block-form nested mappings (e.g., `slider_bias:` in ARTIST.md).
- Runs the type-specific check set (see § *Check sets per artifact type* above).
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
