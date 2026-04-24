#!/usr/bin/env bash
#
# preflight.sh — verify scaffold prerequisites
#
# Usage:
#   preflight.sh [target_dir]
#
# Checks:
#   pnpm present
#   node ≥ 22
#   target_dir state (clean / occupied / missing) — informational, does not fail
#
# Exit:
#   0   pnpm + node OK (environment ready)
#   1   pnpm missing, node missing, or node < 22
#
# Emits machine-readable summary on stdout prefixed with "RESULT:", one
# key=value per line. The caller parses these to decide whether to proceed.

set -euo pipefail

TARGET_DIR="${1:-.}"

ENV_OK=true

# --- pnpm ------------------------------------------------------------------

if command -v pnpm >/dev/null 2>&1; then
  echo "RESULT: pnpm=yes version=$(pnpm --version)"
else
  echo "RESULT: pnpm=no"
  ENV_OK=false
fi

# --- node ≥ 22 -------------------------------------------------------------

if command -v node >/dev/null 2>&1; then
  NODE_VERSION=$(node --version | sed 's/^v//')
  NODE_MAJOR="${NODE_VERSION%%.*}"
  if [[ "$NODE_MAJOR" =~ ^[0-9]+$ ]] && [[ "$NODE_MAJOR" -ge 22 ]]; then
    echo "RESULT: node=yes version=$NODE_VERSION"
  else
    echo "RESULT: node=too-old version=$NODE_VERSION required=22"
    ENV_OK=false
  fi
else
  echo "RESULT: node=no"
  ENV_OK=false
fi

# --- target dir state (informational) --------------------------------------

if [[ ! -d "$TARGET_DIR" ]]; then
  echo "RESULT: target=missing path=$TARGET_DIR"
elif [[ -f "$TARGET_DIR/package.json" ]] \
  || [[ -f "$TARGET_DIR/astro.config.mjs" ]] \
  || [[ -f "$TARGET_DIR/astro.config.ts" ]] \
  || [[ -f "$TARGET_DIR/next.config.ts" ]] \
  || [[ -f "$TARGET_DIR/next.config.js" ]]; then
  echo "RESULT: target=occupied path=$TARGET_DIR"
else
  FILE_COUNT=$(find "$TARGET_DIR" -maxdepth 1 -type f \! -name '.*' 2>/dev/null | wc -l | tr -d ' ')
  echo "RESULT: target=clean path=$TARGET_DIR files=$FILE_COUNT"
fi

# --- verdict ---------------------------------------------------------------

if [[ "$ENV_OK" = true ]]; then
  echo "RESULT: ok=true"
  exit 0
else
  echo "RESULT: ok=false"
  exit 1
fi
