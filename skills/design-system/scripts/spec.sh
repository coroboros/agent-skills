#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=designmd-runtime.sh
source "$SCRIPT_DIR/designmd-runtime.sh"
ORIGINAL_ARGS=("$@")
printf -v RERUN '%q ' bash "$SCRIPT_DIR/spec.sh" "${ORIGINAL_ARGS[@]}"
RERUN="${RERUN% }"

usage() {
  echo "usage: spec.sh [--rules] [--rules-only] [--json] [-o output]" >&2
  exit 2
}

format="markdown"
out=""
args=()
include_rules=0
rules_only=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --rules) args+=("--rules"); include_rules=1; shift ;;
    --rules-only) args+=("--rules-only"); rules_only=1; shift ;;
    --json) format="json"; shift ;;
    --format)
      [[ ${2:-} == "json" || ${2:-} == "markdown" ]] || usage
      format="$2"; shift 2 ;;
    -o|--output)
      [[ -n ${2:-} ]] || usage
      out="$2"; shift 2 ;;
    -h|--help) usage ;;
    *) usage ;;
  esac
done

require_designmd "$RERUN" || exit 1

if [[ -n "$out" ]]; then
  out_dir="$(dirname "$out")"
  [[ -d "$out_dir" ]] || {
    echo "RESULT: status=output-directory-not-found"
    echo "RESULT: path=$out_dir"
    exit 1
  }
  work_out="$(mktemp "$out_dir/.design-spec.XXXXXX")"
else
  work_out="$(mktemp "${TMPDIR:-/tmp}/design-spec-${format}.XXXXXX")"
fi
stderr_tmp="$(mktemp "${TMPDIR:-/tmp}/design-spec-stderr.XXXXXX")"

if ! "$designmd" spec ${args[@]+"${args[@]}"} --format "$format" >"$work_out" 2>"$stderr_tmp"; then
  rm -f "$work_out"
  echo "RESULT: status=cli-failed" >&2
  echo "RESULT: stderr=$stderr_tmp" >&2
  echo "RESULT: rerun=$RERUN" >&2
  echo "RESULT: remediation=Repair or upgrade designmd, verify designmd --version, then rerun" >&2
  exit 1
fi

validation_mode="spec-${format}"
if [[ "$rules_only" -eq 1 ]]; then
  validation_mode="spec-rules-${format}"
elif [[ "$include_rules" -eq 1 ]]; then
  validation_mode="spec-with-rules-${format}"
fi
if ! python3 "$SCRIPT_DIR/validate-output.py" "$validation_mode" "$work_out"; then
  rm -f "$work_out"
  echo "RESULT: status=cli-invalid-output" >&2
  echo "RESULT: stderr=$stderr_tmp" >&2
  echo "RESULT: rerun=$RERUN" >&2
  echo "RESULT: remediation=Repair or upgrade designmd, verify designmd --version, then rerun" >&2
  exit 1
fi

if [[ -n "$out" ]]; then
  mv "$work_out" "$out"
  echo "RESULT: status=ok"
  echo "RESULT: output=$out"
  echo "RESULT: bytes=$(wc -c <"$out" | tr -d ' ')"
  echo "RESULT: runtime=path"
  echo "RESULT: binary=$designmd"
else
  cat "$work_out"
  rm -f "$work_out"
fi
rm -f "$stderr_tmp"
