"""Cross-skill frontmatter conformity tests.

Iterate over every skills/<name>/ directory and validate the frontmatter against
the Agent Skills spec + repo-specific conventions. One failure per skill via subTest
so all violations surface in a single run.
"""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import get_skill_dirs, load_frontmatter  # noqa: E402

KEBAB_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
CANONICAL_COMPATIBILITY = (
    "Claude Code CLI (per Agent Skills spec). Graceful degradation in "
    "other environments supporting the open standard."
)
RESERVED_NAME_EXCEPTIONS = {"claude-md"}


class TestEverySkillHasSkillMd(unittest.TestCase):
    def test_skill_md_exists(self):
        for skill in get_skill_dirs():
            with self.subTest(skill=skill.name):
                self.assertTrue((skill / "SKILL.md").is_file(),
                                f"{skill.name}/SKILL.md missing")


class TestNameField(unittest.TestCase):
    def test_name_matches_folder(self):
        for skill in get_skill_dirs():
            with self.subTest(skill=skill.name):
                fm, _ = load_frontmatter(skill)
                self.assertEqual(fm.get("name"), skill.name,
                                 f"frontmatter name '{fm.get('name')}' != folder '{skill.name}'")

    def test_name_kebab_case_max_64(self):
        for skill in get_skill_dirs():
            with self.subTest(skill=skill.name):
                fm, _ = load_frontmatter(skill)
                name = fm.get("name", "")
                self.assertRegex(name, KEBAB_NAME, f"{skill.name}: name not kebab-case")
                self.assertLessEqual(len(name), 64)
                self.assertFalse(name.startswith("-") or name.endswith("-"),
                                 "name has leading/trailing hyphen")
                self.assertNotIn("--", name, "name contains '--'")

    def test_no_reserved_substrings(self):
        for skill in get_skill_dirs():
            if skill.name in RESERVED_NAME_EXCEPTIONS:
                continue
            with self.subTest(skill=skill.name):
                self.assertNotIn("anthropic", skill.name)
                self.assertNotIn("claude", skill.name)


class TestDescriptionField(unittest.TestCase):
    def test_description_present_and_bounded(self):
        for skill in get_skill_dirs():
            with self.subTest(skill=skill.name):
                fm, _ = load_frontmatter(skill)
                desc = fm.get("description", "")
                self.assertGreater(len(desc), 0, "description empty")
                self.assertLessEqual(len(desc), 1024,
                                     "description > 1024 chars (open-standard cap)")

    def test_combined_with_when_to_use_under_1536(self):
        """Claude Code combines description + when_to_use in the listing — total cap ~1536."""
        for skill in get_skill_dirs():
            with self.subTest(skill=skill.name):
                fm, _ = load_frontmatter(skill)
                combined = (fm.get("description", "") or "") + " " + (fm.get("when_to_use", "") or "")
                self.assertLessEqual(len(combined), 1536)


class TestMetadataField(unittest.TestCase):
    def test_metadata_author_is_coroboros(self):
        for skill in get_skill_dirs():
            with self.subTest(skill=skill.name):
                fm, _ = load_frontmatter(skill)
                meta = fm.get("metadata") or {}
                self.assertEqual(meta.get("author"), "coroboros",
                                 f"{skill.name}: metadata.author != 'coroboros' (got {meta.get('author')!r})")

    def test_no_metadata_version(self):
        """Per repo policy, skills are co-versioned via marketplace.json — never per-skill."""
        for skill in get_skill_dirs():
            with self.subTest(skill=skill.name):
                fm, _ = load_frontmatter(skill)
                meta = fm.get("metadata") or {}
                self.assertNotIn("version", meta,
                                 f"{skill.name}: metadata.version forbidden by repo policy")


class TestCompatibilityField(unittest.TestCase):
    def test_compatibility_canonical_text(self):
        for skill in get_skill_dirs():
            with self.subTest(skill=skill.name):
                fm, _ = load_frontmatter(skill)
                compat = fm.get("compatibility", "")
                self.assertEqual(compat, CANONICAL_COMPATIBILITY,
                                 f"{skill.name}: non-canonical compatibility text")


class TestModelEnum(unittest.TestCase):
    """If `model:` is declared, it must be one of haiku|sonnet|opus per Claude Code
    convention. Free-form strings (or typos like 'sonett') silently ignored at runtime —
    this test pins the enum so a typo surfaces in CI, not in production session start."""

    ALLOWED_MODELS = {"haiku", "sonnet", "opus"}

    def test_model_in_allowed_set(self):
        for skill in get_skill_dirs():
            with self.subTest(skill=skill.name):
                fm, _ = load_frontmatter(skill)
                model = fm.get("model")
                if model is None:
                    continue  # model is optional
                self.assertIn(model, self.ALLOWED_MODELS,
                              f"{skill.name}: model='{model}' not in {self.ALLOWED_MODELS}")


class TestNoXMLMarkupInFrontmatter(unittest.TestCase):
    """The spec forbids XML markup in frontmatter (e.g., `<workflow>...</workflow>`).
    Angle brackets inside argument-hint placeholders (`<file-path>`) are conventional
    and not XML markup — only closing tags (`</word>`) and self-closing (`<word/>`)
    unambiguously indicate XML, so that's what we forbid."""

    XML_TAG = re.compile(r"</[A-Za-z][A-Za-z0-9_-]*>|<[A-Za-z][A-Za-z0-9_-]*/>")

    def test_no_xml_tags(self):
        for skill in get_skill_dirs():
            with self.subTest(skill=skill.name):
                content = (skill / "SKILL.md").read_text(encoding="utf-8")
                if not content.startswith("---\n"):
                    continue
                end = content.find("\n---\n", 4)
                if end < 0:
                    continue
                fm_block = content[4:end]
                match = self.XML_TAG.search(fm_block)
                self.assertIsNone(match,
                                  f"{skill.name}: XML tag '{match.group(0) if match else ''}' in frontmatter")


if __name__ == "__main__":
    unittest.main()
