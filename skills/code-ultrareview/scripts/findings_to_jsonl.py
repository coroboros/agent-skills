#!/usr/bin/env python3
"""Phase 5 JSONL emitter for code-ultrareview.

Maps canonical findings to Conventional Comments JSONL — one record per
line, ready to pipe through `gh pr comment` or any other line-oriented
consumer. Label routing:

    🔴 High  + correctness | design-api          → "issue"
    🟠 Medium + (most axes)                       → "suggestion"
    🟢 Low   + documentation | style              → "nitpick"
    sub-80 Unverified (any axis)                  → "question"
    every other (severity, axis) pair             → "suggestion"

Permalink format is verbatim from Anthropic's `code-review` plugin:

    https://github.com/<owner>/<repo>/blob/<full-sha>/<path>#L<n>-L<m>

The full SHA is resolved via `git rev-parse HEAD` against the repo root
the caller passes in. When owner/repo cannot be derived (no `origin`
remote, or a non-GitHub URL), the permalink field is omitted from the
record — never guessed.

CLI:
    python3 findings_to_jsonl.py \\
        --findings <validated-findings.jsonl> \\
        --output <report.jsonl> \\
        [--repo-root <path>] [--owner-repo <owner/repo>] [--sha <full-sha>]

Each output line is:

    {"label": str, "axis": str, "severity": str, "confidence": int,
     "location": "<file>:<line>" | "<file>:<start>-<end>", "permalink": str?,
     "finding": str, "recommendation": str,
     "validator_score": int?, "validator_reason": str?}
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable

# Reuse synthesis_core primitives — single source of truth for the 80
# threshold. A divergence here flips JSONL Conventional Comments label
# routing relative to the rest of the pipeline.
_SYNTH_PATH = Path(__file__).resolve().parent / "synthesis_core.py"
_spec = importlib.util.spec_from_file_location("synthesis_core", _SYNTH_PATH)
assert _spec is not None and _spec.loader is not None
synthesis_core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(synthesis_core)

CONFIDENCE_THRESHOLD = synthesis_core.CONFIDENCE_THRESHOLD
GIT_TIMEOUT_S = 10

# Conventional Comments label vocabulary.
LABELS = ("issue", "suggestion", "nitpick", "question")

# Severity-aware routing — keys are (severity, axis) for the unverified
# branch we hard-code separately. Non-listed pairs fall back to "suggestion".
_LABEL_ROUTING: dict[tuple[str, str], str] = {
    ("High", "correctness"): "issue",
    ("High", "design-api"): "issue",
    ("Low", "documentation"): "nitpick",
    ("Low", "style"): "nitpick",
}

# Match `git remote get-url origin` outputs to extract `owner/repo`. Repo
# names may contain `.` (e.g. `react.dev`); the optional `.git` suffix is
# stripped via the trailing group.
_GITHUB_URL_PATTERNS = (
    re.compile(r"^git@github\.com:(?P<owner>[^/]+)/(?P<repo>[^/]+?)(\.git)?$"),
    re.compile(r"^https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(\.git)?/?$"),
)

# `location` shapes the parser accepts:
#   "src/foo.ts:24"           → (src/foo.ts, 24, 24)
#   "src/foo.ts:24-30"        → (src/foo.ts, 24, 30)
#   "src/foo.ts"              → (src/foo.ts, None, None)
_LOCATION_RANGE = re.compile(r"^(?P<path>.+?):(?P<start>\d+)-(?P<end>\d+)$")
_LOCATION_LINE = re.compile(r"^(?P<path>.+?):(?P<start>\d+)$")


# ---------------------------------------------------------------------------
# Label routing
# ---------------------------------------------------------------------------


def label_for(finding: dict) -> str:
    """Pick the Conventional Comments label for one finding.

    Sub-80 findings — surfaced under `### ⚠️ Unverified` by A2 — always
    map to `question` regardless of axis. Severity at intake is the
    A2-downgraded `Low`; the original severity (preserved in
    `meta.original_severity`) is not used for label routing because the
    user-visible report shows the downgraded form.
    """
    confidence = int(finding.get("confidence", 0))
    if confidence < CONFIDENCE_THRESHOLD:
        return "question"
    severity = str(finding.get("severity", ""))
    axis = str(finding.get("axis", ""))
    return _LABEL_ROUTING.get((severity, axis), "suggestion")


# ---------------------------------------------------------------------------
# Permalink construction
# ---------------------------------------------------------------------------


def parse_location(location: str) -> tuple[str, int | None, int | None]:
    """Split a `location` string into (path, start, end). Start = end when
    a single line is given. Returns (path, None, None) when no line info."""
    text = (location or "").strip()
    if not text:
        return ("", None, None)
    m = _LOCATION_RANGE.match(text)
    if m:
        return (m.group("path"), int(m.group("start")), int(m.group("end")))
    m = _LOCATION_LINE.match(text)
    if m:
        return (m.group("path"), int(m.group("start")), int(m.group("start")))
    return (text, None, None)


def make_permalink(
    owner_repo: str | None,
    sha: str | None,
    location: str,
) -> str | None:
    """Build the Anthropic verbatim permalink:

        https://github.com/<owner>/<repo>/blob/<full-sha>/<path>#L<n>-L<m>

    Returns `None` when any required piece is missing — owner/repo,
    SHA, or a parseable `<file>:<line>` location. Single-line locations
    render as `#L<n>-L<n>` (anchor the line range explicitly per the
    plugin spec). Locations without line info render the bare path with
    no fragment (still a valid blob URL).
    """
    if not owner_repo or not sha:
        return None
    path, start, end = parse_location(location)
    if not path:
        return None
    base = f"https://github.com/{owner_repo}/blob/{sha}/{path}"
    if start is None:
        return base
    return f"{base}#L{start}-L{end}"


def detect_owner_repo(repo_root: Path) -> str | None:
    """Read `git remote get-url origin` and extract `owner/repo` when the
    remote points at GitHub. Returns `None` otherwise (skips the
    permalink rather than guessing)."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=GIT_TIMEOUT_S, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    url = result.stdout.strip()
    for pattern in _GITHUB_URL_PATTERNS:
        match = pattern.match(url)
        if match:
            return f"{match.group('owner')}/{match.group('repo')}"
    return None


def detect_sha(repo_root: Path) -> str | None:
    """Resolve the full SHA of `HEAD` via `git rev-parse HEAD`. Returns
    `None` when the resolution fails (not a git repo, detached, etc.)."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=GIT_TIMEOUT_S, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    sha = result.stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        return None
    return sha


# ---------------------------------------------------------------------------
# Record assembly
# ---------------------------------------------------------------------------


def to_record(
    finding: dict,
    owner_repo: str | None = None,
    sha: str | None = None,
) -> dict:
    """Project one canonical finding to its Conventional Comments record.

    Fields preserved verbatim: `axis`, `severity`, `confidence`,
    `location`, `finding`, `recommendation`. Validator-produced fields
    (`validator_score`, `meta.validator_reason`) are surfaced when
    present — consumers want the validator's reason on the same record.
    """
    location = str(finding.get("location", ""))
    record: dict = {
        "label": label_for(finding),
        "axis": str(finding.get("axis", "")),
        "severity": str(finding.get("severity", "")),
        "confidence": int(finding.get("confidence", 0)),
        "location": location,
        "finding": str(finding.get("finding", "")),
        "recommendation": str(finding.get("recommendation", "")),
    }
    permalink = make_permalink(owner_repo, sha, location)
    if permalink is not None:
        record["permalink"] = permalink
    if "validator_score" in finding:
        record["validator_score"] = int(finding["validator_score"])
    meta = finding.get("meta") or {}
    reason = meta.get("validator_reason")
    if reason:
        record["validator_reason"] = str(reason)
    return record


def emit(
    findings: Iterable[dict],
    owner_repo: str | None,
    sha: str | None,
) -> Iterable[str]:
    """Yield one JSON line per finding. Deterministic key order so a
    diff over two runs reads cleanly."""
    for f in findings:
        record = to_record(f, owner_repo=owner_repo, sha=sha)
        yield json.dumps(record, ensure_ascii=False, sort_keys=True)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def load_findings(path: Path) -> list[dict]:
    """Read line-delimited JSON. Blank lines and `#`-comment lines skipped.
    A malformed line raises — fail loud, no silent drop."""
    findings: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for lineno, raw in enumerate(handle, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            try:
                findings.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"{path}:{lineno} — invalid JSON: {exc.msg}"
                ) from exc
    return findings


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--findings", required=True, type=Path,
                        help="Input findings JSONL (post-validator).")
    parser.add_argument("--output", type=Path,
                        help="Output JSONL path. Default: stdout.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(),
                        help="Repo root for owner/repo + SHA detection.")
    parser.add_argument("--owner-repo", default=None,
                        help="Override owner/repo (skip git remote lookup).")
    parser.add_argument("--sha", default=None,
                        help="Override full SHA (skip git rev-parse).")
    args = parser.parse_args(argv)

    owner_repo = args.owner_repo or detect_owner_repo(args.repo_root)
    sha = args.sha or detect_sha(args.repo_root)
    findings = load_findings(args.findings)
    lines = list(emit(findings, owner_repo=owner_repo, sha=sha))

    if args.output is None:
        for line in lines:
            print(line)
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + ("\n" if lines else ""),
                           encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
