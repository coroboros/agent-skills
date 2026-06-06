# Songwriting craft — structure, rhyme, meter, hook

Craft for writing singable lyrics aimed at Suno. Read this during `create` **only when the user wants help writing or shaping the lyrics** — not when they supply finished lines. When the user hands you lyrics, they stay verbatim; this file never licenses a restyle (see SKILL.md § *Rules* → *Lyric content is the user's voice*).

Everything here is a guideline. The song wins over the rule — break any of it when the line hits harder broken.

## Contents

- [Song structure](#song-structure)
- [Rhyme](#rhyme)
- [Meter and stress](#meter-and-stress)
- [Emotional arc and dynamics](#emotional-arc-and-dynamics)
- [The hook](#the-hook)
- [Prosody — lyric and melody supporting each other](#prosody--lyric-and-melody-supporting-each-other)
- [Show, don't tell](#show-dont-tell)
- [Consolidated pitfalls](#consolidated-pitfalls)

## Song structure

Pick a skeleton or invent one. The common ones:

| Pattern | Sections | Fits |
|---|---|---|
| ABABCB | Verse / Chorus / Verse / Chorus / Bridge / Chorus | most pop / rock |
| AABA | Verse / Verse / Bridge / Verse (refrain-based) | jazz standards, ballads |
| ABAB | Verse / Chorus alternating | simple, direct |
| AAA | Verse / Verse / Verse (strophic, no chorus) | folk, storytelling |

The six building blocks — use only what the song asks for:

- **Intro** — set the mood, pull the listener in
- **Verse** — the story, the detail, the world
- **Pre-Chorus** — optional tension ramp before the payoff
- **Chorus** — the emotional core, the remembered part
- **Bridge** — a detour: a shift in perspective, imagery, or key
- **Outro** — the farewell; echo or subvert the rest

Each section you choose becomes a bracket metatag on its own line in the Lyrics field — `[Verse 1]`, `[Chorus]`, `[Bridge]`. The arrangement-control mechanics (canon, numbered variants, stacking instrumentation cues per section) live in [`./style-and-lyrics.md`](./style-and-lyrics.md) § *Bracket metatag canon*. Structure serves the emotion, not the reverse.

## Rhyme

Rhyme types, tight to loose:

- **Perfect** — `lean / mean`
- **Family** — `crate / braid` (related consonants)
- **Assonance** — `had / glass` (same vowel, different ending)
- **Consonance** — `scene / when` (different vowel, similar ending)
- **Slant / near** — enough to suggest a connection without locking it

Blend them. All perfect rhymes read as nursery rhyme; all slant reads as lazy. The mix is where it lives. **Internal rhyme** — rhyming inside a line, not only at the ends — tightens flow without adding end-rhyme pressure.

## Meter and stress

Meter is the pattern of stressed vs. unstressed syllables.

- Stressed syllables matter more than total count — match the **stresses** between parallel lines and singability follows.
- Matching syllable counts across parallel lines helps the lines sit on the same melodic phrase.
- Say it aloud. If you stumble, the meter needs work — Suno stumbles in the same places a singer does.
- Break meter on purpose for emphasis or surprise; just know you're doing it.

## Emotional arc and dynamics

Contrast is the lever: a whisper before a scream lands harder than the scream alone. Sparse before dense, slow before fast, low before high. A rough energy map (not a prescription):

```
Intro 2-3 · Verse 5-6 · Pre-Chorus 7 · Chorus 8-9 · Bridge varies · Final Chorus 9-10
```

Encode that arc where Suno reads it — the stacked instrumentation / texture / dynamics cues per section in [`./style-and-lyrics.md`](./style-and-lyrics.md) § *Stacking metatags inside sections* and § *Inline performance cues*. Write the arc once, in the Lyrics-field cues; this file decides the shape, that one renders it.

## The hook

The line people hum back — usually the title or the core phrase. It lands hardest when melody, lyric, and emotion align on the same beat. Place it where it carries: often the first or last line of the chorus. Build outward from the hook rather than writing toward it.

## Prosody — lyric and melody supporting each other

Match the feeling to the musical setting:

- **Stable feelings** (resolution, peace) pair with settled melody, perfect rhyme, resolved cadence.
- **Unstable feelings** (longing, doubt) pair with wandering melody, near-rhyme, unresolved cadence.
- Verse melody typically sits lower; the chorus lifts. Flip it when the song asks.

When prosody and lyric pull the same direction, the take feels intentional; when they fight, it feels like a demo.

## Show, don't tell

A concrete image outlives a flat statement — `your hoodie's still on the hook by the door` beats `I was sad`. Plain language still hits when it's earned (`I give my life`, said straight, at the right moment). The failure mode is the autopilot cliché — `heart of gold` standing in for an image you didn't write.

## Consolidated pitfalls

| Don't | Do |
|---|---|
| Force word order to land a rhyme (Yoda-speak) | Recast the line, or pick a looser rhyme type |
| Rhyme everything perfectly | Blend perfect and slant |
| Hold one energy across every section | Build contrast — whisper to roar to whisper |
| Treat the first draft as sacred | Revise; the draft is raw material |
| State the feeling flat (`I was sad`) | Show it with a concrete image |
| Lean on a cliché on autopilot | Earn the image, or cut it |
