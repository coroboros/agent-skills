"""Write a reviewed regression test for --apply-safe, additively.

The reviewer supplies actual test content and its project-relative path after
inspecting the host's test layout and runner. This writer previews and persists
that content; it cannot derive an executable reproducer from a prose bug report.
The caller verifies failure on the defect and success after its correction.
"""

from __future__ import annotations

from pathlib import Path

from ._common import confirm_write, unified_diff_block


def write(
    repo: Path,
    bug_id: str,
    repro: str,
    expected_failure: str,
    yes: bool = False,
    *,
    test_content: str | None = None,
    test_path: str | None = None,
) -> dict:
    """Preview and write exact reviewed content; never overwrite a file."""
    if not isinstance(test_content, str) or not test_content.strip():
        return {"status": "refusing: missing-test-content",
                "reason": "supply a reviewed executable test for the actual project runner"}
    if not isinstance(test_path, str) or not test_path.strip() or "\0" in test_path:
        return {"status": "refusing: invalid-test-path",
                "reason": "supply the test's repository-relative path"}
    relative = Path(test_path)
    root = repo.resolve()
    target = root / relative
    if (not root.is_dir() or relative.is_absolute() or ".." in relative.parts
            or relative == Path(".") or not target.resolve().is_relative_to(root)):
        return {"status": "refusing: invalid-test-path",
                "reason": "the test path must stay inside the repository"}
    if target.exists() or target.is_symlink():
        return {"status": "refusing: existing-test", "target": test_path,
                "reason": "never overwrite an existing test"}

    diff = unified_diff_block(target, "", test_content)
    if not confirm_write(target, diff, yes=yes):
        return {"status": "skipped", "target": test_path}
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with target.open("x", encoding="utf-8", newline="") as handle:
            handle.write(test_content)
    except FileExistsError:
        return {"status": "refusing: existing-test", "target": test_path,
                "reason": "target appeared after preview; never overwrite"}
    return {"status": "applied", "target": test_path, "bug_id": bug_id}
