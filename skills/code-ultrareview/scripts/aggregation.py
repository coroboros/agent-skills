#!/usr/bin/env python3
"""Aggregation primitives for code-ultrareview.

Composes A2 routing (no silent drop), always-on iteration on sub-80
findings (when a builder is supplied), cross-lens deduplication,
severity-tier assignment, marker attachment, and canonical ordering.
Also computes the closing-block extension consumed by the report
template: `severity_counts`, `lens_summary`, `verdict`, `action_plan`.
Pure stdlib; called from the dispatcher orchestrator after lens
subagents return their findings.

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
PROMOTION_BONUS = 30
PROMOTION_CAP = 95
UNVERIFIED_PREFIX = "[unverified]"

SEVERITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}

# Repo-kind report-header rendering. Mirrors audit_summary._REPO_KIND_LABELS
# but keeps a separate map — the audit-summary token feeds the scope line;
# the repo-kind-header token feeds its own line in the report header.
_REPO_KIND_HEADER_LABELS = {
    "skills": "skills",
    "app": "app",
    "library": "library",
    "docs": "docs",
    "monorepo": "monorepo",
    "python": "python",
    "rust": "rust",
    "go": "go",
}
_REPO_KIND_HEADER_UNKNOWN = "unknown — heuristics not specialized"

# 3-tier visual markers surfaced in every report.
# 🔴 High — blocks ship. 🟠 Medium — fix soon. 🟢 Low — nit / informational.
SEVERITY_MARKERS = {"High": "🔴", "Medium": "🟠", "Low": "🟢"}

# Canonical lens keys — locked across the report table, evals, and the
# pipeline contract (tests/_pipeline/_contracts.py). Order is canonical.
CANONICAL_LENSES = (
    "rules",
    "bugs-drift",
    "docs-version",
    "tests-blindspots",
    "coherence-graph",
    "derivation",
    "prose-hygiene",
)

# Always-on lenses. Derivation is conditional (requires --reconcile).
# prose-hygiene is always-on with `--no-prose-hygiene` opt-out — the
# dispatcher strips the flag from $ARGUMENTS and skips this lens when set.
ALWAYS_ON_LENSES = (
    "rules",
    "bugs-drift",
    "docs-version",
    "tests-blindspots",
    "coherence-graph",
    "prose-hygiene",
)

# Tokens used to build the dedup key from a finding text.
_KEY_TOKENS = 6
_KEY_WORD_RE = re.compile(r"[A-Za-z0-9_]+")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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


def _finding_key(finding: dict) -> tuple[str, str]:
    location = finding.get("location", "")
    text = finding.get("finding", "")
    tokens = _KEY_WORD_RE.findall(text.lower())
    return (location, " ".join(tokens[:_KEY_TOKENS]))


def _truncate(text: str, limit: int = 80) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _lazy_detect_skills():
    """Import the sibling `detect_skills` module on demand."""
    from pathlib import Path
    import importlib.util as _il
    here = Path(__file__).resolve().parent
    spec = _il.spec_from_file_location("detect_skills", here / "detect_skills.py")
    if spec is None or spec.loader is None:
        return None
    module = _il.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Existing pipeline
# ---------------------------------------------------------------------------


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
    rationale prepended to the recommendation. Every retained finding gets
    `meta.marker` attached so downstream consumers render the glyph without
    re-deriving from severity.
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


def iterate_unverified(
    unverified: list[dict],
    builder_fn: Callable[[dict], str],
) -> tuple[list[dict], list[dict], list[dict]]:
    """Re-pass each unverified finding through a build verification.

    `builder_fn(finding)` returns one of `"confirmed"`, `"disproved"`, or
    `"inconclusive"`. Cap: one iteration per finding. Returns
    `(promoted, remaining, dropped)`.

    - confirmed   → confidence += PROMOTION_BONUS (capped), severity
                    restored from `meta.original_severity` (if A2 had
                    downgraded), unverified prefix removed, marker
                    re-attached for the restored severity.
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


# ---------------------------------------------------------------------------
# Closing-block computations: severity counts, lens summary, verdict, action plan
# ---------------------------------------------------------------------------


def compute_repo_kind_header(audit_signals: dict | None) -> str:
    """Build the `Repo: <kind>` header token from the audit JSON.

    `audit_signals` is the dict emitted by `audit_signals.py::audit()`.
    Missing `repo_kind` → falls back to `unknown` so legacy audit JSON
    (no classifier) still renders a clean header. The override suffix
    grammar mirrors `audit_summary._repo_kind_token` so readers see a
    consistent format across both surfaces.
    """
    if not audit_signals:
        return f"Repo: {_REPO_KIND_HEADER_UNKNOWN}"
    repo_kind = audit_signals.get("repo_kind") or "unknown"
    if repo_kind == "unknown":
        return f"Repo: {_REPO_KIND_HEADER_UNKNOWN}"
    label = _REPO_KIND_HEADER_LABELS.get(repo_kind, repo_kind)
    sidecar = audit_signals.get("repo_kind_signals") or {}
    override = sidecar.get("override_source")
    if override == "--repo-kind flag":
        label = f"{label} (override: --repo-kind)"
    elif isinstance(override, str) and override.startswith("config:"):
        label = f"{label} (override: .code-ultrareview.yaml)"
    return f"Repo: {label}"


def compute_severity_counts(verified: list[dict]) -> dict[str, int]:
    """Count verified findings by visual marker.

    Returns keys 🔴 / 🟠 / 🟢 — keys are present even when count is zero,
    so callers never check for missing keys.
    """
    counts: dict[str, int] = {marker: 0 for marker in SEVERITY_MARKERS.values()}
    for f in verified:
        meta = f.get("meta") or {}
        marker = meta.get("marker")
        if marker in counts:
            counts[marker] += 1
    return counts


def compute_lens_summary(
    verified: list[dict],
    unverified: list[dict],
    ran_lenses: tuple[str, ...] | list[str],
) -> list[dict]:
    """Per-lens status snapshot in canonical order.

    Every canonical lens renders as a row, including clean ones. A lens
    not in `ran_lenses` renders as `status: "skipped"`. Top-finding text
    truncates at 80 chars.
    """
    ran = set(ran_lenses)
    summary: list[dict] = []
    for lens in CANONICAL_LENSES:
        if lens not in ran:
            summary.append({
                "lens": lens,
                "status": "skipped",
                "verified_count": 0,
                "unverified_count": 0,
                "top_finding": None,
            })
            continue

        v_for_lens = [f for f in verified if f.get("lens") == lens]
        u_for_lens = [f for f in unverified if f.get("lens") == lens]

        markers = {(f.get("meta") or {}).get("marker") for f in v_for_lens}
        if "🔴" in markers:
            status = "🔴"
        elif "🟠" in markers:
            status = "🟠"
        else:
            status = "🟢"

        top_finding: str | None = None
        if v_for_lens:
            ordered_lens = order(list(v_for_lens))
            top_finding = _truncate(ordered_lens[0].get("finding", ""))

        summary.append({
            "lens": lens,
            "status": status,
            "verified_count": len(v_for_lens),
            "unverified_count": len(u_for_lens),
            "top_finding": top_finding,
        })
    return summary


def compute_verdict(verified: list[dict]) -> dict:
    """Compute Ship / Fix-then-ship / Needs work from verified findings.

    Algorithm:
      - Needs work if any verified finding has marker 🔴 AND
        anthropic_tier "Important".
      - Fix-then-ship if no 🔴 Important but any 🟠 Important.
      - Ship otherwise.

    Unverified findings are excluded by design — sub-80 confidence is
    not load-bearing for the ship decision. Documented in
    `references/verdict-logic.md`.
    """
    def _is_important(f: dict, marker: str) -> bool:
        meta = f.get("meta") or {}
        return (
            meta.get("marker") == marker
            and meta.get("anthropic_tier") == "Important"
        )

    red_important = [f for f in verified if _is_important(f, "🔴")]
    orange_important = [f for f in verified if _is_important(f, "🟠")]

    def _lens_breakdown(findings: list[dict]) -> list[str]:
        counts: dict[str, int] = {}
        for f in findings:
            lens = f.get("lens", "?")
            counts[lens] = counts.get(lens, 0) + 1
        return [f"{n} in {lens}" for lens, n in counts.items()]

    if red_important:
        breakdown = _lens_breakdown(red_important)
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
        breakdown = _lens_breakdown(orange_important)
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
            "rationale": "Six lenses ran clean. Ship.",
            "drivers": [],
        }
    return {
        "label": "Ship",
        "rationale": "Only Nits — no blockers. Ship.",
        "drivers": [],
    }


def compute_action_plan(
    verified: list[dict],
    unverified: list[dict],
    installed_skills: dict,
    route_fn: Callable,
) -> dict:
    """Group findings into paste-ready delegation prompts.

    Output:
      {
        "zero_findings": bool,
        "clusters": [
          {severity, severity_label, lens, count,
           command, fallback_used, prompt_text}
        ],
        "unverified_block": {prompt_text, count} | None,
      }
    """
    if not verified and not unverified:
        return {"zero_findings": True, "clusters": [], "unverified_block": None}

    red_clusters: list[dict] = []
    orange_clusters: list[dict] = []
    green_findings: list[dict] = []

    for lens in CANONICAL_LENSES:
        lens_findings = [f for f in verified if f.get("lens") == lens]
        if not lens_findings:
            continue
        for marker, label, target in (
            ("🔴", "🔴 Fix now", red_clusters),
            ("🟠", "🟠 Fix soon", orange_clusters),
        ):
            cluster = [
                f for f in lens_findings
                if (f.get("meta") or {}).get("marker") == marker
            ]
            if not cluster:
                continue
            route = route_fn(lens, marker, installed_skills)
            label_full = f"{label} ({len(cluster)} findings)"
            target.append({
                "severity": marker,
                "severity_label": label_full,
                "lens": lens,
                "count": len(cluster),
                "command": route["command"],
                "fallback_used": route["fallback_used"],
                "prompt_text": _format_cluster_prompt(
                    route["command"], lens, cluster
                ),
            })
        green_findings.extend(
            f for f in lens_findings
            if (f.get("meta") or {}).get("marker") == "🟢"
        )

    clusters = red_clusters + orange_clusters

    if green_findings:
        route_lens = next(
            (lens for lens in CANONICAL_LENSES
             if any(f.get("lens") == lens for f in green_findings)),
            CANONICAL_LENSES[0],
        )
        route = route_fn(route_lens, "🟢", installed_skills)
        clusters.append({
            "severity": "🟢",
            "severity_label": f"🟢 Nits ({len(green_findings)} findings) — optional cleanup",
            "lens": "mixed",
            "count": len(green_findings),
            "command": route["command"],
            "fallback_used": route["fallback_used"],
            "prompt_text": _format_green_prompt(route["command"], green_findings),
        })

    unverified_block: dict | None = None
    if unverified:
        unverified_block = {
            "count": len(unverified),
            "prompt_text": _format_unverified_prompt(unverified),
        }

    return {
        "zero_findings": False,
        "clusters": clusters,
        "unverified_block": unverified_block,
    }


def _format_cluster_prompt(command: str, lens: str, cluster: list[dict]) -> str:
    """Build the paste-ready prompt for a non-🟢 cluster."""
    lines = [f"{command} apply {lens} fixes ({len(cluster)} findings):"]
    for f in cluster:
        loc = f.get("location", "?")
        issue = _truncate(f.get("finding", ""), 100)
        fix = _truncate(f.get("recommendation", ""), 120)
        lines.append(f"  - {loc} — {issue}")
        if fix:
            lines.append(f"      → {fix}")
    return "\n".join(lines)


def _format_green_prompt(command: str, findings: list[dict]) -> str:
    """Build the polish-block prompt aggregating all 🟢 findings cross-lens."""
    lines = [f"{command} polish ({len(findings)} nits):"]
    for f in findings:
        loc = f.get("location", "?")
        issue = _truncate(f.get("finding", ""), 100)
        lines.append(f"  - {loc} — {issue} [{f.get('lens', '?')}]")
    return "\n".join(lines)


def _format_unverified_prompt(unverified: list[dict]) -> str:
    """Build the prompt for the Unverified follow-up block."""
    lines = [
        "/apex investigate and decide on the following unverified findings:"
    ]
    for f in unverified:
        loc = f.get("location", "?")
        issue = _truncate(f.get("finding", ""), 100)
        lines.append(f"  - {loc} — {issue} [{f.get('lens', '?')}]")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Top-level entry point
# ---------------------------------------------------------------------------


def synthesize(
    findings: list[dict],
    builder_fn: Callable[[dict], str] | None = None,
    ran_lenses: tuple[str, ...] | list[str] | None = None,
    installed_skills: dict | None = None,
    route_fn: Callable | None = None,
    audit_signals: dict | None = None,
) -> dict:
    """End-to-end aggregation. Returns the report payload.

    Iteration on sub-80 findings runs whenever `builder_fn` is supplied —
    that is the always-on contract documented in `references/lenses.md`.
    Callers that lack a build harness (no test runner detected, sandbox
    disabled) pass `builder_fn=None` and the unverified set surfaces
    without promotion attempts.

    Closing-block extensions (`severity_counts`, `lens_summary`, `verdict`,
    `action_plan`) are always computed. `ran_lenses` defaults to the
    always-on five (derivation excluded). `installed_skills` and
    `route_fn` default to runtime detection via
    `detect_skills.detect_installed_skills` / `route_cluster`.
    """
    if ran_lenses is None:
        ran_lenses = ALWAYS_ON_LENSES

    findings = dedupe(findings)
    verified, unverified = apply_a2(findings)

    iteration_dropped: list[dict] = []
    if builder_fn is not None:
        promoted, unverified, iteration_dropped = iterate_unverified(
            unverified, builder_fn
        )
        verified.extend(promoted)

    verified = order([assign_anthropic_tier(f) for f in verified])
    unverified = order(unverified)

    severity_counts = compute_severity_counts(verified)
    lens_summary = compute_lens_summary(verified, unverified, ran_lenses)
    verdict = compute_verdict(verified)

    if installed_skills is None or route_fn is None:
        ds = _lazy_detect_skills()
        if ds is not None:
            if installed_skills is None:
                installed_skills = ds.detect_installed_skills()
            if route_fn is None:
                route_fn = ds.route_cluster

    if installed_skills is None:
        installed_skills = {}

    if route_fn is not None:
        action_plan = compute_action_plan(
            verified, unverified, installed_skills, route_fn
        )
    else:
        action_plan = {
            "zero_findings": not (verified or unverified),
            "clusters": [],
            "unverified_block": None,
        }

    return {
        "verified": verified,
        "unverified": unverified,
        "iteration_dropped": iteration_dropped,
        "severity_counts": severity_counts,
        "lens_summary": lens_summary,
        "verdict": verdict,
        "action_plan": action_plan,
        "repo_kind_header": compute_repo_kind_header(audit_signals),
    }
