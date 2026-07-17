#!/usr/bin/env bash
# audit.sh — wrap `designmd lint` for the /design-system audit subcommand.
# Emits `RESULT: key=value` lines on stdout and writes the raw CLI JSON to a temp file.
# The skill parses the RESULT lines, reads the JSON file, and composes the human-readable report.

set -euo pipefail

usage() {
  echo "usage: audit.sh <path-to-design-md>" >&2
  exit 2
}

[[ $# -eq 1 ]] || usage
path="$1"

if [[ ! -f "$path" ]]; then
  echo "RESULT: status=file-not-found"
  echo "RESULT: path=$path"
  exit 1
fi

if ! command -v designmd >/dev/null 2>&1; then
  echo "RESULT: status=designmd-missing"
  exit 1
fi

json_tmp="$(mktemp -t design-audit-XXXXXX).json"
stderr_tmp="$(mktemp -t design-audit-stderr-XXXXXX).log"

# `lint` exits 1 on findings but still writes valid JSON; only exits >1 are real
# failures.
set +e
designmd lint "$path" >"$json_tmp" 2>"$stderr_tmp"
rc=$?
set -e

if [[ $rc -gt 1 ]]; then
  echo "RESULT: status=cli-failed"
  echo "RESULT: exit-code=$rc"
  echo "RESULT: stderr=$stderr_tmp"
  exit 1
fi

# Propagate rc so the script is CI-gate friendly: exit 0 if no errors, 1 if errors found.
echo "RESULT: status=ok"
echo "RESULT: path=$path"
echo "RESULT: exit-code=$rc"
echo "RESULT: json=$json_tmp"
exit "$rc"
