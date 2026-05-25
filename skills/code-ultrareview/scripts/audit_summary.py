#!/usr/bin/env python3
"""Audit summary — deterministic report-header formatter for code-ultrareview.

Reads the JSON output of `audit_signals.py` from stdin (or `--input <path>`)
and emits the "Scope" + "Estimated wall-clock" header block that the report
template prints. Replaces the prior tier-router routing logic — there is no
tier selection; the lens fan-out runs at full strength regardless.

Usage:
    python3 audit_summary.py [< audit.json]                 # stdin
    python3 audit_summary.py --input audit.json             # explicit file
    python3 audit_summary.py --build [--fuzz] < audit.json  # env flags
"""

from __future__ import annotations

import argparse
import json
import sys

BASE_SECONDS = 60
PER_FILE_SECONDS = 5
PUBLIC_API_SECONDS = 60
NORMATIVE_SPEC_SECONDS = 90
MANIFEST_DELTA_SECONDS = 60
SECURITY_PATHS_SECONDS = 60
BUILD_BASE_SECONDS = 60
BUILD_PER_LOC = 0.3
PROPERTY_FUZZ_SECONDS = 120
DERIVATION_BASE_SECONDS = 30
DERIVATION_PER_ARTIFACT_SECONDS = 15

# Human-readable labels for the scope-line repo-kind prefix. "unknown" is
# omitted — falls through to "trivial diff" or the other scope tokens.
_REPO_KIND_LABELS = {
    "skills": "skills repo",
    "app": "app",
    "library": "library",
    "docs": "docs site",
    "monorepo": "monorepo",
    "python": "python project",
    "rust": "rust project",
    "go": "go module",
}
# Cap the competing-signals suffix to keep the header line scannable.
_COMPETING_SHOWN_MAX = 2


def _repo_kind_token(signals: dict) -> str | None:
    """Build the leading scope token from repo_kind + sidecar dict.

    Returns None when repo_kind is "unknown" or absent — caller suppresses it
    so legacy fixtures still render as "trivial diff" / file count etc.
    """
    repo_kind = signals.get("repo_kind") or "unknown"
    if repo_kind == "unknown":
        return None
    label = _REPO_KIND_LABELS.get(repo_kind, repo_kind)
    sidecar = signals.get("repo_kind_signals") or {}
    competing = sidecar.get("competing_signals") or []
    if competing:
        shown = list(competing)[:_COMPETING_SHOWN_MAX]
        label = f"{label} (+ {', '.join(shown)})"
    override = sidecar.get("override_source")
    if override == "--repo-kind flag":
        label = f"{label} (override: --repo-kind)"
    elif isinstance(override, str) and override.startswith("config:"):
        label = f"{label} (override: .code-ultrareview.yaml)"
    return label


def _scope_tokens(signals: dict) -> list:
    tokens = []
    kind_token = _repo_kind_token(signals)
    if kind_token:
        tokens.append(kind_token)
    if signals.get("dirty_tree"):
        tokens.append("dirty tree")
    files_touched = int(signals.get("files_touched", 0) or 0)
    if files_touched:
        tokens.append(f"{files_touched} file{'s' if files_touched != 1 else ''}")
    if signals.get("public_api_touched"):
        tokens.append("public API")
    specs = signals.get("normative_specs_list") or []
    if specs:
        tokens.append("normative spec (" + ", ".join(specs[:3]) + ")")
    elif signals.get("normative_spec_mentioned"):
        tokens.append("normative spec")
    if signals.get("manifest_graph_delta"):
        tokens.append("manifest")
    if signals.get("security_sensitive_paths"):
        tokens.append("security paths")
    if signals.get("pre_1_0_or_freeze"):
        tokens.append("pre-1.0/freeze")
    breadth = signals.get("planning_artifact_breadth") or [0, -1]
    if isinstance(breadth, (list, tuple)) and len(breadth) >= 1 and int(breadth[0]) > 0:
        count = int(breadth[0])
        days = int(breadth[1]) if len(breadth) > 1 else -1
        freshness = f"{days}d fresh" if days >= 0 else "freshness unknown"
        tokens.append(f"{count} planning artifact{'s' if count != 1 else ''} ({freshness})")
    return tokens


def _format_duration(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    minutes, rem = divmod(seconds, 60)
    if rem == 0:
        return f"{minutes}m"
    return f"{minutes}m {rem}s"


def _contributions(signals: dict, build_tool_available: bool,
                   property_fuzz_available: bool) -> list:
    items = [("base", BASE_SECONDS)]
    files_touched = int(signals.get("files_touched", 0) or 0)
    if files_touched:
        items.append((f"{files_touched} files × {PER_FILE_SECONDS}s",
                      files_touched * PER_FILE_SECONDS))
    if signals.get("public_api_touched"):
        items.append(("public API", PUBLIC_API_SECONDS))
    if signals.get("normative_spec_mentioned"):
        items.append(("normative spec fetch", NORMATIVE_SPEC_SECONDS))
    if signals.get("manifest_graph_delta"):
        items.append(("manifest delta", MANIFEST_DELTA_SECONDS))
    if signals.get("security_sensitive_paths"):
        items.append(("security paths", SECURITY_PATHS_SECONDS))
    if build_tool_available:
        loc_changed = int(signals.get("loc_changed", 0) or 0)
        build_secs = max(BUILD_BASE_SECONDS, int(loc_changed * BUILD_PER_LOC))
        items.append((f"build/execute ({loc_changed} LOC)", build_secs))
    if property_fuzz_available:
        items.append(("property-fuzz", PROPERTY_FUZZ_SECONDS))
    breadth = signals.get("planning_artifact_breadth") or [0, -1]
    if isinstance(breadth, (list, tuple)) and len(breadth) >= 1 and int(breadth[0]) > 0:
        count = int(breadth[0])
        items.append((
            f"derivation lens ({count} planning artifact{'s' if count != 1 else ''})",
            DERIVATION_BASE_SECONDS + count * DERIVATION_PER_ARTIFACT_SECONDS,
        ))
    return items


def _build_rationale(contributions: list, total: int) -> str:
    lines = [f"Estimated wall-clock: {_format_duration(total)} ({total}s)", ""]
    lines.append("Contributions:")
    for name, secs in contributions:
        lines.append(f"  - {name}: +{secs}s")
    return "\n".join(lines)


def format_header(signals: dict, *, build_tool_available: bool = False,
                  property_fuzz_available: bool = False) -> dict:
    """Produce report-header context from audit signals.

    Args:
        signals: output dict from audit_signals.py.
        build_tool_available: caller knows whether a test runner is on PATH
            (e.g., via build_detect.py). Affects wall-clock estimate.
        property_fuzz_available: caller knows whether fast-check / hypothesis
            is present in the repo's manifest. Affects wall-clock estimate.

    Returns:
        dict with three keys:
            scope (str): one-line human-readable summary of what the diff
                touches. "trivial diff" when no scope flags fire.
            estimated_wall_clock_seconds (int): deterministic cost estimate.
            rationale (str): multi-line breakdown of the cost contributors.
    """
    tokens = _scope_tokens(signals)
    scope = " · ".join(tokens) if tokens else "trivial diff"

    contributions = _contributions(
        signals, build_tool_available, property_fuzz_available
    )
    total = sum(secs for _, secs in contributions)
    rationale = _build_rationale(contributions, total)

    return {
        "scope": scope,
        "estimated_wall_clock_seconds": total,
        "rationale": rationale,
    }


def _load_input(input_path) -> dict:
    if input_path:
        with open(input_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="audit_summary — header formatter for code-ultrareview"
    )
    parser.add_argument("--input", help="Read JSON from a file instead of stdin")
    parser.add_argument("--build", action="store_true",
                        help="Build tool available (affects wall-clock estimate)")
    parser.add_argument("--fuzz", action="store_true",
                        help="Property-fuzz library available (affects wall-clock)")
    args = parser.parse_args()

    signals = _load_input(args.input)
    result = format_header(
        signals,
        build_tool_available=args.build,
        property_fuzz_available=args.fuzz,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
