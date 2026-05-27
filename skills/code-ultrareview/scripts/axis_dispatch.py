#!/usr/bin/env python3
"""Phase 3 axis-dispatch orchestrator for code-ultrareview.

The main thread launches the axis subagents — subagents cannot spawn other
subagents (Anthropic's documented contract: `Agent` tool is reserved for
the main thread). This module is the deterministic half:

1. Decide which axes to launch (8 always-on + Coherence when active).
2. Filter `tool-findings.jsonl` per axis using the canonical axis keys.
3. Build the per-axis subagent prompt — citing `anthropic-verbatim.md`
   rubric and false-positive list verbatim.
4. Write per-axis input bundles to disk so the subagent can `Read` them.

The prompt template is uniform across axes — only the `{axis}`, `{brief}`,
and `{findings}` placeholders change. This guarantees every subagent gets
the same rubric, the same false-positive contract, and the same output
schema, regardless of axis.

Canonical schemas:

    scope.json                     # produced by scripts/scope.py
    tool-findings.jsonl            # produced by scripts/battery_ingest.py
    axis-input/{axis}.json         # {scope, findings, brief_path, diff_text}
    axis-prompt/{axis}.txt         # full subagent prompt blob

CLI:
    python3 axis_dispatch.py prepare \\
        --scope scope.json \\
        --findings tool-findings.jsonl \\
        --diff diff.patch \\
        --output-dir <dir>

Stdout: one JSON object mapping `{axis: {input_path, prompt_path}}` that
the main-thread orchestrator reads to fan out the Task calls in parallel.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Canonical axis keys — mirror `synthesis_core.py:CANONICAL_AXES` so a
# rename in one place fails loudly here on the test pass.
CANONICAL_AXES = (
    "correctness",
    "simplification",
    "tests",
    "documentation",
    "style",
    "intent",
    "design-api",
    "performance",
)

CONDITIONAL_AXES = ("coherence",)

# Per-axis brief file under `references/axes/`.
AXIS_BRIEFS = {
    axis: f"references/axes/{axis}.md"
    for axis in CANONICAL_AXES + CONDITIONAL_AXES
}

# Anthropic-verbatim source — every axis prompt cites it.
ANTHROPIC_VERBATIM = "references/anthropic-verbatim.md"

# Soft concurrency cap per the deep research (community-observed).
MAX_PARALLEL_AXES = 10


# ---------------------------------------------------------------------------
# Axis selection
# ---------------------------------------------------------------------------


def decide_axes(scope: dict) -> list[str]:
    """Return the list of axes to launch in Phase 3.

    Always launches the 8 canonical axes. Adds Coherence when
    `scope["activates_coherence"]` is true. Returns a fresh list (not a
    tuple) so callers can mutate.
    """
    axes: list[str] = list(CANONICAL_AXES)
    if scope.get("activates_coherence"):
        axes.append("coherence")
    if len(axes) > MAX_PARALLEL_AXES:
        raise ValueError(
            f"Axis count {len(axes)} exceeds parallel cap "
            f"{MAX_PARALLEL_AXES}; batch externally"
        )
    return axes


# ---------------------------------------------------------------------------
# Tool-finding filter
# ---------------------------------------------------------------------------


def filter_findings_by_axis(findings: list[dict], axis: str) -> list[dict]:
    """Return findings whose `axis` field equals the target axis.

    The filter is exact-match on the canonical axis key. Findings without
    an `axis` field are silently skipped — battery_ingest always sets it,
    so an unset field signals an upstream bug worth ignoring here.
    """
    return [f for f in findings if f.get("axis") == axis]


# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------


PROMPT_TEMPLATE = """\
# Axis review: {axis}

You are the **{axis}** axis reviewer for code-ultrareview Phase 3. Read
the inputs below, apply your axis brief, and emit findings as JSONL on
stdout.

## Your contract

- Read `{anthropic_verbatim}` and apply the 0-100 confidence rubric VERBATIM.
- Read `{anthropic_verbatim}` and silence false positives per the documented taxonomy.
- Read `{brief}` (your axis brief) for scope, severity calibration, and
  repo-kind branches.
- Read `{input_path}` for: `scope` (repo kind, languages, CLAUDE.md chain),
  `findings` (deterministic tool findings filtered to your axis only),
  and `diff_text` (the diff itself).
- Score each finding 0-100 against the verbatim rubric.
- Do NOT check build signal or attempt to build / typecheck. CI does that
  separately (per the verbatim agent-assumption rule).
- Do NOT flag pre-existing issues on lines the diff did not touch.
- Do NOT flag concerns from other axes — stay in your lane.

## Inputs

- Axis brief: `{brief}`
- Anthropic verbatim: `{anthropic_verbatim}`
- Per-axis bundle: `{input_path}`
- Tool findings (pre-filtered to your axis, confidence 100): {findings_count}

## Output

Emit one JSON object per finding to stdout, one per line. Schema:

    {{
        "axis": "{axis}",
        "severity": "High" | "Medium" | "Low",
        "location": "<file>:<line>" | "<file>:<start>-<end>",
        "finding": "<what is wrong>",
        "recommendation": "<what to do>",
        "confidence": <0-100 int>
    }}

Sub-80 confidence findings are NOT dropped — synthesis routes them to the
"Unverified" section per the A2 contract. Emit every finding you judge
worth surfacing, with an honest confidence score.

When you have zero findings, emit a single line:

    {{"axis": "{axis}", "no_findings": true}}

## Stay read-only

Use `Read`, `Grep`, `Glob`, and `Bash` (for `git`, `gh`, and per-axis
orchestrator scripts only). Do NOT use `Write`, `Edit`, or any
file-mutating tool. The synthesis phase owns report emission.
"""


def build_axis_prompt(
    axis: str,
    findings_count: int,
    skill_dir: Path,
    input_path: Path,
) -> str:
    """Build the subagent prompt for a given axis.

    `skill_dir` is the absolute path to the code-ultrareview skill root
    (e.g. `~/.claude/skills/code-ultrareview/` on install, or the repo
    path during development) so the prompt's reference paths are
    unambiguous to the subagent. `input_path` is the absolute path to
    the per-axis JSON bundle the subagent will `Read`.
    """
    if axis not in AXIS_BRIEFS:
        raise ValueError(f"Unknown axis: {axis}")
    return PROMPT_TEMPLATE.format(
        axis=axis,
        brief=str(skill_dir / AXIS_BRIEFS[axis]),
        anthropic_verbatim=str(skill_dir / ANTHROPIC_VERBATIM),
        input_path=str(input_path),
        findings_count=findings_count,
    )


# ---------------------------------------------------------------------------
# Per-axis bundle preparation
# ---------------------------------------------------------------------------


def prepare_axis_bundle(
    axis: str,
    scope: dict,
    all_findings: list[dict],
    diff_text: str,
    output_dir: Path,
    skill_dir: Path,
) -> dict:
    """Write per-axis input + prompt files; return their absolute paths.

    Bundles are written under `output_dir/axis-input/{axis}.json` and
    `output_dir/axis-prompt/{axis}.txt`. Returns:

        {
            "axis": "<axis>",
            "input_path": "<absolute path>",
            "prompt_path": "<absolute path>",
            "findings_count": <int>,
        }
    """
    axis_findings = filter_findings_by_axis(all_findings, axis)

    input_dir = output_dir / "axis-input"
    prompt_dir = output_dir / "axis-prompt"
    input_dir.mkdir(parents=True, exist_ok=True)
    prompt_dir.mkdir(parents=True, exist_ok=True)

    input_path = (input_dir / f"{axis}.json").resolve()
    prompt_path = (prompt_dir / f"{axis}.txt").resolve()

    bundle = {
        "axis": axis,
        "scope": scope,
        "findings": axis_findings,
        "diff_text": diff_text,
        "brief_path": str((skill_dir / AXIS_BRIEFS[axis]).resolve()),
        "anthropic_verbatim_path": str(
            (skill_dir / ANTHROPIC_VERBATIM).resolve()
        ),
    }
    input_path.write_text(
        json.dumps(bundle, indent=2, sort_keys=False), encoding="utf-8"
    )

    prompt = build_axis_prompt(
        axis=axis,
        findings_count=len(axis_findings),
        skill_dir=skill_dir,
        input_path=input_path,
    )
    prompt_path.write_text(prompt, encoding="utf-8")

    return {
        "axis": axis,
        "input_path": str(input_path),
        "prompt_path": str(prompt_path),
        "findings_count": len(axis_findings),
    }


def prepare(
    scope: dict,
    all_findings: list[dict],
    diff_text: str,
    output_dir: Path,
    skill_dir: Path,
) -> dict:
    """Prepare every axis bundle Phase 3 needs.

    Returns a mapping `{axis: bundle_info}` plus a top-level `axes` list
    in deterministic order so the main-thread orchestrator can fan out
    Task calls without sorting.
    """
    axes = decide_axes(scope)
    bundles = {}
    for axis in axes:
        bundles[axis] = prepare_axis_bundle(
            axis=axis,
            scope=scope,
            all_findings=all_findings,
            diff_text=diff_text,
            output_dir=output_dir,
            skill_dir=skill_dir,
        )
    return {
        "axes": axes,
        "coherence_active": "coherence" in axes,
        "bundles": bundles,
    }


# ---------------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------------


def _read_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def _default_skill_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Axis-dispatch orchestrator for code-ultrareview Phase 3"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    prep = sub.add_parser(
        "prepare",
        help="Prepare per-axis input bundles + prompts for parallel launch",
    )
    prep.add_argument("--scope", required=True, help="Path to scope.json")
    prep.add_argument(
        "--findings", required=True, help="Path to tool-findings.jsonl"
    )
    prep.add_argument(
        "--diff", required=True, help="Path to the diff text file"
    )
    prep.add_argument(
        "--output-dir", required=True,
        help="Output directory for axis-input/ and axis-prompt/ subdirs",
    )
    prep.add_argument(
        "--skill-dir", default=None,
        help="Override the skill root (default: auto-detect from script path)",
    )

    args = parser.parse_args()

    if args.cmd == "prepare":
        scope_path = Path(args.scope)
        findings_path = Path(args.findings)
        diff_path = Path(args.diff)
        if not scope_path.is_file():
            print(f"ERROR: scope.json not found: {scope_path}", file=sys.stderr)
            return 2

        scope = _read_json(scope_path)
        findings = _read_jsonl(findings_path)
        diff_text = _read_text(diff_path)
        output_dir = Path(args.output_dir).resolve()
        skill_dir = (
            Path(args.skill_dir).resolve()
            if args.skill_dir else _default_skill_dir()
        )

        try:
            result = prepare(
                scope=scope,
                all_findings=findings,
                diff_text=diff_text,
                output_dir=output_dir,
                skill_dir=skill_dir,
            )
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2

        sys.stdout.write(json.dumps(result, indent=2, sort_keys=False) + "\n")
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
