#!/usr/bin/env python3
"""
validate_rule_file.py — validate a `.claude/rules/*.md` rule file.

Usage:
    validate_rule_file.py <path>

Checks:
  - File has a well-formed YAML frontmatter block (opening and closing `---`
    on their own lines) OR no frontmatter at all (unconditionally-loaded rule).
  - When frontmatter is present and contains a `paths:` key, the value is a
    YAML-style list of quoted or unquoted glob strings.
  - Each `paths:` entry looks like a glob (no unsupported tokens, trailing
    spaces, or stray commas).

Exit:
  0   valid
  1   frontmatter or paths violation
  2   argument or I/O error

Emits a JSON report on stdout:
  {
    "has_frontmatter": bool,
    "has_paths": bool,
    "paths": ["src/**/*.ts", ...],
    "errors": ["..."],
    "summary": {"ok": bool}
  }

Requires Python 3.7+. No third-party dependencies (intentional — a minimal
parser avoids a PyYAML install on every user machine). Accepts the subset
of YAML the rules directory actually uses: `paths:` followed by `- item`
list entries, strings single- or double-quoted or bare.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
PATHS_KEY_RE = re.compile(r"^paths:\s*(.*)$", re.MULTILINE)
LIST_ITEM_RE = re.compile(r"^\s*-\s+(.+)$")
GLOB_OK_RE = re.compile(r"^[\w./*{},\[\]!\- ]+$")


def parse_paths(frontmatter):
    """Return (declared, items) where declared is True iff `paths:` appears."""
    m = PATHS_KEY_RE.search(frontmatter)
    if not m:
        return False, []

    inline = m.group(1).strip()
    # Inline list `paths: [a, b]` — parse it.
    if inline.startswith("[") and inline.endswith("]"):
        inside = inline[1:-1]
        raw_items = [s.strip() for s in inside.split(",") if s.strip()]
        items = []
        for raw in raw_items:
            if (raw.startswith('"') and raw.endswith('"')) or (
                raw.startswith("'") and raw.endswith("'")
            ):
                raw = raw[1:-1]
            items.append(raw)
        return True, items

    # Block list form — lines starting with `-` below `paths:`.
    lines = frontmatter.splitlines()
    items = []
    collecting = False
    for line in lines:
        if PATHS_KEY_RE.match(line):
            collecting = True
            continue
        if collecting:
            stripped = line.strip()
            if not stripped:
                continue
            im = LIST_ITEM_RE.match(line)
            if im:
                raw = im.group(1).strip()
                if (raw.startswith('"') and raw.endswith('"')) or (
                    raw.startswith("'") and raw.endswith("'")
                ):
                    raw = raw[1:-1]
                items.append(raw)
            else:
                # Any non-list line after `paths:` ends the block.
                break
    return True, items


def main():
    if len(sys.argv) < 2:
        print("usage: validate_rule_file.py <path>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    fm_match = FRONTMATTER_RE.search(text)

    errors = []
    has_frontmatter = fm_match is not None
    has_paths = False
    paths_out = []

    if has_frontmatter:
        frontmatter = fm_match.group(1)
        if frontmatter.strip() == "":
            errors.append("frontmatter block is empty (`---` bookends with no content)")

        declared, paths = parse_paths(frontmatter)
        has_paths = declared
        if declared:
            if not paths:
                errors.append("`paths:` declared but has no list items")
            else:
                for idx, entry in enumerate(paths, start=1):
                    if not entry:
                        errors.append(f"paths[{idx}]: empty glob")
                    elif not GLOB_OK_RE.match(entry):
                        errors.append(
                            f"paths[{idx}]: unexpected characters in glob ({entry!r})"
                        )
            paths_out = paths

    report = {
        "has_frontmatter": has_frontmatter,
        "has_paths": has_paths,
        "paths": paths_out,
        "errors": errors,
        "summary": {"ok": not errors},
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
