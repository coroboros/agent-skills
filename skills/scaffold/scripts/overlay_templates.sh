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
#   the shared ignore rules, ensures the Tailwind import, and merges package.json
#   atomically (requires jq), including the validated package name, scripts,
#   "type": "module", and "private": true.
#
#   Idempotent: refuses to overwrite existing non-template files unless --force.
#
# Exit:
#   0   all templates written (or skipped under idempotency rule)
#   1   missing argument, unknown scaffold, missing template, missing target,
#       missing package.json, jq missing, or skipped files without --force
#
# Emits machine-readable summary on stdout prefixed with "RESULT:", one
# key=value per line.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source-path=SCRIPTDIR
# shellcheck source=project-name.sh
source "$SCRIPT_DIR/project-name.sh"

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

if ! validate_project_name "$PROJECT_NAME"; then
  echo "error: project_name is not valid for npm and Cloudflare Workers" >&2
  echo "RESULT: error=$PROJECT_NAME_ERROR"
  exit 1
fi

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATES_DIR="$SKILL_DIR/templates"

[[ -d "$TEMPLATES_DIR/shared" ]]   || { echo "error: missing $TEMPLATES_DIR/shared" >&2; exit 1; }
[[ -d "$TEMPLATES_DIR/$SCAFFOLD" ]] || { echo "error: missing $TEMPLATES_DIR/$SCAFFOLD" >&2; exit 1; }
[[ -d "$TARGET_DIR" ]]             || { echo "error: target_dir does not exist: $TARGET_DIR" >&2; exit 1; }
if [[ -L "$TARGET_DIR" ]]; then
  echo "error: target_dir must not be a symbolic link: $TARGET_DIR" >&2
  echo "RESULT: error=unsafe-target path=$TARGET_DIR"
  exit 1
fi
if ! TARGET_DIR="$(cd "$TARGET_DIR" 2>/dev/null && pwd -P)"; then
  echo "error: target_dir could not be resolved: $TARGET_DIR" >&2
  echo "RESULT: error=unsafe-target path=$TARGET_DIR"
  exit 1
fi

SCRIPTS_TEMPLATE="$TEMPLATES_DIR/$SCAFFOLD/scripts.json"
TAILWIND_TEMPLATE="$TEMPLATES_DIR/shared/tailwind.css"
PKG_JSON="$TARGET_DIR/package.json"

WRITTEN=0
SKIPPED=0
ACTIVE_TEMP=""

# shellcheck disable=SC2329 # Invoked by the EXIT trap below.
cleanup_active_temp() {
  [[ -z "$ACTIVE_TEMP" ]] || rm -f "$ACTIVE_TEMP"
}
trap cleanup_active_temp EXIT

unsafe_destination() {
  local path="$1" reason="$2"
  echo "error: unsafe overlay destination ($reason): $path" >&2
  echo "RESULT: error=unsafe-destination path=$path reason=$reason"
  return 1
}

# Reject destination and parent symlinks before every write. All destinations
# are fixed by this script, but the containment check keeps future additions
# from escaping TARGET_DIR accidentally.
assert_safe_destination() {
  local dest="$1" relative current part index
  local parts=()

  case "$dest" in
    "$TARGET_DIR"/*) relative="${dest#"$TARGET_DIR"/}" ;;
    *) unsafe_destination "$dest" "outside-target"; return 1 ;;
  esac
  [[ -n "$relative" ]] || {
    unsafe_destination "$dest" "target-root"
    return 1
  }

  IFS='/' read -r -a parts <<<"$relative"
  current="$TARGET_DIR"
  for ((index = 0; index < ${#parts[@]} - 1; index++)); do
    part="${parts[$index]}"
    case "$part" in
      ""|.|..) unsafe_destination "$dest" "invalid-component"; return 1 ;;
    esac
    current="$current/$part"
    if [[ -L "$current" ]]; then
      unsafe_destination "$dest" "symlink-parent"
      return 1
    fi
    if [[ -e "$current" && ! -d "$current" ]]; then
      unsafe_destination "$dest" "non-directory-parent"
      return 1
    fi
  done
  if [[ -L "$dest" ]]; then
    unsafe_destination "$dest" "symlink-destination"
    return 1
  fi
  if [[ -e "$dest" && ! -f "$dest" ]]; then
    unsafe_destination "$dest" "non-file-destination"
    return 1
  fi
}

prepare_destination() {
  local dest="$1" parent resolved_parent
  assert_safe_destination "$dest" || return 1
  parent="$(dirname "$dest")"
  mkdir -p "$parent" || return 1
  assert_safe_destination "$dest" || return 1
  resolved_parent="$(cd "$parent" 2>/dev/null && pwd -P)" || {
    unsafe_destination "$dest" "unresolvable-parent"
    return 1
  }
  case "$resolved_parent" in
    "$TARGET_DIR"|"$TARGET_DIR"/*) ;;
    *) unsafe_destination "$dest" "resolved-parent-outside-target"; return 1 ;;
  esac
}

TEMPLATE_SOURCES=(
  "$TEMPLATES_DIR/shared/biome.json.template"
  "$TEMPLATES_DIR/shared/worktreeinclude"
  "$TEMPLATES_DIR/shared/CLAUDE.md"
  "$TEMPLATES_DIR/shared/cloudflare-tooling.md"
  "$TEMPLATES_DIR/shared/node-version"
  "$TEMPLATES_DIR/shared/dev.vars.example"
)
TEMPLATE_DESTINATIONS=(
  "$TARGET_DIR/biome.json"
  "$TARGET_DIR/.worktreeinclude"
  "$TARGET_DIR/CLAUDE.md"
  "$TARGET_DIR/.agents/rules/cloudflare-tooling.md"
  "$TARGET_DIR/.node-version"
  "$TARGET_DIR/.dev.vars.example"
)

case "$SCAFFOLD" in
  next-cloudflare)
    TAILWIND_CSS="$TARGET_DIR/src/app/globals.css"
    TEMPLATE_SOURCES+=(
      "$TEMPLATES_DIR/next-cloudflare/AGENTS.md"
      "$TEMPLATES_DIR/next-cloudflare/wrangler.jsonc.template"
      "$TEMPLATES_DIR/next-cloudflare/open-next.config.ts.template"
    )
    TEMPLATE_DESTINATIONS+=(
      "$TARGET_DIR/AGENTS.md"
      "$TARGET_DIR/wrangler.jsonc"
      "$TARGET_DIR/open-next.config.ts"
    )
    ;;
  astro-cloudflare)
    TAILWIND_CSS="$TARGET_DIR/src/styles/global.css"
    TEMPLATE_SOURCES+=(
      "$TEMPLATES_DIR/astro-cloudflare/AGENTS.md"
      "$TEMPLATES_DIR/astro-cloudflare/seo.md"
      "$TEMPLATES_DIR/astro-cloudflare/astro.config.mjs.template"
      "$TEMPLATES_DIR/astro-cloudflare/index.astro.template"
      "$TEMPLATES_DIR/astro-cloudflare/tsconfig.json.template"
      "$TEMPLATES_DIR/astro-cloudflare/wrangler.jsonc.template"
    )
    TEMPLATE_DESTINATIONS+=(
      "$TARGET_DIR/AGENTS.md"
      "$TARGET_DIR/.agents/rules/seo.md"
      "$TARGET_DIR/astro.config.mjs"
      "$TARGET_DIR/src/pages/index.astro"
      "$TARGET_DIR/tsconfig.json"
      "$TARGET_DIR/wrangler.jsonc"
    )
    ;;
esac

# Validate the entire write set before changing the generated project.
[[ -f "$SCRIPTS_TEMPLATE" && ! -L "$SCRIPTS_TEMPLATE" ]] || {
  echo "RESULT: error=source-missing path=$SCRIPTS_TEMPLATE" >&2
  exit 1
}
for index in "${!TEMPLATE_SOURCES[@]}"; do
  [[ -f "${TEMPLATE_SOURCES[$index]}" ]] || {
    echo "RESULT: error=source-missing path=${TEMPLATE_SOURCES[$index]}" >&2
    exit 1
  }
  assert_safe_destination "${TEMPLATE_DESTINATIONS[$index]}" || exit 1
done
[[ -f "$TEMPLATES_DIR/shared/gitignore" ]] || {
  echo "RESULT: error=source-missing path=$TEMPLATES_DIR/shared/gitignore" >&2
  exit 1
}
[[ -f "$TAILWIND_TEMPLATE" && ! -L "$TAILWIND_TEMPLATE" ]] || {
  echo "RESULT: error=source-missing path=$TAILWIND_TEMPLATE" >&2
  exit 1
}
assert_safe_destination "$TARGET_DIR/.gitignore" || exit 1
assert_safe_destination "$TAILWIND_CSS" || exit 1
assert_safe_destination "$PKG_JSON" || exit 1
[[ -f "$PKG_JSON" && ! -L "$PKG_JSON" ]] || {
  echo "RESULT: error=package-json-missing path=$PKG_JSON" >&2
  exit 1
}

if ! command -v jq >/dev/null 2>&1; then
  echo "error: jq required for package.json merge (https://jqlang.org/download/)" >&2
  echo "RESULT: error=jq-missing"
  exit 1
fi
if ! jq -e 'type == "object"' "$PKG_JSON" >/dev/null \
  || ! jq -e 'type == "object"' "$SCRIPTS_TEMPLATE" >/dev/null; then
  echo "error: package.json and scripts.json must contain JSON objects" >&2
  echo "RESULT: error=invalid-package-json"
  exit 1
fi

# write_file <source> <dest>
# Substitutes tokens, refuses overwrite unless --force.
write_file() {
  local src="$1"
  local dest="$2"

  prepare_destination "$dest" || return 1

  if [[ -e "$dest" ]] && [[ "$FORCE" != "--force" ]]; then
    echo "RESULT: skipped=$dest reason=exists"
    SKIPPED=$((SKIPPED + 1))
    return 0
  fi

  # Substitution order matters: longer tokens first to avoid partial matches.
  # `project-name.example` is left intact (astro site URL placeholder) — user
  # swaps the .example for their real domain after scaffold.
  ACTIVE_TEMP="$(mktemp "$(dirname "$dest")/.overlay.$(basename "$dest").XXXXXX")" || {
    echo "RESULT: error=temp-create-failed path=$dest" >&2
    return 1
  }
  if ! sed \
    -e "s|\[Project Name\]|$PROJECT_NAME|g" \
    -e "s|{project_name}|$PROJECT_SLUG|g" \
    -e "s|\"name\": \"project-name\"|\"name\": \"$PROJECT_SLUG\"|g" \
    "$src" >"$ACTIVE_TEMP"; then
    echo "RESULT: error=template-render-failed path=$dest" >&2
    return 1
  fi
  if ! mv -f "$ACTIVE_TEMP" "$dest"; then
    echo "RESULT: error=template-publish-failed path=$dest" >&2
    return 1
  fi
  ACTIVE_TEMP=""

  echo "RESULT: wrote=$dest"
  WRITTEN=$((WRITTEN + 1))
}

merge_gitignore() {
  local src="$1" dest="$2" line existing found
  prepare_destination "$dest" || return 1
  ACTIVE_TEMP="$(mktemp "$(dirname "$dest")/.overlay.$(basename "$dest").XXXXXX")" || {
    echo "RESULT: error=temp-create-failed path=$dest" >&2
    return 1
  }

  if [[ -f "$dest" ]]; then
    while IFS= read -r existing || [[ -n "$existing" ]]; do
      printf '%s\n' "$existing" >>"$ACTIVE_TEMP"
    done <"$dest"
  fi
  while IFS= read -r line || [[ -n "$line" ]]; do
    found=0
    if [[ -f "$dest" ]]; then
      while IFS= read -r existing || [[ -n "$existing" ]]; do
        if [[ "$existing" == "$line" ]]; then
          found=1
          break
        fi
      done <"$dest"
    fi
    if [[ "$found" -eq 0 ]]; then
      printf '%s\n' "$line" >>"$ACTIVE_TEMP"
    fi
  done <"$src"
  if ! mv -f "$ACTIVE_TEMP" "$dest"; then
    echo "RESULT: error=gitignore-publish-failed path=$dest" >&2
    return 1
  fi
  ACTIVE_TEMP=""
  echo "RESULT: merged-gitignore=$dest"
  WRITTEN=$((WRITTEN + 1))
}

ensure_tailwind_import() {
  local dest="$1"
  prepare_destination "$dest" || return 1
  if [[ -f "$dest" ]] \
    && grep -Eq "^[[:space:]]*@import[[:space:]]+['\"]tailwindcss['\"][[:space:]]*;" "$dest"; then
    echo "RESULT: kept-tailwind=$dest"
    return 0
  fi

  ACTIVE_TEMP="$(mktemp "$(dirname "$dest")/.overlay.$(basename "$dest").XXXXXX")" || {
    echo "RESULT: error=temp-create-failed path=$dest" >&2
    return 1
  }
  cat "$TAILWIND_TEMPLATE" >"$ACTIVE_TEMP"
  [[ ! -f "$dest" ]] || cat "$dest" >>"$ACTIVE_TEMP"
  if ! mv -f "$ACTIVE_TEMP" "$dest"; then
    echo "RESULT: error=tailwind-publish-failed path=$dest" >&2
    return 1
  fi
  ACTIVE_TEMP=""
  echo "RESULT: ensured-tailwind=$dest"
  WRITTEN=$((WRITTEN + 1))
}

for index in "${!TEMPLATE_SOURCES[@]}"; do
  write_file "${TEMPLATE_SOURCES[$index]}" "${TEMPLATE_DESTINATIONS[$index]}"
done
ensure_tailwind_import "$TAILWIND_CSS"
merge_gitignore "$TEMPLATES_DIR/shared/gitignore" "$TARGET_DIR/.gitignore"

prepare_destination "$PKG_JSON" || exit 1
ACTIVE_TEMP="$(mktemp "$TARGET_DIR/.package.json.XXXXXX")" || {
  echo "RESULT: error=package-temp-create-failed"
  exit 1
}
# Merge: our scripts override CLI defaults; preserve the validated npm name.
if ! jq --arg name "$PROJECT_NAME" --slurpfile new "$SCRIPTS_TEMPLATE" \
  '.name = $name | .scripts = ((.scripts // {}) + $new[0]) | .type = "module" | .private = true' \
  "$PKG_JSON" >"$ACTIVE_TEMP"; then
  echo "error: package.json merge failed" >&2
  echo "RESULT: error=package-merge-failed"
  exit 1
fi
if ! mv -f "$ACTIVE_TEMP" "$PKG_JSON"; then
  echo "error: merged package.json could not be published" >&2
  echo "RESULT: error=package-publish-failed"
  exit 1
fi
ACTIVE_TEMP=""
echo "RESULT: merged=$PKG_JSON"

echo "RESULT: written=$WRITTEN skipped=$SKIPPED scaffold=$SCAFFOLD"

if [[ "$SKIPPED" -gt 0 ]] && [[ "$FORCE" != "--force" ]]; then
  echo "RESULT: ok=partial hint=--force to overwrite"
  exit 1
fi

echo "RESULT: ok=true"
exit 0
