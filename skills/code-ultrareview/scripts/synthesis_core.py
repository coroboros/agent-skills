#!/usr/bin/env python3
"""Synthesis primitives for code-ultrareview.

Single source of truth for the 8-axis taxonomy and its inter-axis
precedence — when two or more axes flag the same `file:line`, highest
severity wins; ties resolve via this order:

    Correctness > Design/API > Simplification > Tests > Documentation >
    Style > Intent > Performance > Coherence (conditional)

Owns A2 no-silent-drop routing, severity markers, build-verification
iteration, tier classification, ordering, verdict, and precedence dedup.
Kept separate from Phase 5 (`scripts/synthesize.py`) so axis lenses
(Phase 3) and Haiku validators (Phase 4) reuse the core contracts without
pulling in synthesis-layer concerns.

Findings are plain dicts matching the JSON shape axis subagents emit:
`axis`, `severity` (High|Medium|Low), `location`, `finding`,
`recommendation`, `confidence` (0-100), optional `rule` / `pre_existing` /
`meta`.
"""

from __future__ import annotations

from typing import Callable

CONFIDENCE_THRESHOLD = 80
PROMOTION_BONUS = 30
PROMOTION_CAP = 95
UNVERIFIED_PREFIX = "[unverified]"

SEVERITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}

# 🔴 High — blocks ship. 🟠 Medium — fix soon. 🟢 Low — nit / informational.
SEVERITY_MARKERS = {"High": "🔴", "Medium": "🟠", "Low": "🟢"}

# Always-on. Order here is reporting order, not precedence.
CANONICAL_AXES = (
    "correctness",
    "simplification",
    "tests",
    "documentation",
    "style",
    "intent",
    "design-api",
    "performance",
)

# Inter-axis precedence — highest severity wins; ties resolve via this order.
AXIS_PRIORITY = (
    "correctness",
    "design-api",
    "simplification",
    "tests",
    "documentation",
    "style",
    "intent",
    "performance",
    "coherence",
)

# Activates when `scope.json["activates_coherence"]` is true (metadata in diff).
CONDITIONAL_AXES = ("coherence",)

ALL_AXES = CANONICAL_AXES + CONDITIONAL_AXES


def _attach_marker(finding: dict) -> dict:
    """Attach `meta.marker` to a finding based on its current severity.

    Idempotent — re-calling yields the same dict.
    """
    f = dict(finding)
    severity = f.get("severity", "Low")
    marker = SEVERITY_MARKERS.get(severity, SEVERITY_MARKERS["Low"])
    meta = dict(f.get("meta") or {})
    meta["marker"] = marker
    f["meta"] = meta
    return f


def _restore_severity(finding: dict) -> str:
    """Restore the original severity from `meta.original_severity` if A2
    downgraded it to Low; otherwise keep the current value."""
    meta = finding.get("meta") or {}
    return meta.get("original_severity") or finding.get("severity", "Medium")


def apply_a2(findings: list[dict]) -> tuple[list[dict], list[dict]]:
    """Route findings into (verified, unverified) per the A2 contract.

    - confidence == 0 → dropped (false positive / pre-existing per rubric).
    - 0 < confidence < CONFIDENCE_THRESHOLD → surfaced with
      `[unverified]` prefix, severity downgraded to `Low`, rationale
      prepended to the recommendation. Original severity preserved in
      `meta.original_severity` so build verification can restore it.
    - confidence ≥ CONFIDENCE_THRESHOLD → verified, marker attached.

    Every retained finding gets `meta.marker` so downstream consumers
    render the glyph without re-deriving from severity.
    """
    verified: list[dict] = []
    unverified: list[dict] = []
    for raw in findings:
        f = dict(raw)
        conf = int(f.get("confidence", 0))
        if conf == 0:
            continue
        if conf >= CONFIDENCE_THRESHOLD:
            f = _attach_marker(f)
            verified.append(f)
            continue
        finding_text = f.get("finding", "")
        if not finding_text.startswith(UNVERIFIED_PREFIX):
            f["finding"] = f"{UNVERIFIED_PREFIX} {finding_text}".strip()
        rationale = (
            f"Sub-{CONFIDENCE_THRESHOLD} confidence ({conf}) — "
            "verify locally before action."
        )
        rec = f.get("recommendation", "")
        if rationale not in rec:
            f["recommendation"] = f"{rationale} {rec}".strip()
        meta = dict(f.get("meta") or {})
        meta.setdefault("original_severity", f.get("severity", "Medium"))
        f["meta"] = meta
        f["severity"] = "Low"
        f = _attach_marker(f)
        unverified.append(f)
    return verified, unverified


# Build verification iteration — Phase 3.5, gated by --verify-build.
def iterate_unverified(
    unverified: list[dict],
    builder_fn: Callable[[dict], str],
) -> tuple[list[dict], list[dict], list[dict]]:
    """Re-pass each unverified finding through build verification.

    `builder_fn(finding)` returns `"confirmed"` / `"disproved"` /
    `"inconclusive"`. Cap: one iteration per finding.

    Returns `(promoted, remaining, dropped)`:
      - confirmed   → confidence += PROMOTION_BONUS (capped at PROMOTION_CAP,
                      floor at CONFIDENCE_THRESHOLD), severity restored
                      from `meta.original_severity`, unverified prefix
                      stripped, marker re-attached.
      - disproved   → finding moved to `dropped` (for logging, not surfaced).
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
            new_conf = min(PROMOTION_CAP, old_conf + PROMOTION_BONUS)
            f["confidence"] = max(new_conf, CONFIDENCE_THRESHOLD)
            text = f.get("finding", "")
            if text.startswith(UNVERIFIED_PREFIX):
                text = text[len(UNVERIFIED_PREFIX):].lstrip()
                f["finding"] = text
            f["severity"] = _restore_severity(f)
            f = _attach_marker(f)
            promoted.append(f)
        elif verdict == "disproved":
            dropped.append(dict(raw))
        else:
            remaining.append(dict(raw))

    return promoted, remaining, dropped


def assign_anthropic_tier(finding: dict) -> dict:
    """Add `meta.anthropic_tier` per the documented mapping.

    - Important: confidence ≥ threshold AND severity High/Medium.
    - Nit: confidence ≥ threshold AND severity Low.
    - Pre-existing: finding.pre_existing is True (set by the axis).
    - None: confidence below threshold (handled by A2 routing first).
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


def _is_important(f: dict, marker: str) -> bool:
    meta = f.get("meta") or {}
    return (
        meta.get("marker") == marker
        and meta.get("anthropic_tier") == "Important"
    )


def _axis_breakdown(findings: list[dict]) -> list[str]:
    counts: dict[str, int] = {}
    for f in findings:
        axis = f.get("axis", "?")
        counts[axis] = counts.get(axis, 0) + 1
    return [f"{n} in {axis}" for axis, n in counts.items()]


def compute_verdict(verified: list[dict]) -> dict:
    """Compute Ship / Fix-then-ship / Needs work from verified findings.

    Algorithm:
      - Needs work if any verified finding has marker 🔴 AND
        anthropic_tier "Important".
      - Fix-then-ship if no 🔴 Important but any 🟠 Important.
      - Ship otherwise.

    Unverified findings are excluded by design — sub-80 confidence is not
    load-bearing for the ship decision.
    """
    red_important = [f for f in verified if _is_important(f, "🔴")]
    orange_important = [f for f in verified if _is_important(f, "🟠")]

    if red_important:
        breakdown = _axis_breakdown(red_important)
        rationale = (
            f"{len(red_important)} 🔴 Important "
            f"({', '.join(breakdown)}) — fix red before ship."
        )
        return {
            "label": "Needs work",
            "rationale": rationale,
            "drivers": breakdown,
        }
    if orange_important:
        breakdown = _axis_breakdown(orange_important)
        rationale = (
            f"{len(orange_important)} 🟠 Important "
            f"({', '.join(breakdown)}) — fix before ship."
        )
        return {
            "label": "Fix-then-ship",
            "rationale": rationale,
            "drivers": breakdown,
        }
    if not verified:
        return {
            "label": "Ship",
            "rationale": "Eight axes ran clean. Ship.",
            "drivers": [],
        }
    return {
        "label": "Ship",
        "rationale": "Only Nits — no blockers. Ship.",
        "drivers": [],
    }


def compute_severity_counts(verified: list[dict]) -> dict[str, int]:
    """Count verified findings by visual marker. Keys 🔴 / 🟠 / 🟢 always present."""
    counts: dict[str, int] = {marker: 0 for marker in SEVERITY_MARKERS.values()}
    for f in verified:
        meta = f.get("meta") or {}
        marker = meta.get("marker")
        if marker in counts:
            counts[marker] += 1
    return counts


_AXIS_RANK = {axis: idx for idx, axis in enumerate(AXIS_PRIORITY)}


def _dedup_key(finding: dict) -> tuple[str, str]:
    """Bucket key for inter-axis dedup: `(location, finding-text)`.

    Two axes flagging the same `file:line` with the same finding text
    collide on this key. Different findings at the same line — say a
    correctness null-deref and a tests missing-assert — keep distinct keys
    so both survive (they describe different problems at coincident lines).
    """
    loc = str(finding.get("location", ""))
    text = str(finding.get("finding", "")).strip()
    return (loc, text)


def _precedence_key(finding: dict) -> tuple[int, int]:
    """Sort key for picking the winner inside a dedup bucket.

    Lower tuple wins. Severity first (`SEVERITY_ORDER`), axis-priority
    second (`AXIS_PRIORITY` position). Unknown axes sort to the end.
    """
    severity = SEVERITY_ORDER.get(finding.get("severity", "Low"), 99)
    axis_rank = _AXIS_RANK.get(finding.get("axis", ""), len(AXIS_PRIORITY))
    return (severity, axis_rank)


def dedup_by_precedence(findings: list[dict]) -> list[dict]:
    """Dedup findings by (location, finding text). When ≥2 axes flag the
    same `file:line` with the same wording, highest severity wins;
    ties resolve via `AXIS_PRIORITY` (Correctness > Design/API >
    Simplification > Tests > Documentation > Style > Intent > Performance >
    Coherence). Input order is preserved within the surviving set —
    callers can re-`order(...)` to apply canonical sort.

    Findings with empty `location` are not deduped — they pass through.

    Mirrors the SKILL.md § Phase 5 inter-axis precedence contract — both
    files describe the same `(location, finding-text)` bucket semantics.
    """
    buckets: dict[tuple[str, str], dict] = {}
    survivors: list[dict] = []
    untouched: list[dict] = []
    for raw in findings:
        f = dict(raw)
        loc = str(f.get("location", "")).strip()
        if not loc:
            untouched.append(f)
            continue
        key = _dedup_key(f)
        current = buckets.get(key)
        if current is None or _precedence_key(f) < _precedence_key(current):
            buckets[key] = f
    seen: set[tuple[str, str]] = set()
    for raw in findings:
        loc = str(raw.get("location", "")).strip()
        if not loc:
            continue
        key = _dedup_key(raw)
        if key in seen:
            continue
        seen.add(key)
        survivors.append(buckets[key])
    return survivors + untouched
