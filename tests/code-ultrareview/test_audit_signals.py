"""Tests for skills/code-ultrareview/scripts/audit_signals.py.

Strategy: build a fresh tempdir git repo per scenario, commit a synthetic
diff, then run the script and assert the JSON output. Git config is isolated
(GIT_CONFIG_GLOBAL/SYSTEM=/dev/null) and identity is forced via env so the
suite is deterministic on any contributor's machine.

Each test pins one signal — chained signals are caught by the router's
fixture tests, not here.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "skills" / "code-ultrareview" / "scripts" / "audit_signals.py"

_GIT = shutil.which("git")
GIT = _GIT or "git"
PYTHON = sys.executable


def _env(cwd: Path) -> dict:
    env = os.environ.copy()
    env["GIT_CEILING_DIRECTORIES"] = str(Path(cwd).parent)
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_AUTHOR_NAME"] = "t"
    env["GIT_AUTHOR_EMAIL"] = "t@t"
    env["GIT_COMMITTER_NAME"] = "t"
    env["GIT_COMMITTER_EMAIL"] = "t@t"
    return env


def _git(cwd: Path, *args: str) -> str:
    r = subprocess.run(
        [GIT, *args], cwd=cwd, env=_env(cwd),
        capture_output=True, text=True, timeout=30,
    )
    if r.returncode != 0:
        raise AssertionError(f"git {args} failed: {r.stderr}")
    return r.stdout.strip()


def _new_repo(tmp: Path, default: str = "main") -> Path:
    repo = tmp / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "symbolic-ref", "HEAD", f"refs/heads/{default}")
    return repo


def _write(repo: Path, relpath: str, content: str) -> Path:
    p = repo / relpath
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def _commit_all(repo: Path, msg: str) -> str:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", msg)
    return _git(repo, "rev-parse", "HEAD")


def _run_audit(repo: Path, base: str, target: str = "HEAD") -> dict:
    r = subprocess.run(
        [PYTHON, str(SCRIPT), "--repo", str(repo), "--base", base, "--target", target, "--json"],
        cwd=repo, env=_env(repo), capture_output=True, text=True, timeout=30,
    )
    if r.returncode != 0:
        raise AssertionError(f"audit_signals failed: {r.stderr}")
    return json.loads(r.stdout)


@unittest.skipUnless(_GIT, "git required")
class TestSchema(unittest.TestCase):
    REQUIRED_KEYS = (
        "loc_changed", "files_touched", "files_touched_list",
        "public_api_touched", "normative_spec_mentioned", "normative_specs_list",
        "manifest_graph_delta", "pre_1_0_or_freeze", "test_coverage_delta",
        "security_sensitive_paths",
    )

    def test_emits_all_required_keys(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _write(repo, "src/a.ts", "export const x = 1;\n")
            base = _commit_all(repo, "init")
            _write(repo, "src/a.ts", "export const x = 2;\n")
            _commit_all(repo, "change")
            out = _run_audit(repo, base, "HEAD")
        for key in self.REQUIRED_KEYS:
            self.assertIn(key, out, f"missing key: {key}")


@unittest.skipUnless(_GIT, "git required")
class TestLocAndFiles(unittest.TestCase):
    def test_loc_and_files_counted(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _write(repo, "a.ts", "x\n")
            base = _commit_all(repo, "init")
            _write(repo, "a.ts", "x\ny\nz\n")        # +2
            _write(repo, "b.ts", "new\n")             # +1
            _commit_all(repo, "change")
            out = _run_audit(repo, base, "HEAD")
        self.assertEqual(out["files_touched"], 2)
        self.assertIn("a.ts", out["files_touched_list"])
        self.assertIn("b.ts", out["files_touched_list"])
        self.assertGreaterEqual(out["loc_changed"], 3)


@unittest.skipUnless(_GIT, "git required")
class TestPublicApi(unittest.TestCase):
    def test_root_md_flags_public_api(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _write(repo, "README.md", "# a\n")
            base = _commit_all(repo, "init")
            _write(repo, "README.md", "# b\n")
            _commit_all(repo, "change")
            out = _run_audit(repo, base, "HEAD")
        self.assertTrue(out["public_api_touched"])

    def test_skill_md_flags_public_api(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _write(repo, "skills/foo/SKILL.md", "# foo\n")
            base = _commit_all(repo, "init")
            _write(repo, "skills/foo/SKILL.md", "# foo bar\n")
            _commit_all(repo, "change")
            out = _run_audit(repo, base, "HEAD")
        self.assertTrue(out["public_api_touched"])

    def test_route_file_flags_public_api(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _write(repo, "src/api/route.ts", "x\n")
            base = _commit_all(repo, "init")
            _write(repo, "src/api/route.ts", "y\n")
            _commit_all(repo, "change")
            out = _run_audit(repo, base, "HEAD")
        self.assertTrue(out["public_api_touched"])

    def test_top_level_export_flags_public_api(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _write(repo, "src/lib.ts", "// nothing yet\n")
            base = _commit_all(repo, "init")
            _write(repo, "src/lib.ts", "export const x = 1;\n")
            _commit_all(repo, "change")
            out = _run_audit(repo, base, "HEAD")
        self.assertTrue(out["public_api_touched"])

    def test_non_public_change_does_not_flag(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _write(repo, "src/utils/internal.ts", "let x = 1;\n")
            base = _commit_all(repo, "init")
            _write(repo, "src/utils/internal.ts", "let x = 2;\n")
            _commit_all(repo, "change")
            out = _run_audit(repo, base, "HEAD")
        self.assertFalse(out["public_api_touched"])


@unittest.skipUnless(_GIT, "git required")
class TestNormativeSpec(unittest.TestCase):
    def test_rfc_in_diff_flags(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _write(repo, "src/uri.ts", "// parser\n")
            base = _commit_all(repo, "init")
            _write(repo, "src/uri.ts", "// implements RFC 6874\n")
            _commit_all(repo, "change")
            out = _run_audit(repo, base, "HEAD")
        self.assertTrue(out["normative_spec_mentioned"])
        self.assertTrue(any("RFC" in s for s in out["normative_specs_list"]))

    def test_whatwg_in_readme_flags(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _write(repo, "README.md", "Compatible with WHATWG URL standard.\n")
            _write(repo, "src/x.ts", "let x = 1;\n")
            base = _commit_all(repo, "init")
            _write(repo, "src/x.ts", "let x = 2;\n")
            _commit_all(repo, "change")
            out = _run_audit(repo, base, "HEAD")
        self.assertTrue(out["normative_spec_mentioned"])
        self.assertIn("WHATWG", out["normative_specs_list"])

    def test_no_spec_mention(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _write(repo, "src/x.ts", "let x = 1;\n")
            base = _commit_all(repo, "init")
            _write(repo, "src/x.ts", "let x = 2;\n")
            _commit_all(repo, "change")
            out = _run_audit(repo, base, "HEAD")
        self.assertFalse(out["normative_spec_mentioned"])
        self.assertEqual(out["normative_specs_list"], [])


@unittest.skipUnless(_GIT, "git required")
class TestManifestDelta(unittest.TestCase):
    def test_package_json_flags(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _write(repo, "package.json", '{"name":"x","version":"1.0.0"}\n')
            base = _commit_all(repo, "init")
            _write(repo, "package.json", '{"name":"x","version":"1.0.1"}\n')
            _commit_all(repo, "bump")
            out = _run_audit(repo, base, "HEAD")
        self.assertTrue(out["manifest_graph_delta"])

    def test_code_only_does_not_flag(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _write(repo, "src/a.ts", "x\n")
            base = _commit_all(repo, "init")
            _write(repo, "src/a.ts", "y\n")
            _commit_all(repo, "change")
            out = _run_audit(repo, base, "HEAD")
        self.assertFalse(out["manifest_graph_delta"])


@unittest.skipUnless(_GIT, "git required")
class TestPre10OrFreeze(unittest.TestCase):
    def test_pre_1_0_package_json_flags(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _write(repo, "package.json", '{"name":"x","version":"0.5.0"}\n')
            _write(repo, "src/a.ts", "x\n")
            base = _commit_all(repo, "init")
            _write(repo, "src/a.ts", "y\n")
            _commit_all(repo, "change")
            out = _run_audit(repo, base, "HEAD")
        self.assertTrue(out["pre_1_0_or_freeze"])

    def test_pre_1_0_marketplace_json_flags(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _write(repo, ".claude-plugin/marketplace.json",
                   '{"metadata":{"version":"0.9.0"}}\n')
            _write(repo, "src/a.ts", "x\n")
            base = _commit_all(repo, "init")
            _write(repo, "src/a.ts", "y\n")
            _commit_all(repo, "change")
            out = _run_audit(repo, base, "HEAD")
        self.assertTrue(out["pre_1_0_or_freeze"])

    def test_freeze_commit_subject_flags(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _write(repo, "package.json", '{"version":"1.5.0"}\n')
            _write(repo, "src/a.ts", "x\n")
            base = _commit_all(repo, "init")
            _write(repo, "src/a.ts", "y\n")
            _commit_all(repo, "chore: enter rc freeze")
            out = _run_audit(repo, base, "HEAD")
        self.assertTrue(out["pre_1_0_or_freeze"])

    def test_post_1_0_no_freeze_does_not_flag(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _write(repo, "package.json", '{"version":"2.1.0"}\n')
            _write(repo, "src/a.ts", "x\n")
            base = _commit_all(repo, "init")
            _write(repo, "src/a.ts", "y\n")
            _commit_all(repo, "feat: ordinary work")
            out = _run_audit(repo, base, "HEAD")
        self.assertFalse(out["pre_1_0_or_freeze"])


@unittest.skipUnless(_GIT, "git required")
class TestTestCoverageDelta(unittest.TestCase):
    def test_half_ratio(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _write(repo, "src/a.ts", "x\n")
            base = _commit_all(repo, "init")
            _write(repo, "src/a.ts", "x\na\nb\nc\nd\n")    # +4 code
            _write(repo, "tests/a.test.ts", "test1\ntest2\n")  # +2 test
            _commit_all(repo, "change")
            out = _run_audit(repo, base, "HEAD")
        self.assertAlmostEqual(out["test_coverage_delta"], 0.5, places=2)

    def test_zero_when_no_tests_added(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _write(repo, "src/a.ts", "x\n")
            base = _commit_all(repo, "init")
            _write(repo, "src/a.ts", "x\na\nb\n")
            _commit_all(repo, "change")
            out = _run_audit(repo, base, "HEAD")
        self.assertEqual(out["test_coverage_delta"], 0.0)

    def test_zero_when_no_code_added(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _write(repo, "package.json", '{"version":"1.0.0"}\n')
            base = _commit_all(repo, "init")
            _write(repo, "package.json", '{"version":"1.0.1"}\n')
            _commit_all(repo, "bump")
            out = _run_audit(repo, base, "HEAD")
        self.assertEqual(out["test_coverage_delta"], 0.0)


@unittest.skipUnless(_GIT, "git required")
class TestSecurityPaths(unittest.TestCase):
    def test_auth_path_flags(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _write(repo, "src/auth/login.ts", "x\n")
            base = _commit_all(repo, "init")
            _write(repo, "src/auth/login.ts", "y\n")
            _commit_all(repo, "change")
            out = _run_audit(repo, base, "HEAD")
        self.assertTrue(out["security_sensitive_paths"])

    def test_crypto_path_flags(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _write(repo, "lib/crypto/sign.ts", "x\n")
            base = _commit_all(repo, "init")
            _write(repo, "lib/crypto/sign.ts", "y\n")
            _commit_all(repo, "change")
            out = _run_audit(repo, base, "HEAD")
        self.assertTrue(out["security_sensitive_paths"])

    def test_neutral_path_does_not_flag(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _write(repo, "src/utils/format.ts", "x\n")
            base = _commit_all(repo, "init")
            _write(repo, "src/utils/format.ts", "y\n")
            _commit_all(repo, "change")
            out = _run_audit(repo, base, "HEAD")
        self.assertFalse(out["security_sensitive_paths"])


@unittest.skipUnless(_GIT, "git required")
class TestPerformance(unittest.TestCase):
    """Smoke test — 1000-LOC diff completes in ≤2s on the maintainer's machine."""

    def test_1000_loc_under_2_seconds(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _new_repo(Path(t))
            _write(repo, "src/big.ts", "// start\n")
            base = _commit_all(repo, "init")
            body = "".join(f"const v{i} = {i};\n" for i in range(1000))
            _write(repo, "src/big.ts", body)
            _commit_all(repo, "big change")
            start = time.perf_counter()
            out = _run_audit(repo, base, "HEAD")
            elapsed = time.perf_counter() - start
        self.assertGreaterEqual(out["loc_changed"], 1000)
        self.assertLess(elapsed, 2.0, f"audit took {elapsed:.2f}s (>2s budget)")


@unittest.skipUnless(_GIT, "git required")
class TestErrors(unittest.TestCase):
    def test_non_repo_path_exits_2(self):
        with tempfile.TemporaryDirectory() as t:
            r = subprocess.run(
                [PYTHON, str(SCRIPT), "--repo", t, "--base", "HEAD"],
                capture_output=True, text=True, timeout=10,
            )
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
