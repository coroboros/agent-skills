#!/usr/bin/env bash
# spec.sh — resolve Design.md, translate the skill flags, and emit atomically.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=resolve-designmd.sh
source "$SCRIPT_DIR/resolve-designmd.sh"
ORIGINAL_ARGS=("$@")
RERUN="$(designmd_format_command bash "$SCRIPT_DIR/spec.sh" ${ORIGINAL_ARGS[@]+"${ORIGINAL_ARGS[@]}"})"

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

if resolve_designmd .; then
  :
else
  resolution_rc=$?
  emit_designmd_resolution_error . "$resolution_rc" "$RERUN"
  exit 1
fi

if [[ -n "$out" ]]; then
  out_dir="$(dirname "$out")"
  [[ -d "$out_dir" ]] || {
    echo "RESULT: status=output-directory-not-found"
    echo "RESULT: path=$out_dir"
    exit 1
  }
  work_out="$(mktemp "$out_dir/.design-spec-XXXXXX")"
else
  work_out="$(mktemp -t "design-spec-${format}-XXXXXX")"
fi
stderr_tmp="$(mktemp -t design-spec-stderr-XXXXXX)"

spec_source="designmd-cli"
if run_designmd spec ${args[@]+"${args[@]}"} --format "$format" >"$work_out" 2>"$stderr_tmp"; then
  cli_rc=0
else
  cli_rc=$?
fi
if [[ "$cli_rc" -ne 0 ]]; then
  bundled_spec="$(mktemp -t design-bundled-spec-XXXXXX)"
  if [[ "$rules_only" -eq 0 ]] \
    && grep -Fq 'Failed to load spec.md.' "$stderr_tmp" \
    && designmd_bundled_spec "$bundled_spec" \
    && [[ -s "$bundled_spec" ]]; then
    rules_tmp="$(mktemp -t "design-spec-rules-${format}-XXXXXX")"
    if [[ "$include_rules" -eq 1 ]] \
      && ! run_designmd spec --rules-only --format "$format" >"$rules_tmp" 2>>"$stderr_tmp"; then
      rm -f "$rules_tmp" "$work_out" "$bundled_spec"
      echo "RESULT: status=cli-failed" >&2
      echo "RESULT: stderr=$stderr_tmp" >&2
      emit_designmd_runtime_repair . "$RERUN"
      exit 1
    fi
    if ! python3 - "$bundled_spec" "$rules_tmp" "$format" "$include_rules" >"$work_out" <<'PY'
import json
from pathlib import Path
import sys

spec = Path(sys.argv[1]).read_text(encoding="utf-8")
rules_path = Path(sys.argv[2])
output_format = sys.argv[3]
include_rules = sys.argv[4] == "1"

if output_format == "json":
    payload = {"spec": spec}
    if include_rules:
        rules = json.loads(rules_path.read_text(encoding="utf-8"))
        payload["rules"] = rules["rules"]
    print(json.dumps(payload, indent=2, ensure_ascii=False))
else:
    output = spec
    if include_rules:
        output += "\n\n## Active Linting Rules\n\n" + rules_path.read_text(encoding="utf-8").rstrip("\n")
    print(output)
PY
    then
      rm -f "$rules_tmp" "$work_out" "$bundled_spec"
      echo "RESULT: status=cli-invalid-output" >&2
      echo "RESULT: stderr=$stderr_tmp" >&2
      emit_designmd_runtime_repair . "$RERUN"
      exit 1
    fi
    rm -f "$rules_tmp" "$bundled_spec"
    spec_source="packaged-official-artifact"
  else
    rm -f "$work_out" "$bundled_spec"
    echo "RESULT: status=cli-failed" >&2
    echo "RESULT: stderr=$stderr_tmp" >&2
    emit_designmd_runtime_repair . "$RERUN"
    exit 1
  fi
fi
if [[ ! -s "$work_out" ]]; then
  rm -f "$work_out"
  echo "RESULT: status=cli-invalid-output" >&2
  echo "RESULT: stderr=$stderr_tmp" >&2
  emit_designmd_runtime_repair . "$RERUN"
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
  emit_designmd_runtime_repair . "$RERUN"
  exit 1
fi

if [[ -n "$out" ]]; then
  mv "$work_out" "$out"
  bytes="$(wc -c <"$out" | tr -d ' ')"
  echo "RESULT: status=ok"
  echo "RESULT: output=$out"
  echo "RESULT: bytes=$bytes"
  echo "RESULT: spec-source=$spec_source"
  emit_designmd_metadata
else
  cat "$work_out"
  rm -f "$work_out"
fi
rm -f "$stderr_tmp"
