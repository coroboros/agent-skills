"""Pin the public API of `tests/_meta/_helpers.py`.

`_helpers.py` is imported by every cross-skill `_meta/test_*.py` module
and (via sys.path manipulation) by per-skill tests that share its
utilities. Its function signatures and return shapes are an internal
contract — silent drift here cascades failures across the suite or,
worse, makes tests pass against unintended fixtures.

This module pins:
  - The set of exported public functions (no surprise additions, no
    silent removals).
  - Each function's return type and a minimal shape contract.

When a function genuinely needs to evolve, update this test in the same
PR — that documents the change explicitly.
"""

import inspect
import sys
import unittest
from pathlib import Path

# `_helpers` lives next to this file; sibling-import requires _meta on sys.path.
sys.path.insert(0, str(Path(__file__).parent))

import _helpers  # noqa: E402
from _helpers import REPO_ROOT, SKILLS_DIR, get_skill_dirs, load_frontmatter  # noqa: E402


EXPECTED_PUBLIC_API = {"get_skill_dirs", "load_frontmatter"}
EXPECTED_PUBLIC_CONSTANTS = {"REPO_ROOT", "SKILLS_DIR"}


class TestPublicApi(unittest.TestCase):
    """The set of public callables and constants. Adding to this set is
    intentional — drop or rename triggers a contract update."""

    def test_no_unexpected_public_callables(self):
        public_callables = {
            name for name in dir(_helpers)
            if not name.startswith("_") and callable(getattr(_helpers, name))
            and inspect.getmodule(getattr(_helpers, name)) is _helpers
        }
        unexpected = public_callables - EXPECTED_PUBLIC_API
        missing = EXPECTED_PUBLIC_API - public_callables
        self.assertEqual(
            unexpected, set(),
            f"unexpected public callables in _helpers.py: {unexpected}. "
            "Add to EXPECTED_PUBLIC_API if intentional.",
        )
        self.assertEqual(
            missing, set(),
            f"missing public callables in _helpers.py: {missing}",
        )

    def test_expected_constants_present(self):
        for name in EXPECTED_PUBLIC_CONSTANTS:
            with self.subTest(name=name):
                self.assertTrue(
                    hasattr(_helpers, name),
                    f"_helpers.py missing constant {name}",
                )


class TestRepoRootIsAValidPath(unittest.TestCase):
    """REPO_ROOT must point to the actual repo root (where SKILLS_DIR is)."""

    def test_repo_root_is_a_directory(self):
        self.assertTrue(REPO_ROOT.is_dir(), f"REPO_ROOT not a directory: {REPO_ROOT}")

    def test_skills_dir_is_under_repo_root(self):
        self.assertTrue(SKILLS_DIR.is_dir(), f"SKILLS_DIR not a directory: {SKILLS_DIR}")
        self.assertEqual(
            SKILLS_DIR.parent, REPO_ROOT,
            "SKILLS_DIR must live directly under REPO_ROOT",
        )

    def test_repo_root_contains_marker_files(self):
        """The repo root has README.md + a marketplace manifest — sanity check
        that REPO_ROOT isn't pointing somewhere unexpected."""
        self.assertTrue((REPO_ROOT / "README.md").is_file(),
                        "REPO_ROOT does not contain README.md")
        self.assertTrue((REPO_ROOT / ".claude-plugin" / "marketplace.json").is_file(),
                        "REPO_ROOT does not contain .claude-plugin/marketplace.json")


class TestGetSkillDirsContract(unittest.TestCase):
    """Returns a sorted list of `Path` objects, each pointing to a skill
    folder under SKILLS_DIR. No hidden directories, no files."""

    def test_returns_a_list(self):
        result = get_skill_dirs()
        self.assertIsInstance(result, list)

    def test_each_entry_is_a_directory(self):
        for entry in get_skill_dirs():
            with self.subTest(entry=entry):
                self.assertIsInstance(entry, Path)
                self.assertTrue(entry.is_dir(), f"not a directory: {entry}")

    def test_no_hidden_dirs_returned(self):
        for entry in get_skill_dirs():
            with self.subTest(entry=entry):
                self.assertFalse(
                    entry.name.startswith("."),
                    f"hidden directory leaked into get_skill_dirs(): {entry}",
                )

    def test_result_is_sorted(self):
        result = get_skill_dirs()
        names = [d.name for d in result]
        self.assertEqual(
            names, sorted(names),
            "get_skill_dirs() must return entries sorted by name",
        )

    def test_returns_at_least_the_known_skills(self):
        """Sanity check — known skills are present. Catches accidental
        path-resolution bugs that return an empty list."""
        names = {d.name for d in get_skill_dirs()}
        # A representative sample — adding to this set is intentional.
        for known in ("brand-voice", "humanize-en", "spec", "apex"):
            with self.subTest(known=known):
                self.assertIn(
                    known, names,
                    f"known skill `{known}` not returned — possible path bug",
                )


class TestLoadFrontmatterContract(unittest.TestCase):
    """Returns `(frontmatter_dict, body_str)` from a skill's SKILL.md. The
    frontmatter dict must include `name` and `description` for any valid
    skill (those are spec-required)."""

    def setUp(self):
        # Pick a known-valid skill to exercise the contract.
        self.skill = SKILLS_DIR / "brand-voice"

    def test_returns_tuple_of_two(self):
        result = load_frontmatter(self.skill)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2,
                         "load_frontmatter must return (fm, body) — exactly 2 elements")

    def test_fm_is_dict_body_is_str(self):
        fm, body = load_frontmatter(self.skill)
        self.assertIsInstance(fm, dict)
        self.assertIsInstance(body, str)

    def test_required_keys_in_fm(self):
        fm, _ = load_frontmatter(self.skill)
        for key in ("name", "description"):
            with self.subTest(key=key):
                self.assertIn(key, fm,
                              f"frontmatter missing required key: {key}")

    def test_body_non_empty_for_valid_skill(self):
        _, body = load_frontmatter(self.skill)
        self.assertGreater(len(body.strip()), 100,
                           "body should be substantive for a real skill")


if __name__ == "__main__":
    unittest.main()
