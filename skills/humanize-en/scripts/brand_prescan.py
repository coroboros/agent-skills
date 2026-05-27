#!/usr/bin/env python3
"""
brand_prescan.py — deterministic pre-scan for brand-voice rules.

Loads a BRAND-VOICE.md frontmatter and emits hits for the mechanically
detectable brand-specific patterns. Complements prescan.py's 8 universal
patterns; together they form the deterministic floor before LLM detection.

Brand patterns covered:
  - all_caps_emphasis      — \\b[A-Z]{3,}\\b minus acronym whitelist
  - forbidden_lexicon[*]   — literal phrase, case-insensitive substring
  - rewrite_rules[*].reject — literal phrase, exact substring
  - first-person singular   — bare I/I'm/my/me outside quotations
  - first-person plural     — sentence-initial We
  - second-person 'you'     — you/your/you're/you've minus compound idioms
  - signposting             — Let's dive in / Without further ado / etc.
  - negative_parallelism    — "is not X; it is Y" / "not just X but Y"
  - rule_of_three (heading) — H1-H6 with three comma-separated items
  - rhetorical_questions    — non-quoted lines ending with '?'
  - emoji                   — Unicode emoji ranges

Outputs hits per references/schemas.md § brand prescan hit list. Hits carry
a `source: "brand"` discriminator and a `rule_id` so the SKILL.md coverage
report can attribute each rewrite to the originating rule.

Forward-compatible with `voice.lexical_exceptions.acronyms` and
`voice.lexical_exceptions.compound_idioms` from BRAND-VOICE.md when present;
falls back to the hardcoded defaults below otherwise.

Requires Python 3.7+. No third-party dependencies.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
# Import from prescan (unique to humanize-en) instead of utils — both skills
# ship a `utils.py` and Python caches the first one loaded, which would break
# cross-skill test runs.
from prescan import mask_protected_regions  # noqa: E402

# --- Hardcoded whitelist defaults -------------------------------------------

# Common technical acronyms ≥ 3 chars that legitimately appear in body prose.
# Voice docs may extend via `lexical_exceptions.acronyms`.
DEFAULT_ACRONYM_WHITELIST = frozenset({
    "API", "APIs", "BPM", "CDN", "CLI", "CNN", "CPU", "CSS", "CTA",
    "DAW", "DNA", "DNS", "EDM", "EU", "FAQ", "GPT", "GPU", "GUI",
    "HTML", "HTTP", "HTTPS", "IDE", "IFPI", "ID", "IO", "IP", "JS",
    "JSON", "LICENSE", "LLM", "LUFS", "MIDI", "MIT", "ML", "NLP",
    "NPM", "OK", "ORM", "OS", "PR", "RAM", "README", "RFC", "RNN",
    "SDK", "SQL", "SaaS", "TCP", "TODO", "TS", "UDP", "UK", "URL",
    "US", "USA", "YAML",
})

# Hyphenated idioms that legitimately contain pronouns ('your', 'you', 'yourself')
# but are not reader-direct address.
DEFAULT_COMPOUND_IDIOM_WHITELIST = frozenset({
    "all-in-one", "do-it-yourself", "end-to-end", "in-your-face",
    "off-the-shelf", "on-the-fly", "over-the-counter", "peer-to-peer",
    "side-by-side", "state-of-the-art",
})

# --- Minimal YAML parser ----------------------------------------------------
# Parity counterpart of brand-voice's parse_yaml_minimal — kept here so
# humanize-en remains self-sufficient when brand-voice is not installed
# (the `-f` fallback path in SKILL.md). See
# https://github.com/coroboros/agent-skills/blob/main/skills/brand-voice/scripts/utils.py
# for the mirrored implementation. Only the BRAND-VOICE.md frontmatter
# shape is supported: nested dicts (2-space indent), scalar lists, strings,
# booleans, integers. No anchors, no multi-line strings, no flow sequences
# across lines.


def parse_yaml_minimal(yaml_text):
    """Parse the BRAND-VOICE.md frontmatter subset of YAML. Returns a dict.

    Parity counterpart of `parse_yaml_minimal` in the brand-voice skill
    (https://github.com/coroboros/agent-skills/blob/main/skills/brand-voice/scripts/utils.py)
    — when one changes the other must too. ValueError raised on parse error
    carries a `.line` attribute (1-indexed) for callers that surface the
    offending line.
    """
    lines = yaml_text.splitlines()
    pos = [0]

    def err(msg, lineno):
        e = ValueError(f"yaml: {msg} (line {lineno + 1})")
        e.line = lineno + 1
        return e

    def _strip_comment(line):
        """Strip a `#` inline comment, respecting quoted strings and requiring
        the `#` to be at line start or preceded by whitespace. Otherwise a URL
        fragment, color hex, or anchor inside a value is silently truncated."""
        quote = None
        for idx, ch in enumerate(line):
            if quote:
                if ch == quote:
                    quote = None
                continue
            if ch in ('"', "'"):
                quote = ch
                continue
            if ch == "#" and (idx == 0 or line[idx - 1] in (" ", "\t")):
                return line[:idx]
        return line

    def peek():
        while pos[0] < len(lines):
            line = lines[pos[0]]
            stripped = _strip_comment(line).rstrip()
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
            return (inner.replace('\\"', '"').replace("\\\\", "\\")
                         .replace("\\n", "\n").replace("\\t", "\t"))
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

    def _kv_split(s):
        n = len(s)
        quote = None
        for i, ch in enumerate(s):
            if quote:
                if ch == quote:
                    quote = None
                continue
            if ch in ('"', "'"):
                quote = ch
                continue
            if ch == ":" and (i + 1 == n or s[i + 1] in (" ", "\t")):
                return s[:i].strip(), s[i + 1:].strip()
        return None, None

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
            k, v = (None, None)
            if not (content.startswith('"') or content.startswith("'")
                    or content.startswith("[") or content.startswith("{")):
                k, v = _kv_split(content)
            if k is not None:
                obj = {}
                if v:
                    obj[k] = parse_scalar(v, lineno)
                else:
                    obj[k] = parse_block(indent + 2)
                while True:
                    nxt_line, nxt_lineno = peek()
                    if nxt_line is None:
                        break
                    nxt_indent = indent_of(lines[nxt_lineno])
                    if nxt_indent <= indent:
                        break
                    if nxt_line.lstrip().startswith("- "):
                        break
                    nk, nv = _kv_split(nxt_line.lstrip())
                    if nk is None:
                        raise err(f"unexpected line in list-of-objects: '{nxt_line}'", nxt_lineno)
                    pos[0] += 1
                    if nv:
                        obj[nk] = parse_scalar(nv, nxt_lineno)
                    else:
                        obj[nk] = parse_block(nxt_indent + 2)
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
            key, value = _kv_split(stripped)
            if key is None:
                raise err(f"expected 'key:' got '{stripped}'", lineno)
            pos[0] += 1
            if value:
                result[key] = parse_scalar(value, lineno)
            else:
                child = parse_block(indent + 2)
                result[key] = child if child is not None else {}
        return result

    return parse_block(0) or {}


def _split_flow(s):
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


# --- Brand rule loading -----------------------------------------------------


def load_brand_rules(path):
    """Read a BRAND-VOICE.md file and return its frontmatter dict.

    Raises FileNotFoundError if the path does not resolve, ValueError on
    YAML parse errors. Returns an empty dict if no frontmatter is present
    (caller decides whether to escalate)."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"brand-voice doc not found: {path}")
    text = p.read_text(encoding="utf-8")
    # Strip UTF-8 BOM if present so '---' on line 1 still detects.
    if text.startswith("﻿"):
        text = text[1:]
    if not text.startswith("---\n"):
        return {}
    lines = text.splitlines(keepends=True)
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].rstrip("\n") == "---":
            end_idx = i
            break
    if end_idx is None:
        return {}
    frontmatter = "".join(lines[1:end_idx])
    return parse_yaml_minimal(frontmatter)


def merge_lexical_exceptions(rules):
    """Combine hardcoded whitelists with any voice.lexical_exceptions overrides.

    Returns (acronyms, compound_idioms) as frozensets ready for membership tests."""
    acronyms = set(DEFAULT_ACRONYM_WHITELIST)
    idioms = set(DEFAULT_COMPOUND_IDIOM_WHITELIST)

    lex = rules.get("lexical_exceptions") if isinstance(rules.get("lexical_exceptions"), dict) else {}
    extra_acronyms = lex.get("acronyms") if isinstance(lex.get("acronyms"), list) else []
    extra_idioms = lex.get("compound_idioms") if isinstance(lex.get("compound_idioms"), list) else []

    for a in extra_acronyms:
        if isinstance(a, str) and a:
            acronyms.add(a)
    for i in extra_idioms:
        if isinstance(i, str) and i:
            idioms.add(i.lower())

    return frozenset(acronyms), frozenset(idioms)


# --- Brand pattern detectors ------------------------------------------------

_ALL_CAPS_RE = re.compile(r"\b[A-Z]{3,}\b")
# Boundaries include curly apostrophe (U+2019) so contracted forms `I’m`/`I’ve`
# are not split by the lookbehind. Alternation is longest-first per form so
# the engine prefers `I’m` over bare `I`. Both straight and curly variants
# are listed because the apostrophe is character-distinct under regex.
_FIRST_PERSON_SINGULAR_RE = re.compile(
    r"(?<![\w'’])"
    r"(I'll|I’ll|I've|I’ve|I'd|I’d|I'm|I’m|I"
    r"|Myself|myself|My|my|Me|me)"
    r"(?![\w'’])"
)
_FIRST_PERSON_PLURAL_RE = re.compile(
    r"(?:^|(?<=[.!?]\s)|(?<=\n))"
    r"(We're|We’re|We've|We’ve|We'll|We’ll|We'd|We’d|We"
    r"|we're|we’re|we've|we’ve|we'll|we’ll|we'd|we’d|we)"
    r"(?![\w'’])"
)
_SECOND_PERSON_RE = re.compile(r"\b(you|your|you're|you’re|you've|you’ve|yours|yourself)\b", re.IGNORECASE)
_NEGATIVE_PARALLELISM_PATTERNS = [
    # `is/are/was/were not X[;,] it is/it's/they are/they're Y` — incl. contractions.
    re.compile(
        r"(?:\b(?:is|are|was|were)|['’](?:s|re))\s+not\b"
        r"[^.;\n]{0,80}"
        r"[;,]\s*(?:it\s+is|it['’]s|they\s+are|they['’]re)\b",
        re.IGNORECASE,
    ),
    # `not just X but Y`
    re.compile(r"\bnot\s+just\b[^.\n]{0,80}\bbut\b", re.IGNORECASE),
    # `not only X but [also] Y` — `also` optional to catch the common variant.
    re.compile(r"\bnot\s+only\b[^.\n]{0,80}\bbut\b(?:\s+also)?", re.IGNORECASE),
]
# Strict three-item heading: every item must be comma-free so 4+ comma headings
# do not over-flag (e.g. `## A, B, C, D` is rejected — only exactly 3 items match).
_RULE_OF_THREE_HEADING_RE = re.compile(r"^#{1,6}\s+[^\n,]+,\s+[^\n,]+,\s+[^\n,]+\s*$", re.MULTILINE)
# Match a base emoji codepoint plus an optional variation selector (U+FE0F)
# and an optional zero-width joiner sequence. Without consuming U+FE0F, the
# match for `❤️` would stop at U+2764 and produce a snippet that visually
# loses the variation selector. Regional indicators (U+1F1E6-U+1F1FF) are a
# pair-of-codepoints sequence — flag emojis like 🇺🇸 — included here.
_EMOJI_RE = re.compile(
    "(?:"
    "[\U0001F1E6-\U0001F1FF]{2}"           # regional indicator pair (flag)
    "|[\U0001F300-\U0001F5FF]"             # symbols & pictographs
    "|[\U0001F600-\U0001F64F]"             # emoticons
    "|[\U0001F680-\U0001F6FF]"             # transport & map symbols
    "|[\U0001F700-\U0001F77F]"             # alchemical
    "|[\U0001F780-\U0001F7FF]"             # geometric ext
    "|[\U0001F800-\U0001F8FF]"             # supplemental arrows
    "|[\U0001F900-\U0001F9FF]"             # supplemental symbols & pictographs
    "|[\U0001FA00-\U0001FAFF]"             # symbols & pictographs ext-A
    "|[\U00002600-\U000026FF]"             # misc symbols
    "|[\U00002700-\U000027BF]"             # dingbats
    "|[\U00002B00-\U00002BFF]"             # misc symbols & arrows
    ")"
    "️?"                              # optional variation selector
)
_SIGNPOSTING_PHRASES = [
    "let's dive", "let’s dive", "let us dive",
    "without further ado",
    "here's what you need to know", "here’s what you need to know",
    "in conclusion", "to begin with", "that being said",
    "hope this helps",
]


def _snippet(line, start, end, ctx=20):
    return line[max(0, start - ctx): end + ctx].strip()


def detect_all_caps_emphasis(masked_text, acronym_whitelist, source="brand"):
    """Flag uppercase tokens ≥ 3 chars not in the acronym whitelist."""
    hits = []
    for lineno, line in enumerate(masked_text.splitlines(), start=1):
        for m in _ALL_CAPS_RE.finditer(line):
            tok = m.group(0)
            if tok in acronym_whitelist:
                continue
            hits.append({
                "pattern": "brand:all_caps_emphasis",
                "label": "brand-all-caps-emphasis",
                "line": lineno,
                "snippet": _snippet(line, m.start(), m.end()),
                "source": source,
                "rule_id": "all_caps_emphasis",
            })
    return hits


def detect_forbidden_lexicon(masked_text, terms, source="brand"):
    """Flag every literal occurrence of each forbidden term, case-insensitive."""
    hits = []
    if not terms:
        return hits
    lines = masked_text.splitlines()
    for term in terms:
        if not isinstance(term, str) or not term:
            continue
        # Use word-boundary on alphanumeric edges; non-word chars (hyphens) are
        # treated as part of the term by anchoring to whitespace/punctuation.
        escaped = re.escape(term)
        regex = re.compile(rf"(?i)(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])")
        for lineno, line in enumerate(lines, start=1):
            for m in regex.finditer(line):
                hits.append({
                    "pattern": "brand:forbidden_lexicon",
                    "label": "brand-forbidden-lexicon",
                    "line": lineno,
                    "snippet": _snippet(line, m.start(), m.end()),
                    "source": source,
                    "rule_id": f"forbidden_lexicon:{term}",
                })
    return hits


def detect_rewrite_rule_rejects(masked_text, rules, source="brand"):
    """Flag every literal occurrence of each rewrite_rules[*].reject string."""
    hits = []
    if not rules:
        return hits
    lines = masked_text.splitlines()
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        reject = rule.get("reject")
        rule_id = rule.get("rule_id")
        if not isinstance(reject, str) or not reject or not isinstance(rule_id, str):
            continue
        escaped = re.escape(reject)
        regex = re.compile(escaped, re.IGNORECASE)
        for lineno, line in enumerate(lines, start=1):
            for m in regex.finditer(line):
                hits.append({
                    "pattern": "brand:rewrite_rule",
                    "label": "brand-rewrite-rule",
                    "line": lineno,
                    "snippet": _snippet(line, m.start(), m.end()),
                    "source": source,
                    "rule_id": f"rewrite_rule:{rule_id}",
                })
    return hits


def detect_first_person_singular(masked_text, source="brand"):
    hits = []
    for lineno, line in enumerate(masked_text.splitlines(), start=1):
        for m in _FIRST_PERSON_SINGULAR_RE.finditer(line):
            hits.append({
                "pattern": "brand:first_person_singular",
                "label": "brand-pronoun-1sg",
                "line": lineno,
                "snippet": _snippet(line, m.start(), m.end()),
                "source": source,
                "rule_id": "pronouns:first-person singular",
            })
    return hits


def detect_first_person_plural(masked_text, source="brand"):
    hits = []
    for lineno, line in enumerate(masked_text.splitlines(), start=1):
        for m in _FIRST_PERSON_PLURAL_RE.finditer(line):
            hits.append({
                "pattern": "brand:first_person_plural",
                "label": "brand-pronoun-1pl",
                "line": lineno,
                "snippet": _snippet(line, m.start(), m.end()),
                "source": source,
                "rule_id": "pronouns:first-person plural in marketing",
            })
    return hits


def detect_second_person(masked_text, idiom_whitelist, source="brand"):
    """Flag 'you/your/...' tokens not inside a whitelisted compound idiom."""
    hits = []
    for lineno, line in enumerate(masked_text.splitlines(), start=1):
        idiom_spans = []
        lower = line.lower()
        for idiom in idiom_whitelist:
            start = 0
            while True:
                idx = lower.find(idiom, start)
                if idx < 0:
                    break
                idiom_spans.append((idx, idx + len(idiom)))
                start = idx + 1
        for m in _SECOND_PERSON_RE.finditer(line):
            if any(s <= m.start() < e for s, e in idiom_spans):
                continue
            hits.append({
                "pattern": "brand:second_person",
                "label": "brand-pronoun-2",
                "line": lineno,
                "snippet": _snippet(line, m.start(), m.end()),
                "source": source,
                "rule_id": "pronouns:second-person 'you' in marketing",
            })
    return hits


def detect_signposting(masked_text, source="brand"):
    hits = []
    lines = masked_text.splitlines()
    for lineno, line in enumerate(lines, start=1):
        lower = line.lower()
        for phrase in _SIGNPOSTING_PHRASES:
            idx = lower.find(phrase)
            if idx >= 0:
                hits.append({
                    "pattern": "brand:signposting",
                    "label": "brand-signposting",
                    "line": lineno,
                    "snippet": _snippet(line, idx, idx + len(phrase)),
                    "source": source,
                    "rule_id": "signposting",
                })
    return hits


def detect_negative_parallelism(masked_text, source="brand"):
    hits = []
    for lineno, line in enumerate(masked_text.splitlines(), start=1):
        for regex in _NEGATIVE_PARALLELISM_PATTERNS:
            for m in regex.finditer(line):
                hits.append({
                    "pattern": "brand:negative_parallelism",
                    "label": "brand-negative-parallelism",
                    "line": lineno,
                    "snippet": _snippet(line, m.start(), m.end()),
                    "source": source,
                    "rule_id": "negative_parallelism",
                })
    return hits


def detect_rule_of_three_heading(masked_text, source="brand"):
    hits = []
    for m in _RULE_OF_THREE_HEADING_RE.finditer(masked_text):
        line_start = masked_text.rfind("\n", 0, m.start()) + 1
        line_end = masked_text.find("\n", line_start)
        if line_end < 0:
            line_end = len(masked_text)
        lineno = masked_text.count("\n", 0, line_start) + 1
        line = masked_text[line_start:line_end]
        hits.append({
            "pattern": "brand:rule_of_three_heading",
            "label": "brand-rule-of-three-heading",
            "line": lineno,
            "snippet": line.strip()[:80],
            "source": source,
            "rule_id": "rule_of_three",
        })
    return hits


def detect_rhetorical_questions(masked_text, source="brand"):
    hits = []
    for lineno, line in enumerate(masked_text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith(">"):
            continue
        if stripped.endswith("?"):
            hits.append({
                "pattern": "brand:rhetorical_questions",
                "label": "brand-rhetorical-question",
                "line": lineno,
                "snippet": stripped[:80],
                "source": source,
                "rule_id": "rhetorical_questions",
            })
    return hits


def detect_emoji(masked_text, source="brand"):
    hits = []
    for lineno, line in enumerate(masked_text.splitlines(), start=1):
        for m in _EMOJI_RE.finditer(line):
            hits.append({
                "pattern": "brand:emoji",
                "label": "brand-emoji",
                "line": lineno,
                "snippet": _snippet(line, m.start(), m.end()),
                "source": source,
                "rule_id": "emoji",
            })
    return hits


# --- Top-level scan ---------------------------------------------------------


def scan_brand(text, rules, strict_code_only=False):
    """Run all brand detectors against `text` driven by `rules` (the BRAND-VOICE
    frontmatter dict). Returns a flat list of hits in the prescan-hit shape with
    `source: "brand"` and a `rule_id` per the originating YAML rule."""
    if not isinstance(rules, dict):
        return []

    masked = mask_protected_regions(text, strict_code_only=strict_code_only)
    acronyms, idioms = merge_lexical_exceptions(rules)

    hits = []

    forbidden_patterns = rules.get("forbidden_patterns") or []
    forbidden_set = {p for p in forbidden_patterns if isinstance(p, str)}

    if "all_caps_emphasis" in forbidden_set:
        hits.extend(detect_all_caps_emphasis(masked, acronyms))

    forbidden_lex = rules.get("forbidden_lexicon") or []
    hits.extend(detect_forbidden_lexicon(masked, forbidden_lex))

    rewrite_rules = rules.get("rewrite_rules") or []
    hits.extend(detect_rewrite_rule_rejects(masked, rewrite_rules))

    pronouns = rules.get("pronouns") if isinstance(rules.get("pronouns"), dict) else {}
    forbid_pron = pronouns.get("forbid") or []
    # Lowercase membership: voice docs may write "First-person singular" or
    # "first-person singular" interchangeably — both must enable the detector.
    forbid_pron_set = {p.lower() for p in forbid_pron if isinstance(p, str)}
    if any("first-person singular" in p for p in forbid_pron_set):
        hits.extend(detect_first_person_singular(masked))
    if any("first-person plural" in p for p in forbid_pron_set):
        hits.extend(detect_first_person_plural(masked))
    if any("second-person" in p for p in forbid_pron_set):
        hits.extend(detect_second_person(masked, idioms))

    if "signposting" in forbidden_set:
        hits.extend(detect_signposting(masked))
    if "negative_parallelism" in forbidden_set:
        hits.extend(detect_negative_parallelism(masked))
    if "rule_of_three" in forbidden_set:
        hits.extend(detect_rule_of_three_heading(masked))
    if "rhetorical_questions" in forbidden_set:
        hits.extend(detect_rhetorical_questions(masked))
    if "emoji" in forbidden_set:
        hits.extend(detect_emoji(masked))

    return hits
