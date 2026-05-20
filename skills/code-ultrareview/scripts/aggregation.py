#!/usr/bin/env python3
"""Aggregation primitives for code-ultrareview.

Composes A2 routing (no silent drop), Deep-tier iteration, cross-lens
deduplication, severity-tier assignment, and canonical ordering. Pure
stdlib; called from the dispatcher orchestrator after lens subagents
return their findings.

Findings are passed as plain dicts to keep the wire format identical to
the JSON the lens subagents emit. The shape is:

    {
        "lens": str,
        "severity": "High" | "Medium" | "Low",
        "location": str,
        "finding": str,
        "recommendation": str,
        "confidence": int,
        # optional: "rule", "sub_graph", "pre_existing", "meta"
    }
"""

from __future__ import annotations

import re
from typing import Callable

CONFIDENCE_THRESHOLD = 80
DEEP_PROMOTION_BONUS = 30
DEEP_PROMOTION_CAP = 95
UNVERIFIED_PREFIX = "[unverified — recommend Deep pass]"

SEVERITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}

# Tokens used to build the dedup key from a finding text.
_KEY_TOKENS = 6
_KEY_WORD_RE = re.compile(r"[A-Za-z0-9_]+")


def _finding_key(finding: dict) -> tuple[str, str]:
    location = finding.get("location", "")
    text = finding.get("finding", "")
    tokens = _KEY_WORD_RE.findall(text.lower())
    return (location, " ".join(tokens[:_KEY_TOKENS]))


def dedupe(findings: list[dict]) -> list[dict]:
    """Collapse cross-lens duplicates by (location, finding-key).

    Keeps the highest-confidence finding; merges the other lens name into
    `meta.secondary_lens` (a comma-separated list).
    """
    bucket: dict[tuple[str, str], dict] = {}
    for f in findings:
        key = _finding_key(f)
        existing = bucket.get(key)
        if existing is None:
            bucket[key] = dict(f)
            continue
        kept, dropped = (
            (existing, f) if existing.get("confidence", 0) >= f.get("confidence", 0)
            else (f, existing)
        )
        kept = dict(kept)
        meta = dict(kept.get("meta") or {})
        secondary = meta.get("secondary_lens", "")
        existing_lenses = {l for l in secondary.split(",") if l}
        existing_lenses.add(dropped.get("lens", ""))
        existing_lenses.discard(kept.get("lens", ""))
        existing_lenses.discard("")
        if existing_lenses:
            meta["secondary_lens"] = ",".join(sorted(existing_lenses))
            kept["meta"] = meta
        bucket[key] = kept
    return list(bucket.values())


def apply_a2(findings: list[dict]) -> tuple[list[dict], list[dict]]:
    """Route findings into (verified, unverified) per the A2 contract.

    Findings with `confidence == 0` are dropped (per rubric: false positive
    or pre-existing). Findings with `0 < confidence < 80` are surfaced with
    the unverified prefix, severity downgraded to `Low`, and routing
    rationale prepended to the recommendation.
    """
    verified: list[dict] = []
    unverified: list[dict] = []
    for raw in findings:
        f = dict(raw)
        conf = int(f.get("confidence", 0))
        if conf == 0:
            continue
        if conf >= CONFIDENCE_THRESHOLD:
            verified.append(f)
            continue
        finding_text = f.get("finding", "")
        if not finding_text.startswith(UNVERIFIED_PREFIX):
            f["finding"] = f"{UNVERIFIED_PREFIX} {finding_text}".strip()
        rationale = f"Sub-{CONFIDENCE_THRESHOLD} confidence ({conf}) — re-run with -t deep to verify."
        rec = f.get("recommendation", "")
        if rationale not in rec:
            f["recommendation"] = f"{rationale} {rec}".strip()
        meta = dict(f.get("meta") or {})
        meta.setdefault("original_severity", f.get("severity", "Medium"))
        f["meta"] = meta
        f["severity"] = "Low"
        unverified.append(f)
    return verified, unverified


def deep_iterate(
    unverified: list[dict],
    builder_fn: Callable[[dict], str],
) -> tuple[list[dict], list[dict], list[dict]]:
    """Re-pass each unverified finding through a build verification.

    `builder_fn(finding)` must return one of `"confirmed"`, `"disproved"`,
    or `"inconclusive"`. Cap: one iteration per finding (the dispatcher
    never re-calls). Returns `(promoted, remaining, dropped)`.

    - confirmed   → confidence += DEEP_PROMOTION_BONUS (capped), severity
                    restored to the original (stripped of "Low" downgrade
                    if A2 had applied it), unverified prefix removed.
    - disproved   → finding dropped (returned for logging, not surfaced).
    - inconclusive → finding stays in `remaining` unchanged.
    """
    promoted: list[dict] = []
    remaining: list[dict] = []
    dropped: list[dict] = []

    for raw in unverified:
        verdict = builder_fn(raw)
        if verdict == "confirmed":
            f = dict(raw)
            old_conf = int(f.get("confidence", 0))
            new_conf = min(DEEP_PROMOTION_CAP, old_conf + DEEP_PROMOTION_BONUS)
            f["confidence"] = max(new_conf, CONFIDENCE_THRESHOLD)
            text = f.get("finding", "")
            if text.startswith(UNVERIFIED_PREFIX):
                text = text[len(UNVERIFIED_PREFIX):].lstrip()
                f["finding"] = text
            f["severity"] = _restore_severity(f)
            promoted.append(f)
        elif verdict == "disproved":
            dropped.append(dict(raw))
        else:
            remaining.append(dict(raw))

    return promoted, remaining, dropped


def _restore_severity(finding: dict) -> str:
    """Restore the original severity from `meta.original_severity` if A2
    downgraded it to Low; otherwise keep the current value."""
    meta = finding.get("meta") or {}
    return meta.get("original_severity") or finding.get("severity", "Medium")


def assign_anthropic_tier(finding: dict) -> dict:
    """Add `meta.anthropic_tier` per the documented mapping.

    Important when confidence ≥80 AND severity High/Medium.
    Nit when confidence ≥80 AND severity Low.
    Pre-existing when finding.pre_existing is True (set by lens).
    """
    f = dict(finding)
    if f.get("pre_existing"):
        tier = "Pre-existing"
    else:
        conf = int(f.get("confidence", 0))
        sev = f.get("severity", "")
        if conf >= CONFIDENCE_THRESHOLD and sev in ("High", "Medium"):
            tier = "Important"
        elif conf >= CONFIDENCE_THRESHOLD and sev == "Low":
            tier = "Nit"
        else:
            tier = None
    if tier is not None:
        meta = dict(f.get("meta") or {})
        meta["anthropic_tier"] = tier
        f["meta"] = meta
    return f


def order(findings: list[dict]) -> list[dict]:
    """Canonical ordering: severity → confidence (desc) → location."""
    def key(f: dict):
        sev = SEVERITY_ORDER.get(f.get("severity", "Low"), 99)
        conf = -int(f.get("confidence", 0))
        loc = f.get("location", "")
        return (sev, conf, loc)
    return sorted(findings, key=key)


def synthesize(
    findings: list[dict],
    tier: str = "standard",
    builder_fn: Callable[[dict], str] | None = None,
) -> dict:
    """End-to-end aggregation. Returns the report payload."""
    findings = dedupe(findings)
    verified, unverified = apply_a2(findings)

    deep_dropped: list[dict] = []
    if tier == "deep" and builder_fn is not None:
        promoted, unverified, deep_dropped = deep_iterate(unverified, builder_fn)
        verified.extend(promoted)

    verified = order([assign_anthropic_tier(f) for f in verified])
    unverified = order(unverified)

    return {
        "verified": verified,
        "unverified": unverified,
        "deep_iteration_dropped": deep_dropped,
        "tier": tier,
    }
