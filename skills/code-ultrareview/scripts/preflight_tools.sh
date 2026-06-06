#!/usr/bin/env bash
# Preflight — list battery tools that would run for the given scope, plus
# install commands for any missing ones. Informational only — never installs.
#
# Wraps `run_battery.sh --dry-run` (same dispatch logic, single source of
# truth) and reformats the JSON as a human-readable table.
#
# Usage:
#   preflight_tools.sh --scope <scope.json> [--repo <path>]

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BATTERY="$SCRIPT_DIR/run_battery.sh"

SCOPE=""
REPO="."

usage() {
  cat <<'EOF' >&2
Usage: preflight_tools.sh --scope <scope.json> [--repo <path>]

Lists the battery tools that would run for the given scope, plus install
commands for any missing tools. Informational only — never installs.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope) SCOPE="${2:-}"; shift 2 ;;
    --repo) REPO="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ -z "$SCOPE" ]]; then
  usage
  exit 2
fi
if [[ ! -r "$SCOPE" ]]; then
  echo "ERROR: scope.json not readable: $SCOPE" >&2
  exit 2
fi

# Spool dry-run output to a temp file so we can fail loud on a non-zero exit.
PLAN_FILE="$(mktemp -t preflight_plan_XXXX)"
trap 'rm -f "$PLAN_FILE"' EXIT

if ! bash "$BATTERY" --scope "$SCOPE" --output-dir "$(dirname "$PLAN_FILE")" \
    --repo "$REPO" --dry-run >"$PLAN_FILE"; then
  echo "ERROR: dry-run failed; see stderr above" >&2
  exit 2
fi

python3 - "$PLAN_FILE" "$SCRIPT_DIR" <<'PY'
import json
import re
import sys
from pathlib import Path

plan_path = Path(sys.argv[1])
script_dir = Path(sys.argv[2])

with plan_path.open(encoding="utf-8") as f:
    plan = json.load(f)

# Pull BATTERY_TABLE from run_battery.sh — single source of truth.
battery_sh = (script_dir / "run_battery.sh").read_text(encoding="utf-8")
m = re.search(r"BATTERY_TABLE=\(\s*\n(.+?)\n\)", battery_sh, re.DOTALL)
install_by_tool = {}
axis_by_tool = {}
if m:
    for raw in m.group(1).splitlines():
        line = raw.strip()
        if not line or not line.startswith('"') or not line.endswith('"'):
            continue
        parts = line.strip('"').split("|")
        if len(parts) >= 3:
            install_by_tool[parts[0]] = parts[1]
            axis_by_tool[parts[0]] = parts[2]

repo_kind = plan.get("repo_kind") or "unknown"
languages = plan.get("languages") or []
dispatched = plan.get("dispatched") or []
skipped = plan.get("skipped") or []

print(f"Repo kind:  {repo_kind}")
print(f"Languages:  {', '.join(languages) if languages else '(none)'}")
print()
print(f"Dispatched ({len(dispatched)} tool{'s' if len(dispatched) != 1 else ''}):")
if not dispatched:
    print("  (none — no language in scope matches a battery tool)")
for entry in dispatched:
    tool = entry.get("tool", "?")
    wrapper = entry.get("wrapper", "?")
    axis = axis_by_tool.get(tool, "")
    print(f"  - {tool:<22} via {wrapper:<4}   → {axis}")

print()
print(f"Skipped ({len(skipped)} tool{'s' if len(skipped) != 1 else ''}):")
if not skipped:
    print("  (none — every tool the dispatch wants is available)")
for entry in skipped:
    tool = entry.get("tool", "?")
    install = install_by_tool.get(tool, "?")
    axis = axis_by_tool.get(tool, "")
    print(f"  - {tool:<22} install: {install}")
    if axis:
        print(f"    {'':<22} coverage: {axis}")

print()
print("Informational only — preflight does not install anything.")
PY
