"""Shared helpers for the --apply-safe writers."""

from __future__ import annotations

from difflib import unified_diff
from pathlib import Path


def confirm_write(path: Path, diff_text: str, yes: bool = False) -> bool:
    """Show the diff, prompt the user, return True when the write is approved.

    `yes=True` bypasses the prompt (the -y / --yes flag the orchestrator
    forwards). Otherwise reads `y` / `yes` from stdin (case-insensitive).
    """
    print(f"\n--- {path} ---")
    print(diff_text.rstrip())
    print("--- end diff ---")
    if yes:
        return True
    answer = input(f"Apply this change to {path}? (y/N) ").strip().lower()
    return answer in ("y", "yes")


def unified_diff_block(path: Path, before: str, after: str) -> str:
    """Minimal `diff -u`-style block via difflib."""
    rel = path.name
    a_lines = before.splitlines(keepends=False)
    b_lines = after.splitlines(keepends=False)
    diff = unified_diff(
        a_lines, b_lines,
        fromfile=f"a/{rel}", tofile=f"b/{rel}", lineterm="",
    )
    return "\n".join(diff)
