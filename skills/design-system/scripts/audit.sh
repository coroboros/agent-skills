#!/usr/bin/env bash
# audit.sh — wrap `npx @google/design.md lint` for the /design-system audit subcommand.
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

if ! command -v npx >/dev/null 2>&1; then
  echo "RESULT: status=npx-missing"
  exit 1
fi

json_tmp="$(mktemp -t design-audit-XXXXXX).json"
stderr_tmp="$(mktemp -t design-audit-stderr-XXXXXX).log"

# `lint` exits 1 when errors are found but still writes valid JSON to stdout.
# Treat both exit 0 and exit 1 as "CLI ran successfully"; higher exits are real failures.
set +e
npx -y @google/design.md@latest lint "$path" >"$json_tmp" 2>"$stderr_tmp"
rc=$?
set -e

if [[ $rc -gt 1 ]]; then
  echo "RESULT: status=cli-failed"
  echo "RESULT: exit-code=$rc"
  echo "RESULT: stderr=$stderr_tmp"
  exit 1
fi

# CLI succeeded. The JSON contains .summary.errors, .summary.warnings, .summary.infos, .findings[]
echo "RESULT: status=ok"
echo "RESULT: path=$path"
echo "RESULT: exit-code=$rc"
echo "RESULT: json=$json_tmp"
