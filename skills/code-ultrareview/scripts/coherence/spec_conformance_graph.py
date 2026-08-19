"""Spec-conformance sub-graph entrypoint stub.

Detects normative-spec mentions in the README and project instructions, then emits a deferred
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


def _read_content(path: Path) -> str | None:
    if not path.is_file():
        return None
    try:
        body = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    return body if body.strip() else None


def _instruction_candidates(repo: Path) -> list[Path]:
    candidates: list[Path] = []
    agents_body: str | None = None
    override = repo / "AGENTS.override.md"
    agents = repo / "AGENTS.md"
    override_body = _read_content(override)
    agents_fallback_body = _read_content(agents)
    if override_body is not None:
        candidates.append(override)
        agents_body = override_body
    elif agents_fallback_body is not None:
        candidates.append(agents)
        agents_body = agents_fallback_body

    for relative in ("CLAUDE.md", ".claude/CLAUDE.md", "CLAUDE.local.md"):
        candidate = repo / relative
        if _read_content(candidate) is not None:
            candidates.append(candidate)

    rule_dirs = [repo / ".claude" / "rules"]
    if agents_body and re.search(r"(?:~/)?\.agents/rules(?:/|\b)", agents_body):
        rule_dirs.insert(0, repo / ".agents" / "rules")
    for rules_dir in rule_dirs:
        if rules_dir.is_dir():
            candidates.extend(
                path
                for path in sorted(rules_dir.rglob("*.md"))
                if _read_content(path) is not None
            )
    return candidates


def _detect_specs(repo: Path) -> list[str]:
    found: set[str] = set()
    for p in [repo / "README.md", *_instruction_candidates(repo)]:
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
