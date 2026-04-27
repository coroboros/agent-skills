#!/usr/bin/env python3
"""
lint_all.py — lint every BRAND-VOICE*.md under a root directory.

Use case: a parent BRAND-VOICE.md change can silently regress every child file
that declares `voice.extends`. Running this script in CI surfaces the breakage
on the children, with `source_path` pointing at the offending parent.

Usage:
    lint_all.py                    # current working directory
    lint_all.py <root>             # custom root
    lint_all.py --json             # raw JSON results (one per file)

Exit:
    0  every file passes (GREEN or YELLOW)
    1  at least one file is RED
    2  no BRAND-VOICE*.md files found under <root>

Requires Python 3.7+. No third-party dependencies.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import read_text  # noqa: E402
from voice_lint import lint  # noqa: E402


_DEFAULT_PATTERNS = ("BRAND-VOICE.md", "BRAND-VOICE-*.md")


def _discover(root):
    seen = set()
    out = []
    for pattern in _DEFAULT_PATTERNS:
        for p in sorted(root.rglob(pattern)):
            r = p.resolve()
            if r in seen:
                continue
            seen.add(r)
            out.append(p)
    return out


def _lint_file(path, allow_outside_skill):
    try:
        text = read_text(str(path))
    except (FileNotFoundError, OSError, UnicodeDecodeError) as exc:
        return {
            "path": str(path),
            "verdict": "RED",
            "errors": [{"code": "io-error", "field": None, "message": str(exc), "line": 0}],
            "warnings": [],
            "stats": {},
        }
    return lint(text, str(path), allow_outside_skill=allow_outside_skill)


def main():
    parser = argparse.ArgumentParser(
        description="Lint every BRAND-VOICE*.md under a root directory.",
        prog="lint_all.py",
    )
    parser.add_argument("root", nargs="?", default=".", help="root directory (default: CWD)")
    parser.add_argument("--json", action="store_true", help="emit raw JSON results")
    parser.add_argument(
        "--allow-extends-outside-skill", action="store_true",
        help="suppress 'extends-path-outside-skill' warning",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"error: '{root}' is not a directory", file=sys.stderr)
        return 2

    files = _discover(root)
    if not files:
        print(f"error: no BRAND-VOICE*.md files found under '{root}'", file=sys.stderr)
        return 2

    results = [_lint_file(p, args.allow_extends_outside_skill) for p in files]

    if args.json:
        sys.stdout.write(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
    else:
        worst = "GREEN"
        for r in results:
            v = r["verdict"]
            errs = len(r.get("errors") or [])
            warns = len(r.get("warnings") or [])
            chain = r.get("chain") or []
            chain_label = f"  ← {len(chain) - 1} parent" + ("s" if len(chain) - 1 != 1 else "") if len(chain) > 1 else ""
            print(f"{v:6}  {r['path']}  ({errs} errors, {warns} warnings){chain_label}")
            if v == "RED":
                worst = "RED"
                for e in (r.get("errors") or [])[:5]:
                    src = f" [{e.get('source')}]" if e.get("source") else ""
                    print(f"        ✗ {e['code']}{src}: {e['message']}")
                if len(r.get("errors") or []) > 5:
                    print(f"        … and {len(r['errors']) - 5} more — run /brand-voice validate {r['path']} for full report")
            elif v == "YELLOW" and worst == "GREEN":
                worst = "YELLOW"
        print()
        print(f"summary: {len(results)} file(s); worst verdict: {worst}")

    any_red = any(r["verdict"] == "RED" for r in results)
    return 1 if any_red else 0


if __name__ == "__main__":
    sys.exit(main())
