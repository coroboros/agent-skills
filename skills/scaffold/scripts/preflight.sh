#!/usr/bin/env bash
#
# preflight.sh — verify scaffold prerequisites
#
# Usage:
#   preflight.sh <target_dir> <project_name>
#
# Checks:
#   pnpm present
#   stable even-numbered node >= 22.12.0
#   jq present
#   project_name + Cloudflare service slug
#   target_dir state (clean / occupied / missing) — occupied targets fail closed
#
# Exit:
#   0   pnpm + node + jq OK (environment ready)
#   1   pnpm missing, jq missing, node missing, or unsupported node version
#
# Emits machine-readable summary on stdout prefixed with "RESULT:", one
# key=value per line. The caller parses these to decide whether to proceed.

set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: preflight.sh <target_dir> <project_name>" >&2
  exit 2
fi

TARGET_DIR="$1"
PROJECT_NAME="$2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source-path=SCRIPTDIR
# shellcheck source=project-name.sh
source "$SCRIPT_DIR/project-name.sh"

ENV_OK=true

if ! validate_project_name "$PROJECT_NAME"; then
  echo "RESULT: error=$PROJECT_NAME_ERROR"
  echo "RESULT: ok=false"
  exit 1
fi
echo "RESULT: project-name=valid slug=$PROJECT_SLUG"

TARGET_PATH="${TARGET_DIR%/}"
TARGET_BASENAME=""
if [[ -d "$TARGET_DIR" ]]; then
  if ! TARGET_RESOLVED="$(cd "$TARGET_DIR" 2>/dev/null && pwd -P)"; then
    echo "RESULT: error=invalid-target-name"
    echo "RESULT: ok=false"
    exit 1
  fi
  TARGET_BASENAME="${TARGET_RESOLVED##*/}"
elif [[ -n "$TARGET_PATH" ]]; then
  TARGET_BASENAME="${TARGET_PATH##*/}"
fi
if ! validate_target_basename "$TARGET_BASENAME"; then
  echo "RESULT: error=$TARGET_NAME_ERROR"
  echo "RESULT: ok=false"
  exit 1
fi
echo "RESULT: target-name=valid name=$TARGET_BASENAME"

if command -v pnpm >/dev/null 2>&1; then
  echo "RESULT: pnpm=yes version=$(pnpm --version)"
else
  echo "RESULT: pnpm=no"
  ENV_OK=false
fi

if command -v node >/dev/null 2>&1; then
  NODE_VERSION=$(node --version | sed 's/^v//')
  if [[ "$NODE_VERSION" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
    NODE_MAJOR="${BASH_REMATCH[1]}"
    NODE_MINOR="${BASH_REMATCH[2]}"
    if [[ "$NODE_MAJOR" -lt 22 ]] \
      || { [[ "$NODE_MAJOR" -eq 22 ]] && [[ "$NODE_MINOR" -lt 12 ]]; }; then
      echo "RESULT: node=too-old version=$NODE_VERSION required=22.12.0"
      ENV_OK=false
    elif (( NODE_MAJOR % 2 != 0 )); then
      echo "RESULT: node=unsupported version=$NODE_VERSION reason=odd-major required=stable-even-22.12.0-or-newer"
      ENV_OK=false
    else
      echo "RESULT: node=yes version=$NODE_VERSION"
    fi
  else
    echo "RESULT: node=unsupported version=$NODE_VERSION reason=invalid-version required=stable-even-22.12.0-or-newer"
    ENV_OK=false
  fi
else
  echo "RESULT: node=no"
  ENV_OK=false
fi

if command -v jq >/dev/null 2>&1; then
  echo "RESULT: jq=yes"
else
  echo "RESULT: jq=no"
  ENV_OK=false
fi

if [[ -L "$TARGET_DIR" ]]; then
  echo "RESULT: target=occupied path=$TARGET_DIR"
  ENV_OK=false
elif [[ ! -e "$TARGET_DIR" ]]; then
  echo "RESULT: target=missing path=$TARGET_DIR"
elif [[ ! -d "$TARGET_DIR" ]]; then
  echo "RESULT: target=occupied path=$TARGET_DIR"
  ENV_OK=false
elif [[ -n "$(find "$TARGET_DIR" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]]; then
  echo "RESULT: target=occupied path=$TARGET_DIR"
  ENV_OK=false
else
  echo "RESULT: target=clean path=$TARGET_DIR files=0"
fi

if [[ "$ENV_OK" = true ]]; then
  echo "RESULT: ok=true"
  exit 0
else
  echo "RESULT: ok=false"
  exit 1
fi
