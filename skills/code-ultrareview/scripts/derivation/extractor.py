"""Deterministic structure extraction from planning artifacts.

The derivation lens needs to surface what an artifact CLAIMS so the LLM
subagent can compare each claim against the diff. This module owns the
deterministic part — regex extraction of acceptance criteria, goals, and
decisions — but does NOT classify (that's the subagent's job at runtime).

The output is a list of `Claim` objects with `kind`, `text`, `source_line`.
"""

from __future__ import annotations

import re

from ._common import Claim

# AC items inside a section whose heading matches /Acceptance criteria/i.
AC_SECTION_HEADER = re.compile(r"^(#{1,6})\s+.*acceptance\s+criteria", re.IGNORECASE)
AC_ITEM = re.compile(r"^\s*-\s*\[[ xX]\]\s+(.+?)\s*$")

# Goal items inside a "Goals" / "Objectives" section.
GOAL_SECTION_HEADER = re.compile(r"^(#{1,6})\s+(goals|objectives)\s*$", re.IGNORECASE)
GOAL_ITEM = re.compile(r"^\s*-\s+(?:\*\*[\w\d-]+\*\*\s*[—:-]\s*)?(.+?)\s*$")

# Decision items inside a "Decisions resolved" / "Decisions" block.
DECISION_SECTION_HEADER = re.compile(
    r"^(#{1,6})\s+(decisions(?:\s+resolved)?|resolved\s+decisions)\s*$", re.IGNORECASE
)
DECISION_ITEM = re.compile(r"^\s*-\s+(?:\*\*[\w\d-]+\*\*\s*[—:-]\s*)?(.+?)\s*$")

# Task items inside a Tasks block (spec-style).
TASK_SECTION_HEADER = re.compile(r"^\*\*Tasks:\*\*\s*$", re.IGNORECASE)
TASK_ITEM = re.compile(r"^\s*-\s*\[[ xX]\]\s+(.+?)\s*$")


def extract_claims(markdown: str) -> list:
    """Walk the markdown and pull every claim into a `Claim` list.

    Scans for sections matching Acceptance criteria, Goals/Objectives, and
    Decisions; collects the bullet items within. Items outside any of the
    declared section types are ignored — the extraction is intentionally
    conservative to keep false positives low.
    """
    claims: list = []
    lines = markdown.splitlines()
    state: str | None = None
    state_depth: int = 0

    for idx, line in enumerate(lines, start=1):
        ac_match = AC_SECTION_HEADER.match(line)
        if ac_match:
            state = "ac"
            state_depth = len(ac_match.group(1))
            continue
        goal_match = GOAL_SECTION_HEADER.match(line)
        if goal_match:
            state = "goal"
            state_depth = len(goal_match.group(1))
            continue
        decision_match = DECISION_SECTION_HEADER.match(line)
        if decision_match:
            state = "decision"
            state_depth = len(decision_match.group(1))
            continue
        task_match = TASK_SECTION_HEADER.match(line)
        if task_match:
            state = "task"
            state_depth = 0
            continue

        # Sibling/parent heading closes the section.
        new_section = re.match(r"^(#{1,6})\s+", line)
        if new_section:
            new_depth = len(new_section.group(1))
            if state is not None and new_depth <= state_depth:
                state = None

        # `**Bold:**` standalone closes the Tasks-style section.
        if state == "task" and re.match(r"^\*\*[\w\d ]+:\*\*\s*$", line):
            if not TASK_SECTION_HEADER.match(line):
                state = None

        if state == "ac":
            m = AC_ITEM.match(line)
            if m:
                claims.append(Claim(kind="ac", text=m.group(1).strip(), source_line=idx))
        elif state == "task":
            m = TASK_ITEM.match(line)
            if m:
                claims.append(Claim(kind="task", text=m.group(1).strip(), source_line=idx))
        elif state == "goal":
            m = GOAL_ITEM.match(line)
            if m:
                text = m.group(1).strip()
                if text:
                    claims.append(Claim(kind="goal", text=text, source_line=idx))
        elif state == "decision":
            m = DECISION_ITEM.match(line)
            if m:
                text = m.group(1).strip()
                if text:
                    claims.append(Claim(kind="decision", text=text, source_line=idx))

    return claims


def detect_artifact_kind(path) -> str:
    """Best-effort guess from a filename. The orchestrator passes the kind
    explicitly when known (e.g., `--reconcile gh:pr:42` is always 'pr-body').
    This helper covers @auto-discovered paths.
    """
    name = str(path).lower()
    if "brainstorm" in name:
        return "brainstorm"
    if "spec" in name:
        return "spec"
    if "/apex/" in name or name.endswith("/apex"):
        return "apex-plan"
    if "rfc" in name or "/rfcs/" in name:
        return "rfc"
    if "adr" in name or "/adr/" in name:
        return "adr"
    if "proposal" in name or "/proposals/" in name:
        return "proposal"
    if "design" in name or "/design/" in name:
        return "design"
    return "doc"
