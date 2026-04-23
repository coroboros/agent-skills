#!/usr/bin/env bash
# diff.sh — wrap `npx @google/design.md diff` for the /design-system diff subcommand.
# Emits `RESULT: key=value` lines and writes the raw CLI JSON to a temp file.

set -euo pipefail

usage() {
  echo "usage: diff.sh <before> <after>" >&2
  exit 2
}

[[ $# -eq 2 ]] || usage
before="$1"
after="$2"

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

if ! command -v npx >/dev/null 2>&1; then
  echo "RESULT: status=npx-missing"
  exit 1
fi

json_tmp="$(mktemp -t design-diff-XXXXXX).json"
stderr_tmp="$(mktemp -t design-diff-stderr-XXXXXX).log"

# `diff` exits 1 on regression, 0 on no regression. Both are successful CLI runs.
set +e
npx -y @google/design.md@latest diff "$before" "$after" >"$json_tmp" 2>"$stderr_tmp"
rc=$?
set -e

if [[ $rc -gt 1 ]]; then
  echo "RESULT: status=cli-failed"
  echo "RESULT: exit-code=$rc"
  echo "RESULT: stderr=$stderr_tmp"
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
