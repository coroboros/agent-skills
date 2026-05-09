# Sliders + Voice + Custom Model

The three Creative Sliders, voice-cloning behaviour, and custom-model behaviour for Suno v5.5. Read this when assembling slider settings in TRACK.md, or when MUSIC.md declares a `voice_profile` or `custom_model`.

## Contents

- [The three Creative Sliders](#the-three-creative-sliders)
- [Slider bands by genre](#slider-bands-by-genre)
- [Voices-aware prompting](#voices-aware-prompting)
- [Custom Model-aware prompting](#custom-model-aware-prompting)
- [Stacking Voice + Custom Model](#stacking-voice--custom-model)

## The three Creative Sliders

Suno's official mapping (the API floats live in the API reference; the UI shows percentages 0–100):

| Slider | Range | API parameter | What it controls |
|---|---|---|---|
| Weirdness | 0–100% | `weirdnessConstraint` (0.00–1.00) | Deviation from genre defaults |
| Style Influence | 0–100% | `styleWeight` (0.00–1.00) | Adherence to Style of Music tags |
| Audio Influence | 0–100% | `audioWeight` (0.00–1.00) | Adherence to uploaded audio or attached Voice |

Audio Influence only surfaces when audio is uploaded, a Voice is attached, or Cover mode is active. Below 50%, the upload becomes texture or reference rather than identity.

### Weirdness bands

| Band | Behaviour |
|---|---|
| 0–25% | Predictable, genre-accurate, conservative phrasing |
| 25–50% | Standard expressive output, default territory |
| 50–70% | Unusual instruments, rhythmic surprises, riskier vocal phrasing |
| 70–100% | Genuinely unpredictable; sometimes brilliant, sometimes unusable |

### Style Influence bands

| Band | Behaviour |
|---|---|
| 0–30% | Pure exploration, lyrics drive feel |
| 30–60% | Loose adherence to genre tags |
| 60–80% | Tight adherence — recommended default |
| 80–100% | Plateau; phrasing variation drops |

### Audio Influence

70–90% recommended for cloning resemblance against reference recordings (community-validated). Below 70%, the cloned Voice drifts toward generic. Above 90%, the model occasionally produces glitch artefacts on phonemes outside the training-clip range.

## Slider bands by genre

Pick the band that best matches the brief; centre within the band. State the chosen number in TRACK.md and one-clause rationale per slider.

| Genre family | Weirdness | Style Influence | Audio Influence (when Voice / Model) |
|---|---|---|---|
| Radio pop | 35–50 | 65–80 | 60–75 |
| Hip-hop / trap | 40–55 | 55–70 | 60–80 |
| Worship / gospel | 25–40 | 70–85 | 70–90 |
| Cinematic orchestral | 55–70 | 45–60 | n/a |
| Ambient / experimental | 70–85 | 35–55 | n/a |
| Indie folk / pop | 30–45 | 70–85 | 70–85 |
| Voices clone (resemblance focus) | 30–45 | 60–75 | 75–90 |

**Workflow rule.** Change one slider at a time, regenerate, A/B against the prior take. Otherwise the variable is uncontrolled and you cannot attribute the change to a specific knob. The `revise` step honours this: when the listener feedback is sound-related, move one slider, not three.

## Voices-aware prompting

When a Voice profile is attached (declared in MUSIC.md or selected in Suno's UI):

1. **Drop all vocal descriptors from the Style of Music field.** "Soft male tenor", "breathy female soprano", "autotuned melodic male rap" — all conflict with the cloned voice and produce blended timbre. The validator emits YELLOW when vocal descriptors are present alongside an attached Voice.
2. **Drop vocal descriptors from inline cues in Lyrics.** `[Soft male tenor, close-mic]` becomes `[Close-mic, dry vocal pocket]` — keep the mic / processing cue, drop the timbre.
3. **Set Audio Influence to 70–90%.** Default 78%. Below 70%, the clone drifts toward generic.
4. **Reallocate the freed character budget.** The vocal-direction slot in Style (40–120 chars) is freed when the Voice handles vocal identity. Use those characters for additional production texture or instrumentation detail.

Worked example:

```text
Without Voice (vocal descriptor in Style):
Indie folk, 2010s bedroom, nostalgic, fingerpicked acoustic,
soft male vocal, breathy delivery, lo-fi tape warmth, 95 BPM

With Voice attached (vocal descriptor dropped, characters reallocated):
Indie folk, 2010s bedroom, nostalgic, fingerpicked acoustic,
upright bass, brushed drums, lo-fi tape warmth, room mic,
spring reverb, 95 BPM
```

Suno's official Voices FAQ confirms: *"If you find that the songs you make with your Voice don't sound like you, experiment with turning up the Audio Influence slider in the Create form."*

### Voice resemblance troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Vocal feels generic, doesn't sound like the clone | Audio Influence too low | Raise to 80–90% |
| Glitch artefacts on certain phonemes | Audio Influence too high, training clip didn't cover that register | Lower to 75% or re-record the Voice with broader range |
| Resemblance present but timbre is wrong | Vocal descriptor in Style still active | Remove the descriptor |
| Resemblance drifts mid-song | Style Influence dominating | Lower Style to 60–70%, raise Audio to 80% |

## Custom Model-aware prompting

A Custom Model encodes its training-set's style: genre, era, aesthetic. When selected:

1. **Drop redundant descriptors from Style.** The model already encodes them. Including them again adds noise without adding signal.
2. **Use the Style field for variations** within the model's range — sparser arrangement, tempo deviation, mood shift, alternative instrumentation.
3. **Style Influence stays in 60–75%** for variation work. Pushing higher locks the model into its centre; pushing lower invites drift outside the model's range.

Worked example — Custom Model trained on dark cinematic catalogue:

```text
Without Custom Model:
Dark cinematic orchestral, 2010s trailer scoring, foreboding,
deep strings, timpani rolls, brass stabs, no vocals, D minor, 85 BPM

With Custom Model selected (drop the genre/era/aesthetic the model already encodes):
Sparser arrangement than usual, solo cello lead,
rising tension, no choir, 90 BPM
```

The Custom Model handles "dark cinematic orchestral, 2010s trailer scoring, foreboding". The Style field handles "sparser arrangement than usual, solo cello lead, rising tension" — the deviation from the model's centre.

The validator emits YELLOW when redundant genre/era descriptors are present alongside a declared Custom Model.

## Stacking Voice + Custom Model

The deepest personalization stack v5.5 offers: Custom Model + Voice + Audio Influence 70–90%.

When both are declared in MUSIC.md, the Style field becomes purely directional:

- Drop genre / era / aesthetic (encoded by the Custom Model)
- Drop vocal descriptors (encoded by the Voice)
- Keep: mood adjustments, instrumentation deviations, tempo, key, production texture cues that vary across tracks

The remaining Style stack reads as deviation tags only:

```text
Sparser than usual, slower tempo, strings only,
no percussion, dry close-mic, room reverb, 82 BPM
```

Slider profile for Voice + Model:

- Weirdness 30–45 (lower than usual — the model and voice carry identity, low Weirdness preserves coherence)
- Style Influence 60–70 (pure variation)
- Audio Influence 75–85 (resemblance lock)

The combination is fragile. Validate against reference recordings; expect 4–6 takes before convergence. Save winning takes as `versions/v{N}.md` archive — the prompt that produced a coherent Voice + Model take is durable knowledge.

The canonical structural metatags, inline performance cues, and genre-specific prompt recipes that frame these slider settings live in sibling reference files — see the SKILL.md reference table.
