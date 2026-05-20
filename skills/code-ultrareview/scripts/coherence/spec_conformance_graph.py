"""Spec-conformance sub-graph entrypoint stub.

Detects normative-spec mentions in README/CLAUDE.md and emits a deferred
placeholder finding. Full spec-conformance verification (WebFetch + 7-day
ETag cache + grammar inference) runs in the always-on spec-conformance
pass — see `references/ultra-execution.md`.
"""

from __future__ import annotations

import re
from pathlib import Path

from ._common import Finding, IgnoreFile

SPEC_REGEX = re.compile(
    r"\b(RFC\s?\d+|WHATWG|ISO/IEC\s?\d+|OpenAPI|IETF)\b"
)


def _detect_specs(repo: Path) -> list[str]:
    found: set[str] = set()
    for candidate in ("README.md", "CLAUDE.md"):
        p = repo / candidate
        if not p.exists():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        found.update(SPEC_REGEX.findall(text))
    return sorted(found)


def run(repo: Path, ignore: IgnoreFile, **_) -> list[Finding]:
    specs = _detect_specs(repo)
    if not specs:
        return []
    ignored = set(ignore.list_for("spec-conformance", "ignore_specs"))
    surfaced = [s for s in specs if s not in ignored]
    if not surfaced:
        return []
    return [Finding(
        sub_graph="spec-conformance",
        severity="Low",
        location="(repo)",
        finding=(
            f"Normative spec mention(s) detected: {', '.join(surfaced)}. "
            "Spec-conformance verification (fetch + quote + diff) runs in the dedicated spec-conformance pass."
        ),
        recommendation="The spec-conformance pass fetches the spec, quotes the governing clause, and diffs the code against it.",
        confidence=50,
    )]
