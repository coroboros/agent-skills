#!/usr/bin/env python3
"""
audit_readme.py — deterministic structural + bloat audit of a README.

Usage:
    audit_readme.py <path>

Hard checks (count toward finding total):
  - Every `[text](#anchor)` link resolves to a heading defined in the file.
  - No nested `<details>` blocks (one-level-max rule).
  - Every `<summary>` is followed by a `<br>` within the same line or
    the next 3 lines (Pattern A / B / C discipline).
  - Universal bloat tokens: "in order to", "leverage", "seamlessly",
    "powerful", "robust", "it's important to note", "at this point in time".
  - `<summary>` text starting with `Expand —` (or `Expand –`, `Expand -`).
    The disclosure triangle is the affordance; the prefix is noise.
  - Stale numeric content-counts adjacent to maintainable nouns
    ("25 symlinks", "14 tasks") — rot the moment a row is added.
  - Heading (h2-h6) immediately above a `<details>` whose `<summary>`
    repeats the same label — duplicate signal.

Soft checks (reported, not counted):
  - Anchors whose target heading sits inside a `<details>` block
    (Pattern B groups intentionally place item anchors inside).
  - Visual rhythm — count of GitHub callouts and images. Long
    READMEs with zero of either read as flat; surfaced as a hint.

Output (stdout): JSON object — see `summary.rules` for the canonical
list of per-rule findings and pass flags.

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

# `<summary>Expand — foo</summary>` — strip the prefix (any em-dash / en-dash / hyphen).
EXPAND_PREFIX_RE = re.compile(r"^\s*expand\s+[—–\-]\s*", re.IGNORECASE)

# Numeric content-counts adjacent to maintainable nouns. Narrow on purpose:
# "Python 3.7" / "page 5" / "version 1.20" must NOT trigger. Generic nouns
# like "files", "rows", "columns", "fields" are intentionally excluded —
# they show up in too many non-stale contexts (thresholds, API limits,
# generic descriptions) to be reliable signals on their own.
STALE_COUNT_NOUNS = (
    "symlinks|tasks|imports|tables|commands|hooks|aliases|skills|"
    "packages|entries|items|sections|plugins|dependencies|scripts|"
    "tests|rules|headings|bullets|paragraphs|footnotes"
)
# Allow up to three words (adjectives) between the digit and the noun, so
# "14 declared periodic tasks" matches alongside the plain "25 symlinks".
STALE_COUNT_RE = re.compile(
    r"\b(\d+)(?:\s+\w+){0,3}\s+(" + STALE_COUNT_NOUNS + r")\b",
    re.IGNORECASE,
)

# Stability prefixes — when they sit immediately before the digit, the
# count describes a threshold or API limit, not internal content. Examples:
# `up to 100 tasks per call`, `>5 commands`, `max 3 retries`, `batches of 50`.
STABILITY_PREFIX_RE = re.compile(
    r"(?:>|<|≤|≥|=|max\.?|up\s+to|batches?\s+of|each\s+of|per|page\s+size\s+of|top|first|last)\s*$",
    re.IGNORECASE,
)
# Range prefix like `2–3 tasks` or `2-3 tasks` — the digit is the upper
# bound of a descriptive range, not a stable count of internal content.
RANGE_PREFIX_RE = re.compile(r"\d\s*[–—-]\s*$")

# GitHub callouts: `> [!NOTE|TIP|WARNING|IMPORTANT|CAUTION] ...`
CALLOUT_RE = re.compile(
    r"^>\s*\[!(NOTE|TIP|WARNING|IMPORTANT|CAUTION)\]",
    re.IGNORECASE | re.MULTILINE,
)
MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)\s]+(?:\s+\"[^\"]*\")?\)")
HTML_IMG_RE = re.compile(r"<img\s[^>]*>", re.IGNORECASE)

# A long README — threshold for the visual-rhythm soft signal.
VISUAL_RHYTHM_LINE_THRESHOLD = 200


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


# --- Helpers ---------------------------------------------------------------

def _normalize_label(s):
    """Lowercase + collapse whitespace + strip surrounding punctuation/symbols.
    Used to compare heading text to <summary> text for redundancy detection."""
    s = re.sub(r"\s+", " ", s.lower().strip())
    s = s.strip(" \t·•—–-")
    return s


def find_summary_blocks(structural_text):
    """Yield (start_pos, end_pos, inner_text_stripped) for each <summary>…</summary>
    in the code-stripped text. inner_text_stripped has HTML tags removed."""
    pos = 0
    while True:
        open_m = SUMMARY_OPEN_RE.search(structural_text, pos)
        if not open_m:
            break
        # Find the > that closes the opening tag.
        open_end = structural_text.find(">", open_m.end())
        if open_end < 0:
            break
        close_m = SUMMARY_CLOSE_RE.search(structural_text, open_end + 1)
        if not close_m:
            break
        inner = structural_text[open_end + 1 : close_m.start()]
        # Strip HTML tags so `<em>Expand — foo</em>` becomes `Expand — foo`.
        inner_clean = re.sub(r"<[^>]+>", "", inner).strip()
        yield open_m.start(), close_m.end(), inner_clean
        pos = close_m.end()


# --- Audit -----------------------------------------------------------------

def audit(text):
    # For structural HTML detection, strip only code fences/spans —
    # `<details>` literals inside fenced examples are documentation, not
    # real blocks. HTML tags must remain for this scan to see them.
    structural = mask_code_only(text)
    line_count = text.count("\n") + 1

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

    # Anchor links analysis. First-occurrence wins — earlier h2 anchors beat
    # later h4 collisions, matching GitHub's slug-deduplication intent.
    unresolved = []
    inside_details_info = []
    heading_anchor_pos = {}
    for m in HEADING_RE.finditer(text):
        slug = slugify(m.group(2))
        if slug not in heading_anchor_pos:
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

    # `Expand —` prefix in <summary>. Run on structural (code-stripped) so
    # fenced examples illustrating the wrong pattern don't count.
    expand_prefix_hits = []
    for start_pos, _, inner in find_summary_blocks(structural):
        if EXPAND_PREFIX_RE.match(inner):
            line_num = structural.count("\n", 0, start_pos) + 1
            expand_prefix_hits.append({"line": line_num, "summary": inner[:80]})

    # Stale numeric counts adjacent to maintainable nouns. Run on bloat-masked
    # text to skip code, link targets, and HTML attributes. Skip matches whose
    # digit is preceded by a stability prefix (`up to 100 tasks`) or a range
    # marker (`2–3 tasks`) — those describe limits or ranges, not internal
    # content that rots on add.
    stale_count_hits = []
    for lineno, line in enumerate(masked.splitlines(), start=1):
        for m in STALE_COUNT_RE.finditer(line):
            before = line[: m.start()]
            tail = before[-25:]
            if STABILITY_PREFIX_RE.search(tail):
                continue
            if RANGE_PREFIX_RE.search(tail):
                continue
            stale_count_hits.append({"line": lineno, "match": m.group(0)})

    # Redundant heading immediately above <details> whose <summary> repeats
    # the label. Walk events sorted by position to catch the pattern.
    redundant_heading_hits = []
    event_list = []
    for m in HEADING_RE.finditer(structural):
        event_list.append((m.start(), "heading", m.group(2).strip()))
    for start_pos, _, inner in find_summary_blocks(structural):
        details_open = structural.rfind("<details", 0, start_pos + 1)
        if details_open < 0:
            continue
        event_list.append((details_open, "details", inner))
    event_list.sort()
    for i in range(len(event_list) - 1):
        cur, nxt = event_list[i], event_list[i + 1]
        if cur[1] == "heading" and nxt[1] == "details":
            # Skip if anything substantive sits between them.
            lines_between = structural.count("\n", cur[0], nxt[0])
            if lines_between > 5:
                continue
            if _normalize_label(cur[2]) == _normalize_label(nxt[2]):
                line_num = structural.count("\n", 0, cur[0]) + 1
                redundant_heading_hits.append({
                    "line": line_num,
                    "heading": cur[2],
                    "summary": nxt[2],
                })

    # Visual rhythm — soft signal, not counted.
    callouts = len(CALLOUT_RE.findall(masked))
    images = len(MD_IMAGE_RE.findall(structural)) + len(HTML_IMG_RE.findall(structural))
    flat_flag = (
        line_count > VISUAL_RHYTHM_LINE_THRESHOLD
        and callouts == 0
        and images == 0
    )

    per_rule = {
        "anchors":           {"findings": len(unresolved),             "pass": not unresolved},
        "nested_details":    {"findings": len(nested_lines),           "pass": not nested_lines},
        "summary_br":        {"findings": len(summary_missing_br),     "pass": not summary_missing_br},
        "bloat":             {"findings": len(bloat_hits),             "pass": not bloat_hits},
        "expand_prefix":     {"findings": len(expand_prefix_hits),     "pass": not expand_prefix_hits},
        "stale_counts":      {"findings": len(stale_count_hits),       "pass": not stale_count_hits},
        "redundant_heading": {"findings": len(redundant_heading_hits), "pass": not redundant_heading_hits},
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
        "summary_quality": {
            "expand_prefix": expand_prefix_hits,
            "stale_counts": stale_count_hits,
            "redundant_heading": redundant_heading_hits,
        },
        "visual_rhythm": {
            "callouts": callouts,
            "images": images,
            "line_count": line_count,
            "flat_flag": flat_flag,
        },
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
