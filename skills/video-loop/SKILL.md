---
name: video-loop
description: Prepare a background video loop for a website with optional crossfade, MP4/WebM encoding and poster extraction. Use for loop joins or web delivery of an existing clip.
when_to_use: When the user has a video that needs to loop without visible artifacts on the web (hero sections, backgrounds), or when the end-to-start transition is visible and needs a crossfade fix, or when optimizing video assets for web delivery (MP4 + WebM). Keywords — loop, video, background, hero, seamless, crossfade, encode, webm, mp4, ffmpeg, compress video, optimize video. For audio loops use `/audio-loop` (sibling — parallel architecture, loudness + gapless FLAC + Web Audio snippet). Skip for audio processing, cuts/trimming beyond looping, or motion-graphics work.
argument-hint: "<input.mp4> [options] — e.g. /video-loop hero.mp4 -d 1.5"
allowed-tools: Bash(ffmpeg *) Bash(ffprobe *) Bash(command *) Bash(bash *) Bash(stat *) Read
license: MIT
compatibility: "Requires bash, FFmpeg with libx264/libvpx-vp9 and ffprobe. Visual continuity verification requires playback or frame inspection in the target environment."
metadata:
  author: coroboros
  sources: "ffmpeg.org"
---

# Video Loop

Prepare a background video with an optional end-to-start crossfade and MP4/WebM encoding. Verify repeated playback before claiming an invisible transition; motion and source continuity can still make the join visible.

All ffmpeg work happens in `scripts/video-loop.sh` — this skill validates inputs, optionally helps pick a good fade duration, invokes the script, and turns the script's summary into a human-readable report.

## Parameters

| Flag | Default | Description |
|------|---------|-------------|
| `-d <seconds>` | `1.5` | Crossfade duration in seconds |
| `-q <crf>` | `26` | H.264 CRF — 18 = high quality, 28 = smaller file |
| `-w <crf>` | `32` | VP9 WebM CRF |
| `-o <dir>` | Same as input | Output directory |
| `-p` | off | Also extract a poster frame (first frame as JPEG) |
| `-C` | off | Disable the crossfade — optimize and encode only (`-n` accepted as a deprecated alias) |

> **No `-s/-S` save-mode flag.** Unlike media-cluster siblings (`/audio-loop`, `/markitdown`), video-loop outputs are web assets (MP4 / WebM / poster) the user drops directly into their site's video directory. No downstream skill consumes video files via `-f`, so the `~/.agents/output/<skill>/<project>/` convention would add ceremony without enabling anything — `-o <dir>` is the direct path.

## Workflow

### 1. Validate tools

Confirm `ffmpeg` and `ffprobe` are available: `command -v ffmpeg ffprobe`. If either is missing, stop and ask the user to install (macOS: `brew install ffmpeg`, Debian/Ubuntu: `sudo apt install ffmpeg`). Never auto-install.

### 2. Analyze loop quality (optional but recommended)

Before committing to a crossfade, extract the first and last frames and compare them — this is the one step in the pipeline that genuinely benefits from the model's visual reasoning:

```bash
ffmpeg -y -ss 0 -i <input> -frames:v 1 -update 1 /tmp/vl-first.png
ffmpeg -y -sseof -0.1 -i <input> -frames:v 1 -update 1 /tmp/vl-last.png
```

Read both frames. If they're nearly identical, suggest `-C` (the source already loops cleanly, crossfade would only blur motion). If they differ significantly, proceed with the default fade or recommend a longer `-d` for more gradual blending.

### 3. Run the pipeline

`$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing this SKILL.md elsewhere.

```bash
bash "$SKILL_DIR"/scripts/video-loop.sh <input> [flags]
```

The script does the rest: probes metadata, builds the lossless loop intermediate when crossfade is requested, encodes MP4 (H.264 + faststart) and WebM (VP9), optionally extracts a poster frame. It emits a machine-readable summary on stdout, one `RESULT: key=value` line per fact.

### 4. Verify and report

Play both outputs across several joins in the target browser, checking motion continuity and any crossfade ghosting. First/last-frame comparison alone cannot establish smooth motion. If playback inspection is unavailable, report encoding checks separately and leave visual continuity unverified. The script rejects any output that aliases its source, including a WebM in its own output directory; use `-o` elsewhere.

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

At the loop boundary, the middle approaches the source position where the crossfade begins; actual frame rounding and motion still need playback verification. If the xfade were placed at the end (`[middle][xfade]`), the xfade would end at `A[F]` but loop back to `A[0]` — a visible jump of F seconds.

For a remaining jump, verify the source and inspect the transition before choosing another fade duration. Reprocessing with a fade enabled applies the loop edit again, so return to the original source instead of compounding edits.

## Rules

- NEVER upscale — the script encodes at source resolution
- NEVER re-encode an already-encoded output (double compression). Always start from the original source
- Audio is always stripped (`-an`) — background videos are muted
- The script rejects `-d >= duration/2` — a too-long fade would leave the middle segment empty
- Always report original vs output sizes so the user sees the quality/size tradeoff
