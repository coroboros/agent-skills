"""Tests for eval_patterns.py — corpus pass-rate, JSON shape, CLI flags, error paths.

Pins the eval-result schema documented in `references/schemas.md` § "eval result"
and the exit-code contract (0 all pass, 1 any fail, 2 argument or I/O error).
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "humanize-en"
SCRIPTS = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS))

from eval_patterns import evaluate_sample  # noqa: E402

SCRIPT = SCRIPTS / "eval_patterns.py"
DEFAULT_CORPUS = SKILL_DIR / "eval-corpus" / "samples"


def _run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


class TestDefaultCorpus(unittest.TestCase):
    """The shipped corpus must pass — if it doesn't, prescan.py has regressed
    against the documented patterns or a sample's expected_hits drifted."""

    def test_default_corpus_passes(self):
        r = _run()
        self.assertEqual(
            r.returncode, 0,
            f"shipped corpus failed:\nstdout={r.stdout}\nstderr={r.stderr}",
        )

    def test_default_report_summary_shape(self):
        r = _run()
        self.assertEqual(r.returncode, 0)
        report = json.loads(r.stdout)
        self.assertIn("samples", report)
        self.assertIn("summary", report)
        for key in ("total_samples", "passed", "failed", "pass_rate"):
            self.assertIn(key, report["summary"])
        self.assertGreater(
            report["summary"]["total_samples"], 0,
            "corpus is empty — at least one sample is shipped",
        )
        self.assertEqual(
            report["summary"]["passed"], report["summary"]["total_samples"]
        )
        self.assertEqual(report["summary"]["pass_rate"], 1.0)

    def test_each_sample_result_shape(self):
        r = _run()
        report = json.loads(r.stdout)
        for sample in report["samples"]:
            with self.subTest(sample=sample.get("id")):
                for key in (
                    "id",
                    "expected_patterns",
                    "detected_patterns",
                    "missing",
                    "extra",
                    "pass",
                ):
                    self.assertIn(key, sample)
                self.assertIsInstance(sample["expected_patterns"], list)
                self.assertIsInstance(sample["detected_patterns"], list)
                self.assertIsInstance(sample["missing"], list)
                self.assertIsInstance(sample["extra"], list)
                self.assertIsInstance(sample["pass"], bool)


class TestSampleMode(unittest.TestCase):
    """--sample selects a single file and short-circuits corpus discovery."""

    def test_single_sample_passes(self):
        sample_path = DEFAULT_CORPUS / "clean-prose-01.json"
        self.assertTrue(sample_path.exists(), "fixture removed — test stale")
        r = _run("--sample", str(sample_path))
        self.assertEqual(
            r.returncode, 0,
            f"clean-prose sample failed:\nstdout={r.stdout}\nstderr={r.stderr}",
        )
        report = json.loads(r.stdout)
        self.assertEqual(report["summary"]["total_samples"], 1)
        self.assertEqual(report["samples"][0]["id"], "clean-prose-01")


class TestCorpusFlag(unittest.TestCase):
    """--corpus accepts a custom directory of samples."""

    def test_custom_corpus_dir(self):
        with tempfile.TemporaryDirectory() as t:
            corpus = Path(t) / "samples"
            corpus.mkdir()
            (corpus / "tiny.json").write_text(
                json.dumps({
                    "id": "tiny",
                    "input": "Moreover, the data is fine.",
                    "expected_hits": [{"pattern": 7, "label": "ai-vocabulary"}],
                })
            )
            r = _run("--corpus", str(corpus))
        self.assertEqual(
            r.returncode, 0,
            f"custom corpus failed:\nstdout={r.stdout}\nstderr={r.stderr}",
        )
        report = json.loads(r.stdout)
        self.assertEqual(report["summary"]["total_samples"], 1)
        self.assertEqual(report["samples"][0]["id"], "tiny")


class TestErrorPaths(unittest.TestCase):
    """Exit code 2 — argument or I/O error. Exit code 1 — at least one sample fails."""

    def test_empty_corpus_exits_2(self):
        with tempfile.TemporaryDirectory() as t:
            r = _run("--corpus", t)
        self.assertEqual(r.returncode, 2)
        self.assertIn("no samples", r.stderr)

    def test_missing_corpus_dir_exits_2(self):
        r = _run("--corpus", "/tmp/_does_not_exist_eval_corpus_humanize")
        self.assertEqual(r.returncode, 2)

    def test_malformed_json_sample_exits_2(self):
        with tempfile.TemporaryDirectory() as t:
            corpus = Path(t) / "samples"
            corpus.mkdir()
            (corpus / "broken.json").write_text("{not valid json")
            r = _run("--corpus", str(corpus))
        self.assertEqual(r.returncode, 2)
        self.assertIn("error reading", r.stderr)

    def test_failing_sample_exits_1(self):
        """A sample claiming a pattern prescan won't produce fails fast."""
        with tempfile.TemporaryDirectory() as t:
            corpus = Path(t) / "samples"
            corpus.mkdir()
            (corpus / "fail.json").write_text(
                json.dumps({
                    "id": "fail",
                    "input": "Plain prose with no flags whatsoever.",
                    "expected_hits": [
                        {"pattern": 1, "label": "significance-inflation"}
                    ],
                })
            )
            r = _run("--corpus", str(corpus))
        self.assertEqual(r.returncode, 1)
        report = json.loads(r.stdout)
        self.assertFalse(report["samples"][0]["pass"])
        self.assertEqual(report["samples"][0]["missing"], [1])


class TestEvaluateSample(unittest.TestCase):
    """Direct tests on the evaluate_sample() helper — independent of CLI."""

    def test_match_returns_pass_true(self):
        sample = {
            "id": "match",
            "input": "Moreover, the data is fine.",
            "expected_hits": [{"pattern": 7, "label": "ai-vocabulary"}],
        }
        result = evaluate_sample(sample)
        self.assertTrue(result["pass"])
        self.assertEqual(result["missing"], [])
        self.assertEqual(result["extra"], [])

    def test_missing_pattern_recorded(self):
        sample = {
            "id": "missing",
            "input": "Plain.",
            "expected_hits": [{"pattern": 1, "label": "significance-inflation"}],
        }
        result = evaluate_sample(sample)
        self.assertFalse(result["pass"])
        self.assertEqual(result["missing"], [1])

    def test_extra_pattern_recorded(self):
        sample = {
            "id": "extra",
            "input": "Moreover, this triggers ai-vocabulary.",
            "expected_hits": [],
        }
        result = evaluate_sample(sample)
        self.assertFalse(result["pass"])
        self.assertIn(7, result["extra"])


if __name__ == "__main__":
    unittest.main()
