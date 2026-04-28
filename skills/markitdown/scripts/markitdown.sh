#!/usr/bin/env bash
# markitdown.sh — wrap microsoft/markitdown for the agent-skills repo.
#
# Usage: markitdown.sh [-s|-S] [-d] [-p] [-k] [-l] <file-or-url>
#
#   -s   save to .claude/output/markitdown/<slug>/<stem>.md
#   -S   force no-save (default)
#   -d   use Azure Document Intelligence (needs MARKITDOWN_DOCINTEL_ENDPOINT)
#   -p   enable third-party markitdown plugins
#   -k   keep data URIs (base64 images) in the output
#   -l   list installed plugins and exit
#
# Emits `RESULT: key=value` lines for the skill to parse, then markdown
# either to a file (when -s) or to stdout after a `---` separator.

set -euo pipefail

SAVE=0
USE_DOCINTEL=0
USE_PLUGINS=0
KEEP_DATA=0
LIST_PLUGINS=0

while getopts "sSdpkl" opt; do
  case "$opt" in
    s) SAVE=1 ;;
    S) SAVE=0 ;;
    d) USE_DOCINTEL=1 ;;
    p) USE_PLUGINS=1 ;;
    k) KEEP_DATA=1 ;;
    l) LIST_PLUGINS=1 ;;
    *) echo "ERR: unknown flag -$opt" >&2; exit 2 ;;
  esac
done
shift $((OPTIND - 1))

if ! command -v markitdown >/dev/null 2>&1; then
  echo "ERR: markitdown not installed — run: pip install 'markitdown[all]'" >&2
  exit 127
fi

if [[ $LIST_PLUGINS -eq 1 ]]; then
  exec markitdown --list-plugins
fi

INPUT="${1:-}"
if [[ -z "$INPUT" ]]; then
  echo "ERR: input required (file path or URL)" >&2
  exit 2
fi

IS_URL=0
case "$INPUT" in
  http://*|https://*) IS_URL=1 ;;
esac

if [[ $IS_URL -eq 0 && ! -f "$INPUT" ]]; then
  echo "ERR: file not found: $INPUT" >&2
  exit 2
fi

ARGS=()
if [[ $USE_DOCINTEL -eq 1 ]]; then
  if [[ -z "${MARKITDOWN_DOCINTEL_ENDPOINT:-}" ]]; then
    echo "ERR: -d requires MARKITDOWN_DOCINTEL_ENDPOINT env var" >&2
    exit 2
  fi
  ARGS+=(-d -e "$MARKITDOWN_DOCINTEL_ENDPOINT")
fi
[[ $USE_PLUGINS -eq 1 ]] && ARGS+=(-p)
[[ $KEEP_DATA -eq 1 ]] && ARGS+=(--keep-data-uris)

BASE=$(basename "$INPUT")
STEM="${BASE%.*}"
[[ -z "$STEM" ]] && STEM="$BASE"
SLUG=$(printf '%s' "$STEM" \
  | tr '[:upper:]' '[:lower:]' \
  | tr -cs 'a-z0-9' '-' \
  | sed -E 's/^-+|-+$//g' \
  | cut -d'-' -f1-5)
[[ -z "$SLUG" ]] && SLUG="output"

if [[ $SAVE -eq 1 ]]; then
  OUT_DIR=".claude/output/markitdown/$SLUG"
  mkdir -p "$OUT_DIR"
  OUT_FILE="$OUT_DIR/${STEM}.md"
  markitdown ${ARGS[@]+"${ARGS[@]}"} "$INPUT" -o "$OUT_FILE"
  BYTES=$(wc -c < "$OUT_FILE" | tr -d ' ')
  echo "RESULT: path=$OUT_FILE"
  echo "RESULT: bytes=$BYTES"
  echo "RESULT: slug=$SLUG"
  echo "RESULT: saved=true"
else
  TMP=$(mktemp -t markitdown.XXXXXX)
  trap 'rm -f "$TMP"' EXIT
  markitdown ${ARGS[@]+"${ARGS[@]}"} "$INPUT" -o "$TMP"
  BYTES=$(wc -c < "$TMP" | tr -d ' ')
  echo "RESULT: bytes=$BYTES"
  echo "RESULT: slug=$SLUG"
  echo "RESULT: saved=false"
  echo "---"
  cat "$TMP"
fi
