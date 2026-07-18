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
if [[ -f "$REPO/package.json" ]] \
  && ! package_error="$(validate_package_manifest "$REPO/package.json")"; then
  echo "ERROR: invalid project manifest: $package_error" >&2
  echo "ERROR: remediation: repair package.json so it is valid JSON with object dependency maps, then rerun Code Ultrareview." >&2
  emit_rerun
  exit 2
fi
mkdir -p "$OUTPUT_DIR/raw"
FINDINGS_FINAL="$OUTPUT_DIR/mutation-findings.jsonl"
FINDINGS_OUT="$OUTPUT_DIR/.mutation-findings.pending.jsonl"
: >"$FINDINGS_FINAL"
: >"$FINDINGS_OUT"

cleanup_pending_findings() {
  rm -f "$FINDINGS_OUT"
}
trap cleanup_pending_findings EXIT

commit_findings() {
  mv -f "$FINDINGS_OUT" "$FINDINGS_FINAL"
}

set_mutation_coverage() {
  local status="$1" complete="$2" applicable="$3"
  python3 - "$SCOPE" "$status" "$complete" "$applicable" "$FINDINGS_FINAL" <<'PY'
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
temporary.write_text(
    json.dumps(scope, indent=2, sort_keys=False) + "\n",
    encoding="utf-8",
)
os.replace(temporary, path)
PY
}

if ! set_mutation_coverage "preflight" 0 unknown; then
  echo "ERROR: could not initialize mutation coverage in $SCOPE" >&2
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

package_declares() {
  local package="$1"
  [[ -f "$REPO/package.json" ]] || return 1
  python3 - "$REPO/package.json" "$package" <<'PY' >/dev/null 2>&1
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    package_json = json.load(handle)
declared = any(
    sys.argv[2] in (package_json.get(field) or {})
    for field in ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies")
)
raise SystemExit(0 if declared else 1)
PY
}

has_stryker_config() {
  local config
  for config in \
    stryker.config.js stryker.config.mjs stryker.config.cjs stryker.config.json \
    stryker.conf.js stryker.conf.mjs stryker.conf.cjs stryker.conf.json; do
    [[ -f "$REPO/$config" ]] && return 0
  done
  return 1
}

validate_stryker_json_configs() {
  python3 - "$REPO" <<'PY'
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
        raise SystemExit(0)
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
        import re
        text = pyproject.read_text(encoding="utf-8")
        section = re.search(
            r"(?ms)^\[tool\.mutmut\]\s*(.*?)(?=^\[|\Z)", text
        )
        if section and re.search(r"(?m)^source_paths\s*=", section.group(1)):
            raise SystemExit(0)
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
resolve_stryker() {
  local yarn_bin
  STRYKER_COMMAND=()
  if [[ -x "$REPO/node_modules/.bin/stryker" ]] && package_declares "@stryker-mutator/core"; then
    STRYKER_COMMAND=("$REPO/node_modules/.bin/stryker")
    return 0
  fi
  if package_declares "@stryker-mutator/core" \
    && [[ "$(detect_js_package_manager "$REPO")" == "yarn" ]]; then
    yarn_bin="$(command -v yarn 2>/dev/null || true)"
    if [[ -n "$yarn_bin" ]] \
      && env COREPACK_ENABLE_NETWORK=0 COREPACK_DEFAULT_TO_LATEST=0 \
        "$yarn_bin" --cwd "$REPO" bin stryker >/dev/null 2>&1; then
      STRYKER_COMMAND=(
        env COREPACK_ENABLE_NETWORK=0 COREPACK_DEFAULT_TO_LATEST=0
        "$yarn_bin" --cwd "$REPO" run -B stryker
      )
      return 0
    fi
  fi
  return 1
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
  if ! config_error="$(validate_stryker_json_configs)"; then
    invalid_mutation_input "$config_error" \
      "repair the reported JSON file, verify it with 'python3 -m json.tool <file>', then rerun Code Ultrareview"
    exit $?
  fi
  if ! package_declares "@stryker-mutator/core"; then
    record_missing "stryker" "@stryker-mutator/core is not declared in package.json" \
      "$(tool_install_command "$REPO" stryker)"
  elif ! resolve_stryker; then
    record_missing "stryker" "the declared Stryker binary is unavailable" \
      "$(tool_install_command "$REPO" stryker)"
  fi
  if ! has_stryker_config; then
    record_missing "stryker-config" "no stryker.config.* file is present" \
      "$(js_exec_command "$REPO" stryker) init"
  fi
fi

if [[ $PY_APPLICABLE -eq 1 ]]; then
  if ! config_error="$(validate_python_mutation_manifests)"; then
    invalid_mutation_input "$config_error" \
      "repair the reported manifest, validate setup.cfg with Python configparser or pyproject.toml with Python tomllib, then rerun Code Ultrareview"
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
    if [[ -x "$REPO/mvnw" ]]; then
      JVM_RUNNER="$REPO/mvnw"
    elif JVM_RUNNER="$(command -v mvn 2>/dev/null)"; then
      :
    else
      JVM_RUNNER=""
      record_missing "mvn" "Maven is not installed on PATH" \
        "restore the project's executable mvnw wrapper or $(tool_install_command "$REPO" mvn)"
    fi
  elif [[ -f "$REPO/build.gradle" || -f "$REPO/build.gradle.kts" ]]; then
    JVM_BUILD="gradle"
    if ! has_gradle_pitest_plugin; then
      record_missing "pitest-gradle" "the Gradle Pitest plugin is not declared" \
        "add the 'info.solidsoft.pitest' plugin to build.gradle(.kts), run './gradlew pitest' once, then rerun Code Ultrareview"
    fi
    if [[ ! -x "$REPO/gradlew" ]]; then
      record_missing "gradlew" "the project Gradle wrapper is missing or not executable" \
        "restore the project's executable gradlew wrapper, run './gradlew pitest' once, then rerun Code Ultrareview"
    fi
  else
    record_missing "pitest-build" "no supported JVM build manifest was found" \
      "configure Pitest in the project's existing build system (pitest-maven in pom.xml or info.solidsoft.pitest in build.gradle(.kts)), then rerun Code Ultrareview"
  fi
fi

render_preflight() {
  python3 - "$OUTPUT_DIR/mutation-preflight.json" \
    "$JS_APPLICABLE" "$PY_APPLICABLE" "$JVM_APPLICABLE" "$JVM_BUILD" \
    "${#MISSING_ROWS[@]}" ${MISSING_ROWS[@]+"${MISSING_ROWS[@]}"} <<'PY'
import json
import sys

path = sys.argv[1]
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
with open(path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
print(json.dumps(payload, indent=2))
PY
}

render_preflight >"$OUTPUT_DIR/raw/mutation-preflight.stdout"

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
  commit_findings
  set_mutation_coverage "not-applicable" 1 0 || exit 4
  echo "INFO: mutation testing is not applicable to the changed files." >&2
  exit 0
fi

if [[ "${MUTATION_DRY_RUN:-}" == "1" ]]; then
  commit_findings
  set_mutation_coverage "dry-run" 0 1 || exit 4
  echo "INFO: MUTATION_DRY_RUN=1; prerequisites are complete and no mutation process was started." >&2
  exit 0
fi

runtime_error() {
  set_mutation_coverage "failed" 0 1 || true
  echo "ERROR: $1" >&2
  emit_rerun
  return 4
}

run_stryker() {
  local report marker raw err mutate rc path
  local mutate_files=()
  if ! resolve_stryker; then
    runtime_error "Stryker disappeared after preflight. Install with $(tool_install_command "$REPO" stryker)"
    return $?
  fi
  report="$REPO/reports/mutation/mutation.json"
  marker="$(mktemp -t stryker_report_XXXX)"
  raw="$OUTPUT_DIR/raw/stryker.log"
  err="$OUTPUT_DIR/raw/stryker.stderr"
  for path in "${JS_FILES[@]}"; do
    mutate_files+=("./$path")
  done
  mutate="$(IFS=,; printf '%s' "${mutate_files[*]}")"

  (
    cd "$REPO" && run_with_timeout "$TIMEOUT" "${STRYKER_COMMAND[@]}" run \
      --reporters json --mutate "$mutate"
  ) >"$raw" 2>"$err"
  rc=$?
  if [[ $rc -eq 124 ]]; then
    rm -f "$marker"
    runtime_error "Stryker timed out after ${TIMEOUT}s; its process group was terminated. See $err"
    return $?
  fi
  if [[ $rc -ne 0 && $rc -ne 1 ]]; then
    rm -f "$marker"
    runtime_error "Stryker failed with exit code $rc. See $err"
    return $?
  fi
  if [[ ! -f "$report" || ! "$report" -nt "$marker" ]]; then
    rm -f "$marker"
    runtime_error "Stryker did not produce a fresh JSON report at reports/mutation/mutation.json. See $err"
    return $?
  fi
  rm -f "$marker"

  python3 - "$report" "$FINDINGS_OUT" <<'PY' 2>>"$err"
import json
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

mutant_count = 0
with open(sys.argv[2], "a", encoding="utf-8") as handle:
    for file_path, payload in files.items():
        if not isinstance(file_path, str) or not file_path or not isinstance(payload, dict):
            print("invalid Stryker JSON report: malformed file entry", file=sys.stderr)
            raise SystemExit(4)
        mutants = payload.get("mutants")
        if not isinstance(mutants, list):
            print(f"invalid Stryker JSON report: {file_path} has no mutants list", file=sys.stderr)
            raise SystemExit(4)
        for mutant in mutants:
            mutant_count += 1
            if not isinstance(mutant, dict):
                print(f"invalid Stryker JSON report: malformed mutant in {file_path}", file=sys.stderr)
                raise SystemExit(4)
            status = mutant.get("status")
            if not isinstance(status, str) or not status:
                print(f"invalid Stryker JSON report: mutant in {file_path} has no status", file=sys.stderr)
                raise SystemExit(4)
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
            location = f"{file_path}:{line}:{column}" if line else file_path
            if status == "NoCoverage":
                finding_text = f"Uncovered mutant ({mutant.get('mutatorName', '?')}): {mutant.get('description', 'no description')}"
                recommendation = "Add a test that executes this code path and asserts the intended behavior."
            else:
                finding_text = f"Surviving mutant ({mutant.get('mutatorName', '?')}): {mutant.get('description', 'no description')}"
                recommendation = "Add an assertion that fails when the mutated code path executes."
            finding = {
                "axis": "tests",
                "severity": "Medium",
                "location": location,
                "finding": finding_text,
                "recommendation": recommendation,
                "confidence": 100,
                "source_tool": "stryker",
            }
            handle.write(json.dumps(finding) + "\n")
if mutant_count == 0:
    print("invalid Stryker JSON report: no mutants were evaluated", file=sys.stderr)
    raise SystemExit(4)
PY
  rc=$?
  if [[ $rc -ne 0 ]]; then
    sed -n '1,20p' "$err" >&2
    echo "ERROR: remediation: run '$(js_exec_command "$REPO" stryker) run --reporters json' directly; ensure Stryker evaluates at least one mutant in the changed files and writes the canonical reports/mutation/mutation.json schema, then rerun Code Ultrareview." >&2
    runtime_error "Stryker report could not be parsed reliably. See $err"
    return $?
  fi
}

run_mutmut() {
  local command raw err results actionable shows rc status mutant show_rc
  command="$(command -v mutmut 2>/dev/null || true)"
  if [[ -z "$command" ]]; then
    runtime_error "mutmut disappeared after preflight. Install with $(tool_install_command "$REPO" mutmut)"
    return $?
  fi
  raw="$OUTPUT_DIR/raw/mutmut.log"
  err="$OUTPUT_DIR/raw/mutmut.stderr"
  results="$OUTPUT_DIR/raw/mutmut-results.log"
  actionable="$OUTPUT_DIR/raw/mutmut-actionable.tsv"
  shows="$OUTPUT_DIR/raw/mutmut-shows.txt"

  (cd "$REPO" && run_with_timeout "$TIMEOUT" "$command" run) >"$raw" 2>"$err"
  rc=$?
  if [[ $rc -eq 124 ]]; then
    runtime_error "mutmut timed out after ${TIMEOUT}s; its process group was terminated. See $err"
    return $?
  fi
  if [[ $rc -ne 0 ]]; then
    runtime_error "mutmut failed with exit code $rc. See $err"
    return $?
  fi
  (cd "$REPO" && run_with_timeout "$TIMEOUT" "$command" results) >"$results" 2>>"$err"
  rc=$?
  if [[ $rc -eq 124 ]]; then
    runtime_error "mutmut results timed out after ${TIMEOUT}s; its process group was terminated. See $err"
    return $?
  fi
  if [[ $rc -ne 0 ]]; then
    runtime_error "mutmut results failed with exit code $rc. See $err"
    return $?
  fi
  python3 - "$results" "$actionable" <<'PY' 2>>"$err"
import pathlib
import sys

valid_statuses = {
    "killed",
    "survived",
    "no tests",
    "skipped",
    "suspicious",
    "timeout",
    "check was interrupted by user",
    "not checked",
    "segfault",
}
actionable_statuses = {"survived", "no tests", "suspicious"}
incomplete_statuses = {"check was interrupted by user", "not checked"}
rows = []
incomplete = []
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
    if status in actionable_statuses:
        rows.append((status, mutant))
if incomplete:
    print(
        "incomplete mutmut results: " + ", ".join(incomplete[:5]),
        file=sys.stderr,
    )
    raise SystemExit(4)
with pathlib.Path(sys.argv[2]).open("w", encoding="utf-8") as handle:
    for status, mutant in rows:
        handle.write(f"{status}\t{mutant}\n")
PY
  rc=$?
  if [[ $rc -ne 0 ]]; then
    sed -n '1,20p' "$err" >&2
    echo "ERROR: remediation: run 'mutmut results' directly; repair or update mutmut with '$(tool_install_command "$REPO" mutmut)' until every non-empty result line has a documented status, then rerun Code Ultrareview." >&2
    runtime_error "mutmut results output is incomplete or malformed. See $err"
    return $?
  fi
  : >"$shows"
  while IFS=$'\t' read -r status mutant; do
    [[ -n "$mutant" ]] || continue
    printf '=== %s\t%s ===\n' "$status" "$mutant" >>"$shows"
    (cd "$REPO" && run_with_timeout 15 "$command" show "$mutant") >>"$shows" 2>>"$err"
    show_rc=$?
    if [[ $show_rc -eq 124 ]]; then
      runtime_error "mutmut show timed out after 15s for '$mutant'; its process group was terminated. See $err"
      return $?
    fi
    if [[ $show_rc -ne 0 ]]; then
      runtime_error "mutmut show failed for '$mutant' with exit code $show_rc. See $err"
      return $?
    fi
  done <"$actionable"

  python3 - "$shows" "$FINDINGS_OUT" "${PY_FILES[@]}" <<'PY' 2>>"$err"
import json
import pathlib
import re
import sys

text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
changed = {pathlib.PurePosixPath(path).as_posix() for path in sys.argv[3:]}
blocks = re.split(r"^=== ([^\t]+)\t(.+) ===$", text, flags=re.MULTILINE)
if len(blocks) == 1:
    raise SystemExit(0)

findings = []
for index in range(1, len(blocks), 3):
    status = blocks[index]
    mutant = blocks[index + 1]
    body = blocks[index + 2]
    file_match = re.search(r"^---\s+(?:a/)?([^\t\n]+)", body, re.MULTILINE)
    line_match = re.search(r"^@@\s+-\d+(?:,\d+)?\s+\+(\d+)", body, re.MULTILINE)
    if not file_match:
        print(f"cannot locate source file for mutmut survivor {mutant}", file=sys.stderr)
        raise SystemExit(4)
    file_path = pathlib.PurePosixPath(file_match.group(1).strip()).as_posix()
    if file_path not in changed:
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

with open(sys.argv[2], "a", encoding="utf-8") as handle:
    for finding in findings:
        handle.write(json.dumps(finding) + "\n")
PY
  rc=$?
  if [[ $rc -ne 0 ]]; then
    sed -n '1,20p' "$err" >&2
    runtime_error "mutmut survivor output could not be mapped reliably. See $err"
    return $?
  fi
}

run_pitest() {
  local raw err marker rc report report_root
  raw="$OUTPUT_DIR/raw/pitest.log"
  err="$OUTPUT_DIR/raw/pitest.stderr"
  marker="$(mktemp -t pitest_report_XXXX)"
  if [[ "$JVM_BUILD" == "maven" ]]; then
    report_root="$REPO/target/pit-reports"
    (cd "$REPO" && run_with_timeout "$TIMEOUT" "$JVM_RUNNER" -q -B pitest:mutationCoverage) >"$raw" 2>"$err"
  elif [[ "$JVM_BUILD" == "gradle" ]]; then
    report_root="$REPO/build/reports/pitest"
    (cd "$REPO" && run_with_timeout "$TIMEOUT" "$REPO/gradlew" --no-daemon pitest) >"$raw" 2>"$err"
  else
    rm -f "$marker"
    runtime_error "Pitest has no validated JVM build runner. Rerun mutation preflight."
    return $?
  fi
  rc=$?
  if [[ $rc -eq 124 ]]; then
    rm -f "$marker"
    runtime_error "Pitest timed out after ${TIMEOUT}s; its process group was terminated. See $err"
    return $?
  fi
  if [[ $rc -ne 0 ]]; then
    rm -f "$marker"
    runtime_error "Pitest failed with exit code $rc. See $err"
    return $?
  fi
  report="$(find "$report_root" -type f -name mutations.xml -newer "$marker" -print 2>/dev/null | sort | tail -n 1)"
  rm -f "$marker"
  if [[ -z "$report" || ! -f "$report" ]]; then
    runtime_error "Pitest did not produce a fresh mutations.xml report under $report_root. See $err"
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
    if status not in {"SURVIVED", "NO_COVERAGE"}:
        continue
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

with open(sys.argv[2], "a", encoding="utf-8") as handle:
    for finding in findings:
        handle.write(json.dumps(finding) + "\n")
PY
  rc=$?
  if [[ $rc -ne 0 ]]; then
    sed -n '1,20p' "$err" >&2
    if [[ "$JVM_BUILD" == "maven" ]]; then
      echo "ERROR: remediation: run '$JVM_RUNNER -q -B pitest:mutationCoverage' directly; ensure Pitest evaluates at least one mutant, emits canonical mutations.xml, and maps each package/source pair to one changed file (run one module at a time when needed), then rerun Code Ultrareview." >&2
    else
      echo "ERROR: remediation: run '$REPO/gradlew --no-daemon pitest' directly; ensure Pitest evaluates at least one mutant, emits canonical mutations.xml, and maps each package/source pair to one changed file (run one module at a time when needed), then rerun Code Ultrareview." >&2
    fi
    runtime_error "Pitest report could not be mapped reliably to changed files. See $err"
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

commit_findings
if ! set_mutation_coverage "complete" 1 1; then
  echo "ERROR: mutation findings completed but coverage state could not be persisted." >&2
  emit_rerun
  exit 4
fi
exit 0
