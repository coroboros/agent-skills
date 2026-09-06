#!/usr/bin/env python3
"""Atomic scope, coverage, and artifact identity contracts."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
from typing import Optional

COVERAGE_FIELDS = (
    "tool_coverage", "axis_coverage", "validator_coverage", "build_coverage",
    "mutation_coverage", "reconcile_coverage",
)


def read_scope(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid scope.json: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("scope.json must contain an object")
    files = payload.get("files_touched_list")
    languages = payload.get("languages")
    if not isinstance(files, list) or not files or not all(
        isinstance(item, str) and item for item in files
    ):
        raise ValueError("scope.json files_touched_list must be a non-empty string array")
    for item in files:
        relative = PurePosixPath(item)
        if relative.is_absolute() or ".." in relative.parts or "\0" in item:
            raise ValueError(f"scope.json path must stay inside the repository: {item!r}")
    if not isinstance(languages, list) or not all(
        isinstance(item, str) and item for item in languages
    ):
        raise ValueError("scope.json languages must be a string array")
    if "files_touched" in payload and payload["files_touched"] != len(files):
        raise ValueError("scope.json files_touched does not match files_touched_list")
    for key in COVERAGE_FIELDS:
        value = payload.get(key)
        if value is not None and not isinstance(value, dict):
            raise ValueError(f"scope.json {key} must be an object when present")
    return payload


def blocking_skips(entries: object) -> list:
    """An analyzer recorded as not applicable is complete coverage, not a gap."""
    if entries is None:
        return []
    if not isinstance(entries, list):
        return [entries]
    return [item for item in entries
            if not (isinstance(item, dict) and item.get("applicable") is False)]


def write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def write_jsonl_atomic(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        temporary.write_text(
            "".join(json.dumps(record) + "\n" for record in records),
            encoding="utf-8",
        )
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def read_required_diff(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"required diff file is missing: {path}")
    return path.read_text(encoding="utf-8")


def file_identity(path: Path) -> dict:
    if not path.is_file():
        raise ValueError(f"required run artifact is missing: {path}")
    resolved = path.resolve()
    data = resolved.read_bytes()
    return {"path": str(resolved), "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data)}


def read_reconcile_payload(scope: dict) -> dict | None:
    coverage = scope.get("reconcile_coverage")
    if coverage is None:
        return None
    if not isinstance(coverage, dict) or coverage.get("complete") is not True:
        raise ValueError("requested reconcile coverage is incomplete; rerun reconciliation")
    output = coverage.get("output")
    expected_digest = coverage.get("sha256")
    expected_count = coverage.get("finding_count")
    path = verify_file_identity(
        {"path": output, "sha256": expected_digest}, "reconcile result"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("lens") != "derivation":
        raise ValueError("reconcile result is not a derivation payload")
    artifacts = payload.get("artifacts")
    findings = payload.get("findings")
    if not isinstance(artifacts, list) or not isinstance(findings, list):
        raise ValueError("reconcile result has an invalid schema")
    if isinstance(expected_count, bool) or not isinstance(expected_count, int):
        raise ValueError("reconcile coverage has an invalid finding count")
    if len(findings) != expected_count:
        raise ValueError("reconcile result finding count does not match coverage")
    for artifact in artifacts:
        if (
            not isinstance(artifact, dict)
            or not isinstance(artifact.get("path"), str)
            or not isinstance(artifact.get("claim_count"), int)
            or isinstance(artifact.get("claim_count"), bool)
            or artifact["claim_count"] < 0
        ):
            raise ValueError("reconcile result contains an invalid artifact")
    for finding in findings:
        if (
            not isinstance(finding, dict)
            or finding.get("classification") != "UNCLASSIFIED"
            or not isinstance(finding.get("finding"), str)
            or not finding["finding"].strip()
        ):
            raise ValueError("reconcile result contains an invalid finding")
    return payload


def output_identity(path: Path) -> dict:
    identity = file_identity(path)
    identity["finding_count"] = sum(
        1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    )
    return identity


def verify_file_identity(identity: object, label: str) -> Path:
    if not isinstance(identity, dict):
        raise ValueError(f"{label} identity is missing")
    path_value, digest = identity.get("path"), identity.get("sha256")
    if not isinstance(path_value, str) or not path_value:
        raise ValueError(f"{label} path is missing")
    if not isinstance(digest, str) or len(digest) != 64:
        raise ValueError(f"{label} digest is missing")
    path = Path(path_value)
    current = file_identity(path)
    if current["sha256"] != digest or (
        "bytes" in identity and current["bytes"] != identity["bytes"]
    ):
        raise ValueError(f"{label} changed after prepare: {path}")
    if "finding_count" in identity and output_identity(path)["finding_count"] != identity["finding_count"]:
        raise ValueError(f"{label} finding count changed after prepare: {path}")
    return path


def verify_jsonl_output(state: object, supplied: Path, label: str) -> Path:
    if not isinstance(state, dict):
        raise ValueError(f"{label} coverage is missing")
    count = state.get("finding_count")
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ValueError(f"{label} finding count is invalid")
    identity = {
        "path": state.get("output"),
        "sha256": state.get("sha256"),
        "finding_count": count,
    }
    if isinstance(state.get("bytes"), int):
        identity["bytes"] = state["bytes"]
    path = verify_file_identity(identity, label)
    if path != supplied.resolve():
        raise ValueError(f"{label} path does not match its run manifest")
    return path


def coverage_complete(scope: dict) -> bool:
    for key in ("tool_coverage", "axis_coverage", "validator_coverage"):
        if (scope.get(key) or {}).get("complete") is not True:
            return False
    for key in ("build_coverage", "mutation_coverage", "reconcile_coverage"):
        state = scope.get(key)
        if state is not None and state.get("complete") is not True:
            return False
    return True


def set_phases(
    path: Path,
    phases: dict[str, dict],
    outputs: Optional[dict[str, Path]] = None,
) -> None:
    update_scope(path, phases=phases, outputs=outputs)


def update_scope(
    path: Path,
    *,
    fields: Optional[dict] = None,
    phases: Optional[dict[str, dict]] = None,
    outputs: Optional[dict[str, Path]] = None,
) -> None:
    scope = read_scope(path)
    scope.update(fields or {})
    for phase, state in (phases or {}).items():
        value = dict(state)
        output = (outputs or {}).get(phase)
        if output is not None:
            value.update(output_identity(output))
            value["output"] = value.pop("path")
        scope[f"{phase}_coverage"] = value
    scope["coverage_complete"] = coverage_complete(scope)
    write_json_atomic(path, scope)


def set_phase(
    path: Path,
    phase: str,
    state: dict,
    output: Optional[Path] = None,
) -> None:
    set_phases(path, {phase: state}, {phase: output} if output else None)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scope", type=Path)
    args = parser.parse_args()
    try:
        read_scope(args.scope)
    except ValueError as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
