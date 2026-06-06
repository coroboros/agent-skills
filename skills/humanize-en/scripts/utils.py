#!/usr/bin/env python3
"""
utils.py — shared I/O and helpers for humanize-en scripts.

Requires Python 3.7+. No third-party dependencies.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

# Mirrors the skill-creator seed for reproducible sampling.
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


def mask_protected_regions(text, strict_code_only=False):
    """Replace protected regions with whitespace so eval scoring stays consistent
    with prescan.py. Mirrors prescan.py:mask_protected_regions exactly — when
    one changes, both must change."""
    from prescan import mask_protected_regions as _mask  # local import avoids cycle
    return _mask(text, strict_code_only=strict_code_only)


def seeded_rng():
    """Return a Random instance seeded with the canonical seed."""
    return random.Random(SEED)
