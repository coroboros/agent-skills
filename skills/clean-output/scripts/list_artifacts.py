#!/usr/bin/env python3
"""Enumerate artifacts under ~/.claude/output/ — per-project + _global buckets.

Emits a JSON array on stdout:
    [{"bucket", "project", "skill", "path", "size_bytes", "mtime_iso"}, ...]

`bucket` ∈ {"project", "_global"}. `project` is the kebab-cased name for
"project" rows; null for "_global" rows. Files and top-level directories
inside each `<skill>/` folder are each counted as one artifact — for a
directory, `size_bytes` sums every nested file and `mtime_iso` is the most
recent file's mtime (UTC ISO 8601).

Stdlib only. Python 3.10+.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path


def detect_current_project(cwd: Path) -> str:
    """Mirror the shell snippet in `.claude/rules/repo-conventions.md` § Output paths:
    `git rev-parse --show-toplevel 2>/dev/null || pwd` → kebab-case basename →
    fallback `unnamed`."""
    basename = cwd.name
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            cwd=str(cwd),
        )
        if result.returncode == 0 and result.stdout.strip():
            basename = Path(result.stdout.strip()).name
    except (FileNotFoundError, OSError):
        pass  # git missing — fall back to cwd basename

    kebab = re.sub(r"[^a-z0-9]+", "-", basename.lower()).strip("-")
    return kebab if kebab else "unnamed"


def measure(path: Path) -> tuple[int, str]:
    """Return (size_bytes, mtime_iso_utc) for a file OR a directory tree."""
    if path.is_file():
        st = path.stat()
        mtime = datetime.datetime.fromtimestamp(st.st_mtime, tz=datetime.timezone.utc)
        return st.st_size, mtime.isoformat()

    total = 0
    latest = 0.0
    has_file = False
    for sub in path.rglob("*"):
        if sub.is_file():
            try:
                st = sub.stat()
            except OSError:
                continue
            total += st.st_size
            if st.st_mtime > latest:
                latest = st.st_mtime
            has_file = True
    if not has_file:
        latest = path.stat().st_mtime
    mtime = datetime.datetime.fromtimestamp(latest, tz=datetime.timezone.utc)
    return total, mtime.isoformat()


def enumerate_skill(bucket: str, project: str | None, skill: str, skill_dir: Path) -> list[dict]:
    """Each direct child of a `<skill>/` folder is one artifact (file OR subdir)."""
    out: list[dict] = []
    try:
        children = sorted(skill_dir.iterdir())
    except OSError:
        return out
    for child in children:
        try:
            size, mtime = measure(child)
        except OSError:
            continue
        out.append(
            {
                "bucket": bucket,
                "project": project,
                "skill": skill,
                "path": str(child.resolve()),
                "size_bytes": size,
                "mtime_iso": mtime,
            }
        )
    return out


def enumerate_bucket(bucket: str, project: str | None, bucket_dir: Path) -> list[dict]:
    """A bucket directory contains skill subfolders. Walk each."""
    if not bucket_dir.is_dir():
        return []
    out: list[dict] = []
    for skill_dir in sorted(bucket_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        out.extend(enumerate_skill(bucket, project, skill_dir.name, skill_dir))
    return out


def list_artifacts(
    root: Path,
    current_project: str,
    all_projects: bool,
    project_filter: str | None,
) -> list[dict]:
    if not root.is_dir():
        return []

    out: list[dict] = []

    if all_projects:
        for entry in sorted(root.iterdir()):
            if not entry.is_dir() or entry.name == "_global":
                continue
            out.extend(enumerate_bucket("project", entry.name, entry))
    elif project_filter:
        out.extend(enumerate_bucket("project", project_filter, root / project_filter))
    else:
        out.extend(enumerate_bucket("project", current_project, root / current_project))

    global_dir = root / "_global"
    if global_dir.is_dir():
        out.extend(enumerate_bucket("_global", None, global_dir))

    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Enumerate artifacts under ~/.claude/output/ — per-project + _global buckets."
    )
    parser.add_argument(
        "--all-projects",
        "-A",
        action="store_true",
        help="List every per-project bucket plus _global",
    )
    parser.add_argument(
        "--project",
        "-p",
        metavar="NAME",
        help="Restrict to one named project (plus _global)",
    )
    parser.add_argument(
        "--root",
        type=Path,
        help="Override root path (test only — default: ~/.claude/output/)",
    )
    parser.add_argument(
        "--current-project",
        metavar="NAME",
        help="Override the auto-detected current project (test only)",
    )
    args = parser.parse_args(argv)

    if args.all_projects and args.project:
        parser.error("--all-projects and --project are mutually exclusive")

    root = args.root.expanduser().resolve() if args.root else (Path.home() / ".claude" / "output")
    current = args.current_project or detect_current_project(Path.cwd())

    artifacts = list_artifacts(root, current, args.all_projects, args.project)
    json.dump(artifacts, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
