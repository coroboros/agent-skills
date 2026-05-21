"""Shared types + utilities for the derivation lens.

Exposes:
    Finding             — canonical finding shape (lens="derivation").
    Claim               — one extracted planning claim (AC / Goal / Decision).
    Artifact            — one resolved planning artifact with freshness.
    IgnoreFile          — parsed `.derivation-ignore` allowlist.
    load_ignore         — minimal YAML-subset parser (mirror of coherence's).
    freshness_days      — age of a file in days via `git log -1 --format=%ct` then mtime.
    classify_severity_by_freshness — caps severity when planning artifact is stale.
"""

from __future__ import annotations

import os
import subprocess
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Classification taxonomy (per spec).
GAP = "GAP"
SCOPE_ADD = "SCOPE-ADD"
DECISION_OVERRIDE = "DECISION-OVERRIDE"
CONSISTENT = "CONSISTENT"
UNCLASSIFIED = "UNCLASSIFIED"  # Python-stage placeholder; subagent fills in.

CLASSIFICATIONS = (GAP, SCOPE_ADD, DECISION_OVERRIDE, CONSISTENT, UNCLASSIFIED)

# Default severity per classification.
DEFAULT_SEVERITY = {
    GAP: "Medium",
    SCOPE_ADD: "Low",
    DECISION_OVERRIDE: "Medium",
    CONSISTENT: "Low",
    UNCLASSIFIED: "Low",
}

# Freshness thresholds (in days).
FRESHNESS_CAP_LOW = 30
FRESHNESS_SUMMARY_ONLY = 90


@dataclass
class Finding:
    """Canonical finding emitted by the derivation lens."""

    classification: str = UNCLASSIFIED
    severity: str = "Medium"
    location: str = ""
    finding: str = ""
    recommendation: str = ""
    confidence: int = 0
    lens: str = "derivation"
    artifact_path: str = ""
    artifact_freshness_days: int = -1

    def to_dict(self) -> dict:
        d = asdict(self)
        ordered = {
            "lens": d.pop("lens"),
            "classification": d.pop("classification"),
            "severity": d.pop("severity"),
            "location": d.pop("location"),
            "finding": d.pop("finding"),
            "recommendation": d.pop("recommendation"),
            "confidence": d.pop("confidence"),
        }
        ordered.update(d)
        return ordered


@dataclass
class Claim:
    """One extracted planning claim — an AC item, a goal, or a decision."""

    kind: str  # "ac" | "goal" | "decision" | "task"
    text: str
    source_line: int = 0


@dataclass
class Artifact:
    """One resolved planning artifact."""

    path: str
    kind: str  # "brainstorm" | "spec" | "apex-plan" | "pr-body" | "issue-body" | "doc"
    freshness_days: int = -1
    claims: list = field(default_factory=list)


@dataclass
class IgnoreFile:
    """Parsed `.derivation-ignore` contents — nested {key: {sub: [values]}}."""

    data: dict = field(default_factory=dict)

    def list_for(self, top: str, sub: str) -> list:
        return list(self.data.get(top, {}).get(sub, []))

    def has(self, top: str, sub: str, value: str) -> bool:
        return value in self.list_for(top, sub)


def load_ignore(repo: Path) -> IgnoreFile:
    """Parse `.derivation-ignore` at the repo root.

    Same grammar as coherence's `.coherence-ignore`: indent-2 nested keys,
    indent-4 list items, comments via `#`. Raises ValueError on malformed
    input.
    """
    path = repo / ".derivation-ignore"
    if not path.exists():
        return IgnoreFile()

    data: dict = {}
    current_top: str | None = None
    current_sub: str | None = None

    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        stripped = line.lstrip()

        if indent == 0:
            if not stripped.endswith(":"):
                raise ValueError(f".derivation-ignore:{lineno}: expected '<key>:' at top level, got {raw!r}")
            current_top = stripped[:-1].strip()
            current_sub = None
            data.setdefault(current_top, {})
        elif indent == 2:
            if current_top is None:
                raise ValueError(f".derivation-ignore:{lineno}: sub-key before top-level key: {raw!r}")
            if not stripped.endswith(":"):
                raise ValueError(f".derivation-ignore:{lineno}: expected '<sub-key>:' at indent 2, got {raw!r}")
            current_sub = stripped[:-1].strip()
            data[current_top].setdefault(current_sub, [])
        elif indent == 4:
            if current_top is None or current_sub is None:
                raise ValueError(f".derivation-ignore:{lineno}: list item without sub-key: {raw!r}")
            if not stripped.startswith("- "):
                raise ValueError(f".derivation-ignore:{lineno}: expected '- <value>' at indent 4, got {raw!r}")
            value = stripped[2:].strip()
            if (value.startswith('"') and value.endswith('"')) or (
                value.startswith("'") and value.endswith("'")
            ):
                value = value[1:-1]
            data[current_top][current_sub].append(value)
        else:
            raise ValueError(f".derivation-ignore:{lineno}: unexpected indent {indent}: {raw!r}")

    return IgnoreFile(data=data)


def freshness_days(path: Path, now: float | None = None) -> int:
    """Age of `path` in days. Uses `git log -1 --format=%ct` when path is in
    a git repo; falls back to `mtime` otherwise. Returns -1 when neither is
    available (missing file, unreadable mtime).
    """
    if not path.exists():
        return -1
    ts: float | None = None
    if (path.parent / ".git").exists() or _in_git_repo(path):
        try:
            r = subprocess.run(
                ["git", "-C", str(path.parent), "log", "-1", "--format=%ct", "--", str(path.name)],
                capture_output=True, text=True, timeout=5,
            )
            if r.returncode == 0 and r.stdout.strip():
                ts = float(r.stdout.strip())
        except (subprocess.SubprocessError, OSError):
            pass
    if ts is None:
        try:
            ts = os.path.getmtime(path)
        except OSError:
            return -1
    current = now if now is not None else time.time()
    age = current - ts
    if age < 0:
        return 0
    return int(age // 86400)


def _in_git_repo(path: Path) -> bool:
    try:
        r = subprocess.run(
            ["git", "-C", str(path.parent), "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, timeout=2,
        )
        return r.returncode == 0 and r.stdout.strip() == "true"
    except (subprocess.SubprocessError, OSError):
        return False


def classify_severity_by_freshness(severity: str, days: int) -> str:
    """Cap severity when the planning artifact is stale.

    >FRESHNESS_CAP_LOW days → cap at Low.
    The >FRESHNESS_SUMMARY_ONLY case (drop findings entirely) is handled by
    the orchestrator, not here — this function only adjusts severity.
    """
    if days < 0:
        return severity  # unknown freshness — pass through
    if days > FRESHNESS_CAP_LOW:
        return "Low"
    return severity


def should_emit_findings(days: int) -> bool:
    """When True, the artifact emits classified findings. When False, only
    the coverage summary references it (no row in the findings table).
    """
    if days < 0:
        return True  # unknown freshness — emit
    return days <= FRESHNESS_SUMMARY_ONLY
