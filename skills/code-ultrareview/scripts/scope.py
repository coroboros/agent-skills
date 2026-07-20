#!/usr/bin/env python3
"""Phase 1 scope detector for code-ultrareview.

Deterministic, no LLM. Resolves the review base + target, classifies the
repository kind (8 kinds + unknown), reads the project instruction chain, detects
languages from the diff, and decides whether the conditional Coherence
axis activates. Emits one JSON object on stdout — `scope.json` — read by
every downstream phase.

Repo-kind classification precedence: explicit override (CLI flag) >
config (`.code-ultrareview.yaml`) > filesystem signature detection.

Coherence activation rule: any of these in the diff →
`scope.json["activates_coherence"] = true`:
    package.json
    .claude-plugin/marketplace.json | marketplace.json
    SKILL.md (any depth)
    README.md (root only)
    tsconfig.json
    pyproject.toml
    Cargo.toml
    go.mod

Usage:
    python3 scope.py --base <ref> [--target <ref>] [--repo <path>] \
        [--repo-kind <kind>] [--dirty-tree]
    python3 scope.py --dirty-tree [--repo <path>] [--repo-kind <kind>]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

GIT_TIMEOUT_S = 30
_HUNK_HEADER = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")

# Repo-kind precedence order — skills > monorepo > docs > app > library >
# {python, rust, go} > unknown.
_REPO_KIND_VALUES = (
    "skills", "app", "library", "docs", "monorepo",
    "python", "rust", "go", "unknown",
)
_FRAMEWORK_CONFIGS = (
    "next.config.js", "next.config.ts", "next.config.mjs",
    "astro.config.js", "astro.config.ts", "astro.config.mjs",
    "vite.config.js", "vite.config.ts", "vite.config.mjs",
)
_APP_ONLY_FRAMEWORKS = (
    "next.config.js", "next.config.ts", "next.config.mjs",
    "astro.config.js", "astro.config.ts", "astro.config.mjs",
)
_DOCS_SITE_CONFIGS = (
    "docusaurus.config.js", "docusaurus.config.ts", "docusaurus.config.mjs",
    "mkdocs.yml", "mkdocs.yaml",
    "hugo.toml", "hugo.yaml", "hugo.yml",
    "_config.yml",
)
_WORKSPACE_CONFIGS = (
    "pnpm-workspace.yaml", "lerna.json", "turbo.json", "nx.json",
)
_COMPETING_LABELS = {
    "package_json": "npm tooling",
    "pyproject_toml": "Python tooling",
    "workspace_configs": "workspaces",
    "cargo_toml": "Rust tooling",
    "go_mod": "Go tooling",
}

# Coherence activation triggers. Any of these in the diff flips the axis on.
# Root-only README.md (every subfolder README would over-trigger).
_COHERENCE_TRIGGERS_ANYWHERE = (
    "package.json",
    "SKILL.md",
    "tsconfig.json",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
)
_COHERENCE_TRIGGERS_EXACT = (
    ".claude-plugin/marketplace.json",
    "marketplace.json",
    "README.md",  # exact root match only — checked separately
)

# Language extension → canonical language name.
_EXT_TO_LANG = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".kt": "kotlin",
    ".rb": "ruby",
    ".swift": "swift",
    ".astro": "astro",
    ".svelte": "svelte",
    ".vue": "vue",
    ".md": "markdown",
    ".sh": "shell",
    ".bash": "shell",
    ".sql": "sql",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".json": "json",
}


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, check=False, timeout=GIT_TIMEOUT_S,
    )


def _untracked_files(repo: Path) -> list[str]:
    r = run_git(repo, "ls-files", "--others", "--exclude-standard")
    if r.returncode != 0:
        return []
    return [line for line in r.stdout.splitlines() if line]


def _parse_numstat(stdout: str, files: list, loc: int) -> int:
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
        if path not in files:
            files.append(path)
    return loc


def diff_files(repo: Path, base: str, target: str,
               *, dirty_tree: bool = False) -> tuple[int, list[str]]:
    """Return (loc_changed, files_list).

    Clean tree: numstat of `base..target`.
    Dirty tree: numstat of HEAD + each untracked file counted as all-added.
    """
    loc = 0
    files: list[str] = []

    if dirty_tree:
        r = run_git(repo, "diff", "--numstat", "HEAD")
    else:
        r = run_git(repo, "diff", "--numstat", f"{base}..{target}")
    if r.returncode == 0:
        loc = _parse_numstat(r.stdout, files, loc)

    if dirty_tree:
        for path in _untracked_files(repo):
            full = repo / path
            if not full.is_file():
                continue
            try:
                with open(full, "r", encoding="utf-8", errors="ignore") as f:
                    n = sum(1 for _ in f)
            except OSError:
                n = 0
            loc += n
            if path not in files:
                files.append(path)

    return loc, files


def _merge_line_ranges(ranges: list[list[int]]) -> list[list[int]]:
    merged: list[list[int]] = []
    for start, end in sorted(ranges):
        if merged and start <= merged[-1][1] + 1:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


def changed_line_ranges(
    repo: Path,
    base: str,
    target: str,
    files: list[str],
    *,
    dirty_tree: bool = False,
) -> dict[str, list[list[int]]]:
    """Return added/modified target-line ranges for every touched path."""
    untracked = set(_untracked_files(repo)) if dirty_tree else set()
    result: dict[str, list[list[int]]] = {}

    for path in files:
        if path in untracked:
            full = repo / path
            try:
                with full.open("r", encoding="utf-8", errors="ignore") as handle:
                    line_count = sum(1 for _ in handle)
            except OSError:
                line_count = 0
            result[path] = [[1, line_count]] if line_count else []
            continue

        diff_range = "HEAD" if dirty_tree else f"{base}..{target}"
        patch = run_git(
            repo,
            "diff",
            "--unified=0",
            "--no-color",
            "--no-ext-diff",
            diff_range,
            "--",
            path,
        )
        ranges: list[list[int]] = []
        if patch.returncode == 0:
            for line in patch.stdout.splitlines():
                match = _HUNK_HEADER.match(line)
                if not match:
                    continue
                start = int(match.group(1))
                count = int(match.group(2) or "1")
                if count > 0:
                    ranges.append([start, start + count - 1])
        result[path] = _merge_line_ranges(ranges)

    return result


def resolve_base(repo: Path, override: str | None = None,
                 *, dirty_tree: bool = False) -> tuple[str, str, str]:
    """Run `scripts/resolve_base.sh` and parse its RESULT line.

    Returns (base, target, rule). Dirty-tree mode skips the resolver entirely
    and reports `rule="dirty-tree"` so downstream phases see consistent
    shape.
    """
    if dirty_tree:
        return ("HEAD", "HEAD", "dirty-tree")

    script = Path(__file__).resolve().parent / "resolve_base.sh"
    args = ["bash", str(script)]
    if override:
        args.extend(["-b", override])
    r = subprocess.run(args, cwd=str(repo), capture_output=True, text=True,
                       check=False, timeout=GIT_TIMEOUT_S)
    last = ""
    for line in r.stdout.splitlines():
        if line.startswith("RESULT:"):
            last = line
    if not last:
        raise RuntimeError(
            f"resolve_base.sh produced no RESULT line (exit {r.returncode}): "
            f"{r.stderr.strip()}"
        )
    parts = dict(
        kv.split("=", 1) for kv in last.removeprefix("RESULT:").strip().split()
        if "=" in kv
    )
    if r.returncode != 0:
        hint = parts.get("hint", "no hint")
        raise RuntimeError(f"unresolvable base: {hint}")
    return (parts.get("base", ""), parts.get("target", "HEAD"),
            parts.get("rule", ""))


def _read_json_safe(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _package_json_role(repo: Path, data) -> str | None:
    """Classify a package.json as 'app' or 'library'."""
    if not isinstance(data, dict):
        return None
    scripts_raw = data.get("scripts")
    scripts: dict = scripts_raw if isinstance(scripts_raw, dict) else {}
    has_app_script = any(k in scripts for k in ("dev", "start"))
    has_bin = "bin" in data
    has_app_framework = any((repo / cfg).is_file() for cfg in _APP_ONLY_FRAMEWORKS)
    if has_app_script or has_bin or has_app_framework:
        return "app"
    if any(k in data for k in ("exports", "module", "types")):
        return "library"
    # Permissive default — a bare package.json without role signals reads as app.
    return "app"


def _detect_repo_signals(repo: Path) -> dict:
    signals = {
        "marketplace_json": None,
        "skill_md_count": 0,
        "package_json": None,
        "package_json_role": None,
        "pyproject_toml": None,
        "cargo_toml": None,
        "go_mod": None,
        "framework_configs": [],
        "docs_site_configs": [],
        "workspace_configs": [],
        "python_layout": False,
    }

    mp = repo / ".claude-plugin" / "marketplace.json"
    if mp.is_file():
        signals["marketplace_json"] = ".claude-plugin/marketplace.json"

    skills_dir = repo / "skills"
    if skills_dir.is_dir():
        signals["skill_md_count"] = sum(
            1 for p in skills_dir.glob("*/SKILL.md") if p.is_file()
        )

    pj = repo / "package.json"
    if pj.is_file():
        signals["package_json"] = "package.json"
        data = _read_json_safe(pj)
        signals["package_json_role"] = _package_json_role(repo, data)

    for cfg in _FRAMEWORK_CONFIGS:
        if (repo / cfg).is_file():
            signals["framework_configs"].append(cfg)
    for cfg in _DOCS_SITE_CONFIGS:
        if (repo / cfg).is_file():
            signals["docs_site_configs"].append(cfg)
    for cfg in _WORKSPACE_CONFIGS:
        if (repo / cfg).is_file():
            signals["workspace_configs"].append(cfg)

    pp = repo / "pyproject.toml"
    if pp.is_file():
        signals["pyproject_toml"] = "pyproject.toml"
        if (repo / "src").is_dir():
            signals["python_layout"] = True
        else:
            try:
                for child in repo.iterdir():
                    if child.is_dir() and (child / "__init__.py").is_file():
                        signals["python_layout"] = True
                        break
            except OSError:
                pass

    if (repo / "Cargo.toml").is_file():
        signals["cargo_toml"] = "Cargo.toml"
    if (repo / "go.mod").is_file():
        signals["go_mod"] = "go.mod"

    return signals


def _resolve_repo_kind(signals: dict) -> tuple[str, str, list[str]]:
    competing: list[str] = []

    def add_competing(key: str):
        if signals.get(key):
            label = _COMPETING_LABELS.get(key)
            if label and label not in competing:
                competing.append(label)

    if signals["marketplace_json"] and signals["skill_md_count"] >= 1:
        for key in ("package_json", "workspace_configs", "pyproject_toml"):
            add_competing(key)
        return "skills", "marketplace.json + skills/*/SKILL.md", competing

    if signals["workspace_configs"]:
        primary = "workspace config: " + signals["workspace_configs"][0]
        for key in ("package_json", "pyproject_toml"):
            add_competing(key)
        return "monorepo", primary, competing

    if signals["docs_site_configs"]:
        primary = "docs site config: " + signals["docs_site_configs"][0]
        for key in ("package_json", "workspace_configs"):
            add_competing(key)
        return "docs", primary, competing

    if signals["package_json_role"] == "app":
        if signals["framework_configs"]:
            competing.append("framework: " + signals["framework_configs"][0])
        if signals["workspace_configs"]:
            add_competing("workspace_configs")
        return "app", "package.json (app role)", competing

    if signals["package_json_role"] == "library":
        return "library", "package.json (library role)", competing

    if signals["pyproject_toml"]:
        for key in ("cargo_toml", "go_mod"):
            add_competing(key)
        return "python", "pyproject.toml", competing

    if signals["cargo_toml"]:
        for key in ("go_mod", "pyproject_toml"):
            add_competing(key)
        return "rust", "Cargo.toml", competing

    if signals["go_mod"]:
        add_competing("pyproject_toml")
        return "go", "go.mod", competing

    return "unknown", "no recognized signature", competing


def _load_repo_kind_config(repo: Path) -> str | None:
    """Read `.code-ultrareview.yaml` at repo root for a `repo_kind:` override."""
    cfg = repo / ".code-ultrareview.yaml"
    if not cfg.is_file():
        return None
    try:
        text = cfg.read_text(encoding="utf-8")
    except OSError:
        return None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        if key.strip() != "repo_kind":
            continue
        value = value.strip().strip('"').strip("'")
        if value:
            return value
    return None


def classify_repo(repo: Path, override: str | None = None) -> tuple[str, dict]:
    """Resolve repo_kind. Precedence: override > config > detection."""
    signals = _detect_repo_signals(repo)
    detected_kind, primary, competing = _resolve_repo_kind(signals)

    override_source: str | None = None
    final_kind = detected_kind

    if override is not None:
        if override not in _REPO_KIND_VALUES:
            raise ValueError(
                f"invalid repo_kind override: {override!r} "
                f"(expected one of: {', '.join(_REPO_KIND_VALUES)})"
            )
        final_kind = override
        override_source = "--repo-kind flag"
    else:
        cfg_value = _load_repo_kind_config(repo)
        if cfg_value is not None and cfg_value in _REPO_KIND_VALUES:
            final_kind = cfg_value
            override_source = "config:.code-ultrareview.yaml"

    return final_kind, {
        **signals,
        "primary_signal": primary,
        "competing_signals": competing,
        "override_source": override_source,
    }


def instruction_chain(repo: Path, files_touched: list[str]) -> list[str]:
    """Return the cross-agent instruction baseline, broadest to most specific.

    At each relevant directory, `AGENTS.override.md` wins over `AGENTS.md`.
    Claude-specific entrypoints and recursive rule files follow the shared
    entrypoint at the same level. Project paths are relative to `repo`; user
    instruction paths are absolute.
    """
    chain: list[str] = []
    seen: set[Path] = set()

    def read_nonempty(path: Path) -> str | None:
        if not path.is_file():
            return None
        try:
            body = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None
        return body if body.strip() else None

    def add(path: Path, body: str | None = None) -> bool:
        if body is None:
            body = read_nonempty(path)
        if body is None:
            return False
        resolved = path.resolve()
        if resolved in seen:
            return True
        seen.add(resolved)
        try:
            chain.append(str(path.relative_to(repo)))
        except ValueError:
            chain.append(str(path.resolve()))
        return True

    def add_rules(directory: Path) -> None:
        if not directory.is_dir():
            return
        for rule in sorted(directory.rglob("*.md")):
            add(rule)

    def add_agents_level(directory: Path) -> bool:
        """Add the effective entrypoint; return whether it references shared rules."""
        for name in ("AGENTS.override.md", "AGENTS.md"):
            candidate = directory / name
            body = read_nonempty(candidate)
            if body is None:
                continue
            add(candidate, body)
            return bool(re.search(r"(?:~/)?\.agents/rules(?:/|\b)", body))
        return False

    relevant_dirs: set[Path] = {repo}
    for touched in files_touched:
        parts = Path(touched).parts[:-1]
        for depth in range(1, len(parts) + 1):
            relevant_dirs.add(repo.joinpath(*parts[:depth]))
    ordered_dirs = sorted(
        relevant_dirs,
        key=lambda path: (len(path.relative_to(repo).parts), str(path)),
    )

    home = os.environ.get("HOME", "")
    if home:
        home_path = Path(home)
        if add_agents_level(home_path / ".agents"):
            add_rules(home_path / ".agents" / "rules")
        codex_home_value = os.environ.get("CODEX_HOME")
        codex_home = Path(codex_home_value) if codex_home_value else home_path / ".codex"
        if add_agents_level(codex_home):
            add_rules(codex_home / "rules")
        add(home_path / ".claude" / "CLAUDE.md")
        add_rules(home_path / ".claude" / "rules")

    for directory in ordered_dirs:
        if add_agents_level(directory):
            add_rules(directory / ".agents" / "rules")
        add(directory / "CLAUDE.md")
        add(directory / ".claude" / "CLAUDE.md")
        add(directory / "CLAUDE.local.md")
        add_rules(directory / ".claude" / "rules")

    return chain


def claude_md_chain(repo: Path, files_touched: list[str]) -> list[str]:
    """Compatibility alias for the historical scope schema name."""
    return instruction_chain(repo, files_touched)


def activates_coherence(files_touched: list[str]) -> bool:
    """Decide whether the conditional Coherence axis activates."""
    for path in files_touched:
        # Exact-path match so a nested README.md doesn't over-trigger.
        if path in _COHERENCE_TRIGGERS_EXACT:
            return True
        if Path(path).name in _COHERENCE_TRIGGERS_ANYWHERE:
            return True
    return False


def detect_languages(files_touched: list[str]) -> list[str]:
    """Return the deduplicated sorted list of canonical languages in the diff."""
    found: set[str] = set()
    for path in files_touched:
        ext = Path(path).suffix.lower()
        lang = _EXT_TO_LANG.get(ext)
        if lang:
            found.add(lang)
    return sorted(found)


def build_scope(repo: Path, *, base_override: str | None = None,
                target: str = "HEAD", dirty_tree: bool = False,
                repo_kind_override: str | None = None) -> dict:
    """Assemble the scope.json payload."""
    base, resolved_target, rule = resolve_base(
        repo, override=base_override, dirty_tree=dirty_tree,
    )
    if target and not dirty_tree:
        resolved_target = target

    loc, files = diff_files(repo, base, resolved_target, dirty_tree=dirty_tree)
    line_ranges = changed_line_ranges(
        repo,
        base,
        resolved_target,
        files,
        dirty_tree=dirty_tree,
    )
    repo_kind, signals = classify_repo(repo, override=repo_kind_override)
    chain = instruction_chain(repo, files)
    coherence = activates_coherence(files)
    languages = detect_languages(files)

    return {
        "base": base,
        "target": resolved_target,
        "rule": rule,
        "dirty_tree": dirty_tree,
        "repo_kind": repo_kind,
        "repo_kind_signals": signals,
        "languages": languages,
        "instruction_chain": chain,
        "claude_md_chain": list(chain),  # Backward-compatible schema alias.
        "loc_changed": loc,
        "files_touched": len(files),  # derived count; canonical key is files_touched_list
        "files_touched_list": files,
        "changed_line_ranges": line_ranges,
        "activates_coherence": coherence,
        "tools_skipped": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 1 scope detector for code-ultrareview"
    )
    parser.add_argument("--base", help="base ref (overrides resolve_base.sh)")
    parser.add_argument("--target", default="HEAD",
                        help="target ref (default: HEAD)")
    parser.add_argument("--dirty-tree", action="store_true",
                        help="Review uncommitted work: git diff HEAD plus "
                             "every untracked file. --base/--target ignored.")
    parser.add_argument("--repo", default=".",
                        help="repo path (default: cwd)")
    parser.add_argument("--repo-kind", dest="repo_kind", default=None,
                        choices=_REPO_KIND_VALUES,
                        help="Override detected repo kind")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    if not (repo / ".git").exists() and not (repo / ".git").is_file():
        print(f"ERROR: {repo} is not a git repo", file=sys.stderr)
        return 2

    try:
        scope = build_scope(
            repo,
            base_override=args.base,
            target=args.target,
            dirty_tree=args.dirty_tree,
            repo_kind_override=args.repo_kind,
        )
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except subprocess.TimeoutExpired as exc:
        print(f"ERROR: git timed out: {exc.cmd}", file=sys.stderr)
        return 2

    print(json.dumps(scope, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
