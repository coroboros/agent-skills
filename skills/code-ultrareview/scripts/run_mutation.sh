#!/usr/bin/env bash
# Phase 2 extension — mutation testing (gated by --mutation-test).
#
# Per-language dispatch:
#   JS/TS  → npx stryker run               (when stryker.conf.* or @stryker-mutator
#                                            present)
#   Python → uvx mutmut run --paths-to-mutate=<changed-py-files>
#   JVM    → mvn org.pitest:pitest-maven:mutationCoverage  (when pom.xml present)
#
# Surviving mutants route to the Tests axis as 🟠 Medium with confidence 100
# (deterministic CLI output skips the Phase 4 validator). The script scopes
# to changed files from scope.json["files_touched_list"] only.
#
# Graceful skip: missing tool, missing config, or `MUTATION_DRY_RUN=1`
# emits `WARN: <reason>` to stderr and writes an empty findings file. The
# script never auto-installs — install commands surface in the WARN line.
#
# Usage:
#   run_mutation.sh --scope <scope.json> --output-dir <dir> [--repo <path>]
#                   [--timeout <seconds>]
#
# Exit 0 always when args are valid. Exit 2 on argument or scope.json error.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SCOPE=""
OUTPUT_DIR=""
REPO="."
TIMEOUT="${MUTATION_TIMEOUT:-600}"

usage() {
  cat <<'EOF' >&2
Usage: run_mutation.sh --scope <scope.json> --output-dir <dir> [options]

Required:
  --scope <path>        scope.json from scripts/scope.py
  --output-dir <path>   directory for raw/, mutation-findings.jsonl

Options:
  --repo <path>         repo root (default: cwd)
  --timeout <seconds>   tool timeout (default: 600, override via MUTATION_TIMEOUT)

Env:
  MUTATION_DRY_RUN=1    skip tool invocation; emit empty findings (test hook)

Exit 0 always when args are valid. Exit 2 on argument or scope.json error.
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

REPO="$(cd "$REPO" && pwd)"
mkdir -p "$OUTPUT_DIR/raw"
FINDINGS_OUT="$OUTPUT_DIR/mutation-findings.jsonl"
: >"$FINDINGS_OUT"

# scope.json extraction (mirror of run_battery.sh).
_scope_field() {
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

have_cmd() { command -v "$1" >/dev/null 2>&1; }

emit_warn() {
  echo "WARN: $1" >&2
}

# Dry-run / test hook — emit empty findings, log the skip, exit 0.
if [[ "${MUTATION_DRY_RUN:-}" == "1" ]]; then
  emit_warn "MUTATION_DRY_RUN=1 — skipping mutation tool invocation"
  exit 0
fi

run_stryker() {
  local has_config=0
  for cfg in stryker.conf.js stryker.conf.mjs stryker.conf.json stryker.config.js stryker.config.mjs stryker.config.json; do
    if [[ -f "$REPO/$cfg" ]]; then
      has_config=1
      break
    fi
  done
  if [[ "$has_config" -eq 0 ]]; then
    # Check package.json devDependencies for stryker as a fallback signal.
    if [[ -f "$REPO/package.json" ]] && \
       grep -q '"@stryker-mutator/core"' "$REPO/package.json" 2>/dev/null; then
      has_config=1
    fi
  fi

  if [[ "$has_config" -eq 0 ]]; then
    emit_warn "stryker: no stryker config and no @stryker-mutator/core in package.json — install: npm i -D @stryker-mutator/core (or use npx)"
    return 0
  fi
  if ! have_cmd npx; then
    emit_warn "stryker: npx not on PATH — install Node + npm to enable npx"
    return 0
  fi

  local mutate_args=()
  local f
  for f in "${FILES_TOUCHED[@]:-}"; do
    if [[ "$f" =~ \.(ts|tsx|js|jsx|mjs|cjs)$ ]]; then
      mutate_args+=("$f")
    fi
  done

  local raw="$OUTPUT_DIR/raw/stryker.log"
  local err="$OUTPUT_DIR/raw/stryker.stderr"

  # Stryker writes the machine-readable report to reports/mutation/mutation.json
  # by default. We capture stdout to a log too.
  if [[ ${#mutate_args[@]} -gt 0 ]]; then
    (
      cd "$REPO" && \
      timeout "$TIMEOUT" npx -y stryker run --mutate "$(IFS=,; echo "${mutate_args[*]}")"
    ) >"$raw" 2>"$err" || true
  else
    (
      cd "$REPO" && timeout "$TIMEOUT" npx -y stryker run
    ) >"$raw" 2>"$err" || true
  fi

  local report="$REPO/reports/mutation/mutation.json"
  if [[ ! -f "$report" ]]; then
    emit_warn "stryker: no report at reports/mutation/mutation.json (run failed or timed out)"
    return 0
  fi

  python3 - "$report" "$FINDINGS_OUT" <<'PY'
import json, sys
report_path, out_path = sys.argv[1], sys.argv[2]
try:
    with open(report_path, encoding="utf-8") as fh:
        report = json.load(fh)
except (OSError, json.JSONDecodeError):
    sys.exit(0)
findings = []
files = report.get("files") or {}
for file_path, payload in files.items():
    for mutant in payload.get("mutants") or []:
        if mutant.get("status") != "Survived":
            continue
        loc_start = mutant.get("location", {}).get("start", {})
        line = loc_start.get("line", 0)
        col = loc_start.get("column", 0)
        location = f"{file_path}:{line}:{col}" if line else file_path
        findings.append({
            "axis": "tests",
            "severity": "Medium",
            "location": location,
            "finding": (
                f"Surviving mutant ({mutant.get('mutatorName','?')}): "
                f"{mutant.get('description','no description')}"
            ),
            "recommendation": (
                "Tests did not catch this mutation — add an assertion "
                "that fails when the mutated code path executes."
            ),
            "confidence": 100,
            "source_tool": "stryker",
        })
with open(out_path, "a", encoding="utf-8") as fh:
    for f in findings:
        fh.write(json.dumps(f) + "\n")
PY
}

run_mutmut() {
  if ! have_cmd uvx && ! have_cmd mutmut; then
    emit_warn "mutmut: not on PATH — install: pipx install mutmut (or use uvx — zero-install)"
    return 0
  fi

  local py_args=()
  local f
  for f in "${FILES_TOUCHED[@]:-}"; do
    if [[ "$f" =~ \.py$ ]]; then
      py_args+=("$f")
    fi
  done
  if [[ ${#py_args[@]} -eq 0 ]]; then
    emit_warn "mutmut: no changed .py files in scope — skipping"
    return 0
  fi

  local raw="$OUTPUT_DIR/raw/mutmut.log"
  local err="$OUTPUT_DIR/raw/mutmut.stderr"
  local paths
  paths="$(IFS=,; echo "${py_args[*]}")"

  local mutmut_cmd=(mutmut)
  if have_cmd uvx; then
    mutmut_cmd=(uvx mutmut)
  fi

  (
    cd "$REPO" && \
    timeout "$TIMEOUT" "${mutmut_cmd[@]}" run --paths-to-mutate="$paths"
  ) >"$raw" 2>"$err" || true

  # `mutmut results` lists surviving mutants by ID; `mutmut show <id>` gives
  # the diff. Parse a minimal "id → file:line" mapping from `results` output.
  local results="$OUTPUT_DIR/raw/mutmut-results.log"
  (
    cd "$REPO" && "${mutmut_cmd[@]}" results
  ) >"$results" 2>/dev/null || true

  python3 - "$results" "$FINDINGS_OUT" "$REPO" <<'PY'
import json, re, subprocess, sys
results_path, out_path, repo = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    text = open(results_path, encoding="utf-8").read()
except OSError:
    sys.exit(0)
# `mutmut results` groups by status. Find the "Survived" block.
survived_ids = []
in_block = False
for line in text.splitlines():
    if re.match(r"^Survived", line, re.IGNORECASE):
        in_block = True
        continue
    if in_block and re.match(r"^[A-Z][a-z]+", line):
        in_block = False
    if in_block:
        for m in re.finditer(r"\b(\d+)\b", line):
            survived_ids.append(m.group(1))
findings = []
for mid in survived_ids:
    # Best-effort: ask `mutmut show <id>` for the file/line.
    try:
        r = subprocess.run(
            ["mutmut", "show", mid],
            cwd=repo, capture_output=True, text=True, timeout=15,
        )
        out = r.stdout
    except (subprocess.SubprocessError, OSError):
        out = ""
    file_match = re.search(r"---\s+a/(\S+)", out) or re.search(r"^\s*(\S+\.py):\d+", out, re.MULTILINE)
    line_match = re.search(r"@@\s+-(\d+)", out)
    file_path = file_match.group(1) if file_match else "<unknown>"
    line = line_match.group(1) if line_match else "?"
    findings.append({
        "axis": "tests",
        "severity": "Medium",
        "location": f"{file_path}:{line}",
        "finding": f"Surviving mutmut mutant #{mid}",
        "recommendation": (
            "Tests did not catch this mutation — add an assertion that "
            "fails when the mutated code path executes."
        ),
        "confidence": 100,
        "source_tool": "mutmut",
    })
with open(out_path, "a", encoding="utf-8") as fh:
    for f in findings:
        fh.write(json.dumps(f) + "\n")
PY
}

run_pitest() {
  if [[ ! -f "$REPO/pom.xml" ]]; then
    emit_warn "pitest: no pom.xml (Gradle/standalone pitest not supported yet) — install: configure org.pitest:pitest-maven in pom.xml"
    return 0
  fi
  if ! have_cmd mvn; then
    emit_warn "pitest: mvn not on PATH — install: brew install maven (or distribution-specific)"
    return 0
  fi

  local raw="$OUTPUT_DIR/raw/pitest.log"
  local err="$OUTPUT_DIR/raw/pitest.stderr"

  (
    cd "$REPO" && timeout "$TIMEOUT" \
      mvn -q -B org.pitest:pitest-maven:mutationCoverage
  ) >"$raw" 2>"$err" || true

  # pitest writes target/pit-reports/<YYYY-MM-DD-HH-MI>/mutations.xml. Pick
  # the most recent timestamped dir.
  local pit_root="$REPO/target/pit-reports"
  if [[ ! -d "$pit_root" ]]; then
    emit_warn "pitest: no report dir at target/pit-reports/ (run failed or pitest not configured in pom.xml)"
    return 0
  fi
  local latest
  latest="$(ls -1 "$pit_root" 2>/dev/null | sort | tail -n 1)"
  local report="$pit_root/$latest/mutations.xml"
  if [[ ! -f "$report" ]]; then
    emit_warn "pitest: no mutations.xml under $pit_root/$latest"
    return 0
  fi

  python3 - "$report" "$FINDINGS_OUT" <<'PY'
import json, sys
import xml.etree.ElementTree as ET
report_path, out_path = sys.argv[1], sys.argv[2]
try:
    tree = ET.parse(report_path)
except (OSError, ET.ParseError):
    sys.exit(0)
findings = []
for mutation in tree.getroot().findall("mutation"):
    if mutation.get("status") != "SURVIVED":
        continue
    src = mutation.findtext("sourceFile") or "<unknown>"
    line = mutation.findtext("lineNumber") or "?"
    desc = mutation.findtext("description") or "no description"
    findings.append({
        "axis": "tests",
        "severity": "Medium",
        "location": f"{src}:{line}",
        "finding": f"Surviving pitest mutant: {desc}",
        "recommendation": (
            "Tests did not catch this mutation — add an assertion that "
            "fails when the mutated code path executes."
        ),
        "confidence": 100,
        "source_tool": "pitest",
    })
with open(out_path, "a", encoding="utf-8") as fh:
    for f in findings:
        fh.write(json.dumps(f) + "\n")
PY
}

DISPATCHED=0
if has_lang typescript || has_lang javascript; then
  run_stryker
  DISPATCHED=1
fi
if has_lang python; then
  run_mutmut
  DISPATCHED=1
fi
if has_lang java || has_lang kotlin || has_lang scala; then
  run_pitest
  DISPATCHED=1
fi

if [[ "$DISPATCHED" -eq 0 ]]; then
  emit_warn "no JS/TS, Python, or JVM languages detected in scope — mutation testing skipped"
fi

exit 0
