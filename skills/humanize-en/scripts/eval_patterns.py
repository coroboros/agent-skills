#!/usr/bin/env python3
"""
eval_patterns.py — score prescan.py against the eval corpus.

Usage:
    eval_patterns.py                           # whole corpus (eval-corpus/samples/*.json)
    eval_patterns.py --sample <path.json>      # single sample
    eval_patterns.py --corpus <dir>            # custom corpus directory

Runs prescan.py on each sample's `input`, compares the pattern families it
detected against the sample's `expected_hits`, and emits a JSON report per
`references/schemas.md` § "eval result".

Exit codes:
  0  all samples pass
  1  at least one fails (under- or over-detection)
  2  argument or I/O error

Requires Python 3.7+. No third-party dependencies.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import read_json, write_json  # noqa: E402
from prescan import scan as prescan_scan  # noqa: E402

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_CORPUS = SKILL_DIR / "eval-corpus" / "samples"


def evaluate_sample(sample):
    """Run prescan on sample['input'] and compare against expected_hits.

    Returns a dict shaped per schemas.md § eval result.
    """
    expected = sorted({h["pattern"] for h in sample.get("expected_hits", [])})
    detected_hits = prescan_scan(sample["input"])
    detected = sorted({h["pattern"] for h in detected_hits})

    missing = [p for p in expected if p not in detected]
    extra = [p for p in detected if p not in expected]

    return {
        "id": sample["id"],
        "expected_patterns": expected,
        "detected_patterns": detected,
        "missing": missing,
        "extra": extra,
        "pass": not missing and not extra,
    }


def discover_samples(corpus_dir):
    """Return a sorted list of sample file paths."""
    return sorted(Path(corpus_dir).glob("*.json"))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--sample", help="Single sample file to evaluate.")
    parser.add_argument(
        "--corpus",
        default=str(DEFAULT_CORPUS),
        help=f"Corpus directory (default: {DEFAULT_CORPUS})",
    )
    parser.add_argument(
        "--out",
        help="Write the JSON report to a file instead of stdout.",
    )
    args = parser.parse_args()

    try:
        if args.sample:
            sample_paths = [Path(args.sample)]
        else:
            sample_paths = discover_samples(args.corpus)
            if not sample_paths:
                print(
                    f"error: no samples found in {args.corpus}",
                    file=sys.stderr,
                )
                return 2
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    results = []
    for path in sample_paths:
        try:
            sample = read_json(str(path))
            results.append(evaluate_sample(sample))
        except (OSError, ValueError, KeyError) as exc:
            print(f"error reading {path}: {exc}", file=sys.stderr)
            return 2

    passed = sum(1 for r in results if r["pass"])
    total = len(results)
    report = {
        "samples": results,
        "summary": {
            "total_samples": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": (passed / total) if total else 0.0,
        },
    }

    write_json(report, path=args.out)
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
