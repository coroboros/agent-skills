"""Tests for skills/animated-svg/scripts/check_svg.py.

The validator gates an animated SVG for self-contained, no-JS delivery.
Tests pin the contract: exit-code mapping (0 pass / 1 fail / 2 unparseable),
per-check RESULT schema, and the readme-vs-web profile split on external
references. Pure stdlib — no browser involved.
"""

import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "skills" / "animated-svg" / "scripts" / "check_svg.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _run(*args):
    return subprocess.run(
        ["python3", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


def _checks(stdout):
    """Parse `RESULT: check=<id> status=<s> detail=<text>` lines into {id: status}."""
    out = {}
    for line in stdout.splitlines():
        if not line.startswith("RESULT: check="):
            continue
        rest = line[len("RESULT: check="):]
        check_id, _, tail = rest.partition(" status=")
        status = tail.split(" ", 1)[0]
        out[check_id] = status
    return out


def _verdict(stdout):
    for line in stdout.splitlines():
        if line.startswith("RESULT: verdict="):
            return line.split("verdict=", 1)[1].split(" ", 1)[0]
    return None


class TestPassFixture(unittest.TestCase):
    def setUp(self):
        self.proc = _run(str(FIXTURES / "smil-css-pass.svg"))

    def test_exit_zero(self):
        self.assertEqual(self.proc.returncode, 0, self.proc.stdout)

    def test_all_checks_pass(self):
        checks = _checks(self.proc.stdout)
        self.assertEqual(
            {s for s in checks.values()}, {"pass"},
            f"expected all-pass, got {checks}",
        )

    def test_verdict_line_present(self):
        self.assertEqual(_verdict(self.proc.stdout), "pass")

    def test_detects_both_animation_kinds(self):
        self.assertIn("SMIL", self.proc.stdout)
        self.assertIn("@keyframes", self.proc.stdout)


class TestFailures(unittest.TestCase):
    def test_script_and_handler_fail(self):
        proc = _run(str(FIXTURES / "script-handler-fail.svg"))
        self.assertEqual(proc.returncode, 1)
        checks = _checks(proc.stdout)
        self.assertEqual(checks["no-script"], "fail")

    def test_static_svg_fails_animation_check(self):
        proc = _run(str(FIXTURES / "static-no-animation-fail.svg"))
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(_checks(proc.stdout)["animation-present"], "fail")

    def test_set_only_fails_animation_check(self):
        # A lone <set> is a discrete value flip, not an animation.
        proc = _run(str(FIXTURES / "set-only-fail.svg"))
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(_checks(proc.stdout)["animation-present"], "fail")
        # ...and the reduced-motion check must not contradict it.
        self.assertNotIn("SMIL-only", proc.stdout)

    def test_missing_viewbox_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            svg = Path(tmp) / "no-viewbox.svg"
            svg.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
                '<circle r="4"><animate attributeName="r" values="4;6;4" dur="1s" '
                'repeatCount="indefinite"/></circle></svg>',
                encoding="utf-8",
            )
            proc = _run(str(svg))
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(_checks(proc.stdout)["viewbox"], "fail")


class TestProfiles(unittest.TestCase):
    def test_external_ref_fails_readme_profile(self):
        proc = _run(str(FIXTURES / "external-ref-profiles.svg"), "-p", "readme")
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(_checks(proc.stdout)["self-contained"], "fail")

    def test_external_ref_warns_web_profile(self):
        proc = _run(str(FIXTURES / "external-ref-profiles.svg"), "-p", "web")
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(_checks(proc.stdout)["self-contained"], "warn")

    def test_relative_ref_fails_readme_profile(self):
        # Relative paths never resolve in <img> context either — the gate
        # must reject anything that is not #id or data:.
        proc = _run(str(FIXTURES / "relative-ref-fail.svg"), "-p", "readme")
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(_checks(proc.stdout)["self-contained"], "fail")

    def test_presentation_attr_url_fails_readme_profile(self):
        # fill/filter/mask can carry url() fetches too — same failure in <img>.
        with tempfile.TemporaryDirectory() as tmp:
            svg = Path(tmp) / "fill-url.svg"
            svg.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
                '<title>t</title>'
                '<rect fill="url(https://example.com/x.svg#g)" width="10" height="10">'
                '<animate attributeName="width" values="10;8;10" dur="1s" '
                'repeatCount="indefinite"/></rect></svg>',
                encoding="utf-8",
            )
            proc = _run(str(svg), "-p", "readme")
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(_checks(proc.stdout)["self-contained"], "fail")

    def test_internal_and_data_refs_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            svg = Path(tmp) / "internal-refs.svg"
            svg.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
                '<defs><linearGradient id="g"/></defs>'
                '<use href="#g"/>'
                '<image href="data:image/png;base64,AAAA" width="1" height="1"/>'
                '<rect fill="url(#g)" width="1" height="1">'
                '<animate attributeName="width" values="1;2;1" dur="1s" '
                'repeatCount="indefinite"/></rect></svg>',
                encoding="utf-8",
            )
            proc = _run(str(svg), "-p", "readme")
        self.assertEqual(_checks(proc.stdout)["self-contained"], "pass", proc.stdout)


class TestWarnings(unittest.TestCase):
    def setUp(self):
        self.proc = _run(str(FIXTURES / "hover-text-warns.svg"))

    def test_warnings_do_not_fail_the_gate(self):
        self.assertEqual(self.proc.returncode, 0, self.proc.stdout)

    def test_hover_and_click_warn_on_readme(self):
        self.assertEqual(_checks(self.proc.stdout)["interactivity"], "warn")

    def test_text_warns(self):
        self.assertEqual(_checks(self.proc.stdout)["fonts"], "warn")

    def test_missing_title_warns(self):
        self.assertEqual(_checks(self.proc.stdout)["a11y-title"], "warn")

    def test_interactivity_passes_on_web_profile(self):
        proc = _run(str(FIXTURES / "hover-text-warns.svg"), "-p", "web")
        self.assertEqual(_checks(proc.stdout)["interactivity"], "pass")


class TestUnparseableInputs(unittest.TestCase):
    def test_malformed_xml_exits_two(self):
        proc = _run(str(FIXTURES / "malformed.svg"))
        self.assertEqual(proc.returncode, 2)
        self.assertIn("check=parse status=fail", proc.stdout)

    def test_non_svg_root_exits_two(self):
        proc = _run(str(FIXTURES / "not-an-svg.svg"))
        self.assertEqual(proc.returncode, 2)
        self.assertIn("check=parse status=fail", proc.stdout)

    def test_missing_file_exits_two(self):
        proc = _run(str(FIXTURES / "does-not-exist.svg"))
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
