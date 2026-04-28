#!/usr/bin/env bash
#
# verify_scaffold.sh — post-scaffold health check: biome + typecheck
#
# Usage:
#   verify_scaffold.sh <project_dir>
#
# Runs `pnpm biome check --write .` followed by `pnpm typecheck` inside
# project_dir. On any failure, re-runs without redirection to surface
# diagnostics (bounded to the first 60 lines to keep output parseable).
#
# Exit:
#   0   both biome and typecheck pass
#   1   biome failed, typecheck failed, or project_dir missing
#
# Emits machine-readable summary on stdout prefixed with "RESULT:", one
# key=value per line.

set -euo pipefail

PROJECT_DIR="${1:?project_dir required}"

[[ -d "$PROJECT_DIR" ]] || { echo "error: project_dir does not exist: $PROJECT_DIR" >&2; exit 1; }
[[ -f "$PROJECT_DIR/package.json" ]] || { echo "error: no package.json in $PROJECT_DIR" >&2; exit 1; }

cd "$PROJECT_DIR"

OK=true

# --- biome -----------------------------------------------------------------

if pnpm biome check --write . >/dev/null 2>&1; then
  echo "RESULT: biome=pass"
else
  echo "RESULT: biome=fail"
  echo "--- biome diagnostics (first 60 lines) ---" >&2
  # `|| true` keeps `set -e` + pipefail from aborting the script on the
  # diagnostic re-run; we already know it failed and want typecheck to run too.
  pnpm biome check . 2>&1 | head -60 >&2 || true
  echo "--- end biome diagnostics ---" >&2
  OK=false
fi

# --- typecheck -------------------------------------------------------------

if pnpm typecheck >/dev/null 2>&1; then
  echo "RESULT: typecheck=pass"
else
  echo "RESULT: typecheck=fail"
  echo "--- typecheck diagnostics (first 60 lines) ---" >&2
  pnpm typecheck 2>&1 | head -60 >&2 || true
  echo "--- end typecheck diagnostics ---" >&2
  OK=false
fi

# --- verdict ---------------------------------------------------------------

if [[ "$OK" = true ]]; then
  echo "RESULT: ok=true"
  exit 0
else
  echo "RESULT: ok=false"
  exit 1
fi
