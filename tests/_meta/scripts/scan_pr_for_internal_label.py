#!/usr/bin/env python3
"""Scan a PR's title and body for internal-label patterns.

Reads `{"title": "...", "body": "..."}` JSON from stdin (the shape
`gh pr view --json title,body` emits). Exits 0 if clean; exits 1 with
hit details on stderr; exits 2 on stdin / JSON errors.

CI invocation (`.github/workflows/ci.yml`):

    gh pr view <N> --json title,body | python3 tests/_meta/scripts/scan_pr_for_internal_label.py

The pattern catalog and per-line opt-out are imported from
`tests/_meta/_internal_label_patterns.py` so this script and
`test_no_internal_label_leak.py` cannot drift.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _internal_label_patterns import scan_line  # noqa: E402


def scan_pr(title: str, body: str) -> list[str]:
    """Return human-readable hit lines for the given title and body."""
    hits: list[str] = []
    for name, matched, hint in scan_line(title or ""):
        hits.append(f"PR title — {name}: {matched!r}\n  Hint: {hint}")
    for lineno, line in enumerate((body or "").splitlines(), 1):
        for name, matched, hint in scan_line(line):
            hits.append(
                f"PR body:line {lineno} — {name}: {matched!r}\n  Hint: {hint}"
            )
    return hits


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(
            f"scan_pr_for_internal_label: invalid JSON on stdin — {exc}",
            file=sys.stderr,
        )
        return 2
    title = payload.get("title") or ""
    body = payload.get("body") or ""
    hits = scan_pr(title, body)
    if hits:
        joined = "\n".join(hits)
        print(
            f"Internal-label leak in PR ({len(hits)} hit(s)):\n\n{joined}\n\n"
            f"Per-line opt-out: append `<!-- noqa: internal-label -->` on the same line.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
