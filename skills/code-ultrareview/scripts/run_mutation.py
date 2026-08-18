#!/usr/bin/env python3
"""Run configured mutation analyzers and publish changed-file findings."""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath

from manifest import read_scope, set_phase, write_jsonl_atomic
from process_timeout import run_process
from tool_runtime import ContractError, InputError, guidance, resolve

JS_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".mts", ".cts"}
JVM_EXTENSIONS = {".java", ".kt", ".kts", ".scala"}
JS_TEST_FILE = re.compile(r"(?:^|/)[^/]+\.(?:test|spec)\.(?:[cm]?[jt]sx?)$")


class MutationFailure(RuntimeError):
    pass


def finding(tool: str, location: str, text: str, recommendation: str) -> dict:
    return {"axis": "tests", "severity": "Medium", "location": location,
            "finding": text, "recommendation": recommendation,
            "confidence": 100, "source_tool": tool}


def command_text(command: list[str]) -> str:
    return shlex.join(command)


def run(command: list[str], cwd: Path, timeout: int, raw: Path, error: Path,
        allowed=(0,), env=None) -> None:
    result = run_process(command, cwd=cwd, timeout=timeout, env=env)
    raw.write_bytes(result.stdout)
    with error.open("ab") as handle:
        handle.write((f"$ {command_text(command)}\n").encode())
        handle.write(result.stderr)
    if result.timed_out:
        raise MutationFailure(
            f"{command[0]} timed out after {timeout}s; its process group was terminated"
        )
    if result.returncode not in allowed:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        suffix = f": {detail[-1000:]}" if detail else ""
        raise MutationFailure(
            f"{command_text(command)} failed with exit code {result.returncode}{suffix}"
        )


def relative_files(repo: Path, scope: dict, extensions: set[str]) -> list[str]:
    return [path for path in scope["files_touched_list"]
            if PurePosixPath(path).suffix in extensions and (repo / path).is_file()]


def stryker_files(repo: Path, scope: dict) -> list[str]:
    return [path for path in relative_files(repo, scope, JS_EXTENSIONS)
            if not path.endswith(".d.ts")
            and "__tests__" not in PurePosixPath(path).parts
            and not JS_TEST_FILE.search(path)]


def project_build(repo: Path, files: list[str]):
    builds = set()
    for relative in files:
        current = (repo / relative).parent
        while current == repo or repo in current.parents:
            if (current / "pom.xml").is_file():
                builds.add(("maven", current))
                break
            if (current / "build.gradle").is_file() or (current / "build.gradle.kts").is_file():
                builds.add(("gradle", current))
                break
            if current == repo:
                break
            current = current.parent
    if len(builds) > 1:
        raise ContractError("changed JVM files span Maven and Gradle; review one build at a time")
    if not builds:
        raise ContractError("no supported JVM build governs the changed files")
    return next(iter(builds))


def preflight(repo: Path, scope: dict) -> tuple[dict, dict]:
    files = {
        "javascript-typescript": stryker_files(repo, scope),
        "python": relative_files(repo, scope, {".py"}),
        "jvm": relative_files(repo, scope, JVM_EXTENSIONS),
    }
    runtimes, missing = {}, []
    js_files = files["javascript-typescript"]
    if js_files:
        try:
            command, wrapper, env = resolve(
                repo, js_files, "@stryker-mutator/core", "stryker"
            )
            if not wrapper.startswith("project:"):
                raise ContractError("Stryker must be a declared project dependency")
            project = Path(wrapper.split(":", 2)[2])
            runtimes["stryker"] = (command, project, env, js_files)
        except InputError:
            raise
        except ContractError as exc:
            missing.append({"tool": "stryker", "reason": str(exc),
                            "remediation": guidance(repo, js_files,
                                                    "@stryker-mutator/core")})
    if files["python"]:
        executable = shutil.which("mutmut")
        if not executable:
            missing.append({"tool": "mutmut", "reason": "not installed on PATH",
                            "remediation": "install mutmut in the project's test environment, activate it, and verify `command -v mutmut`"})
        if executable:
            runtimes["mutmut"] = ([executable], repo, None, files["python"])
    if files["jvm"]:
        try:
            build, project = project_build(repo, files["jvm"])
        except ContractError as exc:
            build, project = None, repo
            missing.append({"tool": "pitest-build", "reason": str(exc),
                            "remediation": "configure one Pitest-enabled Maven or Gradle build and review one build at a time"})
        runner = shutil.which("mvn" if build == "maven" else "gradle") if build else None
        if build and not runner:
            missing.append({"tool": build, "reason": f"{build} runner is unavailable",
                            "remediation": f"install {build} and verify `command -v {'mvn' if build == 'maven' else 'gradle'}`"})
        if build and runner:
            runtimes["pitest"] = ([str(runner)], project, None, files["jvm"],
                                  build, repo)
    plan = {"applicable": {name: bool(paths) for name, paths in files.items()},
            "missing": missing, "complete": not missing,
            "status": "blocked" if missing else
                      ("ready" if any(files.values()) else "not-applicable")}
    return plan, runtimes


def parse_stryker(report: Path, repo: Path, project: Path,
                  changed: list[str]) -> list[dict]:
    try:
        value = json.loads(report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MutationFailure(f"invalid Stryker report: {exc}") from exc
    files = value.get("files") if isinstance(value, dict) else None
    if not isinstance(files, dict):
        raise MutationFailure("invalid Stryker report: files must be an object")
    prefix = project.relative_to(repo).as_posix()
    terminal = {"Killed", "Survived", "NoCoverage", "Timeout", "RuntimeError",
                "CompileError", "Ignored"}
    results, incomplete = [], []
    for path, payload in files.items():
        repo_path = (PurePosixPath(prefix) / path).as_posix() if prefix != "." else path
        if repo_path not in changed:
            continue
        mutants = payload.get("mutants") if isinstance(payload, dict) else None
        if not isinstance(mutants, list):
            raise MutationFailure(f"invalid Stryker mutants for {path}")
        for mutant in mutants:
            status = mutant.get("status") if isinstance(mutant, dict) else None
            if status == "Pending":
                incomplete.append(f"{repo_path}: {status}")
                continue
            if status not in terminal:
                raise MutationFailure(f"unsupported Stryker status: {status!r}")
            if status not in {"Survived", "NoCoverage"}:
                continue
            start = mutant.get("location", {}).get("start", {})
            location = f"{repo_path}:{start.get('line', '?')}:{start.get('column', '?')}"
            uncovered = status == "NoCoverage"
            results.append(finding(
                "stryker", location,
                f"{'Uncovered' if uncovered else 'Surviving'} mutant "
                f"({mutant.get('mutatorName', '?')}): {mutant.get('description', 'no description')}",
                "Add a test that executes this code path and asserts the intended behavior."
                if uncovered else "Add an assertion that fails for the mutated behavior.",
            ))
    if incomplete:
        raise MutationFailure("incomplete Stryker results: " + ", ".join(incomplete[:5]))
    return results


def run_stryker(runtime, repo: Path, output: Path, timeout: int) -> list[dict]:
    command, project, env, changed = runtime
    report = project / "reports" / "mutation" / "mutation.json"
    report.unlink(missing_ok=True)
    prefix = PurePosixPath(project.relative_to(repo).as_posix())
    try:
        relative = [PurePosixPath(path).relative_to(prefix).as_posix()
                    if project != repo else path for path in changed]
    except ValueError as exc:
        raise MutationFailure("Stryker scope escapes its declared project") from exc
    mutate = ",".join(f"./{path}" for path in relative)
    run(command + ["run", "--reporters", "json", "--mutate", mutate], project,
        timeout, output / "stryker.log", output / "stryker.stderr", (0, 1), env)
    if not report.is_file():
        raise MutationFailure("Stryker did not produce reports/mutation/mutation.json")
    return parse_stryker(report, repo, project, changed)


def run_mutmut(runtime, output: Path, timeout: int) -> list[dict]:
    command, repo, _env, changed = runtime
    error = output / "mutmut.stderr"
    error.unlink(missing_ok=True)
    run(command + ["run"], repo, timeout, output / "mutmut.log", error)
    results = output / "mutmut-results.log"
    run(command + ["results", "--all", "true"], repo, timeout, results, error)
    terminal = {"caught by type check", "killed", "survived", "no tests",
                "suspicious", "timeout", "segfault"}
    incomplete = {"skipped", "check was interrupted by user", "not checked"}
    evaluated = False
    rows = []
    for number, raw in enumerate(results.read_text().splitlines(), 1):
        if not raw.strip():
            continue
        if ": " not in raw:
            raise MutationFailure(f"invalid mutmut results line {number}: {raw}")
        mutant, status = (part.strip() for part in raw.rsplit(": ", 1))
        if not mutant or status not in terminal | incomplete:
            raise MutationFailure(f"invalid mutmut results line {number}: {raw}")
        evaluated = True
        if status in incomplete:
            raise MutationFailure(f"incomplete mutmut results: {mutant}: {status}")
        if status in {"survived", "no tests", "suspicious"}:
            rows.append((mutant, status))
    if not evaluated:
        raise MutationFailure("mutmut reported zero evaluated mutants")
    findings = []
    shows = output / "mutmut-shows.txt"
    shows.write_text("")
    for mutant, status in rows:
        show = output / ".mutmut-show"
        run(command + ["show", mutant], repo, min(timeout, 15), show, error)
        body = show.read_text(encoding="utf-8")
        with shows.open("a", encoding="utf-8") as handle:
            handle.write(f"=== {status}\t{mutant} ===\n{body}\n")
        match = re.search(r"^---\s+(?:a/)?([^\t\n]+)", body, re.MULTILINE)
        if not match:
            raise MutationFailure(f"cannot locate source file for mutmut mutant {mutant}")
        path = PurePosixPath(match.group(1).strip()).as_posix()
        if path not in changed:
            continue
        definition = re.search(
            r"^[ -](?P<definition>\s*(?:async\s+)?def\s+[A-Za-z_]\w*\s*\([^\n]*)",
            body, re.MULTILINE,
        )
        source_line = "?"
        if definition:
            source = (repo / path).read_text(encoding="utf-8").splitlines()
            matches = [index for index, value in enumerate(source, 1)
                       if value.rstrip() == definition.group("definition").rstrip()]
            if len(matches) == 1:
                source_line = str(matches[0])
        label = {"survived": "Surviving", "no tests": "Uncovered",
                 "suspicious": "Suspicious"}[status]
        findings.append(finding(
            "mutmut", f"{path}:{source_line}",
            f"{label} mutmut mutant: {mutant}",
            "Add a focused assertion that decisively kills this mutant.",
        ))
    return findings


def parse_pitest(reports: list[Path], changed: list[str]) -> list[dict]:
    terminal = {"KILLED", "SURVIVED", "NO_COVERAGE", "NON_VIABLE",
                "TIMED_OUT", "MEMORY_ERROR", "RUN_ERROR"}
    findings, seen = [], set()
    for report in reports:
        try:
            root = ET.parse(report).getroot()
        except (OSError, ET.ParseError) as exc:
            raise MutationFailure(f"invalid Pitest report {report}: {exc}") from exc
        if root.tag.rsplit("}", 1)[-1] != "mutations":
            raise MutationFailure(f"invalid Pitest root in {report}")
        for mutation in (item for item in root if item.tag.rsplit("}", 1)[-1] == "mutation"):
            source = mutation.findtext("sourceFile") or ""
            klass = (mutation.findtext("mutatedClass") or "").split("$", 1)[0]
            package = klass.rsplit(".", 1)[0] if "." in klass else ""
            suffix = f"{package.replace('.', '/')}/{source}" if package else source
            matches = [path for path in changed if path == suffix or path.endswith(f"/{suffix}")]
            if not matches and not package:
                matches = [path for path in changed if PurePosixPath(path).name == source]
            if len(matches) > 1:
                raise MutationFailure(f"ambiguous Pitest source mapping for {klass} / {source}")
            if not matches:
                continue
            status = mutation.get("status")
            if status not in terminal:
                raise MutationFailure(f"unsupported Pitest status: {status!r}")
            if status not in {"SURVIVED", "NO_COVERAGE"}:
                continue
            key = (matches[0], mutation.findtext("lineNumber"),
                   mutation.findtext("description"), status)
            if key in seen:
                continue
            seen.add(key)
            uncovered = status == "NO_COVERAGE"
            findings.append(finding(
                "pitest", f"{matches[0]}:{key[1] or '?'}",
                f"{'Uncovered' if uncovered else 'Surviving'} Pitest mutant: "
                f"{key[2] or 'no description'}",
                "Add a test that executes this path and asserts the intended behavior."
                if uncovered else "Add an assertion that fails for the mutated behavior.",
            ))
    return findings


def run_pitest(runtime, output: Path, timeout: int) -> list[dict]:
    command, project, _env, changed, build, repo = runtime
    before = {path: path.stat().st_mtime_ns for path in repo.rglob("mutations.xml")}
    args = ["-o", "-q", "-B", "pitest:mutationCoverage"] if build == "maven" \
        else ["--offline", "--no-daemon", "pitest"]
    run(command + args, project, timeout, output / "pitest.log", output / "pitest.stderr")
    reports = [path for path in repo.rglob("mutations.xml")
               if path not in before or path.stat().st_mtime_ns != before[path]]
    if not reports:
        raise MutationFailure("Pitest did not produce a fresh mutations.xml report")
    return parse_pitest(reports, changed)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--repo", default=".", type=Path)
    parser.add_argument("--timeout", type=int,
                        default=int(os.environ.get("MUTATION_TIMEOUT", "600")))
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be a positive integer")
    repo, output = args.repo.resolve(), args.output_dir.resolve()
    findings_path = output / "mutation-findings.jsonl"
    findings_path.unlink(missing_ok=True)
    (output / "raw").mkdir(parents=True, exist_ok=True)
    if not repo.is_dir():
        parser.error(f"--repo is not a directory: {repo}")
    try:
        scope = read_scope(args.scope)
    except ValueError as exc:
        print(f"ERROR: invalid mutation input: {exc}", file=sys.stderr)
        return 2
    rerun = command_text([sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]])
    try:
        set_phase(args.scope, "mutation", {"requested": True, "complete": False,
                                           "applicable": None, "status": "preflight"})
        plan, runtimes = preflight(repo, scope)
        applicable = any(plan["applicable"].values())
        if plan["missing"]:
            set_phase(args.scope, "mutation", {"requested": True, "complete": False,
                                               "applicable": applicable, "status": "blocked"})
            for item in plan["missing"]:
                print(f"ERROR: mutation prerequisite '{item['tool']}' is missing: "
                      f"{item['reason']}", file=sys.stderr)
                print(f"ERROR: remediation: {item['remediation']}", file=sys.stderr)
            return 3
        if os.environ.get("MUTATION_DRY_RUN") == "1":
            set_phase(args.scope, "mutation", {"requested": True, "complete": False,
                                               "applicable": applicable, "status": "dry-run"})
            return 0
        findings = []
        if "stryker" in runtimes:
            findings += run_stryker(runtimes["stryker"], repo, output / "raw", args.timeout)
        if "mutmut" in runtimes:
            findings += run_mutmut(runtimes["mutmut"], output / "raw", args.timeout)
        if "pitest" in runtimes:
            findings += run_pitest(runtimes["pitest"], output / "raw", args.timeout)
        write_jsonl_atomic(findings_path, findings)
        set_phase(args.scope, "mutation", {"requested": True, "complete": True,
                                           "applicable": applicable,
                                           "status": "complete" if applicable else "not-applicable"},
                  findings_path)
        return 0
    except InputError as exc:
        try:
            set_phase(args.scope, "mutation", {"requested": True, "complete": False,
                                               "applicable": True, "status": "invalid-input"})
        except ValueError:
            pass
        print(f"ERROR: invalid mutation input: {exc}", file=sys.stderr)
        print(f"ERROR: rerun: {rerun}", file=sys.stderr)
        return 2
    except (ContractError, MutationFailure, ValueError) as exc:
        try:
            set_phase(args.scope, "mutation", {"requested": True, "complete": False,
                                               "applicable": True, "status": "failed"})
        except ValueError:
            pass
        findings_path.unlink(missing_ok=True)
        print(f"ERROR: {exc}", file=sys.stderr)
        print("ERROR: repair the reported analyzer or project configuration, then rerun Code Ultrareview.",
              file=sys.stderr)
        print(f"ERROR: rerun: {rerun}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
