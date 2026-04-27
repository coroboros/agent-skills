"""File-layout invariants: no skill-level README, referenced files exist."""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import get_skill_dirs  # noqa: E402

REF_PATTERN = re.compile(r"(?:^|[\s(\[])(?:steps|references|scripts|templates|assets)/([\w./-]+\.[\w]+)")


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
                # Find every "steps/x.md", "references/y.md", etc. mentioned in the body
                for match in REF_PATTERN.finditer(content):
                    full_match = match.group(0).strip()
                    # Reconstruct the relative path: "steps/x.md"
                    # match.group(0) may include leading whitespace; normalise
                    rel_path = re.search(r"(steps|references|scripts|templates|assets)/[\w./-]+\.[\w]+", full_match)
                    if not rel_path:
                        continue
                    rel = rel_path.group(0)
                    # Strip trailing punctuation that's likely prose, not filename
                    rel = rel.rstrip(".,;:)]")
                    target = skill / rel
                    self.assertTrue(target.exists(),
                                    f"{skill.name}: referenced file '{rel}' missing on disk")


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
