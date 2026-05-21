"""Example sub-graph extractor.

Parses fenced code blocks marked `bash`, `sh`, or `shell`. For each command
invocation, extracts the program + flags and verifies each flag appears in
the program's argparse/getopts definition. Flags absent from the parser
surface as findings.
"""

from __future__ import annotations

import re
from pathlib import Path

from ._common import Finding, IgnoreFile

FENCE_RE = re.compile(
    r"```(?:bash|sh|shell)\s*\n(?P<body>.*?)```",
    re.DOTALL,
)
FLAG_RE = re.compile(r"(?:^|\s)(-{1,2}[a-zA-Z][a-zA-Z0-9_-]*)\b")
INTERPRETERS = {"python", "python3", "bash", "sh", "node", "deno", "ruby", "perl"}


def _extract_commands(text: str) -> list[tuple[str, list[str]]]:
    """From fenced blocks, return [(program_token, flags), ...].

    When the first token is a known interpreter (`python3`, `bash`, `node`…),
    the actual program is the next token so the candidate-script lookup
    targets the script being invoked, not the interpreter binary.
    """
    commands: list[tuple[str, list[str]]] = []
    for m in FENCE_RE.finditer(text):
        body = m.group("body")
        for raw in body.splitlines():
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            stripped = re.sub(r"#.*$", "", stripped).strip()
            if not stripped:
                continue
            tokens = stripped.split()
            if not tokens:
                continue
            idx = 1 if tokens[0] in INTERPRETERS and len(tokens) > 1 else 0
            program = tokens[idx]
            args_text = " ".join(tokens[idx + 1:])
            flags = FLAG_RE.findall(" " + args_text)
            if flags:
                commands.append((program, flags))
    return commands


def _candidate_scripts(repo: Path, program: str) -> list[Path]:
    base = program.split("/")[-1]
    candidates: list[Path] = []
    for root in (repo / "scripts", repo / "skills", repo / "src"):
        if not root.exists():
            continue
        for path in root.rglob(base):
            if path.is_file():
                candidates.append(path)
    return candidates


def _script_recognises_flag(path: Path, flag: str) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    safe = re.escape(flag)
    patterns = (
        rf'["\']{safe}["\']',
        rf'\b{safe}\b\)',
        rf'getopts\s+["\']\w*{re.escape(flag.lstrip("-"))}\w*["\']',
    )
    return any(re.search(p, text) for p in patterns)


def run(repo: Path, ignore: IgnoreFile, **_) -> list[Finding]:
    findings: list[Finding] = []
    allowlist = set(ignore.list_for("example", "ignore_flags"))
    readme = repo / "README.md"
    if not readme.exists():
        return findings
    try:
        text = readme.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings

    for program, flags in _extract_commands(text):
        candidates = _candidate_scripts(repo, program)
        if not candidates:
            continue
        for flag in flags:
            if flag in allowlist:
                continue
            if any(_script_recognises_flag(p, flag) for p in candidates):
                continue
            findings.append(Finding(
                sub_graph="example",
                severity="Medium",
                location=f"README.md: `{program} {flag}`",
                finding=(
                    f"README example uses {flag!r} with {program!r}, but the "
                    f"script does not appear to parse that flag."
                ),
                recommendation=(
                    "Remove the example, add the flag to the parser, or "
                    "allowlist via `.coherence-ignore` under `example.ignore_flags`."
                ),
                confidence=80,
            ))

    return findings
