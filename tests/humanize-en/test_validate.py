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

from validate import _hit_signature, validate  # noqa: E402

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


class TestCleanStatus(unittest.TestCase):
    def test_clean_text_returns_clean(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("The cat sat. The dog ran. Plain prose.\n")
            path = f.name
        try:
            result = validate(path)
            self.assertEqual(result["status"], "clean")
            self.assertEqual(result["residuals"], [])
            self.assertEqual(result["summary"]["total_residuals"], 0)
        finally:
            Path(path).unlink()


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


class TestRegressionStatus(unittest.TestCase):
    def test_regression_when_new_hit_appears(self):
        """A baseline with NO hits + a file that has hits = regression."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("Moreover, the trend continues.\n")
            path = f.name
        try:
            result = validate(path, baseline_hits=[])
            self.assertEqual(result["status"], "regression")
            self.assertIn("new_hits", result)
            self.assertGreater(len(result["new_hits"]), 0)
        finally:
            Path(path).unlink()


class TestHitSignature(unittest.TestCase):
    def test_signature_uses_pattern_line_snippet(self):
        h = {"pattern": 7, "line": 3, "snippet": "Moreover, here"}
        sig = _hit_signature(h)
        self.assertEqual(sig, ("7", 3, "Moreover, here"))

    def test_string_pattern_supported(self):
        """Brand patterns use string IDs like 'brand:all_caps_emphasis'."""
        h = {"pattern": "brand:all_caps_emphasis", "line": 2, "snippet": "ALL"}
        sig = _hit_signature(h)
        self.assertEqual(sig[0], "brand:all_caps_emphasis")


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
