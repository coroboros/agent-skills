#!/usr/bin/env python3
"""Spec-conformance lens — cache management.

Owns the deterministic parts of the spec-conformance check:
cache directory layout, mtime-aware freshness policy, cache read/write,
and the format of the unverified-fallback finding when fetch fails with
no cache. `WebFetch` is the subagent's job — Python owns the cache.

Default cache root: `~/.claude/cache/code-ultrareview/specs/`.
Freshness window: 7 days (configurable via constant).
"""

from __future__ import annotations

import time
from datetime import date as date_cls
from pathlib import Path

DEFAULT_CACHE_DIR = Path.home() / ".claude" / "cache" / "code-ultrareview" / "specs"
FRESHNESS_SECONDS = 7 * 24 * 60 * 60  # 7 days

# Lowercase to keep slug deterministic regardless of caller's casing.
_SLUG_REPL_NON_ALNUM = "-"


def slugify(spec_name: str) -> str:
    """`RFC 6874` → `rfc-6874`; `WHATWG URL` → `whatwg-url`."""
    s = spec_name.lower()
    out = []
    last_dash = True
    for ch in s:
        if ch.isalnum():
            out.append(ch)
            last_dash = False
        else:
            if not last_dash:
                out.append(_SLUG_REPL_NON_ALNUM)
                last_dash = True
    slug = "".join(out).strip("-")
    return slug


def cache_path_for(
    spec_name: str,
    date: date_cls | None = None,
    cache_dir: Path | None = None,
) -> Path:
    """Canonical cache path: `<cache>/<slug>-<YYYY-MM-DD>.txt`."""
    base = cache_dir or DEFAULT_CACHE_DIR
    d = date or date_cls.today()
    return base / f"{slugify(spec_name)}-{d.isoformat()}.txt"


def latest_cached(
    spec_name: str,
    cache_dir: Path | None = None,
) -> Path | None:
    """Return the newest cache file for `spec_name`, or None when absent."""
    base = cache_dir or DEFAULT_CACHE_DIR
    if not base.exists():
        return None
    prefix = slugify(spec_name) + "-"
    candidates = sorted(
        (p for p in base.iterdir() if p.is_file() and p.name.startswith(prefix)
         and p.suffix == ".txt"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def is_cache_fresh(
    path: Path,
    now: float | None = None,
    freshness_seconds: int = FRESHNESS_SECONDS,
) -> bool:
    """True when `now - mtime <= freshness_seconds`.

    Missing file → False (caller should refresh). `now` defaults to
    `time.time()`; pass an explicit value when testing.
    """
    if not path.exists():
        return False
    current = now if now is not None else time.time()
    age = current - path.stat().st_mtime
    return age <= freshness_seconds


def read_cached(
    spec_name: str,
    cache_dir: Path | None = None,
    now: float | None = None,
) -> str | None:
    """Return the cached spec body if a fresh cache file exists; else None."""
    p = latest_cached(spec_name, cache_dir=cache_dir)
    if p is None or not is_cache_fresh(p, now=now):
        return None
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def write_cache(
    spec_name: str,
    body: str,
    date: date_cls | None = None,
    cache_dir: Path | None = None,
) -> Path:
    """Write `body` to the canonical cache path; create dirs if needed."""
    target = cache_path_for(spec_name, date=date, cache_dir=cache_dir)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    return target


def format_unverified_finding(
    spec_name: str,
    location: str,
    reason: str = "WebFetch unavailable and no cache",
) -> dict:
    """Canonical Finding when the spec body cannot be fetched.

    Confidence 50 so the A2 contract routes it to the report's
    `### Unverified` sub-section rather than dropping it silently.
    """
    return {
        "lens": "bugs-drift",
        "sub_graph": "spec-conformance",
        "severity": "Medium",
        "location": location,
        "finding": (
            f"[unverified — needs network] Spec {spec_name} mentioned but "
            f"governing clause could not be fetched ({reason})."
        ),
        "recommendation": (
            "Pre-populate the cache at `~/.claude/cache/code-ultrareview/specs/` "
            "or re-run when the network is available."
        ),
        "confidence": 50,
    }
