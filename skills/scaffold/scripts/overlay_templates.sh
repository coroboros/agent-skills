#!/usr/bin/env bash
#
# overlay_templates.sh — lay down opinionated templates + merge package.json scripts
#
# Usage:
#   overlay_templates.sh <scaffold> <project_name> <target_dir> [--force]
#
# Arguments:
#   scaffold       next-cloudflare | astro-cloudflare
#   project_name   Used for [Project Name] and project-name substitutions
#   target_dir     Project directory (must exist — the framework CLI created it)
#   --force        Overwrite existing non-template files (default: skip with warning)
#
# Behaviour:
#   Copies templates/shared/* and templates/<scaffold>/* into target_dir with
#   token substitution ({project_name}, [Project Name], project-name). Merges
#   scripts.json into the existing package.json (requires jq) and sets
#   "type": "module" + "private": true.
#
#   Idempotent: refuses to overwrite existing non-template files unless --force.
#
# Exit:
#   0   all templates written (or skipped under idempotency rule)
#   1   missing argument, unknown scaffold, missing template, missing target,
#       jq missing, or skipped files without --force
#
# Emits machine-readable summary on stdout prefixed with "RESULT:", one
# key=value per line.

set -euo pipefail

usage() {
  sed -n '2,28p' "$0" | sed 's/^# \{0,1\}//'
  exit 2
}

[[ $# -lt 3 ]] && usage
case "$1" in -h|--help) usage ;; esac

SCAFFOLD="$1"
PROJECT_NAME="$2"
TARGET_DIR="$3"
FORCE="${4:-}"

case "$SCAFFOLD" in
  next-cloudflare|astro-cloudflare) ;;
  *) echo "error: unknown scaffold: $SCAFFOLD (expected next-cloudflare | astro-cloudflare)" >&2; exit 1 ;;
esac

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATES_DIR="$SKILL_DIR/templates"

[[ -d "$TEMPLATES_DIR/shared" ]]   || { echo "error: missing $TEMPLATES_DIR/shared" >&2; exit 1; }
[[ -d "$TEMPLATES_DIR/$SCAFFOLD" ]] || { echo "error: missing $TEMPLATES_DIR/$SCAFFOLD" >&2; exit 1; }
[[ -d "$TARGET_DIR" ]]             || { echo "error: target_dir does not exist: $TARGET_DIR" >&2; exit 1; }

WRITTEN=0
SKIPPED=0

# write_file <source> <dest>
# Substitutes tokens, refuses overwrite unless --force.
write_file() {
  local src="$1"
  local dest="$2"

  if [[ ! -f "$src" ]]; then
    echo "RESULT: error=source-missing path=$src" >&2
    return 1
  fi

  mkdir -p "$(dirname "$dest")"

  if [[ -e "$dest" ]] && [[ "$FORCE" != "--force" ]]; then
    echo "RESULT: skipped=$dest reason=exists"
    SKIPPED=$((SKIPPED + 1))
    return 0
  fi

  # Substitution order matters: longer tokens first to avoid partial matches.
  # `project-name.example` is left intact (astro site URL placeholder) — user
  # swaps the .example for their real domain after scaffold.
  sed \
    -e "s/\[Project Name\]/$PROJECT_NAME/g" \
    -e "s/{project_name}/$PROJECT_NAME/g" \
    -e "s/\"name\": \"project-name\"/\"name\": \"$PROJECT_NAME\"/g" \
    "$src" > "$dest"

  echo "RESULT: wrote=$dest"
  WRITTEN=$((WRITTEN + 1))
}

# --- shared templates ------------------------------------------------------

write_file "$TEMPLATES_DIR/shared/biome.json.template" "$TARGET_DIR/biome.json"
write_file "$TEMPLATES_DIR/shared/gitignore"            "$TARGET_DIR/.gitignore"
write_file "$TEMPLATES_DIR/shared/worktreeinclude"      "$TARGET_DIR/.worktreeinclude"
write_file "$TEMPLATES_DIR/shared/cloudflare-tooling.md" "$TARGET_DIR/.claude/rules/cloudflare-tooling.md"

# --- scaffold-specific templates -------------------------------------------

case "$SCAFFOLD" in
  next-cloudflare)
    write_file "$TEMPLATES_DIR/next-cloudflare/CLAUDE.md"                    "$TARGET_DIR/CLAUDE.md"
    write_file "$TEMPLATES_DIR/next-cloudflare/wrangler.jsonc.template"      "$TARGET_DIR/wrangler.jsonc"
    write_file "$TEMPLATES_DIR/next-cloudflare/open-next.config.ts.template" "$TARGET_DIR/open-next.config.ts"
    ;;
  astro-cloudflare)
    write_file "$TEMPLATES_DIR/astro-cloudflare/CLAUDE.md"                "$TARGET_DIR/CLAUDE.md"
    write_file "$TEMPLATES_DIR/astro-cloudflare/seo.md"                   "$TARGET_DIR/.claude/rules/seo.md"
    write_file "$TEMPLATES_DIR/astro-cloudflare/astro.config.mjs.template" "$TARGET_DIR/astro.config.mjs"
    write_file "$TEMPLATES_DIR/astro-cloudflare/wrangler.jsonc.template"  "$TARGET_DIR/wrangler.jsonc"
    ;;
esac

# --- package.json scripts merge --------------------------------------------

SCRIPTS_TEMPLATE="$TEMPLATES_DIR/$SCAFFOLD/scripts.json"
PKG_JSON="$TARGET_DIR/package.json"

if [[ -f "$SCRIPTS_TEMPLATE" ]] && [[ -f "$PKG_JSON" ]]; then
  if ! command -v jq >/dev/null 2>&1; then
    echo "error: jq required for package.json merge (brew install jq)" >&2
    echo "RESULT: error=jq-missing"
    exit 1
  fi

  TMP_PKG=$(mktemp)
  # Merge: our scripts override CLI defaults; ensure type=module and private=true.
  jq --slurpfile new "$SCRIPTS_TEMPLATE" \
    '.scripts = ((.scripts // {}) + $new[0]) | .type = "module" | .private = true' \
    "$PKG_JSON" > "$TMP_PKG"
  mv "$TMP_PKG" "$PKG_JSON"
  echo "RESULT: merged=$PKG_JSON"
else
  echo "RESULT: merged=none reason=template-or-pkg-missing"
fi

# --- verdict ---------------------------------------------------------------

echo "RESULT: written=$WRITTEN skipped=$SKIPPED scaffold=$SCAFFOLD"

if [[ "$SKIPPED" -gt 0 ]] && [[ "$FORCE" != "--force" ]]; then
  echo "RESULT: ok=partial hint=--force to overwrite"
  exit 1
fi

echo "RESULT: ok=true"
exit 0
