#!/usr/bin/env bash
# Preflight — list battery tools that would run for the given scope, plus
# exact install commands for any missing ones. Never installs.
#
# Wraps `run_battery.sh --dry-run` (same dispatch logic, single source of
# truth) and reformats the JSON as a human-readable table.
#
# Usage:
#   preflight_tools.sh --scope <scope.json> [--repo <path>] [--axes <list>]

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BATTERY="$SCRIPT_DIR/run_battery.sh"

SCOPE=""
REPO="."
AXES=""

usage() {
  cat <<'EOF' >&2
Usage: preflight_tools.sh --scope <scope.json> [--repo <path>] [--axes <list>]

Lists the battery tools that would run for the given scope, plus install
commands for any missing tools. Exits 3 when coverage is incomplete.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope) SCOPE="${2:-}"; shift 2 ;;
    --repo) REPO="${2:-}"; shift 2 ;;
    --axes) AXES="${2:-}"; shift 2 ;;
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
PLAN_FILE="$(mktemp "${TMPDIR:-/tmp}/preflight-plan.XXXXXX")"
trap 'rm -f "$PLAN_FILE"' EXIT

BATTERY_ARGS=(--scope "$SCOPE" --output-dir "$(dirname "$PLAN_FILE")" --repo "$REPO" --dry-run)
[[ -z "$AXES" ]] || BATTERY_ARGS+=(--axes "$AXES")
bash "$BATTERY" "${BATTERY_ARGS[@]}" >"$PLAN_FILE"
battery_rc=$?
if [[ $battery_rc -ne 0 && $battery_rc -ne 3 ]]; then
  echo "ERROR: battery preflight failed; see stderr above" >&2
  exit "$battery_rc"
fi

python3 - "$PLAN_FILE" <<'PY'
import json
import sys
from pathlib import Path

plan_path = Path(sys.argv[1])

with plan_path.open(encoding="utf-8") as f:
    plan = json.load(f)

repo_kind = plan.get("repo_kind") or "unknown"
languages = plan.get("languages") or []
available = plan.get("available") or []
missing = plan.get("missing") or []

print(f"Repo kind:  {repo_kind}")
print(f"Languages:  {', '.join(languages) if languages else '(none)'}")
print()
print(f"Available ({len(available)} tool{'s' if len(available) != 1 else ''}):")
if not available:
    print("  (none — no language in scope matches a battery tool)")
for entry in available:
    tool = entry.get("tool", "?")
    wrapper = entry.get("wrapper", "?")
    axes = ", ".join(entry.get("axes") or [])
    coverage = entry.get("coverage", "")
    print(f"  - {tool:<22} via {wrapper:<7} axes: {axes}")
    if coverage:
        print(f"    {'':<22} coverage: {coverage}")

print()
print(f"Missing ({len(missing)} tool{'s' if len(missing) != 1 else ''}):")
if not missing:
    print("  (none — deterministic coverage is complete for this scope)")
for entry in missing:
    tool = entry.get("tool", "?")
    install = entry.get("install", "?")
    axes = ", ".join(entry.get("axes") or [])
    coverage = entry.get("coverage", "")
    print(f"  - {tool:<22} install: {install}")
    print(f"    {'':<22} axes: {axes}; coverage: {coverage}")

skipped = plan.get("skipped") or []
if skipped:
    print()
    print(f"Not applicable ({len(skipped)} tool{'s' if len(skipped) != 1 else ''}):")
    for entry in skipped:
        print(f"  - {entry.get('tool', '?'):<22} {entry.get('reason', '')}")

print()
if missing:
    print("BLOCKED: run every install command above, then rerun Code Ultrareview.")
else:
    print("READY: deterministic coverage is complete for this scope.")
print("Preflight never installs or resolves packages.")
PY

exit "$battery_rc"
