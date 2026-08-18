#!/usr/bin/env python3
"""Phase 2 tool-output parser for code-ultrareview.

Reads raw outputs from the deterministic tool battery (`run_battery.sh`) and
emits canonical findings as JSONL. One parser per tool. Every finding carries
`confidence: 100` — tool findings are deterministic and skip the Phase 4
validator phase.

Routing matrix (TOOL_TO_AXIS) maps each tool to one of the 8 axes:

    simplification → knip, jscpd, lizard, vulture, deadcode, gocyclo, dupl,
                     cargo-machete
    documentation  → markdownlint-cli2, vale
    design-api    → api-extractor, oasdiff, atlas
    performance   → semgrep (bundled perf-rules only)

Semgrep never loads remote or generic rules at runtime. An unexpected rule ID
is an invalid analyzer report, not Correctness coverage.

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

# Canonical axis routing per tool.
TOOL_TO_AXIS = {
    "knip": "simplification",
    "jscpd": "simplification",
    "markdownlint-cli2": "documentation",
    "api-extractor": "design-api",
    "lizard": "simplification",
    "vulture": "simplification",
    "semgrep": "performance",
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
    """Build a canonical finding dict. Confidence is always 100 — tool findings are deterministic."""
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


def parse_knip(raw: str) -> list[dict]:
    if not raw.strip():
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("knip produced malformed JSON") from exc

    findings: list[dict] = []

    # Knip 6 wraps per-file issue objects in {"issues": [...]}. Keep the
    # legacy array form readable so reports from an older project-local Knip
    # remain valid.
    if isinstance(data, dict) and isinstance(data.get("issues"), list):
        items = data["issues"]
    elif isinstance(data, list):
        items = data
    elif isinstance(data, dict) and (
        "file" in data or "fileName" in data or "files" in data
    ):
        items = [data]
    else:
        raise ValueError("knip JSON does not match a supported report schema")

    for item in items:
        if not isinstance(item, dict):
            raise ValueError("knip issue entries must be JSON objects")
        file = item.get("file") or item.get("fileName") or ""
        if not file:
            continue

        for category in ("exports", "types", "enumMembers", "classMembers",
                         "duplicates", "unresolved"):
            entries = item.get(category)
            if not entries:
                continue
            # knip varies the shape: list of objects, a dict, or a list of names.
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

        # Legacy Knip reports use `files: true`; Knip 6 reports a list whose
        # entries carry the unused path in `name`.
        unused_files: list[str] = []
        if item.get("files") is True:
            unused_files.append(file)
        elif isinstance(item.get("files"), list):
            for entry in item["files"]:
                path = entry.get("name") if isinstance(entry, dict) else entry
                if isinstance(path, str) and path:
                    unused_files.append(path)
        for path in dict.fromkeys(unused_files):
            findings.append(_emit(
                file=path, line_start=1, line_end=1,
                severity="Medium", axis=TOOL_TO_AXIS["knip"],
                source_tool="knip",
                message="file is unused",
                fix_hint="Delete the file or wire it into an entry point.",
            ))

        # Dependency findings carry no file; default to package.json.
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
                line = int(entry.get("line", 1) or 1) if isinstance(entry, dict) else 1
                findings.append(_emit(
                    file=file or "package.json", line_start=line, line_end=line,
                    severity="Low", axis=TOOL_TO_AXIS["knip"],
                    source_tool="knip",
                    message=f"unused {category}: {name}",
                    fix_hint="Remove from package.json.",
                ))

    # Some knip versions also emit whole-file-unused as a top-level "files" list.
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


def parse_jscpd(raw: str) -> list[dict]:
    if not raw.strip():
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("jscpd produced malformed JSON") from exc

    findings: list[dict] = []
    duplicates = data.get("duplicates") if isinstance(data, dict) else None
    if not isinstance(data, dict) or not isinstance(duplicates, list):
        raise ValueError("jscpd JSON is missing the duplicates array")

    for dup in duplicates:
        if not isinstance(dup, dict):
            raise ValueError("jscpd duplicate entries must be JSON objects")
        first = dup.get("firstFile") or {}
        second = dup.get("secondFile") or {}
        lines = dup.get("lines") or dup.get("linesCount") or 0
        if not first.get("name"):
            raise ValueError("jscpd duplicate entry is missing firstFile.name")
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


_MARKDOWNLINT_LINE = re.compile(
    r"^(?P<file>.+?):(?P<line>\d+)(?::(?P<col>\d+))?\s+"
    r"(?:error\s+)?(?P<rule>MD\d+(?:/[^\s]+)?)\s+(?P<message>.+)$"
)


def parse_markdownlint(raw: str) -> list[dict]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = None

    findings: list[dict] = []
    if isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                raise ValueError(
                    "markdownlint-cli2 JSON entries must be objects"
                )
            file = item.get("fileName") or item.get("file") or ""
            if not file:
                raise ValueError(
                    "markdownlint-cli2 JSON entry is missing a file name"
                )
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

    banner = re.compile(r"^markdownlint-cli2 v\d")
    for line_text in raw.splitlines():
        if banner.match(line_text):
            continue
        match = _MARKDOWNLINT_LINE.match(line_text.strip())
        if not match:
            continue
        line = int(match.group("line"))
        findings.append(_emit(
            file=match.group("file"), line_start=line, line_end=line,
            severity="Low", axis=TOOL_TO_AXIS["markdownlint-cli2"],
            source_tool="markdownlint-cli2",
            message=f"{match.group('rule')}: {match.group('message')}",
        ))
    if any(line.strip() and not banner.match(line) for line in raw.splitlines()) and not findings:
        raise ValueError(
            "markdownlint-cli2 produced non-empty output that does not match "
            "its documented text or JSON schema"
        )
    return findings


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
    if raw.strip() and not findings and "API Extractor completed successfully" not in raw:
        raise ValueError(
            "api-extractor produced non-empty output without a documented "
            "finding or successful-completion marker"
        )
    return findings


# `lizard --csv` columns: NLOC,CCN,token,PARAM,length,location
# where location is `name@start-end@file`.
_LIZARD_LOCATION = re.compile(r"^(?P<name>.+)@(?P<start>\d+)-(?P<end>\d+)@(?P<file>.+)$")
LIZARD_CCN_THRESHOLD = 10
LIZARD_PARAM_THRESHOLD = 5


def parse_lizard(raw: str) -> list[dict]:
    findings: list[dict] = []
    recognized = 0
    unknown: list[str] = []
    for raw_line in raw.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("NLOC"):
            recognized += 1
            continue
        # Split on the first 5 commas only — location can itself contain commas.
        parts = line.split(",", 5)
        if len(parts) < 6:
            unknown.append(line)
            continue
        try:
            ccn = int(parts[1].strip())
            param = int(parts[3].strip())
        except ValueError:
            unknown.append(line)
            continue
        loc = parts[5].strip().strip('"')
        m = _LIZARD_LOCATION.match(loc)
        if not m:
            unknown.append(line)
            continue
        recognized += 1
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
    if unknown or (raw.strip() and recognized == 0):
        raise ValueError("lizard produced unrecognized CSV output")
    return findings


_VULTURE_LINE = re.compile(
    r"^(?P<file>[^:]+):(?P<line>\d+):\s*(?:unused\s+)?(?P<kind>\w+)\s+'(?P<name>[^']+)'\s+\((?P<conf>\d+)%\s+confidence\)"
)


def parse_vulture(raw: str) -> list[dict]:
    findings: list[dict] = []
    unknown: list[str] = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        m = _VULTURE_LINE.fullmatch(stripped)
        if not m:
            unknown.append(stripped)
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
    if unknown:
        raise ValueError("vulture produced unrecognized text output")
    return findings


def _semgrep_axis(check_id: str, metadata: dict) -> str:
    rule_id = check_id.rsplit(".", 1)[-1] if isinstance(check_id, str) else ""
    if (
        metadata.get("axis") == "performance"
        and rule_id.startswith(PERF_RULE_PREFIX)
    ):
        return "performance"
    raise ValueError(
        f"unexpected Semgrep rule outside the bundled performance set: {check_id}"
    )


def _semgrep_severity(level: str) -> str:
    mapping = {"ERROR": "High", "WARNING": "Medium", "INFO": "Low"}
    return mapping.get((level or "").upper(), "Medium")


def parse_semgrep(raw: str) -> list[dict]:
    if not raw.strip():
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("semgrep produced malformed JSON") from exc
    results = data.get("results") if isinstance(data, dict) else None
    if not isinstance(results, list):
        raise ValueError("semgrep JSON is missing the results array")

    findings: list[dict] = []
    for r in results:
        if not isinstance(r, dict):
            raise ValueError("semgrep result entries must be JSON objects")
        check_id = r.get("check_id") or ""
        path = r.get("path") or ""
        if not check_id or not path:
            raise ValueError("semgrep result is missing check_id or path")
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


def parse_oasdiff(raw: str) -> list[dict]:
    if not raw.strip():
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("oasdiff produced malformed JSON") from exc
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict) and "breaking" in data:
        items = data["breaking"]
    elif isinstance(data, dict) and "changes" in data:
        items = data["changes"]
    else:
        raise ValueError("oasdiff JSON does not match a supported report schema")
    if not isinstance(items, list):
        raise ValueError("oasdiff changes must be a JSON array")

    findings: list[dict] = []
    for it in items:
        if not isinstance(it, dict):
            raise ValueError("oasdiff change entries must be JSON objects")
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


def parse_atlas(raw: str) -> list[dict]:
    if not raw.strip():
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("atlas produced malformed JSON") from exc

    findings: list[dict] = []
    # Atlas JSON: { "Files": [ { "Name", "Reports": [ { "Diagnostics": [...] } ] } ] }
    if not isinstance(data, dict) or not isinstance(data.get("Files"), list):
        raise ValueError("atlas JSON is missing the Files array")
    files = data["Files"]
    for file_entry in files:
        if not isinstance(file_entry, dict):
            raise ValueError("atlas file entries must be JSON objects")
        fname = file_entry.get("Name") or "migration.sql"
        reports = file_entry.get("Reports") or []
        if not isinstance(reports, list):
            raise ValueError("atlas Reports must be a JSON array")
        for rep in reports:
            if not isinstance(rep, dict):
                raise ValueError("atlas report entries must be JSON objects")
            diagnostics = rep.get("Diagnostics") or []
            if not isinstance(diagnostics, list):
                raise ValueError("atlas Diagnostics must be a JSON array")
            for diag in diagnostics:
                if not isinstance(diag, dict):
                    raise ValueError(
                        "atlas diagnostic entries must be JSON objects"
                    )
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


def parse_vale(raw: str) -> list[dict]:
    if not raw.strip():
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("vale produced malformed JSON") from exc
    if not isinstance(data, dict):
        raise ValueError("vale JSON report must be an object")

    findings: list[dict] = []
    for fname, items in data.items():
        if not isinstance(items, list):
            raise ValueError("vale file entries must be JSON arrays")
        for it in items:
            if not isinstance(it, dict):
                raise ValueError("vale findings must be JSON objects")
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


_DEADCODE_LINE = re.compile(r"^(?P<file>[^:]+\.go):(?P<line>\d+):(?P<col>\d+):\s*(?P<msg>.+)")


def parse_deadcode(raw: str) -> list[dict]:
    findings: list[dict] = []
    unknown: list[str] = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        m = _DEADCODE_LINE.fullmatch(stripped)
        if not m:
            unknown.append(stripped)
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
    if unknown:
        raise ValueError("deadcode produced unrecognized text output")
    return findings


# gocyclo line format: "<ccn> <package> <func> <file>:<line>:<col>"
_GOCYCLO_LINE = re.compile(
    r"^(?P<ccn>\d+)\s+(?P<pkg>\S+)\s+(?P<func>\S+)\s+(?P<file>[^:]+\.go):(?P<line>\d+)"
)


def parse_gocyclo(raw: str) -> list[dict]:
    findings: list[dict] = []
    unknown: list[str] = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        m = _GOCYCLO_LINE.match(stripped)
        if not m:
            unknown.append(stripped)
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
    if unknown:
        raise ValueError("gocyclo produced unrecognized text output")
    return findings


# dupl output: blocks separated by blank lines, each listing locations as
# "<file>:<start>-<end>". Pair every location in a block against the others.
def parse_dupl(raw: str) -> list[dict]:
    findings: list[dict] = []
    block: list[tuple[str, int, int]] = []
    clone_count: int | None = None
    unknown: list[str] = []

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
    summary_re = re.compile(r"^found\s+(?P<count>\d+)\s+clones?:$", re.IGNORECASE)
    total_re = re.compile(r"^Found total (?P<count>\d+) clone groups?\.$")
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            flush()
            block = []
            continue
        summary = summary_re.fullmatch(stripped)
        if summary:
            clone_count = int(summary.group("count"))
            continue
        total = total_re.fullmatch(stripped)
        if total:
            clone_count = int(total.group("count"))
            continue
        m = loc_re.search(stripped)
        if m:
            block.append(
                (m.group("file"), int(m.group("start")), int(m.group("end")))
            )
        else:
            unknown.append(stripped)
    flush()
    if unknown:
        raise ValueError("dupl produced unrecognized text output")
    if clone_count is not None and clone_count > 0 and not findings:
        raise ValueError("dupl reported clones without parseable locations")
    return findings


_MACHETE_HEADER = re.compile(
    r"cargo-machete found the following unused dependencies in .+:"
)
_MACHETE_CRATE = re.compile(r"^\S+ -- (?P<file>.+Cargo\.toml):$")


def parse_cargo_machete(raw: str) -> list[dict]:
    findings: list[dict] = []
    current_file: str | None = None
    saw_dependency = False
    recognized = 0
    unknown: list[str] = []
    clean_re = re.compile(
        r"(?:did(?: not|n't)|does not) find any unused dependencies|"
        r"found no unused dependencies",
        re.IGNORECASE,
    )
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            if saw_dependency:
                break
            continue
        if clean_re.search(stripped):
            recognized += 1
            continue
        if _MACHETE_HEADER.fullmatch(stripped):
            recognized += 1
            continue
        crate = _MACHETE_CRATE.fullmatch(stripped)
        if crate:
            current_file = crate.group("file")
            recognized += 1
            continue
        if current_file is None:
            unknown.append(stripped)
            continue
        name = stripped
        if name.startswith("-"):
            name = name.lstrip("- ").strip()
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", name):
            unknown.append(stripped)
            continue
        recognized += 1
        saw_dependency = True
        findings.append(_emit(
            file=current_file, line_start=1, line_end=1,
            severity="Low", axis=TOOL_TO_AXIS["cargo-machete"],
            source_tool="cargo-machete",
            message=f"unused dependency: {name}",
            fix_hint="Remove from Cargo.toml.",
        ))
    if unknown or (raw.strip() and recognized == 0):
        raise ValueError("cargo-machete produced unrecognized text output")
    return findings


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
        raise ValueError(f"unknown analyzer output: {tool}")
    return parser(raw)


def _read_raw(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


RAW_FILENAMES = {
    "knip": "knip.json",
    "jscpd": "jscpd.json",
    "markdownlint-cli2": "markdownlint-cli2.txt",
    "api-extractor": "api-extractor.txt",
    "lizard": "lizard.txt",
    "vulture": "vulture.txt",
    "semgrep": "semgrep.json",
    "oasdiff": "oasdiff.json",
    "atlas": "atlas.json",
    "vale": "vale.json",
    "deadcode": "deadcode.txt",
    "gocyclo": "gocyclo.txt",
    "dupl": "dupl.txt",
    "cargo-machete": "cargo-machete.txt",
}

# These analyzers report a repository or manifest-level contract. Their line
# number is often a placeholder, so path-level diff scoping is the strongest
# sound filter available. All other analyzers must overlap a changed hunk.
PATH_LEVEL_TOOLS = {
    "knip",
    "api-extractor",
    "oasdiff",
    "atlas",
    "cargo-machete",
}


def batch(raw_dir: Path, tools: list[str] | None = None) -> list[dict]:
    """Read exactly one canonical report for each executed analyzer.

    Empty text reports remain valid for analyzers that communicate a clean run
    through their exit status. Missing files, unknown analyzers, and read errors
    are runtime failures and must not collapse into zero findings.
    """
    all_findings: list[dict] = []
    selected = sorted(tools if tools is not None else RAW_FILENAMES)
    for tool in selected:
        if tool not in PARSERS or tool not in RAW_FILENAMES:
            raise ValueError(f"unknown analyzer output: {tool}")
        entry = raw_dir / RAW_FILENAMES[tool]
        if not entry.is_file():
            raise FileNotFoundError(f"missing analyzer report: {entry}")
        raw = _read_raw(entry)
        all_findings.extend(ingest_one(tool, raw))
    return all_findings


def filter_to_changed_files(
    findings: list[dict],
    changed_files: list[str],
    repo: Path,
    changed_line_ranges: dict[str, list[list[int]]] | None = None,
) -> list[dict]:
    """Keep deterministic findings anchored to reviewed paths and hunks.

    Some analyzers necessarily inspect repository-wide state (for example
    Knip, deadcode, Atlas, and cargo-machete). Their reports are still useful,
    but unchanged-file findings are pre-existing debt and must not be promoted
    to confidence 100 in a diff review.
    """
    repo = repo.resolve()

    def canonical(path: str) -> str:
        candidate = Path(path)
        if candidate.is_absolute():
            try:
                return candidate.resolve().relative_to(repo).as_posix()
            except ValueError:
                return candidate.as_posix()
        normalized = Path(path).as_posix()
        return normalized[2:] if normalized.startswith("./") else normalized

    def with_canonical_file(finding: dict, path: str) -> dict:
        normalized = dict(finding)
        normalized["file"] = path
        return normalized

    allowed = {canonical(path) for path in changed_files}
    if changed_line_ranges is None:
        filtered: list[dict] = []
        for finding in findings:
            path = canonical(str(finding.get("file") or ""))
            if path in allowed:
                filtered.append(with_canonical_file(finding, path))
        return filtered

    ranges_by_path = {
        canonical(path): ranges for path, ranges in changed_line_ranges.items()
    }
    filtered: list[dict] = []
    for finding in findings:
        path = canonical(str(finding.get("file") or ""))
        if path not in allowed:
            continue
        if finding.get("source_tool") in PATH_LEVEL_TOOLS:
            filtered.append(with_canonical_file(finding, path))
            continue
        ranges = ranges_by_path.get(path, [])
        line_start = finding.get("line_start")
        line_end = finding.get("line_end")
        if not isinstance(line_start, int) or not isinstance(line_end, int):
            continue
        if any(line_start <= end and line_end >= start for start, end in ranges):
            filtered.append(with_canonical_file(finding, path))
    return filtered


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
    bat.add_argument(
        "--tools", nargs="*", default=None,
        help="Executed analyzers whose canonical reports must exist",
    )
    bat.add_argument(
        "--scope",
        help="scope.json whose files_touched_list bounds deterministic findings",
    )
    bat.add_argument(
        "--repo", default=".",
        help="Repository root used to normalize absolute analyzer paths",
    )
    bat.add_argument("--output", default=None,
                     help="JSONL path (default: stdout)")

    args = parser.parse_args()

    try:
        if args.cmd == "ingest":
            raw = _read_raw(Path(args.input))
            findings = ingest_one(args.tool, raw)
        else:
            raw_dir = Path(args.raw_dir)
            if not raw_dir.is_dir():
                print(f"ERROR: raw-dir does not exist: {raw_dir}", file=sys.stderr)
                return 2
            findings = batch(raw_dir, args.tools)
            if args.scope:
                scope_path = Path(args.scope)
                scope = json.loads(scope_path.read_text(encoding="utf-8"))
                changed_files = scope.get("files_touched_list")
                if not isinstance(changed_files, list) or not all(
                    isinstance(path, str) for path in changed_files
                ):
                    raise ValueError(
                        "scope.json files_touched_list must be an array of strings"
                    )
                changed_ranges = scope.get("changed_line_ranges")
                if changed_ranges is not None and not isinstance(changed_ranges, dict):
                    raise ValueError(
                        "scope.json changed_line_ranges must be an object when present"
                    )
                if changed_ranges is not None:
                    for path, ranges in changed_ranges.items():
                        if not isinstance(path, str) or not isinstance(ranges, list):
                            raise ValueError(
                                "scope.json changed_line_ranges must map paths to lists"
                            )
                        if any(
                            not isinstance(item, list)
                            or len(item) != 2
                            or not all(
                                type(value) is int and value > 0 for value in item
                            )
                            or item[0] > item[1]
                            for item in ranges
                        ):
                            raise ValueError(
                                "scope.json changed_line_ranges must contain positive "
                                "[start, end] pairs"
                            )
                findings = filter_to_changed_files(
                    findings,
                    changed_files,
                    Path(args.repo),
                    changed_ranges,
                )
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 4

    out = Path(args.output) if args.output else None
    _write_jsonl(findings, out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
