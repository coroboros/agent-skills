"""Shared types + utilities for coherence-graph sub-graph extractors.

Exposes:
    Finding             — canonical finding shape returned by every extractor.
    load_ignore         — minimal YAML-subset parser for `.coherence-ignore`.
    normalize_description / normalize_version — comparison helpers.
    read_json_safe      — quiet JSON loader; returns None on any failure.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class Finding:
    """Canonical finding emitted by every sub-graph."""

    sub_graph: str = ""
    severity: str = "Medium"
    location: str = ""
    finding: str = ""
    recommendation: str = ""
    confidence: int = 0
    lens: str = "coherence-graph"

    def to_dict(self) -> dict:
        d = asdict(self)
        ordered = {
            "lens": d.pop("lens"),
            "sub_graph": d.pop("sub_graph"),
            "severity": d.pop("severity"),
            "location": d.pop("location"),
            "finding": d.pop("finding"),
            "recommendation": d.pop("recommendation"),
            "confidence": d.pop("confidence"),
        }
        ordered.update(d)
        return ordered


@dataclass
class IgnoreFile:
    """Parsed `.coherence-ignore` contents — nested {sub_graph: {key: [values]}}."""

    data: dict = field(default_factory=dict)

    def list_for(self, sub_graph: str, key: str) -> list[str]:
        return list(self.data.get(sub_graph, {}).get(key, []))

    def has(self, sub_graph: str, key: str, value: str) -> bool:
        return value in self.list_for(sub_graph, key)


def load_ignore(repo: Path) -> IgnoreFile:
    """Parse `.coherence-ignore` at the repo root.

    Schema — minimal YAML subset:
        <sub_graph>:
          <key>:
            - <value>
            - <value>

    Indent is exactly two spaces. Comments start with `#` and run to end of
    line. Quoted (`"`/`'`) and unquoted values are both accepted. The parser
    raises ValueError on any unexpected token — silent acceptance of malformed
    config is worse than loud failure.
    """
    path = repo / ".coherence-ignore"
    if not path.exists():
        return IgnoreFile()

    data: dict[str, dict[str, list[str]]] = {}
    current_graph: str | None = None
    current_key: str | None = None

    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        stripped = line.lstrip()

        if indent == 0:
            if not stripped.endswith(":"):
                raise ValueError(f".coherence-ignore:{lineno}: expected '<key>:' at top level, got {raw!r}")
            current_graph = stripped[:-1].strip()
            current_key = None
            data.setdefault(current_graph, {})
        elif indent == 2:
            if current_graph is None:
                raise ValueError(f".coherence-ignore:{lineno}: sub-key before sub-graph: {raw!r}")
            if not stripped.endswith(":"):
                raise ValueError(f".coherence-ignore:{lineno}: expected '<sub-key>:' at indent 2, got {raw!r}")
            current_key = stripped[:-1].strip()
            data[current_graph].setdefault(current_key, [])
        elif indent == 4:
            if current_graph is None or current_key is None:
                raise ValueError(f".coherence-ignore:{lineno}: list item without sub-key: {raw!r}")
            if not stripped.startswith("- "):
                raise ValueError(f".coherence-ignore:{lineno}: expected '- <value>' at indent 4, got {raw!r}")
            value = stripped[2:].strip()
            if (value.startswith('"') and value.endswith('"')) or (
                value.startswith("'") and value.endswith("'")
            ):
                value = value[1:-1]
            data[current_graph][current_key].append(value)
        else:
            raise ValueError(f".coherence-ignore:{lineno}: unexpected indent {indent}: {raw!r}")

    return IgnoreFile(data=data)


def normalize_description(value) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.lower().split())


def normalize_version(value) -> str:
    if not isinstance(value, str):
        return ""
    v = value.strip()
    if v[:1] in ("v", "V"):
        v = v[1:]
    return v


def read_json_safe(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
