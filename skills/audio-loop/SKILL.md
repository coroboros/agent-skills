---
name: audio-loop
description: 'Prepare an existing audio bed for website looping: normalize loudness, optionally balance stereo, encode FLAC and provide Web Audio playback. Use for web ambience or loop-boundary diagnosis; source discontinuities require separate editing.'
when_to_use: When the user has an audio clip that needs to loop without audible artifacts on a web page, or when `<audio loop>` is producing an audible gap or tick at each iteration. Keywords — audio, loop, ambient, hero, background, breeze, wind, rain, atmosphere, soundscape, seamless, gapless, flac, web audio, loudness, lufs, normalize, stereo balance, ffmpeg. For video loops use `/video-loop` (sibling — parallel architecture, crossfade + MP4/WebM encode). Skip for composing, mixing, or mastering music/podcasts, and for transcription — looping an existing music bed for a page stays in scope.
argument-hint: "<input.wav> [options] — e.g. /audio-loop breeze.wav -t -28"
allowed-tools: Bash(ffmpeg *) Bash(ffprobe *) Bash(command *) Bash(bash *) Bash(stat *) Read
license: MIT
compatibility: "Requires bash, FFmpeg and ffprobe for local encoding. Playback verification requires a browser with Web Audio and FLAC decoding; the script does not repair source discontinuities."
metadata:
  author: coroboros
  sources: "ffmpeg.org; developer.mozilla.org/docs/Web/API/Web_Audio_API"
---

# Audio Loop

Prepare a source that already joins continuously for Web Audio playback: optionally balance stereo, normalize loudness and encode FLAC. The pipeline does not repair source discontinuities; inspect the join before promising a seamless result.

All ffmpeg work happens in `scripts/audio-loop.sh` — this skill validates the source, orchestrates the pipeline, and turns the script's summary into a report plus a ready-to-paste JS snippet.

## Parameters

| Flag | Default | Description |
|------|---------|-------------|
| `-t <LUFS>` | `-28` | Integrated loudness target (ambient web default) |
| `-v <0..1>` | `0.6` | Target volume baked into the emitted JS snippet |
| `-o <dir>` | input dir | Output directory |
| `-s` | off | Save to `~/.agents/output/{project}/audio-loop/{slug}/` |
| `-S` | off | Force no-save |
| `-B` | off | Disable stereo balance auto-correction |

**Where each flag is handled.** `-t`, `-o`, and `-B` pass through to `scripts/audio-loop.sh`. `-v` is skill-only — the agent reads it from `$ARGUMENTS` and interpolates it into the `TARGET` constant of the emitted JS snippet; the script never sees it. `-s` / `-S` follow the repo save-mode convention — the agent translates `-s` into an `-o <save_path>` passed to the script, where `<save_path>` is `~/.agents/output/{project}/audio-loop/{slug}/` (`{project}` = kebab-cased basename of the git toplevel, else cwd; create it `$HOME`-expanded, report the fully-expanded absolute path — no tilde, no magic).

**Deliberately no crossfade flag.** If the source WAV has a real sample-level discontinuity at the loop boundary, that's source editing — outside this skill's scope. If the user is hearing a bump with FLAC + Web Audio, see **Diagnostic by negative result** below.

## Workflow

### 1. Validate tools

`command -v ffmpeg ffprobe`. Missing → stop and ask the user to install (macOS: `brew install ffmpeg`, Debian/Ubuntu: `sudo apt install ffmpeg`). Never auto-install.

### 2. Probe the source

The script reads duration, sample rate, channel count, and per-channel RMS via `astats`. Surface these early — the user sees the starting point before any processing.

### 3. Diagnose stereo imbalance (stereo sources only)

The script uses 1 dB RMS as its chosen correction threshold, applying a `pan` filter unless `-B` is set. Use `-B` to preserve intentional stereo asymmetry:

```
pan=stereo|c0=FL|c1=<gain>*FR     # if R is louder
pan=stereo|c0=<gain>*FL|c1=FR     # if L is louder
```

Where `gain = 10^(-|delta_dB| / 20)`. The script computes `delta_dB` from the astats pass, picks the right direction, and wires the filter accordingly. At or below the chosen 1 dB threshold no filter is applied. This is a workflow default, not a universal perceptual guarantee.

### 4. Run the pipeline

`$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing this SKILL.md elsewhere.

```bash
bash "$SKILL_DIR"/scripts/audio-loop.sh <input> [flags]
```

The script chains: probe → (optional pan correction) → `loudnorm=I=<target>:TP=-2:LRA=7` → `aresample=<source_rate>` → `asetnsamples=n=4608:p=0` (bounded frames without padding) → encode FLAC (`-c:a flac -compression_level 8`). It emits `RESULT: key=value` lines on stdout.

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
  const onKeydown = e => {
    if (IGNORED.has(e.key)) return;
    document.removeEventListener('keydown', onKeydown, { capture: true });
    unlock();
  };
  preload();
  document.addEventListener('pointerdown', () => unlock(), { capture: true, once: true });
  document.addEventListener('keydown', onKeydown, { capture: true });
})();
</script>
```

For scroll-tied volume or any multi-channel control surface on top of the baseline, see `references/scroll-tied-pattern.md` — it documents the multiplicative factors architecture (`gain = TARGET × fadeInFactor × scrollVolumeFactor`) so additional control dimensions compose cleanly.

## Verify the loop boundary

Web Audio loops a decoded buffer; codec decoding and the original signal both matter. FLAC preserves the processed PCM, not the original WAV after normalization or balance changes. `decodeAudioData` may resample to the AudioContext rate: see [MDN](https://developer.mozilla.org/en-US/docs/Web/API/BaseAudioContext/decodeAudioData).

Inspect decoded endpoints and listen across repeated joins in the target browser before claiming seamless playback. A failed or worsening crossfade does not prove a codec defect: source discontinuity, fade placement, processing and playback can all contribute. Compare lossless source and decoded output to isolate the cause. Report size from actual files rather than predicting a compression ratio.

### Diagnostic by negative result

Treat a worse crossfade as evidence against that attempted edit, not a definitive diagnosis. If the source itself does not join, identify the required source edit and continue only within the user's authorized scope. The bundled script has no crossfade operation.

## Browser autoplay constraint

Modern browsers block audible playback without a prior user gesture. The emitted snippet attaches one-time `pointerdown` and filtered `keydown` listeners on `document` — any real interaction anywhere on the page unlocks the audio, no splash screen or dedicated button required. `mousemove`, `scroll`, and `wheel` are **not** gestures per the spec; don't try to hook into them. `pointermove` isn't either. On reload the unlock must happen again — this is a per-navigation browser constraint with no workaround short of the user granting the origin autoplay privilege explicitly.

## Rules

- NEVER re-encode an already-encoded output — always start from the original WAV (or lossless source). Re-encoding FLAC→FLAC is pointless; re-encoding AAC→FLAC doesn't recover what AAC threw away.
- Preserve the source sample rate after dynamic `loudnorm`, which can upsample to 192 kHz. Bound encoder frame size without padding; verify duration/sample count when changing that stage.
- FLAC is the only encoded output the skill produces. The opinion is deliberate — the "AAC is fine for short loops" habit is the failure mode this skill prevents.
- Stereo correction uses the chosen Δ > 1 dB default; it does not establish perceptual centering for every source.
- Default loudness target is `-28 LUFS` for ambient web audio (quiet-enough-to-not-intrude, loud-enough-to-hear over UI sounds). Louder targets (e.g. `-18` for hero music) are a user call — pass `-t` explicitly.
- Report source/output sizes and playback verification; retain already-authorized encoding scope.
- Mono sources skip the balance step (stereo-only concern); everything else (loudnorm, encode) proceeds as normal.
- When the output path would overwrite the input (FLAC reprocessed in its own directory), the script exits with a clear error — pass `-o <dir>` to write elsewhere.
