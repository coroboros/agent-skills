#!/usr/bin/env bash
# audit.sh — wrap `designmd lint` for the /design-system audit subcommand.
# Emits `RESULT: key=value` lines on stdout and writes the raw CLI JSON to a temp file.
# The skill parses the RESULT lines, reads the JSON file, and composes the human-readable report.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source-path=SCRIPTDIR
# shellcheck source=designmd-runtime.sh
source "$SCRIPT_DIR/designmd-runtime.sh"
ORIGINAL_ARGS=("$@")

usage() {
  echo "usage: audit.sh <path-to-design-md>" >&2
  exit 2
}

[[ $# -eq 1 ]] || usage
path="$1"
printf -v RERUN '%q ' bash "$SCRIPT_DIR/audit.sh" "${ORIGINAL_ARGS[@]}"
RERUN="${RERUN% }"

if [[ ! -f "$path" ]]; then
  echo "RESULT: status=file-not-found"
  echo "RESULT: path=$path"
  exit 1
fi
path_for_cli="$(cd "$(dirname "$path")" && pwd -P)/$(basename "$path")"
require_designmd "$RERUN" || exit 1

json_tmp="$(mktemp "${TMPDIR:-/tmp}/design-audit-json.XXXXXX")"
stderr_tmp="$(mktemp "${TMPDIR:-/tmp}/design-audit-stderr.XXXXXX")"

# `lint` exits 1 on findings but still writes valid JSON; only exits >1 are real
# failures.
set +e
"$designmd" lint --format json "$path_for_cli" >"$json_tmp" 2>"$stderr_tmp"
rc=$?
set -e

if [[ $rc -gt 1 ]]; then
  rm -f "$json_tmp"
  echo "RESULT: status=cli-failed"
  echo "RESULT: exit-code=$rc"
  echo "RESULT: stderr=$stderr_tmp"
  echo "RESULT: rerun=$RERUN"
  echo "RESULT: remediation=Repair or upgrade designmd, verify designmd --version, then rerun"
  exit 1
fi

if ! python3 "$SCRIPT_DIR/validate-output.py" lint "$json_tmp" --exit-code "$rc"; then
  echo "RESULT: status=cli-invalid-output"
  echo "RESULT: exit-code=$rc"
  echo "RESULT: json=$json_tmp"
  echo "RESULT: stderr=$stderr_tmp"
  echo "RESULT: rerun=$RERUN"
  echo "RESULT: remediation=Repair or upgrade designmd, verify designmd --version, then rerun"
  exit 1
fi

# Propagate rc so the script is CI-gate friendly: exit 0 if no errors, 1 if errors found.
echo "RESULT: status=ok"
echo "RESULT: path=$path"
echo "RESULT: exit-code=$rc"
echo "RESULT: json=$json_tmp"
echo "RESULT: runtime=path"
echo "RESULT: binary=$designmd"
rm -f "$stderr_tmp"
exit "$rc"
