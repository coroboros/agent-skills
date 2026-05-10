---
suno_version: v5.5
title: Whitelist Green Test
bpm: 92
key: D minor
length_target: "3:30"
voice_profile: null
custom_model: null
created: 2026-05-10
revised: null
---

# Whitelist Green Test

## Suno prompt block

### Style of Music
```text
Country soul, late 70s analog, Pedal Steel, Sub Bass, Acoustic Guitar, raspy male vocal, 92 BPM
```

### Lyrics
```text
[Intro]
[Pedal steel guitar, sustained]

[Verse 1]
The road keeps rolling under wheels
The night keeps coming on

[Chorus]
We carry on
```

### Exclude Styles
```text
808s, autotune, EDM drops
```

## Sliders
- **Weirdness**: 35
- **Style Influence**: 75

## Voice / Custom Model
None.

## Rationale
Test fixture for GREEN — every Title-Case pair (`Pedal Steel`, `Sub Bass`,
`Acoustic Guitar`, `Plate Reverb`) is in the NON_ARTIST_PHRASES whitelist.
No citation patterns. No false positives.

## Iteration log
- v0 (2026-05-10): whitelist-green fixture
