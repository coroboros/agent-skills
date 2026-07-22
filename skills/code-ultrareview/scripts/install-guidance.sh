#!/usr/bin/env bash
# shellcheck disable=SC2034 # Output globals are consumed by sourcing scripts.

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
    if (
        candidate.is_absolute()
        or ".." in candidate.parts
        or any(ord(character) < 32 for character in relative)
    ):
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

JS_RELEVANT_FILES=()
JS_DECLARATION_DIR=""
JS_DECLARATION_DIRS=()
JS_UNCOVERED_FILES=()
JS_DECLARATION_STATE="none"
JS_PACKAGE_MANAGER=""
JS_PACKAGE_MANAGER_ROOT=""

js_relevant_package_manifests() {
  local repo="$1"
  python3 - "$repo" ${JS_RELEVANT_FILES[@]+"${JS_RELEVANT_FILES[@]}"} <<'PY'
from pathlib import Path, PurePosixPath
import sys

repo = Path(sys.argv[1]).resolve()
manifests = []

def add(path):
    if path.is_file() and path not in manifests:
        manifests.append(path)

add(repo / "package.json")
for relative in sys.argv[2:]:
    candidate = PurePosixPath(relative)
    current = (repo / Path(*candidate.parts)).parent
    while current == repo or repo in current.parents:
        add(current / "package.json")
        if current == repo:
            break
        current = current.parent

for manifest in manifests:
    print(manifest)
PY
}

validate_relevant_package_manifests() {
  local repo="$1" manifest error
  while IFS= read -r manifest; do
    [[ -n "$manifest" ]] || continue
    if ! error="$(validate_package_manifest "$manifest")"; then
      printf '%s: %s\n' "$manifest" "$error"
      return 1
    fi
  done < <(js_relevant_package_manifests "$repo")
}

js_declaration_dirs() {
  local repo="$1"
  local package="$2"
  python3 - "$repo" "$package" ${JS_RELEVANT_FILES[@]+"${JS_RELEVANT_FILES[@]}"} <<'PY'
import json
from pathlib import Path, PurePosixPath
import sys

repo = Path(sys.argv[1]).resolve()
package_name = sys.argv[2]
dependency_fields = (
    "dependencies",
    "devDependencies",
    "optionalDependencies",
    "peerDependencies",
)

def declares(directory):
    manifest = directory / "package.json"
    if not manifest.is_file():
        return False
    with manifest.open(encoding="utf-8") as handle:
        package = json.load(handle)
    return any(package_name in (package.get(field) or {}) for field in dependency_fields)

if declares(repo):
    print(f"declaration\t{repo}")
    raise SystemExit(0)

declarations = set()
uncovered = []
for relative in sorted(set(sys.argv[3:])):
    candidate = PurePosixPath(relative)
    current = (repo / Path(*candidate.parts)).parent
    declaration = None
    while current == repo or repo in current.parents:
        if declares(current):
            declaration = current
            break
        if current == repo:
            break
        current = current.parent
    if declaration is None:
        uncovered.append(relative)
    else:
        declarations.add(declaration)

for directory in sorted(declarations):
    print(f"declaration\t{directory}")
for relative in uncovered:
    print(f"uncovered\t{relative}")
PY
}

js_declaration_dir() {
  local repo="$1"
  local package="$2"
  local kind value

  JS_DECLARATION_DIR=""
  JS_DECLARATION_DIRS=()
  JS_UNCOVERED_FILES=()
  JS_DECLARATION_STATE="none"
  while IFS=$'\t' read -r kind value; do
    [[ -n "$value" ]] || continue
    case "$kind" in
      declaration) JS_DECLARATION_DIRS+=("$value") ;;
      uncovered) JS_UNCOVERED_FILES+=("$value") ;;
    esac
  done < <(js_declaration_dirs "$repo" "$package")

  case "${#JS_DECLARATION_DIRS[@]}" in
    0) return 1 ;;
    1)
      if [[ ${#JS_UNCOVERED_FILES[@]} -gt 0 ]]; then
        JS_DECLARATION_STATE="partial"
        return 3
      fi
      JS_DECLARATION_DIR="${JS_DECLARATION_DIRS[0]}"
      JS_DECLARATION_STATE="resolved"
      return 0
      ;;
    *)
      JS_DECLARATION_STATE="ambiguous"
      return 2
      ;;
  esac
}

package_declares_js_dependency() {
  js_declaration_dir "$1" "$2"
  [[ "$JS_DECLARATION_STATE" != "none" ]]
}

js_workspace_contains() {
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

js_package_manager_context() {
  local input="${1:-.}"
  local boundary="${2:-$input}"
  local dir origin declared parent eligible

  dir="$(cd "$input" 2>/dev/null && pwd -P)" || return 1
  origin="$dir"
  boundary="$(cd "$boundary" 2>/dev/null && pwd -P)" || return 1
  JS_PACKAGE_MANAGER=""
  JS_PACKAGE_MANAGER_ROOT=""

  while :; do
    declared=""
    eligible=1
    if [[ "$dir" != "$origin" ]] && ! js_workspace_contains "$origin" "$dir"; then
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
    fi
    case "$declared" in
      pnpm|yarn|bun|npm)
        JS_PACKAGE_MANAGER="$declared"
        JS_PACKAGE_MANAGER_ROOT="$dir"
        return 0
        ;;
    esac
    if [[ "$eligible" -eq 1 && -f "$dir/pnpm-lock.yaml" ]]; then
      JS_PACKAGE_MANAGER="pnpm"
    elif [[ "$eligible" -eq 1 && -f "$dir/yarn.lock" ]]; then
      JS_PACKAGE_MANAGER="yarn"
    elif [[ "$eligible" -eq 1 && ( -f "$dir/bun.lock" || -f "$dir/bun.lockb" ) ]]; then
      JS_PACKAGE_MANAGER="bun"
    elif [[ "$eligible" -eq 1 && ( -f "$dir/package-lock.json" || -f "$dir/npm-shrinkwrap.json" ) ]]; then
      JS_PACKAGE_MANAGER="npm"
    fi
    if [[ -n "$JS_PACKAGE_MANAGER" ]]; then
      JS_PACKAGE_MANAGER_ROOT="$dir"
      return 0
    fi
    [[ "$dir" == "$boundary" ]] && break
    parent="$(dirname "$dir")"
    if [[ "$parent" == "$dir" ]] \
      || [[ "$parent" != "$boundary" && "$parent" != "$boundary/"* ]]; then
      break
    fi
    dir="$parent"
  done

  JS_PACKAGE_MANAGER="npm"
  JS_PACKAGE_MANAGER_ROOT="$origin"
}

detect_js_package_manager() {
  js_package_manager_context "${1:-.}" "${2:-${1:-.}}" || return 1
  printf '%s\n' "$JS_PACKAGE_MANAGER"
}

DECLARED_JS_COMMAND=()
DECLARED_JS_WRAPPER=""
DECLARED_JS_PROJECT_DIR=""

resolve_declared_js_binary() {
  local repo="$1"
  local package="$2"
  local binary="$3"
  local project_bin yarn_bin dir parent

  DECLARED_JS_COMMAND=()
  DECLARED_JS_WRAPPER=""
  DECLARED_JS_PROJECT_DIR=""
  js_declaration_dir "$repo" "$package" || return $?
  DECLARED_JS_PROJECT_DIR="$JS_DECLARATION_DIR"

  dir="$JS_DECLARATION_DIR"
  while :; do
    project_bin="$dir/node_modules/.bin/$binary"
    if [[ -x "$project_bin" ]] \
      && { [[ "$dir" == "$JS_DECLARATION_DIR" ]] \
        || js_workspace_contains "$JS_DECLARATION_DIR" "$dir"; }; then
      DECLARED_JS_COMMAND=("$project_bin")
      DECLARED_JS_WRAPPER="project"
      return 0
    fi
    [[ "$dir" == "$repo" ]] && break
    parent="$(dirname "$dir")"
    if [[ "$parent" == "$dir" ]] \
      || [[ "$parent" != "$repo" && "$parent" != "$repo/"* ]]; then
      break
    fi
    dir="$parent"
  done

  js_package_manager_context "$JS_DECLARATION_DIR" "$repo" || return 1
  [[ "$JS_PACKAGE_MANAGER" == "yarn" ]] || return 1
  yarn_bin="$(command -v yarn 2>/dev/null || true)"
  [[ -n "$yarn_bin" ]] || return 1
  if env \
    COREPACK_ENABLE_NETWORK=0 \
    COREPACK_DEFAULT_TO_LATEST=0 \
    YARN_ENABLE_NETWORK=0 \
    "$yarn_bin" --cwd "$JS_DECLARATION_DIR" bin "$binary" >/dev/null 2>&1; then
    DECLARED_JS_COMMAND=(
      env
      COREPACK_ENABLE_NETWORK=0
      COREPACK_DEFAULT_TO_LATEST=0
      YARN_ENABLE_NETWORK=0
      "$yarn_bin" --cwd "$JS_DECLARATION_DIR" run -B "$binary"
    )
    DECLARED_JS_WRAPPER="yarn-pnp"
    return 0
  fi
  return 1
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

js_tool_package() {
  case "$1" in
    knip) printf 'knip\n' ;;
    jscpd) printf 'jscpd\n' ;;
    markdownlint-cli2) printf 'markdownlint-cli2\n' ;;
    api-extractor) printf '@microsoft/api-extractor\n' ;;
    stryker) printf '@stryker-mutator/core\n' ;;
    *) return 1 ;;
  esac
}

js_restore_command() {
  local repo="$1"
  local boundary="${2:-$repo}"
  local install_root
  local quoted_repo
  local quoted_lock

  js_package_manager_context "$repo" "$boundary" || return 1
  install_root="$JS_PACKAGE_MANAGER_ROOT"
  printf -v quoted_repo '%q' "$install_root"
  case "$JS_PACKAGE_MANAGER" in
    pnpm)
      if [[ -f "$install_root/pnpm-lock.yaml" ]]; then
        printf 'pnpm --dir %s install --frozen-lockfile\n' "$quoted_repo"
      else
        printf 'pnpm --dir %s install\n' "$quoted_repo"
      fi
      ;;
    yarn)
      if [[ -f "$install_root/yarn.lock" ]]; then
        printf 'yarn --cwd %s install --immutable\n' "$quoted_repo"
      else
        printf -v quoted_lock '%q' "$install_root/yarn.lock"
        printf 'Restore %s from version control (or create and review it deliberately), then run yarn --cwd %s install --immutable\n' \
          "$quoted_lock" "$quoted_repo"
      fi
      ;;
    bun)
      if [[ -f "$install_root/bun.lock" || -f "$install_root/bun.lockb" ]]; then
        printf 'bun --cwd %s install --frozen-lockfile\n' "$quoted_repo"
      else
        printf 'bun --cwd %s install\n' "$quoted_repo"
      fi
      ;;
    npm|*)
      if [[ -f "$install_root/package-lock.json" || -f "$install_root/npm-shrinkwrap.json" ]]; then
        printf 'npm --prefix %s ci\n' "$quoted_repo"
      else
        printf 'npm --prefix %s install\n' "$quoted_repo"
      fi
      ;;
  esac
}

js_exec_command() {
  local repo="$1"
  local binary="$2"
  local boundary="${3:-$repo}"
  local prefix="./node_modules/.bin"
  local quoted_repo

  if [[ "$(detect_js_package_manager "$repo" "$boundary")" == "yarn" ]]; then
    printf -v quoted_repo '%q' "$repo"
    printf 'env COREPACK_ENABLE_NETWORK=0 COREPACK_DEFAULT_TO_LATEST=0 YARN_ENABLE_NETWORK=0 yarn --cwd %s run -B %s\n' \
      "$quoted_repo" "$binary"
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
  local package

  if package="$(js_tool_package "$tool")"; then
    js_dev_install_command "$repo" "$package"
    return 0
  fi

  case "$tool" in
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
    gradle)
      if command -v brew >/dev/null 2>&1; then
        printf 'brew install gradle\n'
      elif command -v apt-get >/dev/null 2>&1; then
        printf 'Ask an administrator to install Debian package gradle; official guide: https://docs.gradle.org/current/userguide/installation.html\n'
      else
        printf 'Install Gradle from https://docs.gradle.org/current/userguide/installation.html\n'
      fi
      ;;
    *) printf 'Install %s from its official distribution\n' "$tool" ;;
  esac
}

tool_repair_command() {
  local repo="$1"
  local tool="$2"
  local package root_install

  if package="$(js_tool_package "$tool")"; then
    if js_declaration_dir "$repo" "$package"; then
      js_restore_command "$JS_DECLARATION_DIR" "$repo"
      return 0
    fi
    if [[ "$JS_DECLARATION_STATE" == "ambiguous" ]]; then
      root_install="$(js_dev_install_command "$repo" "$package")"
      printf 'Declare %s once at the repository root: from %s run: %s (current declarations: %s)\n' \
        "$package" "$repo" "$root_install" "${JS_DECLARATION_DIRS[*]}"
      return 0
    fi
    if [[ "$JS_DECLARATION_STATE" == "partial" ]]; then
      root_install="$(js_dev_install_command "$repo" "$package")"
      printf 'The %s declaration covers only %s; uncovered inputs: %s. Declare it once at the repository root: from %s run: %s\n' \
        "$package" "${JS_DECLARATION_DIRS[*]}" "${JS_UNCOVERED_FILES[*]}" "$repo" "$root_install"
      return 0
    fi
  fi
  tool_install_command "$repo" "$tool"
}
