#!/usr/bin/env python3
"""Atomic build/test gate for Code Ultrareview's ``--verify-build`` flag.

A generic failing test command cannot prove that a particular review finding is
correct. This gate therefore never changes finding confidence. When requested,
it always runs the repository's declared canonical test command or blocks the
review with an exact remediation.

Exit codes:
    0  build gate passed or was not applicable
    2  invalid arguments or unreadable inputs
    3  missing test command or test runner
    4  timeout, execution error, or failing test command
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import build_detect  # noqa: E402
import process_timeout  # noqa: E402

CONFIDENCE_THRESHOLD = 80
OUTPUT_TAIL_LINES = 100


def _load_findings(path: Path) -> list[dict]:
    if not path.is_file():
        raise ValueError(f"findings JSONL not found: {path}")
    findings: list[dict] = []
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line:
            continue
        try:
            finding = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"invalid findings JSONL at line {line_number}: {exc.msg}"
            ) from exc
        if not isinstance(finding, dict):
            raise ValueError(
                f"invalid findings JSONL at line {line_number}: expected object"
            )
        findings.append(finding)
    return findings


def _write_findings(path: Path, findings: list[dict], meta: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with pending.open("w", encoding="utf-8") as handle:
        for finding in findings:
            handle.write(json.dumps(finding) + "\n")
    os.replace(pending, path)
    sidecar = path.with_suffix(path.suffix + ".meta.json")
    sidecar_pending = sidecar.with_name(f".{sidecar.name}.{os.getpid()}.tmp")
    sidecar_pending.write_text(
        json.dumps(meta, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(sidecar_pending, sidecar)


def _tail(value: bytes) -> str:
    text = value.decode("utf-8", errors="replace")
    return "\n".join(text.splitlines()[-OUTPUT_TAIL_LINES:])


def _reports_zero_tests(tool: str | None, output: str) -> bool:
    if tool == "unittest":
        return re.search(r"\bRan\s+0\s+tests?\b", output) is not None
    if tool == "pytest":
        patterns = (
            r"(?im)^collected\s+0\s+items?\b",
            r"(?im)\b0\s+tests?\s+collected\b",
            r"(?im)\bno\s+tests?\s+ran\b",
        )
        return any(re.search(pattern, output) for pattern in patterns)
    if tool in {"npm", "pnpm", "yarn", "bun"}:
        patterns = (
            r"(?m)^#\s*tests\s+0\s*$",
            r"(?im)^Tests:\s+0\s+total\b",
            r"(?im)\bno tests? (?:found|collected)\b",
        )
        return any(re.search(pattern, output) for pattern in patterns)
    if tool == "cargo":
        counts = [int(value) for value in re.findall(r"(?m)^running\s+(\d+)\s+tests?\b", output)]
        return bool(counts) and not any(counts)
    if tool == "go":
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        return bool(lines) and all("[no test files]" in line for line in lines)
    return False


def _run_build(repo: Path, test_command: str, tool: str | None, timeout: int) -> dict:
    command_env = os.environ.copy()
    command_env["COREPACK_ENABLE_NETWORK"] = "0"
    command_env["COREPACK_DEFAULT_TO_LATEST"] = "0"
    result = process_timeout.run_process(
        test_command,
        shell=True,
        cwd=repo,
        timeout=timeout,
        env=command_env,
    )
    if result.timed_out:
        return {
            "build_status": "timeout",
            "exit_code": None,
            "stdout_tail": _tail(result.stdout),
            "stderr_tail": _tail(result.stderr),
        }
    if result.returncode == process_timeout.EXECUTION_ERROR_EXIT_CODE:
        return {
            "build_status": "error",
            "exit_code": None,
            "stdout_tail": _tail(result.stdout),
            "stderr_tail": _tail(result.stderr),
        }
    stdout_tail = _tail(result.stdout)
    stderr_tail = _tail(result.stderr)
    combined = result.stdout.decode("utf-8", errors="replace") + "\n" + result.stderr.decode(
        "utf-8", errors="replace"
    )
    status = "passed" if result.returncode == 0 else "failed"
    if _reports_zero_tests(tool, combined):
        status = "no-tests-collected"
    return {
        "build_status": status,
        "exit_code": result.returncode,
        "stdout_tail": stdout_tail,
        "stderr_tail": stderr_tail,
    }


def _declared_package_manager(repo: Path, tool: str) -> str | None:
    package_json = repo / "package.json"
    if not package_json.is_file():
        return None
    try:
        payload = json.loads(package_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    value = payload.get("packageManager") if isinstance(payload, dict) else None
    if isinstance(value, str) and value.startswith(f"{tool}@"):
        return value
    return None


def _system_install(package: str, *, brew: str, apt: str, url: str) -> str:
    if shutil.which("brew"):
        return f"Run `brew install {brew}`"
    if shutil.which("apt-get"):
        return (
            f"Ask an administrator to install Debian package(s) `{apt}`; "
            f"official guide: {url}"
        )
    return f"Install {package} from its official guide: {url}"


def _missing_runner_remediation(repo: Path, tool: str | None) -> str:
    if tool in {"pnpm", "yarn"}:
        declared = _declared_package_manager(repo, tool)
        if declared:
            instruction = (
                "Run `"
                f"corepack install --global {shlex.quote(declared)} && "
                f"corepack enable {tool}`"
            )
        else:
            instruction = _system_install(
                tool,
                brew=tool,
                apt=tool,
                url="https://nodejs.org/api/corepack.html",
            )
        return (
            f"{instruction}. Verify `command -v {tool}` and rerun the "
            "exact command printed below."
        )
    if tool == "npm":
        instruction = _system_install(
            "Node.js and npm",
            brew="node",
            apt="nodejs npm",
            url="https://nodejs.org/en/download",
        )
        return (
            f"{instruction}. Verify `command -v npm` and rerun the "
            "exact command printed below."
        )
    if tool == "bun":
        instruction = _system_install(
            "Bun",
            brew="bun",
            apt="bun",
            url="https://bun.sh/docs/installation",
        )
        return (
            f"{instruction}. Verify `command -v bun` and rerun the "
            "exact command printed below."
        )
    if tool == "pytest":
        if (repo / "uv.lock").is_file():
            instruction = "Run `uv sync --locked`"
        elif (repo / "poetry.lock").is_file():
            instruction = "Run `poetry install --sync`"
        elif (repo / "requirements-dev.txt").is_file():
            instruction = "Run `python3 -m pip install -r requirements-dev.txt`"
        elif (repo / "requirements.txt").is_file():
            instruction = "Run `python3 -m pip install -r requirements.txt`"
        else:
            instruction = "Run `python3 -m pip install pytest`"
        return (
            f"{instruction}. Verify `command -v pytest` and rerun the "
            "exact command printed below."
        )
    if tool == "unittest":
        instruction = _system_install(
            "Python 3",
            brew="python",
            apt="python3",
            url="https://www.python.org/downloads/",
        )
        return (
            f"{instruction}. Verify `command -v python3` and rerun the "
            "exact command printed below."
        )
    if tool == "cargo":
        instruction = _system_install(
            "Rust",
            brew="rustup-init",
            apt="cargo rustc",
            url="https://rustup.rs/",
        )
        return (
            f"{instruction}. Verify `command -v cargo` and rerun the "
            "exact command printed below."
        )
    if tool == "go":
        instruction = _system_install(
            "Go",
            brew="go",
            apt="golang-go",
            url="https://go.dev/doc/install",
        )
        return (
            f"{instruction}. Verify `command -v go` and rerun the "
            "exact command printed below."
        )
    if tool == "make":
        instruction = _system_install(
            "Make",
            brew="make",
            apt="make",
            url="https://www.gnu.org/software/make/",
        )
        return (
            f"{instruction}. Verify `command -v make` and rerun the "
            "exact command printed below."
        )
    if tool:
        return (
            f"Install `{tool}` from its official distribution, verify "
            f"`command -v {tool}`, and rerun the exact command printed below."
        )
    return (
        "Add a canonical test entry: a package-manager `test` script; for "
        "Python, configure `pytest` and add a collectable test, or add a "
        "collectable `unittest` suite; otherwise add the project's canonical "
        "Cargo.toml, go.mod, or Makefile `test` target. Then rerun Code "
        "Ultrareview with the exact command printed below."
    )


def _build_failure_remediation(
    status: str,
    test_command: str,
    timeout: int,
) -> str:
    quoted_command = f"`{test_command}`"
    if status == "no-tests-collected":
        return (
            "Add at least one collectable test to the declared suite, run "
            f"{quoted_command} directly until it reports a non-zero test count, "
            "then rerun the exact command printed below."
        )
    if status == "timeout":
        return (
            f"Run {quoted_command} directly and diagnose why it exceeds {timeout}s. "
            "Fix the hang, or use a reviewed larger `--timeout` only when the "
            "canonical suite legitimately needs it, then rerun the exact command "
            "printed below."
        )
    if status == "failed":
        return (
            f"Run {quoted_command} directly, fix every reported test failure until "
            "the command exits zero with tests collected, then rerun the exact "
            "command printed below."
        )
    return (
        f"Run {quoted_command} directly and repair its execution error, then rerun "
        "the exact command printed below."
    )


def _rerun_command() -> str:
    return shlex.join([sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]])


def _print_rerun() -> None:
    print(f"ERROR: rerun: {_rerun_command()}", file=sys.stderr)


def run(
    repo: Path,
    findings: list[dict],
    test_command: str | None,
    *,
    tool: str | None,
    tool_available: bool,
    timeout: int,
) -> tuple[list[dict], dict]:
    sub80_count = sum(
        1 for finding in findings
        if 0 <= int(finding.get("confidence", 0)) < CONFIDENCE_THRESHOLD
    )
    base = {
        "tool": tool,
        "test_command": test_command,
        "sub80_count": sub80_count,
        "promoted_count": 0,
    }
    if not test_command:
        return findings, {
            **base,
            "complete": False,
            "applicable": True,
            "build_status": "missing-test-command",
            "remediation": _missing_runner_remediation(repo, None),
        }
    if not tool_available:
        return findings, {
            **base,
            "complete": False,
            "applicable": True,
            "build_status": "missing-runner",
            "remediation": _missing_runner_remediation(repo, tool),
        }

    result = _run_build(repo, test_command, tool, timeout)
    complete = result["build_status"] == "passed"
    remediation = (
        None
        if complete
        else _build_failure_remediation(result["build_status"], test_command, timeout)
    )
    return findings, {
        **base,
        **result,
        "complete": complete,
        "applicable": True,
        **({"remediation": remediation} if remediation else {}),
        "reason": (
            "canonical test command passed"
            if complete
            else "canonical test command did not complete successfully"
        ),
    }


def _write_scope_coverage(scope_path: Path, scope: dict, meta: dict) -> None:
    scope["build_coverage"] = {
        key: meta.get(key)
        for key in (
            "complete",
            "applicable",
            "build_status",
            "tool",
            "test_command",
            "remediation",
        )
        if key in meta
    }
    scope["coverage_complete"] = bool(
        (scope.get("tool_coverage") or {}).get("complete")
        and (scope.get("axis_coverage") or {}).get("complete")
        and (scope.get("validator_coverage") or {}).get("complete")
        and scope["build_coverage"].get("complete")
        and (
            scope.get("mutation_coverage") is None
            or (scope.get("mutation_coverage") or {}).get("complete")
        )
        and (
            scope.get("reconcile_coverage") is None
            or (scope.get("reconcile_coverage") or {}).get("complete")
        )
    )
    temporary = scope_path.with_name(f".{scope_path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(scope, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, scope_path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", required=True, type=Path)
    parser.add_argument("--findings", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--repo", default=Path.cwd(), type=Path)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    repo = args.repo.expanduser().resolve()
    if not args.scope.is_file():
        print(f"ERROR: scope.json not found: {args.scope}", file=sys.stderr)
        return 2
    if not repo.is_dir():
        print(f"ERROR: repo path is not a directory: {repo}", file=sys.stderr)
        return 2
    if args.timeout <= 0:
        print("ERROR: timeout must be a positive integer", file=sys.stderr)
        return 2
    try:
        scope = json.loads(args.scope.read_text(encoding="utf-8"))
        if not isinstance(scope, dict):
            raise ValueError("scope.json must contain an object")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    preflight = {
        "complete": False,
        "applicable": True,
        "build_status": "preflight",
    }
    try:
        _write_scope_coverage(args.scope, scope, preflight)
        for stale in (args.output, args.output.with_suffix(args.output.suffix + ".meta.json")):
            if stale.exists():
                stale.unlink()
        findings = _load_findings(args.findings)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        failed = {
            **preflight,
            "build_status": "invalid-input",
            "remediation": (
                "Rerun the axis and validator phases to recreate the findings "
                "JSONL, then rerun Code Ultrareview with --verify-build."
            ),
        }
        try:
            _write_scope_coverage(args.scope, scope, failed)
        except OSError:
            pass
        print(f"ERROR: build verification input is invalid: {exc}", file=sys.stderr)
        print(f"ERROR: remediation: {failed['remediation']}", file=sys.stderr)
        _print_rerun()
        return 4

    try:
        detected = build_detect.detect(repo)
        out_findings, meta = run(
            repo,
            findings,
            detected.get("test_command"),
            tool=detected.get("tool"),
            tool_available=bool(detected.get("available")),
            timeout=args.timeout,
        )
        _write_findings(args.output, out_findings, meta)
        _write_scope_coverage(args.scope, scope, meta)
    except build_detect.InvalidManifestError as exc:
        failed = {
            **preflight,
            "build_status": "invalid-manifest",
            "remediation": (
                "Repair package.json so it is valid JSON with a valid scripts "
                "object, then rerun Code Ultrareview with --verify-build."
            ),
        }
        try:
            _write_scope_coverage(args.scope, scope, failed)
        except OSError:
            pass
        print(f"ERROR: build verification project manifest is invalid: {exc}", file=sys.stderr)
        print(f"ERROR: remediation: {failed['remediation']}", file=sys.stderr)
        _print_rerun()
        return 4
    except (OSError, ValueError) as exc:
        failed = {
            **preflight,
            "build_status": "error",
            "remediation": (
                "Repair the project's canonical test configuration or runner, "
                "then rerun Code Ultrareview with --verify-build."
            ),
        }
        try:
            _write_scope_coverage(args.scope, scope, failed)
        except OSError:
            pass
        print(f"ERROR: build verification could not execute reliably: {exc}", file=sys.stderr)
        print(f"ERROR: remediation: {failed['remediation']}", file=sys.stderr)
        _print_rerun()
        return 4

    status = meta["build_status"]
    if meta["complete"]:
        return 0
    if status in {"missing-test-command", "missing-runner"}:
        print(f"ERROR: build verification prerequisite missing: {status}", file=sys.stderr)
        print(f"ERROR: remediation: {meta['remediation']}", file=sys.stderr)
        _print_rerun()
        return 3
    print(
        f"ERROR: build verification failed: {status}; command: "
        f"{meta.get('test_command')}",
        file=sys.stderr,
    )
    if meta.get("stderr_tail"):
        print(meta["stderr_tail"], file=sys.stderr)
    print(f"ERROR: remediation: {meta['remediation']}", file=sys.stderr)
    _print_rerun()
    return 4


if __name__ == "__main__":
    raise SystemExit(main())
