# Genre Templates

Eight copy-paste-ready Suno v5.5 recipes, one per genre family. Each template ships a Style of Music block, an Exclude Styles list, slider settings, a Lyrics scaffold with bracket metatags, and a one-paragraph annotation explaining the choices.

Pick the template that best matches the brief's genre family, paste into TRACK.md, then customise. The rationale fields anchor the customisation — record what you change and why in the TRACK.md Rationale section.

## Contents

- [1 — Cinematic / score](#1--cinematic--score)
- [2 — Melodic techno](#2--melodic-techno)
- [3 — Melodic trap](#3--melodic-trap)
- [4 — Alt rock](#4--alt-rock)
- [5 — Ambient drone](#5--ambient-drone)
- [6 — Vocal-forward indie pop](#6--vocal-forward-indie-pop)
- [7 — Ritual industrial post-punk](#7--ritual-industrial-post-punk)
- [8 — Lo-fi hip-hop / chillhop](#8--lo-fi-hip-hop--chillhop)

## 1 — Cinematic / score

```text
Style of Music:
Dark cinematic orchestral, 2010s trailer scoring, foreboding and grand,
deep strings, timpani rolls, brass stabs, taiko drums, no vocals,
D minor, 85 BPM, plate reverb, wide stereo

Exclude Styles: pop drums, autotune, electric guitar
Sliders: Weirdness 60, Style Influence 55

Lyrics scaffold (Instrumental ON):
[Intro]
[Sparse solo piano, single sustained string]
[Tape hiss, wide stereo]

[Build]
[Layered strings, timpani pulses]
[Plate reverb, gradual swell]

[Drop]
[Full orchestra, taiko, brass stabs]
[Compressed, wide stereo]

[Outro]
[Solo cello, fading reverb tail]
```

**Annotation:** Weirdness pushed to 60 because cinematic underscoring benefits from unexpected harmonic motion. Style Influence kept at 55 because the bracket-stack inside Lyrics carries the section logic. Audio Influence n/a — cinematic scoring rarely uses Voice or Custom Model unless the brand has a recurring orchestral identity.

## 2 — Melodic techno

```text
Style of Music:
Melodic techno, 2020s European club, hypnotic and brooding,
analog arp, sub bass, minimal kick, sparse female vocal hook,
tape saturation, 124 BPM, wide stereo

Exclude Styles: vocals, breakbeats, distorted guitar
Sliders: Weirdness 45, Style Influence 70

Lyrics scaffold:
[Intro]
[Filtered arp, no kick]
[Subtle white noise sweep]

[Build]
[Add sub bass, percussion enters]
[Tension rise, snare roll]

[Drop]
[Full kick + bass, hook arp peaks]
[Stereo wide, sidechain pump]

[Breakdown]
[Drop kick, keep pad + female vocal phrase]

[Drop]
[Second drop variation]

[Outro]
[Filter down, tail to silence]
```

**Annotation:** The female vocal hook stays in Style despite Exclude Styles listing "vocals". The exclusion blocks sung verses; the brief hook phrase reads as texture and survives. If you attach a Voice, drop "sparse female vocal hook" from Style and raise Audio Influence to 75.

## 3 — Melodic trap

```text
Style of Music:
Melodic trap, 2020s atmospheric, dark moody,
deep sub 808s, glitchy hi-hat rolls, pitched vocal chops,
autotuned melodic male rap, reverb-drenched ad-libs,
minor key, 145 BPM half-time

Exclude Styles: live drums, acoustic guitar, bright synths
Sliders: Weirdness 45, Style Influence 65, Audio Influence 75–85 if Voice

Lyrics scaffold:
[Intro]
[Pitched vocal chop loop]
[Reverb tail, dry kick]

[Verse 1]
[Autotuned melodic male delivery]
[Hi-hat rolls, sub bass]
Block cold, head spinning, lights low
…

[Chorus]
[Doubled lead, harmonized 3rds]
[808 drop, layered ad-libs]
…

[Verse 2]
[Same delivery, pull back hi-hats]
…

[Outro]
[808 sustain, reverb fade]
```

**Annotation:** 145 BPM half-time renders as a 70 BPM groove with hi-hats riding the upper grid — the canonical trap feel. State both numbers explicitly. If a Voice is attached for the rapper, drop "autotuned melodic male rap" from Style and let the Voice carry vocal identity; raise Audio Influence to 78.

## 4 — Alt rock

```text
Style of Music:
Alt rock, late 90s post-grunge, brooding,
distorted guitars, driving drums, raspy male vocal,
tape warmth, dry close-mic vocal, 96 BPM

Exclude Styles: 808s, autotune, synthesizers
Sliders: Weirdness 35, Style Influence 75

Lyrics scaffold:
[Intro]
[Clean guitar arpeggio, kick pulse]

[Verse 1]
[Restrained delivery, hi-hat closed]
…

[Pre-Chorus]
(building intensity)
…

[Chorus]
[Distorted guitar wall, raspy belt]
…

[Bridge]
[Half-time drums, feedback drone]
…

[Final Chorus]
[Bigger, doubled vocal, ride cymbal open]
…
```

**Annotation:** Style Influence at 75 because the distorted-guitar identity needs to lock; Weirdness at 35 to keep the riff structure conventional. Late-90s post-grunge is a thin region of the model — if takes drift toward 2010s alt rock or generic punk, raise Style Influence to 80 and add an explicit era reinforcer like "Foo Fighters era pop-rock" — wait, do not name artists. Use "tightly produced 1998 alt rock, glossy radio mix" instead.

## 5 — Ambient drone

```text
Style of Music:
Dark ambient drone, 2010s isolationist, glacial and unsettling,
evolving pads, tape hiss, no percussion, no vocals,
plate reverb, wide stereo, 50 BPM

Exclude Styles: drums, vocals, melodic hook
Sliders: Weirdness 75, Style Influence 40

Lyrics scaffold (Instrumental ON):
[Intro]
[Single sustained pad, low frequency hum]

[Section 1]
[Pad evolves, second layer enters]
[Tape hiss rises]

[Section 2]
[Granular texture, distant feedback]

[Outro]
[Layers strip away, tail to silence]
```

**Annotation:** Weirdness 75 is correct for ambient — the genre rewards melodic surprise. Style Influence 40 lets the texture breathe rather than forcing arrangement convention. `[Section 1]`, `[Section 2]` are Tier 3 community tags — they emit YELLOW in the validator but work reliably enough for ambient where the structural canon (`[Intro]`, `[Verse]`, `[Chorus]`) does not fit. Note the choice in Rationale.

## 6 — Vocal-forward indie pop

```text
Style of Music:
Indie pop, 2010s bedroom, intimate and bittersweet,
fingerpicked acoustic guitar, soft female vocal,
slight lo-fi warmth, room mic, 92 BPM

Exclude Styles: 808s, heavy distortion, EDM drops
Sliders: Weirdness 40, Style Influence 75, Audio Influence 75–85 if Voice

Lyrics scaffold:
[Intro]
[Solo fingerpicked acoustic, room tone]

[Verse 1]
[Soft female vocal, close-mic]
The hallway light still flickers
The dog still waits at the door

[Pre-Chorus]
(building intensity)
And I haven't moved your jacket

[Chorus]
[Doubled vocal, light harmony stack]
Waiting on the weather to change
Waiting on a reason to stay

[Verse 2]
…

[Bridge]
[Solo guitar, whispered]

[Final Chorus]
[Layered harmonies, fuller mix]
```

**Annotation:** Vocal descriptors in Style are kept because no Voice is attached. With a Voice, drop "soft female vocal, room mic" and route those characters into more production detail. The pre-chorus parenthetical `(building intensity)` is the one signature performance cue; everything else stays structural.

## 7 — Ritual industrial post-punk

```text
Style of Music:
Ritual industrial post-punk, late 80s 4AD aesthetic, ominous,
metallic percussion, chorused bass, baritone male incantation,
plate reverb, dry mid, 102 BPM

Exclude Styles: pop hooks, major key, autotune
Sliders: Weirdness 65, Style Influence 60

Lyrics scaffold:
[Intro]
[Metallic clang loop, chorused bass enters]
[Plate reverb, mono mid]

[Verse 1]
[Baritone monotone, dry close-mic]
…

[Chorus]
[Distorted guitar wall, pounding floor toms]
[Shouted vocal layer behind lead]
…

[Bridge]
[Drop drums, single sustained guitar feedback]
…

[Final Chorus]
[Bigger, blown-out compression]
```

**Annotation:** This recipe pulls from a thin region of the model. Generate four variations and discard three. Higher Weirdness (65) is essential — the genre rewards harmonic strangeness. If takes drift toward generic post-punk, add an explicit late-80s 4AD-era era cue and reinforce "ritual industrial" in the first descriptor slot.

## 8 — Lo-fi hip-hop / chillhop

```text
Style of Music:
Lo-fi hip-hop, 2010s bedroom-producer aesthetic, melancholic,
dusty jazzy piano sample, brushed drums, vinyl crackle,
tape saturation, no vocals, 78 BPM

Exclude Styles: vocals, EDM drops, distortion
Sliders: Weirdness 50, Style Influence 70

Lyrics scaffold (Instrumental ON):
[Intro]
[Solo piano sample, vinyl crackle]

[Section 1]
[Drums enter, brushed snare]
[Upright bass walks under]

[Section 2]
[Add Rhodes counter-melody, tape wobble]

[Bridge]
[Drop drums, piano alone]

[Outro]
[Drums return, fade to vinyl noise]
```

**Annotation:** Lo-fi rewards "no vocals" in both Exclude Styles and the Style field. The genre is identified by absence as much as presence. Vinyl crackle as a Style-field texture works reliably; do not put `[vinyl crackle]` in Lyrics — that's an SFX bracket and the validator emits RED. `[Section 1]`, `[Section 2]` are Tier 3 — they emit YELLOW but work for the ambient-leaning pacing of lo-fi.

## How to use these

1. Identify the genre family closest to the brief.
2. Copy the template's Style / Exclude / Sliders / Lyrics scaffold into TRACK.md.
3. Adapt: swap the BPM if the brief asks for different tempo; swap the era if the brief targets a different decade; swap the vocal descriptor (or drop it if a Voice is attached) per the brief.
4. Replace the lyric placeholders (`…`) with actual lyrics.
5. Run `scripts/validate.py` against the result. RED blocks the write; YELLOW surfaces in the user summary.
6. Record the deviations from the template in TRACK.md's Rationale section. The next `revise` decision is anchored on what was kept and what was changed.

The rules these templates follow (descriptor budget, bracket canon, slider bands) and the commercial-rights / deprecation context live in sibling reference files — see the SKILL.md reference table.
