"""Tests for audio-loop.sh — CLI surface, validation, exit codes, output schema.

The script wraps ffmpeg/ffprobe to produce a seamless audio loop. These tests
exercise the script's own logic — argument parsing, validation, exit-code
mapping, and the RESULT key=value schema — not ffmpeg correctness.

Tests that need a real audio fixture skip gracefully when ffmpeg is missing.
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO_ROOT / "skills" / "audio-loop" / "scripts"
SCRIPT = SCRIPTS / "audio-loop.sh"

HAS_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


def _run(*args, env=None):
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )


def _parse_results(stdout):
    """Parse RESULT: key=value lines into a dict."""
    out = {}
    for line in stdout.splitlines():
        if not line.startswith("RESULT: "):
            continue
        body = line[len("RESULT: ") :]
        if "=" in body:
            k, _, v = body.partition("=")
            out[k.strip()] = v.strip()
    return out


def _make_wav(path, duration=1, rate=44100, channels=2, freq=440):
    """Generate a tiny sine-wave WAV via ffmpeg. Caller must check HAS_FFMPEG."""
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency={freq}:duration={duration}:sample_rate={rate}",
            "-ac",
            str(channels),
            str(path),
        ],
        check=True,
        timeout=30,
    )


class TestScriptExists(unittest.TestCase):
    """Sanity — the script lives where the tests expect."""

    def test_script_present(self):
        self.assertTrue(SCRIPT.is_file(), f"script missing: {SCRIPT}")

    def test_script_executable(self):
        self.assertTrue(os.access(SCRIPT, os.X_OK), f"script not executable: {SCRIPT}")


class TestUsage(unittest.TestCase):
    """Argument parsing — usage and help paths exit 2 with usage text on stdout."""

    def test_no_args_prints_usage_and_exits_2(self):
        result = _run()
        self.assertEqual(result.returncode, 2)
        self.assertIn("audio-loop.sh", result.stdout)
        self.assertIn("Usage:", result.stdout)

    def test_dash_h_prints_usage_and_exits_2(self):
        result = _run("-h")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Usage:", result.stdout)

    def test_double_dash_help_prints_usage_and_exits_2(self):
        result = _run("--help")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Usage:", result.stdout)


class TestInputValidation(unittest.TestCase):
    """Input file validation — exit 1 with a clear stderr message."""

    def test_missing_input_exits_1(self):
        result = _run("/definitely/not/a/real/path.wav")
        self.assertEqual(result.returncode, 1)
        self.assertIn("input not found", result.stderr)
        self.assertIn("/definitely/not/a/real/path.wav", result.stderr)


class TestFlagParsing(unittest.TestCase):
    """getopts surface — unknown flags and missing flag values exit 2."""

    def test_unknown_flag_exits_2(self):
        # Use a real file so the input check passes and we hit getopts.
        with tempfile.NamedTemporaryFile(suffix=".wav") as fp:
            result = _run(fp.name, "-z")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown flag", result.stderr)

    def test_missing_flag_value_exits_2(self):
        with tempfile.NamedTemporaryFile(suffix=".wav") as fp:
            result = _run(fp.name, "-t")
        self.assertEqual(result.returncode, 2)
        self.assertIn("requires a value", result.stderr)


class TestSelfOverwriteGuard(unittest.TestCase):
    """The script refuses to write a FLAC over the input FLAC in the same dir."""

    @unittest.skipUnless(HAS_FFMPEG, "ffmpeg/ffprobe not installed")
    def test_self_overwrite_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "loop.flac"
            _make_wav(src.with_suffix(".wav"))
            # Re-encode the WAV to a real FLAC so input == would-be output.
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-i",
                    str(src.with_suffix(".wav")),
                    "-c:a",
                    "flac",
                    str(src),
                ],
                check=True,
                timeout=30,
            )
            result = _run(str(src))
            self.assertEqual(result.returncode, 1)
            self.assertIn("would overwrite input", result.stderr)
            self.assertIn(str(src), result.stderr)


class TestInvalidLufsTarget(unittest.TestCase):
    """Non-numeric LUFS targets are rejected downstream by ffmpeg → script fails non-zero.

    The script does not parse `-t` itself; it forwards the value to loudnorm.
    Under `set -euo pipefail`, an ffmpeg failure surfaces as a non-zero exit
    distinct from the success path.
    """

    @unittest.skipUnless(HAS_FFMPEG, "ffmpeg/ffprobe not installed")
    def test_non_numeric_lufs_target_fails(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.wav"
            _make_wav(src)
            outdir = Path(td) / "out"
            outdir.mkdir()
            result = _run(str(src), "-t", "abc", "-o", str(outdir))
            self.assertNotEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            # No final ok=true should be emitted since loudnorm aborted.
            results = _parse_results(result.stdout)
            self.assertNotEqual(results.get("ok"), "true")
            # outdir must not contain a .flac — the encode step never ran.
            flac_files = list(outdir.glob("*.flac"))
            self.assertEqual(flac_files, [],
                             f"loudnorm-abort left .flac in outdir: {flac_files}")


class TestSuccessfulRunSchema(unittest.TestCase):
    """End-to-end run on a known-good source — verify exit 0, RESULT schema,
    LUFS post-condition math, and output existence."""

    @unittest.skipUnless(HAS_FFMPEG, "ffmpeg/ffprobe not installed")
    def test_full_pipeline_emits_full_schema(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.wav"
            _make_wav(src, duration=2)
            outdir = Path(td) / "out"
            outdir.mkdir()
            result = _run(str(src), "-o", str(outdir))
            self.assertEqual(
                result.returncode,
                0,
                msg=f"stdout={result.stdout}\nstderr={result.stderr}",
            )
            results = _parse_results(result.stdout)

            # Mono-and-stereo-shared keys.
            shared_keys = {
                "input_path",
                "input_bytes",
                "duration_seconds",
                "sample_rate",
                "channels",
                "lufs_target",
                "lufs_out",
                "lufs_delta",
                "peak_out",
                "output_path",
                "output_bytes",
                "ok",
            }
            self.assertTrue(
                shared_keys.issubset(results.keys()),
                msg=f"missing keys: {shared_keys - results.keys()}",
            )

            # Stereo source → per-channel keys + balance flag.
            stereo_keys = {
                "input_rms_left",
                "input_rms_right",
                "input_rms_delta",
                "balance_corrected",
                "output_rms_left",
                "output_rms_right",
            }
            self.assertEqual(results["channels"], "2")
            self.assertTrue(
                stereo_keys.issubset(results.keys()),
                msg=f"missing stereo keys: {stereo_keys - results.keys()}",
            )

            # ok=true is the success sentinel.
            self.assertEqual(results["ok"], "true")

            # Default LUFS target + post-condition tolerance (≤ 1.0 LUFS).
            self.assertEqual(results["lufs_target"], "-28")
            self.assertLessEqual(float(results["lufs_delta"]), 1.0)

            # Output file actually exists with the documented .flac extension.
            out_path = Path(results["output_path"])
            self.assertTrue(out_path.is_file())
            self.assertEqual(out_path.suffix, ".flac")
            self.assertEqual(int(results["output_bytes"]), out_path.stat().st_size)

    @unittest.skipUnless(HAS_FFMPEG, "ffmpeg/ffprobe not installed")
    def test_custom_lufs_target_propagates(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.wav"
            _make_wav(src, duration=2)
            outdir = Path(td) / "out"
            outdir.mkdir()
            result = _run(str(src), "-t", "-20", "-o", str(outdir))
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            results = _parse_results(result.stdout)
            self.assertEqual(results["lufs_target"], "-20")
            # Loudnorm converges within the documented ±1 LUFS window.
            self.assertLessEqual(float(results["lufs_delta"]), 1.0)

    @unittest.skipUnless(HAS_FFMPEG, "ffmpeg/ffprobe not installed")
    def test_balance_correction_disabled_with_dash_b(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.wav"
            _make_wav(src, duration=1)
            outdir = Path(td) / "out"
            outdir.mkdir()
            result = _run(str(src), "-B", "-o", str(outdir))
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            results = _parse_results(result.stdout)
            # -B forces balance_corrected=0 regardless of the L/R delta.
            self.assertEqual(results["balance_corrected"], "0")


class TestExitCodeMapping(unittest.TestCase):
    """The header documents exits 0/1/3 — verify the source declares them."""

    def test_documented_exit_codes(self):
        text = SCRIPT.read_text()
        # Exit code documentation block.
        self.assertIn("Exit codes:", text)
        self.assertIn("0   success", text)
        self.assertIn("1   input / tool validation error", text)
        self.assertIn("3   encoded successfully but post-condition check failed", text)
        # Actual `exit 1` and `exit 3` statements present in the source.
        self.assertIn("exit 1", text)
        self.assertIn("exit 3", text)

    def test_post_condition_uses_one_lufs_tolerance(self):
        """The post-condition check uses ±1 LUFS — confirm the literal is in source.

        Catches regressions if someone widens the tolerance silently.
        """
        text = SCRIPT.read_text()
        self.assertIn("d > 1.0", text)


if __name__ == "__main__":
    unittest.main()
