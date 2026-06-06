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

    def test_oxford_compound_comma_not_a_list(self):
        # A lone comma before "and" joining two clauses is not a serial comma.
        self.assertIsNone(measure("We went home, and we slept soundly here.")["conventions"]["oxford_comma"])

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

    def test_omits_em_dash_and_oxford_when_no_signal(self):
        # No em-dash and no list → those keys are absent from the dict; the
        # always-valued conventions (contractions, exclamation) remain.
        text = " ".join(f"Sentence number {i} stays plain here today." for i in range(35))
        norms = to_sentence_norms(measure(text))
        self.assertIsNotNone(norms)
        self.assertNotIn("em_dash_spacing", norms)
        self.assertNotIn("oxford_comma", norms)
        self.assertIn("contractions", norms)
        self.assertIn("exclamation_marks", norms)

    def test_oxford_false_survives_into_norms(self):
        # A non-serial-comma list keeps oxford_comma present and False — distinct
        # from the omitted-when-None case above.
        text = " ".join(f"We use red, green and blue item {i} here." for i in range(35))
        norms = to_sentence_norms(measure(text))
        self.assertIsNotNone(norms)
        self.assertIn("oxford_comma", norms)
        self.assertFalse(norms["oxford_comma"])


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

    def test_threshold_flag_gates_mapping(self):
        path = str(FIXTURES / "corpus-measurable.md")
        high = subprocess.run([sys.executable, str(SCRIPT), path, "--as-sentence-norms", "--threshold", "100"],
                              capture_output=True, text=True)
        self.assertEqual(high.returncode, 0)
        self.assertIsNone(json.loads(high.stdout))
        low = subprocess.run([sys.executable, str(SCRIPT), path, "--as-sentence-norms", "--threshold", "5"],
                             capture_output=True, text=True)
        self.assertEqual(low.returncode, 0)
        self.assertIsInstance(json.loads(low.stdout), dict)

    def test_unreadable_path_exits_2(self):
        res = subprocess.run([sys.executable, str(SCRIPT), "/nonexistent/path/corpus.md"],
                             capture_output=True, text=True)
        self.assertEqual(res.returncode, 2)
        self.assertEqual(res.stdout.strip(), "")
        self.assertIn("cannot read input", res.stderr)


class TestTokenizerRobustness(unittest.TestCase):
    def test_sentence_final_abbreviation_splits_before_capital(self):
        # "…etc. Then…" is two sentences — the abbreviation period is a real break.
        self.assertEqual(measure("Bring pens, paper, etc. Then we start. Done now today.")["sentence_count"], 3)

    def test_connective_abbreviation_does_not_split(self):
        # "e.g. React" mid-sentence stays one sentence — no spurious fragment.
        self.assertEqual(measure("Use a framework e.g. React for this. Done now today.")["sentence_count"], 2)

    def test_ellipsis_is_not_a_boundary(self):
        self.assertEqual(measure("Wait... what now here friend.")["sentence_count"], 1)

    def test_decimal_is_not_a_boundary(self):
        self.assertEqual(measure("Pi is 3.14 today. Next sentence here now.")["sentence_count"], 2)

    def test_heading_line_dropped_not_merged(self):
        # The heading must not merge into the body sentence.
        self.assertEqual(measure("# My Heading\nThis is the body sentence here now.")["sentence_count"], 1)

    def test_ordered_list_markers_stripped(self):
        md = "1. First item here now.\n2. Second item there now.\n3. Third item right here."
        self.assertEqual(measure(md)["sentence_count"], 3)

    def test_preexisting_sentinel_not_corrupting(self):
        # A literal control-char sentinel in the input is dropped, not restored to a period.
        self.assertEqual(measure("Alpha\x01beta gamma delta. Second one here now.")["sentence_count"], 2)


if __name__ == "__main__":
    unittest.main()
