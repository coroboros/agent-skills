"""Tests for skills/video-loop/scripts/video-loop.sh.

The script orchestrates ffmpeg/ffprobe to build a seamlessly-looping MP4 + WebM
pair with an optional crossfade. Tests target the script's own logic — argument
parsing, fade-duration validation, exit-code mapping, RESULT schema, post-
condition tolerance — not whether ffmpeg encodes correctly.

Arg-validation tests run unconditionally. Full-pipeline tests (codec detection,
duration delta, exit code 0) are gated on `ffmpeg` + `ffprobe` being on PATH.
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO_ROOT / "skills" / "video-loop" / "scripts"
SCRIPT = SCRIPTS / "video-loop.sh"

HAS_FFMPEG = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


def _run(*args, env=None):
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )


def _parse_result(stdout):
    """Parse `RESULT: key=value` lines into a dict. Later keys overwrite earlier ones."""
    out = {}
    for line in stdout.splitlines():
        if not line.startswith("RESULT: "):
            continue
        payload = line[len("RESULT: ") :]
        # `error=` lines pack multiple key=value pairs on one line; keep the first key.
        for token in payload.split(" "):
            if "=" not in token:
                continue
            k, v = token.split("=", 1)
            out[k] = v
    return out


def _make_input(out_dir, name="in.mp4", duration=4, size="64x64", rate=10):
    """Generate a deterministic test video via ffmpeg's lavfi testsrc."""
    path = out_dir / name
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            f"testsrc=duration={duration}:size={size}:rate={rate}",
            "-pix_fmt",
            "yuv420p",
            str(path),
        ],
        check=True,
        capture_output=True,
        timeout=60,
    )
    return path


class ArgParsingTests(unittest.TestCase):
    """Argument handling — no ffmpeg required."""

    def test_script_exists_and_is_executable(self):
        self.assertTrue(SCRIPT.is_file(), f"missing script: {SCRIPT}")

    def test_no_args_prints_usage_and_exits_2(self):
        r = _run()
        self.assertEqual(r.returncode, 2)
        # `usage()` echoes the header comment; "Usage:" is its first visible line.
        self.assertIn("Usage:", r.stdout + r.stderr)

    def test_help_flag_exits_2_with_usage(self):
        for flag in ("-h", "--help"):
            with self.subTest(flag=flag):
                r = _run(flag)
                self.assertEqual(r.returncode, 2)
                self.assertIn("Usage:", r.stdout + r.stderr)

    def test_missing_input_file_exits_1(self):
        r = _run("/tmp/__video_loop_does_not_exist__.mp4")
        self.assertEqual(r.returncode, 1)
        self.assertIn("input not found", r.stderr)

    def test_unknown_flag_exits_2(self):
        # Use a fake path — the script reaches getopts before -f validation.
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td) / "x.mp4"
            fake.write_bytes(b"")
            r = _run(str(fake), "-Z")
            self.assertEqual(r.returncode, 2)
            self.assertIn("unknown flag", r.stderr)

    def test_flag_missing_value_exits_2(self):
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td) / "x.mp4"
            fake.write_bytes(b"")
            r = _run(str(fake), "-d")
            self.assertEqual(r.returncode, 2)
            self.assertIn("requires a value", r.stderr)


@unittest.skipUnless(HAS_FFMPEG, "ffmpeg/ffprobe required for pipeline tests")
class PipelineValidationTests(unittest.TestCase):
    """Validation that requires ffprobe to read the input duration."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.tmp = Path(cls._tmp.name)
        cls.input = _make_input(cls.tmp, duration=4)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_fade_at_or_above_half_duration_exits_1(self):
        # 4 s input, half = 2 s. Fade = 2 → rejected (`f >= h`).
        out = self.tmp / "out_fade_half"
        out.mkdir(exist_ok=True)
        r = _run(str(self.input), "-d", "2", "-o", str(out))
        self.assertEqual(r.returncode, 1)
        self.assertIn("fade", r.stderr.lower())
        self.assertIn("half", r.stderr.lower())

    def test_fade_above_half_duration_exits_1(self):
        # Belt-and-braces: well past half, still exit 1.
        out = self.tmp / "out_fade_above"
        out.mkdir(exist_ok=True)
        r = _run(str(self.input), "-d", "3", "-o", str(out))
        self.assertEqual(r.returncode, 1)

    def test_no_fade_skips_half_duration_check(self):
        # `-n` bypasses the crossfade branch entirely, so a "huge" -d is moot.
        out = self.tmp / "out_no_fade"
        out.mkdir(exist_ok=True)
        r = _run(str(self.input), "-n", "-d", "999", "-o", str(out))
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        result = _parse_result(r.stdout)
        self.assertEqual(result["no_fade"], "1")

    def test_crf_is_not_range_checked_by_script(self):
        # The script does not range-check CRF (valid H.264 range is 0..51).
        # libx264 silently clamps out-of-range values, so passing -q 100 still
        # yields exit 0. This test pins the contract — if upfront validation
        # is added later, flip the assertion.
        out = self.tmp / "out_bad_crf"
        out.mkdir(exist_ok=True)
        r = _run(str(self.input), "-d", "0.5", "-q", "100", "-o", str(out))
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        result = _parse_result(r.stdout)
        # The bogus CRF value is still echoed back through the pipeline,
        # confirming the script forwarded it untouched.
        self.assertEqual(result["mp4_codec"], "h264")


@unittest.skipUnless(HAS_FFMPEG, "ffmpeg/ffprobe required for pipeline tests")
class FullPipelineTests(unittest.TestCase):
    """End-to-end runs that exercise codec detection, RESULT schema, exit 0."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.tmp = Path(cls._tmp.name)
        cls.input = _make_input(cls.tmp, duration=4)
        cls.out = cls.tmp / "out"
        cls.out.mkdir(exist_ok=True)
        cls.proc = _run(str(cls.input), "-d", "0.5", "-o", str(cls.out))
        cls.result = _parse_result(cls.proc.stdout)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_pipeline_exits_0_on_success(self):
        self.assertEqual(self.proc.returncode, 0, msg=self.proc.stderr)

    def test_result_schema_has_required_keys(self):
        expected = {
            "input_bytes",
            "duration_seconds",
            "fade_seconds",
            "no_fade",
            "mp4_path",
            "mp4_bytes",
            "mp4_codec",
            "mp4_duration",
            "expected_duration",
            "duration_delta",
            "webm_path",
            "webm_bytes",
            "webm_codec",
            "ok",
        }
        missing = expected - self.result.keys()
        self.assertFalse(missing, f"missing RESULT keys: {sorted(missing)}")
        self.assertEqual(self.result["ok"], "true")

    def test_codec_detection_h264_and_vp9(self):
        self.assertEqual(self.result["mp4_codec"], "h264")
        self.assertEqual(self.result["webm_codec"], "vp9")

    def test_duration_delta_within_tolerance(self):
        # Tolerance is 0.2 s; clean input/output should be far below that.
        self.assertLessEqual(float(self.result["duration_delta"]), 0.2)

    def test_expected_duration_equals_input_minus_fade(self):
        # 4 s input − 0.5 s fade = 3.5 s expected.
        self.assertAlmostEqual(float(self.result["expected_duration"]), 3.5, places=2)

    def test_output_filenames_differ_from_input(self):
        # No explicit self-overwrite guard exists, but the `-opt.mp4` / `.webm`
        # suffix scheme means an `*.mp4` input never collides with its output.
        mp4 = self.result["mp4_path"]
        webm = self.result["webm_path"]
        self.assertNotEqual(os.path.abspath(mp4), os.path.abspath(str(self.input)))
        self.assertNotEqual(os.path.abspath(webm), os.path.abspath(str(self.input)))
        self.assertTrue(mp4.endswith("-opt.mp4"))
        self.assertTrue(webm.endswith(".webm"))


if __name__ == "__main__":
    unittest.main()
