"""Version sub-graph extractor.

Compares version sources across:
    - package.json.version
    - .claude-plugin/marketplace.json.metadata.version
    - CHANGELOG.md most recent `^## [vV]?\\d+\\.\\d+\\.\\d+` header
    - `git tag -l --sort=-v:refname | head -1`
    - `gh release list -L 1 --json tagName`
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

from ._common import Finding, IgnoreFile, normalize_version, read_json_safe

CHANGELOG_HEADER_RE = re.compile(r"^##\s+\[?v?(\d+\.\d+\.\d+)", re.MULTILINE)
GH_TIMEOUT_S = 5


def _from_package_json(repo: Path) -> str | None:
    data = read_json_safe(repo / "package.json")
    if isinstance(data, dict) and isinstance(data.get("version"), str):
        return data["version"]
    return None


def _from_marketplace_json(repo: Path) -> str | None:
    data = read_json_safe(repo / ".claude-plugin" / "marketplace.json")
    if isinstance(data, dict):
        meta = data.get("metadata") or {}
        if isinstance(meta, dict) and isinstance(meta.get("version"), str):
            return meta["version"]
    return None


def _from_changelog(repo: Path) -> str | None:
    p = repo / "CHANGELOG.md"
    if not p.exists():
        return None
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    m = CHANGELOG_HEADER_RE.search(text)
    return m.group(1) if m else None


def _from_git_tag(repo: Path) -> str | None:
    if not (repo / ".git").exists():
        return None
    try:
        r = subprocess.run(
            ["git", "-C", str(repo), "tag", "-l", "--sort=-v:refname"],
            capture_output=True, text=True, timeout=10,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    if r.returncode != 0:
        return None
    for line in r.stdout.splitlines():
        line = line.strip()
        if line and re.match(r"^v?\d+\.\d+\.\d+", line):
            return line
    return None


def _from_gh_release(repo: Path) -> str | None:
    if os.environ.get("COHERENCE_SKIP_GH") or not shutil.which("gh"):
        return None
    try:
        r = subprocess.run(
            ["gh", "release", "list", "-L", "1", "--json", "tagName",
             "-q", ".[0].tagName"],
            cwd=repo, capture_output=True, text=True, timeout=GH_TIMEOUT_S,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    if r.returncode != 0:
        return None
    name = r.stdout.strip()
    return name or None


def collect_sources(repo: Path) -> list[tuple[str, str]]:
    candidates = [
        ("package.json", _from_package_json(repo)),
        ("marketplace.json", _from_marketplace_json(repo)),
        ("CHANGELOG.md", _from_changelog(repo)),
        ("git-tag", _from_git_tag(repo)),
        ("gh-release", _from_gh_release(repo)),
    ]
    return [(name, value) for name, value in candidates if value]


def run(repo: Path, ignore: IgnoreFile, **_) -> list[Finding]:
    sources = collect_sources(repo)
    findings: list[Finding] = []
    for i, (a_id, a_val) in enumerate(sources):
        for j in range(i + 1, len(sources)):
            b_id, b_val = sources[j]
            if ignore.has("version", "ignore_pairs", f"{a_id}:{b_id}") or \
                    ignore.has("version", "ignore_pairs", f"{b_id}:{a_id}"):
                continue
            if normalize_version(a_val) == normalize_version(b_val):
                continue
            findings.append(Finding(
                sub_graph="version",
                severity="High",
                location=f"{a_id} ↔ {b_id}",
                finding=f"Version divergence: {a_id} = {a_val!r}; {b_id} = {b_val!r}",
                recommendation="Bump the lagging source to the canonical version.",
                confidence=95,
            ))
    return findings
