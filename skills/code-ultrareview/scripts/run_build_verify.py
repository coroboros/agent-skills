#!/usr/bin/env python3
"""Phase 3.5 build-verification orchestrator (gated by `--verify-build`).

Composes `build_detect.detect()` (canonical test command per repo type)
with `synthesis_core.iterate_unverified()` (+30 confidence, cap 95,
floor 80). Runs BEFORE Phase 4 validators — confirmed promotions skip
the Haiku phase entirely.

Verdict rule:
    - Build exits non-zero AND finding axis ∈ {correctness, tests,
      design-api, performance} → "confirmed" (promote +30, cap 95,
      floor 80).
    - Otherwise → "inconclusive" (passes through to validators).

The "disproved" verdict is intentionally unused at MVP — a passing
build does not actively disprove an LLM finding, and a "drop" verdict
would silently lose Unverified candidates that the validator phase can
still confirm. A2 stays load-bearing for those.

Style/Documentation/Intent/Simplification/Coherence findings are
inconclusive regardless of build result — the test command does not
exercise them.

Usage:
    python3 run_build_verify.py \\
        --scope <scope.json> \\
        --findings <axis-findings.jsonl> \\
        --output <build-verified.jsonl> \\
        [--repo <path>] [--timeout 120]

Exit codes:
    0  — ran cleanly (including graceful skip when no build tool found).
    2  — argument error or unreadable inputs.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import build_detect  # noqa: E402
import synthesis_core  # noqa: E402

# Axes whose findings benefit from build verification. Bug-class only —
# the build can't speak to Style/Documentation/Intent/Simplification/Coherence.
BUILD_RELEVANT_AXES = frozenset({"correctness", "tests", "design-api", "performance"})


def _load_findings(path: Path) -> list[dict]:
    """Read a JSONL file into a list of dicts. Missing → []. Bad lines → skipped."""
    if not path.exists():
        return []
    findings: list[dict] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            findings.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return findings


def _write_findings(path: Path, findings: list[dict], meta: dict) -> None:
    """Write JSONL findings + a `<path>.meta.json` sidecar with run metadata."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for finding in findings:
            fh.write(json.dumps(finding) + "\n")
    sidecar = path.with_suffix(path.suffix + ".meta.json")
    sidecar.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


def _run_build(repo: Path, test_command: str, timeout: int) -> tuple[int, str]:
    """Run the test command in `repo`. Returns (exit_code, status_label).

    status_label is one of: `ran`, `timeout`, `error`. The label feeds the
    sidecar metadata; the exit_code drives the per-finding verdict.
    """
    try:
        result = subprocess.run(
            test_command,
            shell=True,
            cwd=str(repo),
            capture_output=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return -1, "timeout"
    except OSError:
        return -2, "error"
    return result.returncode, "ran"


def make_verdict_fn(build_failed: bool):
    """Return a `builder_fn(finding) -> verdict` for `iterate_unverified`."""
    def verdict(finding: dict) -> str:
        axis = finding.get("axis", "")
        if axis not in BUILD_RELEVANT_AXES:
            return "inconclusive"
        return "confirmed" if build_failed else "inconclusive"
    return verdict


def run(
    repo: Path,
    findings: list[dict],
    test_command: str | None,
    *,
    tool_available: bool,
    timeout: int,
) -> tuple[list[dict], dict]:
    """Apply build-verification to `findings`. Returns (out_findings, meta).

    When `test_command` is None or `tool_available` is False, returns the
    input findings unchanged and records the skip reason in meta. Useful
    for orchestration tests that don't want a subprocess to fire.
    """
    threshold = synthesis_core.CONFIDENCE_THRESHOLD
    sub80 = [f for f in findings if int(f.get("confidence", 0)) < threshold]
    rest = [f for f in findings if int(f.get("confidence", 0)) >= threshold]

    if not test_command or not tool_available:
        return findings, {
            "build_status": "skipped",
            "reason": (
                "build tool unavailable on PATH"
                if test_command else "no build tool detected"
            ),
            "tool": None,
            "test_command": test_command,
            "promoted_count": 0,
            "remaining_sub80_count": len(sub80),
        }

    if not sub80:
        return findings, {
            "build_status": "skipped",
            "reason": "no sub-80 findings to verify",
            "tool": None,
            "test_command": test_command,
            "promoted_count": 0,
            "remaining_sub80_count": 0,
        }

    exit_code, status_label = _run_build(repo, test_command, timeout)
    build_failed = exit_code != 0
    iteration = synthesis_core.iterate_unverified(
        sub80, make_verdict_fn(build_failed)
    )
    promoted, remaining = iteration[0], iteration[1]
    return rest + promoted + remaining, {
        "build_status": status_label,
        "tool": None,
        "test_command": test_command,
        "exit_code": exit_code,
        "build_failed": build_failed,
        "promoted_count": len(promoted),
        "remaining_sub80_count": len(remaining),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 3.5 build verification for code-ultrareview"
    )
    parser.add_argument("--scope", required=True, help="path to scope.json")
    parser.add_argument(
        "--findings", required=True,
        help="path to axis-findings.jsonl (Phase 3 output)",
    )
    parser.add_argument(
        "--output", required=True,
        help="path to write build-verified.jsonl",
    )
    parser.add_argument("--repo", default=".", help="repo root (default: cwd)")
    parser.add_argument(
        "--timeout", type=int, default=120,
        help="test command timeout in seconds (default: 120)",
    )
    args = parser.parse_args()

    scope_path = Path(args.scope)
    findings_path = Path(args.findings)
    output_path = Path(args.output)
    repo = Path(args.repo).expanduser().resolve()

    if not scope_path.exists():
        print(f"ERROR: scope.json not found: {scope_path}", file=sys.stderr)
        return 2
    if not repo.is_dir():
        print(f"ERROR: repo path is not a directory: {repo}", file=sys.stderr)
        return 2

    findings = _load_findings(findings_path)

    # Build-tool detection is deterministic — failure to detect is a
    # graceful skip, not an error.
    detected = build_detect.detect(repo)
    tool = detected.get("tool")
    test_command = detected.get("test_command")
    tool_available = bool(detected.get("available"))

    out_findings, meta = run(
        repo, findings, test_command,
        tool_available=tool_available, timeout=args.timeout,
    )
    meta["tool"] = tool

    _write_findings(output_path, out_findings, meta)
    return 0


if __name__ == "__main__":
    sys.exit(main())
