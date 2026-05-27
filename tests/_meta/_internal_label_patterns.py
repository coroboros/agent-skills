"""Shared catalog of internal-label patterns.

Consumed by:
- `tests/_meta/test_no_internal_label_leak.py` — file-tree scan of shipped skill source.
- `tests/_meta/scripts/scan_pr_for_internal_label.py` — PR title + body scan in CI.

One source of truth keeps the two gates in lockstep — a pattern added here is
enforced everywhere.
"""

from __future__ import annotations

import re
from collections.abc import Iterator

PATTERNS: tuple[tuple[re.Pattern[str], str, str], ...] = (
    (
        re.compile(r"\bWS-[1-9][0-9]?\b"),
        "workstream label (WS-N)",
        "Translate to a domain fact — what the change actually does.",
    ),
    # Scope to script extensions only — `the prior <thing>.md` is legitimately
    # used by skills that version a user's `.md` file (e.g., suno-produce
    # archives `TRACK.md` to `versions/`).
    (
        re.compile(r"the prior `?[A-Za-z_][A-Za-z0-9_/]*\.(?:py|sh|bash)`?"),
        "rebuild-history breadcrumb (the prior <script>)",
        "Describe the current state, not the file it replaced.",
    ),
    (
        re.compile(r"carried verbatim from\b"),
        "rebuild-history phrasing (carried verbatim from)",
        "Describe what the code does now, not its lineage.",
    ),
    (
        re.compile(r"\bthe rebuild\b", re.IGNORECASE),
        "process language (the rebuild)",
        "Describe the architecture as it stands, not the path that got it here.",
    ),
    # `spec AC` standalone is a leak. `Spec AC closure` is a named apex
    # feature — the negative lookahead permits it. IGNORECASE catches the
    # capital-S variant the original case-sensitive regex missed.
    (
        re.compile(r"\bspec AC\b(?! closure)", re.IGNORECASE),
        "spec-process vocabulary (spec AC)",
        "Describe the check directly — what is verified, not the spec section that asks for it.",
    ),
)

# Per-line opt-out. Both `#`-style (Python / shell / YAML) and `<!--`-style
# (Markdown) comments recognised.
INLINE_OPT_OUT = re.compile(r"(?:#|<!--)\s*noqa:\s*internal-label\b")


def scan_line(line: str) -> Iterator[tuple[str, str, str]]:
    """Yield `(pattern_name, matched_text, hint)` for each pattern hit on `line`.

    Honors per-line `<!-- noqa: internal-label -->` / `# noqa: internal-label`.
    Stops at the first hit per line so both consumers report identically.
    """
    if INLINE_OPT_OUT.search(line):
        return
    for regex, name, hint in PATTERNS:
        match = regex.search(line)
        if match:
            yield (name, match.group(0), hint)
            return
