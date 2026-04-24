#!/usr/bin/env python3
"""
prescan.py — deterministic pre-scan for 8 of the 10 highest-signal AI tells.

Usage:
    prescan.py <file>
    cat file.md | prescan.py -

Scans for the mechanical, high-confidence patterns so the model starts
from a hit-list rather than re-deriving the catalogue on every run.
Skips content inside fenced code blocks, backticks, URLs, and YAML
frontmatter — those must never be rewritten.

Patterns covered (numbered per references/patterns.md):
   1  Significance inflation     — pivotal, testament, evolving landscape
   4  Promotional vocabulary     — nestled, breathtaking, vibrant, stunning
   7  AI vocabulary wordlist     — delve, tapestry, crucial, underscore, ...
   8  Copula avoidance           — serves as / stands as / features / boasts
   9  Negative parallelism       — "It's not just X, it's Y" / "not only ... but"
  14  Em-dash density            — ≥ 3 em-dashes per line (cheap heuristic for ≥ 4 per 100 words)
  23  Filler phrases             — in order to / it is important to note / at this point in time
  28  Signposting                — Let's dive in / Without further ado / Here's what

Patterns #3 (Superficial -ing) and #10 (Rule of three) from the top-10
SKILL.md Quick reference are deliberately LLM-only — too context-dependent
for regex without false positives.

Output (stdout):
  JSON array of hits — [{"pattern": N, "line": L, "snippet": "..."}]

Exit:
  0   scan complete (hits or not)
  1   argument or I/O error

Emits nothing on stderr unless an error occurs.

Requires Python 3.7+. No third-party dependencies.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# --- Patterns ---------------------------------------------------------------

# (pattern_id, label, compiled_regex)
PATTERNS = [
    (
        1,
        "significance-inflation",
        re.compile(
            r"\b("
            r"pivotal\s+(?:moment|role)"
            r"|testament\s+to"
            r"|evolving\s+landscape"
            r"|(?:in\s+)?today['’]s\s+(?:fast[- ]paced\s+)?world"
            r"|game[- ]chang(?:er|ing)"
            r"|paradigm\s+shift"
            r")\b",
            re.IGNORECASE,
        ),
    ),
    (
        4,
        "promotional",
        re.compile(
            r"\b(nestled|breathtaking|stunning|vibrant|bustling|captivating|picturesque)\b",
            re.IGNORECASE,
        ),
    ),
    (
        7,
        "ai-vocabulary",
        re.compile(
            r"\b("
            r"delve|delves|delving"
            r"|tapestry"
            r"|intricate"
            r"|pivotal"
            r"|testament"
            r"|underscore[ds]?|underscoring"
            r"|crucial"
            r"|garner(?:ed|s)?"
            r"|showcas(?:e[ds]?|ing)"
            r"|interplay"
            r"|meticulous(?:ly)?"
            r"|moreover"
            r"|furthermore"
            r"|indeed"
            r"|additionally"
            r"|notably"
            r"|navigate\s+the\s+complexit(?:y|ies)"
            r")\b",
            re.IGNORECASE,
        ),
    ),
    (
        8,
        "copula-avoidance",
        re.compile(
            r"\b(serves?\s+as|stands?\s+as|boasts?|features?\s+(?:a|an|the))\b",
            re.IGNORECASE,
        ),
    ),
    (
        9,
        "negative-parallelism",
        re.compile(
            r"(?:it’s|it's|it\s+is)\s+not\s+(?:just|only|merely)\s+"
            r"|not\s+only\s+[^.]{1,80}\s+but\s+also\b",
            re.IGNORECASE,
        ),
    ),
    (
        23,
        "filler",
        re.compile(
            r"\b("
            r"in\s+order\s+to"
            r"|it\s+is\s+important\s+to\s+note\s+that"
            r"|at\s+(?:this|the)\s+point\s+in\s+time"
            r"|please\s+(?:note|make\s+sure)"
            r"|needless\s+to\s+say"
            r"|that\s+being\s+said"
            r")\b",
            re.IGNORECASE,
        ),
    ),
    (
        28,
        "signposting",
        re.compile(
            r"("
            r"let’s\s+dive\s+(?:in|into)|let's\s+dive\s+(?:in|into)"
            r"|without\s+further\s+ado"
            r"|here’s\s+what\s+you\s+need\s+to\s+know|here's\s+what\s+you\s+need\s+to\s+know"
            r"|in\s+conclusion"
            r"|hope\s+this\s+helps"
            r")",
            re.IGNORECASE,
        ),
    ),
]

# Em-dash density check — flagged once per dense chunk, not per dash
EM_DASH_RE = re.compile(r"—")  # U+2014


# --- Masking ----------------------------------------------------------------

def mask_protected_regions(text):
    """Replace fenced code, backtick spans, URLs, anchors, and YAML frontmatter
    with spaces of equal length so pattern scans skip them but line numbers
    stay intact."""

    def _blank(m):
        # Preserve newlines so multi-line fences don't shift line numbers.
        return "".join("\n" if c == "\n" else " " for c in m.group(0))

    # YAML frontmatter at file head
    text = re.sub(r"\A---\n.*?\n---\n", _blank, text, count=1, flags=re.DOTALL)
    # Fenced code blocks (```...``` or ~~~...~~~)
    text = re.sub(r"```.*?```", _blank, text, flags=re.DOTALL)
    text = re.sub(r"~~~.*?~~~", _blank, text, flags=re.DOTALL)
    # Inline backticks
    text = re.sub(r"`[^`\n]+`", _blank, text)
    # URLs in () and bare
    text = re.sub(r"\]\([^)]*\)", _blank, text)
    text = re.sub(r"https?://\S+", _blank, text)
    return text


# --- Main -------------------------------------------------------------------

def scan(text):
    masked = mask_protected_regions(text)
    lines = masked.splitlines()
    hits = []

    for lineno, line in enumerate(lines, start=1):
        for pattern_id, label, regex in PATTERNS:
            for m in regex.finditer(line):
                hits.append(
                    {
                        "pattern": pattern_id,
                        "label": label,
                        "line": lineno,
                        "snippet": line[max(0, m.start() - 20) : m.end() + 20].strip(),
                    }
                )

    # Em-dash density — flag any 100-word span with ≥ 4 em-dashes.
    # Cheap heuristic: count per line, flag lines with ≥ 3 em-dashes.
    for lineno, line in enumerate(lines, start=1):
        count = len(EM_DASH_RE.findall(line))
        if count >= 3:
            hits.append(
                {
                    "pattern": 14,
                    "label": "em-dash-density",
                    "line": lineno,
                    "snippet": f"{count} em-dashes in this line",
                }
            )

    return hits


def main():
    if len(sys.argv) < 2:
        print("usage: prescan.py <file> | prescan.py -", file=sys.stderr)
        return 1

    arg = sys.argv[1]
    if arg == "-":
        text = sys.stdin.read()
    else:
        path = Path(arg)
        if not path.is_file():
            print(f"error: file not found: {arg}", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8")

    hits = scan(text)
    print(json.dumps(hits, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
