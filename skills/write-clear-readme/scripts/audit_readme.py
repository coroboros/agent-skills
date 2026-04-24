#!/usr/bin/env python3
"""
audit_readme.py — deterministic structural + bloat audit of a README.

Usage:
    audit_readme.py <path>

Hard checks (count toward finding total):
  - Every `[text](#anchor)` link resolves to a heading defined in the file.
  - No nested `<details>` blocks (one-level-max rule).
  - Every `<summary>` is followed within 3 lines by a `<br>` (Pattern A
    / Pattern B discipline).
  - Universal bloat tokens: "in order to", "leverage", "seamlessly",
    "powerful", "robust", "it's important to note", "at this point in time".

Soft check (reported, not counted — Pattern A groups intentionally place
item anchors inside `<details>`; GitHub auto-expands on hash navigation):
  - Anchors whose target heading sits inside a `<details>` block.

Output (stdout): JSON object
  {
    "anchors": { "unresolved": [...], "inside_details_info": [...] },
    "details": { "nested": [...], "summary_missing_br": [...] },
    "bloat": [ {"line": L, "token": "..."}, ... ],
    "summary": {
      "ok": bool,
      "findings": N,
      "rules": {
        "anchors":        { "findings": N, "pass": bool },
        "nested_details": { "findings": N, "pass": bool },
        "summary_br":     { "findings": N, "pass": bool },
        "bloat":          { "findings": N, "pass": bool }
      }
    }
  }

Exit:
  0   no hard findings (README clean)
  1   one or more hard findings (details in JSON)
  2   argument or I/O error

Requires Python 3.7+. No third-party dependencies.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# --- Regexes ---------------------------------------------------------------

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
ANCHOR_LINK_RE = re.compile(r"\[(?P<text>[^\]]+)\]\(#(?P<anchor>[^)\s]+)\)")
DETAILS_OPEN_RE = re.compile(r"<details\b", re.IGNORECASE)
DETAILS_CLOSE_RE = re.compile(r"</details\s*>", re.IGNORECASE)
SUMMARY_OPEN_RE = re.compile(r"<summary\b", re.IGNORECASE)
SUMMARY_CLOSE_RE = re.compile(r"</summary\s*>", re.IGNORECASE)
BR_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)

BLOAT_PATTERNS = [
    (re.compile(r"\bin\s+order\s+to\b", re.IGNORECASE), "in order to"),
    (re.compile(r"\bleverage[ds]?\b", re.IGNORECASE), "leverage"),
    (re.compile(r"\bseamlessly\b", re.IGNORECASE), "seamlessly"),
    (re.compile(r"\bpowerful\b", re.IGNORECASE), "powerful"),
    (re.compile(r"\brobust\b", re.IGNORECASE), "robust"),
    (re.compile(r"\bit['’]s\s+important\s+to\s+note\b", re.IGNORECASE), "it's important to note"),
    (re.compile(r"\bat\s+(?:this|the)\s+point\s+in\s+time\b", re.IGNORECASE), "at this point in time"),
    (re.compile(r"\bneedless\s+to\s+say\b", re.IGNORECASE), "needless to say"),
]


# --- GitHub-style anchor slugging -----------------------------------------

def slugify(heading):
    """Approximate GitHub's heading-to-anchor conversion.
    Lowercase, spaces → hyphens, strip non-word-except-hyphens."""
    s = heading.strip().lower()
    # Strip inline markdown: `code`, **bold**, *italic*, [text](url) → text
    s = re.sub(r"`([^`]*)`", r"\1", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
    s = re.sub(r"\*([^*]+)\*", r"\1", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    # Replace spaces with hyphens; drop characters that aren't word chars or hyphens.
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^\w\-]", "", s, flags=re.UNICODE)
    return s


# --- Masking ---------------------------------------------------------------

def _blank(m):
    # Preserve newlines so line counting survives multi-line code fences.
    return "".join("\n" if c == "\n" else " " for c in m.group(0))


def mask_code_only(text):
    """Blank out fenced code and inline code. Preserves HTML tags for
    structural scans (<details>, <summary>, <br>)."""
    text = re.sub(r"```.*?```", _blank, text, flags=re.DOTALL)
    text = re.sub(r"~~~.*?~~~", _blank, text, flags=re.DOTALL)
    text = re.sub(r"`[^`\n]+`", _blank, text)
    return text


def mask_for_bloat(text):
    """Blank out code fences, inline code, URL targets, and HTML tags for
    the bloat-token scan."""
    text = mask_code_only(text)
    text = re.sub(r"\]\([^)]*\)", _blank, text)
    text = re.sub(r"<[^>\n]+>", _blank, text)
    return text


# --- Audit -----------------------------------------------------------------

def audit(text):
    # For structural HTML detection, strip only code fences/spans —
    # `<details>` literals inside fenced examples are documentation, not
    # real blocks. HTML tags must remain for this scan to see them.
    structural = mask_code_only(text)

    # Collect all headings → (line, text, slug) from the RAW text (headings
    # can sit anywhere, including inside details).
    headings = []
    for m in HEADING_RE.finditer(text):
        line_num = text.count("\n", 0, m.start()) + 1
        heading_text = m.group(2)
        headings.append((line_num, heading_text, slugify(heading_text)))

    known_slugs = {slug for _, _, slug in headings}

    # Detail block ranges from the code-stripped view.
    details_opens = [m.start() for m in DETAILS_OPEN_RE.finditer(structural)]
    details_closes = [m.start() for m in DETAILS_CLOSE_RE.finditer(structural)]

    # Pair opens/closes naively. Nested will produce unbalanced depth > 1.
    depth = 0
    nested_lines = []
    in_details_spans = []  # list of (start, end) character indices
    events = sorted(
        [(p, "open") for p in details_opens] + [(p, "close") for p in details_closes]
    )
    current_open = None
    for pos, kind in events:
        if kind == "open":
            depth += 1
            if depth > 1:
                nested_lines.append(text.count("\n", 0, pos) + 1)
            if current_open is None:
                current_open = pos
        else:
            depth -= 1
            if depth == 0 and current_open is not None:
                in_details_spans.append((current_open, pos))
                current_open = None

    def inside_details(char_idx):
        for start, end in in_details_spans:
            if start <= char_idx <= end:
                return True
        return False

    # Anchor links analysis.
    unresolved = []
    inside_details_info = []
    heading_anchor_pos = {slug: None for _, _, slug in headings}
    for m in HEADING_RE.finditer(text):
        slug = slugify(m.group(2))
        if heading_anchor_pos.get(slug) is None:
            heading_anchor_pos[slug] = m.start()

    for m in ANCHOR_LINK_RE.finditer(text):
        slug = m.group("anchor")
        line_num = text.count("\n", 0, m.start()) + 1
        if slug not in known_slugs:
            unresolved.append({"line": line_num, "anchor": slug})
        else:
            target_pos = heading_anchor_pos.get(slug)
            if target_pos is not None and inside_details(target_pos):
                inside_details_info.append({"line": line_num, "anchor": slug})

    # <summary> missing <br> check — run on code-stripped view so fenced
    # example <summary> blocks don't count.
    summary_missing_br = []
    for sm in SUMMARY_OPEN_RE.finditer(structural):
        close_m = SUMMARY_CLOSE_RE.search(structural, sm.end())
        if not close_m:
            continue
        after_pos = close_m.end()
        end_of_window = after_pos
        newlines_seen = 0
        while end_of_window < len(structural) and newlines_seen < 4:
            if structural[end_of_window] == "\n":
                newlines_seen += 1
            end_of_window += 1
        window = structural[after_pos:end_of_window]
        if not BR_RE.search(window):
            line_num = structural.count("\n", 0, sm.start()) + 1
            summary_missing_br.append({"line": line_num})

    # Bloat scan (on fully-masked text to skip code / links / HTML).
    masked = mask_for_bloat(text)
    bloat_hits = []
    for lineno, line in enumerate(masked.splitlines(), start=1):
        for regex, token in BLOAT_PATTERNS:
            if regex.search(line):
                bloat_hits.append({"line": lineno, "token": token})

    per_rule = {
        "anchors":        {"findings": len(unresolved),          "pass": not unresolved},
        "nested_details": {"findings": len(nested_lines),        "pass": not nested_lines},
        "summary_br":     {"findings": len(summary_missing_br),  "pass": not summary_missing_br},
        "bloat":          {"findings": len(bloat_hits),          "pass": not bloat_hits},
    }
    findings = sum(rule["findings"] for rule in per_rule.values())

    return {
        "anchors": {
            "unresolved": unresolved,
            "inside_details_info": inside_details_info,
        },
        "details": {
            "nested": [{"line": n} for n in nested_lines],
            "summary_missing_br": summary_missing_br,
        },
        "bloat": bloat_hits,
        "summary": {
            "ok": findings == 0,
            "findings": findings,
            "rules": per_rule,
        },
    }


def main():
    if len(sys.argv) < 2:
        print("usage: audit_readme.py <path>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    report = audit(text)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["summary"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
