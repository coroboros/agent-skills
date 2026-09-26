"""Tests for validate.py — three-outcome contract (clean / residuals / regression),
JSON schema, exit codes, and brand-aware integration."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO_ROOT / "skills" / "humanize-en" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate import validate  # noqa: E402

SCRIPT = SCRIPTS / "validate.py"


def _run(*args, stdin=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        input=stdin, capture_output=True, text=True, timeout=30,
    )


def _voice_doc():
    return (
        "---\n"
        "voice:\n  name: \"T\"\n  last_updated: \"2026-04-27\"\n"
        "forbidden_lexicon:\n  - \"verboten\"\n"
        "rewrite_rules:\n  - reject: \"foo\"\n    accept: \"bar\"\n    rule_id: r\n"
        "sentence_norms:\n  word_count_min: 8\n  word_count_max: 18\n  sentence_max_hard: 25\n"
        "---\n# Brand Voice — T\n## 1. Core voice attributes\nstub stub stub stub stub stub stub stub stub stub.\n"
    )


class TestResidualsStatus(unittest.TestCase):
    def test_residuals_no_baseline(self):
        """Without baseline, every remaining hit is a residual (no regression check)."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("Moreover, the data delves into the topic.\n")
            path = f.name
        try:
            result = validate(path)
            self.assertEqual(result["status"], "residuals")
            self.assertGreater(result["summary"]["total_residuals"], 0)
            self.assertNotIn("new_hits", result)
        finally:
            Path(path).unlink()

    def test_residuals_with_baseline_no_new(self):
        """When baseline contains all current hits, status is residuals (no new_hits)."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("Moreover, this is fine.\n")
            path = f.name
        try:
            from prescan import scan as prescan_scan
            baseline = prescan_scan(Path(path).read_text(encoding="utf-8"))
            result = validate(path, baseline_hits=baseline)
            self.assertEqual(result["status"], "residuals")
            self.assertEqual(result["summary"]["new_hit_count"], 0)
        finally:
            Path(path).unlink()

    def test_clean_file_with_populated_baseline_is_clean(self):
        """When the post-rewrite file has zero hits but the baseline lists
        many, the status is `clean` (the rewrite eliminated everything).
        Pinning the success-case asymmetry: baseline-only hits never count
        against the rewrite — only hits present in the file matter."""
        baseline = [
            {"pattern": 7, "label": "ai-vocabulary", "line": 3,
             "snippet": "Moreover, X here"},
            {"pattern": 23, "label": "filler", "line": 4,
             "snippet": "in order to ship"},
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("The cat sat. The dog ran. Plain prose.\n")
            path = f.name
        try:
            result = validate(path, baseline_hits=baseline)
            self.assertEqual(result["status"], "clean",
                             "zero residuals on file = clean regardless of baseline")
            self.assertEqual(result["summary"]["total_residuals"], 0)
            self.assertEqual(result["summary"]["new_hit_count"], 0)
        finally:
            Path(path).unlink()


class TestRegressionStatus(unittest.TestCase):
    def test_regression_partial_overlap(self):
        """Realistic case: a paragraph's baseline hit survives unchanged
        post-rewrite; another paragraph introduces a new AI tell. The
        unchanged paragraph's snippet matches the baseline (same context),
        so only the new pattern is reported as a regression. Tests the
        `(pattern, snippet)` signature contract end-to-end."""
        from prescan import scan as prescan_scan
        # Step 1: file as it existed at baseline capture
        baseline_text = "Moreover, X here.\n\nA clean paragraph stands.\n"
        # Step 2: capture baseline hits from that exact text
        baseline = prescan_scan(baseline_text)
        # Step 3: write the POST-rewrite file. First paragraph unchanged
        # (so its snippet still matches the baseline); second paragraph
        # introduced a new AI tell (`crucial`) that did not exist before.
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("Moreover, X here.\n\nThis is crucial work.\n")
            path = f.name
        try:
            result = validate(path, baseline_hits=baseline)
            self.assertEqual(result["status"], "regression",
                             "the new `crucial` token must surface as a regression")
            new_snips = " ".join(h["snippet"] for h in result["new_hits"])
            self.assertIn("crucial", new_snips,
                          "the new_hits must point at `crucial`")
            self.assertNotIn("Moreover", new_snips,
                             "the surviving `Moreover` must NOT appear in new_hits")
        finally:
            Path(path).unlink()


class TestBaselineLineDrift(unittest.TestCase):
    def test_line_drift_does_not_create_false_regression(self):
        from prescan import scan
        from brand_prescan import scan_brand

        prose = "Moreover, the verboten word remains.\n"
        baseline = scan("\n\n" + prose, attach_source=True)
        baseline += scan_brand("\n\n" + prose, {"forbidden_lexicon": ["verboten"]})
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target, voice, baseline_path = root / "draft.md", root / "voice.md", root / "baseline.json"
            target.write_text(prose)
            voice.write_text(_voice_doc())
            baseline_path.write_text(json.dumps(baseline))
            result = _run("--brand", str(voice), "--baseline", str(baseline_path), str(target))
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "residuals")
        self.assertEqual(report["summary"], {
            "total_residuals": 2, "universal_residuals": 1,
            "brand_residuals": 1, "new_hit_count": 0,
        })
        self.assertEqual([hit["line"] for hit in report["residuals"]], [1, 1])


class TestBrandIntegration(unittest.TestCase):
    def test_brand_residuals_counted_separately(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as voice:
            voice.write(_voice_doc())
            voice_path = voice.name
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as prose:
            prose.write("Moreover, the verboten word appears.\n")
            prose_path = prose.name
        try:
            result = validate(prose_path, brand_path=voice_path)
            self.assertGreater(result["summary"]["universal_residuals"], 0,
                               "universal pattern 7 'moreover' should fire")
            self.assertGreater(result["summary"]["brand_residuals"], 0,
                               "brand forbidden_lexicon 'verboten' should fire")
        finally:
            Path(prose_path).unlink()
            Path(voice_path).unlink()


class TestCLI(unittest.TestCase):
    def test_clean_exits_0(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("Plain prose with no tells.\n")
            path = f.name
        try:
            r = _run(path)
            self.assertEqual(r.returncode, 0)
            self.assertEqual(json.loads(r.stdout)["status"], "clean")
        finally:
            Path(path).unlink()

    def test_residuals_exits_0(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("Moreover, this delves into stuff.\n")
            path = f.name
        try:
            r = _run(path)
            self.assertEqual(r.returncode, 0)
            self.assertEqual(json.loads(r.stdout)["status"], "residuals")
        finally:
            Path(path).unlink()

    def test_regression_exits_1(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as prose:
            prose.write("Moreover, hits.\n")
            prose_path = prose.name
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as baseline:
            baseline.write("[]")  # empty baseline = any hit is regression
            baseline_path = baseline.name
        try:
            r = _run("--baseline", baseline_path, prose_path)
            self.assertEqual(r.returncode, 1)
            self.assertEqual(json.loads(r.stdout)["status"], "regression")
        finally:
            Path(prose_path).unlink()
            Path(baseline_path).unlink()

    def test_missing_target_exits_2(self):
        r = _run("/tmp/_validate_does_not_exist.md")
        self.assertEqual(r.returncode, 2)

    def test_missing_baseline_exits_2(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("Plain.\n")
            path = f.name
        try:
            r = _run("--baseline", "/tmp/_no_baseline.json", path)
            self.assertEqual(r.returncode, 2)
        finally:
            Path(path).unlink()

    def test_invalid_baseline_json_exits_2(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as prose:
            prose.write("Plain.\n")
            prose_path = prose.name
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as bad:
            bad.write("not json")
            bad_path = bad.name
        try:
            r = _run("--baseline", bad_path, prose_path)
            self.assertEqual(r.returncode, 2)
        finally:
            Path(prose_path).unlink()
            Path(bad_path).unlink()

    def test_baseline_non_list_shape_exits_2(self):
        """A baseline that is valid JSON but not an array (e.g. a top-level
        object) violates the schema. Must exit 2 with a clear error."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as prose:
            prose.write("Plain.\n")
            prose_path = prose.name
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as bad:
            bad.write('{"hits": []}')  # object, not array
            bad_path = bad.name
        try:
            r = _run("--baseline", bad_path, prose_path)
            self.assertEqual(r.returncode, 2,
                             "non-list baseline must violate schema and exit 2")
            self.assertIn("array", r.stderr.lower() + r.stdout.lower())
        finally:
            Path(prose_path).unlink()
            Path(bad_path).unlink()


class TestSchemaShape(unittest.TestCase):
    def test_clean_result_shape(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("Clean.\n")
            path = f.name
        try:
            r = validate(path)
            for key in ("path", "status", "residuals", "summary"):
                self.assertIn(key, r)
            for key in ("total_residuals", "universal_residuals",
                        "brand_residuals", "new_hit_count"):
                self.assertIn(key, r["summary"])
            self.assertEqual(r["status"], "clean")
            self.assertNotIn("new_hits", r,
                             "new_hits absent unless status=='regression'")
        finally:
            Path(path).unlink()


if __name__ == "__main__":
    unittest.main()
