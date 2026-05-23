#!/usr/bin/env python3
"""Audit-phase signal extractor for code-ultrareview.

Computes deterministic signals from a git diff and emits them as JSON.
`audit_summary.py` consumes the output to format the report-header Scope
and Estimated wall-clock block. The fan-out runs at full strength either
way — signals are informational, not gating.

Two review modes:
    - clean tree: `git diff <base> <target>` (two-dot).
    - dirty tree: `git diff HEAD` plus every untracked file (each read in
      full, counted as all-added). A fresh untracked module is never
      silently skipped — the report header reflects the real diff.

The script is stdlib-only and subprocess-driven, mirroring the posture of
`resolve_base.sh`: failures are loud (exit 2), output is machine-readable.

Usage:
    python3 audit_signals.py --base <ref> [--target <ref>] [--repo <path>] [--json]
    python3 audit_signals.py --dirty-tree [--repo <path>] [--json]
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

SPEC_REGEX = re.compile(
    r"\b(RFC\s?\d+|WHATWG|ISO/IEC\s?\d+|OpenAPI|IETF)\b"
)
SECURITY_PATH_REGEX = re.compile(
    r"(auth|crypto|secret|password|token|jwt|oauth|tls|ssl)", re.IGNORECASE
)
FREEZE_COMMIT_REGEX = re.compile(r"\b(freeze|rc\d*|beta\d*)\b", re.IGNORECASE)
TEST_PATH_HINTS = ("test_", "_test.")
TEST_PATH_DIRS = ("/tests/", "/test/", "tests/", "test/")
TEST_PATH_SUFFIXES = (".test.ts", ".test.js", ".test.tsx", ".spec.ts", ".spec.js")
ROUTE_PATH_HINTS = ("route.ts", "route.js", "routes.ts", "routes.js")
MANIFEST_FILES = ("package.json", "marketplace.json", "README.md", "SKILL.md")
GIT_TIMEOUT_S = 30


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, check=False, timeout=GIT_TIMEOUT_S,
    )


def _untracked_files(repo: Path) -> list[str]:
    """Return paths reported by `git ls-files --others --exclude-standard`."""
    r = run_git(repo, "ls-files", "--others", "--exclude-standard")
    if r.returncode != 0:
        return []
    return [line for line in r.stdout.splitlines() if line]


def _file_line_count(path: Path) -> int:
    """Line count of `path`, or 0 on any error."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


def _parse_numstat(stdout: str, loc: int, files: list, added_per_file: dict):
    """Fold one `git diff --numstat` output block into the accumulators."""
    for line in stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        added_s, deleted_s, path = parts
        try:
            added = 0 if added_s == "-" else int(added_s)
            deleted = 0 if deleted_s == "-" else int(deleted_s)
        except ValueError:
            continue
        loc += added + deleted
        if path not in added_per_file:
            files.append(path)
        added_per_file[path] = added
    return loc


def diff_numstat(repo: Path, base: str, target: str, *, dirty_tree: bool = False):
    """Return (total_loc_changed, files_list, per_file_added_dict).

    Clean tree: numstat of `base..target`.
    Dirty tree: numstat of `HEAD` (tracked changes) plus every untracked
    file (counted as all-added LOC). `base`/`target` are ignored when
    `dirty_tree=True`.
    """
    loc = 0
    files: list[str] = []
    added_per_file: dict[str, int] = {}

    if dirty_tree:
        r = run_git(repo, "diff", "--numstat", "HEAD")
    else:
        r = run_git(repo, "diff", "--numstat", f"{base}..{target}")
    if r.returncode == 0:
        loc = _parse_numstat(r.stdout, loc, files, added_per_file)

    if dirty_tree:
        for path in _untracked_files(repo):
            full = repo / path
            if not full.is_file():
                continue
            n = _file_line_count(full)
            loc += n
            if path not in added_per_file:
                files.append(path)
            added_per_file[path] = added_per_file.get(path, 0) + n

    return loc, files, added_per_file


def diff_content(repo: Path, base: str, target: str, *, dirty_tree: bool = False) -> str:
    """Full diff content. For dirty tree: `git diff HEAD` plus the body of
    every untracked file inlined as `+`-prefixed lines so downstream regexes
    (`detect_public_api`, `detect_normative_spec`) see untracked work."""
    if dirty_tree:
        r = run_git(repo, "diff", "HEAD")
    else:
        r = run_git(repo, "diff", f"{base}..{target}")
    content = r.stdout if r.returncode == 0 else ""

    if dirty_tree:
        for path in _untracked_files(repo):
            full = repo / path
            if not full.is_file():
                continue
            try:
                text = full.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            content += f"\n+++ b/{path}\n"
            for line in text.splitlines():
                content += f"+{line}\n"
    return content


def is_test_path(path: str) -> bool:
    p = path.lower()
    if any(p.endswith(s) for s in TEST_PATH_SUFFIXES):
        return True
    if any(d in p for d in TEST_PATH_DIRS):
        return True
    name = Path(p).name
    return any(name.startswith(h) or h in name for h in TEST_PATH_HINTS)


def detect_public_api(files: list[str], content: str) -> bool:
    for f in files:
        if Path(f).parent == Path(".") and f.endswith(".md"):
            return True
        if Path(f).name in ("SKILL.md", "marketplace.json"):
            return True
        if any(hint in f.lower() for hint in ROUTE_PATH_HINTS):
            return True
        if "/routes/" in f or "/pages/" in f or "/app/" in f.lower():
            return True
    for line in content.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            stripped = line[1:].lstrip()
            if stripped.startswith(("export ", "export\t", "export\n")):
                return True
    return False


def detect_normative_spec(repo: Path, content: str) -> tuple[bool, list[str]]:
    matches: set[str] = set()
    matches.update(SPEC_REGEX.findall(content))
    for candidate in ("README.md", "CLAUDE.md"):
        p = repo / candidate
        if p.exists():
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
                matches.update(SPEC_REGEX.findall(text))
            except OSError:
                continue
    return bool(matches), sorted(matches)


def detect_manifest_delta(files: list[str]) -> bool:
    return any(Path(f).name in MANIFEST_FILES for f in files)


def _read_json_safe(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _version_from(data) -> str:
    if not isinstance(data, dict):
        return ""
    version = data.get("version")
    if not version:
        meta = data.get("metadata") or {}
        version = meta.get("version", "") if isinstance(meta, dict) else ""
    return str(version) if version else ""


def detect_pre_1_0_or_freeze(repo: Path) -> bool:
    candidates = [
        repo / "package.json",
        repo / ".claude-plugin" / "marketplace.json",
        repo / "marketplace.json",
    ]
    for p in candidates:
        if not p.exists():
            continue
        data = _read_json_safe(p)
        version = _version_from(data)
        if version.startswith("0."):
            return True
    r = run_git(repo, "log", "-20", "--format=%s")
    if r.returncode == 0:
        for line in r.stdout.splitlines():
            if FREEZE_COMMIT_REGEX.search(line):
                return True
    return False


def compute_test_coverage_delta(files: list[str], added_per_file: dict[str, int]) -> float:
    test_loc = 0
    code_loc = 0
    for f in files:
        n = added_per_file.get(f, 0)
        if n <= 0:
            continue
        if is_test_path(f):
            test_loc += n
        else:
            code_loc += n
    if code_loc == 0:
        return 0.0
    return round(test_loc / code_loc, 3)


def detect_security_paths(files: list[str]) -> bool:
    return any(SECURITY_PATH_REGEX.search(f) for f in files)


_APEX_TASK_RE = re.compile(r"^\d+-")


def _project_name(repo: Path) -> str:
    name = repo.name.lower()
    return re.sub(r"[^a-z0-9]+", "-", name).strip("-") or "unnamed"


def detect_planning_artifacts(repo: Path) -> tuple[int, int]:
    """Count planning artifacts in the conventional set + min freshness days.

    Mirrors derivation's @auto detection at a lighter weight (mtime-based
    freshness, no `gh pr view` call — the audit phase stays offline).
    Returns `(count, min_freshness_days)`. `(0, -1)` when none found.
    """
    home_str = os.environ.get("HOME") or ""
    home = Path(home_str).expanduser() if home_str else Path()
    project = _project_name(repo)
    output_root = home / ".claude" / "output" / project

    candidates: list[Path] = []

    fd = output_root / "forge"
    if fd.is_dir():
        candidates.extend(p for p in fd.glob("forge-*.md") if p.is_file())

    ad = output_root / "apex"
    if ad.is_dir():
        task_dirs = sorted(
            [d for d in ad.iterdir() if d.is_dir() and _APEX_TASK_RE.match(d.name)],
            reverse=True,
        )
        if task_dirs:
            plan = task_dirs[0] / "02-plan.md"
            if plan.is_file():
                candidates.append(plan)

    for sub in ("proposals", "design", "rfcs", "adr"):
        d = repo / "docs" / sub
        if d.is_dir():
            candidates.extend(p for p in d.glob("*.md") if p.is_file())

    if not candidates:
        return (0, -1)

    now = time.time()
    ages: list[int] = []
    for p in candidates:
        try:
            ts = os.path.getmtime(p)
        except OSError:
            continue
        ages.append(max(0, int((now - ts) // 86400)))

    if not ages:
        return (len(candidates), -1)
    return (len(candidates), min(ages))


def audit(repo: Path, base: str, target: str, *, dirty_tree: bool = False) -> dict:
    loc, files, added_per_file = diff_numstat(repo, base, target, dirty_tree=dirty_tree)
    content = diff_content(repo, base, target, dirty_tree=dirty_tree)
    spec_found, spec_list = detect_normative_spec(repo, content)
    artifact_count, artifact_min_freshness = detect_planning_artifacts(repo)
    return {
        "loc_changed": loc,
        "files_touched": len(files),
        "files_touched_list": files,
        "public_api_touched": detect_public_api(files, content),
        "normative_spec_mentioned": spec_found,
        "normative_specs_list": spec_list,
        "manifest_graph_delta": detect_manifest_delta(files),
        "pre_1_0_or_freeze": detect_pre_1_0_or_freeze(repo),
        "test_coverage_delta": compute_test_coverage_delta(files, added_per_file),
        "security_sensitive_paths": detect_security_paths(files),
        "planning_artifact_breadth": [artifact_count, artifact_min_freshness],
        "dirty_tree": dirty_tree,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit-phase signal extractor for code-ultrareview"
    )
    parser.add_argument("--base", help="base ref (e.g., HEAD~5, origin/main)")
    parser.add_argument("--target", default="HEAD", help="target ref (default: HEAD)")
    parser.add_argument("--dirty-tree", action="store_true",
                        help="Review uncommitted work: git diff HEAD plus every untracked file. "
                             "When set, --base and --target are ignored.")
    parser.add_argument("--repo", default=".", help="repo path (default: cwd)")
    parser.add_argument("--json", action="store_true", help="emit JSON (default behavior)")
    args = parser.parse_args()

    if not args.dirty_tree and not args.base:
        parser.error("--base is required (or pass --dirty-tree for uncommitted work)")

    repo = Path(args.repo).resolve()
    if not (repo / ".git").exists() and not (repo / ".git").is_file():
        print(f"ERROR: {repo} is not a git repo", file=sys.stderr)
        return 2

    try:
        result = audit(repo, args.base or "HEAD", args.target,
                       dirty_tree=args.dirty_tree)
    except subprocess.TimeoutExpired as exc:
        print(f"ERROR: git timed out: {exc.cmd}", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
