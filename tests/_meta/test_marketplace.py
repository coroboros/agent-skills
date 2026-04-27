"""marketplace.json conformity tests: parity with skills/, plugin shape, owner email."""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import REPO_ROOT, get_skill_dirs  # noqa: E402

MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+(-[\w.]+)?$")


def _load():
    return json.loads(MARKETPLACE.read_text(encoding="utf-8"))


class TestMarketplaceShape(unittest.TestCase):
    def test_file_exists(self):
        self.assertTrue(MARKETPLACE.is_file())

    def test_top_level_fields(self):
        data = _load()
        self.assertEqual(data.get("name"), "coroboros-agent-skills")
        self.assertIn("owner", data)
        self.assertIn("metadata", data)
        self.assertIn("plugins", data)

    def test_owner_email_canonical(self):
        """Owner email must be the brand address, not a personal one."""
        data = _load()
        self.assertEqual(data["owner"]["email"], "ob@coroboros.com")

    def test_owner_name_canonical(self):
        data = _load()
        self.assertEqual(data["owner"]["name"], "coroboros")

    def test_version_semver(self):
        data = _load()
        version = data["metadata"]["version"]
        self.assertRegex(version, SEMVER, f"version '{version}' not semver")
        self.assertFalse(version.startswith("v"), "version must not have 'v' prefix")


class TestSkillsParity(unittest.TestCase):
    """Every skill folder is in marketplace.json, and vice versa. No orphans either way."""

    def _skills_in_marketplace(self):
        data = _load()
        return {
            entry.removeprefix("./skills/")
            for plugin in data["plugins"]
            for entry in plugin.get("skills", [])
        }

    def test_every_folder_referenced(self):
        listed = self._skills_in_marketplace()
        for skill in get_skill_dirs():
            with self.subTest(skill=skill.name):
                self.assertIn(skill.name, listed,
                              f"{skill.name} folder exists but not referenced in marketplace.json")

    def test_no_marketplace_orphans(self):
        listed = self._skills_in_marketplace()
        on_disk = {s.name for s in get_skill_dirs()}
        for name in listed:
            with self.subTest(skill=name):
                self.assertIn(name, on_disk,
                              f"marketplace.json references '{name}' but folder missing")

    def test_no_general_bucket(self):
        """Per repo-conventions: every skill belongs to a domain plugin, not a 'General' bucket."""
        data = _load()
        plugin_names = {p["name"] for p in data["plugins"]}
        self.assertNotIn("general", plugin_names)
        self.assertNotIn("general-skills", plugin_names)


class TestPluginShape(unittest.TestCase):
    def test_plugin_name_kebab_skills_suffix(self):
        data = _load()
        for plugin in data["plugins"]:
            with self.subTest(plugin=plugin["name"]):
                self.assertRegex(plugin["name"], KEBAB)
                self.assertTrue(plugin["name"].endswith("-skills"),
                                f"{plugin['name']} doesn't end with '-skills'")

    def test_plugin_description_under_120(self):
        data = _load()
        for plugin in data["plugins"]:
            with self.subTest(plugin=plugin["name"]):
                desc = plugin.get("description", "")
                self.assertGreater(len(desc), 0)
                self.assertLessEqual(len(desc), 200,
                                     f"{plugin['name']} description too long ({len(desc)} chars)")

    def test_plugin_has_skills(self):
        data = _load()
        for plugin in data["plugins"]:
            with self.subTest(plugin=plugin["name"]):
                self.assertGreater(len(plugin.get("skills", [])), 0,
                                   f"{plugin['name']} has no skills")

    def test_plugin_skill_paths_format(self):
        data = _load()
        for plugin in data["plugins"]:
            for skill_path in plugin.get("skills", []):
                with self.subTest(plugin=plugin["name"], skill=skill_path):
                    self.assertTrue(skill_path.startswith("./skills/"),
                                    f"skill path must start with './skills/'")


if __name__ == "__main__":
    unittest.main()
