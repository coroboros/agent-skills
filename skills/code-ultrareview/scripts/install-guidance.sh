#!/usr/bin/env bash

validate_review_scope() {
  python3 - "$1" <<'PY'
import json
from pathlib import PurePosixPath
import sys

path = sys.argv[1]
try:
    with open(path, encoding="utf-8") as handle:
        scope = json.load(handle)
except (OSError, json.JSONDecodeError) as exc:
    print(f"scope.json is not valid JSON: {exc}")
    raise SystemExit(1)

if not isinstance(scope, dict):
    print("scope.json must contain an object")
    raise SystemExit(1)

repo_kind = scope.get("repo_kind")
if not isinstance(repo_kind, str) or not repo_kind:
    print("scope.json repo_kind must be a non-empty string")
    raise SystemExit(1)

for field in ("languages", "files_touched_list"):
    value = scope.get(field)
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item for item in value
    ):
        print(f"scope.json {field} must be a list of non-empty strings")
        raise SystemExit(1)

for relative in scope["files_touched_list"]:
    candidate = PurePosixPath(relative)
    if candidate.is_absolute() or ".." in candidate.parts or "\x00" in relative:
        print(f"scope.json contains an unsafe repository path: {relative!r}")
        raise SystemExit(1)

line_ranges = scope.get("changed_line_ranges")
if line_ranges is not None:
    if not isinstance(line_ranges, dict):
        print("scope.json changed_line_ranges must be an object when present")
        raise SystemExit(1)
    touched = set(scope["files_touched_list"])
    for relative, ranges in line_ranges.items():
        candidate = PurePosixPath(relative) if isinstance(relative, str) else None
        if (
            candidate is None
            or not relative
            or candidate.is_absolute()
            or ".." in candidate.parts
            or "\x00" in relative
            or relative not in touched
        ):
            print(f"scope.json changed_line_ranges has an unsafe path: {relative!r}")
            raise SystemExit(1)
        if not isinstance(ranges, list):
            print(f"scope.json changed_line_ranges[{relative!r}] must be a list")
            raise SystemExit(1)
        for item in ranges:
            if (
                not isinstance(item, list)
                or len(item) != 2
                or not all(type(value) is int and value > 0 for value in item)
                or item[0] > item[1]
            ):
                print(
                    f"scope.json changed_line_ranges[{relative!r}] must contain "
                    "positive [start, end] pairs"
                )
                raise SystemExit(1)

for field in (
    "tool_coverage",
    "axis_coverage",
    "validator_coverage",
    "build_coverage",
    "mutation_coverage",
    "reconcile_coverage",
):
    value = scope.get(field)
    if value is not None and not isinstance(value, dict):
        print(f"scope.json {field} must be an object when present")
        raise SystemExit(1)
PY
}

validate_package_manifest() {
  python3 - "$1" <<'PY'
import json
import sys

path = sys.argv[1]
try:
    with open(path, encoding="utf-8") as handle:
        package = json.load(handle)
except (OSError, json.JSONDecodeError) as exc:
    print(f"package.json is not valid JSON: {exc}")
    raise SystemExit(1)
if not isinstance(package, dict):
    print("package.json must contain an object")
    raise SystemExit(1)
for field in (
    "dependencies",
    "devDependencies",
    "optionalDependencies",
    "peerDependencies",
):
    value = package.get(field)
    if value is not None and not isinstance(value, dict):
        print(f"package.json {field} must be an object")
        raise SystemExit(1)
PY
}

detect_js_package_manager() {
  local repo="${1:-.}"
  local declared=""

  if [[ -f "$repo/package.json" ]]; then
    declared="$(python3 - "$repo/package.json" <<'PY' 2>/dev/null || true
import json
import sys

try:
    with open(sys.argv[1], encoding="utf-8") as handle:
        package_json = json.load(handle)
except (OSError, json.JSONDecodeError):
    raise SystemExit(0)

value = package_json.get("packageManager")
if isinstance(value, str):
    print(value.split("@", 1)[0])
PY
)"
  fi

  case "$declared" in
    pnpm|yarn|bun|npm) printf '%s\n' "$declared"; return 0 ;;
  esac

  if [[ -f "$repo/pnpm-lock.yaml" ]]; then
    printf 'pnpm\n'
  elif [[ -f "$repo/yarn.lock" ]]; then
    printf 'yarn\n'
  elif [[ -f "$repo/bun.lock" || -f "$repo/bun.lockb" ]]; then
    printf 'bun\n'
  else
    printf 'npm\n'
  fi
}

js_dev_install_command() {
  local repo="$1"
  local package="$2"

  case "$(detect_js_package_manager "$repo")" in
    pnpm)
      if [[ -f "$repo/pnpm-workspace.yaml" ]]; then
        printf 'pnpm add -Dw %s\n' "$package"
      else
        printf 'pnpm add -D %s\n' "$package"
      fi
      ;;
    yarn) printf 'yarn add -D %s\n' "$package" ;;
    bun) printf 'bun add -d %s\n' "$package" ;;
    npm|*) printf 'npm install --save-dev %s\n' "$package" ;;
  esac
}

js_exec_command() {
  local repo="$1"
  local binary="$2"
  local prefix="./node_modules/.bin"

  if [[ "$(detect_js_package_manager "$repo")" == "yarn" ]]; then
    printf 'yarn run -B %s\n' "$binary"
    return 0
  fi

  # This command is remediation shown after the package has been declared and
  # installed. Calling the binary directly avoids every package-manager
  # fallback that could resolve or download a missing package at execution.
  [[ "$repo" != "." ]] && prefix="$repo/node_modules/.bin"
  printf '%q\n' "$prefix/$binary"
}

tool_install_command() {
  local repo="$1"
  local tool="$2"

  case "$tool" in
    knip) js_dev_install_command "$repo" knip ;;
    jscpd) js_dev_install_command "$repo" jscpd ;;
    markdownlint-cli2) js_dev_install_command "$repo" markdownlint-cli2 ;;
    api-extractor) js_dev_install_command "$repo" @microsoft/api-extractor ;;
    stryker) js_dev_install_command "$repo" @stryker-mutator/core ;;
    lizard) printf 'pipx install lizard\n' ;;
    vulture) printf 'pipx install vulture\n' ;;
    semgrep) printf 'pipx install semgrep\n' ;;
    mutmut) printf 'pipx install mutmut\n' ;;
    vale)
      if command -v brew >/dev/null 2>&1; then
        printf 'brew install vale\n'
      else
        printf 'go install github.com/errata-ai/vale/v3/cmd/vale@latest\n'
      fi
      ;;
    oasdiff)
      if command -v brew >/dev/null 2>&1; then
        printf 'brew install oasdiff\n'
      else
        printf 'go install github.com/oasdiff/oasdiff@latest\n'
      fi
      ;;
    atlas)
      if command -v brew >/dev/null 2>&1; then
        printf 'brew install ariga/tap/atlas\n'
      else
        printf 'go install ariga.io/atlas/cmd/atlas@latest\n'
      fi
      ;;
    deadcode) printf 'go install golang.org/x/tools/cmd/deadcode@latest\n' ;;
    gocyclo) printf 'go install github.com/fzipp/gocyclo/cmd/gocyclo@latest\n' ;;
    dupl) printf 'go install github.com/mibk/dupl@latest\n' ;;
    cargo-machete) printf 'cargo install --locked cargo-machete\n' ;;
    mvn)
      if command -v brew >/dev/null 2>&1; then
        printf 'brew install maven\n'
      elif command -v apt-get >/dev/null 2>&1; then
        printf 'Ask an administrator to install Debian package maven; official guide: https://maven.apache.org/install.html\n'
      else
        printf 'Install Maven from https://maven.apache.org/install.html\n'
      fi
      ;;
    *) printf 'Install %s from its official distribution\n' "$tool" ;;
  esac
}
