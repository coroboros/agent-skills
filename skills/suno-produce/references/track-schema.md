# TRACK / ALBUM / MUSIC schema

The three-layer artifact schema for Suno v5.5 production work. Every file produced by this skill conforms to one of the three.

The split is deliberate: each layer reads the layer below it, never above. `TRACK.md` reads `ALBUM.md` (sibling) for tracklist context. `ALBUM.md` reads `MUSIC.md` (referenced via `-f`) for artist defaults. `MUSIC.md` is a leaf — it reads nothing.

## TRACK.md

The unit of Suno generation. One file per track. Always emitted.

### Frontmatter

```yaml
---
suno_version: v5.5
title: <human title>          # required, ≤ 100 chars
bpm: 92                        # integer, soft guidance — drift ±4 is normal
key: D minor                   # optional, soft guidance — honour rate ~60%
length_target: "3:30"          # MM:SS or "long-form" / "sketch"
voice_profile: null            # set from bound MUSIC.md when applicable
custom_model: null             # set from bound MUSIC.md when applicable
genre_primary: indie folk      # one phrase, drives the load-bearing tag
era: 2010s bedroom             # optional but recommended
mood: nostalgic                # one or two adjectives
created: 2026-05-09            # ISO date, set on initial create
revised: null                  # ISO date, updated by every revise
---
```

`suno_version` is the durable lineage marker. The validator emits a YELLOW when this differs from the running Suno version, signalling that the prompt may not reproduce identically against a newer model.

### Body — six ordered sections

1. **Title** — `# <title>`. The song title repeated for human readability.
2. **Suno prompt block** — copy-paste payload. Three fenced blocks under one `## Suno prompt block` heading. Each is `text` fenced (triple-backtick + text language tag) so Markdown rendering does not interfere with the verbatim copy:

   ```text
   ### Style of Music
   ```text
   <descriptor stack, comma-separated, ≤ 1000 chars, 4–7 descriptors>
   ```

   ### Lyrics
   ```text
   [Intro]
   [Fingerpicked acoustic, room mic]
   [Soft male tenor, breathy delivery]

   The hallway light still flickers
   The dog still waits at the door
   …
   ```

   ### Exclude Styles
   ```text
   <0–3 tags, comma-separated>
   ```
   ```

3. **Sliders** — bullets:

   ```markdown
   ## Sliders
   - **Weirdness**: 40 — keeps phrasing within indie-folk convention
   - **Style Influence**: 75 — the descriptor stack is the identity, lock it in
   - **Audio Influence**: 78 — Voice attached, hold resemblance
   ```

   Audio Influence appears only when `voice_profile` or `custom_model` is set. Each slider gets a one-clause rationale.

4. **Voice / Custom Model** — declared if MUSIC.md is bound; "None." otherwise. When set, repeat the bound names so the file is self-contained when copied without MUSIC.md context:

   ```markdown
   ## Voice / Custom Model
   - **Voice**: `Studio-A` (from MUSIC.md at ~/artists/studio-a/MUSIC.md)
   - **Custom Model**: none
   ```

5. **Rationale** — prose. Why these descriptors, why this BPM, why this slider profile. Anchors the next `revise` decision. Aim 100–250 words.

6. **Iteration log** — a single bulleted list. Append-only. Each entry: `- v{N} ({YYYY-MM-DD}): <change axes>; <one-line summary>; <kept | archived>`. The first entry on `create` is `v0`. Every `revise` appends.

### Worked example — indie folk single

```markdown
---
suno_version: v5.5
title: Midnight Letter
bpm: 92
key: D minor
length_target: "3:30"
voice_profile: null
custom_model: null
genre_primary: indie folk
era: 2010s bedroom
mood: nostalgic
created: 2026-05-09
revised: null
---

# Midnight Letter

## Suno prompt block

### Style of Music
```text
Indie folk, 2010s bedroom, intimate and bittersweet, fingerpicked acoustic guitar, soft male tenor, slight lo-fi tape warmth, room mic, 92 BPM
```

### Lyrics
```text
[Intro]
[Fingerpicked acoustic, room mic]
[Soft male tenor, close-mic]

[Verse 1]
The hallway light still flickers
The dog still waits at the door
I haven't moved your jacket
It still hangs there, the same as before

[Pre-Chorus]
(building intensity)
And every quiet morning sounds the same

[Chorus]
[Doubled vocal, light harmony stack]
Waiting on the weather to change
Waiting on a reason to stay

[Verse 2]
…

[Bridge]
[Solo guitar, whispered]
…

[Final Chorus]
[Layered harmonies, fuller mix]
…

[Outro]
[Solo fingerpicked, fade]
```

### Exclude Styles
```text
808s, heavy distortion, EDM drops
```

## Sliders
- **Weirdness**: 40 — keeps phrasing within indie-folk convention
- **Style Influence**: 75 — the descriptor stack is the identity, lock it in
- **Audio Influence**: n/a — no Voice attached

## Voice / Custom Model
None.

## Rationale
Indie folk leads the Style stack because era + mood read as 2010s-bedroom and that informs vocal pocket more than instrumentation does. 92 BPM sits in the genre's centre band; the song breathes at that tempo. Excluded 808s and heavy distortion because the genre rewards space, and the brief specifically asked for "intimate". Vocal descriptor stays in Style — no Voice attached. Pre-chorus parenthetical `(building intensity)` is the one signature performance cue; everything else is structural.

## Iteration log
- v0 (2026-05-09): initial draft from brief — "intimate indie-folk track about absence, 92 BPM"
```

More worked examples (cinematic, melodic techno, melodic trap, alt rock, ambient drone, indie pop, ritual industrial, lo-fi hip-hop) live in [`./genre-templates.md`](./genre-templates.md). Adapt those by adding the YAML frontmatter and the Rationale + Iteration log sections.

## ALBUM.md

The album / EP concept and arc. One file per album folder. Created only when album mode is detected.

### Frontmatter

```yaml
---
title: <album title>
artist: <artist name | "TBD">
length_target_total: "28:00"
track_count: 7
release_format: EP             # EP | Album | Mixtape | Single (when single is part of a series)
created: 2026-05-09
---
```

### Body — five ordered sections

1. **Concept** — what the album is about, in 3–5 sentences. The overarching theme. Tone and posture across the whole arc.
2. **Arc** — the dramatic shape. Four-line label minimum:
   ```
   - Opening: <vibe / energy>
   - Development: <what shifts>
   - Climax: <peak track or moment>
   - Closing: <resolution or fade>
   ```
3. **Tracklist** — numbered list. Each line: `nn. Title — BPM — key — feel`. The `nn-` prefix matches the per-track folder name.
4. **Transitions** — bullets. Each bullet describes the move between two adjacent tracks: key change, BPM ramp, cross-fade or hard cut, narrative bridge. This is what makes a tracklist an album rather than a playlist.
5. **Rights and distribution** — placeholder section with declared posture: licensed audience, intended platforms, any cover-vs-original status, MUSIC.md binding if any. Cross-reference [`./rights-and-deprecation.md`](./rights-and-deprecation.md) when the artist has a `MUSIC.md`.

### Worked example — short EP

```markdown
---
title: Quiet Rooms
artist: TBD
length_target_total: "18:00"
track_count: 5
release_format: EP
created: 2026-05-09
---

# Quiet Rooms

## Concept
A short EP about absence as a daily routine — what stays in a house after someone leaves. Five tracks, all in minor keys, all under 4 minutes. Indie folk register throughout, with one production shift at the centre. The arc is one continuous evening.

## Arc
- Opening: still and intimate, single fingerpicked acoustic, no drums
- Development: brushed drums enter, harmony stacks introduced
- Climax: track 3 — full band moment, the only loud song on the record
- Closing: returns to solo guitar, fades to room tone

## Tracklist
1. Hallway Light — 88 BPM — D minor — sparse, voice and guitar only
2. The Garden — 92 BPM — A minor — brushed drums, upright bass enters
3. Midnight Letter — 96 BPM — D minor — full band, the loudest track
4. Still Waiting — 90 BPM — F# minor — pulls back, layered harmonies
5. Morning Tone — 78 BPM — D minor — solo guitar, room tone, fades to silence

## Transitions
- 1 → 2: D minor to A minor, key kinship; +4 BPM ramp; soft cross-fade
- 2 → 3: A minor to D minor, downward fifth; +4 BPM ramp; clean cut on the kick
- 3 → 4: D minor to F# minor, modal shift, mood drops; -6 BPM; long cross-fade
- 4 → 5: F# minor to D minor; -12 BPM, full pull-back; cross-fade through room tone

## Rights and distribution
Original songs, no covers, no sampled audio. No `MUSIC.md` bound for this EP — single-project artifact. See [`rights-and-deprecation.md`](./rights-and-deprecation.md) for the export-WAV reminder before model deprecation lands.
```

## MUSIC.md

The artist identity layer. Optional. Artist-scoped — one file referenced from many album folders. The skill never auto-creates one; the user keeps it wherever their workspace lives and binds it via `-f /path/to/MUSIC.md`.

### Frontmatter

```yaml
---
artist: <artist name>
voice_profile: <name registered in Suno UI | null>
voice_consent: <"self" | "licensed: <source>" | "public-domain: <source>" | null>
custom_model: <name registered in Suno UI | null>
custom_model_training_set: <"self-authored" | "licensed: <source>" | null>
recurring_instruments: ["acoustic guitar", "upright bass", "Rhodes"]
slider_bias:
  weirdness_default: 40
  style_influence_default: 75
  audio_influence_default: 78
rights_posture: license-only       # license-only | licensed | public-domain | unknown
created: 2026-05-09
---
```

### Body — four ordered sections

1. **Artist identity** — 2–3 sentences. Era, register, recognisable signatures. The sound someone would describe in one breath.
2. **Voice and Custom Model** — what's registered, what's the consent posture, what's the training-set posture. Cross-reference [`./rights-and-deprecation.md`](./rights-and-deprecation.md) § *Voice-cloning consent*.
3. **Recurring instrumentation and texture** — the descriptor fragments that should bias every TRACK.md created under this identity. Plus textures (`tape warmth`, `room mic`, `vinyl crackle`) that are part of the artist's sound.
4. **Rights posture** — the artist's commercial-rights stance. Statement of what is original, what is licensed, what is public-domain. Reminder to export WAV stems before model deprecation. Cross-reference `rights-and-deprecation.md` for the active litigation context.

### Worked example — minimal MUSIC.md

```markdown
---
artist: Studio-A
voice_profile: studio-a-tenor
voice_consent: self
custom_model: null
custom_model_training_set: null
recurring_instruments: ["fingerpicked acoustic guitar", "upright bass", "brushed drums", "soft male tenor"]
slider_bias:
  weirdness_default: 40
  style_influence_default: 75
  audio_influence_default: 78
rights_posture: license-only
created: 2026-05-09
---

# Studio-A

## Artist identity
Indie folk in the 2010s-bedroom register. Soft male tenor, intimate close-mic vocals, fingerpicked guitar as the spine of every arrangement. Brushed drums and upright bass when the song asks; otherwise sparse.

## Voice and Custom Model
- Voice profile `studio-a-tenor` registered in Suno UI on 2026-05-01. Cloned from self-recorded acapella, 90 seconds, low and high register. Consent: self.
- No Custom Model trained as of 2026-05-09. May add when six-track-minimum catalogue exists.
- See [`rights-and-deprecation.md`](rights-and-deprecation.md) § *Voice-cloning consent* for the consent contract this artist signs against.

## Recurring instrumentation and texture
- Hero instruments: fingerpicked acoustic guitar (always), soft male tenor (always)
- Supporting: upright bass, brushed drums (when arrangement asks), Rhodes (rare, special-occasion)
- Textures: room mic, slight lo-fi tape warmth, no auto-tune, no heavy reverb on lead vocal

## Rights posture
License-only — Suno's commercial assignment to a paid subscriber. No representation that copyright vests. No DMCA / Content ID enforcement available. Original songs, no covers. Voice cloned from self-recorded audio with consent. See [`rights-and-deprecation.md`](rights-and-deprecation.md) for the deprecation cliff and export-WAV reminder.
```

## Validator output schema

The JSON shape returned by [`../scripts/validate.py`](../scripts/validate.py):

```json
{
  "verdict": "GREEN" | "YELLOW" | "RED",
  "file": "tracks/01-midnight-letter/TRACK.md",
  "errors": [
    {"check": "<check_name>", "line": 16, "value": "<actual>", "expected": "<expected>", "fix": "<one-line fix>"}
  ],
  "warnings": [
    {"check": "<check_name>", "line": 16, "value": "<actual>", "expected": "<expected>", "fix": "<one-line fix>"}
  ],
  "info": [
    {"check": "<check_name>", "value": "<actual>", "running": "<runtime value>"}
  ]
}
```

`errors` empties on GREEN and YELLOW. `warnings` empties on GREEN. `info` always populates the `suno_version` running comparison, even on GREEN.

Stable contract for downstream consumers. Future `migrate` verb will read `info.suno_version` to decide what to rewrite.
