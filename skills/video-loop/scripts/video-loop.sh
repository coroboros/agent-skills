#!/usr/bin/env bash
#
# video-loop.sh — build a seamless looping background video (MP4 + WebM)
#
# Usage:
#   video-loop.sh <input> [-d <fade>] [-q <h264_crf>] [-w <vp9_crf>] [-o <out_dir>] [-p] [-n]
#
# Options:
#   -d <fade>       Crossfade duration in seconds (default: 1.5)
#   -q <h264_crf>   H.264 CRF — 18=high quality, 28=small file (default: 26)
#   -w <vp9_crf>    VP9 CRF (default: 32)
#   -o <out_dir>    Output directory (default: same as input)
#   -p              Also extract poster frame (first frame as JPEG)
#   -n              No crossfade — re-encode only
#
# Pipeline:
#   probe → (optional crossfade → lossless intermediate) → encode MP4 → encode WebM → (optional poster)
#
# The crossfade is placed at the START of the output so the loop point is
# invisible: middle ends at frame A[D-F], loops back to the xfade which also
# starts at A[D-F]. Same frame — no jump.
#
# Emits a machine-readable summary on stdout prefixed with "RESULT:", one
# key=value per line. Consumers parse these to report file sizes and deltas.

set -euo pipefail

FADE=1.5
H264_CRF=26
VP9_CRF=32
OUT_DIR=""
POSTER=0
NO_FADE=0

usage() {
  sed -n '2,22p' "$0" | sed 's/^# \{0,1\}//'
  exit 2
}

[[ $# -lt 1 ]] && usage
case "$1" in -h|--help) usage ;; esac

INPUT=$1
shift

while getopts ":d:q:w:o:pn" opt; do
  case $opt in
    d) FADE=$OPTARG ;;
    q) H264_CRF=$OPTARG ;;
    w) VP9_CRF=$OPTARG ;;
    o) OUT_DIR=$OPTARG ;;
    p) POSTER=1 ;;
    n) NO_FADE=1 ;;
    \?) echo "unknown flag: -$OPTARG" >&2; usage ;;
    :)  echo "flag -$OPTARG requires a value" >&2; usage ;;
  esac
done

# --- Validate ---------------------------------------------------------------

[[ -f "$INPUT" ]] || { echo "error: input not found: $INPUT" >&2; exit 1; }
command -v ffmpeg  >/dev/null || { echo "error: ffmpeg not installed" >&2;  exit 1; }
command -v ffprobe >/dev/null || { echo "error: ffprobe not installed" >&2; exit 1; }

# --- Resolve paths ----------------------------------------------------------

INPUT_ABS=$(cd "$(dirname "$INPUT")" && pwd)/$(basename "$INPUT")
BASENAME=$(basename "$INPUT")
STEM="${BASENAME%.*}"
[[ -z "$OUT_DIR" ]] && OUT_DIR=$(dirname "$INPUT_ABS")
mkdir -p "$OUT_DIR"

MP4="$OUT_DIR/${STEM}-opt.mp4"
WEBM="$OUT_DIR/${STEM}.webm"
POSTER_JPG="$OUT_DIR/${STEM}-poster.jpg"
LOOP_TMP="/tmp/vl-loop-$$.mkv"

# --- Probe ------------------------------------------------------------------

DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$INPUT_ABS")
# stat has different flags on macOS (-f%z) vs GNU/Linux (-c%s); try both.
INPUT_BYTES=$(stat -f%z "$INPUT_ABS" 2>/dev/null || stat -c%s "$INPUT_ABS")

trap 'rm -f "$LOOP_TMP"' EXIT

# --- Crossfade (optional) ---------------------------------------------------

if [[ $NO_FADE -eq 1 ]]; then
  LOOP_SOURCE="$INPUT_ABS"
else
  # The fade splits the video into three pieces: end_part ($FADE s from the
  # tail), start_part ($FADE s from the head), middle (the remainder). We
  # xfade end_part → start_part and prepend it to middle, producing an output
  # that loops back to the same frame it ends on.
  TRIM_END=$(awk -v d="$DURATION" -v f="$FADE" 'BEGIN { printf "%.6f", d - f }')
  HALF=$(awk -v d="$DURATION" 'BEGIN { printf "%.6f", d / 2 }')
  if awk -v f="$FADE" -v h="$HALF" 'BEGIN { exit !(f >= h) }'; then
    echo "error: fade ($FADE s) >= half of duration ($HALF s) — pick a shorter -d" >&2
    exit 1
  fi

  ffmpeg -y -loglevel warning -i "$INPUT_ABS" -i "$INPUT_ABS" -filter_complex "
    [0:v]trim=start=${TRIM_END},setpts=PTS-STARTPTS[end_part];
    [0:v]trim=0:${FADE},setpts=PTS-STARTPTS[start_part];
    [1:v]trim=${FADE}:${TRIM_END},setpts=PTS-STARTPTS[middle];
    [end_part][start_part]xfade=transition=fade:duration=${FADE}:offset=0[xfaded];
    [xfaded][middle]concat=n=2:v=1:a=0[out]
  " -map "[out]" -c:v libx264 -crf 0 -preset ultrafast -an "$LOOP_TMP"
  LOOP_SOURCE="$LOOP_TMP"
fi

# --- Encode MP4 -------------------------------------------------------------

ffmpeg -y -loglevel warning -i "$LOOP_SOURCE" \
  -c:v libx264 -crf "$H264_CRF" -preset slow \
  -an -movflags +faststart \
  "$MP4"

# --- Encode WebM ------------------------------------------------------------

ffmpeg -y -loglevel warning -i "$LOOP_SOURCE" \
  -c:v libvpx-vp9 -crf "$VP9_CRF" -b:v 0 \
  -an \
  "$WEBM"

# --- Poster (optional) ------------------------------------------------------

if [[ $POSTER -eq 1 ]]; then
  ffmpeg -y -loglevel warning -ss 0 -i "$MP4" -frames:v 1 -q:v 3 -update 1 "$POSTER_JPG"
fi

# --- Summary ----------------------------------------------------------------

MP4_BYTES=$(stat -f%z "$MP4" 2>/dev/null || stat -c%s "$MP4")
WEBM_BYTES=$(stat -f%z "$WEBM" 2>/dev/null || stat -c%s "$WEBM")

echo "RESULT: input_bytes=$INPUT_BYTES"
echo "RESULT: duration_seconds=$DURATION"
echo "RESULT: fade_seconds=$FADE"
echo "RESULT: no_fade=$NO_FADE"
echo "RESULT: mp4_path=$MP4"
echo "RESULT: mp4_bytes=$MP4_BYTES"
echo "RESULT: webm_path=$WEBM"
echo "RESULT: webm_bytes=$WEBM_BYTES"
if [[ $POSTER -eq 1 ]]; then
  POSTER_BYTES=$(stat -f%z "$POSTER_JPG" 2>/dev/null || stat -c%s "$POSTER_JPG")
  echo "RESULT: poster_path=$POSTER_JPG"
  echo "RESULT: poster_bytes=$POSTER_BYTES"
fi
