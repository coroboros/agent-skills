#!/usr/bin/env bash
# download-media.sh — wrap yt-dlp/yt-dlp for the agent-skills repo.
#
# Usage: download-media.sh [-a] [-b] [-p] [-i] [-c A-B] [-u LANGS] [-r HEIGHT] [-d DIR] <url> [extra yt-dlp args...]
#
#   -a          audio only, mp3 (yt-dlp preset -t mp3; needs ffmpeg)
#   -b          best native quality — skip the mp4 compatibility preset
#   -p          full playlist (default: single video via --no-playlist)
#   -i          inspect only — list available formats, no download
#   -c A-B      clip a time range, e.g. -c 10:15-12:30 (needs ffmpeg)
#   -u LANGS    subtitles as sidecar files, e.g. -u "en.*,fr" (includes auto-generated)
#   -r HEIGHT   cap resolution, e.g. -r 1080
#   -d DIR      destination dir (default ~/.agents/output/<project>/download-media/<slug>/)
#
# Everything after the URL is passed to yt-dlp verbatim.
# Emits `RESULT: key=value` lines for the skill to parse.

set -euo pipefail

AUDIO=0
BEST=0
PLAYLIST=0
INFO=0
SECTION=""
SUBS=""
HEIGHT=""
DEST=""

while getopts ":abpic:u:r:d:" opt; do
  case "$opt" in
    a) AUDIO=1 ;;
    b) BEST=1 ;;
    p) PLAYLIST=1 ;;
    i) INFO=1 ;;
    c) SECTION="$OPTARG" ;;
    u) SUBS="$OPTARG" ;;
    r) HEIGHT="$OPTARG" ;;
    d) DEST="$OPTARG" ;;
    :) echo "ERR: -$OPTARG requires a value" >&2; exit 2 ;;
    *) echo "ERR: unknown flag -$OPTARG" >&2; exit 2 ;;
  esac
done
shift $((OPTIND - 1))

if ! command -v yt-dlp >/dev/null 2>&1; then
  echo "ERR: yt-dlp not installed — run: brew install yt-dlp (or: pipx install yt-dlp)" >&2
  exit 127
fi

URL="${1:-}"
if [[ -z "$URL" ]]; then
  echo "ERR: URL required" >&2
  exit 2
fi
shift

case "$URL" in
  http://*|https://*|*:*) ;;  # plain URLs plus extractor prefixes like ytsearch:
  *) echo "ERR: not a URL: $URL" >&2; exit 2 ;;
esac

if [[ -n "$HEIGHT" && ! "$HEIGHT" =~ ^[0-9]+$ ]]; then
  echo "ERR: -r takes a height in pixels, e.g. -r 1080" >&2
  exit 2
fi

if [[ $AUDIO -eq 1 && ( -n "$HEIGHT" || $BEST -eq 1 ) ]]; then
  echo "ERR: -r and -b are video flags — drop them with -a" >&2
  exit 2
fi

PL_FLAG=--no-playlist
[[ $PLAYLIST -eq 1 ]] && PL_FLAG=--yes-playlist

# Info mode downloads nothing — it wins over download flags and skips the ffmpeg gate.
if [[ $INFO -eq 1 ]]; then
  exec yt-dlp -F "$PL_FLAG" "$URL" "$@"
fi

HAVE_FFMPEG=1
command -v ffmpeg >/dev/null 2>&1 || HAVE_FFMPEG=0
if [[ $HAVE_FFMPEG -eq 0 ]]; then
  if [[ $AUDIO -eq 1 || -n "$SECTION" ]]; then
    echo "ERR: -a and -c need ffmpeg — run: brew install ffmpeg" >&2
    exit 3
  fi
  echo "WARN: ffmpeg not found — video+audio merging unavailable, falling back to single-file formats" >&2
fi

# Slug from the URL tail: last path segment, else the query (youtube.com/watch?v=ID).
TAIL="${URL#*://}"
QUERY=""
case "$TAIL" in
  *\?*) QUERY="${TAIL#*\?}"; TAIL="${TAIL%%\?*}" ;;
esac
TAIL="${TAIL%/}"
SEG="${TAIL##*/}"
[[ -z "$SEG" || "$SEG" == "watch" ]] && SEG="$QUERY"
SLUG=$(printf '%s' "$SEG" \
  | tr '[:upper:]' '[:lower:]' \
  | tr -cs 'a-z0-9' '-' \
  | sed -E 's/^-+|-+$//g' \
  | cut -d'-' -f1-5)
[[ -z "$SLUG" ]] && SLUG="media"

if [[ -z "$DEST" ]]; then
  # Global per repo-conventions.md § Output paths: ~/.agents/output/{project}/download-media/{slug}.
  PROJECT=$(basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-*//; s/-*$//')
  : "${PROJECT:=unnamed}"
  DEST="${HOME}/.agents/output/${PROJECT}/download-media/${SLUG}"
fi
mkdir -p "$DEST"

ARGS=(-P "$DEST" "$PL_FLAG")
[[ $PLAYLIST -eq 1 ]] && ARGS+=(-o "%(playlist_title)s/%(playlist_index)03d - %(title)s [%(id)s].%(ext)s")

if [[ $AUDIO -eq 1 ]]; then
  ARGS+=(-t mp3)
elif [[ $BEST -eq 0 && $HAVE_FFMPEG -eq 1 ]]; then
  ARGS+=(-t mp4)  # h264/aac preferred, remuxed to mp4 — plays everywhere; -b keeps the native best
fi

# Filter composes with the mp4 preset's sort: -f narrows the set, -S orders inside it.
[[ -n "$HEIGHT" ]] && ARGS+=(-f "bv*[height<=${HEIGHT}]+ba/b[height<=${HEIGHT}]")
[[ -n "$SECTION" ]] && ARGS+=(--download-sections "*${SECTION}")
[[ -n "$SUBS" ]] && ARGS+=(--write-subs --write-auto-subs --sub-langs "$SUBS")

# after_move:filepath = final path post-merge/remux; --print-to-file keeps progress visible
# (--print would imply --quiet).
MANIFEST=$(mktemp -t download-media.XXXXXX)
trap 'rm -f "$MANIFEST"' EXIT
# --no-abort-on-error is yt-dlp's default: it skips failing playlist entries but
# still exits non-zero. Capture the code so partial successes keep their RESULT
# lines, then propagate it.
RC=0
yt-dlp "${ARGS[@]}" --print-to-file after_move:filepath "$MANIFEST" "$URL" "$@" || RC=$?

COUNT=0
while IFS= read -r FILE; do
  [[ -z "$FILE" ]] && continue
  echo "RESULT: path=$FILE"
  COUNT=$((COUNT + 1))
done < "$MANIFEST"
echo "RESULT: files=$COUNT"
echo "RESULT: dest=$DEST"
echo "RESULT: slug=$SLUG"
exit $RC
