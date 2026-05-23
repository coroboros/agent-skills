#!/usr/bin/env python3
"""Runtime installed-skill detection + lens-cluster routing for code-ultrareview.

Two responsibilities:

1. **Detection** — `detect_installed_skills(home, project_root)` scans
   `~/.claude/skills/` (global) and `<project_root>/.claude/skills/`
   (project), returning a `{skill_name: Path}` map. Project skills
   shadow global on name collision.

2. **Routing** — `route_cluster(lens, marker, installed_skills)` walks
   the canonical `ROUTING_TABLE` for the given lens × marker cell.
   First installed candidate wins. `fallback_used` flips to True when at
   least one earlier candidate was missing. Final candidate of every
   cell is `("apex", "/apex")`; the function still emits `/apex` even
   when not present, flagging `fallback_used: True` — the report stays
   actionable while the user repairs their install.

Pure stdlib. The `--json` CLI is a dev/debugging entry point for
inspecting the routing-fallback chain; the skill itself imports the
functions directly, never shelling out.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


# Must match `aggregation.CANONICAL_LENSES`. A test pins parity.
CANONICAL_LENSES = (
    "rules",
    "bugs-drift",
    "docs-version",
    "tests-blindspots",
    "coherence-graph",
    "derivation",
)

SEVERITY_MARKERS = ("🔴", "🟠", "🟢")

# Routing table: lens × marker → ordered list of (skill_name, command).
# Final entry of every cell MUST be ("apex", "/apex") — `/apex` is the
# universal fallback and an import-time assertion enforces this.
ROUTING_TABLE: dict[str, dict[str, list[tuple[str, str]]]] = {
    "rules": {
        "🔴": [("apex", "/apex")],
        "🟠": [("apex", "/apex")],
        "🟢": [("oneshot", "/oneshot"), ("apex", "/apex")],
    },
    "bugs-drift": {
        "🔴": [("apex", "/apex")],
        "🟠": [("apex", "/apex")],
        "🟢": [("oneshot", "/oneshot"), ("apex", "/apex")],
    },
    "docs-version": {
        "🔴": [("apex", "/apex")],
        "🟠": [("humanize-en", "/humanize-en"), ("apex", "/apex")],
        "🟢": [("oneshot", "/oneshot"), ("apex", "/apex")],
    },
    "tests-blindspots": {
        "🔴": [("apex", "/apex")],
        "🟠": [("apex", "/apex")],
        "🟢": [("oneshot", "/oneshot"), ("apex", "/apex")],
    },
    "coherence-graph": {
        "🔴": [("apex", "/apex")],
        "🟠": [("apex", "/apex")],
        "🟢": [("oneshot", "/oneshot"), ("apex", "/apex")],
    },
    "derivation": {
        "🔴": [("apex", "/apex")],
        "🟠": [("apex", "/apex")],
        "🟢": [("oneshot", "/oneshot"), ("apex", "/apex")],
    },
}


# Import-time drift guard. Fail loud if a cell is missing or the final
# fallback isn't `/apex` — would silently degrade routing.
def _validate_routing_table() -> None:
    for lens in CANONICAL_LENSES:
        cells = ROUTING_TABLE.get(lens)
        if cells is None:
            raise AssertionError(
                f"ROUTING_TABLE missing canonical lens: {lens}"
            )
        for marker in SEVERITY_MARKERS:
            candidates = cells.get(marker)
            if not candidates:
                raise AssertionError(
                    f"ROUTING_TABLE[{lens!r}][{marker!r}] is empty"
                )
            if candidates[-1] != ("apex", "/apex"):
                raise AssertionError(
                    f"ROUTING_TABLE[{lens!r}][{marker!r}] final fallback "
                    f"must be ('apex', '/apex'); got {candidates[-1]!r}"
                )


_validate_routing_table()


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------


def _scan_skills_dir(skills_dir: Path) -> dict[str, Path]:
    """Return `{skill_name: SKILL.md path}` for direct subdirs with a SKILL.md."""
    result: dict[str, Path] = {}
    if not skills_dir.is_dir():
        return result
    for entry in skills_dir.iterdir():
        if not entry.is_dir():
            continue
        if entry.name.startswith("."):
            continue
        skill_md = entry / "SKILL.md"
        if skill_md.is_file():
            result[entry.name] = skill_md
    return result


def detect_installed_skills(
    home: Path | None = None,
    project_root: Path | None = None,
) -> dict[str, Path]:
    """Detect installed skills from global + project locations.

    - `home` defaults to `Path.home()`; scanned at `<home>/.claude/skills/`.
    - `project_root`, when set, is scanned at
      `<project_root>/.claude/skills/`. Project skills shadow global on
      name collision (project wins).

    Returns `{skill_name: SKILL.md path}`.
    """
    home_path = home if home is not None else Path.home()
    global_dir = home_path / ".claude" / "skills"
    skills = _scan_skills_dir(global_dir)

    if project_root is not None:
        project_dir = Path(project_root) / ".claude" / "skills"
        project_skills = _scan_skills_dir(project_dir)
        skills.update(project_skills)  # project shadows global

    return skills


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------


def route_cluster(
    lens: str,
    marker: str,
    installed_skills: dict,
) -> dict:
    """Resolve the delegation command for a (lens, marker) cluster.

    Walks `ROUTING_TABLE[lens][marker]` candidates in order. First entry
    whose `skill_name` is in `installed_skills` wins. `fallback_used`
    flips True when at least one earlier candidate was missing.

    When no candidate is installed (including `/apex`), still returns
    the final-fallback command (`/apex`) with `fallback_used=True`.
    Callers may surface the absence separately via `apex_missing`.
    """
    if lens not in ROUTING_TABLE:
        raise KeyError(f"Unknown lens: {lens!r}")
    if marker not in ROUTING_TABLE[lens]:
        raise KeyError(f"Unknown marker: {marker!r} for lens {lens!r}")

    candidates = ROUTING_TABLE[lens][marker]
    for i, (skill_name, command) in enumerate(candidates):
        if skill_name in installed_skills:
            return {
                "command": command,
                "skill": skill_name,
                "lens": lens,
                "marker": marker,
                "fallback_used": i > 0,
            }

    # No candidate installed — emit final fallback (always /apex) with the flag.
    final_skill, final_command = candidates[-1]
    return {
        "command": final_command,
        "skill": final_skill,
        "lens": lens,
        "marker": marker,
        "fallback_used": True,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Detect installed Claude Code skills and print as JSON. "
            "Scans ~/.claude/skills/ + optional project .claude/skills/."
        )
    )
    parser.add_argument(
        "--json", action="store_true", help="Print detection as JSON (default)"
    )
    parser.add_argument(
        "--project-root", type=Path, default=None,
        help="Project root to also scan for .claude/skills/",
    )
    args = parser.parse_args(argv)

    skills = detect_installed_skills(project_root=args.project_root)
    payload = {name: str(path) for name, path in sorted(skills.items())}
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
