"""Tests for measure_corpus.py — stylometry engine + sentence_norms mapping."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).parent.parent.parent / "skills" / "brand-voice" / "scripts"
sys.path.insert(0, str(SCRIPTS))
from measure_corpus import measure, to_sentence_norms  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"
SCRIPT = SCRIPTS / "measure_corpus.py"


def _read(name):
    return (FIXTURES / name).read_text(encoding="utf-8")


class TestMeasureShape(unittest.TestCase):
    def test_measurable_corpus_keys_and_order(self):
        stats = measure(_read("corpus-measurable.md"))
        self.assertGreaterEqual(stats["sentence_count"], 30)
        wc = stats["word_counts"]
        self.assertLessEqual(wc["min"], wc["p10"])
        self.assertLessEqual(wc["p10"], wc["median"])
        self.assertLessEqual(wc["median"], wc["p90"])
        self.assertLessEqual(wc["p90"], wc["max"])
        self.assertEqual(set(stats["conventions"]),
                         {"em_dash_spacing", "oxford_comma", "contractions", "exclamation_marks"})


class TestDetectors(unittest.TestCase):
    def test_tight_em_dash(self):
        self.assertEqual(measure(_read("corpus-measurable.md"))["conventions"]["em_dash_spacing"], "tight")

    def test_spaced_em_dash(self):
        stats = measure("Foo — bar baz qux. Quux — corge grault garply.")
        self.assertEqual(stats["conventions"]["em_dash_spacing"], "spaced")

    def test_no_em_dash_omitted(self):
        self.assertIsNone(measure("Plain prose, no dashes. Another plain line here.")["conventions"]["em_dash_spacing"])

    def test_exclamation_allow(self):
        self.assertEqual(measure(_read("corpus-measurable.md"))["conventions"]["exclamation_marks"], "allow")

    def test_no_exclamation_forbid(self):
        self.assertEqual(measure("Calm prose. No shouting here.")["conventions"]["exclamation_marks"], "forbid")

    def test_oxford_true(self):
        stats = measure("We value clarity, candor, and craft. We ship code, tests, and docs.")
        self.assertTrue(stats["conventions"]["oxford_comma"])

    def test_oxford_false(self):
        stats = measure("We value clarity, candor and craft. We ship code, tests and docs.")
        self.assertFalse(stats["conventions"]["oxford_comma"])

    def test_oxford_omitted_without_list(self):
        self.assertIsNone(measure("Two plain sentences. No lists at all.")["conventions"]["oxford_comma"])

    def test_contraction_allow(self):
        self.assertEqual(measure("We don't hedge. We're direct. I'm certain.")["conventions"]["contractions"], "allow")

    def test_possessive_is_not_a_contraction(self):
        # "reader's" is possessive; it must not flip contractions to allow.
        self.assertEqual(measure("The reader's time matters. The brand's voice holds.")["conventions"]["contractions"], "forbid")

    def test_contraction_forbid_on_formal_corpus(self):
        self.assertEqual(measure(_read("corpus-measurable.md"))["conventions"]["contractions"], "forbid")


class TestCodeRobustness(unittest.TestCase):
    def test_code_blocks_do_not_inflate(self):
        stats = measure(_read("corpus-code-heavy.md"))
        # Prose only; fenced blocks and inline code are stripped before measuring.
        self.assertLessEqual(stats["sentence_count"], 10)
        # The code carries long numeric/word runs — none may leak as a long "sentence".
        self.assertLess(stats["word_counts"]["max"], 15)


class TestSentenceNorms(unittest.TestCase):
    def test_measurable_maps_to_lint_valid_norms(self):
        norms = to_sentence_norms(measure(_read("corpus-measurable.md")))
        self.assertIsNotNone(norms)
        self.assertGreaterEqual(norms["word_count_min"], 1)
        self.assertLessEqual(norms["word_count_min"], norms["word_count_max"])
        self.assertLessEqual(norms["word_count_max"], norms["sentence_max_hard"])
        self.assertIn(norms["contractions"], {"allow", "forbid"})
        self.assertIn(norms["exclamation_marks"], {"allow", "forbid"})
        self.assertEqual(norms["em_dash_spacing"], "tight")

    def test_thin_corpus_returns_none(self):
        self.assertIsNone(to_sentence_norms(measure(_read("corpus-thin.md"))))

    def test_threshold_boundary(self):
        stats = measure(_read("corpus-measurable.md"))
        n = stats["sentence_count"]
        self.assertIsNone(to_sentence_norms(stats, threshold=n + 1))
        self.assertIsNotNone(to_sentence_norms(stats, threshold=n))

    def test_uniform_corpus_keeps_min_le_max(self):
        # Every sentence the same length → p10 == p90; the clamp keeps min <= max <= hard.
        text = " ".join("one two three four five." for _ in range(40))
        norms = to_sentence_norms(measure(text))
        self.assertIsNotNone(norms)
        self.assertLessEqual(norms["word_count_min"], norms["word_count_max"])
        self.assertLessEqual(norms["word_count_max"], norms["sentence_max_hard"])


class TestDeterminism(unittest.TestCase):
    def test_same_input_identical_output(self):
        text = _read("corpus-measurable.md")
        self.assertEqual(measure(text), measure(text))

    def test_cli_output_stable(self):
        args = [sys.executable, str(SCRIPT), str(FIXTURES / "corpus-measurable.md")]
        a = subprocess.run(args, capture_output=True, text=True)
        b = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(a.returncode, 0)
        self.assertEqual(a.stdout, b.stdout)


class TestCLI(unittest.TestCase):
    def test_as_sentence_norms_emits_dict(self):
        res = subprocess.run([sys.executable, str(SCRIPT), str(FIXTURES / "corpus-measurable.md"), "--as-sentence-norms"],
                             capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        norms = json.loads(res.stdout)
        self.assertIsInstance(norms, dict)
        self.assertIn("word_count_min", norms)

    def test_as_sentence_norms_thin_emits_null(self):
        res = subprocess.run([sys.executable, str(SCRIPT), str(FIXTURES / "corpus-thin.md"), "--as-sentence-norms"],
                             capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIsNone(json.loads(res.stdout))

    def test_empty_input_exits_2_with_no_stdout(self):
        res = subprocess.run([sys.executable, str(SCRIPT)], input="   \n  ",
                             capture_output=True, text=True)
        self.assertEqual(res.returncode, 2)
        self.assertEqual(res.stdout.strip(), "")
        self.assertIn("empty input", res.stderr)

    def test_stdin_measure(self):
        res = subprocess.run([sys.executable, str(SCRIPT)],
                             input="A short sentence here. Another one follows.",
                             capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertEqual(json.loads(res.stdout)["sentence_count"], 2)


if __name__ == "__main__":
    unittest.main()
