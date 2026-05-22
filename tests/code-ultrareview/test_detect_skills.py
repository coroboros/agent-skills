"""Tests for the installed-skill detection + routing in detect_skills.py."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = REPO_ROOT / "skills" / "code-ultrareview" / "scripts"
DETECT_SKILLS = SCRIPTS_DIR / "detect_skills.py"
AGGREGATION = SCRIPTS_DIR / "aggregation.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


detect_skills = _load("detect_skills", DETECT_SKILLS)
aggregation = _load("aggregation", AGGREGATION)


def _make_skill(skills_dir: Path, name: str) -> Path:
    folder = skills_dir / name
    folder.mkdir(parents=True, exist_ok=True)
    skill_md = folder / "SKILL.md"
    skill_md.write_text(f"---\nname: {name}\ndescription: test\n---\n")
    return skill_md


class TestRoutingTableShape(unittest.TestCase):
    def test_every_canonical_lens_has_every_marker_cell(self):
        for lens in detect_skills.CANONICAL_LENSES:
            self.assertIn(lens, detect_skills.ROUTING_TABLE)
            for marker in detect_skills.SEVERITY_MARKERS:
                self.assertIn(marker, detect_skills.ROUTING_TABLE[lens])
                self.assertTrue(detect_skills.ROUTING_TABLE[lens][marker])

    def test_final_fallback_is_apex_in_every_cell(self):
        for lens in detect_skills.CANONICAL_LENSES:
            for marker in detect_skills.SEVERITY_MARKERS:
                candidates = detect_skills.ROUTING_TABLE[lens][marker]
                self.assertEqual(candidates[-1], ("apex", "/apex"))

    def test_canonical_lenses_parity_with_aggregation(self):
        # Drift guard: detect_skills must match aggregation's canonical list.
        self.assertEqual(
            detect_skills.CANONICAL_LENSES, aggregation.CANONICAL_LENSES
        )


class TestDetectInstalledSkills(unittest.TestCase):
    def test_empty_directory_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / ".claude" / "skills").mkdir(parents=True)
            result = detect_skills.detect_installed_skills(home=tmp_path)
            self.assertEqual(result, {})

    def test_detects_global_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            skills_dir = tmp_path / ".claude" / "skills"
            skills_dir.mkdir(parents=True)
            _make_skill(skills_dir, "apex")
            _make_skill(skills_dir, "oneshot")
            result = detect_skills.detect_installed_skills(home=tmp_path)
            self.assertIn("apex", result)
            self.assertIn("oneshot", result)

    def test_skips_dirs_without_skill_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            skills_dir = tmp_path / ".claude" / "skills"
            skills_dir.mkdir(parents=True)
            (skills_dir / "not-a-skill").mkdir()
            _make_skill(skills_dir, "apex")
            result = detect_skills.detect_installed_skills(home=tmp_path)
            self.assertIn("apex", result)
            self.assertNotIn("not-a-skill", result)

    def test_skips_hidden_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            skills_dir = tmp_path / ".claude" / "skills"
            skills_dir.mkdir(parents=True)
            _make_skill(skills_dir, ".hidden")  # creates .hidden/SKILL.md
            _make_skill(skills_dir, "apex")
            result = detect_skills.detect_installed_skills(home=tmp_path)
            self.assertIn("apex", result)
            self.assertNotIn(".hidden", result)

    def test_project_skill_shadows_global(self):
        with tempfile.TemporaryDirectory() as home_tmp, \
             tempfile.TemporaryDirectory() as project_tmp:
            home_path = Path(home_tmp)
            project_path = Path(project_tmp)
            global_skills = home_path / ".claude" / "skills"
            global_skills.mkdir(parents=True)
            project_skills = project_path / ".claude" / "skills"
            project_skills.mkdir(parents=True)
            global_apex = _make_skill(global_skills, "apex")
            project_apex = _make_skill(project_skills, "apex")
            result = detect_skills.detect_installed_skills(
                home=home_path, project_root=project_path
            )
            self.assertEqual(result["apex"], project_apex)
            self.assertNotEqual(result["apex"], global_apex)

    def test_missing_directories_dont_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            # No .claude/skills/ subdir created.
            result = detect_skills.detect_installed_skills(home=Path(tmp))
            self.assertEqual(result, {})


class TestRouteCluster(unittest.TestCase):
    def test_uses_first_installed_candidate(self):
        installed = {"humanize-en": Path("/x"), "apex": Path("/y")}
        result = detect_skills.route_cluster("docs-version", "🟠", installed)
        self.assertEqual(result["command"], "/humanize-en")
        self.assertFalse(result["fallback_used"])

    def test_falls_back_when_first_candidate_missing(self):
        installed = {"apex": Path("/y")}
        result = detect_skills.route_cluster("docs-version", "🟠", installed)
        self.assertEqual(result["command"], "/apex")
        self.assertTrue(result["fallback_used"])

    def test_emits_apex_command_even_when_apex_missing(self):
        # Anomalous case: no /apex installed. Should still emit /apex string
        # with fallback_used=True so the report stays actionable.
        installed = {}
        result = detect_skills.route_cluster("rules", "🔴", installed)
        self.assertEqual(result["command"], "/apex")
        self.assertTrue(result["fallback_used"])

    def test_docs_version_green_routes_through_fix_grammar(self):
        installed = {"fix-grammar": Path("/x"), "apex": Path("/y")}
        result = detect_skills.route_cluster("docs-version", "🟢", installed)
        self.assertEqual(result["command"], "/fix-grammar")
        self.assertFalse(result["fallback_used"])

    def test_unknown_lens_raises(self):
        with self.assertRaises(KeyError):
            detect_skills.route_cluster("not-a-lens", "🔴", {})

    def test_unknown_marker_raises(self):
        with self.assertRaises(KeyError):
            detect_skills.route_cluster("rules", "💜", {})

    def test_skill_name_in_result(self):
        installed = {"apex": Path("/x")}
        result = detect_skills.route_cluster("rules", "🔴", installed)
        self.assertEqual(result["skill"], "apex")


class TestRoutingTableCoverage(unittest.TestCase):
    def test_coverage_for_each_marker_every_lens(self):
        # 6 lenses × 3 markers = 18 cells routed in this test.
        installed = {"apex": Path("/x")}
        for lens in detect_skills.CANONICAL_LENSES:
            for marker in detect_skills.SEVERITY_MARKERS:
                result = detect_skills.route_cluster(lens, marker, installed)
                self.assertEqual(result["command"], "/apex")
                self.assertEqual(result["lens"], lens)
                self.assertEqual(result["marker"], marker)


class TestCLI(unittest.TestCase):
    def test_json_output_is_valid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            skills_dir = tmp_path / ".claude" / "skills"
            skills_dir.mkdir(parents=True)
            _make_skill(skills_dir, "apex")

            # Run with HOME override so the CLI scans the temp dir.
            env_override = {"HOME": tmp, "PATH": "/usr/bin:/bin"}
            result = subprocess.run(
                [sys.executable, str(DETECT_SKILLS), "--json"],
                capture_output=True, text=True, env=env_override, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertIn("apex", payload)


if __name__ == "__main__":
    unittest.main()
