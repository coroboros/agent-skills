#!/usr/bin/env python3
"""Derivation lens orchestrator.

Resolves `--reconcile` inputs to a list of planning artifacts, extracts
claims from each, and emits the canonical derivation-lens output: a list
of artifacts (with freshness + claim count) plus an UNCLASSIFIED finding
per claim. Classification (GAP / SCOPE-ADD / DECISION-OVERRIDE /
CONSISTENT) happens downstream in the dispatched Explore subagent — this
module owns deterministic structure + finding shape only.

Usage:
    python3 run.py --repo <path> --scope <scope.json> --output <result.json> \
        --reconcile <input>[,<input>...] [--strict] [--json]

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

_SCRIPT_ROOT = Path(__file__).resolve().parent.parent
if str(_SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_ROOT))
from coverage import file_identity, set_phase, write_json_atomic  # noqa: E402

# Allow `python3 run.py ...` direct invocation by adding the parent dir to sys.path.
if __package__ is None or __package__ == "":
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


def _set_reconcile_coverage(
    scope_path: Path,
    *,
    status: str,
    complete: bool,
    output_path: Path,
    finding_count: int | None = None,
) -> None:
    coverage = {
        "requested": True,
        "complete": complete,
        "status": status,
        "output": str(output_path.resolve()),
    }
    if complete:
        identity = file_identity(output_path)
        coverage.update({"sha256": identity["sha256"], "bytes": identity["bytes"]})
    if finding_count is not None:
        coverage["finding_count"] = finding_count
    set_phase(scope_path, "reconcile", coverage)


class ReconcilePrerequisiteError(RuntimeError):
    pass


class ReconcileCoverageError(RuntimeError):
    pass


def resolve_inputs(repo: Path, inputs: list) -> list:
    """Turn a list of --reconcile tokens into Artifact objects.

    Each input may be `@auto`, `@pr`, a path, `gh:pr:<N>`, `gh:issue:<ref>`,
    or a GitHub issue URL. Every explicit input is marked required so a
    missing source or an extraction failure blocks before synthesis.
    """
    seen: set = set()
    artifacts: list = []

    def _add(art: Artifact):
        if art.path in seen:
            if art.required:
                for existing in artifacts:
                    if existing.path == art.path:
                        existing.required = True
                        break
            return
        seen.add(art.path)
        artifacts.append(art)

    for token in inputs:
        token = token.strip()
        if not token:
            continue
        if token == "@auto":
            detected = auto_detect(repo)
            if not detected:
                raise ReconcilePrerequisiteError(
                    "@auto found no planning artifact or current pull request"
                )
            for art in detected:
                _add(art)
            continue
        if token == "@pr":
            _add(Artifact(
                path="gh:pr:current", kind="pr-body", freshness_days=0,
                required=True,
            ))
            continue
        m = GH_PR_REF_RE.match(token)
        if m:
            _add(Artifact(
                path=f"gh:pr:{m.group(1)}", kind="pr-body", freshness_days=0,
                required=True,
            ))
            continue
        m = GH_ISSUE_REF_RE.match(token) or ISSUE_URL_RE.match(token)
        if m:
            owner_repo, number = m.group(1), m.group(2)
            _add(Artifact(
                path=f"gh:issue:{owner_repo}#{number}",
                kind="issue-body",
                freshness_days=-1,
                required=True,
            ))
            continue
        path = Path(token).expanduser()
        if not path.is_absolute():
            path = (repo / path).resolve()
        if path.is_file():
            _add(Artifact(
                path=str(path),
                kind=detect_artifact_kind(path),
                freshness_days=freshness_days(path),
                required=True,
            ))
        elif path.is_dir():
            children = sorted(path.glob("*.md"))
            if not children:
                raise ReconcilePrerequisiteError(
                    f"requested directory contains no Markdown artifacts: {path}"
                )
            for child in children:
                _add(Artifact(
                    path=str(child),
                    kind=detect_artifact_kind(child),
                    freshness_days=freshness_days(child),
                    required=True,
                ))
        else:
            raise ReconcilePrerequisiteError(
                f"requested reconcile path does not exist: {path}"
            )
    return artifacts


def _read_artifact_text(artifact: Artifact, repo: Path) -> str:
    """Return the textual contents of the artifact."""
    if artifact.path.startswith("gh:pr:"):
        number = artifact.path.removeprefix("gh:pr:")
        return fetch_pr_body_text(repo, None if number == "current" else number)
    if artifact.path.startswith("gh:issue:"):
        rest = artifact.path[len("gh:issue:") :]
        owner_repo, number = rest.split("#", 1)
        return fetch_issue_body_text(owner_repo, number)
    try:
        return Path(artifact.path).read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return ""


def _validate_resolved_artifact(artifact: Artifact, text: str) -> None:
    if not text.strip():
        raise ReconcilePrerequisiteError(
            f"resolved reconcile source is unavailable or empty: {artifact.path}"
        )
    lines = text.splitlines()
    if lines and lines[0].strip() == "---" and not any(
        line.strip() == "---" for line in lines[1:]
    ):
        raise ReconcileCoverageError(
            f"requested reconcile source has unclosed frontmatter: {artifact.path}"
        )


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
    total_claims = 0
    for artifact in artifacts:
        text = _read_artifact_text(artifact, repo)
        _validate_resolved_artifact(artifact, text)
        claims = extract_claims(text) if text else []
        total_claims += len(claims)
        if artifact.required and not claims:
            raise ReconcileCoverageError(
                "requested reconcile source contains no extractable Acceptance "
                f"criteria, Goals, Decisions, or Tasks: {artifact.path}"
            )
        art_summary.append({
            "path": artifact.path,
            "kind": artifact.kind,
            "freshness_days": artifact.freshness_days,
            "claim_count": len(claims),
        })
        if not claims:
            continue
        if (
            not artifact.required
            and not should_emit_findings(artifact.freshness_days)
            and not strict
        ):
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
    if total_claims == 0:
        raise ReconcileCoverageError(
            "resolved reconcile sources contain no extractable Acceptance "
            "criteria, Goals, Decisions, or Tasks"
        )
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
    parser.add_argument("--scope", required=True, help="scope.json from Phase 1")
    parser.add_argument(
        "--output", required=True,
        help="Atomic derivation JSON consumed by the Intent-axis bundle",
    )
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
    scope_path = Path(args.scope).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    if not repo.is_dir():
        print(f"--repo path does not exist or is not a directory: {repo}",
              file=sys.stderr)
        return 2
    if not scope_path.is_file():
        print(f"--scope path does not exist or is not a file: {scope_path}",
              file=sys.stderr)
        return 2

    inputs = [tok.strip() for tok in args.reconcile.split(",") if tok.strip()]
    if not inputs:
        print("--reconcile requires at least one source", file=sys.stderr)
        return 2
    try:
        _set_reconcile_coverage(
            scope_path,
            status="preflight",
            complete=False,
            output_path=output_path,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot initialize reconcile coverage: {exc}", file=sys.stderr)
        return 2
    try:
        ignore = load_ignore(repo)
        result = run(repo, inputs, ignore, strict=args.strict)
    except ReconcilePrerequisiteError as exc:
        try:
            _set_reconcile_coverage(
                scope_path,
                status="blocked",
                complete=False,
                output_path=output_path,
            )
        except (OSError, ValueError, json.JSONDecodeError):
            pass
        print(f"ERROR: {exc}", file=sys.stderr)
        print(
            "ERROR: remediation: restore/correct the source; for GitHub sources "
            "install `gh`, run `gh auth login`, verify the reference, then rerun "
            "Code Ultrareview with the same --reconcile value.",
            file=sys.stderr,
        )
        return 3
    except (ReconcileCoverageError, ValueError) as exc:
        try:
            _set_reconcile_coverage(
                scope_path,
                status="failed",
                complete=False,
                output_path=output_path,
            )
        except (OSError, ValueError, json.JSONDecodeError):
            pass
        print(f"ERROR: reconcile coverage is incomplete: {exc}", file=sys.stderr)
        print(
            "ERROR: remediation: repair the planning artifact or ignore file, "
            "then rerun Code Ultrareview with the same --reconcile value.",
            file=sys.stderr,
        )
        return 4
    try:
        write_json_atomic(output_path, result)
        data = output_path.read_bytes()
        _set_reconcile_coverage(
            scope_path,
            status="complete",
            complete=True,
            output_path=output_path,
            finding_count=len(result.get("findings") or []),
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: reconcile result could not be persisted: {exc}", file=sys.stderr)
        return 4
    sys.stdout.buffer.write(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
