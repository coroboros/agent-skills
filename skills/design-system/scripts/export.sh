#!/usr/bin/env bash
# export.sh — wrap `designmd export` for the /design-system export subcommand.
# Emits `RESULT: key=value` lines. If no output path is given, writes to a temp file
# and reports its location (the skill decides where to move it).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=designmd-runtime.sh
source "$SCRIPT_DIR/designmd-runtime.sh"
ORIGINAL_ARGS=("$@")

usage() {
  echo "usage: export.sh <tailwind|dtcg> <path-to-design-md> [output-file]" >&2
  exit 2
}

[[ $# -ge 2 && $# -le 3 ]] || usage
format="$1"
path="$2"
out="${3:-}"
printf -v RERUN '%q ' bash "$SCRIPT_DIR/export.sh" "${ORIGINAL_ARGS[@]}"
RERUN="${RERUN% }"

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
path_for_cli="$(cd "$(dirname "$path")" && pwd -P)/$(basename "$path")"
require_designmd "$RERUN" || exit 1

explicit_out="$out"
if [[ -z "$explicit_out" ]]; then
  work_out="$(mktemp "${TMPDIR:-/tmp}/design-export-${format}.XXXXXX")"
  out="$work_out"
else
  out_dir="$(dirname "$explicit_out")"
  if [[ ! -d "$out_dir" ]]; then
    echo "RESULT: status=output-directory-not-found"
    echo "RESULT: path=$out_dir"
    exit 1
  fi
  work_out="$(mktemp "$out_dir/.design-export-XXXXXX")"
fi
stderr_tmp="$(mktemp "${TMPDIR:-/tmp}/design-export-stderr.XXXXXX")"

if ! "$designmd" export --format "$format" "$path_for_cli" >"$work_out" 2>"$stderr_tmp"; then
  rm -f "$work_out"
  echo "RESULT: status=cli-failed"
  echo "RESULT: stderr=$stderr_tmp"
  echo "RESULT: rerun=$RERUN"
  echo "RESULT: remediation=Repair or upgrade designmd, verify designmd --version, then rerun"
  exit 1
fi

if ! python3 "$SCRIPT_DIR/validate-output.py" "export-$format" "$work_out"; then
  rm -f "$work_out"
  echo "RESULT: status=cli-invalid-output"
  echo "RESULT: stderr=$stderr_tmp"
  echo "RESULT: rerun=$RERUN"
  echo "RESULT: remediation=Repair or upgrade designmd, verify designmd --version, then rerun"
  exit 1
fi

if [[ -n "$explicit_out" ]]; then
  mv "$work_out" "$explicit_out"
  out="$explicit_out"
fi

bytes="$(wc -c <"$out" | tr -d ' ')"

echo "RESULT: status=ok"
echo "RESULT: format=$format"
echo "RESULT: source=$path"
echo "RESULT: output=$out"
echo "RESULT: bytes=$bytes"
echo "RESULT: runtime=path"
echo "RESULT: binary=$designmd"
rm -f "$stderr_tmp"
