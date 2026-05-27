#!/usr/bin/env python3
"""Phase 4 Haiku-validator orchestrator for code-ultrareview.

The main thread launches one Haiku validator per still-sub-80 finding
from Phase 3, batched at ten parallel (subagents cannot spawn other
subagents — repo convention, `skills/agent-creator/SKILL.md:137`). This
module is the deterministic half:

1. Filter the sub-80 finding set from Phase 3 — confidence-100 tool
   findings skip validation entirely.
2. Locate the deepest matching CLAUDE.md snippet from the chain so the
   validator can re-check whether the cited rule actually exists.
3. Build the per-finding validator prompt — citing
   `references/anthropic-verbatim.md` rubric VERBATIM, plus the
   CLAUDE.md re-check requirement.
4. Write per-finding input bundles to disk so the main-thread orchestrator
   can `Read` them and fan out `Task` calls in batches of ten.

After the main thread collects validator stdout, `ingest` parses scores
and reasons, then applies the A2 promote/demote routing on top of
`synthesis_core` primitives — no sub-80 finding silently dropped.

Canonical schemas:

    axis-findings.jsonl            # produced by Phase 3 axis subagents
    validator-input/{NNNN}.json    # {finding, diff_context, claude_md_*, paths}
    validator-prompt/{NNNN}.txt    # full Haiku prompt blob
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
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import TypeVar

# Reuse synthesis_core primitives — single source of truth for the
# 80 threshold, the [unverified] prefix, and the severity restoration
# semantics. A divergence here breaks the A2 contract; tests enforce it.
_SYNTH_PATH = Path(__file__).resolve().parent / "synthesis_core.py"
_spec = importlib.util.spec_from_file_location("synthesis_core", _SYNTH_PATH)
assert _spec is not None and _spec.loader is not None
synthesis_core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(synthesis_core)

CONFIDENCE_THRESHOLD = synthesis_core.CONFIDENCE_THRESHOLD
PROMOTION_CAP = synthesis_core.PROMOTION_CAP
UNVERIFIED_PREFIX = synthesis_core.UNVERIFIED_PREFIX

# Soft concurrency cap — Anthropic's `code-review` plugin batches one
# Haiku validator per finding at ten parallel; the deep research echoes
# the same community-observed limit.
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


# ---------------------------------------------------------------------------
# Filtering — only sub-80 axis findings reach validators
# ---------------------------------------------------------------------------


def filter_sub_threshold(findings: list[dict]) -> list[dict]:
    """Return only findings with confidence in `(0, CONFIDENCE_THRESHOLD)`.

    Excludes:
    - confidence-0 findings — A2 already drops these (false positives).
    - confidence-100 findings — deterministic tool battery output;
      validators never see them.
    - confidence ≥ threshold — already verified; no validator pass.
    """
    out: list[dict] = []
    for f in findings:
        conf = int(f.get("confidence", 0))
        if 0 < conf < CONFIDENCE_THRESHOLD:
            out.append(f)
    return out


# ---------------------------------------------------------------------------
# Batching — never launch more than MAX_BATCH_SIZE validators in parallel
# ---------------------------------------------------------------------------


_T = TypeVar("_T")


def batch(items: list[_T], size: int = MAX_BATCH_SIZE) -> list[list[_T]]:
    """Split an item list into contiguous batches of at most `size`.

    Spec AC: 25 sub-80 findings → 3 batches (10 + 10 + 5). Generic so
    `prepare` can batch indices while tests can batch finding dicts.
    """
    if size <= 0:
        raise ValueError(f"batch size must be positive, got {size}")
    return [items[i:i + size] for i in range(0, len(items), size)]


# ---------------------------------------------------------------------------
# CLAUDE.md snippet lookup — feeds the validator's re-check
# ---------------------------------------------------------------------------


def find_claude_md_snippet(
    rule_text: str,
    claude_md_chain: list[str],
    repo_dir: Path,
) -> tuple[str | None, str | None]:
    """Return `(path, snippet)` for the deepest CLAUDE.md file whose body
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
    for path_str in claude_md_chain:
        path = Path(path_str)
        if not path.is_absolute():
            path = repo_dir / path
        if not path.is_file():
            continue
        try:
            body = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
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


# ---------------------------------------------------------------------------
# Diff-context extraction — give the validator the surrounding hunk
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Prompt template — uniform across findings
# ---------------------------------------------------------------------------


PROMPT_TEMPLATE = """\
# Validator: re-score sub-80 finding

You are a Haiku validator for code-ultrareview Phase 4. One axis
reviewer judged the finding below at sub-80 confidence. Re-score it
0-100 against the VERBATIM Anthropic rubric and verify the CLAUDE.md
citation, if any.

## Your contract

- Read `{anthropic_verbatim}` and apply the 0-100 confidence rubric VERBATIM.
- Read `{anthropic_verbatim}` and silence false positives per the documented taxonomy.
- Re-check the CLAUDE.md citation: if the finding cites a rule, confirm
  the rule text is actually present in the snippet below; demote with
  reason "CLAUDE.md rule not found at {claude_md_path}" when absent.
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

## CLAUDE.md snippet ({claude_md_path})

```
{claude_md_snippet}
```

## Output

Emit EXACTLY two lines to stdout, in this order, nothing else:

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
    claude_md_snippet: str | None,
    claude_md_path: str | None,
    anthropic_verbatim_path: str,
) -> str:
    """Build the Haiku validator prompt for a single finding.

    Missing CLAUDE.md snippet renders explicit "(not found in
    claude_md_chain)" placeholders so the validator can apply the
    demote-with-reason rule deterministically.
    """
    snippet = claude_md_snippet or "(not found in claude_md_chain)"
    path = claude_md_path or "(none)"
    return PROMPT_TEMPLATE.format(
        anthropic_verbatim=anthropic_verbatim_path,
        finding_json=json.dumps(finding, indent=2, sort_keys=False),
        location=finding.get("location", "?"),
        diff_context=diff_context or "(no diff context)",
        claude_md_snippet=snippet,
        claude_md_path=path,
    )


# ---------------------------------------------------------------------------
# Per-finding bundle preparation
# ---------------------------------------------------------------------------


def prepare_validator_bundle(
    index: int,
    finding: dict,
    scope: dict,
    diff_text: str,
    output_dir: Path,
    skill_dir: Path,
    repo_dir: Path | None = None,
) -> dict:
    """Write per-finding input + prompt files; return their absolute paths.

    Bundles are written under `output_dir/validator-input/{NNNN}.json`
    and `output_dir/validator-prompt/{NNNN}.txt`. The `NNNN` prefix is
    zero-padded so directory listings sort in dispatch order.
    """
    chain = list(scope.get("claude_md_chain", []))
    rule_text = str(finding.get("rule") or finding.get("finding", ""))
    claude_md_path, claude_md_snippet = find_claude_md_snippet(
        rule_text, chain, repo_dir or Path.cwd(),
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
        "index": index,
        "finding": finding,
        "diff_context": diff_context,
        "claude_md_path": claude_md_path,
        "claude_md_snippet": claude_md_snippet,
        "anthropic_verbatim_path": anthropic_path,
    }
    input_path.write_text(
        json.dumps(bundle, indent=2, sort_keys=False), encoding="utf-8"
    )

    prompt = build_validator_prompt(
        finding=finding,
        diff_context=diff_context,
        claude_md_snippet=claude_md_snippet,
        claude_md_path=claude_md_path,
        anthropic_verbatim_path=anthropic_path,
    )
    prompt_path.write_text(prompt, encoding="utf-8")

    return {
        "index": index,
        "finding_id": finding.get("location", "?"),
        "input_path": str(input_path),
        "prompt_path": str(prompt_path),
    }


def prepare(
    findings: list[dict],
    scope: dict,
    diff_text: str,
    output_dir: Path,
    skill_dir: Path,
    repo_dir: Path | None = None,
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
        )
    batches = batch(list(range(len(sub_findings))))
    return {
        "count": len(sub_findings),
        "batches": batches,
        "bundles": bundles,
    }


# ---------------------------------------------------------------------------
# Validator stdout parsing
# ---------------------------------------------------------------------------


def parse_validator_output(stdout: str) -> tuple[int, str]:
    """Parse `score: <int>` + `reason: <text>` from validator stdout.

    Raises `ValueError` when either line is missing or malformed — the
    orchestrator surfaces a 🔴 High finding citing the failure rather
    than silently dropping the validation result.
    """
    if not stdout:
        raise ValueError("validator stdout is empty")
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


# ---------------------------------------------------------------------------
# Ingest — apply validator scores while preserving A2
# ---------------------------------------------------------------------------


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
    by_index = {r["index"]: r for r in validator_results}
    out: list[dict] = []
    for i, finding in enumerate(sub_threshold_findings):
        result = by_index.get(i)
        if result is None:
            # No validator output reached us — keep the finding at its
            # original sub-80 confidence with an explicit reason. A2
            # forbids silent drop.
            out.append(_demote_finding(
                finding, int(finding.get("confidence", 0)),
                "Validator produced no output — treat as unverified",
            ))
            continue
        score = int(result["score"])
        reason = str(result.get("reason", ""))
        if score >= CONFIDENCE_THRESHOLD:
            out.append(_promote_finding(finding, score, reason))
        else:
            out.append(_demote_finding(finding, score, reason))
    return out


# ---------------------------------------------------------------------------
# CLI
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
        description="Phase 4 Haiku-validator orchestrator for code-ultrareview"
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
        help="Repo root for resolving relative CLAUDE.md paths "
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
        )
        sys.stdout.write(json.dumps(result, indent=2, sort_keys=False) + "\n")
        return 0

    if args.cmd == "ingest":
        findings_path = Path(args.findings)
        results_path = Path(args.results)
        output_path = Path(args.output)

        all_findings = _read_jsonl(findings_path)
        sub_findings = filter_sub_threshold(all_findings)
        results = _read_jsonl(results_path)
        validated = ingest(results, sub_findings)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as fh:
            for f in validated:
                fh.write(json.dumps(f, sort_keys=False) + "\n")
        sys.stdout.write(
            json.dumps({
                "input_count": len(sub_findings),
                "output_count": len(validated),
                "output_path": str(output_path.resolve()),
            }, indent=2) + "\n"
        )
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
