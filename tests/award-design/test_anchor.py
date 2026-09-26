"""Seed validity, quiet-brief filtering, and replayable anchor commands."""

import importlib.util
import re
import shlex
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
# The skill root is the documented invocation context — `python3 scripts/<name>.py`
# is what SKILL.md tells the model to run, and what the printed command replays.
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
SCRIPT = SKILL_DIR / "scripts" / "anchor.py"

_spec = importlib.util.spec_from_file_location("anchor", SCRIPT)
assert _spec is not None and _spec.loader is not None
anchor = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(anchor)

KEYS = [f"{value:08x}" for value in range(600)]
OKLCH_RE = re.compile(r"^oklch\((0\.\d+) (\d\.\d+) (\d+(?:\.\d+)?)\)$")
FIELDS = {"id", "material", "palette_family", "oklch_ground", "oklch_accent",
          "temperature", "quiet_safe"}
LOUD_FAMILIES = {"neon-microglow", "multi-hue-oklch"}
QUIET_ACCENT_CHROMA = 0.17
def _oklch(value):
    match = OKLCH_RE.match(value)
    assert match is not None, f"unparseable OKLCH: {value}"
    return float(match.group(1)), float(match.group(2)), float(match.group(3))


def _run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          cwd=SKILL_DIR, capture_output=True, text=True)


class TestPoolShape(unittest.TestCase):
    def test_every_seed_carries_every_field(self):
        self.assertTrue(anchor.SEEDS)
        self.assertEqual(len(anchor.SEEDS), len({seed["id"] for seed in anchor.SEEDS}))
        for seed in anchor.SEEDS:
            self.assertEqual(set(seed), FIELDS, seed.get("id"))
            self.assertIsInstance(seed["quiet_safe"], bool)
            self.assertIn(seed["temperature"], {"warm", "cool", "neutral"})

    def test_oklch_values_parse_and_stay_in_gamut_range(self):
        for seed in anchor.SEEDS:
            for role in ("oklch_ground", "oklch_accent"):
                lightness, chroma, hue = _oklch(seed[role])
                self.assertTrue(0.0 < lightness < 1.0, f"{seed['id']} {role}")
                self.assertTrue(0.0 <= chroma <= 0.37, f"{seed['id']} {role}")
                self.assertTrue(0.0 <= hue < 360.0, f"{seed['id']} {role}")


class TestAntiCreamBand(unittest.TestCase):
    """The warm-neutral pale ground is the model default judges read as a tell.
    Only the ground role is barred; accents and type are unrestricted."""

    def test_no_ground_sits_in_the_band(self):
        low, high = anchor.CREAM_BAND["lightness"]
        hue_low, hue_high = anchor.CREAM_BAND["hue"]
        for seed in anchor.SEEDS:
            lightness, chroma, hue = _oklch(seed["oklch_ground"])
            in_band = (low <= lightness <= high and chroma < anchor.CREAM_BAND["chroma_max"]
                       and hue_low <= hue <= hue_high)
            self.assertFalse(in_band, f"{seed['id']} grounds the page in the cream band")


class TestQuietSafety(unittest.TestCase):
    def test_quiet_safe_means_one_decidable_thing(self):
        for seed in anchor.SEEDS:
            accent_chroma = _oklch(seed["oklch_accent"])[1]
            expected = (seed["palette_family"] not in LOUD_FAMILIES
                        and accent_chroma <= QUIET_ACCENT_CHROMA)
            self.assertEqual(seed["quiet_safe"], expected,
                             f"{seed['id']} is labelled quiet_safe={seed['quiet_safe']}")

    def test_regulated_and_quiet_filter_identically(self):
        self.assertEqual(anchor.pool_for("regulated"), anchor.pool_for("quiet"))
        self.assertEqual(anchor.pool_for("default"), anchor.SEEDS)

    def test_a_quiet_brief_never_draws_a_loud_seed(self):
        for brief_class in ("regulated", "quiet"):
            for key in KEYS:
                self.assertTrue(anchor.draw(key, brief_class)["quiet_safe"])


class TestDraw(unittest.TestCase):
    def test_hash_endpoints_select_first_and_last_seed(self):
        for brief_class in ("default", "regulated", "quiet"):
            pool = anchor.pool_for(brief_class)
            for unit, expected in ((0.0, pool[0]), (1.0, pool[-1])):
                with self.subTest(brief_class=brief_class, unit=unit):
                    with patch.object(anchor, "unit", return_value=unit):
                        self.assertEqual(anchor.draw("endpoint", brief_class), expected)

    def test_every_seed_is_reachable(self):
        drawn = {anchor.draw(key, "default")["id"] for key in KEYS}
        self.assertEqual(drawn, {seed["id"] for seed in anchor.SEEDS})


class TestStdoutContract(unittest.TestCase):
    def setUp(self):
        self.result = _run("--from", "4e91b0cc")
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        self.out = self.result.stdout

    def test_header_carries_key_brief_class_and_seed(self):
        header = self.out.splitlines()[0]
        self.assertIn("key=4e91b0cc", header)
        self.assertIn("brief-class=default", header)
        self.assertIn(anchor.draw("4e91b0cc", "default")["id"], header)

    def test_every_seed_field_is_printed(self):
        seed = anchor.draw("4e91b0cc", "default")
        for value in (seed["material"], seed["palette_family"], seed["oklch_ground"],
                      seed["oklch_accent"], seed["temperature"]):
            self.assertIn(value, self.out)

    def test_printed_reproduction_command_reproduces_the_output(self):
        line = next(l for l in self.out.splitlines() if l.startswith("reproduce: "))
        command = line[len("reproduce: "):].split()
        self.assertEqual(command[0], "python3")
        replay = subprocess.run([sys.executable, *command[1:]],
                                cwd=SKILL_DIR, capture_output=True, text=True)
        self.assertEqual(replay.returncode, 0, replay.stderr)
        self.assertEqual(replay.stdout, self.out)

    def test_generated_key_is_printed_and_replayable(self):
        first = _run()
        self.assertEqual(first.returncode, 0, first.stderr)
        line = next(l for l in first.stdout.splitlines() if l.startswith("reproduce: "))
        replay = subprocess.run([sys.executable, *line[len("reproduce: "):].split()[1:]],
                                cwd=SKILL_DIR, capture_output=True, text=True)
        self.assertEqual(replay.stdout, first.stdout)

    def test_accepted_manual_key_replays_as_one_argument(self):
        first = _run('--from', 'seed with spaces; literal $value')
        self.assertEqual(first.returncode, 0)
        line = next(line for line in first.stdout.splitlines() if line.startswith('reproduce: '))
        command = shlex.split(line[len('reproduce: '):])
        replay = subprocess.run([sys.executable, *command[1:]], cwd=SKILL_DIR,
                                capture_output=True, text=True)
        self.assertEqual(replay.returncode, 0, replay.stderr)
        self.assertEqual(replay.stdout, first.stdout)

    def test_quiet_brief_class_is_reported_with_its_smaller_pool(self):
        out = _run("--from", "4e91b0cc", "--brief-class", "regulated").stdout
        self.assertIn("brief-class=regulated", out)
        self.assertIn(f"pool={len(anchor.pool_for('regulated'))}", out)


if __name__ == "__main__":
    unittest.main()
