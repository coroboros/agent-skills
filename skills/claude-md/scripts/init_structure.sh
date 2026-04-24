#!/usr/bin/env bash
#
# init_structure.sh — idempotent scaffold for CLAUDE.md storage strategies.
#
# Usage:
#   init_structure.sh <mode> [target_dir]
#
# Modes (see the Storage Strategy section of claude-md/SKILL.md):
#   single       Only ./CLAUDE.md
#   hybrid       ./CLAUDE.md (slim hub) + ./.claude/rules/ (content)
#   rules-only   ./.claude/rules/ only (no CLAUDE.md at project root)
#
# target_dir defaults to the current working directory.
#
# Idempotent: refuses to overwrite existing files. Use `--force` (after the
# mode, after any target_dir) to replace them.
#
# Exit:
#   0   all requested files created or left intact under idempotency
#   1   argument error or collision without --force
#
# Emits RESULT: key=value lines on stdout; human-readable messages on stderr.

set -euo pipefail

usage() {
  sed -n '2,22p' "$0" | sed 's/^# \{0,1\}//'
  exit 2
}

[[ $# -lt 1 ]] && usage
case "$1" in -h|--help) usage ;; esac

MODE="$1"
shift

TARGET_DIR="${1:-.}"
[[ "${1:-}" == "--force" ]] || shift 2>/dev/null || true
[[ $# -gt 0 ]] || true

FORCE=0
for arg in "$@"; do
  [[ "$arg" == "--force" ]] && FORCE=1
done
# Allow --force either before or after the target.
if [[ "$TARGET_DIR" == "--force" ]]; then
  FORCE=1
  TARGET_DIR="."
fi

case "$MODE" in
  single|hybrid|rules-only) ;;
  *) echo "error: mode must be single | hybrid | rules-only" >&2; exit 1 ;;
esac

[[ -d "$TARGET_DIR" ]] || { echo "error: target_dir does not exist: $TARGET_DIR" >&2; exit 1; }

WRITTEN=0
SKIPPED=0

write_if_new() {
  local path="$1"
  local body="$2"

  if [[ -e "$path" ]] && [[ "$FORCE" -eq 0 ]]; then
    echo "RESULT: skipped=$path reason=exists"
    SKIPPED=$((SKIPPED + 1))
    return 0
  fi

  mkdir -p "$(dirname "$path")"
  printf '%s' "$body" > "$path"
  echo "RESULT: wrote=$path"
  WRITTEN=$((WRITTEN + 1))
}

CLAUDE_MD_MINIMAL='# Project

## Tech stack
- [Primary framework + non-obvious libraries]

## Commands
- `npm run dev` — dev server
- `npm test` — run tests

## Rules
- [Critical, project-specific constraint]
'

CLAUDE_MD_HYBRID='# Project

## Tech stack
- [Primary framework + non-obvious libraries]

## Commands
- `npm run dev` — dev server
- `npm test` — run tests

## Rules
@.claude/rules/style.md
@.claude/rules/testing.md
'

RULES_STYLE='---
paths:
  - "src/**/*.{ts,tsx}"
---
# Style

- [Style rule specific to this path scope]
'

RULES_TESTING='---
paths:
  - "**/*.test.ts"
  - "**/*.spec.ts"
---
# Testing

- [Testing rule specific to this path scope]
'

case "$MODE" in
  single)
    write_if_new "$TARGET_DIR/CLAUDE.md" "$CLAUDE_MD_MINIMAL"
    ;;
  hybrid)
    write_if_new "$TARGET_DIR/CLAUDE.md" "$CLAUDE_MD_HYBRID"
    write_if_new "$TARGET_DIR/.claude/rules/style.md" "$RULES_STYLE"
    write_if_new "$TARGET_DIR/.claude/rules/testing.md" "$RULES_TESTING"
    ;;
  rules-only)
    write_if_new "$TARGET_DIR/.claude/rules/style.md" "$RULES_STYLE"
    write_if_new "$TARGET_DIR/.claude/rules/testing.md" "$RULES_TESTING"
    ;;
esac

echo "RESULT: mode=$MODE written=$WRITTEN skipped=$SKIPPED"

if [[ "$SKIPPED" -gt 0 ]] && [[ "$FORCE" -eq 0 ]]; then
  echo "RESULT: ok=partial hint=--force to overwrite"
  exit 1
fi

echo "RESULT: ok=true"
exit 0
