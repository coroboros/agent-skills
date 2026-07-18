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
import os
import re
import shutil
import sys
from pathlib import Path


class InvalidManifestError(ValueError):
    """Raised when a present project manifest cannot be trusted."""


def _python_manifest_uses_pytest(repo: Path) -> bool:
    for fname in ("pyproject.toml", "requirements.txt", "requirements-dev.txt", "setup.cfg"):
        p = repo / fname
        if not p.exists():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace").lower()
        except OSError:
            continue
        if "pytest" in text:
            return True
    return False


def _has_unittest_suite(repo: Path) -> bool:
    ignored = {".git", ".venv", "venv", "node_modules", "build", "dist"}
    for root, dirs, files in os.walk(repo):
        dirs[:] = [name for name in dirs if name not in ignored]
        for name in files:
            if not name.startswith("test") or not name.endswith(".py"):
                continue
            path = Path(root) / name
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if "unittest" in text and re.search(r"\bdef\s+test_", text):
                return True
    return False


def _makefile_has_test_target(repo: Path) -> bool:
    p = repo / "Makefile"
    if not p.exists():
        return False
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return bool(re.search(r"^test:", text, re.MULTILINE))


def _javascript_test_command(repo: Path) -> tuple[str | None, str | None]:
    """Return the declared package-manager test command, never an invented one."""
    package_json = repo / "package.json"
    if not package_json.is_file():
        return None, None
    try:
        payload = json.loads(package_json.read_text(encoding="utf-8"))
    except OSError as exc:
        raise InvalidManifestError(f"cannot read package.json: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise InvalidManifestError(
            f"package.json is not valid JSON at line {exc.lineno}, "
            f"column {exc.colno}: {exc.msg}"
        ) from exc
    if not isinstance(payload, dict):
        raise InvalidManifestError("package.json must contain an object")
    scripts = payload.get("scripts")
    if scripts is not None and not isinstance(scripts, dict):
        raise InvalidManifestError("package.json scripts must be an object")
    test_script = scripts.get("test") if isinstance(scripts, dict) else None
    if not isinstance(test_script, str) or not test_script.strip():
        return None, None

    package_manager = payload.get("packageManager")
    declared = (
        package_manager.split("@", 1)[0]
        if isinstance(package_manager, str)
        else None
    )
    commands = {
        "pnpm": "pnpm test",
        "yarn": "yarn test",
        "bun": "bun run test",
        "npm": "npm test",
    }
    if declared in commands:
        return declared, commands[declared]
    if (repo / "pnpm-lock.yaml").exists():
        return "pnpm", commands["pnpm"]
    if (repo / "yarn.lock").exists():
        return "yarn", commands["yarn"]
    if (repo / "bun.lock").exists() or (repo / "bun.lockb").exists():
        return "bun", commands["bun"]
    return "npm", commands["npm"]


def detect(repo: Path) -> dict:
    js_tool, js_command = _javascript_test_command(repo)
    if js_tool and js_command:
        return {
            "tool": js_tool,
            "test_command": js_command,
            "available": shutil.which(js_tool) is not None,
        }
    if _python_manifest_uses_pytest(repo):
        return {
            "tool": "pytest",
            "test_command": "pytest -x",
            "available": shutil.which("pytest") is not None,
        }
    if _has_unittest_suite(repo):
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

    try:
        result = detect(repo)
    except InvalidManifestError as exc:
        print(f"ERROR: invalid project manifest: {exc}", file=sys.stderr)
        print(
            "ERROR: remediation: repair package.json so it is valid JSON, "
            "then rerun build detection.",
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result.get("tool") else 1


if __name__ == "__main__":
    sys.exit(main())
