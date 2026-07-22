#!/usr/bin/env bash
# audit.sh — wrap `designmd lint` for the /design-system audit subcommand.
# Emits `RESULT: key=value` lines on stdout and writes the raw CLI JSON to a temp file.
# The skill parses the RESULT lines, reads the JSON file, and composes the human-readable report.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=resolve-designmd.sh
source "$SCRIPT_DIR/resolve-designmd.sh"
ORIGINAL_ARGS=("$@")

usage() {
  echo "usage: audit.sh <path-to-design-md>" >&2
  exit 2
}

[[ $# -eq 1 ]] || usage
path="$1"
RERUN="$(designmd_format_command bash "$SCRIPT_DIR/audit.sh" "${ORIGINAL_ARGS[@]}")"

if [[ ! -f "$path" ]]; then
  echo "RESULT: status=file-not-found"
  echo "RESULT: path=$path"
  exit 1
fi
path_for_cli="$(designmd_absolute_file "$path")"

if resolve_designmd "$path_for_cli"; then
  :
else
  resolution_rc=$?
  emit_designmd_resolution_error "$path_for_cli" "$resolution_rc" "$RERUN"
  exit 1
fi

json_tmp="$(mktemp -t design-audit-json-XXXXXX)"
stderr_tmp="$(mktemp -t design-audit-stderr-XXXXXX)"

# `lint` exits 1 on findings but still writes valid JSON; only exits >1 are real
# failures.
set +e
run_designmd lint --format json "$path_for_cli" >"$json_tmp" 2>"$stderr_tmp"
rc=$?
set -e

if [[ $rc -gt 1 ]]; then
  rm -f "$json_tmp"
  echo "RESULT: status=cli-failed"
  echo "RESULT: exit-code=$rc"
  echo "RESULT: stderr=$stderr_tmp"
  emit_designmd_runtime_repair "$path_for_cli" "$RERUN"
  exit 1
fi

if ! python3 "$SCRIPT_DIR/validate-output.py" lint "$json_tmp" --exit-code "$rc"; then
  echo "RESULT: status=cli-invalid-output"
  echo "RESULT: exit-code=$rc"
  echo "RESULT: json=$json_tmp"
  echo "RESULT: stderr=$stderr_tmp"
  emit_designmd_runtime_repair "$path_for_cli" "$RERUN"
  exit 1
fi

# Propagate rc so the script is CI-gate friendly: exit 0 if no errors, 1 if errors found.
echo "RESULT: status=ok"
echo "RESULT: path=$path"
echo "RESULT: exit-code=$rc"
echo "RESULT: json=$json_tmp"
emit_designmd_metadata
rm -f "$stderr_tmp"
exit "$rc"
