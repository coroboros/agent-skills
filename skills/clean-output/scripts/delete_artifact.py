#!/usr/bin/env python3
"""Path-guarded deletion of one artifact under ~/.claude/output/.

The guard: `Path(p).resolve().is_relative_to(<root>)`. Anything outside the
configured root exits 2 — including paths that escape via `..` or via a
symlink that resolves outside the sandbox. The script never follows a
directory symlink (`shutil.rmtree` raises on a symlink by default); the
SKILL.md never invokes shell `rm`.

Stdlib only. Python 3.10+.

Exit codes:
    0 — deleted
    1 — path missing or unwritable
    2 — guard violation (path outside root, or resolution failed)
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def delete_artifact(path: Path, root: Path) -> int:
    try:
        resolved = path.resolve(strict=False)
    except OSError as e:
        print(f"path resolution failed: {e}", file=sys.stderr)
        return 2

    root_resolved = root.resolve(strict=False)
    if not resolved.is_relative_to(root_resolved):
        print(f"refuse: {resolved} is outside {root_resolved}", file=sys.stderr)
        return 2

    if not (path.exists() or path.is_symlink()):
        print(f"missing: {path}", file=sys.stderr)
        return 1

    try:
        if path.is_symlink() or path.is_file():
            path.unlink()
        else:
            shutil.rmtree(path)
    except OSError as e:
        print(f"delete failed: {e}", file=sys.stderr)
        return 1

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Path-guarded deletion of one artifact under ~/.claude/output/."
    )
    parser.add_argument("path", type=Path, help="Absolute path to the artifact to delete")
    parser.add_argument(
        "--root",
        type=Path,
        help="Override root path (test only — default: ~/.claude/output/)",
    )
    args = parser.parse_args(argv)

    root = args.root.expanduser() if args.root else (Path.home() / ".claude" / "output")
    return delete_artifact(args.path, root)


if __name__ == "__main__":
    sys.exit(main())
