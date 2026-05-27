#!/usr/bin/env python3
"""Phase 5 synthesis orchestrator for code-ultrareview.

Composes `synthesis_core` primitives — dedup by inter-axis precedence,
A2 no-silent-drop routing, Anthropic tier classification, canonical
ordering, verdict computation — then renders the 8-axis markdown report
to stdout (terminal-echo contract) plus a side-by-side Conventional
Comments JSONL through `findings_to_jsonl`. When `--save` is set, the
same bytes land at the canonical output path.

The markdown layout is built programmatically here; `templates/code-
ultrareview.md` documents the canonical wire format. Section order is
fixed:

    📋 Axis summary
    🔎 Findings (🔴 High / 🟠 Medium / 🟢 Low / ⚠️ Unverified)
    ✅ What looks good
    ⚖️ Verdict
    🧰 Tools skipped
    🛡️ What I did NOT check
    📐 Derivation coverage   (only when --reconcile resolved input)
    🪛 --apply-safe summary  (only when --apply-safe ran)

CLI:
    python3 synthesize.py \\
        --scope scope.json \\
        --findings validated-findings.jsonl \\
        [--tool-findings tool-findings.jsonl] \\
        [--positives positives.jsonl] \\
        [--output-dir <dir>] \\
        [--slug <slug>] \\
        [--save | --no-save] \\
        [--reconcile-summary path] \\
        [--apply-safe-summary path]

Inputs:
    `scope.json` — Phase 1 output (repo_kind, languages, tools_skipped, …).
    `validated-findings.jsonl` — Phase 4 output: axis findings after
        Haiku validator scoring, with `validator_score` / `meta
        .validator_reason` fields filled in where applicable.
    `tool-findings.jsonl` — Phase 2 output: confidence-100 deterministic
        tool findings. Skipped by validators; concatenated here.
    `positives.jsonl` — optional list of `{"text": "…"}` records that
        feed the `✅ What looks good` section verbatim.

Outputs (when `--save`):
    `~/.claude/output/{project}/code-ultrareview/code-ultrareview-{slug}.md`
    `~/.claude/output/{project}/code-ultrareview/code-ultrareview-{slug}.jsonl`
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def _load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


synthesis_core = _load_module("synthesis_core")
findings_to_jsonl = _load_module("findings_to_jsonl")

GIT_TIMEOUT_S = 10

CONFIDENCE_THRESHOLD = synthesis_core.CONFIDENCE_THRESHOLD
SEVERITY_MARKERS = synthesis_core.SEVERITY_MARKERS
CANONICAL_AXES = synthesis_core.CANONICAL_AXES

# The four severity sub-sections under `🔎 Findings`, in render order.
_SEVERITY_SECTIONS = (
    ("🔴 High", "High", "H"),
    ("🟠 Medium", "Medium", "M"),
    ("🟢 Low", "Low", "L"),
)
_UNVERIFIED_SECTION = ("⚠️ Unverified", "Unverified", "U")

# Mandatory deferral entries. Always present in `🛡️ What I did NOT check`,
# even when zero tools were skipped — explicit user-facing calibration of
# coverage boundaries.
_DEFERRALS = (
    (
        "Security",
        "Defers to `/security-review` or "
        "`https://github.com/anthropics/claude-code-security-review`. "
        "Distinct concern with its own deeper review pattern.",
    ),
    (
        "Runtime performance",
        "Static patterns only (N+1, sync I/O). No benchmarks, no flamegraphs, "
        "no memory traces.",
    ),
    (
        "Flaky test detection",
        "Structural smells only. Flake requires repeated runs the skill does "
        "not perform.",
    ),
)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def load_findings(path: Path | None) -> list[dict]:
    if path is None:
        return []
    if not path.exists():
        return []
    return findings_to_jsonl.load_findings(path)


def load_scope(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_positives(path: Path | None) -> list[str]:
    if path is None or not path.exists():
        return []
    out: list[str] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            text = str(record.get("text", "")).strip()
            if text:
                out.append(text)
    return out


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


def synthesize(
    scope: dict,
    findings: list[dict],
) -> dict:
    """Apply Phase-5 synthesis to a finding stream.

    Order: A2 routing first (post-validator findings may already carry
    correct severity, but apply_a2 is idempotent and re-attaches markers
    on rerun) → dedup by inter-axis precedence on the verified set →
    Anthropic tier classification → canonical ordering → verdict.

    Returns a dict ready for the renderer:

        {
            "verified": list[dict],         # surviving verified findings
            "unverified": list[dict],       # A2-routed sub-80 (no drop)
            "verdict": dict,                # label + rationale + drivers
            "counts": dict[str, int],       # 🔴/🟠/🟢 per marker
            "axis_summary": list[dict],     # rows for the summary table
        }
    """
    verified, unverified = synthesis_core.apply_a2(findings)
    verified = synthesis_core.dedup_by_precedence(verified)
    verified = [synthesis_core.assign_anthropic_tier(f) for f in verified]
    verified = synthesis_core.order(verified)
    unverified = synthesis_core.order(unverified)
    verdict = synthesis_core.compute_verdict(verified)
    counts = synthesis_core.compute_severity_counts(verified)
    summary = build_axis_summary(scope, verified, unverified)
    return {
        "verified": verified,
        "unverified": unverified,
        "verdict": verdict,
        "counts": counts,
        "axis_summary": summary,
    }


def build_axis_summary(
    scope: dict,
    verified: list[dict],
    unverified: list[dict],
) -> list[dict]:
    """One row per always-on axis plus a coherence row reflecting its
    activation state. Status reflects the highest verified severity in
    the axis (🔴 → 🟠 → 🟢 → `—` when zero verified)."""
    rows: list[dict] = []
    coherence_active = bool(scope.get("activates_coherence"))
    axes = [*CANONICAL_AXES, "coherence"]
    for axis in axes:
        verified_in_axis = [f for f in verified if f.get("axis") == axis]
        unverified_in_axis = [f for f in unverified if f.get("axis") == axis]
        if axis == "coherence" and not coherence_active:
            status = "— inactive (no metadata in diff)"
            top = ""
        else:
            status = _status_marker(verified_in_axis) if verified_in_axis else "🟢"
            top = _top_finding_text(verified_in_axis or unverified_in_axis)
        rows.append({
            "axis": axis,
            "status": status,
            "verified": len(verified_in_axis),
            "unverified": len(unverified_in_axis),
            "top": top,
        })
    return rows


def _status_marker(findings: list[dict]) -> str:
    severities = {f.get("severity") for f in findings}
    if "High" in severities:
        return SEVERITY_MARKERS["High"]
    if "Medium" in severities:
        return SEVERITY_MARKERS["Medium"]
    return SEVERITY_MARKERS["Low"]


def _top_finding_text(findings: list[dict]) -> str:
    if not findings:
        return ""
    text = str(findings[0].get("finding", "")).strip()
    return _truncate(text, 80)


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def render_markdown(
    scope: dict,
    result: dict,
    *,
    slug: str,
    positives: list[str],
    reconcile_block: str | None = None,
    apply_safe_block: str | None = None,
) -> str:
    """Render the 8-axis markdown report in the canonical section order."""
    parts: list[str] = []
    parts.append(_render_header(scope, slug, result["counts"], result["unverified"]))
    parts.append(_render_axis_summary(result["axis_summary"]))
    parts.append(_render_findings(result["verified"], result["unverified"]))
    parts.append(_render_what_looks_good(positives))
    parts.append(_render_verdict(result["verdict"]))
    parts.append(_render_tools_skipped(scope.get("tools_skipped") or []))
    parts.append(_render_did_not_check(scope.get("tools_skipped") or []))
    if reconcile_block:
        parts.append(reconcile_block.strip())
    if apply_safe_block:
        parts.append(apply_safe_block.strip())
    parts.append(_render_footer())
    return "\n\n".join(parts).rstrip() + "\n"


def _render_header(
    scope: dict,
    slug: str,
    counts: dict[str, int],
    unverified: list[dict],
) -> str:
    base = scope.get("base") or "—"
    target = scope.get("target") or "HEAD"
    rule = scope.get("rule") or scope.get("rung") or "—"
    repo_kind = scope.get("repo_kind") or "unknown"
    languages = ", ".join(scope.get("languages") or []) or "—"
    changed_files = scope.get("files_touched_list") or []
    files_count = len(changed_files)
    chain = scope.get("claude_md_chain") or []
    rules_baseline = (
        f"CLAUDE.md chain + {len(chain)} files" if chain
        else "skipped — no rules baseline found"
    )
    coherence = "active" if scope.get("activates_coherence") else "inactive"

    red = counts.get("🔴", 0)
    orange = counts.get("🟠", 0)
    green = counts.get("🟢", 0)
    unv = len(unverified)

    lines = [
        f"# Code ultrareview — {slug}",
        "",
        f"**Base:** `{base}` · **Target:** `{target}` · **Rule:** {rule}",
        f"**Repo:** {repo_kind} · **Languages:** {languages}",
        f"**Rules baseline:** {rules_baseline}",
        f"**Reviewed:** {files_count} changed file(s)",
        f"**Coherence axis:** {coherence}",
        f"**Findings:** {red} 🔴 · {orange} 🟠 · {green} 🟢 (verified) · {unv} unverified",
        "",
        "> **Section discipline (mandatory).** Every `##` heading below is "
        "canonical — render it verbatim, including the emoji prefix and the "
        "`---` separator above it. Do not rename, merge, reorder, or invent "
        "sections. Every severity sub-section inside `## 🔎 Findings` renders "
        "even when its count is `0` (body: `_None._`). The model is a "
        "formatter here, not an editor.",
        ">",
        "> **Terminal echo is mandatory.** The full report below prints to "
        "the chat-terminal on every invocation. The `-s` flag is purely "
        "additive — it writes the same bytes to "
        "`~/.claude/output/{project}/code-ultrareview/code-ultrareview-{slug}.md`. "
        "It does not gate, truncate, or summarise what the user sees in "
        "chat. Terminal output and saved file are byte-for-byte identical.",
    ]
    return "\n".join(lines)


def _render_axis_summary(rows: list[dict]) -> str:
    lines = [
        "---",
        "",
        "## 📋 Axis summary",
        "",
        "Per-axis status snapshot — all 8 canonical axes appear, including "
        "clean ones. The Coherence row reads `— inactive (no metadata in "
        "diff)` when the conditional axis did not launch.",
        "",
        "| Axis | Status | Verified | Unverified | Top finding |",
        "|------|--------|----------|------------|-------------|",
    ]
    for row in rows:
        top = row["top"] or "—"
        lines.append(
            f"| {row['axis']} | {row['status']} | {row['verified']} | "
            f"{row['unverified']} | {top} |"
        )
    return "\n".join(lines)


def _render_findings(verified: list[dict], unverified: list[dict]) -> str:
    parts = [
        "---",
        "",
        "## 🔎 Findings",
        "",
        "Verified findings split by severity into three sub-sections, each "
        "prefixed by its canonical emoji. Row IDs carry a per-section prefix "
        "(`H1`, `H2`, …, `M1`, …, `L1`, …). Unverified findings (confidence "
        "< 80, A2-routed) render as a fourth sub-section, prefixed `⚠️` and "
        "ID-prefixed `U1`, `U2`, …",
        "",
        "Render every sub-section in this exact order, including when the "
        "count is zero (body: `_None._`).",
    ]
    for emoji_name, severity, prefix in _SEVERITY_SECTIONS:
        rows = [f for f in verified if f.get("severity") == severity]
        parts.append("")
        parts.append(f"### {emoji_name} ({len(rows)} findings)")
        parts.append("")
        if not rows:
            parts.append("_None._")
            continue
        parts.append(
            "| # | Axis | Tier | Location | Conf | Finding | Recommendation |"
        )
        parts.append(
            "|---|------|------|----------|------|---------|----------------|"
        )
        for idx, f in enumerate(rows, 1):
            parts.append(_render_row(f"{prefix}{idx}", f, with_tier=True))

    parts.append("")
    parts.append(f"### {_UNVERIFIED_SECTION[0]} ({len(unverified)} findings)")
    parts.append("")
    if not unverified:
        parts.append("_None._")
    else:
        parts.append(
            "Findings with confidence < 80 surfaced per A2 (no silent drop). "
            "Severity is downgraded to Low at routing time. Each row's "
            "recommendation states the score so the reader can decide whether "
            "to verify locally, strengthen the test, or drop."
        )
        parts.append("")
        parts.append(
            "| # | Axis | Location | Conf | Finding | Recommendation |"
        )
        parts.append(
            "|---|------|----------|------|---------|----------------|"
        )
        for idx, f in enumerate(unverified, 1):
            parts.append(_render_row(f"U{idx}", f, with_tier=False))
    return "\n".join(parts)


def _render_row(row_id: str, finding: dict, *, with_tier: bool) -> str:
    axis = finding.get("axis", "?")
    location = finding.get("location", "?")
    conf = int(finding.get("confidence", 0))
    text = _escape_cell(finding.get("finding", ""))
    rec = _escape_cell(finding.get("recommendation", ""))
    loc_cell = f"`{location}`" if location and location != "?" else "—"
    if with_tier:
        tier = (finding.get("meta") or {}).get("anthropic_tier", "—")
        return (
            f"| {row_id} | {axis} | {tier} | {loc_cell} | {conf} | "
            f"{text} | {rec} |"
        )
    return (
        f"| {row_id} | {axis} | {loc_cell} | {conf} | {text} | {rec} |"
    )


def _escape_cell(text) -> str:
    s = str(text or "").strip()
    return s.replace("|", "\\|").replace("\n", " ")


def _render_what_looks_good(positives: list[str]) -> str:
    lines = ["---", "", "## ✅ What looks good", ""]
    if not positives:
        lines.append("_None surfaced this run._")
    else:
        for entry in positives:
            lines.append(f"- {entry.strip()}")
    return "\n".join(lines)


def _render_verdict(verdict: dict) -> str:
    label = verdict.get("label", "Ship")
    rationale = verdict.get("rationale", "")
    drivers = verdict.get("drivers") or []
    lines = ["---", "", "## ⚖️ Verdict", "", f"**{label}** — {rationale}"]
    if len(drivers) >= 2:
        lines.append("")
        lines.append("Drivers:")
        for driver in drivers:
            lines.append(f"- {driver}")
    lines.append("")
    lines.append(
        "Algorithm: any 🔴 + Important → Needs work; else any 🟠 + Important "
        "→ Fix-then-ship; else Ship. Unverified findings are excluded."
    )
    return "\n".join(lines)


def _render_tools_skipped(tools: list) -> str:
    lines = ["---", "", "## 🧰 Tools skipped", ""]
    if not tools:
        lines.append("_None — every detected tool ran._")
        return "\n".join(lines)
    lines.append(
        "Tools the battery would have run but couldn't. Install commands "
        "surface verbatim from `scope.json[\"tools_skipped\"]`."
    )
    lines.append("")
    lines.append("| Tool | Axis | Install |")
    lines.append("|------|------|---------|")
    for entry in tools:
        if isinstance(entry, dict):
            tool = entry.get("tool", "?")
            axis = entry.get("axis", "?")
            install = entry.get("install", "?")
        else:
            tool, axis, install = str(entry), "?", "?"
        lines.append(f"| `{tool}` | {axis} | `{install}` |")
    return "\n".join(lines)


def _render_did_not_check(tools_skipped: list) -> str:
    lines = [
        "---",
        "",
        "## 🛡️ What I did NOT check",
        "",
        "Coverage boundaries — explicit by design.",
        "",
    ]
    for name, body in _DEFERRALS:
        lines.append(f"- **{name}** — {body}")
    if tools_skipped:
        lines.append(
            "- **Tools listed in `## 🧰 Tools skipped` above** — install them "
            "to recover the coverage."
        )
    else:
        lines.append(
            "- **Tools listed in `## 🧰 Tools skipped` above** — none this run."
        )
    return "\n".join(lines)


def _render_footer() -> str:
    return (
        "---\n\n"
        "_Report-only by default. To fix: "
        "`/apex -f ~/.claude/output/{project}/code-ultrareview/"
        "code-ultrareview-{slug}.md` or `/oneshot \"<finding>\"`. Opt-in "
        "`--apply-safe` writes manifest sync + failing tests with diff "
        "preview + per-file confirmation._"
    )


# ---------------------------------------------------------------------------
# Output paths
# ---------------------------------------------------------------------------


def project_slug(repo_root: Path) -> str:
    """Mirror the apex/repo convention: kebab basename of the git toplevel,
    else the cwd basename. All-non-alnum → `unnamed`."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=GIT_TIMEOUT_S, check=False,
        )
        toplevel = result.stdout.strip() if result.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        toplevel = ""
    root = Path(toplevel) if toplevel else repo_root
    base = root.name.lower()
    cleaned = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return cleaned or "unnamed"


def output_paths(repo_root: Path, slug: str) -> tuple[Path, Path]:
    """Build the canonical save-mode paths.

    Returns `(md, jsonl)` under
    `~/.claude/output/<project>/code-ultrareview/`.
    """
    project = project_slug(repo_root)
    base = Path.home() / ".claude" / "output" / project / "code-ultrareview"
    return (
        base / f"code-ultrareview-{slug}.md",
        base / f"code-ultrareview-{slug}.jsonl",
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", required=True, type=Path)
    parser.add_argument("--findings", required=True, type=Path,
                        help="Validated axis findings JSONL (post Phase 4).")
    parser.add_argument("--tool-findings", type=Path, default=None,
                        help="Tool battery findings (confidence-100).")
    parser.add_argument("--positives", type=Path, default=None,
                        help="Positives JSONL — feeds `✅ What looks good`.")
    parser.add_argument("--slug", default=None,
                        help="Output slug. Defaults to `review`.")
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="Write `report.{md,jsonl}` here. Bypasses "
                             "canonical save-mode paths.")
    parser.add_argument("--save", dest="save", action="store_true",
                        help="Write to canonical "
                             "~/.claude/output/.../code-ultrareview-<slug>.{md,jsonl}.")
    parser.add_argument("--no-save", dest="save", action="store_false")
    parser.set_defaults(save=False)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--owner-repo", default=None)
    parser.add_argument("--sha", default=None)
    parser.add_argument("--reconcile-summary", type=Path, default=None,
                        help="Pre-rendered `## 📐 Derivation coverage` block.")
    parser.add_argument("--apply-safe-summary", type=Path, default=None,
                        help="Pre-rendered `## 🪛 --apply-safe summary` block.")
    parser.add_argument("--print", dest="echo",
                        action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args(argv)

    scope = load_scope(args.scope)
    findings: list[dict] = []
    findings.extend(load_findings(args.findings))
    findings.extend(load_findings(args.tool_findings))
    positives = load_positives(args.positives)
    slug = args.slug or "review"

    result = synthesize(scope, findings)

    reconcile_block = _read_text(args.reconcile_summary)
    apply_safe_block = _read_text(args.apply_safe_summary)
    markdown = render_markdown(
        scope, result, slug=slug, positives=positives,
        reconcile_block=reconcile_block,
        apply_safe_block=apply_safe_block,
    )

    owner_repo = args.owner_repo or findings_to_jsonl.detect_owner_repo(args.repo_root)
    sha = args.sha or findings_to_jsonl.detect_sha(args.repo_root)
    jsonl_lines = list(findings_to_jsonl.emit(
        result["verified"] + result["unverified"],
        owner_repo=owner_repo, sha=sha,
    ))
    jsonl_text = "\n".join(jsonl_lines) + ("\n" if jsonl_lines else "")

    if args.echo:
        sys.stdout.write(markdown)
        sys.stdout.flush()

    md_path: Path | None = None
    jsonl_path: Path | None = None
    if args.output_dir is not None:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        md_path = args.output_dir / "report.md"
        jsonl_path = args.output_dir / "report.jsonl"
    elif args.save:
        md_path, jsonl_path = output_paths(args.repo_root, slug)
        md_path.parent.mkdir(parents=True, exist_ok=True)

    if md_path is not None:
        md_path.write_text(markdown, encoding="utf-8")
    if jsonl_path is not None:
        jsonl_path.write_text(jsonl_text, encoding="utf-8")

    if md_path is not None and not args.echo:
        # Quiet save mode — surface the path so callers can `Read` it.
        print(f"RESULT: report={md_path}", file=sys.stderr)
    return 0


def _read_text(path: Path | None) -> str | None:
    if path is None or not path.exists():
        return None
    return path.read_text(encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
