#!/usr/bin/env python3
"""
extract_rules.py — emit a flat, prose-free list of testable voice rules.

Usage:
    extract_rules.py <BRAND-VOICE.md>
    cat BRAND-VOICE.md | extract_rules.py -

Output (stdout, plain text per references/schemas.md § extract_rules.py):

    voice: <name>
    last_updated: <date>

    forbidden:
      - <term>
      - ...

    required:
      - <term>
      - ...

    sentence_norms:
      word_count: <min>-<max> (hard max: <hard>)
      contractions: ...
      ...

    forbidden_patterns:
      - ...

    rewrite_rules:
      - [<rule_id>] <reject> -> <accept>
      - ...

    pronouns: <default> (forbid: <list>)

Empty fields are omitted. Designed for inclusion in a downstream LLM prompt
without JSON parsing — humanize-en consumes this output directly.

Exit:
    0  extraction succeeded
    1  file not found, unreadable, or YAML invalid

Requires Python 3.7+. No third-party dependencies.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow `python3 path/to/extract_rules.py` and `extract_rules.py` invocations.
sys.path.insert(0, str(Path(__file__).parent))
from utils import parse_yaml_minimal, read_text, split_frontmatter  # noqa: E402


def _emit_list(label, items, out):
    if not items:
        return
    out.append(f"{label}:")
    for item in items:
        out.append(f"  - {item}")
    out.append("")


def _emit_section_header(label, out):
    out.append(f"{label}:")


def format_rules(data):
    """Return the plain-text rules block as a string."""
    out = []

    voice = data.get("voice") or {}
    name = voice.get("name") or "(unnamed)"
    last_updated = voice.get("last_updated")
    out.append(f"voice: {name}")
    if last_updated:
        out.append(f"last_updated: {last_updated}")
    out.append("")

    _emit_list("forbidden", data.get("forbidden_lexicon") or [], out)
    _emit_list("required", data.get("required_lexicon") or [], out)

    norms = data.get("sentence_norms") or {}
    if norms:
        _emit_section_header("sentence_norms", out)
        wmin = norms.get("word_count_min")
        wmax = norms.get("word_count_max")
        whard = norms.get("sentence_max_hard")
        if wmin is not None and wmax is not None:
            line = f"  word_count: {wmin}-{wmax}"
            if whard is not None:
                line += f" (hard max: {whard})"
            out.append(line)
        for key in ("contractions", "oxford_comma", "em_dash_spacing", "exclamation_marks"):
            if key in norms:
                value = norms[key]
                if isinstance(value, bool):
                    value = "true" if value else "false"
                out.append(f"  {key}: {value}")
        out.append("")

    _emit_list("forbidden_patterns", data.get("forbidden_patterns") or [], out)

    rules = data.get("rewrite_rules") or []
    if rules:
        _emit_section_header("rewrite_rules", out)
        for rule in rules:
            if not isinstance(rule, dict):
                continue
            rule_id = rule.get("rule_id") or "?"
            reject = rule.get("reject") or "?"
            accept = rule.get("accept") or "?"
            out.append(f"  - [{rule_id}] {reject} -> {accept}")
        out.append("")

    pronouns = data.get("pronouns") or {}
    if pronouns:
        default = pronouns.get("default") or "(unspecified)"
        forbid = pronouns.get("forbid") or []
        forbid_str = ", ".join(forbid) if forbid else "none"
        out.append(f"pronouns: {default} (forbid: {forbid_str})")

    while out and out[-1] == "":
        out.pop()
    return "\n".join(out) + "\n"


def main():
    if len(sys.argv) < 2:
        print("usage: extract_rules.py <BRAND-VOICE.md> | extract_rules.py -", file=sys.stderr)
        return 1

    arg = sys.argv[1]
    try:
        text = read_text(arg)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"error: cannot read '{arg}': {exc}", file=sys.stderr)
        return 1

    fm, _body = split_frontmatter(text)
    if fm is None:
        print(f"error: '{arg}' has no YAML frontmatter", file=sys.stderr)
        return 1

    try:
        data = parse_yaml_minimal(fm)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    sys.stdout.write(format_rules(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
