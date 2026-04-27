#!/usr/bin/env python3
"""
utils.py — shared I/O and helpers for brand-voice scripts.

Mirrors skills/humanize-en/scripts/utils.py — same I/O contract.
Requires Python 3.7+. No third-party dependencies.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


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


def split_frontmatter(text):
    """Return (frontmatter_lines, body_text). Frontmatter is the YAML between
    the leading and second '---' delimiters. body_text excludes the frontmatter
    block and the delimiters but preserves all subsequent newlines.

    Returns (None, text) if no frontmatter is present.
    """
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\n") != "---":
        return None, text
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].rstrip("\n") == "---":
            end_idx = i
            break
    if end_idx is None:
        return None, text
    frontmatter_block = "".join(lines[1:end_idx])
    body = "".join(lines[end_idx + 1 :])
    return frontmatter_block, body


def parse_yaml_minimal(yaml_text):
    """Parse a minimal subset of YAML used by BRAND-VOICE.md frontmatter.

    Supports: nested dicts (2-space indent), lists of scalars, lists of inline
    objects ({k: v, k: v}), strings (quoted/unquoted), booleans, integers.

    Does NOT support: anchors, aliases, multi-line strings (|, >), tags, flow
    sequences across lines.

    Returns a dict. Raises ValueError on parse error with a `.line` attribute
    set to the offending 1-indexed line number.

    Implementation note: this is a deliberate hand-roll to keep the script
    dependency-free (no PyYAML). The frontmatter shape is well-defined by
    canonical-format.md — exotic YAML constructs are out of scope.
    """
    lines = yaml_text.splitlines()
    pos = [0]

    def err(msg, lineno):
        e = ValueError(f"yaml: {msg} (line {lineno + 1})")
        e.line = lineno + 1
        return e

    def peek():
        while pos[0] < len(lines):
            line = lines[pos[0]]
            stripped = line.split("#", 1)[0].rstrip()
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
            return (
                inner
                .replace('\\"', '"')
                .replace("\\\\", "\\")
                .replace("\\n", "\n")
                .replace("\\t", "\t")
            )
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

    def _kv_split(s):
        """Locate the first YAML key-value separator (':' followed by space or EOL).

        Skips quoted segments so 'foo: "a:b"' returns key='foo', value='"a:b"'.
        Returns (key, value) or (None, None) when no separator is present —
        which means strings like 'https://example.com' are NOT misread as `key: value`.
        """
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
                return s[:i].strip(), s[i + 1 :].strip()
        return None, None

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
    """Split a flow-style YAML inner content (`a, b, c` or `k: v, k: v`) on
    commas while respecting [] and {} nesting and quoted strings."""
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


def list_h2_sections(body_text):
    """Return a list of (heading_text, line_number) for each H2 in body_text.

    Line numbers are 1-indexed relative to body_text. Code-fenced blocks are
    skipped so a `## something` inside a code block doesn't count.
    """
    out = []
    in_fence = False
    for idx, line in enumerate(body_text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if stripped.startswith("## ") and not stripped.startswith("###"):
            out.append((stripped[3:].strip(), idx))
    return out


def normalise_section_heading(heading):
    """Strip leading numbering ('1.', '1', '1 /') and lowercase the heading.

    'Core Voice Attributes' → 'core voice attributes'
    '1. Core voice attributes' → 'core voice attributes'
    '1 / Core voice attributes' → 'core voice attributes'
    """
    text = heading.strip().lower()
    text = re.sub(r"^\d+\s*[.\/]?\s*", "", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Inheritance support — `voice.extends` chain resolution and merge
# ---------------------------------------------------------------------------

MAX_EXTENDS_DEPTH = 5

REPLACE_ALLOWED_FIELDS = frozenset({
    "forbidden_lexicon",
    "required_lexicon",
    "forbidden_patterns",
    "rewrite_rules",
    "core_attributes",
    "sentence_norms",
    "contexts",
    "pronouns",
})

REMOVE_ALLOWED_FIELDS = frozenset({
    "forbidden_lexicon",
    "required_lexicon",
    "forbidden_patterns",
    "rewrite_rules",
    "core_attributes",
})


class ExtendsError(RuntimeError):
    """Raised by resolve_extends_chain. `code` attribute matches the lint code."""

    def __init__(self, code, path, detail=""):
        self.code = code
        self.path = path
        self.detail = detail
        msg = f"{code}: {path}"
        if detail:
            msg += f" — {detail}"
        super().__init__(msg)


def canonical_file_id(path):
    """Return a stable identity tuple for cycle detection.

    Uses (st_dev, st_ino) on POSIX where the inode is meaningful; falls back to a
    canonical path string lower-cased on Windows. The inode path is correct on
    macOS HFS+/APFS where the filesystem is case-insensitive by default —
    `Path.resolve()` returns different strings for `./x.md` and `./X.md` even
    though they are the same file, and `os.stat()` correctly reports the same
    inode for both.
    """
    p = Path(path).resolve()
    try:
        st = p.stat()
    except OSError:
        # File missing — caller will surface a more precise error.
        return ("path", str(p).lower() if os.name == "nt" else str(p))
    if os.name != "nt" and getattr(st, "st_ino", 0):
        return ("inode", st.st_dev, st.st_ino)
    return ("path", str(p).lower() if os.name == "nt" else str(p))


_VOICE_EXTENSIONS = (".md", ".mdx", ".markdown")


def resolve_extends_chain(start_path, max_depth=MAX_EXTENDS_DEPTH):
    """Walk the `voice.extends` chain from `start_path`.

    Returns an ordered list of `(Path, frontmatter_dict)` tuples, **root-first**
    (so callers can iterate parent → child).

    Raises `ExtendsError` with one of these `code`s on failure:
    - `extends-cycle`               — the chain revisits a file
    - `extends-depth-exceeded`      — chain longer than `max_depth`
    - `extends-parent-not-found`    — `voice.extends` points at a missing file
    - `extends-parent-invalid`      — frontmatter missing or unparseable
    """
    nodes = []  # (Path, dict) — child-first; reversed before return
    seen_ids = set()
    current = Path(start_path).resolve()
    depth = 0

    while True:
        if not current.is_file():
            raise ExtendsError("extends-parent-not-found", current)

        file_id = canonical_file_id(current)
        if file_id in seen_ids:
            raise ExtendsError("extends-cycle", current)
        seen_ids.add(file_id)

        try:
            text = current.read_text(encoding="utf-8")
        except OSError as exc:
            raise ExtendsError("extends-parent-invalid", current, str(exc))

        fm, _body = split_frontmatter(text)
        if fm is None:
            raise ExtendsError("extends-parent-invalid", current, "no YAML frontmatter")

        try:
            data = parse_yaml_minimal(fm)
        except ValueError as exc:
            raise ExtendsError("extends-parent-invalid", current, str(exc))
        if not isinstance(data, dict):
            raise ExtendsError("extends-parent-invalid", current, "frontmatter root not a mapping")

        nodes.append((current, data))

        voice = data.get("voice") if isinstance(data.get("voice"), dict) else {}
        parent_ref = voice.get("extends")
        if not isinstance(parent_ref, str) or not parent_ref:
            break

        if depth + 1 > max_depth:
            raise ExtendsError("extends-depth-exceeded", current, f"max_depth={max_depth}")

        if not parent_ref.lower().endswith(_VOICE_EXTENSIONS):
            raise ExtendsError(
                "extends-parent-invalid",
                current,
                f"voice.extends must end in {'/'.join(_VOICE_EXTENSIONS)}; got '{parent_ref}'",
            )

        parent_path = Path(parent_ref)
        if not parent_path.is_absolute():
            parent_path = current.parent / parent_path
        current = parent_path.resolve()
        depth += 1

    nodes.reverse()
    return nodes


def merge_voice_dicts(parent, child):
    """Merge two frontmatter dicts per the canonical merge policy.

    Returns a new dict; does not mutate inputs. `parent` may be None or empty
    (treated as no parent); `child` may be None (treated as parent only).

    Order: parent-first then child-appended for unions; `dict.fromkeys()`
    preserves insertion order so output is stable across `PYTHONHASHSEED`.

    Per-field policy is documented in `references/canonical-format.md`. The
    `_replace` and `_remove` overrides on `child` are *not* applied here — they
    are carried into the merged dict for downstream `apply_replace_overrides`
    and `apply_remove_overrides` to process.
    """
    parent = parent or {}
    child = child or {}
    if not isinstance(parent, dict):
        parent = {}
    if not isinstance(child, dict):
        child = {}

    merged = {}

    # voice.* — child wins per key, except `extends` which is per-file (not inherited downstream).
    parent_voice = parent.get("voice") if isinstance(parent.get("voice"), dict) else {}
    child_voice = child.get("voice") if isinstance(child.get("voice"), dict) else {}
    voice = dict(parent_voice)
    for k, v in child_voice.items():
        if k == "extends":
            continue
        voice[k] = v
    voice.pop("extends", None)
    if voice:
        merged["voice"] = voice

    # core_attributes — merge by attribute_id with normalised-name fallback
    ca = _merge_keyed_list(
        parent.get("core_attributes") or [],
        child.get("core_attributes") or [],
        ("attribute_id", "name"),
    )
    if ca:
        merged["core_attributes"] = ca

    # List-of-string fields — union with stable dedup (parent-first order)
    for f in ("forbidden_lexicon", "required_lexicon", "forbidden_patterns"):
        unioned = list(dict.fromkeys((parent.get(f) or []) + (child.get(f) or [])))
        if unioned:
            merged[f] = unioned

    # rewrite_rules — merge by rule_id; child wins on collision
    rr = _merge_keyed_list(
        parent.get("rewrite_rules") or [],
        child.get("rewrite_rules") or [],
        ("rule_id",),
    )
    if rr:
        merged["rewrite_rules"] = rr

    # sentence_norms — shallow merge (key-by-key)
    sn = {**(parent.get("sentence_norms") or {}), **(child.get("sentence_norms") or {})}
    if sn:
        merged["sentence_norms"] = sn

    # contexts — deep merge by context name; per-context shallow merge
    parent_ctx = parent.get("contexts") if isinstance(parent.get("contexts"), dict) else {}
    child_ctx = child.get("contexts") if isinstance(child.get("contexts"), dict) else {}
    if parent_ctx or child_ctx:
        contexts = {}
        ordered_names = list(parent_ctx) + [n for n in child_ctx if n not in parent_ctx]
        for name in ordered_names:
            p_val = parent_ctx.get(name)
            c_val = child_ctx.get(name)
            if isinstance(p_val, dict) and isinstance(c_val, dict):
                contexts[name] = {**p_val, **c_val}
            elif name in child_ctx:
                contexts[name] = c_val
            else:
                contexts[name] = p_val
        merged["contexts"] = contexts

    # pronouns — shallow merge; pronouns.forbid REPLACED if child declares it
    parent_pron = parent.get("pronouns") if isinstance(parent.get("pronouns"), dict) else {}
    child_pron = child.get("pronouns") if isinstance(child.get("pronouns"), dict) else {}
    if parent_pron or child_pron:
        pronouns = {}
        for k in list(parent_pron) + [k for k in child_pron if k not in parent_pron]:
            if k == "forbid" and "forbid" in child_pron:
                pronouns[k] = child_pron[k]
            elif k in child_pron:
                pronouns[k] = child_pron[k]
            else:
                pronouns[k] = parent_pron[k]
        merged["pronouns"] = pronouns

    # Carry the child's _replace / _remove keys forward; apply_*_overrides will consume them.
    for k, v in child.items():
        if k.endswith("_replace") or k.endswith("_remove"):
            merged[k] = v

    # Pass through any other top-level keys child-wins (forward compat for unknown extensions).
    # Canonical fields are excluded regardless of whether they ended up in `merged` —
    # otherwise an empty `forbidden_lexicon: []` from a parent would silently re-appear.
    canonical_handled = {
        "voice",
        "core_attributes",
        "forbidden_lexicon",
        "required_lexicon",
        "forbidden_patterns",
        "rewrite_rules",
        "sentence_norms",
        "contexts",
        "pronouns",
    }
    handled = set(merged.keys()) | canonical_handled
    for src in (parent, child):
        for k, v in (src or {}).items():
            if k in handled:
                continue
            if k.endswith("_replace") or k.endswith("_remove"):
                continue
            merged[k] = v

    return merged


def _merge_keyed_list(parent_list, child_list, key_fields):
    """Merge two lists of dicts by the first available key in `key_fields`.

    Items lacking every key field are appended in order (no merge). Child wins
    on collision; new items appended.
    """
    def _key(item):
        if not isinstance(item, dict):
            return None
        for kf in key_fields:
            v = item.get(kf)
            if isinstance(v, str) and v:
                if kf == "name":
                    return ("name-norm", " ".join(v.lower().split()))
                return (kf, v)
        return None

    result = []
    pos = {}
    for item in parent_list or []:
        k = _key(item)
        if k is None:
            result.append(item)
        else:
            pos[k] = len(result)
            result.append(item)

    for item in child_list or []:
        k = _key(item)
        if k is None:
            result.append(item)
            continue
        if k in pos:
            result[pos[k]] = item
        else:
            pos[k] = len(result)
            result.append(item)

    return result


def apply_replace_overrides(merged):
    """Apply `<field>_replace` keys: replace canonical field, drop the suffix key.

    Whitelisted fields only (others are left in place for the linter to flag).
    Returns a new dict; does not mutate input.
    """
    if not isinstance(merged, dict):
        return merged
    out = dict(merged)
    for key in list(out.keys()):
        if not key.endswith("_replace"):
            continue
        base = key[: -len("_replace")]
        if base in REPLACE_ALLOWED_FIELDS:
            out[base] = out[key]
            del out[key]
    return out


def apply_remove_overrides(merged):
    """Apply `<field>_remove` keys: subtract specified entries, drop the suffix key.

    For list-of-string fields: removes exact matches.
    For list-of-object fields (`rewrite_rules`, `core_attributes`): removes entries
    whose stable ID is in the remove list.
    Returns a new dict; does not mutate input.
    """
    if not isinstance(merged, dict):
        return merged
    out = dict(merged)
    for key in list(out.keys()):
        if not key.endswith("_remove"):
            continue
        base = key[: -len("_remove")]
        if base not in REMOVE_ALLOWED_FIELDS:
            continue
        remove_items = out[key] or []
        del out[key]
        canonical = out.get(base)
        if canonical is None:
            continue
        if base == "rewrite_rules":
            ids = {item for item in remove_items if isinstance(item, str)}
            out[base] = [r for r in canonical
                         if not (isinstance(r, dict) and r.get("rule_id") in ids)]
        elif base == "core_attributes":
            ids = {item for item in remove_items if isinstance(item, str)}
            kept = []
            for r in canonical:
                if isinstance(r, dict):
                    rid = r.get("attribute_id")
                    if not rid:
                        nm = r.get("name")
                        rid = " ".join(nm.lower().split()) if isinstance(nm, str) else None
                    if rid and rid in ids:
                        continue
                kept.append(r)
            out[base] = kept
        else:
            remove_set = {item for item in remove_items if isinstance(item, str)}
            out[base] = [item for item in canonical if item not in remove_set]
    return out


def resolve_and_merge(start_path, max_depth=MAX_EXTENDS_DEPTH):
    """Resolve the chain from `start_path` and produce the fully merged dict.

    Returns `(chain, merged_dict)` so callers (`extract_rules.py --explain`,
    `voice_lint.py`) can inspect the chain alongside the merged result.

    May raise `ExtendsError` on chain failures.
    """
    chain = resolve_extends_chain(start_path, max_depth)
    merged = None
    for _, data in chain:
        merged = merge_voice_dicts(merged, data)
        merged = apply_replace_overrides(merged)
        merged = apply_remove_overrides(merged)
    return chain, merged or {}


def compute_provenance(chain, merged):
    """Per-item origin attribution for `--explain` output.

    Returns a dict where each tracked field maps to either:
      - a dict `{item_key: source_relpath}` for list-typed fields, or
      - a string `source_relpath` for object-typed fields.

    `item_key` is the literal string for list-of-strings, or `(id_field, value)`
    tuple for list-of-objects.
    """
    if not chain:
        return {}

    list_fields = ("forbidden_lexicon", "required_lexicon", "forbidden_patterns")
    keyed_list_fields = {"rewrite_rules": "rule_id", "core_attributes": "attribute_id"}
    object_fields = ("sentence_norms", "contexts", "pronouns")

    def _item_key(field, item):
        if field in keyed_list_fields and isinstance(item, dict):
            id_field = keyed_list_fields[field]
            v = item.get(id_field)
            if isinstance(v, str):
                return (id_field, v)
            if field == "core_attributes":
                nm = item.get("name")
                if isinstance(nm, str):
                    return ("name-norm", " ".join(nm.lower().split()))
        return item

    prov = {}

    # Scalar list / keyed list: walk chain in order, last-write-wins per key
    for f in list_fields + tuple(keyed_list_fields):
        per_item = {}
        for path, data in chain:
            relpath = path.name
            replace_value = data.get(f"{f}_replace")
            if isinstance(replace_value, list):
                per_item = {_item_key(f, x): relpath for x in replace_value}
            canonical = data.get(f)
            if isinstance(canonical, list):
                for item in canonical:
                    per_item[_item_key(f, item)] = relpath
            remove_value = data.get(f"{f}_remove")
            if isinstance(remove_value, list):
                if f in keyed_list_fields:
                    id_field = keyed_list_fields[f]
                    targets = {(id_field, x) for x in remove_value if isinstance(x, str)}
                    if f == "core_attributes":
                        targets |= {("name-norm", " ".join(x.lower().split()))
                                    for x in remove_value if isinstance(x, str)}
                    per_item = {k: v for k, v in per_item.items() if k not in targets}
                else:
                    targets = {x for x in remove_value if isinstance(x, str)}
                    per_item = {k: v for k, v in per_item.items() if k not in targets}

        # Filter to keys that survived in `merged`
        surviving = set()
        for item in (merged.get(f) or []):
            surviving.add(_item_key(f, item))
        prov[f] = {k: v for k, v in per_item.items() if k in surviving}

    # Object fields — last file that declared canonical or `_replace` wins
    for f in object_fields:
        latest = None
        for path, data in chain:
            if data.get(f) is not None or data.get(f"{f}_replace") is not None:
                latest = path.name
        if latest is not None and merged.get(f):
            prov[f] = latest

    return prov
