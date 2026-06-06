# Style of Music + Lyrics — Composing the Prompt

The reference for composing the two prompt-bearing fields in Suno v5.5: the **Style of Music** field (1,000 chars, the descriptor stack) and the **Lyrics** field (5,000 chars, with bracket metatags and parenthetical cues). Read this when synthesising a TRACK.md from a brief, or when revising one against listener feedback.

## Contents

- [Style of Music — descriptor stack](#style-of-music--descriptor-stack)
- [Never name artists or copyrighted entities](#never-name-artists-or-copyrighted-entities)
- [Genre stacking and fusion](#genre-stacking-and-fusion)
- [Vocal direction](#vocal-direction)
- [Production direction (era + texture + mix)](#production-direction-era--texture--mix)
- [BPM and key](#bpm-and-key)
- [Negative prompting](#negative-prompting)
- [Bracket metatag canon (structural)](#bracket-metatag-canon-structural)
- [Stacking metatags inside sections](#stacking-metatags-inside-sections)
- [Inline performance cues](#inline-performance-cues)
- [Lyric flow and pacing](#lyric-flow-and-pacing)
- [Languages and code-switching](#languages-and-code-switching)
- [Phonetic and delivery control](#phonetic-and-delivery-control)
- [SFX bracket tags — do not deploy](#sfx-bracket-tags--do-not-deploy)
- [Section length — bar counts belong in Studio](#section-length--bar-counts-belong-in-studio)
- [Consolidated pitfalls](#consolidated-pitfalls)

## Style of Music — descriptor stack

The Style of Music field is read as an ordered, weighted tag list. The first two to three tags dominate. Fill four to seven descriptors across five classes, in this order:

| Class | Examples | Weight |
|---|---|---|
| Genre | Indie folk, melodic trap, dark ambient | Load-bearing |
| Era / vibe | 90s warmth, 80s gated, 2010s indie | High |
| Mood | Nostalgic, brooding, euphoric | Medium |
| Instruments | Acoustic guitar, 808 sub, Rhodes | Medium |
| Vocal direction | Soft male vocal, breathy soprano | High when no Voice attached |

Place genre first. Era and mood second. Instruments third. Vocal direction last unless vocal is the identity of the track, in which case promote it to second.

### Character budget — recommended allocation

| Bucket | Characters | Tags |
|---|---|---|
| Genre stack | 30–80 | 1–2 |
| Era cue | 20–40 | 1 |
| Mood | 20–60 | 1–2 |
| Instruments | 60–150 | 2–3 |
| Vocal direction | 40–120 | 1 vocal block |
| Production texture | 60–150 | 2–3 texture tags |
| BPM / key | 10–30 | optional |
| Inline negatives | 40–100 | optional, last |

Total: 280–730 characters. The remaining headroom is reserve, not a target. Density beats verbosity.

### Side-by-side: under-specified vs working vs overstuffed

```text
1 descriptor (generic):
indie pop

6 descriptors (working):
indie pop, 2010s bedroom, nostalgic, fingerpicked acoustic,
soft male vocal, lo-fi tape warmth, 95 BPM

12 descriptors (overstuffed; conflicts):
indie pop, dream pop, shoegaze, bedroom, lo-fi, hi-fi polished,
nostalgic, euphoric, dark, fingerpicked acoustic, jangly Rickenbacker,
synthwave pads, 808 trap drums, soft male vocal, belting female vocal,
95 BPM, 140 BPM
```

The 12-tag version forces the model to average across "lo-fi" plus "hi-fi polished", two BPMs, and two vocal genders. Output collapses to a moody average — not what the prompt asked for.

## Never name artists or copyrighted entities

Hard rule for both Style and Lyrics. Two reasons.

**Legal.** The prompt is a discoverable artifact — it lives in `TRACK.md`, gets committed, archived, shared, and propagated. An artist or copyrighted-entity citation in the prompt creates rights exposure (publicity rights, trademark, label trade-name) on a surface that survives the audio. The audio file itself can be deleted; the prompt that produced it is part of the project history.

**Functional.** Suno's filter strips most artist citations before the model sees them. Citations that survive collapse to an averaged tag — the model knows nothing specific about the cited artist, so it picks the tag halfway between the citation and the surrounding descriptors. The output is worse than what an explicit sound-fingerprint description would have produced.

The validator emits **RED** on the citation patterns that signal explicit intent — `in the style of <Name>`, `voice of/like <Name>`, `sounds like <Name>`, `à la <Name>`, `<Name>'s sound/style/voice/era` — in either field. It emits **YELLOW** on bare title-case proper-noun pairs in Style outside the safe-phrase whitelist (`Pedal Steel`, `Sub Bass`, `Plate Reverb`, etc.). Bare title-case in Lyrics is not flagged because lyric lines start with capitals and false-positive rate would dominate.

### How to translate a brief

Replace the artist citation with **era + production texture + vocal timbre**. Keep the descriptor count in the 4–7 band. Examples:

| Brief request | Translated descriptor stack |
|---------------|----------------------------|
| "make me a Sufjan Stevens track" | indie folk, 2010s bedroom, intimate, fingerpicked acoustic, soft male tenor, banjo, breathy delivery, lo-fi tape warmth, 92 BPM |
| "Daft Punk vibe" | French house, 2000s analog, vocoded vocal, sidechain pump, filter sweeps, side-chained pads, 4/4 at 120 BPM |
| "voice like Adele" | full-throated contralto female, gospel-rasp belt, plate reverb, dry close-mic verse, soulful inflection |
| "in the style of Kurt Cobain" | grunge, late-90s Seattle, raspy male tenor, distorted guitar, drop-D tuning, sludgy bass, dry close-mic |
| "Bristol post-punk like Massive Attack" | trip-hop, 90s Bristol, dub-heavy, female alto, programmed breakbeat, sub bass, plate reverb, 88 BPM |
| "Phil Collins drums" | 80s gated reverb, big tom fills, pulsing kick, programmed snare, wide stereo |

The right column is what survives the validator. The left column is what the user said.

### Edge case — proper nouns in lyrics

Character names in lyrics are fine. "Mary called", "John waited" — the validator does not scan Lyrics for bare title-case pairs. What the validator does scan in Lyrics is the citation patterns above, because a character "in the style of Bob Dylan" is still a citation regardless of which field it lives in.

## Genre stacking and fusion

Two genres maximum. Validated pairs share at least one of: tempo, instrumentation register, or vocal idiom.

| Pair | Why it works |
|---|---|
| Pop + EDM | Shared 4/4, shared BPM band |
| Gospel + trap | Shared swung 808 feel, shared vocal range |
| Jazz + hip-hop | Shared swung phrasing |
| Indie folk + electronic | Shared intimate vocal pocket |
| Synthwave + indie pop | Shared 80s gated drum reference |
| Drum & bass + cinematic | Shared sub register, strings ride 174 |
| Country + soul | Shared vocal grit, Rhodes/pedal-steel mix |
| Phonk + drift trap | Shared cowbell, shared 808 |
| Afrobeats + R&B | Shared groove tempo, melodic ad-lib |

Fusion fails when: BPM mismatch (lo-fi 78 + DnB 174 → averaged 120 nothing), vocal idiom conflict (operatic over drill), era conflict (60s Motown over hyperpop). When fusion fails, drop to one genre and reinforce with mood.

## Vocal direction

Name gender, register, timbre, delivery, age, processing — in that order.

| Axis | Tags |
|---|---|
| Gender | male, female, androgynous |
| Register | bass, baritone, tenor, alto, soprano, falsetto |
| Timbre | warm, breathy, raspy, smoky, nasal, smooth |
| Delivery | whispered, spoken, sung, belted, rapped, chanted |
| Age | youthful, mature, weathered |
| Processing | autotuned, vocoded, telephone EQ, doubled, layered |

Worked examples:

```text
Soft breathy female soprano, intimate close-mic, slight room
  → dream pop / bedroom indie

Deep weathered baritone male, raspy delivery, dry
  → folk noir / americana

Autotuned melodic male rap, reverb-heavy, doubled ad-libs
  → modern melodic trap

Belted female alto, gospel rasp, plate reverb
  → soul / contemporary R&B

Falsetto male tenor, breathy, telephone EQ
  → alt R&B

Layered female harmonies, choir-stacked, no lead
  → choral / sacred minimalism

Spoken word female, monotone, dry close-mic
  → trip-hop / spoken-word post-punk

Shouted male tenor, blown-out, room reverb
  → punk / hardcore
```

**When a Voice profile is attached, drop all vocal descriptors from the Style field.** They conflict with the cloned voice and produce blended timbre. See `sliders-and-personalization.md` § Voices-aware prompting.

## Production direction (era + texture + mix)

Era cue + texture cue + mix cue stack into a coherent recording aesthetic.

| Era cue | Texture cue | Mix cue |
|---|---|---|
| 80s gated reverb | Tape hiss | Wide stereo |
| 70s analog warmth | Vinyl crackle | Dry close-mic |
| 90s dusty sample | Plate reverb | Sidechain pump |
| 2010s indie aesthetic | Lo-fi tape | Compressed bus |
| 2020s glossy digital | Hi-fi modern | Stereo-wide polished |
| Late 60s Motown | Spring reverb | Mono mid-forward |

Triggering specific regions:

```text
"80s gated reverb, analog warmth, wide stereo"
  → Phil Collins-era pop region

"90s dusty sample, vinyl crackle, raw head-nod groove"
  → boom-bap region

"2020s glossy digital, sidechain pump, stereo-wide polished"
  → modern dance-pop region

"Lo-fi tape, room mic, dry"
  → bedroom-folk / indie demo region
```

## BPM and key

Numeric BPM works as approximate guidance, not metronome lock. v5.5 holds tempo more reliably than v5, but ±4 BPM drift is normal.

```text
"Indie folk, 95 BPM"          → lands 92–98 BPM
"120–130 BPM"                  → model picks one
"Half-time feel at 140 BPM"    → renders as 70 BPM groove
```

Key specification ("D minor", "A major") is soft guidance. Honour rate ≈ 60%. For mixing-compatibility scenarios, generate, detect actual key with an external tool, then reuse the prompt with the corrected key.

BPM lives in the **Style field only**. Never in Lyrics — the validator flags this as RED.

## Negative prompting

Two mechanisms.

**Inline.** Append `no X` at the end of the Style field. v5.5 processes positives first, then exclusions:

```text
warm acoustic folk, fingerpicked guitar, soft male vocals,
90 BPM, no drums, no electric guitar, no autotune
```

**Exclude Styles toggle.** Pro / Premier only. Custom Mode > More Options > Exclude Styles. Excluded styles appear in Song Preview with a `-` prefix. API equivalent: `negativeTags` (string, comma-separated).

Effective exclusions:

| Category | Tags |
|---|---|
| Instruments | piano, electric guitar, drums, bass, synthesizer, strings, 808s, hi-hats, banjo |
| Vocals | male vocals, female vocals, autotune, vibrato, choir, ad-libs |
| Tempo | fast tempo, slow tempo |
| Era | 1940s, 1980s, 2010s pop |
| Mood | aggressive, melancholic, euphoric |
| Processing | heavy distortion, breathy vocals, reverb-drenched, telephone EQ |

**Cap exclusions at three.** Five `no X` tags with no positive tags produce mush. Positives define, negatives refine.

## Bracket metatag canon (structural)

Bracket tags belong in the Lyrics field, on their own line, at the start of the section they govern. They control arrangement.

**Tier 1 — officially documented (always GREEN):**

```text
[Intro]
[Verse]      [Verse 1] [Verse 2] [Verse 3]
[Pre-Chorus]
[Chorus]     [Chorus 1] [Chorus 2] [Final Chorus]
[Post-Chorus]
[Bridge]
[Outro]
[Instrumental]
```

Numbered variants (`[Verse 1]`, `[Chorus 2]`, `[Final Chorus]`) work reliably.

**Tier 3 — community-validated, inconsistent (validator emits YELLOW):**

```text
[Hook]   [Drop]   [Build]   [Break]
[Solo]   [Interlude]   [Refrain]   [Breakdown]
```

Use sparingly. Prefer Tier 1 when possible.

**Custom invented tags do not work.** `[My Special Section]`, `[The Chorus After The Bridge]` — these get sung as lyrics or ignored entirely.

Order in the Lyrics field is the intended song order. Suno honours it most of the time. When it ignores order, regenerate; do not rewrite the tags.

## Stacking metatags inside sections

Stack three to five tags per section, line-broken, in the order **structural → instrumentation → texture/mood → vocal direction**:

```text
[Intro]
[Fingerpicked acoustic guitar]
[Soft room reverb, vinyl warmth]

[Chorus]
[Soaring falsetto, layered harmonies]
[Strings swell, emotional lift]
```

Worked example — melodic trap verse-chorus:

```text
[Verse 1]
[Pitched vocal chop loop, hi-hat rolls]
[Reverb tail, dry kick]
[Autotuned melodic male delivery]

[Chorus]
[Sub-bass 808 drop, layered ad-libs]
[Reverb-drenched, sidechain pump]
[Doubled lead, harmonized 3rds]
```

Stacking outperforms single tags because a single `[Chorus]` only signals arrangement. Stacked tags signal arrangement plus instrumentation plus texture plus delivery — four control surfaces engaged at the same line break.

## Inline performance cues

Two formats — interchangeable.

**Bracketed cues above the lyric block:**

```text
[Whispered]
The kitchen light was always on
The radio was never off

[Belted]
But I won't carry this anymore
```

**Parenthetical cues inline:**

```text
(whispered) The kitchen light was always on
(belted) But I won't carry this anymore
```

Reliable cues: `[Whispered]`, `[Spoken Word]`, `[Belted]`, `[Falsetto]`, `[Harmonized]`, `[Layered Vocals]`, `[Ad-lib]`, `[Hummed]`, `[Shouted]`. Parentheticals: `(whispered)`, `(belted)`, `(building intensity)`, `(stripped back)`, `(fading)`.

Descriptor-style cues like `[Mood: Nostalgic]` and `[Energy: Soaring]` work inconsistently. Some renders honour them, some treat the bracket contents as lyrics. Use sparingly, audition every time, do not depend.

## Lyric flow and pacing

Tight lines yield faster flow; blank lines between lyrics yield pacing. Line breaks are pacing signal, not aesthetic preference.

```text
Faster flow:
My shrink says I'm crazy
My boss says I'm lazy
I don't mind long as you
call me baby

More pacing:
My shrink says I'm crazy

My boss says I'm lazy

I don't mind long as you
call me baby
```

### Punctuation behaviour

| Mark | Effect |
|---|---|
| Comma | Short syllabic pause, lyric continues |
| Em-dash with spaces — | Longer pause, often delivered as melismatic stretch |
| Ellipsis … | Often sung, occasionally treated as silence |
| Blank line | Section pause, the strongest pacing signal |
| Period | Generally inert |
| Exclamation mark | Ignored; sometimes sung as the word "exclamation" |

For sustained vowels, write the vowel out: `Loooove`. Suno reads vowel elongation reliably.

## Languages and code-switching

Write the target language directly. Tags like `[Bilingual]` or `[Spanglish]` do not work alone.

```text
Multilingual chorus (French / English):
[Chorus]
On danse jusqu'à l'aube
Until the morning light
On danse, on tombe
Holding on so tight
```

For proper nouns and unusual phonemes, write phonetic spelling:

```text
"Saoirse"        → "Seer-sha"
"Nguyen"         → "Nwen"
"Worcestershire" → "Wuss-ter-sher"
```

Best supported languages: English, Spanish, Portuguese, French, Japanese, Korean, Mandarin. Other languages produce accented or imprecise pronunciation.

## Phonetic and delivery control

AI vocalists don't read — they pronounce. The punctuation table and vowel elongation (`Loooove`) under *Lyric flow and pacing* shape pacing and sustain; the phonetic respelling under *Languages and code-switching* fixes unusual proper nouns. Three more delivery controls:

- **ALL CAPS = louder, more intense.** Capitalise a word or line to push the delivery harder at that spot.
- **Spell out numbers; read symbols as words.** `24/7` → `twenty four seven`. Digits and symbols get read inconsistently.
- **Space or hyphenate acronyms.** `AI` → `A I` or `A-I`, so the model says the letters instead of guessing a word.

**Test risky pronunciations early.** Proper nouns and coined words are the highest failure rate. Audition them in a short clip before a full generation — once a take renders, pronunciation is baked into that audio. Fix it in the Lyrics field and regenerate; you cannot correct it after the take exists.

## SFX bracket tags — do not deploy

Most SFX brackets are unreliable in v5.5.

| Tag | Behaviour |
|---|---|
| `[applause]` | Often nothing; sometimes sung |
| `[vinyl crackle]` | Style-field texture only, not a Lyrics tag |
| `[tape hiss]` | Style-field texture only |
| `[gunshot]` | Almost always nothing |
| `[crowd noise]` | Inconsistent |
| `[siren]` | Inconsistent |
| `[doorbell]` | Almost always nothing |

The validator emits RED on SFX brackets in the Lyrics field. Generate ambience separately via Suno Sounds (Suno's experimental sound-effect generator), then layer in Studio.

## Section length — bar counts belong in Studio

Bar-count tags inside Lyrics (`[Verse 8 bars]`, `[Chorus 4 bars]`, `[Bridge 16 bars]`) honour at < 30%. Sometimes the bracket is silently dropped; sometimes the bar count is interpreted as a section name and sung. Either way the rendered section length does not match the spec.

The reliable surface for bar-count work is **Suno Studio's Edit menu**, where the bar count per section is a numeric input at the bottom-left of the section editor. Premier-tier feature. Set it after the prompt produces the take, before exporting.

When the brief asks for a specific bar count (e.g., "8-bar verse"), record the request in Rationale rather than encoding it as a Lyrics bracket — and surface in the user-facing summary that bar-count work happens in Studio, not in the prompt.

### Half-time renders

`145 BPM half-time` renders as a 70 BPM groove with hi-hats riding the upper grid — the canonical trap feel. State both numbers explicitly in Style: `145 BPM half-time` rather than `70 BPM trap`. The model holds tempo against the larger number and feel against the qualifier.

## Consolidated pitfalls

| Don't | Do |
|---|---|
| Type "make a song about love" | Describe the sound: "Indie folk, soft male vocal, fingerpicked guitar, 95 BPM" |
| Stack three or more genres | Maximum two |
| Put `[Verse]` in the Style field | `[Verse]` belongs in Lyrics, on its own line |
| Put "120 BPM" in the Lyrics field | BPM in the Style field |
| Use artist names or copyrighted citations (`in the style of X`, `voice of X`, `à la X`) | Describe the sonic fingerprint — era, texture, vocal timbre. Hard rule, both legal and functional. |
| Write 12 descriptors hoping for richness | Four to seven |
| Use exclamation marks for emphasis | Vowel elongation: `Loooove` |
| Repeat tags across both fields | One field, one job |
| Trust SFX bracket tags | Generate in Suno Sounds, layer in Studio |
| Set bar counts in Lyrics (`[Verse 8 bars]`) | Set bar counts in Suno Studio's Edit menu |
| Stack six exclusions | Cap at three |
| Attach Voice and keep "soft male vocal" in Style | Drop vocal descriptors when Voice attached |

Slider profiles, voice-aware prompting, custom-model-aware prompting, and genre-specific copy-paste recipes live in sibling reference files — see the SKILL.md reference table.
