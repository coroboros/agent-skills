---
name: audio-loop
description: Use this skill whenever a user has an audio file (.wav/.mp3/.flac/etc.) that needs to loop as background on a website or web page — hero ambience, landing-page atmosphere, portfolio mood audio, ambient wind/rain/ocean/forest/breeze/pad beds, or any "play quietly behind the page while users read/scroll/interact" use case. Trigger on intents like making a clip loop seamlessly/gaplessly on a site, fixing a click/tick/pop/bump at the loop boundary, fixing stereo bias or L/R imbalance on a web-bound ambient clip, normalizing loudness (LUFS) for web delivery, encoding a loop for web playback, or fading audio in on first user click/gesture — in any web framework (Next.js, Vue, Astro, Nuxt, plain HTML). The skill outputs a gapless FLAC plus a paste-in Web Audio snippet that unlocks on first interaction. Skip for general audio editing (cuts, mixing, effects), music/podcast mastering, or transcription.
when_to_use: When the user has an audio clip that needs to loop seamlessly on a web page (hero backgrounds, ambient atmospheres, interactive scenes). When `<audio loop>` is producing an audible gap or tick at each iteration. When encoding / normalizing / rebalancing source audio for web delivery. Keywords — audio, loop, ambient, hero, background, breeze, wind, rain, atmosphere, soundscape, seamless, gapless, flac, web audio, loudness, lufs, normalize, stereo balance, ffmpeg. Skip when the user needs general audio editing (cuts, mixing, effects), music or podcast production, or audio transcription — those are different jobs.
argument-hint: "<input.wav> [options] — e.g. /audio-loop breeze.wav -t -28"
model: sonnet
allowed-tools: Bash(ffmpeg *) Bash(ffprobe *) Bash(command *) Bash(bash *) Bash(stat *) Read
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
metadata:
  author: coroboros
  sources:
    - ffmpeg.org
    - developer.mozilla.org/docs/Web/API/Web_Audio_API
---

# Audio Loop

Produce a web-ready seamless audio loop from any source clip: auto-correct stereo balance, normalize loudness, encode lossless FLAC so `AudioBufferSourceNode{loop:true}` plays it sample-accurate and gapless, emit a drop-in Web Audio snippet that unlocks playback on the first user gesture.

All ffmpeg work happens in `scripts/audio-loop.sh` — this skill validates the source, orchestrates the pipeline, and turns the script's summary into a report plus a ready-to-paste JS snippet.

## Parameters

| Flag | Default | Description |
|------|---------|-------------|
| `-t <LUFS>` | `-28` | Integrated loudness target (ambient web default) |
| `-v <0..1>` | `0.6` | Target volume baked into the emitted JS snippet |
| `-o <dir>` | input dir | Output directory |
| `-s` | off | Save to `.claude/output/audio-loop/{slug}/` |
| `-S` | — | Force no-save |
| `-B` | off | Disable stereo balance auto-correction |

**Where each flag is handled.** `-t`, `-o`, and `-B` pass through to `scripts/audio-loop.sh`. `-v` is skill-only — the agent reads it from `$ARGUMENTS` and interpolates it into the `TARGET` constant of the emitted JS snippet; the script never sees it. `-s` / `-S` follow the repo save-mode convention — the agent translates `-s` into an `-o <save_path>` passed to the script.

**Deliberately no crossfade flag.** If the source WAV has a real sample-level discontinuity at the loop boundary, that's source editing — outside this skill's scope. If the user is hearing a bump with FLAC + Web Audio, see **Diagnostic by negative result** below.

## Workflow

### 1. Validate tools

`command -v ffmpeg ffprobe`. Missing → stop and ask the user to install (macOS: `! brew install ffmpeg`, Debian/Ubuntu: `! sudo apt install ffmpeg`). Never auto-install.

### 2. Probe the source

The script reads duration, sample rate, channel count, and per-channel RMS via `astats`. Surface these early — the user sees the starting point before any processing.

### 3. Diagnose stereo imbalance (stereo sources only)

If the two channels differ by more than 1 dB RMS, the ear locks onto the louder side on sustained ambient content. The script auto-corrects with a `pan` filter unless `-B` is set:

```
pan=stereo|c0=FL|c1=<gain>*FR     # if R is louder
pan=stereo|c0=<gain>*FL|c1=FR     # if L is louder
```

Where `gain = 10^(-|delta_dB| / 20)`. The script computes `delta_dB` from the astats pass, picks the right direction, and wires the filter accordingly. Below the 1 dB threshold the imbalance isn't reliably perceptible on sustained ambient content — no filter is applied.

### 4. Run the pipeline

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/audio-loop.sh <input> [flags]
```

The script chains: probe → (optional pan correction) → `loudnorm=I=<target>:TP=-2:LRA=7` → `aresample=<source_rate>` (**crucial** — see **Rules**) → encode FLAC (`-c:a flac -compression_level 8`). It emits `RESULT: key=value` lines on stdout.

### 5. Report

Parse `RESULT:` lines and compose:

- Size comparison (source → FLAC, MB)
- Final integrated loudness + true peak
- Per-channel RMS confirming the balance is centred
- A drop-in Web Audio JS snippet tuned to the file's URL and the `-v` target

**Report template:**

```
| File | Size | Codec | Integrated LUFS | True peak |
|------|------|-------|-----------------|-----------|
| `<stem>.flac` | X MB | FLAC | -28.0 | -2.0 dBFS |

Stereo balance: L -19.70 dB / R -19.71 dB — centred (Δ 0.01 dB)
Duration: 6.50 s · Sample rate: 48 kHz · Channels: 2
```

**Web Audio snippet (paste-in-page):**

```html
<script>
(() => {
  const AUDIO_URL = '/audio/<stem>.flac'; // adjust to where you serve the file
  const TARGET = <v-value>;
  const FADE_MS = 700;

  let ctx, gain, bufferPromise, entered = false;

  function preload() {
    if (ctx) return;
    const Ctor = window.AudioContext || window.webkitAudioContext;
    if (!Ctor) return;
    ctx = new Ctor();
    gain = ctx.createGain();
    gain.gain.value = 0;
    gain.connect(ctx.destination);
    bufferPromise = fetch(AUDIO_URL)
      .then(r => r.arrayBuffer())
      .then(ab => ctx.decodeAudioData(ab));
  }

  async function unlock() {
    if (entered || !ctx) return;
    try { await ctx.resume(); } catch { return; }
    if (ctx.state !== 'running') return;
    let buf;
    try { buf = await bufferPromise; } catch { return; }
    if (entered) return; // second guard — a concurrent unlock() may have finished during the await
    const src = ctx.createBufferSource();
    src.buffer = buf;
    src.loop = true;
    src.connect(gain);
    src.start(0);
    entered = true;
    const now = ctx.currentTime;
    gain.gain.setValueAtTime(0, now);
    gain.gain.linearRampToValueAtTime(TARGET, now + FADE_MS / 1000);
  }

  const IGNORED = new Set(['Shift','Control','Alt','Meta','Tab','Escape','CapsLock']);
  preload();
  document.addEventListener('pointerdown', () => unlock(), { capture: true, once: true });
  document.addEventListener('keydown', e => { if (!IGNORED.has(e.key)) unlock(); }, { capture: true });
})();
</script>
```

For scroll-tied volume or any multi-channel control surface on top of the baseline, see `references/scroll-tied-pattern.md` — it documents the multiplicative factors architecture (`gain = TARGET × fadeInFactor × scrollVolumeFactor`) so additional control dimensions compose cleanly.

## Why Web Audio + FLAC (and not `<audio loop>` or AAC)

Useful context for debugging "I still hear a tick every few seconds" reports.

`<audio loop>` resets its decoder between iterations — the AAC pipeline contributes a few milliseconds of priming + MDCT-boundary artifacts that read as an audible gap on short loops (under 10 s). `AudioBufferSourceNode{loop:true}` is sample-accurate by spec: it wraps from `loopEnd` straight into `loopStart` with no decoder reset, and the buffer it loops is whatever `decodeAudioData` returned.

That means the codec baked into the decoded buffer still matters. AAC's priming samples (typically 2048 samples ≈ 43 ms at 48 kHz) are embedded in the buffer on many browser decoders — the loop wraps into those priming samples and the ear hears it. FLAC is lossless and has no priming, so the decoded buffer is byte-identical to the source WAV — genuinely seamless. The trade is file size: FLAC is typically 6–8× larger than AAC 128 kbps on noise-heavy content, but still modest at a few hundred KB to low single-digit MB for ambient loops.

### Diagnostic by negative result

If the user reports a lingering bump and tried a crossfade that made it *worse*, the discontinuity isn't at the signal layer — a real crossfade would smooth a sample-level click. It's at the codec layer (priming, MDCT, or similar). The fix is switching format, not masking. This is exactly why this skill has no crossfade flag — the absence pushes toward the right diagnosis.

## Browser autoplay constraint

Modern browsers block audible playback without a prior user gesture. The emitted snippet attaches one-time `pointerdown` and filtered `keydown` listeners on `document` — any real interaction anywhere on the page unlocks the audio, no splash screen or dedicated button required. `mousemove`, `scroll`, and `wheel` are **not** gestures per the spec; don't try to hook into them. `pointermove` isn't either. On reload the unlock must happen again — this is a per-navigation browser constraint with no workaround short of the user granting the origin autoplay privilege explicitly.

## Rules

- NEVER re-encode an already-encoded output — always start from the original WAV (or lossless source). Re-encoding FLAC→FLAC is pointless; re-encoding AAC→FLAC doesn't recover what AAC threw away.
- NEVER drop `aresample` after `loudnorm`. `loudnorm` silently upsamples to 192 kHz for its measurement pass; without the trailing `aresample` the FLAC is 4× the size it should be.
- FLAC is the only encoded output the skill produces. The opinion is deliberate — the "AAC is fine for short loops" habit is the failure mode this skill prevents.
- Stereo balance correction kicks in at Δ > 1 dB. The 1 dB threshold comes from JND research on sustained ambient content — below that, the ear doesn't reliably lock on an asymmetry, so adding a pan filter would cost encode quality without a perceptual payoff.
- Default loudness target is `-28 LUFS` for ambient web audio (quiet-enough-to-not-intrude, loud-enough-to-hear over UI sounds). Louder targets (e.g. `-18` for hero music) are a user call — pass `-t` explicitly.
- Always report source-vs-output size so the user explicitly accepts the FLAC size trade.
- Mono sources skip the balance step (stereo-only concern); everything else (loudnorm, encode) proceeds as normal.
- When the output path would overwrite the input (FLAC reprocessed in its own directory), the script exits with a clear error — pass `-o <dir>` to write elsewhere.
