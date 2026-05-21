#!/usr/bin/env python3
"""Build / test tool detection for the execution phase.

Probes the repo for a known manifest in a fixed order and returns the
canonical test command + a flag indicating whether the underlying binary
is available on PATH. First hit wins.

Output JSON (stdout):
    {"tool": "<name>", "test_command": "<cmd>", "available": <bool>}

Exit 0 on detection (including "available": false). Exit 2 when the repo
path does not exist. Exit code 1 when no known manifest is detected.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path


def _detect_python_runner(repo: Path) -> str:
    """Return 'pytest' if any manifest mentions pytest; else 'unittest'."""
    for fname in ("pyproject.toml", "requirements.txt", "requirements-dev.txt", "setup.cfg"):
        p = repo / fname
        if not p.exists():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace").lower()
        except OSError:
            continue
        if "pytest" in text:
            return "pytest"
    return "unittest"


def _makefile_has_test_target(repo: Path) -> bool:
    p = repo / "Makefile"
    if not p.exists():
        return False
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return bool(re.search(r"^test:", text, re.MULTILINE))


def detect(repo: Path) -> dict:
    if (repo / "pnpm-lock.yaml").exists():
        return {
            "tool": "pnpm",
            "test_command": "pnpm test",
            "available": shutil.which("pnpm") is not None,
        }
    if (repo / "yarn.lock").exists():
        return {
            "tool": "yarn",
            "test_command": "yarn test",
            "available": shutil.which("yarn") is not None,
        }
    if (repo / "package-lock.json").exists() or (repo / "package.json").exists():
        return {
            "tool": "npm",
            "test_command": "npm test --no-coverage",
            "available": shutil.which("npm") is not None,
        }
    if (repo / "pyproject.toml").exists() or (repo / "requirements.txt").exists() \
            or (repo / "setup.cfg").exists():
        runner = _detect_python_runner(repo)
        if runner == "pytest":
            return {
                "tool": "pytest",
                "test_command": "pytest -x",
                "available": shutil.which("pytest") is not None,
            }
        return {
            "tool": "unittest",
            "test_command": "python3 -m unittest discover",
            "available": shutil.which("python3") is not None,
        }
    if (repo / "Cargo.toml").exists():
        return {
            "tool": "cargo",
            "test_command": "cargo test",
            "available": shutil.which("cargo") is not None,
        }
    if (repo / "go.mod").exists():
        return {
            "tool": "go",
            "test_command": "go test ./...",
            "available": shutil.which("go") is not None,
        }
    if _makefile_has_test_target(repo):
        return {
            "tool": "make",
            "test_command": "make test",
            "available": shutil.which("make") is not None,
        }
    return {"tool": None, "test_command": None, "available": False}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect the canonical build/test tool for a repo"
    )
    parser.add_argument("--repo", default=".", help="repo path (default: cwd)")
    parser.add_argument("--json", action="store_true", help="emit JSON (default)")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.exists():
        print(f"ERROR: repo path does not exist: {repo}", file=sys.stderr)
        return 2

    result = detect(repo)
    print(json.dumps(result, indent=2))
    return 0 if result.get("tool") else 1


if __name__ == "__main__":
    sys.exit(main())
