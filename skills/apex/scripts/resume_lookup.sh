#!/usr/bin/env bash
#
# resume_lookup.sh — resolve a partial apex task ID to an exact task folder.
#
# Usage:
#   resume_lookup.sh <partial_id>
#
# Glob-searches .claude/output/apex/ for task folders matching <partial_id>:
#   - exact prefix match preferred (e.g. "01" matches "01-auth-middleware")
#   - falls back to substring match anywhere in the name
#
# Exit:
#   0   single match — absolute path on stdout
#   1   ambiguous — candidates listed on stderr (one per line)
#   2   no match — message on stderr
#
# Emits a final `RESULT:` line on stdout for parseability.

set -euo pipefail

PARTIAL="${1:?usage: resume_lookup.sh <partial_id>}"

PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
APEX_DIR="${PROJECT_ROOT}/.claude/output/apex"

if [[ ! -d "$APEX_DIR" ]]; then
  echo "RESULT: error=apex-dir-missing path=$APEX_DIR" >&2
  exit 2
fi

# Collect matches — prefix-matches first, then substring-matches.
declare -a PREFIX_MATCHES=()
declare -a SUBSTRING_MATCHES=()

for dir in "$APEX_DIR"/*/; do
  [[ -d "$dir" ]] || continue
  name=$(basename "$dir")
  if [[ "$name" == "$PARTIAL"* ]]; then
    PREFIX_MATCHES+=("$dir")
  elif [[ "$name" == *"$PARTIAL"* ]]; then
    SUBSTRING_MATCHES+=("$dir")
  fi
done

# Prefer prefix matches when any exist.
if [[ ${#PREFIX_MATCHES[@]} -gt 0 ]]; then
  MATCHES=("${PREFIX_MATCHES[@]}")
elif [[ ${#SUBSTRING_MATCHES[@]} -gt 0 ]]; then
  MATCHES=("${SUBSTRING_MATCHES[@]}")
else
  MATCHES=()
fi

case "${#MATCHES[@]}" in
  0)
    echo "RESULT: error=no-match partial=$PARTIAL" >&2
    exit 2
    ;;
  1)
    # Strip trailing slash.
    path="${MATCHES[0]%/}"
    echo "$path"
    echo "RESULT: ok=true path=$path"
    exit 0
    ;;
  *)
    echo "RESULT: error=ambiguous partial=$PARTIAL count=${#MATCHES[@]}" >&2
    echo "Candidates:" >&2
    for m in "${MATCHES[@]}"; do
      echo "  $(basename "${m%/}")" >&2
    done
    exit 1
    ;;
esac
