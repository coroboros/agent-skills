#!/usr/bin/env python3
"""Phase 4 fresh-context-validator orchestrator for code-ultrareview.

The main thread launches one fresh-context validator per still-sub-80 finding
from Phase 3, batched at ten parallel — subagents cannot spawn other
subagents (Anthropic's documented contract: `Agent` tool is reserved
for the main thread). This module is the deterministic half:

1. Filter the sub-80 finding set from Phase 3 — confidence-100 tool
   findings skip validation entirely.
2. Locate the deepest matching project-instruction snippet from the chain so the
   validator can re-check whether the cited rule actually exists.
3. Build the per-finding validator prompt — citing
   `references/anthropic-verbatim.md` rubric VERBATIM, plus the
   project-instruction re-check requirement.
4. Write per-finding input bundles to disk so the main-thread orchestrator
   can `Read` them and fan out `Task` calls in batches of ten.

After the main thread collects validator stdout, `ingest` parses scores
and reasons, then applies the A2 promote/demote routing on top of
`synthesis_core` primitives — no sub-80 finding silently dropped.

Canonical schemas:

    axis-findings.jsonl            # produced by Phase 3 axis subagents
    validator-input/{NNNN}.json    # {finding, diff_context, instruction_*, paths}
    validator-prompt/{NNNN}.txt    # full validator prompt blob
    validated-findings.jsonl       # produced by ingest

CLI:
    python3 run_validators.py prepare \\
        --scope scope.json \\
        --findings axis-findings.jsonl \\
        --diff diff.patch \\
        --output-dir <dir>

    python3 run_validators.py ingest \\
        --findings axis-findings.jsonl \\
        --results validator-results.jsonl \\
        --output validated-findings.jsonl
"""

from __future__ import annotations

import argparse
import ast
import fnmatch
import importlib.util
import json
import re
import sys
import uuid
from pathlib import Path
from typing import TypeVar

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from runtime_contracts import (  # noqa: E402
    file_identity as _file_identity,
    read_required_diff as _read_text,
    read_scope as _read_json,
    verify_file_identity as _verify_file_identity,
    write_json_atomic as _write_json_atomic,
    write_jsonl_atomic as _write_jsonl_atomic,
)

# Reuse synthesis_core primitives — single source of truth for the
# 80 threshold, the [unverified] prefix, and the severity restoration
# semantics. A divergence here breaks the A2 contract; tests enforce it.
_SYNTH_PATH = _SCRIPT_DIR / "synthesis_core.py"
_spec = importlib.util.spec_from_file_location("synthesis_core", _SYNTH_PATH)
assert _spec is not None and _spec.loader is not None
synthesis_core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(synthesis_core)

CONFIDENCE_THRESHOLD = synthesis_core.CONFIDENCE_THRESHOLD
PROMOTION_CAP = synthesis_core.PROMOTION_CAP
UNVERIFIED_PREFIX = synthesis_core.UNVERIFIED_PREFIX

# Soft concurrency cap — Anthropic's `code-review` plugin batches one
# Fresh-context validator per finding at ten parallel; Anthropic's Haiku
# implementation and the deep research echo the same community-observed limit.
MAX_BATCH_SIZE = 10

# Anthropic-verbatim source — every validator prompt cites it.
ANTHROPIC_VERBATIM = "references/anthropic-verbatim.md"

# Diff context window — number of diff lines stored alongside each
# finding so the validator can verify the citation without re-reading
# the entire diff. Mirrors Anthropic's plugin context budget.
DIFF_CONTEXT_LINES = 40

# Parsers for validator stdout — `score: <int>` and `reason: <text>`.
# The validator prompt requires both keys on separate lines.
_SCORE_RE = re.compile(r"^\s*score\s*:\s*(\d+)\s*$", re.IGNORECASE | re.MULTILINE)
_REASON_RE = re.compile(r"^\s*reason\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
_RUN_ID_RE = re.compile(r"^\s*run-id\s*:\s*([a-f0-9]+)\s*$", re.IGNORECASE | re.MULTILINE)


def filter_sub_threshold(findings: list[dict]) -> list[dict]:
    """Return findings with confidence in `[0, CONFIDENCE_THRESHOLD)`.

    Excludes:
    - confidence-100 findings — deterministic tool battery output;
      validators never see them.
    - confidence ≥ threshold — already verified; no validator pass.

    Confidence zero is still a claim emitted by an axis reviewer. Validation,
    not a sentinel convention, decides whether it is refuted or surfaced.
    """
    out: list[dict] = []
    for f in findings:
        conf = int(f.get("confidence", 0))
        if 0 <= conf < CONFIDENCE_THRESHOLD:
            out.append(f)
    return out


_T = TypeVar("_T")


def batch(items: list[_T], size: int = MAX_BATCH_SIZE) -> list[list[_T]]:
    """Split an item list into contiguous batches of at most `size`.

    Example: 25 sub-80 findings → 3 batches (10 + 10 + 5). Generic so
    `prepare` can batch indices while tests can batch finding dicts.
    """
    if size <= 0:
        raise ValueError(f"batch size must be positive, got {size}")
    return [items[i:i + size] for i in range(0, len(items), size)]


def _frontmatter_paths(body: str) -> list[str] | None:
    """Return a rule's `paths` patterns, or None when it is unscoped."""
    lines = body.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return None

    frontmatter = lines[1:end]
    for index, line in enumerate(frontmatter):
        if not re.match(r"^paths\s*:", line):
            continue
        value = line.split(":", 1)[1].strip()
        raw_patterns: list[str] = []
        if value:
            if value.startswith("[") and value.endswith("]"):
                try:
                    parsed = json.loads(value)
                except json.JSONDecodeError:
                    try:
                        parsed = ast.literal_eval(value)
                    except (SyntaxError, ValueError):
                        parsed = None
                if isinstance(parsed, list) and all(
                    isinstance(item, str) for item in parsed
                ):
                    raw_patterns.extend(parsed)
                else:
                    raw_patterns.extend(value[1:-1].split(","))
            else:
                raw_patterns.append(value)
        else:
            for nested in frontmatter[index + 1:]:
                if nested and not nested[0].isspace():
                    break
                match = re.match(r"^\s*-\s*(.+?)\s*$", nested)
                if match:
                    raw_patterns.append(match.group(1))
        return [
            pattern.strip().strip("'\"")
            for pattern in raw_patterns
            if pattern.strip().strip("'\"")
        ]
    return None


def _expand_braces(pattern: str) -> list[str]:
    """Expand simple comma-separated glob braces recursively."""
    match = re.search(r"\{([^{}]+)\}", pattern)
    if not match:
        return [pattern]
    expanded: list[str] = []
    for choice in match.group(1).split(","):
        replacement = pattern[:match.start()] + choice + pattern[match.end():]
        expanded.extend(_expand_braces(replacement))
    return expanded


def _glob_matches(pattern: str, finding_path: str) -> bool:
    """Match slash-aware globs with `**` and simple brace expansion."""
    normalized_path = finding_path.removeprefix("./").strip("/")

    def match_parts(pattern_parts: list[str], path_parts: list[str]) -> bool:
        if not pattern_parts:
            return not path_parts
        head = pattern_parts[0]
        if head == "**":
            return match_parts(pattern_parts[1:], path_parts) or (
                bool(path_parts) and match_parts(pattern_parts, path_parts[1:])
            )
        return bool(path_parts) and fnmatch.fnmatchcase(path_parts[0], head) and match_parts(
            pattern_parts[1:], path_parts[1:]
        )

    for expanded in _expand_braces(pattern.removeprefix("./").strip("/")):
        if match_parts(expanded.split("/"), normalized_path.split("/")):
            return True
    return False


def _instruction_applies(path_str: str, location: str, body: str) -> bool:
    """Return whether an instruction file can govern the finding."""
    path = Path(path_str)
    finding_path = "" if location == "(repo)" else location.split(":", 1)[0]
    if not path.is_absolute() and finding_path:
        parts = path.parts
        scope_parts = parts[:-1]
        for marker in (".agents", ".claude"):
            if marker in parts:
                scope_parts = parts[:parts.index(marker)]
                break
        scope = "/".join(scope_parts)
        if scope and finding_path != scope and not finding_path.startswith(f"{scope}/"):
            return False

    patterns = _frontmatter_paths(body)
    if patterns is None:
        return True
    return bool(finding_path) and any(
        _glob_matches(pattern, finding_path) for pattern in patterns
    )


def find_instruction_snippet(
    rule_text: str,
    instruction_chain: list[str],
    repo_dir: Path,
    location: str = "",
) -> tuple[str | None, str | None]:
    """Return `(path, snippet)` for the deepest instruction file whose body
    contains `rule_text`, case-insensitive substring match.

    The chain is ordered root-to-deepest; deepest match wins so nested
    overrides surface correctly. `(None, None)` when the rule text is
    absent from every file in the chain or the chain is empty.

    The snippet returned is the first matching paragraph (≤ 600 chars)
    centered on the match, giving the validator enough context to
    confirm the citation without flooding its prompt.
    """
    if not rule_text:
        return (None, None)
    needle = rule_text.strip().lower()
    if not needle:
        return (None, None)
    best: tuple[str | None, str | None] = (None, None)
    for path_str in instruction_chain:
        path = Path(path_str)
        if not path.is_absolute():
            path = repo_dir / path
        if not path.is_file():
            continue
        try:
            body = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if not _instruction_applies(path_str, location, body):
            continue
        lower = body.lower()
        idx = lower.find(needle)
        if idx == -1:
            continue
        start = max(0, idx - 200)
        end = min(len(body), idx + len(needle) + 400)
        snippet = body[start:end].strip()
        best = (path_str, snippet)
    return best


def find_claude_md_snippet(
    rule_text: str,
    claude_md_chain: list[str],
    repo_dir: Path,
) -> tuple[str | None, str | None]:
    """Compatibility alias for callers using the historical function name."""
    return find_instruction_snippet(rule_text, claude_md_chain, repo_dir)


def extract_diff_context(diff_text: str, location: str) -> str:
    """Return up to `DIFF_CONTEXT_LINES` of diff text near `location`.

    `location` is `<file>:<line>` or `<file>:<start>-<end>`. If the file
    name is not found in `diff_text`, returns the first
    `DIFF_CONTEXT_LINES` lines as fallback — validators get *some*
    context even when the location parser misses.
    """
    if not diff_text:
        return ""
    file_part = location.split(":", 1)[0] if ":" in location else location
    lines = diff_text.splitlines()
    if not file_part:
        return "\n".join(lines[:DIFF_CONTEXT_LINES])
    needle = file_part.strip()
    anchor: int | None = None
    for i, line in enumerate(lines):
        if needle and needle in line:
            anchor = i
            break
    if anchor is None:
        return "\n".join(lines[:DIFF_CONTEXT_LINES])
    half = DIFF_CONTEXT_LINES // 2
    start = max(0, anchor - half)
    end = min(len(lines), start + DIFF_CONTEXT_LINES)
    return "\n".join(lines[start:end])


PROMPT_TEMPLATE = """\
# Validator: re-score sub-80 finding

You are a fresh-context validator for code-ultrareview Phase 4. One axis
reviewer judged the finding below at sub-80 confidence. Re-score it
0-100 against the VERBATIM Anthropic rubric and verify the project-instruction
citation, if any.

## Your contract

- Read `{anthropic_verbatim}` and apply the 0-100 confidence rubric VERBATIM.
- Read `{anthropic_verbatim}` and silence false positives per the documented taxonomy.
- Re-check the project-instruction citation: if the finding cites a rule, confirm
  the rule text is actually present in the snippet below; demote with
  reason "Instruction rule not found at {instruction_path}" when absent.
- Do NOT check build signal or attempt to build / typecheck. CI does that
  separately (per the verbatim agent-assumption rule).
- Do NOT propose a new finding. Only re-score the one given.

## Finding

```json
{finding_json}
```

## Diff context (near `{location}`)

```
{diff_context}
```

## Project instruction snippet ({instruction_path})

```
{instruction_snippet}
```

## Output

Emit EXACTLY three lines to stdout, in this order, nothing else:

    run-id: {run_id}
    score: <integer 0-100>
    reason: <single-line explanation, ≤ 200 chars>

A score ≥ 80 promotes the finding into the main report. A score < 80
keeps the finding in `### ⚠️ Unverified` with your reason text.

## Stay read-only

Use `Read` only. Do NOT use `Write`, `Edit`, `Bash`, or any file-mutating
tool. Synthesis owns report emission.
"""


def build_validator_prompt(
    finding: dict,
    diff_context: str,
    instruction_snippet: str | None,
    instruction_path: str | None,
    anthropic_verbatim_path: str,
    run_id: str = "direct-call",
) -> str:
    """Build the fresh-context validator prompt for a single finding.

    Missing instruction snippet renders explicit "(not found in
    instruction_chain)" placeholders so the validator can apply the
    demote-with-reason rule deterministically.
    """
    snippet = instruction_snippet or "(not found in instruction_chain)"
    path = instruction_path or "(none)"
    return PROMPT_TEMPLATE.format(
        anthropic_verbatim=anthropic_verbatim_path,
        finding_json=json.dumps(finding, indent=2, sort_keys=False),
        location=finding.get("location", "?"),
        diff_context=diff_context or "(no diff context)",
        instruction_snippet=snippet,
        instruction_path=path,
        run_id=run_id,
    )


def prepare_validator_bundle(
    index: int,
    finding: dict,
    scope: dict,
    diff_text: str,
    output_dir: Path,
    skill_dir: Path,
    repo_dir: Path | None = None,
    run_id: str = "direct-call",
    input_hashes: dict | None = None,
) -> dict:
    """Write per-finding input + prompt files; return their absolute paths.

    Bundles are written under `output_dir/validator-input/{NNNN}.json`
    and `output_dir/validator-prompt/{NNNN}.txt`. The `NNNN` prefix is
    zero-padded so directory listings sort in dispatch order.
    """
    chain = list(
        scope["instruction_chain"]
        if "instruction_chain" in scope
        else scope.get("claude_md_chain") or []
    )
    rule_text = str(finding.get("rule") or finding.get("finding", ""))
    instruction_path, instruction_snippet = find_instruction_snippet(
        rule_text,
        chain,
        repo_dir or Path.cwd(),
        str(finding.get("location", "")),
    )

    diff_context = extract_diff_context(
        diff_text, str(finding.get("location", "")),
    )

    input_dir = output_dir / "validator-input"
    prompt_dir = output_dir / "validator-prompt"
    input_dir.mkdir(parents=True, exist_ok=True)
    prompt_dir.mkdir(parents=True, exist_ok=True)

    stem = f"{index:04d}"
    input_path = (input_dir / f"{stem}.json").resolve()
    prompt_path = (prompt_dir / f"{stem}.txt").resolve()

    anthropic_path = str((skill_dir / ANTHROPIC_VERBATIM).resolve())

    bundle = {
        "run_id": run_id,
        "input_hashes": input_hashes or {},
        "index": index,
        "finding": finding,
        "diff_context": diff_context,
        "instruction_path": instruction_path,
        "instruction_snippet": instruction_snippet,
        "claude_md_path": instruction_path,
        "claude_md_snippet": instruction_snippet,
        "anthropic_verbatim_path": anthropic_path,
    }
    input_path.write_text(
        json.dumps(bundle, indent=2, sort_keys=False), encoding="utf-8"
    )

    prompt = build_validator_prompt(
        finding=finding,
        diff_context=diff_context,
        instruction_snippet=instruction_snippet,
        instruction_path=instruction_path,
        anthropic_verbatim_path=anthropic_path,
        run_id=run_id,
    )
    prompt_path.write_text(prompt, encoding="utf-8")

    return {
        "index": index,
        "finding_id": finding.get("location", "?"),
        "input_path": str(input_path),
        "prompt_path": str(prompt_path),
        "run_id": run_id,
    }


def prepare(
    findings: list[dict],
    scope: dict,
    diff_text: str,
    output_dir: Path,
    skill_dir: Path,
    repo_dir: Path | None = None,
    run_id: str = "direct-call",
    input_hashes: dict | None = None,
) -> dict:
    """Filter sub-80 findings + write all bundles + return the batch plan.

    The `batches` field is a list of lists of indices; the orchestrator
    launches every index in one batch as parallel `Task` calls in a
    single message, waits for the batch to complete, then advances.
    """
    sub_findings = filter_sub_threshold(findings)
    bundles: dict[int, dict] = {}
    for i, finding in enumerate(sub_findings):
        bundles[i] = prepare_validator_bundle(
            index=i,
            finding=finding,
            scope=scope,
            diff_text=diff_text,
            output_dir=output_dir,
            skill_dir=skill_dir,
            repo_dir=repo_dir,
            run_id=run_id,
            input_hashes=input_hashes,
        )
    batches = batch(list(range(len(sub_findings))))
    return {
        "count": len(sub_findings),
        "batches": batches,
        "bundles": bundles,
        "run_id": run_id,
        "input_hashes": input_hashes or {},
    }


def parse_validator_output(
    stdout: str,
    expected_run_id: str | None = None,
) -> tuple[int, str]:
    """Parse `score: <int>` + `reason: <text>` from validator stdout.

    Raises `ValueError` when either line is missing or malformed — the
    orchestrator surfaces a 🔴 High finding citing the failure rather
    than silently dropping the validation result.
    """
    if not stdout:
        raise ValueError("validator stdout is empty")
    if expected_run_id is not None:
        run_match = _RUN_ID_RE.search(stdout)
        if not run_match or run_match.group(1) != expected_run_id:
            raise ValueError("validator stdout run-id does not match prepare")
    score_match = _SCORE_RE.search(stdout)
    if not score_match:
        raise ValueError("validator stdout missing `score:` line")
    score = int(score_match.group(1))
    if not 0 <= score <= 100:
        raise ValueError(f"validator score out of range: {score}")
    reason_match = _REASON_RE.search(stdout)
    if not reason_match:
        raise ValueError("validator stdout missing `reason:` line")
    reason = reason_match.group(1).strip()
    return score, reason


def _promote_finding(finding: dict, score: int, reason: str) -> dict:
    """Promote a sub-80 finding to verified state at the validator score."""
    f = dict(finding)
    f["confidence"] = min(score, PROMOTION_CAP)
    text = f.get("finding", "")
    if text.startswith(UNVERIFIED_PREFIX):
        text = text[len(UNVERIFIED_PREFIX):].lstrip()
        f["finding"] = text
    f["severity"] = synthesis_core._restore_severity(f)
    f["validator_score"] = score
    meta = dict(f.get("meta") or {})
    meta["validator_reason"] = reason
    meta["validator_outcome"] = "promoted"
    f["meta"] = meta
    return synthesis_core._attach_marker(f)


def _demote_finding(finding: dict, score: int, reason: str) -> dict:
    """Keep a sub-80 finding in Unverified state with the validator's reason."""
    f = dict(finding)
    f["confidence"] = score
    f["validator_score"] = score
    meta = dict(f.get("meta") or {})
    meta["validator_reason"] = reason
    meta["validator_outcome"] = "demoted"
    f["meta"] = meta
    return synthesis_core._attach_marker(f)


def ingest(
    validator_results: list[dict],
    sub_threshold_findings: list[dict],
    expected_run_id: str | None = None,
) -> list[dict]:
    """Apply validator scores to the sub-80 finding set.

    Each entry in `validator_results` has shape:

        {"index": int, "score": int, "reason": str}

    Returns the full updated finding list — the A2 contract guarantees
    `len(output) == len(sub_threshold_findings)`. Promoted findings
    carry `validator_score` ≥ threshold and the verified severity;
    demoted findings stay in Unverified state with the validator's
    reason recorded in `meta.validator_reason`.
    """
    expected = set(range(len(sub_threshold_findings)))
    seen: set[int] = set()
    by_index: dict[int, dict] = {}
    for result in validator_results:
        if not isinstance(result, dict):
            raise ValueError("validator result must be a JSON object")
        if expected_run_id is not None and result.get("run_id") != expected_run_id:
            raise ValueError("validator result run_id does not match prepare")
        index = result.get("index")
        if isinstance(index, bool) or not isinstance(index, int):
            raise ValueError("validator result index must be an integer")
        if index in seen:
            raise ValueError(f"duplicate validator result index: {index}")
        seen.add(index)
        score = result.get("score")
        reason = result.get("reason")
        if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 100:
            raise ValueError(f"invalid validator score at index {index}")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError(f"missing validator reason at index {index}")
        by_index[index] = result
    if seen != expected:
        missing = sorted(expected - seen)
        unexpected = sorted(seen - expected)
        detail = []
        if missing:
            detail.append(f"missing indexes {missing}")
        if unexpected:
            detail.append(f"unexpected indexes {unexpected}")
        raise ValueError("validator coverage incomplete: " + "; ".join(detail))

    out: list[dict] = []
    for i, finding in enumerate(sub_threshold_findings):
        result = by_index[i]
        score = int(result["score"])
        reason = str(result.get("reason", ""))
        if score >= CONFIDENCE_THRESHOLD:
            out.append(_promote_finding(finding, score, reason))
        else:
            out.append(_demote_finding(finding, score, reason))
    return out


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


def _read_jsonl_strict(path: Path) -> list[dict]:
    if not path.is_file():
        raise ValueError(f"JSONL file not found: {path}")
    out: list[dict] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"malformed JSONL at {path}:{line_number}") from exc
        if not isinstance(record, dict):
            raise ValueError(f"JSONL record must be an object at {path}:{line_number}")
        out.append(record)
    return out


def _verify_axis_findings(scope: dict, findings_path: Path) -> None:
    coverage = scope.get("axis_coverage")
    if not isinstance(coverage, dict):
        raise ValueError("axis coverage manifest is missing; rerun axis ingestion")
    expected_path = coverage.get("output")
    expected_digest = coverage.get("sha256")
    expected_count = coverage.get("finding_count")
    if not isinstance(expected_path, str) or not expected_path:
        raise ValueError("axis output manifest is missing; rerun axis ingestion")
    identity = {"path": expected_path, "sha256": expected_digest}
    verified_path = _verify_file_identity(identity, "axis findings")
    if verified_path != findings_path.resolve():
        raise ValueError("validator findings path does not match axis coverage")
    findings = _read_jsonl_strict(verified_path)
    if isinstance(expected_count, bool) or not isinstance(expected_count, int):
        raise ValueError("axis finding count is invalid")
    if len(findings) != expected_count:
        raise ValueError("axis findings count does not match coverage")


def _verify_validator_inputs(scope: dict) -> str:
    coverage = scope.get("validator_coverage")
    if not isinstance(coverage, dict):
        raise ValueError(
            "validator coverage manifest is missing; rerun validator preparation"
        )
    run_id = coverage.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        raise ValueError("validator run_id is missing; rerun validator preparation")
    identities = coverage.get("input_hashes")
    if not isinstance(identities, dict):
        raise ValueError("validator input manifest is missing")
    for key in ("diff", "axis_findings"):
        _verify_file_identity(identities.get(key), key.replace("_", " "))
    return run_id


def _validator_dependencies_complete(scope: dict) -> bool:
    if not (
        (scope.get("tool_coverage") or {}).get("complete") is True
        and (scope.get("axis_coverage") or {}).get("complete") is True
    ):
        return False
    for key in ("mutation_coverage", "build_coverage", "reconcile_coverage"):
        coverage = scope.get(key)
        if coverage is not None and coverage.get("complete") is not True:
            return False
    return True


def _default_skill_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 4 fresh-context-validator orchestrator for code-ultrareview"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    prep = sub.add_parser(
        "prepare",
        help="Prepare per-finding validator input bundles + prompts",
    )
    prep.add_argument("--scope", required=True, help="Path to scope.json")
    prep.add_argument(
        "--findings", required=True,
        help="Path to axis-findings.jsonl from Phase 3",
    )
    prep.add_argument(
        "--diff", required=True, help="Path to the diff text file",
    )
    prep.add_argument(
        "--output-dir", required=True,
        help="Output directory for validator-input/ and validator-prompt/",
    )
    prep.add_argument(
        "--skill-dir", default=None,
        help="Override the skill root (default: auto-detect from script path)",
    )
    prep.add_argument(
        "--repo-dir", default=None,
        help="Repo root for resolving relative instruction paths "
        "(default: current working directory)",
    )

    ing = sub.add_parser(
        "ingest",
        help="Apply validator scores to the sub-80 finding set",
    )
    ing.add_argument(
        "--findings", required=True,
        help="Path to axis-findings.jsonl (the original Phase 3 output)",
    )
    ing.add_argument(
        "--results", required=True,
        help="Path to validator-results.jsonl (one {index, score, reason} per line)",
    )
    ing.add_argument(
        "--output", required=True,
        help="Path to write validated-findings.jsonl",
    )
    ing.add_argument(
        "--scope", required=True,
        help="Path to scope.json whose coverage manifest must be completed",
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
            axis_coverage = scope.get("axis_coverage")
            if not isinstance(axis_coverage, dict):
                raise ValueError(
                    "axis coverage manifest is missing; rerun axis ingestion"
                )
            scope["validator_coverage"] = {
                "complete": False,
                "expected": 0,
                "completed": 0,
            }
            scope["coverage_complete"] = False
            _write_json_atomic(scope_path, scope)
            if axis_coverage.get("complete") is not True:
                raise ValueError(
                    "axis coverage is incomplete; finish every requested axis "
                    "before validator dispatch"
                )
            _verify_axis_findings(scope, findings_path)
            findings = _read_jsonl_strict(findings_path)
            diff_text = _read_text(diff_path)
            run_id = uuid.uuid4().hex
            input_hashes = {
                "diff": _file_identity(diff_path),
                "axis_findings": _file_identity(findings_path),
            }
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"ERROR: validator coverage incomplete: {exc}", file=sys.stderr)
            return 4
        output_dir = Path(args.output_dir).resolve()
        skill_dir = (
            Path(args.skill_dir).resolve()
            if args.skill_dir else _default_skill_dir()
        )
        repo_dir = (
            Path(args.repo_dir).resolve()
            if args.repo_dir else Path.cwd()
        )

        result = prepare(
            findings=findings,
            scope=scope,
            diff_text=diff_text,
            output_dir=output_dir,
            skill_dir=skill_dir,
            repo_dir=repo_dir,
            run_id=run_id,
            input_hashes=input_hashes,
        )
        count = int(result["count"])
        scope["validator_coverage"] = {
            "complete": count == 0,
            "expected": count,
            "completed": 0,
            "run_id": run_id,
            "input_hashes": input_hashes,
        }
        if count == 0:
            scope["validator_coverage"].update({
                "output": str(findings_path.resolve()),
                "sha256": input_hashes["axis_findings"]["sha256"],
                "finding_count": len(findings),
            })
        scope["coverage_complete"] = bool(
            count == 0
            and _validator_dependencies_complete(scope)
        )
        _write_json_atomic(scope_path, scope)
        sys.stdout.write(json.dumps(result, indent=2, sort_keys=False) + "\n")
        return 0

    if args.cmd == "ingest":
        findings_path = Path(args.findings)
        results_path = Path(args.results)
        output_path = Path(args.output)
        scope_path = Path(args.scope)

        try:
            scope = _read_json(scope_path)
            previous = scope.get("validator_coverage")
            if not isinstance(previous, dict):
                raise ValueError(
                    "validator coverage manifest is missing; rerun validator preparation"
                )
            scope["validator_coverage"] = {
                "complete": False,
                "expected": int(previous.get("expected") or 0),
                "completed": 0,
                "run_id": previous.get("run_id"),
                "input_hashes": previous.get("input_hashes"),
            }
            scope["coverage_complete"] = False
            _write_json_atomic(scope_path, scope)
            if output_path.exists():
                output_path.unlink()
            if (scope.get("axis_coverage") or {}).get("complete") is not True:
                raise ValueError(
                    "axis coverage is incomplete; rerun axis ingestion before "
                    "validator ingestion"
                )
            run_id = _verify_validator_inputs(scope)
            _verify_axis_findings(scope, findings_path)
            all_findings = _read_jsonl_strict(findings_path)
            sub_findings = filter_sub_threshold(all_findings)
            if scope["validator_coverage"]["expected"] != len(sub_findings):
                raise ValueError(
                    "validator input count does not match the prepared coverage "
                    "manifest; rerun validator preparation"
                )
            results = _read_jsonl_strict(results_path)
            validated_sub = ingest(
                results,
                sub_findings,
                expected_run_id=run_id,
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"ERROR: validator coverage incomplete: {exc}", file=sys.stderr)
            return 4

        validated_iter = iter(validated_sub)
        validated = []
        for finding in all_findings:
            confidence = int(finding.get("confidence", 0))
            if 0 <= confidence < CONFIDENCE_THRESHOLD:
                validated.append(next(validated_iter))
            else:
                validated.append(finding)

        _write_jsonl_atomic(output_path, validated)
        output_identity = _file_identity(output_path)
        scope["validator_coverage"] = {
            "complete": True,
            "expected": len(sub_findings),
            "completed": len(results),
            "run_id": run_id,
            "input_hashes": previous.get("input_hashes"),
            "output": output_identity["path"],
            "sha256": output_identity["sha256"],
            "finding_count": len(validated),
        }
        scope["coverage_complete"] = _validator_dependencies_complete(scope)
        _write_json_atomic(scope_path, scope)
        sys.stdout.write(
            json.dumps({
                "input_count": len(all_findings),
                "validated_count": len(sub_findings),
                "output_count": len(validated),
                "output_path": str(output_path.resolve()),
            }, indent=2) + "\n"
        )
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
