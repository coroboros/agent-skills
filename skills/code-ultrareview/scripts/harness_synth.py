#!/usr/bin/env python3
"""Property-fuzz harness synthesis.

Detects `fast-check` (JS/TS) or `hypothesis` (Python) in repo manifests
and emits a harness skeleton with TODO blocks where the user fills in
the property assertions. Returns `{"skipped": True, "reason": "..."}`
when neither library is present — the execution phase reports the skip
in the final report, never silently.

The skeleton is intentionally minimal. MVP target: harness compiles and
imports successfully; the user writes the actual property. Spec-grammar
inference (RFC 6874 `ZoneID = 1*( unreserved / pct-encoded )` →
fast-check arbitrary) is documented in the TODO, not silently embedded.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

PYPROJECT_HYPOTHESIS_RE = re.compile(r"\bhypothesis\b", re.IGNORECASE)


def detect_property_lib(repo: Path) -> str | None:
    pkg = repo / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = None
        if isinstance(data, dict):
            for section in ("dependencies", "devDependencies"):
                deps = data.get(section) or {}
                if isinstance(deps, dict) and "fast-check" in deps:
                    return "fast-check"
    for manifest in ("pyproject.toml", "requirements.txt", "requirements-dev.txt"):
        p = repo / manifest
        if not p.exists():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if PYPROJECT_HYPOTHESIS_RE.search(text):
            return "hypothesis"
    return None


def synthesize_fast_check(spec_name: str, invariant: str, slug: str) -> str:
    """Emit a fast-check skeleton."""
    return (
        f"// Generated harness skeleton — {spec_name}\n"
        f"// Invariant: {invariant}\n"
        f"// Fill in the TODO blocks; see references/ultra-execution.md.\n\n"
        f"import * as fc from 'fast-check';\n"
        f"import {{ describe, it }} from 'vitest';\n\n"
        f"describe('{spec_name} conformance', () => {{\n"
        f"  it('{slug}', () => {{\n"
        f"    fc.assert(\n"
        f"      fc.property(\n"
        f"        // TODO: build an arbitrary that respects: {invariant}\n"
        f"        fc.string({{ minLength: 1 }}),\n"
        f"        (input) => {{\n"
        f"          // TODO: assert the property derived from: {invariant}\n"
        f"          return true;\n"
        f"        }},\n"
        f"      ),\n"
        f"    );\n"
        f"  }});\n"
        f"}});\n"
    )


def synthesize_hypothesis(spec_name: str, invariant: str, slug: str) -> str:
    """Emit a hypothesis skeleton."""
    return (
        f'"""Generated harness skeleton — {spec_name}.\n\n'
        f'Invariant: {invariant}\n'
        f'Fill in the TODO blocks; see references/ultra-execution.md.\n'
        f'"""\n\n'
        f"from hypothesis import given, strategies as st\n\n\n"
        f"@given(st.text(min_size=1))  # TODO: respect the grammar of {invariant}\n"
        f"def test_{slug}_property(value):\n"
        f"    # TODO: assert the property derived from: {invariant}\n"
        f"    assert value is not None\n"
    )


def _safe_slug(spec_name: str) -> str:
    out = []
    last_underscore = True
    for ch in spec_name.lower():
        if ch.isalnum():
            out.append(ch)
            last_underscore = False
        elif not last_underscore:
            out.append("_")
            last_underscore = True
    return "".join(out).strip("_") or "conformance"


def synthesize(
    repo: Path,
    spec_name: str,
    invariant: str,
) -> dict:
    """Top-level orchestrator. Returns one of:
        {"emitted": True, "lib": "fast-check"|"hypothesis", "path": <str>, "body": <str>}
        {"skipped": True, "reason": <str>}
    """
    lib = detect_property_lib(repo)
    if lib is None:
        return {
            "skipped": True,
            "reason": (
                "harness synthesis skipped: install fast-check (JS/TS) or "
                "hypothesis (Python) to enable"
            ),
        }
    slug = _safe_slug(spec_name)
    if lib == "fast-check":
        body = synthesize_fast_check(spec_name, invariant, slug)
        rel = f"tests/{slug}.fast-check.ts"
    else:
        body = synthesize_hypothesis(spec_name, invariant, slug)
        rel = f"tests/test_{slug}_property.py"
    return {"emitted": True, "lib": lib, "path": rel, "body": body}
