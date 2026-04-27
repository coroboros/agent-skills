#!/usr/bin/env python3
"""
utils.py — shared I/O and helpers for brand-voice scripts.

Mirrors skills/humanize-en/scripts/utils.py — same I/O contract.
Requires Python 3.7+. No third-party dependencies.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def read_text(path_or_dash):
    """Read UTF-8 text from a path, or stdin if path is '-'.

    Raises FileNotFoundError if the path does not resolve.
    """
    if path_or_dash == "-":
        return sys.stdin.read()
    path = Path(path_or_dash)
    if not path.is_file():
        raise FileNotFoundError(f"file not found: {path_or_dash}")
    return path.read_text(encoding="utf-8")


def read_json(path_or_dash):
    """Read JSON from a path, or stdin if path is '-'."""
    return json.loads(read_text(path_or_dash))


def write_json(obj, path=None, indent=2):
    """Write JSON to a path, or stdout if path is None."""
    output = json.dumps(obj, ensure_ascii=False, indent=indent)
    if path is None:
        print(output)
    else:
        Path(path).write_text(output + "\n", encoding="utf-8")


def split_frontmatter(text):
    """Return (frontmatter_lines, body_text). Frontmatter is the YAML between
    the leading and second '---' delimiters. body_text excludes the frontmatter
    block and the delimiters but preserves all subsequent newlines.

    Returns (None, text) if no frontmatter is present.
    """
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\n") != "---":
        return None, text
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].rstrip("\n") == "---":
            end_idx = i
            break
    if end_idx is None:
        return None, text
    frontmatter_block = "".join(lines[1:end_idx])
    body = "".join(lines[end_idx + 1 :])
    return frontmatter_block, body


def parse_yaml_minimal(yaml_text):
    """Parse a minimal subset of YAML used by BRAND-VOICE.md frontmatter.

    Supports: nested dicts (2-space indent), lists of scalars, lists of inline
    objects ({k: v, k: v}), strings (quoted/unquoted), booleans, integers.

    Does NOT support: anchors, aliases, multi-line strings (|, >), tags, flow
    sequences across lines.

    Returns a dict. Raises ValueError on parse error with a `.line` attribute
    set to the offending 1-indexed line number.

    Implementation note: this is a deliberate hand-roll to keep the script
    dependency-free (no PyYAML). The frontmatter shape is well-defined by
    canonical-format.md — exotic YAML constructs are out of scope.
    """
    lines = yaml_text.splitlines()
    pos = [0]

    def err(msg, lineno):
        e = ValueError(f"yaml: {msg} (line {lineno + 1})")
        e.line = lineno + 1
        return e

    def peek():
        while pos[0] < len(lines):
            line = lines[pos[0]]
            stripped = line.split("#", 1)[0].rstrip()
            if stripped:
                return stripped, pos[0]
            pos[0] += 1
        return None, len(lines)

    def indent_of(line):
        return len(line) - len(line.lstrip(" "))

    def parse_scalar(s, lineno):
        s = s.strip()
        if not s:
            return None
        if s.startswith('"') and s.endswith('"'):
            inner = s[1:-1]
            return (
                inner
                .replace('\\"', '"')
                .replace("\\\\", "\\")
                .replace("\\n", "\n")
                .replace("\\t", "\t")
            )
        if s.startswith("'") and s.endswith("'"):
            return s[1:-1]
        if s == "true":
            return True
        if s == "false":
            return False
        if s == "null" or s == "~":
            return None
        if re.fullmatch(r"-?\d+", s):
            return int(s)
        if re.fullmatch(r"-?\d+\.\d+", s):
            return float(s)
        if s.startswith("[") and s.endswith("]"):
            inner = s[1:-1].strip()
            if not inner:
                return []
            return [parse_scalar(x.strip(), lineno) for x in _split_flow(inner)]
        if s.startswith("{") and s.endswith("}"):
            inner = s[1:-1].strip()
            if not inner:
                return {}
            result = {}
            for pair in _split_flow(inner):
                if ":" not in pair:
                    raise err(f"flow object missing ':' in '{pair}'", lineno)
                k, v = pair.split(":", 1)
                result[k.strip()] = parse_scalar(v.strip(), lineno)
            return result
        return s

    def parse_block(min_indent):
        line, lineno = peek()
        if line is None:
            return None
        cur_indent = indent_of(lines[lineno])
        if cur_indent < min_indent:
            return None
        if line.lstrip().startswith("- "):
            return parse_list(cur_indent)
        return parse_map(cur_indent)

    def parse_list(indent):
        items = []
        while True:
            line, lineno = peek()
            if line is None:
                break
            cur_indent = indent_of(lines[lineno])
            if cur_indent < indent or not line.lstrip().startswith("- "):
                break
            content = line.lstrip()[2:].rstrip()
            pos[0] += 1
            if not content:
                items.append(parse_block(indent + 2))
                continue
            if ":" in content and not (
                content.startswith('"') or content.startswith("'") or content.startswith("[") or content.startswith("{")
            ):
                k, v = content.split(":", 1)
                v = v.strip()
                obj = {}
                if v:
                    obj[k.strip()] = parse_scalar(v, lineno)
                else:
                    obj[k.strip()] = parse_block(indent + 2)
                while True:
                    nxt_line, nxt_lineno = peek()
                    if nxt_line is None:
                        break
                    nxt_indent = indent_of(lines[nxt_lineno])
                    if nxt_indent <= indent:
                        break
                    if nxt_line.lstrip().startswith("- "):
                        break
                    if ":" not in nxt_line:
                        raise err(f"unexpected line in list-of-objects: '{nxt_line}'", nxt_lineno)
                    k2, v2 = nxt_line.split(":", 1)
                    v2 = v2.strip()
                    pos[0] += 1
                    if v2:
                        obj[k2.strip().lstrip()] = parse_scalar(v2, nxt_lineno)
                    else:
                        obj[k2.strip().lstrip()] = parse_block(nxt_indent + 2)
                items.append(obj)
            else:
                items.append(parse_scalar(content, lineno))
        return items

    def parse_map(indent):
        result = {}
        while True:
            line, lineno = peek()
            if line is None:
                break
            cur_indent = indent_of(lines[lineno])
            if cur_indent < indent:
                break
            if cur_indent > indent:
                raise err(f"unexpected indent (got {cur_indent}, want {indent})", lineno)
            if line.lstrip().startswith("- "):
                break
            stripped = line.lstrip()
            if ":" not in stripped:
                raise err(f"expected 'key:' got '{stripped}'", lineno)
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            pos[0] += 1
            if value:
                result[key] = parse_scalar(value, lineno)
            else:
                child = parse_block(indent + 2)
                result[key] = child if child is not None else {}
        return result

    return parse_block(0) or {}


def _split_flow(s):
    """Split a flow-style YAML inner content (`a, b, c` or `k: v, k: v`) on
    commas while respecting [] and {} nesting and quoted strings."""
    out = []
    depth = 0
    quote = None
    start = 0
    for i, ch in enumerate(s):
        if quote:
            if ch == quote:
                quote = None
            continue
        if ch in ('"', "'"):
            quote = ch
            continue
        if ch in ("[", "{"):
            depth += 1
        elif ch in ("]", "}"):
            depth -= 1
        elif ch == "," and depth == 0:
            out.append(s[start:i])
            start = i + 1
    out.append(s[start:])
    return [x.strip() for x in out if x.strip()]


def list_h2_sections(body_text):
    """Return a list of (heading_text, line_number) for each H2 in body_text.

    Line numbers are 1-indexed relative to body_text. Code-fenced blocks are
    skipped so a `## something` inside a code block doesn't count.
    """
    out = []
    in_fence = False
    for idx, line in enumerate(body_text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if stripped.startswith("## ") and not stripped.startswith("###"):
            out.append((stripped[3:].strip(), idx))
    return out


def normalise_section_heading(heading):
    """Strip leading numbering ('1.', '1', '1 /') and lowercase the heading.

    'Core Voice Attributes' → 'core voice attributes'
    '1. Core voice attributes' → 'core voice attributes'
    '1 / Core voice attributes' → 'core voice attributes'
    """
    text = heading.strip().lower()
    text = re.sub(r"^\d+\s*[.\/]?\s*", "", text)
    return text.strip()
