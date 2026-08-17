"""Behavioral tests for the Design System CLI wrappers.

Strategy: argument-validation and missing-file branches run unconditionally.
Runtime tests expose a no-network `designmd` stub on PATH.
"""

from __future__ import annotations

import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO_ROOT / "skills" / "design-system" / "scripts"

LINT_CLEAN = '{"findings":[],"summary":{"errors":0,"warnings":0,"infos":0}}'
LINT_ERRORS = (
    '{"findings":[{"severity":"error","message":"broken token"}],'
    '"summary":{"errors":1,"warnings":0,"infos":0}}'
)
EMPTY_TOKEN_DIFF = {
    group: {"added": [], "removed": [], "modified": []}
    for group in ("colors", "typography", "rounded", "spacing", "components")
}


def _diff_payload(regression: bool) -> str:
    errors = 1 if regression else 0
    return json.dumps({
        "tokens": EMPTY_TOKEN_DIFF,
        "findings": {
            "before": {"errors": 0, "warnings": 0, "infos": 0},
            "after": {"errors": errors, "warnings": 0, "infos": 0},
            "delta": {"errors": errors, "warnings": 0},
        },
        "regression": regression,
    })


TAILWIND_EXPORT = json.dumps({
    "theme": {"extend": {
        "colors": {}, "fontFamily": {}, "fontSize": {},
        "borderRadius": {}, "spacing": {},
    }}
})
DTCG_EXPORT = json.dumps({
    "$schema": "https://www.designtokens.org/schemas/2025.10/format.json"
})


def _make_stub(bin_dir: Path, name: str, body: str) -> None:
    body = body.replace(
        "#!/bin/sh\n",
        '#!/bin/sh\nif [ "$1" = "--version" ]; then echo 0.4.0; exit 0; fi\n',
        1,
    )
    p = bin_dir / name
    p.write_text(body)
    p.chmod(p.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def _run(
    script_name: str,
    *args: str,
    fake_bin: Path | None = None,
    extra_env: dict[str, str] | None = None,
):
    env = os.environ.copy()
    base_path = "/usr/bin:/bin:/usr/sbin:/sbin"
    env["PATH"] = f"{fake_bin}:{base_path}" if fake_bin else base_path
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["bash", str(SCRIPTS / script_name), *args],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
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

    def test_cli_exit_0_reports_status_ok(self):
        # `lint` exit 0 = no errors; script must exit 0 and emit status=ok.
        _make_stub(self.fake_bin, "designmd", f"#!/bin/sh\nprintf '%s\\n' '{LINT_CLEAN}'\nexit 0\n")
        design = self._design_md()
        r = _run("audit.sh", str(design), fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 0)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "ok")
        self.assertEqual(kv.get("path"), str(design))
        self.assertEqual(kv.get("exit-code"), "0")
        self.assertTrue(Path(kv.get("json", "")).is_file())
        self.assertEqual(kv.get("runtime"), "path")

    def test_cli_exit_1_propagated_as_lint_errors(self):
        # `lint` exit 1 = errors found, valid run; script must exit 1 with status=ok.
        _make_stub(self.fake_bin, "designmd", f"#!/bin/sh\nprintf '%s\\n' '{LINT_ERRORS}'\nexit 1\n")
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
            "designmd",
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
        _make_stub(self.fake_bin, "designmd", f"#!/bin/sh\nprintf '%s\\n' '{_diff_payload(False)}'\nexit 0\n")
        before, after = self._design_md("before.md"), self._design_md("after.md")
        r = _run("diff.sh", str(before), str(after), fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 0)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "ok")
        self.assertEqual(kv.get("regression"), "false")
        self.assertEqual(kv.get("exit-code"), "0")

    def test_regression_exit_1_propagated(self):
        _make_stub(self.fake_bin, "designmd", f"#!/bin/sh\nprintf '%s\\n' '{_diff_payload(True)}'\nexit 1\n")
        before, after = self._design_md("before.md"), self._design_md("after.md")
        r = _run("diff.sh", str(before), str(after), fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 1)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "ok")
        self.assertEqual(kv.get("regression"), "true")

    def test_future_token_group_does_not_break_the_stable_contract(self):
        payload = json.loads(_diff_payload(False))
        payload["tokens"]["motion"] = {
            "added": ["duration.fast"], "removed": [], "modified": []
        }
        _make_stub(
            self.fake_bin,
            "designmd",
            f"#!/bin/sh\nprintf '%s\\n' '{json.dumps(payload)}'\nexit 0\n",
        )
        before, after = self._design_md("before.md"), self._design_md("after.md")
        result = _run("diff.sh", str(before), str(after), fake_bin=self.fake_bin)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(_result_kv(result.stdout)["status"], "ok")

    def test_additive_token_metadata_does_not_break_the_stable_contract(self):
        payload = json.loads(_diff_payload(False))
        payload["tokens"]["colors"]["metadata"] = {"source": "future-cli"}
        _make_stub(
            self.fake_bin,
            "designmd",
            f"#!/bin/sh\nprintf '%s\\n' '{json.dumps(payload)}'\nexit 0\n",
        )
        before, after = self._design_md("before.md"), self._design_md("after.md")
        result = _run("diff.sh", str(before), str(after), fake_bin=self.fake_bin)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(_result_kv(result.stdout)["status"], "ok")

    def test_cli_failure_reports_stderr(self):
        _make_stub(self.fake_bin, "designmd", '#!/bin/sh\necho diff-boom >&2\nexit 4\n')
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
        _make_stub(self.fake_bin, "designmd", f"#!/bin/sh\nprintf '%s\\n' '{TAILWIND_EXPORT}'\nexit 0\n")
        design = self._design_md()
        r = _run("export.sh", "tailwind", str(design), fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 0)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "ok")
        self.assertEqual(kv.get("format"), "tailwind")
        self.assertEqual(kv.get("source"), str(design))
        self.assertEqual(kv.get("bytes"), str(len(TAILWIND_EXPORT) + 1))
        out = kv.get("output", "")
        self.assertTrue(Path(out).is_file())
        self.assertEqual(Path(out).read_text(), TAILWIND_EXPORT + "\n")

    def test_explicit_output_path_honoured(self):
        _make_stub(self.fake_bin, "designmd", f"#!/bin/sh\nprintf '%s\\n' '{DTCG_EXPORT}'\nexit 0\n")
        design = self._design_md()
        explicit = self.tmp / "tokens.json"
        r = _run("export.sh", "dtcg", str(design), str(explicit), fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 0)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("output"), str(explicit))
        self.assertTrue(explicit.exists())

    def test_cli_failure_reports_stderr(self):
        _make_stub(self.fake_bin, "designmd", '#!/bin/sh\necho export-boom >&2\nexit 5\n')
        design = self._design_md()
        r = _run("export.sh", "tailwind", str(design), fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 1)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "cli-failed")
        self.assertIn("export-boom", Path(kv["stderr"]).read_text())


class TestRuntimeContract(_TmpMixin, unittest.TestCase):
    def test_missing_binary_fails_with_install_and_exact_rerun(self):
        design = self._design_md()
        result = _run("audit.sh", str(design))
        fields = _result_kv(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(fields["status"], "designmd-missing")
        self.assertIn("@google/design.md", fields["remediation"])
        self.assertIn("audit.sh", fields["rerun"])

    def test_invalid_cli_output_never_reports_success(self):
        _make_stub(self.fake_bin, "designmd", "#!/bin/sh\nprintf '{}\\n'\n")
        result = _run(
            "audit.sh", str(self._design_md()), fake_bin=self.fake_bin
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(_result_kv(result.stdout)["status"], "cli-invalid-output")

    def test_temp_files_honor_tmpdir(self):
        _make_stub(
            self.fake_bin,
            "designmd",
            f"#!/bin/sh\nprintf '%s\\n' '{LINT_CLEAN}'\n",
        )
        temp_dir = self.tmp / "runtime-tmp"
        temp_dir.mkdir()
        result = _run(
            "audit.sh",
            str(self._design_md()),
            fake_bin=self.fake_bin,
            extra_env={"TMPDIR": str(temp_dir)},
        )
        output = Path(_result_kv(result.stdout)["json"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(output.parent, temp_dir)


class TestSpecCli(_TmpMixin, unittest.TestCase):
    SPEC = """# DESIGN.md Format
# Design Tokens
## Schema
# Sections
# Consumer Behavior for Unknown Content
"""

    def _stub(self):
        payload = self.SPEC.replace("'", "'\\''")
        _make_stub(
            self.fake_bin,
            "designmd",
            f"#!/bin/sh\nprintf '%s' '{payload}'\n",
        )

    def test_spec_writes_valid_output_atomically(self):
        self._stub()
        output = self.tmp / "spec.md"
        result = _run(
            "spec.sh", "-o", str(output), fake_bin=self.fake_bin
        )
        fields = _result_kv(result.stdout)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(fields["status"], "ok")
        self.assertEqual(fields["runtime"], "path")
        self.assertEqual(output.read_text(encoding="utf-8"), self.SPEC)

    def test_spec_failure_keeps_final_output_untouched(self):
        _make_stub(self.fake_bin, "designmd", "#!/bin/sh\nexit 9\n")
        output = self.tmp / "spec.md"
        output.write_text("previous\n", encoding="utf-8")
        result = _run(
            "spec.sh", "-o", str(output), fake_bin=self.fake_bin
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(output.read_text(encoding="utf-8"), "previous\n")


if __name__ == "__main__":
    unittest.main()
