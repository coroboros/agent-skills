#!/usr/bin/env python3
"""Resolve declared JavaScript analyzers without downloading packages."""
from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import sys
from pathlib import Path
from coverage import read_scope

DEPENDENCIES = ("devDependencies", "dependencies", "optionalDependencies")
OFFLINE = dict.fromkeys(("COREPACK_ENABLE_NETWORK", "COREPACK_ENABLE_DOWNLOAD_PROMPT",
                         "COREPACK_ENABLE_AUTO_PIN", "COREPACK_DEFAULT_TO_LATEST",
                         "YARN_ENABLE_NETWORK"), "0")
MARKERS = (("pnpm-lock.yaml", "pnpm"), ("yarn.lock", "yarn"), ("bun.lock", "bun"),
           ("bun.lockb", "bun"), ("package-lock.json", "npm"),
           ("npm-shrinkwrap.json", "npm"))

class ContractError(ValueError):
    code = 3
class InputError(ContractError):
    code = 2

def _manifest(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InputError(f"{path}: invalid package.json: {exc}") from exc
    if not isinstance(value, dict):
        raise InputError(f"{path}: package.json must contain an object")
    for key in DEPENDENCIES:
        if key in value and not isinstance(value[key], dict):
            raise InputError(f"{path}: {key} must contain an object")
    return value

def _parents(repo: Path, start: Path):
    repo, start = repo.resolve(), start.resolve()
    current = start if start.is_dir() else start.parent
    while current == repo or repo in current.parents:
        yield current
        if current == repo:
            return
        current = current.parent

def _declaration(repo: Path, relative: str, package: str):
    repo = repo.resolve()
    target = (repo / relative).resolve()
    if target != repo and repo not in target.parents:
        raise InputError(f"scope path escapes the repository: {relative}")
    for directory in _parents(repo, target):
        path = directory / "package.json"
        if path.is_file() and any(
            package in _manifest(path).get(key, {}) for key in DEPENDENCIES
        ):
            return directory
    return None

def package_manager_spec(repo: Path, directory: Path) -> tuple[str, str | None]:
    for parent in _parents(repo, directory):
        path = parent / "package.json"
        declared = _manifest(path).get("packageManager") if path.is_file() else None
        name = declared.split("@", 1)[0] if isinstance(declared, str) else ""
        if name in {"npm", "pnpm", "yarn", "bun"}:
            return name, declared
        for marker, candidate in MARKERS:
            if (parent / marker).exists():
                return candidate, None
    return "npm", None

def _state(repo: Path, files: list[str], package: str):
    declarations = [_declaration(repo, item, package) for item in files]
    declared = {item for item in declarations if item is not None}
    if declared and (None in declarations or len(declared) != 1):
        raise InputError(f"{package} is not declared consistently; "
                         f"declare it once in {repo / 'package.json'}")
    return next(iter(declared), None)

def _project_binary(repo: Path, directory: Path, binary: str) -> Path | None:
    for parent in _parents(repo, directory):
        candidate = parent / "node_modules" / ".bin" / binary
        if candidate.is_file():
            return candidate.resolve()
    return None

def resolve(repo: Path, files: list[str], package: str, binary: str):
    directory = _state(repo, files, package)
    env = dict(os.environ)
    env.update(OFFLINE)
    if directory:
        installed = _project_binary(repo, directory, binary)
        if installed:
            return [str(installed)], f"project:binary:{directory}", env
        manager = package_manager_spec(repo, directory)[0]
        pnp = any((parent / ".pnp.cjs").is_file() for parent in _parents(repo, directory))
        if manager == "yarn" and pnp:
            if not shutil.which("yarn"):
                raise ContractError("declared Yarn PnP runtime requires yarn on PATH")
            command = ["yarn", "--cwd", str(directory), "run", "-B", binary]
            return command, f"project:yarn-pnp:{directory}", env
        raise ContractError(f"declared analyzer is not installed: {package}")
    path = shutil.which(binary)
    if not path:
        raise ContractError(f"required analyzer is unavailable: {binary}")
    return [path], f"path:{path}", env

def guidance(repo: Path, files: list[str], package: str) -> str:
    directory = _state(repo, files, package)
    manager = package_manager_spec(repo, directory or repo)[0]
    if directory:
        command = {"npm": "npm ci --ignore-scripts", "pnpm":
                   "pnpm install --frozen-lockfile --ignore-scripts",
                   "yarn": "YARN_ENABLE_SCRIPTS=false yarn install --immutable",
                   "bun": "bun install --frozen-lockfile --ignore-scripts"}[manager]
    else:
        command = {"npm": f"npm install -D --ignore-scripts {package}",
                   "pnpm": f"pnpm add -D --ignore-scripts {package}",
                   "yarn": f"YARN_ENABLE_SCRIPTS=false yarn add -D {package}",
                   "bun": f"bun add -D --ignore-scripts {package}"}[manager]
    return f"cd {shlex.quote(str(directory or repo))} && {command}"

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("probe", "exec", "install"))
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--scope", type=Path, required=True)
    for option in ("--package", "--binary"):
        parser.add_argument(option, required=True)
    parser.add_argument("--file", action="append", dest="files")
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    try:
        repo = args.repo.resolve(strict=True)
        files = args.files or read_scope(args.scope)["files_touched_list"]
        if args.action == "install":
            print(guidance(repo, files, args.package))
            return 0
        command, wrapper, env = resolve(repo, files, args.package, args.binary)
        if args.action == "probe":
            print(wrapper)
            return 0
        extra = args.arguments[1:] if args.arguments[:1] == ["--"] else args.arguments
        os.execvpe(command[0], command + extra, env)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return getattr(exc, "code", 2)
if __name__ == "__main__":
    raise SystemExit(main())
