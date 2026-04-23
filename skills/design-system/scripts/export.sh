#!/usr/bin/env bash
# export.sh — wrap `npx @google/design.md export` for the /design-system export subcommand.
# Emits `RESULT: key=value` lines. If no output path is given, writes to a temp file
# and reports its location (the skill decides where to move it).

set -euo pipefail

usage() {
  echo "usage: export.sh <tailwind|dtcg> <path-to-design-md> [output-file]" >&2
  exit 2
}

[[ $# -ge 2 && $# -le 3 ]] || usage
format="$1"
path="$2"
out="${3:-}"

if [[ "$format" != "tailwind" && "$format" != "dtcg" ]]; then
  echo "RESULT: status=invalid-format"
  echo "RESULT: format=$format"
  exit 2
fi

if [[ ! -f "$path" ]]; then
  echo "RESULT: status=file-not-found"
  echo "RESULT: path=$path"
  exit 1
fi

if ! command -v npx >/dev/null 2>&1; then
  echo "RESULT: status=npx-missing"
  exit 1
fi

if [[ -z "$out" ]]; then
  out="$(mktemp -t design-export-XXXXXX).${format}"
fi

stderr_tmp="$(mktemp -t design-export-stderr-XXXXXX).log"

if ! npx -y @google/design.md@latest export --format "$format" "$path" >"$out" 2>"$stderr_tmp"; then
  echo "RESULT: status=cli-failed"
  echo "RESULT: stderr=$stderr_tmp"
  exit 1
fi

bytes="$(wc -c <"$out" | tr -d ' ')"

echo "RESULT: status=ok"
echo "RESULT: format=$format"
echo "RESULT: source=$path"
echo "RESULT: output=$out"
echo "RESULT: bytes=$bytes"
