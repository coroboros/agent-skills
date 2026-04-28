"""Tests for lint_all.py — recursive BRAND-VOICE*.md linter.

Exit contract: 0 all GREEN/YELLOW, 1 at least one RED, 2 no files / not a dir.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "skills" / "brand-voice" / "scripts" / "lint_all.py"
FIXTURES = Path(__file__).parent / "fixtures"


def _run(*args, cwd=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=30,
    )


def _seed(tmpdir: Path, name: str, source: str = "parent-corp.md") -> Path:
    """Copy a fixture into tmpdir under the given name."""
    src = FIXTURES / source
    dest = tmpdir / name
    dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return dest


class TestDiscovery(unittest.TestCase):
    def test_no_brand_voice_files_exits_2(self):
        with tempfile.TemporaryDirectory() as t:
            r = _run(t)
        self.assertEqual(r.returncode, 2)
        self.assertIn("no BRAND-VOICE", r.stderr)

    def test_root_must_be_dir(self):
        with tempfile.NamedTemporaryFile(suffix=".md") as fp:
            r = _run(fp.name)
        self.assertEqual(r.returncode, 2)
        self.assertIn("not a directory", r.stderr)


class TestSingleFile(unittest.TestCase):
    def test_canonical_brand_voice_passes(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            _seed(tmp, "BRAND-VOICE.md")
            r = _run(str(tmp))
        self.assertEqual(r.returncode, 0,
                         f"stderr={r.stderr}\nstdout={r.stdout}")
        self.assertIn("summary:", r.stdout)
        self.assertIn("1 file(s)", r.stdout)


class TestMultipleFiles(unittest.TestCase):
    def test_two_files_both_pass(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            _seed(tmp, "BRAND-VOICE.md")
            _seed(tmp, "BRAND-VOICE-OB.md")
            r = _run(str(tmp))
        self.assertEqual(r.returncode, 0,
                         f"stderr={r.stderr}\nstdout={r.stdout}")
        self.assertIn("BRAND-VOICE.md", r.stdout)
        self.assertIn("BRAND-VOICE-OB.md", r.stdout)
        self.assertIn("2 file(s)", r.stdout)


class TestRedFile(unittest.TestCase):
    def test_red_file_exits_1(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            # replace-without-extends is a known-RED fixture.
            _seed(tmp, "BRAND-VOICE.md", source="replace-without-extends.md")
            r = _run(str(tmp))
        self.assertEqual(r.returncode, 1,
                         f"expected exit 1 for RED file: stdout={r.stdout}\nstderr={r.stderr}")
        self.assertIn("RED", r.stdout)


class TestJSONOutput(unittest.TestCase):
    def test_json_is_array_per_file(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            _seed(tmp, "BRAND-VOICE.md")
            r = _run("--json", str(tmp))
        self.assertEqual(r.returncode, 0,
                         f"stderr={r.stderr}\nstdout={r.stdout}")
        data = json.loads(r.stdout)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        for entry in data:
            self.assertIn("verdict", entry)
            self.assertIn("path", entry)
            self.assertIn("errors", entry)
            self.assertIn("warnings", entry)


if __name__ == "__main__":
    unittest.main()
