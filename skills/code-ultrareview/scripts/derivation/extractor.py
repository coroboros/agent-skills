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
AC_FIELD_HEADER = re.compile(r"^\*\*Acceptance\s+criteria:\*\*(?:\s.*)?$", re.IGNORECASE)
FIELD_HEADER = re.compile(r"^\*\*[^*]+:\*\*(?:\s.*)?$")
AC_ITEM = re.compile(r"^\s*-\s*\[[ xX]\]\s+(.+?)\s*$")

# Goal items inside a "Goals" / "Objectives" section.
GOAL_SECTION_HEADER = re.compile(r"^(#{1,6})\s+(goals|objectives)\s*$", re.IGNORECASE)
GOAL_ITEM = re.compile(r"^\s*-\s+(?:\*\*[\w\d-]+\*\*\s*[—:-]\s*)?(.+?)\s*$")

# Decision items inside a "Decisions resolved" / "Decisions" block.
DECISION_SECTION_HEADER = re.compile(
    r"^(#{1,6})\s+(decisions?(?:\s+resolved)?|resolved\s+decisions?)\s*$", re.IGNORECASE
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
    active_claim: Claim | None = None
    item_indent = 0

    for idx, line in enumerate(lines, start=1):
        if AC_FIELD_HEADER.match(line):
            state = "ac"
            state_depth = 0
            active_claim = None
            continue
        ac_match = AC_SECTION_HEADER.match(line)
        if ac_match:
            state = "ac"
            state_depth = len(ac_match.group(1))
            active_claim = None
            continue
        goal_match = GOAL_SECTION_HEADER.match(line)
        if goal_match:
            state = "goal"
            state_depth = len(goal_match.group(1))
            active_claim = None
            continue
        decision_match = DECISION_SECTION_HEADER.match(line)
        if decision_match:
            state = "decision"
            state_depth = len(decision_match.group(1))
            active_claim = None
            continue
        task_match = TASK_SECTION_HEADER.match(line)
        if task_match:
            state = "task"
            state_depth = 0
            active_claim = None
            continue

        # Sibling/parent heading closes the section.
        new_section = re.match(r"^(#{1,6})\s+", line)
        if new_section:
            active_claim = None
            new_depth = len(new_section.group(1))
            if state is not None and (state_depth == 0 or new_depth <= state_depth):
                state = None

        # Canonical Forge fields end at the next field, including inline notes.
        if state_depth == 0 and FIELD_HEADER.match(line):
            state = None
            active_claim = None

        pattern = {"ac": AC_ITEM, "task": TASK_ITEM,
                   "goal": GOAL_ITEM, "decision": DECISION_ITEM}.get(state)
        match = pattern.match(line) if pattern else None
        indent = len(line) - len(line.lstrip())
        if match:
            active_claim = Claim(kind=state, text=match.group(1).strip(), source_line=idx)
            claims.append(active_claim)
            item_indent = indent
        elif line.strip():
            if active_claim is not None and indent > item_indent:
                # Normal Markdown list continuations often carry the When/Then
                # outcome; dropping them loses the actual acceptance condition.
                active_claim.text += "\n" + line.strip()
            else:
                active_claim = None

    return claims


def detect_artifact_kind(path) -> str:
    """Best-effort guess from a filename. The orchestrator passes the kind
    explicitly when known (e.g., `--reconcile gh:pr:42` is always 'pr-body').
    This helper covers @auto-discovered paths.
    """
    name = str(path).lower()
    if "forge" in name:
        return "forge"
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
