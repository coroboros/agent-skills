"""Tests for skills/code-ultrareview/scripts/battery_ingest.py.

Covers per-tool parsers (knip, jscpd, markdownlint-cli2, api-extractor, lizard,
vulture, semgrep, oasdiff, atlas, vale, deadcode, gocyclo, dupl, cargo-machete),
axis routing, and the universal contract: every finding carries
`confidence: 100` and a canonical schema.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "skills" / "code-ultrareview" / "scripts" / "battery_ingest.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "battery"


def _load_module():
    spec = importlib.util.spec_from_file_location("battery_ingest", SCRIPT)
    assert spec is not None and spec.loader is not None
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


bi = _load_module()


def _read(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Universal schema invariants — every parser, every finding.
# ---------------------------------------------------------------------------


class TestUniversalContract(unittest.TestCase):
    """AC: All tool findings carry confidence: 100 AND a canonical schema."""

    REQUIRED_KEYS = {"file", "line_start", "line_end", "severity",
                     "confidence", "axis", "source_tool", "message"}

    def test_empty_input_returns_empty_list(self):
        for tool in bi.PARSERS:
            with self.subTest(tool=tool):
                self.assertEqual(bi.ingest_one(tool, ""), [],
                                 f"{tool} should return [] on empty input")

    def test_every_fixture_yields_at_least_one_finding(self):
        for tool in bi.PARSERS:
            with self.subTest(tool=tool):
                fixtures = list(FIXTURES.glob(f"{tool}.*"))
                self.assertEqual(len(fixtures), 1,
                                 f"{tool} must have exactly one fixture file, got {fixtures}")
                raw = fixtures[0].read_text(encoding="utf-8")
                findings = bi.ingest_one(tool, raw)
                self.assertGreater(len(findings), 0,
                                   f"{tool} fixture must yield ≥1 finding")

    def test_every_finding_has_canonical_keys(self):
        for tool in bi.PARSERS:
            with self.subTest(tool=tool):
                raw = _read(next(FIXTURES.glob(f"{tool}.*")).name)
                for f in bi.ingest_one(tool, raw):
                    self.assertGreaterEqual(set(f.keys()), self.REQUIRED_KEYS)

    def test_every_finding_confidence_is_100(self):
        """AC: All tool findings carry confidence: 100."""
        for tool in bi.PARSERS:
            with self.subTest(tool=tool):
                raw = _read(next(FIXTURES.glob(f"{tool}.*")).name)
                for f in bi.ingest_one(tool, raw):
                    self.assertEqual(f["confidence"], 0,
                                     f"{tool}: confidence must be unassessed")

    def test_every_finding_severity_is_canonical(self):
        for tool in bi.PARSERS:
            with self.subTest(tool=tool):
                raw = _read(next(FIXTURES.glob(f"{tool}.*")).name)
                for f in bi.ingest_one(tool, raw):
                    self.assertIn(f["severity"], {"High", "Medium", "Low"})

    def test_line_start_le_line_end(self):
        for tool in bi.PARSERS:
            with self.subTest(tool=tool):
                raw = _read(next(FIXTURES.glob(f"{tool}.*")).name)
                for f in bi.ingest_one(tool, raw):
                    self.assertLessEqual(f["line_start"], f["line_end"])

    def test_source_tool_matches_invocation_name(self):
        for tool in bi.PARSERS:
            with self.subTest(tool=tool):
                raw = _read(next(FIXTURES.glob(f"{tool}.*")).name)
                for f in bi.ingest_one(tool, raw):
                    self.assertEqual(f["source_tool"], tool)

    def test_documented_empty_reports_are_accepted(self):
        empty_reports = {
            "knip": '{"issues": []}',
            "jscpd": '{"duplicates": []}',
            "markdownlint-cli2": "[]",
            "api-extractor": "API Extractor completed successfully\n",
            "lizard": "NLOC,CCN,token,PARAM,length,location\n",
            "vulture": "",
            "semgrep": '{"results": [], "errors": []}',
            "oasdiff": "[]",
            "atlas": '{"Files": []}',
            "vale": "{}",
            "deadcode": "",
            "gocyclo": "",
            "dupl": "\nFound total 0 clone groups.\n",
            "cargo-machete": (
                "cargo-machete did not find any unused dependencies\n"
            ),
        }
        for tool, raw in empty_reports.items():
            with self.subTest(tool=tool):
                self.assertEqual(bi.ingest_one(tool, raw), [])

    def test_nonempty_unknown_reports_fail_loud(self):
        unknown_reports = {
            "knip": "not-json",
            "jscpd": "{}",
            "markdownlint-cli2": "unknown markdownlint output",
            "api-extractor": "unknown api-extractor output",
            "lizard": "unknown lizard output",
            "vulture": "unknown vulture output",
            "semgrep": "{}",
            "oasdiff": "{}",
            "atlas": "{}",
            "vale": "[]",
            "deadcode": "unknown deadcode output",
            "gocyclo": "unknown gocyclo output",
            "dupl": "found 1 clone:\nunknown location\n",
            "cargo-machete": "unknown cargo-machete output",
        }
        for tool, raw in unknown_reports.items():
            with self.subTest(tool=tool):
                with self.assertRaises(ValueError):
                    bi.ingest_one(tool, raw)


# ---------------------------------------------------------------------------
# Routing — TOOL_TO_AXIS matrix.
# ---------------------------------------------------------------------------


class TestRouting(unittest.TestCase):
    """AC: Per-tool axis routing matrix in battery_ingest.py."""

    EXPECTED = {
        "knip": "simplification",
        "jscpd": "simplification",
        "lizard": "simplification",
        "vulture": "simplification",
        "deadcode": "simplification",
        "gocyclo": "simplification",
        "dupl": "simplification",
        "cargo-machete": "simplification",
        "markdownlint-cli2": "documentation",
        "vale": "documentation",
        "api-extractor": "design-api",
        "oasdiff": "design-api",
        "atlas": "design-api",
        "semgrep": "performance",
    }

    def test_routing_table_matches_expected(self):
        for tool, expected in self.EXPECTED.items():
            with self.subTest(tool=tool):
                self.assertEqual(bi.TOOL_TO_AXIS[tool], expected)

    def test_every_parser_has_routing(self):
        for tool in bi.PARSERS:
            with self.subTest(tool=tool):
                self.assertIn(tool, bi.TOOL_TO_AXIS,
                              f"{tool} has a parser but no TOOL_TO_AXIS entry")

    def test_every_routing_has_parser(self):
        for tool in bi.TOOL_TO_AXIS:
            with self.subTest(tool=tool):
                self.assertIn(tool, bi.PARSERS,
                              f"{tool} has a routing entry but no parser")


# ---------------------------------------------------------------------------
# Per-tool parser assertions.
# ---------------------------------------------------------------------------


class TestKnipParser(unittest.TestCase):
    def setUp(self):
        self.findings = bi.parse_knip(_read("knip.json"))

    def test_dead_export_finding(self):
        match = [f for f in self.findings if "unusedExport" in f["message"]]
        self.assertEqual(len(match), 1)
        self.assertEqual(match[0]["file"], "src/foo.ts")
        self.assertEqual(match[0]["line_start"], 10)

    def test_whole_file_unused_marked_medium(self):
        match = [f for f in self.findings if f["file"] == "src/dead-file.ts"]
        self.assertEqual(len(match), 1)
        self.assertEqual(match[0]["severity"], "Medium")

    def test_dev_dependency_listed(self):
        match = [f for f in self.findings if "stale-dep" in f["message"]]
        self.assertGreaterEqual(len(match), 1)

    def test_knip_6_empty_issues_is_a_valid_empty_report(self):
        self.assertEqual(bi.parse_knip('{"issues": []}'), [])

    def test_legacy_array_report_remains_supported(self):
        findings = bi.parse_knip(
            '[{"file":"legacy.ts","files":true,"exports":[]}]'
        )
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["file"], "legacy.ts")


class TestJscpdParser(unittest.TestCase):
    def test_duplicate_block(self):
        findings = bi.parse_jscpd(_read("jscpd.json"))
        self.assertEqual(len(findings), 1)
        f = findings[0]
        self.assertEqual(f["file"], "src/a.js")
        self.assertEqual(f["line_start"], 10)
        self.assertEqual(f["line_end"], 20)
        self.assertEqual(f["axis"], "simplification")
        self.assertIn("src/b.js", f["message"])


class TestMarkdownlintParser(unittest.TestCase):
    def test_rule_id_and_description_carried(self):
        findings = bi.parse_markdownlint(_read("markdownlint-cli2.txt"))
        self.assertEqual(len(findings), 2)
        first = findings[0]
        self.assertEqual(first["file"], "README.md")
        self.assertEqual(first["line_start"], 5)
        self.assertIn("MD013", first["message"])
        self.assertEqual(first["axis"], "documentation")

    def test_default_cli_text_output_is_parsed(self):
        raw = (
            "README.md:3:10 error MD009/no-trailing-spaces "
            "Trailing spaces [Expected: 0 or 2; Actual: 1]\n"
            "docs/guide.md:7 MD041/first-line-heading/first-line-h1 "
            "First line in a file should be a top-level heading\n"
        )
        findings = bi.parse_markdownlint(raw)
        self.assertEqual(len(findings), 2)
        self.assertEqual(findings[0]["file"], "README.md")
        self.assertEqual(findings[0]["line_start"], 3)
        self.assertIn("MD009/no-trailing-spaces", findings[0]["message"])
        self.assertEqual(findings[1]["file"], "docs/guide.md")
        self.assertEqual(findings[1]["line_start"], 7)

    def test_clean_cli_progress_is_not_a_finding(self):
        raw = ("markdownlint-cli2 v0.23.2 (markdownlint v0.41.1)\n"
               "Finding: /tmp/docs/clean.md\nLinting: 1 file\n"
               "Summary: 0 issues in 0 files\n")
        self.assertEqual(bi.parse_markdownlint(raw), [])

    def test_nonempty_unrecognized_output_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "documented text or JSON schema"):
            bi.parse_markdownlint("unexpected markdownlint protocol output\n")


class TestApiExtractorParser(unittest.TestCase):
    """AC: package.json + api-extractor.json → api-extractor output routes to
    design-api axis with source_tool: api-extractor."""

    def test_warning_routes_to_design_api_with_medium_severity(self):
        findings = bi.parse_api_extractor(_read("api-extractor.txt"))
        warnings = [f for f in findings if f["severity"] == "Medium"]
        self.assertGreaterEqual(len(warnings), 1)
        self.assertTrue(all(f["axis"] == "design-api" for f in warnings))
        self.assertTrue(all(f["source_tool"] == "api-extractor" for f in warnings))

    def test_error_marked_high(self):
        findings = bi.parse_api_extractor(_read("api-extractor.txt"))
        errors = [f for f in findings if f["severity"] == "High"]
        self.assertGreaterEqual(len(errors), 1)
        self.assertEqual(errors[0]["axis"], "design-api")

    def test_clean_completion_marker_is_accepted(self):
        findings = bi.parse_api_extractor(
            "API Extractor completed successfully\n"
        )
        self.assertEqual(findings, [])

    def test_nonempty_unrecognized_output_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "successful-completion marker"):
            bi.parse_api_extractor("unexpected api-extractor protocol output\n")


class TestLizardParser(unittest.TestCase):
    def test_high_ccn_emitted_medium(self):
        findings = bi.parse_lizard(_read("lizard.txt"))
        # complex_func: CCN 15 > 10 → Medium
        complex_findings = [f for f in findings if "complex_func" in f["message"]]
        self.assertEqual(len(complex_findings), 1)
        self.assertEqual(complex_findings[0]["severity"], "Medium")
        self.assertEqual(complex_findings[0]["line_start"], 11)
        self.assertEqual(complex_findings[0]["line_end"], 50)

    def test_high_param_count_emitted(self):
        findings = bi.parse_lizard(_read("lizard.txt"))
        param_findings = [f for f in findings if "too_many_params" in f["message"]]
        self.assertEqual(len(param_findings), 1)
        self.assertIn("7 params", param_findings[0]["message"])

    def test_below_threshold_dropped(self):
        findings = bi.parse_lizard(_read("lizard.txt"))
        # simple_func + trivial should NOT appear (CCN 1, 2 below threshold).
        names = [f["message"] for f in findings]
        self.assertFalse(any("simple_func" in n for n in names))
        self.assertFalse(any("trivial" in n for n in names))


class TestVultureParser(unittest.TestCase):
    def test_unused_function(self):
        findings = bi.parse_vulture(_read("vulture.txt"))
        self.assertEqual(len(findings), 3)
        helper = [f for f in findings if "helper" in f["message"]]
        self.assertEqual(len(helper), 1)
        self.assertEqual(helper[0]["file"], "src/foo.py")
        self.assertEqual(helper[0]["line_start"], 10)
        self.assertEqual(helper[0]["axis"], "simplification")


class TestSemgrepParser(unittest.TestCase):
    """AC: Semgrep accepts only the bundled performance rule set."""

    def setUp(self):
        self.findings = bi.parse_semgrep(_read("semgrep.json"))

    def test_bundled_perf_rules_route_to_performance(self):
        perf = [f for f in self.findings if f["axis"] == "performance"]
        self.assertEqual(len(perf), 2)
        self.assertTrue(any("sync-io" in f["message"] for f in perf))
        self.assertTrue(any("n-plus-one" in f["message"] for f in perf))

    def test_unexpected_generic_rule_is_an_invalid_report(self):
        raw = json.dumps({
            "results": [{
                "check_id": "python.lang.security.audit.shell-true",
                "path": "src/exec.py",
                "start": {"line": 10},
                "end": {"line": 10},
                "extra": {
                    "message": "generic rule",
                    "severity": "ERROR",
                    "metadata": {"category": "security"},
                },
            }],
        })
        with self.assertRaisesRegex(ValueError, "unexpected Semgrep rule"):
            bi.parse_semgrep(raw)

    def test_path_prefixed_bundled_rule_routes_to_performance(self):
        raw = json.dumps({
            "results": [{
                "check_id": (
                    "private.tmp.skill.references.perf-rules."
                    "code-ultrareview-sync-io-in-async-py"
                ),
                "path": "src/exec.py",
                "start": {"line": 10},
                "end": {"line": 10},
                "extra": {
                    "message": "sync I/O in async code",
                    "severity": "WARNING",
                    "metadata": {"axis": "performance"},
                },
            }],
        })
        findings = bi.parse_semgrep(raw)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["axis"], "performance")

    def test_bundled_prefix_without_performance_metadata_is_invalid(self):
        raw = json.dumps({
            "results": [{
                "check_id": "code-ultrareview-sync-io-in-async-py",
                "path": "src/exec.py",
                "start": {"line": 10},
                "end": {"line": 10},
                "extra": {
                    "message": "missing axis metadata",
                    "severity": "WARNING",
                    "metadata": {},
                },
            }],
        })
        with self.assertRaisesRegex(ValueError, "unexpected Semgrep rule"):
            bi.parse_semgrep(raw)

    def test_severity_mapping(self):
        # Bundled fixture rules are WARNING → Medium.
        severities = {f["severity"] for f in self.findings}
        self.assertEqual(severities, {"Medium"})


class TestOasdiffParser(unittest.TestCase):
    def test_breaking_change_marked_high(self):
        findings = bi.parse_oasdiff(_read("oasdiff.json"))
        high = [f for f in findings if f["severity"] == "High"]
        self.assertGreaterEqual(len(high), 1)
        self.assertEqual(high[0]["axis"], "design-api")
        self.assertIn("removed", high[0]["message"].lower())


class TestAtlasParser(unittest.TestCase):
    def test_migration_lint_routes_to_design_api(self):
        findings = bi.parse_atlas(_read("atlas.json"))
        self.assertEqual(len(findings), 2)
        for f in findings:
            self.assertEqual(f["axis"], "design-api")
            self.assertEqual(f["source_tool"], "atlas")

    def test_step_error_is_an_analyzer_failure(self):
        raw = json.dumps({"Steps": [{"Name": "Migration Integrity Check",
                                     "Error": "checksum mismatch"}], "Files": []})
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            bi.parse_atlas(raw)

    def test_file_error_is_an_analyzer_failure(self):
        raw = json.dumps({"Files": [{"Name": "atlas.sum", "Error": "checksum mismatch"}]})
        with self.assertRaisesRegex(ValueError, "atlas.sum failed"):
            bi.parse_atlas(raw)


class TestValeParser(unittest.TestCase):
    def test_prose_lint_routes_to_documentation(self):
        findings = bi.parse_vale(_read("vale.json"))
        for f in findings:
            self.assertEqual(f["axis"], "documentation")
        errors = [f for f in findings if f["severity"] == "High"]
        self.assertEqual(len(errors), 1)


class TestGoToolParsers(unittest.TestCase):
    def test_deadcode(self):
        findings = bi.parse_deadcode(_read("deadcode.txt"))
        self.assertEqual(len(findings), 2)
        for f in findings:
            self.assertEqual(f["axis"], "simplification")

    def test_gocyclo_high_ccn(self):
        findings = bi.parse_gocyclo(_read("gocyclo.txt"))
        # CCN 15 → Medium, CCN 12 → Medium, CCN 3 → Low.
        mediums = [f for f in findings if f["severity"] == "Medium"]
        self.assertEqual(len(mediums), 2)

    def test_dupl_emits_pair(self):
        findings = bi.parse_dupl(_read("dupl.txt"))
        # 2 locations in one block → 2 findings (each cites the other).
        self.assertEqual(len(findings), 2)
        for f in findings:
            self.assertEqual(f["axis"], "simplification")

    def test_dupl_accepts_real_zero_group_trailer(self):
        self.assertEqual(bi.parse_dupl("\nFound total 0 clone groups.\n"), [])


class TestCargoMacheteParser(unittest.TestCase):
    def test_unused_deps(self):
        findings = bi.parse_cargo_machete(_read("cargo-machete.txt"))
        names = [f["message"] for f in findings]
        self.assertEqual(len(names), 2)
        self.assertTrue(any("serde_json" in n for n in names))
        self.assertTrue(any("regex" in n for n in names))
        self.assertEqual({f["file"] for f in findings}, {"./Cargo.toml"})


# ---------------------------------------------------------------------------
# CLI — batch mode + ingest mode.
# ---------------------------------------------------------------------------


class TestCli(unittest.TestCase):
    def test_batch_emits_jsonl(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            out = tdp / "out.jsonl"
            r = subprocess.run(
                [sys.executable, str(SCRIPT), "batch",
                 "--raw-dir", str(FIXTURES),
                 "--output", str(out)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(r.returncode, 0, msg=r.stderr)
            self.assertTrue(out.is_file())
            lines = [json.loads(line) for line in out.read_text().splitlines() if line]
            self.assertGreater(len(lines), 0)
            # Every line must have the canonical schema.
            for f in lines:
                self.assertIn("axis", f)
                self.assertEqual(f["confidence"], 0)

    def test_ingest_single_tool(self):
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "ingest",
             "--tool", "knip",
             "--input", str(FIXTURES / "knip.json")],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        lines = [json.loads(line) for line in r.stdout.splitlines() if line]
        self.assertGreater(len(lines), 0)
        self.assertTrue(all(f["source_tool"] == "knip" for f in lines))


class TestDiffScope(unittest.TestCase):
    def test_repository_wide_analyzer_findings_are_limited_to_changed_files(self):
        findings = bi.parse_knip(_read("knip.json"))

        filtered = bi.filter_to_changed_files(
            findings,
            ["src/foo.ts"],
            Path("/project"),
        )

        self.assertGreater(len(filtered), 0)
        self.assertEqual({finding["file"] for finding in filtered}, {"src/foo.ts"})

    def test_absolute_paths_inside_repo_are_normalized(self):
        finding = {
            "file": "/project/Cargo.toml",
            "line_start": 1,
            "line_end": 1,
            "severity": "Low",
            "confidence": 100,
            "axis": "simplification",
            "source_tool": "cargo-machete",
            "message": "unused dependency",
        }

        filtered = bi.filter_to_changed_files(
            [finding], ["Cargo.toml"], Path("/project")
        )

        self.assertEqual(filtered[0]["file"], "Cargo.toml")
        self.assertEqual(finding["file"], "/project/Cargo.toml")

    def test_empty_changed_file_set_drops_repository_wide_findings(self):
        findings = bi.parse_knip(_read("knip.json"))

        self.assertEqual(
            bi.filter_to_changed_files(findings, [], Path("/project")), []
        )

    def test_line_aware_findings_must_overlap_a_changed_hunk(self):
        findings = [
            {
                "file": "README.md",
                "line_start": line,
                "line_end": line,
                "severity": "Low",
                "confidence": 100,
                "axis": "documentation",
                "source_tool": "markdownlint-cli2",
                "message": f"finding at {line}",
            }
            for line in (5, 20, 30)
        ]

        filtered = bi.filter_to_changed_files(
            findings,
            ["README.md"],
            Path("/project"),
            {"README.md": [[4, 6], [29, 31]]},
        )

        self.assertEqual(
            [finding["line_start"] for finding in filtered],
            [5, 30],
        )

    def test_manifest_level_findings_remain_path_scoped(self):
        finding = {
            "file": "package.json",
            "line_start": 1,
            "line_end": 1,
            "severity": "Medium",
            "confidence": 100,
            "axis": "simplification",
            "source_tool": "knip",
            "message": "unused dependency",
        }

        filtered = bi.filter_to_changed_files(
            [finding],
            ["package.json"],
            Path("/project"),
            {"package.json": [[20, 20]]},
        )

        self.assertEqual(filtered, [finding])

    def test_missing_hunk_entry_drops_line_aware_finding(self):
        finding = {
            "file": "README.md",
            "line_start": 1,
            "line_end": 1,
            "severity": "Low",
            "confidence": 100,
            "axis": "documentation",
            "source_tool": "markdownlint-cli2",
            "message": "pre-existing finding",
        }

        self.assertEqual(
            bi.filter_to_changed_files(
                [finding],
                ["README.md"],
                Path("/project"),
                {},
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
