"""Failing-test writer for --apply-safe.

Given a confirmed bug + repro vector, writes one focused failing test
under the host repo's test layout. Additive only — never modifies
existing files. The test should fail on the unfixed code and pass after
the user implements the fix.

Test layout detection:
    - `tests/` with `*.py` files → Python (pytest or unittest)
    - `tests/` with `*.test.ts` or `*.spec.ts` files → TypeScript
    - Fallback: Python under `tests/<bug-id>/test_<bug-id>.py`.
"""

from __future__ import annotations

from pathlib import Path

from ._common import confirm_write, unified_diff_block


def _bug_slug(bug_id: str) -> str:
    s = bug_id.lower()
    out = []
    last_underscore = True
    for ch in s:
        if ch.isalnum():
            out.append(ch)
            last_underscore = False
        elif not last_underscore:
            out.append("_")
            last_underscore = True
    return "".join(out).strip("_") or "bug"


def _detect_layout(repo: Path) -> str:
    """Return 'python' or 'typescript' based on existing test files."""
    tests = repo / "tests"
    if tests.exists():
        for p in tests.rglob("*.py"):
            if p.is_file():
                return "python"
        for p in tests.rglob("*.test.ts"):
            if p.is_file():
                return "typescript"
        for p in tests.rglob("*.spec.ts"):
            if p.is_file():
                return "typescript"
    src = repo / "src"
    if src.exists():
        for p in src.rglob("*.ts"):
            if p.is_file():
                return "typescript"
    return "python"


def _python_test_body(bug_id: str, repro: str, expected_failure: str) -> str:
    func = _bug_slug(bug_id)
    safe_repro = repro.replace('"""', '"\\""\\""\\"')
    return (
        f'"""Failing test for {bug_id}.\n\n'
        f'Repro: {safe_repro}\n'
        f'Expected failure on unfixed code: {expected_failure}\n'
        f'"""\n\n'
        f"import unittest\n\n\n"
        f"class Test{func.title().replace('_', '')}(unittest.TestCase):\n"
        f"    def test_{func}_reproduces_bug(self):\n"
        f"        # TODO: replace with the actual repro for {bug_id}.\n"
        f"        # Repro vector: {repro!r}\n"
        f"        # Expected failure: {expected_failure!r}\n"
        f"        self.fail({expected_failure!r})\n\n\n"
        f'if __name__ == "__main__":\n'
        f"    unittest.main()\n"
    )


def _typescript_test_body(bug_id: str, repro: str, expected_failure: str) -> str:
    func = _bug_slug(bug_id)
    return (
        f"// Failing test for {bug_id}.\n"
        f"// Repro: {repro}\n"
        f"// Expected failure on unfixed code: {expected_failure}\n\n"
        f"import {{ describe, it, expect }} from 'vitest';\n\n"
        f"describe('{bug_id}', () => {{\n"
        f"  it('{func} reproduces the bug', () => {{\n"
        f"    // TODO: replace with the actual repro for {bug_id}.\n"
        f"    // Repro vector: {repro!r}\n"
        f"    // Expected failure: {expected_failure!r}\n"
        f"    expect.fail({expected_failure!r});\n"
        f"  }});\n"
        f"}});\n"
    )


def _target_path(repo: Path, bug_id: str, layout: str) -> Path:
    slug = _bug_slug(bug_id)
    tests = repo / "tests"
    if layout == "typescript":
        return tests / f"{slug}.test.ts"
    return tests / f"test_{slug}.py"


def write(
    repo: Path,
    bug_id: str,
    repro: str,
    expected_failure: str,
    yes: bool = False,
) -> dict:
    """Write the failing test. Returns a summary dict.

    Refuses (returns `status: refusing`) when the target path already
    exists — overwriting an existing test is out of contract.
    """
    layout = _detect_layout(repo)
    target = _target_path(repo, bug_id, layout)

    if target.exists():
        return {
            "status": "refusing: existing-test",
            "reason": f"{target} already exists — never overwrite",
            "target": str(target.relative_to(repo)),
        }

    body = (
        _python_test_body(bug_id, repro, expected_failure)
        if layout == "python"
        else _typescript_test_body(bug_id, repro, expected_failure)
    )

    diff = unified_diff_block(target, "", body)
    if not confirm_write(target, diff, yes=yes):
        return {"status": "skipped", "target": str(target.relative_to(repo))}

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    return {
        "status": "applied",
        "target": str(target.relative_to(repo)),
        "layout": layout,
    }
