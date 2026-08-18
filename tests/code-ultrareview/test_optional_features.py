"""Behavioral contracts for Code Ultrareview's opt-in execution gates."""

from __future__ import annotations

import json
import os
import signal
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO_ROOT / "skills" / "code-ultrareview" / "scripts"
RUN_BUILD = SCRIPTS / "run_build_verify.py"
RUN_MUTATION = SCRIPTS / "run_mutation.py"
PROCESS_TIMEOUT = SCRIPTS / "process_timeout.py"
MUTATION_FIXTURES = REPO_ROOT / "tests/code-ultrareview/fixtures/mutation"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import manifest as manifest_contract  # noqa: E402
import run_mutation  # noqa: E402
import tool_runtime  # noqa: E402


def _executable(path: Path, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"#!/usr/bin/env bash\nset -eu\n{body}\n", encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return path


def _scope(repo: Path, files: list[str], languages: list[str]) -> Path:
    for relative in files:
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text("\n", encoding="utf-8")
    payload = {
        "base": "main",
        "target": "HEAD",
        "rule": "test",
        "repo_kind": "app",
        "languages": languages,
        "files_touched": len(files),
        "files_touched_list": files,
        "instruction_chain": [],
        "activates_coherence": False,
        "tools_skipped": [],
    }
    path = repo / "scope.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _findings(path: Path, confidence: int = 70) -> Path:
    finding = {
        "axis": "correctness",
        "severity": "High",
        "location": "src/app.py:1",
        "finding": "Example finding",
        "recommendation": "Fix the behavior.",
        "confidence": confidence,
    }
    path.write_text(json.dumps(finding) + "\n", encoding="utf-8")
    return path


def _run_build(repo: Path, scope: Path, env: dict | None = None, timeout: int = 10):
    findings = _findings(repo / "axis-findings.jsonl")
    output = repo / "build-findings.jsonl"
    result = subprocess.run(
        [
            sys.executable, str(RUN_BUILD), "--scope", str(scope),
            "--findings", str(findings), "--output", str(output),
            "--repo", str(repo), "--timeout", str(timeout),
        ],
        capture_output=True,
        text=True,
        timeout=timeout + 5,
        env=env,
        check=False,
    )
    return result, output


def _run_mutation(repo: Path, scope: Path, env: dict | None = None, timeout: int = 10):
    output = repo / "mutation"
    result = subprocess.run(
        [
            sys.executable, str(RUN_MUTATION), "--scope", str(scope),
            "--output-dir", str(output), "--repo", str(repo),
            "--timeout", str(timeout),
        ],
        capture_output=True,
        text=True,
        timeout=timeout + 5,
        env=env,
        check=False,
    )
    return result, output


class TestBuildGate(unittest.TestCase):
    def _unittest_repo(self, repo: Path, passing: bool) -> Path:
        scope = _scope(repo, ["src/app.py"], ["python"])
        (repo / "test_app.py").write_text(
            "import unittest\n\n"
            "class TestApp(unittest.TestCase):\n"
            "    def test_behavior(self):\n"
            f"        self.assertTrue({passing!r})\n",
            encoding="utf-8",
        )
        return scope

    def test_passing_suite_preserves_findings_and_completes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            result, output = _run_build(repo, self._unittest_repo(repo, True))
            state = json.loads((repo / "scope.json").read_text())["build_coverage"]
            finding = json.loads(output.read_text().strip())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(state["complete"])
        self.assertEqual(state["build_status"], "passed")
        self.assertEqual(finding["confidence"], 70)

    def test_failing_suite_blocks_without_changing_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            result, output = _run_build(repo, self._unittest_repo(repo, False))
            state = json.loads((repo / "scope.json").read_text())["build_coverage"]
            finding = json.loads(output.read_text().strip())
        self.assertEqual(result.returncode, 4)
        self.assertIn("fix every reported test failure", result.stderr)
        self.assertFalse(state["complete"])
        self.assertEqual(finding["confidence"], 70)

    def test_missing_test_command_blocks_with_actionable_remediation(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            result, output = _run_build(
                repo, _scope(repo, ["README.md"], ["markdown"])
            )
            output_exists = output.is_file()
        self.assertEqual(result.returncode, 3)
        self.assertIn("Add a canonical test entry", result.stderr)
        self.assertTrue(output_exists)

    def test_package_runner_receives_offline_environment(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope = _scope(repo, ["src/app.ts"], ["typescript"])
            (repo / "package.json").write_text(
                json.dumps({"scripts": {"test": "ignored"}}), encoding="utf-8"
            )
            capture = repo / "environment.txt"
            bin_dir = repo / "bin"
            _executable(
                bin_dir / "npm",
                'printf "%s\\n" "$COREPACK_ENABLE_NETWORK" '
                '"$COREPACK_ENABLE_DOWNLOAD_PROMPT" "$COREPACK_ENABLE_AUTO_PIN" '
                '"$COREPACK_DEFAULT_TO_LATEST" "$YARN_ENABLE_NETWORK" > "$ENV_CAPTURE"\n'
                'printf "# tests 1\\n"',
            )
            env = {
                **os.environ,
                "PATH": f"{bin_dir}:/usr/bin:/bin",
                "ENV_CAPTURE": str(capture),
            }
            result, _ = _run_build(repo, scope, env=env)
            values = capture.read_text().splitlines()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(values, ["0", "0", "0", "0", "0"])


class TestToolRuntime(unittest.TestCase):
    def test_declared_analyzer_never_falls_back_to_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src").mkdir()
            (repo / "src/app.ts").write_text("export {}\n", encoding="utf-8")
            (repo / "package.json").write_text(
                json.dumps({"devDependencies": {"knip": "1.0.0"}}),
                encoding="utf-8",
            )
            bin_dir = repo / "bin"
            _executable(bin_dir / "npm", "exit 0")
            _executable(bin_dir / "knip", "exit 0")
            with mock.patch.dict(os.environ, {"PATH": str(bin_dir)}):
                with self.assertRaisesRegex(tool_runtime.ContractError, "not installed"):
                    tool_runtime.resolve(repo, ["src/app.ts"], "knip", "knip")

    def test_installed_project_binary_runs_directly_for_every_manager(self):
        for manager in ("npm", "pnpm", "yarn", "bun"):
            with self.subTest(manager=manager), tempfile.TemporaryDirectory() as tmp:
                repo = Path(tmp)
                (repo / "src").mkdir()
                (repo / "src/app.ts").write_text("export {}\n", encoding="utf-8")
                (repo / "package.json").write_text(
                    json.dumps({
                        "packageManager": f"{manager}@1.0.0",
                        "devDependencies": {"analyzer-package": "1.0.0"},
                    }),
                    encoding="utf-8",
                )
                binary = repo / "node_modules/.bin/analyzer"
                binary.parent.mkdir(parents=True)
                binary.write_text("", encoding="utf-8")
                with mock.patch.dict(os.environ, {"PATH": "/usr/bin:/bin"}):
                    command, wrapper, env = tool_runtime.resolve(
                        repo, ["src/app.ts"], "analyzer-package", "analyzer"
                    )
                self.assertEqual(command, [str(binary.resolve())])
                self.assertEqual(wrapper, f"project:binary:{repo.resolve()}")
                self.assertEqual(env["COREPACK_ENABLE_NETWORK"], "0")
                self.assertEqual(env["YARN_ENABLE_NETWORK"], "0")

    def test_workspace_declared_analyzer_uses_hoisted_root_binary(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            package = repo / "packages/app"
            package.mkdir(parents=True)
            (package / "src.ts").write_text("export {}\n", encoding="utf-8")
            (package / "package.json").write_text(
                json.dumps({"devDependencies": {"knip": "1.0.0"}}),
                encoding="utf-8",
            )
            binary = repo / "node_modules/.bin/knip"
            _executable(binary, "exit 0")
            command, wrapper, _ = tool_runtime.resolve(
                repo, ["packages/app/src.ts"], "knip", "knip"
            )
        self.assertEqual(command, [str(binary.resolve())])
        self.assertEqual(wrapper, f"project:binary:{package.resolve()}")

    def test_yarn_pnp_runs_from_its_declaring_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src").mkdir()
            (repo / "src/app.ts").write_text("export {}\n", encoding="utf-8")
            (repo / "package.json").write_text(
                json.dumps({
                    "packageManager": "yarn@4.0.0",
                    "devDependencies": {"analyzer-package": "1.0.0"},
                }),
                encoding="utf-8",
            )
            (repo / ".pnp.cjs").write_text("", encoding="utf-8")
            bin_dir = repo / "bin"
            _executable(bin_dir / "yarn", "exit 0")
            with mock.patch.dict(os.environ, {"PATH": str(bin_dir)}):
                command, wrapper, _ = tool_runtime.resolve(
                    repo, ["src/app.ts"], "analyzer-package", "analyzer"
                )
        self.assertEqual(command, ["yarn", "run", "-B", "analyzer"])
        self.assertEqual(wrapper, f"project:yarn-pnp:{repo.resolve()}")

    def test_project_runtime_exec_changes_to_declaring_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope = _scope(repo, ["src/app.ts"], ["typescript"])
            (repo / "package.json").write_text(json.dumps({
                "devDependencies": {"analyzer-package": "1.0.0"},
            }), encoding="utf-8")
            binary = repo / "node_modules/.bin/analyzer"
            _executable(binary, "exit 0")
            with mock.patch.object(sys, "argv", [
                str(SCRIPTS / "tool_runtime.py"), "--repo", str(repo),
                "--scope", str(scope), "--package", "analyzer-package",
                "--binary", "analyzer", "exec",
            ]), mock.patch.object(tool_runtime.os, "chdir") as chdir, \
                    mock.patch.object(tool_runtime.os, "execvpe", side_effect=SystemExit):
                with self.assertRaises(SystemExit):
                    tool_runtime.main()
        chdir.assert_called_once_with(str(repo.resolve()))


class TestMutationGate(unittest.TestCase):
    def test_no_applicable_language_is_a_complete_empty_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            result, output = _run_mutation(
                repo, _scope(repo, ["README.md"], ["markdown"])
            )
            state = json.loads((repo / "scope.json").read_text())["mutation_coverage"]
            findings = (output / "mutation-findings.jsonl").read_text()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(findings, "")
        self.assertEqual(state["status"], "not-applicable")
        self.assertTrue(state["complete"])

    def test_missing_mutmut_blocks_with_project_environment_fix(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            result, output = _run_mutation(
                repo,
                _scope(repo, ["src/app.py"], ["python"]),
                env={**os.environ, "PATH": "/usr/bin:/bin"},
            )
        self.assertEqual(result.returncode, 3)
        self.assertIn("project's test environment", result.stderr)
        self.assertIn("command -v mutmut", result.stderr)
        self.assertFalse((output / "mutation-findings.jsonl").exists())

    def test_declared_stryker_never_falls_back_to_global_binary(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope_path = _scope(repo, ["src/app.ts"], ["typescript"])
            (repo / "package.json").write_text(json.dumps({
                "devDependencies": {"@stryker-mutator/core": "9.4.0"},
            }), encoding="utf-8")
            bin_dir = repo / "bin"
            _executable(bin_dir / "stryker", "exit 0")
            scope = json.loads(scope_path.read_text())
            with mock.patch.dict(os.environ, {"PATH": str(bin_dir)}):
                plan, runtimes = run_mutation.preflight(repo, scope)
        self.assertNotIn("stryker", runtimes)
        self.assertEqual(plan["missing"][0]["tool"], "stryker")
        self.assertIn("declared analyzer is not installed", plan["missing"][0]["reason"])

    def test_stryker_real_schema_ignores_disabled_mutants(self):
        findings = run_mutation.parse_stryker(
            MUTATION_FIXTURES / "stryker.json", Path("/repo"), Path("/repo"),
            ["src/app.ts"],
        )
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["location"], "src/app.ts:1:27")
        self.assertIn("Surviving", findings[0]["finding"])

    def test_stryker_pending_mutant_is_incomplete(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "mutation.json"
            payload = json.loads(
                (MUTATION_FIXTURES / "stryker.json").read_text(encoding="utf-8")
            )
            payload["files"]["src/app.ts"]["mutants"][0]["status"] = "Pending"
            report.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(run_mutation.MutationFailure, "Pending"):
                run_mutation.parse_stryker(
                    report, Path("/repo"), Path("/repo"), ["src/app.ts"]
                )

    def test_stryker_scope_excludes_tests_and_declarations(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope = json.loads(_scope(repo, [
                "src/app.ts", "src/app.test.ts", "src/types.d.ts",
                "src/__tests__/helper.ts",
            ], ["typescript"]).read_text())
            files = run_mutation.stryker_files(repo, scope)
        self.assertEqual(files, ["src/app.ts"])

    def test_jvm_preflight_reports_one_actionable_build_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope = json.loads(_scope(
                repo, ["src/main/java/App.java"], ["java"]
            ).read_text())
            plan, runtimes = run_mutation.preflight(repo, scope)

        self.assertEqual(runtimes, {})
        self.assertEqual(len(plan["missing"]), 1)
        self.assertEqual(plan["missing"][0]["tool"], "pitest-build")
        self.assertIn("one Pitest-enabled", plan["missing"][0]["remediation"])

    def test_jvm_preflight_requires_the_path_runner(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope_path = _scope(repo, ["src/main/java/App.java"], ["java"])
            (repo / "pom.xml").write_text("<project/>\n", encoding="utf-8")
            empty_path = repo / "empty-path"
            empty_path.mkdir()
            scope = json.loads(scope_path.read_text())
            with mock.patch.dict(os.environ, {"PATH": str(empty_path)}):
                plan, runtimes = run_mutation.preflight(repo, scope)

        self.assertEqual(runtimes, {})
        self.assertEqual(plan["missing"][0]["tool"], "maven")
        self.assertIn("command -v mvn", plan["missing"][0]["remediation"])
        self.assertNotIn("wrapper", plan["missing"][0]["remediation"])

    def _mutmut(self, repo: Path, results: str, show: str = "") -> dict:
        bin_dir = repo / "bin"
        body = (
            'case "${1:-}" in\n'
            '  run) exit 0 ;;\n'
            '  results) shift; [[ "$#" -eq 2 && "$1" == "--all" && "$2" == "true" ]] '
            '|| { echo "expected: results --all true" >&2; exit 64; }; '
            f"printf '%b' {json.dumps(results)} ;;\n"
            f"  show) printf '%b' {json.dumps(show)} ;;\n"
            '  *) exit 64 ;;\n'
            'esac'
        )
        _executable(bin_dir / "mutmut", body)
        return {**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin"}

    def test_mutmut_boolean_all_accepts_zero_survivors(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            result, output = _run_mutation(
                repo,
                _scope(repo, ["src/app.py"], ["python"]),
                env=self._mutmut(repo, "    app.x__mutmut_1: killed\n"),
            )
            findings = (output / "mutation-findings.jsonl").read_text()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(findings, "")

    def test_mutmut_zero_evaluated_mutants_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            result, output = _run_mutation(
                repo,
                _scope(repo, ["src/app.py"], ["python"]),
                env=self._mutmut(repo, ""),
            )
        self.assertEqual(result.returncode, 4)
        self.assertIn("zero evaluated mutants", result.stderr)
        self.assertFalse((output / "mutation-findings.jsonl").exists())

    def test_mutmut_survivor_maps_to_changed_file(self):
        results = (MUTATION_FIXTURES / "mutmut-results.txt").read_text()
        show = (MUTATION_FIXTURES / "mutmut-show.txt").read_text()
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope = _scope(repo, ["calc/__init__.py"], ["python"])
            (repo / "calc/__init__.py").write_text(
                '"""Fixture."""\n\nCONSTANT = 1\n\ndef clamp(value):\n'
                '    return max(0, value)\n', encoding="utf-8",
            )
            result, output = _run_mutation(
                repo,
                scope,
                env=self._mutmut(repo, results, show),
            )
            finding = json.loads((output / "mutation-findings.jsonl").read_text())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(finding["source_tool"], "mutmut")
        self.assertEqual(finding["location"], "calc/__init__.py:5")
        self.assertEqual(finding["confidence"], 100)

    def test_incomplete_mutmut_result_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            result, output = _run_mutation(
                repo,
                _scope(repo, ["src/app.py"], ["python"]),
                env=self._mutmut(repo, "app.x__mutmut_1: skipped\n"),
            )
        self.assertEqual(result.returncode, 4)
        self.assertIn("incomplete mutmut results", result.stderr)
        self.assertFalse((output / "mutation-findings.jsonl").exists())

    def test_pitest_maps_multi_module_reports(self):
        xml = (
            '<mutations><mutation status="SURVIVED">'
            '<sourceFile>{name}.java</sourceFile>'
            '<mutatedClass>com.acme.{name}</mutatedClass>'
            '<lineNumber>12</lineNumber><description>changed return</description>'
            '</mutation></mutations>'
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports, changed = [], []
            for module, name in (("alpha", "Alpha"), ("beta", "Beta")):
                report = root / module / "target/pit-reports/mutations.xml"
                report.parent.mkdir(parents=True)
                report.write_text(xml.format(name=name), encoding="utf-8")
                reports.append(report)
                changed.append(f"{module}/src/main/java/com/acme/{name}.java")
            findings = run_mutation.parse_pitest(reports, changed)
        self.assertEqual({item["location"] for item in findings}, {
            "alpha/src/main/java/com/acme/Alpha.java:12",
            "beta/src/main/java/com/acme/Beta.java:12",
        })

    def test_pitest_uses_a_path_runner_from_the_governing_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            project = repo / "service"
            source = project / "src/main/java/App.java"
            source.parent.mkdir(parents=True)
            source.write_text("class App {}\n", encoding="utf-8")
            (project / "pom.xml").write_text("<project/>\n", encoding="utf-8")
            _executable(project / "mvnw", "exit 99")
            bin_dir = repo / "bin"
            runner = _executable(bin_dir / "mvn", "exit 0")
            scope = json.loads(_scope(
                repo, ["service/src/main/java/App.java"], ["java"]
            ).read_text())
            with mock.patch.dict(os.environ, {"PATH": str(bin_dir)}):
                plan, runtimes = run_mutation.preflight(repo, scope)
        self.assertTrue(plan["complete"])
        command, cwd, _env, _changed, build, root = runtimes["pitest"]
        self.assertEqual(command, [str(runner)])
        self.assertEqual(cwd, project)
        self.assertEqual(build, "maven")
        self.assertEqual(root, repo)


class TestProcessTimeout(unittest.TestCase):
    def test_timeout_terminates_descendants(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = root / "leaked"
            result = subprocess.run(
                [
                    sys.executable, str(PROCESS_TIMEOUT), "--timeout", "1",
                    "--cwd", str(root), "--", "bash", "-c",
                    f"(sleep 2; printf leaked > {marker}) & wait",
                ],
                capture_output=True,
                text=True,
                timeout=6,
                check=False,
            )
            time.sleep(1.5)
            leaked = marker.exists()
        self.assertEqual(result.returncode, 124)
        self.assertIn("process group was terminated", result.stderr)
        self.assertFalse(leaked)

    @unittest.skipIf(os.name != "posix", "requires POSIX process groups")
    def test_parent_sigterm_is_forwarded_to_child_group(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker, ready = root / "forwarded", root / "ready"
            child = _executable(
                root / "child.sh",
                'trap \'printf forwarded > "$1"; exit 0\' TERM\n'
                'printf ready > "$2"\n'
                'while :; do sleep 1; done',
            )
            process = subprocess.Popen(
                [
                    sys.executable, str(PROCESS_TIMEOUT), "--timeout", "20",
                    "--cwd", str(root), "--", str(child), str(marker), str(ready),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            deadline = time.time() + 3
            while not ready.exists() and time.time() < deadline:
                time.sleep(0.05)
            self.assertTrue(ready.exists(), "child did not start")
            os.kill(process.pid, signal.SIGTERM)
            process.communicate(timeout=5)
            forwarded = marker.exists()
        self.assertTrue(forwarded)
        self.assertEqual(process.returncode, 143)

    @unittest.skipIf(os.name != "posix", "requires POSIX process groups")
    def test_parent_sigterm_kills_a_group_that_ignores_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker, ready = root / "leaked", root / "ready"
            child = _executable(
                root / "child.sh",
                "trap '' TERM\n"
                '(sleep 3; printf leaked > "$1") &\n'
                'printf ready > "$2"\n'
                "wait",
            )
            process = subprocess.Popen(
                [
                    sys.executable, str(PROCESS_TIMEOUT), "--timeout", "20",
                    "--cwd", str(root), "--", str(child), str(marker), str(ready),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            deadline = time.time() + 3
            while not ready.exists() and time.time() < deadline:
                time.sleep(0.05)
            self.assertTrue(ready.exists(), "child did not start")
            started = time.monotonic()
            os.kill(process.pid, signal.SIGTERM)
            process.communicate(timeout=5)
            elapsed = time.monotonic() - started
            time.sleep(1.1)
            leaked = marker.exists()
        self.assertEqual(process.returncode, 143)
        self.assertLess(elapsed, 4)
        self.assertFalse(leaked)


class TestCoverageArtifacts(unittest.TestCase):
    def test_scope_rejects_paths_outside_the_repository(self):
        for path in ("../outside.py", "/tmp/outside.py"):
            with self.subTest(path=path), tempfile.TemporaryDirectory() as tmp:
                repo = Path(tmp)
                scope = _scope(repo, ["README.md"], ["markdown"])
                payload = json.loads(scope.read_text())
                payload["files_touched_list"] = [path]
                scope.write_text(json.dumps(payload), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "stay inside"):
                    manifest_contract.read_scope(scope)

    def test_tampered_output_is_rejected_by_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scope = _scope(repo, ["README.md"], ["markdown"])
            output = repo / "findings.jsonl"
            manifest_contract.write_jsonl_atomic(output, [])
            manifest_contract.set_phase(
                scope,
                "tool",
                {"complete": True, "applicable": [], "executed": []},
                output,
            )
            output.write_text("{}\n", encoding="utf-8")
            state = json.loads(scope.read_text())["tool_coverage"]
            with self.assertRaisesRegex(ValueError, "changed after prepare"):
                manifest_contract.verify_jsonl_output(state, output, "tool findings")

    def test_atomic_write_preserves_previous_file_on_replace_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "state.json"
            target.write_text("old\n", encoding="utf-8")
            with mock.patch.object(
                manifest_contract.os, "replace", side_effect=OSError("fail")
            ):
                with self.assertRaises(OSError):
                    manifest_contract.write_json_atomic(target, {"new": True})
            self.assertEqual(target.read_text(), "old\n")


if __name__ == "__main__":
    unittest.main()
