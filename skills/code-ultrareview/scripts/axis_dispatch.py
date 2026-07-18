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
import hashlib
import json
import sys
import uuid
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from battery_ingest import TOOL_TO_AXIS  # noqa: E402
from runtime_contracts import (  # noqa: E402
    file_identity as _file_identity,
    read_required_diff as _read_text,
    read_scope as _read_json,
    verify_file_identity as _verify_file_identity,
    write_json_atomic as _write_json_atomic,
    write_jsonl_atomic as _write_jsonl_atomic,
)

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
KNOWN_AXES = frozenset(CANONICAL_AXES + CONDITIONAL_AXES)
DETERMINISTIC_TOOL_AXES = {
    **TOOL_TO_AXIS,
    "stryker": "tests",
    "mutmut": "tests",
    "pitest": "tests",
}

AXIS_BRIEFS = {
    axis: f"references/axes/{axis}.md"
    for axis in CANONICAL_AXES + CONDITIONAL_AXES
}

# Anthropic-verbatim source — every axis prompt cites it.
ANTHROPIC_VERBATIM = "references/anthropic-verbatim.md"

# Soft concurrency cap per the deep research (community-observed).
MAX_PARALLEL_AXES = 10


def parse_axes(value: str | None) -> list[str] | None:
    if value is None:
        return None
    axes = [axis.strip() for axis in value.split(",") if axis.strip()]
    if not axes:
        raise ValueError("--axes must name at least one canonical axis")
    allowed = set(CANONICAL_AXES + CONDITIONAL_AXES)
    unknown = [axis for axis in axes if axis not in allowed]
    if unknown:
        raise ValueError(f"Unknown axis: {unknown[0]}")
    if len(set(axes)) != len(axes):
        raise ValueError("--axes contains duplicate axis names")
    return axes


def decide_axes(scope: dict, selected_axes: list[str] | None = None) -> list[str]:
    """Return the list of axes to launch in Phase 3.

    Launches the 8 canonical axes by default and adds Coherence when
    `scope["activates_coherence"]` is true. An explicit subset is honored, but
    Coherence cannot be selected when metadata did not activate it. Returns a
    fresh list so callers can mutate.
    """
    if selected_axes is None:
        axes: list[str] = list(CANONICAL_AXES)
        if scope.get("activates_coherence"):
            axes.append("coherence")
    else:
        axes = list(selected_axes)
        if "coherence" in axes and not scope.get("activates_coherence"):
            raise ValueError(
                "Coherence is inactive because the diff contains no metadata"
            )
    if len(axes) > MAX_PARALLEL_AXES:
        raise ValueError(
            f"Axis count {len(axes)} exceeds parallel cap "
            f"{MAX_PARALLEL_AXES}; batch externally"
        )
    return axes


def filter_findings_by_axis(findings: list[dict], axis: str) -> list[dict]:
    """Return findings whose `axis` field equals the target axis.

    The filter is exact-match on the canonical axis key. Invalid records fail
    before filtering because silently dropping deterministic evidence would
    make the tool-coverage gate dishonest.
    """
    for finding in findings:
        _validate_tool_finding(finding)
    return [f for f in findings if f.get("axis") == axis]


def _validate_tool_finding(record: dict) -> None:
    if not isinstance(record, dict):
        raise ValueError("each tool finding must be a JSON object")
    axis = record.get("axis")
    if axis not in KNOWN_AXES:
        raise ValueError(f"tool finding carries an unknown or missing axis: {axis!r}")
    confidence = record.get("confidence")
    if isinstance(confidence, bool) or confidence != 100:
        raise ValueError("deterministic tool findings must carry confidence 100")
    severity = record.get("severity")
    if severity not in {"High", "Medium", "Low"}:
        raise ValueError(f"tool finding carries an invalid severity: {severity!r}")
    source_tool = record.get("source_tool")
    if not isinstance(source_tool, str) or not source_tool.strip():
        raise ValueError("tool finding has an invalid source_tool")
    expected_axis = DETERMINISTIC_TOOL_AXES.get(source_tool)
    if expected_axis is None:
        raise ValueError(f"tool finding carries an unknown source_tool: {source_tool!r}")
    if axis != expected_axis:
        raise ValueError(
            f"tool finding routes {source_tool!r} to {axis!r}; expected {expected_axis!r}"
        )
    if source_tool in {"stryker", "mutmut", "pitest"}:
        for field in ("location", "finding", "recommendation"):
            if not isinstance(record.get(field), str) or not record[field].strip():
                raise ValueError(f"mutation finding has an invalid {field}")
        return
    for field in ("file", "message"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            raise ValueError(f"tool finding has an invalid {field}")
    start = record.get("line_start")
    end = record.get("line_end")
    if (
        isinstance(start, bool)
        or not isinstance(start, int)
        or start < 1
        or isinstance(end, bool)
        or not isinstance(end, int)
        or end < start
    ):
        raise ValueError("tool finding has an invalid line range")


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

## Coverage, not filtering

Your job at this stage is coverage, not ranking. Report every issue you find —
including low-severity ones and ones you are not sure about — each with its
severity and an honest 0-100 confidence. Do not suppress a finding because it
looks minor or because you are uncertain: Phase 4 validators and the
80-confidence threshold rank and filter downstream, and a finding that later
gets filtered out is cheaper than a real bug silently dropped. This is not a
license for false positives — the documented taxonomy (pre-existing,
linter-territory, intentional changes) still applies; when a concern is genuine
but weak, report it at low confidence rather than dropping it.

## Inputs

- Axis brief: `{brief}`
- Anthropic verbatim: `{anthropic_verbatim}`
- Per-axis bundle: `{input_path}`
- Tool findings (pre-filtered to your axis, confidence 100): {findings_count}

## Output

Emit one JSON object per finding to stdout, one per line. Schema:

    {{
        "run_id": "{run_id}",
        "axis": "{axis}",
        "severity": "High" | "Medium" | "Low",
        "location": "<file>:<line>" | "<file>:<start>-<end>",
        "finding": "<what is wrong>",
        "recommendation": "<what to do>",
        "confidence": <0-100 int>
    }}

Sub-80 confidence findings are NOT dropped — synthesis routes them to the
"Unverified" section per the A2 contract. Emit every finding, scored honestly;
the downstream filter decides what surfaces.

When you have zero findings, emit a single line:

    {{"run_id": "{run_id}", "axis": "{axis}", "no_findings": true}}

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
    run_id: str = "direct-call",
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
        run_id=run_id,
    )


def prepare_axis_bundle(
    axis: str,
    scope: dict,
    all_findings: list[dict],
    diff_text: str,
    output_dir: Path,
    skill_dir: Path,
    reconcile_payload: dict | None = None,
    run_id: str = "direct-call",
    input_hashes: dict | None = None,
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
        "run_id": run_id,
        "input_hashes": input_hashes or {},
        "axis": axis,
        "scope": scope,
        "findings": axis_findings,
        "diff_text": diff_text,
        "brief_path": str((skill_dir / AXIS_BRIEFS[axis]).resolve()),
        "anthropic_verbatim_path": str(
            (skill_dir / ANTHROPIC_VERBATIM).resolve()
        ),
    }
    if axis == "intent" and reconcile_payload is not None:
        bundle["reconcile"] = reconcile_payload
    input_path.write_text(
        json.dumps(bundle, indent=2, sort_keys=False), encoding="utf-8"
    )

    prompt = build_axis_prompt(
        axis=axis,
        findings_count=len(axis_findings),
        skill_dir=skill_dir,
        input_path=input_path,
        run_id=run_id,
    )
    prompt_path.write_text(prompt, encoding="utf-8")

    return {
        "axis": axis,
        "input_path": str(input_path),
        "prompt_path": str(prompt_path),
        "findings_count": len(axis_findings),
        "run_id": run_id,
    }


def prepare(
    scope: dict,
    all_findings: list[dict],
    diff_text: str,
    output_dir: Path,
    skill_dir: Path,
    selected_axes: list[str] | None = None,
    reconcile_payload: dict | None = None,
    run_id: str = "direct-call",
    input_hashes: dict | None = None,
) -> dict:
    """Prepare every axis bundle Phase 3 needs.

    Returns a mapping `{axis: bundle_info}` plus a top-level `axes` list
    in deterministic order so the main-thread orchestrator can fan out
    Task calls without sorting.
    """
    axes = decide_axes(scope, selected_axes)
    bundles = {}
    for axis in axes:
        bundles[axis] = prepare_axis_bundle(
            axis=axis,
            scope=scope,
            all_findings=all_findings,
            diff_text=diff_text,
            output_dir=output_dir,
            skill_dir=skill_dir,
            reconcile_payload=reconcile_payload,
            run_id=run_id,
            input_hashes=input_hashes,
        )
    return {
        "axes": axes,
        "coherence_active": "coherence" in axes,
        "bundles": bundles,
        "run_id": run_id,
        "input_hashes": input_hashes or {},
    }


def _validate_axis_record(
    record: dict,
    expected_axis: str,
    expected_run_id: str | None = None,
) -> None:
    if not isinstance(record, dict):
        raise ValueError(f"{expected_axis}: each output line must be a JSON object")
    if record.get("axis") != expected_axis:
        raise ValueError(f"{expected_axis}: output carries the wrong axis")
    if expected_run_id is not None and record.get("run_id") != expected_run_id:
        raise ValueError(f"{expected_axis}: output run_id does not match prepare")
    if record.get("no_findings") is True:
        return
    required = ("severity", "location", "finding", "recommendation", "confidence")
    missing = [key for key in required if key not in record]
    if missing:
        raise ValueError(f"{expected_axis}: missing field {missing[0]}")
    if record["severity"] not in {"High", "Medium", "Low"}:
        raise ValueError(f"{expected_axis}: invalid severity")
    confidence = record["confidence"]
    if isinstance(confidence, bool) or not isinstance(confidence, int):
        raise ValueError(f"{expected_axis}: confidence must be an integer")
    if not 0 <= confidence <= 100:
        raise ValueError(f"{expected_axis}: confidence must be between 0 and 100")
    for field in ("location", "finding", "recommendation"):
        if not isinstance(record[field], str) or not record[field].strip():
            raise ValueError(f"{expected_axis}: {field} must be non-empty")


def ingest_axis_results(
    scope: dict,
    results_dir: Path,
    selected_axes: list[str] | None = None,
) -> tuple[list[dict], dict]:
    """Validate one result file per requested axis and build coverage state."""
    prepared_axes = (scope.get("axis_coverage") or {}).get("requested")
    run_id = (scope.get("axis_coverage") or {}).get("run_id")
    if prepared_axes is not None:
        if not isinstance(prepared_axes, list) or not all(
            isinstance(axis, str) for axis in prepared_axes
        ):
            raise ValueError("prepared axis manifest is invalid")
        if selected_axes is None:
            selected_axes = list(prepared_axes)
        elif selected_axes != prepared_axes:
            raise ValueError(
                "ingest axes do not match the axes prepared for dispatch: "
                f"prepared={prepared_axes}, ingest={selected_axes}"
            )
    axes = decide_axes(scope, selected_axes)
    merged: list[dict] = []
    completed: list[str] = []
    for axis in axes:
        path = results_dir / f"{axis}.jsonl"
        if not path.is_file():
            raise ValueError(f"{axis}: missing result file {path}")
        records: list[dict] = []
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), 1
        ):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"{axis}: malformed JSON on line {line_number}"
                ) from exc
            _validate_axis_record(
                record,
                axis,
                run_id if isinstance(run_id, str) else None,
            )
            records.append(record)
        if not records:
            raise ValueError(f"{axis}: result file is empty")
        no_findings = [record for record in records if record.get("no_findings") is True]
        if no_findings and (len(records) != 1 or len(no_findings) != 1):
            raise ValueError(
                f"{axis}: no_findings marker cannot be mixed with findings"
            )
        if not no_findings:
            merged.extend(records)
        completed.append(axis)

    full_axes = decide_axes(scope)
    explicit_scope = bool(
        (scope.get("axis_coverage") or {}).get("explicit_scope")
    )
    coverage = {
        "complete": True,
        "full": axes == full_axes and not explicit_scope,
        "explicit_scope": explicit_scope,
        "requested": axes,
        "completed": completed,
        "run_id": run_id,
        "input_hashes": (scope.get("axis_coverage") or {}).get("input_hashes"),
    }
    return merged, coverage


def _read_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        raise ValueError(f"required tool findings file is missing: {path}")
    out: list[dict] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"invalid tool finding JSON at {path}:{line_number}: {exc}"
            ) from exc
        if not isinstance(record, dict):
            raise ValueError(
                f"tool finding at {path}:{line_number} is not an object"
            )
        try:
            _validate_tool_finding(record)
        except ValueError as exc:
            raise ValueError(
                f"invalid tool finding at {path}:{line_number}: {exc}"
            ) from exc
        out.append(record)
    return out


def _read_reconcile_payload(scope: dict) -> dict | None:
    coverage = scope.get("reconcile_coverage")
    if coverage is None:
        return None
    if not isinstance(coverage, dict) or coverage.get("complete") is not True:
        raise ValueError(
            "requested reconcile coverage is incomplete; repair the source "
            "and rerun Code Ultrareview with the same --reconcile value"
        )
    output = coverage.get("output")
    expected_digest = coverage.get("sha256")
    expected_count = coverage.get("finding_count")
    if not isinstance(output, str) or not output:
        raise ValueError("reconcile coverage has no result path")
    if not isinstance(expected_digest, str) or len(expected_digest) != 64:
        raise ValueError("reconcile coverage has no valid result digest")
    path = Path(output)
    if not path.is_absolute() or not path.is_file():
        raise ValueError(f"reconcile result is missing: {path}")
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected_digest:
        raise ValueError(f"reconcile result digest mismatch: {path}")
    payload = json.loads(data)
    if not isinstance(payload, dict) or payload.get("lens") != "derivation":
        raise ValueError("reconcile result is not a derivation payload")
    artifacts = payload.get("artifacts")
    findings = payload.get("findings")
    if not isinstance(artifacts, list) or not isinstance(findings, list):
        raise ValueError("reconcile result has an invalid schema")
    if isinstance(expected_count, bool) or not isinstance(expected_count, int):
        raise ValueError("reconcile coverage has an invalid finding count")
    if len(findings) != expected_count:
        raise ValueError("reconcile result finding count does not match coverage")
    for finding in findings:
        if (
            not isinstance(finding, dict)
            or finding.get("classification") != "UNCLASSIFIED"
            or not isinstance(finding.get("finding"), str)
            or not finding["finding"].strip()
        ):
            raise ValueError("reconcile result contains an invalid finding")
    return payload


def _read_mutation_findings(scope: dict) -> tuple[list[dict], dict | None]:
    coverage = scope.get("mutation_coverage")
    if coverage is None:
        return [], None
    if not isinstance(coverage, dict):
        raise ValueError("mutation coverage manifest is invalid")
    if coverage.get("applicable") is False:
        return [], None
    if coverage.get("complete") is not True:
        raise ValueError(
            "requested mutation coverage is incomplete; repair the mutation "
            "run and rerun Code Ultrareview"
        )
    identity = {
        "path": coverage.get("output"),
        "sha256": coverage.get("sha256"),
    }
    path = _verify_file_identity(identity, "mutation findings")
    findings = _read_jsonl(path)
    expected_count = coverage.get("finding_count")
    if isinstance(expected_count, bool) or not isinstance(expected_count, int):
        raise ValueError("mutation coverage finding count is invalid")
    if len(findings) != expected_count:
        raise ValueError("mutation findings count does not match coverage")
    return findings, _file_identity(path)


def _verify_axis_inputs(scope: dict) -> None:
    coverage = scope.get("axis_coverage")
    if not isinstance(coverage, dict):
        raise ValueError("axis coverage manifest is missing")
    run_id = coverage.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        raise ValueError("axis run_id is missing; rerun axis preparation")
    identities = coverage.get("input_hashes")
    if not isinstance(identities, dict):
        raise ValueError("axis input manifest is missing; rerun axis preparation")
    for key in ("diff", "tool_findings"):
        _verify_file_identity(identities.get(key), key.replace("_", " "))
    mutation = identities.get("mutation_findings")
    if mutation is not None:
        _verify_file_identity(mutation, "mutation findings")


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
    prep.add_argument(
        "--axes", default=None,
        help="Comma-separated canonical axis subset (scoped report only)",
    )

    ing = sub.add_parser(
        "ingest",
        help="Validate one JSONL result per requested axis and merge findings",
    )
    ing.add_argument("--scope", required=True, help="Path to scope.json")
    ing.add_argument(
        "--results-dir", required=True,
        help="Directory containing <axis>.jsonl result files",
    )
    ing.add_argument("--output", required=True, help="Merged axis findings JSONL")
    ing.add_argument(
        "--axes", default=None,
        help="Comma-separated canonical axis subset (must match prepare)",
    )

    args = parser.parse_args()

    if args.cmd == "prepare":
        scope_path = Path(args.scope)
        findings_path = Path(args.findings)
        diff_path = Path(args.diff)
        if not scope_path.is_file():
            print(f"ERROR: scope.json not found: {scope_path}", file=sys.stderr)
            return 2

        try:
            scope = _read_json(scope_path)
            selected_axes = parse_axes(args.axes)
            requested_axes = selected_axes or decide_axes(scope)
            scope["axis_coverage"] = {
                "complete": False,
                "full": args.axes is None,
                "explicit_scope": args.axes is not None,
                "requested": requested_axes,
                "completed": [],
            }
            scope["validator_coverage"] = {
                "complete": False,
                "expected": 0,
                "completed": 0,
            }
            scope["coverage_complete"] = False
            _write_json_atomic(scope_path, scope)
            tool_coverage = scope.get("tool_coverage")
            if not isinstance(tool_coverage, dict):
                raise ValueError(
                    "deterministic analyzer coverage manifest is missing; "
                    "rerun the battery"
                )
            if tool_coverage.get("complete") is not True:
                raise ValueError(
                    "deterministic analyzer coverage is incomplete; "
                    "repair the battery and rerun Code Ultrareview"
                )
            if scope.get("tools_missing") or scope.get("tools_skipped"):
                raise ValueError(
                    "deterministic analyzers are missing or skipped; "
                    "repair them and rerun Code Ultrareview"
                )
            battery_axes = tool_coverage.get("selected_axes") or []
            if not isinstance(battery_axes, list) or not all(
                isinstance(axis, str) for axis in battery_axes
            ):
                raise ValueError(
                    "deterministic analyzer selected_axes manifest is invalid"
                )
            battery_scoped = bool(tool_coverage.get("explicit_scope") or battery_axes)
            if battery_scoped and selected_axes is None:
                raise ValueError(
                    "the deterministic battery was axis-scoped; rerun axis "
                    "preparation with the same --axes value"
                )
            if battery_scoped and selected_axes != battery_axes:
                raise ValueError(
                    "axis selection does not match the scoped deterministic "
                    f"battery: battery={battery_axes}, axes={selected_axes}"
                )
            reconcile_payload = _read_reconcile_payload(scope)
            findings = _read_jsonl(findings_path)
            mutation_findings, mutation_identity = _read_mutation_findings(scope)
            findings.extend(mutation_findings)
            diff_text = _read_text(diff_path)
            input_hashes = {
                "diff": _file_identity(diff_path),
                "tool_findings": _file_identity(findings_path),
                "mutation_findings": mutation_identity,
            }
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"ERROR: tool coverage incomplete: {exc}", file=sys.stderr)
            return 4
        output_dir = Path(args.output_dir).resolve()
        skill_dir = (
            Path(args.skill_dir).resolve()
            if args.skill_dir else _default_skill_dir()
        )

        run_id = uuid.uuid4().hex
        try:
            result = prepare(
                scope=scope,
                all_findings=findings,
                diff_text=diff_text,
                output_dir=output_dir,
                skill_dir=skill_dir,
                selected_axes=selected_axes,
                reconcile_payload=reconcile_payload,
                run_id=run_id,
                input_hashes=input_hashes,
            )
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2

        scope["axis_coverage"] = {
            "complete": False,
            "full": args.axes is None and result["axes"] == decide_axes(scope),
            "explicit_scope": args.axes is not None or battery_scoped,
            "requested": result["axes"],
            "completed": [],
            "status": "prepared",
            "run_id": run_id,
            "input_hashes": input_hashes,
        }
        scope["validator_coverage"] = {
            "complete": False,
            "expected": 0,
            "completed": 0,
        }
        scope["coverage_complete"] = False
        _write_json_atomic(scope_path, scope)
        sys.stdout.write(json.dumps(result, indent=2, sort_keys=False) + "\n")
        return 0

    if args.cmd == "ingest":
        scope_path = Path(args.scope)
        results_dir = Path(args.results_dir)
        output_path = Path(args.output)
        if not scope_path.is_file() or not results_dir.is_dir():
            print("ERROR: scope or axis result directory is missing", file=sys.stderr)
            return 2
        try:
            scope = _read_json(scope_path)
            previous = scope.get("axis_coverage")
            if not isinstance(previous, dict):
                raise ValueError(
                    "axis coverage manifest is missing; rerun axis preparation"
                )
            scope["axis_coverage"] = {
                "complete": False,
                "full": bool(previous.get("full")),
                "explicit_scope": bool(previous.get("explicit_scope")),
                "requested": list(previous.get("requested") or []),
                "completed": [],
                "status": "ingesting",
                "run_id": previous.get("run_id"),
                "input_hashes": previous.get("input_hashes"),
            }
            scope["validator_coverage"] = {
                "complete": False,
                "expected": 0,
                "completed": 0,
            }
            scope["coverage_complete"] = False
            _write_json_atomic(scope_path, scope)
            if output_path.exists():
                output_path.unlink()
            _verify_axis_inputs(scope)
            selected_axes = parse_axes(args.axes)
            findings, coverage = ingest_axis_results(
                scope, results_dir, selected_axes
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"ERROR: axis coverage incomplete: {exc}", file=sys.stderr)
            return 4

        _write_jsonl_atomic(output_path, findings)
        output_identity = _file_identity(output_path)
        sub_threshold = sum(
            1 for finding in findings if int(finding.get("confidence", 0)) < 80
        )
        coverage["status"] = "complete"
        coverage["output"] = str(output_path.resolve())
        coverage["sha256"] = output_identity["sha256"]
        coverage["finding_count"] = len(findings)
        scope["axis_coverage"] = coverage
        scope["validator_coverage"] = {
            "complete": sub_threshold == 0,
            "expected": sub_threshold,
            "completed": 0,
        }
        scope["coverage_complete"] = bool(
            (scope.get("tool_coverage") or {}).get("complete")
            and coverage["complete"]
            and sub_threshold == 0
            and (
                scope.get("mutation_coverage") is None
                or (scope.get("mutation_coverage") or {}).get("complete")
            )
            and (
                scope.get("reconcile_coverage") is None
                or (scope.get("reconcile_coverage") or {}).get("complete")
            )
        )
        _write_json_atomic(scope_path, scope)
        print(json.dumps({"axes": coverage, "findings": len(findings)}))
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
