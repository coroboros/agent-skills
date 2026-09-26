"""Direction range, challenger exclusion, CLI validation, and replayable commands."""

import importlib.util
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
# The skill root is the documented invocation context — `python3 scripts/<name>.py`
# is what SKILL.md tells the model to run, and what the printed command replays.
SKILL_DIR = REPO_ROOT / "skills" / "award-design"
SCRIPT = SKILL_DIR / "scripts" / "direction_roll.py"

_spec = importlib.util.spec_from_file_location("direction_roll", SCRIPT)
assert _spec is not None and _spec.loader is not None
roll = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(roll)

KEYS = [f"{value:08x}" for value in range(600)]


def _run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          cwd=SKILL_DIR, capture_output=True, text=True)


class TestRollMathematics(unittest.TestCase):
    def test_hash_endpoints_stay_within_the_assignment_and_challenger_pools(self):
        for count in (5, 6, 7):
            for unit, expected in ((0.0, 3), (1.0, count)):
                with self.subTest(count=count, unit=unit):
                    with patch.object(roll, "unit", return_value=unit):
                        self.assertEqual(roll.roll_index("direction", "endpoint", count, 0)[0], expected)
                        challengers = roll.draw_challengers("direction", "endpoint", "editorial")
                        self.assertEqual(len(set(challengers)), 2)
                        self.assertNotIn("editorial", challengers)

    def test_every_index_in_range_is_reachable(self):
        for count in (5, 6, 7):
            drawn = {roll.roll_index("direction", key, count, 0)[0] for key in KEYS}
            self.assertEqual(drawn, set(range(3, count + 1)))

    def test_reroll_salts_the_index(self):
        self.assertEqual(roll.roll_index("direction", "deadbeef", 6, 0)[1], "index")
        self.assertEqual(roll.roll_index("direction", "deadbeef", 6, 1)[1], "index:reroll-1")
        differing = sum(roll.roll_index("direction", key, 6, 0)[0]
                        != roll.roll_index("direction", key, 6, 1)[0] for key in KEYS)
        self.assertGreater(differing, len(KEYS) // 2,
                           "a reroll that mostly returns the same spine is not a reroll")

    def test_scope_separates_the_draw(self):
        differing = sum(roll.roll_index("direction", key, 6, 0)[0]
                        != roll.roll_index("surface", key, 6, 0)[0] for key in KEYS)
        self.assertGreater(differing, len(KEYS) // 2)


class TestChallengerDraw(unittest.TestCase):
    """Two challengers off the same hash — the local contest that keeps the
    assigned spine from being the only thing on the table."""

    def test_two_distinct_names_from_the_nine(self):
        for key in KEYS:
            picks = roll.draw_challengers("direction", key, "editorial")
            self.assertEqual(len(picks), 2)
            self.assertNotEqual(picks[0], picks[1])
            for name in picks:
                self.assertIn(name, roll.ARCHETYPES)

    def test_briefs_own_archetype_is_excluded(self):
        for archetype in roll.ARCHETYPES:
            for key in KEYS[:80]:
                self.assertNotIn(archetype, roll.draw_challengers("direction", key, archetype))


class TestSpineCountContract(unittest.TestCase):
    def test_cli_exits_one_and_explains_the_spines_contract(self):
        for raw in ("4", "8", "0", "-1", "six", "", "5.5"):
            result = _run(raw)
            self.assertEqual(result.returncode, 1, f"{raw!r} should be rejected")
            message = result.stderr.lower()
            self.assertIn("spines", message)
            self.assertIn("design_plan", message)

    def test_cli_rejects_an_unknown_archetype(self):
        result = _run("6", "--from", "abc123", "--archetype", "neubrutalist")
        self.assertEqual(result.returncode, 1)
        self.assertIn("minimalist", result.stderr)


class TestStdoutContract(unittest.TestCase):
    """Push-don't-pull: one invocation must place the load-bearing material in
    context, and survive a reader that stops early or starts late."""

    def setUp(self):
        self.result = _run("6", "--from", "8f3c1a20", "--archetype", "editorial")
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        self.out = self.result.stdout

    def test_header_carries_key_scope_and_index(self):
        header = self.out.splitlines()[0]
        self.assertIn("key=8f3c1a20", header)
        self.assertIn("scope=direction", header)
        self.assertIn("spines=6", header)
        self.assertRegex(header, r"ASSIGNED SPINE [3-6]")

    def test_printed_reproduction_command_reproduces_the_output(self):
        line = next(l for l in self.out.splitlines() if l.startswith("reproduce: "))
        command = line[len("reproduce: "):].split()
        self.assertEqual(command[0], "python3")
        replay = subprocess.run([sys.executable, *command[1:]],
                                cwd=SKILL_DIR, capture_output=True, text=True)
        self.assertEqual(replay.returncode, 0, replay.stderr)
        self.assertEqual(replay.stdout, self.out)

    def test_index_restated_on_the_last_line(self):
        last = self.out.strip().splitlines()[-1]
        self.assertIn("restated for truncated readers", last)
        self.assertRegex(last, r"ASSIGNED SPINE [3-6] of 6")

    def test_generated_key_is_printed_and_replayable(self):
        first = _run("7")
        self.assertEqual(first.returncode, 0, first.stderr)
        line = next(l for l in first.stdout.splitlines() if l.startswith("reproduce: "))
        replay = subprocess.run([sys.executable, *line[len("reproduce: "):].split()[1:]],
                                cwd=SKILL_DIR, capture_output=True, text=True)
        self.assertEqual(replay.stdout, first.stdout)

    def test_accepted_manual_key_replays_as_one_argument(self):
        first = _run('5', '--from', 'seed with spaces; literal $value')
        self.assertEqual(first.returncode, 0)
        line = next(line for line in first.stdout.splitlines() if line.startswith('reproduce: '))
        command = shlex.split(line[len('reproduce: '):])
        replay = subprocess.run([sys.executable, *command[1:]], cwd=SKILL_DIR,
                                capture_output=True, text=True)
        self.assertEqual(replay.returncode, 0, replay.stderr)
        self.assertEqual(replay.stdout, first.stdout)


class TestArchetypeBlock(unittest.TestCase):
    """Tier-1 archetype content ships with the two-tier restructure; a name whose
    file is absent degrades to a pointer, never to a crash."""

    def test_missing_tier_one_file_degrades_gracefully(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = roll.ARCHETYPE_DIR
            roll.ARCHETYPE_DIR = Path(tmp)
            try:
                block = roll.archetype_block("editorial")
            finally:
                roll.ARCHETYPE_DIR = original
        self.assertEqual(len(block), 1)
        self.assertIn("not on disk yet", block[0])
        self.assertIn("references/editorial.md", block[0])

    def test_every_archetype_ships_a_tier_one_file(self):
        """The roll's push-don't-pull delivery is only real if every name in
        ARCHETYPES resolves; a missing file silently downgrades the mechanism to
        the pointer branch and the model never sees the DNA."""
        for archetype in roll.ARCHETYPES:
            with self.subTest(archetype=archetype):
                path = roll.ARCHETYPE_DIR / f"{archetype}.md"
                self.assertTrue(path.is_file(), f"references/archetype/{archetype}.md")
                body = path.read_text(encoding="utf-8")
                self.assertTrue(body.strip(), f"{archetype} tier 1 is empty")
                self.assertIn(body.rstrip(), "\n".join(roll.archetype_block(archetype)))

    def test_present_tier_one_file_is_printed_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "brutalist.md").write_text("# Brutalist\n\nDNA line.\n", encoding="utf-8")
            original = roll.ARCHETYPE_DIR
            roll.ARCHETYPE_DIR = directory
            try:
                body = "\n".join(roll.archetype_block("brutalist"))
                report = roll.report(6, "8f3c1a20", "direction", "brutalist", 0)
            finally:
                roll.ARCHETYPE_DIR = original
        self.assertIn("# Brutalist", body)
        self.assertIn("DNA line.", body)
        self.assertIn("DNA line.", report)

    def test_no_archetype_named_still_rolls(self):
        result = _run("5", "--from", "8f3c1a20")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ARCHETYPE — none named", result.stdout)


if __name__ == "__main__":
    unittest.main()
