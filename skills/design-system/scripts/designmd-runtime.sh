#!/usr/bin/env bash

# Shared PATH-only runtime contract for Design System wrappers.
designmd=""

require_designmd() {
  local rerun="$1"
  designmd="$(command -v designmd 2>/dev/null || true)"
  if [[ -z "$designmd" ]]; then
    echo "RESULT: status=designmd-missing"
    echo "RESULT: rerun=$rerun"
    echo "RESULT: remediation=Run npm install --global --ignore-scripts @google/design.md, verify designmd --version, then rerun"
    return 1
  fi
  if ! "$designmd" --version >/dev/null 2>&1; then
    echo "RESULT: status=designmd-unsupported"
    echo "RESULT: binary=$designmd"
    echo "RESULT: rerun=$rerun"
    echo "RESULT: remediation=Repair or upgrade designmd, verify designmd --version, then rerun"
    return 1
  fi
}
