#!/usr/bin/env python3
"""
validate.py — post-rewrite validation gate for humanize-en.

Runs the deterministic prescan (universal + optional brand) on a file that
has just been rewritten and reports residuals or regressions. Designed to be
called by SKILL.md right after `Edit` applies, before declaring the rewrite
complete.

Usage:
    validate.py <file>
    validate.py --brand path/to/BRAND-VOICE.md <file>
    validate.py --baseline pre-rewrite-hits.json <file>
    validate.py --strict-code-only <file>

Outcomes (stdout JSON):
  status="clean"      — zero hits remain. Rewrite is shippable.
  status="residuals"  — hits remain but no new ones were introduced relative
                        to the baseline. User decides: accept or iterate.
  status="regression" — at least one hit appears that was not in the baseline.
                        Rewrite introduced new tells; revert or fix-forward.

When --baseline is omitted, every remaining hit is reported as a residual
(no regression check possible without a pre-rewrite snapshot).

Output schema (references/schemas.md § validate result):
{
  "path": "<file>",
  "status": "clean" | "residuals" | "regression",
  "residuals": [<prescan-hit>, ...],
  "new_hits": [<prescan-hit>, ...],   # only when status=="regression"
  "summary": {
    "total_residuals": int,
    "universal_residuals": int,
    "brand_residuals": int,
    "new_hit_count": int
  }
}

Exit codes:
  0  status="clean" or status="residuals"
  1  status="regression"
  2  argument or I/O error

Requires Python 3.7+. No third-party dependencies.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from prescan import scan as prescan_scan  # noqa: E402


class _ValidateArgParser(argparse.ArgumentParser):
    def error(self, message):
        print(f"error: {message}", file=sys.stderr)
        print(
            "usage: validate.py <file> [--brand <doc>] [--baseline <hits.json>] [--strict-code-only]",
            file=sys.stderr,
        )
        sys.exit(2)


def _hit_signature(hit):
    """Stable identity for hit-set comparisons. A hit is identified by
    `(pattern, snippet)`.

    Line numbers are deliberately omitted: the rewrite step can shorten or
    lengthen the file, shifting every subsequent line. A signature that
    included the line would treat the same lexical violation at a new line
    number as a regression. The snippet alone (~20 chars on each side of the
    match per `prescan.py:scan`) usually disambiguates same-pattern matches
    that genuinely live in different sentences. Two identical sentences on
    different lines collapse into one signature, which is the right
    trade-off — regressions are about *new* lexical violations appearing,
    not duplicate-count drift."""
    return (
        str(hit.get("pattern")),
        (hit.get("snippet") or "").strip(),
    )


def validate(path, brand_path=None, baseline_hits=None, strict_code_only=False):
    """Re-scan `path` and return a validation result dict per the schema above."""
    text = Path(path).read_text(encoding="utf-8")

    has_brand = bool(brand_path)
    residuals = prescan_scan(text, strict_code_only=strict_code_only, attach_source=has_brand)

    if has_brand:
        from brand_prescan import load_brand_rules, scan_brand
        rules = load_brand_rules(brand_path)
        residuals.extend(scan_brand(text, rules, strict_code_only=strict_code_only))

    universal_count = sum(1 for h in residuals if h.get("source") != "brand")
    brand_count = sum(1 for h in residuals if h.get("source") == "brand")

    new_hits = []
    if baseline_hits is not None:
        baseline_sigs = {_hit_signature(h) for h in baseline_hits}
        new_hits = [h for h in residuals if _hit_signature(h) not in baseline_sigs]

    if not residuals:
        status = "clean"
    elif new_hits:
        status = "regression"
    else:
        status = "residuals"

    result = {
        "path": str(path),
        "status": status,
        "residuals": residuals,
        "summary": {
            "total_residuals": len(residuals),
            "universal_residuals": universal_count,
            "brand_residuals": brand_count,
            "new_hit_count": len(new_hits),
        },
    }
    if status == "regression":
        result["new_hits"] = new_hits
    return result


def main():
    parser = _ValidateArgParser(
        description=(__doc__ or "").split("\n\n")[0],
        prog="validate.py",
    )
    parser.add_argument("path", help="path to the rewritten prose file")
    parser.add_argument("--brand", metavar="<voice-doc>",
                        help="BRAND-VOICE.md to enforce alongside universal patterns")
    parser.add_argument("--baseline", metavar="<hits.json>",
                        help="prescan output captured BEFORE the rewrite, "
                             "for regression detection")
    parser.add_argument("--strict-code-only", action="store_true",
                        help="blank every fenced block (disables pseudo-blocks)")
    args = parser.parse_args()

    target = Path(args.path)
    if not target.is_file():
        print(f"error: file not found: {args.path}", file=sys.stderr)
        return 2

    baseline = None
    if args.baseline:
        baseline_path = Path(args.baseline)
        if not baseline_path.is_file():
            print(f"error: baseline not found: {args.baseline}", file=sys.stderr)
            return 2
        try:
            baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print(f"error: cannot read baseline: {exc}", file=sys.stderr)
            return 2
        if not isinstance(baseline, list):
            print("error: baseline must be a JSON array of prescan hits", file=sys.stderr)
            return 2

    try:
        result = validate(
            str(target),
            brand_path=args.brand,
            baseline_hits=baseline,
            strict_code_only=args.strict_code_only,
        )
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except UnicodeDecodeError as exc:
        print(f"error: file is not valid UTF-8: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: cannot read file: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"error: brand-voice YAML invalid: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["status"] == "regression" else 0


if __name__ == "__main__":
    sys.exit(main())
