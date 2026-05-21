#!/usr/bin/env python3
"""A1 spec-claim trigger helper.

When the diff, README, or CLAUDE.md cites a named normative spec, the
bugs-drift lens fetches the spec via `WebFetch` (Claude Code tool), quotes
the governing clause verbatim, and emits a Finding with confidence ≥80.

This module owns the deterministic parts of A1:
    - detection (regex matching, same alphabet as audit_signals.py)
    - finding formatting (canonical Finding shape with the quoted clause)
    - cache-path helper

The `WebFetch` call itself is the subagent's responsibility — it lives in
the Claude Code runtime, not Python. Subagents call `trigger_a1_finding()`
after WebFetch returns the spec body and after they've located the
divergent code in the diff.

References:
    `references/lenses.md` → Lens 2 → A1.
    `references/aggregation.md` → A1 — spec-claim triggering.
"""

from __future__ import annotations

import re
from pathlib import Path

SPEC_REGEX = re.compile(
    r"\b(RFC\s?\d+|WHATWG|ISO/IEC\s?\d+|OpenAPI|IETF)\b"
)
SPEC_CACHE_DIR = Path.home() / ".claude" / "cache" / "code-ultrareview" / "specs"
A1_CONFIDENCE = 85


def detect_specs(text: str) -> list[str]:
    """Return sorted unique normative-spec mentions in `text`."""
    return sorted(set(SPEC_REGEX.findall(text)))


def cache_path(spec_slug: str, date_str: str) -> Path:
    """Canonical cache path for a fetched spec body.

    `spec_slug` is the kebab form of the spec name (e.g. `rfc-6874`);
    `date_str` is `YYYY-MM-DD` (the WebFetch run's date).
    """
    return SPEC_CACHE_DIR / f"{spec_slug}-{date_str}.txt"


def slugify_spec(spec_name: str) -> str:
    """`RFC 6874` → `rfc-6874`; `WHATWG URL` → `whatwg-url`."""
    s = spec_name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def trigger_a1_finding(
    spec_name: str,
    spec_excerpt: str,
    diff_excerpt: str,
    location: str,
) -> dict:
    """Build the canonical A1 finding.

    Args:
        spec_name: Human-readable spec name (e.g. `RFC 6874`).
        spec_excerpt: Verbatim governing clause from the fetched spec.
        diff_excerpt: The relevant code excerpt from the diff that
            diverges from the clause.
        location: `file:line` of the divergence.

    Returns:
        A dict matching the canonical Finding shape with confidence 85
        and the spec quote in the recommendation. Subagents pass this
        through unchanged.
    """
    if not spec_name or not spec_excerpt or not location:
        raise ValueError("spec_name, spec_excerpt, and location are required")

    return {
        "lens": "bugs-drift",
        "severity": "High",
        "location": location,
        "finding": (
            f"Code diverges from {spec_name}. Diff excerpt: {diff_excerpt!r}"
        ),
        "recommendation": (
            f"{spec_name} requires: {spec_excerpt!r}. Update the code to conform, "
            f"or document the deviation explicitly."
        ),
        "confidence": A1_CONFIDENCE,
        "rule": f"{spec_name}: {spec_excerpt}",
    }


def trigger_unverified_a1_finding(
    spec_name: str,
    location: str,
    reason: str = "WebFetch unavailable and no cache",
) -> dict:
    """A1 finding when the spec body can't be fetched.

    Surfaces with confidence 50 — routes through A2's no-silent-drop
    contract into the report's Unverified sub-section.
    """
    return {
        "lens": "bugs-drift",
        "severity": "Medium",
        "location": location,
        "finding": (
            f"[unverified — needs network] {spec_name} mention detected; "
            f"could not fetch governing clause ({reason})."
        ),
        "recommendation": (
            f"Re-fetch when {spec_name} is reachable, or pre-populate the "
            "cache at `~/.claude/cache/code-ultrareview/specs/`."
        ),
        "confidence": 50,
    }
