"""Auto-detect planning artifacts.

Resolves `--reconcile @auto` to the conventional set of planning sources:

    ~/.agents/output/{project}/forge/forge-*.md
    ~/.agents/output/{project}/apex/{task-id}/                 (latest only)
    docs/proposals/*.md  docs/design/*.md  docs/rfcs/*.md  docs/adr/*.md
    PR body of the current branch (via `gh pr view`)

The orchestrator can also accept explicit paths or `gh:pr:<N>` /
`gh:issue:<owner/repo#N>` references — those are resolved by `run.py`,
not here.

Graceful degradation: missing `gh`, missing `~/.agents/output/{project}/`,
or repo with no branch all degrade silently — only the available sources
get returned.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

from ._common import Artifact, freshness_days
from .extractor import detect_artifact_kind

GH_TIMEOUT_S = 5
APEX_TASK_DIR_RE = re.compile(r"^\d+-[a-z0-9][a-z0-9-]*$")


def project_name(repo: Path) -> str:
    """Kebab-cased basename of the git toplevel (or the input dir).

    Same derivation used across the skills' output paths
    (`~/.agents/output/{project}/{skill}/`).
    """
    try:
        r = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=2,
        )
        if r.returncode == 0 and r.stdout.strip():
            root = Path(r.stdout.strip())
        else:
            root = repo.resolve()
    except (subprocess.SubprocessError, OSError):
        root = repo.resolve()
    name = root.name.lower()
    name = re.sub(r"[^a-z0-9]+", "-", name).strip("-")
    return name or "unnamed"


def claude_output_dir(repo: Path) -> Path:
    """`~/.agents/output/{project}/` for the given repo."""
    home = Path(os.environ.get("HOME", "")).expanduser()
    return home / ".agents" / "output" / project_name(repo)


def _glob_artifacts(repo: Path, sub: str, pattern: str, kind: str) -> list:
    out_dir = claude_output_dir(repo) / sub
    if not out_dir.is_dir():
        return []
    results = []
    for path in sorted(out_dir.glob(pattern)):
        if not path.is_file():
            continue
        results.append(_artifact_for(path, kind))
    return results


def _artifact_for(path: Path, kind: str | None = None) -> Artifact:
    return Artifact(
        path=str(path),
        kind=kind or detect_artifact_kind(path),
        freshness_days=freshness_days(path),
    )


def latest_apex_task(repo: Path) -> Artifact | None:
    """Find the most-recent apex task dir under `~/.agents/output/{project}/apex/`.

    The task-id format is `NN-feature-name`. Reverse-sort by name gives
    the highest numbered dir first, which is the latest invocation.
    """
    apex_root = claude_output_dir(repo) / "apex"
    if not apex_root.is_dir():
        return None
    candidates = []
    for d in apex_root.iterdir():
        if d.is_dir() and APEX_TASK_DIR_RE.match(d.name):
            candidates.append(d)
    if not candidates:
        return None
    candidates.sort(reverse=True)
    latest = candidates[0]
    plan_file = latest / "02-plan.md"
    if plan_file.exists():
        return _artifact_for(plan_file, kind="apex-plan")
    return _artifact_for(latest, kind="apex-plan")


def docs_artifacts(repo: Path) -> list:
    """Find planning markdown under `docs/{proposals,design,rfcs,adr}/`."""
    results = []
    docs = repo / "docs"
    if not docs.is_dir():
        return results
    for sub in ("proposals", "design", "rfcs", "adr"):
        sub_dir = docs / sub
        if not sub_dir.is_dir():
            continue
        for path in sorted(sub_dir.glob("*.md")):
            results.append(_artifact_for(path))
    return results


def _gh_available() -> bool:
    return shutil.which("gh") is not None and not os.environ.get("DERIVATION_SKIP_GH")


def current_pr_body(repo: Path) -> Artifact | None:
    """Fetch the current branch's PR body via `gh pr view --json body`."""
    if not _gh_available():
        return None
    try:
        r = subprocess.run(
            ["gh", "pr", "view", "--json", "body", "-q", ".body"],
            cwd=repo, capture_output=True, text=True, timeout=GH_TIMEOUT_S,
        )
    except (subprocess.SubprocessError, OSError):
        return None
    if r.returncode != 0 or not r.stdout.strip():
        return None
    # Materialize the body into a temp-like artifact representation. The
    # body content lives in `Artifact.path` as a sentinel `gh:pr:<branch>`.
    return Artifact(
        path="gh:pr:current",
        kind="pr-body",
        freshness_days=0,  # PR description is by definition current.
    )


def fetch_pr_body_text(repo: Path) -> str:
    """Return the current PR body as text. Returns '' when unavailable."""
    if not _gh_available():
        return ""
    try:
        r = subprocess.run(
            ["gh", "pr", "view", "--json", "body", "-q", ".body"],
            cwd=repo, capture_output=True, text=True, timeout=GH_TIMEOUT_S,
        )
    except (subprocess.SubprocessError, OSError):
        return ""
    if r.returncode != 0:
        return ""
    return r.stdout


def fetch_issue_body_text(owner_repo: str, number: str) -> str:
    """Return an issue body as text via `gh api repos/<o>/<r>/issues/<N>`.

    Used by `run.py` when --reconcile resolves to `gh:issue:owner/repo#N`
    or a GitHub issue URL.
    """
    if not _gh_available():
        return ""
    try:
        r = subprocess.run(
            ["gh", "api", f"repos/{owner_repo}/issues/{number}",
             "--jq", ".body"],
            capture_output=True, text=True, timeout=GH_TIMEOUT_S,
        )
    except (subprocess.SubprocessError, OSError):
        return ""
    if r.returncode != 0:
        return ""
    return r.stdout


def auto_detect(repo: Path, *, include_pr: bool = True) -> list:
    """Resolve `@auto` to a list of artifacts, freshest first.

    Includes only sources that exist. `gh` failures degrade silently —
    callers can detect the gap from the returned list shape.
    """
    artifacts: list = []
    artifacts.extend(_glob_artifacts(repo, "forge", "forge-*.md", "forge"))
    apex = latest_apex_task(repo)
    if apex is not None:
        artifacts.append(apex)
    artifacts.extend(docs_artifacts(repo))
    if include_pr:
        pr = current_pr_body(repo)
        if pr is not None:
            artifacts.append(pr)

    def _sort_key(art: Artifact) -> int:
        # Negative freshness sorts -1 (unknown) last; lower days = fresher.
        return art.freshness_days if art.freshness_days >= 0 else 10**9

    artifacts.sort(key=_sort_key)
    return artifacts
