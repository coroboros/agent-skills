---
name: download-media
description: Download video or audio from ~1800 sites (YouTube, Vimeo, SoundCloud, Twitch, X…) with the `yt-dlp` CLI — full videos, mp3 audio, playlists, time-range clips, subtitles, capped resolutions. Use whenever the user wants to download, save, grab, or rip a video/audio/playlist from a URL, extract a song as mp3, clip a segment, or fetch subtitles — even when they just say "download this", "get the audio", or "save this playlist".
when_to_use: When the user has a media URL and wants the file on disk — video, audio-only, playlist, clip, or subtitles. Keywords — download video, yt-dlp, youtube, save video, extract audio, mp3, rip, playlist, clip, subtitles, 1080p. Skip when the user wants the transcript or text content (/markitdown), wants to loop or re-encode a local file (/video-loop, /audio-loop), or targets DRM-protected streaming services (Netflix, Disney+, Spotify…) — yt-dlp does not bypass DRM and neither does this skill.
argument-hint: "[-a] [-b] [-p] [-i] [-c A-B] [-u langs] [-r height] [-d dir] <url> [yt-dlp args]"
allowed-tools: Bash(bash *) Bash(yt-dlp *) Bash(command *) Read
license: MIT
metadata:
  author: coroboros
  sources:
    - github.com/yt-dlp/yt-dlp
---

# Download Media

Download video or audio from any [yt-dlp-supported site](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md) using the [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) CLI. The skill validates the input, composes the right flags for the intent, downloads under `~/.agents/output/<project>/download-media/<slug>/` (or a `-d` destination), and reports the final file paths — fully expanded, no tilde, no magic.

The deterministic work — install checks, slug derivation, destination, flag composition, final-path capture — happens in `scripts/download-media.sh`. The skill parses `$ARGUMENTS`, hands them to the script, and turns the script's `RESULT:` lines into a human report.

## Scope

Personal and authorized use: public content, the user's own uploads, Creative Commons and licensed material. yt-dlp cannot bypass DRM and this skill never attempts to; decline requests to rip paid streaming catalogs (Netflix, Disney+, Spotify…) or to evade a site's paywall. Downloading may still be restricted by a site's terms of service and local copyright law — when a request is plainly about piracy, say so and stop.

## Install

```bash
brew install yt-dlp        # macOS
pipx install yt-dlp        # any platform
brew install ffmpeg        # strongly recommended — merging, mp3 extraction, clipping
```

Binaries for other setups: [yt-dlp releases](https://github.com/yt-dlp/yt-dlp/releases/latest). For full YouTube support yt-dlp also wants a JavaScript runtime (deno recommended) — see the [EJS wiki](https://github.com/yt-dlp/yt-dlp/wiki/EJS). Extractors break when sites change; a failing download is often fixed by updating: `brew upgrade yt-dlp` or `pipx upgrade yt-dlp`.

## Parameters

| Flag | Default | Effect |
|------|---------|--------|
| `-a` | off | Audio only, mp3 (yt-dlp preset `-t mp3`; needs ffmpeg; rejects the video flags `-r`/`-b`) |
| `-b` | off | Best native quality — skip the mp4 compatibility preset |
| `-p` | off | Full playlist into a `<playlist title>/` subfolder, files named `NNN - title [id].ext` (default: single video) |
| `-i` | off | Inspect only — list available formats, no download; wins over the download flags |
| `-c A-B` | — | Clip a time range, e.g. `-c 10:15-12:30` (needs ffmpeg) |
| `-u <langs>` | — | Subtitles as sidecar files, e.g. `-u "en.*,fr"` (includes auto-generated) |
| `-r <height>` | — | Cap resolution, e.g. `-r 1080` |
| `-d <dir>` | convention path | Destination directory |

Everything after the URL passes to yt-dlp verbatim — the escape hatch to the full CLI (see Recipes).

Default download: `-t mp4` preset — h264/aac preferred, remuxed to mp4, plays everywhere. `-b` keeps yt-dlp's native best (often webm/mkv, higher fidelity, less compatible).

## Workflow

1. **Empty `$ARGUMENTS`** → propose the most recent media URL from session context and confirm. Ask only when none is detectable.
2. Run the helper:

   `$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing this SKILL.md elsewhere.

   ```bash
   bash "$SKILL_DIR"/scripts/download-media.sh $ARGUMENTS
   ```

   Always single-quote the URL in the command — YouTube URLs routinely carry `&` and `?`, which the shell otherwise interprets.

3. The script emits `RESULT: key=value` lines — one `path` per downloaded file, then `files`, `dest`, `slug` (order not guaranteed; parse by key). With `-i` it prints yt-dlp's format table instead.
4. Parse the `RESULT:` lines and produce the report below.
5. `ERR: yt-dlp not installed` (exit 127) or `ERR: -a and -c need ffmpeg` (exit 3) → print the matching command from `## Install` and stop. Never auto-install on the user's behalf.
6. Any other `ERR:` (exit 2 — missing or non-URL input, unknown flag, missing flag value, invalid `-r`, conflicting flags) → relay the message verbatim and stop. A non-zero exit *with* `RESULT:` lines means a partial playlist success — report the downloaded files and the failure. A yt-dlp extraction failure → surface its stderr and suggest updating yt-dlp first (see Install).

## Output

```
downloaded: <n> file(s) → <dest>
  <path>            # one line per file
```

Subtitle sidecars (`-u`) sit next to the media file but are not listed in `RESULT:` lines — mention they are in `dest`.

## Examples

```bash
/download-media https://youtu.be/dQw4w9WgXcQ                 # video, mp4, best compatible
/download-media -a https://youtu.be/dQw4w9WgXcQ              # mp3
/download-media -r 1080 <url>                                 # cap at 1080p
/download-media -p <playlist-url>                             # whole playlist
/download-media -c 10:15-12:30 <url>                          # clip a segment
/download-media -u "en.*" <url>                               # video + English subtitles
/download-media -i <url>                                      # list formats, download nothing
/download-media -d ~/Downloads <url>                          # custom destination
/download-media <url> --embed-thumbnail --embed-metadata      # passthrough after the URL
```

## Recipes — passthrough after the URL

| Intent | Append after the URL |
|--------|---------------------|
| Logged-in / member content | `--cookies-from-browser firefox` (or `chrome`, `safari`…) |
| Strip sponsor segments | `--sponsorblock-remove sponsor` (needs ffmpeg) |
| Incremental playlist sync | `--download-archive <dir>/archive.txt` |
| Split by chapters | `--split-chapters` |
| Embed thumbnail + metadata | `--embed-thumbnail --embed-metadata` |
| Only playlist items 3–7 | `-I 3:7` (with `-p`) |
| Frame-accurate clip cuts | `--force-keyframes-at-cuts` (with `-c`; slow, re-encodes) |
| Gentle on rate limits | `-t sleep` (preset: spaced requests) |
| Site needs TLS impersonation | `--extractor-args` per site, or install `curl_cffi` |

Compose other yt-dlp flags the same way when an intent is not covered — the full option surface is `yt-dlp --help`.

## Notes

- **Final paths are captured, not guessed** — the script uses `--print-to-file after_move:filepath` so the reported paths are the real ones after merge/remux (`--print` would silence download progress).
- **Playlist URLs holding a `v=` too** (watch-page URLs) download the single video by default; `-p` switches to the whole playlist.
- **Unavailable playlist entries don't lose the run** — yt-dlp skips them and exits non-zero; the script still reports every downloaded file, then propagates the exit code.
- **`-c` takes a time range only** (`START-END`, `HH:MM:SS` or seconds). Chapter-regex sections go through passthrough: `--download-sections "intro"`.
- **Custom `-o` output templates** passed through work, but an absolute `-o` makes yt-dlp ignore the destination dir (`-P`) — prefer `-d` for relocation.
- **No silent overwrites** — yt-dlp skips already-downloaded files by default and the slug-namespaced destination keeps runs predictable.

## Why the wrapper

`yt-dlp` is already a superb CLI; this skill exists to (a) put downloads under the repo's global output convention with the final paths reported deterministically, (b) translate "get me the audio" into the right preset without the user remembering `-t mp3` vs `-x --audio-format`, and (c) keep the full flag surface reachable through verbatim passthrough instead of re-wrapping ~200 options.
