"""Description sub-graph extractor.

Compares description fields across structured sources:
    - package.json.description
    - .claude-plugin/marketplace.json.metadata.description
    - gh repo .description (when `gh` is available)
    - SKILL.md frontmatter (only for single-skill repos)
    - README first paragraph (only when --include-prose)

GitHub topics are a different kind of artifact (keywords, not descriptions)
and are deliberately omitted — pairing them against descriptions produces
false positives without surfacing real drift.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from ._common import (
    Finding, IgnoreFile,
    normalize_description, read_json_safe,
)

GH_TIMEOUT_S = 5


def _gh_repo_description(repo: Path) -> str | None:
    if os.environ.get("COHERENCE_SKIP_GH") or not shutil.which("gh"):
        return None
    try:
        r = subprocess.run(
            ["gh", "repo", "view", "--json", "description", "-q", ".description"],
            cwd=repo, capture_output=True, text=True, timeout=GH_TIMEOUT_S,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    if r.returncode != 0:
        return None
    desc = r.stdout.strip()
    return desc or None


def _parse_skill_md_description(content: str) -> str | None:
    if not content.startswith("---"):
        return None
    lines = content.split("\n")
    end_idx: int | None = None
    for i, line in enumerate(lines[1:], start=1):
        if line == "---":
            end_idx = i
            break
    if end_idx is None:
        return None
    for line in lines[1:end_idx]:
        if line.startswith("description:"):
            value = line[len("description:"):].strip()
            if (value.startswith('"') and value.endswith('"')) or (
                value.startswith("'") and value.endswith("'")
            ):
                value = value[1:-1]
            return value
    return None


def _readme_first_paragraph(readme: Path) -> str | None:
    if not readme.exists():
        return None
    try:
        text = readme.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    lines = text.splitlines()
    after_h1 = False
    para: list[str] = []
    for line in lines:
        if not after_h1:
            if line.startswith("# "):
                after_h1 = True
            continue
        stripped = line.strip()
        if not stripped:
            if para:
                break
            continue
        if stripped.startswith("#"):
            if para:
                break
            continue
        if stripped.startswith("```") or stripped.startswith("> "):
            if para:
                break
            continue
        para.append(stripped)
    return " ".join(para) if para else None


def collect_sources(repo: Path, include_prose: bool) -> list[tuple[str, str]]:
    sources: list[tuple[str, str]] = []

    pkg = read_json_safe(repo / "package.json")
    if pkg and isinstance(pkg.get("description"), str):
        sources.append(("package.json", pkg["description"]))

    mp = read_json_safe(repo / ".claude-plugin" / "marketplace.json")
    if isinstance(mp, dict):
        meta = mp.get("metadata") or {}
        if isinstance(meta, dict) and isinstance(meta.get("description"), str):
            sources.append(("marketplace.json", meta["description"]))

    gh_desc = _gh_repo_description(repo)
    if gh_desc:
        sources.append(("gh-about", gh_desc))

    skills_dir = repo / "skills"
    if skills_dir.exists():
        skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir()]
        if len(skill_dirs) == 1:
            skill_md = skill_dirs[0] / "SKILL.md"
            if skill_md.exists():
                try:
                    desc = _parse_skill_md_description(
                        skill_md.read_text(encoding="utf-8", errors="replace")
                    )
                except OSError:
                    desc = None
                if desc:
                    sources.append((f"skills/{skill_dirs[0].name}/SKILL.md", desc))

    if include_prose:
        prose = _readme_first_paragraph(repo / "README.md")
        if prose:
            sources.append(("README.prose", prose))

    return sources


def run(repo: Path, ignore: IgnoreFile, include_prose: bool = False) -> list[Finding]:
    sources = collect_sources(repo, include_prose)
    findings: list[Finding] = []
    for i, (a_id, a_val) in enumerate(sources):
        for j in range(i + 1, len(sources)):
            b_id, b_val = sources[j]
            if ignore.has("description", "ignore_pairs", f"{a_id}:{b_id}") or \
                    ignore.has("description", "ignore_pairs", f"{b_id}:{a_id}"):
                continue
            if normalize_description(a_val) == normalize_description(b_val):
                continue
            is_prose = a_id == "README.prose" or b_id == "README.prose"
            findings.append(Finding(
                sub_graph="description",
                severity="Low" if is_prose else "Medium",
                location=f"{a_id} ↔ {b_id}",
                finding=f"Description divergence: {a_id} = {a_val!r}; {b_id} = {b_val!r}",
                recommendation="Pick a canonical description and align both sources.",
                confidence=60 if is_prose else 90,
            ))
    return findings
