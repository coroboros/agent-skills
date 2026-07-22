"""Tests for skills/design-system/scripts/{audit,diff,export,spec}.sh.

Strategy: argument-validation and missing-file branches run unconditionally.
For exit-code propagation and stderr handling we stub `designmd` in a fake-bin
directory and prepend it to PATH so the script's availability check succeeds
and the stub's exit code/stderr is what gets propagated. That keeps the
tests deterministic and free of network/install side-effects.
"""

import json
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


def _run(
    script_name: str,
    *args: str,
    fake_bin: Path | None = None,
    cwd: Path | None = None,
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
        cwd=cwd,
        timeout=30,
    )


LINT_CLEAN = (
    '{"findings":[],"summary":{"errors":0,"warnings":0,"infos":0}}'
)
LINT_ERRORS = (
    '{"findings":[{"severity":"error","message":"broken token"}],'
    '"summary":{"errors":1,"warnings":0,"infos":0}}'
)
EMPTY_TOKEN_DIFF = {
    group: {"added": [], "removed": [], "modified": []}
    for group in ("colors", "typography", "rounded", "spacing", "components")
}
DIFF_CLEAN = json.dumps(
    {
        "tokens": EMPTY_TOKEN_DIFF,
        "findings": {
            "before": {"errors": 0, "warnings": 0, "infos": 0},
            "after": {"errors": 0, "warnings": 0, "infos": 0},
            "delta": {"errors": 0, "warnings": 0},
        },
        "regression": False,
    }
)
DIFF_REGRESSION = json.dumps(
    {
        "tokens": EMPTY_TOKEN_DIFF,
        "findings": {
            "before": {"errors": 0, "warnings": 0, "infos": 0},
            "after": {"errors": 1, "warnings": 0, "infos": 0},
            "delta": {"errors": 1, "warnings": 0},
        },
        "regression": True,
    }
)
TAILWIND_EXPORT = json.dumps(
    {
        "theme": {
            "extend": {
                "colors": {},
                "fontFamily": {},
                "fontSize": {},
                "borderRadius": {},
                "spacing": {},
            }
        }
    }
)
DTCG_EXPORT = json.dumps(
    {
        "$schema": "https://www.designtokens.org/schemas/2025.10/format.json",
        "color": {
            "$type": "color",
            "primary": {"$value": "#112233"},
        },
    }
)


def _make_yarn_pnp_stub(bin_dir: Path) -> None:
    _make_stub(
        bin_dir,
        "yarn",
        "#!/bin/bash\n"
        '[[ "$COREPACK_ENABLE_NETWORK" == "0" ]] || exit 65\n'
        '[[ "$COREPACK_DEFAULT_TO_LATEST" == "0" ]] || exit 66\n'
        '[[ "$YARN_ENABLE_NETWORK" == "0" ]] || exit 67\n'
        'if [[ "$3" == "bin" && "$4" == "designmd" ]]; then exit 0; fi\n'
        '[[ "$3" == "run" && "$4" == "-B" && "$5" == "designmd" ]] || exit 64\n'
        'if [[ "$6" == "--version" ]]; then printf "0.3.0\\n"; exit 0; fi\n'
        'case "$6" in\n'
        '  lint)\n'
        '    [[ "$9" == /* && -f "$9" ]] || exit 68\n'
        f"    printf '%s\\n' '{LINT_CLEAN}'\n"
        '    ;;\n'
        '  diff)\n'
        '    [[ "$9" == /* && -f "$9" && "${10}" == /* && -f "${10}" ]] || exit 69\n'
        f"    printf '%s\\n' '{DIFF_CLEAN}'\n"
        '    ;;\n'
        '  export)\n'
        '    [[ "$9" == /* && -f "$9" ]] || exit 70\n'
        f"    printf '%s\\n' '{TAILWIND_EXPORT}'\n"
        '    ;;\n'
        '  *) exit 71 ;;\n'
        'esac\n',
    )


def _make_json_stub(bin_dir: Path, payload: str, rc: int = 0) -> None:
    _make_stub(
        bin_dir,
        "designmd",
        "#!/bin/sh\n"
        'if [ "$1" = "--version" ]; then echo 0.3.0; exit 0; fi\n'
        f"printf '%s\\n' '{payload}'\n"
        f"exit {rc}\n",
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

    def _nested_yarn_pnp_project(self) -> tuple[Path, Path]:
        root = self.tmp / "workspace"
        nested = root / "packages" / "web"
        nested.mkdir(parents=True)
        (root / "package.json").write_text(
            '{"private":true,"packageManager":"yarn@4.9.2",'
            '"workspaces":["packages/*"]}\n',
            encoding="utf-8",
        )
        (root / "yarn.lock").write_text("", encoding="utf-8")
        (nested / "package.json").write_text(
            '{"name":"web","devDependencies":{"@google/design.md":"0.3.0"}}\n',
            encoding="utf-8",
        )
        return root, nested


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
    """Stub designmd so the CLI branch runs deterministically."""

    def test_cli_exit_0_reports_status_ok(self):
        # `lint` exit 0 = no errors; script must exit 0 and emit status=ok.
        _make_json_stub(self.fake_bin, LINT_CLEAN)
        design = self._design_md()
        r = _run("audit.sh", str(design), fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 0)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "ok")
        self.assertEqual(kv.get("path"), str(design))
        self.assertEqual(kv.get("exit-code"), "0")
        self.assertTrue(Path(kv.get("json", "")).is_file())

    def test_cli_exit_1_propagated_as_lint_errors(self):
        # `lint` exit 1 = errors found, valid run; script must exit 1 with status=ok.
        _make_json_stub(self.fake_bin, LINT_ERRORS, rc=1)
        design = self._design_md()
        r = _run("audit.sh", str(design), fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 1)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "ok")
        self.assertEqual(kv.get("exit-code"), "1")

    def test_nested_yarn_pnp_accepts_caller_relative_path(self):
        root, nested = self._nested_yarn_pnp_project()
        design = nested / "DESIGN.md"
        design.write_text("# DESIGN\n", encoding="utf-8")
        _make_yarn_pnp_stub(self.fake_bin)

        result = _run(
            "audit.sh",
            str(design.relative_to(root)),
            fake_bin=self.fake_bin,
            cwd=root,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(_result_kv(result.stdout).get("status"), "ok")
        self.assertEqual(_result_kv(result.stdout).get("cli-wrapper"), "yarn-pnp")

    def test_invalid_json_schema_blocks_the_audit(self):
        _make_json_stub(self.fake_bin, "{}")
        design = self._design_md()

        result = _run("audit.sh", str(design), fake_bin=self.fake_bin)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(_result_kv(result.stdout).get("status"), "cli-invalid-output")

    def test_summary_and_exit_code_must_match_findings(self):
        inconsistent = (
            '{"findings":[{"severity":"error","message":"broken"}],'
            '"summary":{"errors":0,"warnings":0,"infos":0}}'
        )
        _make_json_stub(self.fake_bin, inconsistent, rc=0)
        design = self._design_md()

        result = _run("audit.sh", str(design), fake_bin=self.fake_bin)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(_result_kv(result.stdout).get("status"), "cli-invalid-output")

    def test_cli_exit_higher_reports_cli_failed_with_stderr(self):
        # rc > 1 = real CLI failure; script must report cli-failed and propagate stderr file.
        _make_stub(
            self.fake_bin,
            "designmd",
            '#!/bin/sh\n'
            'if [ "$1" = "--version" ]; then echo 0.3.0; exit 0; fi\n'
            'echo boom >&2\nexit 7\n',
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

    def test_missing_cli_fails_without_runtime_resolution(self):
        design = self._design_md()
        r = _run("audit.sh", str(design))
        self.assertEqual(r.returncode, 1)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "designmd-missing")
        self.assertEqual(
            kv.get("install"),
            f"npm --prefix {self.tmp.resolve()} install --save-dev "
            "@google/design.md",
        )
        self.assertEqual(
            kv.get("rerun"),
            f"bash {SCRIPTS / 'audit.sh'} {design}",
        )
        self.assertIn("exact rerun command", kv.get("remediation", ""))

    def test_invalid_project_manifest_blocks_global_fallback(self):
        project = self.tmp / "invalid-project"
        project.mkdir()
        design = project / "DESIGN.md"
        design.write_text("# DESIGN\n", encoding="utf-8")
        (project / "package.json").write_text("{broken\n", encoding="utf-8")
        marker = self.tmp / "global-ran"
        _make_stub(
            self.fake_bin,
            "designmd",
            "#!/bin/sh\n"
            f'touch "{marker}"\n'
            "printf '0.3.0\\n'\n",
        )

        result = _run("audit.sh", str(design), fake_bin=self.fake_bin)

        self.assertEqual(result.returncode, 1)
        metadata = _result_kv(result.stdout)
        self.assertEqual(metadata.get("status"), "invalid-project-manifest")
        self.assertEqual(
            Path(metadata.get("path", "")).resolve(),
            (project / "package.json").resolve(),
        )
        self.assertIn("Repair package.json", metadata.get("remediation", ""))
        self.assertIn("audit.sh", metadata.get("rerun", ""))
        self.assertFalse(marker.exists())

    def test_non_object_dependency_map_is_an_invalid_project_manifest(self):
        project = self.tmp / "invalid-dependencies"
        project.mkdir()
        design = project / "DESIGN.md"
        design.write_text("# DESIGN\n", encoding="utf-8")
        (project / "package.json").write_text(
            '{"devDependencies":["@google/design.md"]}\n',
            encoding="utf-8",
        )

        result = _run("audit.sh", str(design))

        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            _result_kv(result.stdout).get("status"),
            "invalid-project-manifest",
        )

    def test_missing_cli_install_command_matches_project_package_manager(self):
        cases = (
            ("pnpm", '{"packageManager":"pnpm@10.0.0"}\n', "pnpm --dir {project} add -D @google/design.md"),
            ("yarn", '{"packageManager":"yarn@4.0.0"}\n', "yarn --cwd {project} add -D @google/design.md"),
            ("bun", '{"packageManager":"bun@1.2.0"}\n', "bun --cwd {project} add -d @google/design.md"),
            ("npm", '{"packageManager":"npm@11.0.0"}\n', "npm --prefix {project} install --save-dev @google/design.md"),
        )
        for name, package_json, expected in cases:
            with self.subTest(package_manager=name):
                project = self.tmp / name
                project.mkdir()
                (project / "package.json").write_text(package_json, encoding="utf-8")
                design = project / "DESIGN.md"
                design.write_text("# DESIGN\n", encoding="utf-8")
                result = _run("audit.sh", str(design))
                self.assertEqual(result.returncode, 1)
                self.assertEqual(
                    _result_kv(result.stdout).get("install"),
                    expected.format(project=project.resolve()),
                )

    def test_pnpm_workspace_install_targets_the_workspace_root(self):
        (self.tmp / "pnpm-workspace.yaml").write_text(
            "packages:\n  - packages/*\n", encoding="utf-8"
        )
        (self.tmp / "package.json").write_text(
            '{"packageManager":"pnpm@10.0.0"}\n', encoding="utf-8"
        )
        design = self.tmp / "DESIGN.md"
        design.write_text("# DESIGN\n", encoding="utf-8")

        result = _run("audit.sh", str(design))

        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            _result_kv(result.stdout).get("install"),
            f"pnpm --dir {self.tmp.resolve()} add -Dw @google/design.md",
        )

    def test_nested_package_install_command_makes_exact_rerun_succeed(self):
        root = self.tmp / "workspace"
        root.mkdir()
        root_manifest = root / "package.json"
        root_manifest.write_text('{"name":"unrelated-root"}\n', encoding="utf-8")
        nested = root / "vendor" / "design"
        nested.mkdir(parents=True)
        (nested / "package.json").write_text(
            '{"name":"vendored-design"}\n', encoding="utf-8"
        )
        design = nested / "DESIGN.md"
        design.write_text("# DESIGN\n", encoding="utf-8")
        _make_stub(
            self.fake_bin,
            "npm",
            "#!/bin/bash\n"
            '[[ "$1" == "--prefix" && "$3" == "install" ]] || exit 61\n'
            '[[ "$4" == "--save-dev" && "$5" == "@google/design.md" ]] || exit 62\n'
            'project="$2"\n'
            'mkdir -p "$project/node_modules/.bin"\n'
            'printf \'%s\\n\' \'{"name":"vendored-design","devDependencies":{"@google/design.md":"0.3.0"}}\' > "$project/package.json"\n'
            'cat > "$project/node_modules/.bin/designmd" <<\'SHIM\'\n'
            "#!/bin/sh\n"
            'if [ "$1" = "--version" ]; then printf \'0.3.0\\n\'; exit 0; fi\n'
            f"printf '%s\\n' '{LINT_CLEAN}'\n"
            "SHIM\n"
            'chmod +x "$project/node_modules/.bin/designmd"\n',
        )
        workspace_env = {"DESIGNMD_WORKSPACE_ROOT": str(root)}

        first = _run(
            "audit.sh",
            str(design),
            fake_bin=self.fake_bin,
            extra_env=workspace_env,
        )
        install = _result_kv(first.stdout).get("install", "")
        installed = subprocess.run(
            ["bash", "-c", install],
            capture_output=True,
            text=True,
            env={
                **os.environ,
                "PATH": f"{self.fake_bin}:/usr/bin:/bin:/usr/sbin:/sbin",
            },
            timeout=10,
        )
        rerun = _run(
            "audit.sh",
            str(design),
            fake_bin=self.fake_bin,
            extra_env=workspace_env,
        )

        self.assertEqual(first.returncode, 1, first.stdout + first.stderr)
        self.assertEqual(
            install,
            f"npm --prefix {nested.resolve()} install --save-dev "
            "@google/design.md",
        )
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertEqual(rerun.returncode, 0, rerun.stdout + rerun.stderr)
        self.assertEqual(_result_kv(rerun.stdout).get("status"), "ok")
        self.assertEqual(
            root_manifest.read_text(encoding="utf-8"),
            '{"name":"unrelated-root"}\n',
        )

    def test_project_local_cli_precedes_path(self):
        local_bin = self.tmp / "node_modules" / ".bin"
        local_bin.mkdir(parents=True)
        _make_json_stub(local_bin, LINT_CLEAN)
        (self.tmp / "package.json").write_text(
            '{"devDependencies":{"@google/design.md":"0.1.1"}}\n',
            encoding="utf-8",
        )
        _make_stub(self.fake_bin, "designmd", "#!/bin/sh\nexit 9\n")
        project_dir = self.tmp / "apps" / "web"
        project_dir.mkdir(parents=True)
        design = project_dir / "DESIGN.md"
        design.write_text("# DESIGN\n")

        r = _run(
            "audit.sh",
            str(design),
            fake_bin=self.fake_bin,
            extra_env={"DESIGNMD_WORKSPACE_ROOT": str(self.tmp)},
        )

        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(_result_kv(r.stdout).get("status"), "ok")

    def test_declared_yarn_pnp_cli_runs_without_node_modules(self):
        project = self.tmp / "yarn-pnp"
        project.mkdir()
        design = project / "DESIGN.md"
        design.write_text("# DESIGN\n", encoding="utf-8")
        (project / "package.json").write_text(
            '{"packageManager":"yarn@4.9.2",'
            '"devDependencies":{"@google/design.md":"0.3.0"}}\n',
            encoding="utf-8",
        )
        (project / "yarn.lock").write_text("", encoding="utf-8")
        marker = self.tmp / "yarn-runs.log"
        _make_stub(
            self.fake_bin,
            "yarn",
            "#!/bin/bash\n"
            '[[ "$COREPACK_ENABLE_NETWORK" == "0" ]] || exit 65\n'
            '[[ "$COREPACK_DEFAULT_TO_LATEST" == "0" ]] || exit 66\n'
            '[[ "$YARN_ENABLE_NETWORK" == "0" ]] || exit 67\n'
            'if [[ "$3" == "bin" && "$4" == "designmd" ]]; then exit 0; fi\n'
            'if [[ "$3" != "run" || "$4" != "-B" || "$5" != "designmd" ]]; then exit 64; fi\n'
            f'printf "%s\\n" "$*" >> "{marker}"\n'
            'if [[ "$6" == "--version" ]]; then printf "0.3.0\\n"; exit 0; fi\n'
            f"printf '%s\\n' '{LINT_CLEAN}'\n",
        )

        result = _run("audit.sh", str(design), fake_bin=self.fake_bin)

        self.assertEqual(result.returncode, 0, result.stderr)
        metadata = _result_kv(result.stdout)
        self.assertEqual(metadata.get("status"), "ok")
        self.assertEqual(metadata.get("cli-wrapper"), "yarn-pnp")
        self.assertIn("run -B designmd", metadata.get("cli", ""))
        self.assertFalse((project / "node_modules").exists())
        self.assertEqual(len(marker.read_text(encoding="utf-8").splitlines()), 3)

    def test_declared_yarn_pnp_never_falls_back_to_global_cli(self):
        project = self.tmp / "yarn-pnp"
        project.mkdir()
        design = project / "DESIGN.md"
        design.write_text("# DESIGN\n", encoding="utf-8")
        (project / "package.json").write_text(
            '{"packageManager":"yarn@4.9.2",'
            '"devDependencies":{"@google/design.md":"0.3.0"}}\n',
            encoding="utf-8",
        )
        (project / "yarn.lock").write_text("", encoding="utf-8")
        _make_stub(self.fake_bin, "yarn", "#!/bin/sh\nexit 1\n")
        _make_json_stub(self.fake_bin, LINT_CLEAN)

        result = _run("audit.sh", str(design), fake_bin=self.fake_bin)

        self.assertEqual(result.returncode, 1)
        metadata = _result_kv(result.stdout)
        self.assertEqual(metadata.get("status"), "yarn-runtime-unavailable")
        self.assertIn("corepack install --global yarn@4.9.2", metadata.get("install", ""))
        self.assertIn("yarn --cwd", metadata.get("install", ""))
        self.assertIn("install --immutable", metadata.get("install", ""))
        self.assertIn("audit.sh", metadata.get("rerun", ""))

    def test_declared_yarn_without_lockfile_requires_reviewed_restore(self):
        project = self.tmp / "yarn-no-lock"
        project.mkdir()
        design = project / "DESIGN.md"
        design.write_text("# DESIGN\n", encoding="utf-8")
        (project / "package.json").write_text(
            '{"packageManager":"yarn@4.9.2",'
            '"devDependencies":{"@google/design.md":"0.3.0"}}\n',
            encoding="utf-8",
        )
        _make_stub(self.fake_bin, "yarn", "#!/bin/sh\nexit 1\n")

        result = _run("audit.sh", str(design), fake_bin=self.fake_bin)

        self.assertEqual(result.returncode, 1)
        metadata = _result_kv(result.stdout)
        self.assertEqual(metadata.get("status"), "yarn-runtime-unavailable")
        install = metadata.get("install", "")
        self.assertIn(f"Restore {project.resolve()}/yarn.lock", install)
        self.assertIn("create and review it deliberately", install)
        self.assertIn(
            f"yarn --cwd {project.resolve()} install --immutable",
            install,
        )
        self.assertNotIn("yarn add", install)
        self.assertIn("audit.sh", metadata.get("rerun", ""))

    def test_yarn_repair_ignores_unrelated_ancestor_package_manager(self):
        ancestor = self.tmp / "unrelated"
        ancestor.mkdir()
        (ancestor / "package.json").write_text(
            '{"packageManager":"yarn@9.9.9"}\n', encoding="utf-8"
        )
        project = ancestor / "project"
        project.mkdir()
        design = project / "DESIGN.md"
        design.write_text("# DESIGN\n", encoding="utf-8")
        (project / "package.json").write_text(
            '{"devDependencies":{"@google/design.md":"0.3.0"}}\n',
            encoding="utf-8",
        )
        (project / "yarn.lock").write_text("", encoding="utf-8")
        _make_stub(self.fake_bin, "yarn", "#!/bin/sh\nexit 1\n")

        result = _run("audit.sh", str(design), fake_bin=self.fake_bin)

        self.assertEqual(result.returncode, 1)
        metadata = _result_kv(result.stdout)
        self.assertEqual(metadata.get("status"), "yarn-runtime-unavailable")
        install = metadata.get("install", "")
        self.assertNotIn("yarn@9.9.9", install)
        self.assertIn('"packageManager": "yarn@<reviewed-version>"', install)
        self.assertIn(str((project / "package.json").resolve()), install)
        self.assertIn("install --immutable", install)

    def test_declared_node_modules_dependency_never_falls_back_to_global_cli(self):
        project = self.tmp / "npm-project"
        project.mkdir()
        design = project / "DESIGN.md"
        design.write_text("# DESIGN\n", encoding="utf-8")
        (project / "package.json").write_text(
            '{"devDependencies":{"@google/design.md":"0.3.0"}}\n',
            encoding="utf-8",
        )
        (project / "package-lock.json").write_text("{}\n", encoding="utf-8")
        marker = self.tmp / "global-ran"
        _make_stub(
            self.fake_bin,
            "designmd",
            "#!/bin/sh\n"
            f'touch "{marker}"\n'
            "printf '%s\\n' '0.3.0'\n",
        )

        result = _run("audit.sh", str(design), fake_bin=self.fake_bin)

        self.assertEqual(result.returncode, 1)
        metadata = _result_kv(result.stdout)
        self.assertEqual(metadata.get("status"), "designmd-missing")
        self.assertEqual(
            metadata.get("install"),
            f"npm --prefix {project.resolve()} ci",
        )
        self.assertNotIn("@google/design.md", metadata.get("install", ""))
        self.assertFalse(marker.exists())

    def test_undeclared_project_binary_does_not_shadow_path(self):
        local_bin = self.tmp / "node_modules" / ".bin"
        local_bin.mkdir(parents=True)
        _make_stub(local_bin, "designmd", "#!/bin/sh\nexit 9\n")
        _make_json_stub(self.fake_bin, LINT_CLEAN)
        design = self._design_md()

        r = _run("audit.sh", str(design), fake_bin=self.fake_bin)

        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(_result_kv(r.stdout).get("status"), "ok")

    def test_declared_workspace_dependency_can_use_hoisted_binary(self):
        local_bin = self.tmp / "node_modules" / ".bin"
        local_bin.mkdir(parents=True)
        _make_json_stub(local_bin, LINT_CLEAN)
        project_dir = self.tmp / "packages" / "web"
        project_dir.mkdir(parents=True)
        (self.tmp / "package.json").write_text(
            '{"private":true,"workspaces":["packages/*"]}\n',
            encoding="utf-8",
        )
        (project_dir / "package.json").write_text(
            '{"devDependencies":{"@google/design.md":"0.1.1"}}\n',
            encoding="utf-8",
        )
        design = project_dir / "DESIGN.md"
        design.write_text("# DESIGN\n")

        r = _run(
            "audit.sh",
            str(design),
            extra_env={"DESIGNMD_WORKSPACE_ROOT": str(self.tmp)},
        )

        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(_result_kv(r.stdout).get("status"), "ok")

    def test_pnpm_workspace_dependency_can_use_hoisted_binary(self):
        root = self.tmp / "workspace"
        local_bin = root / "node_modules" / ".bin"
        local_bin.mkdir(parents=True)
        _make_json_stub(local_bin, LINT_CLEAN)
        (root / "pnpm-workspace.yaml").write_text(
            "packages:\n  - 'packages/*'\n", encoding="utf-8"
        )
        project_dir = root / "packages" / "web"
        project_dir.mkdir(parents=True)
        (project_dir / "package.json").write_text(
            '{"devDependencies":{"@google/design.md":"0.3.0"}}\n',
            encoding="utf-8",
        )
        design = project_dir / "DESIGN.md"
        design.write_text("# DESIGN\n", encoding="utf-8")

        result = _run("audit.sh", str(design))

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            Path(_result_kv(result.stdout)["cli"]).resolve(),
            (local_bin / "designmd").resolve(),
        )

    def test_configured_workspace_root_rejects_external_input(self):
        workspace = self.tmp / "workspace"
        workspace.mkdir()
        external = self.tmp / "external"
        external.mkdir()
        design = external / "DESIGN.md"
        design.write_text("# DESIGN\n", encoding="utf-8")
        _make_json_stub(self.fake_bin, LINT_CLEAN)

        result = _run(
            "audit.sh",
            str(design),
            fake_bin=self.fake_bin,
            extra_env={"DESIGNMD_WORKSPACE_ROOT": str(workspace)},
        )

        self.assertEqual(result.returncode, 1)
        self.assertEqual(_result_kv(result.stdout).get("status"), "outside-workspace")
        self.assertIn("DESIGNMD_WORKSPACE_ROOT", result.stdout)

    def test_no_git_workspace_finds_hoisted_declared_binary(self):
        root = self.tmp / "workspace"
        local_bin = root / "node_modules" / ".bin"
        local_bin.mkdir(parents=True)
        _make_json_stub(local_bin, LINT_CLEAN)
        (root / "package.json").write_text(
            '{"devDependencies":{"@google/design.md":"0.3.0"}}\n',
            encoding="utf-8",
        )
        nested = root / "docs" / "brand"
        nested.mkdir(parents=True)
        design = nested / "DESIGN.md"
        design.write_text("# DESIGN\n", encoding="utf-8")

        result = _run("audit.sh", str(design))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            Path(_result_kv(result.stdout)["cli"]).resolve(),
            (local_bin / "designmd").resolve(),
        )

    def test_no_git_workspace_with_nested_manifest_finds_hoisted_binary(self):
        root = self.tmp / "workspace"
        local_bin = root / "node_modules" / ".bin"
        local_bin.mkdir(parents=True)
        _make_json_stub(local_bin, LINT_CLEAN)
        (root / "package.json").write_text(
            '{"private":true,"workspaces":["packages/*"]}\n',
            encoding="utf-8",
        )
        (root / "package-lock.json").write_text("{}\n", encoding="utf-8")
        nested = root / "packages" / "web"
        nested.mkdir(parents=True)
        (nested / "package.json").write_text(
            '{"devDependencies":{"@google/design.md":"0.3.0"}}\n',
            encoding="utf-8",
        )
        design = nested / "DESIGN.md"
        design.write_text("# DESIGN\n", encoding="utf-8")

        result = _run("audit.sh", str(design))

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            Path(_result_kv(result.stdout)["cli"]).resolve(),
            (local_bin / "designmd").resolve(),
        )

    def test_nested_npm_declaration_restores_from_workspace_lock(self):
        root = self.tmp / "workspace"
        root.mkdir()
        (root / "package.json").write_text(
            '{"private":true,"workspaces":["packages/*"]}\n',
            encoding="utf-8",
        )
        (root / "package-lock.json").write_text("{}\n", encoding="utf-8")
        nested = root / "packages" / "web"
        nested.mkdir(parents=True)
        (nested / "package.json").write_text(
            '{"devDependencies":{"@google/design.md":"0.3.0"}}\n',
            encoding="utf-8",
        )
        design = nested / "DESIGN.md"
        design.write_text("# DESIGN\n", encoding="utf-8")

        result = _run("audit.sh", str(design))

        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            _result_kv(result.stdout).get("install"),
            f"npm --prefix {root.resolve()} ci",
        )

    def test_unrelated_root_npm_lock_does_not_claim_nested_package(self):
        root = self.tmp / "workspace"
        root.mkdir()
        (root / "package.json").write_text(
            '{"name":"root-app"}\n', encoding="utf-8"
        )
        (root / "package-lock.json").write_text("{}\n", encoding="utf-8")
        nested = root / "vendor" / "design"
        nested.mkdir(parents=True)
        (nested / "package.json").write_text(
            '{"devDependencies":{"@google/design.md":"0.3.0"}}\n',
            encoding="utf-8",
        )
        design = nested / "DESIGN.md"
        design.write_text("# DESIGN\n", encoding="utf-8")

        result = _run("audit.sh", str(design))

        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            _result_kv(result.stdout).get("install"),
            f"npm --prefix {nested.resolve()} install",
        )

    def test_unrelated_root_binary_does_not_claim_nested_package(self):
        root = self.tmp / "workspace"
        local_bin = root / "node_modules" / ".bin"
        local_bin.mkdir(parents=True)
        _make_json_stub(local_bin, LINT_CLEAN)
        (root / "package.json").write_text(
            '{"name":"root-app"}\n', encoding="utf-8"
        )
        nested = root / "vendor" / "design"
        nested.mkdir(parents=True)
        (nested / "package.json").write_text(
            '{"devDependencies":{"@google/design.md":"0.3.0"}}\n',
            encoding="utf-8",
        )
        design = nested / "DESIGN.md"
        design.write_text("# DESIGN\n", encoding="utf-8")

        result = _run("audit.sh", str(design))

        self.assertEqual(result.returncode, 1)
        metadata = _result_kv(result.stdout)
        self.assertEqual(metadata.get("status"), "designmd-missing")
        self.assertEqual(
            metadata.get("install"),
            f"npm --prefix {nested.resolve()} install",
        )

    def test_unrelated_root_declaration_and_binary_do_not_claim_nested_package(self):
        root = self.tmp / "workspace"
        local_bin = root / "node_modules" / ".bin"
        local_bin.mkdir(parents=True)
        marker = self.tmp / "unrelated-root-ran"
        _make_stub(
            local_bin,
            "designmd",
            "#!/bin/sh\n"
            f'touch "{marker}"\n'
            "printf '%s\\n' '0.3.0'\n",
        )
        (root / "package.json").write_text(
            '{"devDependencies":{"@google/design.md":"0.3.0"}}\n',
            encoding="utf-8",
        )
        nested = root / "vendor" / "design"
        nested.mkdir(parents=True)
        (nested / "package.json").write_text(
            '{"name":"vendored-design"}\n', encoding="utf-8"
        )
        design = nested / "DESIGN.md"
        design.write_text("# DESIGN\n", encoding="utf-8")
        _make_json_stub(self.fake_bin, LINT_CLEAN)

        result = _run(
            "audit.sh",
            str(design),
            fake_bin=self.fake_bin,
            extra_env={"DESIGNMD_WORKSPACE_ROOT": str(root)},
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        metadata = _result_kv(result.stdout)
        self.assertEqual(metadata.get("status"), "ok")
        self.assertEqual(metadata.get("cli-wrapper"), "path")
        self.assertFalse(marker.exists())

    def test_malformed_unrelated_root_manifest_does_not_block_nested_package(self):
        root = self.tmp / "workspace"
        root.mkdir()
        (root / "package.json").write_text("{broken\n", encoding="utf-8")
        nested = root / "vendor" / "design"
        nested.mkdir(parents=True)
        (nested / "package.json").write_text(
            '{"name":"vendored-design"}\n', encoding="utf-8"
        )
        design = nested / "DESIGN.md"
        design.write_text("# DESIGN\n", encoding="utf-8")
        _make_json_stub(self.fake_bin, LINT_CLEAN)

        result = _run(
            "audit.sh",
            str(design),
            fake_bin=self.fake_bin,
            extra_env={"DESIGNMD_WORKSPACE_ROOT": str(root)},
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        metadata = _result_kv(result.stdout)
        self.assertEqual(metadata.get("status"), "ok")
        self.assertEqual(metadata.get("cli-wrapper"), "path")

    def test_unrelated_non_npm_lock_does_not_claim_nested_package(self):
        for lockfile in ("pnpm-lock.yaml", "yarn.lock", "bun.lock"):
            with self.subTest(lockfile=lockfile):
                root = self.tmp / lockfile.replace(".", "-")
                root.mkdir()
                (root / lockfile).write_text("\n", encoding="utf-8")
                nested = root / "vendor" / "design"
                nested.mkdir(parents=True)
                (nested / "package.json").write_text(
                    '{"devDependencies":{"@google/design.md":"0.3.0"}}\n',
                    encoding="utf-8",
                )
                design = nested / "DESIGN.md"
                design.write_text("# DESIGN\n", encoding="utf-8")

                result = _run("audit.sh", str(design))

                self.assertEqual(result.returncode, 1)
                self.assertEqual(
                    _result_kv(result.stdout).get("install"),
                    f"npm --prefix {nested.resolve()} install",
                )

    def test_broken_cli_reports_repair_instruction(self):
        _make_stub(self.fake_bin, "designmd", "#!/bin/sh\nexit 9\n")
        design = self._design_md()

        result = _run("audit.sh", str(design), fake_bin=self.fake_bin)

        self.assertEqual(result.returncode, 1)
        kv = _result_kv(result.stdout)
        self.assertEqual(kv.get("status"), "designmd-unsupported")
        self.assertEqual(
            kv.get("install"),
            f"npm --prefix {self.tmp.resolve()} install --save-dev "
            "@google/design.md",
        )

    def test_success_removes_stderr_temp_file(self):
        _make_json_stub(self.fake_bin, LINT_CLEAN)
        tmp_dir = self.tmp / "tmp"
        tmp_dir.mkdir()
        design = self._design_md()

        result = _run(
            "audit.sh",
            str(design),
            fake_bin=self.fake_bin,
            extra_env={"TMPDIR": str(tmp_dir)},
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        leftovers = [path.name for path in tmp_dir.iterdir() if path.name != "xcrun_db"]
        self.assertEqual(leftovers, [Path(_result_kv(result.stdout)["json"]).name])

    def test_success_reports_cli_identity(self):
        _make_json_stub(self.fake_bin, LINT_CLEAN)
        design = self._design_md()

        result = _run("audit.sh", str(design), fake_bin=self.fake_bin)
        metadata = _result_kv(result.stdout)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(metadata.get("cli"), str(self.fake_bin / "designmd"))
        self.assertEqual(metadata.get("cli-version"), "0.3.0")

    def test_wrappers_do_not_invoke_runtime_package_resolvers(self):
        for name in (
            "audit.sh",
            "diff.sh",
            "export.sh",
            "spec.sh",
            "resolve-designmd.sh",
        ):
            text = (SCRIPTS / name).read_text(encoding="utf-8")
            self.assertNotIn("npx", text)
            self.assertNotIn("@latest", text)


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
    def test_missing_cli_has_exact_remediation(self):
        before, after = self._design_md("before.md"), self._design_md("after.md")
        result = _run("diff.sh", str(before), str(after))
        self.assertEqual(result.returncode, 1)
        kv = _result_kv(result.stdout)
        self.assertEqual(kv.get("status"), "designmd-missing")
        self.assertEqual(
            kv.get("install"),
            f"npm --prefix {self.tmp.resolve()} install --save-dev "
            "@google/design.md",
        )

    def test_no_regression_exit_0(self):
        _make_json_stub(self.fake_bin, DIFF_CLEAN)
        before, after = self._design_md("before.md"), self._design_md("after.md")
        r = _run("diff.sh", str(before), str(after), fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 0)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "ok")
        self.assertEqual(kv.get("regression"), "false")
        self.assertEqual(kv.get("exit-code"), "0")

    def test_regression_exit_1_propagated(self):
        _make_json_stub(self.fake_bin, DIFF_REGRESSION, rc=1)
        before, after = self._design_md("before.md"), self._design_md("after.md")
        r = _run("diff.sh", str(before), str(after), fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 1)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "ok")
        self.assertEqual(kv.get("regression"), "true")

    def test_nested_yarn_pnp_accepts_caller_relative_paths(self):
        root, nested = self._nested_yarn_pnp_project()
        before = nested / "before.md"
        after = nested / "after.md"
        before.write_text("# Before\n", encoding="utf-8")
        after.write_text("# After\n", encoding="utf-8")
        _make_yarn_pnp_stub(self.fake_bin)

        result = _run(
            "diff.sh",
            str(before.relative_to(root)),
            str(after.relative_to(root)),
            fake_bin=self.fake_bin,
            cwd=root,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(_result_kv(result.stdout).get("status"), "ok")
        self.assertEqual(_result_kv(result.stdout).get("cli-wrapper"), "yarn-pnp")

    def test_payload_and_exit_code_disagreement_blocks_the_diff(self):
        _make_json_stub(self.fake_bin, DIFF_REGRESSION, rc=0)
        before, after = self._design_md("before.md"), self._design_md("after.md")

        result = _run("diff.sh", str(before), str(after), fake_bin=self.fake_bin)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(_result_kv(result.stdout).get("status"), "cli-invalid-output")

    def test_cli_failure_reports_stderr(self):
        _make_stub(
            self.fake_bin,
            "designmd",
            '#!/bin/sh\n'
            'if [ "$1" = "--version" ]; then echo 0.3.0; exit 0; fi\n'
            'echo diff-boom >&2\nexit 4\n',
        )
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
    def test_missing_cli_has_exact_remediation(self):
        design = self._design_md()
        result = _run("export.sh", "tailwind", str(design))
        self.assertEqual(result.returncode, 1)
        kv = _result_kv(result.stdout)
        self.assertEqual(kv.get("status"), "designmd-missing")
        self.assertEqual(
            kv.get("install"),
            f"npm --prefix {self.tmp.resolve()} install --save-dev "
            "@google/design.md",
        )

    def test_success_emits_full_schema(self):
        # Stub writes to stdout, which the script redirects into the output file.
        payload = TAILWIND_EXPORT
        _make_json_stub(self.fake_bin, payload)
        design = self._design_md()
        r = _run("export.sh", "tailwind", str(design), fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 0)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "ok")
        self.assertEqual(kv.get("format"), "tailwind")
        self.assertEqual(kv.get("source"), str(design))
        self.assertEqual(kv.get("bytes"), str(len(payload) + 1))
        out = kv.get("output", "")
        self.assertEqual(Path(out).read_text(), payload + "\n")

    def test_nested_yarn_pnp_accepts_caller_relative_path(self):
        root, nested = self._nested_yarn_pnp_project()
        design = nested / "DESIGN.md"
        design.write_text("# DESIGN\n", encoding="utf-8")
        _make_yarn_pnp_stub(self.fake_bin)

        result = _run(
            "export.sh",
            "tailwind",
            str(design.relative_to(root)),
            fake_bin=self.fake_bin,
            cwd=root,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(_result_kv(result.stdout).get("status"), "ok")
        self.assertEqual(_result_kv(result.stdout).get("cli-wrapper"), "yarn-pnp")

    def test_explicit_output_path_honoured(self):
        _make_json_stub(self.fake_bin, DTCG_EXPORT)
        design = self._design_md()
        explicit = self.tmp / "tokens.json"
        r = _run("export.sh", "dtcg", str(design), str(explicit), fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 0)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("output"), str(explicit))
        self.assertTrue(explicit.exists())

    def test_cli_failure_reports_stderr(self):
        _make_stub(
            self.fake_bin,
            "designmd",
            '#!/bin/sh\n'
            'if [ "$1" = "--version" ]; then echo 0.3.0; exit 0; fi\n'
            'echo export-boom >&2\nexit 5\n',
        )
        design = self._design_md()
        r = _run("export.sh", "tailwind", str(design), fake_bin=self.fake_bin)
        self.assertEqual(r.returncode, 1)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "cli-failed")
        self.assertIn("export-boom", Path(kv["stderr"]).read_text())

    def test_failure_preserves_existing_explicit_output(self):
        _make_stub(self.fake_bin, "designmd", "#!/bin/sh\necho partial\nexit 5\n")
        design = self._design_md()
        explicit = self.tmp / "tokens.json"
        explicit.write_text('{"existing":true}\n', encoding="utf-8")

        result = _run(
            "export.sh", "dtcg", str(design), str(explicit), fake_bin=self.fake_bin
        )

        self.assertEqual(result.returncode, 1)
        self.assertEqual(explicit.read_text(encoding="utf-8"), '{"existing":true}\n')

    def test_valid_json_with_wrong_tailwind_shape_is_rejected(self):
        _make_json_stub(self.fake_bin, '{"tokens":{}}')
        design = self._design_md()

        result = _run("export.sh", "tailwind", str(design), fake_bin=self.fake_bin)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(_result_kv(result.stdout).get("status"), "cli-invalid-output")

    def test_dtcg_schema_and_token_group_are_required(self):
        _make_json_stub(self.fake_bin, '{"color":{}}')
        design = self._design_md()

        result = _run("export.sh", "dtcg", str(design), fake_bin=self.fake_bin)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(_result_kv(result.stdout).get("status"), "cli-invalid-output")

    def test_schema_only_dtcg_export_is_valid(self):
        payload = json.dumps(
            {"$schema": "https://www.designtokens.org/schemas/2025.10/format.json"}
        )
        _make_json_stub(self.fake_bin, payload)
        design = self._design_md()

        result = _run("export.sh", "dtcg", str(design), fake_bin=self.fake_bin)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(_result_kv(result.stdout).get("status"), "ok")

    def test_dtcg_rejects_noncanonical_schema_url(self):
        payload = json.dumps(
            {
                "$schema": "https://evil.example/designtokens.org/schemas/fake.json",
                "color": {"$type": "color", "primary": {"$value": "#112233"}},
            }
        )
        _make_json_stub(self.fake_bin, payload)
        design = self._design_md()

        result = _run("export.sh", "dtcg", str(design), fake_bin=self.fake_bin)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(_result_kv(result.stdout).get("status"), "cli-invalid-output")

    def test_dtcg_rejects_group_without_valid_token_leaf(self):
        payload = json.dumps(
            {
                "$schema": "https://www.designtokens.org/schemas/2025.10/format.json",
                "color": {"$type": "color", "primary": {}},
            }
        )
        _make_json_stub(self.fake_bin, payload)
        design = self._design_md()

        result = _run("export.sh", "dtcg", str(design), fake_bin=self.fake_bin)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(_result_kv(result.stdout).get("status"), "cli-invalid-output")

    def test_invalid_json_preserves_existing_explicit_output(self):
        _make_stub(self.fake_bin, "designmd", "#!/bin/sh\necho not-json\n")
        design = self._design_md()
        explicit = self.tmp / "tokens.json"
        explicit.write_text('{"existing":true}\n', encoding="utf-8")

        result = _run(
            "export.sh", "dtcg", str(design), str(explicit), fake_bin=self.fake_bin
        )

        self.assertEqual(result.returncode, 1)
        self.assertEqual(_result_kv(result.stdout).get("status"), "cli-invalid-output")
        self.assertEqual(explicit.read_text(encoding="utf-8"), '{"existing":true}\n')


# ---------- spec.sh ----------


class TestSpecCliResolution(_TmpMixin, unittest.TestCase):
    def test_missing_cli_reports_designmd_missing(self):
        r = _run("spec.sh", cwd=self.tmp)
        self.assertEqual(r.returncode, 1)
        kv = _result_kv(r.stdout)
        self.assertEqual(kv.get("status"), "designmd-missing")
        self.assertEqual(
            kv.get("install"),
            f"npm --prefix {self.tmp.resolve()} install --save-dev "
            "@google/design.md",
        )

    def test_project_local_cli_receives_flags(self):
        local_bin = self.tmp / "node_modules" / ".bin"
        local_bin.mkdir(parents=True)
        _make_stub(
            local_bin,
            "designmd",
            '#!/bin/sh\n'
            'if [ "$1" = "--version" ]; then echo 0.3.0; exit 0; fi\n'
            'printf "# DESIGN.md Format\\n\\n%s\\n\\n" "$*"\n'
            'printf "# Design Tokens\\n\\n## Schema\\n\\n# Sections\\n\\n"\n'
            'printf "# Consumer Behavior for Unknown Content\\n\\n"\n'
            'printf "| Rule | Severity | What it checks |\\n"\n'
            'printf "|------|----------|----------------|\\n"\n'
            'printf "| tokens | info | Token inventory |\\n"\n',
        )
        (self.tmp / "package.json").write_text(
            '{"devDependencies":{"@google/design.md":"0.1.1"}}\n',
            encoding="utf-8",
        )

        r = _run("spec.sh", "--rules", cwd=self.tmp)

        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("# DESIGN.md Format", r.stdout)
        self.assertIn("spec --rules --format markdown", r.stdout)

    def test_rules_only_json_translates_flags(self):
        local_bin = self.tmp / "node_modules" / ".bin"
        local_bin.mkdir(parents=True)
        _make_stub(
            local_bin,
            "designmd",
            '#!/bin/sh\n'
            'if [ "$1" = "--version" ]; then echo 0.3.0; exit 0; fi\n'
            'printf \'{"rules":[{"name":"contrast-ratio","severity":"warning","description":"%s"}]}\\n\' "$*"\n',
        )
        (self.tmp / "package.json").write_text(
            '{"devDependencies":{"@google/design.md":"0.3.0"}}\n',
            encoding="utf-8",
        )

        result = _run("spec.sh", "--rules-only", "--json", cwd=self.tmp)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn(
            "spec --rules-only --format json", payload["rules"][0]["description"]
        )

    def test_packaged_spec_path_bug_uses_same_package_artifact(self):
        package_root = self.tmp / "node_modules" / "@google" / "design.md"
        local_bin = self.tmp / "node_modules" / ".bin"
        local_bin.mkdir(parents=True)
        (package_root / "dist" / "linter").mkdir(parents=True)
        (package_root / "package.json").write_text(
            '{"name":"@google/design.md","version":"0.3.0"}\n',
            encoding="utf-8",
        )
        (package_root / "dist" / "linter" / "spec.md").write_text(
            "# DESIGN.md Format\n\nOfficial packaged spec\n\n"
            "# Design Tokens\n\n## Schema\n\n# Sections\n\n"
            "# Consumer Behavior for Unknown Content\n",
            encoding="utf-8",
        )
        _make_stub(
            local_bin,
            "designmd",
            "#!/bin/sh\n"
            'if [ "$1" = "--version" ]; then echo 0.3.0; exit 0; fi\n'
            'case " $* " in\n'
            '  *" --rules-only --format json "*) echo \'{"rules":[{"name":"tokens","severity":"info","description":"Token inventory"}]}\'; exit 0 ;;\n'
            '  *" --rules-only "*) echo "| Rule |"; exit 0 ;;\n'
            "esac\n"
            'echo "Error: Failed to load spec.md." >&2\n'
            "exit 1\n"
            f"# cmd-shim-target={package_root / 'dist' / 'index.js'}\n",
        )
        (self.tmp / "package.json").write_text(
            '{"devDependencies":{"@google/design.md":"0.3.0"}}\n',
            encoding="utf-8",
        )

        result = _run("spec.sh", "--rules", "--json", cwd=self.tmp)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("Official packaged spec", payload["spec"])
        self.assertEqual(payload["rules"][0]["name"], "tokens")

    def test_truncated_spec_output_is_rejected(self):
        local_bin = self.tmp / "node_modules" / ".bin"
        local_bin.mkdir(parents=True)
        _make_stub(
            local_bin,
            "designmd",
            "#!/bin/sh\n"
            'if [ "$1" = "--version" ]; then echo 0.3.0; exit 0; fi\n'
            'echo "# DESIGN.md Format"\n',
        )
        (self.tmp / "package.json").write_text(
            '{"devDependencies":{"@google/design.md":"0.3.0"}}\n',
            encoding="utf-8",
        )

        result = _run("spec.sh", cwd=self.tmp)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(_result_kv(result.stderr).get("status"), "cli-invalid-output")

    def test_unrelated_cli_failure_does_not_use_packaged_artifact(self):
        local_bin = self.tmp / "node_modules" / ".bin"
        local_bin.mkdir(parents=True)
        _make_stub(
            local_bin,
            "designmd",
            "#!/bin/sh\n"
            'if [ "$1" = "--version" ]; then echo 0.3.0; exit 0; fi\n'
            "echo 'unrelated failure' >&2\nexit 7\n",
        )
        (self.tmp / "package.json").write_text(
            '{"devDependencies":{"@google/design.md":"0.3.0"}}\n',
            encoding="utf-8",
        )

        result = _run("spec.sh", cwd=self.tmp)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(_result_kv(result.stderr).get("status"), "cli-failed")

    def test_invalid_json_preserves_existing_output(self):
        local_bin = self.tmp / "node_modules" / ".bin"
        local_bin.mkdir(parents=True)
        _make_stub(local_bin, "designmd", "#!/bin/sh\necho not-json\n")
        (self.tmp / "package.json").write_text(
            '{"devDependencies":{"@google/design.md":"0.3.0"}}\n',
            encoding="utf-8",
        )
        output = self.tmp / "spec.json"
        output.write_text('{"existing":true}\n', encoding="utf-8")

        result = _run(
            "spec.sh", "--json", "--output", str(output), cwd=self.tmp
        )

        self.assertEqual(result.returncode, 1)
        self.assertEqual(_result_kv(result.stderr).get("status"), "cli-invalid-output")
        self.assertEqual(output.read_text(encoding="utf-8"), '{"existing":true}\n')

    def test_invalid_markdown_preserves_existing_output(self):
        local_bin = self.tmp / "node_modules" / ".bin"
        local_bin.mkdir(parents=True)
        _make_stub(
            local_bin,
            "designmd",
            '#!/bin/sh\n'
            'if [ "$1" = "--version" ]; then echo 0.3.0; exit 0; fi\n'
            'echo not-the-canonical-spec\n',
        )
        (self.tmp / "package.json").write_text(
            '{"devDependencies":{"@google/design.md":"0.3.0"}}\n',
            encoding="utf-8",
        )
        output = self.tmp / "spec.md"
        output.write_text("existing\n", encoding="utf-8")

        result = _run("spec.sh", "--output", str(output), cwd=self.tmp)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(_result_kv(result.stderr).get("status"), "cli-invalid-output")
        self.assertEqual(output.read_text(encoding="utf-8"), "existing\n")


if __name__ == "__main__":
    unittest.main()
