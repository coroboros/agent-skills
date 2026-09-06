# Step: revise

Archive the current `TRACK.md` and emit a refined one based on listener feedback.

## Inputs

- `<path>` — path to the project folder containing `TRACK.md`. Either a single-track folder (`{track-slug}/`) or an album track folder (`projects/{album-slug}/tracks/{nn-slug}/`).
- `<feedback>` — natural-language listener notes. Examples: "chorus too dry, vocals washed out", "raise the energy in the bridge, drop the hi-hats in verse 2", "this nailed it but the BPM feels 5 too slow".

## Workflow

### 1. Resolve and read

- Resolve `<path>` to its `TRACK.md`. Error out if missing — suggest `create` instead.
- Revise a given `TRACK.md` one invocation at a time; independent tracks may be
  revised in parallel.
- Read the existing TRACK.md, the iteration log, and any sibling `ALBUM.md` and bound `ARTIST.md` (if `-f` is passed or the parent project has one).

### 2. Determine next version number

Read existing names matching `v<number>.md` in `versions/`. Next version is `v{N+1}` where `N` is the greatest numeric suffix, or zero when none exists. Gaps and unrelated filenames do not reuse a prior number. First revision archives the initial as `v1`.

### 3. Archive the current take

Copy current `TRACK.md` to `versions/v{N+1}.md` verbatim with exclusive creation. The canonical take stays in place until step 8. Use the standard library's `xb` mode so an existing archive can never be overwritten, including a destination created concurrently:

```bash
python3 - "{path}" <<'PY'
from pathlib import Path
import re
import sys

track_dir = Path(sys.argv[1])
content = (track_dir / "TRACK.md").read_bytes()
versions = track_dir / "versions"
versions.mkdir(exist_ok=True)
numbers = [int(match.group(1)) for entry in versions.iterdir()
           if (match := re.fullmatch(r"v([0-9]+)\.md", entry.name))]
archive = versions / f"v{max(numbers, default=0) + 1}.md"
with archive.open("xb") as output:
    try:
        output.write(content)
    except OSError:
        archive.unlink()
        raise
print(archive)
PY
```

Keep the emitted archive path for the revision report. Any archive error stops the revision before the canonical file changes; a collision is reported, never retried by overwriting it.

### 4. Parse feedback into change axes

Categorise the feedback by which prompt surface it targets:

| Feedback flavour | Target surface | Examples |
|------------------|----------------|----------|
| Mix / sound | Style of Music + Sliders + Exclude Styles | "too wet", "vocals dry", "bass-heavy" |
| Performance | Lyrics inline cues + parentheticals | "chorus stronger", "whisper the verse" |
| Arrangement | Lyrics structural brackets + ALBUM.md transitions | "drop drums in bridge", "add a pre-chorus" |
| Tempo / key | Frontmatter + Style of Music | "BPM too slow", "wrong key" |
| Identity / vocal | Voice / Custom Model + Style vocal descriptor | "vocal feels generic", "should sound more raspy" |
| Vibe drift | Style descriptor stack rewrite | "lost the moodiness", "feels too clean now" |

A single feedback message can hit multiple axes. Parse each independently. When the feedback is short ("better!" / "love it but the chorus is weak"), make minimal changes — only what the words specifically request.

### 5. Synthesise the revised prompts

For each touched axis, apply the targeted edit while preserving everything else:

- **Mix / sound** — adjust the Style descriptors (add `dry close-mic vocal`, remove `reverb-drenched`), tighten sliders, add specific Exclude Styles tags.
- **Performance** — add `(whispered)` / `(building intensity)` / `[Belted, layered harmonies]` cues at the targeted section.
- **Arrangement** — restructure bracket order, add `[Pre-Chorus]`, drop a `[Bridge]` if the feedback says it dragged.
- **Tempo / key** — update frontmatter `bpm` and `key`, restate in the Style of Music field.
- **Identity / vocal** — when no Voice is attached: rewrite the vocal descriptor in Style; when a Voice is attached: drop the descriptor (it conflicts) and raise Audio Influence by 5–10 percentage points.
- **Vibe drift** — re-anchor on the original Rationale; restore descriptors that were lost to a previous iteration.

Hold prompts that the feedback did not touch. Do not "improve" untouched lines — the user is reacting to a specific delta, not asking for a full rewrite.

### 6. Update the iteration log

Append an entry. The format:

```
- v{N+1} ({YYYY-MM-DD}): <change axes touched>; <one-line summary of the diff>; <kept | archived>
```

Example:

```
- v3 (2026-05-09): mix + performance — drop reverb-drenched, add (whispered) to verse 1, raise Audio Influence 78→85; archived v2
```

### 7. Validate the candidate

Allocate a unique temp folder for this invocation so another track's revision
cannot replace the candidate between validation and installation:

```bash
python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="suno-revise-"))'
```

Keep the printed absolute path as `$REVISION_DIR` (substitute that literal path
when shell state does not persist). Write the revised candidate to
`$REVISION_DIR/TRACK.md`, keeping the canonical filename because the validator
dispatches on it. Update frontmatter `revised: YYYY-MM-DD` in the candidate; leave
`created:` untouched.

`$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing the skill's SKILL.md elsewhere.

```bash
python3 "$SKILL_DIR"/scripts/validate.py "$REVISION_DIR/TRACK.md"
```

Same RED/YELLOW/GREEN handling as `create`. RED (exit 1) blocks the move in step 8 — `{path}/TRACK.md` still holds the previous take, never touched by RED content. Fix the temp candidate and re-validate; no re-archiving needed (only the candidate is re-synthesised; `versions/v{N+1}.md` stays as the previous take).

### 8. Write the new TRACK.md

On GREEN or YELLOW (exit 0 or 2), `mv` that same `$REVISION_DIR/TRACK.md` over
`{path}/TRACK.md`, then remove this invocation's empty temp folder. Keep the
candidate on failure. The archived `versions/v{N+1}.md` is the previous take,
untouched; the new TRACK.md is the current best.

### 9. Print the user-facing summary

- Path to the new TRACK.md
- One-line summary of changes per axis
- Validator findings (YELLOW only — RED is blocked above)
- Pointer to the archive: `Previous take saved at {path}/versions/v{N+1}.md`
- Copy-paste reminder: `Open {path}/TRACK.md and re-paste the Style / Lyrics / Exclude blocks into Suno.`

## Edge cases

- **Feedback appears contradictory** — first distinguish its musical dimensions: more rhythmic energy and lower loudness can coexist. State a routine interpretation and revise; ask through available question tooling or plain text only when the intended result remains irreconcilable or materially ambiguous.
- **Feedback names a section that doesn't exist** ("the bridge feels off" but there is no `[Bridge]`) — surface, ask whether to add one or whether the user means a different section.
- **Feedback targets audio that the prompt cannot reach** ("the vocals sound autotuned" when no autotune is in the prompt) — note that Suno's voice synthesis can introduce unsolicited processing; suggest adding `no autotune` to Exclude Styles, or attaching a Voice profile.
- **No `versions/` directory yet** — first revise on a v0 track. Create the directory; archive the v0 TRACK.md as `versions/v1.md`.
- **Iteration count > 10 without convergence** — soft stop. Surface to the user that Suno-style iteration usually converges in 3–6 takes; persistent dissatisfaction may mean the brief itself needs rewriting. Suggest `/forge` or a fresh `create` with a tightened brief.
