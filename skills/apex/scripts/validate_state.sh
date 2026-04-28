#!/usr/bin/env bash
#
# validate_state.sh — check apex state integrity before entering a step.
#
# Usage:
#   validate_state.sh <task_id> <step_num>
#
# Checks in order:
#   1. Task folder exists under .claude/output/apex/
#   2. 00-context.md exists inside it
#   3. Every prior step file (01..step_num-1) exists
#   4. Every prior step row in the 00-context.md Progress table reads
#      "✓ Complete"
#
# Exit:
#   0   state valid — safe to enter step_num
#   1   task folder or 00-context.md missing
#   2   prior step file missing
#   3   prior step not marked complete
#
# Emits RESULT: lines; detailed findings go to stderr.

set -euo pipefail

TASK_ID="${1:?usage: validate_state.sh <task_id> <step_num>}"
STEP_NUM="${2:?usage: validate_state.sh <task_id> <step_num>}"

[[ "$STEP_NUM" =~ ^[1-4]$ ]] || {
  echo "error: step_num must be 1-4, got $STEP_NUM" >&2
  exit 1
}

PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
TASK_DIR="${PROJECT_ROOT}/.claude/output/apex/${TASK_ID}"
CONTEXT="${TASK_DIR}/00-context.md"

if [[ ! -d "$TASK_DIR" ]]; then
  echo "RESULT: error=task-missing path=$TASK_DIR" >&2
  exit 1
fi

if [[ ! -f "$CONTEXT" ]]; then
  echo "RESULT: error=context-missing path=$CONTEXT" >&2
  exit 1
fi

# Verify each prior step. C-style loop for macOS BSD-seq portability —
# `seq 1 0` counts down on BSD instead of producing an empty range.
for ((prior=1; prior<STEP_NUM; prior++)); do
  prior_num=$(printf "%02d" "$prior")
  # Find the step file (e.g., 01-analyze.md)
  prior_file=$(find "$TASK_DIR" -maxdepth 1 -name "${prior_num}-*.md" | head -1)

  if [[ -z "$prior_file" ]] || [[ ! -f "$prior_file" ]]; then
    echo "RESULT: error=step-file-missing step=$prior_num" >&2
    exit 2
  fi

  # Extract step name from filename: 01-analyze.md → analyze
  step_name=$(basename "$prior_file" .md | sed "s/^${prior_num}-//")

  # Grep the progress table for "| NN-name | ✓ Complete |"
  if ! grep -qE "\|\s*${prior_num}-${step_name}\s*\|\s*✓ Complete" "$CONTEXT"; then
    echo "RESULT: error=step-incomplete step=$prior_num name=$step_name" >&2
    exit 3
  fi
done

echo "RESULT: ok=true task_id=$TASK_ID step=$STEP_NUM"
exit 0
