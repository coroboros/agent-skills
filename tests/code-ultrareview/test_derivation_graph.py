"""Tests for the derivation lens (skills/code-ultrareview/scripts/derivation/).

The derivation lens reconciles planning artifacts (forge, spec, apex
plan, PR body, issue body) against the diff. The Python orchestrator owns
deterministic structure extraction; LLM-driven classification happens in
the dispatched Explore subagent at runtime. Tests assert the Python
shape — what gets extracted, how freshness caps severity, how the
`.derivation-ignore` allowlist suppresses findings, how `@auto` resolves
to the conventional set.

`gh` calls are disabled via `DERIVATION_SKIP_GH=1` so fixtures behave
identically regardless of the runner's GitHub auth state.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DERIVATION_DIR = REPO_ROOT / "skills" / "code-ultrareview" / "scripts" / "derivation"
RUN_SCRIPT = DERIVATION_DIR / "run.py"
FIXTURES = REPO_ROOT / "tests" / "code-ultrareview" / "fixtures" / "derivation"

_SCRIPTS_DIR = DERIVATION_DIR.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from derivation import (  # noqa: E402
    _common,
    auto_detect,
    extractor,
    run as run_module,
)


def _env() -> dict:
    env = os.environ.copy()
    env["DERIVATION_SKIP_GH"] = "1"
    return env


def _run_cli_process(repo: Path, reconcile: str = "@auto", *extra: str):
    with tempfile.TemporaryDirectory() as td:
        runtime = Path(td)
        scope = runtime / "scope.json"
        output = runtime / "reconcile.json"
        scope.write_text("{}\n", encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(RUN_SCRIPT), "--repo", str(repo),
             "--scope", str(scope), "--output", str(output),
             "--reconcile", reconcile, *extra],
            env=_env(), capture_output=True, text=True, timeout=15,
        )


def _run_cli(repo: Path, reconcile: str = "@auto", *extra: str) -> dict:
    r = _run_cli_process(repo, reconcile, *extra)
    if r.returncode != 0:
        raise AssertionError(f"run.py exit {r.returncode}: {r.stderr}")
    return json.loads(r.stdout)


class TestExtractor(unittest.TestCase):
    def test_extracts_ac_items(self):
        md = (
            "# Spec\n\n"
            "## Acceptance criteria\n\n"
            "- [ ] AC1: thing works\n"
            "- [x] AC2: other thing works\n"
            "- not an AC (no checkbox)\n"
        )
        claims = extractor.extract_claims(md)
        kinds = [c.kind for c in claims]
        self.assertEqual(kinds, ["ac", "ac"])
        self.assertIn("AC1", claims[0].text)
        self.assertIn("AC2", claims[1].text)

    def test_extracts_goals(self):
        md = (
            "## Goals\n\n"
            "- **G1** — first goal here\n"
            "- **G2** — second goal here\n"
        )
        claims = extractor.extract_claims(md)
        self.assertEqual(len(claims), 2)
        self.assertEqual(claims[0].kind, "goal")
        self.assertIn("first goal", claims[0].text)

    def test_extracts_decisions(self):
        md = (
            "## Decisions resolved\n\n"
            "- **Topology**: single skill, replace outright.\n"
            "- **Default mode**: always full pass.\n"
        )
        claims = extractor.extract_claims(md)
        self.assertEqual(len(claims), 2)
        self.assertEqual(claims[0].kind, "decision")

    def test_section_boundary_closes_state(self):
        md = (
            "## Acceptance criteria\n\n"
            "- [ ] AC1\n"
            "\n"
            "## Other section\n\n"
            "- [ ] not-an-ac\n"
        )
        claims = extractor.extract_claims(md)
        self.assertEqual(len(claims), 1)
        self.assertEqual(claims[0].text, "AC1")

    def test_detect_artifact_kind_from_filename(self):
        self.assertEqual(extractor.detect_artifact_kind("forge-foo.md"), "forge")
        self.assertEqual(extractor.detect_artifact_kind("spec-bar.md"), "spec")
        self.assertEqual(extractor.detect_artifact_kind("/proj/docs/rfcs/0001-foo.md"), "rfc")
        self.assertEqual(extractor.detect_artifact_kind("/proj/docs/adr/0001-x.md"), "adr")
        self.assertEqual(extractor.detect_artifact_kind("README.md"), "doc")


class TestFreshness(unittest.TestCase):
    def test_freshness_unknown_returns_negative(self):
        with tempfile.TemporaryDirectory() as t:
            missing = Path(t) / "no-such-file.md"
            self.assertEqual(_common.freshness_days(missing), -1)

    def test_freshness_from_mtime(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "file.md"
            p.write_text("hi", encoding="utf-8")
            # Just-created file → 0 days.
            self.assertEqual(_common.freshness_days(p), 0)

    def test_classify_severity_by_freshness_caps_at_low(self):
        self.assertEqual(_common.classify_severity_by_freshness("High", 45), "Low")
        self.assertEqual(_common.classify_severity_by_freshness("Medium", 31), "Low")
        self.assertEqual(_common.classify_severity_by_freshness("High", 30), "High")
        self.assertEqual(_common.classify_severity_by_freshness("Medium", 0), "Medium")
        self.assertEqual(_common.classify_severity_by_freshness("Medium", -1), "Medium")

    def test_should_emit_findings(self):
        self.assertTrue(_common.should_emit_findings(0))
        self.assertTrue(_common.should_emit_findings(89))
        self.assertTrue(_common.should_emit_findings(90))
        self.assertFalse(_common.should_emit_findings(91))
        self.assertTrue(_common.should_emit_findings(-1))


class TestIgnoreFileParser(unittest.TestCase):
    def test_empty_when_file_missing(self):
        with tempfile.TemporaryDirectory() as t:
            ig = _common.load_ignore(Path(t))
        self.assertEqual(ig.data, {})

    def test_parses_nested_lists(self):
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / ".derivation-ignore").write_text(
                "paths:\n"
                "  ignore_paths:\n"
                "    - ~/.agents/output/x/spec/spec-legacy.md\n"
                "    - spec-temp.md\n"
                "claims:\n"
                "  ignore_text:\n"
                "    - out of scope\n",
                encoding="utf-8",
            )
            ig = _common.load_ignore(Path(t))
        self.assertEqual(
            ig.list_for("paths", "ignore_paths"),
            ["~/.agents/output/x/spec/spec-legacy.md", "spec-temp.md"],
        )
        self.assertTrue(ig.has("claims", "ignore_text", "out of scope"))

    def test_malformed_raises(self):
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / ".derivation-ignore").write_text(
                "paths:\n  ignore_paths\n    - foo\n", encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                _common.load_ignore(Path(t))


class TestAutoDetect(unittest.TestCase):
    def test_project_name_kebabs_repo_basename(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertTrue(auto_detect.project_name(Path(t)))

    def test_auto_detect_returns_empty_when_no_sources(self):
        with tempfile.TemporaryDirectory() as t:
            os.environ["DERIVATION_SKIP_GH"] = "1"
            repo = Path(t)
            artifacts = auto_detect.auto_detect(repo)
            # gh skipped; HOME may resolve elsewhere — at minimum no docs/ in tempdir → empty or only home-based
            # We just assert no crash and a list result.
            self.assertIsInstance(artifacts, list)

    def test_docs_artifacts_glob(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "docs" / "rfcs").mkdir(parents=True)
            (repo / "docs" / "rfcs" / "0001-foo.md").write_text("# RFC\n", encoding="utf-8")
            (repo / "docs" / "design" / "subdir").mkdir(parents=True)
            (repo / "docs" / "design" / "alpha.md").write_text("# design\n", encoding="utf-8")
            artifacts = auto_detect.docs_artifacts(repo)
        kinds = sorted({a.kind for a in artifacts})
        self.assertIn("rfc", kinds)
        self.assertIn("design", kinds)
        self.assertEqual(len(artifacts), 2)


class TestRunResolveInputs(unittest.TestCase):
    def test_explicit_path_resolves_to_artifact(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            f = repo / "spec-foo.md"
            f.write_text("# spec\n\n## Acceptance criteria\n\n- [ ] AC1\n", encoding="utf-8")
            artifacts = run_module.resolve_inputs(repo, [str(f)])
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0].kind, "spec")
        self.assertTrue(artifacts[0].required)

    def test_directory_resolves_to_each_md(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            d = repo / "plans"
            d.mkdir()
            (d / "a.md").write_text("# a", encoding="utf-8")
            (d / "b.md").write_text("# b", encoding="utf-8")
            artifacts = run_module.resolve_inputs(repo, [str(d)])
        self.assertEqual(len(artifacts), 2)

    def test_missing_explicit_path_is_a_prerequisite_error(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            with self.assertRaises(run_module.ReconcilePrerequisiteError):
                run_module.resolve_inputs(repo, ["missing-spec.md"])

    def test_empty_explicit_directory_is_a_prerequisite_error(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            plans = repo / "plans"
            plans.mkdir()
            with self.assertRaises(run_module.ReconcilePrerequisiteError):
                run_module.resolve_inputs(repo, [str(plans)])

    def test_issue_url_resolves_to_gh_issue_token(self):
        with tempfile.TemporaryDirectory() as t:
            url = "https://github.com/foo/bar/issues/42"
            artifacts = run_module.resolve_inputs(Path(t), [url])
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0].kind, "issue-body")
        self.assertIn("foo/bar#42", artifacts[0].path)


class TestRunOrchestratorFixtures(unittest.TestCase):
    def setUp(self):
        os.environ["DERIVATION_SKIP_GH"] = "1"

    def test_gap_fixture_emits_unclassified_finding(self):
        out = _run_cli(FIXTURES / "gap", reconcile=str(FIXTURES / "gap" / "spec.md"))
        self.assertEqual(out["lens"], "derivation")
        self.assertGreaterEqual(len(out["findings"]), 1)
        self.assertEqual(out["findings"][0]["classification"], "UNCLASSIFIED")
        self.assertEqual(out["findings"][0]["lens"], "derivation")

    def test_consistent_fixture_shape(self):
        # The Python stage cannot tell GAP from CONSISTENT — that's the
        # subagent's job. Just assert the artifact + claims surface.
        out = _run_cli(FIXTURES / "consistent",
                       reconcile=str(FIXTURES / "consistent" / "spec.md"))
        self.assertEqual(out["lens"], "derivation")
        self.assertGreaterEqual(len(out["artifacts"]), 1)
        self.assertGreaterEqual(out["artifacts"][0]["claim_count"], 1)

    def test_auto_detected_sources_without_claims_block(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            rfc = repo / "docs" / "rfcs" / "0001-notes.md"
            rfc.parent.mkdir(parents=True)
            rfc.write_text(
                "# Notes\n\nThis document has no planning claims.\n",
                encoding="utf-8",
            )

            result = _run_cli_process(repo, "@auto")

        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertIn("no extractable Acceptance criteria", result.stderr)
        self.assertIn("repair the planning artifact", result.stderr)

    def test_stale_explicit_artifact_still_emits_claims(self):
        # Copy the committed fixture into a non-git tempdir so freshness
        # falls back to mtime (the committed file's git timestamp is
        # recent and would otherwise override our backdate).
        import shutil
        import time as _time
        src = FIXTURES / "stale-artifact" / "spec.md"
        if not src.exists():
            self.skipTest("fixture missing")
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            dst = repo / "spec.md"
            shutil.copy(src, dst)
            ancient = _time.time() - (100 * 86400)
            os.utime(dst, (ancient, ancient))
            out = _run_cli(repo, str(dst))
        self.assertEqual(len(out["artifacts"]), 1)
        self.assertGreaterEqual(len(out["findings"]), 1)
        self.assertTrue(all(item["severity"] == "Low" for item in out["findings"]))

    def test_explicit_source_without_extractable_claims_blocks(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            source = repo / "notes.md"
            source.write_text("# Notes\n\nNothing actionable.\n", encoding="utf-8")
            result = _run_cli_process(repo, str(source))
        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertIn("contains no extractable", result.stderr)
        self.assertIn("then rerun Code Ultrareview", result.stderr)

    def test_unclosed_frontmatter_blocks(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            source = repo / "spec.md"
            source.write_text(
                "---\ntitle: Broken\n## Acceptance criteria\n- [ ] Works\n",
                encoding="utf-8",
            )
            result = _run_cli_process(repo, str(source))
        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertIn("unclosed frontmatter", result.stderr)

    def test_explicit_pr_unavailable_blocks_with_auth_remediation(self):
        with tempfile.TemporaryDirectory() as t:
            result = _run_cli_process(Path(t), "@pr")
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertIn("source is unavailable or empty", result.stderr)
        self.assertIn("gh auth login", result.stderr)
        self.assertIn("same --reconcile value", result.stderr)

    def test_allowlisted_path_suppresses_findings(self):
        fixture = FIXTURES / "allowlisted"
        out = _run_cli(fixture, reconcile=str(fixture / "spec.md"))
        # The spec.md path is allowlisted by .derivation-ignore → no findings.
        self.assertEqual(out["findings"], [])

    def test_scope_add_and_decision_override_shapes(self):
        # Same as consistent — Python emits UNCLASSIFIED; subagent classifies.
        for case in ("scope-add", "decision-override"):
            with self.subTest(case=case):
                fixture = FIXTURES / case
                spec_path = fixture / "spec.md"
                if not spec_path.exists():
                    continue
                out = _run_cli(fixture, reconcile=str(spec_path))
                self.assertEqual(out["lens"], "derivation")


class TestRunOutputSchema(unittest.TestCase):
    def test_auto_without_any_source_blocks_instead_of_no_op(self):
        with tempfile.TemporaryDirectory() as t:
            result = _run_cli_process(Path(t), reconcile="@auto")
            self.assertEqual(result.returncode, 3, result.stderr)
            self.assertIn("@auto found no planning artifact", result.stderr)

    def test_cli_persists_hashed_complete_coverage_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            spec = repo / "spec.md"
            spec.write_text(
                "# Spec\n\n## Goals\n\n- Preserve the contract\n",
                encoding="utf-8",
            )
            scope = repo / "scope.json"
            scope.write_text("{}\n", encoding="utf-8")
            output = repo / "reconcile.json"
            result = subprocess.run(
                [
                    sys.executable, str(RUN_SCRIPT),
                    "--repo", str(repo),
                    "--scope", str(scope),
                    "--output", str(output),
                    "--reconcile", str(spec),
                ],
                env=_env(), capture_output=True, text=True, timeout=15,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            coverage = json.loads(scope.read_text())["reconcile_coverage"]
            self.assertTrue(coverage["complete"])
            self.assertEqual(coverage["status"], "complete")
            self.assertEqual(coverage["output"], str(output.resolve()))
            self.assertEqual(
                coverage["sha256"], hashlib.sha256(output.read_bytes()).hexdigest()
            )
            self.assertEqual(coverage["finding_count"], 1)
            self.assertEqual(json.loads(result.stdout), json.loads(output.read_text()))

    def test_finding_carries_required_fields(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            f = repo / "spec-x.md"
            f.write_text(
                "# spec\n\n## Acceptance criteria\n\n- [ ] AC1: do thing\n",
                encoding="utf-8",
            )
            out = _run_cli(repo, reconcile=str(f))
        self.assertGreaterEqual(len(out["findings"]), 1)
        finding = out["findings"][0]
        for key in ("lens", "classification", "severity", "location",
                    "finding", "recommendation", "confidence"):
            self.assertIn(key, finding, f"finding missing {key}")
        self.assertEqual(finding["lens"], "derivation")

    def test_cap_5_findings_per_artifact(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            f = repo / "spec-many.md"
            ac_lines = "\n".join(f"- [ ] AC{i}" for i in range(1, 11))
            f.write_text(f"# spec\n\n## Acceptance criteria\n\n{ac_lines}\n",
                         encoding="utf-8")
            out = _run_cli(repo, str(f))
        self.assertLessEqual(len(out["findings"]), 5)
        # With --strict, the cap lifts.
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            f = repo / "spec-many.md"
            ac_lines = "\n".join(f"- [ ] AC{i}" for i in range(1, 11))
            f.write_text(f"# spec\n\n## Acceptance criteria\n\n{ac_lines}\n",
                         encoding="utf-8")
            out = _run_cli(repo, str(f), "--strict")
        self.assertGreaterEqual(len(out["findings"]), 10)


if __name__ == "__main__":
    unittest.main()
