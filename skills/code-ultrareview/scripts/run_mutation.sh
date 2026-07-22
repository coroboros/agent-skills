#!/usr/bin/env bash
# Mutation testing extension for Code Ultrareview (enabled by --mutation-test).
#
# The extension is atomic: every prerequisite for every applicable language is
# checked before a mutation process starts. Missing tools or project config
# exit 3 with exact remediation. Runtime, timeout, or report failures exit 4.
# No package is installed or resolved while the skill runs.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROCESS_TIMEOUT="$SCRIPT_DIR/process_timeout.py"
# shellcheck source-path=SCRIPTDIR
# shellcheck source=install-guidance.sh
source "$SCRIPT_DIR/install-guidance.sh"

SCOPE=""
OUTPUT_DIR=""
REPO="."
TIMEOUT="${MUTATION_TIMEOUT:-600}"
ORIGINAL_ARGS=("$@")

format_command() {
  local argument escaped
  local rendered=()
  for argument in "$@"; do
    printf -v escaped '%q' "$argument"
    rendered+=("$escaped")
  done
  local IFS=' '
  printf '%s\n' "${rendered[*]}"
}

MUTATION_RERUN="$(format_command bash "$SCRIPT_DIR/run_mutation.sh" ${ORIGINAL_ARGS[@]+"${ORIGINAL_ARGS[@]}"})"

emit_rerun() {
  echo "ERROR: rerun: $MUTATION_RERUN" >&2
}

usage() {
  cat <<'EOF' >&2
Usage: run_mutation.sh --scope <scope.json> --output-dir <dir> [options]

Required:
  --scope <path>        scope.json from scripts/scope.py
  --output-dir <path>   directory for raw/, mutation-findings.jsonl

Options:
  --repo <path>         repo root (default: cwd)
  --timeout <seconds>   per-tool timeout (default: 600)

Env:
  MUTATION_DRY_RUN=1    validate and print the plan without running tools

Exit 0 complete or not applicable; 2 invalid input; 3 missing prerequisite;
4 mutation runtime, timeout, or report failure.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope) SCOPE="${2:-}"; shift 2 ;;
    --output-dir) OUTPUT_DIR="${2:-}"; shift 2 ;;
    --repo) REPO="${2:-}"; shift 2 ;;
    --timeout) TIMEOUT="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ -z "$SCOPE" || -z "$OUTPUT_DIR" ]]; then
  usage
  exit 2
fi
if [[ ! -r "$SCOPE" ]]; then
  echo "ERROR: scope.json not readable: $SCOPE" >&2
  exit 2
fi
if [[ ! "$TIMEOUT" =~ ^[1-9][0-9]*$ ]]; then
  echo "ERROR: timeout must be a positive integer: $TIMEOUT" >&2
  exit 2
fi

if ! REPO="$(cd "$REPO" 2>/dev/null && pwd -P)"; then
  echo "ERROR: repo path is not a readable directory: $REPO" >&2
  exit 2
fi
if ! scope_error="$(validate_review_scope "$SCOPE")"; then
  echo "ERROR: invalid Code Ultrareview scope: $scope_error" >&2
  echo "ERROR: remediation: rerun scope.py to recreate scope.json, then rerun Code Ultrareview." >&2
  emit_rerun
  exit 2
fi
FINDINGS_FINAL="$OUTPUT_DIR/mutation-findings.jsonl"
FINDINGS_OUT="$OUTPUT_DIR/.mutation-findings.pending.jsonl"
PREFLIGHT_FINAL="$OUTPUT_DIR/mutation-preflight.json"
PREFLIGHT_STDOUT="$OUTPUT_DIR/raw/mutation-preflight.stdout"
PREFLIGHT_ERROR="$OUTPUT_DIR/raw/mutation-preflight.stderr"
PREFLIGHT_STDOUT_PENDING=""

# shellcheck disable=SC2329 # Invoked by the EXIT trap below.
cleanup_pending_outputs() {
  rm -f "$FINDINGS_OUT"
  [[ -z "$PREFLIGHT_STDOUT_PENDING" ]] || rm -f "$PREFLIGHT_STDOUT_PENDING"
}
trap cleanup_pending_outputs EXIT

invalidate_mutation_outputs() {
  rm -f \
    "$FINDINGS_FINAL" \
    "$FINDINGS_OUT" \
    "$PREFLIGHT_FINAL" \
    "$PREFLIGHT_STDOUT" \
    "$PREFLIGHT_ERROR"
}

set_mutation_coverage() {
  local status="$1" complete="$2" applicable="$3"
  python3 - "$SCOPE" "$status" "$complete" "$applicable" \
    "$FINDINGS_FINAL" <<'PY'
import hashlib
import json
import os
from pathlib import Path
import sys

path = Path(sys.argv[1])
with path.open(encoding="utf-8") as handle:
    scope = json.load(handle)
applicable = None if sys.argv[4] == "unknown" else sys.argv[4] == "1"
complete = sys.argv[3] == "1"
scope["mutation_coverage"] = {
    "requested": True,
    "complete": complete,
    "applicable": applicable,
    "status": sys.argv[2],
}
if complete and applicable:
    findings_path = Path(sys.argv[5]).resolve()
    data = findings_path.read_bytes()
    count = sum(1 for line in data.splitlines() if line.strip())
    scope["mutation_coverage"].update({
        "output": str(findings_path),
        "sha256": hashlib.sha256(data).hexdigest(),
        "finding_count": count,
    })
if not complete:
    scope["coverage_complete"] = False
temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
try:
    temporary.write_text(
        json.dumps(scope, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)
finally:
    temporary.unlink(missing_ok=True)
PY
}

publish_findings() {
  local status="$1" complete="$2" applicable="$3"
  if ! commit_findings; then
    set_mutation_coverage "failed" 0 "$applicable" || true
    echo "ERROR: mutation findings could not be published atomically to $FINDINGS_FINAL." >&2
    echo "ERROR: remediation: verify that $OUTPUT_DIR is writable and supports same-directory rename, then rerun Code Ultrareview." >&2
    emit_rerun
    return 1
  fi
  if ! set_mutation_coverage "$status" "$complete" "$applicable"; then
    rm -f "$FINDINGS_FINAL"
    set_mutation_coverage "failed" 0 "$applicable" || true
    echo "ERROR: mutation findings were discarded because coverage state could not be persisted to $SCOPE." >&2
    echo "ERROR: remediation: verify that the scope directory is writable and supports atomic replacement, then rerun Code Ultrareview." >&2
    emit_rerun
    return 1
  fi
}

if ! set_mutation_coverage "preflight" 0 unknown; then
  if ! invalidate_mutation_outputs; then
    echo "ERROR: stale mutation outputs could not be fully invalidated under $OUTPUT_DIR" >&2
  fi
  echo "ERROR: could not initialize mutation coverage in $SCOPE" >&2
  echo "ERROR: remediation: verify that the scope directory is writable and supports atomic replacement, then rerun Code Ultrareview." >&2
  emit_rerun
  exit 4
fi
if ! rm -f "$FINDINGS_FINAL"; then
  set_mutation_coverage "failed" 0 unknown || true
  echo "ERROR: stale mutation findings could not be removed from $FINDINGS_FINAL" >&2
  echo "ERROR: remediation: verify that $OUTPUT_DIR is writable, remove the stale findings file, then rerun Code Ultrareview." >&2
  emit_rerun
  exit 4
fi
if ! mkdir -p "$OUTPUT_DIR/raw"; then
  set_mutation_coverage "failed" 0 unknown || true
  echo "ERROR: mutation output directory could not be created: $OUTPUT_DIR/raw" >&2
  echo "ERROR: remediation: verify that $OUTPUT_DIR is writable, then rerun Code Ultrareview." >&2
  emit_rerun
  exit 4
fi
if ! rm -f "$PREFLIGHT_FINAL" "$PREFLIGHT_STDOUT" "$PREFLIGHT_ERROR"; then
  set_mutation_coverage "failed" 0 unknown || true
  echo "ERROR: stale mutation preflight output could not be removed from $OUTPUT_DIR" >&2
  echo "ERROR: remediation: verify that $OUTPUT_DIR is writable, remove the stale preflight files, then rerun Code Ultrareview." >&2
  emit_rerun
  exit 4
fi
if ! PREFLIGHT_STDOUT_PENDING="$(mktemp "$OUTPUT_DIR/raw/.mutation-preflight.stdout.XXXXXX")"; then
  set_mutation_coverage "failed" 0 unknown || true
  echo "ERROR: pending mutation preflight output could not be created in $OUTPUT_DIR/raw" >&2
  echo "ERROR: remediation: verify that $OUTPUT_DIR/raw is writable and supports same-directory temporary files, then rerun Code Ultrareview." >&2
  emit_rerun
  exit 4
fi
if ! : >"$FINDINGS_OUT"; then
  set_mutation_coverage "failed" 0 unknown || true
  echo "ERROR: pending mutation findings could not be created in $OUTPUT_DIR" >&2
  echo "ERROR: remediation: verify that $OUTPUT_DIR is writable, then rerun Code Ultrareview." >&2
  emit_rerun
  exit 4
fi

commit_findings() {
  mv -f "$FINDINGS_OUT" "$FINDINGS_FINAL"
}

if [[ -f "$REPO/package.json" ]] \
  && ! package_error="$(validate_package_manifest "$REPO/package.json")"; then
  echo "ERROR: invalid project manifest: $package_error" >&2
  echo "ERROR: remediation: repair package.json so it is valid JSON with object dependency maps, then rerun Code Ultrareview." >&2
  emit_rerun
  exit 2
fi

_scope_field() {
  python3 - "$SCOPE" "$1" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    current = json.load(handle)
for key in sys.argv[2].lstrip(".").split("."):
    if not key:
        continue
    current = current.get(key) if isinstance(current, dict) else None
    if current is None:
        break
if isinstance(current, list):
    for item in current:
        print(item)
elif current is not None:
    print(current)
PY
}

LANGUAGES=()
while IFS= read -r line; do
  [[ -n "$line" ]] && LANGUAGES+=("$line")
done < <(_scope_field languages)

FILES_TOUCHED=()
while IFS= read -r line; do
  [[ -n "$line" ]] && FILES_TOUCHED+=("$line")
done < <(_scope_field files_touched_list)

has_lang() {
  local target="$1" language
  [[ ${#LANGUAGES[@]} -gt 0 ]] || return 1
  for language in "${LANGUAGES[@]}"; do
    [[ "$language" == "$target" ]] && return 0
  done
  return 1
}

JS_FILES=()
PY_FILES=()
JVM_FILES=()
if [[ ${#FILES_TOUCHED[@]} -gt 0 ]]; then
  for relative in "${FILES_TOUCHED[@]}"; do
    [[ -f "$REPO/$relative" ]] || continue
    case "$relative" in
      *.ts|*.tsx|*.js|*.jsx|*.mjs|*.cjs) JS_FILES+=("$relative") ;;
      *.py) PY_FILES+=("$relative") ;;
      *.java|*.kt|*.kts|*.scala) JVM_FILES+=("$relative") ;;
    esac
  done
fi
# shellcheck disable=SC2034 # install-guidance.sh consumes this sourced-state array.
JS_RELEVANT_FILES=()
if [[ ${#JS_FILES[@]} -gt 0 ]]; then
  # shellcheck disable=SC2034 # install-guidance.sh consumes this sourced-state array.
  JS_RELEVANT_FILES=("${JS_FILES[@]}")
fi

JS_APPLICABLE=0
PY_APPLICABLE=0
JVM_APPLICABLE=0
if [[ ${#JS_FILES[@]} -gt 0 ]] && { has_lang typescript || has_lang javascript; }; then
  JS_APPLICABLE=1
fi
if [[ ${#PY_FILES[@]} -gt 0 ]] && has_lang python; then
  PY_APPLICABLE=1
fi
if [[ ${#JVM_FILES[@]} -gt 0 ]] && { has_lang java || has_lang kotlin || has_lang scala; }; then
  JVM_APPLICABLE=1
fi

run_with_timeout() {
  local seconds="$1"
  shift
  python3 "$PROCESS_TIMEOUT" --timeout "$seconds" -- "$@"
}

has_stryker_config() {
  local project_dir="$1" config
  for config in \
    stryker.config.js stryker.config.mjs stryker.config.cjs stryker.config.json \
    stryker.conf.js stryker.conf.mjs stryker.conf.cjs stryker.conf.json; do
    [[ -f "$project_dir/$config" ]] && return 0
  done
  return 1
}

validate_stryker_json_configs() {
  python3 - "$1" <<'PY'
import json
from pathlib import Path
import sys

repo = Path(sys.argv[1])
for name in ("stryker.config.json", "stryker.conf.json"):
    path = repo / name
    if not path.is_file():
        continue
    try:
        with path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        print(f"{name} is not valid JSON: {error}")
        raise SystemExit(1)
    if not isinstance(payload, dict):
        print(f"{name} must contain an object")
        raise SystemExit(1)
PY
}

validate_python_mutation_manifests() {
  python3 - "$REPO" <<'PY'
import configparser
from pathlib import Path
import sys

repo = Path(sys.argv[1])
setup_cfg = repo / "setup.cfg"
if setup_cfg.is_file():
    try:
        parser = configparser.ConfigParser()
        with setup_cfg.open(encoding="utf-8") as handle:
            parser.read_file(handle)
    except (OSError, UnicodeError, configparser.Error) as error:
        print(f"setup.cfg is invalid: {error}")
        raise SystemExit(1)

pyproject = repo / "pyproject.toml"
if pyproject.is_file():
    try:
        import tomllib
    except ModuleNotFoundError:
        print(
            "Python 3.11+ is required to validate pyproject.toml with "
            "the standard-library tomllib parser"
        )
        raise SystemExit(1)
    try:
        with pyproject.open("rb") as handle:
            payload = tomllib.load(handle)
    except (OSError, ValueError) as error:
        print(f"pyproject.toml is not valid TOML: {error}")
        raise SystemExit(1)
    if not isinstance(payload, dict):
        print("pyproject.toml must contain a table")
        raise SystemExit(1)
PY
}

validate_pom_manifest() {
  python3 - "$REPO/pom.xml" <<'PY'
import sys
import xml.etree.ElementTree as ET

try:
    ET.parse(sys.argv[1])
except (OSError, ET.ParseError) as error:
    print(f"pom.xml is not valid XML: {error}")
    raise SystemExit(1)
PY
}

has_mutmut_config() {
  python3 - "$REPO" <<'PY' >/dev/null 2>&1
import configparser
import pathlib
import sys

repo = pathlib.Path(sys.argv[1])
setup_cfg = repo / "setup.cfg"
if setup_cfg.is_file():
    parser = configparser.ConfigParser()
    parser.read(setup_cfg, encoding="utf-8")
    if parser.has_option("mutmut", "source_paths"):
        raise SystemExit(0)

pyproject = repo / "pyproject.toml"
if pyproject.is_file():
    try:
        import tomllib
        with pyproject.open("rb") as handle:
            data = tomllib.load(handle)
        if (data.get("tool", {}).get("mutmut", {}).get("source_paths")):
            raise SystemExit(0)
    except ModuleNotFoundError:
        raise SystemExit(1)
    except (OSError, ValueError):
        pass
raise SystemExit(1)
PY
}

has_pitest_plugin() {
  [[ -f "$REPO/pom.xml" ]] || return 1
  python3 - "$REPO/pom.xml" <<'PY' >/dev/null 2>&1
import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
for element in root.iter():
    if element.tag.rsplit("}", 1)[-1] != "plugin":
        continue
    values = {child.tag.rsplit("}", 1)[-1]: (child.text or "").strip() for child in element}
    if values.get("groupId") == "org.pitest" and values.get("artifactId") == "pitest-maven":
        raise SystemExit(0)
raise SystemExit(1)
PY
}

has_gradle_pitest_plugin() {
  local build_file=""
  [[ -f "$REPO/build.gradle.kts" ]] && build_file="$REPO/build.gradle.kts"
  [[ -z "$build_file" && -f "$REPO/build.gradle" ]] && build_file="$REPO/build.gradle"
  [[ -n "$build_file" ]] || return 1
  grep -Fq 'info.solidsoft.pitest' "$build_file"
}

STRYKER_COMMAND=()
STRYKER_PROJECT_DIR=""
STRYKER_PROJECT_REL=""
resolve_stryker() {
  STRYKER_COMMAND=()
  STRYKER_PROJECT_DIR=""
  STRYKER_PROJECT_REL=""
  if resolve_declared_js_binary "$REPO" "@stryker-mutator/core" stryker; then
    STRYKER_COMMAND=("${DECLARED_JS_COMMAND[@]}")
    STRYKER_PROJECT_DIR="$DECLARED_JS_PROJECT_DIR"
    if [[ "$STRYKER_PROJECT_DIR" != "$REPO" ]]; then
      STRYKER_PROJECT_REL="${STRYKER_PROJECT_DIR#"$REPO"/}"
      [[ "$STRYKER_PROJECT_REL" != "$STRYKER_PROJECT_DIR" ]] || return 1
    fi
    return 0
  fi
  return 1
}

stryker_scope_is_complete() {
  local path
  [[ -n "$STRYKER_PROJECT_DIR" ]] || return 1
  [[ -z "$STRYKER_PROJECT_REL" ]] && return 0
  for path in "${JS_FILES[@]}"; do
    [[ "$path" == "$STRYKER_PROJECT_REL/"* ]] || return 1
  done
}

MISSING_ROWS=()
JVM_BUILD=""
JVM_RUNNER=""
record_missing() {
  MISSING_ROWS+=("$1|$2|$3")
}

invalid_mutation_input() {
  set_mutation_coverage "invalid-input" 0 1 || true
  echo "ERROR: invalid mutation project configuration: $1" >&2
  echo "ERROR: remediation: $2" >&2
  emit_rerun
  return 2
}

if [[ $JS_APPLICABLE -eq 1 ]]; then
  if ! manifest_error="$(validate_relevant_package_manifests "$REPO")"; then
    invalid_mutation_input "$manifest_error" \
      "repair the reported package.json, then rerun Code Ultrareview"
    exit $?
  fi
  if ! js_declaration_dir "$REPO" "@stryker-mutator/core"; then
    case "$JS_DECLARATION_STATE" in
      ambiguous)
        record_missing "stryker-scope" \
          "changed JavaScript files map to multiple Stryker declarations: ${JS_DECLARATION_DIRS[*]}" \
          "$(tool_repair_command "$REPO" stryker)"
        ;;
      partial)
        record_missing "stryker-scope" \
          "changed JavaScript files are only partially covered by Stryker declaration(s): ${JS_DECLARATION_DIRS[*]}; uncovered inputs: ${JS_UNCOVERED_FILES[*]}" \
          "$(tool_repair_command "$REPO" stryker)"
        ;;
      *)
        record_missing "stryker" "@stryker-mutator/core is not declared for the changed JavaScript files" \
          "$(tool_install_command "$REPO" stryker)"
        ;;
    esac
  elif ! resolve_stryker; then
    record_missing "stryker" "the declared Stryker binary is unavailable" \
      "$(tool_repair_command "$REPO" stryker)"
  else
    if ! stryker_scope_is_complete; then
      record_missing "stryker-scope" \
        "not every changed JavaScript file belongs to $STRYKER_PROJECT_DIR" \
        "$(tool_repair_command "$REPO" stryker)"
    fi
    if ! config_error="$(validate_stryker_json_configs "$STRYKER_PROJECT_DIR")"; then
      invalid_mutation_input "$config_error" \
        "repair the reported JSON file, verify it with 'python3 -m json.tool <file>', then rerun Code Ultrareview"
      exit $?
    fi
    if ! has_stryker_config "$STRYKER_PROJECT_DIR"; then
      record_missing "stryker-config" \
        "no stryker.config.* file is present in $STRYKER_PROJECT_DIR" \
        "$(js_exec_command "$STRYKER_PROJECT_DIR" stryker "$REPO") init"
    fi
  fi
fi

if [[ $PY_APPLICABLE -eq 1 ]]; then
  if ! config_error="$(validate_python_mutation_manifests)"; then
    invalid_mutation_input "$config_error" \
      "repair the reported manifest; when pyproject.toml is present, run this skill with Python 3.11+ so standard-library tomllib can validate it, then rerun Code Ultrareview"
    exit $?
  fi
  if ! command -v mutmut >/dev/null 2>&1; then
    record_missing "mutmut" "mutmut is not installed on PATH" \
      "$(tool_install_command "$REPO" mutmut)"
  fi
  if ! has_mutmut_config; then
    record_missing "mutmut-config" "source_paths is not configured" \
      "add '[tool.mutmut]' with 'source_paths = [\"src\"]' to pyproject.toml"
  fi
fi

if [[ $JVM_APPLICABLE -eq 1 ]]; then
  if [[ -f "$REPO/pom.xml" ]]; then
    if ! config_error="$(validate_pom_manifest)"; then
      invalid_mutation_input "$config_error" \
        "repair pom.xml, verify it with 'python3 -c \"import xml.etree.ElementTree as ET; ET.parse(\\\"pom.xml\\\")\"', then rerun Code Ultrareview"
      exit $?
    fi
    JVM_BUILD="maven"
    if ! has_pitest_plugin; then
      record_missing "pitest" "org.pitest:pitest-maven is not declared in pom.xml" \
        "declare org.pitest:pitest-maven under pom.xml build.plugins"
    fi
    if JVM_RUNNER="$(command -v mvn 2>/dev/null)"; then
      :
    else
      JVM_RUNNER=""
      record_missing "mvn" "Maven is not installed on PATH" \
        "$(tool_install_command "$REPO" mvn)"
    fi
  elif [[ -f "$REPO/build.gradle" || -f "$REPO/build.gradle.kts" ]]; then
    JVM_BUILD="gradle"
    if ! has_gradle_pitest_plugin; then
      record_missing "pitest-gradle" "the Gradle Pitest plugin is not declared" \
        "add the 'info.solidsoft.pitest' plugin to build.gradle(.kts), provision its dependencies, then rerun Code Ultrareview"
    fi
    if JVM_RUNNER="$(command -v gradle 2>/dev/null)"; then
      :
    else
      JVM_RUNNER=""
      record_missing "gradle" "Gradle is not installed on PATH" \
        "$(tool_install_command "$REPO" gradle)"
    fi
  else
    record_missing "pitest-build" "no supported JVM build manifest was found" \
      "configure Pitest in the project's existing build system (pitest-maven in pom.xml or info.solidsoft.pitest in build.gradle(.kts)), then rerun Code Ultrareview"
  fi
fi

render_preflight() {
  python3 - "$PREFLIGHT_FINAL" \
    "$JS_APPLICABLE" "$PY_APPLICABLE" "$JVM_APPLICABLE" "$JVM_BUILD" \
    "${#MISSING_ROWS[@]}" ${MISSING_ROWS[@]+"${MISSING_ROWS[@]}"} <<'PY'
import json
import os
from pathlib import Path
import sys
import tempfile

path = Path(sys.argv[1])
applicable = {
    "javascript-typescript": sys.argv[2] == "1",
    "python": sys.argv[3] == "1",
    "jvm": sys.argv[4] == "1",
}
count = int(sys.argv[6])
missing = []
for row in sys.argv[7:7 + count]:
    tool, reason, remediation = row.split("|", 2)
    missing.append({"tool": tool, "reason": reason, "remediation": remediation})
payload = {
    "applicable": applicable,
    "jvm_build": sys.argv[5] or None,
    "missing": missing,
    "complete": not missing,
    "status": "not-applicable" if not any(applicable.values()) else ("blocked" if missing else "ready"),
}
temporary = None
try:
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    os.replace(temporary, path)
except Exception:
    if temporary is not None:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
    raise
print(json.dumps(payload, indent=2))
PY
}

if ! render_preflight >"$PREFLIGHT_STDOUT_PENDING" 2>"$PREFLIGHT_ERROR"; then
  rm -f "$PREFLIGHT_FINAL" "$PREFLIGHT_STDOUT" "$PREFLIGHT_STDOUT_PENDING"
  PREFLIGHT_STDOUT_PENDING=""
  set_mutation_coverage "failed" 0 unknown || true
  sed -n '1,20p' "$PREFLIGHT_ERROR" >&2
  echo "ERROR: mutation preflight could not be published atomically to $PREFLIGHT_FINAL." >&2
  echo "ERROR: remediation: verify that $OUTPUT_DIR is writable and supports same-directory atomic replacement, then rerun Code Ultrareview." >&2
  emit_rerun
  exit 4
fi
if ! mv -f "$PREFLIGHT_STDOUT_PENDING" "$PREFLIGHT_STDOUT"; then
  rm -f "$PREFLIGHT_FINAL" "$PREFLIGHT_STDOUT" "$PREFLIGHT_STDOUT_PENDING"
  PREFLIGHT_STDOUT_PENDING=""
  set_mutation_coverage "failed" 0 unknown || true
  echo "ERROR: mutation preflight diagnostics could not be published atomically to $PREFLIGHT_STDOUT." >&2
  echo "ERROR: remediation: verify that $OUTPUT_DIR/raw is writable and supports same-directory atomic replacement, then rerun Code Ultrareview." >&2
  emit_rerun
  exit 4
fi
PREFLIGHT_STDOUT_PENDING=""

if [[ ${#MISSING_ROWS[@]} -gt 0 ]]; then
  set_mutation_coverage "blocked" 0 1 || true
  for row in "${MISSING_ROWS[@]}"; do
    tool="${row%%|*}"
    rest="${row#*|}"
    reason="${rest%%|*}"
    remediation="${rest#*|}"
    echo "ERROR: mutation prerequisite '$tool' is missing: $reason." >&2
    echo "ERROR: remediation: $remediation" >&2
  done
  echo "ERROR: mutation coverage is incomplete; fix every prerequisite and rerun Code Ultrareview." >&2
  emit_rerun
  exit 3
fi

if [[ $JS_APPLICABLE -eq 0 && $PY_APPLICABLE -eq 0 && $JVM_APPLICABLE -eq 0 ]]; then
  publish_findings "not-applicable" 1 0 || exit 4
  echo "INFO: mutation testing is not applicable to the changed files." >&2
  exit 0
fi

if [[ "${MUTATION_DRY_RUN:-}" == "1" ]]; then
  publish_findings "dry-run" 0 1 || exit 4
  echo "INFO: MUTATION_DRY_RUN=1; prerequisites are complete and no mutation process was started." >&2
  exit 0
fi

runtime_error() {
  local message="$1" remediation="$2"
  set_mutation_coverage "failed" 0 1 || true
  echo "ERROR: $message" >&2
  echo "ERROR: repair/install: $remediation" >&2
  emit_rerun
  return 4
}

run_stryker() {
  local report raw err mutate rc path relative repair_command
  local mutate_files=()
  if ! resolve_stryker; then
    runtime_error "Stryker disappeared after preflight." \
      "$(tool_repair_command "$REPO" stryker)"
    return $?
  fi
  repair_command="$(tool_repair_command "$REPO" stryker)"
  report="$STRYKER_PROJECT_DIR/reports/mutation/mutation.json"
  raw="$OUTPUT_DIR/raw/stryker.log"
  err="$OUTPUT_DIR/raw/stryker.stderr"
  for path in "${JS_FILES[@]}"; do
    relative="$path"
    [[ -z "$STRYKER_PROJECT_REL" ]] || relative="${path#"$STRYKER_PROJECT_REL"/}"
    mutate_files+=("./$relative")
  done
  mutate="$(IFS=,; printf '%s' "${mutate_files[*]}")"
  rm -f "$report"

  (
    cd "$STRYKER_PROJECT_DIR" && run_with_timeout "$TIMEOUT" "${STRYKER_COMMAND[@]}" run \
      --reporters json --mutate "$mutate"
  ) >"$raw" 2>"$err"
  rc=$?
  if [[ $rc -eq 124 ]]; then
    runtime_error \
      "Stryker timed out after ${TIMEOUT}s; its process group was terminated. See $err" \
      "$repair_command"
    return $?
  fi
  if [[ $rc -ne 0 && $rc -ne 1 ]]; then
    runtime_error "Stryker failed with exit code $rc. See $err" "$repair_command"
    return $?
  fi
  if [[ ! -f "$report" ]]; then
    runtime_error \
      "Stryker did not produce a fresh JSON report at reports/mutation/mutation.json. See $err" \
      "$repair_command"
    return $?
  fi

  python3 - "$report" "$FINDINGS_OUT" "$STRYKER_PROJECT_REL" \
    "${JS_FILES[@]}" <<'PY' 2>>"$err"
import json
from pathlib import PurePosixPath
import sys

try:
    with open(sys.argv[1], encoding="utf-8") as handle:
        report = json.load(handle)
except (OSError, json.JSONDecodeError) as error:
    print(f"invalid Stryker JSON report: {error}", file=sys.stderr)
    raise SystemExit(4)

if not isinstance(report, dict):
    print("invalid Stryker JSON report: root must be an object", file=sys.stderr)
    raise SystemExit(4)
files = report.get("files")
if not isinstance(files, dict) or not files:
    print("invalid Stryker JSON report: non-empty files object is required", file=sys.stderr)
    raise SystemExit(4)

prefix = PurePosixPath(sys.argv[3]) if sys.argv[3] else None
changed = {PurePosixPath(path).as_posix() for path in sys.argv[4:]}
terminal_statuses = {
    "Killed",
    "Survived",
    "NoCoverage",
    "Timeout",
    "RuntimeError",
    "CompileError",
}
incomplete_statuses = {"Ignored", "Pending"}
evaluated = 0
incomplete = []
findings = []
for file_path, payload in files.items():
    if not isinstance(file_path, str) or not file_path or not isinstance(payload, dict):
        print("invalid Stryker JSON report: malformed file entry", file=sys.stderr)
        raise SystemExit(4)
    reported = PurePosixPath(file_path)
    if reported.is_absolute() or ".." in reported.parts:
        print(f"invalid Stryker JSON report path: {file_path}", file=sys.stderr)
        raise SystemExit(4)
    repo_path = (prefix / reported).as_posix() if prefix else reported.as_posix()
    if repo_path not in changed:
        continue
    mutants = payload.get("mutants")
    if not isinstance(mutants, list):
        print(f"invalid Stryker JSON report: {file_path} has no mutants list", file=sys.stderr)
        raise SystemExit(4)
    for mutant in mutants:
        if not isinstance(mutant, dict):
            print(f"invalid Stryker JSON report: malformed mutant in {file_path}", file=sys.stderr)
            raise SystemExit(4)
        status = mutant.get("status")
        if not isinstance(status, str) or not status:
            print(f"invalid Stryker JSON report: mutant in {file_path} has no status", file=sys.stderr)
            raise SystemExit(4)
        if status in incomplete_statuses:
            incomplete.append(f"{repo_path}: {status}")
            continue
        if status not in terminal_statuses:
            print(
                f"invalid Stryker JSON report: unsupported mutant status {status!r} in {file_path}",
                file=sys.stderr,
            )
            raise SystemExit(4)
        evaluated += 1
        if status not in {"Survived", "NoCoverage"}:
            continue
        location_payload = mutant.get("location")
        if not isinstance(location_payload, dict):
            print(f"invalid Stryker JSON report: mutant in {file_path} has no location", file=sys.stderr)
            raise SystemExit(4)
        start = location_payload.get("start")
        if not isinstance(start, dict):
            print(f"invalid Stryker JSON report: mutant in {file_path} has no start location", file=sys.stderr)
            raise SystemExit(4)
        line = start.get("line", 0)
        column = start.get("column", 0)
        location = f"{repo_path}:{line}:{column}" if line else repo_path
        if status == "NoCoverage":
            finding_text = f"Uncovered mutant ({mutant.get('mutatorName', '?')}): {mutant.get('description', 'no description')}"
            recommendation = "Add a test that executes this code path and asserts the intended behavior."
        else:
            finding_text = f"Surviving mutant ({mutant.get('mutatorName', '?')}): {mutant.get('description', 'no description')}"
            recommendation = "Add an assertion that fails when the mutated code path executes."
        findings.append({
            "axis": "tests",
            "severity": "Medium",
            "location": location,
            "finding": finding_text,
            "recommendation": recommendation,
            "confidence": 100,
            "source_tool": "stryker",
        })
if incomplete:
    print(
        "incomplete Stryker results: " + ", ".join(incomplete[:5]),
        file=sys.stderr,
    )
    raise SystemExit(4)
if evaluated == 0:
    print("invalid Stryker JSON report: no changed-file mutants were evaluated", file=sys.stderr)
    raise SystemExit(4)
with open(sys.argv[2], "a", encoding="utf-8") as handle:
    for finding in findings:
        handle.write(json.dumps(finding) + "\n")
PY
  rc=$?
  if [[ $rc -ne 0 ]]; then
    sed -n '1,20p' "$err" >&2
    echo "ERROR: diagnostic: run '$(js_exec_command "$STRYKER_PROJECT_DIR" stryker "$REPO") run --reporters json' directly and verify the canonical reports/mutation/mutation.json schema." >&2
    runtime_error "Stryker report could not be parsed reliably. See $err" \
      "$repair_command"
    return $?
  fi
}

run_mutmut() {
  local command raw err results terminals shows rc status mutant show_rc repair_command
  repair_command="$(tool_install_command "$REPO" mutmut)"
  command="$(command -v mutmut 2>/dev/null || true)"
  if [[ -z "$command" ]]; then
    runtime_error "mutmut disappeared after preflight." "$repair_command"
    return $?
  fi
  raw="$OUTPUT_DIR/raw/mutmut.log"
  err="$OUTPUT_DIR/raw/mutmut.stderr"
  results="$OUTPUT_DIR/raw/mutmut-results.log"
  terminals="$OUTPUT_DIR/raw/mutmut-terminal.tsv"
  shows="$OUTPUT_DIR/raw/mutmut-shows.txt"

  (cd "$REPO" && run_with_timeout "$TIMEOUT" "$command" run) >"$raw" 2>"$err"
  rc=$?
  if [[ $rc -eq 124 ]]; then
    runtime_error \
      "mutmut timed out after ${TIMEOUT}s; its process group was terminated. See $err" \
      "$repair_command"
    return $?
  fi
  if [[ $rc -ne 0 ]]; then
    runtime_error "mutmut failed with exit code $rc. See $err" "$repair_command"
    return $?
  fi
  (cd "$REPO" && run_with_timeout "$TIMEOUT" "$command" results --all) >"$results" 2>>"$err"
  rc=$?
  if [[ $rc -eq 124 ]]; then
    runtime_error \
      "mutmut results timed out after ${TIMEOUT}s; its process group was terminated. See $err" \
      "$repair_command"
    return $?
  fi
  if [[ $rc -ne 0 ]]; then
    runtime_error "mutmut results failed with exit code $rc. See $err" \
      "$repair_command"
    return $?
  fi
  python3 - "$results" "$terminals" <<'PY' 2>>"$err"
import pathlib
import sys

terminal_statuses = {
    "caught by type check",
    "killed",
    "survived",
    "no tests",
    "suspicious",
    "timeout",
    "segfault",
}
incomplete_statuses = {
    "skipped",
    "check was interrupted by user",
    "not checked",
}
valid_statuses = terminal_statuses | incomplete_statuses
rows = []
incomplete = []
evaluated = 0
for number, raw_line in enumerate(
    pathlib.Path(sys.argv[1]).read_text(encoding="utf-8").splitlines(), start=1
):
    line = raw_line.strip()
    if not line:
        continue
    if ": " not in line:
        print(f"invalid mutmut results line {number}: {raw_line}", file=sys.stderr)
        raise SystemExit(4)
    mutant, status = line.rsplit(": ", 1)
    if not mutant or status not in valid_statuses:
        print(f"invalid mutmut results line {number}: {raw_line}", file=sys.stderr)
        raise SystemExit(4)
    if status in incomplete_statuses:
        incomplete.append(f"{mutant}: {status}")
        continue
    evaluated += 1
    rows.append((status, mutant))
if incomplete:
    print(
        "incomplete mutmut results: " + ", ".join(incomplete[:5]),
        file=sys.stderr,
    )
    raise SystemExit(4)
if evaluated == 0:
    print("incomplete mutmut results: no mutants were evaluated", file=sys.stderr)
    raise SystemExit(4)
with pathlib.Path(sys.argv[2]).open("w", encoding="utf-8") as handle:
    for status, mutant in rows:
        handle.write(f"{status}\t{mutant}\n")
PY
  rc=$?
  if [[ $rc -ne 0 ]]; then
    sed -n '1,20p' "$err" >&2
    echo "ERROR: remediation: run 'mutmut results --all' directly; repair the mutation scope or update mutmut with '$(tool_install_command "$REPO" mutmut)' until at least one mutant is evaluated and every result line has a documented status, then rerun Code Ultrareview." >&2
    runtime_error "mutmut results output is incomplete or malformed. See $err" \
      "$repair_command"
    return $?
  fi
  : >"$shows"
  while IFS=$'\t' read -r status mutant; do
    [[ -n "$mutant" ]] || continue
    printf '=== %s\t%s ===\n' "$status" "$mutant" >>"$shows"
    (cd "$REPO" && run_with_timeout 15 "$command" show "$mutant") >>"$shows" 2>>"$err"
    show_rc=$?
    if [[ $show_rc -eq 124 ]]; then
      runtime_error \
        "mutmut show timed out after 15s for '$mutant'; its process group was terminated. See $err" \
        "$repair_command"
      return $?
    fi
    if [[ $show_rc -ne 0 ]]; then
      runtime_error \
        "mutmut show failed for '$mutant' with exit code $show_rc. See $err" \
        "$repair_command"
      return $?
    fi
  done <"$terminals"

  python3 - "$shows" "$FINDINGS_OUT" "${PY_FILES[@]}" <<'PY' 2>>"$err"
import json
import pathlib
import re
import sys

text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
changed = {pathlib.PurePosixPath(path).as_posix() for path in sys.argv[3:]}
blocks = re.split(r"^=== ([^\t]+)\t(.+) ===$", text, flags=re.MULTILINE)
if len(blocks) == 1:
    print("invalid mutmut show output: no terminal mutant blocks were produced", file=sys.stderr)
    raise SystemExit(4)

findings = []
mapped_mutations = 0
actionable_statuses = {"survived", "no tests", "suspicious"}
for index in range(1, len(blocks), 3):
    status = blocks[index]
    mutant = blocks[index + 1]
    body = blocks[index + 2]
    file_match = re.search(r"^---\s+(?:a/)?([^\t\n]+)", body, re.MULTILINE)
    line_match = re.search(r"^@@\s+-\d+(?:,\d+)?\s+\+(\d+)", body, re.MULTILINE)
    if not file_match:
        print(f"cannot locate source file for mutmut mutant {mutant}", file=sys.stderr)
        raise SystemExit(4)
    file_path = pathlib.PurePosixPath(file_match.group(1).strip()).as_posix()
    if file_path not in changed:
        continue
    mapped_mutations += 1
    if status not in actionable_statuses:
        continue
    line = line_match.group(1) if line_match else "?"
    if status == "no tests":
        finding_text = f"Uncovered mutmut mutant: {mutant}"
        recommendation = "Add a test that executes this mutant's code path and asserts the intended behavior."
    elif status == "suspicious":
        finding_text = f"Suspicious mutmut mutant: {mutant}"
        recommendation = "Investigate the slow mutation result and add a focused assertion that decisively kills the mutant."
    else:
        finding_text = f"Surviving mutmut mutant: {mutant}"
        recommendation = "Add an assertion that fails when the mutated code path executes."
    findings.append({
        "axis": "tests",
        "severity": "Medium",
        "location": f"{file_path}:{line}",
        "finding": finding_text,
        "recommendation": recommendation,
        "confidence": 100,
        "source_tool": "mutmut",
    })

if mapped_mutations == 0:
    print("invalid mutmut results: no changed-file mutants were evaluated", file=sys.stderr)
    raise SystemExit(4)

with open(sys.argv[2], "a", encoding="utf-8") as handle:
    for finding in findings:
        handle.write(json.dumps(finding) + "\n")
PY
  rc=$?
  if [[ $rc -ne 0 ]]; then
    sed -n '1,20p' "$err" >&2
    runtime_error "mutmut terminal output could not be mapped reliably. See $err" \
      "$repair_command"
    return $?
  fi
}

run_pitest() {
  local raw err marker rc report report_root repair_command
  raw="$OUTPUT_DIR/raw/pitest.log"
  err="$OUTPUT_DIR/raw/pitest.stderr"
  marker="$(mktemp -t pitest_report_XXXX)"
  if [[ "$JVM_BUILD" == "maven" ]]; then
    report_root="$REPO/target/pit-reports"
    repair_command="$(format_command "$JVM_RUNNER" --offline -q -B pitest:mutationCoverage)"
    (cd "$REPO" && run_with_timeout "$TIMEOUT" "$JVM_RUNNER" --offline -q -B pitest:mutationCoverage) >"$raw" 2>"$err"
  elif [[ "$JVM_BUILD" == "gradle" ]]; then
    report_root="$REPO/build/reports/pitest"
    repair_command="$(format_command "$JVM_RUNNER" --offline --no-daemon pitest)"
    (cd "$REPO" && run_with_timeout "$TIMEOUT" "$JVM_RUNNER" --offline --no-daemon pitest) >"$raw" 2>"$err"
  else
    rm -f "$marker"
    runtime_error \
      "Pitest has no validated JVM build runner." \
      "configure Pitest in Maven or Gradle, install the matching runner, then rerun: $MUTATION_RERUN"
    return $?
  fi
  rc=$?
  if [[ $rc -eq 124 ]]; then
    rm -f "$marker"
    runtime_error \
      "Pitest timed out after ${TIMEOUT}s; its process group was terminated. See $err" \
      "$repair_command"
    return $?
  fi
  if [[ $rc -ne 0 ]]; then
    rm -f "$marker"
    runtime_error "Pitest failed with exit code $rc. See $err" "$repair_command"
    return $?
  fi
  report="$(find "$report_root" -type f -name mutations.xml -newer "$marker" -print 2>/dev/null | sort | tail -n 1)"
  rm -f "$marker"
  if [[ -z "$report" || ! -f "$report" ]]; then
    runtime_error \
      "Pitest did not produce a fresh mutations.xml report under $report_root. See $err" \
      "$repair_command"
    return $?
  fi

  python3 - "$report" "$FINDINGS_OUT" "${JVM_FILES[@]}" <<'PY' 2>>"$err"
import json
import pathlib
import sys
import xml.etree.ElementTree as ET

try:
    tree = ET.parse(sys.argv[1])
except (OSError, ET.ParseError) as error:
    print(f"invalid Pitest XML report: {error}", file=sys.stderr)
    raise SystemExit(4)

changed = [pathlib.PurePosixPath(path).as_posix() for path in sys.argv[3:]]
findings = []
mapped_mutations = 0
terminal_statuses = {
    "KILLED",
    "SURVIVED",
    "NO_COVERAGE",
    "NON_VIABLE",
    "TIMED_OUT",
    "MEMORY_ERROR",
    "RUN_ERROR",
}
root = tree.getroot()
if root.tag.rsplit("}", 1)[-1] != "mutations":
    print("invalid Pitest XML report: root element must be mutations", file=sys.stderr)
    raise SystemExit(4)
mutations = [
    child for child in root
    if child.tag.rsplit("}", 1)[-1] == "mutation"
]
if not mutations:
    print("invalid Pitest XML report: no mutations were evaluated", file=sys.stderr)
    raise SystemExit(4)
for mutation in mutations:
    status = mutation.get("status")
    if not status:
        print("invalid Pitest XML report: mutation has no status", file=sys.stderr)
        raise SystemExit(4)
    source_name = mutation.findtext("sourceFile") or ""
    mutated_class = (mutation.findtext("mutatedClass") or "").split("$", 1)[0]
    if not source_name:
        print("Pitest survivor is missing sourceFile", file=sys.stderr)
        raise SystemExit(4)

    package = mutated_class.rsplit(".", 1)[0] if "." in mutated_class else ""
    suffix = f"{package.replace('.', '/')}/{source_name}" if package else source_name
    matches = [
        path for path in changed
        if path == suffix or path.endswith(f"/{suffix}")
    ]
    if not matches and not package:
        matches = [path for path in changed if pathlib.PurePosixPath(path).name == source_name]
    if len(matches) > 1:
        print(
            f"ambiguous Pitest source mapping for {mutated_class or '?'} / "
            f"{source_name}: {', '.join(matches)}",
            file=sys.stderr,
        )
        raise SystemExit(4)
    if not matches:
        continue

    if status not in terminal_statuses:
        print(
            f"invalid Pitest XML report: unsupported changed-file status {status!r}",
            file=sys.stderr,
        )
        raise SystemExit(4)
    mapped_mutations += 1
    if status not in {"SURVIVED", "NO_COVERAGE"}:
        continue

    if status == "NO_COVERAGE":
        finding_text = f"Uncovered Pitest mutant: {mutation.findtext('description') or 'no description'}"
        recommendation = "Add a test that executes this code path and asserts the intended behavior."
    else:
        finding_text = f"Surviving Pitest mutant: {mutation.findtext('description') or 'no description'}"
        recommendation = "Add an assertion that fails when the mutated code path executes."
    findings.append({
        "axis": "tests",
        "severity": "Medium",
        "location": f"{matches[0]}:{mutation.findtext('lineNumber') or '?'}",
        "finding": finding_text,
        "recommendation": recommendation,
        "confidence": 100,
        "source_tool": "pitest",
    })

if mapped_mutations == 0:
    print(
        "invalid Pitest XML report: no changed-file mutations were evaluated",
        file=sys.stderr,
    )
    raise SystemExit(4)

with open(sys.argv[2], "a", encoding="utf-8") as handle:
    for finding in findings:
        handle.write(json.dumps(finding) + "\n")
PY
  rc=$?
  if [[ $rc -ne 0 ]]; then
    sed -n '1,20p' "$err" >&2
    echo "ERROR: remediation: run '$repair_command' directly; ensure Pitest evaluates at least one mutant, emits canonical mutations.xml, and maps each package/source pair to one changed file (run one module at a time when needed), then rerun Code Ultrareview." >&2
    runtime_error "Pitest report could not be mapped reliably to changed files. See $err" \
      "$repair_command"
    return $?
  fi
}

if [[ $JS_APPLICABLE -eq 1 ]]; then
  run_stryker || exit $?
fi
if [[ $PY_APPLICABLE -eq 1 ]]; then
  run_mutmut || exit $?
fi
if [[ $JVM_APPLICABLE -eq 1 ]]; then
  run_pitest || exit $?
fi

if ! publish_findings "complete" 1 1; then
  exit 4
fi
exit 0
