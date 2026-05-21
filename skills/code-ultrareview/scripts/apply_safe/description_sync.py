"""Description-sync writer for --apply-safe.

Aligns structured description fields under a strict **full-agreement
guard**: write the new value only when every present source already
agrees on the new value. Partial agreement → refuses with
`refusing: partial-agreement` and exits 1.

The guard is the Risk #3 mitigation — auto-fixing descriptions when
sources disagree could overwrite a deliberate divergence. Use
`.coherence-ignore` to whitelist legitimate divergences instead.
"""

from __future__ import annotations

import json
from pathlib import Path

from ._common import confirm_write, unified_diff_block

DESCRIPTION_FILES = (
    "package.json",
    ".claude-plugin/marketplace.json",
)


def _read_description(repo: Path, relpath: str) -> str | None:
    p = repo / relpath
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    if isinstance(data.get("description"), str):
        return data["description"]
    meta = data.get("metadata") or {}
    if isinstance(meta, dict) and isinstance(meta.get("description"), str):
        return meta["description"]
    return None


def _write_description(repo: Path, relpath: str, new_value: str) -> str:
    p = repo / relpath
    data = json.loads(p.read_text(encoding="utf-8"))
    if "description" in data:
        data["description"] = new_value
    elif isinstance(data.get("metadata"), dict) and "description" in data["metadata"]:
        data["metadata"]["description"] = new_value
    after = json.dumps(data, indent=2) + "\n"
    p.write_text(after, encoding="utf-8")
    return after


def collect_descriptions(repo: Path) -> list[tuple[str, str]]:
    """[(relpath, description), ...] for every description source present."""
    return [
        (relpath, value)
        for relpath in DESCRIPTION_FILES
        if (value := _read_description(repo, relpath)) is not None
    ]


def all_agree(entries: list[tuple[str, str]]) -> bool:
    """True when every present source has the same description value."""
    values = {v for _, v in entries}
    return len(values) <= 1


def sync(
    repo: Path,
    new_value: str | None = None,
    yes: bool = False,
) -> dict:
    """Apply description sync under the full-agreement guard.

    Args:
        new_value: the target description. If None, the function assumes the
            existing canonical value (all sources already agree) and is a
            no-op. If provided, every present source must already equal
            `new_value` — partial agreement refuses with status
            `refusing: partial-agreement`.
        yes: bypass per-file confirmation.

    Returns a summary dict.
    """
    entries = collect_descriptions(repo)
    if not entries:
        return {"status": "no-op", "reason": "no description sources found"}

    if new_value is None:
        if all_agree(entries):
            return {"status": "no-op", "reason": "all sources agree"}
        return {
            "status": "refusing: partial-agreement",
            "reason": "sources disagree and no canonical value was supplied",
            "values": dict(entries),
        }

    if not all(value == new_value for _, value in entries):
        return {
            "status": "refusing: partial-agreement",
            "reason": (
                "at least one source disagrees with the requested new value — "
                "the full-agreement guard forbids the write"
            ),
            "values": dict(entries),
            "requested": new_value,
        }

    # All sources already match `new_value` — write nothing, surface no-op.
    return {"status": "no-op", "reason": "all sources already match", "canonical": new_value}


def force_apply_when_agreed(
    repo: Path,
    new_value: str,
    yes: bool = False,
) -> dict:
    """Strong variant used when the orchestrator wants to overwrite *all*
    sources to a new value — only allowed when every source already shares
    a common (possibly different) value, per the full-agreement guard.

    Mirrors `sync` but writes when every existing source equals each other
    (even if they differ from `new_value`).
    """
    entries = collect_descriptions(repo)
    if not entries:
        return {"status": "no-op", "reason": "no description sources found"}
    if not all_agree(entries):
        return {
            "status": "refusing: partial-agreement",
            "reason": "sources disagree — the full-agreement guard forbids the write",
            "values": dict(entries),
            "requested": new_value,
        }
    applied: list[str] = []
    skipped: list[str] = []
    for relpath, _ in entries:
        abs_path = repo / relpath
        before = abs_path.read_text(encoding="utf-8")
        after = _preview_content(repo, relpath, new_value)
        if before == after:
            continue
        diff = unified_diff_block(abs_path, before, after)
        if confirm_write(abs_path, diff, yes=yes):
            _write_description(repo, relpath, new_value)
            applied.append(relpath)
        else:
            skipped.append(relpath)
    return {
        "status": "applied" if applied else "skipped",
        "canonical": new_value,
        "applied": applied,
        "skipped": skipped,
    }


def _preview_content(repo: Path, relpath: str, new_value: str) -> str:
    p = repo / relpath
    data = json.loads(p.read_text(encoding="utf-8"))
    if "description" in data:
        data["description"] = new_value
    elif isinstance(data.get("metadata"), dict) and "description" in data["metadata"]:
        data["metadata"]["description"] = new_value
    return json.dumps(data, indent=2) + "\n"
