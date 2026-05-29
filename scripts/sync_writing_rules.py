#!/usr/bin/env python3
"""Propagate canonical blocks from `.claude/rules/skill-{prose,label-hygiene,execution-discipline}-rules.md` into each declared SKILL.md.

Three rule families share this script:

- `writing-rules` — style block (front-load verbs, no marketing words, no AI tells).
- `label-hygiene` — author-coordinate vocabulary block (`WS-N`, "the rebuild", "spec AC", etc.).
- `execution-discipline` — engineering block (minimal scope, general solutions over test-gaming, investigate before claiming).

Each rule has its own canonical file, marker pair, and declared-skill list. A present block is
replaced in-place; an absent one is inserted right after H1. Inserts prepend, so the rule iterated
LAST lands closest to H1. Tuple order is therefore (writing-rules, label-hygiene, execution-discipline),
producing top-to-bottom: execution-discipline, label-hygiene, writing-rules.

Idempotent — second run produces zero diff. Exit 0 on success, 1 on parse error
(any canonical file malformed), 2 if any declared skill is missing or malformed.

Output: one line per (rule, skill) — `{UPDATED|UNCHANGED|INSERTED} skills/<name>/SKILL.md (<rule_id>)`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import NamedTuple

REPO_ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = REPO_ROOT / ".claude" / "rules"
SKILLS_DIR = REPO_ROOT / "skills"


class Rule(NamedTuple):
    id: str
    canonical_file: Path
    start_marker: str
    end_marker: str
    declared_header: str


RULES: tuple[Rule, ...] = (
    Rule(
        id="writing-rules",
        canonical_file=RULES_DIR / "skill-prose-rules.md",
        start_marker="<!-- canonical:writing-rules:start -->",
        end_marker="<!-- canonical:writing-rules:end -->",
        declared_header="## Declared prose-emitting skills",
    ),
    Rule(
        id="label-hygiene",
        canonical_file=RULES_DIR / "skill-label-hygiene-rules.md",
        start_marker="<!-- canonical:label-hygiene:start -->",
        end_marker="<!-- canonical:label-hygiene:end -->",
        declared_header="## Declared label-hygiene skills",
    ),
    Rule(
        id="execution-discipline",
        canonical_file=RULES_DIR / "skill-execution-discipline-rules.md",
        start_marker="<!-- canonical:execution-discipline:start -->",
        end_marker="<!-- canonical:execution-discipline:end -->",
        declared_header="## Declared execution-discipline skills",
    ),
)


def parse_canonical_file(
    text: str, start_marker: str, end_marker: str, declared_header: str
) -> tuple[str, list[str]]:
    """Extract the canonical block (between markers) and the declared skill list."""
    start = text.find(start_marker)
    end = text.find(end_marker)
    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            f"canonical markers not found or malformed (looking for {start_marker!r} and {end_marker!r})"
        )
    block = text[start : end + len(end_marker)]

    m = re.search(
        rf"^{re.escape(declared_header)}\s*$(.*?)^## ",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if not m:
        raise ValueError(f"section {declared_header!r} not found")
    declared = []
    for line in m.group(1).splitlines():
        bm = re.match(r"^- ([a-z][a-z0-9-]*)\s*$", line.strip())
        if bm:
            declared.append(bm.group(1))
    if not declared:
        raise ValueError(f"declared skill list under {declared_header!r} is empty")
    return block, declared


def patch_skill(
    skill_md: Path, canonical_block: str, start_marker: str, end_marker: str
) -> str:
    """Insert or replace the canonical block in a SKILL.md.

    Returns one of: "UPDATED", "UNCHANGED", "INSERTED".
    """
    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    if start_marker in text and end_marker in text:
        start_idx = text.index(start_marker)
        end_idx = text.index(end_marker) + len(end_marker)
        new_text = text[:start_idx] + canonical_block + text[end_idx:]
        if new_text == text:
            return "UNCHANGED"
        skill_md.write_text(new_text, encoding="utf-8")
        return "UPDATED"

    h1_pos = None
    for i, line in enumerate(lines):
        if line.startswith("# ") and not line.startswith("## "):
            h1_pos = i
            break
    if h1_pos is None:
        raise ValueError(f"{skill_md}: no H1 heading found")

    head = lines[: h1_pos + 1]
    tail = lines[h1_pos + 1 :]
    while tail and tail[0].strip() == "":
        tail.pop(0)

    insertion = "\n" + canonical_block + "\n\n"
    new_text = "".join(head) + insertion + "".join(tail)
    skill_md.write_text(new_text, encoding="utf-8")
    return "INSERTED"


def process_rule(rule: Rule) -> list[str]:
    """Process one rule: parse its canonical file, patch every declared skill.

    Returns the list of failing skill names (empty on success).
    """
    try:
        canonical_text = rule.canonical_file.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR ({rule.id}): cannot read canonical file: {exc}", file=sys.stderr)
        raise

    block, declared = parse_canonical_file(
        canonical_text, rule.start_marker, rule.end_marker, rule.declared_header
    )

    failures: list[str] = []
    for name in declared:
        skill_md = SKILLS_DIR / name / "SKILL.md"
        if not skill_md.is_file():
            print(f"MISSING skills/{name}/SKILL.md ({rule.id})", file=sys.stderr)
            failures.append(name)
            continue
        try:
            status = patch_skill(skill_md, block, rule.start_marker, rule.end_marker)
        except ValueError as exc:
            print(f"ERROR skills/{name}/SKILL.md ({rule.id}): {exc}", file=sys.stderr)
            failures.append(name)
            continue
        print(f"{status} skills/{name}/SKILL.md ({rule.id})")
    return failures


def main() -> int:
    aggregate_failures: list[tuple[str, str]] = []
    for rule in RULES:
        try:
            failures = process_rule(rule)
        except (OSError, ValueError) as exc:
            print(f"ERROR ({rule.id}): {exc}", file=sys.stderr)
            return 1
        for name in failures:
            aggregate_failures.append((rule.id, name))
    return 2 if aggregate_failures else 0


if __name__ == "__main__":
    sys.exit(main())
