#!/usr/bin/env bash
# diff.sh — wrap `designmd diff` for the /design-system diff subcommand.
# Emits `RESULT: key=value` lines and writes the raw CLI JSON to a temp file.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=designmd-runtime.sh
source "$SCRIPT_DIR/designmd-runtime.sh"
ORIGINAL_ARGS=("$@")

usage() {
  echo "usage: diff.sh <before> <after>" >&2
  exit 2
}

[[ $# -eq 2 ]] || usage
before="$1"
after="$2"
printf -v RERUN '%q ' bash "$SCRIPT_DIR/diff.sh" "${ORIGINAL_ARGS[@]}"
RERUN="${RERUN% }"

if [[ ! -f "$before" ]]; then
  echo "RESULT: status=before-not-found"
  echo "RESULT: path=$before"
  exit 1
fi
if [[ ! -f "$after" ]]; then
  echo "RESULT: status=after-not-found"
  echo "RESULT: path=$after"
  exit 1
fi
before_for_cli="$(cd "$(dirname "$before")" && pwd -P)/$(basename "$before")"
after_for_cli="$(cd "$(dirname "$after")" && pwd -P)/$(basename "$after")"
require_designmd "$RERUN" || exit 1

json_tmp="$(mktemp "${TMPDIR:-/tmp}/design-diff-json.XXXXXX")"
stderr_tmp="$(mktemp "${TMPDIR:-/tmp}/design-diff-stderr.XXXXXX")"

# `diff` exits 1 on regression, 0 on no regression. Both are successful CLI runs.
set +e
"$designmd" diff --format json "$before_for_cli" "$after_for_cli" >"$json_tmp" 2>"$stderr_tmp"
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

if ! python3 "$SCRIPT_DIR/validate-output.py" diff "$json_tmp" --exit-code "$rc"; then
  echo "RESULT: status=cli-invalid-output"
  echo "RESULT: exit-code=$rc"
  echo "RESULT: json=$json_tmp"
  echo "RESULT: stderr=$stderr_tmp"
  echo "RESULT: rerun=$RERUN"
  echo "RESULT: remediation=Repair or upgrade designmd, verify designmd --version, then rerun"
  exit 1
fi

if [[ $rc -eq 1 ]]; then
  regression="true"
else
  regression="false"
fi

echo "RESULT: status=ok"
echo "RESULT: before=$before"
echo "RESULT: after=$after"
echo "RESULT: regression=$regression"
echo "RESULT: exit-code=$rc"
echo "RESULT: json=$json_tmp"
echo "RESULT: runtime=path"
echo "RESULT: binary=$designmd"
rm -f "$stderr_tmp"
# Propagate rc so the script is CI-gate friendly: exit 0 no regression, 1 on regression.
exit "$rc"
