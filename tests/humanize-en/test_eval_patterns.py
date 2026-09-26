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
SCRIPT = SCRIPTS / "eval_patterns.py"
DEFAULT_CORPUS = SKILL_DIR / "eval-corpus" / "samples"


def _run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


class TestDefaultCorpus(unittest.TestCase):
    """The shipped corpus must pass — if it doesn't, prescan.py has regressed
    against the documented patterns or a sample's expected_hits drifted."""

    def test_shipped_corpora_match_expected_patterns(self):
        for args, corpus in (((), DEFAULT_CORPUS), (("--brand",), SKILL_DIR / "eval-corpus/brand-voice")):
            with self.subTest(corpus=corpus.name):
                expected_ids = {json.loads(path.read_text())["id"] for path in corpus.glob("*.json")}
                self.assertTrue(expected_ids)
                result = _run(*args)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                report = json.loads(result.stdout)
                self.assertEqual({sample["id"] for sample in report["samples"]}, expected_ids)
                self.assertEqual(report["summary"], {
                    "total_samples": len(expected_ids), "passed": len(expected_ids),
                    "failed": 0, "pass_rate": 1.0,
                })
                for sample in report["samples"]:
                    self.assertEqual(sample["detected_patterns"], sample["expected_patterns"])
                    self.assertEqual(sample["missing"], [])
                    self.assertEqual(sample["extra"], [])
                    self.assertTrue(sample["pass"])


class TestSampleMode(unittest.TestCase):
    """--sample selects a single file and short-circuits corpus discovery."""

    def test_single_sample_passes(self):
        sample_path = DEFAULT_CORPUS / "clean-prose-01.json"
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
        cases = (("Plain prose.", [{"pattern": 1}], [1], []),
                 ("Moreover, the data is fine.", [], [], [7]))
        for text, expected, missing, extra in cases:
            with self.subTest(text=text), tempfile.TemporaryDirectory() as t:
                corpus = Path(t)
                (corpus / "fail.json").write_text(json.dumps({
                    "id": "fail", "input": text, "expected_hits": expected,
                }))
                result = _run("--corpus", str(corpus))
            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads(result.stdout)
            self.assertFalse(report["samples"][0]["pass"])
            self.assertEqual(report["samples"][0]["missing"], missing)
            self.assertEqual(report["samples"][0]["extra"], extra)
            self.assertEqual(report["summary"]["failed"], 1)


if __name__ == "__main__":
    unittest.main()
