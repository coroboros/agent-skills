#!/usr/bin/env python3
"""Derivation lens orchestrator.

Resolves `--reconcile` inputs to a list of planning artifacts, extracts
claims from each, and emits the canonical derivation-lens output: a list
of artifacts (with freshness + claim count) plus an UNCLASSIFIED finding
per claim. Classification (GAP / SCOPE-ADD / DECISION-OVERRIDE /
CONSISTENT) happens downstream in the dispatched Explore subagent — this
module owns deterministic structure + finding shape only.

Usage:
    python3 run.py --repo <path> --reconcile <input>[,<input>...] [--strict] [--json]

Input forms:
    @auto            — auto-detect at conventional paths
    @pr              — current branch's PR body (via `gh pr view`)
    <path>           — explicit file or directory
    gh:pr:<N>        — PR by number (current repo, via `gh`)
    gh:issue:owner/repo#N — issue by ref (via `gh api`)
    https://github.com/owner/repo/issues/N — issue URL (parsed → gh api)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Allow `python3 run.py ...` direct invocation by adding the parent dir to sys.path.
if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from derivation._common import (  # type: ignore[no-redef]
        Artifact,
        Finding,
        IgnoreFile,
        UNCLASSIFIED,
        DEFAULT_SEVERITY,
        classify_severity_by_freshness,
        freshness_days,
        load_ignore,
        should_emit_findings,
    )
    from derivation.auto_detect import (  # type: ignore[no-redef]
        auto_detect,
        fetch_issue_body_text,
        fetch_pr_body_text,
    )
    from derivation.extractor import (  # type: ignore[no-redef]
        detect_artifact_kind,
        extract_claims,
    )
else:
    from ._common import (
        Artifact,
        Finding,
        IgnoreFile,
        UNCLASSIFIED,
        DEFAULT_SEVERITY,
        classify_severity_by_freshness,
        freshness_days,
        load_ignore,
        should_emit_findings,
    )
    from .auto_detect import (
        auto_detect,
        fetch_issue_body_text,
        fetch_pr_body_text,
    )
    from .extractor import detect_artifact_kind, extract_claims

ISSUE_URL_RE = re.compile(
    r"https?://github\.com/([^/]+/[^/]+)/issues/(\d+)"
)
GH_ISSUE_REF_RE = re.compile(r"gh:issue:([^/]+/[^/]+)#(\d+)")
GH_PR_REF_RE = re.compile(r"gh:pr:(\d+)")


def resolve_inputs(repo: Path, inputs: list) -> list:
    """Turn a list of --reconcile tokens into Artifact objects.

    Each input may be `@auto`, `@pr`, a path, `gh:pr:<N>`, `gh:issue:<ref>`,
    or a GitHub issue URL. Missing/unfetchable inputs are silently skipped
    — the orchestrator can detect the gap from the resulting list.
    """
    seen: set = set()
    artifacts: list = []

    def _add(art: Artifact):
        if art.path in seen:
            return
        seen.add(art.path)
        artifacts.append(art)

    for token in inputs:
        token = token.strip()
        if not token:
            continue
        if token == "@auto":
            for art in auto_detect(repo):
                _add(art)
            continue
        if token == "@pr":
            body = fetch_pr_body_text(repo)
            if body:
                _add(Artifact(path="gh:pr:current", kind="pr-body", freshness_days=0))
            continue
        m = GH_PR_REF_RE.match(token)
        if m:
            _add(Artifact(path=f"gh:pr:{m.group(1)}", kind="pr-body", freshness_days=0))
            continue
        m = GH_ISSUE_REF_RE.match(token) or ISSUE_URL_RE.match(token)
        if m:
            owner_repo, number = m.group(1), m.group(2)
            _add(Artifact(
                path=f"gh:issue:{owner_repo}#{number}",
                kind="issue-body",
                freshness_days=-1,
            ))
            continue
        # Otherwise treat as a path.
        path = Path(token).expanduser()
        if not path.is_absolute():
            path = (repo / path).resolve()
        if path.is_file():
            _add(Artifact(
                path=str(path),
                kind=detect_artifact_kind(path),
                freshness_days=freshness_days(path),
            ))
        elif path.is_dir():
            for child in sorted(path.glob("*.md")):
                _add(Artifact(
                    path=str(child),
                    kind=detect_artifact_kind(child),
                    freshness_days=freshness_days(child),
                ))
    return artifacts


def _read_artifact_text(artifact: Artifact, repo: Path) -> str:
    """Return the textual contents of the artifact."""
    if artifact.path.startswith("gh:pr:"):
        return fetch_pr_body_text(repo)
    if artifact.path.startswith("gh:issue:"):
        rest = artifact.path[len("gh:issue:") :]
        owner_repo, number = rest.split("#", 1)
        return fetch_issue_body_text(owner_repo, number)
    try:
        return Path(artifact.path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _path_matches(entry: str, artifact_path: str) -> bool:
    """Path-allowlist matching.

    Absolute or `~`-prefixed entries match by exact path (after expanding
    `~`). Relative entries match when the artifact path equals the entry,
    ends with `/<entry>`, or its basename equals the entry — covers the
    common cases (`spec.md` matches `/tmp/foo/spec.md`).
    """
    import os.path as _p
    expanded = _p.expanduser(entry)
    if expanded == artifact_path:
        return True
    if entry.startswith("/") or entry.startswith("~"):
        return False
    if artifact_path == entry:
        return True
    if artifact_path.endswith("/" + entry):
        return True
    if _p.basename(artifact_path) == entry:
        return True
    return False


def _ignore_match(ignore: IgnoreFile, artifact: Artifact, claim_text: str) -> bool:
    """Check `.derivation-ignore` for path / kind / claim allowlists."""
    for entry in ignore.list_for("paths", "ignore_paths"):
        if _path_matches(entry, artifact.path):
            return True
    if ignore.has("paths", "ignore_kinds", artifact.kind):
        return True
    if ignore.has("claims", "ignore_text", claim_text):
        return True
    return False


def run(repo: Path, inputs: list, ignore: IgnoreFile,
        *, strict: bool = False) -> dict:
    """Emit derivation-lens output for the given repo + inputs.

    The output schema:
        {
          "lens": "derivation",
          "artifacts": [
              {"path": str, "kind": str, "freshness_days": int, "claim_count": int}
          ],
          "findings": [
              {"lens": "derivation", "classification": "UNCLASSIFIED",
               "severity": ..., "location": "<artifact>:<source_line>",
               "finding": "<claim text>", "recommendation": ..., ...}
          ]
        }

    Each finding represents one claim awaiting LLM classification.
    Artifacts older than the summary-only threshold emit no findings —
    only the artifact entry shows in the summary.
    """
    artifacts = resolve_inputs(repo, inputs)
    art_summary: list = []
    findings: list = []
    for artifact in artifacts:
        text = _read_artifact_text(artifact, repo)
        claims = extract_claims(text) if text else []
        art_summary.append({
            "path": artifact.path,
            "kind": artifact.kind,
            "freshness_days": artifact.freshness_days,
            "claim_count": len(claims),
        })
        if not claims:
            continue
        if not should_emit_findings(artifact.freshness_days) and not strict:
            continue
        # Cap to ≤5 findings per artifact (Risk #2 — overcorrection guard).
        emitted = 0
        for claim in claims:
            if emitted >= 5 and not strict:
                break
            if _ignore_match(ignore, artifact, claim.text):
                continue
            severity = classify_severity_by_freshness(
                DEFAULT_SEVERITY[UNCLASSIFIED], artifact.freshness_days,
            )
            findings.append(Finding(
                classification=UNCLASSIFIED,
                severity=severity,
                location=f"{artifact.path}:{claim.source_line}",
                finding=claim.text,
                recommendation=(
                    f"Compare this {claim.kind} against the diff. "
                    "Classify as GAP / SCOPE-ADD / DECISION-OVERRIDE / CONSISTENT."
                ),
                confidence=0,
                artifact_path=artifact.path,
                artifact_freshness_days=artifact.freshness_days,
            ).to_dict())
            emitted += 1
    return {
        "lens": "derivation",
        "artifacts": art_summary,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Derivation lens — reconcile planning artifacts against the diff"
    )
    parser.add_argument("--repo", required=True, help="Repository root")
    parser.add_argument(
        "--reconcile", default="@auto",
        help="Comma-separated list of inputs (@auto / @pr / path / gh:pr:N / gh:issue:owner/repo#N / URL)",
    )
    parser.add_argument("--strict", action="store_true",
                        help="Disable freshness-based finding suppression + cap")
    parser.add_argument("--json", action="store_true",
                        help="Emit JSON (default; flag retained for symmetry with coherence lens)")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir():
        print(f"--repo path does not exist or is not a directory: {repo}",
              file=sys.stderr)
        return 2

    inputs = [tok.strip() for tok in args.reconcile.split(",") if tok.strip()]
    ignore = load_ignore(repo)
    result = run(repo, inputs, ignore, strict=args.strict)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
