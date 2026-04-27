#!/usr/bin/env python3
"""
extract_rules.py — emit a flat, prose-free list of testable voice rules.

Usage:
    extract_rules.py [flags] <BRAND-VOICE.md>
    cat BRAND-VOICE.md | extract_rules.py [flags] -

Flags (see references/schemas.md § extract_rules.py for full spec):

    --full                       (default) emit core_attributes + contexts + source_urls
                                 alongside the legacy fields. Required for humanize-en parity.
    --legacy                     emit the v1 minimal output. Byte-identical to the pre-extends
                                 shape. Mutually exclusive with --full.
    --no-resolve-extends         skip voice.extends chain resolution; emit child-only rules.
    --explain                    annotate each item with `# from <relpath>` provenance.
                                 Default output is byte-stable (LLM-prompt determinism).
    --explain-json               emit structured provenance JSON instead of plain text.
    --allow-extends-outside-skill  suppress the warning when chain escapes the skill dir.

Empty fields are omitted. Designed for inclusion in a downstream LLM prompt without
JSON parsing — humanize-en consumes this output directly.

Exit:
    0  extraction succeeded
    1  file not found, unreadable, YAML invalid, or chain resolution failed

Requires Python 3.7+. No third-party dependencies.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import (  # noqa: E402
    ExtendsError,
    compute_provenance,
    parse_yaml_minimal,
    read_text,
    resolve_and_merge,
    split_frontmatter,
)


def _bool_str(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _emit_string_list(label, items, out, prov_map=None):
    if not items:
        return
    out.append(f"{label}:")
    for item in items:
        suffix = ""
        if prov_map:
            origin = prov_map.get(item)
            if origin:
                suffix = f"  # from {origin}"
        out.append(f"  - {item}{suffix}")
    out.append("")


def format_rules_legacy(data):
    """v1 minimal output. Byte-identical to the pre-extends shape.

    Used by external consumers pinned to the legacy contract; verified by
    `tests/test_backwards_compat.py`.
    """
    out = []

    voice = data.get("voice") or {}
    name = voice.get("name") or "(unnamed)"
    last_updated = voice.get("last_updated")
    out.append(f"voice: {name}")
    if last_updated:
        out.append(f"last_updated: {last_updated}")
    out.append("")

    _emit_string_list("forbidden", data.get("forbidden_lexicon") or [], out)
    _emit_string_list("required", data.get("required_lexicon") or [], out)

    norms = data.get("sentence_norms") or {}
    if norms:
        out.append("sentence_norms:")
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
                out.append(f"  {key}: {_bool_str(norms[key])}")
        out.append("")

    _emit_string_list("forbidden_patterns", data.get("forbidden_patterns") or [], out)

    rules = data.get("rewrite_rules") or []
    if rules:
        out.append("rewrite_rules:")
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


def format_rules_full(data, prov=None):
    """v2 full output: legacy fields + core_attributes + contexts + source_urls.

    Required by humanize-en post-migration. Annotates per-item provenance when `prov`
    is provided (from `--explain`); default output is byte-stable for LLM determinism.
    """
    out = []

    voice = data.get("voice") or {}
    name = voice.get("name") or "(unnamed)"
    last_updated = voice.get("last_updated")
    source_urls = voice.get("source_urls") or []

    out.append(f"voice: {name}")
    if last_updated:
        out.append(f"last_updated: {last_updated}")
    out.append("")

    if source_urls:
        out.append("source_urls:")
        for url in source_urls:
            out.append(f"  - {url}")
        out.append("")

    cores = data.get("core_attributes") or []
    if cores:
        out.append("core_attributes:")
        ca_prov = (prov or {}).get("core_attributes") if isinstance((prov or {}).get("core_attributes"), dict) else None
        for attr in cores:
            if not isinstance(attr, dict):
                continue
            aid = attr.get("attribute_id")
            nm = attr.get("name") or "?"
            fm = attr.get("failure_mode") or ""
            line = f"  - [{aid}] {nm}" if isinstance(aid, str) and aid else f"  - {nm}"
            if fm:
                line += f": {fm}"
            if ca_prov:
                origin = None
                if isinstance(aid, str) and aid:
                    origin = ca_prov.get(("attribute_id", aid))
                if origin is None and isinstance(nm, str):
                    origin = ca_prov.get(("name-norm", " ".join(nm.lower().split())))
                if origin:
                    line += f"  # from {origin}"
            out.append(line)
        out.append("")

    fl_prov = (prov or {}).get("forbidden_lexicon") if isinstance((prov or {}).get("forbidden_lexicon"), dict) else None
    rl_prov = (prov or {}).get("required_lexicon") if isinstance((prov or {}).get("required_lexicon"), dict) else None
    fp_prov = (prov or {}).get("forbidden_patterns") if isinstance((prov or {}).get("forbidden_patterns"), dict) else None

    _emit_string_list("forbidden", data.get("forbidden_lexicon") or [], out, fl_prov)
    _emit_string_list("required", data.get("required_lexicon") or [], out, rl_prov)

    norms = data.get("sentence_norms") or {}
    if norms:
        out.append("sentence_norms:")
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
                out.append(f"  {key}: {_bool_str(norms[key])}")
        sn_prov = (prov or {}).get("sentence_norms") if prov else None
        if isinstance(sn_prov, str):
            out.append(f"  # from {sn_prov}")
        out.append("")

    _emit_string_list("forbidden_patterns", data.get("forbidden_patterns") or [], out, fp_prov)

    rules = data.get("rewrite_rules") or []
    if rules:
        out.append("rewrite_rules:")
        rr_prov = (prov or {}).get("rewrite_rules") if isinstance((prov or {}).get("rewrite_rules"), dict) else None
        for rule in rules:
            if not isinstance(rule, dict):
                continue
            rule_id = rule.get("rule_id") or "?"
            reject = rule.get("reject") or "?"
            accept = rule.get("accept") or "?"
            line = f"  - [{rule_id}] {reject} -> {accept}"
            if rr_prov:
                origin = rr_prov.get(("rule_id", rule_id))
                if origin:
                    line += f"  # from {origin}"
            out.append(line)
        out.append("")

    contexts = data.get("contexts") or {}
    if contexts:
        out.append("contexts:")
        ctx_prov = (prov or {}).get("contexts") if prov else None
        for ctx_name, ctx_data in contexts.items():
            out.append(f"  {ctx_name}:")
            if isinstance(ctx_data, dict):
                for k, v in ctx_data.items():
                    out.append(f"    {k}: {_bool_str(v)}")
        if isinstance(ctx_prov, str):
            out.append(f"  # from {ctx_prov}")
        out.append("")

    pronouns = data.get("pronouns") or {}
    if pronouns:
        default = pronouns.get("default") or "(unspecified)"
        forbid = pronouns.get("forbid") or []
        forbid_str = ", ".join(forbid) if forbid else "none"
        line = f"pronouns: {default} (forbid: {forbid_str})"
        pron_prov = (prov or {}).get("pronouns") if prov else None
        if isinstance(pron_prov, str):
            line += f"  # from {pron_prov}"
        out.append(line)

    while out and out[-1] == "":
        out.pop()
    return "\n".join(out) + "\n"


def _explain_json(chain, merged, provenance):
    """Structured provenance for tooling. See references/schemas.md."""
    fl_prov = provenance.get("forbidden_lexicon") or {}
    rl_prov = provenance.get("required_lexicon") or {}
    fp_prov = provenance.get("forbidden_patterns") or {}
    rr_prov = provenance.get("rewrite_rules") or {}
    ca_prov = provenance.get("core_attributes") or {}

    def _ca_origin(attr):
        if not isinstance(attr, dict):
            return None
        aid = attr.get("attribute_id")
        if isinstance(aid, str):
            o = ca_prov.get(("attribute_id", aid))
            if o:
                return o
        nm = attr.get("name")
        if isinstance(nm, str):
            return ca_prov.get(("name-norm", " ".join(nm.lower().split())))
        return None

    payload = {
        "chain": [str(p) for p, _ in chain],
        "voice": merged.get("voice") or {},
        "merged": {
            "forbidden_lexicon": [
                {"value": v, "source": fl_prov.get(v)} for v in (merged.get("forbidden_lexicon") or [])
            ],
            "required_lexicon": [
                {"value": v, "source": rl_prov.get(v)} for v in (merged.get("required_lexicon") or [])
            ],
            "forbidden_patterns": [
                {"value": v, "source": fp_prov.get(v)} for v in (merged.get("forbidden_patterns") or [])
            ],
            "rewrite_rules": [
                {**r, "source": rr_prov.get(("rule_id", r.get("rule_id")))}
                for r in (merged.get("rewrite_rules") or []) if isinstance(r, dict)
            ],
            "core_attributes": [
                {**a, "source": _ca_origin(a)}
                for a in (merged.get("core_attributes") or []) if isinstance(a, dict)
            ],
            "sentence_norms": merged.get("sentence_norms"),
            "contexts": merged.get("contexts"),
            "pronouns": merged.get("pronouns"),
        },
        "object_provenance": {
            "sentence_norms": provenance.get("sentence_norms"),
            "contexts": provenance.get("contexts"),
            "pronouns": provenance.get("pronouns"),
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Emit a flat list of testable voice rules from BRAND-VOICE.md.",
        prog="extract_rules.py",
    )
    parser.add_argument("path", help="path to BRAND-VOICE.md (or '-' for stdin)")
    parser.add_argument(
        "--full", action="store_true",
        help="emit full output (default): legacy fields + core_attributes + contexts + source_urls",
    )
    parser.add_argument(
        "--legacy", action="store_true",
        help="emit the v1 minimal output (byte-identical to the pre-extends shape)",
    )
    parser.add_argument(
        "--no-resolve-extends", dest="resolve_extends", action="store_false", default=True,
        help="skip voice.extends chain resolution; emit child-only rules",
    )
    parser.add_argument(
        "--explain", action="store_true",
        help="annotate each item with '# from <file>' provenance",
    )
    parser.add_argument(
        "--explain-json", action="store_true",
        help="emit structured provenance JSON instead of plain text",
    )
    parser.add_argument(
        "--allow-extends-outside-skill", action="store_true",
        help="suppress 'extends-path-outside-skill' warning when chain escapes skill dir",
    )
    args = parser.parse_args()

    if args.legacy and args.full:
        print("error: --legacy and --full are mutually exclusive", file=sys.stderr)
        return 1
    use_full = not args.legacy

    try:
        text = read_text(args.path)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"error: cannot read '{args.path}': {exc}", file=sys.stderr)
        return 1

    fm, _body = split_frontmatter(text)
    if fm is None:
        print(f"error: '{args.path}' has no YAML frontmatter", file=sys.stderr)
        return 1
    try:
        data = parse_yaml_minimal(fm)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if not isinstance(data, dict):
        print("error: frontmatter root must be a mapping", file=sys.stderr)
        return 1

    voice = data.get("voice") if isinstance(data.get("voice"), dict) else {}
    has_extends = isinstance(voice.get("extends"), str) and voice.get("extends")

    chain = []
    merged = data

    if args.resolve_extends and has_extends and args.path != "-":
        try:
            chain, merged = resolve_and_merge(args.path)
        except ExtendsError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
    elif args.path != "-":
        # Single-node chain — useful for explain mode when there is no inheritance
        chain = [(Path(args.path).resolve(), data)]

    provenance = {}
    if (args.explain or args.explain_json) and chain and has_extends:
        provenance = compute_provenance(chain, merged)

    if args.explain_json:
        sys.stdout.write(_explain_json(chain, merged, provenance))
        return 0

    use_prov = provenance if (args.explain and provenance) else None

    if use_full:
        sys.stdout.write(format_rules_full(merged, prov=use_prov))
    else:
        sys.stdout.write(format_rules_legacy(merged))
    return 0


if __name__ == "__main__":
    sys.exit(main())
