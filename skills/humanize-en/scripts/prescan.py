#!/usr/bin/env python3
"""
prescan.py — deterministic pre-scan for the 8 highest-signal universal AI
tells, plus optional brand-aware detection driven by a BRAND-VOICE.md.

Usage:
    prescan.py <file>
    cat file.md | prescan.py -
    prescan.py --brand path/to/BRAND-VOICE.md <file>
    prescan.py --strict-code-only <file>

Universal patterns (numbered per references/patterns.md):
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

Brand patterns (when --brand is set, see brand_prescan.py for the full list):
  all_caps_emphasis, forbidden_lexicon[*], rewrite_rules[*].reject,
  first/second-person pronouns, signposting, negative_parallelism,
  rule_of_three_heading, rhetorical_questions, emoji.

Flags:
  --brand <path>          Load YAML rules from a BRAND-VOICE.md and scan for
                          brand-specific patterns alongside the universal 8.
  --strict-code-only      Treat every fenced block as code (legacy behaviour).
                          Default: fences with no info-string or `text` are
                          pseudo-blocks and their bodies are scanned.

Output (stdout):
  JSON array of hits per references/schemas.md § prescan hit list. Hits
  carry a `source` field ("universal" or "brand") and brand hits add a
  `rule_id` per the originating YAML rule.

Exit:
  0   scan complete (hits or not)
  1   argument or I/O error

Emits nothing on stderr unless an error occurs.

Requires Python 3.7+. No third-party dependencies.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

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


# Info-strings that mark a fenced block as a *pseudo-block* — its content is
# prose-shaped (label-prefixed lines, ASCII tables, terminal transcripts) and
# must still be scanned for AI tells. Anything else is real code: blanked.
PSEUDO_BLOCK_INFO_STRINGS = frozenset({"", "text"})

# Fenced-block regex with a named info-string capture. `info` is the part
# between the opening fence marker and the trailing newline ('text', 'python',
# or empty). The body is non-greedy up to the closing fence on its own line.
_BACKTICK_FENCE_RE = re.compile(
    r"```(?P<info>[^\n`]*)\n.*?```",
    re.DOTALL,
)
_TILDE_FENCE_RE = re.compile(
    r"~~~(?P<info>[^\n~]*)\n.*?~~~",
    re.DOTALL,
)


def mask_protected_regions(text, strict_code_only=False):
    """Replace protected regions with whitespace so pattern scans skip them
    but line numbers stay intact.

    - Fenced blocks with a non-empty, non-`text` info-string are treated as
      real code and fully blanked.
    - Fenced blocks with no info-string or `text` are pseudo-blocks: only the
      opening and closing fence markers are blanked; the body remains scannable
      prose.
    - `strict_code_only=True` reverts to the legacy behaviour: every fenced
      block is blanked regardless of its info-string. Use when the user
      explicitly wants verbatim preservation of every fenced region.

    Always blanked: YAML frontmatter, inline backticks, URLs, markdown link
    targets — these never carry prose meant for AI-tell detection."""

    def _blank(m):
        # Preserve newlines so multi-line regions don't shift line numbers.
        return "".join("\n" if c == "\n" else " " for c in m.group(0))

    def _blank_fence(m):
        info = (m.group("info") or "").strip().lower()
        if strict_code_only or info not in PSEUDO_BLOCK_INFO_STRINGS:
            return _blank(m)
        full = m.group(0)
        first_nl = full.index("\n")
        opener = full[:first_nl]
        body = full[first_nl:-3]
        closer = full[-3:]
        return (" " * len(opener)) + body + (" " * len(closer))

    text = re.sub(r"\A---\n.*?\n---\n", _blank, text, count=1, flags=re.DOTALL)
    text = _BACKTICK_FENCE_RE.sub(_blank_fence, text)
    text = _TILDE_FENCE_RE.sub(_blank_fence, text)
    text = re.sub(r"`[^`\n]+`", _blank, text)
    text = re.sub(r"\]\([^)]*\)", _blank, text)
    text = re.sub(r"https?://\S+", _blank, text)
    return text


def scan(text, strict_code_only=False, attach_source=False):
    """Run the universal prescan. When `attach_source=True`, every hit gains a
    `source: "universal"` discriminator (used when merging with brand hits)."""
    masked = mask_protected_regions(text, strict_code_only=strict_code_only)
    lines = masked.splitlines()
    hits = []

    for lineno, line in enumerate(lines, start=1):
        for pattern_id, label, regex in PATTERNS:
            for m in regex.finditer(line):
                hit = {
                    "pattern": pattern_id,
                    "label": label,
                    "line": lineno,
                    "snippet": line[max(0, m.start() - 20): m.end() + 20].strip(),
                }
                if attach_source:
                    hit["source"] = "universal"
                hits.append(hit)

    # Em-dash density — flag any 100-word span with ≥ 4 em-dashes.
    # Cheap heuristic: count per line, flag lines with ≥ 3 em-dashes.
    for lineno, line in enumerate(lines, start=1):
        count = len(EM_DASH_RE.findall(line))
        if count >= 3:
            hit = {
                "pattern": 14,
                "label": "em-dash-density",
                "line": lineno,
                "snippet": f"{count} em-dashes in this line",
            }
            if attach_source:
                hit["source"] = "universal"
            hits.append(hit)

    return hits


class _PrescanArgParser(argparse.ArgumentParser):
    """Override argparse's default exit code 2 for usage errors. The skill's
    schema (references/schemas.md) pins exit code 1 for any argument or I/O
    failure — keeping the contract stable across releases."""

    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"usage: prescan.py <file> | prescan.py - [--brand <doc>] [--strict-code-only]",
              file=sys.stderr)
        sys.exit(1)


def main():
    parser = _PrescanArgParser(
        description=(__doc__ or "").split("\n\n")[0],
        prog="prescan.py",
        add_help=True,
    )
    parser.add_argument("path", help="path to a prose file (or '-' for stdin)")
    parser.add_argument(
        "--brand",
        metavar="<voice-doc>",
        help="path to a BRAND-VOICE.md; activates brand-aware detection",
    )
    parser.add_argument(
        "--strict-code-only",
        action="store_true",
        help="blank every fenced block (legacy behaviour, disables pseudo-blocks)",
    )
    args = parser.parse_args()

    if args.path == "-":
        text = sys.stdin.read()
    else:
        path = Path(args.path)
        if not path.is_file():
            print(f"error: file not found: {args.path}", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8")

    has_brand = bool(args.brand)
    hits = scan(text, strict_code_only=args.strict_code_only, attach_source=has_brand)

    if has_brand:
        try:
            from brand_prescan import load_brand_rules, scan_brand
            rules = load_brand_rules(args.brand)
        except FileNotFoundError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        except ValueError as exc:
            print(f"error: brand-voice YAML invalid: {exc}", file=sys.stderr)
            return 1
        hits.extend(scan_brand(text, rules, strict_code_only=args.strict_code_only))

    print(json.dumps(hits, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
