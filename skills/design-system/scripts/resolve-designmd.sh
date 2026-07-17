#!/usr/bin/env bash

resolve_designmd() {
  local input="${1:-.}"
  local dir candidate package_json parent declared=0

  if [[ -d "$input" ]]; then
    dir="$input"
  else
    dir="$(dirname "$input")"
  fi
  dir="$(cd "$dir" 2>/dev/null && pwd -P)" || return 1

  while :; do
    candidate="$dir/node_modules/.bin/designmd"
    package_json="$dir/package.json"
    if [[ "$declared" -eq 0 && -f "$package_json" ]] \
      && python3 - "$package_json" <<'PY' >/dev/null 2>&1
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    package_json = json.load(handle)
declared = any(
    "@google/design.md" in (package_json.get(field) or {})
    for field in ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies")
)
raise SystemExit(0 if declared else 1)
PY
    then
      declared=1
    fi
    if [[ "$declared" -eq 1 && -x "$candidate" ]]; then
      printf '%s\n' "$candidate"
      return 0
    fi
    [[ "$dir" == "/" ]] && break
    parent="$(dirname "$dir")"
    [[ "$parent" == "$dir" ]] && break
    dir="$parent"
  done

  command -v designmd 2>/dev/null
}
