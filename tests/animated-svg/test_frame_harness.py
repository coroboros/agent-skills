"""Tests for skills/animated-svg/scripts/frame_harness.py.

The harness writes frozen-frame HTML pages for an animated SVG. Tests pin
the generator's contract — page count, freeze mechanics present in the
output, RESULT schema, input validation — not what a browser renders.
"""

import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "skills" / "animated-svg" / "scripts" / "frame_harness.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
PASS_SVG = FIXTURES / "smil-css-pass.svg"


def _run(*args):
    return subprocess.run(
        ["python3", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


def _frames(stdout):
    """Parse `RESULT: frame=<path> t=<sec>` lines into [(path, t)]."""
    out = []
    for line in stdout.splitlines():
        if not line.startswith("RESULT: frame="):
            continue
        rest = line[len("RESULT: frame="):]
        path, _, t = rest.rpartition(" t=")
        out.append((Path(path), t))
    return out


class TestGeneration(unittest.TestCase):
    def test_one_page_per_timestamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = _run(str(PASS_SVG), "-t", "0,0.75,1.5", "-o", tmp)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            frames = _frames(proc.stdout)
            self.assertEqual(len(frames), 3)
            self.assertEqual([t for _, t in frames], ["0", "0.75", "1.5"])
            for path, _ in frames:
                self.assertTrue(path.is_file(), f"missing page: {path}")

    def test_page_freezes_smil_and_waapi(self):
        with tempfile.TemporaryDirectory() as tmp:
            _run(str(PASS_SVG), "-t", "0.75", "-o", tmp)
            html = (Path(tmp) / "frame-t0.75.html").read_text(encoding="utf-8")
            self.assertIn("pauseAnimations", html)
            self.assertIn("setCurrentTime", html)
            self.assertIn("getAnimations", html)
            self.assertIn("const T = 0.75;", html)

    def test_page_inlines_the_svg(self):
        with tempfile.TemporaryDirectory() as tmp:
            _run(str(PASS_SVG), "-t", "0", "-o", tmp)
            html = (Path(tmp) / "frame-t0.html").read_text(encoding="utf-8")
            self.assertIn('xmlns="http://www.w3.org/2000/svg"', html)
            self.assertIn("stroke-dashoffset", html)

    def test_bg_and_size_options_land_in_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            _run(str(PASS_SVG), "-t", "0", "-o", tmp, "--bg", "#0d1117", "--size", "400")
            html = (Path(tmp) / "frame-t0.html").read_text(encoding="utf-8")
            self.assertIn("background: #0d1117", html)
            self.assertIn("width: 400px", html)


class TestValidation(unittest.TestCase):
    def test_missing_svg_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = _run(str(FIXTURES / "does-not-exist.svg"), "-t", "0", "-o", tmp)
        self.assertEqual(proc.returncode, 2)

    def test_garbage_times_exit_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = _run(str(PASS_SVG), "-t", "abc", "-o", tmp)
        self.assertEqual(proc.returncode, 2)

    def test_negative_times_exit_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = _run(str(PASS_SVG), "-t", "0,-1", "-o", tmp)
        self.assertEqual(proc.returncode, 2)

    def test_empty_times_exit_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = _run(str(PASS_SVG), "-t", ",", "-o", tmp)
        self.assertEqual(proc.returncode, 2)

    def test_non_utf8_input_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "binary.svg"
            bad.write_bytes(b"\x89PNG\r\n\x1a\n\xff\xfe")
            proc = _run(str(bad), "-t", "0", "-o", tmp)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("RESULT: error=", proc.stdout)

    def test_duplicate_times_deduped(self):
        # `1` and `1.0` map to the same page — one file, one RESULT line.
        with tempfile.TemporaryDirectory() as tmp:
            proc = _run(str(PASS_SVG), "-t", "1,1.0", "-o", tmp)
            self.assertEqual(proc.returncode, 0)
            self.assertEqual(len(_frames(proc.stdout)), 1)
            self.assertEqual(len(list(Path(tmp).glob("frame-*.html"))), 1)


if __name__ == "__main__":
    unittest.main()
