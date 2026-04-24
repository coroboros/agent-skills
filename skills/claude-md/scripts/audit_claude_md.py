#!/usr/bin/env python3
"""
audit_claude_md.py — deterministic bloat + structure audit of a CLAUDE.md.

Usage:
    audit_claude_md.py <path>

Checks:
  - Line count vs the 200-line target (over 200 degrades adherence)
  - 6 bloat categories (linter-enforced rules, marketing/vision,
    obvious info, verbose explanations, redundant specs, generic
    best practices) — each with a regex catalog
  - `@import` references resolve to existing files

Exit:
  0   clean (no bloat hits, no broken imports, under target length)
  1   findings (details in JSON)
  2   argument or I/O error

Emits a JSON report on stdout:
  {
    "lines": N,
    "target_lines": 200,
    "over_target": bool,
    "bloat": [ {"line": L, "category": "...", "match": "..."} ],
    "broken_imports": [ {"line": L, "path": "..."} ],
    "summary": {"ok": bool, "findings": N}
  }

Requires Python 3.7+. No third-party dependencies.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

TARGET_LINES = 200

BLOAT_CATEGORIES = {
    "linter-enforced": [
        r"\beslint\b", r"\bprettier\b", r"\bbiome\b",
        r"typescript[- ]strict",
        r"use\s+strict\s+typing",
        r"format\s+code\s+properly",
        r"run\s+(?:npm|pnpm|yarn)\s+(?:lint|format)\s+before\s+commit",
    ],
    "marketing-or-vision": [
        r"^\s*(mission|vision|goals?)\s*:",
        r"we\s+believe",
        r"\bour\s+commitment\b",
        r"\bmission\s+statement\b",
        r"\bbest[- ]in[- ]class\b",
    ],
    "obvious-info": [
        r"node_modules/\s+contains",
        r"package\.json\s+contains\s+dependencies",
        r"framework\s+default",
        r"standard\s+(?:react|next|astro|python|node)",
    ],
    "verbose-explanation": [
        r"for\s+more\s+information",
        r"it\s+is\s+important\s+to\s+(?:note|remember)",
        r"please\s+(?:note|make\s+sure|ensure)",
        r"at\s+this\s+point\s+in\s+time",
        r"in\s+order\s+to",
    ],
    "redundant-spec": [
        r"required\s+dependencies:",
        r"environment\s+variables:\s*$",
        r"package\s+scripts\s+available",
    ],
    "generic-best-practices": [
        r"\bwrite\s+clean\s+code\b",
        r"\bDRY\s+principle\b",
        r"\bSOLID\s+principles?\b",
        r"follow\s+best\s+practices",
        r"\bKISS\s+principle\b",
        r"keep\s+it\s+simple",
        r"separation\s+of\s+concerns",
    ],
}

IMPORT_RE = re.compile(r"@([^\s@]+\.md)")


def mask_protected(text):
    """Blank out fenced code, HTML comments, and inline backticks so their
    content doesn't trigger bloat patterns or phantom imports."""

    def _blank(m):
        return " " * len(m.group(0))

    text = re.sub(r"```.*?```", _blank, text, flags=re.DOTALL)
    text = re.sub(r"<!--.*?-->", _blank, text, flags=re.DOTALL)
    text = re.sub(r"`[^`\n]+`", _blank, text)
    return text


def scan_bloat(lines):
    hits = []
    for lineno, line in enumerate(lines, start=1):
        for category, patterns in BLOAT_CATEGORIES.items():
            for pattern in patterns:
                m = re.search(pattern, line, flags=re.IGNORECASE)
                if m:
                    hits.append(
                        {
                            "line": lineno,
                            "category": category,
                            "match": m.group(0),
                        }
                    )
    return hits


def check_imports(text, source_dir):
    broken = []
    for m in IMPORT_RE.finditer(text):
        path = m.group(1)
        # Resolve relative to the file's directory; ~ and absolute paths too.
        expanded = Path(path).expanduser()
        if not expanded.is_absolute():
            expanded = source_dir / expanded
        if not expanded.is_file():
            line = text.count("\n", 0, m.start()) + 1
            broken.append({"line": line, "path": path})
    return broken


def main():
    if len(sys.argv) < 2:
        print("usage: audit_claude_md.py <path>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    raw = path.read_text(encoding="utf-8")
    masked = mask_protected(raw)
    lines = masked.splitlines()

    total_lines = len(raw.splitlines())

    bloat_hits = scan_bloat(lines)
    broken_imports = check_imports(raw, path.parent)

    findings = len(bloat_hits) + len(broken_imports)
    over_target = total_lines > TARGET_LINES
    if over_target:
        findings += 1

    report = {
        "lines": total_lines,
        "target_lines": TARGET_LINES,
        "over_target": over_target,
        "bloat": bloat_hits,
        "broken_imports": broken_imports,
        "summary": {"ok": findings == 0, "findings": findings},
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if findings == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
