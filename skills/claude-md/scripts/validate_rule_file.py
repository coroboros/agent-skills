#!/usr/bin/env python3
"""
validate_rule_file.py — validate a `.claude/rules/*.md` rule file.

Usage:
    validate_rule_file.py <path>

Checks:
  - File has a delimited frontmatter block (opening and closing `---`
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
parser avoids a PyYAML install on every user machine). Checks frontmatter
delimiters and a bounded YAML `paths:` list subset, not unrelated YAML keys.
Glob strings can be quoted or plain; YAML indicators must be quoted.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---(?:\n|\Z)", re.DOTALL)
PATHS_KEY_RE = re.compile(r"^paths:[ \t]*(.*)$", re.MULTILINE)
LIST_ITEM_RE = re.compile(r"^([ \t]*)-\s+(.+)$")
GLOB_OK_RE = re.compile(r"^[\w./*{},\[\]!\- ]+$")


def path_scalar(raw, flow=False):
    """Decode the supported YAML string subset without accepting aliases."""
    raw = raw.strip()
    if not raw:
        raise ValueError("empty paths item; supply a quoted glob")
    if raw.startswith('"'):
        try:
            return json.loads(raw)
        except ValueError as exc:
            raise ValueError("invalid double-quoted paths item; use a JSON-style string") from exc
    if raw.startswith("'"):
        if not re.fullmatch(r"'(?:[^']|'')*'", raw):
            raise ValueError("invalid single-quoted paths item")
        return raw[1:-1].replace("''", "'")
    if (raw[0] in "!&*?{}[],:>#%@`|-'\"" or re.search(r":\s|\s#", raw)
            or (flow and re.search(r"[\[\]{},]", raw))
            or raw.lower() in {"null", "~", "true", "false", "yes", "no", "on", "off", ".inf", ".nan"}
            or raw[0].isdigit() or re.match(r"\.\d", raw)):
        raise ValueError(f"quote paths item {raw!r} so YAML reads a glob string, not an indicator or value")
    return raw


def inline_items(inside):
    """Split a flow list while keeping quoted commas and scalar syntax."""
    if not inside.strip():
        return []
    parts = re.findall(r'''(?:"(?:[^"\\]|\\.)*"|'(?:[^']|'')*'|[^,])+|,''', inside)
    items = []
    expect_item = True
    for part in parts:
        if part == ",":
            if expect_item:
                raise ValueError("empty paths item in inline list")
            expect_item = True
        else:
            if not expect_item:
                raise ValueError("paths items must be separated by commas")
            items.append(path_scalar(part, flow=True))
            expect_item = False
    return items


def parse_paths(frontmatter):
    """Return (declared, items) where declared is True iff `paths:` appears."""
    m = PATHS_KEY_RE.search(frontmatter)
    if not m:
        return False, []

    inline = m.group(1).strip()
    # Inline list form: `paths: [a, b]`.
    if inline.startswith("[") and inline.endswith("]"):
        inside = inline[1:-1]
        return True, inline_items(inside)

    if inline:
        raise ValueError("`paths:` must be a complete inline list or a block list")

    # Block list form — lines starting with `-` below `paths:`.
    lines = frontmatter.splitlines()
    items = []
    collecting = False
    list_indent = None
    for line in lines:
        if PATHS_KEY_RE.match(line):
            collecting = True
            continue
        if collecting:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            im = LIST_ITEM_RE.match(line)
            if im:
                indent = im.group(1)
                if "\t" in indent or (list_indent is not None and indent != list_indent):
                    raise ValueError("paths list items must use the same space indentation")
                list_indent = indent
                items.append(path_scalar(im.group(2)))
            else:
                if re.match(r"^[\w-]+:", line):
                    break  # the next top-level frontmatter key
                raise ValueError("paths must be a flat list of glob strings")
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

    if text.startswith("---\n") and not has_frontmatter:
        errors.append("frontmatter opening delimiter has no closing `---`")

    if has_frontmatter:
        frontmatter = fm_match.group(1)
        if frontmatter.strip() == "":
            errors.append("frontmatter block is empty (`---` bookends with no content)")

        try:
            declared, paths = parse_paths(frontmatter)
        except ValueError as exc:
            errors.append(str(exc))
            declared, paths = True, []
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
