#!/usr/bin/env bash
# Phase 2 tool battery — code-ultrareview.
#
# Reads scope.json (repo_kind + languages + files_touched_list), runs
# deterministic CLIs per the dispatch matrix below, captures raw outputs,
# and invokes battery_ingest.py to emit canonical findings as JSONL.
#
# Try order per tool: npx wrapper → uvx wrapper → PATH binary → graceful skip.
# Missing tools emit `WARN: <tool> not found — install: <cmd>` to stderr and
# land in <output-dir>/tools-skipped.json. The battery NEVER auto-installs.
#
# Usage:
#   run_battery.sh --scope <scope.json> --output-dir <dir> [--repo <path>] [--dry-run]
#
# Exit 0 on success (graceful skip is not a failure). Exit 2 on argument
# error or unreadable scope.json.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INGEST="$SCRIPT_DIR/battery_ingest.py"
PERF_RULES_DIR="$SCRIPT_DIR/../references/perf-rules"

SCOPE=""
OUTPUT_DIR=""
REPO="."
DRY_RUN=0

# ---------------------------------------------------------------------------
# Dispatch matrix — single source of truth.
#
# Format: "<tool>|<install-command>|<axis-coverage-hint>"
# Used by both the runtime dispatcher and `preflight_tools.sh`.
# Mirrored by the README "Tool → Axis → Install command" table — drift
# fails `tests/code-ultrareview/test_battery.py::test_readme_parity`.
# ---------------------------------------------------------------------------

# shellcheck disable=SC2034
BATTERY_TABLE=(
  "knip|npm i -D knip (or use npx — zero-install)|simplification (JS/TS dead code)"
  "jscpd|npm i -D jscpd (or use npx — zero-install)|simplification (duplication)"
  "markdownlint-cli2|npm i -D markdownlint-cli2 (or use npx — zero-install)|documentation (Markdown lint)"
  "api-extractor|npm i -D @microsoft/api-extractor (or use npx — zero-install)|design-api (TS public surface)"
  "lizard|pipx install lizard (or use uvx — zero-install)|simplification (cyclomatic complexity)"
  "vulture|pipx install vulture (or use uvx — zero-install)|simplification (dead Python code)"
  "semgrep|pipx install semgrep (or use uvx — zero-install)|correctness + performance (patterns)"
  "vale|brew install vale (Go binary, no Python wrapper)|documentation (prose lint)"
  "oasdiff|brew install oasdiff|design-api (OpenAPI breaking changes)"
  "atlas|brew install ariga/tap/atlas|design-api (DB migration lint)"
  "deadcode|go install golang.org/x/tools/cmd/deadcode@latest|simplification (Go unreachable)"
  "gocyclo|go install github.com/fzipp/gocyclo/cmd/gocyclo@latest|simplification (Go complexity)"
  "dupl|go install github.com/mibk/dupl@latest|simplification (Go duplication)"
  "cargo-machete|cargo install cargo-machete|simplification (Rust unused deps)"
)

usage() {
  cat <<'EOF' >&2
Usage: run_battery.sh --scope <scope.json> --output-dir <dir> [options]

Required:
  --scope <path>        scope.json from scripts/scope.py
  --output-dir <path>   directory for raw/, tool-findings.jsonl, tools-skipped.json

Options:
  --repo <path>         repo root (default: cwd)
  --dry-run             print dispatch plan as JSON, do not run tools

Exit 0 always when args are valid. Exit 2 on argument or scope.json error.
EOF
}

# ---------------------------------------------------------------------------
# Arg parsing
# ---------------------------------------------------------------------------

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope) SCOPE="${2:-}"; shift 2 ;;
    --output-dir) OUTPUT_DIR="${2:-}"; shift 2 ;;
    --repo) REPO="${2:-}"; shift 2 ;;
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

REPO="$(cd "$REPO" && pwd)"
mkdir -p "$OUTPUT_DIR/raw"

# ---------------------------------------------------------------------------
# scope.json field extraction (via python3 — already a hard dependency).
# ---------------------------------------------------------------------------

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

REPO_KIND="$(_scope_field repo_kind)"

# Portable line-array population (bash 3.2 lacks `mapfile`).
LANGUAGES=()
while IFS= read -r _line; do
  [[ -n "$_line" ]] && LANGUAGES+=("$_line")
done < <(_scope_field languages)

FILES_TOUCHED=()
while IFS= read -r _line; do
  [[ -n "$_line" ]] && FILES_TOUCHED+=("$_line")
done < <(_scope_field files_touched_list)

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

has_file_match() {
  # Args: <regex>
  local pat="$1" f
  if [[ ${#FILES_TOUCHED[@]} -eq 0 ]]; then
    return 1
  fi
  for f in "${FILES_TOUCHED[@]}"; do
    if [[ "$f" =~ $pat ]]; then
      return 0
    fi
  done
  return 1
}

has_repo_file() {
  # Args: <relative-path>
  [[ -f "$REPO/$1" ]]
}

# ---------------------------------------------------------------------------
# Dispatch decision — encoded inline. Mirrors SKILL.md Phase 2 description.
# ---------------------------------------------------------------------------

# Result accumulators.
DISPATCHED=()
SKIPPED_NAMES=()
SKIPPED_INSTALLS=()
SKIPPED_AXES=()

want_tool() {
  # Args: <tool>. Returns 0 if dispatch matrix says yes for this scope.
  local tool="$1"
  case "$tool" in
    knip)
      has_lang typescript || has_lang javascript
      ;;
    jscpd)
      # jscpd works cross-language — run when any code language is present.
      has_lang typescript || has_lang javascript || has_lang python || \
        has_lang go || has_lang rust || has_lang java
      ;;
    markdownlint-cli2)
      has_file_match '\.md$'
      ;;
    api-extractor)
      has_repo_file "api-extractor.json"
      ;;
    lizard)
      has_lang python || has_lang typescript || has_lang javascript || \
        has_lang go || has_lang rust
      ;;
    vulture)
      has_lang python
      ;;
    semgrep)
      # Always run when any code language is present — also carries perf-rules.
      has_lang python || has_lang typescript || has_lang javascript || \
        has_lang go || has_lang rust
      ;;
    vale)
      has_repo_file ".vale.ini"
      ;;
    oasdiff)
      # OpenAPI yaml/json in diff.
      has_file_match '(openapi|swagger)\.(ya?ml|json)$'
      ;;
    atlas)
      has_file_match '(^|/)migrations/'
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
  # Args: <tool>. Echoes the install command from BATTERY_TABLE.
  local tool="$1" row name cmd
  for row in "${BATTERY_TABLE[@]}"; do
    name="${row%%|*}"
    if [[ "$name" == "$tool" ]]; then
      cmd="${row#*|}"
      cmd="${cmd%%|*}"
      printf '%s\n' "$cmd"
      return 0
    fi
  done
  printf 'unknown\n'
}

axis_hint() {
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

mark_skipped() {
  local tool="$1"
  SKIPPED_NAMES+=("$tool")
  SKIPPED_INSTALLS+=("$(install_cmd "$tool")")
  SKIPPED_AXES+=("$(axis_hint "$tool")")
  echo "WARN: $tool not found — install: $(install_cmd "$tool")" >&2
}

mark_dispatched() {
  DISPATCHED+=("$1")
}

# ---------------------------------------------------------------------------
# Tool runners. Each writes raw output to $OUTPUT_DIR/raw/<tool>.<ext>.
# Try order: npx → uvx → PATH binary → mark_skipped.
# ---------------------------------------------------------------------------

have_cmd() { command -v "$1" >/dev/null 2>&1; }

# npx invocations use `-y` to skip interactive install prompts.
# Stderr is captured per tool to <tool>.stderr for debug.
_capture() {
  # Args: <out-file> <stderr-file> -- <cmd...>
  local out="$1" err="$2"; shift 2
  if [[ "$1" == "--" ]]; then shift; fi
  ( cd "$REPO" && "$@" ) >"$out" 2>"$err" || true
}

run_knip() {
  local out="$OUTPUT_DIR/raw/knip.json"
  local err="$OUTPUT_DIR/raw/knip.stderr"
  if have_cmd npx; then
    _capture "$out" "$err" -- npx -y knip --reporter json --no-progress
    mark_dispatched knip
    return 0
  fi
  if have_cmd knip; then
    _capture "$out" "$err" -- knip --reporter json --no-progress
    mark_dispatched knip
    return 0
  fi
  mark_skipped knip
}

run_jscpd() {
  local out="$OUTPUT_DIR/raw/jscpd.json"
  local err="$OUTPUT_DIR/raw/jscpd.stderr"
  if have_cmd npx; then
    _capture "$out" "$err" -- npx -y jscpd --silent --reporters json --output "$OUTPUT_DIR/raw/jscpd_out" "$REPO"
    # jscpd writes to <output>/jscpd-report.json — copy if found.
    if [[ -f "$OUTPUT_DIR/raw/jscpd_out/jscpd-report.json" ]]; then
      cp "$OUTPUT_DIR/raw/jscpd_out/jscpd-report.json" "$out"
    fi
    mark_dispatched jscpd
    return 0
  fi
  if have_cmd jscpd; then
    _capture "$out" "$err" -- jscpd --silent --reporters json --output "$OUTPUT_DIR/raw/jscpd_out" "$REPO"
    if [[ -f "$OUTPUT_DIR/raw/jscpd_out/jscpd-report.json" ]]; then
      cp "$OUTPUT_DIR/raw/jscpd_out/jscpd-report.json" "$out"
    fi
    mark_dispatched jscpd
    return 0
  fi
  mark_skipped jscpd
}

run_markdownlint() {
  local out="$OUTPUT_DIR/raw/markdownlint-cli2.json"
  local err="$OUTPUT_DIR/raw/markdownlint-cli2.stderr"
  # Build the md file list from scope.json's files_touched_list.
  local md_files=()
  local f
  if [[ ${#FILES_TOUCHED[@]} -gt 0 ]]; then
    for f in "${FILES_TOUCHED[@]}"; do
      [[ "$f" =~ \.md$ ]] && md_files+=("$f")
    done
  fi
  if [[ ${#md_files[@]} -eq 0 ]]; then
    md_files=("**/*.md")
  fi
  if have_cmd npx; then
    _capture "$out" "$err" -- npx -y markdownlint-cli2 --output "$out" "${md_files[@]}"
    mark_dispatched markdownlint-cli2
    return 0
  fi
  if have_cmd markdownlint-cli2; then
    _capture "$out" "$err" -- markdownlint-cli2 --output "$out" "${md_files[@]}"
    mark_dispatched markdownlint-cli2
    return 0
  fi
  mark_skipped markdownlint-cli2
}

run_api_extractor() {
  local out="$OUTPUT_DIR/raw/api-extractor.txt"
  local err="$OUTPUT_DIR/raw/api-extractor.stderr"
  if have_cmd npx; then
    _capture "$out" "$err" -- npx -y @microsoft/api-extractor run --local --verbose
    mark_dispatched api-extractor
    return 0
  fi
  if have_cmd api-extractor; then
    _capture "$out" "$err" -- api-extractor run --local --verbose
    mark_dispatched api-extractor
    return 0
  fi
  mark_skipped api-extractor
}

run_lizard() {
  local out="$OUTPUT_DIR/raw/lizard.csv"
  local err="$OUTPUT_DIR/raw/lizard.stderr"
  local target="$REPO"
  if have_cmd uvx; then
    _capture "$out" "$err" -- uvx lizard --csv "$target"
    # Rename .csv → .txt so battery_ingest picks it up by stem.
    [[ -f "$out" ]] && mv "$out" "$OUTPUT_DIR/raw/lizard.txt"
    mark_dispatched lizard
    return 0
  fi
  if have_cmd lizard; then
    _capture "$out" "$err" -- lizard --csv "$target"
    [[ -f "$out" ]] && mv "$out" "$OUTPUT_DIR/raw/lizard.txt"
    mark_dispatched lizard
    return 0
  fi
  mark_skipped lizard
}

run_vulture() {
  local out="$OUTPUT_DIR/raw/vulture.txt"
  local err="$OUTPUT_DIR/raw/vulture.stderr"
  if have_cmd uvx; then
    _capture "$out" "$err" -- uvx vulture "$REPO"
    mark_dispatched vulture
    return 0
  fi
  if have_cmd vulture; then
    _capture "$out" "$err" -- vulture "$REPO"
    mark_dispatched vulture
    return 0
  fi
  mark_skipped vulture
}

run_semgrep() {
  local out="$OUTPUT_DIR/raw/semgrep.json"
  local err="$OUTPUT_DIR/raw/semgrep.stderr"
  # Run with `--config=auto` (generic patterns) AND bundled perf-rules.
  local configs=("--config=auto")
  if [[ -d "$PERF_RULES_DIR" ]]; then
    configs+=("--config=$PERF_RULES_DIR")
  fi
  if have_cmd uvx; then
    _capture "$out" "$err" -- uvx semgrep --json --quiet "${configs[@]}" "$REPO"
    mark_dispatched semgrep
    return 0
  fi
  if have_cmd semgrep; then
    _capture "$out" "$err" -- semgrep --json --quiet "${configs[@]}" "$REPO"
    mark_dispatched semgrep
    return 0
  fi
  mark_skipped semgrep
}

run_vale() {
  local out="$OUTPUT_DIR/raw/vale.json"
  local err="$OUTPUT_DIR/raw/vale.stderr"
  # Vale is a Go binary — PATH only.
  if have_cmd vale; then
    _capture "$out" "$err" -- vale --output JSON "$REPO"
    mark_dispatched vale
    return 0
  fi
  mark_skipped vale
}

run_oasdiff() {
  local out="$OUTPUT_DIR/raw/oasdiff.json"
  local err="$OUTPUT_DIR/raw/oasdiff.stderr"
  if ! have_cmd oasdiff; then
    mark_skipped oasdiff
    return 0
  fi
  # Resolve a base/target OpenAPI spec from the changed files. oasdiff
  # compares two spec files; we run against the current and the HEAD~1
  # version if available.
  local current=""
  local f
  if [[ ${#FILES_TOUCHED[@]} -gt 0 ]]; then
    for f in "${FILES_TOUCHED[@]}"; do
      if [[ "$f" =~ (openapi|swagger)\.(ya?ml|json)$ ]]; then
        current="$REPO/$f"
        break
      fi
    done
  fi
  if [[ -z "$current" ]]; then
    mark_skipped oasdiff
    return 0
  fi
  # Stash HEAD~1 version to a temp file.
  local previous
  previous="$(mktemp -t oasdiff_prev_XXXX)"
  if ( cd "$REPO" && git show "HEAD~1:${current#$REPO/}" ) >"$previous" 2>/dev/null; then
    _capture "$out" "$err" -- oasdiff breaking -f json "$previous" "$current"
  else
    # No prior version — record no findings.
    echo "[]" >"$out"
  fi
  rm -f "$previous"
  mark_dispatched oasdiff
}

run_atlas() {
  local out="$OUTPUT_DIR/raw/atlas.json"
  local err="$OUTPUT_DIR/raw/atlas.stderr"
  if ! have_cmd atlas; then
    mark_skipped atlas
    return 0
  fi
  _capture "$out" "$err" -- atlas migrate lint --format json
  mark_dispatched atlas
}

run_deadcode() {
  local out="$OUTPUT_DIR/raw/deadcode.txt"
  local err="$OUTPUT_DIR/raw/deadcode.stderr"
  if ! have_cmd deadcode; then
    mark_skipped deadcode
    return 0
  fi
  _capture "$out" "$err" -- deadcode ./...
  mark_dispatched deadcode
}

run_gocyclo() {
  local out="$OUTPUT_DIR/raw/gocyclo.txt"
  local err="$OUTPUT_DIR/raw/gocyclo.stderr"
  if ! have_cmd gocyclo; then
    mark_skipped gocyclo
    return 0
  fi
  _capture "$out" "$err" -- gocyclo -over 10 .
  mark_dispatched gocyclo
}

run_dupl() {
  local out="$OUTPUT_DIR/raw/dupl.txt"
  local err="$OUTPUT_DIR/raw/dupl.stderr"
  if ! have_cmd dupl; then
    mark_skipped dupl
    return 0
  fi
  _capture "$out" "$err" -- dupl -t 50 ./...
  mark_dispatched dupl
}

run_cargo_machete() {
  local out="$OUTPUT_DIR/raw/cargo-machete.txt"
  local err="$OUTPUT_DIR/raw/cargo-machete.stderr"
  if ! have_cmd cargo-machete; then
    mark_skipped cargo-machete
    return 0
  fi
  _capture "$out" "$err" -- cargo-machete
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

# ---------------------------------------------------------------------------
# Dry-run path — print the dispatch plan and exit.
# ---------------------------------------------------------------------------

if [[ "$DRY_RUN" -eq 1 ]]; then
  python3 - "$SCOPE" "$REPO" "${ALL_TOOLS[@]}" <<'PY'
import json, os, re, shutil, sys
scope_path = sys.argv[1]
repo = sys.argv[2]
tools = sys.argv[3:]
with open(scope_path, encoding="utf-8") as f:
    scope = json.load(f)
languages = set(scope.get("languages") or [])
files = scope.get("files_touched_list") or []

def has_lang(t): return t in languages
def has_file_match(rx):
    return any(re.search(rx, f) for f in files)
def has_repo_file(p): return os.path.isfile(os.path.join(repo, p))

decisions = {}
for tool in tools:
    want = False
    if tool == "knip": want = has_lang("typescript") or has_lang("javascript")
    elif tool == "jscpd": want = bool(languages & {"typescript","javascript","python","go","rust","java"})
    elif tool == "markdownlint-cli2": want = has_file_match(r"\.md$")
    elif tool == "api-extractor": want = has_repo_file("api-extractor.json")
    elif tool == "lizard": want = bool(languages & {"python","typescript","javascript","go","rust"})
    elif tool == "vulture": want = has_lang("python")
    elif tool == "semgrep": want = bool(languages & {"python","typescript","javascript","go","rust"})
    elif tool == "vale": want = has_repo_file(".vale.ini")
    elif tool == "oasdiff": want = has_file_match(r"(openapi|swagger)\.(ya?ml|json)$")
    elif tool == "atlas": want = has_file_match(r"(^|/)migrations/")
    elif tool == "deadcode": want = has_lang("go")
    elif tool == "gocyclo": want = has_lang("go")
    elif tool == "dupl": want = has_lang("go")
    elif tool == "cargo-machete": want = has_lang("rust")
    decisions[tool] = want

# Availability — check npx/uvx/path for each tool.
def avail(tool):
    if tool in ("knip","jscpd","markdownlint-cli2","api-extractor"):
        if shutil.which("npx"): return "npx"
        if shutil.which(tool): return "path"
        return None
    if tool in ("lizard","vulture","semgrep"):
        if shutil.which("uvx"): return "uvx"
        if shutil.which(tool): return "path"
        return None
    # Path-only tools.
    return "path" if shutil.which(tool) else None

dispatched = []
skipped = []
for tool, want in decisions.items():
    if not want:
        continue
    if avail(tool):
        dispatched.append({"tool": tool, "wrapper": avail(tool)})
    else:
        skipped.append({"tool": tool})

print(json.dumps({
    "repo_kind": scope.get("repo_kind"),
    "languages": sorted(languages),
    "dispatched": dispatched,
    "skipped": skipped,
}, indent=2))
PY
  exit 0
fi

# ---------------------------------------------------------------------------
# Real execution path — invoke each wanted tool.
# ---------------------------------------------------------------------------

for tool in "${ALL_TOOLS[@]}"; do
  if want_tool "$tool"; then
    run_for_tool "$tool"
  fi
done

# ---------------------------------------------------------------------------
# Aggregate raw outputs → tool-findings.jsonl
# ---------------------------------------------------------------------------

# Normalize raw filenames so battery_ingest's stem dispatch picks every tool.
# (Most runners already write <tool>.<ext>; nothing extra needed here.)
python3 "$INGEST" batch --raw-dir "$OUTPUT_DIR/raw" --output "$OUTPUT_DIR/tool-findings.jsonl"

# ---------------------------------------------------------------------------
# Write tools-skipped.json AND merge the same list into scope.json["tools_skipped"]
# so downstream phases (synthesis, "What I did NOT check") can read either file.
# ---------------------------------------------------------------------------

python3 - "$OUTPUT_DIR/tools-skipped.json" "$SCOPE" "${#SKIPPED_NAMES[@]}" "${SKIPPED_NAMES[@]:-}" "${SKIPPED_INSTALLS[@]:-}" "${SKIPPED_AXES[@]:-}" <<'PY'
import json, sys
out_path = sys.argv[1]
scope_path = sys.argv[2]
n = int(sys.argv[3])
names = sys.argv[4:4+n]
installs = sys.argv[4+n:4+2*n]
axes = sys.argv[4+2*n:4+3*n]

entries = [
    {"tool": names[i], "install": installs[i], "axis": axes[i]}
    for i in range(n)
]

with open(out_path, "w", encoding="utf-8") as f:
    json.dump({"skipped": entries}, f, indent=2)

# Mutate scope.json in place — Phase 5 synthesis reads `scope.json["tools_skipped"]`
# for the "What I did NOT check" closing section.
try:
    with open(scope_path, encoding="utf-8") as f:
        scope = json.load(f)
    scope["tools_skipped"] = entries
    with open(scope_path, "w", encoding="utf-8") as f:
        json.dump(scope, f, indent=2)
except (OSError, json.JSONDecodeError):
    # Scope file gone or corrupted between read and write — non-fatal; the
    # separate tools-skipped.json still carries the data.
    pass
PY

exit 0
