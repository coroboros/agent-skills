"""WS-5 acceptance tests for `scripts/synthesize.py`.

Pins the eight contracts from the workstream:

    1. Inter-axis precedence — when ≥2 axes flag the same `file:line`
       with the same finding text, highest severity wins; tie → axis order
       Correctness > Design/API > Simplification > Tests > Documentation
       > Style > Intent > Performance > Coherence.
    2. A2 carryover — sub-80 confidence findings always surface in the
       `### ⚠️ Unverified` sub-section. Never silently dropped.
    3. Verdict algorithm — carried from `synthesis_core.compute_verdict`;
       this test asserts the report header reflects it.
    4. "What I did NOT check" — always present, even when zero tools
       were skipped (with the body switching to "none this run.").
    5. Required sections — every entry in
       `report_required_sections` appears in the rendered markdown.
    6. Severity counts in header — `{n_red} 🔴 · {n_orange} 🟠 ·
       {n_green} 🟢 (verified) · {n_unverified} unverified`.
    7. Coherence axis state — header surfaces `active` or `inactive` per
       `scope.json["activates_coherence"]`.
    8. Save-mode paths — `--output-dir <dir>` writes `report.md` +
       `report.jsonl`; `--save` lands at the canonical
       `~/.agents/output/<project>/code-ultrareview/code-ultrareview-<slug>.{md,jsonl}`.
"""

from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT_DIR = REPO_ROOT / "skills" / "code-ultrareview" / "scripts"
SYNTHESIZE = SCRIPT_DIR / "synthesize.py"

sys.path.insert(0, str(REPO_ROOT / "tests" / "_pipeline"))
from _contracts import CLUSTERS  # noqa: E402

REVIEW = CLUSTERS["review"]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


synthesis_core = _load("synthesis_core")
synthesize = _load("synthesize")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _finding(**overrides) -> dict:
    base = {
        "axis": "correctness",
        "severity": "Medium",
        "location": "src/a.ts:10",
        "finding": "Potential null deref",
        "recommendation": "Add a guard",
        "confidence": 85,
    }
    base.update(overrides)
    return base


def _scope(**overrides) -> dict:
    base = {
        "base": "abc1234",
        "target": "HEAD",
        "rule": "merge-base",
        "repo_kind": "app",
        "languages": ["typescript"],
        "instruction_chain": ["AGENTS.md"],
        "activates_coherence": False,
        "tools_skipped": [],
        "tools_missing": [],
        "changed_files": ["src/a.ts"],
        "tool_coverage": {
            "complete": True,
            "selected_axes": [],
            "applicable": [],
            "executed": [],
        },
        "validator_coverage": {"complete": True, "expected": 0, "completed": 0},
        "coverage_complete": True,
    }
    base.update(overrides)
    if "axis_coverage" not in overrides:
        requested = list(synthesis_core.CANONICAL_AXES)
        if base["activates_coherence"]:
            requested.append("coherence")
        base["axis_coverage"] = {
            "complete": True,
            "full": True,
            "requested": requested,
            "completed": requested,
        }
    return base


def _write_jsonl(path: Path, findings: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(f, sort_keys=True) for f in findings) + "\n",
        encoding="utf-8",
    )


def _identity(path: Path) -> dict:
    data = path.read_bytes()
    return {
        "path": str(path.resolve()),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def _run_synthesize(
    scope: dict,
    findings: list[dict],
    *,
    output_dir: Path,
    save: bool = False,
    slug: str = "audit",
    repo_root: Path | None = None,
    tool_findings: list[dict] | None = None,
    mutation_findings: list[dict] | None = None,
    positives: list[str] | None = None,
    supply_mutation: bool = True,
    tamper_validated_after_manifest: bool = False,
) -> tuple[str, str, int]:
    """Drive `synthesize.py` via subprocess. Returns (stdout, stderr, rc)."""
    workdir = output_dir
    workdir.mkdir(parents=True, exist_ok=True)
    scope_path = workdir / "scope.json"
    prepared_scope = json.loads(json.dumps(scope))
    diff_path = workdir / "diff.patch"
    diff_path.write_text("diff --git a/src/a.ts b/src/a.ts\n", encoding="utf-8")
    findings_path = workdir / "validated-findings.jsonl"
    _write_jsonl(findings_path, findings)
    axis_path = workdir / "axis-findings.jsonl"
    _write_jsonl(axis_path, findings)
    tool_path = workdir / "tool-findings.jsonl"
    tool_records = tool_findings or []
    _write_jsonl(tool_path, tool_records)

    if "tool_coverage" in prepared_scope:
        prepared_scope["tool_coverage"].update({
            "output": str(tool_path.resolve()),
            "sha256": _identity(tool_path)["sha256"],
            "finding_count": len(tool_records),
        })
    if "axis_coverage" in prepared_scope:
        prepared_scope["axis_coverage"].update({
            "run_id": "axis-test-run",
            "input_hashes": {
                "diff": _identity(diff_path),
                "tool_findings": _identity(tool_path),
                "mutation_findings": None,
            },
            "output": str(axis_path.resolve()),
            "sha256": _identity(axis_path)["sha256"],
            "finding_count": len(findings),
        })
    if "validator_coverage" in prepared_scope:
        prepared_scope["validator_coverage"].update({
            "run_id": "validator-test-run",
            "input_hashes": {
                "diff": _identity(diff_path),
                "axis_findings": _identity(axis_path),
            },
            "output": str(findings_path.resolve()),
            "sha256": _identity(findings_path)["sha256"],
            "finding_count": len(findings),
        })

    mutation_path: Path | None = None
    mutation_coverage = prepared_scope.get("mutation_coverage")
    if (
        isinstance(mutation_coverage, dict)
        and mutation_coverage.get("applicable") is True
        and mutation_coverage.get("complete") is True
    ):
        mutation_path = workdir / "mutation-findings.jsonl"
        mutation_records = mutation_findings or []
        _write_jsonl(mutation_path, mutation_records)
        mutation_identity = _identity(mutation_path)
        mutation_coverage.update({
            "output": str(mutation_path.resolve()),
            "sha256": mutation_identity["sha256"],
            "finding_count": len(mutation_records),
        })
        if "axis_coverage" in prepared_scope:
            prepared_scope["axis_coverage"]["input_hashes"][
                "mutation_findings"
            ] = mutation_identity

    scope_path.write_text(json.dumps(prepared_scope), encoding="utf-8")
    if tamper_validated_after_manifest:
        with findings_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(_finding(finding="Tampered after manifest")) + "\n")
    args = [
        sys.executable, str(SYNTHESIZE),
        "--scope", str(scope_path),
        "--findings", str(findings_path),
        "--slug", slug,
        "--output-dir", str(workdir),
        "--repo-root", str(repo_root or workdir),
    ]
    if save:
        args.append("--save")
    args += ["--tool-findings", str(tool_path)]
    if mutation_path is not None and supply_mutation:
        args += ["--mutation-findings", str(mutation_path)]
    if positives:
        positives_path = workdir / "positives.jsonl"
        positives_path.write_text(
            "\n".join(json.dumps({"text": t}) for t in positives) + "\n",
            encoding="utf-8",
        )
        args += ["--positives", str(positives_path)]
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    return result.stdout, result.stderr, result.returncode


def _run_synthesize_invalid_scope(
    scope_text: str,
    *,
    output_dir: Path,
) -> subprocess.CompletedProcess:
    scope_path = output_dir / "scope.json"
    findings_path = output_dir / "findings.jsonl"
    tool_path = output_dir / "tool-findings.jsonl"
    scope_path.write_text(scope_text, encoding="utf-8")
    findings_path.write_text("", encoding="utf-8")
    tool_path.write_text("", encoding="utf-8")
    return subprocess.run(
        [
            sys.executable,
            str(SYNTHESIZE),
            "--scope",
            str(scope_path),
            "--findings",
            str(findings_path),
            "--tool-findings",
            str(tool_path),
            "--output-dir",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )


# ---------------------------------------------------------------------------
# 1. Inter-axis precedence
# ---------------------------------------------------------------------------


class TestInterAxisPrecedence(unittest.TestCase):
    def test_two_axes_same_location_highest_severity_wins(self):
        """🔴 High Correctness + 🟠 Medium Style at the same file:line with
        the same finding text → Correctness wins."""
        f_correctness = _finding(
            axis="correctness", severity="High",
            location="src/a.ts:10", finding="Drift",
            confidence=90,
        )
        f_style = _finding(
            axis="style", severity="Medium",
            location="src/a.ts:10", finding="Drift",
            confidence=90,
        )
        survivors = synthesis_core.dedup_by_precedence([f_correctness, f_style])
        self.assertEqual(len(survivors), 1)
        self.assertEqual(survivors[0]["axis"], "correctness")
        self.assertEqual(survivors[0]["severity"], "High")

    def test_tie_severity_resolves_via_axis_priority(self):
        """Equal severity, different axes → AXIS_PRIORITY tie-break.
        Design/API ranks before Style; Style loses."""
        f_design = _finding(
            axis="design-api", severity="Medium",
            location="api/users.ts:5", finding="Public API rename",
            confidence=88,
        )
        f_style = _finding(
            axis="style", severity="Medium",
            location="api/users.ts:5", finding="Public API rename",
            confidence=88,
        )
        survivors = synthesis_core.dedup_by_precedence([f_style, f_design])
        self.assertEqual(len(survivors), 1)
        self.assertEqual(survivors[0]["axis"], "design-api")

    def test_distinct_finding_text_same_line_both_survive(self):
        """Different findings at the same line — say a correctness
        null-deref and a tests missing-assert — keep distinct keys so
        both survive."""
        f_correctness = _finding(
            axis="correctness", severity="High",
            location="src/a.ts:10", finding="Null deref",
            confidence=90,
        )
        f_tests = _finding(
            axis="tests", severity="Medium",
            location="src/a.ts:10", finding="Missing assert",
            confidence=85,
        )
        survivors = synthesis_core.dedup_by_precedence([f_correctness, f_tests])
        self.assertEqual(len(survivors), 2)

    def test_axis_priority_full_order(self):
        """The full priority order pins the spec: Correctness > Design/API >
        Simplification > Tests > Documentation > Style > Intent > Performance >
        Coherence."""
        expected = (
            "correctness", "design-api", "simplification", "tests",
            "documentation", "style", "intent", "performance", "coherence",
        )
        self.assertEqual(synthesis_core.AXIS_PRIORITY, expected)

    def test_findings_without_location_pass_through(self):
        """Findings with empty `location` are skipped by the deduper."""
        f1 = _finding(location="", finding="Generic note")
        f2 = _finding(location="", finding="Other generic note")
        survivors = synthesis_core.dedup_by_precedence([f1, f2])
        # Both pass through unchanged.
        self.assertEqual(len(survivors), 2)


# ---------------------------------------------------------------------------
# 2. A2 carryover — `synthesize.synthesize()` preserves Unverified
# ---------------------------------------------------------------------------


class TestA2Carryover(unittest.TestCase):
    def test_sub_80_finding_lands_in_unverified(self):
        result = synthesize.synthesize(
            _scope(),
            [_finding(confidence=65, finding="Likely null deref")],
        )
        self.assertEqual(result["verified"], [])
        self.assertEqual(len(result["unverified"]), 1)
        self.assertTrue(
            result["unverified"][0]["finding"].startswith(
                synthesis_core.UNVERIFIED_PREFIX
            )
        )

    def test_validator_reason_is_rendered_for_unverified_finding(self):
        finding = _finding(confidence=60, finding="Plausible edge case")
        finding["meta"] = {
            "validator_reason": "The contract is not established by the diff."
        }
        with tempfile.TemporaryDirectory() as tmp:
            stdout, stderr, rc = _run_synthesize(
                _scope(), [finding], output_dir=Path(tmp),
            )
        self.assertEqual(rc, 0, stderr)
        self.assertIn(
            "Validator: The contract is not established by the diff.",
            stdout,
        )

    def test_high_confidence_finding_stays_verified(self):
        result = synthesize.synthesize(
            _scope(),
            [_finding(confidence=90, severity="High")],
        )
        self.assertEqual(len(result["verified"]), 1)
        self.assertEqual(result["unverified"], [])


# ---------------------------------------------------------------------------
# 3. Verdict algorithm — surfaces in `synthesize.synthesize()` and the report
# ---------------------------------------------------------------------------


class TestVerdict(unittest.TestCase):
    def test_ship_when_no_findings(self):
        result = synthesize.synthesize(_scope(), [])
        self.assertEqual(result["verdict"]["label"], "Ship")

    def test_needs_work_when_red_important(self):
        result = synthesize.synthesize(
            _scope(),
            [_finding(severity="High", confidence=90)],
        )
        self.assertEqual(result["verdict"]["label"], "Needs work")
        self.assertIn("🔴", result["verdict"]["rationale"])

    def test_fix_then_ship_when_orange_important(self):
        result = synthesize.synthesize(
            _scope(),
            [_finding(severity="Medium", confidence=90)],
        )
        self.assertEqual(result["verdict"]["label"], "Fix-then-ship")


# ---------------------------------------------------------------------------
# 4. "What I did NOT check" — mandatory closing section
# ---------------------------------------------------------------------------


class TestWhatIDidNotCheck(unittest.TestCase):
    def test_present_when_no_tools_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            stdout, _, rc = _run_synthesize(
                _scope(), [], output_dir=Path(tmp),
            )
        self.assertEqual(rc, 0, stdout)
        self.assertIn("## 🛡️ What I did NOT check", stdout)
        self.assertIn("/security-review", stdout)
        self.assertIn("Runtime performance", stdout)
        self.assertIn("Flaky test detection", stdout)

    def test_skipped_tool_blocks_synthesis(self):
        scope = _scope(tools_skipped=[
            {"tool": "oasdiff", "axis": "design-api",
             "install": "brew install oasdiff"},
        ])
        with tempfile.TemporaryDirectory() as tmp:
            stdout, stderr, rc = _run_synthesize(
                scope, [], output_dir=Path(tmp),
            )
        self.assertEqual(rc, 4)
        self.assertEqual(stdout, "")
        self.assertIn("analyzers were skipped", stderr)
        self.assertIn("rerun the review", stderr)


# ---------------------------------------------------------------------------
# 5. Required sections — every entry in the contract appears in the report
# ---------------------------------------------------------------------------


class TestRequiredSectionsInReport(unittest.TestCase):
    def test_all_required_sections_in_minimal_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            stdout, _, rc = _run_synthesize(_scope(), [], output_dir=Path(tmp))
        self.assertEqual(rc, 0, stdout)
        for section in REVIEW["report_required_sections"]:
            self.assertIn(
                f"## {section}", stdout,
                f"section `## {section}` missing from rendered report",
            )

    def test_sections_render_in_canonical_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            stdout, _, rc = _run_synthesize(_scope(), [], output_dir=Path(tmp))
        self.assertEqual(rc, 0, stdout)
        # Line-anchored search — backticked `## 🔎 Findings` references
        # inside the blockquote prose are NOT headings.
        import re
        offsets = []
        for section in REVIEW["report_required_sections"]:
            match = re.search(
                rf"^## {re.escape(section)}\s*$", stdout, re.MULTILINE,
            )
            self.assertIsNotNone(
                match, f"section `## {section}` missing as a real heading",
            )
            offsets.append(match.start())
        self.assertEqual(offsets, sorted(offsets), "sections out of order")


# ---------------------------------------------------------------------------
# 6. Severity counts in header
# ---------------------------------------------------------------------------


class TestHeaderSeverityCounts(unittest.TestCase):
    def test_counts_match_findings(self):
        findings = [
            _finding(severity="High", confidence=90, location="a.ts:1",
                     finding="bug 1"),
            _finding(severity="High", confidence=90, location="b.ts:1",
                     finding="bug 2"),
            _finding(severity="Medium", confidence=90, location="c.ts:1",
                     finding="bug 3"),
            _finding(severity="Low", confidence=90, location="d.ts:1",
                     finding="bug 4"),
            # Sub-80 → routed to unverified.
            _finding(severity="High", confidence=70, location="e.ts:1",
                     finding="bug 5"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            stdout, _, rc = _run_synthesize(
                _scope(), findings, output_dir=Path(tmp),
            )
        self.assertEqual(rc, 0, stdout)
        self.assertIn("**Findings:** 2 🔴 · 1 🟠 · 1 🟢 (verified) · 1 unverified",
                      stdout)

    def test_empty_rules_chain_does_not_mark_style_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            stdout, _, rc = _run_synthesize(
                _scope(instruction_chain=[]), [], output_dir=Path(tmp),
            )
        self.assertEqual(rc, 0, stdout)
        self.assertIn(
            "**Rules baseline:** none — Style used observable repository conventions",
            stdout,
        )
        self.assertNotIn("Rules baseline:** skipped", stdout)

    def test_canonical_empty_chain_ignores_stale_legacy_alias(self):
        with tempfile.TemporaryDirectory() as tmp:
            stdout, _, rc = _run_synthesize(
                _scope(
                    instruction_chain=[],
                    claude_md_chain=["CLAUDE.md"],
                ),
                [],
                output_dir=Path(tmp),
            )
        self.assertEqual(rc, 0, stdout)
        self.assertIn(
            "**Rules baseline:** none — Style used observable repository conventions",
            stdout,
        )

    def test_nonempty_rules_chain_uses_generic_label(self):
        with tempfile.TemporaryDirectory() as tmp:
            stdout, _, rc = _run_synthesize(
                _scope(instruction_chain=["AGENTS.md", "CLAUDE.md"]),
                [],
                output_dir=Path(tmp),
            )
        self.assertEqual(rc, 0, stdout)
        self.assertIn("**Rules baseline:** instruction chain + 2 files", stdout)


# ---------------------------------------------------------------------------
# 7. Coherence axis state in header
# ---------------------------------------------------------------------------


class TestCoherenceAxisState(unittest.TestCase):
    def test_active_when_scope_activates(self):
        with tempfile.TemporaryDirectory() as tmp:
            stdout, _, rc = _run_synthesize(
                _scope(activates_coherence=True), [], output_dir=Path(tmp),
            )
        self.assertEqual(rc, 0, stdout)
        self.assertIn("**Coherence axis:** active", stdout)

    def test_inactive_when_scope_doesnt_activate(self):
        with tempfile.TemporaryDirectory() as tmp:
            stdout, _, rc = _run_synthesize(
                _scope(activates_coherence=False), [], output_dir=Path(tmp),
            )
        self.assertEqual(rc, 0, stdout)
        self.assertIn("**Coherence axis:** inactive", stdout)


# ---------------------------------------------------------------------------
# 8. Save-mode paths
# ---------------------------------------------------------------------------


class TestOutputPaths(unittest.TestCase):
    def test_output_dir_writes_report_md_and_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _, _, rc = _run_synthesize(
                _scope(),
                [_finding(severity="High", confidence=90)],
                output_dir=tmp_path,
            )
            self.assertEqual(rc, 0)
            md = tmp_path / "report.md"
            jsonl = tmp_path / "report.jsonl"
            self.assertTrue(md.exists())
            self.assertTrue(jsonl.exists())
            self.assertIn("## 🔎 Findings", md.read_text(encoding="utf-8"))
            # Every JSONL line parses cleanly.
            for line in jsonl.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    json.loads(line)

    def test_save_mode_writes_to_canonical_path(self):
        """`--save` lands at `~/.agents/output/<project>/code-ultrareview/
        code-ultrareview-<slug>.{md,jsonl}`. Run inside a temp git repo so
        the `<project>` slug is deterministic."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = tmp_path / "fake-project"
            repo.mkdir()
            subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
            output_root = tmp_path / "home"
            env = os.environ.copy()
            env["HOME"] = str(output_root)
            scope_path = repo / "scope.json"
            findings_path = repo / "findings.jsonl"
            findings_path.write_text(
                json.dumps(_finding(severity="High", confidence=90)) + "\n",
                encoding="utf-8",
            )
            axis_path = repo / "axis-findings.jsonl"
            axis_path.write_bytes(findings_path.read_bytes())
            tool_findings_path = repo / "tool-findings.jsonl"
            tool_findings_path.write_text("", encoding="utf-8")
            diff_path = repo / "diff.patch"
            diff_path.write_text("diff --git", encoding="utf-8")
            scope = _scope()
            scope["tool_coverage"].update({
                "output": str(tool_findings_path.resolve()),
                "sha256": _identity(tool_findings_path)["sha256"],
                "finding_count": 0,
            })
            scope["axis_coverage"].update({
                "run_id": "axis-save-run",
                "input_hashes": {
                    "diff": _identity(diff_path),
                    "tool_findings": _identity(tool_findings_path),
                    "mutation_findings": None,
                },
                "output": str(axis_path.resolve()),
                "sha256": _identity(axis_path)["sha256"],
                "finding_count": 1,
            })
            scope["validator_coverage"].update({
                "run_id": "validator-save-run",
                "input_hashes": {
                    "diff": _identity(diff_path),
                    "axis_findings": _identity(axis_path),
                },
                "output": str(findings_path.resolve()),
                "sha256": _identity(findings_path)["sha256"],
                "finding_count": 1,
            })
            scope_path.write_text(json.dumps(scope), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SYNTHESIZE),
                 "--scope", str(scope_path),
                 "--findings", str(findings_path),
                 "--tool-findings", str(tool_findings_path),
                 "--slug", "audit",
                 "--save",
                 "--repo-root", str(repo)],
                capture_output=True, text=True, env=env, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            canonical_dir = (
                output_root / ".agents" / "output" / "fake-project"
                / "code-ultrareview"
            )
            self.assertTrue((canonical_dir / "code-ultrareview-audit.md").exists())
            self.assertTrue((canonical_dir / "code-ultrareview-audit.jsonl").exists())


# ---------------------------------------------------------------------------
# Coherence axis filtering — only renders when active
# ---------------------------------------------------------------------------


class TestCoherenceRowRendering(unittest.TestCase):
    def test_coherence_row_says_inactive_when_off(self):
        with tempfile.TemporaryDirectory() as tmp:
            stdout, _, rc = _run_synthesize(
                _scope(activates_coherence=False), [], output_dir=Path(tmp),
            )
        self.assertEqual(rc, 0, stdout)
        # Axis summary table row for coherence reads "— inactive ...".
        self.assertIn(
            "| coherence | — inactive (no metadata in diff)",
            stdout,
        )


# ---------------------------------------------------------------------------
# Positives — `✅ What looks good` carries the user-provided text
# ---------------------------------------------------------------------------


class TestPositives(unittest.TestCase):
    def test_positives_render_when_provided(self):
        with tempfile.TemporaryDirectory() as tmp:
            stdout, _, rc = _run_synthesize(
                _scope(), [],
                output_dir=Path(tmp),
                positives=["Token-bucket refill correct", "Error pattern reused"],
            )
        self.assertEqual(rc, 0, stdout)
        self.assertIn("Token-bucket refill correct", stdout)
        self.assertIn("Error pattern reused", stdout)

    def test_positives_section_shows_none_when_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            stdout, _, rc = _run_synthesize(_scope(), [], output_dir=Path(tmp))
        self.assertEqual(rc, 0, stdout)
        # No positives feed → section renders with `_None surfaced this run._`.
        self.assertIn("_None surfaced this run._", stdout)


# ---------------------------------------------------------------------------
# Tool-findings input — confidence-100 findings concatenated
# ---------------------------------------------------------------------------


class TestToolFindingsConcat(unittest.TestCase):
    def test_tool_findings_appear_in_report(self):
        tool = {
            "axis": "documentation",
            "severity": "Low",
            "location": "README.md:3",
            "finding": "Trailing whitespace",
            "recommendation": "Strip trailing space",
            "confidence": 100,
            "source_tool": "markdownlint-cli2",
        }
        with tempfile.TemporaryDirectory() as tmp:
            stdout, _, rc = _run_synthesize(
                _scope(),
                [],
                output_dir=Path(tmp),
                tool_findings=[tool],
            )
        self.assertEqual(rc, 0, stdout)
        self.assertIn("Trailing whitespace", stdout)
        # Routed to 🟢 Low under Findings.
        green_offset = stdout.index("### 🟢 Low")
        next_section = stdout.index("###", green_offset + 1)
        self.assertIn("Trailing whitespace", stdout[green_offset:next_section])


# ---------------------------------------------------------------------------
# Render-layer regression — header file count + tools-skipped axis column
# ---------------------------------------------------------------------------


class TestRenderLayerRegression(unittest.TestCase):
    """Pins three render-layer bugs that slipped past the 1315-test suite.

    Each test fails if the corresponding fix is reverted:
    1. `synthesize.py:286` reading `changed_files` instead of `files_touched_list`.
    2. `run_battery.sh:673` writing `axis_lost` instead of `axis`.
    3. `synthesize.py:580` passing `--print/--no-print` as a single name to
       `argparse.BooleanOptionalAction`.
    """

    def test_header_renders_changed_file_count(self):
        """Header reads `**Reviewed:** N changed file(s)` where N matches
        `scope['files_touched_list']` length — not the absent
        `changed_files` legacy key."""
        scope = _scope(
            files_touched_list=[
                "src/a.ts", "src/b.ts", "src/c.ts",
                "src/d.ts", "src/e.ts", "src/f.ts",
                "src/g.ts",
            ],
        )
        # Make sure no `changed_files` shadow key is present — proves the
        # renderer reads from `files_touched_list`.
        scope.pop("changed_files", None)
        with tempfile.TemporaryDirectory() as tmp:
            stdout, stderr, rc = _run_synthesize(
                scope,
                [_finding()],
                output_dir=Path(tmp),
            )
        self.assertEqual(rc, 0, stderr)
        self.assertIn("**Reviewed:** 7 changed file(s)", stdout)

    def test_synthesis_blocks_when_analyzer_was_skipped(self):
        """A partial tool battery can never render a Ship verdict."""
        scope = _scope(
            tools_skipped=[{
                "tool": "oasdiff",
                "install": "brew install oasdiff",
                "axis": "design-api",
                "reason": "not found — install: brew install oasdiff",
            }],
        )
        with tempfile.TemporaryDirectory() as tmp:
            stdout, stderr, rc = _run_synthesize(
                scope,
                [_finding()],
                output_dir=Path(tmp),
            )
        self.assertEqual(rc, 4)
        self.assertEqual(stdout, "")
        self.assertIn("analyzers were skipped", stderr)
        self.assertNotIn("Ship", stderr)

    def test_synthesis_blocks_without_coverage_manifest(self):
        scope = _scope()
        scope.pop("tool_coverage")
        scope.pop("axis_coverage")
        scope.pop("validator_coverage")
        scope.pop("coverage_complete")
        with tempfile.TemporaryDirectory() as tmp:
            stdout, stderr, rc = _run_synthesize(
                scope, [], output_dir=Path(tmp),
            )
        self.assertEqual(rc, 4)
        self.assertEqual(stdout, "")
        self.assertIn("coverage manifest is not complete", stderr)

    def test_malformed_scope_fails_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            workdir = Path(tmp)
            result = _run_synthesize_invalid_scope(
                "{broken\n",
                output_dir=workdir,
            )

        self.assertEqual(result.returncode, 4)
        self.assertEqual(result.stdout, "")
        self.assertIn("cannot synthesize a verdict", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_mistyped_coverage_manifest_never_synthesizes(self):
        scope = _scope()
        scope["axis_coverage"] = "complete"
        with tempfile.TemporaryDirectory() as tmp:
            workdir = Path(tmp)
            result = _run_synthesize_invalid_scope(
                json.dumps(scope),
                output_dir=workdir,
            )

        self.assertEqual(result.returncode, 4)
        self.assertEqual(result.stdout, "")
        self.assertIn("axis review manifest missing or invalid", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_synthesis_blocks_incomplete_requested_mutation_coverage(self):
        scope = _scope(
            mutation_coverage={
                "requested": True,
                "complete": False,
                "applicable": True,
                "status": "failed",
            },
        )
        with tempfile.TemporaryDirectory() as tmp:
            stdout, stderr, rc = _run_synthesize(
                scope, [], output_dir=Path(tmp),
            )
        self.assertEqual(rc, 4)
        self.assertEqual(stdout, "")
        self.assertIn("requested mutation coverage is incomplete", stderr)
        self.assertNotIn("**Ship**", stderr)

    def test_applicable_mutation_findings_are_required(self):
        scope = _scope(
            mutation_coverage={
                "requested": True,
                "complete": True,
                "applicable": True,
                "status": "passed",
            },
        )
        with tempfile.TemporaryDirectory() as tmp:
            stdout, stderr, rc = _run_synthesize(
                scope,
                [],
                output_dir=Path(tmp),
                mutation_findings=[
                    _finding(
                        axis="tests",
                        finding="Surviving mutation",
                        location="src/a.ts:12",
                    )
                ],
                supply_mutation=False,
            )
        self.assertEqual(rc, 4)
        self.assertEqual(stdout, "")
        self.assertIn(
            "applicable mutation findings were not supplied",
            stderr,
        )
        self.assertNotIn("Ship", stderr)

    def test_applicable_mutation_finding_is_rendered(self):
        scope = _scope(
            mutation_coverage={
                "requested": True,
                "complete": True,
                "applicable": True,
                "status": "passed",
            },
        )
        mutation = _finding(
            axis="tests",
            finding="Surviving mutation",
            location="src/a.ts:12",
            recommendation="Add a test that kills this mutation",
            confidence=90,
        )
        with tempfile.TemporaryDirectory() as tmp:
            stdout, stderr, rc = _run_synthesize(
                scope,
                [],
                output_dir=Path(tmp),
                mutation_findings=[mutation],
            )
        self.assertEqual(rc, 0, stderr)
        self.assertIn("Surviving mutation", stdout)
        self.assertIn("Add a test that kills this mutation", stdout)

    def test_tampered_validated_findings_never_synthesize(self):
        with tempfile.TemporaryDirectory() as tmp:
            stdout, stderr, rc = _run_synthesize(
                _scope(),
                [_finding()],
                output_dir=Path(tmp),
                tamper_validated_after_manifest=True,
            )
        self.assertEqual(rc, 4)
        self.assertEqual(stdout, "")
        self.assertIn(
            "validated findings digest does not match its run manifest",
            stderr,
        )
        self.assertNotIn("Ship", stderr)

    def test_synthesis_blocks_incomplete_requested_reconcile_coverage(self):
        scope = _scope(
            reconcile_coverage={
                "requested": True,
                "complete": False,
                "status": "failed",
                "output": "/tmp/reconcile.json",
            },
        )
        with tempfile.TemporaryDirectory() as tmp:
            stdout, stderr, rc = _run_synthesize(
                scope, [], output_dir=Path(tmp),
            )
        self.assertEqual(rc, 4)
        self.assertEqual(stdout, "")
        self.assertIn("requested reconcile coverage is incomplete", stderr)
        self.assertNotIn("**Ship**", stderr)

    def test_missing_required_findings_file_never_synthesizes_ship(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            scope_path = tmp_path / "scope.json"
            missing = tmp_path / "missing-findings.jsonl"
            missing.write_text("", encoding="utf-8")
            axis_findings = tmp_path / "axis-findings.jsonl"
            axis_findings.write_text("", encoding="utf-8")
            tool_findings = tmp_path / "tool-findings.jsonl"
            tool_findings.write_text("", encoding="utf-8")
            diff_path = tmp_path / "diff.patch"
            diff_path.write_text("diff --git", encoding="utf-8")
            scope = _scope()
            scope["tool_coverage"].update({
                "output": str(tool_findings.resolve()),
                "sha256": _identity(tool_findings)["sha256"],
                "finding_count": 0,
            })
            scope["axis_coverage"].update({
                "run_id": "axis-missing-run",
                "input_hashes": {
                    "diff": _identity(diff_path),
                    "tool_findings": _identity(tool_findings),
                    "mutation_findings": None,
                },
                "output": str(axis_findings.resolve()),
                "sha256": _identity(axis_findings)["sha256"],
                "finding_count": 0,
            })
            scope["validator_coverage"].update({
                "run_id": "validator-missing-run",
                "input_hashes": {
                    "diff": _identity(diff_path),
                    "axis_findings": _identity(axis_findings),
                },
                "output": str(missing.resolve()),
                "sha256": _identity(missing)["sha256"],
                "finding_count": 0,
            })
            scope_path.write_text(json.dumps(scope), encoding="utf-8")
            missing.unlink()
            result = subprocess.run(
                [
                    sys.executable,
                    str(SYNTHESIZE),
                    "--scope",
                    str(scope_path),
                    "--findings",
                    str(missing),
                    "--tool-findings",
                    str(tool_findings),
                    "--output-dir",
                    str(tmp_path / "out"),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 4)
        self.assertEqual(result.stdout, "")
        self.assertIn("required findings file is missing", result.stderr)
        self.assertIn("rerun the failed axis/validator phase", result.stderr)
        self.assertNotIn("**Ship**", result.stderr)

    def test_missing_tool_findings_file_never_synthesizes_ship(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            scope_path = tmp_path / "scope.json"
            findings = tmp_path / "validated-findings.jsonl"
            findings.write_text("", encoding="utf-8")
            missing = tmp_path / "missing-tool-findings.jsonl"
            missing.write_text("", encoding="utf-8")
            axis_findings = tmp_path / "axis-findings.jsonl"
            axis_findings.write_text("", encoding="utf-8")
            diff_path = tmp_path / "diff.patch"
            diff_path.write_text("diff --git", encoding="utf-8")
            scope = _scope()
            scope["tool_coverage"].update({
                "output": str(missing.resolve()),
                "sha256": _identity(missing)["sha256"],
                "finding_count": 0,
            })
            scope["axis_coverage"].update({
                "run_id": "axis-missing-tool-run",
                "input_hashes": {
                    "diff": _identity(diff_path),
                    "tool_findings": _identity(missing),
                    "mutation_findings": None,
                },
                "output": str(axis_findings.resolve()),
                "sha256": _identity(axis_findings)["sha256"],
                "finding_count": 0,
            })
            scope["validator_coverage"].update({
                "run_id": "validator-missing-tool-run",
                "input_hashes": {
                    "diff": _identity(diff_path),
                    "axis_findings": _identity(axis_findings),
                },
                "output": str(findings.resolve()),
                "sha256": _identity(findings)["sha256"],
                "finding_count": 0,
            })
            scope_path.write_text(json.dumps(scope), encoding="utf-8")
            missing.unlink()
            result = subprocess.run(
                [
                    sys.executable,
                    str(SYNTHESIZE),
                    "--scope",
                    str(scope_path),
                    "--findings",
                    str(findings),
                    "--tool-findings",
                    str(missing),
                    "--output-dir",
                    str(tmp_path / "out"),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 4)
        self.assertEqual(result.stdout, "")
        self.assertIn("required findings file is missing", result.stderr)
        self.assertNotIn("**Ship**", result.stderr)

    def test_axis_subset_never_emits_global_ship_verdict(self):
        scope = _scope(axis_coverage={
            "complete": True,
            "full": False,
            "requested": ["correctness", "tests"],
            "completed": ["correctness", "tests"],
        })
        with tempfile.TemporaryDirectory() as tmp:
            stdout, stderr, rc = _run_synthesize(
                scope, [], output_dir=Path(tmp),
            )
        self.assertEqual(rc, 0, stderr)
        self.assertIn("**Coverage:** scoped: correctness, tests", stdout)
        self.assertIn("**Scoped findings only**", stdout)
        self.assertNotIn("Ship", stdout)
        self.assertNotIn("Fix-then-ship", stdout)
        self.assertNotIn("Needs work", stdout)

    def test_print_flag_help_is_clean(self):
        """`synthesize.py --help` exits 0; corrupted slash-syntax does not
        appear in the rendered help.

        BooleanOptionalAction passed `--print/--no-print` as a single name
        string registers a name with an embedded slash, which renders as
        `--print/--no-print, --no-print/--no-print` in the options section.
        The clean shape (single name → auto-paired) renders as
        `--print | --no-print` in usage and `--print, --no-print` (or
        separate option entries) in the options list.
        """
        result = subprocess.run(
            [sys.executable, str(SYNTHESIZE), "--help"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        help_text = result.stdout
        # Corrupted shape signature — never appears with a clean argument name.
        self.assertNotIn("--print/--no-print", help_text)
        self.assertNotIn("--no-print/--no-print", help_text)
        # Clean shape sanity check — `--print` and `--no-print` both surfaced.
        self.assertIn("--print", help_text)
        self.assertIn("--no-print", help_text)


if __name__ == "__main__":
    unittest.main()
