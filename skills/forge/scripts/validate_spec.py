#!/usr/bin/env python3
"""
validate_spec.py — validate a spec.md against the canonical schema.

Usage:
    validate_spec.py <spec.md>

Checks:
  - 3-7 workstreams (### WS-N: headings under ## Workstreams)
  - Each workstream has Priority (P0/P1/P2) and Complexity (S/M/L/XL)
  - Each workstream has a non-empty Acceptance criteria block
  - Dependencies reference real workstream IDs
  - No cycles in the dependency graph

Exit:
  0   valid
  1   schema violation (wrong count, missing fields)
  2   dependency error (unknown ID or cycle)

Emits RESULT: key=value lines on stdout; detailed findings on stderr.

Requires Python 3.7+. No third-party dependencies.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

WS_HEADING = re.compile(r"^###\s+(WS-\d+):", re.MULTILINE)
PRIORITY = re.compile(r"\|\s*Priority\s*\|\s*(P[012])\s*\|")
COMPLEXITY = re.compile(r"\|\s*Complexity\s*\|\s*(XL|S|M|L)\s*\|")
DEPENDS = re.compile(r"\|\s*Depends on\s*\|\s*(.+?)\s*\|")
AC_HEADER = re.compile(r"\*\*Acceptance criteria:\*\*")
AC_ITEM = re.compile(r"^-\s*\[[ x]\]\s+\S", re.MULTILINE)


def split_blocks(content):
    """Return [(ws_id, block_text), ...] for every ### WS-N: under ## Workstreams."""
    m = re.search(
        r"^## Workstreams\s*\n(.*?)(?=^## |\Z)",
        content,
        re.DOTALL | re.MULTILINE,
    )
    if not m:
        return []

    body = m.group(1)
    pieces = re.split(r"(?=^### WS-\d+:)", body, flags=re.MULTILINE)
    blocks = []
    for piece in pieces:
        h = WS_HEADING.search(piece)
        if h:
            blocks.append((h.group(1), piece))
    return blocks


def validate_workstream(ws_id, block, known_ids):
    errors = []

    if not PRIORITY.search(block):
        errors.append(f"{ws_id}: missing or invalid Priority (expected P0/P1/P2)")
    if not COMPLEXITY.search(block):
        errors.append(f"{ws_id}: missing or invalid Complexity (expected S/M/L/XL)")

    ac = AC_HEADER.search(block)
    if not ac:
        errors.append(f"{ws_id}: missing Acceptance criteria section")
    else:
        tail = block[ac.end():]
        if not AC_ITEM.search(tail):
            errors.append(f"{ws_id}: Acceptance criteria section has no `- [ ]` items")

    dep = DEPENDS.search(block)
    if dep:
        text = dep.group(1).strip()
        if text not in ("—", "-", ""):
            for dep_id in re.findall(r"WS-\d+", text):
                if dep_id not in known_ids:
                    errors.append(f"{ws_id}: depends on {dep_id} which is not defined")

    return errors


def build_graph(blocks):
    graph = {}
    for ws_id, block in blocks:
        deps = []
        dep = DEPENDS.search(block)
        if dep:
            text = dep.group(1).strip()
            if text not in ("—", "-", ""):
                deps = re.findall(r"WS-\d+", text)
        graph[ws_id] = deps
    return graph


def find_cycle(graph):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = defaultdict(lambda: WHITE)
    parent = {}

    def dfs(start):
        stack = [(start, iter(graph.get(start, [])))]
        color[start] = GRAY
        while stack:
            node, it = stack[-1]
            try:
                nxt = next(it)
            except StopIteration:
                color[node] = BLACK
                stack.pop()
                continue

            if color[nxt] == GRAY:
                # Reconstruct cycle from nxt back to node, then close.
                path = [nxt, node]
                cur = parent.get(node)
                while cur is not None and cur != nxt:
                    path.append(cur)
                    cur = parent.get(cur)
                path.append(nxt)
                path.reverse()
                return path
            if color[nxt] == WHITE:
                color[nxt] = GRAY
                parent[nxt] = node
                stack.append((nxt, iter(graph.get(nxt, []))))
        return []

    for node in list(graph):
        if color[node] == WHITE:
            cyc = dfs(node)
            if cyc:
                return cyc
    return []


def main():
    if len(sys.argv) < 2:
        print("usage: validate_spec.py <spec.md>", file=sys.stderr)
        return 1

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"RESULT: error=file-missing path={path}")
        return 1

    content = path.read_text(encoding="utf-8")
    blocks = split_blocks(content)
    count = len(blocks)

    if count == 0:
        print("RESULT: error=no-workstreams-section")
        return 1
    if count < 3 or count > 7:
        print(f"  spec must have 3-7 workstreams, found {count}", file=sys.stderr)
        print(f"RESULT: error=ws-count-out-of-range count={count}")
        return 1

    known_ids = {ws_id for ws_id, _ in blocks}
    schema_errors = []
    for ws_id, block in blocks:
        schema_errors.extend(validate_workstream(ws_id, block, known_ids))

    if schema_errors:
        for err in schema_errors:
            print(f"  {err}", file=sys.stderr)
        print(f"RESULT: error=schema-violations count={len(schema_errors)}")
        return 1

    graph = build_graph(blocks)
    cycle = find_cycle(graph)
    if cycle:
        joined = " -> ".join(cycle)
        print(f"  cycle: {joined}", file=sys.stderr)
        print(f"RESULT: error=dependency-cycle path={joined}")
        return 2

    print(f"RESULT: ok=true workstreams={count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
