---
name: video-loop
description: Create a seamless looping background video — crossfade the loop point, encode optimized MP4 + WebM, optional poster frame. Use whenever the user has a video that needs to loop for web use (hero sections, backgrounds, landing-page ambience), wants to fix a visible jump at the loop point, or needs to optimize a clip for web delivery — even if they just say "make this loop smoothly" or "compress this for the site".
when_to_use: When the user has a video that needs to loop seamlessly on the web (hero sections, backgrounds). When the end-to-start transition is visible and needs a crossfade fix. When optimizing video assets for web delivery (MP4 + WebM). Keywords — loop, video, background, hero, seamless, crossfade, encode, webm, mp4, ffmpeg, compress video, optimize video. For audio loops use /audio-loop (sibling skill, parallel architecture — loudness + gapless FLAC + Web Audio snippet). Skip when the user needs audio processing, cuts/trimming beyond looping, or motion-graphics work — those are different jobs.
argument-hint: "<input.mp4> [options] — e.g. /video-loop hero.mp4 -d 1.5"
model: sonnet
allowed-tools: Bash(ffmpeg *) Bash(ffprobe *) Bash(command *) Bash(bash *) Bash(stat *) Read
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
metadata:
  author: coroboros
  sources:
    - ffmpeg.org
---

# Video Loop

Create a seamless looping background video from any source clip. A crossfade blends the last and first frames so the `<video loop>` transition is invisible, then the pipeline encodes web-optimized MP4 + WebM.

All ffmpeg work happens in `scripts/video-loop.sh` — this skill validates inputs, optionally helps pick a good fade duration, invokes the script, and turns the script's summary into a human-readable report.

## Parameters

| Flag | Default | Description |
|------|---------|-------------|
| `-d <seconds>` | `1.5` | Crossfade duration in seconds |
| `-q <crf>` | `26` | H.264 CRF — 18 = high quality, 28 = smaller file |
| `-w <crf>` | `32` | VP9 WebM CRF |
| `-o <dir>` | Same as input | Output directory |
| `-p` | off | Also extract a poster frame (first frame as JPEG) |
| `-n` | off | No crossfade — optimize and encode only |

## Workflow

### 1. Validate tools

Confirm `ffmpeg` and `ffprobe` are available: `command -v ffmpeg ffprobe`. If either is missing, stop and ask the user to install (macOS: `! brew install ffmpeg`, Debian/Ubuntu: `! sudo apt install ffmpeg`). Never auto-install.

### 2. Analyze loop quality (optional but recommended)

Before committing to a crossfade, extract the first and last frames and compare them — this is the one step in the pipeline that genuinely benefits from the model's visual reasoning:

```bash
ffmpeg -y -ss 0 -i <input> -frames:v 1 -update 1 /tmp/vl-first.png
ffmpeg -y -sseof -0.1 -i <input> -frames:v 1 -update 1 /tmp/vl-last.png
```

Read both frames. If they're nearly identical, suggest `-n` (the source already loops cleanly, crossfade would only blur motion). If they differ significantly, proceed with the default fade or recommend a longer `-d` for more gradual blending.

### 3. Run the pipeline

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/video-loop.sh <input> [flags]
```

The script does the rest: probes metadata, builds the lossless loop intermediate when crossfade is requested, encodes MP4 (H.264 + faststart) and WebM (VP9), optionally extracts a poster frame. It emits a machine-readable summary on stdout, one `RESULT: key=value` line per fact.

### 4. Report

Parse the `RESULT:` lines to compose:

- A size table comparing input vs outputs (absolute MB and delta percent)
- A ready-to-paste HTML snippet for the user's site

**Report template:**

```
| File | Size | Codec | vs Original |
|------|------|-------|-------------|
| `*-opt.mp4` | X MB | H.264 | -XX% |
| `*.webm` | X MB | VP9 | -XX% |
| `*-poster.jpg` | X KB | JPEG | — |
```

**HTML snippet:**

```html
<video autoplay muted loop playsinline preload="metadata" poster="/videos/poster.jpg">
  <source src="/videos/name.webm" type="video/webm" />
  <source src="/videos/name-opt.mp4" type="video/mp4" />
</video>
```

WebM first — browsers pick the first supported source.

## Why crossfade-first matters

Useful background for debugging "I still see a jump" reports. The script places the xfade at the **start** of the output, not the end:

- `[xfade]` (F seconds): blends `A[end]` → `A[start]`. First frame = `A[D-F]`, last frame = `A[F]`
- `[middle]` (D−2F seconds): untouched frames from `A[F]` to `A[D-F]`

At the loop boundary, `[middle]` ends at `A[D-F]` and the player loops back to `[xfade]`, which starts at the same frame — invisible transition. If the xfade were placed at the end (`[middle][xfade]`), the xfade would end at `A[F]` but loop back to `A[0]` — a visible jump of F seconds.

If the user reports a visible jump despite running the skill, first check whether they pointed at an already-encoded file (re-running re-encodes but doesn't re-loop). If the source is correct, try a longer `-d` — short fades are more visible on high-motion content.

## Rules

- NEVER upscale — the script encodes at source resolution
- NEVER re-encode an already-encoded output (double compression). Always start from the original source
- Audio is always stripped (`-an`) — background videos are muted
- The script rejects `-d >= duration/2` — a too-long fade would leave the middle segment empty
- Always report original vs output sizes so the user sees the quality/size tradeoff
