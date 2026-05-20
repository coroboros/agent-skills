#!/usr/bin/env python3
"""Audit-phase signal extractor for code-ultrareview.

Computes eight deterministic signals from a git diff between two refs and
emits them as JSON. The tier router consumes this output to pick a review
tier (standard / deep / ultra) and surface a rationale.

The script is stdlib-only and subprocess-driven, mirroring the posture of
`resolve_base.sh`: failures are loud (exit 2), output is machine-readable.

Usage:
    python3 audit_signals.py --base <ref> [--target <ref>] [--repo <path>] [--json]
"""

import argparse
import json
import re
import subprocess
import sys
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


def diff_numstat(repo: Path, base: str, target: str):
    """Return (total_loc_changed, files_list, per_file_added_dict)."""
    r = run_git(repo, "diff", "--numstat", f"{base}..{target}")
    if r.returncode != 0:
        return 0, [], {}
    loc = 0
    files: list[str] = []
    added_per_file: dict[str, int] = {}
    for line in r.stdout.splitlines():
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
        files.append(path)
        added_per_file[path] = added
    return loc, files, added_per_file


def diff_content(repo: Path, base: str, target: str) -> str:
    r = run_git(repo, "diff", f"{base}..{target}")
    return r.stdout if r.returncode == 0 else ""


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


def audit(repo: Path, base: str, target: str) -> dict:
    loc, files, added_per_file = diff_numstat(repo, base, target)
    content = diff_content(repo, base, target)
    spec_found, spec_list = detect_normative_spec(repo, content)
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
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit-phase signal extractor for code-ultrareview"
    )
    parser.add_argument("--base", required=True, help="base ref (e.g., HEAD~5, origin/main)")
    parser.add_argument("--target", default="HEAD", help="target ref (default: HEAD)")
    parser.add_argument("--repo", default=".", help="repo path (default: cwd)")
    parser.add_argument("--json", action="store_true", help="emit JSON (default behavior)")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    if not (repo / ".git").exists() and not (repo / ".git").is_file():
        print(f"ERROR: {repo} is not a git repo", file=sys.stderr)
        return 2

    try:
        result = audit(repo, args.base, args.target)
    except subprocess.TimeoutExpired as exc:
        print(f"ERROR: git timed out: {exc.cmd}", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
