#!/usr/bin/env python3
"""Shared artifact and scope contracts for Code Ultrareview phases."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

COVERAGE_FIELDS = (
    "tool_coverage",
    "axis_coverage",
    "validator_coverage",
    "build_coverage",
    "mutation_coverage",
    "reconcile_coverage",
)


def read_scope(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("scope.json must contain an object")
    for key in COVERAGE_FIELDS:
        value = payload.get(key)
        if value is not None and not isinstance(value, dict):
            raise ValueError(f"scope.json {key} must be an object when present")
    return payload


def write_json_atomic(path: Path, payload: dict) -> None:
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def write_jsonl_atomic(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        "".join(json.dumps(record, sort_keys=False) + "\n" for record in records),
        encoding="utf-8",
    )
    os.replace(temporary, path)


def read_required_diff(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"required diff file is missing: {path}")
    return path.read_text(encoding="utf-8")


def file_identity(path: Path) -> dict:
    if not path.is_file():
        raise ValueError(f"required run artifact is missing: {path}")
    resolved = path.resolve()
    data = resolved.read_bytes()
    return {
        "path": str(resolved),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }


def verify_file_identity(identity: object, label: str) -> Path:
    if not isinstance(identity, dict):
        raise ValueError(f"{label} identity is missing")
    path_value = identity.get("path")
    digest = identity.get("sha256")
    if not isinstance(path_value, str) or not path_value:
        raise ValueError(f"{label} path is missing")
    if not isinstance(digest, str) or len(digest) != 64:
        raise ValueError(f"{label} digest is missing")
    path = Path(path_value)
    current = file_identity(path)
    if current["sha256"] != digest:
        raise ValueError(f"{label} digest changed after prepare: {path}")
    return path
