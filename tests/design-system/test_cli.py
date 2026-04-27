"""Tests for skills/design-system/scripts/{audit,diff,export}.sh.

Strategy: argument-validation and missing-file branches run unconditionally.
For exit-code propagation and stderr handling we stub `npx` in a fake-bin
directory and prepend it to PATH so the script's `command -v npx` succeeds
and the stub's exit code/stderr is what gets propagated. That keeps the
tests deterministic and free of network/install side-effects.
"""

import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO_ROOT / "skills" / "design-system" / "scripts"


def _make_stub(bin_dir: Path, name: str, body: str) -> None:
    p = bin_dir / name
    p.write_text(body)
    p.chmod(p.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def _run(script_name: str, *args: str, fake_bin: Path | None = None):
    env = os.environ.copy()
    base_path = "/usr/bin:/bin:/usr/sbin:/sbin"
    env["PATH"] = f"{fake_bin}:{base_path}" if fake_bin else base_path
    return subprocess.run(
        ["bash", str(SCRIPTS / script_name), *args],
        capture_output=True,
        text=True,
        env=env,
    )


def _result_kv(stdout: str) -> dict[str, str]:
    """Parse `RESULT: key=value` lines into a dict."""
    out: dict[str, str] = {}
    for line in stdout.splitlines():
        if line.startswith("RESULT: "):
            kv = line[len("RESULT: ") :]
            if "=" in kv:
                k, v = kv.split("=", 1)
                out[k] = v
    return out


class _TmpMixin:
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.fake_bin = self.tmp / "bin"
        self.fake_bin.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def _design_md(self, name: str = "DESIGN.md") -> Path:
        p = self.tmp / name
        p.write_text("# DESIGN\n")
        return p


# ---------- audit.sh ----------


class TestAuditUsage(_TmpMixin, unittest.TestCase):
    def test_no_args_prints_usage_and_exits_2(self):
        r = _run("audit.sh")
        self.assertEqual(r.returncode, 2)
        self.assertIn("usage: audit.sh", r.stderr)

    def test_too_many_args_prints_usage(self):
        r = _run("audit.sh", "a", "b")
        self.assertEqual(r.returncode, 2)
        self.assertIn("usage: audit.sh", r.stderr)

    def test_missing_file_emits_file_not_found(self):
        r = _run("audit.sh", str(self.tmp / "nope.md"))
        self.assertEqual(r.returncode, 1)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "file-not-found")
        self.assertEqual(kv.get("path"), str(self.tmp / "nope.md"))


class TestAuditCliPropagation(_TmpMixin, unittest.TestCase):
    """Stub npx so the script's npx-detected branch runs deterministically."""

    def test_cli_exit_0_reports_status_ok(self):
        # `lint` exit 0 = no errors; script must exit 0 and emit status=ok.
        _make_stub(self.fake_bin, "npx", '#!/bin/sh\necho \'{"summary":{"errors":0}}\'\nexit 0\n')
        design = self._design_md()
        r = _run("audit.sh", str(design), fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 0)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "ok")
        self.assertEqual(kv.get("path"), str(design))
        self.assertEqual(kv.get("exit-code"), "0")
        self.assertTrue(kv.get("json", "").endswith(".json"))

    def test_cli_exit_1_propagated_as_lint_errors(self):
        # `lint` exit 1 = errors found, valid run; script must exit 1 with status=ok.
        _make_stub(self.fake_bin, "npx", '#!/bin/sh\necho \'{"summary":{"errors":3}}\'\nexit 1\n')
        design = self._design_md()
        r = _run("audit.sh", str(design), fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 1)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "ok")
        self.assertEqual(kv.get("exit-code"), "1")

    def test_cli_exit_higher_reports_cli_failed_with_stderr(self):
        # rc > 1 = real CLI failure; script must report cli-failed and propagate stderr file.
        _make_stub(
            self.fake_bin,
            "npx",
            '#!/bin/sh\necho boom >&2\nexit 7\n',
        )
        design = self._design_md()
        r = _run("audit.sh", str(design), fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 1)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "cli-failed")
        self.assertEqual(kv.get("exit-code"), "7")
        stderr_path = kv.get("stderr", "")
        self.assertTrue(stderr_path)
        self.assertIn("boom", Path(stderr_path).read_text())


# ---------- diff.sh ----------


class TestDiffUsage(_TmpMixin, unittest.TestCase):
    def test_no_args_prints_usage(self):
        r = _run("diff.sh")
        self.assertEqual(r.returncode, 2)
        self.assertIn("usage: diff.sh", r.stderr)

    def test_one_arg_prints_usage(self):
        r = _run("diff.sh", "only-one.md")
        self.assertEqual(r.returncode, 2)
        self.assertIn("usage: diff.sh", r.stderr)

    def test_missing_before_emits_before_not_found(self):
        after = self._design_md("after.md")
        r = _run("diff.sh", str(self.tmp / "missing.md"), str(after))
        self.assertEqual(r.returncode, 1)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "before-not-found")

    def test_missing_after_emits_after_not_found(self):
        before = self._design_md("before.md")
        r = _run("diff.sh", str(before), str(self.tmp / "missing.md"))
        self.assertEqual(r.returncode, 1)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "after-not-found")


class TestDiffCliPropagation(_TmpMixin, unittest.TestCase):
    def test_no_regression_exit_0(self):
        _make_stub(self.fake_bin, "npx", '#!/bin/sh\necho \'{}\'\nexit 0\n')
        before, after = self._design_md("before.md"), self._design_md("after.md")
        r = _run("diff.sh", str(before), str(after), fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 0)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "ok")
        self.assertEqual(kv.get("regression"), "false")
        self.assertEqual(kv.get("exit-code"), "0")

    def test_regression_exit_1_propagated(self):
        _make_stub(self.fake_bin, "npx", '#!/bin/sh\necho \'{}\'\nexit 1\n')
        before, after = self._design_md("before.md"), self._design_md("after.md")
        r = _run("diff.sh", str(before), str(after), fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 1)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "ok")
        self.assertEqual(kv.get("regression"), "true")

    def test_cli_failure_reports_stderr(self):
        _make_stub(self.fake_bin, "npx", '#!/bin/sh\necho diff-boom >&2\nexit 4\n')
        before, after = self._design_md("before.md"), self._design_md("after.md")
        r = _run("diff.sh", str(before), str(after), fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 1)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "cli-failed")
        self.assertEqual(kv.get("exit-code"), "4")
        self.assertIn("diff-boom", Path(kv["stderr"]).read_text())


# ---------- export.sh ----------


class TestExportUsage(_TmpMixin, unittest.TestCase):
    def test_no_args_prints_usage(self):
        r = _run("export.sh")
        self.assertEqual(r.returncode, 2)
        self.assertIn("usage: export.sh", r.stderr)

    def test_too_many_args_prints_usage(self):
        r = _run("export.sh", "tailwind", "a.md", "out.css", "extra")
        self.assertEqual(r.returncode, 2)
        self.assertIn("usage: export.sh", r.stderr)

    def test_invalid_format_rejected(self):
        design = self._design_md()
        r = _run("export.sh", "scss", str(design))
        self.assertEqual(r.returncode, 2)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "invalid-format")
        self.assertEqual(kv.get("format"), "scss")

    def test_format_tailwind_accepted(self):
        # Format check happens before the file check, so a missing file with
        # a valid format must NOT trip invalid-format.
        r = _run("export.sh", "tailwind", str(self.tmp / "missing.md"))
        self.assertEqual(r.returncode, 1)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "file-not-found")

    def test_format_dtcg_accepted(self):
        r = _run("export.sh", "dtcg", str(self.tmp / "missing.md"))
        self.assertEqual(r.returncode, 1)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "file-not-found")

    def test_missing_file_emits_file_not_found(self):
        r = _run("export.sh", "tailwind", str(self.tmp / "nope.md"))
        self.assertEqual(r.returncode, 1)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "file-not-found")
        self.assertEqual(kv.get("path"), str(self.tmp / "nope.md"))


class TestExportCliPropagation(_TmpMixin, unittest.TestCase):
    def test_success_emits_full_schema(self):
        # Stub writes to stdout, which the script redirects into the output file.
        _make_stub(self.fake_bin, "npx", '#!/bin/sh\nprintf "tokens-go-here"\nexit 0\n')
        design = self._design_md()
        r = _run("export.sh", "tailwind", str(design), fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 0)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "ok")
        self.assertEqual(kv.get("format"), "tailwind")
        self.assertEqual(kv.get("source"), str(design))
        self.assertEqual(kv.get("bytes"), str(len("tokens-go-here")))
        out = kv.get("output", "")
        self.assertTrue(out.endswith(".tailwind"))
        self.assertEqual(Path(out).read_text(), "tokens-go-here")

    def test_explicit_output_path_honoured(self):
        _make_stub(self.fake_bin, "npx", '#!/bin/sh\nprintf "x"\nexit 0\n')
        design = self._design_md()
        explicit = self.tmp / "tokens.json"
        r = _run("export.sh", "dtcg", str(design), str(explicit), fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 0)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("output"), str(explicit))
        self.assertTrue(explicit.exists())

    def test_cli_failure_reports_stderr(self):
        _make_stub(self.fake_bin, "npx", '#!/bin/sh\necho export-boom >&2\nexit 5\n')
        design = self._design_md()
        r = _run("export.sh", "tailwind", str(design), fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 1)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "cli-failed")
        self.assertIn("export-boom", Path(kv["stderr"]).read_text())


if __name__ == "__main__":
    unittest.main()
