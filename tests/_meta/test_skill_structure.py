"""File-layout invariants: no skill-level README, referenced files exist."""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import get_skill_dirs  # noqa: E402

REF_PATTERN = re.compile(
    r"(?:^|[\s(\[])"                                     # boundary: line start, whitespace, (, [
    r"((?:steps|references|scripts|templates|assets)"    # capture starts at root subdir
    r"(?:/[\w.-]+)+"                                     # one or more path segments (handles nested)
    r"\.[\w]+)"                                          # required extension
)


class TestNoSkillReadme(unittest.TestCase):
    """Per repo-conventions: skill folders never carry their own README.md.
    User docs live in the root README only — subfolders may have a README for
    maintainer-facing notes, but the skill root must not."""

    def test_no_root_readme(self):
        for skill in get_skill_dirs():
            with self.subTest(skill=skill.name):
                self.assertFalse((skill / "README.md").is_file(),
                                 f"{skill.name}/README.md forbidden — root README is canonical")


class TestReferencedFilesExist(unittest.TestCase):
    """Every `steps/<file>`, `references/<file>`, `scripts/<file>`, etc.
    cited in SKILL.md must exist on disk. Catches broken refs introduced by
    rename/delete without a SKILL.md update."""

    def test_refs_resolve(self):
        for skill in get_skill_dirs():
            with self.subTest(skill=skill.name):
                content = (skill / "SKILL.md").read_text(encoding="utf-8")
                # Find every "steps/x.md", "references/sub/y.md", etc. in the body
                for match in REF_PATTERN.finditer(content):
                    rel = match.group(1).rstrip(".,;:)]")
                    target = skill / rel
                    self.assertTrue(target.exists(),
                                    f"{skill.name}: referenced file '{rel}' missing on disk")


class TestRefPatternRegex(unittest.TestCase):
    """Self-tests for REF_PATTERN — covers the cases the production scan must catch
    and the cases it must skip. Without these tests the regex could silently drift."""

    def test_matches_flat_reference(self):
        m = REF_PATTERN.search("Read references/foo.md for context.")
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "references/foo.md")

    def test_matches_nested_reference(self):
        """Nested subdirs (`references/sub/foo.md`) must be caught."""
        m = REF_PATTERN.search("Run scripts/sub/utils.sh now.")
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "scripts/sub/utils.sh")

    def test_skips_inline_code_refs(self):
        """Refs inside inline backticks (`scripts/x.sh`) are deliberately skipped.
        They're often cross-skill mentions (e.g., `its references/x.md`) referring
        to a sibling skill's tree, not a local reference. Catching them produces
        false positives. The boundary class excludes backtick by design."""
        m = REF_PATTERN.search("Use `templates/page.tsx` to start.")
        self.assertIsNone(m)

    def test_skips_unrelated_paths(self):
        """`src/foo.ts` doesn't match — only the named subdirs do."""
        self.assertIsNone(REF_PATTERN.search("Edit src/foo.ts here."))

    def test_skips_url_paths(self):
        """`https://example.com/scripts/x.sh` should NOT match — it's a URL,
        not a relative skill reference. Boundary class excludes /."""
        m = REF_PATTERN.search("https://example.com/scripts/x.sh")
        self.assertIsNone(m)


class TestSubdirContentExpectations(unittest.TestCase):
    def test_scripts_dir_has_at_least_one_file(self):
        """If scripts/ exists, it should not be empty (otherwise drop the dir)."""
        for skill in get_skill_dirs():
            scripts_dir = skill / "scripts"
            if not scripts_dir.is_dir():
                continue
            with self.subTest(skill=skill.name):
                non_pycache = [
                    f for f in scripts_dir.iterdir()
                    if f.name not in {"__pycache__", "__init__.py"}
                ]
                self.assertGreater(len(non_pycache), 0,
                                   f"{skill.name}/scripts/ exists but is empty")

    def test_steps_dir_has_at_least_one_file(self):
        for skill in get_skill_dirs():
            steps_dir = skill / "steps"
            if not steps_dir.is_dir():
                continue
            with self.subTest(skill=skill.name):
                files = list(steps_dir.iterdir())
                self.assertGreater(len(files), 0, f"{skill.name}/steps/ exists but is empty")


if __name__ == "__main__":
    unittest.main()
