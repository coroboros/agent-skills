#!/usr/bin/env bash
# audit-extensions.sh — bidirectional drift check between DESIGN.md extension YAML,
# prose references, and the globals.css @theme block.
#
# Wraps audit_extensions.py — emits RESULT: lines on stdout. The skill parses the
# RESULT lines and FINDING: lines, then composes the human-readable report.

set -euo pipefail

usage() {
  echo "usage: audit-extensions.sh <path-to-design-md> [--css <path>] [--strict] [--json]" >&2
  exit 2
}

[[ $# -ge 1 ]] || usage

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
py_script="$script_dir/audit_extensions.py"

if [[ ! -f "$py_script" ]]; then
  echo "RESULT: status=script-missing"
  echo "RESULT: expected=$py_script"
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "RESULT: status=python3-missing"
  exit 1
fi

exec python3 "$py_script" "$@"
