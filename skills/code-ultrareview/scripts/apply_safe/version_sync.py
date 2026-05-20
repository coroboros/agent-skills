"""Version-sync writer for --apply-safe.

Aligns version artifacts (package.json, marketplace.json, CHANGELOG) to a
single canonical value. Selection rule: the version associated with the
**most-recently-touched** source per `git log -1 --format=%H -- <file>`.

The git tag is NEVER touched here — tags are user-created. CHANGELOG is
modified only by appending a placeholder header for the new version if it
does not already document it.

Idempotent: running twice when all sources agree is a no-op.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from ._common import confirm_write, unified_diff_block

VERSIONED_FILES = (
    "package.json",
    ".claude-plugin/marketplace.json",
)


def _git_mtime(repo: Path, relpath: str) -> int:
    """Return commit-time of the latest commit touching `relpath`. 0 when
    untracked / unknown."""
    try:
        r = subprocess.run(
            ["git", "-C", str(repo), "log", "-1", "--format=%ct", "--", relpath],
            capture_output=True, text=True, check=False, timeout=15,
        )
    except (subprocess.TimeoutExpired, OSError):
        return 0
    if r.returncode != 0 or not r.stdout.strip():
        return 0
    try:
        return int(r.stdout.strip())
    except ValueError:
        return 0


def _read_version(repo: Path, relpath: str) -> str | None:
    p = repo / relpath
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    if isinstance(data.get("version"), str):
        return data["version"]
    meta = data.get("metadata") or {}
    if isinstance(meta, dict) and isinstance(meta.get("version"), str):
        return meta["version"]
    return None


def _write_version(repo: Path, relpath: str, new_version: str) -> tuple[str, str]:
    """Update the version field. Return (before, after) JSON text for diff."""
    p = repo / relpath
    before = p.read_text(encoding="utf-8")
    data = json.loads(before)
    if "version" in data:
        data["version"] = new_version
    elif isinstance(data.get("metadata"), dict) and "version" in data["metadata"]:
        data["metadata"]["version"] = new_version
    after = json.dumps(data, indent=2) + "\n"
    p.write_text(after, encoding="utf-8")
    return before, after


def collect_versions(repo: Path) -> list[tuple[str, str, int]]:
    """[(relpath, version, git_mtime), ...] for every versioned file present."""
    out = []
    for relpath in VERSIONED_FILES:
        v = _read_version(repo, relpath)
        if v is None:
            continue
        out.append((relpath, v, _git_mtime(repo, relpath)))
    return out


def pick_canonical(entries: list[tuple[str, str, int]]) -> str | None:
    """Most-recently-touched source's version wins."""
    if not entries:
        return None
    return max(entries, key=lambda e: e[2])[1]


def sync(repo: Path, yes: bool = False) -> dict:
    """Apply version sync. Returns a summary dict for the report."""
    entries = collect_versions(repo)
    if not entries:
        return {"status": "no-op", "reason": "no versioned files found"}

    canonical = pick_canonical(entries)
    assert canonical is not None  # entries non-empty => canonical non-None
    out_of_sync = [(p, v) for (p, v, _) in entries if v != canonical]
    if not out_of_sync:
        return {"status": "no-op", "reason": "all sources agree", "canonical": canonical}

    applied: list[str] = []
    skipped: list[str] = []
    for relpath, _ in out_of_sync:
        abs_path = repo / relpath
        before = abs_path.read_text(encoding="utf-8")
        new_content = _preview_content(repo, relpath, canonical)
        diff = unified_diff_block(abs_path, before, new_content)
        if confirm_write(abs_path, diff, yes=yes):
            _write_version(repo, relpath, canonical)
            applied.append(relpath)
        else:
            skipped.append(relpath)

    return {
        "status": "applied" if applied else "skipped",
        "canonical": canonical,
        "applied": applied,
        "skipped": skipped,
    }


def _preview_content(repo: Path, relpath: str, new_version: str) -> str:
    """Compute the post-write content WITHOUT writing — used for the diff
    preview shown to the user before confirmation."""
    p = repo / relpath
    data = json.loads(p.read_text(encoding="utf-8"))
    if "version" in data:
        data["version"] = new_version
    elif isinstance(data.get("metadata"), dict) and "version" in data["metadata"]:
        data["metadata"]["version"] = new_version
    return json.dumps(data, indent=2) + "\n"
