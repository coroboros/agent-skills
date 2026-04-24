#!/usr/bin/env python3
"""
utils.py — shared I/O and helpers for humanize-en scripts.

Requires Python 3.7+. No third-party dependencies.
"""

from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path

# Canonical seed for any sampling the eval infrastructure does.
# Reproducibility mirrors the skill-creator pattern (seed=42).
SEED = 42


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


def mask_protected_regions(text):
    """Replace fenced code, backtick spans, URLs, anchors, and YAML frontmatter
    with spaces of equal length so pattern scans skip them but line numbers
    stay intact. Mirrors prescan.py's behaviour so eval scripts score the
    same regions the prescan did."""

    def _blank(m):
        return " " * len(m.group(0))

    text = re.sub(r"\A---\n.*?\n---\n", _blank, text, count=1, flags=re.DOTALL)
    text = re.sub(r"```.*?```", _blank, text, flags=re.DOTALL)
    text = re.sub(r"~~~.*?~~~", _blank, text, flags=re.DOTALL)
    text = re.sub(r"`[^`\n]+`", _blank, text)
    text = re.sub(r"\]\([^)]*\)", _blank, text)
    text = re.sub(r"https?://\S+", _blank, text)
    return text


def seeded_rng():
    """Return a Random instance seeded with the canonical seed."""
    return random.Random(SEED)
