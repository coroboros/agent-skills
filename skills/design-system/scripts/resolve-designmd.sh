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

designmd_absolute_file() {
  local input="$1" parent leaf
  parent="$(dirname "$input")"
  leaf="$(basename "$input")"
  parent="$(cd "$parent" 2>/dev/null && pwd -P)" || return 1
  printf '%s/%s\n' "$parent" "$leaf"
}

run_designmd() {
  [[ ${#DESIGNMD_COMMAND[@]} -gt 0 ]] || return 1
  "${DESIGNMD_COMMAND[@]}" "$@"
}

designmd_project_origin() {
  local start="$1"
  local root="$2"
  local current="$start"
  local parent

  while :; do
    if [[ -f "$current/package.json" ]]; then
      printf '%s\n' "$current"
      return 0
    fi
    [[ "$current" == "$root" ]] && break
    parent="$(dirname "$current")"
    if [[ "$parent" == "$current" ]] \
      || [[ "$parent" != "$root" && "$parent" != "$root/"* ]]; then
      break
    fi
    current="$parent"
  done
  printf '%s\n' "$start"
}

resolve_designmd() {
  local input="${1:-.}"
  local dir root origin candidate package_json parent declared=0 declared_dir=""
  local eligible
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
  origin="$(designmd_project_origin "$dir" "$root")"

  while :; do
    eligible=1
    if [[ "$dir" != "$origin" ]] \
      && ! designmd_workspace_contains "$origin" "$dir"; then
      eligible=0
    fi
    candidate="$dir/node_modules/.bin/designmd"
    package_json="$dir/package.json"
    if [[ "$eligible" -eq 1 && -f "$package_json" ]] \
      && ! designmd_valid_package_manifest "$package_json"; then
      DESIGNMD_INVALID_MANIFEST="$package_json"
      return 74
    fi
    if [[ "$eligible" -eq 1 && "$declared" -eq 0 && -f "$package_json" ]] \
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
      if [[ -z "$declared_dir" ]]; then
        declared_dir="$dir"
        DESIGNMD_PROJECT_DIR="$declared_dir"
      fi
    fi
    if [[ "$eligible" -eq 1 && "$declared" -eq 1 && -x "$candidate" ]] \
      && { [[ "$dir" == "$declared_dir" ]] \
        || designmd_workspace_contains "$declared_dir" "$dir"; }; then
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
      && env COREPACK_ENABLE_NETWORK=0 COREPACK_DEFAULT_TO_LATEST=0 YARN_ENABLE_NETWORK=0 \
        "$yarn_bin" --cwd "$declared_dir" bin designmd >/dev/null 2>&1; then
      DESIGNMD_COMMAND=(
        env COREPACK_ENABLE_NETWORK=0 COREPACK_DEFAULT_TO_LATEST=0 YARN_ENABLE_NETWORK=0
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
    env COREPACK_ENABLE_NETWORK=0 COREPACK_DEFAULT_TO_LATEST=0 YARN_ENABLE_NETWORK=0 \
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
  local dir root parent declared origin eligible

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
  origin="$(designmd_project_origin "$dir" "$root")"

  while :; do
    eligible=1
    if [[ "$dir" != "$origin" ]] \
      && ! designmd_workspace_contains "$origin" "$dir"; then
      eligible=0
    fi
    if [[ "$eligible" -eq 1 && -f "$dir/package.json" ]]; then
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
    if [[ "$eligible" -eq 1 && -f "$dir/pnpm-lock.yaml" ]]; then
      printf 'pnpm\n'; return 0
    elif [[ "$eligible" -eq 1 && -f "$dir/yarn.lock" ]]; then
      printf 'yarn\n'; return 0
    elif [[ "$eligible" -eq 1 && ( -f "$dir/bun.lock" || -f "$dir/bun.lockb" ) ]]; then
      printf 'bun\n'; return 0
    elif [[ "$eligible" -eq 1 && ( -f "$dir/package-lock.json" || -f "$dir/npm-shrinkwrap.json" ) ]]; then
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

designmd_workspace_contains() {
  local child="$1"
  local workspace="$2"
  [[ "$child" == "$workspace" ]] && return 0
  python3 - "$child" "$workspace" <<'PY' >/dev/null 2>&1
import json
from pathlib import Path
import re
import sys

child = Path(sys.argv[1]).resolve()
workspace = Path(sys.argv[2]).resolve()
try:
    relative = child.relative_to(workspace).as_posix()
except ValueError:
    raise SystemExit(1)

def normalize_pattern(value):
    if not isinstance(value, str):
        raise ValueError("workspace pattern must be a string")
    value = value.strip()
    excluded = value.startswith("!")
    if excluded:
        value = value[1:]
    while value.startswith("./"):
        value = value[2:]
    value = value.rstrip("/")
    parts = value.split("/")
    if (
        not value
        or value.startswith("/")
        or "\\" in value
        or "\x00" in value
        or any(part in {"", ".", ".."} for part in parts)
        or any(character in value for character in "?[]{}")
        or any("**" in part and part != "**" for part in parts)
    ):
        raise ValueError("unsupported or unsafe workspace pattern")
    return excluded, value


def pattern_matches(path, pattern):
    translated = ["^"]
    index = 0
    while index < len(pattern):
        if pattern.startswith("**/", index):
            translated.append("(?:[^/]+/)*")
            index += 3
        elif pattern.startswith("**", index):
            translated.append(".*")
            index += 2
        elif pattern[index] == "*":
            translated.append("[^/]*")
            index += 1
        else:
            translated.append(re.escape(pattern[index]))
            index += 1
    translated.append("$")
    return re.fullmatch("".join(translated), path) is not None


def package_workspace_patterns():
    manifest = workspace / "package.json"
    if not manifest.is_file():
        return []
    package = json.loads(manifest.read_text(encoding="utf-8"))
    workspaces = package.get("workspaces")
    if workspaces is None:
        return []
    if isinstance(workspaces, list):
        return workspaces
    if isinstance(workspaces, dict) and isinstance(workspaces.get("packages"), list):
        return workspaces["packages"]
    raise ValueError("unsupported package.json workspaces field")


def yaml_scalar(value):
    value = value.strip()
    if value.startswith("'"):
        match = re.fullmatch(r"'((?:[^']|'')*)'\s*(?:#.*)?", value)
        if not match:
            raise ValueError("unsupported single-quoted YAML scalar")
        return match.group(1).replace("''", "'")
    if value.startswith('"'):
        match = re.fullmatch(r'("(?:[^"\\]|\\.)*")\s*(?:#.*)?', value)
        if not match:
            raise ValueError("unsupported double-quoted YAML scalar")
        return json.loads(match.group(1))
    return re.split(r"\s+#", value, maxsplit=1)[0].strip()


def pnpm_workspace_patterns():
    manifest = workspace / "pnpm-workspace.yaml"
    if not manifest.is_file():
        return []
    patterns = []
    in_packages = False
    for raw_line in manifest.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indentation = len(raw_line) - len(raw_line.lstrip())
        if not in_packages:
            if indentation == 0 and re.fullmatch(r"packages\s*:\s*(?:#.*)?", stripped):
                in_packages = True
            continue
        if indentation == 0:
            break
        match = re.fullmatch(r"\s*-\s*(.+)", raw_line)
        if not match:
            raise ValueError("unsupported pnpm packages block")
        patterns.append(yaml_scalar(match.group(1)))
    return patterns


try:
    patterns = [
        normalize_pattern(pattern)
        for pattern in package_workspace_patterns() + pnpm_workspace_patterns()
    ]
except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
    raise SystemExit(1)

included = any(
    not excluded and pattern_matches(relative, pattern)
    for excluded, pattern in patterns
)
excluded = any(
    excluded and pattern_matches(relative, pattern)
    for excluded, pattern in patterns
)
if included and not excluded:
    raise SystemExit(0)

for name in ("package-lock.json", "npm-shrinkwrap.json"):
    try:
        lock = json.loads((workspace / name).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        continue
    packages = lock.get("packages")
    if isinstance(packages, dict) and relative in packages:
        raise SystemExit(0)
raise SystemExit(1)
PY
}

designmd_yarn_restore_command() {
  local dir="$1"
  local command_prefix="${2:-}"
  local lock_root quoted_dir quoted_lock

  lock_root="$(designmd_workspace_root "$dir")" || lock_root="$dir"
  if [[ "$lock_root" != "$dir" ]] \
    && ! designmd_workspace_contains "$dir" "$lock_root"; then
    lock_root="$dir"
  fi
  printf -v quoted_dir '%q' "$dir"
  if [[ -f "$lock_root/yarn.lock" ]]; then
    printf '%syarn --cwd %s install --immutable\n' "$command_prefix" "$quoted_dir"
  else
    printf -v quoted_lock '%q' "$lock_root/yarn.lock"
    printf 'Restore %s from version control (or create and review it deliberately), then run %syarn --cwd %s install --immutable\n' \
      "$quoted_lock" "$command_prefix" "$quoted_dir"
  fi
}

designmd_restore_command() {
  local dir="${DESIGNMD_PROJECT_DIR:-${1:-.}}"
  local lock_root install_dir quoted_dir

  lock_root="$(designmd_workspace_root "$dir")" || lock_root="$dir"
  if [[ "$lock_root" != "$dir" ]] \
    && ! designmd_workspace_contains "$dir" "$lock_root"; then
    lock_root="$dir"
  fi
  case "$(designmd_package_manager "$dir")" in
    pnpm)
      printf -v quoted_dir '%q' "$dir"
      if [[ -f "$lock_root/pnpm-lock.yaml" ]]; then
        printf 'pnpm --dir %s install --frozen-lockfile\n' "$quoted_dir"
      else
        printf 'pnpm --dir %s install\n' "$quoted_dir"
      fi
      ;;
    yarn) designmd_yarn_restore_command "$dir" ;;
    bun)
      printf -v quoted_dir '%q' "$dir"
      if [[ -f "$lock_root/bun.lock" || -f "$lock_root/bun.lockb" ]]; then
        printf 'bun --cwd %s install --frozen-lockfile\n' "$quoted_dir"
      else
        printf 'bun --cwd %s install\n' "$quoted_dir"
      fi
      ;;
    npm|*)
      install_dir="$dir"
      if [[ -f "$lock_root/package-lock.json" || -f "$lock_root/npm-shrinkwrap.json" ]] \
        && designmd_workspace_contains "$dir" "$lock_root"; then
        install_dir="$lock_root"
      fi
      printf -v quoted_dir '%q' "$install_dir"
      if [[ -f "$install_dir/package-lock.json" || -f "$install_dir/npm-shrinkwrap.json" ]]; then
        printf 'npm --prefix %s ci\n' "$quoted_dir"
      else
        printf 'npm --prefix %s install\n' "$quoted_dir"
      fi
      ;;
  esac
}

designmd_install_command() {
  local input="${1:-.}"
  local dir root origin quoted_origin

  if [[ -n "$DESIGNMD_PROJECT_DIR" ]]; then
    designmd_restore_command "$input"
    return 0
  fi

  if [[ -d "$input" ]]; then
    dir="$input"
  else
    dir="$(dirname "$input")"
  fi
  dir="$(cd "$dir" 2>/dev/null && pwd -P)" || {
    printf 'Resolve the governing project directory, then add @google/design.md as a reviewed development dependency\n'
    return 0
  }
  root="$(designmd_workspace_root "$dir")" || root="$dir"
  origin="$(designmd_project_origin "$dir" "$root")"
  printf -v quoted_origin '%q' "$origin"

  case "$(designmd_package_manager "$origin")" in
    pnpm)
      if [[ "$origin" == "$root" && -f "$root/pnpm-workspace.yaml" ]]; then
        printf 'pnpm --dir %s add -Dw @google/design.md\n' "$quoted_origin"
      else
        printf 'pnpm --dir %s add -D @google/design.md\n' "$quoted_origin"
      fi
      ;;
    yarn) printf 'yarn --cwd %s add -D @google/design.md\n' "$quoted_origin" ;;
    bun) printf 'bun --cwd %s add -d @google/design.md\n' "$quoted_origin" ;;
    npm|*) printf 'npm --prefix %s install --save-dev @google/design.md\n' "$quoted_origin" ;;
  esac
}

designmd_yarn_repair_command() {
  local input="${1:-.}" dir root origin parent eligible package_manager version
  local quoted_version quoted_manifest quoted_dir
  if [[ -d "$input" ]]; then
    dir="$input"
  else
    dir="$(dirname "$input")"
  fi
  dir="$(cd "$dir" 2>/dev/null && pwd -P)" || {
    printf 'Resolve the governing project directory, add and review an explicit packageManager Yarn pin, then run corepack enable and an immutable Yarn install\n'
    return 0
  }
  root="$(designmd_workspace_root "$dir")" || root="$dir"
  origin="$(designmd_project_origin "$dir" "$root")"
  while :; do
    eligible=1
    if [[ "$dir" != "$origin" ]] \
      && ! designmd_workspace_contains "$origin" "$dir"; then
      eligible=0
    fi
    if [[ "$eligible" -eq 1 && -f "$dir/package.json" ]]; then
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
        printf -v quoted_version '%q' "$version"
        designmd_yarn_restore_command "$origin" \
          "corepack enable && corepack install --global yarn@$quoted_version && "
        return 0
      fi
    fi
    [[ "$dir" == "$root" ]] && break
    parent="$(dirname "$dir")"
    if [[ "$parent" == "$dir" ]] \
      || [[ "$parent" != "$root" && "$parent" != "$root/"* ]]; then
      break
    fi
    dir="$parent"
  done
  printf -v quoted_manifest '%q' "$origin/package.json"
  printf -v quoted_dir '%q' "$origin"
  printf 'Add and review an explicit "packageManager": "yarn@<reviewed-version>" pin in %s, then run corepack enable && corepack install --global yarn@<reviewed-version> && yarn --cwd %s install --immutable\n' \
    "$quoted_manifest" "$quoted_dir"
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
      echo "RESULT: remediation=Add and review a governing Yarn pin when absent, provision that runtime and the declared dependencies, then run the exact rerun command"
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
