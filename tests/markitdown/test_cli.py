"""Tests for markitdown.sh — the wrapper's own logic.

Covers flag parsing, URL vs file detection, slug normalization (lowercase,
non-alphanum→dash, max 5 segments), RESULT schema, save-path layout, temp
file cleanup, and the env-var requirement for `-d`.

We do NOT test the wrapped `markitdown` CLI (Microsoft's). For arg-parsing
tests we shim `markitdown` on PATH so the wrapper proceeds past the install
check; the shim writes a known payload to whatever path is passed via `-o`.
"""

import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO_ROOT / "skills" / "markitdown" / "scripts"
SCRIPT = SCRIPTS / "markitdown.sh"


SHIM_PAYLOAD = "# shim output\n"

SHIM_BODY = """#!/usr/bin/env bash
# Fake `markitdown` for wrapper tests. Parses -o <path>, writes a fixed
# payload, exits 0 by default. With MARKITDOWN_SHIM_FAIL=1 exits non-zero
# AFTER creating the temp file (so we can verify the wrapper's trap runs).
set -e
out=""
fail="${MARKITDOWN_SHIM_FAIL:-0}"
list_plugins=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    -o) out="$2"; shift 2 ;;
    --list-plugins) list_plugins=1; shift ;;
    *) shift ;;
  esac
done
if [[ $list_plugins -eq 1 ]]; then
  echo "shim: no plugins"
  exit 0
fi
if [[ -n "$out" ]]; then
  printf '%s' "PAYLOAD" > "$out"
fi
if [[ "$fail" == "1" ]]; then
  echo "shim: forced failure" >&2
  exit 3
fi
""".replace("PAYLOAD", SHIM_PAYLOAD)


def _run(*args, env=None, cwd=None):
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        env=env,
        cwd=cwd,
    )


def _shim_env(shim_dir, **extra):
    """Return an env that puts the shim first on PATH and inherits HOME etc."""
    env = os.environ.copy()
    env["PATH"] = f"{shim_dir}{os.pathsep}{env.get('PATH', '')}"
    # Wipe Azure endpoint by default so -d tests are deterministic.
    env.pop("MARKITDOWN_DOCINTEL_ENDPOINT", None)
    env.update(extra)
    return env


def _empty_path_env(**extra):
    """Env with a PATH that does NOT contain markitdown (forces exit 127)."""
    env = os.environ.copy()
    # Keep only system bins; ensure markitdown isn't here.
    env["PATH"] = "/usr/bin:/bin"
    env.pop("MARKITDOWN_DOCINTEL_ENDPOINT", None)
    env.update(extra)
    # Sanity — if the host has markitdown in /usr/bin we cannot test exit 127
    # this way. The dedicated test below skips itself if so.
    return env


class TestNoMarkitdown(unittest.TestCase):
    """If `markitdown` is not on PATH, the wrapper must exit 127 with the
    install hint, regardless of args."""

    def test_exit_127_when_missing(self):
        env = _empty_path_env()
        if shutil.which("markitdown", path=env["PATH"]):
            self.skipTest("markitdown unexpectedly present in /usr/bin:/bin")
        r = _run("anything.pdf", env=env)
        self.assertEqual(r.returncode, 127)
        self.assertIn("not installed", r.stderr)
        self.assertIn("pip install", r.stderr)


class TestShimmedWrapper(unittest.TestCase):
    """Tests using a fake `markitdown` shim on PATH so the wrapper passes the
    install check and we can exercise its own logic."""

    @classmethod
    def setUpClass(cls):
        cls.shim_dir = Path(tempfile.mkdtemp(prefix="markitdown-shim-"))
        shim = cls.shim_dir / "markitdown"
        shim.write_text(SHIM_BODY)
        shim.chmod(shim.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.shim_dir, ignore_errors=True)

    def setUp(self):
        # Each test runs in its own cwd so `.claude/output/...` is isolated.
        self.cwd = Path(tempfile.mkdtemp(prefix="markitdown-cwd-"))

    def tearDown(self):
        shutil.rmtree(self.cwd, ignore_errors=True)

    def _run(self, *args, **env_extra):
        return _run(*args, env=_shim_env(self.shim_dir, **env_extra), cwd=str(self.cwd))

    # --- arg-parsing -------------------------------------------------------

    def test_no_args_exits_2(self):
        r = self._run()
        self.assertEqual(r.returncode, 2)
        self.assertIn("input required", r.stderr)

    def test_unknown_flag_exits_2(self):
        r = self._run("-z", "foo.txt")
        self.assertEqual(r.returncode, 2)
        # getopts emits its own message AND the script appends its own.
        self.assertIn("ERR", r.stderr)

    def test_missing_local_file_exits_2(self):
        r = self._run("/tmp/_does_not_exist_markitdown_test.pdf")
        self.assertEqual(r.returncode, 2)
        self.assertIn("file not found", r.stderr)

    def test_list_plugins_short_circuits(self):
        # `-l` execs through to the shim's --list-plugins handler. No input arg
        # required and the wrapper should not hit the input validation path.
        r = self._run("-l")
        self.assertEqual(r.returncode, 0)
        self.assertIn("no plugins", r.stdout)

    # --- URL vs file detection --------------------------------------------

    def test_url_https_skips_file_check(self):
        # No file on disk, but https:// URL must be accepted.
        r = self._run("https://example.com/page.html")
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        self.assertIn("RESULT: saved=false", r.stdout)

    def test_url_http_skips_file_check(self):
        r = self._run("http://example.com/page.html")
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        self.assertIn("RESULT: saved=false", r.stdout)

    def test_url_lookalike_without_scheme_treated_as_file(self):
        """`example.com/foo` (no scheme) is a path, must fail the file check."""
        r = self._run("example.com/foo")
        self.assertEqual(r.returncode, 2)
        self.assertIn("file not found", r.stderr)

    # --- save / no-save ---------------------------------------------------

    def _write_input(self, name="My Document.PDF"):
        f = self.cwd / name
        f.write_text("dummy")
        return f

    def test_default_no_save_emits_result_and_separator(self):
        f = self._write_input("hello.txt")
        r = self._run(str(f))
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        self.assertIn("RESULT: bytes=", r.stdout)
        self.assertIn("RESULT: slug=hello", r.stdout)
        self.assertIn("RESULT: saved=false", r.stdout)
        self.assertIn("\n---\n", r.stdout)
        # Payload streamed after the separator.
        self.assertIn(SHIM_PAYLOAD.strip(), r.stdout)
        # No `path=` key in no-save mode.
        self.assertNotIn("RESULT: path=", r.stdout)

    def test_save_flag_writes_under_claude_output(self):
        f = self._write_input("Report Q1.PDF")
        r = self._run("-s", str(f))
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        self.assertIn("RESULT: saved=true", r.stdout)
        self.assertIn("RESULT: slug=report-q1", r.stdout)
        self.assertIn("RESULT: path=.claude/output/markitdown/report-q1/Report Q1.md", r.stdout)
        # File on disk where the RESULT says.
        out_file = self.cwd / ".claude" / "output" / "markitdown" / "report-q1" / "Report Q1.md"
        self.assertTrue(out_file.is_file())
        self.assertEqual(out_file.read_text(), SHIM_PAYLOAD)
        # Bytes value matches actual size.
        bytes_line = next(
            l for l in r.stdout.splitlines() if l.startswith("RESULT: bytes=")
        )
        self.assertEqual(bytes_line, f"RESULT: bytes={len(SHIM_PAYLOAD)}")

    def test_uppercase_S_overrides_lowercase_s(self):
        """getopts processes flags left-to-right; `-s -S` must end with SAVE=0
        (no-save). The wrapper streams payload to stdout, no .claude/output."""
        f = self._write_input("doc.txt")
        r = self._run("-s", "-S", str(f))
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        self.assertIn("RESULT: saved=false", r.stdout)
        self.assertFalse((self.cwd / ".claude").exists())

    def test_lowercase_s_overrides_uppercase_S(self):
        """Symmetric — `-S -s` ends with SAVE=1."""
        f = self._write_input("doc.txt")
        r = self._run("-S", "-s", str(f))
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        self.assertIn("RESULT: saved=true", r.stdout)

    # --- slug generation --------------------------------------------------

    def test_slug_lowercases_and_normalizes_specials(self):
        f = self._write_input("My Weird File!! v2.PDF")
        r = self._run("-s", str(f))
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        # Uppercase → lowercase, non-alphanum runs collapse to single `-`,
        # multiple specials (`!! `) collapse to one dash.
        self.assertIn("RESULT: slug=my-weird-file-v2", r.stdout)

    def test_slug_capped_at_five_segments(self):
        f = self._write_input("one two three four five six seven.txt")
        r = self._run("-s", str(f))
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        # `cut -d'-' -f1-5` keeps at most 5 dash-separated segments.
        self.assertIn("RESULT: slug=one-two-three-four-five", r.stdout)
        self.assertNotIn("six", r.stdout.split("RESULT: slug=", 1)[1].splitlines()[0])

    def test_slug_strips_leading_trailing_dashes(self):
        f = self._write_input("---weird---.md")
        r = self._run("-s", str(f))
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        self.assertIn("RESULT: slug=weird", r.stdout)

    def test_slug_falls_back_to_output_when_empty(self):
        """Pure-symbol stem collapses to empty after normalization → SLUG=output."""
        f = self._write_input("!!!.txt")
        r = self._run("-s", str(f))
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        self.assertIn("RESULT: slug=output", r.stdout)

    # --- Document Intelligence flag --------------------------------------

    def test_d_flag_without_endpoint_exits_2(self):
        f = self._write_input("doc.pdf")
        # _shim_env() already strips the env var; explicit for clarity.
        r = self._run("-d", str(f))
        self.assertEqual(r.returncode, 2)
        self.assertIn("MARKITDOWN_DOCINTEL_ENDPOINT", r.stderr)

    def test_d_flag_with_endpoint_passes_through(self):
        f = self._write_input("doc.pdf")
        r = self._run(
            "-d",
            str(f),
            MARKITDOWN_DOCINTEL_ENDPOINT="https://example.cognitiveservices.azure.com/",
        )
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        self.assertIn("RESULT: saved=false", r.stdout)

    # --- temp file cleanup -----------------------------------------------

    def test_temp_file_cleaned_on_success(self):
        f = self._write_input("doc.txt")
        before = set(Path(tempfile.gettempdir()).glob("markitdown.*"))
        r = self._run(str(f))
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        after = set(Path(tempfile.gettempdir()).glob("markitdown.*"))
        self.assertEqual(after - before, set(), "wrapper leaked a temp file on success")

    def test_temp_file_cleaned_when_markitdown_fails(self):
        """Trap-on-EXIT must remove the mktemp file even when the wrapped CLI
        errors out (set -e triggers exit after mktemp + trap are in place)."""
        f = self._write_input("doc.txt")
        before = set(Path(tempfile.gettempdir()).glob("markitdown.*"))
        r = self._run(str(f), MARKITDOWN_SHIM_FAIL="1")
        self.assertNotEqual(r.returncode, 0, "shim should have failed the run")
        after = set(Path(tempfile.gettempdir()).glob("markitdown.*"))
        self.assertEqual(after - before, set(), "wrapper leaked a temp file on failure")


if __name__ == "__main__":
    unittest.main()
