---
name: suno-produce
description: Turn a music brief into Suno v5.5-ready prompt artifacts — TRACK.md per generation, optional ALBUM.md for multi-track projects, optional MUSIC.md for artist-scoped identity. Artifact-emit-only — the user copy-pastes the prompt block into Suno's UI, listens, then iterates via `revise`. No API integration. Use when the user wants to make a song, produce a track or album, write a Suno prompt, or compose music with v5.5 — even when they don't say "Suno" by name.
when_to_use: When the user wants to create a song, track, EP, or album with Suno v5.5. Routes via `$ARGUMENTS` first token — `create` (default — synthesise TRACK.md from a brief, optionally ALBUM.md when album mode is detected), `revise <path> "<feedback>"` (archive current TRACK.md to versions/, emit a refined one), `validate <path>` (deterministic linter — char limits, descriptor counts, slider ranges, metatag canon). Triggers on "make a song", "write me a track", "produce a song", "song about", "lyrics for", "Suno prompt", "make an album", "EP about", "v5.5 prompt", "/suno", "/track". Skip when the user wants pure lyric writing without a Suno target (defer to a generic writing skill); when the request is broad music research (run `/brainstorm` first then `-f` the result into this); when the request is audio post-production like loops or mastering (defer to `/audio-loop`).
argument-hint: "[create|revise|validate] <description-or-path> [-f MUSIC.md]"
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
allowed-tools: Read Write Edit Glob Grep AskUserQuestion WebSearch Bash(mkdir *) Bash(test *) Bash(ls *) Bash(python3 *) Bash(git *) Bash(cp *) Bash(mv *)
model: opus
metadata:
  author: coroboros
  sources:
    - https://github.com/coroboros/research/blob/main/articles/suno-v5-5-operator-reference.md
    - https://suno.com/blog/v5-5
    - https://help.suno.com
    - https://github.com/Spidy88/suno-claude-skill
    - https://blakecrosley.com/guides/suno
    - https://stokemctoke.com/the-complete-suno-ai-meta-tags-guide/
    - https://www.suno.wiki/faq/metatags/
---

# Suno Produce

Govern music-production artifacts for Suno v5.5: a `TRACK.md` per generation, optional `ALBUM.md` for multi-track projects, optional `MUSIC.md` for an artist-scoped identity layer. Three layers, each with a clear job. The user copy-pastes the Suno prompt block from `TRACK.md` into Suno's Web/iOS/Android UI, listens to the two takes Suno produces, picks a winner, then runs `revise` with feedback to iterate.

Artifact-emit-only by design. Suno has no official public API. Reverse-engineered wrappers (kie.ai, sunoapi.org, gcui-art/suno-api) are degrading — PiAPI dropped Suno V5 entirely, gcui-art's maintainer is asking for a takeover, the Warner Music settlement signals tighter enforcement. The text prompts are durable; they survive model deprecation. The audio takes are not — export WAV stems from Suno's UI for anything you want to keep.

Additional context from the user: $ARGUMENTS

## Subcommand routing

Parse the first positional token of `$ARGUMENTS`. If it matches a verb below, load the referenced step file and follow its workflow. Otherwise fall through to *Default workflow* at the end of this document.

| First token | Mode | Reference |
|-------------|------|-----------|
| `create` | Synthesise a TRACK.md (and optionally ALBUM.md) from a brief. Default verb when no token matches and the argument looks like a music description. | [`steps/create.md`](./steps/create.md) |
| `revise` | Archive `<path>/TRACK.md` to `<path>/versions/v{N+1}.md`, emit a refined TRACK.md with adjustments justified by `<feedback>`. | [`steps/revise.md`](./steps/revise.md) |
| `validate` (aliases: `lint`, `check`) | Run [`scripts/validate.py`](./scripts/validate.py) against `<path>/TRACK.md`. Report GREEN / YELLOW / RED with line-anchored findings. | [`steps/validate.md`](./steps/validate.md) |
| (none) | See *Default workflow* below | (this file) |

The `create` verb is implied when no token matches a verb and the remainder of `$ARGUMENTS` reads like a brief — "indie folk track about a long winter", "make me a melodic-trap EP". The `revise` and `validate` verbs always require an explicit token plus a path.

## File taxonomy

Three layers, progressively scaffolded — emit only what the brief actually calls for. Do not pre-create empty files.

| File | Role | Scope | Created when |
|------|------|-------|--------------|
| **TRACK.md** | Unit of Suno generation. The copy-paste-into-Suno bundle. | One file per track. | Always. Every invocation that ends in a Suno-ready prompt produces one. |
| **ALBUM.md** | Album/EP concept, arc, tracklist with BPM/key flow, transitions. | One per album folder. | Only when the brief reads as multi-track ("EP", "album", "record", "4-track", "side A side B"). Auto-detect with confirmation prompt. |
| **MUSIC.md** | Artist identity: Voice profile, Custom Model, recurring instrumentation, rights/compliance posture. | **Artist-scoped, not project-scoped** — one file referenced from many album folders. | Only when the user passes `-f path/to/MUSIC.md` to bind the work to an artist identity, or asks to set one up. Never auto-created. |

The three layers stack. `TRACK.md` reads `ALBUM.md` (sibling) for tracklist context if present. `ALBUM.md` reads `MUSIC.md` (referenced via `-f`) for artist defaults if present. Each layer adds context without overwriting the lower layer.

## Project folder layout

### Standalone single (one track, no album)

```
{track-slug}/
  TRACK.md
  versions/
    v1.md, v2.md, …       # archived prior takes (created by revise)
  audio/                   # optional, gitignored — user drops Suno exports here
    v1-takeA.wav, …
  .gitignore               # the skill emits this if missing — ignores audio/
```

### Album / EP

```
projects/{album-slug}/
  ALBUM.md
  tracks/
    01-{track-slug}/
      TRACK.md
      versions/
      audio/
    02-{track-slug}/
      TRACK.md
      …
  .gitignore
```

The track-slug is kebab-case from the title, max 5 words. The leading two-digit prefix (`01-`, `02-`) matches the tracklist order in `ALBUM.md`. Reordering renames the folders; the skill handles this in `revise` when the album order changes.

`MUSIC.md` lives wherever the user keeps it — typically a brand workspace root (`~/<artist>/MUSIC.md`) — and is referenced from any project folder via `-f /path/to/MUSIC.md`. The skill never creates `MUSIC.md` on its own; it only consumes one when passed.

## TRACK.md schema

YAML frontmatter (machine-validatable) plus six prose sections in this order. Adopted from the community-converged Suno track-bundle pattern across Spidy88, Blake Crosley, Stoke McToke, and suno.wiki — all four guides ship the same five sections (Title / Style / Lyrics / Sliders / Tips), wrapped here in a frontmatter for `validate.py`.

```yaml
---
suno_version: v5.5
title: <human title>
bpm: 92
key: D minor          # soft guidance — Suno honours about 60% of the time
length_target: "3:30"
voice_profile: null   # set from MUSIC.md when bound; null when no Voice attached
custom_model: null    # set from MUSIC.md when bound
created: 2026-05-09
revised: null
---
```

Then in this exact order:

1. **Title** — the song title, repeated for human readability
2. **Suno prompt block** — the copy-paste payload. Three fenced blocks: `### Style of Music` (≤1000 chars, 4–7 descriptors), `### Lyrics` (≤5000 chars, with bracket metatags and parenthetical cues), `### Exclude Styles` (≤3 tags). All three are `text` fenced for clean copy-paste with no Markdown rendering interference.
3. **Sliders** — Weirdness, Style Influence, Audio Influence as bullets with rationale. Audio Influence only present when `voice_profile` or `custom_model` is set.
4. **Voice / Custom Model** — declared if MUSIC.md is bound; "None." otherwise.
5. **Rationale** — why these specific descriptors, why this BPM, why this slider profile. Anchors the `revise` decisions.
6. **Iteration log** — bullet per version: `v1 (date): <what was tried>; <listener feedback>; <kept | archived>`.

Front-load the Suno prompt block. Users grab it and paste; rationale lives below the fold.

Full schema with worked examples per genre (cinematic, melodic-trap, indie-folk, ambient drone, ritual industrial, lo-fi hip-hop) lives in [`references/track-schema.md`](./references/track-schema.md).

## Auto-detect sufficient specification

Skip the AskUserQuestion interview when the user-provided brief covers **at least three** of the five anchor dimensions below. The model proceeds directly to synthesis.

When the brief is thinner, use `AskUserQuestion` (max 4 questions) for the missing essentials. Multi-select where applicable. Recommended option first. Cap the interview — one round, then proceed with what was answered. Do not loop.

The five anchor dimensions:

| Dimension | Why it matters | Example values |
|-----------|---------------|----------------|
| Genre | Drives the Style of Music load-bearing tag | indie folk, melodic trap, ambient drone, alt rock |
| Mood | Two-word descriptor that calibrates feel | nostalgic, brooding, euphoric, glacial |
| Vocal direction | Gender + register + delivery (drop entirely if Voice attached) | soft male tenor, breathy female soprano, autotuned melodic male rap |
| Length target | Drives section count + tempo decisions | 1:30 sketch, 3:30 single, 6:00 long-form |
| References | Era / artist sound-fingerprint (never artist names — describe the sound) | late-90s post-grunge, 2010s bedroom indie, Bristol post-punk dub |

If `MUSIC.md` is bound via `-f`, defaults flow from it: artist identity supplies vocal profile (drop those questions), recurring instruments, rights posture, and any persistent slider biases.

## Voice and Custom Model awareness

When `MUSIC.md` declares `voice_profile:` or `custom_model:`, the skill changes prompt assembly:

- **Voice attached** — drop all vocal descriptors from the Style of Music field. They conflict with the cloned voice and produce blended timbre. Set Audio Influence to 75–90% (78% default). Reallocate the freed character budget to instruments and production texture.
- **Custom Model attached** — drop redundant style descriptors that the model already encodes (genre, era, aesthetic). Use the Style field for variations within the model's range — sparser arrangement, tempo deviation, mood shift.
- **Both** — stack. Drop genre/era + drop vocal descriptors. The Style field becomes purely directional.

The skill records `voice_profile` and `custom_model` in `TRACK.md` frontmatter so `validate.py` can flag conflicts (e.g., vocal descriptors present despite an attached Voice).

## Validation contract

[`scripts/validate.py`](./scripts/validate.py) auto-dispatches by filename — `TRACK.md`, `ALBUM.md`, or `MUSIC.md` — and runs the matching check set. Every artifact the skill writes runs through validation before disk. Verdicts: GREEN (zero issues), YELLOW (warnings only — write proceeds with the warning surfaced), RED (errors — block the write, fix and re-run). Exit codes: 0 GREEN, 1 RED, 2 YELLOW.

**TRACK.md** — Suno v5.5 prompt-bundle rules:

| Check | Verdict |
|-------|---------|
| Style of Music ≤ 1000 chars, Lyrics ≤ 5000 chars, Title ≤ 100 chars | RED on overflow |
| Style descriptor count 4–7 | YELLOW outside band |
| Slider values 0–100 | RED out of range |
| Exclude Styles ≤ 3 | YELLOW above |
| Bracket metatag canon — Tier 1 GREEN; Tier 3 community tags YELLOW; SFX brackets RED | mixed |
| BPM in Lyrics field | RED |
| Voice attached + vocal descriptors in Style | YELLOW |
| Genre count > 2, conflicting eras, artist names | YELLOW |
| `suno_version` mismatch | YELLOW |

**ALBUM.md** — concept + tracklist consistency:

| Check | Verdict |
|-------|---------|
| `title` non-empty, ≤ 100 chars | RED |
| `release_format` ∈ {EP, Album, Mixtape, Single} | RED |
| Required sections present (Concept / Arc / Tracklist / Transitions) | RED on missing |
| Arc contains all four labels (Opening / Development / Climax / Closing) | YELLOW per missing label |
| `track_count` matches tracklist line count | RED on mismatch |
| Tracklist line shape `nn. Title — BPM — key — feel` | YELLOW per malformed line |
| `created` ISO date | YELLOW on bad format |

**MUSIC.md** — artist identity + voice consent:

| Check | Verdict |
|-------|---------|
| `artist` non-empty | RED |
| `voice_profile` declared → `voice_consent` required | RED |
| `voice_consent` shape ∈ {`self`, `licensed: <source>`, `public-domain: <source>`} | YELLOW on bad format |
| `custom_model` declared → `custom_model_training_set` recommended | YELLOW |
| `slider_bias.*` values in [0, 100] | RED out of range |
| `rights_posture` ∈ {license-only, licensed, public-domain, unknown} | YELLOW on bad format |
| Required sections present (Artist identity / Voice and Custom Model / Recurring instrumentation / Rights posture) | RED on missing |

The script reads the artifact and writes a JSON report to stdout; the skill captures it and threads warnings into the user-facing summary. Full check list, examples, and edge-case behaviour live in [`steps/validate.md`](./steps/validate.md).

## Default workflow (no subcommand)

When the first token of `$ARGUMENTS` does not match `create|revise|validate|lint|check`:

1. **Argument reads like a music brief** ("indie folk about a long winter", "melodic trap heartbreak track") → run `create` with that brief.
2. **Argument is a path** to an existing folder containing `TRACK.md` → run `validate` on it.
3. **Empty `$ARGUMENTS` and a `TRACK.md` exists in the working directory** → run `validate` on it.
4. **Empty `$ARGUMENTS` and no nearby `TRACK.md`** → if session context has a music brief candidate (recent music discussion or lyric draft), propose `/suno-produce create "<inferred brief>"` and confirm. Otherwise suggest `/suno-produce create "<your brief>"` and stop. Never silently start an interview.

The default exists to avoid silent state-modifying actions. Every write goes through an explicit verb.

## Rules

- **Artifact-emit-only.** Never call a Suno API, never invoke a reverse-engineered wrapper, never expose an `--api` flag. The user runs the prompt in Suno's UI. The wrapper ecosystem is degrading; this skill stays out of it.
- **One field, one job.** The Style of Music field carries genre / era / mood / instruments / vocal direction. The Lyrics field carries the lyric text plus bracket metatags. Never put BPM in Lyrics. Never put `[Verse]` in Style.
- **Two genres maximum.** Three or more genres muddy the output. When the brief asks for fusion, pick one primary and reinforce with mood / instrumentation.
- **Front-load the prompt block.** TRACK.md begins with the copy-paste-ready payload, not with the rationale. Users paste, then read.
- **Versions are sacred.** `revise` archives the prior `TRACK.md` to `versions/v{N+1}.md` before overwriting. Never lose the previous take.
- **Validate before write.** Every `create` and `revise` runs `scripts/validate.py` on the synthesised content. RED never reaches disk. YELLOW surfaces in the user-facing summary.
- **Voice attached → drop vocal descriptors.** Always. Vocal direction in Style conflicts with a cloned Voice and produces blended timbre.
- **Auto-detect album mode → confirm before scaffolding.** When the brief reads as multi-track, propose the album folder structure and ask for confirmation. Never silently create `ALBUM.md`.
- **Describe the sound, never an artist.** Suno filters or ignores artist names. The brief "make me a Sufjan Stevens track" gets translated to "indie folk, intimate fingerpicked acoustic, soft male tenor, banjo, breathy delivery, lo-fi tape warmth".
- **Lyric content is the user's voice, not Coroboros'.** The skill's own commentary (rationale, iteration log, validation summaries) follows the institutional Coroboros voice. The lyrics themselves are user-authored — never humanise or restyle them.
- **Surface deprecation reality.** Suno's current models are scheduled for deprecation when WMG-licensed successors ship. The skill records `suno_version: v5.5` in frontmatter so a future `migrate` subcommand can rewrite prompts to v6 syntax. Recommend the user export WAV from Suno before deprecation lands.

## When to defer to another skill

- **Pure lyric writing without Suno target** → a generic writing skill. This skill assumes the prompt will be fed to Suno; the lyric format includes bracket metatags and parenthetical cues that read awkwardly elsewhere.
- **Broad music research** ("compare melodic-trap producers", "what's working in 2026 indie folk") → `/brainstorm`, then `-f` the brief into `/suno-produce` once the direction is clear.
- **Audio post-production** (looping a generated track for a website, mastering, removing reverb tails outside Suno Studio) → `/audio-loop` for web loops; Suno Studio 1.2 (Remove FX, Warp Markers) inside the Suno UI for the rest.
- **Voice profile registration** — out of scope. The user registers Voices and trains Custom Models in Suno's UI. This skill consumes them via MUSIC.md but does not manage them.
- **Brand-voice work** (defining a writing voice for marketing copy) → `/brand-voice`. MUSIC.md is the music analog — a separate file with a different schema.
- **Visual identity** (album art, music videos) → `/award-design` for hero pages, `/canvas-design` for static art, `/video-loop` for hero motion.

## Reference

- [`steps/create.md`](./steps/create.md), [`steps/revise.md`](./steps/revise.md), [`steps/validate.md`](./steps/validate.md) — per-subcommand workflows, the AskUserQuestion templates for the interview, the synthesis recipe for each prompt field.
- [`references/style-and-lyrics.md`](./references/style-and-lyrics.md) — composing the prompt: descriptor stack, genre fusion, vocal direction, production direction, BPM/key, negative prompting, bracket metatag canon, lyric flow, languages, SFX warning, consolidated pitfalls. Read by `create` and `revise` whenever the brief touches the Style of Music or Lyrics fields.
- [`references/sliders-and-personalization.md`](./references/sliders-and-personalization.md) — the three Creative Sliders, voice-aware prompting, custom-model-aware prompting, voice + model stacking. Read when assembling slider settings or when MUSIC.md declares a `voice_profile` / `custom_model`.
- [`references/genre-templates.md`](./references/genre-templates.md) — eight copy-paste-ready Suno v5.5 recipes (cinematic, melodic techno, melodic trap, alt rock, ambient drone, indie pop, ritual industrial, lo-fi hip-hop). Read when matching the brief's genre family to a starting template.
- [`references/track-schema.md`](./references/track-schema.md) — TRACK / ALBUM / MUSIC schemas in full, with a worked TRACK.md example. Cross-references `genre-templates.md` for additional recipes.
- [`references/rights-and-deprecation.md`](./references/rights-and-deprecation.md) — self-contained summary of the WMG settlement, copyright vesting (license, not vested rights), voice-cloning consent, the v6 deprecation cliff. Surfaced into MUSIC.md when artist identity is declared. Not repeated per track.
- [`scripts/validate.py`](./scripts/validate.py) — validates a TRACK.md against v5.5's field limits and the rule set above. Python 3.7+, stdlib only. Walks YAML frontmatter, parses fenced Style / Lyrics / Exclude blocks, returns GREEN / YELLOW / RED with line-anchored findings.

The full upstream Suno v5.5 operator reference (1,200+ lines covering features, plans, API access, litigation, deprecation timeline) lives at the public sources cited in `metadata.sources` above. The skill bundles only the actionable subset — what the steps actually consult.
