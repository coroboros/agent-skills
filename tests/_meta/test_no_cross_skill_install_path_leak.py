"""CI gate against bare cross-skill repo paths in shipped skill source.

Each skill in `skills/<name>/` is installable standalone via
`npx skills add coroboros/agent-skills --skill <name>`. When that
happens, only the chosen skill folder lands at the user's
`~/.claude/skills/<name>/` — sibling skills are NOT present.

A reference inside the skill source to `skills/<other>/...` is a
dead link on partial install AND a wrong path on full install (the
install location is `~/.claude/skills/<other>/`, not
`skills/<other>/`). The bulletproof three-layer pattern replaces
every bare path:

  - Documentation citation → `https://github.com/coroboros/agent-skills/blob/main/skills/<other>/...`
    + sibling skill by name (`/<other>`).
  - Runtime dispatch → slash command `/<other>` for skill invocation;
    triple-fallback for direct script:
    `${CLAUDE_SKILL_DIR}/../<other>/...` → `~/.claude/skills/<other>/...`
    → `~/.agents/skills/<other>/...` → fail-loud with install hint.
  - Parity contract → GitHub URL + the phrase "parity counterpart" +
    "both files must change together".

Anthropic's canonical guidance documents only the by-name reference
(`coroboros/archivist/docs/insights/skills-how-anthropic-uses-skills.md:217`,
Composing Skills). GitHub URLs + triple-fallback are this repo's
extension for the gaps the doc leaves open.

Background: this gate is the second member of the "shipped-skill
cleanliness" family. The first member is `test_no_internal_label_leak.py`.
See `~/.claude/output/agent-skills/postmortems/internal-label-enforcement-gap.md`
for the full family analysis.
"""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import REPO_ROOT, SKILLS_DIR  # noqa: E402

_SCAN_EXTENSIONS = (".md", ".py", ".sh", ".bash", ".json")

# Files that legitimately document the install-context pattern with
# literal `skills/<other>/...` examples. Surface as informational
# rather than as findings.
_ALLOWLIST_PATHS = (
    # Forge owns the spec format and references the cross-skill pattern.
    "skills/forge",
    # Apex steps teach the workflow rules with literal examples.
    "skills/apex/steps",
    # The code-ultrareview Documentation axis brief catalogues the
    # pattern as table cells.
    "skills/code-ultrareview/references/axes/documentation.md",
)

# Patterns that, when they end the substring immediately preceding a
# `skills/<name>/` match, mark the occurrence as properly bulletproof.
# Each pattern is anchored at the end of the prefix (`$` in the regex).
_ALLOWED_PREFIX_REGEXES = tuple(
    re.compile(p)
    for p in (
        r"~/\.claude/$",
        r"~/\.agents/$",
        r"\.claude/$",
        r"\$\{CLAUDE_SKILL_DIR\}/$",
        r"\$\{HOME\}/\.claude/$",
        r"\$\{HOME\}/\.agents/$",
        # GitHub URL with any ref segment (`main`, a commit SHA, a branch).
        r"github\.com/coroboros/agent-skills/blob/[^/\s]+/$",
        # apex's derivation-lens runtime fallback uses
        # `$(git rev-parse --show-toplevel)/skills/<other>/...`.
        r"rev-parse --show-toplevel\)/$",
    )
)

# Per-line opt-out marker. Both `#`-style (Python / shell / JSON-less
# comments) and `<!--`-style (Markdown) are recognised.
_INLINE_OPT_OUT = re.compile(r"(?:#|<!--)\s*noqa:\s*cross-skill-path\b")


def _enumerate_skill_names() -> tuple[str, ...]:
    """Read actual skill names from `skills/*/SKILL.md`.

    Dynamic enumeration: new skills are auto-protected without a
    regex update.
    """
    names: list[str] = []
    for path in sorted(SKILLS_DIR.iterdir()):
        if not path.is_dir():
            continue
        if (path / "SKILL.md").exists():
            names.append(path.name)
    return tuple(names)


def _build_pattern(skill_names: tuple[str, ...]) -> re.Pattern[str]:
    """Build the skill-name-aware `skills/<actual-skill>/` regex.

    Skill-name-aware (rather than `[a-z][a-z0-9-]+/`) avoids false
    positives on generic enumerations like `skills/app/library/docs/...`
    — `app`/`library`/etc. are not skill names.
    """
    if not skill_names:
        return re.compile(r"(?!)")
    alternation = "|".join(re.escape(name) for name in skill_names)
    return re.compile(rf"\bskills/({alternation})/")


def _is_allowed_prefix(prefix: str) -> bool:
    return any(rx.search(prefix) for rx in _ALLOWED_PREFIX_REGEXES)


def _is_allowlisted_path(rel_path: str) -> bool:
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
        if any(part.startswith("__") and part.endswith("__") for part in path.parts):
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        if _is_allowlisted_path(rel):
            continue
        out.append(path)
    return sorted(out)


def _scan_text(text: str, pattern: re.Pattern[str]) -> list[tuple[int, str]]:
    """Return (lineno, matched_text) for each unallowlisted hit."""
    hits: list[tuple[int, str]] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if _INLINE_OPT_OUT.search(line):
            continue
        for match in pattern.finditer(line):
            prefix = line[: match.start()]
            if _is_allowed_prefix(prefix):
                continue
            hits.append((lineno, match.group(0)))
            break
    return hits


def _scan_file(path: Path, pattern: re.Pattern[str]) -> list[tuple[int, str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    return _scan_text(text, pattern)


_HINT = (
    "Cross-skill reference uses a bare repo path. On partial install "
    "via `npx skills add ... --skill <name>`, the sibling skill is "
    "not present at this path. Use the bulletproof pattern:\n"
    "  - Citation → "
    "https://github.com/coroboros/agent-skills/blob/main/skills/<other>/...\n"
    "  - Runtime dispatch → slash command `/<other>`, or triple-fallback "
    "(`${CLAUDE_SKILL_DIR}/../<other>/...` → "
    "`~/.claude/skills/<other>/...` → `~/.agents/skills/<other>/...`).\n"
    "  - Parity contract → GitHub URL + \"parity counterpart\".\n"
    "Per-line opt-out: append `# noqa: cross-skill-path` "
    "(`<!-- noqa: cross-skill-path -->` in Markdown)."
)


class TestNoCrossSkillInstallPathLeak(unittest.TestCase):
    """Block bare cross-skill repo paths from shipped skill source."""

    def setUp(self):
        self.skill_names = _enumerate_skill_names()
        self.pattern = _build_pattern(self.skill_names)

    def test_skill_enumeration_is_non_empty(self):
        self.assertGreater(
            len(self.skill_names),
            0,
            "Expected at least one skill with SKILL.md under skills/.",
        )

    def test_no_bare_cross_skill_path_in_shipped_surface(self):
        violations: list[str] = []
        for path in _iter_scannable_files():
            rel = path.relative_to(REPO_ROOT).as_posix()
            for lineno, matched in _scan_file(path, self.pattern):
                violations.append(
                    f"{rel}:{lineno} — bare cross-skill path: {matched!r}"
                )
        if violations:
            joined = "\n".join(violations)
            self.fail(
                f"Cross-skill install-path leak in shipped skill source "
                f"({len(violations)} violation(s)):\n\n{joined}\n\n{_HINT}\n\n"
                f"Allowlist whole files only when they legitimately document "
                f"the pattern with literal examples. Append paths to "
                f"`_ALLOWLIST_PATHS` in this test."
            )

    def test_allowlist_paths_actually_exist(self):
        for entry in _ALLOWLIST_PATHS:
            path = REPO_ROOT / entry
            self.assertTrue(
                path.exists(),
                f"Allowlist entry does not exist on disk: {entry}",
            )

    def test_inline_opt_out_marker_is_recognised(self):
        self.assertTrue(_INLINE_OPT_OUT.search(
            "see skills/code-ultrareview/scripts/x.py  # noqa: cross-skill-path"
        ))
        self.assertTrue(_INLINE_OPT_OUT.search(
            "see `skills/code-ultrareview/scripts/x.py`  <!-- noqa: cross-skill-path -->"
        ))

    def test_positive_sample_fires(self):
        """A bare `skills/<other>/...` reference must be flagged."""
        pattern = _build_pattern(("agent-creator", "apex", "code-ultrareview"))
        line = "See skills/code-ultrareview/references/axes/intent.md for the taxonomy."
        match = pattern.search(line)
        self.assertIsNotNone(match)
        assert match is not None
        prefix = line[: match.start()]
        self.assertFalse(_is_allowed_prefix(prefix))

    def test_github_url_prefix_is_allowed(self):
        pattern = _build_pattern(("agent-creator", "apex", "code-ultrareview"))
        line = (
            "See https://github.com/coroboros/agent-skills/blob/main/"
            "skills/code-ultrareview/references/axes/intent.md."
        )
        matches = list(pattern.finditer(line))
        self.assertEqual(len(matches), 1)
        prefix = line[: matches[0].start()]
        self.assertTrue(_is_allowed_prefix(prefix))

    def test_github_url_with_markdown_link_text_is_allowed(self):
        """A line where the URL also appears as Markdown link text must pass.

        The text portion of `[github.com/.../blob/main/skills/<x>/...](https://...)`
        carries the same `skills/<x>/` substring, prefixed by
        `github.com/coroboros/agent-skills/blob/main/`.
        """
        pattern = _build_pattern(("code-ultrareview",))
        line = (
            "see [github.com/coroboros/agent-skills/blob/main/"
            "skills/code-ultrareview/references/axes/intent.md]"
            "(https://github.com/coroboros/agent-skills/blob/main/"
            "skills/code-ultrareview/references/axes/intent.md)"
        )
        matches = list(pattern.finditer(line))
        self.assertEqual(len(matches), 2)
        for m in matches:
            prefix = line[: m.start()]
            self.assertTrue(
                _is_allowed_prefix(prefix),
                f"Expected allowed prefix before match at col {m.start()}",
            )

    def test_install_path_prefix_is_allowed(self):
        pattern = _build_pattern(("agent-creator", "apex", "code-ultrareview"))
        line = "lives at ~/.claude/skills/code-ultrareview/references/axes/intent.md"
        matches = list(pattern.finditer(line))
        self.assertEqual(len(matches), 1)
        prefix = line[: matches[0].start()]
        self.assertTrue(_is_allowed_prefix(prefix))

    def test_dotclaude_skills_prefix_is_allowed(self):
        """`.claude/skills/<other>/` (project-local install) must pass."""
        pattern = _build_pattern(("award-design", "design-system"))
        line = (
            "  2. `.claude/skills/award-design/references/anti-patterns.md` "
            "(project-local install)"
        )
        matches = list(pattern.finditer(line))
        self.assertEqual(len(matches), 1)
        prefix = line[: matches[0].start()]
        self.assertTrue(_is_allowed_prefix(prefix))

    def test_repo_toplevel_fallback_prefix_is_allowed(self):
        pattern = _build_pattern(("code-ultrareview", "apex"))
        line = (
            'elif [ -f "$(git rev-parse --show-toplevel)/'
            'skills/code-ultrareview/scripts/derivation/run.py" ]; then'
        )
        matches = list(pattern.finditer(line))
        self.assertEqual(len(matches), 1)
        prefix = line[: matches[0].start()]
        self.assertTrue(_is_allowed_prefix(prefix))

    def test_repo_kind_string_is_not_a_violation(self):
        """A `repo_kind` enumeration like `skills/app/library/...` must NOT flag.

        Skill-name-aware regex excludes generic words because they
        are not real skill names.
        """
        pattern = _build_pattern(("agent-creator", "apex", "code-ultrareview"))
        line = "repo-kind classification (skills/app/library/docs/monorepo/python/rust/go/unknown)"
        matches = list(pattern.finditer(line))
        self.assertEqual(
            len(matches), 0, "Generic words shouldn't match the skill-name-aware regex"
        )

    def test_inline_opt_out_suppresses_a_real_match(self):
        """End-to-end: a matching line with the noqa marker is exempt."""
        text = (
            "see skills/code-ultrareview/scripts/x.py  # noqa: cross-skill-path\n"
        )
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(text)
            fpath = Path(f.name)
        try:
            pattern = _build_pattern(("code-ultrareview",))
            hits = _scan_file(fpath, pattern)
            self.assertEqual(hits, [], "noqa marker should suppress the hit")
        finally:
            fpath.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
