#!/usr/bin/env bash

DESIGNMD_COMMAND=()
DESIGNMD_WRAPPER=""
DESIGNMD_PROJECT_DIR=""
DESIGNMD_BINARY=""
DESIGNMD_YARN_BIN=""
DESIGNMD_INVALID_MANIFEST=""

designmd_valid_package_manifest() {
  python3 - "$1" <<'PY' >/dev/null 2>&1
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    package = json.load(handle)
if not isinstance(package, dict):
    raise SystemExit(1)
for field in (
    "dependencies",
    "devDependencies",
    "optionalDependencies",
    "peerDependencies",
):
    value = package.get(field)
    if value is not None and not isinstance(value, dict):
        raise SystemExit(1)
PY
}

designmd_format_command() {
  local argument escaped
  local rendered=()
  for argument in "$@"; do
    printf -v escaped '%q' "$argument"
    rendered+=("$escaped")
  done
  local IFS=' '
  printf '%s\n' "${rendered[*]}"
}

run_designmd() {
  [[ ${#DESIGNMD_COMMAND[@]} -gt 0 ]] || return 1
  "${DESIGNMD_COMMAND[@]}" "$@"
}

resolve_designmd() {
  local input="${1:-.}"
  local dir root candidate package_json parent declared=0 declared_dir=""
  local yarn_bin path_tool

  DESIGNMD_COMMAND=()
  DESIGNMD_WRAPPER=""
  DESIGNMD_PROJECT_DIR=""
  DESIGNMD_BINARY=""
  DESIGNMD_YARN_BIN=""
  DESIGNMD_INVALID_MANIFEST=""

  command -v python3 >/dev/null 2>&1 || return 71

  if [[ -d "$input" ]]; then
    dir="$input"
  else
    dir="$(dirname "$input")"
  fi
  dir="$(cd "$dir" 2>/dev/null && pwd -P)" || return 1
  root="$(designmd_workspace_root "$dir")" || return $?

  while :; do
    candidate="$dir/node_modules/.bin/designmd"
    package_json="$dir/package.json"
    if [[ -f "$package_json" ]] \
      && ! designmd_valid_package_manifest "$package_json"; then
      DESIGNMD_INVALID_MANIFEST="$package_json"
      return 74
    fi
    if [[ "$declared" -eq 0 && -f "$package_json" ]] \
      && python3 - "$package_json" <<'PY' >/dev/null 2>&1
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    package_json = json.load(handle)
declared = any(
    "@google/design.md" in (package_json.get(field) or {})
    for field in ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies")
)
raise SystemExit(0 if declared else 1)
PY
    then
      declared=1
      [[ -n "$declared_dir" ]] || declared_dir="$dir"
    fi
    if [[ "$declared" -eq 1 && -x "$candidate" ]]; then
      DESIGNMD_COMMAND=("$candidate")
      DESIGNMD_WRAPPER="project"
      DESIGNMD_PROJECT_DIR="$declared_dir"
      DESIGNMD_BINARY="$candidate"
      run_designmd --version >/dev/null 2>&1 || return 72
      return 0
    fi
    [[ "$dir" == "$root" ]] && break
    parent="$(dirname "$dir")"
    if [[ "$parent" == "$dir" ]] \
      || [[ "$parent" != "$root" && "$parent" != "$root/"* ]]; then
      break
    fi
    dir="$parent"
  done

  if [[ -n "$declared_dir" ]] \
    && [[ "$(designmd_package_manager "$declared_dir")" == "yarn" ]]; then
    yarn_bin="$(command -v yarn 2>/dev/null || true)"
    if [[ -n "$yarn_bin" ]] \
      && env COREPACK_ENABLE_NETWORK=0 COREPACK_DEFAULT_TO_LATEST=0 \
        "$yarn_bin" --cwd "$declared_dir" bin designmd >/dev/null 2>&1; then
      DESIGNMD_COMMAND=(
        env COREPACK_ENABLE_NETWORK=0 COREPACK_DEFAULT_TO_LATEST=0
        "$yarn_bin" --cwd "$declared_dir" run -B designmd
      )
      DESIGNMD_WRAPPER="yarn-pnp"
      DESIGNMD_PROJECT_DIR="$declared_dir"
      DESIGNMD_BINARY="$yarn_bin"
      DESIGNMD_YARN_BIN="$yarn_bin"
      run_designmd --version >/dev/null 2>&1 || return 72
      return 0
    fi
    return 73
  fi

  # A project declaration is authoritative. Falling back to an unrelated
  # global binary would silently change the validator version and invalidate
  # reproducibility when the local install is incomplete.
  [[ -z "$declared_dir" ]] || return 1

  path_tool="$(command -v designmd 2>/dev/null || true)"
  [[ -n "$path_tool" ]] || return 1
  DESIGNMD_COMMAND=("$path_tool")
  DESIGNMD_WRAPPER="path"
  DESIGNMD_BINARY="$path_tool"
  run_designmd --version >/dev/null 2>&1 || return 72
}

designmd_bundled_spec() {
  local destination="$1"
  if [[ "$DESIGNMD_WRAPPER" == "yarn-pnp" ]]; then
    env COREPACK_ENABLE_NETWORK=0 COREPACK_DEFAULT_TO_LATEST=0 \
      "$DESIGNMD_YARN_BIN" --cwd "$DESIGNMD_PROJECT_DIR" node - "$destination" <<'JS'
const fs = require("fs");
const path = require("path");

const destination = process.argv[2];
let current = path.dirname(require.resolve("@google/design.md"));
while (true) {
  const packageJson = path.join(current, "package.json");
  if (fs.existsSync(packageJson)) {
    const packageData = JSON.parse(fs.readFileSync(packageJson, "utf8"));
    if (packageData.name === "@google/design.md") {
      for (const relative of ["dist/spec.md", "dist/linter/spec.md"]) {
        const artifact = path.join(current, relative);
        if (fs.existsSync(artifact)) {
          fs.copyFileSync(artifact, destination);
          process.exit(0);
        }
      }
      process.exit(1);
    }
  }
  const parent = path.dirname(current);
  if (parent === current) process.exit(1);
  current = parent;
}
JS
    return $?
  fi

  python3 - "$DESIGNMD_BINARY" "$destination" <<'PY'
import json
from pathlib import Path
import re
import shutil
import sys

binary = Path(sys.argv[1]).expanduser()
destination = Path(sys.argv[2])
candidates = []
try:
    candidates.append(binary.resolve())
except OSError:
    pass
try:
    shim = binary.read_text(encoding="utf-8", errors="replace")
except OSError:
    shim = ""
match = re.search(r"^# cmd-shim-target=(.+)$", shim, re.MULTILINE)
if match:
    target = Path(match.group(1).strip())
    if not target.is_absolute():
        target = binary.parent / target
    candidates.append(target.resolve())

seen = set()
for candidate in candidates:
    for parent in (candidate.parent, *candidate.parents):
        if parent in seen:
            continue
        seen.add(parent)
        package_json = parent / "package.json"
        try:
            package = json.loads(package_json.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if package.get("name") != "@google/design.md":
            continue
        for relative in ("dist/spec.md", "dist/linter/spec.md"):
            artifact = parent / relative
            if artifact.is_file():
                shutil.copyfile(artifact, destination)
                raise SystemExit(0)
raise SystemExit(1)
PY
}

designmd_workspace_root() {
  local input="${1:-.}" dir configured git_root current fallback=""
  if [[ -d "$input" ]]; then
    dir="$input"
  else
    dir="$(dirname "$input")"
  fi
  dir="$(cd "$dir" 2>/dev/null && pwd -P)" || return 1

  configured="${DESIGNMD_WORKSPACE_ROOT:-}"
  if [[ -n "$configured" ]]; then
    configured="$(cd "$configured" 2>/dev/null && pwd -P)" || return 1
    case "$dir" in
      "$configured"|"$configured"/*) printf '%s\n' "$configured"; return 0 ;;
      *) return 70 ;;
    esac
  fi

  git_root="$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null || true)"
  if [[ -n "$git_root" ]]; then
    printf '%s\n' "$git_root"
    return 0
  fi

  current="$dir"
  while :; do
    if [[ -z "$fallback" && -f "$current/package.json" ]]; then
      fallback="$current"
    fi
    if [[ -f "$current/pnpm-workspace.yaml" \
      || -f "$current/pnpm-lock.yaml" \
      || -f "$current/yarn.lock" \
      || -f "$current/package-lock.json" \
      || -f "$current/bun.lock" \
      || -f "$current/bun.lockb" ]]; then
      printf '%s\n' "$current"
      return 0
    fi
    if [[ -f "$current/package.json" ]] \
      && python3 - "$current/package.json" <<'PY' >/dev/null 2>&1
import json
import sys

try:
    with open(sys.argv[1], encoding="utf-8") as handle:
        package = json.load(handle)
except (OSError, json.JSONDecodeError):
    raise SystemExit(1)
raise SystemExit(0 if package.get("workspaces") else 1)
PY
    then
      printf '%s\n' "$current"
      return 0
    fi
    [[ "$current" == "/" ]] && break
    current="$(dirname "$current")"
  done
  printf '%s\n' "${fallback:-$dir}"
}

designmd_package_manager() {
  local input="${1:-.}"
  local dir root parent declared

  if [[ -d "$input" ]]; then
    dir="$input"
  else
    dir="$(dirname "$input")"
  fi
  dir="$(cd "$dir" 2>/dev/null && pwd -P)" || {
    printf 'npm\n'
    return 0
  }
  root="$(designmd_workspace_root "$dir")" || {
    printf 'npm\n'
    return 0
  }

  while :; do
    if [[ -f "$dir/package.json" ]]; then
      declared="$(python3 - "$dir/package.json" <<'PY' 2>/dev/null || true
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
      case "$declared" in
        npm|pnpm|yarn|bun) printf '%s\n' "$declared"; return 0 ;;
      esac
    fi
    if [[ -f "$dir/pnpm-lock.yaml" ]]; then
      printf 'pnpm\n'; return 0
    elif [[ -f "$dir/yarn.lock" ]]; then
      printf 'yarn\n'; return 0
    elif [[ -f "$dir/bun.lock" || -f "$dir/bun.lockb" ]]; then
      printf 'bun\n'; return 0
    elif [[ -f "$dir/package-lock.json" || -f "$dir/npm-shrinkwrap.json" ]]; then
      printf 'npm\n'; return 0
    fi
    [[ "$dir" == "$root" ]] && break
    parent="$(dirname "$dir")"
    if [[ "$parent" == "$dir" ]] \
      || [[ "$parent" != "$root" && "$parent" != "$root/"* ]]; then
      break
    fi
    dir="$parent"
  done
  printf 'npm\n'
}

emit_designmd_metadata() {
  local version descriptor
  version="$(run_designmd --version 2>/dev/null | sed -n '1p' || true)"
  [[ -n "$version" ]] || version="unknown"
  descriptor="$(designmd_format_command "${DESIGNMD_COMMAND[@]}")"
  echo "RESULT: cli=$descriptor"
  echo "RESULT: cli-wrapper=$DESIGNMD_WRAPPER"
  echo "RESULT: cli-version=$version"
}

designmd_install_command() {
  case "$(designmd_package_manager "${1:-.}")" in
    pnpm)
      if [[ -f "$(designmd_workspace_root "${1:-.}")/pnpm-workspace.yaml" ]]; then
        printf 'pnpm add -Dw @google/design.md\n'
      else
        printf 'pnpm add -D @google/design.md\n'
      fi
      ;;
    yarn) printf 'yarn add -D @google/design.md\n' ;;
    bun) printf 'bun add -d @google/design.md\n' ;;
    npm|*) printf 'npm install --save-dev @google/design.md\n' ;;
  esac
}

designmd_yarn_repair_command() {
  local input="${1:-.}" dir package_manager version
  if [[ -d "$input" ]]; then
    dir="$input"
  else
    dir="$(dirname "$input")"
  fi
  dir="$(cd "$dir" 2>/dev/null && pwd -P)" || dir="."
  while [[ "$dir" != "/" ]]; do
    if [[ -f "$dir/package.json" ]]; then
      package_manager="$(python3 - "$dir/package.json" <<'PY' 2>/dev/null || true
import json
import sys

try:
    with open(sys.argv[1], encoding="utf-8") as handle:
        package = json.load(handle)
except (OSError, json.JSONDecodeError):
    raise SystemExit(0)
value = package.get("packageManager")
if isinstance(value, str) and value.startswith("yarn@"):
    print(value)
PY
)"
      if [[ -n "$package_manager" ]]; then
        version="${package_manager#yarn@}"
        printf 'corepack enable && corepack install --global yarn@%s && yarn --cwd %q install --immutable\n' \
          "$version" "$dir"
        return 0
      fi
    fi
    dir="$(dirname "$dir")"
  done
  printf 'corepack enable && yarn install --immutable\n'
}

emit_designmd_missing() {
  local input="${1:-.}" rerun="${2:-}" command
  command="$(designmd_install_command "$input")"
  echo "RESULT: status=designmd-missing"
  echo "RESULT: install=$command"
  [[ -z "$rerun" ]] || echo "RESULT: rerun=$rerun"
  echo "RESULT: remediation=Run the install command, then run the exact rerun command"
}

emit_designmd_resolution_error() {
  local input="${1:-.}" status="${2:-1}" rerun="${3:-}" command
  case "$status" in
    70)
      echo "RESULT: status=outside-workspace"
      echo "RESULT: path=$input"
      echo "RESULT: remediation=Use a target inside DESIGNMD_WORKSPACE_ROOT or correct that environment variable"
      ;;
    71)
      echo "RESULT: status=python3-missing"
      echo "RESULT: install=Install Python 3 from https://www.python.org/downloads/ or your system package manager"
      [[ -z "$rerun" ]] || echo "RESULT: rerun=$rerun"
      echo "RESULT: remediation=Install Python 3, then run the exact rerun command"
      ;;
    72)
      command="$(designmd_install_command "$input")"
      echo "RESULT: status=designmd-unsupported"
      echo "RESULT: install=$command"
      [[ -z "$rerun" ]] || echo "RESULT: rerun=$rerun"
      echo "RESULT: remediation=Upgrade or repair the declared designmd binary, then run the exact rerun command"
      ;;
    73)
      command="$(designmd_yarn_repair_command "$input")"
      echo "RESULT: status=yarn-runtime-unavailable"
      echo "RESULT: install=$command"
      [[ -z "$rerun" ]] || echo "RESULT: rerun=$rerun"
      echo "RESULT: remediation=Provision the pinned Yarn runtime and declared dependencies, then run the exact rerun command"
      ;;
    74)
      echo "RESULT: status=invalid-project-manifest"
      echo "RESULT: path=$DESIGNMD_INVALID_MANIFEST"
      [[ -z "$rerun" ]] || echo "RESULT: rerun=$rerun"
      echo "RESULT: remediation=Repair package.json so it is valid JSON with object dependency maps, then run the exact rerun command"
      ;;
    *) emit_designmd_missing "$input" "$rerun" ;;
  esac
}

emit_designmd_runtime_repair() {
  local input="${1:-.}" rerun="${2:-}" command
  command="$(designmd_install_command "$input")"
  echo "RESULT: install=$command"
  [[ -z "$rerun" ]] || echo "RESULT: rerun=$rerun"
  echo "RESULT: remediation=Repair or upgrade the declared designmd package, then run the exact rerun command"
}
