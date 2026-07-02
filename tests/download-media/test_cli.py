"""Tests for download-media.sh — the wrapper's own logic.

Covers flag parsing, flag→yt-dlp argv composition, URL validation, slug
derivation, the RESULT schema, destination layout, manifest cleanup, and
the exit-code contract (2 usage, 3 ffmpeg-required, 127 not installed).

We do NOT test the wrapped `yt-dlp` CLI. A shim on PATH records the argv
the wrapper composed and honors `--print-to-file after_move:filepath` by
writing fake final paths to the manifest.
"""

import os
import re
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "skills" / "download-media" / "scripts" / "download-media.sh"

FAKE_PATH = "/fake/dest/Video Title [abc123].mp4"

SHIM_BODY = """#!/usr/bin/env bash
# Fake `yt-dlp` for wrapper tests. Records argv to $YTDLP_SHIM_ARGS, honors
# `--print-to-file after_move:filepath <file>` by appending $YTDLP_SHIM_FILES
# fake paths (default 1). With YTDLP_SHIM_FAIL=1 exits non-zero AFTER the
# manifest write (so we can verify the wrapper's trap cleans up).
set -e
if [[ -n "${YTDLP_SHIM_ARGS:-}" ]]; then
  printf '%s\\n' "$@" > "$YTDLP_SHIM_ARGS"
fi
manifest=""
prev=""
for a in "$@"; do
  if [[ "$prev" == "after_move:filepath" ]]; then manifest="$a"; fi
  prev="$a"
done
if [[ -n "$manifest" ]]; then
  n="${YTDLP_SHIM_FILES:-1}"
  for ((i = 0; i < n; i++)); do
    echo "FAKE_PATH" >> "$manifest"
  done
fi
if [[ "${YTDLP_SHIM_FAIL:-0}" == "1" ]]; then
  echo "shim: forced failure" >&2
  exit 9
fi
""".replace("FAKE_PATH", FAKE_PATH)


def _project(root: Path) -> str:
    """Python mirror of the script's bash kebab (basename | lower | -cs | strip)."""
    return re.sub(r"[^a-z0-9]+", "-", root.name.lower()).strip("-")


def _run(*args, env=None, cwd=None):
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        env=env,
        cwd=cwd,
        timeout=30,
    )


class TestNoYtDlp(unittest.TestCase):
    """If `yt-dlp` is not on PATH, the wrapper must exit 127 with the
    install hint, regardless of args."""

    def test_exit_127_when_missing(self):
        env = os.environ.copy()
        env["PATH"] = "/usr/bin:/bin"
        if shutil.which("yt-dlp", path=env["PATH"]):
            self.skipTest("yt-dlp unexpectedly present in /usr/bin:/bin")
        r = _run("https://example.com/v", env=env)
        self.assertEqual(r.returncode, 127)
        self.assertIn("not installed", r.stderr)
        self.assertIn("brew install yt-dlp", r.stderr)


class _ShimCase(unittest.TestCase):
    """Base: a fake `yt-dlp` (and optionally `ffmpeg`) shim dir on a pinned
    PATH, an isolated HOME, and argv capture."""

    with_ffmpeg = True

    @classmethod
    def setUpClass(cls):
        cls.shim_dir = Path(tempfile.mkdtemp(prefix="ytdlp-shim-"))
        for name, body in (("yt-dlp", SHIM_BODY), ("ffmpeg", "#!/usr/bin/env bash\nexit 0\n")):
            if name == "ffmpeg" and not cls.with_ffmpeg:
                continue
            shim = cls.shim_dir / name
            shim.write_text(body)
            shim.chmod(shim.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.shim_dir, ignore_errors=True)

    def setUp(self):
        self.cwd = Path(tempfile.mkdtemp(prefix="dlm-cwd-"))
        self.home = Path(tempfile.mkdtemp(prefix="dlm-home-"))
        self.argv_file = self.cwd / "argv.txt"

    def tearDown(self):
        shutil.rmtree(self.cwd, ignore_errors=True)
        shutil.rmtree(self.home, ignore_errors=True)

    def _run(self, *args, **env_extra):
        env = os.environ.copy()
        # Pinned PATH: shim first, then system bins only — deterministic
        # yt-dlp/ffmpeg presence regardless of the host machine.
        env["PATH"] = f"{self.shim_dir}{os.pathsep}/usr/bin:/bin"
        env["HOME"] = str(self.home)
        env["GIT_CEILING_DIRECTORIES"] = str(self.cwd.parent)
        env["YTDLP_SHIM_ARGS"] = str(self.argv_file)
        env.update(env_extra)
        return _run(*args, env=env, cwd=str(self.cwd))

    def _argv(self):
        return self.argv_file.read_text().splitlines()


class TestUsageErrors(_ShimCase):
    def test_no_url_exits_2(self):
        r = self._run()
        self.assertEqual(r.returncode, 2)
        self.assertIn("URL required", r.stderr)

    def test_unknown_flag_exits_2(self):
        r = self._run("-z", "https://example.com/v")
        self.assertEqual(r.returncode, 2)
        # Silent getopts: the offending letter lands in $OPTARG, not a bare `?`.
        self.assertIn("unknown flag -z", r.stderr)

    def test_missing_flag_value_exits_2(self):
        r = self._run("-u")
        self.assertEqual(r.returncode, 2)
        self.assertIn("-u requires a value", r.stderr)

    def test_non_url_exits_2(self):
        r = self._run("notaurl")
        self.assertEqual(r.returncode, 2)
        self.assertIn("not a URL", r.stderr)

    def test_bad_height_exits_2(self):
        r = self._run("-r", "tall", "https://example.com/v")
        self.assertEqual(r.returncode, 2)
        self.assertIn("-r takes a height", r.stderr)

    def test_audio_with_height_exits_2(self):
        r = self._run("-a", "-r", "720", "https://example.com/v")
        self.assertEqual(r.returncode, 2)
        self.assertIn("video flags", r.stderr)

    def test_audio_with_best_exits_2(self):
        r = self._run("-a", "-b", "https://example.com/v")
        self.assertEqual(r.returncode, 2)
        self.assertIn("video flags", r.stderr)


class TestArgvComposition(_ShimCase):
    URL = "https://example.com/v"

    def test_default_is_single_video_mp4_preset(self):
        r = self._run(self.URL)
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        argv = self._argv()
        self.assertIn("--no-playlist", argv)
        self.assertIn("mp4", argv[argv.index("-t") + 1])
        self.assertIn("--print-to-file", argv)
        self.assertEqual(argv[-1], self.URL)

    def test_audio_uses_mp3_preset(self):
        r = self._run("-a", self.URL)
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        argv = self._argv()
        self.assertEqual(argv[argv.index("-t") + 1], "mp3")

    def test_best_skips_preset(self):
        r = self._run("-b", self.URL)
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        self.assertNotIn("-t", self._argv())

    def test_playlist_flag_and_template(self):
        r = self._run("-p", self.URL)
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        argv = self._argv()
        self.assertIn("--yes-playlist", argv)
        self.assertNotIn("--no-playlist", argv)
        template = argv[argv.index("-o") + 1]
        self.assertIn("%(playlist_index)03d", template)

    def test_height_becomes_format_filter(self):
        r = self._run("-r", "720", self.URL)
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        argv = self._argv()
        self.assertEqual(argv[argv.index("-f") + 1], "bv*[height<=720]+ba/b[height<=720]")

    def test_section_gets_time_range_prefix(self):
        r = self._run("-c", "10:15-12:30", self.URL)
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        argv = self._argv()
        self.assertEqual(argv[argv.index("--download-sections") + 1], "*10:15-12:30")

    def test_subs_flags(self):
        r = self._run("-u", "en.*,fr", self.URL)
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        argv = self._argv()
        self.assertIn("--write-subs", argv)
        self.assertIn("--write-auto-subs", argv)
        self.assertEqual(argv[argv.index("--sub-langs") + 1], "en.*,fr")

    def test_passthrough_appended_after_url(self):
        r = self._run(self.URL, "--sponsorblock-remove", "sponsor")
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        argv = self._argv()
        self.assertEqual(argv[-2:], ["--sponsorblock-remove", "sponsor"])
        self.assertEqual(argv[argv.index("--sponsorblock-remove") - 1], self.URL)

    def test_info_mode_lists_formats_only(self):
        r = self._run("-i", self.URL)
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        argv = self._argv()
        self.assertEqual(argv[:2], ["-F", "--no-playlist"])
        self.assertNotIn("--print-to-file", argv)
        self.assertNotIn("RESULT:", r.stdout)


class TestDestinationAndResults(_ShimCase):
    URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    def test_default_dest_under_global_output(self):
        r = self._run(self.URL)
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        dest = (self.home / ".agents" / "output" / _project(self.cwd)
                / "download-media" / "v-dqw4w9wgxcq")
        self.assertIn(f"RESULT: dest={dest}", r.stdout)
        self.assertTrue(dest.is_dir())
        argv = self._argv()
        self.assertEqual(argv[argv.index("-P") + 1], str(dest))
        # De-pollution: nothing written inside the project tree except argv capture.
        self.assertFalse((self.cwd / ".agents").exists())

    def test_dest_override(self):
        custom = self.cwd / "media"
        r = self._run("-d", str(custom), self.URL)
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        self.assertIn(f"RESULT: dest={custom}", r.stdout)
        argv = self._argv()
        self.assertEqual(argv[argv.index("-P") + 1], str(custom))
        self.assertFalse((self.home / ".agents").exists())

    def test_result_schema_single_file(self):
        r = self._run(self.URL)
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        self.assertIn(f"RESULT: path={FAKE_PATH}", r.stdout)
        self.assertIn("RESULT: files=1", r.stdout)
        self.assertIn("RESULT: slug=v-dqw4w9wgxcq", r.stdout)

    def test_result_schema_multi_file(self):
        r = self._run(self.URL, YTDLP_SHIM_FILES="3")
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        self.assertEqual(r.stdout.count("RESULT: path="), 3)
        self.assertIn("RESULT: files=3", r.stdout)


class TestSlugDerivation(_ShimCase):
    def _slug(self, url):
        r = self._run(url)
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        line = next(l for l in r.stdout.splitlines() if l.startswith("RESULT: slug="))
        return line.split("=", 1)[1]

    def test_short_link_uses_id(self):
        self.assertEqual(self._slug("https://youtu.be/dQw4w9WgXcQ"), "dqw4w9wgxcq")

    def test_watch_url_falls_back_to_query(self):
        self.assertEqual(
            self._slug("https://www.youtube.com/watch?v=Abc_123"), "v-abc-123"
        )

    def test_path_segment_with_trailing_slash(self):
        self.assertEqual(self._slug("https://vimeo.com/123456789/"), "123456789")

    def test_extractor_prefix_is_accepted(self):
        self.assertEqual(self._slug("ytsearch1:lofi hip hop"), "ytsearch1-lofi-hip-hop")

    def test_slug_capped_at_five_segments(self):
        slug = self._slug("https://site.com/one-two-three-four-five-six-seven")
        self.assertEqual(slug, "one-two-three-four-five")

    def test_bare_domain_uses_host(self):
        """No path segment → the host itself is the last segment; the `media`
        fallback is reserved for a slug that kebabs to empty."""
        self.assertEqual(self._slug("https://example.com/"), "example-com")


class TestManifestCleanup(_ShimCase):
    URL = "https://example.com/v"

    def _leaked(self):
        return set(Path(tempfile.gettempdir()).glob("download-media.*"))

    def test_manifest_cleaned_on_success(self):
        before = self._leaked()
        r = self._run(self.URL)
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        self.assertEqual(self._leaked() - before, set(), "wrapper leaked its manifest")

    def test_partial_failure_keeps_results_and_propagates_exit(self):
        """yt-dlp's default --no-abort-on-error skips bad playlist entries but
        exits non-zero; downloaded files must still be reported. The shim
        writes its manifest entry BEFORE failing to model exactly that."""
        before = self._leaked()
        r = self._run(self.URL, YTDLP_SHIM_FAIL="1")
        self.assertEqual(r.returncode, 9, "yt-dlp exit code must propagate")
        self.assertIn(f"RESULT: path={FAKE_PATH}", r.stdout)
        self.assertIn("RESULT: files=1", r.stdout)
        self.assertEqual(self._leaked() - before, set(), "wrapper leaked its manifest")


class TestNoFfmpeg(_ShimCase):
    """yt-dlp present, ffmpeg absent — degraded-mode contract."""

    with_ffmpeg = False
    URL = "https://example.com/v"

    def setUp(self):
        super().setUp()
        if shutil.which("ffmpeg", path="/usr/bin:/bin"):
            self.skipTest("ffmpeg unexpectedly present in /usr/bin:/bin")

    def test_audio_requires_ffmpeg_exit_3(self):
        r = self._run("-a", self.URL)
        self.assertEqual(r.returncode, 3)
        self.assertIn("need ffmpeg", r.stderr)

    def test_section_requires_ffmpeg_exit_3(self):
        r = self._run("-c", "0:10-0:20", self.URL)
        self.assertEqual(r.returncode, 3)
        self.assertIn("need ffmpeg", r.stderr)

    def test_video_warns_and_skips_mp4_preset(self):
        r = self._run(self.URL)
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        self.assertIn("WARN: ffmpeg not found", r.stderr)
        self.assertNotIn("-t", self._argv())

    def test_info_mode_skips_ffmpeg_gate(self):
        """`-i` downloads nothing — it must not die on the -a ffmpeg check."""
        r = self._run("-i", "-a", self.URL)
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        self.assertEqual(self._argv()[0], "-F")


if __name__ == "__main__":
    unittest.main()
