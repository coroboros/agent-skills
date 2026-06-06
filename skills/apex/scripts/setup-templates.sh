#!/usr/bin/env bash
# APEX Template Setup Script
#
# Usage: setup-templates.sh "feature-name" [other args...]
# The script auto-generates the task ID with the next available number.

set -euo pipefail

# First arg is the feature name (kebab-case).
FEATURE_NAME="${1:-}"
TASK_DESCRIPTION="${2:-}"
AUTO_MODE="${3:-false}"
SAVE_MODE="${4:-false}"
ECONOMY_MODE="${5:-false}"
BRANCH_MODE="${6:-false}"
INTERACTIVE_MODE="${7:-false}"
BRANCH_NAME="${8:-}"
ORIGINAL_INPUT="${9:-}"

if [[ -z "$FEATURE_NAME" ]]; then
    echo "Error: FEATURE_NAME is required"
    exit 1
fi

if [[ -z "$TASK_DESCRIPTION" ]]; then
    echo "Error: TASK_DESCRIPTION is required"
    exit 1
fi

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Must match resume_lookup.sh / update-progress.sh / validate_state.sh —
# divergence strands output where the sibling scripts can't find it.
# Global per repo-conventions.md § Output paths: ~/.claude/output/{project}/apex.
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
PROJECT=$(basename "$PROJECT_ROOT" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-*//; s/-*$//')
: "${PROJECT:=unnamed}"  # all-non-alphanumeric basename kebabs empty — keep the path well-formed
APEX_OUTPUT_DIR="${HOME}/.claude/output/${PROJECT}/apex"

mkdir -p "$APEX_OUTPUT_DIR"

NEXT_NUM=1
if [[ -d "$APEX_OUTPUT_DIR" ]]; then
    # Find highest existing number prefix (tolerate empty dir: grep returns 1 on no match).
    # SC2010 disabled: filenames this script creates are strictly NN-kebab-case ASCII —
    # the warning's "non-alphanumeric filenames" concern does not apply.
    # shellcheck disable=SC2010
    HIGHEST=$(ls -1 "$APEX_OUTPUT_DIR" 2>/dev/null | grep -oE '^[0-9]+' | sort -n | tail -1 || true)
    if [[ -n "$HIGHEST" ]]; then
        # Force base-10 interpretation (leading zeros would be treated as octal)
        NEXT_NUM=$((10#$HIGHEST + 1))
    fi
fi

TASK_NUM=$(printf "%02d" "$NEXT_NUM")
TASK_ID="${TASK_NUM}-${FEATURE_NAME}"

OUTPUT_DIR="${APEX_OUTPUT_DIR}/${TASK_ID}"

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE_DIR="${SKILL_DIR}/templates"

mkdir -p "$OUTPUT_DIR"

# Values pass through awk's ENVIRON[] array (literal strings, no escape
# processing), eliminating both the sed s/// regex-metachar surface and the
# awk -v backslash-escape interpretation. The inner loop uses index/substr
# (literal substitution, never regex), so user-controlled TASK_DESCRIPTION can
# carry any byte without breaking templating. W011 hardening surface flagged by
# external scanners.
render_template() {
    local template_file="$1"
    local output_file="$2"

    TASK_ID="$TASK_ID" \
    TASK_DESCRIPTION="$TASK_DESCRIPTION" \
    TIMESTAMP="$TIMESTAMP" \
    AUTO_MODE="$AUTO_MODE" \
    SAVE_MODE="$SAVE_MODE" \
    ECONOMY_MODE="$ECONOMY_MODE" \
    BRANCH_MODE="$BRANCH_MODE" \
    INTERACTIVE_MODE="$INTERACTIVE_MODE" \
    BRANCH_NAME="$BRANCH_NAME" \
    ORIGINAL_INPUT="$ORIGINAL_INPUT" \
    awk '
        BEGIN {
            keys[1]  = "{{task_id}}";          vals[1]  = ENVIRON["TASK_ID"]
            keys[2]  = "{{task_description}}"; vals[2]  = ENVIRON["TASK_DESCRIPTION"]
            keys[3]  = "{{timestamp}}";        vals[3]  = ENVIRON["TIMESTAMP"]
            keys[4]  = "{{auto_mode}}";        vals[4]  = ENVIRON["AUTO_MODE"]
            keys[5]  = "{{save_mode}}";        vals[5]  = ENVIRON["SAVE_MODE"]
            keys[6]  = "{{economy_mode}}";     vals[6]  = ENVIRON["ECONOMY_MODE"]
            keys[7]  = "{{branch_mode}}";      vals[7]  = ENVIRON["BRANCH_MODE"]
            keys[8]  = "{{interactive_mode}}"; vals[8]  = ENVIRON["INTERACTIVE_MODE"]
            keys[9]  = "{{branch_name}}";      vals[9]  = ENVIRON["BRANCH_NAME"]
            keys[10] = "{{original_input}}";   vals[10] = ENVIRON["ORIGINAL_INPUT"]
        }
        {
            for (i = 1; i <= 10; i++) {
                while ((p = index($0, keys[i])) > 0) {
                    $0 = substr($0, 1, p - 1) vals[i] substr($0, p + length(keys[i]))
                }
            }
            print
        }
        ' "$template_file" > "$output_file"
}

render_template "${TEMPLATE_DIR}/00-context.md" "${OUTPUT_DIR}/00-context.md"

# Step files start as headers only; content is appended during execution.
render_template "${TEMPLATE_DIR}/01-analyze.md" "${OUTPUT_DIR}/01-analyze.md"
render_template "${TEMPLATE_DIR}/02-plan.md" "${OUTPUT_DIR}/02-plan.md"
render_template "${TEMPLATE_DIR}/03-execute.md" "${OUTPUT_DIR}/03-execute.md"
render_template "${TEMPLATE_DIR}/04-examine.md" "${OUTPUT_DIR}/04-examine.md"

# Caller parses these to capture the generated task ID and output path.
echo "TASK_ID=${TASK_ID}"
echo "OUTPUT_DIR=${OUTPUT_DIR}"
echo "✓ APEX templates initialized: ${OUTPUT_DIR}"
exit 0
