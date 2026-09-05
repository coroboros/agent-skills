#!/usr/bin/env bash
# APEX Progress Update Script
# Updates 00-context.md progress table

set -euo pipefail

TASK_ID="${1:-}"
STEP_NUMBER="${2:-}"
STEP_NAME="${3:-}"
STATUS="${4:-}"  # "in_progress" or "complete"

if [[ -z "$TASK_ID" ]] || [[ -z "$STEP_NUMBER" ]] || [[ -z "$STEP_NAME" ]] || [[ -z "$STATUS" ]]; then
    echo "Usage: $0 <task_id> <step_number> <step_name> <status>"
    echo "Example: $0 01-add-auth 01 analyze complete"
    exit 1
fi

PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
PROJECT=$(basename "$PROJECT_ROOT" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-*//; s/-*$//')
: "${PROJECT:=unnamed}"  # all-non-alphanumeric basename kebabs empty — keep the path well-formed
CONTEXT_FILE="${HOME}/.agents/output/${PROJECT}/apex/${TASK_ID}/00-context.md"

if [[ ! -f "$CONTEXT_FILE" ]]; then
    echo "Error: Context file not found: $CONTEXT_FILE"
    exit 1
fi

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

if [[ "$STATUS" == "in_progress" ]]; then
    STATUS_SYMBOL="⏳ In Progress"
elif [[ "$STATUS" == "complete" ]]; then
    STATUS_SYMBOL="✓ Complete"
else
    echo "Error: Invalid status. Use 'in_progress' or 'complete'"
    exit 1
fi

# Scope the temp file under ~/.agents/output — keeps inter-process state off
# the world-writable /tmp surface flagged by external scanners (W011).
APEX_TEMP_DIR="${HOME}/.agents/output"
mkdir -p "$APEX_TEMP_DIR"
TEMP_FILE=$(mktemp "$APEX_TEMP_DIR/.apex-progress.XXXXXX")
trap 'rm -f "$TEMP_FILE"' EXIT

awk -v step="${STEP_NUMBER}-${STEP_NAME}" \
    -v status="$STATUS_SYMBOL" \
    -v timestamp="$TIMESTAMP" '
BEGIN { in_table = 0; found = 0 }
{
    if ($0 ~ /^## Progress/) {
        in_table = 1
        print $0
        next
    }
    if (in_table && $0 ~ /^## /) in_table = 0

    if (in_table && index($0, "| " step " |") == 1) {
        printf "| %s | %s | %s |\n", step, status, timestamp
        found = 1
        next
    }

    print $0
}
END {
    if (!found) {
        print "Error: Step not found in progress table" > "/dev/stderr"
        exit 1
    }
}
' "$CONTEXT_FILE" > "$TEMP_FILE"

mv "$TEMP_FILE" "$CONTEXT_FILE"

echo "✓ Progress updated: ${STEP_NUMBER}-${STEP_NAME} → ${STATUS_SYMBOL}"
exit 0
