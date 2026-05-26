#!/usr/bin/env python3
"""Phase 2 tool-output parser for code-ultrareview.

Reads raw outputs from the deterministic tool battery (`run_battery.sh`) and
emits canonical findings as JSONL. One parser per tool. Every finding carries
`confidence: 100` — tool findings are deterministic and skip the validator
phase (WS-4).

Routing matrix (TOOL_TO_AXIS) maps each tool to one of the 8 axes:

    correctness   → semgrep (generic)
    simplification → knip, jscpd, lizard, vulture, deadcode, gocyclo, dupl,
                     cargo-machete
    documentation  → markdownlint-cli2, vale
    design-api    → api-extractor, oasdiff, atlas
    performance   → semgrep (bundled perf-rules — routed via rule metadata)

The performance routing for semgrep is dynamic: a finding whose `check_id`
starts with `code-ultrareview-` (the bundled perf-rules namespace) or whose
metadata declares `axis: performance` routes to performance; everything else
from semgrep routes to correctness.

Canonical finding schema:

    {
        "file": str,
        "line_start": int,
        "line_end": int,
        "severity": "High" | "Medium" | "Low",
        "confidence": 100,
        "axis": str,
        "source_tool": str,
        "message": str,
        "fix_hint": str | None,  # optional
    }

CLI:
    # Single-tool: parse one raw output, emit JSONL on stdout
    battery_ingest.py ingest --tool knip --input raw/knip.json

    # Batch: read raw/<tool>.<ext> for every supported tool, emit one JSONL
    battery_ingest.py batch --raw-dir <dir> --output <jsonl-path>
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Callable

CONFIDENCE = 100
PERF_RULE_PREFIX = "code-ultrareview-"

# Canonical axis routing per tool. Semgrep's per-finding axis decision lives
# inside parse_semgrep() since it depends on the rule namespace, not the tool.
TOOL_TO_AXIS = {
    "knip": "simplification",
    "jscpd": "simplification",
    "markdownlint-cli2": "documentation",
    "api-extractor": "design-api",
    "lizard": "simplification",
    "vulture": "simplification",
    "semgrep": "correctness",  # default — perf-rules override per-finding
    "oasdiff": "design-api",
    "atlas": "design-api",
    "vale": "documentation",
    "deadcode": "simplification",
    "gocyclo": "simplification",
    "dupl": "simplification",
    "cargo-machete": "simplification",
}


def _emit(*, file: str, line_start: int, line_end: int | None,
          severity: str, axis: str, source_tool: str, message: str,
          fix_hint: str | None = None) -> dict:
    """Build a canonical finding dict. Confidence is always 100."""
    out = {
        "file": file,
        "line_start": int(line_start),
        "line_end": int(line_end) if line_end is not None else int(line_start),
        "severity": severity,
        "confidence": CONFIDENCE,
        "axis": axis,
        "source_tool": source_tool,
        "message": message,
    }
    if fix_hint:
        out["fix_hint"] = fix_hint
    return out


# ---------------------------------------------------------------------------
# knip — unused exports / files / deps
# ---------------------------------------------------------------------------

def parse_knip(raw: str) -> list[dict]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []

    findings: list[dict] = []

    # knip's JSON reporter shape: array of per-file issue objects.
    items = data if isinstance(data, list) else [data]

    for item in items:
        if not isinstance(item, dict):
            continue
        file = item.get("file") or item.get("fileName") or ""
        if not file:
            continue

        # Unused exports / types — each is a {symbol, line, col} object.
        for category in ("exports", "types", "enumMembers", "classMembers",
                         "duplicates", "unresolved"):
            entries = item.get(category)
            if not entries:
                continue
            # entries can be a list of objects, a dict, or a list of names
            if isinstance(entries, dict):
                iter_entries = entries.values()
            elif isinstance(entries, list):
                iter_entries = entries
            else:
                continue
            for entry in iter_entries:
                line = 1
                name = ""
                if isinstance(entry, dict):
                    line = int(entry.get("line", 1) or 1)
                    name = entry.get("name") or entry.get("symbol") or ""
                else:
                    name = str(entry)
                findings.append(_emit(
                    file=file, line_start=line, line_end=line,
                    severity="Low", axis=TOOL_TO_AXIS["knip"],
                    source_tool="knip",
                    message=f"unused {category[:-1] if category.endswith('s') else category}"
                            f"{f': {name}' if name else ''}",
                    fix_hint="Remove if truly unused, or wire it up.",
                ))

        # Whole-file unused (item.files == true means the file itself is unused).
        if item.get("files") is True:
            findings.append(_emit(
                file=file, line_start=1, line_end=1,
                severity="Medium", axis=TOOL_TO_AXIS["knip"],
                source_tool="knip",
                message="file is unused",
                fix_hint="Delete the file or wire it into an entry point.",
            ))

        # Unlisted / unused dependencies — usually at package.json.
        for category in ("dependencies", "devDependencies", "unlisted",
                         "binaries", "optionalPeerDependencies"):
            entries = item.get(category)
            if not entries:
                continue
            if not isinstance(entries, list):
                continue
            for entry in entries:
                name = entry.get("name") if isinstance(entry, dict) else str(entry)
                if not name:
                    continue
                findings.append(_emit(
                    file=file or "package.json", line_start=1, line_end=1,
                    severity="Low", axis=TOOL_TO_AXIS["knip"],
                    source_tool="knip",
                    message=f"unused {category}: {name}",
                    fix_hint="Remove from package.json.",
                ))

    # Some knip versions also emit a top-level "files" list (whole-file unused).
    if isinstance(data, dict):
        for path in data.get("files") or []:
            if not isinstance(path, str):
                continue
            findings.append(_emit(
                file=path, line_start=1, line_end=1,
                severity="Medium", axis=TOOL_TO_AXIS["knip"],
                source_tool="knip",
                message="file is unused",
                fix_hint="Delete the file or wire it into an entry point.",
            ))

    return findings


# ---------------------------------------------------------------------------
# jscpd — code duplication
# ---------------------------------------------------------------------------

def parse_jscpd(raw: str) -> list[dict]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []

    findings: list[dict] = []
    duplicates = data.get("duplicates") if isinstance(data, dict) else None
    if not isinstance(duplicates, list):
        return findings

    for dup in duplicates:
        if not isinstance(dup, dict):
            continue
        first = dup.get("firstFile") or {}
        second = dup.get("secondFile") or {}
        lines = dup.get("lines") or dup.get("linesCount") or 0
        if not first.get("name"):
            continue
        line_start = int(first.get("start", 1) or 1)
        line_end = int(first.get("end", line_start) or line_start)
        msg = (
            f"duplicated block ({lines} lines) also in "
            f"{second.get('name', '?')}:{second.get('start', '?')}-{second.get('end', '?')}"
        )
        findings.append(_emit(
            file=first.get("name", ""), line_start=line_start, line_end=line_end,
            severity="Medium", axis=TOOL_TO_AXIS["jscpd"],
            source_tool="jscpd",
            message=msg,
            fix_hint="Extract shared logic or accept the duplication.",
        ))
    return findings


# ---------------------------------------------------------------------------
# markdownlint-cli2 — Markdown lint
# ---------------------------------------------------------------------------

def parse_markdownlint(raw: str) -> list[dict]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []

    findings: list[dict] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        file = item.get("fileName") or item.get("file") or ""
        line = int(item.get("lineNumber") or 1)
        rule_names = item.get("ruleNames") or []
        rule_desc = item.get("ruleDescription") or ""
        error_ctx = item.get("errorContext") or ""
        rule_id = rule_names[0] if rule_names else "MD???"
        msg = f"{rule_id}: {rule_desc}"
        if error_ctx:
            msg = f"{msg} — {error_ctx}"
        findings.append(_emit(
            file=file, line_start=line, line_end=line,
            severity="Low", axis=TOOL_TO_AXIS["markdownlint-cli2"],
            source_tool="markdownlint-cli2",
            message=msg,
        ))
    return findings


# ---------------------------------------------------------------------------
# api-extractor — public TS API surface
# ---------------------------------------------------------------------------

_API_EXTRACTOR_LINE = re.compile(
    r"(?P<level>Warning|Error):\s+(?P<file>[^:]+):(?P<line>\d+):(?P<col>\d+)\s*-\s*\((?P<rule>[^)]+)\)\s*(?P<msg>.+)"
)


def parse_api_extractor(raw: str) -> list[dict]:
    findings: list[dict] = []
    for line in raw.splitlines():
        m = _API_EXTRACTOR_LINE.search(line)
        if not m:
            continue
        sev = "High" if m.group("level") == "Error" else "Medium"
        findings.append(_emit(
            file=m.group("file"),
            line_start=int(m.group("line")),
            line_end=int(m.group("line")),
            severity=sev, axis=TOOL_TO_AXIS["api-extractor"],
            source_tool="api-extractor",
            message=f"{m.group('rule')}: {m.group('msg').strip()}",
        ))
    return findings


# ---------------------------------------------------------------------------
# lizard — cyclomatic complexity
# ---------------------------------------------------------------------------

# CSV header from `lizard --csv`:
#   NLOC,CCN,token,PARAM,length,location
# location format: name@start-end@file
_LIZARD_LOCATION = re.compile(r"^(?P<name>.+)@(?P<start>\d+)-(?P<end>\d+)@(?P<file>.+)$")
LIZARD_CCN_THRESHOLD = 10
LIZARD_PARAM_THRESHOLD = 5


def parse_lizard(raw: str) -> list[dict]:
    findings: list[dict] = []
    for raw_line in raw.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("NLOC"):
            continue
        # Robust CSV split — only first 5 commas separate cols (location may contain commas, rare).
        parts = line.split(",", 5)
        if len(parts) < 6:
            continue
        try:
            ccn = int(parts[1].strip())
            param = int(parts[3].strip())
        except ValueError:
            continue
        loc = parts[5].strip().strip('"')
        m = _LIZARD_LOCATION.match(loc)
        if not m:
            continue
        if ccn <= LIZARD_CCN_THRESHOLD and param <= LIZARD_PARAM_THRESHOLD:
            continue
        reasons = []
        if ccn > LIZARD_CCN_THRESHOLD:
            reasons.append(f"CCN {ccn} > {LIZARD_CCN_THRESHOLD}")
        if param > LIZARD_PARAM_THRESHOLD:
            reasons.append(f"{param} params > {LIZARD_PARAM_THRESHOLD}")
        sev = "Medium" if ccn > LIZARD_CCN_THRESHOLD else "Low"
        findings.append(_emit(
            file=m.group("file"),
            line_start=int(m.group("start")),
            line_end=int(m.group("end")),
            severity=sev, axis=TOOL_TO_AXIS["lizard"],
            source_tool="lizard",
            message=f"{m.group('name')}: {', '.join(reasons)}",
            fix_hint="Split into smaller functions; extract guard clauses.",
        ))
    return findings


# ---------------------------------------------------------------------------
# vulture — dead Python code
# ---------------------------------------------------------------------------

_VULTURE_LINE = re.compile(
    r"^(?P<file>[^:]+):(?P<line>\d+):\s*(?:unused\s+)?(?P<kind>\w+)\s+'(?P<name>[^']+)'\s+\((?P<conf>\d+)%\s+confidence\)"
)


def parse_vulture(raw: str) -> list[dict]:
    findings: list[dict] = []
    for line in raw.splitlines():
        m = _VULTURE_LINE.search(line)
        if not m:
            continue
        findings.append(_emit(
            file=m.group("file"),
            line_start=int(m.group("line")),
            line_end=int(m.group("line")),
            severity="Low", axis=TOOL_TO_AXIS["vulture"],
            source_tool="vulture",
            message=f"unused {m.group('kind')}: {m.group('name')} "
                    f"({m.group('conf')}% lint confidence)",
            fix_hint="Remove if truly unused.",
        ))
    return findings


# ---------------------------------------------------------------------------
# semgrep — patterns. Routes generic → correctness, perf-rules → performance.
# ---------------------------------------------------------------------------

def _semgrep_axis(check_id: str, metadata: dict) -> str:
    if metadata.get("axis") == "performance":
        return "performance"
    if isinstance(check_id, str) and check_id.startswith(PERF_RULE_PREFIX):
        return "performance"
    # All other semgrep rules default to correctness.
    return "correctness"


def _semgrep_severity(level: str) -> str:
    mapping = {"ERROR": "High", "WARNING": "Medium", "INFO": "Low"}
    return mapping.get((level or "").upper(), "Medium")


def parse_semgrep(raw: str) -> list[dict]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    results = data.get("results") if isinstance(data, dict) else None
    if not isinstance(results, list):
        return []

    findings: list[dict] = []
    for r in results:
        if not isinstance(r, dict):
            continue
        check_id = r.get("check_id") or ""
        path = r.get("path") or ""
        start = (r.get("start") or {}).get("line", 1)
        end = (r.get("end") or {}).get("line", start)
        extra = r.get("extra") or {}
        metadata = extra.get("metadata") or {}
        message = extra.get("message") or check_id
        severity = _semgrep_severity(extra.get("severity") or "WARNING")
        axis = _semgrep_axis(check_id, metadata)
        findings.append(_emit(
            file=path, line_start=int(start), line_end=int(end),
            severity=severity, axis=axis, source_tool="semgrep",
            message=f"{check_id}: {message.strip()}",
        ))
    return findings


# ---------------------------------------------------------------------------
# oasdiff — OpenAPI breaking-change detector
# ---------------------------------------------------------------------------

def parse_oasdiff(raw: str) -> list[dict]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    items = data if isinstance(data, list) else (
        data.get("breaking") or data.get("changes") or []
    )
    if not isinstance(items, list):
        return []

    findings: list[dict] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        # oasdiff levels: 3 = ERR (breaking), 2 = WARN, 1 = INFO
        level = int(it.get("level", 3) or 3)
        sev = "High" if level >= 3 else "Medium" if level == 2 else "Low"
        op = it.get("operation") or ""
        path = it.get("path") or ""
        text = it.get("text") or it.get("id") or "breaking change"
        source = (it.get("source") or {})
        file = source.get("file") or "openapi.yaml"
        line = int(source.get("line", 1) or 1)
        findings.append(_emit(
            file=file, line_start=line, line_end=line,
            severity=sev, axis=TOOL_TO_AXIS["oasdiff"],
            source_tool="oasdiff",
            message=f"{op} {path}: {text}".strip(),
        ))
    return findings


# ---------------------------------------------------------------------------
# atlas — DB migration lint
# ---------------------------------------------------------------------------

def parse_atlas(raw: str) -> list[dict]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []

    findings: list[dict] = []
    # Atlas json shape: { "Files": [ { "Name": "...", "Reports": [ { "Diagnostics": [...] } ] } ] }
    files = (data.get("Files") if isinstance(data, dict) else None) or []
    for file_entry in files:
        if not isinstance(file_entry, dict):
            continue
        fname = file_entry.get("Name") or "migration.sql"
        reports = file_entry.get("Reports") or []
        for rep in reports:
            for diag in rep.get("Diagnostics") or []:
                pos = diag.get("Pos") or 0
                text = diag.get("Text") or "migration warning"
                code = diag.get("Code") or ""
                findings.append(_emit(
                    file=fname, line_start=max(1, int(pos or 1)),
                    line_end=max(1, int(pos or 1)),
                    severity="High", axis=TOOL_TO_AXIS["atlas"],
                    source_tool="atlas",
                    message=f"{code}: {text}".strip(": "),
                ))
    return findings


# ---------------------------------------------------------------------------
# vale — prose lint
# ---------------------------------------------------------------------------

def parse_vale(raw: str) -> list[dict]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, dict):
        return []

    findings: list[dict] = []
    for fname, items in data.items():
        if not isinstance(items, list):
            continue
        for it in items:
            if not isinstance(it, dict):
                continue
            line = int(it.get("Line", 1) or 1)
            sev = {"error": "High", "warning": "Medium", "suggestion": "Low"}.get(
                (it.get("Severity") or "warning").lower(), "Low"
            )
            check = it.get("Check") or ""
            msg = it.get("Message") or check
            findings.append(_emit(
                file=fname, line_start=line, line_end=line,
                severity=sev, axis=TOOL_TO_AXIS["vale"],
                source_tool="vale",
                message=f"{check}: {msg}".strip(": "),
            ))
    return findings


# ---------------------------------------------------------------------------
# deadcode (Go) — `deadcode ./...`
# ---------------------------------------------------------------------------

_DEADCODE_LINE = re.compile(r"^(?P<file>[^:]+\.go):(?P<line>\d+):(?P<col>\d+):\s*(?P<msg>.+)")


def parse_deadcode(raw: str) -> list[dict]:
    findings: list[dict] = []
    for line in raw.splitlines():
        m = _DEADCODE_LINE.match(line.strip())
        if not m:
            continue
        findings.append(_emit(
            file=m.group("file"),
            line_start=int(m.group("line")),
            line_end=int(m.group("line")),
            severity="Low", axis=TOOL_TO_AXIS["deadcode"],
            source_tool="deadcode",
            message=f"dead code: {m.group('msg').strip()}",
            fix_hint="Remove if truly unreachable.",
        ))
    return findings


# ---------------------------------------------------------------------------
# gocyclo — Go cyclomatic complexity
# ---------------------------------------------------------------------------

# Format: "<ccn> <package> <func> <file>:<line>:<col>"
_GOCYCLO_LINE = re.compile(
    r"^(?P<ccn>\d+)\s+(?P<pkg>\S+)\s+(?P<func>\S+)\s+(?P<file>[^:]+\.go):(?P<line>\d+)"
)


def parse_gocyclo(raw: str) -> list[dict]:
    findings: list[dict] = []
    for line in raw.splitlines():
        m = _GOCYCLO_LINE.match(line.strip())
        if not m:
            continue
        ccn = int(m.group("ccn"))
        findings.append(_emit(
            file=m.group("file"),
            line_start=int(m.group("line")),
            line_end=int(m.group("line")),
            severity="Medium" if ccn > 10 else "Low",
            axis=TOOL_TO_AXIS["gocyclo"],
            source_tool="gocyclo",
            message=f"{m.group('func')} CCN {ccn}",
            fix_hint="Split into smaller functions.",
        ))
    return findings


# ---------------------------------------------------------------------------
# dupl — Go duplication
# ---------------------------------------------------------------------------

# Format (default): blocks separated by blank lines, each block lists locations
# as "<file>:<start>-<end>". We pair consecutive locations within a block.
def parse_dupl(raw: str) -> list[dict]:
    findings: list[dict] = []
    block: list[tuple[str, int, int]] = []

    def flush():
        if len(block) < 2:
            return
        for i, (file, s, e) in enumerate(block):
            partners = [b for j, b in enumerate(block) if j != i]
            descriptions = [f"{p[0]}:{p[1]}-{p[2]}" for p in partners]
            findings.append(_emit(
                file=file, line_start=s, line_end=e,
                severity="Medium", axis=TOOL_TO_AXIS["dupl"],
                source_tool="dupl",
                message=f"duplicated block — also in {', '.join(descriptions)}",
                fix_hint="Extract shared logic.",
            ))

    loc_re = re.compile(r"(?P<file>[^\s]+\.go):(?P<start>\d+),(?P<end>\d+)")
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            flush()
            block = []
            continue
        m = loc_re.search(stripped)
        if m:
            block.append(
                (m.group("file"), int(m.group("start")), int(m.group("end")))
            )
    flush()
    return findings


# ---------------------------------------------------------------------------
# cargo-machete — unused Rust dependencies
# ---------------------------------------------------------------------------

_MACHETE_HEADER = re.compile(
    r"cargo-machete found the following unused dependencies in (?P<file>.+):"
)


def parse_cargo_machete(raw: str) -> list[dict]:
    findings: list[dict] = []
    current_file: str | None = None
    for line in raw.splitlines():
        m = _MACHETE_HEADER.search(line)
        if m:
            current_file = m.group("file").strip()
            continue
        if current_file is None:
            continue
        name = line.strip()
        if not name or name.startswith("cargo-machete"):
            continue
        # name is like "  serde_json" (indented) — strip leading spaces.
        if name.startswith("-"):
            name = name.lstrip("- ").strip()
        findings.append(_emit(
            file=current_file, line_start=1, line_end=1,
            severity="Low", axis=TOOL_TO_AXIS["cargo-machete"],
            source_tool="cargo-machete",
            message=f"unused dependency: {name}",
            fix_hint="Remove from Cargo.toml.",
        ))
    return findings


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

PARSERS: dict[str, Callable[[str], list[dict]]] = {
    "knip": parse_knip,
    "jscpd": parse_jscpd,
    "markdownlint-cli2": parse_markdownlint,
    "api-extractor": parse_api_extractor,
    "lizard": parse_lizard,
    "vulture": parse_vulture,
    "semgrep": parse_semgrep,
    "oasdiff": parse_oasdiff,
    "atlas": parse_atlas,
    "vale": parse_vale,
    "deadcode": parse_deadcode,
    "gocyclo": parse_gocyclo,
    "dupl": parse_dupl,
    "cargo-machete": parse_cargo_machete,
}


def ingest_one(tool: str, raw: str) -> list[dict]:
    parser = PARSERS.get(tool)
    if parser is None:
        return []
    return parser(raw)


def _read_raw(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def batch(raw_dir: Path) -> list[dict]:
    """Read raw/<tool>.<ext> for every tool the dir holds; emit aggregated findings.

    File-extension is informational only; the tool name (stem) drives parsing.
    """
    all_findings: list[dict] = []
    for entry in sorted(raw_dir.iterdir()):
        if not entry.is_file():
            continue
        tool = entry.stem
        if tool not in PARSERS:
            continue
        raw = _read_raw(entry)
        if not raw:
            continue
        all_findings.extend(ingest_one(tool, raw))
    return all_findings


def _write_jsonl(findings: list[dict], output: Path | None) -> None:
    lines = [json.dumps(f, sort_keys=False) for f in findings]
    text = "\n".join(lines) + ("\n" if lines else "")
    if output is None:
        sys.stdout.write(text)
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Tool-output parser for code-ultrareview")
    sub = parser.add_subparsers(dest="cmd", required=True)

    ing = sub.add_parser("ingest", help="Parse one tool's raw output")
    ing.add_argument("--tool", required=True, choices=sorted(PARSERS.keys()))
    ing.add_argument("--input", required=True, help="Path to the raw output file")
    ing.add_argument("--output", default=None,
                     help="JSONL path (default: stdout)")

    bat = sub.add_parser("batch", help="Parse every raw/<tool>.<ext> in a directory")
    bat.add_argument("--raw-dir", required=True, help="Directory of raw tool outputs")
    bat.add_argument("--output", default=None,
                     help="JSONL path (default: stdout)")

    args = parser.parse_args()

    if args.cmd == "ingest":
        raw = _read_raw(Path(args.input))
        findings = ingest_one(args.tool, raw)
    else:
        raw_dir = Path(args.raw_dir)
        if not raw_dir.is_dir():
            print(f"ERROR: raw-dir does not exist: {raw_dir}", file=sys.stderr)
            return 2
        findings = batch(raw_dir)

    out = Path(args.output) if args.output else None
    _write_jsonl(findings, out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
