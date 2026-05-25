#!/usr/bin/env python3
"""Prose-hygiene detector for the code-ultrareview prose-hygiene lens.

Stdlib-only. Reads a PR body (optional), PR title (optional),
NUL-delimited commit records from `fetch_commits.sh` (optional), and zero
or more prose file paths from the diff. Emits a JSON list of findings on
stdout in the canonical lens schema consumed by `scripts/aggregation.py`.

The check categories are the portable baseline shipped with the skill:

  - internal-leak       — local paths, personal emails, machine hostnames
  - ai-signature-footer — Co-Authored-By: Claude, "🤖 Generated with", etc.
  - rule-restatement    — body lines restating a rule the body claims to
                          follow (generalized silent-compliance pattern)
  - length-overflow     — PR body / commit body over budget
  - ai-vocabulary       — delve, tapestry, additionally, moreover, etc.
  - em-dash-density     — > 1 em-dash per 100 words
  - commit-shape-non-cc — conventional-commit shape; severity gated by
                          repo-level CC adoption auto-detect

The layered-discovery contract (project rules > user-global rules >
baseline) is the orchestrator's responsibility; this detector ships the
baseline. `discover_rules(repo_root)` returns the discovered paths so the
orchestrator can compose the report header line.

Scope filter — prose files matching SKILL.md, CLAUDE.md, evals.json,
.claude/rules/, or skills/<name>/ are excluded (model-instruction files,
not shared prose deliverables).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

LENS = "prose-hygiene"

# Length budgets — module-level constants so a reader can tune at the top.
PR_BODY_SOFT_CAP_LINES = 80
PR_BODY_HARD_CAP_LINES = 150
PR_BODY_SUMMARY_MAX_BULLETS = 5
PR_BODY_TEST_PLAN_MAX_ITEMS = 8
COMMIT_SUBJECT_MAX_CHARS = 72
COMMIT_BODY_LINE_MAX_CHARS = 100
COMMIT_BODY_MAX_LINES = 20

EM_DASH_PER_100_WORDS_MAX = 1.0

# Categories where confidence is anchored on the evidence (regex match on
# concrete text), not on heuristic judgment.
CONF_HIGH = 90
CONF_MED = 80
CONF_LOW = 70

# Conventional-commit types — the closed set the skill recognizes.
CC_TYPES = (
    "feat", "fix", "docs", "chore", "refactor", "test",
    "perf", "ci", "build", "style", "revert",
)
CC_SUBJECT_RE = re.compile(
    r"^(?:" + "|".join(CC_TYPES) + r")(?:\([^)]+\))?!?:\s+\S"
)

# ---------------------------------------------------------------------------
# Pattern banks
# ---------------------------------------------------------------------------

INTERNAL_LEAK_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"/Users/[A-Za-z0-9_.-]+/"), "macos-home-path"),
    (re.compile(r"/home/[A-Za-z0-9_.-]+/"), "linux-home-path"),
    (re.compile(r"[CcDd]:\\Users\\[A-Za-z0-9_.-]+\\"), "windows-home-path"),
    (
        re.compile(
            r"\b[A-Za-z0-9._%+-]+@(?:gmail|icloud|yahoo|hotmail|outlook|"
            r"proton(?:mail)?|me|aol)\.[a-z]+\b",
            re.IGNORECASE,
        ),
        "personal-email",
    ),
    (
        re.compile(r"\b[A-Z][A-Za-z]+'s-(?:MacBook|iMac|Mac-?(?:Pro|Mini))[A-Za-z-]*\b"),
        "machine-hostname",
    ),
]

# Authoring-process traces — references to internal authoring tooling that
# ship to readers who have no access to that environment. Anchored on
# path-context so plain mentions of a public tool by name (e.g. a README
# row describing the `brand-voice` skill) do not fire — only paths and
# possessive constructions tied to authoring.
AUTHORING_TRACE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(
            r"(?:~|\$HOME|/Users/[A-Za-z0-9_.-]+|/home/[A-Za-z0-9_.-]+)"
            r"/(?:\.claude/)?brand-voices?/",
            re.IGNORECASE,
        ),
        "brand-voice-path",
    ),
    (
        re.compile(
            r"(?:~|\$HOME|/Users/[A-Za-z0-9_.-]+|/home/[A-Za-z0-9_.-]+)"
            r"/(?:[A-Za-z0-9_.-]+/)*BRAND-VOICE(?:-[A-Z_]+)?\.md\b",
        ),
        "brand-voice-path-filename",
    ),
    (
        re.compile(r"\bmaintainer-specific\b", re.IGNORECASE),
        "maintainer-specific",
    ),
    (
        re.compile(
            r"\bmaintainer'?s?\s+(?:path|tool|config|voice|rules)\b",
            re.IGNORECASE,
        ),
        "maintainer-possessive",
    ),
    (
        re.compile(
            r"\b(?:internal|private)\s+(?:voice|rules|tooling|tool|config|path)\b",
            re.IGNORECASE,
        ),
        "internal-tooling",
    ),
]

AI_SIGNATURE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^Co-Authored-By:\s*Claude\b", re.MULTILINE | re.IGNORECASE), "claude-coauthor"),
    (re.compile(r"^Co-Authored-By:\s*Cursor\b", re.MULTILINE | re.IGNORECASE), "cursor-coauthor"),
    (re.compile(r"🤖\s*Generated with", re.IGNORECASE), "robot-generated-with"),
    (re.compile(r"^\s*Generated with\s+\[?[Cc]laude\b", re.MULTILINE), "generated-with-claude"),
    (re.compile(r"^\s*As an AI\b", re.MULTILINE | re.IGNORECASE), "as-an-ai"),
]

# Rule-restatement — bullet/checklist lines that restate a rule the body
# claims to follow. Section headers ("## Test plan") and ordinary bullets
# do NOT match — only bullets whose content references a rule by name.
RULE_RESTATEMENT_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(
            r"^\s*[-*]\s*\[?[ x]?\]?\s*No (?:AI[- ]signature|Claude(?:-?signature)?|signature)\s+footer",
            re.MULTILINE | re.IGNORECASE,
        ),
        "no-ai-footer-restatement",
    ),
    (
        re.compile(
            r"^\s*[-*]\s*\[?[ x]?\]?\s*(?:Per|As instructed by) (?:the )?(?:rule|requirements?|guidance|spec|brief)\b",
            re.MULTILINE | re.IGNORECASE,
        ),
        "per-instructed-by",
    ),
    (
        re.compile(
            r"^\s*[-*]\s*\[?[ x]?\]?\s*(?:Followed|Following|Adhered to) (?:the )?(?:rule|convention|guideline|policy)\b",
            re.MULTILINE | re.IGNORECASE,
        ),
        "followed-rule",
    ),
    (
        re.compile(
            r"^\s*[-*]\s*\[?[ x]?\]?\s*(?:Silent[- ]compliance|No\s+secrets?\s+committed)\b",
            re.MULTILINE | re.IGNORECASE,
        ),
        "silent-compliance-restatement",
    ),
]

# Defensive negations — sentences that describe skill behavior in the
# negative when a positive assertion is equivalent. Anchored on
# `~/.claude/rules/writing.md` § "Assert positively. Reserve negation for
# real constraints (`NEVER commit secrets`)." Allowlist (below) carves
# out the legitimate mandates and behavioral contracts.
DEFENSIVE_NEGATION_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(
            r"\b(?:The|This|Our)\s+(?:lens|skill|script|tool|check|detector|orchestrator)"
            r"\s+never\s+(?:names?|mentions?|references?|uses?|exposes?|hardcodes?|leaks?)\b",
            re.IGNORECASE,
        ),
        "skill-subject-negation",
    ),
    (
        re.compile(r"\bno\s+\w+-specific\s+\w+\b", re.IGNORECASE),
        "defensive-scoping",
    ),
    (
        re.compile(
            r"\bnever\s+(?:names?|mentions?|references?)\s+(?:any|a)\s+\w+",
            re.IGNORECASE,
        ),
        "anchored-negation",
    ),
]

MANDATE_ALLOWLIST: list[re.Pattern[str]] = [
    re.compile(r"\bNEVER\b"),  # case-sensitive — uppercase is the mandate marker.
    re.compile(r"\bnever fail(?:s|ing)? silently\b", re.IGNORECASE),
    re.compile(r"\bnever break(?:s|ing)? the public API\b", re.IGNORECASE),
    re.compile(r"\bnever aborts?\b", re.IGNORECASE),
    re.compile(r"\bnever advertises?\b", re.IGNORECASE),
    re.compile(r"\bnever silent[- ]drop", re.IGNORECASE),
]

AI_VOCABULARY = (
    "delve", "tapestry", "intricate", "pivotal", "testament", "underscore",
    "crucial", "garner", "showcase", "additionally", "moreover",
    "furthermore", "indeed",
)
AI_VOCABULARY_RE = re.compile(
    r"\b(?:" + "|".join(AI_VOCABULARY) + r")\b",
    re.IGNORECASE,
)

# Filler test-plan items — vague verifications a senior reviewer would
# reject as non-actionable.
FILLER_TEST_PLAN_RE = re.compile(
    r"^\s*[-*]\s*\[?[ x]?\]?\s*(?:test (?:it )?thoroughly|verify (?:nothing|everything) (?:broke|works)|"
    r"make sure (?:it|everything) works|check (?:that )?(?:it works|everything))\b",
    re.MULTILINE | re.IGNORECASE,
)

# Scope tiers — every file in the diff classifies into one tier, and each
# tier runs a different check subset:
#
# - 'full'      — Tier 1, shared prose (README, CHANGELOG, RELEASE-NOTES,
#                 CONTRIBUTING, docs/). All baseline categories apply.
# - 'leak-only' — Tier 2, model-instruction files (SKILL.md, CLAUDE.md,
#                 AGENTS.md, .cursorrules, .claude/rules/, .cursor/,
#                 evals.json) AND source code (.py, .ts, .js, .go, …).
#                 Only leak + signature + authoring-process checks run.
#                 A local path, personal email, machine hostname, or AI
#                 co-author footer is a leak regardless of file type.
#                 Style/length/vocab/defensive-negation categories are
#                 prose contracts that do not apply to model instructions
#                 or source code.
# - 'skip'      — Build artifacts and generated binaries. Nothing runs.

FULL_PROSE_RE = re.compile(
    r"(?:^|/)(?:"
    r"README(?:\.[A-Za-z_-]+)?\.(?:md|mdx|rst|txt)"
    r"|CHANGELOG(?:\.[A-Za-z_-]+)?\.(?:md|mdx|rst|txt)"
    r"|RELEASE[-_]?NOTES?(?:\.[A-Za-z_-]+)?\.(?:md|mdx|rst|txt)"
    r"|CONTRIBUTING(?:\.[A-Za-z_-]+)?\.(?:md|mdx|rst|txt)"
    r"|docs?/.*\.(?:md|mdx|rst)"
    r")$",
    re.IGNORECASE,
)

SKIP_RE = re.compile(
    r"(?:^|/)(?:"
    r"dist/|build/|out/|target/|coverage/|node_modules/|\.git/|\.next/|"
    r"\.nuxt/|vendor/|__pycache__/|\.venv/|venv/|env/|\.tox/|\.pytest_cache/"
    r")"
    r"|(?:^|/)(?:pnpm-lock\.yaml|package-lock\.json|npm-shrinkwrap\.json)$"
    r"|\.(?:lock|lockb|min\.js|min\.css|pyc|pyo|so|o|a|dylib|class|jar|"
    r"war|wasm|map|tsbuildinfo)$",
    re.IGNORECASE,
)

# Deprecated alias — old consumers that imported `SCOPE_EXCLUDE_RE` get
# skip-only semantics. New callers should use `classify_scope`.
SCOPE_EXCLUDE_RE = SKIP_RE


# ---------------------------------------------------------------------------
# Data shape
# ---------------------------------------------------------------------------


@dataclass
class Finding:
    lens: str = LENS
    severity: str = "Low"
    location: str = ""
    finding: str = ""
    recommendation: str = ""
    confidence: int = CONF_LOW
    category: str = ""
    meta: dict = field(default_factory=dict)


def _emit(findings: list[Finding]) -> None:
    json.dump([_finding_dict(f) for f in findings], sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def _finding_dict(f: Finding) -> dict:
    d = asdict(f)
    # Drop empty meta to keep the wire format clean.
    if not d["meta"]:
        d.pop("meta")
    return d


# ---------------------------------------------------------------------------
# Discovery helpers
# ---------------------------------------------------------------------------


def discover_rules(repo_root: Path) -> list[str]:
    """Return rule files discovered in standard Claude Code locations.

    Order: per-repo overrides → project rules → user-global rules. Project
    rules win on conflict per `overrides.md` precedence — the orchestrator
    composes the merge; this helper only enumerates the paths.
    """
    found: list[Path] = []
    home = Path.home()

    # Per-repo + project rules
    for p in (
        repo_root / "CLAUDE.md",
        repo_root / ".claude" / "rules" / "writing.md",
        repo_root / ".claude" / "rules" / "git-conventions.md",
        repo_root / ".claude" / "rules" / "privacy.md",
    ):
        if p.is_file():
            found.append(p)

    # User-global rules
    for p in (
        home / ".claude" / "CLAUDE.md",
        home / ".claude" / "rules" / "writing.md",
        home / ".claude" / "rules" / "git-conventions.md",
        home / ".claude" / "rules" / "privacy.md",
    ):
        if p.is_file():
            found.append(p)

    return [str(p) for p in found]


def cc_is_adopted(repo_root: Path) -> bool:
    """Return True if the repo uses Conventional Commits.

    Three signals (any one is sufficient):
      1. A `.commitlintrc*` or `commitlint.config.*` file exists at root.
      2. `commitlint` or `@commitlint/*` is in `package.json` dependencies.
      3. ≥50% of the last 20 commit subjects match the CC pattern.
    """
    for pattern in (".commitlintrc*", "commitlint.config.*"):
        if any(repo_root.glob(pattern)):
            return True

    pj = repo_root / "package.json"
    if pj.is_file():
        try:
            data = json.loads(pj.read_text(encoding="utf-8"))
            for section in ("dependencies", "devDependencies"):
                deps = data.get(section) or {}
                if any(
                    k == "commitlint" or k.startswith("@commitlint/")
                    for k in deps
                ):
                    return True
        except (json.JSONDecodeError, OSError):
            pass

    try:
        out = subprocess.run(
            ["git", "log", "-n", "20", "--pretty=format:%s"],
            cwd=str(repo_root),
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

    subjects = [s for s in out.stdout.split("\n") if s.strip()]
    if not subjects:
        return False
    matches = sum(1 for s in subjects if CC_SUBJECT_RE.match(s))
    # Integer-arithmetic 50% threshold; the `max(1, …)` floor avoids the
    # degenerate "0 matches needed" case when the sample is tiny.
    return matches >= max(1, len(subjects) * 50 // 100)


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------


def parse_commits(records_text: str) -> list[dict]:
    """Parse the NUL-delimited records emitted by fetch_commits.sh.

    Each record: `<sha>\\0<subject>\\0<body>\\0---\\n`. The leading
    `RESULT:` header line (if present) is skipped — consumers that pipe the
    full script output get the right behavior without a pre-strip.
    """
    # Strip the optional `RESULT:` header(s).
    body = "\n".join(
        line for line in records_text.split("\n")
        if not line.startswith("RESULT:")
    )
    chunks = body.split("---\n")
    commits: list[dict] = []
    for chunk in chunks:
        chunk = chunk.strip("\n")
        if not chunk:
            continue
        parts = chunk.split("\x00")
        if len(parts) < 3:
            continue
        sha, subject, body_text = parts[0], parts[1], parts[2]
        commits.append(
            {"sha": sha.strip(), "subject": subject, "body": body_text}
        )
    return commits


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------


def _check_text_leaks(text: str, source: str, findings: list[Finding]) -> None:
    for pattern, category in INTERNAL_LEAK_PATTERNS:
        for match in pattern.finditer(text):
            line_no = text.count("\n", 0, match.start()) + 1
            findings.append(
                Finding(
                    severity="High",
                    location=f"{source}:{line_no}",
                    finding=f"Internal leak ({category}): `{match.group(0)}`",
                    recommendation=(
                        "Scrub before publishing — `~/`, repo-relative paths, "
                        "or branded equivalents."
                    ),
                    confidence=CONF_HIGH,
                    category="internal-leak",
                    meta={"pattern": category},
                )
            )


def _check_authoring_process(text: str, source: str, findings: list[Finding]) -> None:
    for pattern, category in AUTHORING_TRACE_PATTERNS:
        for match in pattern.finditer(text):
            line_no = text.count("\n", 0, match.start()) + 1
            findings.append(
                Finding(
                    severity="High",
                    location=f"{source}:{line_no}",
                    finding=f"Authoring-process trace ({category}): `{match.group(0)}`",
                    recommendation=(
                        "Scrub before publishing — the artifact ships to readers "
                        "who have no access to the authoring environment."
                    ),
                    confidence=CONF_HIGH,
                    category="authoring-process-trace",
                    meta={"pattern": category},
                )
            )


def _compute_skip_regions(text: str) -> list[tuple[int, int]]:
    """Byte-offset spans that defensive-negation must not match against.

    Fenced code blocks quote prose verbatim (often other people's), HTML
    comments are author scratchpad, and table cells are structural —
    negation in any of these is rarely a body assertion.
    """
    regions: list[tuple[int, int]] = []
    for m in re.finditer(r"```[\s\S]*?```", text):
        regions.append((m.start(), m.end()))
    for m in re.finditer(r"<!--[\s\S]*?-->", text):
        regions.append((m.start(), m.end()))
    for m in re.finditer(r"^\s*\|.*$", text, re.MULTILINE):
        regions.append((m.start(), m.end()))
    return regions


def _in_skip_region(pos: int, regions: list[tuple[int, int]]) -> bool:
    return any(start <= pos < end for start, end in regions)


def _check_defensive_negation(text: str, source: str, findings: list[Finding]) -> None:
    skip_regions = _compute_skip_regions(text)
    for pattern, category in DEFENSIVE_NEGATION_PATTERNS:
        for match in pattern.finditer(text):
            if _in_skip_region(match.start(), skip_regions):
                continue
            line_start = text.rfind("\n", 0, match.start()) + 1
            line_end = text.find("\n", match.end())
            if line_end == -1:
                line_end = len(text)
            line = text[line_start:line_end]
            if any(allow.search(line) for allow in MANDATE_ALLOWLIST):
                continue
            line_no = text.count("\n", 0, match.start()) + 1
            findings.append(
                Finding(
                    severity="Medium",
                    location=f"{source}:{line_no}",
                    finding=f"Defensive negation ({category}): `{match.group(0)}`",
                    recommendation=(
                        "Assert positively. Reserve negation for real constraints "
                        "(`NEVER commit secrets`)."
                    ),
                    confidence=CONF_MED,
                    category="defensive-negation",
                    meta={"pattern": category},
                )
            )


def _check_signature_footers(text: str, source: str, findings: list[Finding]) -> None:
    for pattern, category in AI_SIGNATURE_PATTERNS:
        for match in pattern.finditer(text):
            line_no = text.count("\n", 0, match.start()) + 1
            findings.append(
                Finding(
                    severity="High",
                    location=f"{source}:{line_no}",
                    finding=f"AI signature footer ({category}): `{match.group(0).strip()}`",
                    recommendation="Remove AI co-authorship and generator footers.",
                    confidence=CONF_HIGH,
                    category="ai-signature-footer",
                    meta={"pattern": category},
                )
            )


def _check_rule_restatement(text: str, source: str, findings: list[Finding]) -> None:
    for pattern, category in RULE_RESTATEMENT_PATTERNS:
        for match in pattern.finditer(text):
            line_no = text.count("\n", 0, match.start()) + 1
            findings.append(
                Finding(
                    severity="Medium",
                    location=f"{source}:{line_no}",
                    finding=(
                        f"Restates a rule the body claims to follow ({category}): "
                        f"`{match.group(0).strip()}`"
                    ),
                    recommendation=(
                        "Comply silently — the rule belongs in repo conventions, "
                        "not in the artifact."
                    ),
                    confidence=CONF_MED,
                    category="rule-restatement",
                    meta={"pattern": category},
                )
            )
    for match in FILLER_TEST_PLAN_RE.finditer(text):
        line_no = text.count("\n", 0, match.start()) + 1
        findings.append(
            Finding(
                severity="Medium",
                location=f"{source}:{line_no}",
                finding=f"Filler test-plan item: `{match.group(0).strip()}`",
                recommendation="Replace with an enumerable, reproducible verification step.",
                confidence=CONF_MED,
                category="rule-restatement",
                meta={"pattern": "filler-test-plan"},
            )
        )


def _check_ai_vocabulary(text: str, source: str, findings: list[Finding]) -> None:
    seen: dict[str, int] = {}
    for match in AI_VOCABULARY_RE.finditer(text):
        term = match.group(0).lower()
        line_no = text.count("\n", 0, match.start()) + 1
        # Report at most three matches per term to keep noise bounded.
        count = seen.get(term, 0)
        if count >= 3:
            seen[term] = count + 1
            continue
        seen[term] = count + 1
        findings.append(
            Finding(
                severity="Low",
                location=f"{source}:{line_no}",
                finding=f"AI vocabulary: `{term}`",
                recommendation="Replace with the surrounding voice's word.",
                confidence=CONF_LOW,
                category="ai-vocabulary",
                meta={"term": term},
            )
        )


def _check_em_dash_density(text: str, source: str, findings: list[Finding]) -> None:
    words = len(re.findall(r"\w+", text))
    if words < 100:
        return
    em_dashes = text.count("—")
    density = (em_dashes / words) * 100
    if density > EM_DASH_PER_100_WORDS_MAX:
        findings.append(
            Finding(
                severity="Low",
                location=f"{source}:1",
                finding=(
                    f"Em-dash density {density:.2f} per 100 words "
                    f"({em_dashes} em-dashes, {words} words)"
                ),
                recommendation="Replace some em-dashes with parens, commas, or full stops.",
                confidence=CONF_LOW,
                category="em-dash-density",
                meta={"em_dashes": em_dashes, "words": words},
            )
        )


def _check_pr_body_length(body: str, findings: list[Finding]) -> None:
    lines = body.split("\n")
    non_blank = [line for line in lines if line.strip()]
    total = len(non_blank)
    if total > PR_BODY_HARD_CAP_LINES:
        findings.append(
            Finding(
                severity="Medium",
                location=f"PR body:{len(lines)}",
                finding=f"PR body overlong: {total} non-blank lines (hard cap {PR_BODY_HARD_CAP_LINES})",
                recommendation=(
                    "Trim Summary/Test plan; details belong in the diff, the spec, "
                    "or linked docs."
                ),
                confidence=CONF_HIGH,
                category="length-overflow",
                meta={"non_blank_lines": total, "cap": PR_BODY_HARD_CAP_LINES},
            )
        )
    elif total > PR_BODY_SOFT_CAP_LINES:
        findings.append(
            Finding(
                severity="Low",
                location=f"PR body:{len(lines)}",
                finding=f"PR body long: {total} non-blank lines (soft cap {PR_BODY_SOFT_CAP_LINES})",
                recommendation="Consider trimming — every sentence should change the reader's understanding.",
                confidence=CONF_MED,
                category="length-overflow",
                meta={"non_blank_lines": total, "cap": PR_BODY_SOFT_CAP_LINES},
            )
        )

    # Section-level budgets — count bullet lines under "## Summary" and
    # "## Test plan". The trailing `## ` marker bounds the section.
    for section, max_items, label in (
        ("Summary", PR_BODY_SUMMARY_MAX_BULLETS, "Summary bullets"),
        ("Test plan", PR_BODY_TEST_PLAN_MAX_ITEMS, "Test-plan items"),
    ):
        bullets = _count_section_bullets(body, section)
        if bullets is not None and bullets > max_items:
            findings.append(
                Finding(
                    severity="Low",
                    location=f"PR body:Section '{section}'",
                    finding=f"{label}: {bullets} (cap {max_items})",
                    recommendation=f"Cap the {section} section at {max_items} items.",
                    confidence=CONF_MED,
                    category="length-overflow",
                    meta={"section": section, "count": bullets, "cap": max_items},
                )
            )


def _count_section_bullets(body: str, heading: str) -> int | None:
    """Return the bullet count under `## <heading>`, or None if absent."""
    pattern = re.compile(
        r"^\s*##\s+" + re.escape(heading) + r"\s*$(.*?)(?=^\s*##\s+|\Z)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    match = pattern.search(body)
    if not match:
        return None
    section = match.group(1)
    return sum(1 for line in section.split("\n") if re.match(r"^\s*[-*]\s", line))


def _check_commit_shape(
    commits: list[dict],
    adopted: bool,
    findings: list[Finding],
) -> None:
    for c in commits:
        sha_short = c["sha"][:7]
        subject = c["subject"]

        if len(subject) > COMMIT_SUBJECT_MAX_CHARS:
            findings.append(
                Finding(
                    severity="Low",
                    location=f"commit {sha_short}:subject",
                    finding=(
                        f"Subject {len(subject)} chars (cap {COMMIT_SUBJECT_MAX_CHARS}): "
                        f"`{subject[:80]}…`"
                    ),
                    recommendation="Shorten the subject; details belong in the body.",
                    confidence=CONF_HIGH,
                    category="length-overflow",
                    meta={"chars": len(subject), "cap": COMMIT_SUBJECT_MAX_CHARS},
                )
            )

        body = c.get("body", "").rstrip("\n")
        body_lines = body.split("\n") if body else []
        non_blank_body = [line for line in body_lines if line.strip()]
        if len(non_blank_body) > COMMIT_BODY_MAX_LINES:
            findings.append(
                Finding(
                    severity="Low",
                    location=f"commit {sha_short}:body",
                    finding=(
                        f"Body {len(non_blank_body)} non-blank lines "
                        f"(cap {COMMIT_BODY_MAX_LINES})"
                    ),
                    recommendation="Tighten the body — keep the `why`, drop the narration.",
                    confidence=CONF_MED,
                    category="length-overflow",
                    meta={"lines": len(non_blank_body), "cap": COMMIT_BODY_MAX_LINES},
                )
            )
        for idx, line in enumerate(body_lines, start=2):
            if len(line) > COMMIT_BODY_LINE_MAX_CHARS:
                findings.append(
                    Finding(
                        severity="Low",
                        location=f"commit {sha_short}:body:{idx}",
                        finding=(
                            f"Body line {len(line)} chars "
                            f"(cap {COMMIT_BODY_LINE_MAX_CHARS})"
                        ),
                        recommendation="Wrap commit body lines at ~100 chars for `git log` readability.",
                        confidence=CONF_MED,
                        category="length-overflow",
                        meta={"chars": len(line), "cap": COMMIT_BODY_LINE_MAX_CHARS},
                    )
                )
                break  # one finding per commit body is enough

        # CC shape — adopted repos block; non-adopted repos only inform.
        if not CC_SUBJECT_RE.match(subject):
            if adopted:
                findings.append(
                    Finding(
                        severity="Medium",
                        location=f"commit {sha_short}:subject",
                        finding=f"Non-conventional subject: `{subject}`",
                        recommendation=(
                            "Use `<type>(<scope>)?: <description>` "
                            f"(types: {', '.join(CC_TYPES)})."
                        ),
                        confidence=CONF_HIGH,
                        category="commit-shape-non-cc",
                        meta={"adopted": True, "subject": subject},
                    )
                )
            else:
                findings.append(
                    Finding(
                        severity="Low",
                        location=f"commit {sha_short}:subject",
                        finding=f"Subject does not match Conventional Commits: `{subject}`",
                        recommendation=(
                            "Optional — adopt CC by adding a `.commitlintrc*` file "
                            "or matching ≥50% of recent commits."
                        ),
                        confidence=CONF_LOW,
                        category="commit-shape-non-cc",
                        meta={"adopted": False, "subject": subject},
                    )
                )

        # Signature footer, leaks, authoring traces, and defensive negations
        # all apply to the commit body.
        if body:
            _check_signature_footers(body, f"commit {sha_short}:body", findings)
            _check_text_leaks(body, f"commit {sha_short}:body", findings)
            _check_authoring_process(body, f"commit {sha_short}:body", findings)
            _check_defensive_negation(body, f"commit {sha_short}:body", findings)


def classify_scope(path) -> str:
    """Return 'full' | 'leak-only' | 'skip' for a file path.

    See the comment block above `FULL_PROSE_RE` for the tier definitions.
    """
    norm = str(path).replace("\\", "/")
    if SKIP_RE.search(norm):
        return "skip"
    if FULL_PROSE_RE.search(norm):
        return "full"
    return "leak-only"


def filter_scope(paths: Iterable[str]) -> list[str]:
    """Return paths that are not in the `skip` tier.

    Old semantics filtered model-instruction files entirely; the new
    semantics only filter the skip tier — model-instruction files pass
    through to the leak-only tier where leak / signature /
    authoring-process checks still apply.
    """
    return [p for p in paths if classify_scope(p) != "skip"]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Prose-hygiene detector for the code-ultrareview prose-hygiene lens.",
    )
    p.add_argument("--pr-body-file", type=Path, default=None)
    p.add_argument("--pr-title", type=str, default=None)
    p.add_argument("--commits-file", type=Path, default=None)
    p.add_argument("--prose-file", action="append", default=[], dest="prose_files")
    p.add_argument("--repo-root", type=Path, default=Path.cwd())
    p.add_argument(
        "--discover-rules-only",
        action="store_true",
        help="Print discovered rule paths (one per line) and exit.",
    )
    p.add_argument(
        "--cc-adopted-only",
        action="store_true",
        help="Print `true` or `false` for CC adoption and exit.",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    if args.discover_rules_only:
        for path in discover_rules(args.repo_root):
            print(path)
        return 0

    if args.cc_adopted_only:
        print("true" if cc_is_adopted(args.repo_root) else "false")
        return 0

    findings: list[Finding] = []

    # PR title — only the leak and signature-footer checks apply (length and
    # AI-vocabulary on a one-line title would over-fire).
    if args.pr_title:
        _check_text_leaks(args.pr_title, "PR title:1", findings)
        _check_signature_footers(args.pr_title, "PR title:1", findings)
        _check_authoring_process(args.pr_title, "PR title:1", findings)
        _check_defensive_negation(args.pr_title, "PR title:1", findings)

    # PR body — full check set.
    if args.pr_body_file and args.pr_body_file.is_file():
        body = args.pr_body_file.read_text(encoding="utf-8")
        _check_text_leaks(body, "PR body", findings)
        _check_signature_footers(body, "PR body", findings)
        _check_authoring_process(body, "PR body", findings)
        _check_defensive_negation(body, "PR body", findings)
        _check_rule_restatement(body, "PR body", findings)
        _check_ai_vocabulary(body, "PR body", findings)
        _check_em_dash_density(body, "PR body", findings)
        _check_pr_body_length(body, findings)

    # Commits.
    if args.commits_file and args.commits_file.is_file():
        records = args.commits_file.read_text(encoding="utf-8")
        commits = parse_commits(records)
        adopted = cc_is_adopted(args.repo_root)
        _check_commit_shape(commits, adopted, findings)

    # Prose files in the diff — classify per tier, then run the
    # appropriate check subset.
    for path_str in args.prose_files:
        tier = classify_scope(path_str)
        if tier == "skip":
            continue
        path = Path(path_str)
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")

        # Leak / signature / authoring-process checks run at both tiers —
        # these patterns anchor on concrete strings that are leaks
        # regardless of file type.
        _check_text_leaks(text, path_str, findings)
        _check_signature_footers(text, path_str, findings)
        _check_authoring_process(text, path_str, findings)

        # Style + length + vocab + defensive-negation checks run only at
        # the full-prose tier — they are prose contracts that do not
        # apply to model instructions or source code.
        if tier == "full":
            _check_defensive_negation(text, path_str, findings)
            _check_ai_vocabulary(text, path_str, findings)
            _check_em_dash_density(text, path_str, findings)

    _emit(findings)
    return 0


if __name__ == "__main__":
    sys.exit(main())
