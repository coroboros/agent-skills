"""Capability sub-graph extractor.

Parses the README for capability lists (Features, Commands, Skills,
Workstreams). For each item, attempts to resolve a supporting reference —
a file/path, a function/class name, or a flag with an argparse equivalent.
An item with zero references surfaces as one finding.
"""

from __future__ import annotations

import re
from pathlib import Path

from ._common import Finding, IgnoreFile

CAPABILITY_HEADERS = ("features", "commands", "skills", "workstreams")
HEADER_RE = re.compile(r"^(#{2,4})\s+(.+?)\s*$", re.MULTILINE)
LIST_ITEM_RE = re.compile(r"^\s*[-*+]\s+(.+?)\s*$", re.MULTILINE)
FLAG_RE = re.compile(r"^(--?[a-zA-Z][a-zA-Z0-9_-]*)\b")


def _parse_capabilities(readme: Path) -> list[tuple[str, str]]:
    """Return [(section_title, item), ...] under capability-shaped headers."""
    if not readme.exists():
        return []
    try:
        text = readme.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    capabilities: list[tuple[str, str]] = []
    sections = list(HEADER_RE.finditer(text))
    for idx, m in enumerate(sections):
        title = m.group(2).strip().lower()
        if title not in CAPABILITY_HEADERS:
            continue
        body_start = m.end()
        body_end = sections[idx + 1].start() if idx + 1 < len(sections) else len(text)
        body = text[body_start:body_end]
        for item_m in LIST_ITEM_RE.finditer(body):
            raw = item_m.group(1).strip()
            label = raw.split(":", 1)[0].split("—", 1)[0].split(" - ", 1)[0]
            label = label.strip().strip("`").strip("*").strip()
            if label:
                capabilities.append((title, label))
    return capabilities


def _resolve(repo: Path, item: str) -> bool:
    token = item.strip().strip("`")
    if not token:
        return False

    flag_m = FLAG_RE.match(token)
    if flag_m:
        return _resolve_flag(repo, flag_m.group(1))

    if "/" in token or token.endswith((".py", ".ts", ".js", ".md", ".sh")):
        return _resolve_path(repo, token)

    return _resolve_path(repo, token) or _resolve_symbol(repo, token)


def _resolve_path(repo: Path, token: str) -> bool:
    direct = repo / token
    if direct.exists():
        return True
    matches = list(repo.glob(f"**/{token}"))
    if matches:
        return True
    matches = list(repo.glob(f"**/*{token}*"))
    return bool(matches)


def _resolve_symbol(repo: Path, token: str) -> bool:
    safe = re.escape(token)
    patterns = (
        rf"def\s+{safe}\b",
        rf"class\s+{safe}\b",
        rf"function\s+{safe}\b",
        rf"const\s+{safe}\b",
        rf"export\s+(default\s+)?(class|function|const)?\s*{safe}\b",
    )
    for root in (repo / "src", repo / "scripts", repo / "skills", repo / "lib"):
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in (".py", ".ts", ".tsx", ".js", ".jsx", ".sh"):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for pattern in patterns:
                if re.search(pattern, text):
                    return True
    return False


def _resolve_flag(repo: Path, flag: str) -> bool:
    safe = re.escape(flag)
    patterns = (
        rf'["\']{safe}["\']',
        rf'add_argument\(\s*["\']{safe}["\']',
        rf'\b{safe}\b\)',
    )
    for root in (repo / "src", repo / "scripts", repo / "skills"):
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in (".py", ".ts", ".js", ".sh"):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for pattern in patterns:
                if re.search(pattern, text):
                    return True
    return False


def run(repo: Path, ignore: IgnoreFile, **_) -> list[Finding]:
    findings: list[Finding] = []
    capabilities = _parse_capabilities(repo / "README.md")
    ignored = set(ignore.list_for("capability", "ignore_items"))
    for section, item in capabilities:
        if item in ignored:
            continue
        if _resolve(repo, item):
            continue
        findings.append(Finding(
            sub_graph="capability",
            severity="Medium",
            location=f"README.md § {section}",
            finding=f"README lists capability {item!r} with no supporting reference in the repo.",
            recommendation=(
                "Implement the capability, remove the README mention, "
                "or allowlist it in `.coherence-ignore` under `capability.ignore_items`."
            ),
            confidence=70,
        ))
    return findings
