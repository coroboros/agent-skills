"""Tests for skills/claude-md/scripts/init_structure.sh.

Three modes (single | hybrid | rules-only) create different file sets.
Idempotent — collision without --force exits 1; --force overwrites.
"""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "skills" / "claude-md" / "scripts" / "init_structure.sh"

BASH = shutil.which("bash") or "/bin/bash"


def _run(*args):
    return subprocess.run(
        [BASH, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


class TestArgs(unittest.TestCase):
    def test_no_args_exits_2(self):
        r = _run()
        self.assertEqual(r.returncode, 2)

    def test_unknown_mode_exits_1(self):
        with tempfile.TemporaryDirectory() as t:
            r = _run("nope", t)
        self.assertEqual(r.returncode, 1)
        self.assertIn("mode must be", r.stderr)

    def test_missing_target_dir_exits_1(self):
        r = _run("single", "/tmp/_does_not_exist_init_structure_humanize")
        self.assertEqual(r.returncode, 1)
        self.assertIn("does not exist", r.stderr)


class TestSingleMode(unittest.TestCase):
    def test_creates_only_claude_md(self):
        with tempfile.TemporaryDirectory() as t:
            r = _run("single", t)
            self.assertEqual(r.returncode, 0,
                             f"stderr={r.stderr}\nstdout={r.stdout}")
            tmp = Path(t)
            self.assertTrue((tmp / "CLAUDE.md").is_file())
            # Single mode does NOT create .claude/rules/.
            self.assertFalse((tmp / ".claude").exists())
            self.assertIn("RESULT: wrote=", r.stdout)
            self.assertIn("CLAUDE.md", r.stdout)
            self.assertIn("RESULT: ok=true", r.stdout)


class TestHybridMode(unittest.TestCase):
    def test_creates_claude_md_plus_rules(self):
        with tempfile.TemporaryDirectory() as t:
            r = _run("hybrid", t)
            self.assertEqual(r.returncode, 0,
                             f"stderr={r.stderr}\nstdout={r.stdout}")
            tmp = Path(t)
            self.assertTrue((tmp / "CLAUDE.md").is_file())
            self.assertTrue((tmp / ".claude" / "rules" / "style.md").is_file())
            self.assertTrue((tmp / ".claude" / "rules" / "testing.md").is_file())
            # CLAUDE.md must reference the rule files via @-imports.
            content = (tmp / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertIn("@.claude/rules/style.md", content)
            self.assertIn("@.claude/rules/testing.md", content)


class TestRulesOnlyMode(unittest.TestCase):
    def test_creates_only_rules(self):
        with tempfile.TemporaryDirectory() as t:
            r = _run("rules-only", t)
            self.assertEqual(r.returncode, 0,
                             f"stderr={r.stderr}\nstdout={r.stdout}")
            tmp = Path(t)
            self.assertFalse((tmp / "CLAUDE.md").exists())
            self.assertTrue((tmp / ".claude" / "rules" / "style.md").is_file())
            self.assertTrue((tmp / ".claude" / "rules" / "testing.md").is_file())


class TestIdempotency(unittest.TestCase):
    def test_re_run_without_force_exits_1(self):
        with tempfile.TemporaryDirectory() as t:
            r1 = _run("single", t)
            self.assertEqual(r1.returncode, 0)
            r2 = _run("single", t)
            self.assertEqual(r2.returncode, 1)
            self.assertIn("RESULT: skipped=", r2.stdout)
            self.assertIn("ok=partial", r2.stdout)

    def test_re_run_with_force_overwrites(self):
        with tempfile.TemporaryDirectory() as t:
            r1 = _run("single", t)
            self.assertEqual(r1.returncode, 0)
            tmp = Path(t)
            (tmp / "CLAUDE.md").write_text("// tampered\n")
            r2 = _run("single", t, "--force")
            self.assertEqual(r2.returncode, 0,
                             f"stderr={r2.stderr}\nstdout={r2.stdout}")
            self.assertNotEqual((tmp / "CLAUDE.md").read_text(),
                                "// tampered\n")
            self.assertIn("RESULT: ok=true", r2.stdout)


if __name__ == "__main__":
    unittest.main()
