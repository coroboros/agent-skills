"""Tests for skills/design-system/scripts/{audit-extensions.sh,audit_extensions.py}.

Exercises the bidirectional drift contract: YAML extensions ↔ globals.css @theme
↔ prose references. The script is self-contained Python (stdlib only) so the
tests run on every contributor's machine — no npx, no @google/design.md, no
Tailwind install required.
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO_ROOT / "skills" / "design-system" / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

SCRIPT_SH = SCRIPTS / "audit-extensions.sh"
SCRIPT_PY = SCRIPTS / "audit_extensions.py"


def _run(*args, cwd=None):
    return subprocess.run(
        ["bash", str(SCRIPT_SH), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=30,
    )


def _result_kv(stdout):
    out = {}
    for line in stdout.splitlines():
        if line.startswith("RESULT: "):
            kv = line[len("RESULT: ") :]
            if "=" in kv:
                k, v = kv.split("=", 1)
                out[k] = v
    return out


def _findings(stdout):
    """Parse `FINDING: level=X rule=Y ...` lines into a list of dicts."""
    out = []
    for line in stdout.splitlines():
        if not line.startswith("FINDING: "):
            continue
        rest = line[len("FINDING: ") :]
        # First two tokens are level=... rule=...; the rest is free-form message
        parts = rest.split(" ", 2)
        if len(parts) < 2:
            continue
        kv = {}
        for p in parts[:2]:
            if "=" in p:
                k, v = p.split("=", 1)
                kv[k] = v
        kv["message"] = parts[2] if len(parts) > 2 else ""
        out.append(kv)
    return out


class TestArtifactsExist(unittest.TestCase):
    def test_shell_wrapper_exists(self):
        self.assertTrue(SCRIPT_SH.is_file())

    def test_python_script_exists(self):
        self.assertTrue(SCRIPT_PY.is_file())

    def test_shell_wrapper_executable(self):
        self.assertTrue(os.access(SCRIPT_SH, os.X_OK))


class TestArgumentValidation(unittest.TestCase):
    def test_no_args_prints_usage_and_exits_2(self):
        r = _run()
        self.assertEqual(r.returncode, 2)
        self.assertIn("usage: audit-extensions.sh", r.stderr)

    def test_missing_design_md_emits_file_not_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = _run(str(Path(tmp) / "nope.md"))
        self.assertEqual(r.returncode, 1)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "file-not-found")

    def test_missing_css_emits_css_not_found(self):
        """Pass --css to a missing path; the script must surface css-not-found
        before any audit logic runs."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "DESIGN.md").write_text("---\nname: x\n---\n")
            r = _run(str(tmp / "DESIGN.md"), "--css", str(tmp / "nope.css"))
        self.assertEqual(r.returncode, 1)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "css-not-found")


class TestCssAutoDetect(unittest.TestCase):
    """Without --css, the script probes the project tree for globals.css.
    Order: src/app/ → src/styles/ → src/style.css → app/ → src/app/global.css."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        # Minimal DESIGN.md with one extension token
        (self.tmp / "DESIGN.md").write_text(
            "---\n"
            "name: x\n"
            "shadows:\n"
            "  lifted: 0 1px 1px 0 rgb(0 0 0 / 0.1)\n"
            "---\n\n"
            "## Layout\n"
        )

    def tearDown(self):
        self._tmp.cleanup()

    def _make_css(self, relpath, body="@theme { --shadow-lifted: 0; }"):
        p = self.tmp / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
        return p

    def test_detects_src_app_globals_css(self):
        css = self._make_css("src/app/globals.css")
        r = _run(str(self.tmp / "DESIGN.md"))
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "ok")
        self.assertEqual(kv.get("css"), str(css.resolve()))

    def test_detects_src_styles_globals_css(self):
        css = self._make_css("src/styles/globals.css")
        r = _run(str(self.tmp / "DESIGN.md"))
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "ok")
        self.assertEqual(kv.get("css"), str(css.resolve()))

    def test_no_css_anywhere_returns_css_not_found(self):
        r = _run(str(self.tmp / "DESIGN.md"))
        self.assertEqual(r.returncode, 1)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "css-not-found")


class TestCleanFixture(unittest.TestCase):
    """The clean fixture exercises every namespace and resolves cleanly."""

    def setUp(self):
        self.design = FIXTURES / "clean" / "DESIGN.md"
        self.css = FIXTURES / "clean" / "globals.css"

    def test_exits_zero(self):
        r = _run(str(self.design), "--css", str(self.css))
        self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)

    def test_zero_findings(self):
        r = _run(str(self.design), "--css", str(self.css))
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("errors"), "0")
        self.assertEqual(kv.get("warnings"), "0")
        self.assertEqual(kv.get("infos"), "0")

    def test_extensions_field_lists_namespaces(self):
        r = _run(str(self.design), "--css", str(self.css))
        kv = _result_kv(r.stdout)
        ns = kv.get("extensions", "").split(",")
        for required in ("motion", "shadows", "aspectRatios", "heights", "zIndex", "opacity"):
            with self.subTest(namespace=required):
                self.assertIn(required, ns)


class TestDriftedFixture(unittest.TestCase):
    """Drifted fixture: each rule fires at least once."""

    def setUp(self):
        self.design = FIXTURES / "drifted" / "DESIGN.md"
        self.css = FIXTURES / "drifted" / "globals.css"

    def test_exits_one(self):
        r = _run(str(self.design), "--css", str(self.css))
        self.assertEqual(r.returncode, 1)

    def test_extension_missing_css_fires(self):
        r = _run(str(self.design), "--css", str(self.css))
        rules = [f["rule"] for f in _findings(r.stdout)]
        self.assertIn("extension-missing-css", rules)

    def test_extension_broken_ref_fires(self):
        r = _run(str(self.design), "--css", str(self.css))
        rules = [f["rule"] for f in _findings(r.stdout)]
        self.assertIn("extension-broken-ref", rules)

    def test_extension_orphan_css_warning_only_by_default(self):
        r = _run(str(self.design), "--css", str(self.css))
        findings = _findings(r.stdout)
        orphans = [f for f in findings if f["rule"] == "extension-orphan-css"]
        self.assertEqual(len(orphans), 1, msg="expected exactly one orphan")
        self.assertEqual(orphans[0]["level"], "warnings")

    def test_strict_promotes_orphan_to_error(self):
        r = _run(str(self.design), "--css", str(self.css), "--strict")
        self.assertEqual(r.returncode, 1)
        findings = _findings(r.stdout)
        orphans = [f for f in findings if f["rule"] == "extension-orphan-css"]
        self.assertEqual(orphans[0]["level"], "errors")

    def test_broken_ref_includes_file_line_number(self):
        """The error message must cite a file-line number, not a body-line."""
        r = _run(str(self.design), "--css", str(self.css))
        text = r.stdout
        # The drifted fixture's ## Layout starts around file line 32; the
        # broken-ref must reference a line number ≥ 30 (after frontmatter).
        # Grab the first line=N from the broken-ref message.
        import re as _re
        m = _re.search(r"motion\.duration-undefined-token.*line\s+(\d+)", text)
        self.assertIsNotNone(m, "expected a line number in the broken-ref message")
        line_no = int(m.group(1))
        # Frontmatter ends around line 27; prose ref must be after.
        self.assertGreater(line_no, 25)


class TestJsonOutput(unittest.TestCase):
    def test_json_mode_emits_valid_json(self):
        design = FIXTURES / "drifted" / "DESIGN.md"
        css = FIXTURES / "drifted" / "globals.css"
        r = _run(str(design), "--css", str(css), "--json")
        self.assertEqual(r.returncode, 1)
        # The script's bash wrapper still emits no RESULT lines in --json mode.
        # The Python script writes a single JSON document to stdout.
        try:
            doc = json.loads(r.stdout)
        except json.JSONDecodeError:
            self.fail(f"--json output is not valid JSON:\n{r.stdout}")
        self.assertIn("summary", doc)
        self.assertIn("findings", doc)
        self.assertGreater(doc["summary"]["errors"], 0)


class TestPython3Required(unittest.TestCase):
    """The wrapper must check for python3 availability and emit a clean
    error when missing. Verified by inspecting the wrapper source — running
    bash without python3 on PATH is non-portable across CI environments."""

    def test_wrapper_probes_python3(self):
        text = SCRIPT_SH.read_text(encoding="utf-8")
        self.assertIn("command -v python3", text)
        self.assertIn("python3-missing", text)


if __name__ == "__main__":
    unittest.main()
