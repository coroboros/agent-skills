#!/usr/bin/env python3
"""Tier-0 distillation gate — the existing suite is the capital's ablation harness.

Blueprint §6: no file moves until tier 0 is green. Every rule the award-design
corpus carries is already pinned by a test, so any distillation — a reference
move, a heading merge, a 45-line cut — shows up here as a test that stopped
passing. That is the measurement: the suite tells you exactly which capital a
proposed cut destroys, at $0 and before a single token of eval spend.

The gate is differential, not absolute. It compares the current failure set
against `ablation_baseline.json`; only failures the baseline does not carry are
regressions. A deletion that is *adjudicated* — the content is genuinely dead
and the test goes with it, carrying its adjudication note — is recorded by
re-running with `--update-baseline`, which makes the removal a deliberate,
reviewable act instead of a silent one.

Usage:
    python3 ablation_gate.py [--update-baseline]

Exit codes: 0 = no new failures, 1 = new failures or a broken run.
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
TEST_DIR = "tests/award-design"
BASELINE_PATH = HERE / "ablation_baseline.json"

# unittest writes `FAIL: test_x (module.Class.test_x)` — the parenthetical is the
# full dotted id on 3.11+, and a bare `module.Class` on older runtimes.
RESULT_RE = re.compile(r"^(FAIL|ERROR): (\S+) \(([^)]+)\)", re.MULTILINE)

REGRESSION_MESSAGE = (
    "capital regression — adjudicate each: restore the content or delete the test "
    "WITH its adjudication note")


def run_suite():
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", TEST_DIR],
        cwd=REPO_ROOT, capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def parse_failures(output):
    failing = set()
    for _, name, qualifier in RESULT_RE.findall(output):
        failing.add(qualifier if qualifier.endswith(f".{name}") else f"{qualifier}.{name}")
    return failing


def load_baseline():
    if not BASELINE_PATH.is_file():
        return None
    return set(json.loads(BASELINE_PATH.read_text(encoding="utf-8"))["failing"])


def write_baseline(failing):
    BASELINE_PATH.write_text(
        json.dumps({"generated": date.today().isoformat(), "failing": sorted(failing)}, indent=2)
        + "\n", encoding="utf-8")


def group_by_class(test_ids):
    grouped = {}
    for test_id in sorted(test_ids):
        grouped.setdefault(test_id.rsplit(".", 1)[0], []).append(test_id)
    return grouped


def format_report(new_failures, fixed):
    lines = [REGRESSION_MESSAGE, ""]
    for test_class, test_ids in group_by_class(new_failures).items():
        lines.append(f"{test_class} — {len(test_ids)} new failure(s)")
        lines.extend(f"  {test_id.rsplit('.', 1)[1]}" for test_id in test_ids)
        lines.append("")
    if fixed:
        lines.append(f"{len(fixed)} baseline failure(s) now pass — "
                     "re-run with --update-baseline once adjudicated.")
    return "\n".join(lines).rstrip()


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="award-design tier-0 ablation gate — differential test-failure check")
    parser.add_argument("--update-baseline", action="store_true",
                        help="rewrite the baseline from this run (adjudicated deletions only)")
    args = parser.parse_args(argv)

    returncode, output = run_suite()
    failing = parse_failures(output)
    # A run that died before reporting (import crash, wrong cwd, missing runtime)
    # returns non-zero with nothing parsed — that is a broken gate, never a pass.
    if returncode != 0 and not failing:
        print("ablation gate could not read a result from the suite — the run itself is broken:",
              file=sys.stderr)
        print("\n".join(output.strip().splitlines()[-20:]), file=sys.stderr)
        return 1

    if args.update_baseline:
        write_baseline(failing)
        print(f"baseline rewritten: {len(failing)} failing test(s) recorded in "
              f"{BASELINE_PATH.name}")
        return 0

    baseline = load_baseline()
    if baseline is None:
        print(f"no baseline at {BASELINE_PATH.name} — generate it from a known-good tree "
              "with --update-baseline", file=sys.stderr)
        return 1

    new_failures = failing - baseline
    fixed = baseline - failing
    if new_failures:
        print(format_report(new_failures, fixed))
        return 1

    note = f" ({len(fixed)} baseline failure(s) now pass)" if fixed else ""
    print(f"tier 0 green — {len(failing)} failing test(s), none new against the baseline{note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
