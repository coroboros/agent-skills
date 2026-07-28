"""award-design — the material anchor draws a ground the model would not have picked.

The palette rut is narrower than the direction rut and better documented: warm
cream, serif, terracotta, or the GitHub-dark it swaps to when told "not cream"
(`anti-patterns.md`). A seeded draw only escapes it if the POOL escapes it, so
most of this file audits the curation rather than the arithmetic — the anti-cream
band is empty of grounds, the hue buckets are spread instead of piled on the
frequent hues, every seed names a physical material, and `quiet_safe` means one
decidable thing so a regulated brief gets a real filter and not a label. The
draw's determinism is pinned separately: the printed key and command are the
whole audit trail."""

import hashlib
import importlib.util
import math
import re
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

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
FAMILIES = {"dark-base-accent", "mono-oklch-depth", "earthy-pastel",
            "neon-microglow", "multi-hue-oklch"}
LOUD_FAMILIES = {"neon-microglow", "multi-hue-oklch"}
QUIET_ACCENT_CHROMA = 0.17
BUCKET_DEGREES = 30
# A seed is a thing with a surface and a temperature; these are page styles.
SOFTWARE_ARCHETYPES = ("dark mode", "light mode", "glassmorph", "neumorph", "material design",
                       "flat design", "skeuomorph", "brutalist", "editorial", "minimal")


def _oklch(value):
    match = OKLCH_RE.match(value)
    assert match is not None, f"unparseable OKLCH: {value}"
    return float(match.group(1)), float(match.group(2)), float(match.group(3))


def _run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          cwd=SKILL_DIR, capture_output=True, text=True)


class TestPoolShape(unittest.TestCase):
    def test_pool_size_and_unique_ids(self):
        self.assertGreaterEqual(len(anchor.SEEDS), 24)
        self.assertEqual(len(anchor.SEEDS), len({seed["id"] for seed in anchor.SEEDS}))

    def test_every_seed_carries_every_field(self):
        for seed in anchor.SEEDS:
            self.assertEqual(set(seed), FIELDS, seed.get("id"))
            self.assertIsInstance(seed["quiet_safe"], bool)
            self.assertIn(seed["temperature"], {"warm", "cool", "neutral"})

    def test_all_five_color_strategies_are_represented(self):
        present = Counter(seed["palette_family"] for seed in anchor.SEEDS)
        self.assertEqual(set(present), FAMILIES)
        for family, count in present.items():
            self.assertGreaterEqual(count, 3, f"{family} is too thin to survive the filter")

    def test_oklch_values_parse_and_stay_in_gamut_range(self):
        for seed in anchor.SEEDS:
            for role in ("oklch_ground", "oklch_accent"):
                lightness, chroma, hue = _oklch(seed[role])
                self.assertTrue(0.0 < lightness < 1.0, f"{seed['id']} {role}")
                self.assertTrue(0.0 <= chroma <= 0.37, f"{seed['id']} {role}")
                self.assertTrue(0.0 <= hue < 360.0, f"{seed['id']} {role}")

    def test_materials_are_physical_not_software_archetypes(self):
        for seed in anchor.SEEDS:
            lowered = f"{seed['id']} {seed['material']}".lower()
            for term in SOFTWARE_ARCHETYPES:
                self.assertNotIn(term, lowered,
                                 f"{seed['id']} names a page style, not a material")


class TestAntiCreamBand(unittest.TestCase):
    """The warm-neutral pale ground is the model default judges read as a tell.
    It is barred from the GROUND role — accents and type may live anywhere."""

    def test_band_definition_has_not_been_widened(self):
        self.assertEqual(anchor.CREAM_BAND,
                         {"lightness": (0.84, 0.97), "chroma_max": 0.06, "hue": (40.0, 100.0)})

    def test_no_ground_sits_in_the_band(self):
        low, high = anchor.CREAM_BAND["lightness"]
        hue_low, hue_high = anchor.CREAM_BAND["hue"]
        for seed in anchor.SEEDS:
            lightness, chroma, hue = _oklch(seed["oklch_ground"])
            in_band = (low <= lightness <= high and chroma < anchor.CREAM_BAND["chroma_max"]
                       and hue_low <= hue <= hue_high)
            self.assertFalse(in_band, f"{seed['id']} grounds the page in the cream band")


class TestHueSpread(unittest.TestCase):
    """An unseeded pick piles onto the frequent hues; a pool that does the same
    hands the rut back. Every 30° bucket carries a ground, none carries a crowd."""

    def _buckets(self):
        return Counter(int(_oklch(seed["oklch_ground"])[2] // BUCKET_DEGREES)
                       for seed in anchor.SEEDS)

    def test_every_bucket_is_populated(self):
        self.assertEqual(set(self._buckets()), set(range(360 // BUCKET_DEGREES)))

    def test_no_bucket_is_overweight(self):
        for bucket, count in self._buckets().items():
            self.assertLessEqual(count, 3, f"bucket {bucket * BUCKET_DEGREES}° is crowded")


class TestQuietSafety(unittest.TestCase):
    def test_quiet_safe_means_one_decidable_thing(self):
        for seed in anchor.SEEDS:
            accent_chroma = _oklch(seed["oklch_accent"])[1]
            expected = (seed["palette_family"] not in LOUD_FAMILIES
                        and accent_chroma <= QUIET_ACCENT_CHROMA)
            self.assertEqual(seed["quiet_safe"], expected,
                             f"{seed['id']} is labelled quiet_safe={seed['quiet_safe']}")

    def test_quiet_pool_stays_wide_enough_to_be_a_draw(self):
        quiet = anchor.pool_for("quiet")
        self.assertGreaterEqual(len(quiet), 10)
        self.assertGreaterEqual(len({seed["palette_family"] for seed in quiet}), 3)

    def test_regulated_and_quiet_filter_identically(self):
        self.assertEqual(anchor.pool_for("regulated"), anchor.pool_for("quiet"))
        self.assertEqual(anchor.pool_for("default"), anchor.SEEDS)

    def test_a_quiet_brief_never_draws_a_loud_seed(self):
        for brief_class in ("regulated", "quiet"):
            for key in KEYS:
                self.assertTrue(anchor.draw(key, brief_class)["quiet_safe"])


class TestDraw(unittest.TestCase):
    def test_unit_matches_the_published_formula(self):
        for key in KEYS[:50]:
            expected = int.from_bytes(hashlib.sha256(
                f"{anchor.SCOPE}:{anchor.SALT}:{key}".encode("utf-8")).digest()[:4], "big") / 0xFFFFFFFF
            self.assertEqual(anchor.unit(anchor.SCOPE, anchor.SALT, key), expected)

    def test_index_is_the_seeded_position_in_the_pool(self):
        pool = anchor.pool_for("default")
        for key in KEYS[:200]:
            expected = pool[math.floor(anchor.unit(anchor.SCOPE, anchor.SALT, key) * len(pool))]
            self.assertEqual(anchor.draw(key, "default")["id"], expected["id"])

    def test_every_seed_is_reachable(self):
        drawn = {anchor.draw(key, "default")["id"] for key in KEYS}
        self.assertEqual(drawn, {seed["id"] for seed in anchor.SEEDS})

    def test_same_key_draws_the_same_seed(self):
        for key in KEYS[:40]:
            self.assertEqual(anchor.draw(key, "default")["id"], anchor.draw(key, "default")["id"])

    def test_different_keys_move_the_draw(self):
        self.assertGreater(len({anchor.draw(key, "default")["id"] for key in KEYS[:60]}), 10)


class TestStdoutContract(unittest.TestCase):
    def setUp(self):
        self.result = _run("--from", "4e91b0cc")
        self.out = self.result.stdout

    def test_exits_zero(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)

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

    def test_composition_sentence_bounds_the_anchors_authority(self):
        lowered = self.out.lower()
        self.assertIn("compose", lowered)
        self.assertIn("never overrides an explicit brand commitment", lowered)

    def test_generated_key_is_printed_and_replayable(self):
        first = _run()
        self.assertEqual(first.returncode, 0, first.stderr)
        line = next(l for l in first.stdout.splitlines() if l.startswith("reproduce: "))
        replay = subprocess.run([sys.executable, *line[len("reproduce: "):].split()[1:]],
                                cwd=SKILL_DIR, capture_output=True, text=True)
        self.assertEqual(replay.stdout, first.stdout)

    def test_quiet_brief_class_is_reported_with_its_smaller_pool(self):
        out = _run("--from", "4e91b0cc", "--brief-class", "regulated").stdout
        self.assertIn("brief-class=regulated", out)
        self.assertIn(f"pool={len(anchor.pool_for('regulated'))}", out)


if __name__ == "__main__":
    unittest.main()
