#!/usr/bin/env python3
"""
eval_patterns.py — score prescan against the eval corpus.

Usage:
    eval_patterns.py                           # universal corpus (eval-corpus/samples/*.json)
    eval_patterns.py --brand                   # brand corpus (eval-corpus/brand-voice/*.json)
    eval_patterns.py --sample <path.json>      # single sample (auto-detects brand)
    eval_patterns.py --corpus <dir>            # custom corpus directory

Runs the deterministic scan on each sample's `input` and compares the
detected patterns against `expected_hits`. Universal samples reference
patterns by integer ID (1-32); brand samples reference them by string slug
("brand:all_caps_emphasis", etc.) and may inline a `brand_voice_yaml` to
exercise brand-aware detection.

Exit codes:
  0  all samples pass
  1  at least one fails (under- or over-detection)
  2  argument or I/O error

Requires Python 3.7+. No third-party dependencies.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import read_json, write_json  # noqa: E402
from prescan import scan as prescan_scan  # noqa: E402

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_CORPUS = SKILL_DIR / "eval-corpus" / "samples"
BRAND_CORPUS = SKILL_DIR / "eval-corpus" / "brand-voice"


def evaluate_sample(sample):
    """Run prescan on sample['input'] and compare against expected_hits.

    When the sample carries `brand_voice_yaml`, also run brand-aware detection
    and compare both universal pattern numbers (ints) and brand pattern slugs
    (strings) against the expected set.

    Returns a dict shaped per schemas.md § eval result. The `pass` field is
    True when missing == [] AND extra == []."""
    expected = sorted({h["pattern"] for h in sample.get("expected_hits", [])},
                      key=lambda x: (isinstance(x, str), x))

    has_brand = bool(sample.get("brand_voice_yaml"))
    detected_hits = prescan_scan(sample["input"], attach_source=has_brand)

    if has_brand:
        from brand_prescan import load_brand_rules, scan_brand
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".md", delete=False, encoding="utf-8"
            ) as tmp:
                tmp.write("---\n" + sample["brand_voice_yaml"] + "---\n")
                tmp.write("\n# Test\n\n## 1. Core voice attributes\n\nstub\n")
                tmp_path = tmp.name
            rules = load_brand_rules(tmp_path)
            detected_hits.extend(scan_brand(sample["input"], rules))
        finally:
            if tmp_path is not None:
                try:
                    Path(tmp_path).unlink()
                except FileNotFoundError:
                    pass

    detected = sorted({h["pattern"] for h in detected_hits},
                      key=lambda x: (isinstance(x, str), x))

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
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument("--sample", help="Single sample file to evaluate.")
    parser.add_argument(
        "--corpus",
        default=None,
        help=f"Corpus directory (default: {DEFAULT_CORPUS} or "
             f"{BRAND_CORPUS} when --brand is set)",
    )
    parser.add_argument(
        "--brand",
        action="store_true",
        help="Run the brand-voice corpus instead of the universal corpus. "
             "Equivalent to --corpus eval-corpus/brand-voice.",
    )
    parser.add_argument(
        "--out",
        help="Write the JSON report to a file instead of stdout.",
    )
    args = parser.parse_args()

    if args.corpus is None:
        args.corpus = str(BRAND_CORPUS if args.brand else DEFAULT_CORPUS)

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
