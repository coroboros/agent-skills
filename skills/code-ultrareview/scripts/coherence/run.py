#!/usr/bin/env python3
"""Coherence-graph orchestrator.

Runs all six sub-graph extractors and emits a unified JSON findings list.
Reads `.coherence-ignore` from the repo root and applies the allowlist
per sub-graph.

Usage:
    python3 run.py --repo <path> [--include-prose] [--json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow `python3 run.py ...` direct invocation by adding the parent dir to sys.path
if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from coherence import (  # type: ignore[no-redef]
        _common,
        capability_graph,
        cross_reference_graph,
        description_graph,
        example_graph,
        spec_conformance_graph,
        version_graph,
    )
else:
    from . import (
        _common,
        capability_graph,
        cross_reference_graph,
        description_graph,
        example_graph,
        spec_conformance_graph,
        version_graph,
    )


SUB_GRAPHS = (
    ("description", description_graph),
    ("version", version_graph),
    ("capability", capability_graph),
    ("cross-reference", cross_reference_graph),
    ("example", example_graph),
    ("spec-conformance", spec_conformance_graph),
)


def run_all(repo: Path, include_prose: bool = False) -> list[dict]:
    ignore = _common.load_ignore(repo)
    findings: list[dict] = []
    for name, module in SUB_GRAPHS:
        kwargs = {"include_prose": include_prose} if name == "description" else {}
        try:
            sub_findings = module.run(repo, ignore, **kwargs)
        except Exception as exc:
            findings.append(_common.Finding(
                sub_graph=name, severity="Low",
                location=f"(sub-graph {name})",
                finding=f"Sub-graph crashed: {exc!r}",
                recommendation="Investigate the extractor; degrade gracefully if persistent.",
                confidence=0,
            ).to_dict())
            continue
        for f in sub_findings:
            findings.append(f.to_dict())
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Coherence-graph lens — cross-artifact drift detector"
    )
    parser.add_argument("--repo", default=".", help="repo path (default: cwd)")
    parser.add_argument("--include-prose", action="store_true",
                        help="Also compare README prose against structured descriptions")
    parser.add_argument("--json", action="store_true",
                        help="Emit JSON (default behavior)")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.exists():
        print(f"ERROR: repo path does not exist: {repo}", file=sys.stderr)
        return 2

    try:
        findings = run_all(repo, include_prose=args.include_prose)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(json.dumps({"lens": "coherence-graph", "findings": findings}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
