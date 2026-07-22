#!/usr/bin/env bash
# shellcheck disable=SC2034 # Output globals are consumed by sourcing scripts.

PROJECT_SLUG=""
PROJECT_NAME_ERROR=""
TARGET_NAME_ERROR=""

is_valid_unscoped_package_name() {
  local package_name="$1"

  [[ ${#package_name} -le 214 ]] \
    && [[ "$package_name" =~ ^[a-z0-9][a-z0-9._-]*$ ]] \
    && [[ "$package_name" != "node_modules" ]] \
    && [[ "$package_name" != "favicon.ico" ]]
}

validate_project_name() {
  local project_name="$1" package_name

  PROJECT_SLUG=""
  PROJECT_NAME_ERROR=""
  if [[ ${#project_name} -gt 214 ]] \
    || { ! is_valid_unscoped_package_name "$project_name" \
      && [[ ! "$project_name" =~ ^@[a-z0-9][a-z0-9._-]*/[a-z0-9][a-z0-9._-]*$ ]]; }; then
    PROJECT_NAME_ERROR="invalid-project-name"
    return 1
  fi

  package_name="${project_name##*/}"
  case "$package_name" in
    node_modules|favicon.ico)
      PROJECT_NAME_ERROR="invalid-project-name"
      return 1
      ;;
  esac

  PROJECT_SLUG="${project_name#@}"
  PROJECT_SLUG="${PROJECT_SLUG//\//-}"
  PROJECT_SLUG="${PROJECT_SLUG//[._]/-}"
  if [[ ${#PROJECT_SLUG} -gt 63 ]] \
    || [[ ! "$PROJECT_SLUG" =~ ^[a-z0-9]([a-z0-9-]*[a-z0-9])?$ ]]; then
    PROJECT_NAME_ERROR="invalid-cloudflare-service-name"
    return 1
  fi
}

validate_target_basename() {
  TARGET_NAME_ERROR=""
  if ! is_valid_unscoped_package_name "$1"; then
    TARGET_NAME_ERROR="invalid-target-name"
    return 1
  fi
}
