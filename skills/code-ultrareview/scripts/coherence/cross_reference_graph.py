"""Cross-reference sub-graph extractor.

Walks `.md` files at repo root and inside `skills/*/`. Resolves:
    - Relative file links (./foo.md, ../bar/baz.md) — file existence
    - Anchor links (path#section, #section) — heading existence in target
    - Skill-name references (`/forge`, `/apex`) — match against marketplace skills
"""

from __future__ import annotations

import fnmatch
import re
from pathlib import Path

from ._common import Finding, IgnoreFile, read_json_safe

MD_LINK_RE = re.compile(r"\[(?P<text>[^\]]+)\]\((?P<target>[^)\s]+)(?:\s+\"[^\"]*\")?\)")
# Match ONLY `/skill-name` — slash + kebab name, the entire backtick content.
# Anything inside a backtick with extra characters (e.g., a path like
# `${CLAUDE_SKILL_DIR}/scripts/foo.sh`) is intentionally ignored.
BACKTICK_SKILL_RE = re.compile(r"`/([a-z][a-z0-9-]{2,40})`")
FENCED_BLOCK_RE = re.compile(r"```.*?```", re.DOTALL)
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "tel:")

# Slash-commands the lens never flags as missing — they belong to Claude Code,
# Anthropic upstream skills, or sibling-skill pointers we deliberately preserve.
# Extend this set rather than allowlist per repo when the command is widely
# known and external.
KNOWN_EXTERNALS = {
    # Claude Code built-in slash commands
    "init", "memory", "clear", "compact", "agents", "help", "exit", "quit",
    "feedback", "bug", "release-notes", "cost", "status", "model", "login",
    "logout", "permissions", "config", "doctor", "ide", "vim", "resume",
    "continue", "settings", "hooks",
    # Autonomous-workflow commands (Claude Code v2.1.139+)
    "goal", "loop",
    # Anthropic built-in review / sibling skill pointers
    "ultrareview", "security-review", "find-docs", "review", "simplify",
    "modernize", "oneshot",
    # Anthropic-published skills
    "canvas-design", "skill-creator", "code-reviewer",
}


def _is_external(target: str) -> bool:
    return target.startswith(EXTERNAL_PREFIXES)


def _slugify_heading(heading: str) -> str:
    s = heading.strip().lower()
    s = re.sub(r"[`*_]", "", s)
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    return s


def _headings_in(path: Path) -> set[str]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return set()
    return {_slugify_heading(m.group(1)) for m in HEADING_RE.finditer(text)}


def _iter_md_files(repo: Path):
    for p in repo.glob("*.md"):
        if p.is_file():
            yield p
    skills_dir = repo / "skills"
    if skills_dir.exists():
        for p in skills_dir.rglob("*.md"):
            if p.is_file():
                yield p


def _is_path_allowlisted(path_str: str, allowlist: list[str]) -> bool:
    return any(fnmatch.fnmatch(path_str, pattern) for pattern in allowlist)


def _marketplace_skills(repo: Path) -> set[str]:
    data = read_json_safe(repo / ".claude-plugin" / "marketplace.json")
    if not isinstance(data, dict):
        return set()
    skills: set[str] = set()
    for plugin in data.get("plugins", []) or []:
        if not isinstance(plugin, dict):
            continue
        for s in plugin.get("skills", []) or []:
            if isinstance(s, str):
                base = s.rstrip("/").split("/")[-1]
                if base:
                    skills.add(base)
    return skills


def run(repo: Path, ignore: IgnoreFile, **_) -> list[Finding]:
    findings: list[Finding] = []
    allowlist = ignore.list_for("cross-reference", "ignore_paths")
    skills_in_marketplace = _marketplace_skills(repo)

    for md_path in _iter_md_files(repo):
        rel = md_path.relative_to(repo).as_posix()
        if _is_path_allowlisted(rel, allowlist):
            continue
        try:
            text = md_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        # Strip fenced code blocks before link/skill parsing — examples inside
        # them are not real references.
        clean = FENCED_BLOCK_RE.sub("", text)

        for m in MD_LINK_RE.finditer(clean):
            target = m.group("target").strip()
            if _is_external(target) or target.startswith("#"):
                continue
            if target.startswith("mailto:") or target.startswith("tel:"):
                continue
            path_part, _, anchor = target.partition("#")
            if not path_part:
                continue
            resolved = (md_path.parent / path_part).resolve()
            if not resolved.exists():
                findings.append(Finding(
                    sub_graph="cross-reference",
                    severity="High",
                    location=f"{rel}: link to {target!r}",
                    finding=f"Broken link: {target!r} from {rel} — target does not exist.",
                    recommendation="Fix the link target or update the path.",
                    confidence=95,
                ))
                continue
            if anchor and resolved.is_file() and resolved.suffix == ".md":
                headings = _headings_in(resolved)
                if _slugify_heading(anchor) not in headings:
                    findings.append(Finding(
                        sub_graph="cross-reference",
                        severity="Medium",
                        location=f"{rel}: anchor {anchor!r}",
                        finding=f"Anchor {anchor!r} not found in {resolved.relative_to(repo).as_posix()}.",
                        recommendation="Update the anchor or restore the missing heading.",
                        confidence=85,
                    ))

        if skills_in_marketplace:
            for m in BACKTICK_SKILL_RE.finditer(clean):
                name = m.group(1)
                if name in skills_in_marketplace:
                    continue
                if name in KNOWN_EXTERNALS:
                    continue
                findings.append(Finding(
                    sub_graph="cross-reference",
                    severity="Medium",
                    location=f"{rel}: /{name}",
                    finding=f"Reference to /{name} but no matching skill in marketplace.json.",
                    recommendation="Add the skill to the marketplace, rewrite the pointer, or remove the mention.",
                    confidence=80,
                ))

    return findings
