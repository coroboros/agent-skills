#!/usr/bin/env python3
"""
voice_lint.py — validate a BRAND-VOICE.md against canonical-format.md.

Usage:
    voice_lint.py [flags] <BRAND-VOICE.md>
    cat BRAND-VOICE.md | voice_lint.py [flags] -

Flags:
    --allow-extends-outside-skill   suppress 'extends-path-outside-skill' warning

Output (stdout, JSON per references/schemas.md § voice_lint.py).

Exit:
    0  GREEN or YELLOW (errors == 0)
    1  RED (errors >= 1)
    2  file not found, unreadable, or not UTF-8

Requires Python 3.7+. No third-party dependencies.
"""

from __future__ import annotations

import argparse
import datetime
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import (  # noqa: E402
    REMOVE_ALLOWED_FIELDS,
    REPLACE_ALLOWED_FIELDS,
    ExtendsError,
    apply_remove_overrides,
    apply_replace_overrides,
    list_h2_sections,
    merge_voice_dicts,
    normalise_section_heading,
    parse_yaml_minimal,
    read_text,
    resolve_extends_chain,
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


def _err(code, field, message, line=2, source=None, source_path=None, **extra):
    e = {"code": code, "field": field, "message": message, "line": line}
    if source is not None:
        e["source"] = source
    if source_path is not None:
        e["source_path"] = source_path
    e.update(extra)
    return e


def _check_frontmatter_fields(data, errors, warnings, has_extends=False):
    """Static frontmatter checks.

    When `has_extends` is True (i.e., this is a child file declaring
    `voice.extends`), the required-field check is relaxed: only `voice.name`
    must be present locally. The other required fields (`forbidden_lexicon`,
    `rewrite_rules`, `sentence_norms`) may be inherited and are validated at
    the merged level by the chain-walker.
    """
    if has_extends:
        if not (data.get("voice") or {}).get("name"):
            errors.append(_err("missing-required-field", "voice.name",
                               "required frontmatter field 'voice.name' is missing or wrong type"))
    else:
        for field, check in REQUIRED_FIELDS:
            if not check(data):
                errors.append(_err("missing-required-field", field,
                                   f"required frontmatter field '{field}' is missing or wrong type"))

    norms = data.get("sentence_norms") or {}
    if isinstance(norms, dict):
        wmin = norms.get("word_count_min")
        wmax = norms.get("word_count_max")
        whard = norms.get("sentence_max_hard")
        if isinstance(wmin, int) and isinstance(wmax, int) and wmin > wmax:
            errors.append(_err("invalid-field-value", "sentence_norms.word_count_min",
                               f"word_count_min ({wmin}) must be <= word_count_max ({wmax})"))
        if isinstance(wmax, int) and isinstance(whard, int) and wmax > whard:
            errors.append(_err("invalid-field-value", "sentence_norms.word_count_max",
                               f"word_count_max ({wmax}) must be <= sentence_max_hard ({whard})"))
        em = norms.get("em_dash_spacing")
        if em is not None and em not in VALID_EM_DASH_SPACING:
            errors.append(_err("invalid-field-value", "sentence_norms.em_dash_spacing",
                               f"em_dash_spacing must be one of {sorted(VALID_EM_DASH_SPACING)}, got '{em}'"))
        exc = norms.get("exclamation_marks")
        if exc is not None and exc not in VALID_EXCLAMATION:
            errors.append(_err("invalid-field-value", "sentence_norms.exclamation_marks",
                               f"exclamation_marks must be one of {sorted(VALID_EXCLAMATION)}, got '{exc}'"))
        contr = norms.get("contractions")
        if contr is not None and contr not in VALID_CONTRACTIONS:
            errors.append(_err("invalid-field-value", "sentence_norms.contractions",
                               f"contractions must be one of {sorted(VALID_CONTRACTIONS)}, got '{contr}'"))

    rules = data.get("rewrite_rules") or []
    seen_ids = {}
    for i, rule in enumerate(rules):
        if not isinstance(rule, dict):
            errors.append(_err("invalid-field-value", f"rewrite_rules[{i}]",
                               "rewrite_rules entries must be mappings with reject/accept/rule_id"))
            continue
        rule_id = rule.get("rule_id")
        if not rule_id:
            errors.append(_err("missing-required-field", f"rewrite_rules[{i}].rule_id",
                               "every rewrite rule must have a rule_id"))
            continue
        if not RULE_ID_RE.match(str(rule_id)):
            errors.append(_err("invalid-field-value", f"rewrite_rules[{i}].rule_id",
                               f"rule_id must be kebab-case [a-z0-9-]+, got '{rule_id}'"))
        if rule_id in seen_ids:
            errors.append(_err("duplicate-rule-id", f"rewrite_rules[{i}].rule_id",
                               f"rule_id '{rule_id}' duplicates rewrite_rules[{seen_ids[rule_id]}]"))
        else:
            seen_ids[rule_id] = i

    forbidden_lex = data.get("forbidden_lexicon") or []
    if not forbidden_lex and not has_extends:
        # Children with voice.extends inherit the parent's lexicon — empty here is fine.
        warnings.append(_err("empty-required-lexicon", "forbidden_lexicon",
                             "forbidden_lexicon is empty; without it the voice has no banned terms"))

    voice = data.get("voice") or {}
    if not voice.get("source_urls"):
        warnings.append(_err("no-source-urls", "voice.source_urls",
                             "voice.source_urls is empty; doc is interview-only or hand-authored"))

    last_updated = voice.get("last_updated")
    if isinstance(last_updated, str):
        try:
            d = datetime.date.fromisoformat(last_updated)
            age = (datetime.date.today() - d).days
            if age > 180:
                warnings.append(_err("outdated-last-updated", "voice.last_updated",
                                     f"voice.last_updated is {age} days old; consider running update"))
        except ValueError:
            errors.append(_err("invalid-field-value", "voice.last_updated",
                               f"voice.last_updated must be ISO date YYYY-MM-DD, got '{last_updated}'"))


def _check_inheritance(data, errors, warnings):
    """Inheritance-specific frontmatter checks: mutex, _replace/_remove rules,
    attribute_id requirements."""
    voice = data.get("voice") if isinstance(data.get("voice"), dict) else {}
    has_extends = isinstance(voice.get("extends"), str) and bool(voice.get("extends"))

    suffix_keys = [k for k in data.keys() if isinstance(k, str) and (k.endswith("_replace") or k.endswith("_remove"))]
    bases_seen = {}
    for k in suffix_keys:
        if k.endswith("_replace"):
            base = k[: -len("_replace")]
            kind = "replace"
            allowed = REPLACE_ALLOWED_FIELDS
            unsupported_code = "replace-on-unsupported-field"
            no_extends_code = "replace-without-extends"
        else:
            base = k[: -len("_remove")]
            kind = "remove"
            allowed = REMOVE_ALLOWED_FIELDS
            unsupported_code = "remove-on-unsupported-field"
            no_extends_code = "remove-without-extends"

        if not has_extends:
            errors.append(_err(no_extends_code, k,
                               f"'{k}' is meaningless without voice.extends in the same file"))
            continue
        if base not in allowed:
            errors.append(_err(unsupported_code, k,
                               f"'{k}' is not on the allowlist; allowed bases: {sorted(allowed)}"))
            continue
        bases_seen.setdefault(base, []).append((kind, k))

    # Mutex policy:
    #   X + X_replace   — contradictory (replace vs additive merge)
    #   X_replace + X_remove — contradictory (replace nukes parent's; remove targets parent's)
    # ALLOWED:
    #   X + X_remove   — additive merge + selective subtraction (the common case
    #                    where a child adds a few entries and removes a couple of inherited ones)
    for base, occurrences in bases_seen.items():
        kinds = {kind for kind, _ in occurrences}
        canonical_present = base in data
        if canonical_present and "replace" in kinds:
            offenders = [k for kind, k in occurrences if kind == "replace"]
            errors.append(_err("replace-conflict-with-extending", base,
                               f"'{base}' is declared alongside {offenders}; pick one of "
                               f"the canonical field or '{base}_replace'"))
        if "replace" in kinds and "remove" in kinds:
            offenders = [k for _, k in occurrences]
            errors.append(_err("replace-conflict-with-extending", base,
                               f"both '{base}_replace' and '{base}_remove' declared ({offenders}); "
                               f"replace already drops parent's value — remove is meaningless"))

    cores = data.get("core_attributes") or []
    if isinstance(cores, list):
        for i, attr in enumerate(cores):
            if not isinstance(attr, dict):
                continue
            aid = attr.get("attribute_id")
            if not isinstance(aid, str) or not aid:
                errors.append(_err("core-attribute-missing-id", f"core_attributes[{i}]",
                                   "core_attributes entry lacks attribute_id (kebab-case, stable merge key)"))


def _check_prose(body, sections, errors, warnings, has_extends=False):
    """Prose section presence, order, content density.

    When `has_extends` is True, the recommended-section check is relaxed:
    sections 5-11 may be inherited from the parent's prose. Only the four
    required sections (1-4) must be present locally — they explain the child's
    own voice.
    """
    seen = {}
    seen_order = []
    for heading, lineno in sections:
        norm = normalise_section_heading(heading)
        if norm in seen:
            errors.append(_err("duplicate-section", f"section:{norm}",
                               f"H2 '{heading}' appears twice (also at line {seen[norm]})", line=lineno))
        else:
            seen[norm] = lineno
            seen_order.append(norm)

    for required in REQUIRED_SECTIONS:
        if required not in seen:
            errors.append(_err("missing-section", f"section:{required}",
                               f"required H2 section '{required}' is missing", line=0))

    if not has_extends:
        for recommended in RECOMMENDED_SECTIONS:
            if recommended not in seen:
                warnings.append(_err("recommended-section-missing", f"section:{recommended}",
                                     f"recommended H2 section '{recommended}' is missing", line=0))

    found_canonical = [s for s in seen_order if s in ALL_CANONICAL_SECTIONS]
    expected_canonical = [s for s in ALL_CANONICAL_SECTIONS if s in seen]
    if found_canonical != expected_canonical:
        errors.append(_err("section-out-of-order", "section:order",
                           f"canonical sections must appear in this order: {expected_canonical}; "
                           f"found: {found_canonical}", line=0))

    body_lines = (body or "").splitlines()
    section_starts = [(s, l) for s, l in sections if normalise_section_heading(s) in ALL_CANONICAL_SECTIONS]
    section_starts.sort(key=lambda t: t[1])
    for idx, (heading, lineno) in enumerate(section_starts):
        next_line = section_starts[idx + 1][1] if idx + 1 < len(section_starts) else len(body_lines) + 1
        section_text = "\n".join(body_lines[lineno: next_line - 1])
        prose = re.sub(r"```.*?```", "", section_text, flags=re.DOTALL)
        prose = re.sub(r"`[^`\n]+`", "", prose)
        if len(prose.strip()) < 50:
            warnings.append(_err("section-light-content",
                                 f"section:{normalise_section_heading(heading)}",
                                 f"section '{heading}' has under 50 chars of prose", line=lineno))


def _is_outside_skill(child_path, parent_path):
    """Heuristic: True when parent_path lives outside the child's directory tree.

    Used to flag chains that escape the skill — a footgun for cross-machine
    portability (paths like ~/Desktop/...). Suppressed by --allow-extends-outside-skill.
    """
    try:
        Path(parent_path).resolve().relative_to(Path(child_path).resolve().parent)
        return False
    except ValueError:
        return True


def _check_overrides_warnings(chain, child_data, warnings):
    """Surface inheritance-time warnings detectable from chain data only.

    rewrite-rule-overridden-by-child: child's rule_id collides with an ancestor's
    without `override: true`.
    """
    child_rules = child_data.get("rewrite_rules") or []
    if not isinstance(child_rules, list):
        return

    ancestor_ids = set()
    for _, anc_data in chain[:-1]:  # all parents
        for r in (anc_data.get("rewrite_rules") or []):
            if isinstance(r, dict):
                rid = r.get("rule_id")
                if isinstance(rid, str):
                    ancestor_ids.add(rid)
        replace_rules = anc_data.get("rewrite_rules_replace") or []
        if isinstance(replace_rules, list):
            for r in replace_rules:
                if isinstance(r, dict):
                    rid = r.get("rule_id")
                    if isinstance(rid, str):
                        ancestor_ids.add(rid)

    for r in child_rules:
        if not isinstance(r, dict):
            continue
        rid = r.get("rule_id")
        if isinstance(rid, str) and rid in ancestor_ids and not r.get("override"):
            warnings.append(_err("rewrite-rule-overridden-by-child", f"rewrite_rules[?].rule_id={rid}",
                                 f"child redefines rule_id '{rid}' from an ancestor without 'override: true'; "
                                 "silent overrides regress tone — mark the override or rename the rule"))


def _stats_from_data(data, body=None, fm=None, sections=None, text=None):
    fm_lines = (fm or "").count("\n")
    body_lines = (body or "").count("\n")
    total_lines = (text or "").count("\n") + (1 if text and not text.endswith("\n") else 0)
    rule_count = len(((data or {}).get("rewrite_rules")) or [])
    forbidden_count = len(((data or {}).get("forbidden_lexicon")) or [])
    section_count = len(sections or [])
    return {
        "frontmatter_lines": fm_lines,
        "prose_lines": body_lines,
        "total_lines": total_lines,
        "rule_count": rule_count,
        "forbidden_lexicon_count": forbidden_count,
        "section_count": section_count,
    }


def _stats_merged(merged):
    return {
        "rule_count": len((merged or {}).get("rewrite_rules") or []),
        "forbidden_lexicon_count": len((merged or {}).get("forbidden_lexicon") or []),
    }


def _verdict(path, errors, warnings, text, body=None, fm=None, data=None, sections=None,
             chain=None, merged_stats=None):
    if errors:
        v = "RED"
    elif warnings:
        v = "YELLOW"
    else:
        v = "GREEN"

    out = {
        "path": path,
        "verdict": v,
        "errors": errors,
        "warnings": warnings,
        "stats": _stats_from_data(data, body=body, fm=fm, sections=sections, text=text),
    }
    if chain:
        out["chain"] = chain
    if merged_stats is not None:
        out["merged_stats"] = merged_stats
    return out


def _lint_isolated(text, path):
    """Lint a single file in isolation (no chain walk). Used for parent recursion."""
    errors = []
    warnings = []

    fm, body = split_frontmatter(text)
    if fm is None:
        errors.append(_err("frontmatter-invalid-yaml", None,
                           "no YAML frontmatter found (file must start with '---' on line 1)", line=1))
        return _verdict(path, errors, warnings, text, body=text, fm=None)

    try:
        data = parse_yaml_minimal(fm)
    except ValueError as exc:
        errors.append(_err("frontmatter-invalid-yaml", None, str(exc),
                           line=getattr(exc, "line", 2)))
        return _verdict(path, errors, warnings, text, body=body, fm=None)

    if not isinstance(data, dict):
        errors.append(_err("frontmatter-invalid-yaml", None, "frontmatter root must be a mapping"))
        return _verdict(path, errors, warnings, text, body=body, fm=None)

    voice = data.get("voice") if isinstance(data.get("voice"), dict) else {}
    has_extends = isinstance(voice.get("extends"), str) and bool(voice.get("extends"))

    _check_frontmatter_fields(data, errors, warnings, has_extends=has_extends)
    _check_inheritance(data, errors, warnings)
    sections = list_h2_sections(body or "")
    _check_prose(body, sections, errors, warnings, has_extends=has_extends)

    return _verdict(path, errors, warnings, text, body=body, fm=fm, data=data, sections=sections)


def lint(text, path, allow_outside_skill=False):
    """Public entry point. Lints `text` (the file content) and walks the chain.

    `path` is the file path used for chain resolution (relative paths in
    `voice.extends` resolve against `path`'s directory).
    """
    isolated = _lint_isolated(text, path)
    for e in isolated.get("errors", []):
        e.setdefault("source", "child")
    for w in isolated.get("warnings", []):
        w.setdefault("source", "child")

    if isolated["verdict"] == "RED":
        return isolated

    fm, body = split_frontmatter(text)
    data = parse_yaml_minimal(fm) if fm else {}
    sections = list_h2_sections(body or "")

    voice = data.get("voice") if isinstance(data.get("voice"), dict) else {}
    has_extends = isinstance(voice.get("extends"), str) and bool(voice.get("extends"))

    chain_paths = []
    merged_stats = None
    chain_errors = []
    chain_warnings = []

    if has_extends and path != "(stdin)":
        try:
            chain = resolve_extends_chain(path)
            chain_paths = [str(p) for p, _ in chain]

            for parent_path, _parent_data in chain[:-1]:
                if not allow_outside_skill and _is_outside_skill(path, parent_path):
                    chain_warnings.append(_err(
                        "extends-path-outside-skill", "voice.extends",
                        f"chain reaches '{parent_path}' which lives outside the linted file's directory; "
                        "pass --allow-extends-outside-skill to suppress",
                        source="child",
                        source_path=str(parent_path),
                    ))
                try:
                    parent_text = parent_path.read_text(encoding="utf-8")
                except OSError as exc:
                    chain_errors.append(_err(
                        "extends-parent-invalid", "voice.extends",
                        f"cannot read parent '{parent_path}': {exc}",
                        source="child",
                        source_path=str(parent_path),
                    ))
                    continue
                parent_verdict = _lint_isolated(parent_text, str(parent_path))
                parent_errs = parent_verdict.get("errors") or []
                parent_warns = parent_verdict.get("warnings") or []
                if parent_errs:
                    chain_errors.append(_err(
                        "extends-parent-invalid", "voice.extends",
                        f"parent '{parent_path}' fails its own lint",
                        source=f"parent:{parent_path}",
                        source_path=str(parent_path),
                        parent_errors=parent_errs,
                    ))
                for w in parent_warns:
                    w.setdefault("source", f"parent:{parent_path}")
                    w.setdefault("source_path", str(parent_path))
                    chain_warnings.append(w)

            if not chain_errors:
                merged = None
                for _, anc_data in chain:
                    merged = merge_voice_dicts(merged, anc_data)
                    merged = apply_replace_overrides(merged)
                    merged = apply_remove_overrides(merged)
                merged = merged or {}

                merged_errors = []
                merged_warnings = []
                _check_frontmatter_fields(merged, merged_errors, merged_warnings)
                _check_overrides_warnings(chain, data, merged_warnings)
                for e in merged_errors:
                    e["source"] = "merged"
                for w in merged_warnings:
                    w.setdefault("source", "merged")
                chain_errors.extend(merged_errors)
                chain_warnings.extend(merged_warnings)

                merged_stats = _stats_merged(merged)
        except ExtendsError as exc:
            chain_errors.append(_err(
                exc.code, "voice.extends", str(exc),
                source="child",
                source_path=str(exc.path),
            ))

    errors = list(isolated.get("errors") or []) + chain_errors
    warnings = list(isolated.get("warnings") or []) + chain_warnings

    return _verdict(path, errors, warnings, text,
                    body=body, fm=fm, data=data, sections=sections,
                    chain=chain_paths or None, merged_stats=merged_stats)


def main():
    parser = argparse.ArgumentParser(
        description="Validate a BRAND-VOICE.md against canonical-format.md.",
        prog="voice_lint.py",
    )
    parser.add_argument("path", help="path to BRAND-VOICE.md (or '-' for stdin)")
    parser.add_argument(
        "--allow-extends-outside-skill", action="store_true",
        help="suppress 'extends-path-outside-skill' warning",
    )
    args = parser.parse_args()

    try:
        text = read_text(args.path)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: cannot read '{args.path}': {exc}", file=sys.stderr)
        return 2
    except UnicodeDecodeError as exc:
        print(f"error: '{args.path}' is not valid UTF-8: {exc}", file=sys.stderr)
        return 2

    path_label = args.path if args.path != "-" else "(stdin)"
    result = lint(text, path_label, allow_outside_skill=args.allow_extends_outside_skill)
    write_json(result)
    return 0 if result["verdict"] != "RED" else 1


if __name__ == "__main__":
    sys.exit(main())
