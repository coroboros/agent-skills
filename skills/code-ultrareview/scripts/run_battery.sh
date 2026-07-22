#!/usr/bin/env bash
# Phase 2 tool battery — code-ultrareview.
#
# Reads scope.json (repo_kind + languages + files_touched_list), runs
# deterministic CLIs per the dispatch matrix below, captures raw outputs,
# and invokes battery_ingest.py to emit canonical findings as JSONL.
#
# Try order per tool: directly declared project binary -> PATH binary.
# The battery preflights every analyzer applicable to the requested scope. A
# missing analyzer blocks the review before any tool runs and prints the exact
# install command. The battery NEVER auto-installs.
#
# Usage:
#   run_battery.sh --scope <scope.json> --output-dir <dir> [--repo <path>]
#                  [--axes <list>] [--dry-run]
#
# Exit 0 on complete success, 2 on invalid input, 3 when a required analyzer
# is missing, and 4 when an analyzer cannot execute reliably.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INGEST="$SCRIPT_DIR/battery_ingest.py"
PROCESS_TIMEOUT="$SCRIPT_DIR/process_timeout.py"
PERF_RULES_DIR="$SCRIPT_DIR/../references/perf-rules"
MARKDOWNLINT_BASE_CONFIG="$SCRIPT_DIR/../references/markdownlint-base.markdownlint-cli2.jsonc"
# shellcheck source-path=SCRIPTDIR
# shellcheck source=install-guidance.sh
source "$SCRIPT_DIR/install-guidance.sh"

SCOPE=""
OUTPUT_DIR=""
REPO="."
DRY_RUN=0
AXES=""
TOOL_TIMEOUT="${BATTERY_TIMEOUT:-300}"
JSCPD_MIN_LINES="${JSCPD_MIN_LINES:-15}"
JSCPD_MIN_TOKENS="${JSCPD_MIN_TOKENS:-100}"
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

BATTERY_RERUN="$(format_command bash "$SCRIPT_DIR/run_battery.sh" ${ORIGINAL_ARGS[@]+"${ORIGINAL_ARGS[@]}"})"

emit_rerun() {
  echo "ERROR: rerun: $BATTERY_RERUN" >&2
}

# Dispatch matrix — single source of truth, format
# "<tool>|<canonical-axes>|<coverage>". Install commands are generated from
# the target repo by install-guidance.sh so JavaScript guidance matches npm,
# pnpm, Yarn, or Bun exactly.

# shellcheck disable=SC2034
BATTERY_TABLE=(
  "knip|simplification|JS/TS dead code"
  "jscpd|simplification|duplication"
  "markdownlint-cli2|documentation|Markdown lint"
  "api-extractor|design-api|TS public surface"
  "lizard|simplification|cyclomatic complexity"
  "vulture|simplification|dead Python code"
  "semgrep|performance|bundled static performance patterns"
  "vale|documentation|prose lint"
  "oasdiff|design-api|OpenAPI breaking changes"
  "atlas|design-api|configured DB migration lint"
  "deadcode|simplification|Go unreachable code"
  "gocyclo|simplification|Go complexity"
  "dupl|simplification|Go duplication"
  "cargo-machete|simplification|Rust unused dependencies"
)

usage() {
  cat <<'EOF' >&2
Usage: run_battery.sh --scope <scope.json> --output-dir <dir> [options]

Required:
  --scope <path>        scope.json from scripts/scope.py
  --output-dir <path>   directory for raw/, tool-findings.jsonl, tools-skipped.json

Options:
  --repo <path>         repo root (default: cwd)
  --axes <list>         comma-separated canonical axes (default: all)
  --timeout <seconds>   per-analyzer timeout (default: 300)
  --dry-run             print dispatch plan as JSON, do not run tools

Exit 0 complete; 2 invalid input; 3 missing analyzer; 4 analyzer failure.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope) SCOPE="${2:-}"; shift 2 ;;
    --output-dir) OUTPUT_DIR="${2:-}"; shift 2 ;;
    --repo) REPO="${2:-}"; shift 2 ;;
    --axes) AXES="${2:-}"; shift 2 ;;
    --timeout) TOOL_TIMEOUT="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
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
if [[ ! "$TOOL_TIMEOUT" =~ ^[1-9][0-9]*$ ]]; then
  echo "ERROR: timeout must be a positive integer: $TOOL_TIMEOUT" >&2
  exit 2
fi
if [[ ! "$JSCPD_MIN_LINES" =~ ^[1-9][0-9]*$ ]]; then
  echo "ERROR: JSCPD_MIN_LINES must be a positive integer: $JSCPD_MIN_LINES" >&2
  exit 2
fi
if [[ ! "$JSCPD_MIN_TOKENS" =~ ^[1-9][0-9]*$ ]]; then
  echo "ERROR: JSCPD_MIN_TOKENS must be a positive integer: $JSCPD_MIN_TOKENS" >&2
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

FINDINGS_FINAL="$OUTPUT_DIR/tool-findings.jsonl"
PREFLIGHT_FINAL="$OUTPUT_DIR/tool-preflight.json"

# Invalidate the previous public result before validating project manifests or
# resolving analyzers. A failed rerun must never leave a stale complete verdict.
if ! python3 - "$SCOPE" "$AXES" <<'PY'
import json
import os
from pathlib import Path
import sys

scope_path = Path(sys.argv[1])
selected_axes = [axis.strip() for axis in sys.argv[2].split(",") if axis.strip()]
with scope_path.open(encoding="utf-8") as handle:
    scope = json.load(handle)
scope["tools_dispatched"] = []
scope["tools_missing"] = []
scope["tools_skipped"] = []
scope["tool_coverage"] = {
    "complete": False,
    "selected_axes": selected_axes,
    "explicit_scope": bool(selected_axes),
    "applicable": [],
    "executed": [],
}
scope["coverage_complete"] = False
temporary = scope_path.with_name(f".{scope_path.name}.{os.getpid()}.tmp")
temporary.write_text(
    json.dumps(scope, indent=2, sort_keys=False) + "\n",
    encoding="utf-8",
)
os.replace(temporary, scope_path)
PY
then
  rm -f "$FINDINGS_FINAL" 2>/dev/null || true
  echo "ERROR: tool coverage state could not be invalidated in $SCOPE" >&2
  echo "ERROR: remediation: verify that the scope directory is writable and supports atomic replacement, then rerun Code Ultrareview." >&2
  emit_rerun
  exit 4
fi
if ! rm -f "$FINDINGS_FINAL"; then
  echo "ERROR: stale analyzer findings could not be removed from $FINDINGS_FINAL" >&2
  echo "ERROR: remediation: verify that $OUTPUT_DIR is writable, remove the stale findings file, then rerun Code Ultrareview." >&2
  emit_rerun
  exit 4
fi
if ! rm -f "$PREFLIGHT_FINAL"; then
  echo "ERROR: stale analyzer preflight could not be removed from $PREFLIGHT_FINAL" >&2
  echo "ERROR: remediation: verify that $OUTPUT_DIR is writable, remove the stale preflight path, then rerun Code Ultrareview." >&2
  emit_rerun
  exit 4
fi
if ! mkdir -p "$OUTPUT_DIR/raw"; then
  echo "ERROR: analyzer output directory could not be created: $OUTPUT_DIR/raw" >&2
  echo "ERROR: remediation: verify that $OUTPUT_DIR is writable, then rerun Code Ultrareview." >&2
  emit_rerun
  exit 4
fi

# scope.json field extraction via python3 — already a hard dependency.
_scope_field() {
  # Args: <jq-style dot path>. Returns one value per line.
  python3 - "$SCOPE" "$1" <<'PY'
import json, sys
path = sys.argv[2]
with open(sys.argv[1], encoding="utf-8") as f:
    data = json.load(f)
cur = data
for key in path.lstrip(".").split("."):
    if not key:
        continue
    if isinstance(cur, dict):
        cur = cur.get(key)
    else:
        cur = None
    if cur is None:
        break
if cur is None:
    sys.exit(0)
if isinstance(cur, list):
    for item in cur:
        print(item)
else:
    print(cur)
PY
}

# Portable line-array population (bash 3.2 lacks `mapfile`).
LANGUAGES=()
while IFS= read -r _line; do
  [[ -n "$_line" ]] && LANGUAGES+=("$_line")
done < <(_scope_field languages)

FILES_TOUCHED=()
while IFS= read -r _line; do
  [[ -n "$_line" ]] && FILES_TOUCHED+=("$_line")
done < <(_scope_field files_touched_list)

# shellcheck disable=SC2034 # install-guidance.sh consumes this sourced-state array.
JS_RELEVANT_FILES=()
if [[ ${#FILES_TOUCHED[@]} -gt 0 ]]; then
  # shellcheck disable=SC2034 # install-guidance.sh consumes this sourced-state array.
  JS_RELEVANT_FILES=("${FILES_TOUCHED[@]}")
fi
if ! package_error="$(validate_relevant_package_manifests "$REPO")"; then
  echo "ERROR: invalid project manifest: $package_error" >&2
  echo "ERROR: remediation: repair package.json at the reported path so it is valid JSON with object dependency maps, then rerun Code Ultrareview." >&2
  emit_rerun
  exit 2
fi

has_lang() {
  local target="$1" l
  if [[ ${#LANGUAGES[@]} -eq 0 ]]; then
    return 1
  fi
  for l in "${LANGUAGES[@]}"; do
    [[ "$l" == "$target" ]] && return 0
  done
  return 1
}

has_existing_file_match() {
  local pat="$1" f
  if [[ ${#FILES_TOUCHED[@]} -eq 0 ]]; then
    return 1
  fi
  for f in "${FILES_TOUCHED[@]}"; do
    if [[ "$f" =~ $pat && -f "$REPO/$f" ]]; then
      return 0
    fi
  done
  return 1
}

has_repo_file() {
  # Args: <relative-path>
  [[ -f "$REPO/$1" ]]
}

# Dispatch decision — mirrors SKILL.md Phase 2 description.
SELECTED_AXES=()
if [[ -n "$AXES" ]]; then
  IFS=',' read -r -a SELECTED_AXES <<< "$AXES"
  for _axis in "${SELECTED_AXES[@]}"; do
    _axis="${_axis//[[:space:]]/}"
    case "$_axis" in
      correctness|simplification|tests|documentation|style|intent|design-api|performance|coherence) ;;
      *) echo "ERROR: unknown axis: $_axis" >&2; exit 2 ;;
    esac
  done
fi

tool_axes() {
  local tool="$1" row name rest
  for row in "${BATTERY_TABLE[@]}"; do
    name="${row%%|*}"
    if [[ "$name" == "$tool" ]]; then
      rest="${row#*|}"
      printf '%s\n' "${rest%%|*}"
      return 0
    fi
  done
  printf 'unknown\n'
}

coverage_hint() {
  local tool="$1" row name rest
  for row in "${BATTERY_TABLE[@]}"; do
    name="${row%%|*}"
    if [[ "$name" == "$tool" ]]; then
      rest="${row#*|}"
      printf '%s\n' "${rest#*|}"
      return 0
    fi
  done
  printf 'unknown\n'
}

axis_selected_for_tool() {
  local tool="$1" axes selected candidate
  [[ ${#SELECTED_AXES[@]} -eq 0 ]] && return 0
  axes=",$(tool_axes "$tool"),"
  for selected in "${SELECTED_AXES[@]}"; do
    candidate="${selected//[[:space:]]/}"
    [[ "$axes" == *",$candidate,"* ]] && return 0
  done
  return 1
}

want_tool() {
  # Args: <tool>. Returns 0 if dispatch matrix says yes for this scope.
  local tool="$1"
  axis_selected_for_tool "$tool" || return 1
  case "$tool" in
    knip)
      has_lang typescript || has_lang javascript
      ;;
    jscpd)
      has_existing_file_match '\.(py|js|jsx|ts|tsx|mjs|cjs|go|rs|java|rb|php|cs|cpp|c|h|hpp|swift|kt)$'
      ;;
    markdownlint-cli2)
      has_existing_file_match '\.md$'
      ;;
    api-extractor)
      has_repo_file "api-extractor.json"
      ;;
    lizard)
      has_existing_file_match '\.(py|js|jsx|ts|tsx|mjs|cjs|go|rs|java|rb|php|cs|cpp|c|h|hpp|swift|kt)$'
      ;;
    vulture)
      has_lang python
      ;;
    semgrep)
      has_existing_file_match '\.(py|js|jsx|ts|tsx|mjs|cjs|go|rs|java|rb|php|cs|cpp|c|h|hpp|swift|kt)$'
      ;;
    vale)
      has_repo_file ".vale.ini" && has_existing_file_match '\.(md|txt|rst|adoc)$'
      ;;
    oasdiff)
      has_existing_file_match '(openapi|swagger)\.(ya?ml|json)$'
      ;;
    atlas)
      has_repo_file "atlas.hcl" && has_existing_file_match '(^|/)migrations/'
      ;;
    deadcode)
      has_lang go
      ;;
    gocyclo)
      has_lang go
      ;;
    dupl)
      has_lang go
      ;;
    cargo-machete)
      has_lang rust
      ;;
    *)
      return 1
      ;;
  esac
}

install_cmd() {
  tool_repair_command "$REPO" "$1"
}

DISPATCHED=()
mark_dispatched() {
  DISPATCHED+=("$1")
}

# Tool runners. Each writes raw output to $OUTPUT_DIR/raw/<tool>.<ext>.
# JavaScript tools prefer a directly declared repository dependency;
# every tool may fall back to an already-installed PATH command.

RESOLVED_COMMAND=()
RESOLVED_WRAPPER=""

set_js_relevant_files_for_tool() {
  local tool="$1" file pattern=""
  JS_RELEVANT_FILES=()
  case "$tool" in
    knip) pattern='\.(js|jsx|ts|tsx|mjs|cjs)$' ;;
    jscpd) pattern='\.(py|js|jsx|ts|tsx|mjs|cjs|go|rs|java|rb|php|cs|cpp|c|h|hpp|swift|kt)$' ;;
    markdownlint-cli2) pattern='\.md$' ;;
    api-extractor) pattern='\.(ts|tsx)$' ;;
  esac
  for file in "${FILES_TOUCHED[@]}"; do
    [[ -n "$pattern" && "$file" =~ $pattern ]] \
      && JS_RELEVANT_FILES+=("$file")
  done
  if [[ "$tool" == "api-extractor" && -f "$REPO/api-extractor.json" ]]; then
    JS_RELEVANT_FILES+=("api-extractor.json")
  fi
}

resolve_tool() {
  local tool="$1"
  local package="" path_tool
  RESOLVED_COMMAND=()
  RESOLVED_WRAPPER=""
  case "$tool" in
    knip) package="knip" ;;
    jscpd) package="jscpd" ;;
    markdownlint-cli2) package="markdownlint-cli2" ;;
    api-extractor) package="@microsoft/api-extractor" ;;
  esac
  if [[ -n "$package" ]]; then
    set_js_relevant_files_for_tool "$tool"
    if resolve_declared_js_binary "$REPO" "$package" "$tool"; then
      RESOLVED_COMMAND=("${DECLARED_JS_COMMAND[@]}")
      RESOLVED_WRAPPER="$DECLARED_JS_WRAPPER"
      return 0
    fi
    # A declared dependency is authoritative. Do not replace a missing project
    # install with a potentially different global analyzer version.
    package_declares_js_dependency "$REPO" "$package" && return 1
  fi
  path_tool="$(command -v "$tool" 2>/dev/null || true)"
  [[ -n "$path_tool" ]] || return 1
  RESOLVED_COMMAND=("$path_tool")
  RESOLVED_WRAPPER="path"
}

CAPTURE_RC=0
_capture() {
  # Args: <out-file> <stderr-file> -- <cmd...>
  local out="$1" err="$2"; shift 2
  if [[ "$1" == "--" ]]; then shift; fi
  python3 "$PROCESS_TIMEOUT" \
    --timeout "$TOOL_TIMEOUT" \
    --cwd "$REPO" \
    --stdout "$out" \
    --stderr "$err" \
    -- "$@"
  CAPTURE_RC=$?
  return 0
}

capture_succeeded() {
  local tool="$1" rc="$2" err="$3"
  if [[ "$rc" -eq 124 ]]; then
    echo "ERROR: $tool timed out after ${TOOL_TIMEOUT}s; its process group was terminated." >&2
    echo "ERROR: analyzer stderr: $err" >&2
    echo "ERROR: repair/install: $(install_cmd "$tool")" >&2
    echo "ERROR: remediation: verify '$tool' independently, then rerun Code Ultrareview with --timeout <seconds>." >&2
    emit_rerun
    return 4
  fi
  case "$tool:$rc" in
    knip:0|knip:1|jscpd:0|jscpd:1|markdownlint-cli2:0|markdownlint-cli2:1|\
    api-extractor:0|api-extractor:1|lizard:0|vulture:0|vulture:3|\
    semgrep:0|semgrep:1|vale:0|vale:1|oasdiff:0|oasdiff:1|\
    atlas:0|atlas:1|deadcode:0|gocyclo:0|dupl:0|cargo-machete:0|\
    cargo-machete:1)
      return 0
      ;;
  esac

  echo "ERROR: $tool failed with exit code $rc; Code Ultrareview is incomplete." >&2
  echo "ERROR: analyzer stderr: $err" >&2
  echo "ERROR: repair/install: $(install_cmd "$tool")" >&2
  echo "ERROR: remediation: repair the analyzer, then rerun Code Ultrareview." >&2
  emit_rerun
  return 4
}

print_resolved_version_command() {
  [[ ${#RESOLVED_COMMAND[@]} -gt 0 ]] || return 0
  printf 'ERROR: verify:' >&2
  printf ' %q' "${RESOLVED_COMMAND[@]}" >&2
  printf ' --version\n' >&2
}

require_json_file() {
  local tool="$1" path="$2" err="${3:-}"
  if ! python3 - "$tool" "$path" <<'PY' >/dev/null 2>&1
import json
import os
from pathlib import Path
import sys

tool, path = sys.argv[1:3]
with open(path, encoding="utf-8") as handle:
    payload = json.load(handle)

valid = False
if tool == "knip":
    valid = (
        isinstance(payload, list)
        or (
            isinstance(payload, dict)
            and isinstance(payload.get("issues"), list)
        )
    )
elif tool == "jscpd":
    valid = isinstance(payload, dict) and isinstance(payload.get("duplicates"), list)
elif tool == "semgrep":
    valid = (
        isinstance(payload, dict)
        and isinstance(payload.get("results"), list)
        and isinstance(payload.get("errors"), list)
    )
elif tool == "vale":
    valid = isinstance(payload, dict) and all(
        isinstance(value, list) for value in payload.values()
    )
elif tool == "oasdiff":
    valid = isinstance(payload, list)
elif tool == "atlas":
    valid = isinstance(payload, dict) and isinstance(payload.get("Files"), list)
else:
    valid = payload is not None

raise SystemExit(0 if valid else 1)
PY
  then
    echo "ERROR: $tool did not produce its documented JSON schema at $path." >&2
    [[ -z "$err" ]] || echo "ERROR: analyzer stderr: $err" >&2
    print_resolved_version_command
    echo "ERROR: repair/install: $(install_cmd "$tool")" >&2
    echo "ERROR: remediation: inspect the report and stderr, verify the analyzer version, repair or update it, then rerun Code Ultrareview." >&2
    emit_rerun
    return 4
  fi
}

require_semgrep_without_errors() {
  local report="$1" err="$2"
  if ! python3 - "$report" <<'PY' >&2
import json
import os
from pathlib import Path
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    errors = json.load(handle).get("errors", [])
if errors:
    print("ERROR: Semgrep reported analyzer errors:")
    for item in errors:
        print(json.dumps(item, sort_keys=True))
    raise SystemExit(1)
PY
  then
    echo "ERROR: Semgrep report: $report" >&2
    echo "ERROR: Semgrep stderr: $err" >&2
    echo "ERROR: repair/install: $(install_cmd semgrep)" >&2
    echo "ERROR: remediation: repair the rules or analyzer, then rerun Code Ultrareview." >&2
    emit_rerun
    return 4
  fi
}

require_nonempty_file() {
  local tool="$1" path="$2"
  if [[ ! -s "$path" ]]; then
    echo "ERROR: $tool completed without the expected report at $path." >&2
    echo "ERROR: repair/install: $(install_cmd "$tool")" >&2
    echo "ERROR: remediation: repair the analyzer, then rerun Code Ultrareview." >&2
    emit_rerun
    return 4
  fi
}

require_findings_report() {
  local tool="$1" rc="$2" path="$3"
  [[ "$rc" -eq 0 || -s "$path" ]] && return 0
  echo "ERROR: $tool exited with its findings code but produced no parseable report at $path." >&2
  echo "ERROR: repair/install: $(install_cmd "$tool")" >&2
  echo "ERROR: remediation: repair the analyzer or its output configuration, verify it independently, then rerun Code Ultrareview." >&2
  emit_rerun
  return 4
}

resolve_required_tool() {
  local tool="$1"
  if ! resolve_tool "$tool"; then
    echo "ERROR: $tool disappeared after preflight; install: $(install_cmd "$tool")" >&2
    emit_rerun
    return 3
  fi
}

report_path_for_tool() {
  case "$1" in
    knip|jscpd|semgrep|vale|oasdiff|atlas)
      printf '%s/raw/%s.json\n' "$OUTPUT_DIR" "$1"
      ;;
    markdownlint-cli2|api-extractor|lizard|vulture|deadcode|gocyclo|dupl|cargo-machete)
      printf '%s/raw/%s.txt\n' "$OUTPUT_DIR" "$1"
      ;;
    *)
      printf '%s/raw\n' "$OUTPUT_DIR"
      ;;
  esac
}

run_knip() {
  local out="$OUTPUT_DIR/raw/knip.json"
  local err="$OUTPUT_DIR/raw/knip.stderr"
  resolve_required_tool knip || return $?
  _capture "$out" "$err" -- "${RESOLVED_COMMAND[@]}" --reporter json --no-progress
  capture_succeeded knip "$CAPTURE_RC" "$err" || return $?
  require_json_file knip "$out" "$err" || return $?
  mark_dispatched knip
}

run_jscpd() {
  local out="$OUTPUT_DIR/raw/jscpd.json"
  local err="$OUTPUT_DIR/raw/jscpd.stderr"
  # Scope to changed code files only — pre-existing-tier findings on
  # unchanged paths surface from LLM axis review, not the deterministic battery.
  local code_files=()
  local f relative input_dir report_dir capture_rc
  if [[ ${#FILES_TOUCHED[@]} -gt 0 ]]; then
    for f in "${FILES_TOUCHED[@]}"; do
      [[ "$f" =~ \.(py|js|jsx|ts|tsx|mjs|cjs|go|rs|java|rb|php|cs|cpp|c|h|hpp|swift|kt)$ && -f "$REPO/$f" ]] && code_files+=("./$f")
    done
  fi
  if [[ ${#code_files[@]} -eq 0 ]]; then
    return 0
  fi
  resolve_required_tool jscpd || return $?

  # jscpd 5 loses file names in JSON when multiple file arguments are passed.
  # A temporary tree preserves repository-relative names while keeping the
  # deterministic scan strictly bounded to changed files.
  input_dir="$(mktemp -d "$OUTPUT_DIR/raw/jscpd-input.XXXXXX")" || return 4
  report_dir="$(mktemp -d "$OUTPUT_DIR/raw/jscpd-report.XXXXXX")" || {
    rm -rf -- "$input_dir"
    return 4
  }
  for f in "${code_files[@]}"; do
    relative="${f#./}"
    mkdir -p "$input_dir/$(dirname "$relative")" || {
      rm -rf -- "$input_dir" "$report_dir"
      return 4
    }
    cp -- "$REPO/$relative" "$input_dir/$relative" || {
      rm -rf -- "$input_dir" "$report_dir"
      return 4
    }
  done

  rm -f "$out"
  _capture "$out" "$err" -- "${RESOLVED_COMMAND[@]}" \
    --silent \
    --min-lines "$JSCPD_MIN_LINES" \
    --min-tokens "$JSCPD_MIN_TOKENS" \
    --reporters json \
    --output "$report_dir" \
    "$input_dir"
  capture_rc="$CAPTURE_RC"
  if [[ -f "$report_dir/jscpd-report.json" ]]; then
    cp "$report_dir/jscpd-report.json" "$out"
  fi
  rm -rf -- "$input_dir" "$report_dir"
  capture_succeeded jscpd "$capture_rc" "$err" || return $?
  if [[ ! -f "$out" ]]; then
    echo "ERROR: jscpd completed without its JSON report; stderr: $err" >&2
    echo "ERROR: repair/install: $(install_cmd jscpd)" >&2
    emit_rerun
    return 4
  fi
  require_json_file jscpd "$out" "$err" || return $?
  mark_dispatched jscpd
}

run_markdownlint() {
  local out="$OUTPUT_DIR/raw/markdownlint-cli2.txt"
  local err="$OUTPUT_DIR/raw/markdownlint-cli2.stderr"
  local md_files=()
  local f
  if [[ ${#FILES_TOUCHED[@]} -gt 0 ]]; then
    for f in "${FILES_TOUCHED[@]}"; do
      [[ "$f" =~ \.md$ && -f "$REPO/$f" ]] && md_files+=("$REPO/$f")
    done
  fi
  [[ ${#md_files[@]} -gt 0 ]] || return 0
  if [[ ! -r "$MARKDOWNLINT_BASE_CONFIG" ]]; then
    echo "ERROR: bundled Markdownlint base config is missing; reinstall the code-ultrareview skill." >&2
    emit_rerun
    return 4
  fi
  resolve_required_tool markdownlint-cli2 || return $?
  # MD013's arbitrary line-length default overwhelms review signal in projects
  # that have not chosen a Markdown style. The bundled file is a base config:
  # repository and nested configs still override it normally.
  _capture "$out" "$err" -- "${RESOLVED_COMMAND[@]}" \
    --config "$MARKDOWNLINT_BASE_CONFIG" --no-globs "${md_files[@]}"
  capture_succeeded markdownlint-cli2 "$CAPTURE_RC" "$err" || return $?
  if [[ -s "$err" ]]; then
    printf '\n' >> "$out"
    sed -n '/^[^[:space:]].*:[0-9][0-9]*\(:[0-9][0-9]*\)\{0,1\} /p' "$err" >> "$out"
  fi
  require_findings_report markdownlint-cli2 "$CAPTURE_RC" "$out" || return $?
  mark_dispatched markdownlint-cli2
}

run_api_extractor() {
  local out="$OUTPUT_DIR/raw/api-extractor.txt"
  local err="$OUTPUT_DIR/raw/api-extractor.stderr"
  resolve_required_tool api-extractor || return $?
  _capture "$out" "$err" -- "${RESOLVED_COMMAND[@]}" run --local --verbose
  capture_succeeded api-extractor "$CAPTURE_RC" "$err" || return $?
  [[ ! -s "$err" ]] || cat "$err" >> "$out"
  require_nonempty_file api-extractor "$out" || return $?
  mark_dispatched api-extractor
}

run_lizard() {
  local out="$OUTPUT_DIR/raw/lizard.csv"
  local err="$OUTPUT_DIR/raw/lizard.stderr"
  local target="$REPO"
  resolve_required_tool lizard || return $?
  _capture "$out" "$err" -- "${RESOLVED_COMMAND[@]}" --csv "$target"
  capture_succeeded lizard "$CAPTURE_RC" "$err" || return $?
  require_nonempty_file lizard "$out" || return $?
  [[ -f "$out" ]] && mv "$out" "$OUTPUT_DIR/raw/lizard.txt"
  mark_dispatched lizard
}

run_vulture() {
  local out="$OUTPUT_DIR/raw/vulture.txt"
  local err="$OUTPUT_DIR/raw/vulture.stderr"
  resolve_required_tool vulture || return $?
  _capture "$out" "$err" -- "${RESOLVED_COMMAND[@]}" "$REPO"
  capture_succeeded vulture "$CAPTURE_RC" "$err" || return $?
  require_findings_report vulture "$CAPTURE_RC" "$out" || return $?
  mark_dispatched vulture
}

run_semgrep() {
  local out="$OUTPUT_DIR/raw/semgrep.json"
  local err="$OUTPUT_DIR/raw/semgrep.stderr"
  # Bundled perf-rules only — `--config=auto` fetches from the semgrep
  # registry at runtime, which violates the public-skill posture (zero
  # implicit network calls beyond git/gh/explicit user-set tools).
  local configs=()
  if [[ -d "$PERF_RULES_DIR" ]]; then
    configs+=("--config=$PERF_RULES_DIR")
  fi
  if [[ ${#configs[@]} -eq 0 ]]; then
    echo "ERROR: bundled Semgrep rules are missing; reinstall the code-ultrareview skill" >&2
    emit_rerun
    return 4
  fi
  # Scope to changed code files only.
  local code_files=()
  local f
  if [[ ${#FILES_TOUCHED[@]} -gt 0 ]]; then
    for f in "${FILES_TOUCHED[@]}"; do
      [[ "$f" =~ \.(py|js|jsx|ts|tsx|mjs|cjs|go|rs|java|rb|php|cs|cpp|c|h|hpp|swift|kt)$ && -f "$REPO/$f" ]] && code_files+=("./$f")
    done
  fi
  if [[ ${#code_files[@]} -eq 0 ]]; then
    return 0
  fi
  resolve_required_tool semgrep || return $?
  _capture "$out" "$err" -- "${RESOLVED_COMMAND[@]}" --json --quiet --metrics=off \
    --disable-version-check --no-rewrite-rule-ids \
    "${configs[@]}" "${code_files[@]}"
  capture_succeeded semgrep "$CAPTURE_RC" "$err" || return $?
  require_json_file semgrep "$out" "$err" || return $?
  require_semgrep_without_errors "$out" "$err" || return $?
  mark_dispatched semgrep
}

run_vale() {
  local out="$OUTPUT_DIR/raw/vale.json"
  local err="$OUTPUT_DIR/raw/vale.stderr"
  # Vale is a Go binary — PATH only. Pass changed prose files only.
  local prose_files=()
  local f
  if [[ ${#FILES_TOUCHED[@]} -gt 0 ]]; then
    for f in "${FILES_TOUCHED[@]}"; do
      [[ "$f" =~ \.(md|txt|rst|adoc)$ && -f "$REPO/$f" ]] && prose_files+=("./$f")
    done
  fi
  if [[ ${#prose_files[@]} -eq 0 ]]; then
    return 0
  fi
  resolve_required_tool vale || return $?
  _capture "$out" "$err" -- "${RESOLVED_COMMAND[@]}" --output JSON "${prose_files[@]}"
  capture_succeeded vale "$CAPTURE_RC" "$err" || return $?
  require_json_file vale "$out" "$err" || return $?
  mark_dispatched vale
}

run_oasdiff() {
  local out="$OUTPUT_DIR/raw/oasdiff.json"
  local err="$OUTPUT_DIR/raw/oasdiff.stderr"
  resolve_required_tool oasdiff || return $?
  local base
  base="$(_scope_field base)"
  if [[ -z "$base" ]]; then
    echo "ERROR: oasdiff requires scope.json base to compare changed specifications." >&2
    echo "ERROR: remediation: rerun scope resolution with a valid --base, then rerun Code Ultrareview." >&2
    emit_rerun
    return 4
  fi

  printf '[]\n' >"$out"
  : >"$err"
  local current current_out previous spec_err f
  for f in "${FILES_TOUCHED[@]}"; do
    if [[ ! "$f" =~ (openapi|swagger)\.(ya?ml|json)$ || ! -f "$REPO/$f" ]]; then
      continue
    fi
    current="$REPO/$f"
    previous="$(mktemp -t oasdiff_prev_XXXX)"
    current_out="$(mktemp -t oasdiff_out_XXXX)"
    spec_err="$(mktemp -t oasdiff_err_XXXX)"
    if (cd "$REPO" && git show "${base}:${f}") >"$previous" 2>/dev/null; then
      _capture "$current_out" "$spec_err" -- \
        "${RESOLVED_COMMAND[@]}" breaking -f json "$previous" "$current"
      if ! capture_succeeded oasdiff "$CAPTURE_RC" "$spec_err"; then
        cat "$spec_err" >>"$err"
        rm -f "$previous" "$current_out" "$spec_err"
        return 4
      fi
      if ! require_json_file oasdiff "$current_out" "$spec_err"; then
        rm -f "$previous" "$current_out" "$spec_err"
        return 4
      fi
      if ! python3 - "$out" "$current_out" <<'PY'
import json
import os
from pathlib import Path
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    combined = json.load(handle)
with open(sys.argv[2], encoding="utf-8") as handle:
    current = json.load(handle)
if not isinstance(combined, list) or not isinstance(current, list):
    raise SystemExit(4)
combined.extend(current)
with open(sys.argv[1], "w", encoding="utf-8") as handle:
    json.dump(combined, handle)
    handle.write("\n")
PY
      then
        rm -f "$previous" "$current_out" "$spec_err"
        echo "ERROR: oasdiff reports could not be combined reliably." >&2
        emit_rerun
        return 4
      fi
    fi
    [[ ! -s "$spec_err" ]] || cat "$spec_err" >>"$err"
    rm -f "$previous" "$current_out" "$spec_err"
  done
  require_json_file oasdiff "$out" "$err" || return $?
  mark_dispatched oasdiff
}

run_atlas() {
  local out="$OUTPUT_DIR/raw/atlas.json"
  local err="$OUTPUT_DIR/raw/atlas.stderr"
  resolve_required_tool atlas || return $?
  _capture "$out" "$err" -- "${RESOLVED_COMMAND[@]}" migrate lint --format '{{ json . }}'
  capture_succeeded atlas "$CAPTURE_RC" "$err" || return $?
  require_json_file atlas "$out" "$err" || return $?
  mark_dispatched atlas
}

run_deadcode() {
  local out="$OUTPUT_DIR/raw/deadcode.txt"
  local err="$OUTPUT_DIR/raw/deadcode.stderr"
  resolve_required_tool deadcode || return $?
  _capture "$out" "$err" -- "${RESOLVED_COMMAND[@]}" ./...
  capture_succeeded deadcode "$CAPTURE_RC" "$err" || return $?
  mark_dispatched deadcode
}

run_gocyclo() {
  local out="$OUTPUT_DIR/raw/gocyclo.txt"
  local err="$OUTPUT_DIR/raw/gocyclo.stderr"
  resolve_required_tool gocyclo || return $?
  _capture "$out" "$err" -- "${RESOLVED_COMMAND[@]}" -over 10 .
  capture_succeeded gocyclo "$CAPTURE_RC" "$err" || return $?
  mark_dispatched gocyclo
}

run_dupl() {
  local out="$OUTPUT_DIR/raw/dupl.txt"
  local err="$OUTPUT_DIR/raw/dupl.stderr"
  resolve_required_tool dupl || return $?
  _capture "$out" "$err" -- "${RESOLVED_COMMAND[@]}" -t 50 ./...
  capture_succeeded dupl "$CAPTURE_RC" "$err" || return $?
  mark_dispatched dupl
}

run_cargo_machete() {
  local out="$OUTPUT_DIR/raw/cargo-machete.txt"
  local err="$OUTPUT_DIR/raw/cargo-machete.stderr"
  resolve_required_tool cargo-machete || return $?
  _capture "$out" "$err" -- "${RESOLVED_COMMAND[@]}"
  capture_succeeded cargo-machete "$CAPTURE_RC" "$err" || return $?
  require_findings_report cargo-machete "$CAPTURE_RC" "$out" || return $?
  mark_dispatched cargo-machete
}

# Tool → runner dispatch — a case statement (bash 3.2 lacks `declare -A`).
run_for_tool() {
  case "$1" in
    knip) run_knip ;;
    jscpd) run_jscpd ;;
    markdownlint-cli2) run_markdownlint ;;
    api-extractor) run_api_extractor ;;
    lizard) run_lizard ;;
    vulture) run_vulture ;;
    semgrep) run_semgrep ;;
    vale) run_vale ;;
    oasdiff) run_oasdiff ;;
    atlas) run_atlas ;;
    deadcode) run_deadcode ;;
    gocyclo) run_gocyclo ;;
    dupl) run_dupl ;;
    cargo-machete) run_cargo_machete ;;
    *) echo "ERROR: unknown tool: $1" >&2; return 1 ;;
  esac
}

# Iteration order = BATTERY_TABLE order = deterministic for tests.
ALL_TOOLS=()
for row in "${BATTERY_TABLE[@]}"; do
  ALL_TOOLS+=("${row%%|*}")
done

AVAILABLE_ROWS=()
MISSING_ROWS=()
for tool in "${ALL_TOOLS[@]}"; do
  if want_tool "$tool"; then
    if resolve_tool "$tool"; then
      AVAILABLE_ROWS+=("$tool|$RESOLVED_WRAPPER|$(tool_axes "$tool")|$(coverage_hint "$tool")")
    else
      MISSING_ROWS+=("$tool|$(tool_axes "$tool")|$(coverage_hint "$tool")|$(install_cmd "$tool")")
    fi
  fi
done

render_plan() {
  local destination="$1"
  python3 - "$SCOPE" "$AXES" "$destination" \
    "${#AVAILABLE_ROWS[@]}" ${AVAILABLE_ROWS[@]+"${AVAILABLE_ROWS[@]}"} \
    "${#MISSING_ROWS[@]}" ${MISSING_ROWS[@]+"${MISSING_ROWS[@]}"} <<'PY'
import json
import os
from pathlib import Path
import sys

scope_path, axes, destination = sys.argv[1:4]
cursor = 4
available_count = int(sys.argv[cursor])
cursor += 1
available_rows = sys.argv[cursor:cursor + available_count]
cursor += available_count
missing_count = int(sys.argv[cursor])
cursor += 1
missing_rows = sys.argv[cursor:cursor + missing_count]

with open(scope_path, encoding="utf-8") as handle:
    scope = json.load(handle)

def parse_available(row):
    tool, wrapper, tool_axes, coverage = row.split("|", 3)
    return {
        "tool": tool,
        "wrapper": wrapper,
        "axes": tool_axes.split(","),
        "coverage": coverage,
    }

def parse_missing(row):
    tool, tool_axes, coverage, install = row.split("|", 3)
    return {
        "tool": tool,
        "axes": tool_axes.split(","),
        "coverage": coverage,
        "install": install,
    }

payload = {
    "repo_kind": scope.get("repo_kind"),
    "languages": sorted(scope.get("languages") or []),
    "selected_axes": [axis.strip() for axis in axes.split(",") if axis.strip()],
    "available": [parse_available(row) for row in available_rows],
    "missing": [parse_missing(row) for row in missing_rows],
    "complete": not missing_rows,
}
rendered = json.dumps(payload, indent=2) + "\n"
if destination == "-":
    sys.stdout.write(rendered)
else:
    destination_path = Path(destination)
    temporary = destination_path.with_name(
        f".{destination_path.name}.{os.getpid()}.tmp"
    )
    try:
        temporary.write_text(rendered, encoding="utf-8")
        os.replace(temporary, destination_path)
    except OSError as error:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        print(f"tool preflight could not be published atomically: {error}", file=sys.stderr)
        raise SystemExit(1)
PY
}

if [[ "$DRY_RUN" -eq 1 ]]; then
  render_plan -
  [[ ${#MISSING_ROWS[@]} -eq 0 ]] || exit 3
  exit 0
fi

if ! render_plan "$PREFLIGHT_FINAL"; then
  rm -f "$PREFLIGHT_FINAL" 2>/dev/null || true
  echo "ERROR: analyzer preflight could not be published atomically at $PREFLIGHT_FINAL" >&2
  echo "ERROR: remediation: verify that $OUTPUT_DIR is writable and supports same-directory rename, then rerun Code Ultrareview." >&2
  emit_rerun
  exit 4
fi

FINDINGS_PENDING="$OUTPUT_DIR/.tool-findings.pending.jsonl"
if ! : >"$FINDINGS_PENDING"; then
  echo "ERROR: pending analyzer findings could not be created in $OUTPUT_DIR" >&2
  echo "ERROR: remediation: verify that $OUTPUT_DIR is writable, then rerun Code Ultrareview." >&2
  emit_rerun
  exit 4
fi
# shellcheck disable=SC2329 # Invoked by the EXIT trap below.
cleanup_pending_findings() {
  rm -f "$FINDINGS_PENDING"
}
trap cleanup_pending_findings EXIT

if ! python3 - "$SCOPE" "$OUTPUT_DIR/tool-preflight.json" <<'PY'
import json
import os
from pathlib import Path
import sys

scope_path = Path(sys.argv[1])
with Path(sys.argv[2]).open(encoding="utf-8") as handle:
    plan = json.load(handle)
with scope_path.open(encoding="utf-8") as handle:
    scope = json.load(handle)
scope["tools_missing"] = plan["missing"]
scope["tools_skipped"] = []
scope["tool_coverage"] = {
    "complete": False,
    "selected_axes": plan["selected_axes"],
    "explicit_scope": bool(plan["selected_axes"]),
    "applicable": [entry["tool"] for entry in plan["available"] + plan["missing"]],
    "executed": [],
}
scope["coverage_complete"] = False
temporary = scope_path.with_name(f".{scope_path.name}.{os.getpid()}.tmp")
temporary.write_text(
    json.dumps(scope, indent=2, sort_keys=False) + "\n",
    encoding="utf-8",
)
os.replace(temporary, scope_path)
PY
then
  echo "ERROR: tool coverage state could not be initialized in $SCOPE" >&2
  emit_rerun
  exit 4
fi

if [[ ${#MISSING_ROWS[@]} -gt 0 ]]; then
  for row in "${MISSING_ROWS[@]}"; do
    tool="${row%%|*}"
    rest="${row#*|}"
    axes="${rest%%|*}"
    rest="${rest#*|}"
    coverage="${rest%%|*}"
    install="${rest#*|}"
    echo "ERROR: required analyzer '$tool' is missing ($coverage; axes: $axes)." >&2
    echo "ERROR: install: $install" >&2
    echo "ERROR: remediation: run the install command, then rerun Code Ultrareview." >&2
  done
  emit_rerun
  exit 3
fi

for tool in "${ALL_TOOLS[@]}"; do
  if want_tool "$tool"; then
    run_for_tool "$tool"
    runner_rc=$?
    [[ $runner_rc -eq 0 ]] || exit "$runner_rc"
  fi
done

if [[ ${#DISPATCHED[@]} -ne ${#AVAILABLE_ROWS[@]} ]]; then
  echo "ERROR: one or more applicable analyzers completed without a report." >&2
  emit_rerun
  exit 4
fi

INGEST_ERROR="$OUTPUT_DIR/battery-ingest.stderr"
if ! python3 "$INGEST" batch \
  --raw-dir "$OUTPUT_DIR/raw" \
  --tools ${DISPATCHED[@]+"${DISPATCHED[@]}"} \
  --scope "$SCOPE" \
  --repo "$REPO" \
  --output "$FINDINGS_PENDING" \
  2>"$INGEST_ERROR"
then
  echo "ERROR: analyzer outputs could not be ingested reliably." >&2
  failed_reports=0
  for tool in "${DISPATCHED[@]}"; do
    diagnostic="$OUTPUT_DIR/raw/$tool.ingest.stderr"
    if ! python3 "$INGEST" ingest \
      --tool "$tool" \
      --input "$(report_path_for_tool "$tool")" \
      --output /dev/null \
      2>"$diagnostic"
    then
      failed_reports=$((failed_reports + 1))
      cat "$diagnostic" >&2
      echo "ERROR: analyzer report: $(report_path_for_tool "$tool")" >&2
      echo "ERROR: analyzer stderr: $OUTPUT_DIR/raw/$tool.stderr" >&2
      if resolve_tool "$tool"; then
        print_resolved_version_command
      fi
      echo "ERROR: repair/install: $(install_cmd "$tool")" >&2
    else
      rm -f "$diagnostic"
    fi
  done
  if [[ "$failed_reports" -eq 0 ]]; then
    cat "$INGEST_ERROR" >&2
    echo "ERROR: remediation: repair the scope or output contract reported above, then rerun Code Ultrareview." >&2
  else
    echo "ERROR: remediation: repair only the analyzer reports listed above, verify them independently, then rerun Code Ultrareview." >&2
  fi
  emit_rerun
  exit 4
fi
rm -f "$INGEST_ERROR"

if ! mv -f "$FINDINGS_PENDING" "$FINDINGS_FINAL"; then
  echo "ERROR: analyzer findings could not be published atomically." >&2
  echo "ERROR: remediation: verify that $OUTPUT_DIR is writable and supports same-directory rename, then rerun Code Ultrareview." >&2
  emit_rerun
  exit 4
fi

if ! python3 - "$OUTPUT_DIR/tools-skipped.json" "$SCOPE" \
  "$OUTPUT_DIR/tool-preflight.json" "$FINDINGS_FINAL" \
  ${DISPATCHED[@]+"${DISPATCHED[@]}"} <<'PY'
import hashlib
import json
import os
from pathlib import Path
import sys

out_path, scope_path, preflight_path, findings_path = sys.argv[1:5]
dispatched = sys.argv[5:]
with open(out_path, "w", encoding="utf-8") as handle:
    json.dump({"skipped": []}, handle, indent=2)
    handle.write("\n")
with open(scope_path, encoding="utf-8") as handle:
    scope = json.load(handle)
with open(preflight_path, encoding="utf-8") as handle:
    plan = json.load(handle)
scope["tools_dispatched"] = dispatched
scope["tools_missing"] = []
scope["tools_skipped"] = []
scope["tool_coverage"] = {
    "complete": True,
    "selected_axes": plan["selected_axes"],
    "explicit_scope": bool(plan["selected_axes"]),
    "applicable": [entry["tool"] for entry in plan["available"]],
    "executed": dispatched,
}
findings_path = Path(findings_path).resolve()
findings_data = findings_path.read_bytes()
scope["tool_coverage"].update({
    "output": str(findings_path),
    "sha256": hashlib.sha256(findings_data).hexdigest(),
    "finding_count": sum(1 for line in findings_data.splitlines() if line.strip()),
})
scope_path = Path(scope_path)
temporary = scope_path.with_name(f".{scope_path.name}.{os.getpid()}.tmp")
temporary.write_text(
    json.dumps(scope, indent=2, sort_keys=False) + "\n",
    encoding="utf-8",
)
os.replace(temporary, scope_path)
PY
then
  rm -f "$FINDINGS_FINAL"
  echo "ERROR: analyzer findings completed but tool coverage state could not be persisted." >&2
  echo "ERROR: remediation: verify that the scope directory is writable and supports atomic replacement, then rerun Code Ultrareview." >&2
  emit_rerun
  exit 4
fi

exit 0
