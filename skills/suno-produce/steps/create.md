# Step: create

Synthesise a new TRACK.md (and optionally ALBUM.md) from a music brief. Default verb when no other verb matches.

## Inputs

- `<brief>` — the music description. Free text. Examples: "indie folk track about a long winter", "make me a melodic-trap EP about leaving home, 4 tracks, 2010s lo-fi feel".
- `-f <path/to/ARTIST.md>` — optional. Bind the artifact to an artist identity. Reads voice profile, custom model, recurring instrumentation, rights posture from the bound ARTIST.md.

## Workflow

### 1. Detect album mode

Scan the brief for multi-track signals:

- Words: "EP", "album", "record", "mixtape", "side A / side B", explicit track counts ("4-track", "5 songs"), or numbered track lists in the brief.
- Plural "tracks" or "songs" with no qualifier → ambiguous; ask.

If detected, run `AskUserQuestion` once with two options to confirm (when `AskUserQuestion` is unavailable, ask in plain text and wait for the reply):

- **Album / EP mode (recommended)** — produce `ALBUM.md` with concept and tracklist, plus per-track folders under `tracks/`.
- **Single track only** — produce a single `TRACK.md` and ignore the multi-track signals.

If not detected, proceed in single-track mode without asking.

### 2. Read ARTIST.md if bound

When `-f` was passed, read the file. Extract:

- `voice_profile` (if any) — sets `voice_profile` in TRACK.md frontmatter; drops vocal descriptors from Style; biases Audio Influence to 78%.
- `custom_model` (if any) — sets `custom_model` in frontmatter; drops redundant genre/era from Style.
- `recurring_instruments` — biases the Style of Music descriptor stack toward these.
- `rights_posture` — surfaces in the user-facing summary; not repeated in TRACK.md.

If `-f` is missing, treat as no artist binding. Skip these defaults.

### 3. Auto-detect sufficient specification

Count how many of the five anchor dimensions the brief provides:

| Dimension | Detection signal |
|-----------|------------------|
| Genre | Named genre / subgenre, or near-synonym |
| Mood | Mood adjectives (nostalgic, brooding, euphoric, glacial, etc.) |
| Vocal direction | Gender / register / delivery / "no vocals" / "instrumental" |
| Length target | Time-format like "3:30", or "single", "long-form", "sketch" |
| References | Era ("late-90s", "2010s"), regional scene ("Bristol post-punk"), or sound-fingerprint description |

When `ARTIST.md` is bound, vocal direction counts as supplied.

- **≥ 3 dimensions** → skip the interview, proceed directly to synthesis.
- **< 3 dimensions** → run `AskUserQuestion` for the missing ones (max 4 questions, multi-select where applicable, recommended option first). One round only — do not loop.

### 4. Synthesise the prompt block

Field-by-field. The composing rules live in [`../references/style-and-lyrics.md`](../references/style-and-lyrics.md) (descriptor stack, bracket metatag canon, lyric flow, languages, phonetic/delivery control, SFX warning, consolidated pitfalls). Slider settings and Voice / Custom Model adjustments live in [`../references/sliders-and-personalization.md`](../references/sliders-and-personalization.md). For copy-paste-ready genre recipes, see [`../references/genre-templates.md`](../references/genre-templates.md):

**Style of Music** — 4 to 7 descriptors, ordered: genre → era → mood → instruments → vocal direction. Comma-separated. Front-load the genre. Add BPM as the last item when known. Total ≤ 1000 chars; aim 280–730. When a Voice is attached, omit the vocal-direction descriptor entirely.

**Lyrics** — bracketed structural metatags ([Intro], [Verse 1], [Pre-Chorus], [Chorus], [Bridge], [Outro]) on their own lines. Stack 1–3 inline cues per section: instrumentation, texture, vocal delivery. Use parenthetical cues sparingly for performance direction (`(whispered)`, `(belted)`, `(building intensity)`). Phonetic spelling for unusual proper nouns. Total ≤ 5000 chars. Skip the Lyrics section entirely for instrumental tracks; mark the brief `[Instrumental]` and toggle Suno's Instrumental setting in the user-facing summary. When the user wants help writing or shaping the lyrics — not when they supply finished lines — consult [`../references/songwriting-craft.md`](../references/songwriting-craft.md) for structure, rhyme, meter, hook, and prosody; it aids singable lyrics and never restyles lines the user already wrote.

**Exclude Styles** — 0 to 3 tags. Use sparingly: positives define, negatives refine. Common candidates: `male vocals`, `female vocals`, `autotune`, `heavy distortion`, `pop hooks`, `808s`, `EDM drops`, `drums`, `piano`. Cap at 3 — more produces mush.

**Sliders** — per-genre defaults from [`../references/sliders-and-personalization.md`](../references/sliders-and-personalization.md) § *Slider bands by genre*, adjusted for Voice / Custom Model:

| Genre family | Weirdness | Style Influence | Audio Influence (only if Voice/Model) |
|--------------|-----------|-----------------|---------------------------------------|
| Radio pop | 35–50 | 65–80 | 60–75 |
| Hip-hop / trap | 40–55 | 55–70 | 60–80 |
| Worship / gospel | 25–40 | 70–85 | 70–90 |
| Cinematic orchestral | 55–70 | 45–60 | n/a |
| Ambient / experimental | 70–85 | 35–55 | n/a |
| Indie folk / pop | 30–45 | 70–85 | 70–85 |

Pick the band that best matches the brief; centre within the band; explain in the Rationale.

### 5. Assemble TRACK.md

Use the schema from [`../references/track-schema.md`](../references/track-schema.md). Order strictly: frontmatter → Title → Suno prompt block (Style fenced, Lyrics fenced, Exclude fenced) → Sliders → Voice / Custom Model → Rationale → Iteration log.

The first iteration log entry on `create`:

```
- v0 (YYYY-MM-DD): initial draft from brief — "<one-line brief paraphrase>"
```

The `revise` step appends entries with the same shape.

### 6. Assemble ALBUM.md if album mode

When album mode was confirmed in step 1, produce `ALBUM.md` alongside the per-track files. Schema in `references/track-schema.md` § ALBUM. Sections: concept, arc (opening / development / climax / closing), tracklist (numbered, each line: `nn. Title — BPM — key — feel`), transitions (key changes, BPM ramps, cross-fades), rights-and-distribution placeholder.

For an N-track album, scaffold the `tracks/01-{slug}/`, `tracks/02-{slug}/`, … directories. Synthesise each TRACK.md in the same pass — the album arc informs each track's Rationale section, and the tracklist transitions get cross-referenced from each TRACK.md's iteration log.

### 7. Validate

Run [`../scripts/validate.py`](../scripts/validate.py) on every TRACK.md just-written and on ALBUM.md.

`$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing this SKILL.md elsewhere.

```bash
python3 "$SKILL_DIR"/scripts/validate.py <path/to/TRACK.md>
```

- **GREEN** → write proceeds, no surfacing in summary.
- **YELLOW** → write proceeds, warnings included in user-facing summary verbatim.
- **RED** → block. Fix the issue in the synthesis (re-tighten descriptor count, trim Lyrics, drop SFX brackets) and re-validate. Do not write to disk on RED. Do not ask the user — the model fixes and retries up to twice. If still RED on the third attempt, surface the validator output and stop.

### 8. Emit `.gitignore` if missing

When the project folder has no `.gitignore`, write one with:

```gitignore
audio/
*.wav
*.mp3
*.flac
*.m4a
.DS_Store
```

Audio takes are large and not worth versioning. Prompts are durable; audio is not. The user can override locally if they want to commit a specific take.

### 9. Print the user-facing summary

Output in conversation:

- Path to the TRACK.md (and ALBUM.md if applicable)
- A single-line copy-paste pointer: `Open {path}/TRACK.md, copy the Style / Lyrics / Exclude blocks into Suno's Custom Mode.`
- Slider settings the user needs to set in the Suno UI explicitly (the sliders are not auto-applied — they are emitted as instructions)
- Any YELLOW validator warnings, verbatim
- If ARTIST.md was bound: which artist defaults flowed in, which were overridden by the brief
- Rights reminder if ARTIST.md is set up: short pointer to `references/rights-and-deprecation.md` summary
- **My Taste reminder** when this is the first track for a new artist or an evaluation/A-B run: `Suno's My Taste personalization is default-on. Disable from avatar menu > My Taste during evaluation work — otherwise the variable is uncontrolled.` See [`../references/sliders-and-personalization.md`](../references/sliders-and-personalization.md) § *My Taste*.

### 10. Iteration handoff

End with: `When you've listened, run /suno-produce revise {path} "<feedback>"` — primes the next loop.

## Edge cases

- **Brief names an artist or a copyrighted entity** ("a Sufjan Stevens track", "voice like Adele", "in the style of Daft Punk") — translate to sound-fingerprint descriptors before synthesis. Hard rule, both legal (rights exposure on a discoverable prompt) and functional (Suno filters or ignores the citation, model collapses to averaged tag). The validator will RED any citation pattern that survives. Worked rewrites: "Sufjan Stevens" → "indie folk, intimate fingerpicked acoustic, soft male tenor, banjo, breathy delivery, lo-fi tape warmth"; "Adele-like voice" → "full-throated contralto female, gospel-rasp belt, plate reverb, dry close-mic verse"; "Daft Punk vibe" → "French house, sidechain pump, vocoded vocal, filter sweeps, 4/4 at 120 BPM". Note the translation in Rationale so the user sees what was rewritten and why.
- **Brief is in a non-English language target** (e.g., "make me a French chanson") — write Lyrics in the target language directly. Avoid `[Bilingual]` and similar tags — they don't work alone. See [`../references/style-and-lyrics.md`](../references/style-and-lyrics.md) § *Languages and code-switching*.
- **Brief asks for SFX in lyrics** ("with applause", "with vinyl crackle") — Style-field texture instead, never Lyrics-field bracket. SFX brackets are unreliable. Note in Rationale that the user can layer specific SFX in Suno Studio after generation.
- **Brief asks for bar counts** ("8-bar verse") — bar-count tags don't work in Lyrics; honour rate < 30%. Surface that bar-count work belongs in Suno Studio's section editor, not in this prompt.
- **Brief contradicts ARTIST.md** (e.g., ARTIST.md declares female vocal but brief asks for male) — surface the conflict via `AskUserQuestion`. Override only on confirmation. Never silently pick.
- **Existing TRACK.md at the target path** — refuse to overwrite. Suggest `revise` instead. The `create` verb writes only to fresh paths.
- **Project folder collision** — if `{slug}/` exists with non-skill content, refuse. Ask for an explicit slug.
