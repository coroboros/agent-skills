#!/usr/bin/env python3
"""audit_extensions.py — bidirectional drift check between DESIGN.md extension YAML,
prose references, and the globals.css @theme block.

Self-contained: no third-party dependencies. Parses only what it needs from YAML
(top-level extension namespaces with map-of-strings shape per the Google spec
extension convention) and CSS (@theme block custom properties).

Reference: skills/design-system/references/extended-tokens.md
           skills/design-system/references/subcommand-audit-extensions.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

EXTENSION_NAMESPACES = (
    "motion",
    "shadows",
    "aspectRatios",
    "heights",
    "containers",
    "breakpoints",
    "zIndex",
    "borderWidths",
    "opacity",
    "scrollTriggers",
)

NAMESPACE_TO_CSS_PREFIX = {
    "shadows": "--shadow-",
    "aspectRatios": "--aspect-",
    "heights": "--height-",
    "containers": "--container-",
    "breakpoints": "--breakpoint-",
    "zIndex": "--z-",
    "borderWidths": "--border-",
    "opacity": "--opacity-",
    "scrollTriggers": "--scroll-",
}

MOTION_PREFIXES = ("--duration-", "--ease-")

CSS_PROBE_ORDER = (
    "src/app/globals.css",
    "src/styles/globals.css",
    "src/style.css",
    "app/globals.css",
    "src/app/global.css",
)


def split_frontmatter(text):
    """Return (frontmatter_text, body_text, body_line_offset).

    body_line_offset is the 1-indexed line number on which body line 1 sits in
    the original file — used to report file-line numbers for prose findings.
    """
    if not text.startswith("---\n"):
        return None, text, 1
    end = text.find("\n---", 4)
    if end < 0:
        return None, text, 1
    after = end + 4
    if after < len(text) and text[after] == "\n":
        after += 1
    fm = text[4:end]
    body = text[after:]
    # Count newlines in everything before the body to compute the file-line offset
    body_line_offset = text[:after].count("\n") + 1
    return fm, body, body_line_offset


def parse_yaml_extensions(yaml_text):
    """Extract extension namespaces from YAML frontmatter.

    Returns a dict[namespace] = dict[token-name] = raw-value-string.

    Constrained parser: handles only top-level keys whose value is a flat map of
    strings (the spec's map-of-strings extension convention). Two-space indent.
    Skips comments and blank lines. Ignores quoting on values (preserves verbatim).
    """
    extensions = {}
    lines = yaml_text.splitlines()
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.split("#", 1)[0].rstrip()
        if not stripped:
            i += 1
            continue
        m = re.match(r"^([a-zA-Z][a-zA-Z0-9_]*):\s*$", line)
        if m and m.group(1) in EXTENSION_NAMESPACES:
            ns = m.group(1)
            extensions[ns] = {}
            i += 1
            while i < n:
                child = lines[i]
                child_stripped = child.split("#", 1)[0].rstrip()
                if not child_stripped:
                    i += 1
                    continue
                if not child.startswith("  "):
                    break
                cm = re.match(r"^  ([a-zA-Z][a-zA-Z0-9_-]*):\s*(.*)$", child)
                if cm:
                    extensions[ns][cm.group(1)] = cm.group(2).strip()
                    i += 1
                else:
                    break
        else:
            i += 1
    return extensions


def yaml_token_to_css_var(namespace, token_name):
    """Map (namespace, token-name) → CSS custom property name."""
    if namespace == "motion":
        return f"--{token_name}"
    prefix = NAMESPACE_TO_CSS_PREFIX[namespace]
    return f"{prefix}{token_name}"


def parse_css_theme(css_text):
    """Extract --custom-property: value pairs from @theme blocks.

    Handles multiple @theme blocks (Tailwind v4 allows multiple), respects nested
    braces shallowly (the @theme body has no nested blocks in practice).
    """
    properties = {}
    i = 0
    n = len(css_text)
    while i < n:
        idx = css_text.find("@theme", i)
        if idx < 0:
            break
        brace = css_text.find("{", idx)
        if brace < 0:
            break
        depth = 1
        j = brace + 1
        while j < n and depth > 0:
            ch = css_text[j]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            j += 1
        body = css_text[brace + 1 : j - 1]
        body = re.sub(r"/\*.*?\*/", "", body, flags=re.DOTALL)
        for raw_line in body.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            m = re.match(r"^(--[a-zA-Z0-9_-]+)\s*:\s*(.+?);?\s*$", line)
            if m:
                properties[m.group(1)] = m.group(2).strip()
        i = j
    return properties


def find_prose_references(body_text, line_offset=1):
    """Extract token references to extension namespaces from prose.

    Two forms:
      - Braced: {namespace.token-name}
      - Backticked bare: `namespace.token-name`

    Returns a list of (namespace, token-name, file_line_number).
    `line_offset` is the file line on which body line 1 sits.
    """
    refs = []
    in_fence = False
    pattern_braced = re.compile(r"\{([a-zA-Z][a-zA-Z0-9_]*)\.([a-zA-Z][a-zA-Z0-9_-]*)\}")
    pattern_backtick = re.compile(r"`([a-zA-Z][a-zA-Z0-9_]*)\.([a-zA-Z][a-zA-Z0-9_-]*)`")
    for body_lineno, line in enumerate(body_text.splitlines(), start=0):
        file_lineno = line_offset + body_lineno
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for m in pattern_braced.finditer(line):
            ns = m.group(1)
            if ns in EXTENSION_NAMESPACES:
                refs.append((ns, m.group(2), file_lineno))
        for m in pattern_backtick.finditer(line):
            ns = m.group(1)
            if ns in EXTENSION_NAMESPACES:
                refs.append((ns, m.group(2), file_lineno))
    return refs


def find_globals_css(start_dir):
    start = Path(start_dir).resolve()
    for candidate in CSS_PROBE_ORDER:
        p = start / candidate
        if p.is_file():
            return p
    return None


def expected_css_prefixes(extensions):
    prefixes = set()
    for ns in extensions:
        if ns == "motion":
            prefixes.update(MOTION_PREFIXES)
        elif ns in NAMESPACE_TO_CSS_PREFIX:
            prefixes.add(NAMESPACE_TO_CSS_PREFIX[ns])
    return prefixes


def audit(design_path, css_path, strict=False):
    text = design_path.read_text(encoding="utf-8")
    fm, body, body_line_offset = split_frontmatter(text)
    if fm is None:
        return {
            "status": "no-frontmatter",
            "summary": {"errors": 0, "warnings": 0, "infos": 0},
            "findings": {"errors": [], "warnings": [], "infos": []},
        }

    extensions = parse_yaml_extensions(fm)
    css_text = css_path.read_text(encoding="utf-8")
    css_props = parse_css_theme(css_text)

    findings = {"errors": [], "warnings": [], "infos": []}

    yaml_css_vars = set()
    for ns, tokens in extensions.items():
        for token_name in tokens:
            css_var = yaml_token_to_css_var(ns, token_name)
            yaml_css_vars.add(css_var)
            if css_var not in css_props:
                findings["errors"].append({
                    "rule": "extension-missing-css",
                    "namespace": ns,
                    "token": token_name,
                    "expected_css": css_var,
                    "message": (
                        f"YAML defines `{ns}.{token_name}` but `{css_var}` "
                        f"is missing from globals.css @theme"
                    ),
                })

    prefixes = expected_css_prefixes(extensions)
    for css_var in sorted(css_props):
        if any(css_var.startswith(p) for p in prefixes):
            if css_var not in yaml_css_vars:
                level = "errors" if strict else "warnings"
                findings[level].append({
                    "rule": "extension-orphan-css",
                    "css_var": css_var,
                    "message": (
                        f"`{css_var}` exists in globals.css @theme but no "
                        f"matching YAML extension token"
                    ),
                })

    refs = find_prose_references(body, line_offset=body_line_offset)
    for ns, token_name, lineno in refs:
        if ns not in extensions:
            findings["errors"].append({
                "rule": "extension-broken-ref",
                "namespace": ns,
                "token": token_name,
                "line": lineno,
                "message": (
                    f"Prose references `{ns}.{token_name}` (line {lineno}) "
                    f"but namespace `{ns}` not defined in YAML"
                ),
            })
        elif token_name not in extensions[ns]:
            findings["errors"].append({
                "rule": "extension-broken-ref",
                "namespace": ns,
                "token": token_name,
                "line": lineno,
                "message": (
                    f"Prose references `{ns}.{token_name}` (line {lineno}) "
                    f"but token not defined under `{ns}:` YAML"
                ),
            })

    return {
        "status": "ok",
        "extensions_found": sorted(extensions.keys()),
        "summary": {
            "errors": len(findings["errors"]),
            "warnings": len(findings["warnings"]),
            "infos": len(findings["infos"]),
        },
        "findings": findings,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Drift check between DESIGN.md extension YAML, "
                    "prose references, and globals.css @theme."
    )
    parser.add_argument("path", help="Path to DESIGN.md")
    parser.add_argument("--css", help="Path to globals.css (auto-detected if omitted)")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Promote orphan warnings to errors",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args(argv)

    design_path = Path(args.path)
    if not design_path.is_file():
        print("RESULT: status=file-not-found")
        print(f"RESULT: path={args.path}")
        return 1

    if args.css:
        css_path = Path(args.css)
        if not css_path.is_file():
            print("RESULT: status=css-not-found")
            print(f"RESULT: css-path={args.css}")
            return 1
    else:
        css_path = find_globals_css(design_path.parent)
        if css_path is None:
            print("RESULT: status=css-not-found")
            print(f"RESULT: search-root={design_path.parent.resolve()}")
            return 1

    result = audit(design_path, css_path, strict=args.strict)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"RESULT: status={result['status']}")
        print(f"RESULT: path={design_path}")
        print(f"RESULT: css={css_path}")
        if result["status"] == "ok":
            print(f"RESULT: extensions={','.join(result['extensions_found']) or '(none)'}")
            print(f"RESULT: errors={result['summary']['errors']}")
            print(f"RESULT: warnings={result['summary']['warnings']}")
            print(f"RESULT: infos={result['summary']['infos']}")
            for level in ("errors", "warnings", "infos"):
                for f in result["findings"][level]:
                    print(f"FINDING: level={level} rule={f['rule']} {f['message']}")

    return 1 if result.get("summary", {}).get("errors", 0) else 0


if __name__ == "__main__":
    sys.exit(main())
