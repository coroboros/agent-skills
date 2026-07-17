#!/usr/bin/env bash
# spec.sh — resolve the installed Design.md CLI and emit its canonical spec.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=resolve-designmd.sh
source "$SCRIPT_DIR/resolve-designmd.sh"

if ! DESIGNMD="$(resolve_designmd .)"; then
  echo "RESULT: status=designmd-missing"
  exit 1
fi

exec "$DESIGNMD" spec "$@"
