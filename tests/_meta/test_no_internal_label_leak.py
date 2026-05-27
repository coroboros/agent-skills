"""CI gate against author-coordinate language in shipped skill source.

Workstream labels (`WS-N`), spec-process vocabulary (`spec AC`,
`the rebuild`, `carried verbatim from prior X`), and rebuild-history
breadcrumbs require the reader to have the author's mental model.
They are useful at authoring time, noise to anyone consuming the
shipped skill.

The skill bundle (`skills/<name>/`) is what users install via
`npx skills add`. Everything in there is user-facing. The check
scans those files only — repo-level dev docs (`tests/<skill>/MIGRATION.md`,
postmortems, this test itself) live outside `skills/` and are
out of scope.

Allowlist files legitimately document the format the patterns live in:
- `skills/forge/**` — forge produces the spec format (`### WS-N:`).
- `skills/apex/steps/step-03-execute.md` / `step-04-examine.md` —
  apex teaches the anti-pattern rule with the literal `WS-3` example.
- Files referencing `Spec AC closure` — a named apex feature, not a leak.

Background on why this exists: see
`~/.claude/output/agent-skills/postmortems/internal-label-enforcement-gap.md`
for the root-cause analysis of PR #57's leak. The summary: apex's
rule fires only when /apex is the orchestrator. Manual-authoring
sessions bypass it. This test is the load-bearing fail-loud signal
for repo-wide enforcement.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import REPO_ROOT, SKILLS_DIR  # noqa: E402
from _internal_label_patterns import INLINE_OPT_OUT, PATTERNS, scan_line  # noqa: E402

# File extensions worth scanning. Markdown + Python + Shell + JSON cover
# every shipped surface inside skills/. Other extensions (yml, toml,
# images) carry no prose.
_SCAN_EXTENSIONS = (".md", ".py", ".sh", ".bash", ".json")

# Path-prefix allowlist (relative to repo root).
# A path matches the allowlist when it equals an entry OR starts with
# an entry followed by `/`. Directory entries are open-ended.
_ALLOWLIST_PATHS = (
    # Forge owns the spec format — it produces the `### WS-N:` headings.
    "skills/forge",
    # Apex teaches the anti-pattern rule with the literal WS-3 example.
    # The rule body itself contains the very tokens it forbids.
    "skills/apex/steps/step-03-execute.md",
    "skills/apex/steps/step-04-examine.md",
    # The code-ultrareview Documentation axis brief catalogues the
    # patterns this gate blocks, so it carries every literal as table
    # cells. Same precedent as the apex rule files.
    "skills/code-ultrareview/references/axes/documentation.md",
)


def _is_allowlisted(rel_path: str) -> bool:
    for entry in _ALLOWLIST_PATHS:
        if rel_path == entry:
            return True
        if rel_path.startswith(entry + "/"):
            return True
    return False


def _iter_scannable_files() -> list[Path]:
    out: list[Path] = []
    for path in SKILLS_DIR.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in _SCAN_EXTENSIONS:
            continue
        # Skip __pycache__ and similar.
        if any(part.startswith("__") and part.endswith("__") for part in path.parts):
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        if _is_allowlisted(rel):
            continue
        out.append(path)
    return sorted(out)


def _scan_file(path: Path) -> list[tuple[int, str, str, str]]:
    """Return (lineno, pattern_name, matched_text, hint) tuples for each hit."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    hits: list[tuple[int, str, str, str]] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for name, matched, hint in scan_line(line):
            hits.append((lineno, name, matched, hint))
    return hits


class TestNoInternalLabelLeak(unittest.TestCase):
    """Block author-coordinate language from shipped skill source."""

    def test_no_internal_label_leak_in_shipped_surface(self):
        violations: list[str] = []
        for path in _iter_scannable_files():
            rel = path.relative_to(REPO_ROOT).as_posix()
            for lineno, name, matched, hint in _scan_file(path):
                violations.append(
                    f"{rel}:{lineno} — {name}: {matched!r}\n"
                    f"  Hint: {hint}"
                )

        if violations:
            joined = "\n".join(violations)
            self.fail(
                f"Internal-label leak in shipped skill source "
                f"({len(violations)} violation(s)):\n\n{joined}\n\n"
                f"These tokens require the reader to have the author's mental "
                f"model. Translate them to domain facts. Per-line opt-out: "
                f"append `# noqa: internal-label` to the line when the prose "
                f"legitimately names the anti-pattern.\n\n"
                f"To allowlist a whole file (only for files that document the "
                f"format these tokens live in), add the path to "
                f"`_ALLOWLIST_PATHS` in this test."
            )

    def test_allowlist_paths_actually_exist(self):
        """Catch typos / renames in `_ALLOWLIST_PATHS`."""
        for entry in _ALLOWLIST_PATHS:
            path = REPO_ROOT / entry
            self.assertTrue(
                path.exists(),
                f"Allowlist entry does not exist on disk: {entry}",
            )

    def test_inline_opt_out_marker_is_recognised(self):
        """Both `#` and `<!--` opt-out markers are recognised."""
        self.assertTrue(INLINE_OPT_OUT.search(
            "Refers to WS-3 as the anti-pattern.  # noqa: internal-label"
        ))
        self.assertTrue(INLINE_OPT_OUT.search(
            "Refers to WS-3 in prose.  <!-- noqa: internal-label -->"
        ))

    def test_spec_ac_closure_is_not_a_leak(self):
        """`Spec AC closure` is a named apex feature — must not flag."""
        line = "Skip if § 0a Spec AC closure applied."
        for regex, name, _ in PATTERNS:
            if name.startswith("spec-process"):
                self.assertIsNone(
                    regex.search(line),
                    "`Spec AC closure` is a named feature and must be exempt",
                )

    def test_bare_spec_ac_is_a_leak(self):
        """`spec AC` without `closure` after must flag."""
        line = "verified per the spec AC contract"
        matched = False
        for regex, name, _ in PATTERNS:
            if name.startswith("spec-process"):
                matched = regex.search(line) is not None
        self.assertTrue(matched, "Bare `spec AC` must be caught")

    def test_capital_s_spec_ac_is_a_leak(self):
        """Capital-S `Spec AC` (no `closure` after) must flag.

        The gate originally used a case-sensitive regex and missed
        `Spec AC: 25 findings` in a docstring. IGNORECASE closes that gap.
        """
        line = "    Spec AC: 25 sub-80 findings → 3 batches"
        matched = False
        for regex, name, _ in PATTERNS:
            if name.startswith("spec-process"):
                matched = regex.search(line) is not None
        self.assertTrue(matched, "Capital-S `Spec AC` must be caught")

    def test_capital_s_spec_ac_closure_is_not_a_leak(self):
        """`Spec AC closure` (capital S, with `closure`) must NOT flag.

        Apex's named feature stays exempt even with IGNORECASE — the
        negative lookahead `(?! closure)` is also case-insensitive.
        """
        line = "Skip if § 0a Spec AC closure applied."
        for regex, name, _ in PATTERNS:
            if name.startswith("spec-process"):
                self.assertIsNone(
                    regex.search(line),
                    "Spec AC closure stays exempt with IGNORECASE",
                )


if __name__ == "__main__":
    unittest.main()
