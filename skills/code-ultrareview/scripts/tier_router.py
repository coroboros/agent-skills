#!/usr/bin/env python3
"""Tier router for code-ultrareview audit phase.

Reads the JSON output of `audit_signals.py` from stdin (or `--input <path>`),
computes a weighted score across eight signals, and picks one of three tiers
(standard / deep / ultra). Emits the routing decision with a multi-line
rationale enumerating each signal's contribution.

The script also exposes the Ultra-tier confirmation gate (`--gate`), which
prints the rationale and prompts the user before committing to an Ultra-tier
run. Bypassed by `--apply-safe` (the user has already opted in) and `-y`
(yes-to-all). Wired so `unittest.mock.patch("builtins.input")` can exercise
the call site directly.

Usage:
    python3 tier_router.py [< audit.json]                 # routing
    python3 tier_router.py --input audit.json             # explicit file
    python3 tier_router.py --gate --input router.json     # confirmation
    python3 tier_router.py --gate --input router.json -y  # bypass prompt
"""

import argparse
import json
import sys

WEIGHTS = {
    "loc_changed": 0.20,
    "files_touched": 0.10,
    "public_api_touched": 0.20,
    "normative_spec_mentioned": 0.20,
    "manifest_graph_delta": 0.10,
    "pre_1_0_or_freeze": 0.05,
    "test_coverage_delta": 0.10,
    "security_sensitive_paths": 0.05,
}

TIER_THRESHOLDS = {
    "standard_max": 0.35,
    "deep_max": 0.70,
}

ESTIMATED_TOKENS = {
    "standard": 50000,
    "deep": 150000,
    "ultra": 400000,
}

LOC_FULL_SCALE = 500.0
FILES_FULL_SCALE = 20.0


def normalize_loc(loc: int) -> float:
    if loc <= 0:
        return 0.0
    return min(1.0, loc / LOC_FULL_SCALE)


def normalize_files(n: int) -> float:
    if n <= 0:
        return 0.0
    return min(1.0, n / FILES_FULL_SCALE)


def normalize_test_gap(ratio) -> float:
    if ratio is None:
        return 0.0
    try:
        r = float(ratio)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, 1.0 - min(1.0, r))


def score_signals(signals: dict) -> dict:
    return {
        "loc_changed": normalize_loc(signals.get("loc_changed", 0)),
        "files_touched": normalize_files(signals.get("files_touched", 0)),
        "public_api_touched": 1.0 if signals.get("public_api_touched") else 0.0,
        "normative_spec_mentioned": 1.0 if signals.get("normative_spec_mentioned") else 0.0,
        "manifest_graph_delta": 1.0 if signals.get("manifest_graph_delta") else 0.0,
        "pre_1_0_or_freeze": 1.0 if signals.get("pre_1_0_or_freeze") else 0.0,
        "test_coverage_delta": normalize_test_gap(signals.get("test_coverage_delta")),
        "security_sensitive_paths": 1.0 if signals.get("security_sensitive_paths") else 0.0,
    }


def total_score(contributions: dict) -> float:
    return round(sum(WEIGHTS[k] * v for k, v in contributions.items()), 4)


def pick_tier(score: float) -> str:
    if score < TIER_THRESHOLDS["standard_max"]:
        return "standard"
    if score < TIER_THRESHOLDS["deep_max"]:
        return "deep"
    return "ultra"


def build_rationale(contributions: dict, score: float, tier: str) -> str:
    lines = [f"Tier: {tier} (score {score:.2f})", ""]
    lines.append("Signal contributions (weight × value):")
    any_nonzero = False
    for key, value in contributions.items():
        if value > 0:
            any_nonzero = True
            lines.append(f"  - {key}: {WEIGHTS[key]:.2f} × {value:.2f} = {WEIGHTS[key] * value:.3f}")
    if not any_nonzero:
        lines.append("  - (none — all signals at zero)")
    lines.append("")
    lines.append(
        f"Thresholds: standard < {TIER_THRESHOLDS['standard_max']}, "
        f"deep < {TIER_THRESHOLDS['deep_max']}, "
        f"ultra ≥ {TIER_THRESHOLDS['deep_max']}"
    )
    return "\n".join(lines)


def route(signals: dict) -> dict:
    contributions = score_signals(signals)
    score = total_score(contributions)
    tier = pick_tier(score)
    return {
        "score": score,
        "tier": tier,
        "rationale": build_rationale(contributions, score, tier),
        "estimated_tokens": ESTIMATED_TOKENS[tier],
    }


def confirm_ultra(tier: str, rationale: str, estimated_tokens: int,
                  apply_safe: bool, yes: bool) -> bool:
    """Gate the Ultra tier behind an interactive prompt.

    Returns True when the run should proceed. Bypassed when tier != "ultra",
    when --apply-safe is set (user opted in explicitly), or when -y is set.
    """
    if tier != "ultra":
        return True
    if apply_safe or yes:
        return True
    print(rationale)
    print(f"\nEstimated tokens: {estimated_tokens}")
    answer = input("Proceed? (y/N) ").strip().lower()
    return answer in ("y", "yes")


def _load_input(input_path) -> dict:
    if input_path:
        with open(input_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def main() -> int:
    parser = argparse.ArgumentParser(description="Tier router for code-ultrareview")
    parser.add_argument("--input", help="Read JSON from a file instead of stdin")
    parser.add_argument(
        "--gate", action="store_true",
        help="Confirmation mode: reads a router result, prompts on Ultra unless bypassed"
    )
    parser.add_argument("--apply-safe", action="store_true",
                        help="(--gate only) bypass Ultra prompt — user already opted in")
    parser.add_argument("-y", "--yes", action="store_true",
                        help="(--gate only) bypass Ultra prompt — yes-to-all")
    args = parser.parse_args()

    payload = _load_input(args.input)

    if args.gate:
        proceed = confirm_ultra(
            tier=payload.get("tier", ""),
            rationale=payload.get("rationale", ""),
            estimated_tokens=int(payload.get("estimated_tokens", 0)),
            apply_safe=args.apply_safe,
            yes=args.yes,
        )
        return 0 if proceed else 2

    result = route(payload)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
