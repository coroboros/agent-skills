"""Tests for the Ultra tier — build detection, spec-conformance cache,
property-fuzz harness synthesis, and the three --apply-safe writers.

Each writer is exercised via mocked `input()` so the confirmation gate
is verified end-to-end (mock returning `n` → no file writes; mock
returning `y` → write proceeds; `yes=True` → no prompt at all).
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO_ROOT / "skills" / "code-ultrareview" / "scripts"
APPLY_SAFE_DIR = SCRIPTS / "apply_safe"
FIXTURES = REPO_ROOT / "tests" / "code-ultrareview" / "fixtures" / "ultra"

# Add the scripts dir to sys.path so apply_safe sub-modules resolve their
# relative imports.
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


build_detect = _load("build_detect", SCRIPTS / "build_detect.py")

# apply_safe modules — load via the package import path (already on sys.path)
from apply_safe import (  # noqa: E402
    description_sync,
    failing_test_writer,
    version_sync,
)


# ---------------------------------------------------------------------------
# build_detect
# ---------------------------------------------------------------------------


class TestBuildDetect(unittest.TestCase):
    def test_pnpm_lock_picks_pnpm(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "pnpm-lock.yaml").write_text("", encoding="utf-8")
            (repo / "package.json").write_text(
                json.dumps({"scripts": {"test": "node --test"}}),
                encoding="utf-8",
            )
            result = build_detect.detect(repo)
        self.assertEqual(result["tool"], "pnpm")
        self.assertEqual(result["test_command"], "pnpm test")

    def test_yarn_lock_picks_yarn(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "yarn.lock").write_text("", encoding="utf-8")
            (repo / "package.json").write_text(
                json.dumps({"scripts": {"test": "node --test"}}),
                encoding="utf-8",
            )
            result = build_detect.detect(repo)
        self.assertEqual(result["tool"], "yarn")

    def test_package_manager_declaration_precedes_conflicting_lockfile(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "yarn.lock").write_text("", encoding="utf-8")
            (repo / "package.json").write_text(
                json.dumps({
                    "packageManager": "pnpm@10.13.1",
                    "scripts": {"test": "node --test"},
                }),
                encoding="utf-8",
            )
            result = build_detect.detect(repo)
        self.assertEqual(result["tool"], "pnpm")
        self.assertEqual(result["test_command"], "pnpm test")

    def test_bun_declaration_and_lock_use_declared_test_script(self):
        for package_json in (
            {"packageManager": "bun@1.2.18", "scripts": {"test": "vitest run"}},
            {"scripts": {"test": "vitest run"}},
        ):
            with self.subTest(package_manager=package_json.get("packageManager")):
                with tempfile.TemporaryDirectory() as t:
                    repo = Path(t)
                    (repo / "bun.lock").write_text("", encoding="utf-8")
                    (repo / "package.json").write_text(
                        json.dumps(package_json), encoding="utf-8"
                    )
                    result = build_detect.detect(repo)
                self.assertEqual(result["tool"], "bun")
                self.assertEqual(result["test_command"], "bun run test")

    def test_package_json_picks_npm(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "package.json").write_text(
                json.dumps({"scripts": {"test": "node --test"}}),
                encoding="utf-8",
            )
            result = build_detect.detect(repo)
        self.assertEqual(result["tool"], "npm")
        self.assertEqual(result["test_command"], "npm test")

    def test_package_json_without_test_script_does_not_invent_npm_test(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "package.json").write_text(
                json.dumps({"scripts": {"build": "node build.js"}}),
                encoding="utf-8",
            )
            result = build_detect.detect(repo)
        self.assertIsNone(result["tool"])
        self.assertIsNone(result["test_command"])

    def test_invalid_package_json_does_not_fall_through_to_another_stack(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "package.json").write_text("{broken\n", encoding="utf-8")
            (repo / "pyproject.toml").write_text(
                "[tool.pytest.ini_options]\n", encoding="utf-8"
            )

            with self.assertRaisesRegex(
                build_detect.InvalidManifestError,
                "package.json is not valid JSON",
            ):
                build_detect.detect(repo)

    def test_cli_reports_invalid_package_json_without_traceback(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "package.json").write_text("{broken\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "build_detect.py"), "--repo", str(repo)],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid project manifest", result.stderr)
        self.assertIn("repair package.json", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_pyproject_with_pytest_picks_pytest(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "pyproject.toml").write_text(
                "[tool.pytest.ini_options]\nminversion='7.0'\n", encoding="utf-8"
            )
            result = build_detect.detect(repo)
        self.assertEqual(result["tool"], "pytest")

    def test_python_manifest_without_runner_does_not_invent_unittest(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "pyproject.toml").write_text(
                '[project]\nname="x"\n', encoding="utf-8"
            )
            result = build_detect.detect(repo)
        self.assertIsNone(result["tool"])
        self.assertIsNone(result["test_command"])

    def test_collectable_unittest_suite_picks_unittest(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            tests = repo / "tests"
            tests.mkdir()
            (tests / "test_example.py").write_text(
                "import unittest\n\n"
                "class ExampleTest(unittest.TestCase):\n"
                "    def test_example(self):\n"
                "        self.assertTrue(True)\n",
                encoding="utf-8",
            )
            result = build_detect.detect(repo)
        self.assertEqual(result["tool"], "unittest")

    def test_cargo_toml_picks_cargo(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "Cargo.toml").write_text("[package]\nname='x'\n", encoding="utf-8")
            result = build_detect.detect(repo)
        self.assertEqual(result["tool"], "cargo")

    def test_go_mod_picks_go(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "go.mod").write_text("module x\n", encoding="utf-8")
            result = build_detect.detect(repo)
        self.assertEqual(result["tool"], "go")

    def test_makefile_with_test_target_picks_make(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "Makefile").write_text("test:\n\techo ok\n", encoding="utf-8")
            result = build_detect.detect(repo)
        self.assertEqual(result["tool"], "make")

    def test_empty_repo_returns_no_tool(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            result = build_detect.detect(repo)
        self.assertIsNone(result["tool"])

    def test_cli_emits_json(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "package.json").write_text(
                json.dumps({"scripts": {"test": "node --test"}}),
                encoding="utf-8",
            )
            r = subprocess.run(
                [sys.executable, str(SCRIPTS / "build_detect.py"), "--repo", str(repo)],
                capture_output=True, text=True, timeout=10,
            )
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertEqual(data["tool"], "npm")


# ---------------------------------------------------------------------------
# version_sync
# ---------------------------------------------------------------------------


class TestVersionSync(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self._init_git(self.repo)
        # Silence diff prints from confirm_write — writers are still exercised
        # via mocked input or yes=True.
        self._stdout_ctx = contextlib.redirect_stdout(io.StringIO())
        self._stdout_ctx.__enter__()

    def tearDown(self):
        self._stdout_ctx.__exit__(None, None, None)
        self.tmp.cleanup()

    def _init_git(self, repo: Path):
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "t@t"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
        subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=repo, check=True)
        subprocess.run(["git", "config", "core.hooksPath", os.devnull], cwd=repo, check=True)
        self._commit_counter = 0

    def _commit(self, msg: str):
        self._commit_counter += 1
        # Force monotonic commit timestamps so `_git_mtime`'s recency check
        # is deterministic regardless of how fast the test runs.
        ts = 1700000000 + self._commit_counter
        env = {
            **os.environ,
            "GIT_AUTHOR_DATE": f"@{ts} +0000",
            "GIT_COMMITTER_DATE": f"@{ts} +0000",
        }
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", msg], cwd=self.repo, env=env, check=True)

    def test_no_op_when_in_sync(self):
        (self.repo / "package.json").write_text(
            json.dumps({"version": "1.0.0"}, indent=2), encoding="utf-8"
        )
        (self.repo / ".claude-plugin").mkdir()
        (self.repo / ".claude-plugin" / "marketplace.json").write_text(
            json.dumps({"metadata": {"version": "1.0.0"}}, indent=2),
            encoding="utf-8",
        )
        self._commit("init")
        result = version_sync.sync(self.repo, yes=True)
        self.assertEqual(result["status"], "no-op")

    def test_recency_wins(self):
        (self.repo / "package.json").write_text(
            json.dumps({"version": "1.0.0"}, indent=2), encoding="utf-8"
        )
        (self.repo / ".claude-plugin").mkdir()
        (self.repo / ".claude-plugin" / "marketplace.json").write_text(
            json.dumps({"metadata": {"version": "1.0.0"}}, indent=2),
            encoding="utf-8",
        )
        self._commit("init both at 1.0.0")
        # Bump marketplace.json to 1.1.0 in a second commit — most-recent wins.
        (self.repo / ".claude-plugin" / "marketplace.json").write_text(
            json.dumps({"metadata": {"version": "1.1.0"}}, indent=2),
            encoding="utf-8",
        )
        self._commit("bump marketplace to 1.1.0")
        result = version_sync.sync(self.repo, yes=True)
        self.assertEqual(result["status"], "applied")
        self.assertEqual(result["canonical"], "1.1.0")

    def test_idempotent_second_run(self):
        (self.repo / "package.json").write_text(
            json.dumps({"version": "2.0.0"}, indent=2), encoding="utf-8"
        )
        (self.repo / ".claude-plugin").mkdir()
        (self.repo / ".claude-plugin" / "marketplace.json").write_text(
            json.dumps({"metadata": {"version": "1.0.0"}}, indent=2),
            encoding="utf-8",
        )
        self._commit("init")
        first = version_sync.sync(self.repo, yes=True)
        second = version_sync.sync(self.repo, yes=True)
        self.assertEqual(first["status"], "applied")
        self.assertEqual(second["status"], "no-op")

    def test_user_rejection_skips_write(self):
        (self.repo / "package.json").write_text(
            json.dumps({"version": "1.0.0"}, indent=2), encoding="utf-8"
        )
        (self.repo / ".claude-plugin").mkdir()
        (self.repo / ".claude-plugin" / "marketplace.json").write_text(
            json.dumps({"metadata": {"version": "1.1.0"}}, indent=2),
            encoding="utf-8",
        )
        self._commit("init")
        with contextlib.redirect_stdout(io.StringIO()), \
                mock.patch("builtins.input", return_value="n"):
            result = version_sync.sync(self.repo, yes=False)
        self.assertEqual(result["status"], "skipped")
        self.assertEqual(result["applied"], [])


# ---------------------------------------------------------------------------
# description_sync
# ---------------------------------------------------------------------------


class TestDescriptionSync(unittest.TestCase):
    def test_partial_agreement_refuses(self):
        fixture = FIXTURES / "description-partial-agreement"
        result = description_sync.sync(fixture, new_value="Gamma")
        self.assertEqual(result["status"], "refusing: partial-agreement")

    def test_full_agreement_no_op_when_already_matches(self):
        fixture = FIXTURES / "description-full-agreement"
        result = description_sync.sync(
            fixture, new_value="Original description that all sources share."
        )
        self.assertEqual(result["status"], "no-op")

    def test_force_apply_writes_when_sources_agree(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "package.json").write_text(
                json.dumps({"description": "old"}, indent=2), encoding="utf-8"
            )
            (repo / ".claude-plugin").mkdir()
            (repo / ".claude-plugin" / "marketplace.json").write_text(
                json.dumps({"metadata": {"description": "old"}}, indent=2),
                encoding="utf-8",
            )
            with contextlib.redirect_stdout(io.StringIO()):
                result = description_sync.force_apply_when_agreed(
                    repo, "new value", yes=True,
                )
        self.assertEqual(result["status"], "applied")
        self.assertEqual(result["canonical"], "new value")
        self.assertEqual(len(result["applied"]), 2)

    def test_force_apply_refuses_when_sources_disagree(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "package.json").write_text(
                json.dumps({"description": "alpha"}, indent=2), encoding="utf-8"
            )
            (repo / ".claude-plugin").mkdir()
            (repo / ".claude-plugin" / "marketplace.json").write_text(
                json.dumps({"metadata": {"description": "beta"}}, indent=2),
                encoding="utf-8",
            )
            with contextlib.redirect_stdout(io.StringIO()):
                result = description_sync.force_apply_when_agreed(repo, "gamma", yes=True)
        self.assertEqual(result["status"], "refusing: partial-agreement")


# ---------------------------------------------------------------------------
# failing_test_writer
# ---------------------------------------------------------------------------


class TestFailingTestWriter(unittest.TestCase):
    def setUp(self):
        self._stdout_ctx = contextlib.redirect_stdout(io.StringIO())
        self._stdout_ctx.__enter__()

    def tearDown(self):
        self._stdout_ctx.__exit__(None, None, None)

    def test_writes_python_test_file(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "tests").mkdir()
            (repo / "tests" / "existing.py").write_text("# existing\n", encoding="utf-8")
            result = failing_test_writer.write(
                repo, bug_id="zone-id-bug",
                repro="parseZoneId('illegal%') should reject",
                expected_failure="parser accepts invalid chars",
                yes=True,
            )
            self.assertEqual(result["status"], "applied")
            target = repo / result["target"]
            self.assertTrue(target.exists())
            self.assertIn("zone_id_bug", target.read_text(encoding="utf-8"))

    def test_writes_typescript_test_file(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "tests").mkdir()
            (repo / "tests" / "existing.test.ts").write_text(
                "// existing\n", encoding="utf-8"
            )
            result = failing_test_writer.write(
                repo, bug_id="overflow",
                repro="add(MAX_INT, 1) wraps to negative",
                expected_failure="overflow not detected",
                yes=True,
            )
            self.assertEqual(result["status"], "applied")
            self.assertTrue(result["target"].endswith(".test.ts"))

    def test_refuses_to_overwrite_existing_test(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "tests").mkdir()
            existing = repo / "tests" / "test_zone_id_bug.py"
            existing.write_text("# existing\n", encoding="utf-8")
            result = failing_test_writer.write(
                repo, bug_id="zone-id-bug",
                repro="…", expected_failure="…", yes=True,
            )
            self.assertEqual(result["status"], "refusing: existing-test")
            self.assertEqual(existing.read_text(encoding="utf-8"), "# existing\n")

    def test_user_rejection_skips_write(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            (repo / "tests").mkdir()
            (repo / "tests" / "existing.py").write_text("# existing\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()), \
                    mock.patch("builtins.input", return_value="n"):
                result = failing_test_writer.write(
                    repo, bug_id="bug-x",
                    repro="…", expected_failure="…", yes=False,
                )
        self.assertEqual(result["status"], "skipped")


# ---------------------------------------------------------------------------
# apply_safe confirm prompt
# ---------------------------------------------------------------------------


class TestApplySafeConfirm(unittest.TestCase):
    def test_mock_input_n_prevents_writes(self):
        from apply_safe._common import confirm_write
        with tempfile.TemporaryDirectory() as t:
            target = Path(t) / "f.txt"
            with contextlib.redirect_stdout(io.StringIO()), \
                    mock.patch("builtins.input", return_value="n"):
                approved = confirm_write(target, "diff text", yes=False)
        self.assertFalse(approved)

    def test_mock_input_y_approves(self):
        from apply_safe._common import confirm_write
        with tempfile.TemporaryDirectory() as t:
            target = Path(t) / "f.txt"
            with contextlib.redirect_stdout(io.StringIO()), \
                    mock.patch("builtins.input", return_value="y"):
                approved = confirm_write(target, "diff text", yes=False)
        self.assertTrue(approved)

    def test_yes_flag_bypasses_prompt(self):
        from apply_safe._common import confirm_write
        with contextlib.redirect_stdout(io.StringIO()), \
                mock.patch("builtins.input") as m:
            approved = confirm_write(Path("/tmp/f.txt"), "diff", yes=True)
        self.assertTrue(approved)
        m.assert_not_called()


if __name__ == "__main__":
    unittest.main()
