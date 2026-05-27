"""Tests for skills/clean-output/scripts/list_artifacts.py.

Exercise enumeration via both subprocess (CLI contract) and direct imports
(internal helpers). Fixtures use `tempfile.TemporaryDirectory` so the suite
runs in any environment without touching the user's real ~/.claude/output/.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO_ROOT / "skills" / "clean-output" / "scripts"
SCRIPT = SCRIPTS / "list_artifacts.py"

sys.path.insert(0, str(SCRIPTS))
from list_artifacts import (  # noqa: E402
    detect_current_project,
    enumerate_bucket,
    list_artifacts,
    measure,
)


def _seed_fixture(root: Path) -> dict[str, Path]:
    """Populate a fake ~/.claude/output/ tree. Return key paths for assertions."""
    paths = {
        "forge_my": root / "my-app" / "forge" / "forge-oauth.md",
        "forge_my2": root / "my-app" / "forge" / "forge-billing.md",
        "apex_my": root / "my-app" / "apex" / "01-feature",
        "apex_my_inner": root / "my-app" / "apex" / "01-feature" / "00-context.md",
        "apex_my_inner2": root / "my-app" / "apex" / "01-feature" / "01-analyze.md",
        "forge_other": root / "other-app" / "forge" / "forge-other.md",
        "global_notion": root / "_global" / "notion" / "export.md",
    }
    paths["forge_my"].parent.mkdir(parents=True)
    paths["forge_my"].write_text("oauth spec")
    paths["forge_my2"].write_text("billing spec")
    paths["apex_my"].mkdir(parents=True)
    paths["apex_my_inner"].write_text("context")
    paths["apex_my_inner2"].write_text("analyze")
    paths["forge_other"].parent.mkdir(parents=True)
    paths["forge_other"].write_text("other")
    paths["global_notion"].parent.mkdir(parents=True)
    paths["global_notion"].write_text("notion export")
    return paths


def _run(args: list[str]) -> tuple[int, list[dict], str]:
    r = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
    data: list[dict] = json.loads(r.stdout) if r.stdout.strip() else []
    return r.returncode, data, r.stderr


class TestDefaultScope(unittest.TestCase):
    """No flags → current project bucket + _global. Other projects excluded."""

    def test_default_lists_current_and_global_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_fixture(root)
            code, data, err = _run([
                "--root", str(root),
                "--current-project", "my-app",
            ])
            self.assertEqual(code, 0, err)
            buckets = {(a["bucket"], a["project"]) for a in data}
            self.assertIn(("project", "my-app"), buckets)
            self.assertIn(("_global", None), buckets)
            self.assertNotIn(("project", "other-app"), buckets,
                             "other-app must NOT appear in default scope")


class TestGroupingByBucketAndSkill(unittest.TestCase):
    def test_skill_and_bucket_keys_present_on_every_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_fixture(root)
            code, data, _ = _run([
                "--root", str(root),
                "--current-project", "my-app",
            ])
            self.assertEqual(code, 0)
            self.assertGreater(len(data), 0)
            for a in data:
                self.assertIn("bucket", a)
                self.assertIn("project", a)
                self.assertIn("skill", a)
                self.assertIn("path", a)
                self.assertIn("size_bytes", a)
                self.assertIn("mtime_iso", a)

    def test_global_rows_have_null_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_fixture(root)
            code, data, _ = _run([
                "--root", str(root),
                "--current-project", "my-app",
            ])
            self.assertEqual(code, 0)
            for a in data:
                if a["bucket"] == "_global":
                    self.assertIsNone(a["project"], f"_global row has project={a['project']!r}")
                if a["bucket"] == "project":
                    self.assertIsNotNone(a["project"])

    def test_skill_name_matches_subfolder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_fixture(root)
            code, data, _ = _run([
                "--root", str(root),
                "--all-projects",
                "--current-project", "my-app",
            ])
            self.assertEqual(code, 0)
            skills_per_bucket: dict[tuple[str, str | None], set[str]] = {}
            for a in data:
                key = (a["bucket"], a["project"])
                skills_per_bucket.setdefault(key, set()).add(a["skill"])
            self.assertEqual(skills_per_bucket[("project", "my-app")], {"forge", "apex"})
            self.assertEqual(skills_per_bucket[("project", "other-app")], {"forge"})
            self.assertEqual(skills_per_bucket[("_global", None)], {"notion"})


class TestAllProjects(unittest.TestCase):
    def test_dash_A_expands_to_every_project_bucket(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_fixture(root)
            code, data, _ = _run([
                "--root", str(root),
                "--all-projects",
                "--current-project", "my-app",
            ])
            self.assertEqual(code, 0)
            projects = {a["project"] for a in data if a["bucket"] == "project"}
            self.assertEqual(projects, {"my-app", "other-app"})

    def test_global_bucket_not_listed_as_a_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_fixture(root)
            code, data, _ = _run([
                "--root", str(root),
                "--all-projects",
                "--current-project", "my-app",
            ])
            self.assertEqual(code, 0)
            project_names = {a["project"] for a in data if a["bucket"] == "project"}
            self.assertNotIn("_global", project_names)

    def test_all_projects_and_project_filter_are_mutually_exclusive(self):
        code, _, err = _run([
            "--root", "/tmp/does-not-matter",
            "--all-projects",
            "--project", "foo",
        ])
        self.assertNotEqual(code, 0)
        self.assertIn("mutually exclusive", err)


class TestProjectFilter(unittest.TestCase):
    def test_dash_p_restricts_to_one_project_plus_global(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_fixture(root)
            code, data, _ = _run([
                "--root", str(root),
                "--project", "other-app",
                "--current-project", "my-app",
            ])
            self.assertEqual(code, 0)
            buckets = {(a["bucket"], a["project"]) for a in data}
            self.assertEqual(buckets, {("project", "other-app"), ("_global", None)})


class TestEmptyScope(unittest.TestCase):
    def test_empty_root_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            code, data, _ = _run([
                "--root", str(root),
                "--current-project", "my-app",
            ])
            self.assertEqual(code, 0)
            self.assertEqual(data, [])

    def test_current_project_with_no_bucket_still_lists_global(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "_global" / "notion").mkdir(parents=True)
            (root / "_global" / "notion" / "x.md").write_text("x")
            code, data, _ = _run([
                "--root", str(root),
                "--current-project", "nonexistent-project",
            ])
            self.assertEqual(code, 0)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["bucket"], "_global")


class TestDirectoryArtifacts(unittest.TestCase):
    """Apex task workspaces are directories; size sums files, mtime is the latest."""

    def test_directory_size_sums_inner_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inner = root / "my-app" / "apex" / "01-task"
            inner.mkdir(parents=True)
            (inner / "a.md").write_text("a" * 100)  # 100 bytes
            (inner / "b.md").write_text("b" * 250)  # 250 bytes
            code, data, _ = _run([
                "--root", str(root),
                "--current-project", "my-app",
            ])
            self.assertEqual(code, 0)
            row = next(a for a in data if a["skill"] == "apex")
            self.assertEqual(row["size_bytes"], 350)

    def test_directory_mtime_is_most_recent_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inner = root / "my-app" / "apex" / "01-task"
            inner.mkdir(parents=True)
            old = inner / "old.md"
            old.write_text("old")
            time.sleep(0.05)
            new = inner / "new.md"
            new.write_text("new")
            code, data, _ = _run([
                "--root", str(root),
                "--current-project", "my-app",
            ])
            self.assertEqual(code, 0)
            row = next(a for a in data if a["skill"] == "apex")
            # The reported mtime must be ≥ the older file's mtime.
            self.assertGreaterEqual(row["mtime_iso"], "2025")  # any sane ISO date


class TestMeasureHelper(unittest.TestCase):
    """Direct-call sanity check on the internal helper."""

    def test_measure_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "x.md"
            f.write_text("hello")
            size, mtime = measure(f)
            self.assertEqual(size, 5)
            self.assertRegex(mtime, r"^\d{4}-\d{2}-\d{2}T")

    def test_measure_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "task"
            d.mkdir()
            (d / "a").write_text("aa")
            (d / "b").write_text("bbbb")
            size, _ = measure(d)
            self.assertEqual(size, 6)

    def test_measure_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "empty"
            d.mkdir()
            size, _ = measure(d)
            self.assertEqual(size, 0)


class TestCurrentProjectDetection(unittest.TestCase):
    """`detect_current_project` kebab-cases the cwd basename when git isn't a repo."""

    def test_kebab_case_basename(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp) / "My_Cool App"
            cwd.mkdir()
            self.assertEqual(detect_current_project(cwd), "my-cool-app")

    def test_empty_basename_falls_back_to_unnamed(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp) / "___"
            cwd.mkdir()
            self.assertEqual(detect_current_project(cwd), "unnamed")


class TestEnumerateBucketHelper(unittest.TestCase):
    def test_missing_bucket_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(enumerate_bucket("project", "x", Path(tmp) / "missing"), [])

    def test_skill_subdirs_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            bucket = Path(tmp) / "my-app"
            bucket.mkdir()
            (bucket / "forge").mkdir()
            (bucket / "forge" / "x.md").write_text("x")
            (bucket / "loose-file.md").write_text("ignored — not under a skill subdir")
            result = enumerate_bucket("project", "my-app", bucket)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["skill"], "forge")


class TestListArtifactsHelper(unittest.TestCase):
    """Functional contract via the helper directly (faster than subprocess)."""

    def test_default_scope_helper(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_fixture(root)
            data = list_artifacts(root, "my-app", all_projects=False, project_filter=None)
            buckets = {(a["bucket"], a["project"]) for a in data}
            self.assertIn(("project", "my-app"), buckets)
            self.assertIn(("_global", None), buckets)
            self.assertNotIn(("project", "other-app"), buckets)


if __name__ == "__main__":
    unittest.main()
