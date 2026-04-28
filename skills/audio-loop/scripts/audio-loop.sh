#!/usr/bin/env bash
#
# audio-loop.sh — produce a web-ready seamless audio loop (FLAC)
#
# Usage:
#   audio-loop.sh <input> [-t <lufs>] [-o <out_dir>] [-B]
#
# Options:
#   -t <lufs>       Integrated loudness target (default: -28)
#   -o <out_dir>    Output directory (default: same as input)
#   -B              Disable stereo balance auto-correction
#
# Pipeline:
#   probe → (optional pan correction) → loudnorm → aresample → FLAC
#
# The loudnorm filter silently upsamples to 192 kHz for its internal measurement
# pass; the trailing `aresample=<source_rate>` puts the stream back on the
# original rate so the FLAC doesn't balloon to 4× the expected size.
#
# Stereo sources are probed per-channel. If the RMS delta between L and R
# exceeds 1 dB, a pan filter attenuates the louder side to centre the image.
# The -B flag disables the correction entirely.
#
# Emits a machine-readable summary on stdout prefixed with "RESULT:", one
# key=value per line. Consumers parse these to compose the user-facing report.
#
# Exit codes:
#   0   success — output within post-condition tolerance
#   1   input / tool validation error, or self-overwrite guard hit
#   3   encoded successfully but post-condition check failed (output LUFS
#       more than ±1 from target — indicates a loudnorm regression)

set -euo pipefail

LUFS_TARGET=-28
OUT_DIR=""
NO_BALANCE=0

usage() {
  sed -n '2,27p' "$0" | sed 's/^# \{0,1\}//'
  exit 2
}

[[ $# -lt 1 ]] && usage
case "$1" in -h|--help) usage ;; esac

INPUT=$1
shift

while getopts ":t:o:B" opt; do
  case $opt in
    t) LUFS_TARGET=$OPTARG ;;
    o) OUT_DIR=$OPTARG ;;
    B) NO_BALANCE=1 ;;
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

OUTPUT="$OUT_DIR/${STEM}.flac"

# Self-overwrite guard — only hits when reprocessing a FLAC in its own directory.
# The FLAC encode would clobber the source; catch it upfront with a clear message.
if [[ "$INPUT_ABS" == "$OUTPUT" ]]; then
  echo "error: output would overwrite input ($OUTPUT). Pass -o <dir> to write elsewhere." >&2
  exit 1
fi

# --- Probe ------------------------------------------------------------------

DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$INPUT_ABS")
CHANNELS=$(ffprobe -v error -select_streams a:0 -show_entries stream=channels -of csv=p=0 "$INPUT_ABS")
SAMPLE_RATE=$(ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate -of csv=p=0 "$INPUT_ABS")
# stat flags differ between macOS (-f%z) and GNU/Linux (-c%s); try both.
INPUT_BYTES=$(stat -f%z "$INPUT_ABS" 2>/dev/null || stat -c%s "$INPUT_ABS")

# --- Stereo balance (stereo sources only) ----------------------------------

PAN_FILTER=""
L_RMS=""
R_RMS=""
DELTA_DB=0
BALANCE_CORRECTED=0

if [[ "$CHANNELS" -eq 2 ]]; then
  # astats emits one "RMS level dB" line per channel, followed by a summary
  # line. Take the first two — that's L and R.
  STATS=$(ffmpeg -hide_banner -nostats -i "$INPUT_ABS" \
          -af astats=metadata=1:reset=0:measure_perchannel=RMS_level \
          -f null - 2>&1 | grep "RMS level dB" | head -2)
  L_RMS=$(echo "$STATS" | sed -n '1p' | awk '{print $NF}')
  R_RMS=$(echo "$STATS" | sed -n '2p' | awk '{print $NF}')

  DELTA_DB=$(awk -v l="$L_RMS" -v r="$R_RMS" 'BEGIN { printf "%.3f", r - l }')
  ABS_DELTA=$(awk -v d="$DELTA_DB" 'BEGIN { printf "%.3f", (d < 0) ? -d : d }')

  # Threshold: correct above 1 dB. Below that, JND research on sustained
  # ambient content shows the imbalance isn't reliably perceptible.
  if [[ $NO_BALANCE -eq 0 ]] && awk -v a="$ABS_DELTA" 'BEGIN { exit !(a > 1.0) }'; then
    if awk -v d="$DELTA_DB" 'BEGIN { exit !(d > 0) }'; then
      # R is louder — attenuate R.
      GAIN=$(awk -v d="$DELTA_DB" 'BEGIN { printf "%.6f", 10 ^ (-d / 20) }')
      PAN_FILTER="pan=stereo|c0=FL|c1=${GAIN}*FR,"
    else
      # L is louder — attenuate L.
      GAIN=$(awk -v d="$DELTA_DB" 'BEGIN { printf "%.6f", 10 ^ (d / 20) }')
      PAN_FILTER="pan=stereo|c0=${GAIN}*FL|c1=FR,"
    fi
    BALANCE_CORRECTED=1
  fi
fi

# --- Encode FLAC ------------------------------------------------------------

ffmpeg -y -hide_banner -loglevel warning -i "$INPUT_ABS" \
  -af "${PAN_FILTER}loudnorm=I=${LUFS_TARGET}:TP=-2:LRA=7,aresample=${SAMPLE_RATE}" \
  -c:a flac -compression_level 8 \
  "$OUTPUT"

# --- Verify output ----------------------------------------------------------

# Integrated loudness + true peak from ebur128 summary.
EBUR_OUT=$(ffmpeg -hide_banner -nostats -i "$OUTPUT" \
           -filter:a ebur128=peak=true -f null - 2>&1)
OUT_LUFS=$(echo "$EBUR_OUT" | awk '/^ *I: / && /LUFS/ { val=$2 } END { print val }')
OUT_PEAK=$(echo "$EBUR_OUT" | awk '/True peak:/,/^$/' | awk '/Peak:/ { val=$2 } END { print val }')

# Per-channel RMS of the output (confirms the correction landed).
if [[ "$CHANNELS" -eq 2 ]]; then
  OUT_STATS=$(ffmpeg -hide_banner -nostats -i "$OUTPUT" \
              -af astats=metadata=1:reset=0:measure_perchannel=RMS_level \
              -f null - 2>&1 | grep "RMS level dB" | head -2)
  OUT_L=$(echo "$OUT_STATS" | sed -n '1p' | awk '{print $NF}')
  OUT_R=$(echo "$OUT_STATS" | sed -n '2p' | awk '{print $NF}')
fi

OUTPUT_BYTES=$(stat -f%z "$OUTPUT" 2>/dev/null || stat -c%s "$OUTPUT")

# --- Post-condition checks --------------------------------------------------

# Integrated loudness within ±1 LUFS of the target. Outside this window
# suggests loudnorm failed to converge — surface loud and fail the call so
# the caller doesn't ship a mis-leveled loop.
LUFS_OK=1
LUFS_DELTA=""
if [[ -n "${OUT_LUFS:-}" ]]; then
  LUFS_DELTA=$(awk -v o="$OUT_LUFS" -v t="$LUFS_TARGET" 'BEGIN { d = o - t; printf "%.3f", (d < 0 ? -d : d) }')
  if awk -v d="$LUFS_DELTA" 'BEGIN { exit !(d > 1.0) }'; then
    LUFS_OK=0
  fi
fi

# --- Summary ----------------------------------------------------------------

echo "RESULT: input_path=$INPUT_ABS"
echo "RESULT: input_bytes=$INPUT_BYTES"
echo "RESULT: duration_seconds=$DURATION"
echo "RESULT: sample_rate=$SAMPLE_RATE"
echo "RESULT: channels=$CHANNELS"
if [[ "$CHANNELS" -eq 2 ]]; then
  echo "RESULT: input_rms_left=$L_RMS"
  echo "RESULT: input_rms_right=$R_RMS"
  echo "RESULT: input_rms_delta=$DELTA_DB"
  echo "RESULT: balance_corrected=$BALANCE_CORRECTED"
  echo "RESULT: output_rms_left=${OUT_L:-}"
  echo "RESULT: output_rms_right=${OUT_R:-}"
fi
echo "RESULT: lufs_target=$LUFS_TARGET"
echo "RESULT: lufs_out=${OUT_LUFS:-}"
echo "RESULT: lufs_delta=${LUFS_DELTA:-}"
echo "RESULT: peak_out=${OUT_PEAK:-}"
echo "RESULT: output_path=$OUTPUT"
echo "RESULT: output_bytes=$OUTPUT_BYTES"

if [[ "$LUFS_OK" -eq 0 ]]; then
  echo "RESULT: error=lufs-out-of-range actual=$OUT_LUFS target=$LUFS_TARGET delta=$LUFS_DELTA"
  echo "RESULT: ok=false"
  exit 3
fi

echo "RESULT: ok=true"
