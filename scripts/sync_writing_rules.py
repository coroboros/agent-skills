#!/usr/bin/env python3
"""Propagate the canonical writing-rules block from .claude/rules/skill-prose-rules.md into each declared SKILL.md.

Idempotent — second run produces zero diff. Exit 0 on success, 1 on parse error
(canonical file malformed), 2 if any declared skill is missing or malformed.

Output: one line per skill (UPDATED | UNCHANGED | INSERTED skills/<name>/SKILL.md).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICAL_FILE = REPO_ROOT / ".claude" / "rules" / "skill-prose-rules.md"
SKILLS_DIR = REPO_ROOT / "skills"

START_MARKER = "<!-- canonical:writing-rules:start -->"
END_MARKER = "<!-- canonical:writing-rules:end -->"


def parse_canonical_file(text: str) -> tuple[str, list[str]]:
    """Extract the canonical block (between markers) and the declared skill list.

    The block sits inside a fenced ```markdown code block in skill-prose-rules.md.
    The declared list is rendered as `- name` bullets under "## Declared prose-emitting skills".
    """
    # Locate the canonical block — between the two markers, INSIDE the fenced code block.
    start = text.find(START_MARKER)
    end = text.find(END_MARKER)
    if start == -1 or end == -1 or end <= start:
        raise ValueError("canonical markers not found or malformed in canonical file")
    block = text[start : end + len(END_MARKER)]

    # Locate the declared skills section.
    m = re.search(
        r"^## Declared prose-emitting skills\s*$(.*?)^## ",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if not m:
        raise ValueError("'## Declared prose-emitting skills' section not found")
    declared = []
    for line in m.group(1).splitlines():
        bm = re.match(r"^- ([a-z][a-z0-9-]*)\s*$", line.strip())
        if bm:
            declared.append(bm.group(1))
    if not declared:
        raise ValueError("declared skill list is empty")
    return block, declared


def patch_skill(skill_md: Path, canonical_block: str) -> str:
    """Insert or replace the canonical block in a SKILL.md.

    Returns one of: "UPDATED", "UNCHANGED", "INSERTED".
    """
    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    # If markers already present, replace from start marker to end marker (inclusive).
    if START_MARKER in text and END_MARKER in text:
        start_idx = text.index(START_MARKER)
        end_idx = text.index(END_MARKER) + len(END_MARKER)
        new_text = text[:start_idx] + canonical_block + text[end_idx:]
        if new_text == text:
            return "UNCHANGED"
        skill_md.write_text(new_text, encoding="utf-8")
        return "UPDATED"

    # Markers absent — insert immediately after the H1 line.
    h1_pos = None
    for i, line in enumerate(lines):
        if line.startswith("# ") and not line.startswith("## "):
            h1_pos = i
            break
    if h1_pos is None:
        raise ValueError(f"{skill_md}: no H1 heading found")

    # Build the insertion: blank line + canonical block + blank line, after the H1.
    # We want H1 followed by exactly one blank line, then the canonical block, then exactly
    # one blank line, then the original content that came after H1.
    head = lines[: h1_pos + 1]
    tail = lines[h1_pos + 1 :]
    # Strip leading blank lines from tail so we control spacing.
    while tail and tail[0].strip() == "":
        tail.pop(0)

    insertion = "\n" + canonical_block + "\n\n"
    new_text = "".join(head) + insertion + "".join(tail)
    skill_md.write_text(new_text, encoding="utf-8")
    return "INSERTED"


def main() -> int:
    try:
        canonical_text = CANONICAL_FILE.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: cannot read canonical file: {exc}", file=sys.stderr)
        return 1

    try:
        block, declared = parse_canonical_file(canonical_text)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    failures = []
    for name in declared:
        skill_md = SKILLS_DIR / name / "SKILL.md"
        if not skill_md.is_file():
            print(f"MISSING skills/{name}/SKILL.md", file=sys.stderr)
            failures.append(name)
            continue
        try:
            status = patch_skill(skill_md, block)
        except ValueError as exc:
            print(f"ERROR skills/{name}/SKILL.md: {exc}", file=sys.stderr)
            failures.append(name)
            continue
        print(f"{status} skills/{name}/SKILL.md")

    return 2 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
