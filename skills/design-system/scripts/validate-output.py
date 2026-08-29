#!/usr/bin/env python3
"""Validate the stable minimum output contracts of designmd."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DTCG_SCHEMA = re.compile(
    r"^https://www\.designtokens\.org/schemas/\d{4}\.\d{2}/format\.json$"
)
SPEC_HEADINGS = (
    "# DESIGN.md Format",
    "# Design Tokens",
    "## Schema",
    "# Sections",
    "# Consumer Behavior for Unknown Content",
)


def _counts(value: object, keys: tuple[str, ...]) -> bool:
    return isinstance(value, dict) and all(
        isinstance(value.get(key), int) and not isinstance(value.get(key), bool)
        and value[key] >= 0
        for key in keys
    )


def _integers(value: object, keys: tuple[str, ...]) -> bool:
    return isinstance(value, dict) and all(
        isinstance(value.get(key), int) and not isinstance(value.get(key), bool)
        for key in keys
    )


def validate_lint(payload: object, exit_code: int | None = None) -> bool:
    if not isinstance(payload, dict) or not isinstance(payload.get("findings"), list):
        return False
    if not _counts(payload.get("summary"), ("errors", "warnings", "infos")):
        return False
    valid_findings = all(
        isinstance(item, dict)
        and item.get("severity") in {"error", "warning", "info"}
        and isinstance(item.get("message"), str)
        and bool(item["message"].strip())
        for item in payload["findings"]
    )
    if not valid_findings:
        return False
    counts = {
        severity: sum(
            item.get("severity") == singular
            for item in payload["findings"]
        )
        for severity, singular in (
            ("errors", "error"),
            ("warnings", "warning"),
            ("infos", "info"),
        )
    }
    if any(payload["summary"][key] != value for key, value in counts.items()):
        return False
    return exit_code is None or exit_code == (1 if counts["errors"] else 0)


def validate_diff(payload: object, exit_code: int | None = None) -> bool:
    if not isinstance(payload, dict) or not isinstance(payload.get("tokens"), dict):
        return False
    token_groups = {"colors", "typography", "rounded", "spacing", "components"}
    if not token_groups.issubset(payload["tokens"]):
        return False
    if not all(
        isinstance(group, dict)
        and {"added", "removed", "modified"}.issubset(group)
        and all(
            isinstance(group[key], list)
            and all(isinstance(item, str) for item in group[key])
            for key in ("added", "removed", "modified")
        )
        for group in (payload["tokens"][name] for name in token_groups)
    ):
        return False
    findings = payload.get("findings")
    valid = (
        isinstance(payload.get("regression"), bool)
        and isinstance(findings, dict)
        and _counts(findings.get("before"), ("errors", "warnings", "infos"))
        and _counts(findings.get("after"), ("errors", "warnings", "infos"))
        and _integers(findings.get("delta"), ("errors", "warnings"))
    )
    if not valid:
        return False
    delta = findings["delta"]
    expected_delta = {
        key: findings["after"][key] - findings["before"][key]
        for key in ("errors", "warnings")
    }
    if delta != expected_delta:
        return False
    expected_regression = delta["errors"] > 0 or delta["warnings"] > 0
    if payload["regression"] != expected_regression:
        return False
    return exit_code is None or exit_code == (1 if expected_regression else 0)


def validate_export_tailwind(payload: object) -> bool:
    if not isinstance(payload, dict):
        return False
    theme = payload.get("theme")
    extend = theme.get("extend") if isinstance(theme, dict) else None
    required = {"colors", "fontFamily", "fontSize", "borderRadius", "spacing"}
    return (
        isinstance(extend, dict)
        and required.issubset(extend)
        and all(isinstance(extend[key], dict) for key in required)
    )


def validate_export_dtcg(payload: object) -> bool:
    if not isinstance(payload, dict):
        return False
    schema = payload.get("$schema")
    if not isinstance(schema, str) or DTCG_SCHEMA.fullmatch(schema) is None:
        return False
    groups = [value for key, value in payload.items() if not key.startswith("$")]
    if not groups:
        return True
    return all(_valid_dtcg_node(group, None) for group in groups)


def _valid_dtcg_node(node: object, inherited_type: str | None) -> bool:
    if not isinstance(node, dict):
        return False
    own_type = node.get("$type", inherited_type)
    if own_type is not None and (
        not isinstance(own_type, str) or not own_type.strip()
    ):
        return False
    children = [value for key, value in node.items() if not key.startswith("$")]
    if "$value" in node:
        return (
            own_type is not None
            and node["$value"] is not None
            and not children
        )
    return bool(children) and all(
        _valid_dtcg_node(child, own_type) for child in children
    )


def _valid_spec(payload: object) -> bool:
    return (
        isinstance(payload, dict)
        and isinstance(payload.get("spec"), str)
        and validate_spec_markdown(payload["spec"])
    )


def _valid_rules(payload: object) -> bool:
    if not isinstance(payload, dict):
        return False
    rules = payload.get("rules")
    return (
        isinstance(rules, list)
        and bool(rules)
        and all(
            isinstance(rule, dict)
            and isinstance(rule.get("name"), str)
            and bool(rule["name"].strip())
            and rule.get("severity") in {"error", "warning", "info"}
            and isinstance(rule.get("description"), str)
            and bool(rule["description"].strip())
            for rule in rules
        )
    )


def validate_spec_json(payload: object) -> bool:
    return _valid_spec(payload)


def validate_spec_rules_json(payload: object) -> bool:
    return _valid_rules(payload)


def validate_spec_with_rules_json(payload: object) -> bool:
    return _valid_spec(payload) and _valid_rules(payload)


def _has_rules_table(text: str) -> bool:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    try:
        header = lines.index("| Rule | Severity | What it checks |")
    except ValueError:
        return False
    if header + 2 >= len(lines) or "---" not in lines[header + 1]:
        return False
    rows = lines[header + 2 :]
    return any(
        len(cells := [cell.strip() for cell in line.strip("|").split("|")]) >= 3
        and cells[0]
        and cells[1] in {"error", "warning", "info"}
        and cells[2]
        for line in rows
        if line.startswith("|") and line.endswith("|")
    )


def validate_spec_markdown(text: str) -> bool:
    return all(marker in text for marker in SPEC_HEADINGS)


def validate_spec_rules_markdown(text: str) -> bool:
    return _has_rules_table(text)


def validate_spec_with_rules_markdown(text: str) -> bool:
    return validate_spec_markdown(text) and _has_rules_table(text)


VALIDATORS = {
    "lint": validate_lint,
    "diff": validate_diff,
    "export-dtcg": validate_export_dtcg,
    "export-tailwind": validate_export_tailwind,
    "spec-json": validate_spec_json,
    "spec-markdown": validate_spec_markdown,
    "spec-rules-json": validate_spec_rules_json,
    "spec-rules-markdown": validate_spec_rules_markdown,
    "spec-with-rules-json": validate_spec_with_rules_json,
    "spec-with-rules-markdown": validate_spec_with_rules_markdown,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=sorted(VALIDATORS))
    parser.add_argument("path", type=Path)
    parser.add_argument("--exit-code", type=int)
    args = parser.parse_args()
    try:
        content = args.path.read_text(encoding="utf-8")
    except OSError:
        return 1
    if args.mode.endswith("markdown"):
        payload: object = content
    else:
        try:
            payload = json.loads(content)
        except json.JSONDecodeError:
            return 1
    validator = VALIDATORS[args.mode]
    if args.mode in {"lint", "diff"}:
        valid = validator(payload, args.exit_code)
    else:
        valid = validator(payload)
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
