---
name: suno-produce
description: Turn a music brief into Suno v5.5-ready prompt artifacts — TRACK.md per generation, optional ALBUM.md for multi-track projects, optional ARTIST.md for artist-scoped identity. Artifact-emit-only — the user copy-pastes the prompt block into Suno's UI, listens, then iterates via `revise`. No API integration. Hardens the copyright contract — never lets artist names or copyrighted citations through into a prompt (legal exposure + Suno filters them anyway). Use when the user wants to make a song, produce a track or album, write a Suno prompt, or compose music with v5.5 — even when they don't say "Suno" by name.
when_to_use: When the user wants to create a song, track, EP, or album with Suno v5.5. Routes via `$ARGUMENTS` first token — `create` (default — synthesise TRACK.md from a brief, optionally ALBUM.md when album mode is detected), `revise <path> "<feedback>"` (archive current TRACK.md to versions/, emit a refined one), `validate <path>` (deterministic linter — char limits, descriptor counts, slider ranges, metatag canon, copyright/artist-citation contract). Triggers on "make a song", "write me a track", "produce a song", "song about", "lyrics for", "Suno prompt", "make an album", "EP about", "v5.5 prompt", "/suno", "/track". Skip when the user wants pure lyric writing without a Suno target (defer to a generic writing skill); when the request is broad music research (run `/brainstorm` first then `-f` the result into this); when the request is audio post-production like loops or mastering (defer to `/audio-loop`).
argument-hint: "[create|revise|validate] <description-or-path> [-f ARTIST.md]"
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
allowed-tools: Read Write Edit Glob Grep AskUserQuestion WebSearch Bash(mkdir *) Bash(test *) Bash(ls *) Bash(python3 *) Bash(git *) Bash(cp *) Bash(mv *)
model: opus
metadata:
  author: coroboros
  sources:
    - github.com/coroboros/research/blob/main/articles/suno-v5-5-operator-reference.md
    - suno.com/blog/v5-5
    - help.suno.com
    - github.com/Spidy88/suno-claude-skill
    - blakecrosley.com/guides/suno
    - stokemctoke.com/the-complete-suno-ai-meta-tags-guide/
    - www.suno.wiki/faq/metatags/
---

# Suno Produce

<!-- canonical:writing-rules:start -->
## Important — Writing rules

These rules govern every prose artifact this skill emits — READMEs, CHANGELOGs, commit messages, PR bodies, release notes, doc paragraphs, non-trivial comments. Apply them at draft time, verify before output.

- Match the surrounding style — punctuation, capitalization, backtick conventions, em-dash vs parens, bullet style.
- Every sentence changes the reader's understanding. Cut it otherwise.
- Front-load the verb — "Creates", not "This helps you create".
- Concrete over abstract. Lists for ≥3 enumerable items.
- Assert positively. Reserve negation for real constraints (`NEVER commit secrets`).
- No marketing words: powerful, robust, seamlessly, leverage, unlock, comprehensive, delightful.
- No AI tells: delve, tapestry, intricate, pivotal, testament, underscore, crucial, garner, showcase, additionally, moreover, furthermore, indeed.
- After drafting English prose, invoke `/humanize-en` if installed.
<!-- canonical:writing-rules:end -->

Govern music-production artifacts for Suno v5.5: a `TRACK.md` per generation, optional `ALBUM.md` for multi-track projects, optional `ARTIST.md` for an artist-scoped identity layer. Three layers, each with a clear job. The user copy-pastes the Suno prompt block from `TRACK.md` into Suno's Web/iOS/Android UI, listens to the two takes Suno produces, picks a winner, then runs `revise` with feedback to iterate.

Artifact-emit-only by design. Suno has no official public API. Reverse-engineered wrappers (kie.ai, sunoapi.org, gcui-art/suno-api) are degrading — PiAPI dropped Suno V5 entirely, gcui-art's maintainer is asking for a takeover, the Warner Music settlement signals tighter enforcement. The text prompts are durable; they survive model deprecation. The audio takes are not — export WAV stems from Suno's UI for anything you want to keep.

**Tier reality.** v5.5 is Pro/Premier only. Free tier is locked to v4.5-all and stays non-commercial regardless of later upgrades. Validator and refs assume v5.5; running the prompts on v4.5-all degrades but does not crash.

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
| **ARTIST.md** | Artist identity: Voice profile, Custom Model, recurring instrumentation, rights/compliance posture. | **Artist-scoped, not project-scoped** — one file referenced from many album folders. | Only when the user passes `-f path/to/ARTIST.md` to bind the work to an artist identity, or asks to set one up. Never auto-created. |

The three layers stack. `TRACK.md` reads `ALBUM.md` (sibling) for tracklist context if present. `ALBUM.md` reads `ARTIST.md` (referenced via `-f`) for artist defaults if present. Each layer adds context without overwriting the lower layer.

The third layer is named `ARTIST.md` — not `MUSIC.md` — because the file describes an artist identity (voice, custom model, recurring instrumentation, rights posture), not music itself. The community Suno-prompt formats (Spidy88, Blake Crosley, Stoke McToke, suno.wiki) do not have an equivalent layer; this is a deliberate addition to the open standard.

## Project folder layout

Two shapes — **standalone single** (`{track-slug}/TRACK.md` + `versions/` + `audio/` + `.gitignore`) and **album/EP** (`projects/{album-slug}/ALBUM.md` + `tracks/01-{slug}/TRACK.md` per track). `ARTIST.md` lives outside project folders (typically `~/<artist>/ARTIST.md`) and is referenced via `-f`. Track-slug is kebab-case (max 5 words); the `01-` prefix matches the tracklist order in `ALBUM.md`. Full directory trees and the rename-on-reorder behaviour: [`references/track-schema.md`](./references/track-schema.md) § *Project folder layout*.

## Suno v5.5 field limits

The validator enforces these as RED errors on overflow:

| Field | Limit |
|-------|-------|
| Style of Music | 1,000 chars (4–7 descriptors, front-loaded) |
| Lyrics | 5,000 chars (bracket metatags + parenthetical cues) |
| Title | 100 chars (cosmetic — no audio effect) |
| Simple Mode prompt | 500 chars (Custom Mode preferred for serious work) |

Account/plan caps (generation length, audio upload, voice input, custom model training set + per-account limit, stems, output specs) live in [`references/rights-and-deprecation.md`](./references/rights-and-deprecation.md) § *Plan tiers* and § *Output specs*.

## TRACK.md schema

YAML frontmatter (`suno_version`, `title`, `bpm`, `key`, `length_target`, `voice_profile`, `custom_model`, `created`, `revised`) + six ordered sections: **Title** → **Suno prompt block** (three `text`-fenced sub-blocks: Style of Music ≤1000 chars / 4–7 descriptors, Lyrics ≤5000 chars with bracket metatags + parenthetical cues, Exclude Styles ≤3 tags) → **Sliders** (Weirdness, Style Influence, Audio Influence — only when a Voice or Custom Model is attached — each with rationale) → **Voice / Custom Model** (declared if ARTIST.md is bound; "None." otherwise) → **Rationale** (why these descriptors, BPM, sliders — anchors `revise`) → **Iteration log** (`v1 (date): <what was tried>; <feedback>; <kept | archived>`).

Adopted from the community-converged track-bundle pattern (Spidy88, Blake Crosley, Stoke McToke, suno.wiki) — same five user-visible sections, wrapped in a frontmatter for `validate.py`. Front-load the Suno prompt block; users grab it and paste, rationale lives below.

Full frontmatter shape, worked examples per genre (cinematic, melodic-trap, indie-folk, ambient drone, ritual industrial, lo-fi hip-hop), and the ALBUM.md / ARTIST.md schemas live in [`references/track-schema.md`](./references/track-schema.md).

## Auto-detect sufficient specification

Skip the interview when the brief covers **at least 3** of the 5 anchor dimensions below; otherwise use `AskUserQuestion` (max 4, recommended-option first, single round — do not loop) for the gaps. If `ARTIST.md` is bound via `-f`, vocal profile / instrumentation / rights / slider defaults flow from it (drop those questions).

| Dimension | Why it matters | Example values |
|-----------|---------------|----------------|
| Genre | Drives the Style of Music load-bearing tag | indie folk, melodic trap, ambient drone, alt rock |
| Mood | Two-word descriptor that calibrates feel | nostalgic, brooding, euphoric, glacial |
| Vocal direction | Gender + register + delivery (drop if Voice attached) | soft male tenor, breathy female soprano, autotuned melodic male rap |
| Length target | Drives section count + tempo | 1:30 sketch, 3:30 single, 6:00 long-form |
| References | Era / sound-fingerprint (never artist names — describe the sound) | late-90s post-grunge, 2010s bedroom indie, Bristol post-punk dub |

## My Taste — disable for evaluation runs

v5.5 ships a default-on personalization layer (**My Taste**) that perturbs takes when prompts are underspecified. It does not override an explicit Style field, but the variable is uncontrolled until disabled from the avatar menu. Surface this reminder when synthesising the first track for a new artist or doing A/B / slider-band work. Detail: [`references/sliders-and-personalization.md`](./references/sliders-and-personalization.md).

## Voice and Custom Model awareness

When `ARTIST.md` declares `voice_profile:` or `custom_model:`, prompt assembly changes:

- **Voice attached** — drop vocal descriptors from Style (they conflict with the cloned voice and produce blended timbre); set Audio Influence to 75–90% (78% default).
- **Custom Model attached** — drop redundant style descriptors the model already encodes (genre, era, aesthetic); use Style for variations within the model's range.
- **Both** — stack: drop genre/era + drop vocal descriptors. Style becomes purely directional.

The skill records `voice_profile` and `custom_model` in TRACK.md frontmatter so `validate.py` flags conflicts (e.g., vocal descriptors despite an attached Voice).

## Validation contract

[`scripts/validate.py`](./scripts/validate.py) auto-dispatches by filename — TRACK / ALBUM / ARTIST — and runs the matching check set. Every artifact runs through validation before disk. Exit codes: 0 GREEN (zero issues), 1 RED (block — fix and re-run), 2 YELLOW (write proceeds with warning).

Highest-stakes RED checks: artist citation patterns (`in the style of X`, `sounds like X`, `voice of/like X`, `à la X`, `<Name>'s sound/style/voice/era`) anywhere in Style or Lyrics; field overflow (Style >1000 chars, Lyrics >5000, Title >100); BPM in Lyrics; missing required sections; voice-consent missing when `voice_profile` is declared. Full check tables for TRACK / ALBUM / ARTIST plus edge-case behaviour: [`steps/validate.md`](./steps/validate.md) § *Check sets per artifact type*.

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
- **Never name artists or copyrighted entities in prompts.** Hard rule, two reasons. *Legal* — citing an artist or copyrighted entity creates rights exposure (publicity rights, trademark, label trade-name); the prompt is a discoverable artifact, shared and committed. *Functional* — Suno filters or ignores the citation, so the model collapses to an averaged tag rather than the requested fingerprint. The validator emits **RED** on high-confidence citation patterns (`in the style of <Name>`, `voice of/like <Name>`, `sounds like <Name>`, `à la <Name>`, `<Name>'s sound/style/voice/era`) in Style or Lyrics, and **YELLOW** on bare title-case proper-noun pairs in Style. Translate every brief reference to sound — era + production texture + vocal timbre. Example: "make me a track like Sufjan Stevens" → "indie folk, intimate fingerpicked acoustic, soft male tenor, banjo, breathy delivery, lo-fi tape warmth". More translated stacks: [`references/style-and-lyrics.md`](./references/style-and-lyrics.md).
- **Lyric content is the user's voice — never humanise or restyle.** The skill's commentary (rationale, iteration log, validation summaries) is functional prose; the lyrics stay verbatim as the user wrote them.
- **Surface deprecation reality.** Suno's current models are scheduled for deprecation when WMG-licensed successors ship. The skill records `suno_version: v5.5` in frontmatter so a future `migrate` subcommand can rewrite prompts to v6 syntax. Recommend the user export WAV from Suno before deprecation lands.

## When to defer to another skill

- **Pure lyric writing without Suno target** → a generic writing skill. The lyric format here includes bracket metatags and cues that read awkwardly elsewhere.
- **Broad music research** ("what's working in 2026 indie folk") → `/brainstorm`, then `-f` the brief back into this skill.
- **Audio post-production** → `/audio-loop` for web loops; Suno Studio 1.2 (Remove FX, Warp Markers) for everything else.
- **Voice profile registration** — out of scope. Register Voices and train Custom Models in Suno's UI; this skill only consumes them via ARTIST.md.
- **Brand-voice work** (writing voice for marketing copy) → `/brand-voice`. ARTIST.md is the music analog.
- **Visual identity** → `/award-design` for hero pages, `/canvas-design` for static art, `/video-loop` for hero motion.

## Reference

- [`steps/create.md`](./steps/create.md), [`revise.md`](./steps/revise.md), [`validate.md`](./steps/validate.md) — per-subcommand workflows.
- [`references/style-and-lyrics.md`](./references/style-and-lyrics.md) — descriptor stack, genre fusion, vocal/production direction, BPM/key, bracket metatag canon, lyric flow, languages, SFX warning, translated stacks for artist requests.
- [`references/sliders-and-personalization.md`](./references/sliders-and-personalization.md) — Creative Sliders, voice/model-aware prompting, voice+model stacking, My Taste.
- [`references/genre-templates.md`](./references/genre-templates.md) — 8 copy-paste-ready v5.5 recipes (cinematic, melodic techno, melodic trap, alt rock, ambient drone, indie pop, ritual industrial, lo-fi hip-hop).
- [`references/track-schema.md`](./references/track-schema.md) — TRACK / ALBUM / ARTIST schemas + project folder layout + worked example.
- [`references/rights-and-deprecation.md`](./references/rights-and-deprecation.md) — plan tiers, output specs, post-generation pipeline, WMG settlement, voice-cloning consent, v6 deprecation cliff.
- [`scripts/validate.py`](./scripts/validate.py) — deterministic linter (Python 3.7+, stdlib only) returning GREEN / YELLOW / RED with line-anchored findings.

The full upstream Suno v5.5 operator reference (1,200+ lines covering features, plans, API access, litigation, deprecation timeline) lives at the public sources cited in `metadata.sources` above. The skill bundles only the actionable subset — what the steps actually consult.
