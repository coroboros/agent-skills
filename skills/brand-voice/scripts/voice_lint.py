#!/usr/bin/env python3
"""
voice_lint.py — validate a BRAND-VOICE.md against canonical-format.md.

Usage:
    voice_lint.py <BRAND-VOICE.md>
    cat BRAND-VOICE.md | voice_lint.py -

Output (stdout, JSON per references/schemas.md § voice_lint.py).

Exit:
    0  GREEN or YELLOW (errors == 0)
    1  RED (errors >= 1)
    2  file not found, unreadable, or not UTF-8

Requires Python 3.7+. No third-party dependencies.
"""

from __future__ import annotations

import datetime
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import (  # noqa: E402
    list_h2_sections,
    normalise_section_heading,
    parse_yaml_minimal,
    read_text,
    split_frontmatter,
    write_json,
)


REQUIRED_SECTIONS = [
    "core voice attributes",
    "rewrite rules — do/don't",
    "forbidden lexicon and patterns",
    "sentence-level norms",
]

RECOMMENDED_SECTIONS = [
    "tone by context",
    "pronouns and self-reference",
    "format conventions",
    "visual pairing",
    "quick diagnostic",
    "counter-examples",
    "reference texts",
]

ALL_CANONICAL_SECTIONS = REQUIRED_SECTIONS + RECOMMENDED_SECTIONS

REQUIRED_FIELDS = [
    ("voice.name", lambda d: bool((d.get("voice") or {}).get("name"))),
    ("forbidden_lexicon", lambda d: isinstance(d.get("forbidden_lexicon"), list)),
    ("rewrite_rules", lambda d: isinstance(d.get("rewrite_rules"), list)),
    ("sentence_norms", lambda d: isinstance(d.get("sentence_norms"), dict)),
]

VALID_EM_DASH_SPACING = {"spaced", "tight", "forbid"}
VALID_EXCLAMATION = {"allow", "forbid"}
VALID_CONTRACTIONS = {"allow", "forbid"}
RULE_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def lint(text, path):
    errors = []
    warnings = []

    fm_lines = text.split("\n", 1)[0:1]
    fm, body = split_frontmatter(text)
    if fm is None:
        errors.append({
            "code": "frontmatter-invalid-yaml",
            "field": None,
            "message": "no YAML frontmatter found (file must start with '---' on line 1)",
            "line": 1,
        })
        return _verdict(path, errors, warnings, text, body=text, fm=None)

    try:
        data = parse_yaml_minimal(fm)
    except ValueError as exc:
        errors.append({
            "code": "frontmatter-invalid-yaml",
            "field": None,
            "message": str(exc),
            "line": getattr(exc, "line", 2),
        })
        return _verdict(path, errors, warnings, text, body=body, fm=None)

    if not isinstance(data, dict):
        errors.append({
            "code": "frontmatter-invalid-yaml",
            "field": None,
            "message": "frontmatter root must be a mapping",
            "line": 2,
        })
        return _verdict(path, errors, warnings, text, body=body, fm=None)

    for field, check in REQUIRED_FIELDS:
        if not check(data):
            errors.append({
                "code": "missing-required-field",
                "field": field,
                "message": f"required frontmatter field '{field}' is missing or wrong type",
                "line": 2,
            })

    norms = data.get("sentence_norms") or {}
    if isinstance(norms, dict):
        wmin = norms.get("word_count_min")
        wmax = norms.get("word_count_max")
        whard = norms.get("sentence_max_hard")
        if isinstance(wmin, int) and isinstance(wmax, int) and wmin > wmax:
            errors.append({
                "code": "invalid-field-value",
                "field": "sentence_norms.word_count_min",
                "message": f"word_count_min ({wmin}) must be <= word_count_max ({wmax})",
                "line": 2,
            })
        if isinstance(wmax, int) and isinstance(whard, int) and wmax > whard:
            errors.append({
                "code": "invalid-field-value",
                "field": "sentence_norms.word_count_max",
                "message": f"word_count_max ({wmax}) must be <= sentence_max_hard ({whard})",
                "line": 2,
            })
        em = norms.get("em_dash_spacing")
        if em is not None and em not in VALID_EM_DASH_SPACING:
            errors.append({
                "code": "invalid-field-value",
                "field": "sentence_norms.em_dash_spacing",
                "message": f"em_dash_spacing must be one of {sorted(VALID_EM_DASH_SPACING)}, got '{em}'",
                "line": 2,
            })
        exc = norms.get("exclamation_marks")
        if exc is not None and exc not in VALID_EXCLAMATION:
            errors.append({
                "code": "invalid-field-value",
                "field": "sentence_norms.exclamation_marks",
                "message": f"exclamation_marks must be one of {sorted(VALID_EXCLAMATION)}, got '{exc}'",
                "line": 2,
            })
        contr = norms.get("contractions")
        if contr is not None and contr not in VALID_CONTRACTIONS:
            errors.append({
                "code": "invalid-field-value",
                "field": "sentence_norms.contractions",
                "message": f"contractions must be one of {sorted(VALID_CONTRACTIONS)}, got '{contr}'",
                "line": 2,
            })

    rules = data.get("rewrite_rules") or []
    seen_ids = {}
    for i, rule in enumerate(rules):
        if not isinstance(rule, dict):
            errors.append({
                "code": "invalid-field-value",
                "field": f"rewrite_rules[{i}]",
                "message": "rewrite_rules entries must be mappings with reject/accept/rule_id",
                "line": 2,
            })
            continue
        rule_id = rule.get("rule_id")
        if not rule_id:
            errors.append({
                "code": "missing-required-field",
                "field": f"rewrite_rules[{i}].rule_id",
                "message": "every rewrite rule must have a rule_id",
                "line": 2,
            })
            continue
        if not RULE_ID_RE.match(str(rule_id)):
            errors.append({
                "code": "invalid-field-value",
                "field": f"rewrite_rules[{i}].rule_id",
                "message": f"rule_id must be kebab-case [a-z0-9-]+, got '{rule_id}'",
                "line": 2,
            })
        if rule_id in seen_ids:
            errors.append({
                "code": "duplicate-rule-id",
                "field": f"rewrite_rules[{i}].rule_id",
                "message": f"rule_id '{rule_id}' duplicates rewrite_rules[{seen_ids[rule_id]}]",
                "line": 2,
            })
        else:
            seen_ids[rule_id] = i

    sections = list_h2_sections(body or "")
    seen = {}
    seen_order = []
    for heading, lineno in sections:
        norm = normalise_section_heading(heading)
        if norm in seen:
            errors.append({
                "code": "duplicate-section",
                "field": f"section:{norm}",
                "message": f"H2 '{heading}' appears twice (also at line {seen[norm]})",
                "line": lineno,
            })
        else:
            seen[norm] = lineno
            seen_order.append(norm)

    for required in REQUIRED_SECTIONS:
        if required not in seen:
            errors.append({
                "code": "missing-section",
                "field": f"section:{required}",
                "message": f"required H2 section '{required}' is missing",
                "line": 0,
            })

    for recommended in RECOMMENDED_SECTIONS:
        if recommended not in seen:
            warnings.append({
                "code": "recommended-section-missing",
                "field": f"section:{recommended}",
                "message": f"recommended H2 section '{recommended}' is missing",
                "line": 0,
            })

    found_canonical = [s for s in seen_order if s in ALL_CANONICAL_SECTIONS]
    expected_canonical = [s for s in ALL_CANONICAL_SECTIONS if s in seen]
    if found_canonical != expected_canonical:
        errors.append({
            "code": "section-out-of-order",
            "field": "section:order",
            "message": f"canonical sections must appear in this order: {expected_canonical}; found: {found_canonical}",
            "line": 0,
        })

    forbidden_lex = data.get("forbidden_lexicon") or []
    if not forbidden_lex:
        warnings.append({
            "code": "empty-required-lexicon",
            "field": "forbidden_lexicon",
            "message": "forbidden_lexicon is empty; without it the voice has no banned terms",
            "line": 2,
        })

    voice = data.get("voice") or {}
    if not voice.get("source_urls"):
        warnings.append({
            "code": "no-source-urls",
            "field": "voice.source_urls",
            "message": "voice.source_urls is empty; doc is interview-only or hand-authored",
            "line": 2,
        })

    last_updated = voice.get("last_updated")
    if isinstance(last_updated, str):
        try:
            d = datetime.date.fromisoformat(last_updated)
            age = (datetime.date.today() - d).days
            if age > 180:
                warnings.append({
                    "code": "outdated-last-updated",
                    "field": "voice.last_updated",
                    "message": f"voice.last_updated is {age} days old; consider running update",
                    "line": 2,
                })
        except ValueError:
            errors.append({
                "code": "invalid-field-value",
                "field": "voice.last_updated",
                "message": f"voice.last_updated must be ISO date YYYY-MM-DD, got '{last_updated}'",
                "line": 2,
            })

    body_lines = (body or "").splitlines()
    section_starts = [(s, l) for s, l in sections if normalise_section_heading(s) in ALL_CANONICAL_SECTIONS]
    section_starts.sort(key=lambda t: t[1])
    for idx, (heading, lineno) in enumerate(section_starts):
        next_line = section_starts[idx + 1][1] if idx + 1 < len(section_starts) else len(body_lines) + 1
        section_text = "\n".join(body_lines[lineno : next_line - 1])
        prose = re.sub(r"```.*?```", "", section_text, flags=re.DOTALL)
        prose = re.sub(r"`[^`\n]+`", "", prose)
        if len(prose.strip()) < 50:
            warnings.append({
                "code": "section-light-content",
                "field": f"section:{normalise_section_heading(heading)}",
                "message": f"section '{heading}' has under 50 chars of prose",
                "line": lineno,
            })

    return _verdict(path, errors, warnings, text, body=body, fm=fm, data=data, sections=sections)


def _verdict(path, errors, warnings, text, body=None, fm=None, data=None, sections=None):
    if errors:
        verdict = "RED"
    elif warnings:
        verdict = "YELLOW"
    else:
        verdict = "GREEN"

    fm_lines = (fm or "").count("\n")
    body_lines = (body or "").count("\n")
    total_lines = text.count("\n") + (1 if not text.endswith("\n") else 0)

    rule_count = len(((data or {}).get("rewrite_rules")) or [])
    forbidden_count = len(((data or {}).get("forbidden_lexicon")) or [])
    section_count = len(sections or [])

    return {
        "path": path,
        "verdict": verdict,
        "errors": errors,
        "warnings": warnings,
        "stats": {
            "frontmatter_lines": fm_lines,
            "prose_lines": body_lines,
            "total_lines": total_lines,
            "rule_count": rule_count,
            "forbidden_lexicon_count": forbidden_count,
            "section_count": section_count,
        },
    }


def main():
    if len(sys.argv) < 2:
        print("usage: voice_lint.py <BRAND-VOICE.md> | voice_lint.py -", file=sys.stderr)
        return 2

    arg = sys.argv[1]
    try:
        text = read_text(arg)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: cannot read '{arg}': {exc}", file=sys.stderr)
        return 2
    except UnicodeDecodeError as exc:
        print(f"error: '{arg}' is not valid UTF-8: {exc}", file=sys.stderr)
        return 2

    result = lint(text, arg if arg != "-" else "(stdin)")
    write_json(result)

    return 0 if result["verdict"] != "RED" else 1


if __name__ == "__main__":
    sys.exit(main())
